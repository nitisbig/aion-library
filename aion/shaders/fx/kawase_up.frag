#version 330
// Dual-Kawase upsample (8 taps), optionally added onto a base.
uniform sampler2D u_src; uniform sampler2D u_base; uniform float u_base_w; uniform vec2 u_texel;
in vec2 v_uv; out vec4 frag;
void main() {
    vec2 o = u_texel;
    vec4 s = texture(u_src, v_uv + vec2(-o.x * 2.0, 0.0));
    s += texture(u_src, v_uv + vec2(-o.x, o.y)) * 2.0;
    s += texture(u_src, v_uv + vec2(0.0, o.y * 2.0));
    s += texture(u_src, v_uv + vec2(o.x, o.y)) * 2.0;
    s += texture(u_src, v_uv + vec2(o.x * 2.0, 0.0));
    s += texture(u_src, v_uv + vec2(o.x, -o.y)) * 2.0;
    s += texture(u_src, v_uv + vec2(0.0, -o.y * 2.0));
    s += texture(u_src, v_uv + vec2(-o.x, -o.y)) * 2.0;
    frag = s / 12.0 + u_base_w * texture(u_base, v_uv);
}
