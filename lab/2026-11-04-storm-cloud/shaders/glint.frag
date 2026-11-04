in vec3 v_col;
in float v_edge, v_rim;
out vec4 o;
void main() {
    float r = length(gl_PointCoord - 0.5) * 2.0;
    if (r > 1.0) discard;
    float f = smoothstep(1.0, 1.0 - v_edge, r);
    f *= 1.0 + v_rim * (0.5 * smoothstep(0.6, 0.94, r) - 0.15);
    o = vec4(v_col * f, 0.0);
}
