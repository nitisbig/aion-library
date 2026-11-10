#version 330
// Directional / radial blur (zoom-blur transitions, speed lines).
uniform sampler2D u_src; uniform vec2 u_dir; uniform float u_radial; uniform vec2 u_center; uniform int u_taps;
in vec2 v_uv; out vec4 frag;
void main() {
    vec2 dir = u_radial > 0.0 ? (v_uv - u_center) * u_radial : u_dir;
    vec4 s = vec4(0.0);
    for (int i = 0; i < u_taps; i++) {
        float k = float(i) / float(max(u_taps - 1, 1)) - 0.5;
        s += texture(u_src, v_uv + dir * k);
    }
    frag = s / float(u_taps);
}
