// Point cloud forest: animation (wind, water, fireflies, mist, dissolve), scan reveal, mirrored stream
// reflection, per-point circle-of-confusion bokeh with energy conservation.
in vec4 in_pa;    // position.xyz, area represented (m²)
in vec4 in_nw;    // normal.xyz, wind weight
in vec4 in_m;     // colour variation, material, height above ground, world radius

uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_fy, u_tanX, u_tanY;
uniform float u_tau, u_t, u_wind, u_gustT0;
uniform float u_focus, u_aper, u_maxSize, u_base, u_fog, u_capPix;
uniform vec3 u_scanC; uniform float u_scanR;
uniform vec3 u_lineO, u_lineDir; uniform float u_lineD;
uniform float u_reflect, u_yw;
uniform vec3 u_pal[19];
uniform vec3 u_moon;
uniform float u_lidar;
uniform vec3 u_cmap[5];
uniform float u_gain;
uniform int u_only;   // debug: draw one material only (-1 = all)

out vec3 v_col;
out float v_edge, v_rim;

const int GROUND = 0, LITTER = 1, PATH = 2, BARK = 3, TWIG = 4, LEAF = 5, NEEDLE = 6, FERN = 7, GRASS = 8,
          MOSS = 9, ROCK = 10, LOG = 11, FUNGI = 12, FLOWER = 13, WATER = 14, MIST = 15, FIREFLY = 16,
          GBARK = 17, GLEAF = 18;

uint pcg(uint v) { uint s = v * 747796405u + 2891336453u; uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u; return (w >> 22u) ^ w; }
float h01(uint v) { return float(pcg(v)) / 4294967295.0; }

void cull() { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 0.0; v_col = vec3(0.0); }

float streamZ(float x) { return -60.0 + 2.5 * sin(x / 9.0 + 0.5); }
float streamHW(float x) { return 2.0 + 0.4 * sin(x / 5.0); }

vec3 cmap(float x) {
    x = clamp(x, 0.0, 1.0) * 4.0;
    int i = min(int(x), 3);
    return mix(u_cmap[i], u_cmap[i + 1], smoothstep(0.0, 1.0, x - float(i)));
}

