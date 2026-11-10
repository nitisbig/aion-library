#version 330
#include "common/color.glsl"
// Glow source: the layer's alpha (or colour) tinted, for blurring.
uniform sampler2D u_src; uniform vec3 u_color; uniform int u_use_color; in vec2 v_uv; out vec4 frag;
void main() {
    vec4 c = texture(u_src, v_uv);
    vec3 rgb = u_use_color == 1 ? u_color * c.a : c.rgb;
    frag = vec4(rgb, c.a);
}
