// Act 3: Flamm's paraboloid y = sink·(√(8(r−2)) − H_RIM), with the rim at y = 0 and the throat (r = 2) below.
in vec2 in_xz; in float in_r; in float in_s; in float in_t0; in float in_dur; in float in_kind; in float in_phase; in vec3 in_col;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_time, u_sink, u_hrim;
out VS { float s; float p; vec3 col; float r; float kind; float phase; vec3 world; } vs;
void main() {
    float y = u_sink * (sqrt(8.0 * max(in_r - 2.0, 0.0)) - u_hrim);
    vec3 w = vec3(in_xz.x, y, in_xz.y);
    vec3 rel = w - u_cam;
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, dot(rel, u_fwd));
    vs.p = clamp((u_time - in_t0) / in_dur, 0.0, 1.0);
    vs.s = in_s; vs.col = in_col; vs.r = in_r; vs.kind = in_kind; vs.phase = in_phase; vs.world = w;
}
