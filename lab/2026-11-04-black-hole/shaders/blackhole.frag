// Schwarzschild ray tracer using precomputed geodesic tables (Luminet's method).
// Constants (B_C, EPS, Y0, Y1, PHI_MAX, U_CMAX, NB, NPHI, NU, R_IN, R_OUT, T_MIN, T_MAX) are
// injected as #defines by render.py.
in vec2 uv;
out vec4 o;

uniform sampler2D u_lutU;     // (NB x NPHI)  u(b, phi)
uniform sampler2D u_lutPhc;   // (NB x NU)    phi_c(b, u_cam)
uniform sampler2D u_phiEnd;   // (NB x 1)
uniform sampler2D u_bb;       // (N_T x 1)    blackbody rgb, Y = 1

uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_pix;

uniform float u_gas, u_front, u_ignite, u_disk, u_drain, u_tau;
uniform float u_Tpeak, u_beam, u_shift, u_gain, u_mode;
uniform float u_stars, u_hero, u_starGain;
uniform vec3 u_heroDir;
uniform float u_ring, u_ringW, u_sweep, u_sweepAmp, u_ringT;
uniform vec3 u_ringTint;

const float PI = 3.14159265358979;
const float TAU = 6.28318530717959;

// ── tables (manual bilinear: hardware filtering has only 8-bit weights) ───────
float bil(sampler2D s, vec2 size, vec2 xy) {
    vec2 p = clamp(xy, 0.0, 1.0) * (size - 1.0);
    p = min(p, size - 1.0001);
    ivec2 i = ivec2(floor(p));
    vec2 f = p - vec2(i);
    float a = texelFetch(s, i, 0).r, b = texelFetch(s, i + ivec2(1, 0), 0).r;
    float c = texelFetch(s, i + ivec2(0, 1), 0).r, d = texelFetch(s, i + ivec2(1, 1), 0).r;
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
float bcoord(float b) { return (asinh((b - B_C) / EPS) - Y0) / (Y1 - Y0); }

vec3 blackbody(float T) {
    float x = clamp(log(T / T_MIN) / log(T_MAX / T_MIN), 0.0, 1.0) * (N_T - 1.0);
    int i = int(floor(min(x, N_T - 1.001)));
    return mix(texelFetch(u_bb, ivec2(i, 0), 0).rgb, texelFetch(u_bb, ivec2(i + 1, 0), 0).rgb, x - float(i));
}

// ── noise ────────────────────────────────────────────────────────────────────
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
float vnoise(vec3 p) {
    vec3 i = floor(p), f = fract(p);
    vec3 w = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float n000 = hash13(i), n100 = hash13(i + vec3(1, 0, 0));
    float n010 = hash13(i + vec3(0, 1, 0)), n110 = hash13(i + vec3(1, 1, 0));
    float n001 = hash13(i + vec3(0, 0, 1)), n101 = hash13(i + vec3(1, 0, 1));
    float n011 = hash13(i + vec3(0, 1, 1)), n111 = hash13(i + vec3(1, 1, 1));
    return mix(mix(mix(n000, n100, w.x), mix(n010, n110, w.x), w.y),
               mix(mix(n001, n101, w.x), mix(n011, n111, w.x), w.y), w.z);
}
float fbm(vec3 p) {
    float s = 0.0, a = 0.5;
    for (int i = 0; i < 5; i++) { s += a * vnoise(p); p = p * 2.03 + vec3(1.7, 9.2, 3.1); a *= 0.52; }
    return s;
}

// ── disk ─────────────────────────────────────────────────────────────────────
// Novikov–Thorne-like flux F ∝ r^-3 (1 - sqrt(6/r)); its maximum is at r = 49/6.
float fluxNT(float r) { return pow(r, -3.0) * max(1.0 - sqrt(R_IN / r), 0.0) / 2.6227e-4; }

// density of the gas at radius r and co-rotating angle a
float gasDensity(float r, float a) {
    float lr = log(r);
    vec3 q = vec3(cos(a) * 2.2, sin(a) * 2.2, lr * 5.0);
    vec3 w = vec3(fbm(q + vec3(5.2, 1.3, 0.0)), fbm(q + vec3(1.7, 9.2, 4.0)), fbm(q + vec3(8.3, 2.8, 1.0)));
    float n = fbm(q * 1.3 + 1.6 * (w - 0.5));                         // domain-warped turbulence
    float fine = vnoise(vec3(cos(a) * 7.0, sin(a) * 7.0, lr * 34.0 + 2.0 * n));   // sheared filaments
    return smoothstep(0.22, 0.8, n) * (0.75 + 0.4 * fine);
}

struct Hit { vec3 emit; float alpha; };

Hit shadeDisk(float r, float az, float g, float wr, float wa) {
    Hit h;
    h.emit = vec3(0.0); h.alpha = 0.0;
    float edge = smoothstep(R_OUT, R_OUT - 5.0, r) * smoothstep(R_IN - 0.15, R_IN + 0.25, r);
    float Om = pow(r, -1.5);
    float a = az + Om * u_tau;                         // co-rotating angle (Keplerian shear)
    float lit = smoothstep(u_front - 0.3, u_front + 1.6, r) * u_ignite;
    lit *= smoothstep(u_drain + 0.6, u_drain - 1.2, r);
    float glow = exp(-pow((r - u_front) / 0.8, 2.0)) * clamp((u_front - R_IN) / 2.0, 0.0, 1.0) * u_ignite;
    if (u_mode < 0.5) {
        float d = gasDensity(r, a);
        float F = fluxNT(r);
        float T = u_Tpeak * pow(max(F, 1e-6), 0.25);
        float I = F * pow(g, u_beam) * (0.25 + d) * (lit + 2.5 * glow) * u_disk * u_gain;
        h.emit = blackbody(max(T * pow(g, u_shift) * (1.0 + 0.5 * glow), T_MIN)) * I;
        h.alpha = (1.0 - exp(-(0.6 + 3.0 * d) * edge)) * u_gas;
    } else {
        // iso-radius contours r = 6, 7, ... 19 plus co-rotating spokes
        float fr = abs(r - floor(r + 0.5));
        float lw = 0.75 * wr + 1e-4;
        float rings = 1.0 - smoothstep(lw, 2.2 * lw, fr);
        rings *= (abs(r - R_IN) < 0.5) ? 2.2 : (mod(floor(r + 0.5), 2.0) < 0.5 ? 1.0 : 0.55);
        // dashes riding on each contour at that contour's own Keplerian speed
        float rr = floor(r + 0.5);
        float ad = az + pow(rr, -1.5) * u_tau;
        float x = ad * 36.0 / TAU;
        float fs = abs(x - floor(x + 0.5));
        float dash = 0.35 + 0.65 * smoothstep(0.32, 0.18, fs);
        float spokes = 0.0;
        rings *= dash;
        float lines = max(rings, spokes) * edge;
        vec3 tint = mix(vec3(1.0, 0.42, 0.62), vec3(0.45, 0.82, 1.0), smoothstep(0.65, 1.35, g));
        tint = mix(tint, vec3(1.0), 0.35);
        h.emit = tint * lines * pow(g, 2.0) * (lit + 2.5 * glow) * u_disk * u_gain;
        h.alpha = 0.32 * edge * u_gas;
    }
    return h;
}

// ── stars ────────────────────────────────────────────────────────────────────
vec3 faceDir(int f, vec2 st) {
    if (f == 0) return vec3(1.0, st.y, st.x);
    if (f == 1) return vec3(-1.0, st.y, st.x);
    if (f == 2) return vec3(st.x, 1.0, st.y);
    if (f == 3) return vec3(st.x, -1.0, st.y);
    if (f == 4) return vec3(st.x, st.y, 1.0);
    return vec3(st.x, st.y, -1.0);
}
vec3 starKernel(vec3 dir, vec3 sdir, float flux, float T, float sigma) {
    if (dot(dir, sdir) < 0.0) return vec3(0.0);
    float d = length(cross(dir, sdir));
    float k = u_pix * u_pix / (TAU * sigma * sigma);
    return blackbody(T) * flux * k * exp(-0.5 * d * d / (sigma * sigma));
}
vec3 starLayer(vec3 dir, float N, float prob, float fluxK, float seed, float sigma) {
    vec3 ad = abs(dir);
    int f; vec2 st;
    if (ad.x >= ad.y && ad.x >= ad.z) { f = dir.x > 0.0 ? 0 : 1; st = dir.zy / ad.x; }
    else if (ad.y >= ad.z)            { f = dir.y > 0.0 ? 2 : 3; st = dir.xz / ad.y; }
    else                              { f = dir.z > 0.0 ? 4 : 5; st = dir.xy / ad.z; }
    vec2 g = (st * 0.5 + 0.5) * N;
    vec2 cell = floor(g);
    vec3 col = vec3(0.0);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = cell + vec2(i, j);
        if (c.x < 0.0 || c.y < 0.0 || c.x >= N || c.y >= N) continue;
        vec3 h = hash33(vec3(c, float(f) * 17.0 + seed));
        if (h.x > prob) continue;
        vec3 h2 = hash33(vec3(c.yx, float(f) * 5.0 + seed + 91.0));
        vec2 sp = (c + 0.15 + 0.7 * h.yz) / N * 2.0 - 1.0;
        vec3 sdir = normalize(faceDir(f, sp));
        float flux = fluxK * pow(h2.x, 5.0);
        float T = mix(3300.0, 13000.0, pow(h2.y, 1.6));
        col += starKernel(dir, sdir, flux, T, sigma);
    }
    return col;
}

