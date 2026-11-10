#version 330
#include "common/color.glsl"
// Composite one layer surface onto the accumulation buffer (linear, premultiplied).
uniform sampler2D u_src;
uniform int u_enc;            // 0 linear premul, 1 sRGB premul (Cairo), 2 sRGB straight (PNG)
uniform float u_opacity;
uniform sampler2D u_matte;
uniform int u_matte_mode;     // 0 none, 1 alpha, 2 alpha_inv, 3 luma, 4 luma_inv
uniform sampler2D u_dst;      // copy of the destination (advanced blend modes)
uniform int u_mode;           // 0 GL-blended (normal/add/screen); >=10 advanced, see comp/blend.py
uniform vec2 u_res;
in vec2 v_uv;
out vec4 frag;

vec4 decode(vec4 c, int enc) {
    if (enc == 1) { c = unpremul(c); return premul(vec4(srgb2lin(c.rgb), c.a)); }
    if (enc == 2) { return premul(vec4(srgb2lin(c.rgb), c.a)); }
    return c;
}

vec3 blend(int m, vec3 s, vec3 d) {
    if (m == 10) return s * d;                                                   // multiply
    if (m == 11) return mix(2.0 * s * d, 1.0 - 2.0 * (1.0 - s) * (1.0 - d), step(0.5, d)); // overlay
    if (m == 12) {                                                                // soft light
        vec3 q = mix(sqrt(d), d * (16.0 * d - 12.0) * d + 4.0 * d, step(d, vec3(0.25)));
        return mix(d + (2.0 * s - 1.0) * (q - d), d - (1.0 - 2.0 * s) * d * (1.0 - d), step(s, vec3(0.5)));
    }
    if (m == 13) return abs(s - d);                                               // difference
    if (m == 14) return max(s, d);                                                // lighten
    if (m == 15) return min(s, d);                                                // darken
    if (m == 16) return min(vec3(1.0), d / max(1.0 - s, 1e-4));                   // color dodge
    return s;
}

void main() {
    vec4 s = decode(texture(u_src, v_uv), u_enc) * u_opacity;
    vec2 sp = gl_FragCoord.xy / u_res;
    if (u_matte_mode > 0) {
        vec4 m = texture(u_matte, sp);
        float k = (u_matte_mode <= 2) ? m.a : clamp(luma(unpremul(m).rgb) * m.a, 0.0, 1.0);
        if (u_matte_mode == 2 || u_matte_mode == 4) k = 1.0 - k;
        s *= k;
    }
    if (u_mode < 10) { frag = s; return; }
    vec4 d = texture(u_dst, sp);
    vec3 cs = s.a > 1e-6 ? s.rgb / s.a : vec3(0.0);
    vec3 cd = d.a > 1e-6 ? d.rgb / d.a : vec3(0.0);
    vec3 rgb = (1.0 - s.a) * d.rgb + (1.0 - d.a) * s.rgb + s.a * d.a * blend(u_mode, cs, cd);
    frag = vec4(rgb, s.a + d.a * (1.0 - s.a));
}
