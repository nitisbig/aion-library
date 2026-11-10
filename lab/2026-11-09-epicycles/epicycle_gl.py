"""Lab prototype of EpicyclePlate: an epicycle chain + glowing ink on the GPU.

Geometry (rims, arms, ink ribbon, pen) is expanded to anti-aliased quads in numpy
each frame and drawn additively on black into a 4× MSAA buffer, then finished by
the shared `post_gl.GlowFinish` (bloom, vignette, grain), like every other plate.

    r = EpicycleRenderer((854, 480))
    rgba = r.render(terms, t=0.37, ink="hairline", camera=(0+0j, 1.0))
"""

from __future__ import annotations

import numpy as np
from manim import color_to_rgb

from aion import fourier as F
from aion import style as S
from aion.components.post_gl import GlowFinish
from aion.components.shader_plate import _ctx

VS = """
#version 330
uniform vec2 u_res;
in vec2 in_pos;      // pixels
in vec4 in_col;      // premultiplied rgb, a = intensity
in float in_across;  // −1 … 1 across the stroke (feathered edge)
in float in_soft;    // 0 = crisp line, 1 = gaussian glow
out vec4 v_col; out float v_across; out float v_soft;
void main() {
    v_col = in_col; v_across = in_across; v_soft = in_soft;
    gl_Position = vec4(in_pos / u_res * 2.0 - 1.0, 0.0, 1.0);
}
"""
FS = """
#version 330
in vec4 v_col; in float v_across; in float v_soft;
out vec4 f_col;
void main() {
    float d = abs(v_across);
    float crisp = 1.0 - smoothstep(0.55, 1.0, d);
    float glow = exp(-d * d * 4.0);
    float a = mix(crisp, glow, v_soft) * v_col.a;
    f_col = vec4(v_col.rgb * a, 1.0);
}
"""


def _rgb(c):
    return np.array(color_to_rgb(c), "f4")


def strip_quads(p: np.ndarray, width, color, alpha, soft=0.0):
    """Polyline(s) (pixels, complex; shape (m,) or (k, m)) → triangle vertices.

    width / alpha broadcast to the polyline shape; color is one color or (k, 3).
    Vectorized over all k strips at once (hundreds of rims cost one numpy pass)."""
    p = np.atleast_2d(np.asarray(p, complex))
    k, n = p.shape
    if n < 2 or k == 0:
        return np.zeros((0, 8), "f4")
    width = np.broadcast_to(np.asarray(width, float), (k, n)) if np.ndim(width) < 2 else width
    alpha = np.broadcast_to(np.asarray(alpha, float), (k, n)) if np.ndim(alpha) < 2 else alpha
    width = np.broadcast_to(width, (k, n)); alpha = np.broadcast_to(alpha, (k, n))
    d = np.gradient(p, axis=1)
    d = d / np.maximum(np.abs(d), 1e-9)
    nrm = 1j * d * (width / 2 + 1.0)                    # +1 px for the feather
    L, R = p + nrm, p - nrm
    if isinstance(color, str):
        col = np.broadcast_to(_rgb(color), (k, n, 3))
    else:                                               # (k, 3): one color per strip
        col = np.broadcast_to(np.asarray(color, "f4").reshape(k, 1, 3), (k, n, 3))
    out = np.empty((k, n, 2, 8), "f4")
    out[..., 0, 0], out[..., 0, 1] = L.real, L.imag
    out[..., 1, 0], out[..., 1, 1] = R.real, R.imag
    out[..., :, 2:5] = col[:, :, None, :]
    out[..., :, 5] = alpha[..., None]
    out[..., 0, 6], out[..., 1, 6] = -1.0, 1.0
    out[..., :, 7] = soft
    VL, VR = out[:, :, 0], out[:, :, 1]
    quads = np.stack([VL[:, :-1], VR[:, :-1], VL[:, 1:], VR[:, :-1], VR[:, 1:], VL[:, 1:]], 2)
    return quads.reshape(-1, 8)


def disc(center: complex, radius: float, color, alpha=1.0):
    """A soft glowing dot as a gaussian quad."""
    c = center
    corners = [c + radius * (x + 1j * y) for x, y in ((-1, -1), (1, -1), (-1, 1), (1, 1))]
    col = _rgb(color)
    # across coordinate = distance from center (radial); use two triangles with in_across = r
    out = []
    for q, (x, y) in zip(corners, ((-1, -1), (1, -1), (-1, 1), (1, 1))):
        out.append([q.real, q.imag, *col, alpha, np.hypot(x, y) / np.sqrt(2) * 1.6, 1.0])
    a, b, c_, d = out
    return np.array([a, b, c_, b, d, c_], "f4")


