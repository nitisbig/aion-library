#version 330
#include "common/color.glsl"
// Vignette, chromatic aberration and film grain (deterministic per frame).
uniform sampler2D u_src; uniform vec2 u_res; uniform float u_vignette; uniform float u_vig_round;
uniform float u_ca; uniform float u_grain; uniform float u_frame_index; uniform float u_grain_size;
in vec2 v_uv; out vec4 frag;
void main() {
    vec2 d = v_uv - 0.5;
    vec4 c;
    if (u_ca > 0.0) {
        vec2 off = d * u_ca * 0.01;
        c = texture(u_src, v_uv);
        c.r = texture(u_src, v_uv - off).r;
        c.b = texture(u_src, v_uv + off).b;
    } else {
        c = texture(u_src, v_uv);
    }
    if (u_vignette > 0.0) {
        vec2 q = d * vec2(mix(1.0, u_res.x / u_res.y, u_vig_round), 1.0);
        float v = smoothstep(0.85, 0.15, length(q) * 1.15);
        c.rgb *= mix(1.0, v, u_vignette);
    }
    if (u_grain > 0.0) {
        vec2 p = floor(gl_FragCoord.xy / max(u_grain_size, 1.0));
        float n = ign(p, u_frame_index) + ign(p.yx + 17.0, u_frame_index + 31.0) - 1.0;
        float l = luma(c.rgb);
        c.rgb += n * u_grain * sqrt(max(l, 0.0)) * (1.0 - min(l, 1.0) * 0.5);
        c.rgb = max(c.rgb, 0.0);
    }
    frag = c;
}
