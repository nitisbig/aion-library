// Billboard sprites: ink particles (0), recognised-digit glyphs (1), shockwave rings (2).
in vec3 in_pos; in float in_size; in float in_b; in float in_kind; in float in_param; in vec3 in_col;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_focus, u_dof, u_H;
out float v_b; out float v_kind; out float v_param; out float v_px; out float v_coc; out vec3 v_col;
void main() {
    vec3 rel = in_pos - u_cam;
    float z = max(dot(rel, u_fwd), 0.05);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, z);
    float px = in_size / (z * u_tanHalf) * 0.5 * u_H;
    float coc = in_kind < 0.5 ? u_dof * u_H * 0.006 * abs(1.0 - u_focus / z) : 0.0;
    v_col = in_col;
    v_px = px; v_coc = coc; v_kind = in_kind; v_param = in_param;
    float pad = in_kind < 0.5 ? 2.5 : 1.0;
    v_b = in_kind < 0.5 ? in_b * px * px / ((px + coc) * (px + coc)) : in_b;
    gl_PointSize = in_b > 0.002 ? min(2.0 * (px * pad + coc) + 2.0, 2040.0) : 0.0;
}
