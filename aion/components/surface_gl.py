"""A 3D surface z = f(x, y) rendered on the GPU (moderngl) inside a Manim scene.

    H = [ValueTracker(2), ValueTracker(3), ValueTracker(2)]
    cam = {"yaw": ValueTracker(-55), "pitch": ValueTracker(32), "dist": ValueTracker(9)}
    plate = SurfacePlate(lambda: {
        "H": tuple(v.get_value() for v in H),
        "yaw": cam["yaw"].get_value(), "pitch": cam["pitch"].get_value(),
        "dist": cam["dist"].get_value(),
        "fog": 0.05, "contour": 1.0,
        "slices": [slice_line(angle_deg=0, color=S.HX, plane=0.18)],
    })
    self.add(plate)                       # re-rendered every frame
    dot.add_updater(lambda m: m.move_to(plate.surface_point(0.4, 0.2)))   # 2.5D overlay

Why: Manim's ThreeDScene draws 3D on the CPU (Cairo), far too slow for long
1080p60 shots on 2 cores. Here the mesh renders on the GPU in milliseconds and
Manim only composites the image. `project()` uses the *same* camera matrix as
the shader, so Manim labels, dots and arrows stay pixel-locked to the surface.

Everything is driven by the state callback (ValueTrackers). Don't animate the
plate mobject itself (FadeIn, .animate): copies would share GPU state. Use the
"opacity" key instead.

State keys (all optional, see DEFAULTS):
  height  H (a, b, c), w (wq, wg, wc, w4), wm, offset, gauss [(cx, cy, amp, sigma)…],
          zs (vertical scale), zclip (soft clamp, 0 = off)
  domain  R (half size), center (cx, cy), edge (radius fraction where the fade-out starts)
  camera  target (x, y, z), yaw, pitch (degrees), dist, fov (vertical degrees)
  look    fill (surface opacity; < 1 switches to additive "wireframe" mode), opacity,
          zlo/zhi (colour ramp range), contour, contour_step, grid (along-x, along-y),
          grid_step, grid_angle (deg), tint (bend tint strength), tint_center,
          fog, fog_height, fog_color, time (fog drift), sky (horizon haze strength)
  extras  slices [dict from slice_line()], disc (dict from tangent_disc() or None)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

import moderngl
import numpy as np
from manim import ORIGIN, ImageMobject, color_to_rgb, config

from .. import style as S
from .shader_plate import _ctx
from . import blit
from .post_gl import GlowFinish

blit.install()

SHADER_DIR = Path(__file__).resolve().parents[1] / "shaders"

MAX_GAUSS = 16
MAX_SLICES = 4

DEFAULTS: dict = {
    # height model
    "H": (2.0, 0.0, 2.0), "w": (1.0, 0.0, 0.0, 0.0), "wm": 0.0, "offset": 0.0,
    "gauss": [], "zs": 0.35, "zclip": 0.0,
    # domain
    "R": 3.0, "center": (0.0, 0.0), "edge": 0.72,
    # camera
    "target": (0.0, 0.0, 0.0), "yaw": -60.0, "pitch": 30.0, "dist": 9.0, "fov": 38.0,
    # look
    "fill": 1.0, "opacity": 1.0, "zlo": -1.5, "zhi": 1.5,
    "contour": 0.0, "contour_step": 0.25,
    "grid": (0.35, 0.35), "grid_step": 0.5, "grid_angle": 0.0,
    "tint": 0.0, "tint_center": (0.0, 0.0),
    "fog": 0.0, "fog_height": 0.0, "fog_color": None, "time": 0.0, "sky": 0.0,
    "slices": [], "disc": None,
    # luminous look (Aion design system): lum 1 = black body + silver lines; finish = glow pass
    "lum": 0.0, "bloom": 0.0, "vignette": 0.0, "grain": 0.0,
}


def _rgb(c) -> tuple[float, float, float]:
    return tuple(float(v) for v in color_to_rgb(c))


def slice_line(angle_deg: float = 0.0, offset: float = 0.0, color=S.TEXT, line: float = 1.0,
               plane: float = 0.0, width: float = 0.022, rise: float = 0.9) -> dict:
    """A vertical plane through the floor line at `angle_deg` (0 = facing east, 90 = north),
    shifted by `offset` along its normal. Draws the cut curve on the surface (strength `line`)
    and, if `plane` > 0, a translucent sheet of the plane rising `rise` above the cut."""
    a = math.radians(angle_deg)
    n = (-math.sin(a), math.cos(a))           # normal of a line running in direction a
    return {"n": n, "d": offset, "color": color, "line": line, "plane": plane,
            "width": width, "rise": rise, "dir": (math.cos(a), math.sin(a))}


def tangent_disc(x: float, y: float, r: float = 0.55, alpha: float = 0.45, color=S.TEXT) -> dict:
    return {"x": x, "y": y, "r": r, "alpha": alpha, "color": color}


def height(state: dict, x, y):
    """Python mirror of shaders/surface.glsl (numpy-friendly)."""
    s = {**DEFAULTS, **state}
    x, y = np.asarray(x, float), np.asarray(y, float)
    a, b, c = s["H"]
    wq, wg, wc, w4 = s["w"]
    raw = wq * 0.5 * (a * x * x + 2 * b * x * y + c * y * y)
    for cx, cy, amp, sig in s["gauss"]:
        raw = raw + wg * amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sig * sig))
    raw = raw + wc * (x ** 3 - 3 * x + y ** 2) + w4 * (x ** 4 + y ** 4) + \
        s["wm"] * (x ** 3 - 3 * x * y * y) + s["offset"]
    z = s["zs"] * raw
    if s["zclip"] > 0:
        z = s["zclip"] * np.tanh(z / s["zclip"])
    return z


def camera_matrices(s: dict, aspect: float) -> tuple[np.ndarray, np.ndarray]:
    """(mvp, eye) for the orbit camera described by `s` (row-major math matrices)."""
    yaw, pitch = math.radians(s["yaw"]), math.radians(s["pitch"])
    tgt = np.array(s["target"], float)
    eye = tgt + s["dist"] * np.array([math.cos(pitch) * math.cos(yaw),
                                      math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
    f = tgt - eye
    f /= np.linalg.norm(f)
    up = np.array([0.0, 0.0, 1.0])
    if abs(f @ up) > 0.999:                    # straight down: use +y as screen-up
        up = np.array([0.0, 1.0, 0.0])
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    view = np.eye(4)
    view[0, :3], view[1, :3], view[2, :3] = r, u, -f
    view[:3, 3] = -view[:3, :3] @ eye
    near, far = 0.05, 200.0
    t = 1.0 / math.tan(math.radians(s["fov"]) / 2)
    proj = np.zeros((4, 4))
    proj[0, 0], proj[1, 1] = t / aspect, t
    proj[2, 2], proj[2, 3] = (far + near) / (near - far), 2 * far * near / (near - far)
    proj[3, 2] = -1.0
    return proj @ view, eye


_GL: dict[int, dict] = {}


class SurfacePlate(ImageMobject):
    """GPU surface as an ImageMobject of size `width` × `height` (Manim units) at `center`.

    `opaque=True` (default) is the fast path for a plate that sits on a pure-black
    background: the image is written premultiplied with alpha 1. While its opacity
    is below 1 the plate is blitted additively, so two plates cross-dissolve. Use `opaque=False`
    when the plate must composite over other mobjects (cards, other plates).
    """

    def __init__(self, state: Callable[[], dict], *, width: float | None = None,
                 height: float | None = None, center=ORIGIN, mesh: int = 220,
                 samples: int = 4, opaque: bool = True, scale: float = 1.0, **kw):
        width = width or config.frame_width
        height = height or config.frame_height
        ppu = config.pixel_width / config.frame_width * scale
        w, h = max(2, int(round(width * ppu))), max(2, int(round(height * ppu)))
        ctx = _ctx()
        head = "#version 330\n" + (SHADER_DIR / "surface.glsl").read_text()
        prog = ctx.program(vertex_shader=head + _SURF_VS, fragment_shader=head + _SURF_FS)
        flat = ctx.program(vertex_shader=_FLAT_VS, fragment_shader=_FLAT_FS)

        g = np.linspace(-1, 1, mesh + 1, dtype="f4")
        gx, gy = np.meshgrid(g, g)
        verts = np.stack([gx.ravel(), gy.ravel()], 1).astype("f4")
        i = np.arange(mesh)
        a = (i[None, :] + (mesh + 1) * i[:, None]).ravel()
        idx = np.stack([a, a + 1, a + mesh + 1, a + 1, a + mesh + 2, a + mesh + 1], 1)
        vao = ctx.vertex_array(prog, [(ctx.buffer(verts.tobytes()), "2f", "in_uv")],
                               index_buffer=ctx.buffer(idx.astype("i4").tobytes()))
        sky = ctx.program(vertex_shader=_SKY_VS, fragment_shader=_SKY_FS)
        sky_vao = ctx.vertex_array(sky, [(ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes()), "2f", "in_pos")])
        flat_vbo = ctx.buffer(reserve=4 * 7 * 6 * 400 * MAX_SLICES)
        flat_vao = ctx.vertex_array(flat, [(flat_vbo, "3f 4f", "in_pos", "in_col")])

        samples = min(samples, ctx.max_samples)
        ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)],
                             depth_attachment=ctx.depth_renderbuffer((w, h), samples=samples))
        out = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])

        super().__init__(np.zeros((h, w, 4), dtype=np.uint8), **kw)
        self._gl_key = id(self)
        _GL[self._gl_key] = dict(prog=prog, flat=flat, sky=sky, sky_vao=sky_vao, vao=vao, flat_vbo=flat_vbo,
                                 flat_vao=flat_vao, ms=ms, out=out, size=(w, h),
                                 state=state, opaque=opaque)
        self.plate_w, self.plate_h = width, height
        self.plate_c = np.array(center, float)
        self.stretch_to_fit_width(width)
        self.stretch_to_fit_height(height)
        self.move_to(center)
        self._fast_blit = True
        self._frame = 0
        self.render_gl()
        self.add_updater(lambda m: m.render_gl())

    # ── state & geometry (Python side) ─────────────────────────
    def state(self) -> dict:
        return {**DEFAULTS, **_GL[self._gl_key]["state"]()}

    def height(self, x, y, s: dict | None = None):
        return height(s or self.state(), x, y)

    def project(self, x: float, y: float, z: float, s: dict | None = None) -> np.ndarray:
        """World point → Manim coordinates on this plate (same matrix as the shader)."""
        s = s or self.state()
        w, h = _GL[self._gl_key]["size"]
        mvp, _ = camera_matrices(s, w / h)
        p = mvp @ np.array([x, y, z, 1.0])
        ndc = p[:2] / p[3]
        return self.plate_c + np.array([ndc[0] * self.plate_w / 2, ndc[1] * self.plate_h / 2, 0.0])

    def surface_point(self, x: float, y: float, lift: float = 0.0) -> np.ndarray:
        s = self.state()
        return self.project(x, y, float(self.height(x, y, s)) + lift, s)

    # ── GPU ────────────────────────────────────────────────────
    def render_gl(self) -> "SurfacePlate":
        gl = _GL[self._gl_key]
        s = self.state()
        ctx, prog = _ctx(), gl["prog"]
        w, h = gl["size"]
        mvp, eye = camera_matrices(s, w / h)
        fog_col = _rgb(s["fog_color"] or S.FOG)

        gauss = list(s["gauss"])[:MAX_GAUSS]
        gpad = [tuple(map(float, g)) for g in gauss] + [(0.0, 0.0, 0.0, 1.0)] * (MAX_GAUSS - len(gauss))
        sl = list(s["slices"])[:MAX_SLICES]
        sl_plane = [(*q["n"], q["d"], q["width"]) for q in sl] + [(0, 1, 1e6, 0)] * (MAX_SLICES - len(sl))
        sl_col = [(*_rgb(q["color"]), q["line"]) for q in sl] + [(0, 0, 0, 0)] * (MAX_SLICES - len(sl))
        sa = math.radians(s["grid_angle"])
        U = {
            "u_mvp": mvp.T.astype("f4").tobytes(), "u_eye": tuple(eye),
            "u_H": tuple(s["H"]), "u_w": tuple(s["w"]), "u_wm": s["wm"], "u_offset": s["offset"],
            "u_gauss": gpad, "u_ngauss": len(gauss), "u_zs": s["zs"], "u_zclip": s["zclip"],
            "u_R": s["R"], "u_center": tuple(s["center"]), "u_edge": s["edge"],
            "u_fill": s["fill"], "u_zlo": s["zlo"], "u_zhi": s["zhi"],
            "u_lo": _rgb(S.SURF_LO), "u_hi": _rgb(S.SURF_HI),
            "u_contour": s["contour"], "u_contour_step": s["contour_step"],
            "u_grid": tuple(s["grid"]), "u_grid_step": s["grid_step"],
            "u_grid_rot": (math.cos(sa), math.sin(sa)), "u_grid_col": _rgb(S.SURF_LINE),
            "u_tint": s["tint"], "u_tint_center": tuple(s["tint_center"]),
            "u_smile": _rgb(S.SMILE), "u_frown": _rgb(S.FROWN),
            "u_fog": s["fog"], "u_fog_h": s["fog_height"], "u_fog_col": fog_col, "u_time": s["time"],
            "u_sl_plane": sl_plane, "u_sl_col": sl_col, "u_px": config.pixel_height / 1080.0,
            "u_lum": float(s["lum"]), "u_body": _rgb(S.TERRAIN_BODY), "u_line": _rgb(S.TERRAIN_LINE),
        }
        for k, v in U.items():
            if k in prog:
                if k == "u_mvp":
                    prog[k].write(v)
                else:
                    prog[k].value = v

        ms = gl["ms"]
        ms.use()
        ms.clear(0.0, 0.0, 0.0, 0.0, depth=1.0)
        if s["sky"] > 0:                                  # horizon haze behind everything
            yaw, pitch = math.radians(s["yaw"]), math.radians(s["pitch"])
            fwd = -np.array([math.cos(yaw), math.sin(yaw), 0.0])
            hp = mvp @ np.array([*(np.array(s["target"]) + 200 * fwd)[:2], s["target"][2], 1.0])
            gl["sky"]["u_horizon"].value = float(hp[1] / hp[3])
            gl["sky"]["u_col"].value = fog_col
            gl["sky"]["u_strength"].value = float(s["sky"])
            gl["sky_vao"].render()
        ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        wire = s["fill"] < 0.999
        ms.depth_mask = not wire
        gl["vao"].render()

        gl["flat"]["u_mvp"].write(mvp.T.astype("f4").tobytes())
        ms.depth_mask = False
        for tris, depth in ((self._curtains(s, fog_col, eye), True),
                            (self._disc(s, fog_col, eye), False)):
            if not len(tris):
                continue
            if not depth:
                ctx.disable(moderngl.DEPTH_TEST)
            gl["flat_vbo"].orphan(max(tris.nbytes, gl["flat_vbo"].size))
            gl["flat_vbo"].write(tris.tobytes())
            gl["flat_vao"].render(moderngl.TRIANGLES, vertices=len(tris))
        ms.depth_mask = True
        ctx.disable(moderngl.DEPTH_TEST | moderngl.BLEND)

        finish = gl["opaque"] and (s["bloom"] > 0 or s["vignette"] > 0 or s["grain"] > 0)
        if finish:
            if gl.get("glow") is None:
                gl["glow"] = GlowFinish((w, h))
            gl["glow"].apply(ms, gl["out"], bloom=s["bloom"], vignette=s["vignette"], grain=s["grain"],
                             seed=(s["time"] * 60.0) % 997.0 + self._frame)
            self._frame = (self._frame + 1) % 997
        else:
            ctx.copy_framebuffer(gl["out"], ms)
        ctx.viewport = (0, 0, w, h)
        img = np.frombuffer(gl["out"].read(components=4), dtype=np.uint8).reshape(h, w, 4)[::-1]
        op = float(np.clip(s["opacity"], 0, 1))
        if gl["opaque"]:
            rgb = img[..., :3] if op >= 0.999 else (img[..., :3] * op).astype(np.uint8)
            arr = np.empty((h, w, 4), np.uint8)
            arr[..., :3] = rgb
            arr[..., 3] = 255
            # while fading, add onto what is below (on pure black this is an exact
            # cross-dissolve with another fading plate) instead of blacking it out
            self._blit_add = op < 0.999
        else:
            self._blit_add = False
            f = img.astype(np.float32)
            a = f[..., 3:4] / 255.0
            f[..., :3] = np.where(a > 0, f[..., :3] / np.maximum(a, 1e-6), 0)
            f[..., 3] *= op
            arr = np.clip(f, 0, 255).astype(np.uint8)
        self.pixel_array = np.ascontiguousarray(arr)
        return self

    @staticmethod
    def _fogged(s, fog_col, eye, rgb, alpha, p):
        d = np.linalg.norm(np.asarray(p) - eye)
        f = 1 - math.exp(-s["fog"] * d)
        c = [(1 - f) * a + f * b for a, b in zip(rgb, fog_col)]
        return [ci * alpha for ci in c] + [alpha]

    def _curtains(self, s: dict, fog_col, eye) -> np.ndarray:
        """Translucent slice curtains, as premultiplied triangles."""
        out = []

        def fogged(rgb, alpha, p):
            return self._fogged(s, fog_col, eye, rgb, alpha, p)

        R = s["R"]
        for q in list(s["slices"])[:MAX_SLICES]:
            if q["plane"] <= 0:
                continue
            # A "curtain": the part of the cutting plane that rises above the surface,
            # brightest at the cut curve, fading upward and toward the ends.
            nx, ny = q["n"]
            dx, dy = q["dir"]
            cx, cy = s["center"]
            base = np.array([cx + nx * q["d"], cy + ny * q["d"]])
            L = R * 0.97
            ts = np.linspace(-L, L, 97)
            xs, ys = base[0] + ts * dx, base[1] + ts * dy
            zs = height(s, xs, ys)
            rise = q["rise"]
            rgb = _rgb(q["color"])
            sheet = q["plane"] * (1.0 - 0.6 * float(np.clip(s["lum"], 0, 1)))   # luminous: bloom does the rest
            ends = np.clip((L - np.abs(ts)) / (0.35 * R), 0, 1) ** 1.5
            for k in range(len(ts) - 1):
                quad = []
                for j in (k, k + 1):
                    bot = (xs[j], ys[j], zs[j] + 0.002)
                    top = (xs[j], ys[j], zs[j] + rise)
                    quad += [(bot, fogged(rgb, sheet * ends[j], bot)),
                             (top, fogged(rgb, 0.0, top))]
                for m in (0, 1, 2, 1, 3, 2):
                    out.append([*quad[m][0], *quad[m][1]])
        return np.array(out, dtype="f4").reshape(-1, 7)

    def _disc(self, s: dict, fog_col, eye) -> np.ndarray:
        """The tangent disc: drawn over the surface (an annotation, no depth test)."""
        out = []

        def fogged(rgb, alpha, p):
            return self._fogged(s, fog_col, eye, rgb, alpha, p)

        dsc = s["disc"]
        if dsc:
            z = float(height(s, dsc["x"], dsc["y"])) + 0.004
            rgb = _rgb(dsc["color"])
            c0 = (dsc["x"], dsc["y"], z)
            n = 72
            if s["lum"] > 0.5:                       # luminous: a thin bright ring over a faint film
                r0, r1 = dsc["r"] * 0.93, dsc["r"] * 1.0
                for k in range(n):
                    a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
                    q = [(dsc["x"] + r * math.cos(t), dsc["y"] + r * math.sin(t), z)
                         for r, t in ((r0, a0), (r1, a0), (r0, a1), (r1, a1))]
                    f0 = (dsc["x"], dsc["y"], z)
                    out += [[*f0, *fogged(rgb, dsc["alpha"] * 0.12, f0)],
                            [*q[0], *fogged(rgb, dsc["alpha"] * 0.22, q[0])],
                            [*q[2], *fogged(rgb, dsc["alpha"] * 0.22, q[2])]]
                    for i in (0, 1, 2, 1, 3, 2):
                        out.append([*q[i], *fogged(rgb, min(1.0, dsc["alpha"] * 1.8), q[i])])
                return np.array(out, dtype="f4").reshape(-1, 7)
            for k in range(n):
                a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
                p0 = (dsc["x"] + dsc["r"] * math.cos(a0), dsc["y"] + dsc["r"] * math.sin(a0), z)
                p1 = (dsc["x"] + dsc["r"] * math.cos(a1), dsc["y"] + dsc["r"] * math.sin(a1), z)
                out += [[*c0, *fogged(rgb, dsc["alpha"] * 0.55, c0)],
                        [*p0, *fogged(rgb, dsc["alpha"], p0)],
                        [*p1, *fogged(rgb, dsc["alpha"], p1)]]
        return np.array(out, dtype="f4").reshape(-1, 7)


_SURF_VS = """
in vec2 in_uv;
uniform mat4 u_mvp;
uniform float u_R;
uniform vec2 u_center;
out vec2 v_p;
out vec3 v_world;
void main() {
    vec2 p = u_center + in_uv * u_R;
    float z = height(p);
    v_p = p;
    v_world = vec3(p, z);
    gl_Position = u_mvp * vec4(p, z, 1.0);
}
"""

_SURF_FS = """
in vec2 v_p;
in vec3 v_world;
uniform vec3 u_eye;
uniform float u_R, u_edge, u_fill, u_zlo, u_zhi;
uniform vec2 u_center;
uniform vec3 u_lo, u_hi;
uniform float u_contour, u_contour_step;
uniform vec2 u_grid;
uniform float u_grid_step;
uniform vec2 u_grid_rot;
uniform vec3 u_grid_col;
uniform float u_tint;
uniform vec2 u_tint_center;
uniform vec3 u_smile, u_frown;
uniform float u_fog, u_fog_h, u_time;
uniform vec3 u_fog_col;
uniform vec4 u_sl_plane[4];
uniform vec4 u_sl_col[4];
uniform float u_lum;                                    // 0 = slate look, 1 = luminous (design system)
uniform vec3 u_body, u_line;
out vec4 frag;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x),
               mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}
