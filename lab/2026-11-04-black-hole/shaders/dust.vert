// Act 1 travel: world-space dust and passing stars, drawn as motion streaks between the
// projections from the previous and the current camera.
in vec3 in_pos; in float in_bright; in float in_temp; in float in_size; in float in_kind;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform vec3 u_camP, u_rightP, u_upP, u_fwdP;
uniform float u_tanHalf, u_aspect, u_dust;
uniform sampler2D u_bb;
out VS { vec4 prev; vec3 col; float size; } vs;
vec4 proj(vec3 p, vec3 c, vec3 r, vec3 u, vec3 f) {
    vec3 rel = p - c;
    return vec4(dot(rel, r) / (u_tanHalf * u_aspect), dot(rel, u) / u_tanHalf, 0.0, dot(rel, f));
}
void main() {
    gl_Position = proj(in_pos, u_cam, u_right, u_up, u_fwd);
    vs.prev = proj(in_pos, u_camP, u_rightP, u_upP, u_fwdP);
    float rel = length(in_pos - u_cam) / length(u_cam);          // distance in units of the camera's r
    float k = in_kind > 0.5 ? 0.09 : 0.04;
    float I = in_bright * min(pow(k / rel, 2.0), in_kind > 0.5 ? 60.0 : 8.0);
    I *= smoothstep(0.0015, 0.006, rel);                         // no giant blobs right at the lens
    float x = clamp(log(in_temp / T_MIN) / log(T_MAX / T_MIN), 0.0, 1.0) * (N_T - 1.0);
    vs.col = texelFetch(u_bb, ivec2(int(x), 0), 0).rgb * I * u_dust;
    vs.size = in_size;
}
