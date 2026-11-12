// Voyage: deep-sky objects and one foreground planet, spliced into aion's Schwarzschild ray tracer
// (voyage.py inserts this file before main() and calls voyageSky / vPlanet from it).
// Sky objects are sampled along the *lensed* ray direction, so the hole bends, doubles and rings them
// exactly like the stars. The planet is close to the camera and far from the hole: straight rays.
uniform float v_gain, v_time, v_plR, v_plAmt;
uniform vec3 v_nebA, v_nebB, v_snr, v_snrT1, v_snrT2, v_gal, v_galT1, v_galT2, v_psr, v_psrT1, v_psrT2;
uniform vec3 v_plC, v_plAxis, v_plSun;

// emission nebula: domain-warped gas, bright ionisation rims, dark dust lanes
vec3 vNebula(vec3 d, vec3 c, float R, vec3 colA, vec3 colB, float seed, float fp) {
    float ca = dot(d, c);
    if (ca < cos(min(R * 1.8, 3.0))) return vec3(0.0);
    float ang = acos(clamp(ca, -1.0, 1.0));
    float k = 2.6 / R;
    vec3 p = d * k + seed;
    float fs = fp * k;
    vec3 w = vec3(fbmLod(p + 1.3, fs), fbmLod(p + 7.1, fs), fbmLod(p + 3.7, fs));
    float n = fbmLod(p + 1.9 * (w - 0.5), fs);
    float n2 = fbmLod(p * 1.8 + 3.0 * w, fs * 1.8);
    float shape = exp(-1.8 * pow(ang / R, 2.0));
    float body = smoothstep(0.30, 0.78, n + 0.30 * shape) * shape;
    float fil = pow(clamp(1.0 - abs(n - 0.56) * 7.0, 0.0, 1.0), 4.0) * shape;
    float dust = smoothstep(0.52, 0.72, n2) * shape;
    vec3 col = mix(colA, colB, smoothstep(0.38, 0.66, n2));
    vec3 e = col * body * body * 1.6 + mix(colA, vec3(1.0), 0.35) * fil * 0.8;
    return e * (1.0 - 0.85 * dust);
}

// grand-design spiral galaxy, disk inclined 60°: two logarithmic arms, dust on their inner edge,
// pink star-forming knots, a warm bulge
vec3 vSpiral(vec3 d, float fp) {
    const float R = 0.115;
    if (dot(d, v_gal) < cos(2.2 * R)) return vec3(0.0);
    vec3 v = d - v_gal;
    vec2 q = vec2(dot(v, v_galT1), dot(v, v_galT2) / 0.5) / R;
    float r = length(q), th = atan(q.y, q.x);
    float fs = fp / R;
    float keep = 1.0 - smoothstep(0.08, 0.3, fs);        // structure finer than the lensed footprint averages out
    float n = fbmLod(vec3(q * 5.0, 2.7), fs * 5.0);
    float sw = 2.0 * (th - 2.4 * log(r + 0.04)) + 2.2 * (n - 0.5);
    float arm = mix(0.3, pow(0.5 + 0.5 * cos(sw), 2.0), keep);
    float lane = keep * pow(0.5 + 0.5 * cos(sw + 1.1), 6.0) * smoothstep(0.08, 0.3, r);
    float disk = exp(-3.4 * r) * smoothstep(1.25, 0.8, r);
    float bulge = exp(-pow(r / 0.11, 2.0));
    float knots = keep * pow(vnoise(vec3(q * 26.0, 5.0)), 7.0) * arm;
    vec3 col = vec3(0.50, 0.68, 1.0) * disk * (0.12 + 1.5 * arm * (0.4 + n)) * (1.0 - 0.75 * lane)
             + vec3(1.0, 0.80, 0.55) * (1.6 * bulge + 0.5 * exp(-9.0 * r))
             + vec3(1.0, 0.35, 0.5) * knots * disk * 5.0;
    return col * 0.5;
}

