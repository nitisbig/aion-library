"""3D Gaussian splats on the luminous terrain (promoted from lab/2026-11-04-gaussian-splat-city).

A layer drawn *inside* TerrainPlate's render (same camera, same depth buffer, same
bloom), so the splat mountains are occluded by ridges in front of them and glow with
the rest of the frame. Every splat is a real anisotropic 3D Gaussian lying on the
ground: Σ = s₁² t₁t₁ᵀ + s₂² t₂t₂ᵀ + s₃² nnᵀ with t₁ along the contour, t₂ down the
slope and n the surface normal (all from the GLSL height field, so the splats follow
the terrain as it changes). Projection is the EWA one of 3DGS (Kerbl et al. 2023):
Σ′ = J W Σ Wᵀ Jᵀ plus a 0.3 px low-pass with opacity compensation, one quad per
Gaussian at ±3σ along the 2D eigenvectors, sorted back to front on the CPU and
blended premultiplied-over.

State keys (read from the TerrainPlate state, see SPLAT_DEFAULTS):
  splat   overall opacity of the layer (0 = layer skipped)
  form    0 = every splat in the spiral galaxy, 1 = settled on the ground. Splats
          leave the galaxy in a wave from the walker outward, fly in an arc as
          large soft blobs and sharpen into thin surface splats as they land
          (what "training" looks like)
  lift    0..1: the splats tear off the ground and rise as sparks, fading out
  gal     1 = the splats start in a spiral galaxy, 0 = they condense in place: each
          one appears just above its spot as a soft blob and settles, sharpening
  neb     galaxy centre (x, y, z); nebR its radius; nebtilt its tilt (deg)
  sbright brightness of the splats
"""

from __future__ import annotations

import math

import moderngl
import numpy as np
from manim import color_to_rgb

from .. import style as S

SPLAT_DEFAULTS: dict = {
    "splat": 0.0, "form": 1.0, "lift": 0.0, "gal": 1.0, "neb": (6.0, 3.8, 1.9), "nebR": 6.0, "nebtilt": 34.0,
    "sbright": 1.0,
}

STAR_FRAC = 0.07          # this share of the splats never lands: they stay in the sky as stars

_FN = """
uniform float u_form, u_lift, u_time, u_nebR, u_rmax, u_gal;
uniform vec3 u_neb;
uniform mat3 u_nebM;
uniform vec3 u_eye;

float hashf(float h, float k) { return fract(sin(h * 127.1 + k * 311.7) * 43758.5453); }

// the spiral galaxy every splat starts in (3 arms, a bright core)
vec3 galaxy(float h) {
    float arm = floor(hashf(h, 1.0) * 3.0);
    float r = u_nebR * pow(hashf(h, 2.0), 0.75);
    float th = arm * 2.0944 + 0.55 * r + 0.55 * (hashf(h, 3.0) - 0.5) + 0.35 * u_time;
    float thick = 0.35 * (1.0 - r / u_nebR) + 0.08;
    vec3 q = vec3(r * cos(th), r * sin(th), (hashf(h, 4.0) - 0.5) * 2.0 * thick);
    q.xy += 0.5 * (vec2(hashf(h, 5.0), hashf(h, 6.0)) - 0.5) * (0.4 + r * 0.15);
    return u_neb + u_nebM * q;
}

// a star in the sky dome (the splats that never land)
vec3 star(float h) {
    float a = hashf(h, 7.0) * 6.2831853, e = mix(0.06, 0.75, pow(hashf(h, 8.0), 0.7));
    return vec3(cos(a) * cos(e), sin(a) * cos(e), sin(e)) * 46.0;
}

vec3 normal_at(vec2 p) {
    float e = 0.05;
    float hx = height(p + vec2(e, 0.0)) - height(p - vec2(e, 0.0));
    float hy = height(p + vec2(0.0, e)) - height(p - vec2(0.0, e));
    return normalize(vec3(-hx / (2.0 * e), -hy / (2.0 * e), 1.0));
}

// progress of one splat from the galaxy to the ground (wave from the walker outward)
float land(vec2 p, float h) {
    float delay = 0.55 * clamp((length(p) - u_m0) / (u_rmax - u_m0), 0.0, 1.0) + 0.2 * hashf(h, 9.0);
    return clamp((u_form - delay) / 0.25, 0.0, 1.0);                  // a front 0.25 wide sweeps outward
}

float rise(float h) { return clamp((u_lift * 1.6 - 0.6 * hashf(h, 10.0)) / 1.0, 0.0, 1.0); }

// world position of splat (p, h)
vec3 splat_pos(vec2 p, float h, bool isStar) {
    vec3 g = vec3(p, height(p) + 0.03);
    vec3 home = isStar ? star(h) : g;
    float f = land(p, h);
    float fe = f * f * (3.0 - 2.0 * f);
    vec3 from = u_gal > 0.0 ? mix(home + vec3(0.0, 0.0, 0.6 + 0.9 * hashf(h, 23.0)), galaxy(h), u_gal)
                            : home + vec3(0.0, 0.0, 0.6 + 0.9 * hashf(h, 23.0));
    vec3 pos = mix(from, home, fe);
    pos.z += u_gal * sin(3.14159 * fe) * (1.2 + 1.2 * hashf(h, 11.0));  // from the galaxy they fly in an arc
    float l = rise(h);
    vec3 drift = vec3(hashf(h, 12.0) - 0.5, hashf(h, 13.0) - 0.5, 0.0) * 4.0;
    pos += (vec3(0.0, 0.0, 9.0) + drift) * l * l;
    return pos;
}
"""

