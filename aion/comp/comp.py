"""Comp: a stack of layers composited on the GPU in linear light.

    comp = Comp(size=(1920, 1080), fps=60, background="#0d1117")
    comp.add(ShaderLayer("layers/domain_coloring.frag", z=-1, u_theta=key(2.0, 0, 3.14)))
    comp.add(manim_layer)
    comp.fx = [Bloom(0.6), Vignette(0.3)]
    rgb = comp.frame(2.5)              # HxWx3 uint8, top row first

Pipeline per frame: background → layers by (z, insertion) → each layer's own fx
(isolated in a full-frame buffer) → matte → blend into an RGBA16F linear
premultiplied accumulator → comp fx → sRGB + dither → readback.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from aion.comp.blend import ADVANCED, FAST, gl_func
from aion.comp.camera import Camera
from aion.gpu import pool
from aion.gpu.context import gl
from aion.gpu.program import fullscreen, program, set_uniforms
from aion.layers.base import ENC_LINEAR, Layer, RenderContext, Surface

__all__ = ["Comp", "hex_to_linear"]

_MATTE = {"alpha": 1, "alpha_inv": 2, "luma": 3, "luma_inv": 4}


def hex_to_linear(c) -> tuple[float, float, float]:
    """'#rrggbb' / (r, g, b) sRGB 0-1 / ManimColor → linear RGB.

    Example:
        r, g, b = hex_to_linear(C.accent)
    """
    if hasattr(c, "to_rgb"):
        c = c.to_rgb()
    if isinstance(c, str):
        c = c.lstrip("#")
        c = tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    c = np.asarray(c, dtype=float)[:3]
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).tolist())


class Comp(Layer):
    """Layer stack → frame. A Comp is itself a Layer (use it as a precomp).

    Example:
        comp = Comp((1280, 720), 30, C.bg, layers=[Gradient(C.bg2, C.bg)], fx=[Bloom()])
        img = comp.frame(1.0)            # HxWx3 uint8
    """

    vector = True

    def __init__(self, size: tuple[int, int] = (1920, 1080), fps: float = 60, background=None,
                 layers: Iterable[Layer] = (), fx=(), camera: Camera | None = None,
                 frame_height: float = 8.0, seed: int = 0, **layer_kw):
        super().__init__(**layer_kw)
        self.size = (int(size[0]), int(size[1]))
        self.fps = fps
        self.frame_units = (frame_height * self.size[0] / self.size[1], frame_height)
        self.background = None if background is None else hex_to_linear(background)
        self.layers: list[Layer] = []
        self.comp_fx = list(fx)
        self.camera = camera or Camera()
        self.seed = seed
        self._acc = None
        self._out = None
        self._last_frame: tuple[float, np.ndarray] | None = None
        for layer in layers:
            self.add(layer)

    # ── building ─────────────────────────────────────────────────────────────
    def add(self, layer: Layer) -> Layer:
        layer.order = len(self.layers)
        self.layers.append(layer)
        return layer

    def content_changes(self, t0: float, t1: float) -> bool:
        return (self.camera.changes(t0, t1)
                or any(l.changes(t0, t1) or (l.start != -math.inf and t0 < l.start <= t1)
                       or (l.end != math.inf and t0 < l.end <= t1) for l in self.layers)
                or any(getattr(f, "changes", lambda a, b: True)(t0, t1) for f in self.comp_fx))

    def context(self, t: float, frame_index: int | None = None) -> RenderContext:
        k = round(t * self.fps) if frame_index is None else frame_index
        return RenderContext(self.size, self.fps, self.frame_units, t, k, self.camera.at(t), self.seed)

    # ── rendering ────────────────────────────────────────────────────────────
    def _mvp(self, layer: Layer, surf: Surface, t: float, rc: RenderContext) -> np.ndarray:
        """Unit quad → clip space."""
        fw, fh = self.frame_units
        to_clip = np.diag([2 / fw, 2 / fh, 1.0])
        if surf.extent is None or layer.vector:
            if not surf.screen_rot:
                return np.eye(3)
            c, s = math.cos(-surf.screen_rot), math.sin(-surf.screen_rot)
            return to_clip @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) @ np.diag([fw / 2, fh / 2, 1.0])
        w, h = surf.extent
        quad = np.diag([w / 2, h / 2, 1.0])
        return to_clip @ rc.view(layer.parallax) @ layer.model(t) @ quad

    def _draw(self, surf: Surface, mvp, opacity: float, mode: str, dst, matte=None, matte_mode="alpha"):
        """Draw a surface onto render target `dst` (pool.RenderTarget)."""
        ctx = gl()
        prog = program("comp/composite.frag", "comp/quad.vert")
        adv = ADVANCED.get(mode)
        uniforms = dict(u_mvp=mvp, u_enc=surf.enc, u_opacity=opacity, u_res=self.size,
                        u_src=(surf.tex, 0), u_mode=adv or 0,
                        u_matte_mode=_MATTE[matte_mode] if matte is not None else 0)
        if matte is not None:
            uniforms["u_matte"] = (matte.tex, 1)
        copy = None
        if adv:
            copy = pool.target(self.size, "f2")
            ctx.copy_framebuffer(copy.fbo, dst.fbo)
            uniforms["u_dst"] = (copy.tex, 2)
        set_uniforms(prog, **uniforms)
        dst.fbo.use()
        if adv:
            ctx.disable(_BLEND())
        else:
            ctx.enable(_BLEND())
            ctx.blend_func = gl_func(mode if mode in FAST else "normal")
        prog_vao = _quad_vao(prog)
        prog_vao.render(mode=_STRIP(), vertices=4)
        ctx.disable(_BLEND())
        if copy is not None:
            pool.release(copy)

    def _isolate(self, layer: Layer, t: float, rc: RenderContext) -> Surface:
        """Render one layer alone into a full-frame linear buffer, then run its fx."""
        surf = layer.surface(t, rc)
        rt = pool.target(self.size, "f2")
        rt.use()
        self._draw(surf, self._mvp(layer, surf, t, rc), 1.0, "normal", rt)
        for f in layer.fx:
            rt2 = f.apply(rt, t, rc)
            if rt2 is not rt:
                pool.release(rt)
                rt = rt2
        out = Surface(rt.tex, ENC_LINEAR, None)
        out._rt = rt
        return out

    def render(self, t: float, rc: RenderContext | None = None):
        """Composite all layers at time t into the accumulator (RenderTarget, linear premul)."""
        rc = rc or self.context(t)
        if self._acc is None:
            self._acc = pool.target(self.size, "f2", pooled=False)
        acc = self._acc
        bg = self.background
        acc.use(clear=(*bg, 1.0) if bg is not None else (0, 0, 0, 0))
        temps = []
        for layer in sorted(self.layers, key=lambda l: (l.z, l.order)):
            if not layer.visible(t):
                continue
            if layer.fx:
                surf = self._isolate(layer, t, rc)
                temps.append(surf._rt)
                mvp = np.eye(3)
            else:
                surf = layer.surface(t, rc)
                mvp = self._mvp(layer, surf, t, rc)
            matte = None
            if layer.matte is not None:
                matte_s = self._isolate(layer.matte, t, rc)
                temps.append(matte_s._rt)
                matte = matte_s
            self._draw(surf, mvp, float(layer.opacity(t)), layer.blend, acc, matte, layer.matte_mode)
        for rt in temps:
            pool.release(rt)
        out = acc
        for f in self.comp_fx:
            nxt = f.apply(out, t, rc)
            if out is not acc and nxt is not out:
                pool.release(out)
            out = nxt
        return out

    def draw(self, t: float, rc: RenderContext) -> Surface:
        """As a precomp layer inside another comp."""
        rt = self.render(t, self.context(t, rc.frame_index))
        return Surface(rt.tex, ENC_LINEAR, None)

    def frame(self, t: float, frame_index: int | None = None, alpha: bool = False) -> np.ndarray:
        """Final display-referred frame: HxWx3 (or HxWx4 with alpha) uint8, top row first."""
        if self._last_frame is not None:
            t_prev, img = self._last_frame
            if not self.content_changes(min(t_prev, t), max(t_prev, t)) and img.shape[2] == (4 if alpha else 3):
                return img
        rc = self.context(t, frame_index)
        src = self.render(t, rc)
        img = self.output(src, rc, alpha)
        if src is not self._acc:
            pool.release(src)
        self._last_frame = (t, img)
        return img

    def output(self, src, rc: RenderContext, alpha: bool = False) -> np.ndarray:
        ctx = gl()
        comps = 4 if alpha else 3
        if self._out is None or self._out.size != self.size:
            self._out = pool.target(self.size, "f1", pooled=False, linear=False)
        prog = program("comp/output.frag")
        set_uniforms(prog, u_src=(src.tex, 0), u_bg=self.background or (0, 0, 0),
                     u_frame_index=float(rc.frame_index), u_alpha=int(alpha))
        self._out.use(clear=None)
        ctx.disable(_BLEND())
        fullscreen(prog).render(vertices=3)
        data = self._out.fbo.read(components=comps, dtype="f1", alignment=1)
        return np.frombuffer(data, np.uint8).reshape(self.size[1], self.size[0], comps)


_QUAD_VAOS: dict[int, object] = {}


def _quad_vao(prog):
    vao = _QUAD_VAOS.get(id(prog))
    if vao is None:
        vao = _QUAD_VAOS[id(prog)] = gl().vertex_array(prog, [])
    return vao


def _BLEND():
    import moderngl

    return moderngl.BLEND


def _STRIP():
    import moderngl

    return moderngl.TRIANGLE_STRIP
