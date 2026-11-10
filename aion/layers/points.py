"""GPU layers for data: point clouds / particles and scalar fields (sim output, heatmaps).

    cache = bake(Particles(n=30000), s.start, s.end)
    s.add(PointsLayer(lambda t: cache.at(t)["pos"], color=C.accent, size=2.5, glow=0.6))
    s.add(PointsLayer(lambda t: bodies.at(t)["pos"], values=lambda t: speed(t), cmap="inferno"))

    w = bake(Wave2D(drops=[(0.2, .5, .5, 1)]), s.start, s.end)
    s.add(FieldLayer(lambda t: w.at(t)["h"], cmap="diverging", vmin=-0.3, vmax=0.3, extent=(14.2, 8)))

Both draw in world (Manim) units through the comp camera, so Manim overlays line up.
"""

from __future__ import annotations

import math
from typing import Callable

import numpy as np

from aion.comp.comp import hex_to_linear
from aion.core.track import track
from aion.gpu import pool
from aion.gpu.context import gl
from aion.gpu.program import fullscreen, program, set_uniforms
from aion.layers.base import ENC_LINEAR, Layer, RenderContext, Surface

__all__ = ["PointsLayer", "FieldLayer", "CMAPS"]

CMAPS = {"inferno": 0, "diverging": 1, "ramp": 2, "viridis": 3}

_CMAP_GLSL = """
vec3 cmap(float x, int id, vec3 c0, vec3 c1, vec3 c2) {
    x = clamp(x, 0.0, 1.0);
    if (id == 0) {   // inferno-like (polynomial fit, linear-ish output)
        vec3 c = vec3(0.0002, 0.0016, -0.0194) + x * (vec3(0.1065, 0.5639, 3.9327) + x * (vec3(11.6024, -3.9728, -15.9423)
               + x * (vec3(-41.7040, 17.4364, 44.3541) + x * (vec3(77.1629, -33.4023, -81.8073)
               + x * (vec3(-71.3194, 32.6261, 73.2095) + x * vec3(25.1311, -12.2426, -23.0703))))));
        return pow(clamp(c, 0.0, 1.0), vec3(2.2));
    }
    if (id == 1) return x < 0.5 ? mix(c0, c1, x * 2.0) : mix(c1, c2, x * 2.0 - 1.0);
    if (id == 3) {
        vec3 c = vec3(0.2777, 0.0054, 0.3341) + x * (vec3(0.1050, 1.4046, 1.3846) + x * (vec3(-0.3309, 0.2148, 0.0951)
               + x * (vec3(-4.6342, -5.7991, -19.3324) + x * (vec3(6.2283, 14.1799, 56.6906)
               + x * (vec3(4.7764, -13.7451, -65.3530) + x * vec3(-5.4355, 4.6459, 26.3124))))));
        return pow(clamp(c, 0.0, 1.0), vec3(2.2));
    }
    return mix(c0, c2, x);
}
"""

_PT_VERT = """
#version 330
in vec2 in_pos; in float in_val;
uniform mat3 u_view; uniform vec2 u_frame; uniform float u_size; uniform float u_vmin; uniform float u_vmax;
out float v_val;
void main() {
    vec3 s = u_view * vec3(in_pos, 1.0);
    gl_Position = vec4(s.xy / (u_frame * 0.5), 0.0, 1.0);
    gl_PointSize = u_size;
    v_val = (in_val - u_vmin) / max(u_vmax - u_vmin, 1e-9);
}
"""

_PT_FRAG = """
#version 330
""" + _CMAP_GLSL + """
uniform vec3 u_color; uniform int u_cmap; uniform vec3 u_c0; uniform vec3 u_c1; uniform vec3 u_c2;
uniform float u_glow; uniform float u_alpha;
in float v_val; out vec4 frag;
void main() {
    vec2 d = gl_PointCoord * 2.0 - 1.0;
    float r2 = dot(d, d);
    if (r2 > 1.0) discard;
    float core = smoothstep(1.0, 0.55, r2);
    float halo = exp(-r2 * 3.0) * u_glow;
    float a = clamp(core + halo, 0.0, 1.0) * u_alpha;
    vec3 c = u_cmap >= 0 ? cmap(v_val, u_cmap, u_c0, u_c1, u_c2) : u_color;
    frag = vec4(c * a, a);
}
"""

_FIELD_FRAG = """
""" + _CMAP_GLSL + """
uniform sampler2D u_field; uniform vec2 u_center; uniform vec2 u_extent; uniform float u_vmin; uniform float u_vmax;
uniform int u_cmap; uniform vec3 u_c0; uniform vec3 u_c1; uniform vec3 u_c2; uniform float u_alpha;
uniform float u_contours;
in vec2 v_pos; out vec4 frag;
void main() {
    vec2 uv = (v_pos - u_center) / u_extent + 0.5;
    if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) { frag = vec4(0.0); return; }
    float v = (texture(u_field, uv).r - u_vmin) / max(u_vmax - u_vmin, 1e-9);
    vec3 c = cmap(v, u_cmap, u_c0, u_c1, u_c2);
    if (u_contours > 0.0) {
        float f = fract(v * u_contours);
        float w = fwidth(v * u_contours);
        c *= 1.0 - 0.35 * (1.0 - smoothstep(0.0, w * 1.5, min(f, 1.0 - f)));
    }
    frag = vec4(c * u_alpha, u_alpha);
}
"""


