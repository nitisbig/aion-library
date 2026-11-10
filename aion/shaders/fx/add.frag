#version 330
// out = a + b * k * tint   (b's alpha optionally included for glows)
uniform sampler2D u_a; uniform sampler2D u_b; uniform float u_k; uniform vec3 u_tint; uniform float u_alpha_w;
in vec2 v_uv; out vec4 frag;
void main() {
    vec4 a = texture(u_a, v_uv), b = texture(u_b, v_uv) * u_k;
    vec3 rgb = a.rgb + b.rgb * u_tint;
    float al = clamp(a.a + u_alpha_w * b.a * (1.0 - a.a), 0.0, 1.0);
    frag = vec4(rgb, max(al, a.a));
}
