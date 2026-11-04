// Act 1 pulsar fly-by: a volumetric neutron star (hot core, pulsar-wind torus, polar jets) with
// two magnetic-pole beams sweeping around the spin axis. Ray-marched with straight rays (the hole
// is ≳ 300M away here; its lensing is < 1° and ignored). Output is additive HDR.
in vec2 uv;
out vec4 o;
uniform vec3 u_cam, u_right, u_up, u_fwd;
uniform float u_tanHalf, u_aspect, u_ns, u_time;
uniform vec3 u_nsPos, u_spin, u_beam;

const float BOUND = 120.0;
const int STEPS = 96;

float hash12(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }

void main() {
    if (u_ns <= 0.0) { o = vec4(0.0); return; }
    vec2 ndc = uv * 2.0 - 1.0;
    vec3 d = normalize(u_fwd + ndc.x * u_tanHalf * u_aspect * u_right + ndc.y * u_tanHalf * u_up);
    vec3 oc = u_cam - u_nsPos;
    float bq = dot(oc, d), c = dot(oc, oc) - BOUND * BOUND;
    float disc = bq * bq - c;
    vec3 col = vec3(0.0);
    // core: a tiny white-hot star with a tight halo (closest approach of the ray to the star)
    float tc = max(-bq, 0.0);
    float dc = length(oc + d * tc);
    float px = tc * 2.0 * u_tanHalf / 1080.0;                  // world size of ~1 px at that distance
    col += vec3(0.75, 0.85, 1.0) * (3.0 * exp(-pow(dc / max(0.35, 1.2 * px), 2.0)) + 0.6 / (1.0 + pow(dc / 2.5, 2.0)));
    if (disc > 0.0) {
        float t0 = max(-bq - sqrt(disc), 0.0), t1 = -bq + sqrt(disc);
        float dt = (t1 - t0) / float(STEPS);
        float j = hash12(gl_FragCoord.xy);                    // fixed per-pixel offset (no temporal noise)
        for (int i = 0; i < STEPS; i++) {
            vec3 q = u_cam + d * (t0 + (float(i) + j) * dt) - u_nsPos;
            float r = length(q);
            // magnetic-pole beams (synchrotron blue-violet), widening and fading with distance
            for (int s = -1; s <= 1; s += 2) {
                vec3 bd = u_beam * float(s);
                float a = dot(q, bd);
                if (a > 0.0) {
                    float rad = length(q - a * bd);
                    float w = 0.5 + 0.075 * a;
                    float dens = exp(-pow(rad / w, 2.0)) * exp(-a / 42.0) * smoothstep(0.0, 3.0, a) / (w * 0.9);
                    col += vec3(0.42, 0.52, 1.0) * dens * dt * 0.55;
                }
            }
            // pulsar-wind nebula: equatorial torus + faint polar jets along the spin axis
            float h = dot(q, u_spin);
            float rr = length(q - h * u_spin);
            float ang = atan(dot(q, cross(u_spin, u_beam)), dot(q, u_beam - dot(u_beam, u_spin) * u_spin));
            float ripple = 0.7 + 0.3 * sin(ang * 3.0 + rr * 0.35 - u_time * 1.5);
            float tor = exp(-pow((rr - 13.0) / 4.0, 2.0) - pow(h / 2.2, 2.0)) * ripple;
            float inner = exp(-pow((rr - 6.0) / 1.6, 2.0) - pow(h / 1.0, 2.0));
            float jet = exp(-pow(rr / (0.6 + 0.06 * abs(h)), 2.0)) * exp(-abs(h) / 25.0);
            col += mix(vec3(0.2, 0.75, 0.9), vec3(0.9, 0.3, 0.8), smoothstep(8.0, 18.0, rr)) * tor * dt * 0.05;
            col += vec3(0.7, 0.85, 1.0) * inner * dt * 0.06;
            col += vec3(0.6, 0.5, 1.0) * jet * dt * 0.05;
        }
    }
    o = vec4(col * u_ns, 1.0);
}
