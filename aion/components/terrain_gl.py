"""A luminous terrain on a black stage, rendered on the GPU (moderngl) inside Manim.

The look of the channel's design system: the stage stays black, the ground is a
near-black body, and light comes only from thin geometry drawn *on* it: silver
contour lines (every 4th one brighter), a faint wire grid, drifting mist made of
particles, and a two-level bloom. A vignette and a light film grain finish the frame.

    rig = Rig(**TERRAIN_DEFAULTS, H=(2, 0, -2), wm=1.0)
    plate = TerrainPlate(rig.state)            # re-rendered every frame
    self.add(plate)
    dot.add_updater(lambda m: m.move_to(plate.surface_point(0, 0)))

Height = a windowed quadratic patch ½·pᵀHp (the math of the narration) + a ridged
fBm mountain range that is exactly zero inside radius `m0`. `height()` /
`surface_point()` / `project()` mirror the patch only, so they are exact wherever
r < m0 or wm = 0 (where every overlay in the video lives).

Drive it through the state callback (ValueTrackers), never by animating the plate
itself (copies would share GPU state). Fade it with the "opacity" key.

State keys (see TERRAIN_DEFAULTS):
  height  H, zs, win, zclip, wm, m0, m1, mamp, mscale, mseed
  domain  edge (radius beyond which the ground is cut away, lines fading before it)
  camera  target, yaw, pitch, dist, fov (same orbit camera as SurfacePlate)
  lines   contour, cstep, grid, gstep, lw (px at 1080p), reveal (radius of the
          draw-on front around the origin), rim (silhouette light)
  colour  tint, tintR (blue where the patch rises above the walker, orange where it
          falls, within radius tintR)
  air     fog, fognear, mist, haze (big soft fog banks), time (drift clock)
  extras  slices [(angle_deg, strength, color, length)], disc (x, y, r, alpha),
          disc_color, ping (radius, alpha)
  finish  bloom, vignette, grain, opacity
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

import moderngl
import numpy as np
from manim import ORIGIN, ImageMobject, color_to_rgb, config

from .. import style as S
from . import blit
from .shader_plate import _ctx
from .splat_gl import SPLAT_DEFAULTS, SplatLayer
from .surface_gl import camera_matrices

blit.install()

SHADER_DIR = Path(__file__).resolve().parents[1] / "shaders"
MAX_SLICES = 4

TERRAIN_DEFAULTS: dict = {
    "H": (0.0, 0.0, 0.0), "zs": 0.35, "win": 1.9, "zclip": 0.0,
    "wm": 1.0, "m0": 3.0, "m1": 8.0, "mamp": 5.0, "mscale": 0.13, "mseed": (9.3, 1.7), "mback": 0.3,
    "edge": 60.0,
    "target": (0.0, 0.0, 0.3), "yaw": 200.0, "pitch": 14.0, "dist": 6.0, "fov": 40.0,
    "contour": 1.0, "cstep": 0.12, "grid": 0.22, "gstep": 0.5, "gridR": 3.5, "lw": 1.6, "reveal": 99.0,
    "rim": 0.5, "mline": 0.18, "dots": 1.0,
    "tint": 0.0, "tintR": 2.2,
    "fog": 0.08, "fognear": 3.0, "fogH": 1.6, "mist": 0.6, "haze": 0.25, "time": 0.0,
    "slices": [], "disc": (0.0, 0.0, 0.5, 0.0), "disc_color": S.TEXT, "ping": (0.0, 0.0),
    "bloom": 1.0, "vignette": 0.5, "grain": 0.04, "opacity": 1.0, "aurora": 0.0, "paint": 0.0, "paintR": 3.5,
    **SPLAT_DEFAULTS,
}


def _rgb(c) -> tuple[float, float, float]:
    return tuple(float(v) for v in color_to_rgb(c))


def patch_height(s: dict, x, y):
    """Python mirror of patch_h() in terrain.glsl."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    a, b, c = s["H"]
    q = 0.5 * (a * x * x + 2 * b * x * y + c * y * y)
    w = np.exp(-(x * x + y * y) / (2 * s["win"] ** 2)) if s["win"] > 0 else 1.0
    z = s["zs"] * q * w
    if s["zclip"] > 0:
        z = s["zclip"] * np.tanh(z / s["zclip"])
    return z


