"""Tower Bridge: 30 s architecture piece, rendered with moderngl on the GPU.

    uv run python lab/2026-11-04-london-bridge/render.py still --t 20 --look A --height 540
    uv run python lab/2026-11-04-london-bridge/render.py looks --t 20          # A/B/C side by side
    uv run python lab/2026-11-04-london-bridge/render.py video --look A --height 480 --fps 30
    uv run python lab/2026-11-04-london-bridge/render.py video --look A --height 1080 --fps 60 --mb 4
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import moderngl
import numpy as np
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402

DURATION = 30.0
OUT = HERE / "out"


# ── colour / easing helpers ─────────────────────────────────────────────────
def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])
    return tuple((c ** 2.2) * k)


def smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def ease_out_expo(x):
    x = np.clip(x, 0.0, 1.0)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ramp(t, a, b, ease=smoother):
    return float(ease((t - a) / (b - a)))


# ── looks ───────────────────────────────────────────────────────────────────
CYAN, STONE_C, AMBER, BLUE, WHITE, GREY, RED = (
    "#58C4DD", "#C8955A", "#FFB347", "#2A6F97", "#E6E6E6", "#5C6370", "#FC6255")
GOLD, GOLD_DIM, GOLD_HI = "#E8B04A", "#8A6A2E", "#FFF1C1"

# per group: (colour, intensity, width multiplier)
LOOKS = {
    "A": dict(  # blueprint
        groups={G.WATER: (BLUE, 0.9, 0.8), G.PIER: (STONE_C, 0.55, 1.0), G.STEEL: (CYAN, 1.0, 1.0),
                G.STONE: (STONE_C, 0.75, 0.95), G.WALKWAY: (CYAN, 1.0, 1.0), G.CHAIN: (CYAN, 1.15, 1.35),
                G.HANGER: (CYAN, 0.6, 0.8), G.DECK: (WHITE, 0.45, 0.9), G.BASCULE: (WHITE, 0.75, 1.0),
                G.SHORE: (STONE_C, 0.6, 0.95), G.CHAMBER: (GREY, 0.8, 0.8), G.CWEIGHT: (RED, 1.0, 1.1),
                G.TIE: (CYAN, 1.0, 1.3)},
        pulse=AMBER, width=1.7, bloom=0.6, grain=0.010, ca=1.0, exposure=0.95, refl=0.07, mesh=False),
    "H": None,  # filled in below: A + late solid dissolve
    "B": dict(  # gold hologram
        groups={G.WATER: (GOLD_DIM, 0.8, 0.7), G.PIER: (GOLD_DIM, 0.8, 0.9), G.STEEL: (GOLD, 0.95, 0.8),
                G.STONE: (GOLD, 0.55, 0.8), G.WALKWAY: (GOLD, 1.0, 0.85), G.CHAIN: (GOLD, 1.2, 1.1),
                G.HANGER: (GOLD, 0.55, 0.7), G.DECK: (GOLD_DIM, 0.8, 0.8), G.BASCULE: (GOLD, 0.8, 0.85),
                G.SHORE: (GOLD, 0.5, 0.8), G.CHAMBER: (GOLD_DIM, 0.8, 0.7), G.CWEIGHT: (GOLD_HI, 0.9, 1.0),
                G.TIE: (GOLD, 1.0, 1.1)},
        pulse=GOLD_HI, width=1.25, bloom=1.0, grain=0.022, ca=1.6, exposure=1.0, refl=0.09, mesh=False),
    "C": dict(  # rim-lit solids + lines, hidden lines removed
        groups={G.WATER: (BLUE, 0.9, 0.8), G.PIER: (STONE_C, 0.5, 1.0), G.STEEL: (CYAN, 0.9, 1.0),
                G.STONE: (STONE_C, 0.8, 1.0), G.WALKWAY: (CYAN, 1.0, 1.0), G.CHAIN: (CYAN, 1.15, 1.35),
                G.HANGER: (CYAN, 0.6, 0.8), G.DECK: (WHITE, 0.45, 0.9), G.BASCULE: (WHITE, 0.75, 1.0),
                G.SHORE: (STONE_C, 0.6, 1.0), G.CHAMBER: (GREY, 0.8, 0.8), G.CWEIGHT: (RED, 1.0, 1.1),
                G.TIE: (CYAN, 1.0, 1.3)},
        pulse=AMBER, width=1.6, bloom=0.5, grain=0.012, ca=0.8, exposure=1.0, refl=0.06, mesh=True,
        mesh_base="#15171C", mesh_rim=STONE_C),
}


LOOKS["H"] = dict(LOOKS["A"], mesh=True, mesh_base="#15171C", mesh_rim=STONE_C, solid_from=25.5)
LOOKS["C"]["solid_from"] = None
LOOKS["S"] = dict(LOOKS["H"], width=1.5, bloom=0.0, grain=0.0, ca=0.0, exposure=1.9, refl=0.10,
                  wobble=0.0, vignette=0.25, ssaa=2, mb_off=True)


# ── timeline ────────────────────────────────────────────────────────────────
def timeline(t):
    """Everything time-dependent, computed on the CPU from absolute time t (s)."""
    rv = np.zeros(G.N_GROUPS)
    sp = np.full(G.N_GROUPS, 0.5)
    k = np.ones(G.N_GROUPS)          # extra intensity multipliers

    rv[G.WATER] = ramp(t, 0.2, 3.2, ease_out_expo); sp[G.WATER] = 0.6
    rv[G.PIER] = ramp(t, 2.4, 4.6); sp[G.PIER] = 0.6
    rv[G.STEEL] = ramp(t, 3.4, 8.6); sp[G.STEEL] = 0.75
    rv[G.SHORE] = ramp(t, 7.5, 11.0); sp[G.SHORE] = 0.6
    rv[G.STONE] = ramp(t, 8.0, 13.0); sp[G.STONE] = 0.7
    rv[G.DECK] = ramp(t, 9.5, 12.8); sp[G.DECK] = 0.7
    rv[G.BASCULE] = ramp(t, 10.2, 13.0); sp[G.BASCULE] = 0.5
    rv[G.WALKWAY] = ramp(t, 13.0, 15.8); sp[G.WALKWAY] = 0.55
    rv[G.TIE] = ramp(t, 14.6, 15.4); sp[G.TIE] = 0.0
    rv[G.CHAIN] = ramp(t, 14.8, 17.6); sp[G.CHAIN] = 0.4
    rv[G.HANGER] = ramp(t, 16.0, 18.2); sp[G.HANGER] = 0.6
    rv[G.CHAMBER] = ramp(t, 21.4, 22.6); sp[G.CHAMBER] = 0.4
    rv[G.CWEIGHT] = ramp(t, 21.8, 22.8); sp[G.CWEIGHT] = 0.5

    # steel recedes once the stone skin is on, so the x-ray stays readable
    k[G.STEEL] = 1.0 - 0.45 * ramp(t, 9.0, 13.0) + 0.25 * ramp(t, 21.0, 22.5)
    # load path: walkways/tie light up as the pulses arrive
    pulse = ramp(t, 18.0, 19.0) * (1 - ramp(t, 21.6, 22.8))
    k[G.WALKWAY] *= 1 - 0.45 * pulse
    k[G.TIE] *= 1 - 0.3 * pulse
    k[G.CHAIN] *= 1 - 0.35 * pulse
    # cut-away fades back out at the end
    k[G.CHAMBER] *= 1 - ramp(t, 27.6, 28.8)
    k[G.CWEIGHT] *= 1 - ramp(t, 27.6, 28.8)

    theta = np.radians(G.BASCULE_MAX_DEG) * (ramp(t, 22.3, 24.9) - ramp(t, 25.7, 28.1))
    fade = 1 - ramp(t, 28.7, 30.0)
    head = 1.0
    return dict(reveal=rv, spread=sp, k=k, pulse=pulse, theta=theta, fade=fade, head=head)


# camera keys: (t, eye, target, fov_deg)
CAM_KEYS = [
    (0.0, (0, 5, 230), (0, 6, 0), 32),
    (3.0, (0, 10, 205), (0, 18, 0), 34),
    (8.0, (-45, 26, 150), (0, 30, 0), 38),
    (13.0, (-135, 42, 140), (-8, 30, 0), 40),
    (18.0, (-195, 64, 215), (0, 26, 0), 40),
    (21.5, (-178, 56, 230), (0, 26, 0), 40),
    (25.0, (-72, 3.5, 115), (0, 24, 0), 42),
    (27.5, (-95, 12, 140), (0, 27, 0), 41),
    (30.0, (-185, 50, 235), (0, 27, 0), 38),
]


def _hermite(keys, t, idx):
    ts = np.array([k[0] for k in keys])
    P = np.array([np.atleast_1d(np.array(k[idx], float)) for k in keys])
    t = float(np.clip(t, ts[0], ts[-1]))
    i = min(np.searchsorted(ts, t, side="right") - 1, len(ts) - 2)

    def m(j):
        if j == 0 or j == len(ts) - 1:
            return np.zeros_like(P[j])
        return (P[j + 1] - P[j - 1]) / (ts[j + 1] - ts[j - 1])

    dt = ts[i + 1] - ts[i]
    u = (t - ts[i]) / dt
    h00, h10 = 2 * u**3 - 3 * u**2 + 1, u**3 - 2 * u**2 + u
    h01, h11 = -2 * u**3 + 3 * u**2, u**3 - u**2
    return h00 * P[i] + h10 * dt * m(i) + h01 * P[i + 1] + h11 * dt * m(i + 1)


def camera(t, aspect):
    eye = _hermite(CAM_KEYS, t, 1)
    tgt = _hermite(CAM_KEYS, t, 2)
    fov = float(_hermite(CAM_KEYS, t, 3)[0])
    f = tgt - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    view = np.eye(4)
    view[0, :3], view[1, :3], view[2, :3] = r, u, -f
    view[:3, 3] = -view[:3, :3] @ eye
    near, far = 2.0, 1500.0
    fy = 1 / np.tan(np.radians(fov) / 2)
    proj = np.zeros((4, 4))
    proj[0, 0], proj[1, 1] = fy / aspect, fy
    proj[2, 2], proj[2, 3] = (far + near) / (near - far), 2 * far * near / (near - far)
    proj[3, 2] = -1
    return proj @ view, eye


# ── shaders ─────────────────────────────────────────────────────────────────
COMMON = """
uniform float u_reveal[16];
uniform float u_spread[16];
uniform float u_theta;
vec3 rig(vec3 p, float r){
    if (r < 0.5) return p;
    bool left = r < 1.5;
    vec3 piv = vec3(left ? -34.5 : 34.5, 8.0, 0.0);
    float th = left ? u_theta : -u_theta;
    vec3 d = p - piv; float c = cos(th), s = sin(th);
    return piv + vec3(c*d.x - s*d.y, s*d.x + c*d.y, d.z);
}
"""

LINE_VS = "#version 330\n" + COMMON + """
in vec3 in_pos; in float in_s; in float in_order; in float in_group; in float in_rig;
uniform mat4 u_vp; uniform float u_mirror; uniform float u_time; uniform vec3 u_eye; uniform float u_bias; uniform float u_wobble;
out VS { float s; float p; float g; vec3 world; float origy; } vs;
void main(){
    int g = int(in_group + 0.5);
    vec3 w = rig(in_pos, in_rig);
    vs.origy = w.y;
    if (u_mirror > 0.5) {
        w.y = -w.y;
        float depth = clamp(-w.y / 25.0, 0.0, 1.0) * u_wobble;
        w.x += 0.55 * depth * sin(w.y * 0.85 + u_time * 2.1 + w.z * 0.05);
        w.z += 0.30 * depth * sin(w.y * 0.6 - u_time * 1.7);
    }
    if (u_bias > 0.0) w += normalize(u_eye - w) * u_bias;
    vs.world = w; vs.s = in_s; vs.g = in_group;
    float sp = u_spread[g];
    vs.p = clamp((u_reveal[g] - in_order * sp) / max(1.0 - sp, 1e-3), 0.0, 1.0);
    gl_Position = u_vp * vec4(w, 1.0);
}
"""

LINE_GS = """
#version 330
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
in VS { float s; float p; float g; vec3 world; float origy; } gi[];
uniform vec2 u_res; uniform float u_width[16]; uniform float u_wscale;
out float f_s; out float f_d; out vec3 f_world; out float f_origy;
flat out float f_p; flat out float f_g; flat out float f_hw; flat out float f_thin;
void emit(vec4 c, vec2 pix, float s, float d, vec3 w, float oy){
    gl_Position = vec4(pix / (0.5 * u_res) * c.w, c.z, c.w);
    f_s = s; f_d = d; f_world = w; f_origy = oy;
    EmitVertex();
}
void main(){
    float p = gi[0].p, s0 = gi[0].s, s1 = gi[1].s;
    if (p <= s0 + 1e-5) return;
    float f = clamp((p - s0) / max(s1 - s0, 1e-6), 0.0, 1.0);
    vec4 a = gl_in[0].gl_Position;
    vec4 b = mix(gl_in[0].gl_Position, gl_in[1].gl_Position, f);
    float sa = s0, sb = mix(s0, s1, f);
    vec3 wa = gi[0].world, wb = mix(gi[0].world, gi[1].world, f);
    float oa = gi[0].origy, ob = mix(gi[0].origy, gi[1].origy, f);
    const float NEAR = 2.2;
    if (a.w < NEAR && b.w < NEAR) return;
    if (a.w < NEAR) { float t = (NEAR - a.w) / (b.w - a.w); a = mix(a, b, t); sa = mix(sa, sb, t); wa = mix(wa, wb, t); oa = mix(oa, ob, t); }
    if (b.w < NEAR) { float t = (NEAR - b.w) / (a.w - b.w); b = mix(b, a, t); sb = mix(sb, sa, t); wb = mix(wb, wa, t); ob = mix(ob, oa, t); }
    vec2 pa = a.xy / a.w * 0.5 * u_res, pb = b.xy / b.w * 0.5 * u_res;
    vec2 dir = pb - pa; float L = length(dir);
    dir = L > 1e-4 ? dir / L : vec2(1.0, 0.0);
    vec2 n = vec2(-dir.y, dir.x);
    int g = int(gi[0].g + 0.5);
    float wpx = u_width[g] * u_wscale;
    float thin = min(wpx, 1.0);
    float hw = 0.5 * max(wpx, 1.0);
    float e = hw + 1.0;                     // quad half-extent incl. AA fringe
    f_p = p; f_g = gi[0].g; f_hw = hw; f_thin = thin;
    emit(a, pa - dir * hw + n * e, sa, e, wa, oa);
    emit(a, pa - dir * hw - n * e, sa, -e, wa, oa);
    emit(b, pb + dir * hw + n * e, sb, e, wb, ob);
    emit(b, pb + dir * hw - n * e, sb, -e, wb, ob);
    EndPrimitive();
}
"""

LINE_FS = """
#version 330
in float f_s; in float f_d; in vec3 f_world; in float f_origy;
flat in float f_p; flat in float f_g; flat in float f_hw; flat in float f_thin;
uniform vec3 u_color[16]; uniform float u_inten[16];
uniform float u_pulse; uniform vec3 u_pulse_col; uniform float u_time; uniform float u_mirror;
uniform float u_refl; uniform vec3 u_eye; uniform float u_head;
out vec4 o;
void main(){
    int g = int(f_g + 0.5);
    float cov = clamp(f_hw + 0.5 - abs(f_d), 0.0, 1.0) * f_thin;
    if (cov <= 0.0) discard;
    vec3 base = u_color[g] * u_inten[g];
    vec3 col = base;
    // bright drawing head
    float head = exp(-max(f_p - f_s, 0.0) * 22.0) * (1.0 - smoothstep(0.96, 1.0, f_p));
    col += (base * 2.0 + vec3(0.35) * u_inten[g]) * head * u_head;
    // tension pulses travelling toward the centre (chain, tie, walkway)
    if (g == 4 || g == 5 || g == 12) {
        float ph = fract(abs(f_world.x) / 36.0 + u_time * 0.6);
        float pl = pow(1.0 - ph, 7.0) + 0.25 * pow(1.0 - ph, 2.0);
        col += u_pulse_col * pl * u_pulse * 2.2;
    }
    // water shimmer
    if (g == 0) {
        float sh = 0.55 + 0.45 * sin(f_world.x * 0.19 + f_world.z * 0.31 + u_time * 1.6)
                              * sin(f_world.x * 0.053 - u_time * 0.9 + f_world.z * 0.11);
        col *= sh * (1.0 - smoothstep(60.0, 300.0, abs(f_world.x)) * 0.7);
    }
    // depth fog
    float dist = length(f_world - u_eye);
    col *= mix(1.0, 0.3, smoothstep(140.0, 480.0, dist));
    if (u_mirror > 0.5) {
        if (f_origy < 0.05) discard;
        col *= u_refl * exp(-f_origy / 30.0);
    } else if (f_world.y < -0.05) {
        col *= 0.55;                          // under the waterline: seen "through" the water
    }
    o = vec4(col * cov, 1.0);
}
"""

MESH_VS = "#version 330\n" + COMMON + """
in vec3 in_pos; in vec3 in_nrm; in float in_group; in float in_rig;
uniform mat4 u_vp;
out vec3 v_world; out vec3 v_nrm; flat out float v_g;
void main(){
    vec3 w = rig(in_pos, in_rig);
    vec3 n = rig(in_pos + in_nrm, in_rig) - w;
    v_world = w; v_nrm = normalize(n); v_g = in_group;
    gl_Position = u_vp * vec4(w, 1.0);
}
"""

MESH_FS = """
#version 330
in vec3 v_world; in vec3 v_nrm; flat in float v_g;
uniform float u_reveal[16]; uniform vec3 u_eye; uniform vec3 u_base; uniform vec3 u_rim; uniform float u_solid;
out vec4 o;
void main(){
    int g = int(v_g + 0.5);
    if (v_world.y / 66.0 > min(u_reveal[g], u_solid) * 1.15 - 0.08) discard;   // bottom-up build
    vec3 V = normalize(u_eye - v_world);
    vec3 N = normalize(v_nrm);
    if (dot(N, V) < 0.0) N = -N;
    vec3 L = normalize(vec3(-0.5, 0.8, 0.35));
    float key = max(dot(N, L), 0.0);
    float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    vec3 col = u_base * (0.35 + 0.9 * key) + u_rim * rim * 0.35;
    float dist = length(v_world - u_eye);
    col *= mix(1.0, 0.35, smoothstep(140.0, 480.0, dist));
    o = vec4(col, 1.0);
}
"""

QUAD_VS = """
#version 330
in vec2 in_pos; out vec2 uv;
void main(){ uv = in_pos * 0.5 + 0.5; gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

COPY_FS = """
#version 330
in vec2 uv; uniform sampler2D tex; uniform float u_scale; out vec4 o;
void main(){ o = vec4(texture(tex, uv).rgb * u_scale, 1.0); }
"""

DOWN_FS = """
#version 330
in vec2 uv; uniform sampler2D tex; uniform vec2 u_texel; out vec4 o;
void main(){
    vec2 h = u_texel * 0.5;
    vec3 c = texture(tex, uv).rgb * 4.0;
    c += texture(tex, uv - h).rgb + texture(tex, uv + h).rgb;
    c += texture(tex, uv + vec2(h.x, -h.y)).rgb + texture(tex, uv - vec2(h.x, -h.y)).rgb;
    o = vec4(c / 8.0, 1.0);
}
"""

UP_FS = """
#version 330
in vec2 uv; uniform sampler2D tex; uniform vec2 u_texel; out vec4 o;
void main(){
    vec2 h = u_texel * 0.5;
    vec3 c = texture(tex, uv + vec2(-h.x * 2.0, 0.0)).rgb;
    c += texture(tex, uv + vec2(-h.x, h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(0.0, h.y * 2.0)).rgb;
    c += texture(tex, uv + vec2(h.x, h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(h.x * 2.0, 0.0)).rgb;
    c += texture(tex, uv + vec2(h.x, -h.y)).rgb * 2.0;
    c += texture(tex, uv + vec2(0.0, -h.y * 2.0)).rgb;
    c += texture(tex, uv + vec2(-h.x, -h.y)).rgb * 2.0;
    o = vec4(c / 12.0, 1.0);
}
"""

FINAL_FS = """
#version 330
in vec2 uv; uniform sampler2D scene; uniform sampler2D bloom;
uniform float u_bloom; uniform float u_exposure; uniform float u_fade; uniform float u_grain;
uniform float u_ca; uniform float u_frame; uniform vec2 u_res; uniform float u_vig;
out vec4 o;
float hash(vec2 p){ p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }
vec3 hdr(vec2 q){ return texture(scene, q).rgb + texture(bloom, q).rgb * u_bloom; }
void main(){
    vec2 d = uv - 0.5;
    vec2 off = d * 0.0035 * u_ca;
    vec3 c = vec3(hdr(uv + off).r, hdr(uv).g, hdr(uv - off).b);
    c = 1.0 - exp(-c * u_exposure);                 // soft filmic clip
    c *= 1.0 - u_vig * smoothstep(0.35, 0.95, length(d * vec2(1.0, 0.8)));  // vignette
    c *= u_fade;
    c = pow(c, vec3(1.0 / 2.2));
    float n = hash(uv * u_res + u_frame * 17.13) - 0.5;
    float lum = dot(c, vec3(0.299, 0.587, 0.114));
    c += n * u_grain * (0.4 + lum);
    o = vec4(clamp(c, 0.0, 1.0), 1.0);
}
"""


RESOLVE_FS = """
#version 330
uniform sampler2D tex; uniform int u_ss; out vec4 o;
void main(){
    ivec2 b = ivec2(gl_FragCoord.xy) * u_ss;
    vec3 c = vec3(0.0);
    for (int y = 0; y < u_ss; y++) for (int x = 0; x < u_ss; x++) c += texelFetch(tex, b + ivec2(x, y), 0).rgb;
    o = vec4(c / float(u_ss * u_ss), 1.0);
}
"""


# ── renderer ────────────────────────────────────────────────────────────────
class Renderer:
    def __init__(self, width, height, look="A", mb=1):
        self.look = LOOKS[look]
        self.ss = self.look.get("ssaa", 1)
        self.OW, self.OH = width, height                  # output size
        width, height = width * self.ss, height * self.ss  # internal (supersampled) size
        self.W, self.H = width, height
        self.mb = 1 if self.look.get("mb_off") else mb
        self.ctx = ctx = moderngl.create_context(standalone=True)

        geo = G.build()
        lines = G.line_array(geo)
        mesh = G.mesh_array(geo)

        self.line_prog = ctx.program(vertex_shader=LINE_VS, geometry_shader=LINE_GS, fragment_shader=LINE_FS)
        self.line_vao = ctx.vertex_array(self.line_prog, [(ctx.buffer(lines.tobytes()), "3f 1f 1f 1f 1f",
                                                           "in_pos", "in_s", "in_order", "in_group", "in_rig")])
        self.mesh_prog = ctx.program(vertex_shader=MESH_VS, fragment_shader=MESH_FS)
        self.mesh_vao = ctx.vertex_array(self.mesh_prog, [(ctx.buffer(mesh.tobytes()), "3f 3f 1f 1f",
                                                           "in_pos", "in_nrm", "in_group", "in_rig")])

        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        mk = lambda fs: ctx.program(vertex_shader=QUAD_VS, fragment_shader=fs)   # noqa: E731
        self.copy_p, self.down_p, self.up_p, self.final_p = mk(COPY_FS), mk(DOWN_FS), mk(UP_FS), mk(FINAL_FS)
        self.res_p = mk(RESOLVE_FS)
        self.res_v = ctx.vertex_array(self.res_p, [(quad, "2f", "in_pos")])
        qv = lambda p: ctx.vertex_array(p, [(quad, "2f", "in_pos")])               # noqa: E731
        self.copy_v, self.down_v, self.up_v, self.final_v = map(qv, (self.copy_p, self.down_p, self.up_p, self.final_p))

        def target(w, h, depth=False, dtype="f2", comps=4):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            att = ctx.depth_renderbuffer((w, h)) if depth else None
            return tex, ctx.framebuffer(color_attachments=[tex], depth_attachment=att)

        self.scene_tex, self.scene_fbo = target(width, height, depth=True)
        self.acc_tex, self.acc_fbo = target(width, height)
        self.levels = []
        w, h = width, height
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.out_tex, self.out_fbo = target(width, height, dtype="f1", comps=3)
        self.fin_tex, self.fin_fbo = target(self.OW, self.OH, dtype="f1", comps=3)
        for _, fbo in self.levels:
            fbo.clear(0, 0, 0, 1)

        # static uniforms
        L = self.look
        cols = [(0.0, 0.0, 0.0)] * G.N_GROUPS
        self.base_inten = np.zeros(G.N_GROUPS)
        widths = [1.0] * G.N_GROUPS
        for gid, (c, inten, wm) in L["groups"].items():
            cols[gid] = lin(c)
            self.base_inten[gid] = inten
            widths[gid] = wm
        self.line_prog["u_color"].value = cols
        self.line_prog["u_width"].value = widths
        self.line_prog["u_wscale"].value = L["width"] * height / 1080 * (1.25 if height < 700 else 1.0)
        self.line_prog["u_res"].value = (width, height)
        self.line_prog["u_pulse_col"].value = lin(L["pulse"])
        self.line_prog["u_refl"].value = L["refl"]
        self.line_prog["u_wobble"].value = L.get("wobble", 1.0)
        if L["mesh"]:
            self.mesh_prog["u_base"].value = lin(L["mesh_base"])
            self.mesh_prog["u_rim"].value = lin(L["mesh_rim"])

    def _draw_scene(self, t):
        ctx, L = self.ctx, self.look
        tl = timeline(t)
        vp, eye = camera(t, self.W / self.H)
        vp_b = vp.T.astype("f4").tobytes()
        lp = self.line_prog
        lp["u_vp"].write(vp_b)
        lp["u_eye"].value = tuple(eye)
        lp["u_time"].value = t
        lp["u_reveal"].value = tuple(tl["reveal"])
        lp["u_spread"].value = tuple(tl["spread"])
        lp["u_inten"].value = tuple(self.base_inten * tl["k"])
        lp["u_theta"].value = tl["theta"]
        lp["u_pulse"].value = tl["pulse"]
        lp["u_head"].value = tl["head"]

        self.scene_fbo.use()
        self.scene_fbo.clear(0, 0, 0, 1, depth=1.0)
        ctx.blend_func = moderngl.ONE, moderngl.ONE

        # reflections first (additive, no depth)
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.enable(moderngl.BLEND)
        lp["u_mirror"].value = 1.0
        lp["u_bias"].value = 0.0
        self.line_vao.render(moderngl.LINES)
        lp["u_mirror"].value = 0.0

        if L["mesh"]:
            mp = self.mesh_prog
            mp["u_vp"].write(vp_b)
            mp["u_eye"].value = tuple(eye)
            mp["u_reveal"].value = tuple(tl["reveal"])
            mp["u_theta"].value = tl["theta"]
            sf = L.get("solid_from")
            mp["u_solid"].value = 1.0 if sf is None else ramp(t, sf, sf + 2.0)
            ctx.disable(moderngl.BLEND)
            ctx.enable(moderngl.DEPTH_TEST)
            self.mesh_vao.render(moderngl.TRIANGLES)
            ctx.enable(moderngl.BLEND)
            ctx.depth_mask = False
            lp["u_bias"].value = 0.35
            self.line_vao.render(moderngl.LINES)
            ctx.depth_mask = True
            ctx.disable(moderngl.DEPTH_TEST)
        else:
            self.line_vao.render(moderngl.LINES)
        return tl

    def frame(self, t, fps, frame_idx=0):
        ctx, L = self.ctx, self.look
        self.acc_fbo.use()
        self.acc_fbo.clear(0, 0, 0, 1)
        shutter = 0.5 / fps
        tl = None
        for i in range(self.mb):
            ts = t + ((i + 0.5) / self.mb - 0.5) * shutter if self.mb > 1 else t
            tl = self._draw_scene(min(max(ts, 0.0), DURATION))
            self.acc_fbo.use()
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self.scene_tex.use(0)
            self.copy_p["tex"].value = 0
            self.copy_p["u_scale"].value = 1.0 / self.mb
            self.copy_v.render(moderngl.TRIANGLE_STRIP)
        tl = timeline(t)

        # bloom: dual-filter down / up chain
        ctx.disable(moderngl.BLEND)
        src = self.acc_tex
        for tex, fbo in (self.levels if L["bloom"] > 0 else []):
            fbo.use()
            src.use(0)
            self.down_p["tex"].value = 0
            self.down_p["u_texel"].value = (1 / src.width, 1 / src.height)
            self.down_v.render(moderngl.TRIANGLE_STRIP)
            src = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in (range(len(self.levels) - 1, 0, -1) if L["bloom"] > 0 else []):
            src = self.levels[k][0]
            self.levels[k - 1][1].use()
            src.use(0)
            self.up_p["tex"].value = 0
            self.up_p["u_texel"].value = (1 / src.width, 1 / src.height)
            self.up_v.render(moderngl.TRIANGLE_STRIP)
        ctx.disable(moderngl.BLEND)

        self.out_fbo.use()
        self.acc_tex.use(0)
        self.levels[0][0].use(1)
        fp = self.final_p
        fp["scene"].value, fp["bloom"].value = 0, 1
        fp["u_bloom"].value = L["bloom"] / 3.0
        fp["u_exposure"].value = L["exposure"]
        fp["u_fade"].value = tl["fade"]
        fp["u_grain"].value = L["grain"]
        fp["u_ca"].value = L["ca"]
        fp["u_frame"].value = float(frame_idx % 997)
        fp["u_res"].value = (self.W, self.H)
        fp["u_vig"].value = L.get("vignette", 0.55)
        self.final_v.render(moderngl.TRIANGLE_STRIP)
        if self.ss == 1:
            return self.out_fbo.read(components=3, alignment=1)   # bottom-up rows
        self.fin_fbo.use()
        self.out_tex.use(0)
        self.res_p["tex"].value = 0
        self.res_p["u_ss"].value = self.ss
        self.res_v.render(moderngl.TRIANGLE_STRIP)
        return self.fin_fbo.read(components=3, alignment=1)


# ── CLI ─────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def save_png(buf, w, h, path):
    from PIL import Image
    img = Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    return img


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h, a.look, mb=a.mb)
    OUT.mkdir(exist_ok=True)
    for t in a.t:
        path = OUT / f"still_{a.look}_{t:05.2f}s.png"
        save_png(r.frame(t, 60), w, h, path)
        print(path)


