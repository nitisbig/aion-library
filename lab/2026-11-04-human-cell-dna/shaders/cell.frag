// Human cell, raymarched in µm. Every membrane is a thin emissive shell (gaussian in its SDF), so grazing rays
// glow brighter: the fresnel-rim, x-ray look of bioluminescent microscopy. Volumes (cytoplasm haze, ribosomes,
// chromatin, nucleoli) are emissive densities. Output: rgb = HDR colour, a = emission-weighted depth (for DOF).
in vec2 uv;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_H, u_time; uniform vec2 u_res;

uniform float CELL_R; uniform vec3 SQUASH;
uniform vec3 NUC_C; uniform float NUC_R, GAP, PORE_R, PORE_H;
uniform vec4 NUCLEOLI[2];
uniform vec3 GOLGI_DIR, CENTRO;
uniform vec4 MITO[28];      // a.xyz r | b.xyz phase
uniform vec4 VES[52];       // c.xyz r | kind phase - -
uniform vec4 MT[22];        // end.xyz phase
uniform vec4 MOTES[40];     // pos.xyz brightness

uniform vec3 C_MEM, C_CYTO, C_RIBO, C_ENV, C_PORE, C_CHROM, C_NUCLEOLUS, C_ER, C_GOLGI, C_MITO, C_CRISTA,
             C_LYSO, C_VES, C_MT, C_MOTE;
uniform float u_gain; uniform int u_off;
out vec4 o;

const float PI = 3.14159265;

// ── noise ──
float h31(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.x + p.y) * p.z); }
vec3 h33(vec3 p) {
    p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33);
    return fract((p.xxy + p.yxx) * p.zyx);
}
float vnoise(vec3 p) {        // value noise in [-1, 1]
    vec3 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float n000 = h31(i), n100 = h31(i + vec3(1, 0, 0)), n010 = h31(i + vec3(0, 1, 0)), n110 = h31(i + vec3(1, 1, 0));
    float n001 = h31(i + vec3(0, 0, 1)), n101 = h31(i + vec3(1, 0, 1)), n011 = h31(i + vec3(0, 1, 1)), n111 = h31(i + vec3(1, 1, 1));
    return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y), mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z) * 2.0 - 1.0;
}
float fbm2(vec3 p) { return vnoise(p) * 0.65 + vnoise(p * 2.03 + 7.1) * 0.35; }

float sdCapsule(vec3 p, vec3 a, vec3 b, float r, out float h) {
    vec3 pa = p - a, ba = b - a;
    h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}
float sdSeg(vec3 p, vec3 a, vec3 b) { vec3 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0); return length(pa - ba * h); }

// ── nuclear pore lattice (mirrors anatomy.pore_lattice) ──
vec3 poreDir(int row, int col, int nrows) {
    float lat = -PI / 2.0 + (float(row) + 0.5) * PI / float(nrows);
    int ncol = max(int(floor(2.0 * PI * cos(lat) / PORE_H)), 1);
    uint hsh = ((uint(row) * 73856093u) ^ (uint(col) * 19349663u)) & 1023u;
    float jit = (float(hsh) / 1023.0 - 0.5) * 0.5;
    float lon = (float(col) + 0.5 + jit + 0.5 * float(row % 2)) * 2.0 * PI / float(ncol);
    uint h2 = ((uint(col) * 83492791u) ^ (uint(row) * 2654435u)) & 1023u;
    lat += (float(h2) / 1023.0 - 0.5) * 0.4 * PI / float(nrows);
    return vec3(cos(lat) * cos(lon), sin(lat), cos(lat) * sin(lon));
}
// distance (µm, tangential) to the nearest pore centre on the envelope, and that pore's direction
float nearestPore(vec3 n, out vec3 pd) {
    int nrows = int(floor(PI / PORE_H));
    float lat = asin(clamp(n.y, -1.0, 1.0));
    float lon = atan(n.z, n.x); if (lon < 0.0) lon += 2.0 * PI;
    int row0 = int(floor((lat + PI / 2.0) / PI * float(nrows)));
    float best = 1e9; pd = n;
    for (int dr = -1; dr <= 1; dr++) {
        int row = row0 + dr;
        if (row < 0 || row >= nrows) continue;
        float latr = -PI / 2.0 + (float(row) + 0.5) * PI / float(nrows);
        int ncol = max(int(floor(2.0 * PI * cos(latr) / PORE_H)), 1);
        float fc = lon / (2.0 * PI) * float(ncol) - 0.5 - 0.5 * float(row % 2);
        int c0 = int(floor(fc + 0.5));
        for (int dc = -1; dc <= 1; dc++) {
            int col = ((c0 + dc) % ncol + ncol) % ncol;
            vec3 d = poreDir(row, col, nrows);
            float ch = length(n - d);
            if (ch < best) { best = ch; pd = d; }
        }
    }
    return best * NUC_R;
}