void main() {
    vec2 ndc = uv * 2.0 - 1.0;
    vec3 d = normalize(u_fwd + ndc.x * u_tanHalf * u_aspect * u_right + ndc.y * u_tanHalf * u_up);
    float rc = length(u_cam);
    vec3 e1 = u_cam / rc;
    float cosA = -dot(d, e1);
    vec3 perp = d + cosA * e1;
    float sinA = length(perp);
    vec3 e2 = perp / max(sinA, 1e-7);
    float b = max(rc * sinA / sqrt(1.0 - 2.0 / rc), 1.001e-3);
    float xb = bcoord(b);
    bool outward = cosA < 0.0;
    float phc = bil(u_lutPhc, vec2(NB, NU), vec2(xb, sqrt((1.0 / rc) / U_CMAX)));
    float phiEnd = bil(u_phiEnd, vec2(NB, 1.0), vec2(xb, 0.0));
    float Lz = -b * cross(e1, e2).y;                   // photon angular momentum about the disk axis
    float gObs = 1.0 / sqrt(1.0 - 2.0 / rc);           // static observer's blueshift

    // disk crossings: the ray plane meets the disk plane every π of swept angle
    float psi0 = mod(atan(-e1.y, e2.y), PI);
    float rk[3]; float azk[3]; bool hk[3];
    for (int k = 0; k < 3; k++) {
        float psi = psi0 + float(k) * PI;
        float phi = phc + psi;
        float u = bil(u_lutU, vec2(NB, NPHI), vec2(xb, phi / PHI_MAX));
        float r = 1.0 / max(u, 1e-4);
        vec3 p = r * (cos(psi) * e1 + sin(psi) * e2);
        rk[k] = r;
        azk[k] = atan(p.z, p.x);
        hk[k] = !outward && phi < phiEnd && phi < PHI_MAX && u > 0.0 && r > R_IN - 0.2 && r < R_OUT;
    }
    // screen-space derivatives (uniform control flow) for anti-aliased contour lines
    float wr[3]; float wa[3];
    for (int k = 0; k < 3; k++) {
        wr[k] = fwidth(rk[k]);
        float a1 = azk[k] + pow(rk[k], -1.5) * u_tau;
        float a2 = mod(a1 + PI, TAU);                  // same angle with the seam moved
        wa[k] = min(fwidth(a1), fwidth(a2));
    }

    vec3 col = vec3(0.0);
    float T = 1.0;                                      // transmittance
    for (int k = 0; k < 3; k++) {
        if (!hk[k]) continue;
        float r = rk[k];
        float g = sqrt(1.0 - 3.0 / r) / (1.0 - pow(r, -1.5) * Lz) * gObs;
        Hit h = shadeDisk(r, azk[k], g, wr[k], wa[k]);
        col += T * h.emit * max(h.alpha, u_mode > 0.5 ? 1.0 : 0.0);
        T *= 1.0 - h.alpha;
    }

    // photon ring: emission placed at b = √27 (where light orbits at r = 3M)
    float db = (b - B_C) / u_ringW;
    float ringI = exp(-db * db * (db < 0.0 ? 6.0 : 1.0));
    if (u_sweep >= 0.0) {
        float th = atan(ndc.y, ndc.x * u_aspect);
        float head = PI * 0.5 - u_sweep * TAU;          // starts at the top, runs clockwise
        float behind = mod(th - head, TAU);             // angular distance behind the head
        float swept = 1.0 - smoothstep(u_sweep * TAU, u_sweep * TAU + 0.05, behind);
        ringI *= swept * (1.0 + 4.0 * u_sweepAmp * exp(-behind * 4.0));
    }
    col += T * u_ring * ringI * u_ringTint;

    // lensed starfield
    float psiE = outward ? phc : phiEnd - phc;
    vec3 dOut = cos(psiE) * e1 + sin(psiE) * e2;
    float fp = max(length(dFdx(dOut)), length(dFdy(dOut)));
    bool sky = outward || (b > B_C && phiEnd < PHI_MAX);
    if (sky && u_stars > 0.0) {
        float sigma = max(0.55 * fp, 0.5 * u_pix);
        vec3 s = starLayer(dOut, 190.0, 0.13, 1.6, 0.0, sigma);
        s += starLayer(dOut, 34.0, 0.30, 9.0, 7.0, sigma);
        s += starKernel(dOut, u_heroDir, 26.0 * u_hero, 11000.0, sigma);
        col += T * s * u_stars * u_starGain;
    }
    o = vec4(col, 1.0);
}
