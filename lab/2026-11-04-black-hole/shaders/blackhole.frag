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
uniform float u_sky, u_skyAmt, u_ss, u_starBoost;   // sky: 0 none, 1 celestial grid, 2 galaxy band
uniform vec3 u_skyPole, u_skyGC;
// "O" looks: lensed celestial objects
uniform float u_objects;
uniform vec3 u_nebC[3]; uniform float u_nebR[3]; uniform vec3 u_nebA[3]; uniform vec3 u_nebB[3];
uniform float u_nebI[3]; uniform float u_nebSeed[3];
uniform vec3 u_snDir; uniform float u_snI, u_snT, u_snAge;

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
    float d = smoothstep(0.22, 0.8, n) * (0.75 + 0.4 * fine);
    if (u_ss > 1.5) {    // crisp looks: one finer layer of sheared filaments (safe under supersampling)
        float hair = vnoise(vec3(cos(a) * 16.0, sin(a) * 16.0, lr * 120.0 + 4.0 * n));
        d *= 0.72 + 0.5 * hair;
    }
    return d;
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

// ── lensed sky layers (filtered by the lensed footprint fp, so they stay sharp and alias-free) ──
// fbm with level of detail: octaves finer than the pixel footprint are replaced by their mean
float fbmLod(vec3 p, float fs) {
    float s = 0.0, a = 0.5;
    for (int i = 0; i < 6; i++) {
        float w = 1.0 - smoothstep(0.25, 0.6, fs);
        s += a * mix(0.5, vnoise(p), w);
        p = p * 2.03 + vec3(1.7, 9.2, 3.1); fs *= 2.03; a *= 0.52;
    }
    return s;
}
vec3 galaxy(vec3 d, float fp) {
    vec3 gy = cross(u_skyPole, u_skyGC);
    float lat = asin(clamp(dot(d, u_skyPole), -1.0, 1.0));
    float lon = atan(dot(d, gy), dot(d, u_skyGC));
    float n = fbmLod(d * 5.0, fp * 5.0);
    float lanes = fbmLod(d * 13.0 + 7.3, fp * 13.0);
    float band = exp(-pow(lat / 0.2, 2.0));
    float bulge = exp(-pow(lon / 0.75, 2.0) - pow(lat / 0.22, 2.0));
    float dust = smoothstep(0.42, 0.68, lanes) * exp(-pow((lat - 0.015) / 0.06, 2.0));
    float I = (band * (0.01 + 1.5 * pow(n, 3.0)) + 1.2 * bulge * (0.35 + 0.65 * n)) * (1.0 - 0.9 * dust);
    vec3 col = mix(vec3(0.62, 0.72, 1.0), vec3(1.0, 0.80, 0.58), clamp(1.4 * bulge + 0.25 * n, 0.0, 1.0));
    return col * I * 0.085;
}
// lines every 10° of celestial latitude/longitude, majors every 30°, the equator brightest
float gridLine(float x, float fw, float lw) {
    float d = abs(fract(x + 0.5) - 0.5) / max(fw, 1e-6);       // distance in pixels
    return (1.0 - smoothstep(lw, lw + 1.0, d)) * (1.0 - smoothstep(0.08, 0.3, fw));
}
vec3 skyGrid(vec3 d, float lat, float lon, float lon2) {
    const float STEP = PI / 18.0;
    float x = lat / STEP, y = lon / STEP, y2 = lon2 / STEP;
    float fx = fwidth(x), fy = min(fwidth(y), fwidth(y2));
    float lw = 0.35 * u_ss;
    float mx = abs(mod(floor(x + 0.5), 3.0)) < 0.5 ? 1.0 : 0.45;
    float my = abs(mod(floor(y + 0.5), 3.0)) < 0.5 ? 1.0 : 0.45;
    float eq = abs(floor(x + 0.5)) < 0.5 ? 1.8 : 1.0;
    float lx = gridLine(x, fx, lw) * mx * eq;
    float ly = gridLine(y, fy, lw) * my * (1.0 - smoothstep(1.25, 1.5, abs(lat)));   // thin out at the poles
    vec3 c = vec3(0.30, 0.55, 1.0) * max(ly, 0.0) + mix(vec3(0.30, 0.55, 1.0), vec3(1.0, 0.62, 0.35), eq - 1.0 > 0.0 ? 1.0 : 0.0) * lx;
    return c * 0.22;
}