# ── GLSL ─────────────────────────────────────────────────────────────
_VS = """
in vec2 in_uv;
uniform mat4 u_mvp;
uniform float u_R;
out vec2 v_p;
out vec3 v_w;
void main() {
    vec2 p = sign(in_uv) * pow(abs(in_uv), vec2(1.7)) * u_R;   // dense near the walker
    float z = height(p);
    v_p = p;
    v_w = vec3(p, z);
    gl_Position = u_mvp * vec4(p, z, 1.0);
}
"""

_FS = """
in vec2 v_p;
in vec3 v_w;
uniform vec3 u_eye;
uniform float u_px, u_lw, u_edge;
uniform vec3 u_line, u_body, u_smile, u_frown, u_aurA, u_aurB;
uniform float u_aurora;
uniform float u_paint, u_paintR;   // parametric gradient fill of the walker's ground
uniform vec3 u_pc[4];              // its corner colours (−x−y, +x−y, −x+y, +x+y)
uniform float u_contour, u_cstep, u_grid, u_gstep, u_gridR, u_reveal, u_rim, u_mline;
uniform float u_fog, u_fognear, u_fogH, u_tint, u_tintR;
uniform vec4 u_sl[4];        // (dir.x, dir.y, strength, half length)
uniform vec3 u_slc[4];
uniform vec4 u_disc;         // (x, y, r, alpha)
uniform vec3 u_discc;
uniform vec2 u_ping;         // (radius, alpha)
out vec4 f_col;

// coverage of lines at integer values of x, `w` px wide; fades where lines crowd
float lines(float x, float w) {
    float fw = max(fwidth(x), 1e-5);
    float d = abs(fract(x - 0.5) - 0.5) / fw;
    float cov = 1.0 - smoothstep(w * 0.5 - 0.5, w * 0.5 + 0.5, d);
    return cov * (1.0 - smoothstep(0.16, 0.42, fw));
}

// coverage of the single curve g = 0 (g in world units)
float curve(float g, float w) {
    float fw = max(fwidth(g), 1e-5);
    float d = abs(g) / fw;
    // edge-on silhouettes have huge derivatives: no coverage there (else dotted rims)
    return (1.0 - smoothstep(w * 0.5 - 0.5, w * 0.5 + 0.5, d)) * (1.0 - smoothstep(0.04, 0.12, fw));
}

void main() {
    float r = length(v_p);
    if (r > u_edge) discard;
    float edgeF = 1.0 - smoothstep(u_edge * 0.8, u_edge, r);
    float h = height(v_p);                                   // exact, per pixel
    vec3 n = normalize(cross(dFdx(v_w), dFdy(v_w)));
    if (n.z < 0.0) n = -n;
    vec3 V = normalize(u_eye - v_w);
    float d = length(u_eye - v_w);
    // height fog: thick in the valleys, thin on the peaks
    float zm = max(0.5 * (v_w.z + u_eye.z), 0.0);
    float vis = exp(-u_fog * max(d - u_fognear, 0.0) * exp(-zm / u_fogH));
    float shade = 0.28 + 0.72 * max(dot(n, normalize(vec3(-0.45, 0.55, 0.70))), 0.0);
    float rim = pow(1.0 - max(dot(n, V), 0.0), 4.0);
    float w = max(u_lw * u_px, 0.9);
    float reveal = 1.0 - smoothstep(u_reveal - 0.8, u_reveal, r);

    float cz = h / u_cstep + 0.5;                 // half-step offset: flat ground stays dark
    float minor = 1.0 - smoothstep(4.0, 10.0, d);  // far away only the major lines remain
    float con = 0.5 * minor * lines(cz, w) + 0.75 * lines(cz / 4.0, w * 1.3);
    float grd = max(lines(v_p.x / u_gstep, w * 0.8), lines(v_p.y / u_gstep, w * 0.8));
    grd *= exp(-r * r / (2.0 * u_gridR * u_gridR));          // the wire grid belongs to the walker's ground
    con *= mix(1.0, u_mline, smoothstep(0.0, 0.12, mountain_mask(v_p)));
    float lum = (u_contour * con + u_grid * grd) * shade;
    lum += u_rim * rim * smoothstep(0.0, 0.3, mountain_mask(v_p)) * smoothstep(3.0, 8.0, d);   // skyline silhouettes
    lum *= vis * edgeF * reveal;

    // bend tint: blue where the ground rises from the walker's level, orange where it falls
    float hp = patch_h(v_p);
    float tw = u_tint * exp(-r * r / (2.0 * u_tintR * u_tintR)) * smoothstep(0.0, 0.05, abs(hp));
    // aurora: the neutral lines take an ice-cyan → lavender sheen that turns around the walker
    float ang = atan(v_p.y, v_p.x);
    vec3 aur = mix(u_aurA, u_aurB, 0.5 + 0.5 * sin(ang * 1.0 + 0.35 * r));
    vec3 base = mix(u_line, aur, u_aurora);
    vec3 lc = mix(base, hp > 0.0 ? u_smile : u_frown, clamp(tw, 0.0, 1.0));
    lum *= 1.0 + 0.6 * clamp(tw, 0.0, 1.0);

    vec3 col = u_body * shade * vis * edgeF + lc * lum;

    // parametric fill: a bilinear gradient over (x, y), brighter where the patch is high,
    // lit like a solid surface, fading out where the mountains begin
    if (u_paint > 0.0) {
        vec2 uv = clamp(v_p / (0.75 * u_paintR) * 0.5 + 0.5, 0.0, 1.0);
        vec3 pc = mix(mix(u_pc[0], u_pc[1], uv.x), mix(u_pc[2], u_pc[3], uv.x), uv.y);
        float hl = clamp(0.5 + hp / 0.8, 0.0, 1.0);
        float fr = pow(1.0 - max(dot(n, V), 0.0), 2.0);          // grazing angles glow a little
        float fade = (1.0 - smoothstep(0.96 * u_paintR, u_paintR, r)) * (1.0 - smoothstep(0.0, 0.3, mountain_mask(v_p)));
        pc *= (0.30 + 0.70 * shade) * (0.55 + 0.75 * hl) + 0.35 * fr;
        col += pc * u_paint * fade * vis * edgeF * reveal;
        // the patch's boundary curve, crisp
        float rim = curve(r - u_paintR, w * 1.4) * (1.0 - smoothstep(0.0, 0.3, mountain_mask(v_p)));
        col += mix(u_aurA, u_aurB, uv.x) * rim * u_paint * 1.4 * vis * edgeF * reveal;
    }

    // slice curves through the origin, drawn on the ground
    for (int i = 0; i < 4; i++) {
        if (u_sl[i].z <= 0.0) continue;
        vec2 dir = u_sl[i].xy;
        float across = dot(v_p, vec2(-dir.y, dir.x));
        float along = dot(v_p, dir);
        float len = 1.0 - smoothstep(u_sl[i].w * 0.6, u_sl[i].w, abs(along));
        float core = curve(across, w * 2.0);
        float halo = exp(-pow(across / 0.07, 2.0)) * 0.35;
        col += u_slc[i] * u_sl[i].z * (core + halo) * len * mix(0.4, 1.0, vis);
    }

    // tangent disc: a thin ring and a whisper of fill
    if (u_disc.w > 0.0) {
        float dr = length(v_p - u_disc.xy);
        float ring = curve(dr - u_disc.z, w * 1.2) + exp(-pow((dr - u_disc.z) / 0.04, 2.0)) * 0.15;
        float fill = (1.0 - smoothstep(u_disc.z - 0.02, u_disc.z, dr)) * 0.10;
        col += u_discc * u_disc.w * (ring + fill);
    }

    // sonar ping from the walker, swallowed by the fog
    if (u_ping.y > 0.0) {
        float pr = r - u_ping.x;
        float ring = curve(pr, w * 1.4) + exp(-pow(pr / 0.10, 2.0)) * 0.4;
        col += u_line * u_ping.y * ring * vis;
    }
    f_col = vec4(col, 1.0);
}
"""

