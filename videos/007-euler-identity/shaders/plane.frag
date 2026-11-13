#version 330
// The complex plane, domain-colored, in WORLD space (v_pos), so it stays locked to the Manim grid under
// any camera move. Multiplying the plane by e^{i theta} turns the color wheel by theta:
//   the color at z is the original color of w = e^{-i theta} z.
//   hue        = arg(w)              (red-ish along the positive real axis at theta = 0)
//   rings      = faint contours at |z| = 2^k
//   brightness = dark at z = 0, rolling off far away, scaled by u_value
#include "common/color.glsl"

uniform vec2  u_origin;   // where z = 0 sits (Manim units)
uniform float u_unit;     // Manim units per 1 in z
uniform float u_theta;    // turn of the whole plane (radians)
uniform float u_opacity;  // output alpha
uniform float u_sat;      // saturation
uniform float u_value;    // peak brightness (sRGB)
uniform vec4  u_clip;   // (x0, y0, x1, y1) world box; outside it nothing is drawn (all zeros: no clip)
in vec2 v_pos;
out vec4 frag;

const float TAU = 6.28318530718;

void main() {
    if (u_clip.z > u_clip.x && (v_pos.x < u_clip.x || v_pos.x > u_clip.z || v_pos.y < u_clip.y || v_pos.y > u_clip.w)) {
        frag = vec4(0.0); return;
    }
    vec2 z = (v_pos - u_origin) / u_unit;
    float c = cos(-u_theta), s = sin(-u_theta);
    vec2 w = vec2(c * z.x - s * z.y, s * z.x + c * z.y);

    float r = length(w);
    float hue = fract(atan(w.y, w.x) / TAU + 1.0);
    float ring = fract(log2(max(r, 1e-4)));
    float contour = 0.8 + 0.2 * smoothstep(0.0, 0.1, ring) * smoothstep(1.0, 0.9, ring);
    float bright = smoothstep(0.0, 1.0, r) * exp(-0.05 * r * r);

    vec3 col = hsv2rgb(vec3(hue, u_sat, u_value)) * contour * bright;
    frag = vec4(srgb2lin(col), u_opacity);
}