// supernova remnant: a thin, broken shell of shocked filaments (hydrogen red, oxygen teal)
vec3 vRemnant(vec3 d, float fp) {
    const float R = 0.075;
    if (dot(d, v_snr) < cos(1.7 * R)) return vec3(0.0);
    vec3 v = d - v_snr;
    vec2 q = vec2(dot(v, v_snrT1), dot(v, v_snrT2)) / R;
    float r = length(q), fs = fp / R;
    vec3 p = vec3(q * 1.6, 4.0);
    float n = fbmLod(p + 1.5 * vec3(fbmLod(p + 3.1, fs * 1.6), fbmLod(p + 8.7, fs * 1.6), 0.0), fs * 1.6);
    float rw = r + 0.55 * (n - 0.5);                                    // the blast wave met uneven gas
    float shell = exp(-pow((rw - 0.78) / 0.085, 2.0)) + 0.35 * exp(-pow((rw - 0.55) / 0.07, 2.0));
    float fil = pow(clamp(1.0 - abs(fbmLod(p * 3.4 + 1.7, fs * 5.5) - 0.5) * 6.0, 0.0, 1.0), 3.0);
    float gaps = smoothstep(0.38, 0.6, fbmLod(p * 0.9 + 21.0, fs * 1.5));   // parts of the shell are missing
    vec3 c = mix(vec3(1.0, 0.30, 0.24), vec3(0.30, 0.80, 0.90), smoothstep(0.42, 0.60, n));
    return c * shell * (0.05 + 1.3 * fil) * (0.25 + 0.75 * gaps) * 0.5 * smoothstep(1.6, 1.1, r);
}

// neutron star: a blue-white point with two lighthouse beams 65° off its spin axis; it flashes
// each time a beam sweeps across the line of sight
vec3 vPulsar(vec3 d, float sigma) {
    if (dot(d, v_psr) < 0.985) return vec3(0.0);
    vec3 v = d - v_psr;
    vec2 q = vec2(dot(v, v_psrT1), dot(v, v_psrT2));
    float r = length(q);
    float ph = v_time * TAU / 1.7;
    const float SA = 0.906, CA = 0.423;
    vec2 bq = vec2(SA * cos(ph), CA);
    float bz = SA * sin(ph), bl = length(bq);
    vec2 bh = bq / bl;
    float a = abs(dot(q, bh)), across = abs(q.x * bh.y - q.y * bh.x);
    float w = 0.0012 + 0.07 * a + sigma;
    float beam = exp(-pow(across / w, 2.0)) * exp(-a / (0.085 * bl)) * (0.0012 / w);
    float flash = pow(abs(bz) / SA, 10.0);
    float core = u_pix * u_pix / (TAU * sigma * sigma) * exp(-0.5 * r * r / (sigma * sigma)) * 14.0 * (1.0 + 5.0 * flash);
    float halo = exp(-r / 0.006) * 0.10 * (1.0 + 2.0 * flash);
    return vec3(0.62, 0.80, 1.0) * (core + halo + 0.9 * beam);
}

vec3 voyageSky(vec3 d, float fp) {
    float sigma = max(0.55 * fp, 0.5 * u_pix);
    vec3 c = 0.36 * vNebula(d, v_nebA, 0.34, vec3(1.0, 0.22, 0.30), vec3(0.20, 0.62, 0.75), 3.0, fp)
           + 0.30 * vNebula(d, v_nebB, 0.17, vec3(0.25, 0.45, 1.0), vec3(0.75, 0.50, 1.0), 11.0, fp);
    c += vSpiral(d, fp) + vRemnant(d, fp) + vPulsar(d, sigma) + 1.6 * galaxies(d, sigma) + supernova(d, sigma);
    return c;
}

