"""EpicyclePlate: a chain of rotating circles drawing glowing ink, on the GPU.

    terms = F.order_terms(F.coefficients(3.4 * treble_clef(1000), 100), keep_zero_first=False)
    t = ValueTracker(0.0)                                   # drawing time, in loops
    plate = EpicyclePlate(lambda: {"terms": terms, "t": t.get_value(), "ink_from": 0.0})
    self.add(plate, t)
    self.play(t.animate.set_value(1.0), run_time=12, rate_func=linear)
    pen = plate.project(plate.pen())                        # Manim point of the pen (for labels)

Drawing coordinates are Manim coordinates (complex x + iy): with the default
camera the plate is an exact overlay of the Manim frame. Geometry (rims, arms,
brush ink, pen, sparks) is expanded to anti-aliased quads in numpy and drawn
additively on black with 4x MSAA, then finished by the shared `GlowFinish`
(two-level bloom, vignette, grain) so it glows like every other plate.

The plate is composited *additively* (it is light on black), so Manim mobjects
under it stay visible and mobjects added after it draw on top.

Drive it only through the state callback (ValueTrackers), never by animating the
plate itself (copies would share GPU state). Keys, all optional (see DEFAULTS):

  chain   terms [(n, c)…] in drawing units · origin (complex root of the chain)
          t (loops) · frame k (turn the whole picture backward k times per loop)
  ink     ink_from (loops; None = no ink) · ink_alpha · ink_width (px at the oldest end)
          ink_head (px added at the pen) · ink_fade (oldest ink alpha, 0…1)
  parts   rim_alpha · arm_alpha · pen_alpha · sparks (0 = off, 1 = full)
          rim_tint (0 = silver rims, 1 = blue/orange/green by speed sign)
          rim_vivid (0…1: one S.RIM_HUES hue per circle, brighter big rims, tiny rims faded) · pen_glow
          rim_count (None = every rim; n = rims for the first n circles only, the rest still steer the pen)
          sweep (0…1 along the chain's length: a light pulse riding the arms; None = off)
          ink_boost (0 = normal, 1 = a bright flash along the whole ink)
  camera  cam (complex point at the plate center) · zoom · yaw, tilt (deg, 2.5D) · persp
  finish  opacity · bloom · vignette · grain

Lab notes and timings: lab/2026-11-09-epicycles/NOTES.md (about 40–50 ms per 1080p frame
with 200–500 circles on the Radeon R4).
"""

from __future__ import annotations

import hashlib
import math
from typing import Callable

import numpy as np

from aion import style as S
from manim import ORIGIN, ImageMobject, color_to_rgb, config

from .. import fourier as F
from .. import style as S
from . import blit
from .post_gl import GlowFinish
from .shader_plate import _ctx

blit.install()

_GL: dict[int, dict] = {}

DEFAULTS: dict = {
    "terms": [], "origin": 0j, "t": 0.0, "frame": 0,
    "ink_from": None, "ink_alpha": 1.0, "ink_width": 1.4, "ink_head": 4.5, "ink_fade": 0.55,
    "ink_color": S.INK, "ink_samples": 8000,
    "rim_alpha": 1.0, "arm_alpha": 1.0, "pen_alpha": 1.0, "sparks": 0.0,
    "rim_tint": 1.0, "rim_vivid": 0.0, "pen_glow": 1.0, "rim_count": None, "sweep": None, "ink_boost": 0.0,
    "cam": None, "zoom": 1.0, "yaw": 0.0, "tilt": 0.0, "persp": 9.0,
    "opacity": 1.0, "bloom": 1.0, "vignette": 0.5, "grain": 0.04,
}

_VS = """
#version 330
uniform vec2 u_res;
in vec2 in_pos; in vec4 in_col; in float in_across; in float in_soft;
out vec4 v_col; out float v_across; out float v_soft;
void main() {
    v_col = in_col; v_across = in_across; v_soft = in_soft;
    gl_Position = vec4(in_pos / u_res * 2.0 - 1.0, 0.0, 1.0);
}
"""
_FS = """
#version 330
in vec4 v_col; in float v_across; in float v_soft;
out vec4 f_col;
void main() {
    float d = abs(v_across);
    float a = mix(1.0 - smoothstep(0.55, 1.0, d), exp(-d * d * 4.0), v_soft) * v_col.a;
    f_col = vec4(v_col.rgb * a, 1.0);
}
"""

