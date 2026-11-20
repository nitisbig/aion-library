// shared: camera, waves (twin of scene.wave_h), the galley's frame and path, fog, scan reveal
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_fy, u_tanX, u_tanY, u_t;
uniform vec3 u_sunDir, u_sunCol, u_skyCol, u_fogCol;
uniform float u_fog, u_fade, u_reveal, u_amb, u_night, u_sink;
uniform vec3 u_revealO;
uniform vec3 u_shipPos; uniform vec2 u_shipRot;      // roll, pitch
uniform float u_furl, u_row, u_lit;
uniform float u_arrive, u_shipD, u_shipZ0, u_shipX;

const vec2 WD[5] = vec2[](vec2(0.92, -0.38), vec2(0.6, 0.8), vec2(-0.3, 0.95), vec2(0.99, 0.1), vec2(-0.7, 0.7));
const float WL[5] = float[](34.0, 19.0, 10.5, 5.6, 2.9);
const float WA[5] = float[](0.32, 0.2, 0.1, 0.05, 0.025);
const float WP[5] = float[](0.0, 1.7, 4.1, 2.3, 5.5);

vec3 wave(vec2 xz, float t) {           // (height, dh/dx, dh/dz)
    float h = 0.0, dx = 0.0, dz = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 d = normalize(WD[i]);
        float k = 6.2831853 / WL[i], w = sqrt(9.81 * k) * 0.8;
        float ph = k * dot(d, xz) - w * t + WP[i];
        h += WA[i] * sin(ph);
        float c = WA[i] * k * cos(ph);
        dx += c * d.x; dz += c * d.y;
    }
    return vec3(h, dx, dz);
}

float easeOut(float u) { u = clamp(u, 0.0, 1.0); return 1.0 - pow(1.0 - u, 2.4); }
vec3 shipAt(float t) { return vec3(u_shipX, 0.0, u_shipZ0 - u_shipD * easeOut(t / u_arrive)); }
float shipSpeed(float t) { float u = clamp(t / u_arrive, 0.0, 1.0); return u < 1.0 ? 2.4 * pow(1.0 - u, 1.4) : 0.0; }

vec3 shipRot(vec3 lp) {                 // local (x bow, y up, z starboard) → world axes, with roll and pitch
    float r = u_shipRot.x, p = u_shipRot.y;
    vec3 a = vec3(lp.x, cos(r) * lp.y - sin(r) * lp.z, sin(r) * lp.y + cos(r) * lp.z);
    vec3 b = vec3(cos(p) * a.x - sin(p) * a.y, sin(p) * a.x + cos(p) * a.y, a.z);
    return vec3(b.z, b.y, -b.x);
}

vec3 toView(vec3 p) { vec3 v = p - u_cam; return vec3(dot(v, u_right), dot(v, u_up), dot(v, u_fwd)); }
vec4 toClip(vec3 v) {
    const float n = 0.06, f = 2000.0;
    return vec4(v.x / u_tanX, v.y / u_tanY, (v.z * (f + n) - 2.0 * f * n) / (f - n), v.z);
}

vec2 reveal(vec3 p) {
    float d = length(p - u_revealO);
    float vis = smoothstep(u_reveal + 0.5, u_reveal - 6.0, d);
    float front = exp(-pow((d - u_reveal) / (1.2 + 0.01 * u_reveal), 2.0)) * step(u_reveal, 1500.0);
    return vec2(vis, front);
}

vec3 hazed(vec3 c, float z) {           // distance dims and tints toward the evening haze
    float f = exp(-u_fog * z);
    float l = dot(c, vec3(0.3, 0.5, 0.2));
    return mix(l * u_fogCol, c, f) * (0.3 + 0.7 * f);
}
