in float v_b; in float v_px; in float v_coc;
uniform vec3 u_col; uniform float u_amt;
out vec4 o;
void main() {
    float r = length(gl_PointCoord * 2.0 - 1.0) * (v_px + 1.0) / max(v_px, 0.5);
    float disc = 1.0 - smoothstep(0.85, 1.0, r);
    float ring = smoothstep(0.55, 0.95, r) * disc * 0.6;                    // bokeh rim
    float k = v_coc > 2.0 ? disc * 0.7 + ring : exp(-r * r * 3.0);
    o = vec4(u_col * k * v_b * u_amt, 1.0);
}
