// one screen-aligned quad per lightning segment (instanced); thickness from distance, HDR intensity from the
// bolt's state (leader growth, return stroke, fading branches); transmittance through the cloud per endpoint
in vec4 in_a;    // xyz, grow time
in vec4 in_b;    // xyz, weight (subtree size)
in vec4 in_f;    // main channel, subtree size, bolt id, 0
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanX, u_tanY, u_fy, u_W, u_H, u_px, u_sigma;
uniform vec4 u_bolt[3];   // grow, leader, main, branch
uniform sampler3D dens;
out float v_x, v_cw, v_I, v_Tc, v_Th;
vec3 view(vec3 p) { vec3 d = p - u_cam; return vec3(dot(d, u_right), dot(d, u_up), dot(d, u_fwd)); }
float depthTo(vec3 p) {
    vec3 d = p - u_cam;
    float od = 0.0;
    const int N = 28;
    for (int j = 0; j < N; j++) od += textureLod(dens, boxUVW(u_cam + d * (float(j) + 0.5) / float(N)), 1.0).r;
    return od * length(d) / float(N) * u_sigma;
}
void main() {
    vec4 B = u_bolt[int(in_f.z + 0.5)];
    int vid = gl_VertexID;
    gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
    v_I = 0.0;
    if (B.x < 0.0 || in_a.w > B.x) return;
    vec3 va = view(in_a.xyz), vb = view(in_b.xyz);
    if (va.z < 0.05 || vb.z < 0.05) return;
    vec2 half_ = vec2(u_W, u_H) * 0.5;
    vec2 pa = va.xy / (va.z * vec2(u_tanX, u_tanY)) * half_;
    vec2 pb = vb.xy / (vb.z * vec2(u_tanX, u_tanY)) * half_;
    bool isMain = in_f.x > 0.5;
    float w = in_b.w;
    float fresh = exp(-max(B.x - in_a.w, 0.0) / 0.012);          // the leader's newest steps glow
    float I = B.y * (0.12 + 0.6 * w + 2.5 * fresh) + (isMain ? B.z : B.w * (0.08 + 0.9 * w) * max(B.z, 0.25));
    float worldW = isMain ? 0.03 : 0.004 + 0.025 * w;
    float z = 0.5 * (va.z + vb.z);
    float cw = worldW * u_fy / z;                                 // true core width in px
    float drawn = max(cw, 0.75 * u_px);
    I *= clamp(cw / drawn, 0.25, 1.0) * 1.4;
    float hw = drawn * 3.0 + 9.0 * u_px;
    vec2 dir = pb - pa;
    float len = length(dir);
    dir = len > 1e-4 ? dir / len : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    bool endB = (vid & 1) == 1;
    float side = (vid >> 1) == 0 ? -1.0 : 1.0;
    vec2 P = (endB ? pb : pa) + n * side * hw + dir * (endB ? 1.0 : -1.0) * drawn;
    float od = depthTo(endB ? in_b.xyz : in_a.xyz);
    v_Tc = exp(-od);
    v_Th = exp(-0.18 * od) * 0.6 + 0.4 * exp(-0.04 * od);          // scattered glow still escapes
    v_x = side * hw;
    v_cw = drawn * 0.5;
    v_I = I;
    gl_Position = vec4(P / half_, 0.0, 1.0);
}