_MIST_VS = """
in vec4 in_p;                 // x0, y0, layer height, seed
uniform mat4 u_mvp;
uniform vec3 u_eye;
uniform float u_R, u_time, u_size, u_alpha, u_fog, u_fognear, u_edge, u_vy, u_near0, u_near1;
out float v_a;
void main() {
    float s = in_p.w;
    vec2 vel = vec2(0.10, u_vy) * (0.5 + fract(s * 7.31));
    vec2 p = mod(in_p.xy + vel * u_time + u_R, 2.0 * u_R) - u_R;
    float z = height(p) + in_p.z;
    vec4 cp = u_mvp * vec4(p, z, 1.0);
    gl_Position = cp;
    float d = length(vec3(p, z) - u_eye);
    gl_PointSize = clamp(u_size * (0.55 + 0.9 * fract(s * 13.7)) / max(cp.w, 0.2), 1.0, 480.0);
    float tw = 0.55 + 0.45 * sin(u_time * (0.4 + fract(s * 3.3)) + s * 40.0);
    float edge = 1.0 - smoothstep(u_edge * 0.8, u_edge, length(p));
    v_a = u_alpha * tw * edge * exp(-u_fog * 0.7 * max(d - u_fognear, 0.0)) * smoothstep(u_near0, u_near1, d);
}
"""

