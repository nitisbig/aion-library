#version 330
// Quiet starfield behind the diagrams: the same sky the intro's black hole sits in, without the lensing.
// Two depths of pin-point stars with slight colour temperature and slow twinkle; drifts very slowly.
in vec2 v_uv; out vec4 frag;
uniform float u_time; uniform vec2 u_res; uniform float u_amt;
float h21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
vec3 stars(vec2 uv, float n, float drift, float keep) {
    vec2 p = uv * n + vec2(u_time * drift, 0.0);
    vec2 id = floor(p), f = fract(p) - 0.5;
    float r = h21(id);
    if (r < keep) return vec3(0.0);
    vec2 o = vec2(h21(id + 3.1), h21(id + 7.7)) - 0.5;
    float d = length(f - 0.7 * o);
    float px = n / u_res.y;                                 // one output pixel, in cell units
    float s = (0.55 + 0.9 * h21(id + 1.3)) * px;
    float m = h21(id + 5.5);
    float b = exp(-d * d / (s * s)) * (0.15 + 0.85 * m * m);        // most stars faint, a few bright
    b *= 0.78 + 0.22 * sin(u_time * (0.8 + 2.5 * r) + r * 40.0);
    return mix(vec3(1.0, 0.84, 0.68), vec3(0.72, 0.84, 1.0), h21(id + 9.9)) * b;
}
void main() {
    vec2 uv = vec2(v_uv.x * u_res.x / u_res.y, v_uv.y);
    vec3 c = stars(uv, 30.0, 0.006, 0.955) + 0.7 * stars(uv + 3.7, 58.0, 0.003, 0.95);
    frag = vec4(c * u_amt, 1.0);
}
