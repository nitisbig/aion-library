// shared: volume box, lights (line segments), the carved tunnel, phase function
uniform vec3 u_boxMin, u_boxMax;
uniform vec4 u_la[4];        // light segment start xyz, radius
uniform vec4 u_lb[4];        // light segment end xyz, intensity
uniform vec4 u_cav[16];      // tunnel centre line xyz, radius
uniform float u_cavOn;
uniform float u_tb;          // billow clock
const float PI = 3.14159265;

vec3 boxUVW(vec3 p) { return (p - u_boxMin) / (u_boxMax - u_boxMin); }
vec3 segClosest(vec3 p, vec3 a, vec3 b) {
    vec3 ab = b - a;
    float t = clamp(dot(p - a, ab) / max(dot(ab, ab), 1e-6), 0.0, 1.0);
    return a + t * ab;
}
// 0 inside the tunnel carved for the inside shot, 1 elsewhere
float carve(vec3 p) {
    if (u_cavOn < 0.5) return 1.0;
    float d = 1e9;
    for (int i = 0; i < 15; i++) {
        vec3 a = u_cav[i].xyz, b = u_cav[i + 1].xyz, ab = b - a;
        float t = clamp(dot(p - a, ab) / max(dot(ab, ab), 1e-6), 0.0, 1.0);
        d = min(d, length(p - a - t * ab) - mix(u_cav[i].w, u_cav[i + 1].w, t));
    }
    d += 0.35 * sin(p.x * 2.1 + 1.3) * sin(p.y * 1.7 + 0.4) * sin(p.z * 2.3 + 2.0);
    return smoothstep(-0.3, 0.6, d);
}
float hg(float c, float g) { float g2 = g * g; return (1.0 - g2) / pow(1.0 + g2 - 2.0 * g * c, 1.5); }   // ×4π: iso = 1
// strong forward lobe (silver lining) + soft back lobe + isotropic part for multiple scattering
float phase(float c) { return 0.55 * hg(c, 0.65) + 0.2 * hg(c, -0.3) + 0.25; }
// radiance arriving at p from the 4 lights, given the illumination volume sample I and view direction rd
float lightAt(vec3 p, vec3 rd, vec4 I) {
    float L = 0.0;
    for (int k = 0; k < 4; k++) {
        if (u_lb[k].w <= 0.0) continue;
        vec3 q = segClosest(p, u_la[k].xyz, u_lb[k].xyz);
        L += I[k] * phase(dot(rd, normalize(q - p + 1e-5)));
    }
    return L;
}
