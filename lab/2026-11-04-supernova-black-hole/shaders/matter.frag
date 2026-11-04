// Everything made of matter: the red supergiant (surface + cut-away onion shells), the collapsing
// iron core, the proto-neutron star, the shock, the black hole's shadow (before the lensing pass
// takes over), the ejecta photosphere, the remnant (ray-marched, lensed) and the neutrino streaks.
// All lengths are in units of the camera distance D (the remnant: in units of its own radius).
// Output: premultiplied RGBA, composited over the sky.
in vec2 uv;
out vec4 o;

uniform float u_time, u_T;
uniform float u_Rs, u_cut, u_starOn;
uniform float u_shell[6];
uniform vec3 u_shellCol[6];
uniform float u_Teff, u_flash;
uniform float u_core, u_coreMode, u_coreHeat, u_bounceFlash, u_shadow;
uniform float u_shock, u_stalled, u_sasiA, u_sasiPh, u_postShock;
uniform float u_ej, u_ejT, u_ejOp, u_ejI, u_blast;
uniform float u_rem, u_remNeb, u_remGlow;
uniform float u_nuOn, u_nuS, u_nuEnd;

const vec3 SASI_AXIS = vec3(0.27, 0.93, -0.25);

// ── ray / solid intersection: sphere minus the cut-away octant {x > c, y > c, z > c} ──
// kind: 0 miss, 1 outer surface, 2 cut face (axis = face normal index)
float hitStar(vec3 ro, vec3 rd, float R, float c, out int kind, out int axis) {
    kind = 0; axis = -1;
    float b = dot(ro, rd), cc = dot(ro, ro) - R * R;
    float disc = b * b - cc;
    if (disc < 0.0) return -1.0;
    float sq = sqrt(disc);
    float t0 = -b - sq, t1 = -b + sq;
    if (t1 <= 0.0) return -1.0;
    t0 = max(t0, 0.0);
    float tn0 = -1e30, tn1 = 1e30;
    int ax = -1;
    for (int i = 0; i < 3; i++) {
        float oi = ro[i], di = rd[i];
        if (abs(di) < 1e-9) { if (oi <= c) tn0 = 1e30; continue; }
        float th = (c - oi) / di;
        if (di > 0.0) tn0 = max(tn0, th);
        else if (th < tn1) { tn1 = th; ax = i; }
    }
    if (tn0 < tn1 && tn0 <= t0 && tn1 > t0) {            // the sphere is entered inside the cut
        if (tn1 < t1) { kind = 2; axis = ax; return tn1; }
        return -1.0;
    }
    kind = 1;
    return t0;
}
float hitSphere(vec3 ro, vec3 rd, float R) {
    float b = dot(ro, rd), cc = dot(ro, ro) - R * R;
    float disc = b * b - cc;
    if (disc < 0.0) return -1.0;
    float t0 = -b - sqrt(disc);
    return t0 > 0.0 ? t0 : -1.0;
}

// ── the onion ────────────────────────────────────────────────────────────────
vec3 shellColor(float re, float w) {
    vec3 c = u_shellCol[0];
    for (int k = 0; k < 5; k++) c = mix(c, u_shellCol[k + 1], smoothstep(-w, w, log(re / u_shell[k])));
    return c;
}
float shellRims(float re, float w) {
    float s = 0.0;
    for (int k = 0; k < 5; k++) {
        float x = log(re / u_shell[k]) / (0.0045 + w);
        s += exp(-x * x);
    }
    return s;
}
// brightness: inner shells hotter
float shellHeat(float re) {
    float h = 1.0;
    for (int k = 0; k < 5; k++) h += 0.16 * step(re, u_shell[k]);
    return h;
}

vec3 saturate(vec3 c, float k) {
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return max(mix(vec3(l), c, k), 0.0);
}