_TF_VS = """
in vec4 in_s;          // x, y, seed, size
out vec3 o_pos;
void main() { o_pos = splat_pos(in_s.xy, in_s.z, in_s.z < %STAR%); }
"""

_VS = """
in vec4 in_s;
uniform mat4 u_mvp;
uniform vec3 u_right, u_up, u_fwd;
uniform float u_fy, u_alpha, u_fog, u_fognear, u_fogH, u_bright, u_edge;
uniform vec2 u_res;
uniform vec3 u_pal[6];
out vec2 v_xy;
out vec4 v_col;

const vec2 CORNER[4] = vec2[](vec2(-1, -1), vec2(1, -1), vec2(-1, 1), vec2(1, 1));

vec3 ramp(float t) {
    t = clamp(t, 0.0, 1.0) * 5.0;
    int i = int(min(floor(t), 4.0));
    return mix(u_pal[i], u_pal[i + 1], t - float(i));
}

void cull() { gl_Position = vec4(3.0, 3.0, 3.0, 1.0); v_col = vec4(0.0); v_xy = vec2(0.0); }

void main() {
    vec2 p = in_s.xy;
    float h = in_s.z, size = in_s.w;
    bool isStar = h < %STAR%;
    if (!isStar && length(p) > u_edge) { cull(); return; }
    vec3 pos = splat_pos(p, h, isStar);
    float f = land(p, h);
    float l = rise(h);

    // shape: thin surface splat on the ground, round soft blob in flight, round point in the galaxy
    vec3 n = normal_at(p);
    vec3 t1 = cross(n, vec3(0.0, 0.0, 1.0));
    t1 = length(t1) < 1e-3 ? vec3(1.0, 0.0, 0.0) : normalize(t1);
    vec3 t2 = cross(n, t1);
    float an = 1.6 + 1.4 * hashf(h, 14.0);
    vec3 s = size * vec3(an, 0.6, 0.05);
    float flight = sin(3.14159 * f);
    float onGround = isStar ? 0.0 : smoothstep(0.85, 1.0, f) * (1.0 - l);
    float spark = step(hashf(h, 21.0), 0.25);                         // a quarter of them become sparks
    float blob = mix(1.4 * size * (1.0 - f) * (1.0 - f), (0.25 * size + 0.012) * flight, u_gal) + 0.022 * l + 0.018 * (1.0 - f) * (1.0 - l) * (1.0 - onGround);
    s *= onGround;
    if (isStar) blob += 0.10 * f;

    // colour: altitude ramp teal → blue → violet → magenta → peach, lit from the moon side
    float hn = isStar ? hashf(h, 15.0) : clamp(pos.z / 5.2, 0.0, 1.0);
    vec3 gal = ramp(0.15 + 0.85 * hashf(h, 2.0));               // galaxy colour (by radius)
    vec3 col = ramp(hn * 0.92 + 0.08 * hashf(h, 16.0));
    float lit = pow(max(dot(n, normalize(vec3(-0.45, 0.55, 0.70))), 0.0), 2.2);
    vec3 V = normalize(u_eye - pos);
    float rim = pow(1.0 - max(dot(n, V), 0.0), 3.0);
    float alt = 0.18 + 0.82 * smoothstep(0.2, 3.5, pos.z);           // the valley floor stays dark
    col = col * (0.10 + 0.95 * lit) * alt + col * rim * 0.45 * alt;
    col = mix(mix(col * 0.8, gal * 0.9, u_gal), col, smoothstep(0.55, 1.0, f));
    col = mix(col, ramp(0.55 + 0.45 * hashf(h, 22.0)) * 1.6, smoothstep(0.0, 0.3, l));   // sparks burn bright as they rise
    col *= u_bright * (0.8 + 0.4 * hashf(h, 17.0));
    if (isStar) col = mix(vec3(0.85, 0.9, 1.0), ramp(hashf(h, 18.0)), 0.5) * (0.6 + 0.8 * pow(hashf(h, 19.0), 6.0));

    // fog: height fog like the ground's (stars and the galaxy sit above it)
    float d = length(u_eye - pos);
    float zm = max(0.5 * (pos.z + u_eye.z), 0.0);
    float vis = exp(-u_fog * max(d - u_fognear, 0.0) * exp(-zm / u_fogH));
    vis = mix(1.0, vis * vis * vis, isStar ? 0.0 : onGround);   // colour drowns in fog faster than lines
    float tw = isStar ? 0.55 + 0.45 * sin(u_time * (0.8 + hashf(h, 20.0)) + h * 90.0) : 1.0;
    float a = u_alpha * vis * tw * mix(0.55, 0.32, flight) * (1.0 - smoothstep(0.55, 1.0, l));
    a *= mix(1.0 - smoothstep(0.0, 0.25, l), 1.0, spark);
    a *= isStar ? 0.9 : mix(0.45, 1.0, onGround) * (0.35 + 0.65 * alt);
    a *= mix(smoothstep(0.0, 0.5, f), 1.0, u_gal);                   // condensing: born out of nothing

    // EWA projection of the 3D Gaussian (rows of the view: right, up, forward)
    vec3 dd = pos - u_eye;
    float vx = dot(dd, u_right), vy = dot(dd, u_up), vz = dot(dd, u_fwd);
    a *= smoothstep(1.2, 3.5, vz) * mix(1.0, smoothstep(3.0, 7.0, vz), flight);                                     // nothing big flies past the lens
    if (vz < 0.3 || a < 0.004) { cull(); return; }
    float iz = 1.0 / vz;
    vec2 c = vec2(u_fy * vx * iz, u_fy * vy * iz);
    mat3 A = mat3(t1 * s.x, t2 * s.y, n * s.z);
    float sa = 0.0, sb = 0.0, sc = 0.0;
    for (int k = 0; k < 3; k++) {
        vec3 ax = A[k];
        vec3 av = vec3(dot(ax, u_right), dot(ax, u_up), dot(ax, u_fwd));
        vec2 j = vec2(u_fy * iz * (av.x - vx * iz * av.z), u_fy * iz * (av.y - vy * iz * av.z));
        sa += j.x * j.x; sb += j.x * j.y; sc += j.y * j.y;
    }
    float bp = u_fy * iz * blob;
    sa += bp * bp; sc += bp * bp;
    float det0 = sa * sc - sb * sb;
    sa += 0.3; sc += 0.3;
    float det1 = sa * sc - sb * sb;
    a *= sqrt(max(det0, 0.0) / det1);
    float mid = 0.5 * (sa + sc);
    float rad = sqrt(max(0.25 * (sa - sc) * (sa - sc) + sb * sb, 1e-12));
    float l1 = mid + rad, l2 = max(mid - rad, 0.1);
    vec2 e1 = abs(sb) > 1e-7 ? normalize(vec2(sb, l1 - sa)) : (sa >= sc ? vec2(1, 0) : vec2(0, 1));
    vec2 e2 = vec2(-e1.y, e1.x);
    float r1 = 3.0 * sqrt(l1), r2 = 3.0 * sqrt(l2);
    if (r1 > 0.8 * u_res.y || a < 0.004) { cull(); return; }

    vec2 cr = CORNER[gl_VertexID];
    vec2 px = c + cr.x * e1 * r1 + cr.y * e2 * r2;
    // depth: the centre pulled toward the camera by its own size, so a splat is not cut by its own slope
    vec4 clip = u_mvp * vec4(pos + V * (2.5 * max(max(s.x, s.y), blob) + 0.02), 1.0);
    gl_Position = vec4(px / (0.5 * u_res) * clip.w, clip.z, clip.w);
    v_xy = cr * 3.0;
    v_col = vec4(col, min(a, 0.98));
}
"""