class EpicycleRenderer:
    def __init__(self, size=(854, 480), samples=4, units_per_frame=8.0):
        ctx = self.ctx = _ctx()
        self.size = w, h = size
        self.ppu = h / units_per_frame                      # pixels per drawing unit
        self.prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.vbo = ctx.buffer(reserve=4 * 8 * 6 * 200_000, dynamic=True)
        self.vao = ctx.vertex_array(self.prog, [(self.vbo, "2f 4f 1f 1f", "in_pos", "in_col", "in_across", "in_soft")])
        samples = min(samples, ctx.max_samples)
        self.ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)])
        self.out = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])
        self.finish = GlowFinish((w, h))
        self.prog["u_res"].value = (float(w), float(h))
        self._circle = np.exp(2j * np.pi * np.linspace(0, 1, 97))

    def to_px(self, z, cam):
        center, zoom = cam
        w, h = self.size
        return (np.asarray(z) - center) * self.ppu * zoom + (w / 2 + 1j * h / 2)

    def ink_path(self, terms, samples_per_loop=8000):
        """The whole drawing sampled once per term set (cached): slicing it per frame is free."""
        key = (id(terms), len(terms), samples_per_loop)
        if getattr(self, "_ink_key", None) != key:
            n = np.array([n for n, _ in terms]); c = np.array([c for _, c in terms])
            s = np.arange(samples_per_loop) / samples_per_loop
            z = np.zeros(samples_per_loop, complex)
            for i in range(0, len(n), 64):                  # chunked matrix product
                z += c[i:i + 64] @ np.exp(2j * np.pi * np.outer(n[i:i + 64], s))
            self._ink_key, self._ink = key, z
        return self._ink

    def geometry(self, terms, t, ink="hairline", camera=(0j, 1.0), ink_span=1.0, ink_samples=None):
        cam = camera
        joints = F.chain_points(terms, t)
        jp = self.to_px(joints, cam)
        parts = []
        radii = np.abs(np.array([c for _, c in terms]))
        rim_px = radii * self.ppu * cam[1]
        vis = np.flatnonzero(rim_px >= 1.5)
        if len(vis):
            rings = jp[vis, None] + rim_px[vis, None] * self._circle[None, :]
            sign = np.array([terms[i][0] for i in vis])
            cols = np.where((sign > 0)[:, None], _rgb(S.FWD), np.where((sign < 0)[:, None], _rgb(S.BWD), _rgb(S.STILL)))
            a = (S.RIM_OPACITY * np.minimum(1.0, rim_px[vis] / 6))[:, None]
            parts.append(strip_quads(rings, 1.1, cols.astype("f4"), a))
        # arms: tiny arms fade out, so 200 overlapping joints near the pen don't bloom into a blob
        arm_px = np.abs(np.diff(jp))
        arm_a = 0.75 * np.clip(arm_px / 24, 0, 1) ** 1.5
        arms = np.stack([jp[:-1], jp[1:]], 1)               # one 2-point strip per arm
        parts.append(strip_quads(arms, 1.4, np.broadcast_to(_rgb(S.ARM), (len(arms), 3)), arm_a[:, None]))
        path = self.ink_path(terms)
        L = len(path)
        i1 = int(round(t * L)); i0 = i1 - max(2, int(ink_span * L))
        idx = np.arange(i0, i1 + 1) % L
        ip = self.to_px(path[idx], cam)
        ip[-1] = jp[-1]                                     # ink ends exactly on the pen
        age = np.linspace(1, 0, len(ip))
        if ink == "hairline":
            parts.append(strip_quads(ip, 2.2, S.INK, 0.35 + 0.65 * (1 - age) ** 2))
        elif ink == "brush":
            parts.append(strip_quads(ip, 0.8 + 4.5 * (1 - age) ** 3, S.INK, 0.25 + 0.75 * (1 - age)))
            parts.append(strip_quads(ip, 10 * (1 - age) ** 6, S.INK, 0.25 * (1 - age) ** 6, soft=1.0))
        elif ink == "comet":
            dash = ((np.arange(len(ip)) // 12) % 2 == 0) | (age < 0.08)   # dotted, solid near the pen
            parts.append(strip_quads(ip, 2.0, S.INK, dash * (0.3 + 0.7 * (1 - age) ** 2)))
            head = age < 0.08
            parts.append(strip_quads(ip[head], 14 * (1 - age[head] / 0.08), S.INK, 0.35 * (1 - age[head] / 0.08), soft=1.0))
        parts.append(disc(jp[-1], 7, S.INK, 0.8))
        parts.append(disc(jp[-1], 2.5, S.LIGHT, 1.0))
        return np.concatenate(parts)

    def render(self, terms, t, ink="hairline", camera=(0j, 1.0), **kw) -> np.ndarray:
        ctx = self.ctx
        verts = self.geometry(terms, t, ink, camera, **kw)
        data = verts.tobytes()
        if len(data) > self.vbo.size:
            self.vbo.orphan(len(data))
        self.vbo.write(data)
        self.ms.use()
        ctx.viewport = (0, 0, *self.size)
        self.ms.clear(0, 0, 0, 1)
        ctx.enable(ctx.BLEND)
        ctx.blend_func = ctx.ONE, ctx.ONE
        self.vao.render(vertices=len(verts))
        ctx.disable(ctx.BLEND)
        self.finish.apply(self.ms, self.out, bloom=1.0, vignette=0.5, grain=0.04, seed=t * 100)
        w, h = self.size
        return np.frombuffer(self.out.read(components=4), np.uint8).reshape(h, w, 4)[::-1]