def cmd_looks(a):
    from PIL import Image
    w, h = size_for(a.height)
    OUT.mkdir(exist_ok=True)
    for t in a.t:
        tiles = []
        for look in "ABC":
            r = Renderer(w, h, look)
            tiles.append(save_png(r.frame(t, 60), w, h, OUT / f"look_{look}_{t:05.2f}s.png"))
            r.ctx.release()
        sheet = Image.new("RGB", (w * 3 + 20, h), (40, 40, 40))
        for i, im in enumerate(tiles):
            sheet.paste(im, (i * (w + 10), 0))
        path = OUT / f"looks_{t:05.2f}s.png"
        sheet.save(path)
        print(path)


def cmd_video(a):
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(DURATION * fps))
    r = Renderer(w, h, a.look, mb=a.mb)
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"tower_bridge_{a.look}_{h}p{fps}.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "vflip",
         "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    bar = tqdm(total=n, desc=f"TowerBridge@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    for i in range(n):
        ff.stdin.write(r.frame(i / fps, fps, i))
        bar.update(1)
    ff.stdin.close()
    ff.wait()
    bar.close()
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still"); s.add_argument("--t", type=float, nargs="+", default=[20.0])
    s.add_argument("--look", default="A"); s.add_argument("--height", type=int, default=540)
    s.add_argument("--mb", type=int, default=1)
    s = sub.add_parser("looks"); s.add_argument("--t", type=float, nargs="+", default=[20.0])
    s.add_argument("--height", type=int, default=540)
    s = sub.add_parser("video"); s.add_argument("--look", default="A")
    s.add_argument("--height", type=int, default=480); s.add_argument("--fps", type=int, default=30)
    s.add_argument("--mb", type=int, default=1); s.add_argument("--crf", type=int, default=16)
    s.add_argument("--preset", default="medium"); s.add_argument("--out", default=None)
    a = ap.parse_args()
    {"still": cmd_still, "looks": cmd_looks, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
