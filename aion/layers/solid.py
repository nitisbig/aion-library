"""Solid colors and gradients (full-frame, GPU)."""

from __future__ import annotations

from aion.comp.comp import hex_to_linear
from aion.core.track import track
from aion.gpu import pool
from aion.gpu.program import fullscreen, program, set_uniforms
from aion.layers.base import ENC_LINEAR, Layer, RenderContext, Surface

__all__ = ["Solid", "Gradient"]

_GRAD = """
#include "common/color.glsl"
uniform vec3 u_a; uniform vec3 u_b; uniform vec2 u_center; uniform float u_radius;
uniform vec2 u_dir; uniform int u_radial; uniform float u_alpha;
in vec2 v_uv; in vec2 v_pos; out vec4 frag;
void main() {
    float k = u_radial == 1 ? clamp(length(v_pos - u_center) / u_radius, 0.0, 1.0)
                            : clamp(dot(v_pos - u_center, u_dir) / u_radius * 0.5 + 0.5, 0.0, 1.0);
    k = k * k * (3.0 - 2.0 * k);
    frag = vec4(mix(u_a, u_b, k) * u_alpha, u_alpha);
}
"""


class _Full(Layer):
    vector = True

    def _target(self, rc: RenderContext):
        if getattr(self, "_rt", None) is None or self._rt.size != rc.size:
            self._rt = pool.target(rc.size, "f2", pooled=False)
        return self._rt


class Solid(_Full):
    """Flat color filling the frame (linear-light compositing of an sRGB color).

    Example:
        Solid("#101418", z=-100)
    """

    def __init__(self, color="#000000", **kw):
        super().__init__(parallax=0.0, **kw)
        self.color = track(color)

    def tracks(self):
        return super().tracks() + [self.color]

    def content_changes(self, t0, t1):
        return self.color.changes(t0, t1)

    def draw(self, t, rc):
        rt = self._target(rc)
        rt.use(clear=(*hex_to_linear(self.color(t)), 1.0))
        return Surface(rt.tex, ENC_LINEAR, None)


class Gradient(_Full):
    """Linear or radial gradient between two sRGB colors (world space, Manim units).

    Example:
        Gradient("#16202a", "#07090c", radial=True, radius=9, z=-100)
    """

    def __init__(self, a="#1a2330", b="#06080b", radial: bool = True, center=(0.0, 0.0), radius: float = 8.0,
                 direction=(0.0, 1.0), alpha: float = 1.0, **kw):
        kw.setdefault("parallax", 0.3)
        super().__init__(**kw)
        self.a, self.b, self.radial, self.center = a, b, radial, center
        self.radius, self.direction, self.alpha = radius, direction, alpha

    def draw(self, t, rc):
        import numpy as np

        rt = self._target(rc)
        prog = program(_GRAD)
        set_uniforms(prog, u_a=hex_to_linear(self.a), u_b=hex_to_linear(self.b), u_center=self.center,
                     u_radius=self.radius, u_dir=self.direction, u_radial=int(self.radial), u_alpha=self.alpha,
                     u_frame=rc.frame_units, u_view_inv=np.linalg.inv(rc.view(self.parallax)))
        rt.use()
        fullscreen(prog).render(vertices=3)
        return Surface(rt.tex, ENC_LINEAR, None)