SPARK_RATE = 50_000      # sparks born per loop of drawing time
SPARK_LIFE = 0.07        # loops


def _rgb(c) -> np.ndarray:
    return np.array(color_to_rgb(c), "f4")


def strips(p: np.ndarray, width, color, alpha, soft: float = 0.0) -> np.ndarray:
    """Polyline(s) in pixels (complex, shape (m,) or (k, m)) → feathered triangle vertices.

    width and alpha broadcast to the polyline shape; color is one color or (k, 3) floats."""
    p = np.atleast_2d(np.asarray(p, complex))
    k, n = p.shape
    if n < 2 or k == 0:
        return np.zeros((0, 8), "f4")
    width = np.broadcast_to(np.asarray(width, float), (k, n))
    alpha = np.broadcast_to(np.asarray(alpha, float), (k, n))
    d = np.gradient(p, axis=1)
    d = d / np.maximum(np.abs(d), 1e-9)
    nrm = 1j * d * (width / 2 + 1.0)                       # +1 px of feather
    L, R = p + nrm, p - nrm
    arr = _rgb(color) if isinstance(color, str) else np.asarray(color, "f4")
    col = np.broadcast_to(arr if arr.ndim == 1 else arr.reshape(k, 1, 3), (k, n, 3))
    out = np.empty((k, n, 2, 8), "f4")
    out[..., 0, 0], out[..., 0, 1] = L.real, L.imag
    out[..., 1, 0], out[..., 1, 1] = R.real, R.imag
    out[..., :, 2:5] = col[:, :, None, :]
    out[..., :, 5] = alpha[..., None]
    out[..., 0, 6], out[..., 1, 6] = -1.0, 1.0
    out[..., :, 7] = soft
    VL, VR = out[:, :, 0], out[:, :, 1]
    q = np.stack([VL[:, :-1], VR[:, :-1], VL[:, 1:], VR[:, :-1], VR[:, 1:], VL[:, 1:]], 2)
    return q.reshape(-1, 8)


def glows(centers: np.ndarray, radius, color, alpha) -> np.ndarray:
    """Soft gaussian dots (one quad each), vectorized."""
    c = np.atleast_1d(np.asarray(centers, complex))
    m = len(c)
    if m == 0:
        return np.zeros((0, 8), "f4")
    r = np.broadcast_to(np.asarray(radius, float), (m,))
    a = np.broadcast_to(np.asarray(alpha, float), (m,))
    col = np.asarray(color, "f4") if not isinstance(color, str) else _rgb(color)
    col = np.broadcast_to(col.reshape(-1, 3) if col.ndim == 2 else col, (m, 3))
    corners = np.array([-1 - 1j, 1 - 1j, -1 + 1j, 1 - 1j, 1 + 1j, -1 + 1j])
    pos = c[:, None] + r[:, None] * corners[None, :]
    out = np.empty((m, 6, 8), "f4")
    out[..., 0], out[..., 1] = pos.real, pos.imag
    out[..., 2:5] = col[:, None, :]
    out[..., 5] = a[:, None]
    out[..., 6] = np.abs(corners)[None, :] / math.sqrt(2) * 1.6
    out[..., 7] = 1.0
    return out.reshape(-1, 8)


def _hash01(i: np.ndarray, salt: float) -> np.ndarray:
    """Deterministic per-index noise in [0, 1) (no RNG state: any frame renders alone)."""
    x = np.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - np.floor(x)


