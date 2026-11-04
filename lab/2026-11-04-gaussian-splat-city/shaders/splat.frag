in vec2 v_xy;
in vec3 v_col;
in float v_alpha, v_depth, v_ell;
in vec3 v_hue;
layout(location = 0) out vec4 o0;     // premultiplied colour, α
layout(location = 1) out vec4 o1;     // α-weighted depth (for DOF), α
void main() {
    float r2 = dot(v_xy, v_xy);
    if (r2 > 9.0) discard;
    float g = exp(-0.5 * r2);
    vec3 c = v_col;
    if (v_ell > 0.01) {               // show the Gaussian as an ellipse: flat core + thin rim at 2σ
        float rr = sqrt(r2);
        float rim = exp(-pow((rr - 1.95) / 0.13, 2.0));
        float core = smoothstep(2.1, 1.8, rr);
        g = mix(g, 0.55 * core + rim, v_ell);
        c = mix(c, mix(c * 1.5, v_hue, 0.55) * (0.7 + 2.5 * rim), v_ell);
    }
    float a = min(0.99, v_alpha * g);
    if (a < 1.0 / 255.0) discard;
    o0 = vec4(c * a, a);
    o1 = vec4(v_depth * a, 0.0, 0.0, a);
}