_FS = """
in vec2 v_xy;
in vec4 v_col;
out vec4 f_col;
void main() {
    float r2 = dot(v_xy, v_xy);
    if (r2 > 9.0) discard;
    float a = v_col.a * exp(-0.5 * r2);
    if (a < 1.0 / 255.0) discard;
    f_col = vec4(v_col.rgb * a, a);
}
"""


def _rgb(c):
    return tuple(float(v) for v in color_to_rgb(c))


def mountain_mask(x, y, m0: float, m1: float, mback: float):
    """Python mirror of mountain_mask() in terrain.glsl (with wm = 1)."""
    r = np.hypot(np.where(x < 0, x * mback, x), y)
    t = np.clip((r - m0) / (m1 - m0), 0, 1)
    return t * t * (3 - 2 * t)


def splat_seeds(n: int, m0: float, rmax: float, seed: int = 5, m1: float = 8.0, mback: float = 0.3) -> np.ndarray:
    """(x, y, h, size) per splat: ground splats where the mountains are (density ∝ 1/r, so
    even on screen, thinned by the mountain mask); h < STAR_FRAC marks the sky stars."""
    rng = np.random.default_rng(seed)
    out = []
    while sum(len(o) for o in out) < n:
        k = 4 * n
        r = m0 + (rmax - m0) * rng.random(k) ** 1.5
        a = rng.uniform(0, 2 * np.pi, k)
        x, y = r * np.cos(a), r * np.sin(a)
        keep = rng.random(k) < mountain_mask(x, y, m0, m1, mback)
        out.append(np.stack([x[keep], y[keep], r[keep]], 1))
    xyr = np.concatenate(out)[:n]
    h = rng.random(n)
    size = (0.018 + 0.0075 * xyr[:, 2]) * (0.6 + 0.8 * rng.random(n))
    return np.stack([xyr[:, 0], xyr[:, 1], h, size], 1).astype("f4")