_DOTS_VS = """
in vec3 in_d;                 // x, y, seed
uniform mat4 u_mvp;
uniform vec3 u_eye;
uniform float u_alpha, u_px, u_fog, u_fognear, u_fogH, u_time, u_reveal;
out float v_a;
void main() {
    vec2 p = in_d.xy;
    float m = mountain_mask(p);
    float z = height(p);
    gl_Position = u_mvp * vec4(p, z + 0.04, 1.0);      // just above the ground: no z-fighting
    if (m < 0.02) { v_a = 0.0; gl_PointSize = 1.0; return; }
    float e = 0.06;
    float hx = height(p + vec2(e, 0.0)) - height(p - vec2(e, 0.0));
    float hy = height(p + vec2(0.0, e)) - height(p - vec2(0.0, e));
    vec3 n = normalize(vec3(-hx / (2.0 * e), -hy / (2.0 * e), 1.0));
    float lit = pow(max(dot(n, normalize(vec3(-0.45, 0.55, 0.70))), 0.0), 2.6);
    float d = length(vec3(p, z) - u_eye);
    float zm = max(0.5 * (z + u_eye.z), 0.0);
    float vis = exp(-u_fog * max(d - u_fognear, 0.0) * exp(-zm / u_fogH));
    float peak = 0.35 + 0.65 * smoothstep(0.5, 4.5, z);          // moonlit tops
    float tw = 0.75 + 0.25 * sin(u_time * 1.3 + in_d.z * 60.0);
    float rev = 1.0 - smoothstep(u_reveal - 1.5, u_reveal, length(p));
    v_a = u_alpha * m * vis * (0.04 + 1.1 * lit) * peak * tw * rev * smoothstep(0.5, 2.0, d);
    gl_PointSize = max(1.0, 1.6 * u_px * (0.7 + 0.6 * fract(in_d.z * 17.3)));
}
"""

