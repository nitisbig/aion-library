// Geodesic overlay: world-space polylines projected with the ray tracer's pinhole camera.
in vec3 in_pos; in float in_s; in float in_ray; in vec3 in_col;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_reveal, u_nray;
out VS { float s; float p; vec3 col; } vs;
void main() {
    vec3 rel = in_pos - u_cam;
    float z = dot(rel, u_fwd);
    gl_Position = vec4(dot(rel, u_right) / (u_tanHalf * u_aspect), dot(rel, u_up) / u_tanHalf, 0.0, z);
    float delay = 0.45 * in_ray / max(u_nray - 1.0, 1.0);
    vs.p = clamp((u_reveal - delay) / 0.55, 0.0, 1.0);
    vs.s = in_s; vs.col = in_col;
}