// accumulated state
vec3 E; float A; float Dmin;
float PIX;
void shell(float d, float th, vec3 col, float I, float absorb) {
    float w = max(th, PIX * 1.3);
    float g = exp(-(d * d) / (w * w)) / w;
    E += col * g * I;
    A += g * absorb;
    Dmin = min(Dmin, max(abs(d) - w, 0.0));
}
void dens(float rho, vec3 col, float absorb) { E += col * rho; A += rho * absorb; }

vec3 cellSpace(vec3 p) { return p / SQUASH; }

void sampleAt(vec3 p, float t) {
    // cell membrane: a lumpy ellipsoid that slowly breathes
    vec3 q = cellSpace(p);
    float rr = length(q);
    float lump = 0.55 * vnoise(p * 0.16 + vec3(0.0, 0.03 * u_time, 0.0)) + 0.18 * vnoise(p * 0.45 + 3.0);
    float dCell = (rr - CELL_R - lump) * 0.8;
    float camOut = 0.15 + 0.85 * smoothstep(CELL_R - 1.5, CELL_R + 0.5, length(cellSpace(u_cam)));
    if ((u_off & 1) == 0) shell(dCell, 0.012, C_MEM, 0.014 * camOut, 0.03);
    if (dCell > 0.0) return;

    // ── nucleus ──
    vec3 pn = p - NUC_C;
    float rn = length(pn);
    vec3 nn = pn / max(rn, 1e-6);
    float dN = rn - NUC_R;
    if (abs(dN) < 0.35 && (u_off & 2) == 0) {
        vec3 pd;
        float dp = nearestPore(nn, pd);
        float hole = smoothstep(PORE_R * 0.72, PORE_R * 1.02, dp);
        shell(dN, 0.006, C_ENV, 0.025 * hole, 0.1 * hole);
        shell(dN - GAP, 0.006, C_ENV, 0.025 * hole, 0.1 * hole);
        // pore complex: 8-fold ring (torus) + central transport channel
        vec3 t1 = normalize(cross(pd, abs(pd.y) < 0.9 ? vec3(0, 1, 0) : vec3(1, 0, 0)));
        vec3 t2 = cross(pd, t1);
        vec3 pj = nn - pd * dot(nn, pd);
        float psi = atan(dot(pj, t2), dot(pj, t1));
        float u = dN - GAP * 0.5;
        float ring = length(vec2(dp - PORE_R * 0.92, u)) - 0.016 * (1.0 + 0.35 * cos(8.0 * psi));
        float far = smoothstep(0.9, 0.25, PIX / PORE_R);
        shell(ring, 0.004, C_PORE, 0.07 * (0.25 + 0.75 * far) * (0.35 + 0.65 * smoothstep(0.05, 0.4, t)), 0.2);
        float ch = exp(-(dp * dp) / (0.022 * 0.022)) * exp(-(u * u) / (0.03 * 0.03));
        dens(ch * 0.8, C_PORE, 0.0);
        Dmin = min(Dmin, max(ring - 0.01, 0.0));
    } else {
        Dmin = min(Dmin, abs(dN) - 0.3);
    }
    if (dN < 0.0) {
        if ((u_off & 4) != 0) return;
        A += 0.55 * smoothstep(0.0, -0.1, dN);          // dense nucleoplasm hides the far envelope
        // chromatin: threads where two noise fields both cross zero; finer threads appear close to the camera
        vec3 pc = pn * 2.3 + vec3(0.0, 0.02 * u_time, 0.0);
        float n1 = vnoise(pc), n2 = vnoise(pc + vec3(17.3, 4.1, 9.7));
        float th = 0.016 + min(PIX * 0.4, 0.03);
        float thread = exp(-(n1 * n1 + n2 * n2) / th);
        float near = 1.0 - smoothstep(0.6, 3.0, t);
        float fine = 0.0;
        if (near > 0.0) {
            vec3 pf = pn * 9.0;
            float m1 = vnoise(pf + 3.3), m2 = vnoise(pf + vec3(1.7, 8.2, 5.5));
            fine = exp(-(m1 * m1 + m2 * m2) / (0.016 + min(PIX * 3.0, 0.03))) * near;
        }
        float terr = 0.55 + 0.45 * vnoise(pn * 0.7 + 11.0);
        dens((thread * 0.9 * terr + fine * 1.4 + 0.004) * smoothstep(0.0, -0.08, dN), C_CHROM, 0.6);
        for (int k = 0; k < 2; k++) {
            vec4 nl = NUCLEOLI[k];
            float dl = length(pn - nl.xyz) - nl.w * (1.0 + 0.12 * fbm2(pn * 2.5 + float(k) * 5.0));
            float core = smoothstep(0.05, -0.25, dl) * (0.6 + 0.4 * fbm2(pn * 6.0));
            dens(core * 0.07, C_NUCLEOLUS, 1.0);
            shell(dl, 0.02, C_NUCLEOLUS, 0.03, 0.05);
        }
        return;
    }

    // ── cytoplasm ──
    if ((u_off & 8) == 0) {
    float haze = 0.0004 * (0.6 + 0.4 * vnoise(p * 0.4 + 2.0));
    dens(haze, C_CYTO, 0.02);
    // free ribosomes: jittered grid of tiny glints (~25 nm)
    {
        vec3 g = p * 6.0;
        vec3 ci = floor(g);
        vec3 j = h33(ci);
        if (j.x > 0.55) {
            vec3 lp = (fract(g) - 0.5 - (j - 0.5) * 0.6) / 6.0;
            float w = max(0.0125, PIX * 0.9);
            float d = length(lp);
            dens(exp(-(d * d) / (w * w)) * 0.025 / w * 0.02, C_RIBO, 0.0);
        }
    }
    }

    // rough ER: patchy folded sheets around the nucleus, studded with ribosomes
    if (dN < 2.6 && (u_off & 16) == 0) {
        float warp = rn + 0.38 * vnoise(p * 0.7 + 1.0);
        float sp = 0.42;
        float x = (warp - NUC_R - 0.3) / sp;
        float dEr = (abs(fract(x) - 0.5)) * sp;
        float m = smoothstep(-0.15, 0.25, vnoise(p * 0.45 + 5.0)) * smoothstep(NUC_R + 2.4, NUC_R + 1.6, warp)
                * smoothstep(NUC_R + 0.15, NUC_R + 0.35, warp);
        float gaway = smoothstep(0.55, 0.85, dot(nn, normalize(GOLGI_DIR)));
        m *= 1.0 - gaway;
        if (m > 0.01) {
            vec3 gr = p * 11.0 + vnoise(p * 3.0) * 0.5;
            vec3 jj = h33(floor(gr));
            float dots = step(0.45, jj.y) * smoothstep(0.22, 0.0, length(fract(gr) - 0.5 - (jj - 0.5) * 0.55));
            shell(dEr - 0.01, 0.014, C_ER, 0.012 * m, 0.04 * m);
            shell(dEr - 0.01, 0.03, C_RIBO, 0.05 * m * dots, 0.0);
        } else Dmin = min(Dmin, 0.15);
    }

    // Golgi: 6 curved cisternae, concave toward the nucleus, with swollen rims
    if ((u_off & 32) == 0) {
        vec3 g = normalize(GOLGI_DIR);
        vec3 gc = NUC_C + g * (NUC_R + 2.3);
        vec3 cs = gc - g * 3.0;
        float rr2 = length(p - cs);
        float k = clamp(floor((rr2 - 2.6) / 0.17 + 0.5), 0.0, 5.0);
        float d = abs(rr2 - 2.6 - k * 0.17) - 0.02;
        vec3 lp = p - gc;
        float lat = length(lp - g * dot(lp, g));
        float capR = 1.35 - 0.12 * abs(k - 2.5) + 0.15 * vnoise(p * 3.0);
        float dG = max(d, lat - capR);
        float rim = smoothstep(capR - 0.2, capR, lat);
        shell(dG, 0.01 + rim * 0.03, C_GOLGI, 0.05 * (1.0 + rim), 0.08);
        Dmin = min(Dmin, max(dG, 0.0) * 0.8);
    }

    // mitochondria: outer membrane, inner membrane, cristae folds
    for (int i = 0; i < 14 && (u_off & 64) == 0; i++) {
        vec4 a = MITO[2 * i], b = MITO[2 * i + 1];
        float h;
        float wob = 0.03 * sin(u_time * 0.8 + b.w * 6.28);
        float dm = sdCapsule(p, a.xyz, b.xyz, a.w + wob, h);
        Dmin = min(Dmin, max(dm - 0.05, 0.0));
        if (dm > 0.1) continue;
        shell(dm, 0.008, C_MITO, 0.06, 0.12);
        shell(dm + 0.035, 0.006, C_MITO, 0.035, 0.06);
        vec3 ax = normalize(b.xyz - a.xyz);
        float L = length(b.xyz - a.xyz) + 2.0 * a.w;
        float s = (dot(p - a.xyz, ax) + a.w) / 0.17 + b.w * 3.0 + 0.25 * sin(dot(p, vec3(7.0, 5.0, 3.0)));
        float plate = abs(fract(s) - 0.5) * 0.17;
        float dc = max(plate - 0.006, max(dm + 0.04, -(dm + a.w * 0.8)));
        shell(dc, 0.006, C_CRISTA, 0.06, 0.08);
        dens(smoothstep(0.0, -0.05, dm) * 0.015, C_MITO, 0.3);
    }

    // vesicles and lysosomes
    for (int i = 0; i < 26 && (u_off & 128) == 0; i++) {
        vec4 c = VES[2 * i], m = VES[2 * i + 1];
        vec3 cc = c.xyz + 0.08 * vec3(sin(u_time * 0.5 + m.y * 30.0), cos(u_time * 0.4 + m.y * 20.0), 0.0);
        float d = length(p - cc) - c.w;
        Dmin = min(Dmin, max(d - 0.03, 0.0));
        if (d > 0.08) continue;
        vec3 col = m.x > 0.5 ? C_LYSO : C_VES;
        shell(d, 0.007, col, 0.06, 0.1);
        dens(smoothstep(0.0, -0.08, d) * (m.x > 0.5 ? 0.03 : 0.01) * (0.6 + 0.4 * vnoise(p * 9.0)), col, 0.5);
    }

    // centrosome: two perpendicular centrioles + radiating microtubules
    {
        float h;
        float d1 = sdCapsule(p, CENTRO - vec3(0.0, 0.0, 0.22), CENTRO + vec3(0.0, 0.0, 0.22), 0.1, h);
        float d2 = sdCapsule(p, CENTRO + vec3(0.12, -0.25, 0.0), CENTRO + vec3(0.12, 0.2, 0.0), 0.1, h);
        float dc = min(d1, d2);
        shell(dc, 0.01, C_MT, 0.12, 0.15);
        dens(exp(-dot(p - CENTRO, p - CENTRO) / 0.25) * 0.01, C_MT, 0.0);
        Dmin = min(Dmin, max(dc - 0.04, 0.0));
        for (int i = 0; i < 22; i++) {
            vec4 e = MT[i];
            float d = sdSeg(p, CENTRO, e.xyz);
            shell(d, 0.0125, C_MT, 0.02, 0.0);
            Dmin = min(Dmin, max(d - 0.02, 0.0));
        }
    }
}