// ── foreground: a ringed ice giant ───────────────────────────────────────────
float ringDensity(float rr, float w) {
    float bands = 0.50 + 0.50 * vnoise(vec3(rr * 23.0, 1.0, 2.0));
    bands *= 1.0 - 0.9 * exp(-pow((rr - 1.95) / 0.035, 2.0));                 // a gap
    bands = mix(bands, 0.5, smoothstep(0.02, 0.12, w));
    return bands * smoothstep(1.30 - w, 1.38 + w, rr) * smoothstep(2.36 + w, 2.28 - w, rr);
}
vec3 vPlanet(vec3 col, vec3 ro, vec3 rd) {
    if (v_plAmt <= 0.0) return col;
    vec3 oc = ro - v_plC;
    float tb = -dot(oc, rd);
    float q2 = dot(oc, oc) - tb * tb;
    float aP = 0.0, tS = 1e9;
    vec3 pc = vec3(0.0);
    if (tb > 0.0) {
        float wpx = u_pix * tb;
        aP = 1.0 - smoothstep(v_plR - wpx, v_plR + wpx, sqrt(max(q2, 0.0)));
        tS = tb - sqrt(max(v_plR * v_plR - q2, 0.0));
    }
    if (aP > 0.0) {
        vec3 ps = ro + rd * tS - v_plC;
        vec3 n = normalize(ps);
        float lat = dot(n, v_plAxis);
        vec3 e1 = normalize(cross(v_plAxis, vec3(0.3, 0.1, 0.9))), e2 = cross(v_plAxis, e1);
        float lon = atan(dot(n, e2), dot(n, e1));
        float turb = fbm(vec3(cos(lon) * 2.0, sin(lon) * 2.0, lat * 7.0));
        float b1 = vnoise(vec3(lat * 7.0 + 1.2 * (turb - 0.5), 0.5, 0.5));
        float b2 = vnoise(vec3(lat * 19.0 + 2.0 * (turb - 0.5), 3.5, 0.5));
        vec3 alb = mix(vec3(0.16, 0.30, 0.48), vec3(0.62, 0.76, 0.82), smoothstep(0.3, 0.7, b1)) * (0.8 + 0.4 * b2);
        alb *= 1.0 - 0.35 * lat * lat;
        float mu = dot(n, v_plSun);
        float shade = 1.0;                                    // the rings' shadow on the cloud tops
        float sn = dot(v_plSun, v_plAxis);
        float ts = -dot(ps, v_plAxis) / (abs(sn) > 1e-4 ? sn : 1e-4);
        if (ts > 0.0) shade -= 0.75 * ringDensity(length(ps + v_plSun * ts) / v_plR, 0.01);
        float fres = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
        pc = alb * smoothstep(-0.05, 0.9, mu) * 0.5 * shade
           + vec3(0.35, 0.60, 1.0) * fres * smoothstep(-0.25, 0.3, mu) * 0.45
           + vec3(0.003, 0.005, 0.009);
    }
    float dn = dot(rd, v_plAxis);
    float tR = dot(v_plC - ro, v_plAxis) / (abs(dn) > 1e-5 ? dn : 1e-5);
    float aR = 0.0;
    vec3 rcol = vec3(0.0);
    if (tR > 0.0) {
        vec3 pr = ro + rd * tR - v_plC;
        float rr = length(pr) / v_plR;
        aR = 0.85 * ringDensity(rr, u_pix * tR / (v_plR * max(abs(dn), 0.05)));
        float sb = dot(pr, v_plSun);
        float lit = 1.0 - 0.96 * step(sb, 0.0) * smoothstep(v_plR * 1.03, v_plR * 0.95, length(pr - sb * v_plSun));
        rcol = vec3(0.80, 0.72, 0.60) * (0.30 + 0.70 * abs(dot(v_plAxis, v_plSun))) * lit * 0.5;
    }
    aP *= v_plAmt; aR *= v_plAmt;
    if (tR > 0.0 && tR < tS) { col = mix(col, pc, aP); col = mix(col, rcol, aR); }
    else                     { col = mix(col, rcol, aR); col = mix(col, pc, aP); }
    return col;
}
