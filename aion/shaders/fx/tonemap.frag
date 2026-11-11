#version 330
// ACES filmic tonemap (Narkowicz fit) in linear light: HDR highlights roll off instead of clipping.
uniform sampler2D u_src; uniform float u_exposure;
in vec2 v_uv; out vec4 frag;
void main() {
    vec4 c = texture(u_src, v_uv);
    vec3 x = (c.a > 1e-6 ? c.rgb / c.a : vec3(0.0)) * exp2(u_exposure);
    x = clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
    frag = vec4(x * c.a, c.a);
}
