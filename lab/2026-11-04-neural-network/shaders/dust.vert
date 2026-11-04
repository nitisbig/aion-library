// Ambient depth dust: slow drift, bokeh discs when out of focus.
in vec3 in_pos; in vec3 in_vel; in float in_b;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_focus, u_dof, u_H, u_time;
out float v_b; out float v_px; out float v_coc;
void main() {
    vec3 p = in_pos + in_vel * u_time;
    vec3 rel = p - u_cam;
    float z = dot(rel, u_fwd);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, max(z, 0.05));
    float coc = min(u_H * 0.012 * abs(1.0 - u_focus / max(z, 0.05)) * u_dof, u_H * 0.03);
    float base = u_H / 1080.0 * 1.4;
    v_px = base + coc; v_coc = coc;
    v_b = in_b * (z > 0.3 ? 1.0 : 0.0) * base * base / (v_px * v_px) * smoothstep(0.3, 2.0, z);
    gl_PointSize = 2.0 * v_px + 2.0;
}
