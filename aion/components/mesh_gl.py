"""Lit 3D meshes + glowing point sprites on the GPU (moderngl), as a Manim ImageMobject.

    plate = MeshPlate(lambda: {
        "meshes": [tube_mesh(points, radius, colors, emissive)],   # opaque, lit, depth-tested
        "glass":  [ribbon_mesh(bottom, top, colors)],              # translucent, after opaque
        "points": (xyz (N,3), rgba (N,4), size_px (N,)),            # additive sprites
        "yaw": -90, "pitch": 28, "dist": 9.5, "target": (0, 0, 0.2), "fov": 38,
        "bloom": 1.0, "opacity": 1.0,
    })
    label.move_to(plate.project(x, y, z))                          # pinned 2.5D labels

Meshes are plain triangle lists built in numpy (helpers below). Shading: Phong with a
brushed-metal base plus a per-vertex emissive term (glowing hot metal). The camera is
the orbit camera from `surface_gl.camera_matrices`, so `project()` matches the shader.
The finish (bloom, vignette, grain) is `post_gl.GlowFinish`, as on every other plate.
Re-rendered every frame through a dt updater (so `wait()` never freezes it).
"""

from __future__ import annotations

from typing import Callable

import moderngl
import numpy as np
from manim import ORIGIN, ImageMobject, color_to_rgb, config

from .. import style as S
from . import blit
from .post_gl import GlowFinish
from .shader_plate import _ctx
from .surface_gl import camera_matrices

blit.install()

DEFAULTS = {"meshes": [], "glass": [], "points": None, "yaw": -90.0, "pitch": 28.0, "dist": 9.5,
            "target": (0.0, 0.0, 0.0), "fov": 38.0, "bloom": 1.0, "vignette": 0.5, "grain": 0.03,
            "opacity": 1.0, "metal": "#8A93A3", "light": (-0.4, -0.7, 1.0)}

_MESH_VS = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos; in vec3 in_nrm; in vec4 in_col; in vec3 in_emit;
out vec3 v_pos; out vec3 v_nrm; out vec4 v_col; out vec3 v_emit;
void main() { v_pos = in_pos; v_nrm = in_nrm; v_col = in_col; v_emit = in_emit;
              gl_Position = u_mvp * vec4(in_pos, 1.0); }
"""
_MESH_FS = """
#version 330
uniform vec3 u_eye; uniform vec3 u_light; uniform float u_lit;
in vec3 v_pos; in vec3 v_nrm; in vec4 v_col; in vec3 v_emit;
out vec4 f_col;
void main() {
    vec3 n = normalize(v_nrm), l = normalize(u_light), e = normalize(u_eye - v_pos);
    if (dot(n, e) < 0.0) n = -n;
    float d = max(dot(n, l), 0.0);
    float sp = pow(max(dot(reflect(-l, n), e), 0.0), 36.0);
    float rim = pow(1.0 - max(dot(n, e), 0.0), 3.0);
    vec3 c = v_col.rgb * (0.22 + 0.62 * d) + vec3(0.55) * sp + v_col.rgb * 0.25 * rim;
    c = mix(v_col.rgb, c, u_lit) + v_emit;
    f_col = vec4(c * v_col.a, v_col.a);          // premultiplied
}
"""
_PT_VS = """
#version 330
uniform mat4 u_mvp; uniform float u_px;
in vec3 in_pos; in vec4 in_col; in float in_size;
out vec4 v_col;
void main() { v_col = in_col; gl_Position = u_mvp * vec4(in_pos, 1.0);
              gl_PointSize = in_size * u_px; }
"""
_PT_FS = """
#version 330
in vec4 v_col; out vec4 f_col;
void main() { vec2 d = gl_PointCoord * 2.0 - 1.0; float r2 = dot(d, d);
              if (r2 > 1.0) discard;
              float a = exp(-3.5 * r2) * v_col.a; f_col = vec4(v_col.rgb * a, a); }
