// soft dot when in focus, flat bokeh disc with a slightly bright rim when out of focus
in vec3 v_col;
in float v_edge, v_rim;
out vec4 o;
void main() {
    float r = length(gl_PointCoord - 0.5) * 2.0;
    if (r > 1.0) discard;
    float f = smoothstep(1.0, 1.0 - v_edge, r);
    f *= 1.0 + v_rim * (0.45 * smoothstep(0.55, 0.92, r) - 0.12);
    o = vec4(v_col * f, 0.0);
}
