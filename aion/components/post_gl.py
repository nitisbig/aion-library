"""Design-system frame finish for GPU plates: two-level bloom, vignette, film grain.

    finish = GlowFinish((w, h))
    ...render the scene into a multisampled fbo `ms`...
    finish.apply(ms, out_fbo, bloom=1.0, vignette=0.5, grain=0.04, opacity=1.0, seed=t)

Bloom: resolve → ¼ (threshold, so only bright lines glow) → ⅛, each blurred H then V,
added back over the scene. Grain is luminance-weighted, so pure black stays almost black.
Shared by TerrainPlate and SurfacePlate, so every plate in a video glows the same way.
"""

from __future__ import annotations

import numpy as np

from .shader_plate import _ctx

QUAD_VS = """
#version 330
in vec2 in_pos;
out vec2 v_uv;
void main() { v_uv = in_pos * 0.5 + 0.5; gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

DOWN_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_src;
uniform vec2 u_texel;        // source texel size
uniform float u_thresh;
out vec4 f_col;
void main() {                // 4 bilinear taps = a 4x4 box: thin lines are never skipped
    vec4 c = texture(u_src, v_uv + u_texel * vec2(-1, -1)) + texture(u_src, v_uv + u_texel * vec2(1, -1))
           + texture(u_src, v_uv + u_texel * vec2(-1, 1)) + texture(u_src, v_uv + u_texel * vec2(1, 1));
    f_col = max(c * 0.25 - u_thresh, 0.0);      // only what is bright blooms
}
"""

BLUR_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_src;
uniform vec2 u_step;
out vec4 f_col;
void main() {
    float w[5] = float[](0.2270, 0.1945, 0.1216, 0.0541, 0.0162);
    vec4 c = texture(u_src, v_uv) * w[0];
    for (int i = 1; i < 5; i++) {
        c += texture(u_src, v_uv + u_step * float(i)) * w[i];
        c += texture(u_src, v_uv - u_step * float(i)) * w[i];
    }
    f_col = c;
}
"""

COMP_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_scene, u_b1, u_b2;
uniform vec2 u_res;
uniform float u_bloom, u_vig, u_grain, u_opacity, u_seed;
out vec4 f_col;
float hash(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33);
                     return fract((p3.x + p3.y) * p3.z); }
void main() {
    vec3 c = texture(u_scene, v_uv).rgb;
    c += u_bloom * (0.9 * texture(u_b1, v_uv).rgb + 0.8 * texture(u_b2, v_uv).rgb);
    vec2 q = v_uv - 0.5;
    q.x *= u_res.x / u_res.y;
    c *= 1.0 - u_vig * smoothstep(0.30, 1.05, length(q) * 1.15);
    float l = clamp(dot(c, vec3(0.3, 0.6, 0.1)) * 3.0, 0.0, 1.0);
    c += (hash(v_uv * u_res + u_seed) - 0.5) * u_grain * (0.12 + 0.88 * l);
    f_col = vec4(clamp(c, 0.0, 1.0) * u_opacity, 1.0);
}
"""


class GlowFinish:
    """Bloom + vignette + grain for one plate size. Owns its textures and programs."""

    def __init__(self, size: tuple[int, int]):
        ctx = _ctx()
        self.size = w, h = size
        self.down = ctx.program(vertex_shader=QUAD_VS, fragment_shader=DOWN_FS)
        self.blur = ctx.program(vertex_shader=QUAD_VS, fragment_shader=BLUR_FS)
        self.comp = ctx.program(vertex_shader=QUAD_VS, fragment_shader=COMP_FS)
        quad = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes())
        self.qv = {p: ctx.vertex_array(prog, [(quad, "2f", "in_pos")])
                   for p, prog in (("down", self.down), ("blur", self.blur), ("comp", self.comp))}

        def tex(sz):
            t = ctx.texture(sz, 4)
            t.repeat_x = t.repeat_y = False
            return t, ctx.framebuffer(color_attachments=[t])

        self.scene = tex((w, h))
        self.q4 = (max(2, w // 4), max(2, h // 4))
        self.q8 = (max(2, w // 8), max(2, h // 8))
        self.b1 = (tex(self.q4), tex(self.q4))
        self.b2 = (tex(self.q8), tex(self.q8))

    @staticmethod
    def _set(prog, values: dict):
        for k, v in values.items():
            if k in prog:
                prog[k].value = v

    def apply(self, ms, out, *, bloom=1.0, vignette=0.5, grain=0.04, opacity=1.0, seed=0.0):
        """Resolve `ms` (a multisampled fbo), finish it, and draw into `out`."""
        ctx = _ctx()
        w, h = self.size
        st, sfbo = self.scene
        ctx.copy_framebuffer(sfbo, ms)

        def pass_(prog, key, src, dst_fbo, size, **u):
            dst_fbo.use()
            ctx.viewport = (0, 0, *size)
            src.use(0)
            prog["u_src"].value = 0
            self._set(prog, u)
            self.qv[key].render()

        (a1, f1), (b1, g1) = self.b1
        (a2, f2), (b2, g2) = self.b2
        q4, q8 = self.q4, self.q8
        if bloom > 0:
            pass_(self.down, "down", st, f1, q4, u_texel=(1.0 / w, 1.0 / h), u_thresh=0.05)
            pass_(self.blur, "blur", a1, g1, q4, u_step=(1.0 / q4[0], 0.0))
            pass_(self.blur, "blur", b1, f1, q4, u_step=(0.0, 1.0 / q4[1]))
            pass_(self.down, "down", a1, f2, q8, u_texel=(0.5 / q4[0], 0.5 / q4[1]), u_thresh=0.0)
            pass_(self.blur, "blur", a2, g2, q8, u_step=(1.5 / q8[0], 0.0))
            pass_(self.blur, "blur", b2, f2, q8, u_step=(0.0, 1.5 / q8[1]))

        out.use()
        ctx.viewport = (0, 0, w, h)
        st.use(0)
        a1.use(1)
        a2.use(2)
        self._set(self.comp, {"u_scene": 0, "u_b1": 1, "u_b2": 2, "u_res": (float(w), float(h)),
                              "u_bloom": float(bloom), "u_vig": float(vignette), "u_grain": float(grain),
                              "u_opacity": float(opacity), "u_seed": float(seed)})
        self.qv["comp"].render()