_MIST_FS = """
in float v_a;
uniform vec3 u_col;
uniform float u_soft;
out vec4 f_col;
void main() {
    vec2 c = gl_PointCoord * 2.0 - 1.0;
    float a = v_a * exp(-dot(c, c) * u_soft);
    f_col = vec4(u_col * a, a);
}
"""

_QUAD_VS = """
#version 330
in vec2 in_pos;
out vec2 v_uv;
void main() { v_uv = in_pos * 0.5 + 0.5; gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

_DOWN_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_src;
uniform vec2 u_texel;        // source texel size
uniform float u_thresh;
out vec4 f_col;
void main() {                // 4 bilinear taps = a 4x4 box: thin lines are never skipped
    vec4 c = texture(u_src, v_uv + u_texel * vec2(-1, -1)) + texture(u_src, v_uv + u_texel * vec2(1, -1))
           + texture(u_src, v_uv + u_texel * vec2(-1, 1)) + texture(u_src, v_uv + u_texel * vec2(1, 1));
    f_col = max(c * 0.25 - u_thresh, 0.0);      // only what is bright blooms
}
"""

_BLUR_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_src;
uniform vec2 u_step;
out vec4 f_col;
void main() {
    float w[5] = float[](0.2270, 0.1945, 0.1216, 0.0541, 0.0162);
    vec4 c = texture(u_src, v_uv) * w[0];
    for (int i = 1; i < 5; i++) {
        c += texture(u_src, v_uv + u_step * float(i)) * w[i];
        c += texture(u_src, v_uv - u_step * float(i)) * w[i];
    }
    f_col = c;
}
"""

_COMP_FS = """
#version 330
in vec2 v_uv;
uniform sampler2D u_scene, u_b1, u_b2;
uniform vec2 u_res;
uniform float u_bloom, u_vig, u_grain, u_opacity, u_seed;
out vec4 f_col;
float hash(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33);
                     return fract((p3.x + p3.y) * p3.z); }