vec3 interior(vec3 p, float w) {
    float r = length(p);
    vec3 dir = p / r;
    float lr = log(r);
    // texture coordinates that scale with r: the pattern is self-similar under the log zoom
    vec3 q = (dir + vec3(0.36, 0.80, 0.48) * lr) * 0.55;
    float wob = (texture(u_noise, dir * 0.45 + vec3(0.0, 0.0, 0.11 * lr)).r - 0.5) * 0.10;
    float re = r * exp(wob);
    vec4 nz = N4(q);
    float cells = nz.g;
    float gran = ridged(N4(q * 2.7 + 0.31).b);
    float tex = 0.42 + 0.50 * smoothstep(0.2, 0.8, cells) - 0.18 * (1.0 - gran);
    vec3 col = shellColor(re, w) * tex * shellHeat(re) * 0.42;
    col += mix(shellColor(re, w), vec3(1.0), 0.5) * shellRims(re, w) * 0.5;
    // iron heats as it is compressed
    float inFe = 1.0 - smoothstep(-w, w, log(re / u_shell[0]));
    col *= mix(1.0, u_coreHeat, inFe);
    // inward streaming during the collapse (radial streaks sliding toward the centre)
    if (u_T < 0.0) {
        float fall = N4(vec3(dir.xy * 6.0, lr * 0.25 + u_time * 0.35)).a;
        col *= 0.85 + 0.3 * smoothstep(0.4, 0.9, fall) * smoothstep(-0.3, -0.02, u_T);
    }
    // shocked matter: fingers of inner material pushed outward (Rayleigh–Taylor), hot
    if (u_shock > 0.0) {
        float sasi = 1.0 + u_sasiA * dot(dir, normalize(SASI_AXIS)) * sin(u_sasiPh);
        float rsh = u_shock * sasi * (1.0 + 0.10 * (N(dir * 0.7 + 0.5) - 0.5));
        float x = log(r / rsh);
        float inside = 1.0 - smoothstep(-w - 0.004, w + 0.004, x);
        // Rayleigh–Taylor fingers: inner material pushed outward, strongest just behind the front
        vec3 qf = (dir * 1.4 + vec3(0.36, 0.80, 0.48) * lr * 0.5) * 0.7;      // radially stretched 2:1
        float fing = pow(ridged(N4(qf).r), 3.0) * smoothstep(-0.9, -0.05, x);
        vec3 mixc = saturate(shellColor(r * exp(-1.2 * fing - 0.1), w), 1.6);
        // hot, billowing post-shock gas (isotropic cells, temperature falling toward the front)
        vec3 qb = (dir + vec3(0.36, 0.80, 0.48) * lr) * 0.9 + vec3(0.0, 0.0, u_T * 1.5);
        float billow = fbm2(qb);
        float Tg = mix(2400.0, 7000.0, clamp(0.10 + 0.95 * pow(billow, 1.4) * exp(x * 0.35), 0.0, 1.0));
        vec3 hot = saturate(blackbody(Tg), 1.8) * (0.10 + 0.65 * pow(billow, 1.6));
        hot = mix(hot, mixc * (0.25 + 0.35 * billow), 0.12 + 0.5 * fing);
        hot = mix(hot, vec3(1.0, 0.55, 0.22) * (0.3 + 1.1 * billow), u_stalled * 0.6);
        hot *= 1.0 + 0.6 * exp(x / 0.06);                                       // glow just behind the front
        col = mix(col, hot, inside * u_postShock);
        col += vec3(0.75, 0.88, 1.0) * exp(-pow(x / (0.008 + w), 2.0)) * 1.6 * u_postShock;     // the shock front
    }
    return col;
}

// ── red-supergiant surface ───────────────────────────────────────────────────
vec3 surface(vec3 n, vec3 rd) {
    float mu = max(dot(n, -rd), 0.0);
    float big = fbm2(n * 0.32 + vec3(0.0, u_time * 0.0012, 0.0));
    float gran = ridged(N4(n * 1.25 + 0.2).g);
    float cells = 0.62 * smoothstep(0.25, 0.8, big) + 0.38 * gran;
    float T = u_Teff * (0.92 + 0.13 * cells);
    float limb = 1.0 - 0.8 * (1.0 - pow(mu, 0.7));
    vec3 c = saturate(blackbody(T * 0.93), 1.6) * limb * (0.45 + 0.85 * cells) * 0.26;
    c += blackbody(36000.0) * u_flash * 14.0 * (0.55 + 0.45 * cells) * (0.4 + 0.6 * limb);
    return c;
}

// ── ejecta photosphere ───────────────────────────────────────────────────────
vec3 photosphere(vec3 n, vec3 rd) {
    float mu = max(dot(n, -rd), 0.0);
    float clumps = fbm2(n * 0.7 + 0.3);
    float rt = ridged(N4(n * 2.2 + 0.7).b);
    float T = u_ejT * (0.9 + 0.2 * clumps);
    float limb = 1.0 - 0.6 * (1.0 - mu);
    float hotspots = pow(rt, 4.0) * u_blast;                    // Rayleigh–Taylor plumes punching out
    return blackbody(T * (1.0 + 0.25 * hotspots)) * u_ejI * limb * (0.55 + 0.45 * clumps + 0.25 * rt + 1.4 * hotspots);
}