void main() {
    uint id = uint(gl_VertexID);
    float ph = h01(id), ph2 = h01(id + 7919u);
    int mat = int(in_m.y + 0.5);
    if (u_only >= 0 && mat != u_only) { cull(); return; }
    vec3 p0 = in_pa.xyz;
    vec3 n = in_nw.xyz;
    float area = in_pa.w, wind = in_nw.w, var = in_m.x, hag = in_m.z, rad = in_m.w;
    float tau = u_tau;
    float emit = 1.0;

    // ── per-material motion ──
    vec3 p = p0;
    if (mat == WATER) {
        float x = mod(p0.x + 0.9 * tau + 70.0, 140.0) - 70.0;
        float l = p0.z;
        p = vec3(x, u_yw + 0.012 * sin(x * 3.0 + tau * 2.0 + l * 5.0), streamZ(x) + l * streamHW(x));
        p0 = p;
        float glint = pow(0.5 + 0.5 * sin(tau * 3.1 + ph * 40.0 + x * 2.3 - l * 3.0), 10.0);
        emit = 0.35 + 3.0 * glint;
    } else if (mat == FIREFLY) {
        p += vec3(1.6 * sin(tau * 0.31 + ph * 6.28) + 0.5 * sin(tau * 0.83 + ph * 17.0),
                  0.45 * sin(tau * 0.47 + ph * 9.0) + 0.2 * sin(tau * 1.3 + ph2 * 5.0),
                  1.6 * cos(tau * 0.27 + ph2 * 11.0) + 0.5 * sin(tau * 0.71 + ph * 3.0));
        float b = 0.5 + 0.5 * sin(tau * (0.8 + 0.6 * ph2) + ph * 40.0);
        emit = 0.06 + smoothstep(0.55, 0.95, b);
    } else if (mat == MIST) {
        p += vec3(0.7 * sin(tau * 0.18 + ph * 6.0), 0.15 * sin(tau * 0.3 + ph2 * 4.0), 0.7 * cos(tau * 0.15 + ph * 5.0));
        emit = 0.6 + 0.4 * sin(tau * 0.4 + ph2 * 6.28);
    } else if (wind > 0.0) {
        float w = wind * u_wind;
        vec3 sway = vec3(sin(tau * 0.9 + p0.x * 0.07 + p0.z * 0.05) + 0.4 * sin(tau * 2.1 + p0.z * 0.2),
                         0.0, 0.6 * sin(tau * 0.7 + p0.z * 0.08 + 1.3));
        float amp = (mat == GRASS || mat == FERN) ? 0.05 : 0.28;
        p += sway * w * amp;
        if (mat == LEAF || mat == NEEDLE || mat == GLEAF || mat == FERN || mat == GRASS)
            p += (vec3(ph, ph2, fract(ph * 7.0)) - 0.5) * w * 0.05 * sin(tau * 7.0 + ph * 30.0);
    }

    // ── dissolve: a gust from the edges lifts the forest into dust ──
    float dt = max(u_t - (u_gustT0 + (1.0 - clamp(length(p0.xz - vec2(0.0, -48.0)) / 95.0, 0.0, 1.0)) * 2.3 + ph * 0.6), 0.0);
    if (dt > 0.0) {
        p += vec3(sin(ph * 50.0 + dt * 1.5) * 0.9 * dt, 2.0 * dt + 2.5 * dt * dt, cos(ph2 * 70.0 + dt * 1.3) * 0.9 * dt);
        emit *= exp(-dt * 1.5) * (1.0 + 5.0 * dt * exp(-4.0 * dt));
    }

    // ── mirrored reflection in the stream (exact for a flat water plane) ──
    float rk = 1.0;
    if (u_reflect > 0.5) {
        if (p.y < u_yw + 0.05 || mat == WATER || mat == MIST) { cull(); return; }
        p.y = 2.0 * u_yw - p.y;
        float s = (u_yw - u_cam.y) / (p.y - u_cam.y);
        if (s <= 0.0 || s >= 1.0) { cull(); return; }
        vec3 hit = u_cam + s * (p - u_cam);
        if (abs(hit.z - streamZ(hit.x)) > streamHW(hit.x) * 0.95) { cull(); return; }
        p.x += 0.04 * length(p - u_cam) * 0.05 * sin(hit.z * 9.0 + tau * 3.0);
        rk = 0.28;
    }

    // ── scan reveal: a line across the floor, then an expanding sphere ──
    vec3 white = vec3(1.0, 0.97, 0.92);
    float vis = 1.0, glow = 0.0, flash = 0.0;
    if (mat != FIREFLY) {
        float fr = u_scanR - length(p0 - u_scanC);
        vis = smoothstep(-0.6, 0.0, fr);
        glow = exp(-fr * fr / 0.06) * step(0.01, u_scanR);
        flash = vis * exp(-max(fr, 0.0) / 1.8) * step(0.01, u_scanR);
        if (hag < 1.2 && length(p0.xz - u_lineO.xz) < 7.0) {
            float f2 = u_lineD - dot(p0 - u_lineO, u_lineDir);
            float v2 = smoothstep(-0.12, 0.0, f2);
            if (v2 > vis) { vis = v2; flash = v2 * exp(-max(f2, 0.0) / 2.0); }
            glow = max(glow, 1.3 * exp(-f2 * f2 / 0.015) * (1.0 - step(0.01, u_scanR)));
        }
        if (vis + glow < 0.002) { cull(); return; }
    }

    // ── project ──
    vec3 v = p - u_cam;
    float z = dot(v, u_fwd);
    if (z < 0.08) { cull(); return; }
    float x = dot(v, u_right), y = dot(v, u_up);
    gl_Position = vec4(x / (z * u_tanX), y / (z * u_tanY), 0.0, 1.0);

    // ── colour ──
    vec3 base = u_pal[mat] * (0.7 + 0.6 * var);
    if (u_lidar > 0.0 && mat != FIREFLY && mat != WATER && mat != FUNGI && mat != FLOWER) {
        float lum = dot(u_pal[mat], vec3(0.2126, 0.7152, 0.0722)) * (0.7 + 0.6 * var);
        base = mix(base, cmap(hag / 26.0) * lum * 2.2, u_lidar);
    }
    bool lit = !(mat == FIREFLY || mat == WATER || mat == MIST || mat == FUNGI || mat == FLOWER);
    float shade = lit ? 0.35 + 0.65 * max(dot(n, u_moon), 0.0) + 0.15 * max(-dot(n, u_moon), 0.0) : 1.0;
    vec3 col = base * shade * emit;
    col = mix(col, white * max(length(col), 0.4) * 1.8, clamp(flash, 0.0, 1.0) * 0.7);
    col = col * vis + white * glow * 0.7;

    // ── size: perspective base dot, circle of confusion, world radius ──
    float coc = u_aper * u_fy * abs(1.0 / u_focus - 1.0 / z);
    float world = 2.0 * rad * u_fy / z;
    float size = clamp(max(max(u_base, coc), world), 1.0, u_maxSize);
    // energy: projected area of the patch this point stands for, capped so close points stay dots
    float E = min(area * u_fy * u_fy / (z * z), u_capPix);
    if (mat == FIREFLY) E = area * u_capPix * 25.0;                   // emitters keep their brightness
    // a surface seen edge-on covers less screen: without this the ground piles up into a bright horizon band
    bool surf = mat == GROUND || mat == LITTER || mat == PATH || mat == BARK || mat == ROCK || mat == LOG
             || mat == MOSS || mat == GBARK;
    if (surf) E *= max(abs(dot(n, v)) / length(v), 0.12);
    // low ground cover lines the path, so it stacks up at the vanishing point: grazing falloff + quicker fog
    bool cover = mat == FERN || mat == GRASS || mat == FLOWER || mat == FUNGI;
    if (cover) E *= max(abs(dot(n, v)) / length(v), 0.2);
    E *= exp(-z / (cover ? 0.45 * u_fog : u_fog)) * rk * u_gain;
    float edge = clamp(2.2 / size, 0.06, 1.0);
    float norm = max(0.785 * size * size * (1.0 - 0.7 * pow(edge, 1.5)), 1.0);
    gl_PointSize = size;
    v_col = col * E / norm;
    v_edge = edge;
    v_rim = smoothstep(6.0, 14.0, size);
}
