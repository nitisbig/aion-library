in float v_b; in float v_px; in vec3 v_col;
uniform vec3 u_col; uniform float u_gain;
out vec4 o;
void main() {
    float r = length(gl_PointCoord * 2.0 - 1.0) * (v_px + 1.0);
    float k = exp(-r * r / max(v_px * v_px * 0.35, 0.4));
    o = vec4(mix(v_col, u_col, 0.35) * k * v_b * u_gain, 1.0);
}