// ── supernova remnant: knots, filaments and the forward shock, in units of its radius ──
vec3 remnant(vec3 ro, vec3 rd) {
    float b = dot(ro, rd), cc = dot(ro, ro) - 1.08 * 1.08;
    float disc = b * b - cc;
    if (disc < 0.0) return vec3(0.0);
    float sq = sqrt(disc);
    float t0 = max(-b - sq, 0.0), t1 = -b + sq;
    if (t1 <= 0.0) return vec3(0.0);
    const int STEPS = 44;
    float dt = (t1 - t0) / float(STEPS);
    float j = hash12(gl_FragCoord.xy);
    vec3 acc = vec3(0.0);
    for (int i = 0; i < STEPS; i++) {
        vec3 p = ro + rd * (t0 + (float(i) + j) * dt);
        float r = length(p);
        if (r < 0.40) continue;
        float shell = smoothstep(0.42, 0.72, r) * smoothstep(1.02, 0.90, r);
        vec4 nz = N4(p * 0.42 + 0.1);
        float fil = pow(ridged(nz.r), 7.0);
        float knots = smoothstep(0.66, 0.86, N4(p * 1.1 + 0.5).g);
        vec3 neb = vec3(1.0, 0.36, 0.14) * (0.12 + 1.2 * fil) * shell;
        vec3 ha = vec3(1.0, 0.16, 0.22) * fil * smoothstep(0.70, 0.95, r) * smoothstep(1.02, 0.94, r);
        vec3 o3 = vec3(0.12, 0.72, 0.85) * knots * knots * (0.08 + 1.4 * fil) * smoothstep(0.48, 0.75, r) * smoothstep(0.98, 0.78, r);
        float fs = exp(-pow((r - 1.0) / 0.012, 2.0)) * (0.35 + 0.65 * N(p * 0.9 + 0.2));
        vec3 x = vec3(0.45, 0.62, 1.0) * fs;
        acc += (u_remNeb * neb + u_remGlow * (1.5 * ha + 1.8 * o3 + 0.5 * x)) * dt;
    }
    return acc * 1.3;
}

// ── neutrino streaks (screen-radial lines from the core; emission stops when the hole forms) ──
vec3 neutrinos(vec3 d) {
    vec2 q = tanCoords(d);
    float rho = length(q), th = atan(q.y, q.x);
    const float NBIN = 260.0;
    float fb = (th + PI) / TAU * NBIN;
    float cell = floor(fb);
    vec3 col = vec3(0.0);
    float w = 0.75 * u_pix * u_ss;
    for (int k = -1; k <= 1; k++) {
        float ci = mod(cell + float(k), NBIN);
        for (int m = 0; m < 2; m++) {
            vec3 h = hash33(vec3(ci, float(m), 19.0));
            float se = h.x * u_nuEnd;                      // emission time after bounce (screen s)
            float age = u_nuS - se;
            if (age < 0.0) continue;
            float thc = (ci + 0.5 + 0.8 * (h.y - 0.5)) / NBIN * TAU - PI;
            float head = 0.015 + age * (0.55 + 0.5 * h.z);
            float len = 0.04 + 0.30 * age;
            float dth = mod(th - thc + PI, TAU) - PI;
            float perp = abs(dth) * rho;
            float along = clamp((rho - (head - len)) / len, 0.0, 1.0) * step(rho, head);
            col += vec3(0.50, 0.72, 1.0) * exp(-pow(perp / w, 2.0)) * along * along * (0.35 / (1.0 + 1.5 * age));
        }
    }
    return col;
}

