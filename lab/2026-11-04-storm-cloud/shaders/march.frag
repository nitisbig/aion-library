// volumetric ray march through the particle density, lit from inside by the lightning
in vec2 uv;
uniform sampler3D dens, illum, noiseTex;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanX, u_tanY, u_sigma, u_frame, u_base, u_pixAng;
float g_foot = 0.01;   // world size of a pixel at the current sample (noise LOD)
uniform vec3 u_lcol, u_albedo, u_amb;
uniform float u_under;              // warm underglow (look C)
uniform vec3 u_underCol;
uniform vec3 u_rainLo, u_rainHi;
// dusk: low sun, sky, earth shadow, distant cloud deck
uniform sampler3D sunVol;
uniform float u_erode, u_baseLod, u_anvilY;
uniform float u_sunOn, u_earthY, u_deckOn, u_deckLo, u_deckHi;
uniform vec3 u_sunDir, u_sunCol, u_skyZen, u_skyHorSun, u_skyHorAway, u_hazeCol;
layout(location = 0) out vec4 o_col;
layout(location = 1) out vec4 o_depth;

float pcg(uvec3 v) {          // structure-free per-pixel hash (IGN's diagonal pattern showed as hatching)
    v = v * 1664525u + 1013904223u;
    v.x += v.y * v.z; v.y += v.z * v.x; v.z += v.x * v.y;
    v ^= v >> 16u;
    v.x += v.y * v.z; v.y += v.z * v.x; v.z += v.x * v.y;
    return float(v.x & 0xFFFFFFu) / 16777216.0;
}

float rainShaft(vec3 p) {
    if (any(lessThan(p, u_rainLo)) || any(greaterThan(p, u_rainHi))) return 0.0;
    vec2 c = 0.5 * (u_rainLo.xz + u_rainHi.xz), hw = 0.5 * (u_rainHi.xz - u_rainLo.xz);
    float n = texture(noiseTex, vec3(p.x * 0.35, p.y * 0.05 + u_tb * 0.02, p.z * 0.35)).r;
    float r = length((p.xz - c) / hw) + 0.45 * (n - 0.5);
    float streak = texture(noiseTex, vec3(p.x * 0.9, p.y * 0.07 + u_tb * 0.25, p.z * 0.9)).r;
    float top = smoothstep(u_rainHi.y, u_rainHi.y - 0.6, p.y), bot = smoothstep(u_rainLo.y, u_rainLo.y + 3.0, p.y);
    return 0.02 * smoothstep(0.95, 0.25, r) * top * bot * (0.35 + smoothstep(0.3, 0.8, streak));
}

float density(vec3 p) {
    vec3 w = boxUVW(p);
    float rain = rainShaft(p);
    if (any(lessThan(w, vec3(0.0))) || any(greaterThan(w, vec3(1.0)))) return rain;
    float base = textureLod(dens, w, u_baseLod).r;               // blurred: a smooth "distance-like" field
    if (base < 0.004) return rain;
    float anvil = smoothstep(u_anvilY, u_anvilY + 1.0, p.y);
    vec3 q = mix(p, vec3(p.x * 0.45, p.y * 2.2, p.z * 0.6), anvil);   // anvil: stretched, fibrous
    // explicit LOD from the pixel footprint (64 texels per tile): octaves finer than a pixel fade to their mean
    float l1 = log2(max(g_foot * 0.19 * 64.0, 1e-3)), l2 = log2(max(g_foot * 0.55 * 64.0, 1e-3)),
          l3 = log2(max(g_foot * 1.6 * 64.0, 1e-3));
    float n1 = textureLod(noiseTex, q * 0.19 + vec3(0.0, -0.01, 0.0) * u_tb, max(l1, 0.0)).r;
    float n2 = textureLod(noiseTex, q * 0.55 + vec3(0.01, -0.025, 0.0) * u_tb, max(l2, 0.0)).r;
    float n3 = textureLod(noiseTex, q * 1.6 + vec3(0.0, -0.04, 0.02) * u_tb, max(l3, 0.0)).r;
    n2 = mix(n2, 0.5, smoothstep(1.5, 3.5, l2));
    n3 = mix(n3, 0.5, smoothstep(1.0, 3.0, l3));
    float e = 0.5 * n1 + 0.33 * n2 + 0.17 * n3;            // billowy field, ~[0.2, 0.8]
    float thr = 0.62 - 0.75 * e + u_erode * (0.5 - e);                             // high noise → surface pushed outward (a billow)
    float d = smoothstep(thr, thr + 0.07, base);             // crisp, cauliflower edges
    float fine = textureLod(dens, w, 0.0).r;
    return d * (0.45 + 0.55 * fine) + rain;
}