uniform float u_px;                                     // pixels per 1080p pixel
// Periodic line of width `px` pixels on the continuous coordinate v (lines at integers).
float gridline(float v, float px) {
    float fw = max(fwidth(v), 1e-5);
    float d = abs(fract(v + 0.5) - 0.5) / fw;           // distance in pixels
    float l = 1.0 - smoothstep(0.5 * px * u_px - 0.5, 0.5 * px * u_px + 0.5, d);
    return l * (1.0 - smoothstep(0.12, 0.35, fw));      // fade out where lines get too dense
}

void main() {
    vec2 p = v_p;
    float z = v_world.z;
    float e = 0.002 * u_R;
    float hx = (height(p + vec2(e, 0)) - height(p - vec2(e, 0))) / (2.0 * e);
    float hy = (height(p + vec2(0, e)) - height(p - vec2(0, e))) / (2.0 * e);
    vec3 n = normalize(vec3(-hx, -hy, 1.0));
    vec3 V = normalize(u_eye - v_world);
    if (dot(n, V) < 0.0) n = -n;                       // underside seen from below

    // base: slate ramp by height, key + fill light, soft rim
    float t = clamp((z - u_zlo) / max(u_zhi - u_zlo, 1e-4), 0.0, 1.0);
    vec3 base = mix(u_lo, u_hi, t);
    vec3 L1 = normalize(vec3(-0.45, -0.6, 0.75));
    vec3 L2 = normalize(vec3(0.7, 0.4, 0.35));
    float dif = max(dot(n, L1), 0.0) * 0.85 + max(dot(n, L2), 0.0) * 0.25;
    float rim = pow(1.0 - max(dot(n, V), 0.0), 3.0);
    vec3 col = base * (0.38 + 0.9 * dif) + rim * 0.12 * u_hi;
    // luminous: a near-black body, a whisper of relief light, a silver silhouette rim
    vec3 lc = u_body * (0.6 + 0.8 * dif) + u_line * (0.035 * dif + 0.16 * rim);
    vec3 lline = u_line;                                // line colour (bend-tinted below)

    // bend tint: sign of the second derivative along the ray from tint_center
    if (u_tint > 0.0) {
        vec2 d = p - u_tint_center;
        float r = length(d);
        vec2 u = r > 1e-4 ? d / r : vec2(1, 0);
        float k = (height(p + u * 0.05) - 2.0 * height(p) + height(p - u * 0.05)) / 0.0025;
        vec3 tc = k > 0.0 ? u_smile : u_frown;
        float s = u_tint * smoothstep(0.0, 0.15, abs(k)) * smoothstep(0.0, 0.25, r);
        col = mix(col, tc * (0.35 + 0.65 * dif), 0.42 * s);
        lc = mix(lc, tc * (0.10 + 0.14 * dif), 0.6 * s);
        lline = mix(lline, tc, 0.85 * s);
    }

    float mask = 0.0;                                   // line coverage (for wire mode)
    // coordinate grid (rotatable)
    vec2 q = vec2(u_grid_rot.x * p.x + u_grid_rot.y * p.y, -u_grid_rot.y * p.x + u_grid_rot.x * p.y);
    vec2 gq = q / u_grid_step;
    float gx = gridline(gq.y, 1.6) * u_grid.x;         // lines of constant y (run along x)
    float gy = gridline(gq.x, 1.6) * u_grid.y;         // lines of constant x
    float g = max(gx, gy);
    col = mix(col, u_grid_col, (u_fill < 0.999 ? 1.0 : 0.55) * g);
    lc += lline * 0.7 * g;
    mask = max(mask, g);

    // contour lines
    if (u_contour > 0.0) {
        float zc = z / u_contour_step;
        float c = gridline(zc, 2.0) * u_contour;
        col = mix(col, vec3(0.80, 0.85, 0.92), 0.55 * c);
        lc += lline * 0.75 * c;
        mask = max(mask, c);
    }

    // slice cut curves (with a soft glow)
    for (int i = 0; i < 4; i++) {
        vec4 P = u_sl_plane[i];
        vec4 C = u_sl_col[i];
        if (C.a <= 0.0) continue;
        float d = dot(P.xy, p - u_center) - P.z;
        float fw = max(fwidth(d), 1e-5);
        float w = max(P.w, 1.3 * fw * u_px);
        float l = (1.0 - smoothstep(w - fw, w + fw, abs(d))) * C.a;
        float glow = exp(-d * d / (2.0 * pow(P.w * 4.0, 2.0))) * 0.45 * C.a;
        col = mix(col, C.rgb, max(l, glow * 0.6));
        lc = mix(lc, C.rgb * 1.15, l) + C.rgb * glow * 0.35;
        mask = max(mask, l);
    }

    col = mix(col, lc, u_lum);

    // fog: distance + low-lying drifting height fog
    float dist = length(u_eye - v_world);
    float f = 1.0 - exp(-u_fog * dist);
    if (u_fog_h > 0.0) {
        float nz = vnoise(p * 0.7 + vec2(u_time * 0.07, u_time * 0.03)) * 0.6
                 + vnoise(p * 1.9 - vec2(u_time * 0.05, 0.0)) * 0.4;
        f += u_fog_h * exp(-max(z - u_zlo, 0.0) * 1.4) * (0.55 + 0.45 * nz);
    }
    f = clamp(f, 0.0, 1.0);
    vec3 fogc = u_fog_col * exp(-dist * 0.035);         // far fog sinks to black
    col = mix(col, fogc, f);

    // edge fade so the finite mesh dissolves into black
    vec2 rr = abs(p - u_center) / u_R;
    float r = pow(pow(rr.x, 4.0) + pow(rr.y, 4.0), 0.25);
    float edge = 1.0 - smoothstep(u_edge, 0.98, r);
    float a = edge * max(u_fill, mask);
    frag = vec4(col * a, a);
}
"""

_FLAT_VS = """
#version 330
in vec3 in_pos;
in vec4 in_col;
uniform mat4 u_mvp;
out vec4 v_col;
void main() { v_col = in_col; gl_Position = u_mvp * vec4(in_pos, 1.0); }
"""

_FLAT_FS = """
#version 330
in vec4 v_col;
out vec4 frag;
void main() { frag = v_col; }
"""

_SKY_VS = """
#version 330
in vec2 in_pos;
out float v_y;
void main() { v_y = in_pos.y; gl_Position = vec4(in_pos, 0.9999, 1.0); }
"""

_SKY_FS = """
#version 330
in float v_y;
uniform float u_horizon, u_strength;
uniform vec3 u_col;
out vec4 frag;
void main() {
    float d = v_y - u_horizon;
    float a = u_strength * (d > 0.0 ? exp(-d * 2.6) : 0.55 + 0.45 * exp(d * 3.0));
    frag = vec4(u_col * a, a);
}
"""