void main() {
    vec3 rd = viewDir(uv);
    vec3 ro = u_camN;
    vec3 col = vec3(0.0);
    float alpha = 0.0;
    float thC = acos(clamp(dot(rd, -ro), -1.0, 1.0));   // angle from the centre

    // 1) ejecta photosphere (encloses everything else while opaque)
    if (u_ej > 0.0 && u_ejOp > 0.0) {
        float te = hitSphere(ro, rd, u_ej);
        if (te > 0.0) {
            vec3 n = normalize(ro + rd * te);
            col += photosphere(n, rd) * u_ejOp;
            alpha = u_ejOp;
        }
        float pb = length(cross(ro, rd));                 // scattering halo just outside the limb
        if (pb > u_ej) {
            col += blackbody(u_ejT) * u_ejI * 0.25 * exp(-(pb - u_ej) / (0.06 * u_ej)) * u_ejOp;
            // blast corona: hot gas racing ahead of the photosphere, broken into radial rays
            if (u_blast > 0.0) {
                float x = (pb - u_ej) / u_ej;
                // rays: noise in the angle around the line of sight to the centre (radial on screen)
                vec3 a0 = normalize(ro);
                vec3 e1 = normalize(cross(a0, vec3(0.0, 1.0, 0.0))), e2 = cross(a0, e1);
                float th = atan(dot(rd, e2), dot(rd, e1));
                float rays = pow(N4(vec3(cos(th), sin(th), 0.0) * 2.2 + vec3(0.3, 0.6, x * 0.05)).r, 4.0) * 1.6;
                col += blackbody(u_ejT) * u_ejI * u_blast * (0.5 * exp(-x / 0.12) + 1.4 * rays * exp(-x / 0.5));
            }
        }
    }

    // 2) the star: surface, cut faces, core dome, shadow
    if (u_starOn > 0.0 && alpha < 0.999) {
        int kind, axis;
        float t = hitStar(ro, rd, u_Rs, u_cut, kind, axis);
        float tc = u_core > 0.0 ? hitSphere(ro, rd, u_core) : -1.0;
        float tb = (u_shadow > 0.0 && u_lensOn < 0.5) ? hitSphere(ro, rd, u_shadow) : -1.0;
        vec3 c = vec3(0.0);
        float a = 0.0;
        // anti-aliasing width in log r on the faces
        vec3 pf = ro + rd * max(t, 0.0);
        float w = fwidth(log(max(length(pf), 1e-30)));
        w = clamp(w, 0.0, 0.2);
        if (tb > 0.0) {
            c = vec3(0.0); a = 1.0;                       // the newborn black hole's shadow
        } else if (tc > 0.0) {
            vec3 n = normalize(ro + rd * tc);
            float mu = max(dot(n, -rd), 0.0);
            if (u_coreMode < 0.5) {
                float g = fbm2(n * 0.9 + 0.4);
                c = u_shellCol[0] * (0.75 + 0.5 * g) * (0.55 + 0.45 * mu) * 0.6 * u_coreHeat;
            } else {
                float g = fbm2(n * 1.1 + vec3(0.0, u_T * 4.0, 0.0));
                c = vec3(0.70, 0.84, 1.0) * (3.0 + 2.0 * g) * (0.6 + 0.4 * mu);
            }
            a = 1.0;
        } else if (kind == 1) {
            c = surface(normalize(pf), rd); a = 1.0;
        } else if (kind == 2) {
            // read as a concave corner: lit floor (y face), darker walls, occlusion along the edges
            vec3 e = pf - vec3(u_cut);
            float edge = axis == 0 ? min(e.y, e.z) : (axis == 1 ? min(e.x, e.z) : min(e.x, e.y));
            float ao = 0.55 + 0.45 * smoothstep(0.0, 0.22, edge / length(pf));
            c = interior(pf, w) * (axis == 1 ? 1.0 : (axis == 0 ? 0.80 : 0.66)) * ao; a = 1.0;
        } else {
            // atmosphere: a deep-red extended envelope with plumes, just outside the limb
            float pb = length(cross(ro, rd));
            float tca = max(-dot(ro, rd), 0.0);
            if (dot(ro, ro) > u_Rs * u_Rs && pb > u_Rs) {
                float x = (pb - u_Rs) / u_Rs;
                vec3 cn = normalize(ro + rd * tca);
                float pl = fbm2(cn * 0.6 + vec3(0.0, 0.0, x * 0.4));
                c = vec3(0.9, 0.22, 0.08) * (0.30 * exp(-x / 0.05) + 0.06 * exp(-x / 0.35) * (0.4 + 1.2 * pl));
                c += blackbody(30000.0) * u_flash * 2.5 * exp(-x / 0.25);
            }
        }
        // the shadow's rim: hot fallback gas spiralling in
        if (u_shadow > 0.0 && u_lensOn < 0.5) {
            float ang = asin(clamp(u_shadow, 0.0, 1.0));
            float x = (thC - ang) / ang;
            c += vec3(1.0, 0.62, 0.32) * 2.2 * exp(-pow(x / 0.12, 2.0)) * step(-0.05, x);
        }
        col += (1.0 - alpha) * c * u_starOn;
        alpha += (1.0 - alpha) * a * u_starOn;
        // proto-neutron star: neutrinosphere glow; the bounce flash
        if (u_coreMode > 0.5 && u_coreMode < 1.5) {
            float ang = asin(clamp(u_core, 0.0, 1.0));
            col += vec3(0.6, 0.78, 1.0) * 1.6 * exp(-max(thC - ang, 0.0) / (1.4 * ang));
        }
        col += vec3(1.0, 0.95, 0.9) * u_bounceFlash * (4.0 * exp(-thC / 0.04) + 0.5 * exp(-thC / 0.3));
    }

    // 3) the remnant: optically thin, lensed by the hole in the last shot
    if (u_rem > 0.0 && (u_remNeb + u_remGlow) > 0.0) {
        bool esc;
        vec3 dOut = lensDir(rd, esc);
        if (esc) col += remnant(ro / u_rem, dOut) * (1.0 - 0.8 * alpha);
    }

    // 4) neutrinos pass through everything
    // (dimmer over the star's disc, so they read as passing through, not painted on)
    if (u_nuOn > 0.0) col += neutrinos(rd) * (length(cross(ro, rd)) < u_Rs ? 0.35 : 1.0);

    o = vec4(col, alpha);
}