class EpicyclePlate(ImageMobject):
    """An epicycle chain as an ImageMobject of size `width` × `height` (Manim units) at `center`."""

    def __init__(self, state: Callable[[], dict], *, width: float | None = None,
                 height: float | None = None, center=ORIGIN, samples: int = 4, scale: float = 1.0, **kw):
        width = width or config.frame_width
        height = height or config.frame_height
        ppu = config.pixel_width / config.frame_width * scale
        w, h = max(2, int(round(width * ppu))), max(2, int(round(height * ppu)))
        ctx = _ctx()
        prog = ctx.program(vertex_shader=_VS, fragment_shader=_FS)
        prog["u_res"].value = (float(w), float(h))
        vbo = ctx.buffer(reserve=4 * 8 * 6 * 100_000, dynamic=True)
        vao = ctx.vertex_array(prog, [(vbo, "2f 4f 1f 1f", "in_pos", "in_col", "in_across", "in_soft")])
        samples = min(samples, ctx.max_samples)
        ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)])
        out = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])
        super().__init__(np.zeros((h, w, 4), dtype=np.uint8), **kw)
        self._gl_key = id(self)
        _GL[self._gl_key] = dict(prog=prog, vbo=vbo, vao=vao, ms=ms, out=out, size=(w, h),
                                 glow=GlowFinish((w, h)), state=state, ink=(None, None))
        self.plate_w, self.plate_h = width, height
        self.plate_c = np.array(center, float)
        self.ppu = ppu
        self.k = config.pixel_height / 1080.0                    # stroke widths are 1080p px
        self.stretch_to_fit_width(width)
        self.stretch_to_fit_height(height)
        self.move_to(center)
        self._fast_blit = True
        self._blit_add = True
        self._circle = np.exp(2j * np.pi * np.linspace(0, 1, 97))
        self.render_gl()
        self.add_updater(lambda m, dt: m.render_gl())        # dt: keeps wait() rendering every frame

    # ── state & geometry (Python side, usable by overlays) ─────────────────
    def state(self) -> dict:
        s = {**DEFAULTS, **_GL[self._gl_key]["state"]()}
        s["terms"] = list(s["terms"])
        if s["cam"] is None:
            s["cam"] = complex(self.plate_c[0], self.plate_c[1])
        return s

    def joints(self, s: dict | None = None) -> np.ndarray:
        """Every arm joint in drawing coordinates at the state's t (joints[-1] = the pen)."""
        s = self.state() if s is None else {**DEFAULTS, **s}
        return s["origin"] + F.chain_points(s["terms"], s["t"], frame=s["frame"])

    def pen(self, s: dict | None = None) -> complex:
        return complex(self.joints(s)[-1])

    def _view(self, z, s):
        """Drawing coords → (screen-relative units, perspective scale). Yaw, tilt, perspective."""
        d = (np.asarray(z, complex) - s["cam"]) * np.exp(-1j * math.radians(s["yaw"]))
        x, y = d.real, d.imag
        tl = math.radians(s["tilt"])
        yv, depth = y * math.cos(tl), y * math.sin(tl)        # tilt the plane away from the viewer
        k = s["persp"] / (s["persp"] + depth) if s["tilt"] else 1.0
        return (x + 1j * yv) * k * s["zoom"], k

    def _px(self, z, s):
        w, h = _GL[self._gl_key]["size"]
        v, _ = self._view(z, s)
        return v * self.ppu + (w / 2 + 1j * h / 2)

    def project(self, z, s: dict | None = None) -> np.ndarray:
        """Drawing point (complex) → Manim point on this plate (pins labels to the GL geometry)."""
        s = s or self.state()
        v, _ = self._view(z, s)
        return self.plate_c + np.array([v.real, v.imag, 0.0])

    # ── ink ───────────────────────────────────────────────────────────────
    def _path(self, s):
        """The whole drawing at ink_samples per loop, cached per (terms, frame)."""
        gl = _GL[self._gl_key]
        n = np.array([n for n, _ in s["terms"]], float)
        c = np.array([c for _, c in s["terms"]], complex)
        key = hashlib.sha1(n.tobytes() + c.tobytes() + bytes([s["frame"] % 256])
                           + int(s["ink_samples"]).to_bytes(4, "little")).hexdigest()
        if gl["ink"][0] != key:
            gl["ink"] = (key, self._sum(n - s["frame"], c, np.arange(s["ink_samples"]) / s["ink_samples"]))
        return gl["ink"][1]

    @staticmethod
    def _sum(n, c, t):
        z = np.zeros(len(t), complex)
        for i in range(0, len(n), 64):                         # chunked: memory stays small
            z += c[i:i + 64] @ np.exp(2j * np.pi * np.outer(n[i:i + 64], t))
        return z

    def _ink(self, s):
        """(points in drawing coords, age 0 at the pen … 1 oldest) from ink_from to t."""
        t0, t1 = s["ink_from"], s["t"]
        span = t1 - t0
        if span <= 0 or not s["terms"]:
            return np.zeros(0, complex), np.zeros(0)
        path, M = self._path(s), s["ink_samples"]
        i0, i1 = math.ceil(t0 * M), math.floor(t1 * M)
        idx = np.arange(i0, i1 + 1)
        z = path[idx % M] if len(idx) else np.zeros(0, complex)
        tt = idx / M
        if s["zoom"] > 3:                                      # zoomed: fresh, fine samples near the pen
            fine_span = min(span, 4.0 / (s["zoom"] * 8))
            n = np.array([n for n, _ in s["terms"]], float) - s["frame"]
            c = np.array([c for _, c in s["terms"]], complex)
            tf = np.linspace(t1 - fine_span, t1, 1200)
            keep = tt < tf[0]
            z, tt = np.concatenate([z[keep], self._sum(n, c, tf)]), np.concatenate([tt[keep], tf])
        else:                                                  # end exactly on the pen
            z = np.append(z, self.pen(s) - s["origin"])
            tt = np.append(tt, t1)
        z = z + s["origin"]
        age = (t1 - tt) / max(min(span, 1.0), 1e-9)
        return z, np.clip(age, 0, 1)

    # ── render ────────────────────────────────────────────────────────────
    def geometry(self, s: dict) -> np.ndarray:
        parts = []
        terms = s["terms"]
        jz = self.joints(s)
        jp = self._px(jz, s)
        scale = self.ppu * s["zoom"]
        sweep_boost = np.ones(max(len(terms), 1))
        if terms and s["sweep"] is not None:
            seg = np.abs(np.diff(jz))
            frac = (np.cumsum(seg) - seg / 2) / max(seg.sum(), 1e-9)
            sweep_boost = 1 + 2.5 * np.exp(-((frac - s["sweep"]) / 0.07) ** 2)
        if terms and s["rim_alpha"] > 0:
            radii = np.abs(np.array([c for _, c in terms])) * scale
            vis = np.flatnonzero(radii >= 1.5 * self.k)
            if s["rim_count"] is not None:             # only the first rim_count circles (chain order) get rims
                vis = vis[vis < int(s["rim_count"])]
            if len(vis):
                rings_z = jz[vis, None] + (radii[vis, None] / scale) * self._circle[None, :]
                rings = self._px(rings_z, s)
                sign = np.array([terms[i][0] for i in vis]) - s["frame"]
                tinted = np.where((sign > 0)[:, None], _rgb(S.FWD),
                                  np.where((sign < 0)[:, None], _rgb(S.BWD), _rgb(S.STILL)))
                cols = _rgb(S.ARM) + (tinted - _rgb(S.ARM)) * float(np.clip(s["rim_tint"], 0, 1))
                a = s["rim_alpha"] * S.RIM_OPACITY * np.minimum(1.0, radii[vis] / (6 * self.k))
                v = float(np.clip(s["rim_vivid"], 0, 1))
                if v > 0:                          # one distinct hue per circle; tiny rims fade (no glow pile-up)
                    hues = np.array([_rgb(c) for c in S.RIM_HUES])[vis % len(S.RIM_HUES)]
                    cols = cols + (hues - cols) * v
                    fade = np.clip(radii[vis] / (S.RIM_FADE_PX * self.k), 0, 1) ** 2
                    a = a + (s["rim_alpha"] * S.RIM_VIVID_OPACITY * fade - a) * v
                a = a * sweep_boost[vis]
                parts.append(strips(rings, 1.1 * self.k, cols.astype("f4"), a[:, None]))
        if len(jp) > 1 and s["arm_alpha"] > 0:
            arm_px = np.abs(np.diff(jp))
            short = 24 + 16 * float(np.clip(s["rim_vivid"], 0, 1))     # vivid: short arms fade sooner (crisp pen)
            a = s["arm_alpha"] * 0.75 * np.clip(arm_px / (short * self.k), 0, 1) ** 2 * sweep_boost[:len(arm_px)]
            arms = np.stack([jp[:-1], jp[1:]], 1)
            parts.append(strips(arms, 1.4 * self.k, np.broadcast_to(_rgb(S.ARM), (len(arms), 3)), a[:, None]))
        if s["ink_from"] is not None and s["ink_alpha"] > 0:
            z, age = self._ink(s)
            if len(z) > 1:
                ip = self._px(z, s)
                fresh = 1 - age
                ia = s["ink_alpha"] * (1 + 1.5 * s["ink_boost"])
                parts.append(strips(ip, self.k * (s["ink_width"] + s["ink_head"] * fresh ** 3), s["ink_color"],
                                    ia * (s["ink_fade"] + (1 - s["ink_fade"]) * fresh)))
                parts.append(strips(ip, self.k * 10 * fresh ** 6, s["ink_color"], ia * 0.25 * fresh ** 6, soft=1.0))
                if s["ink_boost"] > 0:
                    parts.append(strips(ip, self.k * 9, s["ink_color"], 0.22 * s["ink_boost"], soft=1.0))
        if s["sparks"] > 0 and s["ink_from"] is not None:
            parts.append(self._sparks(s))
        if terms and s["pen_alpha"] > 0:
            g = s["pen_glow"]
            parts.append(glows(jp[-1:], (3 + 4 * g) * self.k, s["ink_color"], (0.45 + 0.35 * g) * s["pen_alpha"]))
            parts.append(glows(jp[-1:], 2.5 * self.k, S.LIGHT, s["pen_alpha"]))
        return np.concatenate(parts) if parts else np.zeros((0, 8), "f4")

    def _sparks(self, s) -> np.ndarray:
        """Stateless sparks: born along the ink at fixed drawing times, so any frame renders alone."""
        t1 = s["t"]
        lo = max(s["ink_from"], t1 - SPARK_LIFE)
        i = np.arange(math.ceil(lo * SPARK_RATE), math.floor(t1 * SPARK_RATE) + 1)
        if len(i) == 0:
            return np.zeros((0, 8), "f4")
        tb = i / SPARK_RATE
        path, M = self._path(s), s["ink_samples"]
        born = path[np.round(tb * M).astype(int) % M] + s["origin"]
        a = np.clip((t1 - tb) / SPARK_LIFE, 0, 1)               # 0 newborn … 1 gone
        ang = 2 * np.pi * _hash01(i, 1.0)
        spd = 0.25 + 0.75 * _hash01(i, 2.0)
        drift = 0.35 * spd * (1 - np.exp(-3 * a)) * np.exp(1j * ang)
        swirl = 0.12 * a * a * np.exp(1j * (2.3 * born.real + 1.7 * born.imag + 4 * a))
        z = born + (drift + swirl) * (0.6 + 0.4 / max(s["zoom"], 1))
        heat = 1 - a
        col = np.stack([np.ones_like(heat), 0.55 + 0.33 * heat, 0.12 + 0.2 * heat], 1).astype("f4")
        alpha = s["sparks"] * 0.55 * heat ** 1.6 * (0.4 + 0.6 * _hash01(i, 3.0))
        return glows(self._px(z, s), self.k * (1.6 + 1.2 * heat), col, alpha)

    def render_gl(self) -> "EpicyclePlate":
        gl = _GL[self._gl_key]
        ctx = _ctx()
        s = self.state()
        w, h = gl["size"]
        verts = self.geometry(s).astype("f4", copy=False)
        data = verts.tobytes()
        if len(data) > gl["vbo"].size:
            gl["vbo"].orphan(len(data))
        if data:
            gl["vbo"].write(data)
        gl["ms"].use()
        ctx.viewport = (0, 0, w, h)
        gl["ms"].clear(0, 0, 0, 1)
        ctx.enable(ctx.BLEND)
        ctx.blend_func = ctx.ONE, ctx.ONE
        if len(verts):
            gl["vao"].render(vertices=len(verts))
        ctx.disable(ctx.BLEND)
        gl["glow"].apply(gl["ms"], gl["out"], bloom=s["bloom"] * S.GL_BLOOM_SCALE, vignette=min(s["vignette"], S.GL_VIGNETTE_MAX),
                         grain=min(s["grain"], S.GL_GRAIN_MAX),
                         seed=(s["t"] * 997.0) % 991.0)
        ctx.viewport = (0, 0, w, h)
        img = np.frombuffer(gl["out"].read(components=4), np.uint8).reshape(h, w, 4)[::-1]
        op = float(np.clip(s["opacity"], 0, 1))
        arr = np.empty((h, w, 4), np.uint8)
        arr[..., :3] = img[..., :3] if op >= 0.999 else (img[..., :3] * op).astype(np.uint8)
        arr[..., 3] = 255
        self.pixel_array = np.ascontiguousarray(arr)
        return self
