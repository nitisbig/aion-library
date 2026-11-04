in float v_x, v_cw, v_I, v_Tc, v_Th;
uniform vec3 u_boltCol;
uniform float u_px;
out vec4 o;
void main() {
    if (v_I <= 0.0) discard;
    float x = abs(v_x);
    float core = exp(-x * x / (2.0 * v_cw * v_cw));
    float halo = exp(-x / (3.5 * u_px)) * 0.10;
    vec3 c = mix(u_boltCol, vec3(1.0), 0.6 * core);             // white-hot core, tinted glow
    o = vec4(c * v_I * (core * v_Tc + halo * v_Th), 0.0);
}
