#version 330
// The complex plane in PERSPECTIVE: every pixel casts a ray from a pinhole camera onto the plane z = 0.
// The camera matches shots3d.Cam3 exactly (keep the two in sync):
//   eye    C = T + dist * (cos(pitch) sin(yaw), -cos(pitch) cos(yaw), sin(pitch))
//   right  r = (cos(yaw), sin(yaw), 0);  forward f = normalize(T - C);  up u = cross(r, f)
//   screen = (dot(q, r), dot(q, u)) / dot(q, f) * F + (sx, sy),  q = P - C,  F = 4 / tan(fov / 2)
// Pitch 90° with dist = F is exactly the flat 2D layout (1 plane unit = 1 Manim unit).
//
// Drawn on the plane (all crisp, nothing glows):
//   domain colors of w = e^{-i theta} z on an OKLCH wheel (hue = arg w, dark at 0), opacity u_colors, with a
//   soft glossy sheen; grid lines tinted by the field (u_tint), half steps only near the camera
//   a half-step grid (u_minor), the integer grid (u_grid), the two axes (u_axis), all turned by theta,
//   anti-aliased analytically; line widths are in Manim stroke units (0.01 world units each) on the plane.
//   a depth fade toward the horizon (u_fog: the e-folding distance beyond the target)
//   a reveal disc of radius u_reveal (world units) about the origin, edged by a thin grid-colored ring
#include "common/color.glsl"

uniform float u_yaw, u_pitch, u_dist, u_fov, u_tx, u_ty, u_sx, u_sy, u_fog;
uniform vec2  u_origin;       // plane point z = 0 (world)
uniform float u_unit;         // world units per 1 in z (domain colors)
uniform float u_step;         // integer-grid spacing (world units); half-step lines between
uniform float u_theta;        // turn of the whole plane
uniform float u_colors;       // domain color opacity
uniform float u_lines;        // grid opacity
uniform float u_sat, u_value;
uniform float u_reveal;       // reveal radius (world units)
uniform float u_edge;         // reveal ring opacity
uniform float u_wgrid, u_wminor, u_waxis;          // stroke widths (Manim units: 1 = 0.01 world)
uniform vec3  u_cgrid, u_cminor, u_caxis;          // sRGB theme colors
uniform float u_tint;         // 0: theme grid colors, 1: lines tinted by the field's hue
uniform float u_sheen;        // glossy highlight strength (a light above and behind the plane)
uniform float u_kmajor, u_kminor;                  // integer / half-step line opacity
uniform vec4  u_clip;   // (x0, y0, x1, y1) world box; outside it nothing is drawn (all zeros: no clip)
in vec2 v_pos;
out vec4 frag;

const float TAU = 6.28318530718;

// coverage of the lines x = integer, width w (in x units), pristine-grid style: thin lines fade, never alias
float lines(float x, float w) {
    float fw = max(fwidth(x), 1e-6);
    float wd = max(w, fw);
    float d = abs(fract(x + 0.5) - 0.5);
    float c = 1.0 - smoothstep(0.5 * wd - 0.5 * fw, 0.5 * wd + 0.5 * fw, d);
    return c * min(w / fw, 1.0) * (1.0 - smoothstep(0.25, 0.5, fw));
}
vec3 oklch(float L, float C, float h) {        // OKLCH → linear sRGB
    vec3 lab = vec3(L, C * cos(h), C * sin(h));
    float l_ = lab.x + 0.3963377774 * lab.y + 0.2158037573 * lab.z;
    float m_ = lab.x - 0.1055613458 * lab.y - 0.0638541728 * lab.z;
    float s_ = lab.x - 0.0894841775 * lab.y - 1.2914855480 * lab.z;
    vec3 c = vec3(l_ * l_ * l_, m_ * m_ * m_, s_ * s_ * s_);
    return max(vec3(4.0767416621 * c.x - 3.3077115913 * c.y + 0.2309699292 * c.z,
                    -1.2684380046 * c.x + 2.6097574011 * c.y - 0.3413193965 * c.z,
                    -0.0041960863 * c.x - 0.7034186147 * c.y + 1.7076147010 * c.z), 0.0);
}
float line0(float x, float w) {             // only the line x = 0
    float fw = max(fwidth(x), 1e-6);
    float wd = max(w, fw);
    float c = 1.0 - smoothstep(0.5 * wd - 0.5 * fw, 0.5 * wd + 0.5 * fw, abs(x));
    return c * min(w / fw, 1.0);
}
vec4 over(vec4 dst, vec3 col, float a) { return vec4(col * a, a) + dst * (1.0 - a); }   // premultiplied

