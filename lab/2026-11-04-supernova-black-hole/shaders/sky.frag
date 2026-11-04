// The sky at infinity, seen through the black hole's lens: far stars, the Milky Way band, distant
// galaxies, a globular cluster, and the near layer (bright stars, three emission nebulae) that the
// gravitational wave reaches within the scene's 300 years.
in vec2 uv;
out vec4 o;

uniform float u_sky;
uniform vec3 u_skyPole, u_skyGC;                          // galactic frame
uniform vec3 u_nebC[3]; uniform float u_nebR[3]; uniform vec3 u_nebA[3]; uniform vec3 u_nebB[3];
uniform float u_nebI[3]; uniform float u_nebSeed[3];
uniform vec3 u_gcDir; uniform float u_gcR;                // globular cluster
// gravitational-wave sweep: observed when T = (|p| + |p − cam|)/c for an object at p
uniform float u_Tyr;                                      // physical time, years
uniform vec3 u_camLy;                                     // camera position, light years
uniform float u_gwAmp;

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
void cubeCell(vec3 dir, out int f, out vec2 st) {
    vec3 ad = abs(dir);
    if (ad.x >= ad.y && ad.x >= ad.z) { f = dir.x > 0.0 ? 0 : 1; st = dir.zy / ad.x; }
    else if (ad.y >= ad.z)            { f = dir.y > 0.0 ? 2 : 3; st = dir.xz / ad.y; }
    else                              { f = dir.z > 0.0 ? 4 : 5; st = dir.xy / ad.z; }
}
vec3 starLayer(vec3 dir, float N, float prob, float fluxK, float seed, float sigma) {
    int f; vec2 st;
    cubeCell(dir, f, st);
    vec2 cell = floor((st * 0.5 + 0.5) * N);
    vec3 col = vec3(0.0);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = cell + vec2(i, j);
        if (c.x < 0.0 || c.y < 0.0 || c.x >= N || c.y >= N) continue;
        vec3 h = hash33(vec3(c, float(f) * 17.0 + seed));
        if (h.x > prob) continue;
        vec3 h2 = hash33(vec3(c.yx, float(f) * 5.0 + seed + 91.0));
        vec3 sdir = normalize(faceDir(f, (c + 0.15 + 0.7 * h.yz) / N * 2.0 - 1.0));
        float flux = fluxK * pow(h2.x, 5.0);
        float T = mix(3300.0, 13000.0, pow(h2.y, 1.6));
        col += starKernel(dir, sdir, flux, T, sigma);
    }
    return col;
}
// globular cluster: a dense knot of old (cool, yellow) stars with an unresolved glow
vec3 globular(vec3 dir, float sigma) {
    float ca = dot(dir, u_gcDir);
    if (ca < cos(6.0 * u_gcR)) return vec3(0.0);
    float a = acos(clamp(ca, -1.0, 1.0)) / u_gcR;
    float dens = 1.0 / (1.0 + a * a * 2.5) * exp(-a * 0.35);
    int f; vec2 st;
    cubeCell(dir, f, st);
    const float NG = 2600.0;
    vec2 cell = floor((st * 0.5 + 0.5) * NG);
    vec3 col = vec3(0.0);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = cell + vec2(i, j);
        vec3 h = hash33(vec3(c, float(f) * 7.0 + 404.0));
        if (h.x > 0.8 * dens) continue;
        vec3 h2 = hash33(vec3(c.yx, float(f) * 3.0 + 77.0));
        vec3 sdir = normalize(faceDir(f, (c + 0.15 + 0.7 * h.yz) / NG * 2.0 - 1.0));
        col += starKernel(dir, sdir, 0.35 * pow(h2.x, 3.0), mix(3600.0, 6500.0, h2.y), sigma);
    }
    return col + blackbody(4800.0) * 0.012 * dens * dens;
}

