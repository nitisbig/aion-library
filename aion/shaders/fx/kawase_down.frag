#version 330
// Dual-Kawase downsample (5 taps).
uniform sampler2D u_src; uniform vec2 u_texel; in vec2 v_uv; out vec4 frag;
void main() {
    vec2 o = u_texel;
    vec4 s = texture(u_src, v_uv) * 4.0;
    s += texture(u_src, v_uv - o) + texture(u_src, v_uv + o);
    s += texture(u_src, v_uv + vec2(o.x, -o.y)) + texture(u_src, v_uv - vec2(o.x, -o.y));
    frag = s / 8.0;
}
