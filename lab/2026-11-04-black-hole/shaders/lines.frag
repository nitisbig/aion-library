in float f_s; in float f_d; flat in float f_p; flat in float f_hw; flat in float f_thin; flat in vec3 f_col;
uniform float u_alpha;
out vec4 o;
void main() {
    float cov = clamp(f_hw + 0.5 - abs(f_d), 0.0, 1.0) * f_thin;
    if (cov <= 0.0) discard;
    float head = exp(-max(f_p - f_s, 0.0) * 30.0) * (1.0 - smoothstep(0.97, 1.0, f_p));
    float tail = (0.55 + 0.45 * smoothstep(0.0, 0.25, f_s)) * (1.0 - smoothstep(0.7, 1.0, f_s));  // soft ends
    vec3 c = f_col * (tail + 3.0 * head);
    o = vec4(c * cov * u_alpha, 1.0);
}
