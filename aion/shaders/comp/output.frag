#version 330
#include "common/color.glsl"
// Linear premultiplied accumulation -> display sRGB, dithered, flipped for top-down readback.
uniform sampler2D u_src;
uniform vec3 u_bg;          // linear background under any remaining transparency
uniform float u_frame_index;
uniform int u_alpha;        // 1: keep alpha (straight sRGB RGBA output)
in vec2 v_uv;
out vec4 frag;
void main() {
    vec4 c = texture(u_src, vec2(v_uv.x, 1.0 - v_uv.y));
    c.a = clamp(c.a, 0.0, 1.0);   // additive blends can push alpha past 1
    // static dither: identical across frames so reused hold frames stay bit-exact (grain is an fx)
    float dith = (ign(gl_FragCoord.xy, 0.0) - 0.5) / 255.0 + 0.0 * u_frame_index;
    if (u_alpha == 1) {
        vec4 u = unpremul(c);
        frag = vec4(lin2srgb(u.rgb) + dith, u.a);
    } else {
        vec3 rgb = c.rgb + u_bg * (1.0 - c.a);
        frag = vec4(lin2srgb(rgb) + dith, 1.0);
    }
}
