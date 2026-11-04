// Signal particles streaming along lit edges. Position = Bézier(u) of their edge, evaluated here.
in float in_e; in float in_u0; in float in_speed; in float in_size; in vec2 in_jit; in float in_l;
uniform vec3 u_lc[8];
uniform sampler2D u_edge;   // rows 0,1: state
uniform sampler2D u_ctrl;   // (NE × 4) control points
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_focus, u_dof, u_H, u_time, u_psize;
out float v_b; out float v_px; out vec3 v_col;
void main() {
    int e = int(in_e + 0.5);
    vec4 A = texelFetch(u_edge, ivec2(e, 0), 0);
    vec4 B = texelFetch(u_edge, ivec2(e, 1), 0);
    float u = fract(in_u0 + u_time * in_speed);
    float vis = B.z;                                         // edge afterglow = current flowing
    if (A.z >= 0.0 && A.z < 1.0) vis *= step(u, A.z);        // not ahead of the pulse
    vec3 P0 = texelFetch(u_ctrl, ivec2(e, 0), 0).xyz, P1 = texelFetch(u_ctrl, ivec2(e, 1), 0).xyz;
    vec3 P2 = texelFetch(u_ctrl, ivec2(e, 2), 0).xyz, P3 = texelFetch(u_ctrl, ivec2(e, 3), 0).xyz;
    float s = 1.0 - u;
    vec3 p = s * s * s * P0 + 3.0 * s * s * u * P1 + 3.0 * s * u * u * P2 + u * u * u * P3;
    float sw = sin(u * 3.14159);
    int l = int(in_l + 0.5);
    v_col = mix(u_lc[l], u_lc[l + 1], u);
    p += vec3(0.0, in_jit.x, in_jit.y) * sw;
    vec3 rel = p - u_cam;
    float z = max(dot(rel, u_fwd), 0.05);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, z);
    float coc = u_dof * u_H * 0.006 * abs(1.0 - u_focus / z);
    float px = u_psize * in_size + coc;
    v_px = px;
    v_b = vis * sw * (u_psize * in_size) * (u_psize * in_size) / (px * px);
    gl_PointSize = vis > 0.001 ? 2.0 * px + 2.0 : 0.0;
}