void main() {
    vec2 ndc = gl_FragCoord.xy / u_res * 2.0 - 1.0;
    vec3 rd = normalize(u_fwd + ndc.x * u_tanHalf * u_aspect * u_right + ndc.y * u_tanHalf * u_up);
    vec3 ro = u_cam;
    E = vec3(0.0); A = 0.0;
    vec3 col = vec3(0.0);
    float T = 1.0, zsum = 0.0, wsum = 0.0;
    float pixAng = 2.0 * u_tanHalf / u_H;

    // drifting motes outside the cell (shallow-focus particles)
    for (int i = 0; i < 40; i++) {
        vec4 m = MOTES[i];
        vec3 mp = m.xyz + vec3(sin(u_time * 0.13 + float(i)), cos(u_time * 0.11 + float(i) * 1.7), 0.0) * 1.5;
        vec3 v = mp - ro;
        float tz = dot(v, rd);
        if (tz <= 0.0) continue;
        float d = length(v - rd * tz);
        float w = max(0.05, tz * pixAng * 1.2);
        float g = exp(-(d * d) / (w * w)) * m.w * min(0.05 / w, 1.0);
        col += C_MOTE * g;
        zsum += tz * g; wsum += g;
    }

    // ray vs. cell bounding sphere
    float Rb = CELL_R * 1.12;
    float bq = dot(ro, rd), cq = dot(ro, ro) - Rb * Rb;
    float disc = bq * bq - cq;
    if (disc > 0.0) {
        float sd = sqrt(disc);
        float t0 = max(-bq - sd, 0.0), t1 = -bq + sd;
        float t = t0 + h31(vec3(gl_FragCoord.xy, 1.0)) * 0.002 * max(t0, 0.1);
        for (int it = 0; it < 320 && t < t1; it++) {
            vec3 p = ro + rd * t;
            PIX = t * pixAng;
            E = vec3(0.0); A = 0.0; Dmin = 1e9;
            sampleAt(p, t);
            float stepMax = clamp(0.05 * t, 0.002, 0.3);
            float dt = clamp(Dmin * 0.7, PIX * 0.9, stepMax);
            dt = max(dt, 0.0015);
            vec3 em = E * u_gain * dt;
            col += T * em;
            float lum = dot(em, vec3(0.3, 0.5, 0.2)) * T;
            zsum += lum * t; wsum += lum;
            T *= exp(-A * dt);
            if (T < 0.02) break;
            t += dt;
        }
    }
    float depth = wsum > 1e-6 ? zsum / wsum : 1e6;
    o = vec4(col, depth);
}