void main() {
    vec2 ndc = uv * 2.0 - 1.0;
    vec3 rd = normalize(u_fwd + ndc.x * u_tanX * u_right + ndc.y * u_tanY * u_up);
    vec3 inv = 1.0 / rd;
    vec3 t0 = (u_boxMin - u_cam) * inv, t1 = (u_boxMax - u_cam) * inv;
    vec3 tmin = min(t0, t1), tmax = max(t0, t1);
    float tn = max(max(max(tmin.x, tmin.y), tmin.z), 0.0);
    float tf = min(min(tmax.x, tmax.y), tmax.z);
    vec3 col = vec3(0.0);
    float T = 1.0, depth = 1e4;
    if (tf > tn) {
        float jit = pcg(uvec3(uvec2(gl_FragCoord.xy), uint(u_frame)));
        float t = tn;
        float dt = clamp(0.0045 * t + 0.02, 0.025, 0.14);
        t += dt * jit;
        for (int i = 0; i < 420 && t < tf; i++) {
            vec3 p = u_cam + rd * t;
            g_foot = t * u_pixAng;
            dt = clamp(0.0045 * t + 0.02, 0.025, 0.14);
            if (textureLod(dens, boxUVW(p), 3.0).r < 0.0015 && !(all(greaterThan(p, u_rainLo)) && all(lessThan(p, u_rainHi)))) {
                t += max(dt * 3.0, 0.3);
                continue;
            }
            float d = density(p);
            if (d > 0.0) {
                float s = d * u_sigma;
                vec4 I = texture(illum, boxUVW(p));
                // fine self-shadow toward the strongest light: the coarse light volume can't resolve the
                // crevices between turrets, so take a few short steps through the full-detail density
                float sunL = 0.0;
                if (u_sunOn > 0.5) {
                    float od = density(p + u_sunDir * 0.15) * 0.15 + density(p + u_sunDir * 0.4) * 0.25
                             + density(p + u_sunDir * 0.8) * 0.4 + density(p + u_sunDir * 1.4) * 0.6;
                    float fine = exp(-od * u_sigma * 0.5) * 0.8 + 0.2;
                    float earth = smoothstep(u_earthY - 0.8, u_earthY + 0.8, p.y);   // Earth's shadow line
                    sunL = textureLod(sunVol, boxUVW(p), 0.0).r * fine * earth * phase(dot(rd, u_sunDir));
                } else if (u_lb[0].w > 0.0) {
                    vec3 q = segClosest(p, u_la[0].xyz, u_lb[0].xyz);
                    vec3 ld = normalize(q - p + 1e-5);
                    float od = density(p + ld * 0.12) * 0.12 + density(p + ld * 0.3) * 0.2
                             + density(p + ld * 0.6) * 0.35 + density(p + ld * 1.05) * 0.5;
                    I.x *= exp(-od * u_sigma * 0.55) * 0.85 + 0.15;
                }
                float L = lightAt(p, rd, I);
                float powder = 1.0 - 0.6 * exp(-s * 0.6);           // dark crevices between turrets
                // sky occlusion: cloud above a point blocks the sky light → bright tops, dark undersides/crevices
                float occ = density(p + vec3(0.0, 0.35, 0.0)) * 0.35 + density(p + vec3(0.0, 0.9, 0.0)) * 0.55;
                float skyVis = exp(-occ * u_sigma * 0.35);
                vec3 amb = u_amb * skyVis * (0.6 + 0.4 * smoothstep(u_base, 11.0, p.y))
                         + u_under * u_underCol * exp(-max(p.y - u_base, 0.0) * 0.9);
                vec3 Ls = (L * u_lcol * powder + sunL * u_sunCol * powder + amb) * u_albedo;
                float st = exp(-s * dt);
                col += T * Ls * (1.0 - st);
                T *= st;
                if (T < 0.5 && depth > 1e3) depth = t;
                if (T < 0.01) { T = 0.0; break; }
            }
            t += dt;
        }
    }
    if (u_sunOn > 0.5 && T > 0.0) {
        // the cloud deck far below: a slab of fBm, lit by the sun from above, fading into the horizon haze
        if (u_deckOn > 0.5 && rd.y < -0.002) {
            float a = (u_deckHi - u_cam.y) / rd.y, b = (u_deckLo - u_cam.y) / rd.y;
            float tmax = 260.0;
            if (a < tmax) {
                b = min(b, tmax);
                float jit = pcg(uvec3(uvec2(gl_FragCoord.xy), uint(u_frame) + 77u));
                const int N = 36;
                float dt = (b - a) / float(N);
                float tt = a + dt * jit;
                for (int i = 0; i < N && T > 0.01; i++, tt += dt) {
                    vec3 p = u_cam + rd * tt;
                    float h = (p.y - u_deckLo) / (u_deckHi - u_deckLo);
                    float foot = tt * u_pixAng;
                    float n = textureLod(noiseTex, vec3(p.x * 0.022, h * 0.35, p.z * 0.022), log2(max(foot * 0.022 * 64.0, 1.0))).r;
                    float n2 = textureLod(noiseTex, vec3(p.x * 0.07, h * 0.6 + 0.3, p.z * 0.07), log2(max(foot * 0.07 * 64.0, 1.0))).r;
                    n2 = mix(n2, 0.5, smoothstep(0.0, 2.5, log2(max(foot * 0.07 * 64.0, 1e-3))));
                    float prof = smoothstep(0.0, 0.25, h) * smoothstep(1.0, 0.45, h);
                    float d = smoothstep(0.42, 0.62, (0.65 * n + 0.35 * n2) * (0.55 + 0.45 * prof) + 0.15 * prof);
                    if (d <= 0.0) continue;
                    float s = d * 1.6;
                    float up = (u_deckHi - p.y) * 1.2 / max(u_sunDir.y, 0.05);
                    float sun = (exp(-up * d) + 0.3 * exp(-up * d * 0.2)) * phase(dot(rd, u_sunDir)) * smoothstep(-0.05, 0.03, u_sunDir.y);
                    vec3 Ls = (sun * u_sunCol * 0.6 + mix(u_skyHorAway, u_skyZen, 0.6) * 0.5) * u_albedo;
                    float fog = 1.0 - exp(-tt / 110.0);
                    Ls = mix(Ls, u_hazeCol, fog);
                    float st = exp(-s * dt);
                    col += T * Ls * (1.0 - st);
                    T *= st;
                }
            }
        }
        // sky: zenith → horizon glow (warm toward the sun), sun disk + halo; below the horizon, haze
        float h = rd.y, cs = dot(rd, u_sunDir);
        vec3 hor = mix(u_skyHorAway, u_skyHorSun, pow(max(cs, 0.0), 2.5));
        vec3 sky = mix(hor, u_skyZen, pow(smoothstep(-0.01, 0.3, h), 0.45));
        sky *= 1.0 - 0.75 * smoothstep(0.15, 0.6, h);          // deep, almost black zenith
        sky = mix(sky, u_hazeCol, smoothstep(0.0, -0.08, h));
        sky += u_sunCol * (0.35 * pow(max(cs, 0.0), 600.0) + 0.05 * pow(max(cs, 0.0), 40.0) + 0.02 * pow(max(cs, 0.0), 6.0));
        sky += u_sunCol * 60.0 * smoothstep(0.99990, 0.99994, cs) * smoothstep(-0.004, 0.002, h);
        col += T * sky;
        T = 0.0;
    }
    o_col = vec4(col, T);
    o_depth = vec4(depth);
}
