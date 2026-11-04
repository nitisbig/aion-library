// A = (reveal, w/scale, pulse phase, pulse amp)   B = (back phase, grad amp, glow, grad glow)
in float f_s; in float f_d;
flat in float f_hw; flat in float f_soft; flat in float f_gain; flat in vec4 f_a; flat in vec4 f_b;
flat in vec3 f_c0; flat in vec3 f_c1;
uniform vec3 u_hot;
uniform float u_base, u_pulse, u_trail, u_alpha, u_negK;
out vec4 o;
void main() {
    if (f_s > f_a.x) discard;
    float cov = clamp(f_hw + 0.5 - abs(f_d), 0.0, 1.0);                 // crisp 1-px AA edge
    if (f_soft > 0.0) cov = 1.0 - smoothstep(f_hw - 0.5, f_hw + 0.5 + f_soft, abs(f_d));
    if (cov <= 0.0) discard;
    float w = f_a.y, mag = min(abs(w), 1.6);
    vec3 col = mix(f_c0, f_c1, smoothstep(0.15, 0.85, f_s));
    // negative weights: same hue, darker and desaturated
    vec3 hue = w >= 0.0 ? col : mix(vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), col, 0.45) * u_negK;
    float ends = 0.4 + 0.6 * smoothstep(0.0, 0.1, f_s) * smoothstep(1.0, 0.9, f_s);
    float base = u_base * (0.05 + pow(mag, 1.7)) * ends;
    float grow = f_a.x < 1.0 ? exp(-(f_a.x - f_s) * 40.0) * 1.5 : 0.0;
    float pl = 0.0;
    if (f_a.z >= 0.0) {
        float d = f_a.z - f_s;
        if (d >= 0.0) pl = exp(-d * u_trail) * 1.0 + exp(-d * d * 2500.0) * 2.2;
    }
    pl *= f_a.w * u_pulse;
    vec3 c = hue * (base * (1.0 + grow) + f_b.z * 0.7 * ends) + mix(col, u_hot, 0.35) * pl;
    o = vec4(c * cov * f_gain * u_alpha, 1.0);
}
