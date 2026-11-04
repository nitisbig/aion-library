// Instanced sphere impostors (points). World units are nm.
in vec3 in_pos; in float in_r; in vec3 in_col; in float in_emit; in float in_group;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_H, u_near, u_far;
uniform vec3 u_groupVis;
out vec3 v_col; out float v_emit; out float v_rpx; out float v_z; out float v_r; out float v_vis; out float v_group;
void main() {
    vec3 rel = in_pos - u_cam;
    float z = dot(rel, u_fwd);
    float vis = in_group < 0.5 ? u_groupVis.x : (in_group < 1.5 ? u_groupVis.y : u_groupVis.z);
    v_vis = vis; v_group = in_group;
    if (z < u_near + in_r || vis < 0.004) { gl_Position = vec4(0, 0, -2, 1); gl_PointSize = 0.0; return; }
    float d = log(z / u_near) / log(u_far / u_near);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, (2.0 * d - 1.0) * z, z);
    float rpx = in_r / (z * u_tanHalf) * 0.5 * u_H;
    v_rpx = rpx; v_z = z; v_r = in_r; v_col = in_col; v_emit = in_emit;
    gl_PointSize = clamp(2.0 * rpx + 2.0, 1.0, 1024.0);
}
