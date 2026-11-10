#version 330
#include "common/color.glsl"
// Bloom prefilter: soft-knee threshold on luminance, 4-tap downsample.
uniform sampler2D u_src; uniform vec2 u_texel; uniform float u_threshold; uniform float u_knee;
in vec2 v_uv; out vec4 frag;
void main() {
    vec4 c = 0.25 * (texture(u_src, v_uv + u_texel * vec2(-1, -1)) + texture(u_src, v_uv + u_texel * vec2(1, -1))
                   + texture(u_src, v_uv + u_texel * vec2(-1, 1)) + texture(u_src, v_uv + u_texel * vec2(1, 1)));
    float l = max(c.r, max(c.g, c.b));
    float soft = clamp(l - u_threshold + u_knee, 0.0, 2.0 * u_knee);
    soft = soft * soft / (4.0 * u_knee + 1e-5);
    float w = max(soft, l - u_threshold) / max(l, 1e-5);
    frag = vec4(c.rgb * w, 0.0);
}