void main() {
    if (u_clip.z > u_clip.x && (v_pos.x < u_clip.x || v_pos.x > u_clip.z || v_pos.y < u_clip.y || v_pos.y > u_clip.w)) {
        frag = vec4(0.0); return;
    }
    float cp = cos(u_pitch), sp = sin(u_pitch), cy = cos(u_yaw), sy = sin(u_yaw);
    vec3 T = vec3(u_tx, u_ty, 0.0);
    vec3 C = T + u_dist * vec3(cp * sy, -cp * cy, sp);
    vec3 f = normalize(T - C);
    vec3 r = vec3(cy, sy, 0.0);
    vec3 u = cross(r, f);
    float F = 4.0 / tan(0.5 * u_fov);
    vec3 D = normalize(f * F + r * (v_pos.x - u_sx) + u * (v_pos.y - u_sy));
    if (D.z > -1e-5) { frag = vec4(0.0); return; }
    float s = -C.z / D.z;
    vec2 P = C.xy + s * D.xy;

    vec2 q = P - u_origin;
    float ct = cos(-u_theta), st = sin(-u_theta);
    vec2 qr = vec2(ct * q.x - st * q.y, st * q.x + ct * q.y);   // the un-turned plane point

    float fogk = exp(-max(s - u_dist, 0.0) / max(u_fog, 1e-3));
    float rw = length(q);
    float px = 2.0 * fwidth(rw);
    float mask = 1.0 - smoothstep(u_reveal - max(px, 0.02), u_reveal, rw);

    // domain colors on a perceptually even OKLCH wheel (no harsh HSV yellow/cyan bands), lit like a glossy floor
    vec2 w = qr / u_unit;
    float rr = length(w);
    float hang = atan(w.y, w.x) + 0.5;                          // positive real axis lands on warm red
    float ring = fract(log2(max(rr, 1e-4)));
    float contour = 0.86 + 0.14 * smoothstep(0.0, 0.12, ring) * smoothstep(1.0, 0.88, ring);
    float bright = smoothstep(0.0, 1.1, rr) * exp(-0.035 * rr * rr);
    vec3 R = vec3(D.xy, -D.z);                                  // the view ray mirrored by the plane
    float sheen = u_sheen * pow(max(dot(R, normalize(vec3(-0.3, 0.55, 0.78))), 0.0), 18.0);
    vec3 dom = oklch(0.74 * u_value * contour * bright, 0.26 * u_sat * bright, hang) * (1.0 + sheen);
    vec4 acc = vec4(dom, 1.0) * (u_colors * mask);

    // grid: hairlines tinted by the field under them; half steps only near the camera; crisp white axes
    vec3 tint = oklch(0.80, 0.15, hang) * (1.0 + 0.6 * sheen);
    vec3 cmaj = mix(srgb2lin(u_cgrid), tint, u_tint);
    vec3 cmin = mix(srgb2lin(u_cminor), 0.55 * tint, u_tint);
    vec2 g = qr / u_step;
    float wm = 0.01 * u_wminor / u_step * 2.0;          // half-step lines live at 2g
    float near = 1.0 - smoothstep(0.05, 0.14, max(fwidth(2.0 * g.x), fwidth(2.0 * g.y)));
    float minor = max(lines(2.0 * g.x, wm), lines(2.0 * g.y, wm)) * near * u_kminor;
    float wg = 0.01 * u_wgrid / u_step;
    float far = 1.0 - smoothstep(0.08, 0.32, max(fwidth(g.x), fwidth(g.y)));   // thin out toward the horizon
    float major = max(lines(g.x, wg), lines(g.y, wg)) * u_kmajor * (0.25 + 0.75 * far);
    float wa = 0.01 * u_waxis / u_step;
    float axis = max(line0(g.x, wa), line0(g.y, wa));
    float L = u_lines * mask;
    acc = over(acc, cmin, minor * L);
    acc = over(acc, cmaj, major * L);
    acc = over(acc, srgb2lin(u_caxis), axis * L);

    // the reveal's edge
    float edge = u_edge * (1.0 - smoothstep(0.0, max(px, 1e-4), abs(rw - u_reveal)));
    acc = over(acc, srgb2lin(u_cgrid), edge * u_lines);

    acc *= fogk;
    frag = acc.a > 1e-6 ? vec4(acc.rgb / acc.a, acc.a) : vec4(0.0);
}
