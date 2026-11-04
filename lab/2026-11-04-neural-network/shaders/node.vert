in vec3 in_pos; in float in_r; in float in_reveal; in float in_act; in float in_grad; in float in_kind; in vec3 in_col;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_focus, u_dof, u_H, u_margin;
out float v_rpx; out float v_coc; out float v_reveal; out float v_act; out float v_grad; out float v_kind; out vec3 v_col;
void main() {
    vec3 rel = in_pos - u_cam;
    float z = max(dot(rel, u_fwd), 0.05);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, z);
    float rpx = in_r / (z * u_tanHalf) * 0.5 * u_H;
    float coc = u_dof * u_H * 0.006 * abs(1.0 - u_focus / z);
    v_rpx = rpx; v_coc = coc; v_reveal = in_reveal; v_act = in_act; v_grad = in_grad; v_kind = in_kind; v_col = in_col;
    gl_PointSize = min(2.0 * (rpx * u_margin + coc + 2.0), 2040.0);
}
