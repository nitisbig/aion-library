"""ShaderLayer: a fragment shader as a full-frame layer, uniforms driven by Tracks.

    s.shader("layers/domain_coloring.frag", z=-1,
             u_theta=key(T.turn, 0.0, PI / 2), u_sat=0.8, u_opacity=fade(T.field))

Shader contract (see docs/layers.md):
    in vec2 v_uv;    // 0..1 screen
    in vec2 v_pos;   // Manim units, camera already applied (draw in world space)
    out vec4 frag;   // LINEAR rgb, STRAIGHT alpha (premultiplied for you)
Auto uniforms (declare to use): u_time (absolute s), u_local (s since layer start),
u_res (px), u_frame (units), u_frame_index, u_seed, u_view, u_view_inv.
`#include "common/color.glsl"` for srgb2lin / hsv2rgb / ign dithering.
Every other `u_*` keyword becomes a uniform; values may be Tracks.
"""

from __future__ import annotations

import math
import re

import numpy as np

from aion.core.track import track
from aion.gpu import pool
from aion.gpu.program import fullscreen, load_source, program, set_uniforms
from aion.layers.base import ENC_LINEAR, Layer, RenderContext, Surface

__all__ = ["ShaderLayer"]

_PREMUL = """
uniform sampler2D u_in; in vec2 v_uv; out vec4 frag;
void main() { vec4 c = texture(u_in, v_uv); frag = vec4(c.rgb * c.a, c.a); }
"""


class ShaderLayer(Layer):
    """Full-frame GLSL layer. `animated` is auto-detected from u_time/u_local use.

    Example:
        ShaderLayer("layers/domain_coloring.frag", u_theta=key(T.turn, 0, 1.57), u_sat=0.8)
    """

    vector = True

    def __init__(self, frag: str, *, scale_res: float = 1.0, animated: bool | None = None, **kw):
        uniforms = {k: track(v) for k, v in list(kw.items()) if k.startswith("u_")}
        for k in uniforms:
            kw.pop(k)
        super().__init__(name=kw.pop("name", frag.split("/")[-1] if "\n" not in frag else "shader"), **kw)
        self.frag = frag
        self.uniforms = uniforms
        self.scale_res = scale_res
        src = load_source(frag)
        self.animated = animated if animated is not None else bool(re.search(r"\bu_(time|local|frame_index)\b", src))
        self._rt = self._raw = None

    def tracks(self):
        return super().tracks() + list(self.uniforms.values())

    def content_changes(self, t0, t1):
        return self.animated or any(u.changes(t0, t1) for u in self.uniforms.values())

    def cache_key(self):
        return super().cache_key() + [load_source(self.frag)]

    def draw(self, t: float, rc: RenderContext) -> Surface:
        size = (max(1, int(rc.size[0] * self.scale_res)), max(1, int(rc.size[1] * self.scale_res)))
        if self._rt is None or self._rt.size != size:
            self._rt = pool.target(size, "f2", pooled=False)
            self._raw = pool.target(size, "f2", pooled=False)
        view = rc.view(self.parallax)
        start = self.start if math.isfinite(self.start) else 0.0
        vals = {k: v(t) for k, v in self.uniforms.items()}
        prog = program(self.frag)
        auto = dict(u_time=t, u_local=t - start, u_res=size, u_frame=rc.frame_units,
                    u_frame_index=rc.frame_index, u_seed=float(rc.seed), u_view=view,
                    u_view_inv=np.linalg.inv(view))
        set_uniforms(prog, **{**auto, **vals})    # explicit uniforms override the automatic ones
        self._raw.use()
        fullscreen(prog).render(vertices=3)
        # straight → premultiplied
        pm = program(_PREMUL)
        set_uniforms(pm, u_in=(self._raw.tex, 0))
        self._rt.use()
        fullscreen(pm).render(vertices=3)
        return Surface(self._rt.tex, ENC_LINEAR, None)
