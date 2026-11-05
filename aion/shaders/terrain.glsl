// Height field shared by the luminous terrain programs (TerrainPlate).
//   height(p) = patch(p) + mountains(p)
// patch: the quadratic ½·pᵀHp the narration is about, windowed so it can sit
// inside a landscape. mountains: ridged fBm, exactly zero inside radius u_m0, so
// the Python mirror (patch only) is exact wherever the walker and labels live.

uniform vec3 u_H;          // (a, b, c) → H = [[a, b], [b, c]]
uniform float u_zs;        // vertical scale of the patch
uniform float u_win;       // gaussian window radius of the patch (0 = unwindowed)
uniform float u_zclip;     // soft clamp of the patch height (0 = off)
uniform float u_wm;        // mountain amount 0..1
uniform float u_m0, u_m1;  // mountain mask: 0 inside m0, full beyond m1
uniform float u_mamp;      // mountain height
uniform float u_mscale;    // mountain feature frequency
uniform vec2 u_mseed;
uniform float u_mback;     // mountains pushed back on the camera side (x < 0): an open valley to stand in

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float a = hash12(i), b = hash12(i + vec2(1, 0));
    float c = hash12(i + vec2(0, 1)), d = hash12(i + vec2(1, 1));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float ridged(vec2 p) {
    float s = 0.0, a = 0.5, w = 1.0;
    mat2 R = mat2(0.8, -0.6, 0.6, 0.8);
    for (int i = 0; i < 6; i++) {
        float n = 1.0 - abs(vnoise(p) * 2.0 - 1.0);
        n *= n;
        s += a * n * w;
        w = clamp(n * 1.7, 0.0, 1.0);
        p = R * p * 2.03 + vec2(17.1, 3.7);
        a *= 0.5;
    }
    return s;
}

float patch_h(vec2 p) {
    float q = 0.5 * (u_H.x * p.x * p.x + 2.0 * u_H.y * p.x * p.y + u_H.z * p.y * p.y);
    float w = u_win > 0.0 ? exp(-dot(p, p) / (2.0 * u_win * u_win)) : 1.0;
    float z = u_zs * q * w;
    if (u_zclip > 0.0) z = u_zclip * tanh(z / u_zclip);
    return z;
}

// where the mountains are (0 inside m0, 1 beyond m1); the open valley is on the camera side
float mountain_mask(vec2 p) {
    float r = length(vec2(p.x < 0.0 ? p.x * u_mback : p.x, p.y));   // ≤ |p|: zero inside m0 holds
    return u_wm * smoothstep(u_m0, u_m1, r);
}

float mountains(vec2 p) {
    if (u_wm <= 0.0) return 0.0;
    float m = mountain_mask(p) / u_wm;
    if (m <= 0.0) return 0.0;
    float r = length(p);
    // an alpine basin: walls that rise with distance, carved into ridges (domain-warped)
    vec2 q = p * u_mscale + u_mseed;
    q += 0.55 * vec2(vnoise(q * 0.5) - 0.5, vnoise(q * 0.5 + 7.3) - 0.5);
    float ridge = ridged(q);
    float massif = smoothstep(0.18, 0.82, vnoise(q * 0.33 + 2.1));
    float rise = smoothstep(u_m0, u_m1 * 2.6, r);
    return u_wm * m * u_mamp * (0.42 * rise + ridge * (0.25 + 0.9 * massif) * (0.45 + 0.55 * rise));
}

float height(vec2 p) { return patch_h(p) + mountains(p); }