// ── lensed celestial objects ──────────────────────────────────────────────────
// emission nebula: domain-warped fbm, ionisation-front filaments, dark dust lanes
vec3 nebula(vec3 d, int i, float fp) {
    vec3 c = u_nebC[i]; float R = u_nebR[i];
    float ca = dot(d, c);
    if (ca < cos(min(R * 1.8, 3.0))) return vec3(0.0);
    float ang = acos(clamp(ca, -1.0, 1.0));
    float k = 2.6 / R;
    vec3 p = d * k + u_nebSeed[i];
    float fs = fp * k;
    vec3 w = vec3(fbmLod(p + 1.3, fs), fbmLod(p + 7.1, fs), fbmLod(p + 3.7, fs));
    float n = fbmLod(p + 1.9 * (w - 0.5), fs);
    float n2 = fbmLod(p * 1.8 + 3.0 * w, fs * 1.8);
    float shape = exp(-1.8 * pow(ang / R, 2.0));
    float body = smoothstep(0.30, 0.78, n + 0.30 * shape) * shape;
    float dens = body * body;
    float fil = pow(clamp(1.0 - abs(n - 0.56) * 7.0, 0.0, 1.0), 4.0) * shape;     // bright rims
    float dust = smoothstep(0.52, 0.72, n2) * shape;
    vec3 col = mix(u_nebA[i], u_nebB[i], smoothstep(0.38, 0.66, n2));
    vec3 e = col * dens * 1.6 + mix(u_nebA[i], vec3(1.0), 0.35) * fil * 0.8;
    return e * (1.0 - 0.85 * dust) * u_nebI[i];
}
// distant galaxies: rare small elliptical smudges (ellipticals warm, spirals with a bluer disk)
vec3 galaxies(vec3 dir, float sigmaPx) {
    vec3 ad = abs(dir);
    int f; vec2 st;
    if (ad.x >= ad.y && ad.x >= ad.z) { f = dir.x > 0.0 ? 0 : 1; st = dir.zy / ad.x; }
    else if (ad.y >= ad.z)            { f = dir.y > 0.0 ? 2 : 3; st = dir.xz / ad.y; }
    else                              { f = dir.z > 0.0 ? 4 : 5; st = dir.xy / ad.z; }
    const float N = 70.0;
    vec2 cell = floor((st * 0.5 + 0.5) * N);
    vec3 col = vec3(0.0);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = cell + vec2(i, j);
        if (c.x < 0.0 || c.y < 0.0 || c.x >= N || c.y >= N) continue;
        vec3 h = hash33(vec3(c, float(f) * 13.0 + 211.0));
        if (h.x > 0.05) continue;
        vec3 h2 = hash33(vec3(c.yx, float(f) * 3.0 + 517.0));
        vec3 g = normalize(faceDir(f, (c + 0.2 + 0.6 * h.yz) / N * 2.0 - 1.0));
        vec3 t1 = normalize(cross(g, abs(g.y) < 0.9 ? vec3(0, 1, 0) : vec3(1, 0, 0)));
        vec3 t2 = cross(g, t1);
        float th = h2.x * TAU, e = 0.25 + 0.75 * h2.y;
        vec2 q = vec2(dot(dir - g, t1), dot(dir - g, t2));
        q = vec2(cos(th) * q.x + sin(th) * q.y, -sin(th) * q.x + cos(th) * q.y);
        float s = 0.0006 + 0.0022 * pow(h2.z, 2.0);
        float sx = max(s, sigmaPx), sy = max(s * e, sigmaPx);
        float r2 = q.x * q.x / (sx * sx) + q.y * q.y / (sy * sy);
        bool spiral = h.z > 0.45;
        vec3 core = vec3(1.0, 0.82, 0.6), disk = spiral ? vec3(0.55, 0.7, 1.0) : core;
        vec3 gc = mix(disk, core, exp(-r2 * 3.0));
        col += gc * exp(-0.5 * r2) * (0.05 + 0.25 * h2.z) * (s * s) / (sx * sy);
    }
    return col;
}
// supernova: lensed point source with a light curve, diffraction spikes and a light echo
vec3 supernova(vec3 d, float sigma) {
    if (u_snI <= 0.0 || dot(d, u_snDir) < 0.9) return vec3(0.0);
    vec3 v = d - u_snDir;
    float x = dot(v, u_right), y = dot(v, u_up);
    float r = length(vec2(x, y));
    vec3 c = blackbody(u_snT);
    float core = exp(-0.5 * r * r / (sigma * sigma)) * 60.0 + exp(-r / (6.0 * u_pix)) * 2.0;
    float L = 40.0 * u_pix * sqrt(u_snI), w = 0.7 * u_pix * u_ss;
    float spikes = exp(-abs(x) / L) * exp(-pow(y / w, 2.0)) + exp(-abs(y) / L) * exp(-pow(x / w, 2.0));
    vec2 xr = vec2(x + y, x - y) * 0.7071;
    spikes += 0.35 * (exp(-abs(xr.x) / (0.5 * L)) * exp(-pow(xr.y / w, 2.0)) + exp(-abs(xr.y) / (0.5 * L)) * exp(-pow(xr.x / w, 2.0)));
    float echoR = 0.006 * sqrt(u_snAge), echo = exp(-pow((r - echoR) / (0.0012 + 0.1 * echoR), 2.0));
    vec3 echoC = mix(vec3(0.3, 0.6, 1.0), vec3(1.0, 0.4, 0.5), clamp(u_snAge / 6.0, 0.0, 1.0));
    return c * u_snI * (core + 1.5 * spikes) + echoC * echo * 0.12 * exp(-u_snAge / 7.0) * step(0.0, u_snAge);
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
        // soft leading edge, gaussian-tapered head, long fading tail
        float swept = 1.0 - smoothstep(u_sweep * TAU - 0.02, u_sweep * TAU + 0.18, behind);
        float headI = exp(-pow((behind - 0.06) / 0.09, 2.0));
        ringI *= swept * (1.0 + u_sweepAmp * (3.0 * headI + 1.2 * exp(-behind * 2.5)));
    }
    col += T * u_ring * ringI * u_ringTint;

    // lensed starfield
    float psiE = outward ? phc : phiEnd - phc;
    vec3 dOut = cos(psiE) * e1 + sin(psiE) * e2;
    float fp = max(length(dFdx(dOut)), length(dFdy(dOut)));
    bool sky = outward || (b > B_C && phiEnd < PHI_MAX);
    // sky-layer coordinates and their derivatives (uniform control flow)
    vec3 gy = cross(u_skyPole, u_skyGC);
    float slat = asin(clamp(dot(dOut, u_skyPole), -1.0, 1.0));
    float slon = atan(dot(dOut, gy), dot(dOut, u_skyGC));
    float slon2 = atan(-dot(dOut, gy), -dot(dOut, u_skyGC));   // same angle, seam on the other side
    vec3 grid = u_sky > 0.5 && u_sky < 1.5 ? skyGrid(dOut, slat, slon, slon2) : vec3(0.0);
    if (sky && u_skyAmt > 0.0) {
        vec3 skyc = u_sky > 1.5 ? galaxy(dOut, fp) : grid;
        col += T * skyc * u_skyAmt;
    }
    if (sky && u_objects > 0.0) {
        float sigmaO = max(0.55 * fp, 0.5 * u_pix);
        vec3 ob = nebula(dOut, 0, fp) + nebula(dOut, 1, fp) + nebula(dOut, 2, fp);
        ob += galaxies(dOut, sigmaO) + supernova(dOut, sigmaO);
        col += T * ob * u_objects;
    }
    if (sky && u_stars > 0.0) {
        float sigma = max(0.55 * fp, 0.5 * u_pix);
        vec3 s = starLayer(dOut, 190.0, min(0.13 * u_starBoost, 0.6), 1.6, 0.0, sigma);
        s += starLayer(dOut, 34.0, 0.30, 9.0, 7.0, sigma);
        s += starKernel(dOut, u_heroDir, 26.0 * u_hero, 11000.0, sigma);
        col += T * s * u_stars * u_starGain;
    }
    o = vec4(col, 1.0);
}