"""

_GL: dict[int, dict] = {}


def rgb(c) -> np.ndarray:
    return np.array(color_to_rgb(c), float)


# ── mesh helpers (all return (T*3, 13) float arrays: pos 3, nrm 3, rgba 4, emit 3) ──
def _frames(p: np.ndarray, closed: bool):
    """Tangent / normal / binormal along a polyline (normal kept close to +z-perp)."""
    t = np.gradient(p, axis=0)
    if closed:
        t = np.roll(p, -1, 0) - np.roll(p, 1, 0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
    up = np.array([0.0, 0.0, 1.0])
    b = np.cross(t, up)
    bad = np.linalg.norm(b, axis=1) < 1e-6
    b[bad] = np.cross(t[bad], [1.0, 0.0, 0.0])
    b /= np.linalg.norm(b, axis=1, keepdims=True)
    n = np.cross(b, t)
    return t, n, b


def tube_mesh(p, radius, color, emit=None, closed=False, sides: int = 18, alpha=1.0) -> np.ndarray:
    """A tube along polyline p (M,3). color/emit: (3,) or (M,3). radius: scalar or (M,)."""
    p = np.asarray(p, float)
    M = len(p)
    _, n, b = _frames(p, closed)
    r = np.broadcast_to(np.asarray(radius, float), (M,))
    a = np.linspace(0, 2 * np.pi, sides + 1)
    ca, sa = np.cos(a), np.sin(a)
    nrm = ca[None, :, None] * n[:, None, :] + sa[None, :, None] * b[:, None, :]   # (M, S+1, 3)
    pos = p[:, None, :] + r[:, None, None] * nrm
    col = np.broadcast_to(np.asarray(color, float).reshape(-1, 3), (M, 3))
    em = np.zeros((M, 3)) if emit is None else np.broadcast_to(np.asarray(emit, float).reshape(-1, 3), (M, 3))
    rows = list(range(M)) + ([0] if closed else [])
    i0, i1 = np.array(rows[:-1]), np.array(rows[1:])
    j0, j1 = np.arange(sides), np.arange(1, sides + 1)
    I0, J0 = np.meshgrid(i0, j0, indexing="ij")
    I1, J1 = np.meshgrid(i1, j1, indexing="ij")
    quads = [(I0, J0), (I1, J0), (I1, J1), (I0, J0), (I1, J1), (I0, J1)]
    out = np.empty((len(i0) * sides * 6, 13), "f4")
    for k, (I, J) in enumerate(quads):
        sl = slice(k, None, 6)
        out[sl, 0:3] = pos[I, J].reshape(-1, 3)
        out[sl, 3:6] = nrm[I, J].reshape(-1, 3)
        out[sl, 6:9] = col[I].reshape(-1, 3)
        out[sl, 9] = alpha
        out[sl, 10:13] = em[I].reshape(-1, 3)
    return out


def ribbon_mesh(bottom, top, color, alpha_bottom=0.0, alpha_top=0.35, emit_scale=1.0) -> np.ndarray:
    """A translucent curtain between two polylines (M,3) with per-point color (M,3); unlit, emissive."""
    bottom, top = np.asarray(bottom, float), np.asarray(top, float)
    col = np.broadcast_to(np.asarray(color, float).reshape(-1, 3), (len(top), 3))
    i0, i1 = np.arange(len(top) - 1), np.arange(1, len(top))
    tri_idx = [(i0, 0), (i0, 1), (i1, 1), (i0, 0), (i1, 1), (i1, 0)]   # (row, 0 = bottom / 1 = top)
    out = np.zeros((len(i0) * 6, 13), "f4")
    for k, (I, which) in enumerate(tri_idx):
        sl = slice(k, None, 6)
        src = top if which else bottom
        a = alpha_top if which else alpha_bottom
        out[sl, 0:3] = src[I]
        out[sl, 3:6] = [0, 0, 1]
        out[sl, 6:9] = 0.0
        out[sl, 9] = a
        out[sl, 10:13] = col[I] * emit_scale * a
    return out


class MeshPlate(ImageMobject):
    def __init__(self, state: Callable[[], dict], *, width: float | None = None, height: float | None = None,
                 center=ORIGIN, samples: int = 4, **kw):
        width = width or config.frame_width
        height = height or config.frame_height
        ppu = config.pixel_width / config.frame_width
        w, h = max(2, int(round(width * ppu))), max(2, int(round(height * ppu)))
        ctx = _ctx()
        mesh = ctx.program(vertex_shader=_MESH_VS, fragment_shader=_MESH_FS)
        pts = ctx.program(vertex_shader=_PT_VS, fragment_shader=_PT_FS)
        mvbo = ctx.buffer(reserve=4 * 13 * 3 * 200_000, dynamic=True)
        pvbo = ctx.buffer(reserve=4 * 8 * 20_000, dynamic=True)
        samples = min(samples, ctx.max_samples)
        ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)],
                             depth_attachment=ctx.depth_renderbuffer((w, h), samples=samples))
        out = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])
        super().__init__(np.zeros((h, w, 4), np.uint8), **kw)
        self._gl_key = id(self)
        _GL[self._gl_key] = dict(mesh=mesh, pts=pts, mvbo=mvbo, pvbo=pvbo, ms=ms, out=out, size=(w, h),
                                 glow=GlowFinish((w, h)), state=state,
                                 mvao=ctx.vertex_array(mesh, [(mvbo, "3f 3f 4f 3f", "in_pos", "in_nrm", "in_col", "in_emit")]),
                                 pvao=ctx.vertex_array(pts, [(pvbo, "3f 4f 1f", "in_pos", "in_col", "in_size")]))
        self.plate_w, self.plate_h = width, height
        self.plate_c = np.array(center, float)
        self.stretch_to_fit_width(width)
        self.stretch_to_fit_height(height)
        self.move_to(center)
        self._fast_blit = True
        self._frame = 0
        self.render_gl()
        self.add_updater(lambda m, dt: m.render_gl())

    def state(self) -> dict:
        return {**DEFAULTS, **_GL[self._gl_key]["state"]()}

    def project(self, x, y, z, s: dict | None = None) -> np.ndarray:
        s = s or self.state()
        w, h = _GL[self._gl_key]["size"]
        mvp, _ = camera_matrices(s, w / h)
        p = mvp @ np.array([x, y, z, 1.0])
        ndc = p[:2] / p[3]
        return self.plate_c + np.array([ndc[0] * self.plate_w / 2, ndc[1] * self.plate_h / 2, 0.0])

    def _draw(self, vbo, vao, arr, mode):
        if arr is None or not len(arr):
            return
        data = np.ascontiguousarray(arr, "f4").tobytes()
        if len(data) > vbo.size:
            vbo.orphan(len(data))
        vbo.write(data)
        vao.render(mode, vertices=len(arr))

    def render_gl(self) -> "MeshPlate":
        gl = _GL[self._gl_key]
        ctx = _ctx()
        s = self.state()
        w, h = gl["size"]
        op = float(np.clip(s["opacity"], 0, 1))
        if op <= 0.002:
            self.pixel_array = np.zeros((h, w, 4), np.uint8)
            self._blit_add = True
            return self
        mvp, eye = camera_matrices(s, w / h)
        m = gl["mesh"]
        m["u_mvp"].write(mvp.T.astype("f4").tobytes())
        m["u_eye"].value = tuple(map(float, eye))
        m["u_light"].value = tuple(map(float, s["light"]))
        gl["pts"]["u_mvp"].write(mvp.T.astype("f4").tobytes())
        gl["pts"]["u_px"].value = config.pixel_height / 1080.0
        ms = gl["ms"]
        ms.use()
        ctx.viewport = (0, 0, w, h)
        ms.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        m["u_lit"].value = 1.0
        meshes = [x for x in s["meshes"] if x is not None and len(x)]
        if meshes:
            self._draw(gl["mvbo"], gl["mvao"], np.concatenate(meshes), moderngl.TRIANGLES)
        ms.depth_mask = False
        glass = [x for x in s["glass"] if x is not None and len(x)]
        if glass:
            m["u_lit"].value = 0.0
            ctx.blend_func = moderngl.ONE, moderngl.ONE      # glowing translucent: additive
            self._draw(gl["mvbo"], gl["mvao"], np.concatenate(glass), moderngl.TRIANGLES)
        if s["points"] is not None and len(s["points"][0]):
            xyz, col, size = s["points"]
            arr = np.concatenate([xyz, col, np.asarray(size, float)[:, None]], 1)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self._draw(gl["pvbo"], gl["pvao"], arr, moderngl.POINTS)
        ms.depth_mask = True
        ctx.disable(moderngl.DEPTH_TEST | moderngl.BLEND)
        gl["glow"].apply(ms, gl["out"], bloom=s["bloom"] * S.GL_BLOOM_SCALE, vignette=min(s["vignette"], S.GL_VIGNETTE_MAX),
                         grain=min(s["grain"], S.GL_GRAIN_MAX),
                         seed=float(self._frame % 997))
        self._frame += 1
        ctx.viewport = (0, 0, w, h)
        img = np.frombuffer(gl["out"].read(components=4), np.uint8).reshape(h, w, 4)[::-1]
        arr = np.empty((h, w, 4), np.uint8)
        arr[..., :3] = img[..., :3] if op >= 0.999 else (img[..., :3] * op).astype(np.uint8)
        arr[..., 3] = 255
        self._blit_add = True           # light on black: add onto whatever Manim drew below
        self.pixel_array = np.ascontiguousarray(arr)
        return self
