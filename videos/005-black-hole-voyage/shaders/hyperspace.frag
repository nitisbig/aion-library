#version 330
// Behind the quote: the far side of the hole. A slice through a 7-dimensional cubic lattice (the
// construction that gives quasicrystals: seven plane waves, 180°/7 apart, never repeating), drawn as
// thin contour lines, zooming inward for ever and folding as the lattice drifts through the slice.
// Deliberately dim: it has to sit under text. Linear RGB, straight alpha.
in vec2 v_uv; in vec2 v_pos; out vec4 frag;
uniform float u_time, u_open, u_amt;
uniform vec3 u_colA, u_colB, u_colC;
const float PI = 3.14159265358979;

float lattice(vec2 x, float ph) {
    float s = 0.0;
    for (int k = 0; k < 7; k++) {
        float a = float(k) * PI / 7.0;
        s += cos(dot(x, vec2(cos(a), sin(a))) + ph * (0.6 + 0.23 * float(k)));    // each axis drifts at its own rate
    }
    return s / 7.0;
}
vec3 sheet(vec2 p, float scale, float ph, float px) {
    float v = lattice(p * scale, ph);
    float g = 0.27 * scale * px;                                   // rms change of v across one pixel
    float f = abs(fract(v * 5.0 + 0.5) - 0.5) / 5.0;               // distance to the nearest contour of v
    float line = 1.0 - smoothstep(0.7 * g, 2.0 * g, f);            // a hairline...
    float halo = exp(-f / (7.0 * g));                              // ...with a tight glow, black in between
    float node = pow(max(v, 0.0), 7.0);                            // where all seven axes agree
    vec3 c = mix(u_colA, u_colB, 0.32 + 0.32 * sin(3.0 * v + 0.35 * length(p)));     // mostly the deeper colour
    return c * (line + 0.22 * halo) + u_colC * node * 1.2;
}
void main() {
    vec2 p = v_pos;
    float r = length(p);
    float tw = 0.10 * u_time + 0.35 / (0.6 + r);                   // space twists more near the centre
    p = mat2(cos(tw), -sin(tw), sin(tw), cos(tw)) * p;
    p *= 1.0 + 0.10 * sin(0.9 * r - 0.5 * u_time);                 // slow breathing ripples
    float px = 8.0 / 1080.0;
    float z = u_time * 0.07;
    vec3 col = vec3(0.0);
    for (int i = 0; i < 3; i++) {                                  // three depths, cross-faded: an endless zoom
        float k = fract(z) + float(i);
        float w = sin(PI * k / 3.0);
        col += sheet(p, 1.5 * pow(2.2, k), u_time * 0.5 + 2.0 * float(i) + floor(z), px) * w * w;
    }
    float open = smoothstep(u_open * 11.0, u_open * 11.0 - 3.0 - 4.0 * u_open, r);    // opens outward from the centre
    float edge = 1.0 - 0.6 * smoothstep(4.5, 8.5, r);
    float core = 0.35 + 0.65 * smoothstep(0.0, 2.2, r);            // the far end of the tunnel stays dark
    vec2 e = (v_pos - vec2(0.3, 0.1)) / vec2(6.4, 2.6);          // a darker pocket where the portrait and quote sit
    float pocket = 0.30 + 0.70 * smoothstep(0.55, 1.25, length(e));
    frag = vec4(col * 0.20 * u_amt * open * edge * core * pocket, 1.0);
}