// ── extended objects (texture noise: the mipmaps filter them by the lensed footprint) ──
// procedural value noise with level of detail (from the black-hole lab): octaves finer than the
// lensed pixel footprint collapse to their mean, so lensed structure stays alias-free
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
vec3 galaxies(vec3 dir, float sigmaPx) {
    int f; vec2 st;
    cubeCell(dir, f, st);
    const float NGx = 70.0;
    vec2 cell = floor((st * 0.5 + 0.5) * NGx);
    vec3 col = vec3(0.0);
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 c = cell + vec2(i, j);
        if (c.x < 0.0 || c.y < 0.0 || c.x >= NGx || c.y >= NGx) continue;
        vec3 h = hash33(vec3(c, float(f) * 13.0 + 211.0));
        if (h.x > 0.05) continue;
        vec3 h2 = hash33(vec3(c.yx, float(f) * 3.0 + 517.0));
        vec3 g = normalize(faceDir(f, (c + 0.2 + 0.6 * h.yz) / NGx * 2.0 - 1.0));
        vec3 t1 = normalize(cross(g, abs(g.y) < 0.9 ? vec3(0, 1, 0) : vec3(1, 0, 0)));
        vec3 t2 = cross(g, t1);
        float th = h2.x * TAU, e = 0.25 + 0.75 * h2.y;
        vec2 q = vec2(dot(dir - g, t1), dot(dir - g, t2));
        q = vec2(cos(th) * q.x + sin(th) * q.y, -sin(th) * q.x + cos(th) * q.y);
        float s = 0.0006 + 0.0022 * pow(h2.z, 2.0);
        float sx = max(s, sigmaPx), sy = max(s * e, sigmaPx);
        float r2 = q.x * q.x / (sx * sx) + q.y * q.y / (sy * sy);
        vec3 core = vec3(1.0, 0.82, 0.6), disk = h.z > 0.45 ? vec3(0.55, 0.7, 1.0) : core;
        col += mix(disk, core, exp(-r2 * 3.0)) * exp(-0.5 * r2) * (0.05 + 0.25 * h2.z) * (s * s) / (sx * sy);
    }
    return col;
}

// ── gravitational-wave sweep over the near layer ─────────────────────────────
// Each direction gets a smooth distance (3–140 ly). The wave reaches the object at |p|/c and its
// light reaches the camera |p − cam|/c later; we see the stretch-and-squeeze (h₊) then.
vec3 gwShift(vec3 d) {
    if (u_gwAmp <= 0.0) return d;
    float dly = exp(mix(log(3.0), log(140.0), clamp((fbm2(d * 0.09 + 0.71) - 0.25) * 2.0, 0.0, 1.0)));
    float tau = dly + length(d * dly - u_camLy);
    float x = log(max(u_Tyr, 1e-6) / tau) / 0.10;
    if (abs(x) > 4.0) return d;
    float h = u_gwAmp * exp(-0.5 * x * x) * sin(2.6 * x);
    vec2 q = tanCoords(d);
    float ps = 0.6;                                      // polarisation angle
    mat2 R = mat2(cos(ps), sin(ps), -sin(ps), cos(ps));
    vec2 qr = transpose(R) * q;
    qr += 0.5 * h * vec2(qr.x, -qr.y);
    return fromTan(R * qr);
}

void main() {
    vec3 d = viewDir(uv);
    bool esc;
    vec3 dOut = lensDir(d, esc);
    float fp = max(length(dFdx(dOut)), length(dFdy(dOut)));
    vec3 dNear = gwShift(dOut);
    vec3 col = vec3(0.0);
    if (esc && u_sky > 0.0) {
        float sigma = max(0.55 * fp, 0.5 * u_pix);
        col += galaxy(dOut, fp) * 0.75;
        col += galaxies(dOut, sigma);
        col += starLayer(dOut, 190.0, 0.13, 1.6, 0.0, sigma);           // far, faint, dense
        col += globular(dOut, sigma);
        col += nebula(dNear, 0, fp) + nebula(dNear, 1, fp) + nebula(dNear, 2, fp);
        col += starLayer(dNear, 34.0, 0.30, 9.0, 7.0, sigma);           // near, bright, sparse
        col += starLayer(dNear, 80.0, 0.22, 3.0, 3.0, sigma);
        col *= u_sky;
    }
    // photon ring: light that orbited at r = 3M arrives at b = √27 (a thin ring, width ~1 px)
    if (u_lensOn > 0.5) {
        float sinA = length(cross(d, u_camN));
        float b = u_rcM * sinA / sqrt(1.0 - 2.0 / u_rcM);
        float wb = max(fwidth(b), 1e-4) * 1.2;
        float x = (b - B_C) / wb;
        col += vec3(1.0, 0.80, 0.62) * 0.55 * exp(-x * x) * step(-dot(d, u_camN), 1.0);
    }
    o = vec4(col, 1.0);
}
