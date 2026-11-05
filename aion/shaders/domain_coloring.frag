#version 330
// Domain coloring of w = e^{-i theta} z over the Manim frame.
//   hue        = arg(w)            (the color wheel turns with theta)
//   rings      = faint contours at |z| = 2^k
//   brightness = 0 at z = 0, rolls off far from the origin
uniform vec2  u_frame;    // Manim frame size (units)
uniform vec2  u_origin;   // where z = 0 sits (Manim units)
uniform float u_unit;     // Manim units per 1 in z
uniform float u_theta;    // rotation of the coloring (radians)
uniform float u_opacity;  // output alpha
uniform float u_sat;
in vec2 v_uv;
out vec4 frag;

const float TAU = 6.28318530718;

vec3 hsv2rgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

void main() {
    vec2 p = (v_uv - 0.5) * u_frame;
    vec2 z = (p - u_origin) / u_unit;
    float c = cos(-u_theta), s = sin(-u_theta);
    vec2 w = vec2(c * z.x - s * z.y, s * z.x + c * z.y);

    float r = length(w);
    float hue = fract(atan(w.y, w.x) / TAU + 1.0);
    float ring = fract(log2(max(r, 1e-4)));
    float contour = 0.82 + 0.18 * smoothstep(0.0, 0.12, ring) * smoothstep(1.0, 0.88, ring);
    float bright = smoothstep(0.0, 0.9, r) * exp(-0.035 * r * r);

    vec3 col = hsv2rgb(vec3(hue, u_sat, 1.0)) * contour * bright;
    frag = vec4(col, u_opacity);
}