void main() {
    vec3 c = texture(u_scene, v_uv).rgb;
    c += u_bloom * (0.9 * texture(u_b1, v_uv).rgb + 0.8 * texture(u_b2, v_uv).rgb);
    vec2 q = v_uv - 0.5;
    q.x *= u_res.x / u_res.y;
    c *= 1.0 - u_vig * smoothstep(0.30, 1.05, length(q) * 1.15);
    float l = clamp(dot(c, vec3(0.3, 0.6, 0.1)) * 3.0, 0.0, 1.0);
    c += (hash(v_uv * u_res + u_seed) - 0.5) * u_grain * (0.12 + 0.88 * l);
    f_col = vec4(clamp(c, 0.0, 1.0) * u_opacity, 1.0);
}
"""

_GL: dict[int, dict] = {}


def _dust_points(n: int, R: float, seed: int) -> np.ndarray:
    """Points on the floor plane, density ∝ 1/r (perspective then spreads them evenly)."""
    rng = np.random.default_rng(seed)
    r = 2.5 + (R - 2.5) * rng.random(n)
    a = rng.uniform(0, 2 * np.pi, n)
    return np.stack([r * np.cos(a), r * np.sin(a), rng.random(n)], 1).astype("f4")


def _mist_points(n: int, R: float, lo: float, hi: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pts = np.empty((n, 4), "f4")
    pts[:, 0:2] = rng.uniform(-R, R, (n, 2))
    pts[:, 2] = lo + (hi - lo) * rng.random(n) ** 2          # most mist hugs the ground
    pts[:, 3] = rng.random(n)
    return pts


class TerrainPlate(ImageMobject):
    """Full-frame GPU terrain. Opaque: meant to sit directly on the black stage."""

    def __init__(self, state: Callable[[], dict], *, mesh: int = 480, R: float = 40.0,
                 samples: int = 4, dust: int = 5000, banks: int = 420, dots: int = 450_000, seed: int = 11,
                 splats: int = 0, **kw):
        w, h = config.pixel_width, config.pixel_height
        ctx = _ctx()
        head = "#version 330\n" + (SHADER_DIR / "terrain.glsl").read_text()
        prog = ctx.program(vertex_shader=head + _VS, fragment_shader=head + _FS)
        mist = ctx.program(vertex_shader=head + _MIST_VS, fragment_shader="#version 330\n" + _MIST_FS)
        dprog = ctx.program(vertex_shader=head + _DOTS_VS, fragment_shader="#version 330\n" + _MIST_FS)
        down = ctx.program(vertex_shader=_QUAD_VS, fragment_shader=_DOWN_FS)
        blur = ctx.program(vertex_shader=_QUAD_VS, fragment_shader=_BLUR_FS)
        comp = ctx.program(vertex_shader=_QUAD_VS, fragment_shader=_COMP_FS)

        g = np.linspace(-1, 1, mesh + 1, dtype="f4")
        gx, gy = np.meshgrid(g, g)
        verts = np.stack([gx.ravel(), gy.ravel()], 1).astype("f4")
        i = np.arange(mesh)
        a = (i[None, :] + (mesh + 1) * i[:, None]).ravel()
        idx = np.stack([a, a + 1, a + mesh + 1, a + 1, a + mesh + 2, a + mesh + 1], 1)
        vao = ctx.vertex_array(prog, [(ctx.buffer(verts.tobytes()), "2f", "in_uv")],
                               index_buffer=ctx.buffer(idx.astype("i4").tobytes()))
        dust_vao = ctx.vertex_array(mist, [(ctx.buffer(_mist_points(dust, 14.0, 0.03, 1.1, seed).tobytes()),
                                            "4f", "in_p")])
        bank_vao = ctx.vertex_array(mist, [(ctx.buffer(_mist_points(banks, 14.0, 0.1, 0.9, seed + 1).tobytes()),
                                            "4f", "in_p")])
        dots_vao = ctx.vertex_array(dprog, [(ctx.buffer(_dust_points(dots, 34.0, seed + 2).tobytes()), "3f", "in_d")])
        quad = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes())
        qv = {p: ctx.vertex_array(prog_, [(quad, "2f", "in_pos")])
              for p, prog_ in (("down", down), ("blur", blur), ("comp", comp))}

        samples = min(samples, ctx.max_samples)
        ms = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4, samples=samples)],
                             depth_attachment=ctx.depth_renderbuffer((w, h), samples=samples))

        def tex(size):
            t = ctx.texture(size, 4)
            t.repeat_x = t.repeat_y = False
            return t, ctx.framebuffer(color_attachments=[t])

        scene = tex((w, h))
        q4 = (max(2, w // 4), max(2, h // 4))
        q8 = (max(2, w // 8), max(2, h // 8))
        b1a, b1b, b2a, b2b = tex(q4), tex(q4), tex(q8), tex(q8)
        out = ctx.framebuffer(color_attachments=[ctx.renderbuffer((w, h), 4)])

        super().__init__(np.zeros((h, w, 4), dtype=np.uint8), **kw)
        self._gl_key = id(self)
        _GL[self._gl_key] = dict(prog=prog, mist=mist, dprog=dprog, dots=dots_vao, down=down, blur=blur, comp=comp, vao=vao,
                                 dust=dust_vao, banks=bank_vao, qv=qv, ms=ms, scene=scene,
                                 b1=(b1a, b1b), b2=(b2a, b2b), q4=q4, q8=q8, out=out, size=(w, h),
                                 R=R, state=state,
                                 splats=SplatLayer(ctx, head, splats, TERRAIN_DEFAULTS["m0"]) if splats else None)
        self.stretch_to_fit_width(config.frame_width)
        self.stretch_to_fit_height(config.frame_height)
        self.move_to(ORIGIN)
        self._fast_blit = True
        self.render_gl()
        self.add_updater(lambda m: m.render_gl())

    # ── geometry (Python side) ─────────────────────────────────
    def state(self) -> dict:
        return {**TERRAIN_DEFAULTS, **_GL[self._gl_key]["state"]()}

    def height(self, x, y, s: dict | None = None):
        return patch_height(s or self.state(), x, y)

    def project(self, x: float, y: float, z: float, s: dict | None = None) -> np.ndarray:
        s = s or self.state()
        w, h = _GL[self._gl_key]["size"]
        mvp, _ = camera_matrices(s, w / h)
        p = mvp @ np.array([x, y, z, 1.0])
        ndc = p[:2] / p[3]
        return np.array([ndc[0] * config.frame_width / 2, ndc[1] * config.frame_height / 2, 0.0])

    def surface_point(self, x: float, y: float, lift: float = 0.0) -> np.ndarray:
        s = self.state()
        return self.project(x, y, float(self.height(x, y, s)) + lift, s)

    # ── GPU ────────────────────────────────────────────────────
    @staticmethod
    def _set(prog, values: dict):
        for k, v in values.items():
            if k in prog:
                if k == "u_mvp":
                    prog[k].write(v)
                else:
                    prog[k].value = v

    def render_gl(self) -> "TerrainPlate":
        gl = _GL[self._gl_key]
        s = self.state()
        ctx = _ctx()
        w, h = gl["size"]
        px = h / 1080.0
        mvp, eye = camera_matrices(s, w / h)
        mvp_b = mvp.T.astype("f4").tobytes()

        sl = list(s["slices"])[:MAX_SLICES]
        sl_u = [(math.cos(math.radians(a)), math.sin(math.radians(a)), float(k), float(L))
                for a, k, _c, L in sl] + [(1.0, 0.0, 0.0, 1.0)] * (MAX_SLICES - len(sl))
        sl_c = [_rgb(c) for _a, _k, c, _L in sl] + [(0.0, 0.0, 0.0)] * (MAX_SLICES - len(sl))
        height_u = {
            "u_H": tuple(s["H"]), "u_zs": s["zs"], "u_win": s["win"], "u_zclip": s["zclip"],
            "u_wm": s["wm"], "u_m0": s["m0"], "u_m1": s["m1"], "u_mamp": s["mamp"],
            "u_mscale": s["mscale"], "u_mseed": tuple(s["mseed"]), "u_mback": s["mback"],
        }
        common = {"u_mvp": mvp_b, "u_eye": tuple(eye), "u_fog": s["fog"], "u_fognear": s["fognear"],
                  "u_fogH": s["fogH"],
                  "u_edge": s["edge"], "u_R": gl["R"]}
        self._set(gl["prog"], {
            **height_u, **common,
            "u_px": px, "u_lw": s["lw"], "u_line": _rgb(S.TERRAIN_LINE), "u_body": _rgb(S.TERRAIN_BODY),
            "u_smile": _rgb(S.SMILE), "u_frown": _rgb(S.FROWN),
            "u_aurA": _rgb(S.CURVE_A), "u_aurB": _rgb(S.CURVE_B), "u_aurora": s["aurora"],
            "u_paint": s["paint"], "u_paintR": s["paintR"], "u_pc": [_rgb(c) for c in S.GROUND_GRADIENT],
            "u_contour": s["contour"], "u_cstep": s["cstep"], "u_grid": s["grid"], "u_gstep": s["gstep"], "u_gridR": s["gridR"],
            "u_reveal": s["reveal"], "u_rim": s["rim"], "u_mline": s["mline"], "u_tint": s["tint"], "u_tintR": s["tintR"],
            "u_sl": sl_u, "u_slc": sl_c, "u_disc": tuple(map(float, s["disc"])),
            "u_discc": _rgb(s["disc_color"]), "u_ping": tuple(map(float, s["ping"])),
        })

        ms = gl["ms"]
        ms.use()
        ms.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)
        ctx.enable(moderngl.DEPTH_TEST)
        gl["vao"].render()
        if gl["splats"] is not None:
            ms.depth_mask = False
            gl["splats"].render(s, height_u, mvp_b, eye, (w, h), px, s["time"])
            ms.depth_mask = True
            ctx.disable(moderngl.BLEND)

        # mist: additive, depth-tested against the ground, never writing depth
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        ms.depth_mask = False
        if s["dots"] > 0:
            self._set(gl["dprog"], {**height_u, **common, "u_time": s["time"], "u_px": px,
                                    "u_alpha": 0.9 * s["dots"], "u_reveal": s["reveal"],
                                    "u_col": _rgb(S.TERRAIN_LINE), "u_soft": 1.6})
            gl["dots"].render(moderngl.POINTS)
        mist = gl["mist"]
        self._set(mist, {**height_u, **common, "u_time": s["time"], "u_col": _rgb(S.MIST)})
        if s["haze"] > 0:
            self._set(mist, {"u_size": 900.0 * px, "u_alpha": 0.04 * s["haze"], "u_soft": 2.2, "u_vy": 0.02,
                             "u_near0": 3.0, "u_near1": 7.0})
            gl["banks"].render(moderngl.POINTS)
        if s["mist"] > 0:
            self._set(mist, {"u_size": 30.0 * px, "u_alpha": 0.9 * s["mist"], "u_soft": 3.5, "u_vy": 0.05,
                             "u_near0": 0.3, "u_near1": 1.2})
            gl["dust"].render(moderngl.POINTS)
        ms.depth_mask = True
        ctx.disable(moderngl.DEPTH_TEST | moderngl.BLEND)

        # bloom: resolve → ¼ → ⅛, each blurred twice (H, V)
        st, sfbo = gl["scene"]
        ctx.copy_framebuffer(sfbo, ms)
        down, blur, qv = gl["down"], gl["blur"], gl["qv"]

        def pass_(prog, key, src, dst_fbo, size, **u):
            dst_fbo.use()
            ctx.viewport = (0, 0, *size)
            src.use(0)
            prog["u_src"].value = 0
            self._set(prog, u)
            qv[key].render()

        (a1, f1), (b1, g1) = gl["b1"]
        (a2, f2), (b2, g2) = gl["b2"]
        q4, q8 = gl["q4"], gl["q8"]
        pass_(down, "down", st, f1, q4, u_texel=(1.0 / w, 1.0 / h), u_thresh=0.05)
        pass_(blur, "blur", a1, g1, q4, u_step=(1.0 / q4[0], 0.0))
        pass_(blur, "blur", b1, f1, q4, u_step=(0.0, 1.0 / q4[1]))
        pass_(down, "down", a1, f2, q8, u_texel=(0.5 / q4[0], 0.5 / q4[1]), u_thresh=0.0)
        pass_(blur, "blur", a2, g2, q8, u_step=(1.5 / q8[0], 0.0))
        pass_(blur, "blur", b2, f2, q8, u_step=(0.0, 1.5 / q8[1]))

        out = gl["out"]
        out.use()
        ctx.viewport = (0, 0, w, h)
        st.use(0)
        a1.use(1)
        a2.use(2)
        comp = gl["comp"]
        self._set(comp, {"u_scene": 0, "u_b1": 1, "u_b2": 2, "u_res": (float(w), float(h)),
                         "u_bloom": s["bloom"], "u_vig": s["vignette"], "u_grain": s["grain"],
                         "u_opacity": float(np.clip(s["opacity"], 0, 1)),
                         "u_seed": float((s["time"] * 60.0) % 997.0)})
        qv["comp"].render()

        img = np.frombuffer(out.read(components=4), dtype=np.uint8).reshape(h, w, 4)[::-1]
        self.pixel_array = np.ascontiguousarray(img)
        # while fading, add onto what is below (exact cross-dissolve on pure black)
        self._blit_add = float(s["opacity"]) < 0.999
        return self
