// Shared by sky.frag and matter.frag: noise, blackbody, camera ray, Schwarzschild lensing.
// Constants (B_C, EPS, Y0, Y1, PHI_MAX, U_CMAX, NB, NPHI, NU, T_MIN, T_MAX, N_T) come from render.py.
const float PI = 3.14159265358979;
const float TAU = 6.28318530717959;

uniform sampler3D u_noise;       // 128³ periodic band-limited noise, 4 independent channels, mipmapped
uniform sampler2D u_bb;          // blackbody rgb (Y = 1), N_T × 1
uniform sampler2D u_lutPhc;      // φ_c(b, u_cam)
uniform sampler2D u_phiEnd;      // φ_end(b)

uniform vec3 u_camN, u_right, u_up, u_fwd;   // camera direction from the centre (unit) and its basis
uniform float u_tanHalf, u_aspect, u_pix, u_ss;
uniform float u_lensOn, u_rcM;               // lensing on/off, camera distance in units of GM/c²

vec3 viewDir(vec2 uv) {
    vec2 ndc = uv * 2.0 - 1.0;
    return normalize(u_fwd + ndc.x * u_tanHalf * u_aspect * u_right + ndc.y * u_tanHalf * u_up);
}

// ── noise ────────────────────────────────────────────────────────────────────
vec4 N4(vec3 p) { return texture(u_noise, p); }
float N(vec3 p) { return texture(u_noise, p).r; }
float hash13(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.zyx + 31.32);
    return fract((p.x + p.y) * p.z);
}
vec3 hash33(vec3 p) {
    p = fract(p * vec3(0.1031, 0.1030, 0.0973));
    p += dot(p, p.yxz + 33.33);
    return fract((p.xxy + p.yxx) * p.zyx);
}
float hash12(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
// two scales of the texture (it is already band-limited fbm-like within one tile)
float fbm2(vec3 p) { return 0.62 * texture(u_noise, p).r + 0.38 * texture(u_noise, p * 3.07 + 0.37).g; }
float ridged(float n) { return 1.0 - abs(2.0 * n - 1.0); }

vec3 blackbody(float T) {
    float x = clamp(log(T / T_MIN) / log(T_MAX / T_MIN), 0.0, 1.0) * (N_T - 1.0);
    int i = int(floor(min(x, N_T - 1.001)));
    return mix(texelFetch(u_bb, ivec2(i, 0), 0).rgb, texelFetch(u_bb, ivec2(i + 1, 0), 0).rgb, x - float(i));
}

// ── lensing ──────────────────────────────────────────────────────────────────
float bil(sampler2D s, vec2 size, vec2 xy) {      // manual bilinear (hardware weights are 8-bit)
    vec2 p = clamp(xy, 0.0, 1.0) * (size - 1.0);
    p = min(p, size - 1.0001);
    ivec2 i = ivec2(floor(p));
    vec2 f = p - vec2(i);
    float a = texelFetch(s, i, 0).r, b = texelFetch(s, i + ivec2(1, 0), 0).r;
    float c = texelFetch(s, i + ivec2(0, 1), 0).r, d = texelFetch(s, i + ivec2(1, 1), 0).r;
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
float bcoord(float b) { return (asinh((b - B_C) / EPS) - Y0) / (Y1 - Y0); }

// Direction the ray leaves to (at infinity) when traced back from the camera, and whether it
// escapes at all. Exact table lookup for b < 2000 M; first-order weak field beyond, where the
// deflection still owed from the camera onwards is (2M/b)(1 + cos A).
vec3 lensDir(vec3 d, out bool escapes) {
    escapes = true;
    if (u_lensOn < 0.5) return d;
    float rc = u_rcM;
    vec3 e1 = u_camN;
    float cosA = -dot(d, e1);
    vec3 perp = d + cosA * e1;
    float sinA = length(perp);
    vec3 e2 = perp / max(sinA, 1e-12);
    float b = max(rc * sinA / sqrt(1.0 - 2.0 / rc), 1.001e-3);
    bool outward = cosA < 0.0;
    float psiE;
    if (b < 1999.0) {
        float xb = bcoord(b);
        float phc = bil(u_lutPhc, vec2(NB, NU), vec2(xb, sqrt(min((1.0 / rc) / U_CMAX, 1.0))));
        float phiEnd = bil(u_phiEnd, vec2(NB, 1.0), vec2(xb, 0.0));
        psiE = outward ? phc : phiEnd - phc;
        escapes = outward || (b > B_C && phiEnd < PHI_MAX);
    } else {
        psiE = atan(sinA, -cosA) + (2.0 / b) * (1.0 + cosA);
    }
    return cos(psiE) * e1 + sin(psiE) * e2;
}

// tangent-plane coordinates of a direction in the camera frame
vec2 tanCoords(vec3 d) { return vec2(dot(d, u_right), dot(d, u_up)) / max(dot(d, u_fwd), 1e-4); }
vec3 fromTan(vec2 q) { return normalize(u_fwd + q.x * u_right + q.y * u_up); }
