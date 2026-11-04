// 3D Gaussian splatting, one instanced quad per Gaussian (Kerbl et al. 2023 projection):
//   Σ' = J W Σ Wᵀ Jᵀ, plus the mip-splatting 0.3 px low-pass with opacity compensation.
// Per-splat animation (reveal / scan / dissolve) changes μ, a uniform scale of Σ, an isotropic blur term and α.
layout(std430, binding = 0) readonly buffer Splats { vec4 S[]; };
in uint in_idx;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_fy, u_tanX, u_tanY;
uniform vec2 u_res;
uniform float u_revealR, u_band, u_seedVis, u_scanY, u_scanAmt, u_scanW, u_dissR, u_tau;
uniform vec3 u_glassA, u_glassB, u_seedCol, u_hueA, u_hueB;
out vec2 v_xy;
out vec3 v_col;
out float v_alpha, v_depth, v_ell;
out vec3 v_hue;

const vec2 CORNER[4] = vec2[](vec2(-1, -1), vec2(1, -1), vec2(-1, 1), vec2(1, 1));

void cull() { gl_Position = vec4(3.0, 3.0, 3.0, 1.0); v_alpha = 0.0; }

void main() {
    uint b = in_idx * 5u;
    vec4 A = S[b], B = S[b + 1u], C = S[b + 2u], D = S[b + 3u], E = S[b + 4u];
    vec3 p = A.xyz;
    mat3 cov = mat3(B.x, B.y, B.z, B.y, B.w, C.x, B.z, C.x, C.y);
    float h = C.z;
    int grp = int(C.w + 0.5);
    vec3 col = D.rgb;
    float shk = D.w;
    vec3 nrm = E.xyz;

    if (grp == 2)   // floaters drift in the void
        p += vec3(sin(u_tau * 0.13 + h * 40.0), 0.5 * sin(u_tau * 0.1 + h * 17.0), cos(u_tau * 0.11 + h * 29.0)) * 6.0;
    float r = length(p.xz);

    // training reveal: seed points → large isotropic blobs (densify by h) → sharp anisotropic splats
    float pr = clamp((u_revealR - r) / u_band, 0.0, 1.0);
    float seed = step(h, 0.035) * u_seedVis;
    float ap = clamp((pr - 0.6 * h) / 0.25, 0.0, 1.0);
    float sh = smoothstep(0.3, 1.0, pr);
    float k = ap;
    float blob = (1.0 + 6.0 * (1.0 - 0.8 * h)) * (1.0 - sh) * ap;
    float am = max(seed * (1.0 - ap) * 0.75, ap * mix(0.3, 1.0, sh));
    col *= mix(0.4, 1.0, sh);                                          // blobs stay soft, not neon clouds
    col = mix(col, u_seedCol, seed * (1.0 - ap));

    // scan: a horizontal band where every Gaussian shrinks and shows its own ellipse
    float e = u_scanAmt * exp(-pow((p.y - u_scanY) / u_scanW, 2.0));
    k *= mix(1.0, 0.33, e);

    // dissolve from the outside in: drift away, blur, fade
    float dd = clamp((r - u_dissR + 60.0 * h) / 120.0, 0.0, 1.0);
    vec3 drift = normalize(vec3(sin(h * 91.0), 0.7 + fract(h * 13.0), cos(h * 57.0)));
    p += drift * dd * dd * 70.0;
    blob += dd * 1.5;
    col *= 1.0 - 0.7 * dd;
    am *= 1.0 - smoothstep(0.35, 1.0, dd);

    // time-varying light
    if (grp == 1) col *= 0.55 + 1.8 * pow(0.5 + 0.5 * sin(p.y * 0.09 - u_tau * 2.6), 6.0);
    if (grp == 4) col *= 0.12 + 3.0 * pow(max(0.0, sin(u_tau * 2.4 + h * 20.0)), 16.0);

    // view-dependent colour (glass): a degree-1 lobe along the normal plus moving reflection bands
    vec3 vdir = normalize(u_cam - p);
    if (shk > 0.0) {
        float f = abs(dot(nrm, vdir));
        vec3 rf = reflect(-vdir, nrm);
        float band = 0.5 + 0.5 * sin(dot(rf, vec3(7.0, 19.0, 5.0)) + p.y * 0.05);
        col += shk * (u_glassA * pow(1.0 - f, 3.0) * (0.35 + band) + u_glassB * band * band * f);
    }

    vec3 d = p - u_cam;
    vec3 v = vec3(dot(d, u_right), dot(d, u_up), dot(d, u_fwd));
    float op = A.w * am * smoothstep(0.8, 3.5, v.z);
    if (v.z < 0.4 || op < 0.004) { cull(); return; }

    float tx = clamp(v.x / v.z, -1.3 * u_tanX, 1.3 * u_tanX) * v.z;
    float ty = clamp(v.y / v.z, -1.3 * u_tanY, 1.3 * u_tanY) * v.z;
    float iz = 1.0 / v.z;
    mat3 J = mat3(u_fy * iz, 0.0, 0.0,
                  0.0, u_fy * iz, 0.0,
                  -u_fy * tx * iz * iz, -u_fy * ty * iz * iz, 0.0);
    mat3 W = transpose(mat3(u_right, u_up, u_fwd));
    seed *= (1.0 - ap);
    float sp = seed * 0.9 * v.z / u_fy * (u_res.y / 480.0);           // seed points: ~1 px regardless of distance
    mat3 Sg = cov * (k * k) + mat3(blob * blob + sp * sp);
    mat3 T = J * W;
    mat3 S2 = T * Sg * transpose(T);
    float a = S2[0][0], bb = S2[0][1], c = S2[1][1];
    float det0 = a * c - bb * bb;
    a += 0.3; c += 0.3;
    float det1 = a * c - bb * bb;
    op *= sqrt(max(det0, 0.0) / det1);
    float mid = 0.5 * (a + c);
    float rad = sqrt(max(0.25 * (a - c) * (a - c) + bb * bb, 1e-12));
    float l1 = mid + rad, l2 = max(mid - rad, 0.1);
    vec2 e1 = abs(bb) > 1e-7 ? normalize(vec2(bb, l1 - a)) : (a >= c ? vec2(1, 0) : vec2(0, 1));
    vec2 e2 = vec2(-e1.y, e1.x);
    float r1 = 3.0 * sqrt(l1), r2 = 3.0 * sqrt(l2);
    if (r1 > 2.5 * u_res.y || op < 0.004) { cull(); return; }

    vec2 cr = CORNER[gl_VertexID];
    vec2 px = vec2(u_fy * v.x * iz, u_fy * v.y * iz) + cr.x * e1 * r1 + cr.y * e2 * r2;
    gl_Position = vec4(px / (0.5 * u_res), 0.0, 1.0);
    v_xy = cr * 3.0;
    v_col = col;
    v_alpha = min(op, 0.99);
    v_depth = v.z;
    v_ell = e;
    v_hue = mix(u_hueA, u_hueB, fract(h * 7.31));
}