def _cm(cmap, colors):
    c = [hex_to_linear(x) for x in colors]
    return CMAPS.get(cmap, -1) if cmap else -1, c


class PointsLayer(Layer):
    """Point sprites at world positions from `positions(t)` → (N, 2|3) array.

    Example:
        PointsLayer(lambda t: cache.at(t)["pos"], color=C.accent, size=3, glow=0.5)
    """

    vector = True

    def __init__(self, positions: Callable[[float], np.ndarray], values: Callable | None = None, color="#58c4dd",
                 size: float = 3.0, glow: float = 0.4, alpha=1.0, cmap: str | None = None, vmin: float = 0.0,
                 vmax: float = 1.0, colors=("#2b6cb0", "#e6edf3", "#ff7a59"), additive: bool = True,
                 animated: bool = True, **kw):
        kw.setdefault("blend", "add" if additive else "normal")
        super().__init__(**kw)
        self.positions, self.values = positions, values
        self.color, self.size, self.glow = hex_to_linear(color), size, glow
        self.alpha = track(alpha)
        self.cmap_id, self.cols = _cm(cmap if values is not None else None, colors)
        self.vmin, self.vmax = vmin, vmax
        self.animated = animated
        self._rt = self._vbo = self._vao = None
        self._n = 0

    def content_changes(self, t0, t1):
        return self.animated or self.alpha.changes(t0, t1)

    def draw(self, t: float, rc: RenderContext) -> Surface:
        import moderngl

        ctx = gl()
        if self._rt is None or self._rt.size != rc.size:
            self._rt = pool.target(rc.size, "f2", pooled=False)
        p = np.asarray(self.positions(t), np.float32)[:, :2]
        v = np.asarray(self.values(t), np.float32).reshape(-1) if self.values else np.zeros(len(p), np.float32)
        data = np.empty((len(p), 3), np.float32)
        data[:, :2], data[:, 2] = p, v
        prog = program(_PT_FRAG, _PT_VERT)
        if self._vbo is None or len(p) != self._n:
            self._vbo = ctx.buffer(reserve=max(12, data.nbytes))
            self._vao = ctx.vertex_array(prog, [(self._vbo, "2f 1f", "in_pos", "in_val")])
            self._n = len(p)
        self._vbo.write(data.tobytes())
        scale = rc.size[1] / 1080.0
        set_uniforms(prog, u_view=rc.view(self.parallax), u_frame=rc.frame_units, u_size=self.size * scale * 2,
                     u_vmin=self.vmin, u_vmax=self.vmax, u_color=self.color, u_cmap=self.cmap_id,
                     u_c0=self.cols[0], u_c1=self.cols[1], u_c2=self.cols[2], u_glow=self.glow,
                     u_alpha=float(self.alpha(t)))
        self._rt.use()
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        self._vao.render(moderngl.POINTS, vertices=len(p))
        ctx.disable(moderngl.BLEND)
        return Surface(self._rt.tex, ENC_LINEAR, None)


class FieldLayer(Layer):
    """A scalar field `field(t)` → (ny, nx) array (row 0 = bottom) shown with a colormap.

    Example:
        FieldLayer(lambda t: w.at(t)["h"], cmap="diverging", vmin=-.3, vmax=.3, contours=12)
    """

    vector = True

    def __init__(self, field: Callable[[float], np.ndarray], cmap: str = "inferno", vmin: float = 0.0,
                 vmax: float = 1.0, extent=(14.222, 8.0), center=(0.0, 0.0), colors=("#2b6cb0", "#0d1117", "#ff7a59"),
                 alpha=1.0, contours: float = 0.0, animated: bool = True, **kw):
        super().__init__(**kw)
        self.field, self.vmin, self.vmax = field, vmin, vmax
        self.cmap_id, self.cols = _cm(cmap, colors)
        self.extent, self.center = extent, center
        self.alpha, self.contours, self.animated = track(alpha), contours, animated
        self._rt = self._tex = None

    def content_changes(self, t0, t1):
        return self.animated or self.alpha.changes(t0, t1)

    def draw(self, t, rc):
        import moderngl

        a = np.ascontiguousarray(self.field(t), np.float32)
        h, w = a.shape
        if self._tex is None or self._tex.size != (w, h):
            self._tex = gl().texture((w, h), 1, dtype="f4")
            self._tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self._tex.repeat_x = self._tex.repeat_y = False
        self._tex.write(a.tobytes())
        if self._rt is None or self._rt.size != rc.size:
            self._rt = pool.target(rc.size, "f2", pooled=False)
        prog = program(_FIELD_FRAG)
        view = rc.view(self.parallax)
        set_uniforms(prog, u_field=(self._tex, 0), u_center=self.center, u_extent=self.extent, u_vmin=self.vmin,
                     u_vmax=self.vmax, u_cmap=self.cmap_id, u_c0=self.cols[0], u_c1=self.cols[1],
                     u_c2=self.cols[2], u_alpha=float(self.alpha(t)), u_contours=self.contours,
                     u_frame=rc.frame_units, u_view_inv=np.linalg.inv(view))
        self._rt.use()
        fullscreen(prog).render(vertices=3)
        return Surface(self._rt.tex, ENC_LINEAR, None)