class SplatLayer:
    """Built and driven by TerrainPlate (pass `splats=N`)."""

    def __init__(self, ctx, head: str, n: int, m0: float, rmax: float = 30.0, seed: int = 5):
        star = f"{STAR_FRAC:.4f}"
        self.ctx, self.rmax = ctx, rmax
        self.tf = ctx.program(vertex_shader=head + _FN + _TF_VS.replace("%STAR%", star), varyings=["o_pos"])
        self.prog = ctx.program(vertex_shader=head + _FN + _VS.replace("%STAR%", star),
                                fragment_shader="#version 330\n" + _FS)
        self.data = splat_seeds(n, m0, rmax, seed)
        self.n = n
        self.src = ctx.buffer(self.data.tobytes())
        self.pos = ctx.buffer(reserve=n * 12)
        self.tf_vao = ctx.vertex_array(self.tf, [(self.src, "4f", "in_s")])
        self.inst = ctx.buffer(reserve=n * 16)
        self.vao = ctx.vertex_array(self.prog, [(self.inst, "4f/i", "in_s")])

    @staticmethod
    def _set(prog, values: dict):
        for k, v in values.items():
            if k in prog:
                if k in ("u_mvp", "u_nebM"):
                    prog[k].write(v)
                else:
                    prog[k].value = v

    def render(self, s: dict, height_u: dict, mvp_b: bytes, eye, size, px: float, time: float):
        if s["splat"] <= 0.0:
            return
        w, h = size
        yaw, pitch = math.radians(s["yaw"]), math.radians(s["pitch"])
        tgt = np.array(s["target"], float)
        fwd = tgt - eye
        fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0.0, 0.0, 1.0])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        tl = math.radians(s["nebtilt"])
        cz, sz = math.cos(yaw + math.pi / 2), math.sin(yaw + math.pi / 2)     # tilt the galaxy toward the camera
        Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1.0]])
        Rx = np.array([[1, 0, 0], [0, math.cos(tl), -math.sin(tl)], [0, math.sin(tl), math.cos(tl)]])
        M = (Rz @ Rx).T.astype("f4").tobytes()                               # column-major for GLSL
        fn = {**height_u, "u_form": float(s["form"]), "u_lift": float(s["lift"]), "u_time": float(time),
              "u_nebR": float(s["nebR"]), "u_neb": tuple(map(float, s["neb"])), "u_nebM": M,
              "u_eye": tuple(map(float, eye)), "u_m0": float(s["m0"]), "u_rmax": self.rmax,
              "u_gal": float(s["gal"])}

        # 1 · where is every splat this frame (transform feedback) → back-to-front order
        self._set(self.tf, fn)
        self.tf_vao.transform(self.pos, mode=moderngl.POINTS, vertices=self.n)
        P = np.frombuffer(self.pos.read(), dtype="f4").reshape(-1, 3)
        order = np.argsort(-((P - eye) @ fwd), kind="stable")
        self.inst.write(self.data[order].tobytes())

        # 2 · draw: premultiplied over, depth-tested against the ground, no depth writes
        fy = 0.5 * h / math.tan(math.radians(s["fov"]) / 2)
        self._set(self.prog, {**fn, "u_mvp": mvp_b, "u_right": tuple(right), "u_up": tuple(up), "u_fwd": tuple(fwd),
                              "u_fy": float(fy), "u_res": (float(w), float(h)),
                              "u_alpha": float(np.clip(s["splat"], 0, 1)), "u_bright": float(s["sbright"]),
                              "u_fog": s["fog"], "u_fognear": s["fognear"], "u_fogH": s["fogH"], "u_edge": s["edge"],
                              "u_pal": [_rgb(c) for c in S.SPLAT_RAMP]})
        ctx = self.ctx
        ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=self.n)
