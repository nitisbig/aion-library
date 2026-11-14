#version 330
// Animated streak texture of the hero field (line integral convolution, Forssell's moving kernel).
// For each pixel, trace the streamline through v_pos forward and backward with unit-speed RK2 steps, and
// average a fine world-space value noise along it, weighted by a travelling cosine kernel. The result reads
// as brushed strokes that drift downstream. Everything is in WORLD space, so it is locked to the Manim layers
// under any camera move. The field matches shots.hero() exactly (keep the two in sync):
//   F = drift + sum_i q_i (p - c_i) / (|p - c_i|^2 + a^2) + sum_j g_j perp(p - c_j) / (|p - c_j|^2 + a^2)
#include "common/color.glsl"

uniform vec4  u_src;        // source/sink centres: (x0, y0, x1, y1)
uniform vec2  u_q;          // their strengths
uniform vec4  u_vtx;        // vortex centres
uniform vec2  u_g;          // their circulations
uniform vec2  u_drift;
uniform float u_a;          // smoothing radius
uniform float u_time;       // absolute seconds (auto)
uniform float u_rate;       // flow time scale (matches the dust)
uniform float u_opacity;
uniform float u_gain;       // contrast of the strokes
uniform float u_cell;       // noise cell size (world units)
uniform vec3  u_color;      // sRGB
in vec2 v_pos;
out vec4 frag;

const int N = 22;           // steps each way
const float H = 0.03;       // step (world units)
const float TAU = 6.28318530718;

vec2 F(vec2 p) {
    vec2 v = u_drift;
    float a2 = u_a * u_a;
    vec2 d = p - u_src.xy; v += u_q.x * d / (dot(d, d) + a2);
    d = p - u_src.zw;      v += u_q.y * d / (dot(d, d) + a2);
    d = p - u_vtx.xy;      v += u_g.x * vec2(-d.y, d.x) / (dot(d, d) + a2);
    d = p - u_vtx.zw;      v += u_g.y * vec2(-d.y, d.x) / (dot(d, d) + a2);
    return v;
}
vec2 dir(vec2 p) { vec2 v = F(p); float l = length(v); return l > 1e-5 ? v / l : vec2(0.0); }

float hash(vec2 c) { return fract(sin(dot(c, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {                      // bilinear value noise, cell = u_cell
    vec2 q = p / u_cell, i = floor(q), f = q - i;
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void main() {
    float L = float(N) * H;
    float phase = u_time * u_rate * 0.9;  // the kernel travels downstream at about the flow speed
    float acc = 0.0, wsum = 0.0;
    for (int side = -1; side <= 1; side += 2) {
        vec2 p = v_pos;
        for (int k = 0; k < N; k++) {
            float s = float(side) * float(k) * H;           // signed arc length along the streamline
            float hann = 0.5 + 0.5 * cos(3.14159265 * s / L);
            float w = hann * (0.55 + 0.45 * cos(TAU * (s / L - fract(phase / L))));
            acc += w * noise(p);
            wsum += w;
            vec2 m = p + 0.5 * float(side) * H * dir(p);    // RK2 midpoint
            p += float(side) * H * dir(m);
        }
    }
    float v = acc / max(wsum, 1e-6);
    float c = clamp((v - 0.5) * u_gain + 0.5, 0.0, 1.0);
    c = smoothstep(0.45, 1.0, c);                            // keep the dark gaps black: strokes, not haze
    float speed = clamp(length(F(v_pos)) / 0.6, 0.25, 1.0);  // slow regions read dimmer
    frag = vec4(srgb2lin(u_color), c * speed * u_opacity);
}
