"""Procedural point sets for 'Does the Past Still Exist?'. Taichi bakes the noisy surfaces (the remembered
place's ground, the tunnel of time); numpy builds the rest (tree, people, cosmos, the block of moments, text).
Every set is cached as out/geo_<name>_<hash>.npz (hash of the builder's source + its helpers).

Vertex layout (11 floats): pos(3) | A = (albedo, green, size, aux) | B = (b0, b1, b2, b3).
Lines use the same layout, two vertices per segment. aux/B mean different things per set (see shaders/world.vert).

    uv run python lab/2026-11-15-does-the-past-exist/geometry.py            # build all + stats
    uv run python lab/2026-11-15-does-the-past-exist/geometry.py scene      # (re)build one set
"""
import hashlib
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TAU = 2 * np.pi
FONT = Path.home() / ".local/share/fonts/inter/InterVariable.ttf"


def pack(pos, alb, green, size, aux, b0=0.0, b1=0.0, b2=0.0, b3=0.0):
    n = len(pos)
    o = np.zeros((n, 11), np.float32)
    o[:, :3] = pos
    for j, v in enumerate((alb, green, size, aux, b0, b1, b2, b3)):
        o[:, 3 + j] = v
    return o


def polyline_segments(P, attrs):
    """P (n, 3) polyline, attrs (n, 8) → GL_LINES vertex pairs."""
    V = np.concatenate([P, attrs], 1).astype(np.float32)
    return np.stack([V[:-1], V[1:]], 1).reshape(-1, 11)


def attrs(n, alb=1.0, grn=0.0, size=1.0, aux=0.0, b0=0.0, b1=0.0, b2=0.0, b3=0.0):
    A = np.zeros((n, 8), np.float32)
    for j, v in enumerate((alb, grn, size, aux, b0, b1, b2, b3)):
        A[:, j] = v
    return A


def sst(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def cell_hash(P, cell):
    """A stable pseudo-random value in [0, 1) per voxel cell: points of one fragment share it."""
    c = np.floor(P / cell)
    v = np.sin(c[:, 0] * 127.1 + c[:, 1] * 311.7 + c[:, 2] * 74.7) * 43758.5453
    return (v - np.floor(v)).astype(np.float32)


def _ti():
    import taichi as ti
    ti.init(arch=ti.cpu, cpu_max_num_threads=2, log_level=ti.WARN, offline_cache=True)
    return ti


def _noise_funcs(ti):
    vec3 = ti.math.vec3

    @ti.func
    def h3(p):
        return ti.math.fract(ti.sin(p.x * 127.1 + p.y * 311.7 + p.z * 74.7) * 43758.5453)

    @ti.func
    def vnoise(p):
        i = ti.floor(p)
        f = p - i
        w = f * f * (3.0 - 2.0 * f)
        a = ti.math.mix(h3(i), h3(i + vec3(1, 0, 0)), w.x)
        b = ti.math.mix(h3(i + vec3(0, 1, 0)), h3(i + vec3(1, 1, 0)), w.x)
        c = ti.math.mix(h3(i + vec3(0, 0, 1)), h3(i + vec3(1, 0, 1)), w.x)
        d = ti.math.mix(h3(i + vec3(0, 1, 1)), h3(i + vec3(1, 1, 1)), w.x)
        return ti.math.mix(ti.math.mix(a, b, w.y), ti.math.mix(c, d, w.y), w.z)

    @ti.func
    def fbm(p):
        v, a, tot = 0.0, 0.5, 0.0
        q = p
        for _ in ti.static(range(4)):
            v += a * vnoise(q)
            tot += a
            q = q * 2.03 + vec3(17.1, 9.2, 3.7)
            a *= 0.5
        return v / tot

    @ti.func
    def sstep(e0, e1, x):
        t = ti.math.clamp((x - e0) / (e1 - e0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    return h3, vnoise, fbm, sstep


# ── darkness: a vast sparse field; points awaken one by one ─────────────────
def build_dust(rng):
    n = 70_000
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    r = 2.5 + 46 * rng.uniform(0, 1, n) ** 1.5
    pos = d * r[:, None]
    pos[:, 1] *= 0.55
    birth = rng.uniform(0, 1, n) ** 0.75
    first = rng.choice(n, 30, replace=False)          # the very first: isolated sparks in front of the camera
    pos[first] = np.c_[rng.uniform(-4, 4, 30), rng.uniform(-2.2, 2.2, 30), -rng.uniform(5, 16, 30)]
    birth[first] = np.sort(rng.uniform(0, 0.05, 30))
    size = rng.choice([1.0, 1.5, 2.3, 3.4], n, p=[0.6, 0.25, 0.11, 0.04])
    size[first] = rng.choice([2.3, 3.4], 30)
    alb = rng.uniform(0.45, 1.2, n)
    alb[first] = 1.4
    grn = (rng.uniform(0, 1, n) < 0.1) * rng.uniform(0.4, 1.0, n)
    return dict(pts=pack(pos, alb, grn, size, birth, rng.uniform(0, 1, n), pos[:, 0], pos[:, 1], pos[:, 2]))


# ── text made of particles (title, closing question) ─────────────────────────
def _text_points(rng, lines, n_per, width, y_gap):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), 200)
    try:
        font.set_variation_by_axes([300])
    except Exception:
        pass
    out = []
    for li, text in enumerate(lines):
        dr0 = ImageDraw.Draw(Image.new("L", (10, 10)))
        adv = [dr0.textlength(ch, font=font) + 30 for ch in text]
        tw = sum(adv) - 30
        W, H = int(tw + 80), 300
        im = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(im)
        x = 40
        for ch, a in zip(text, adv):
            dr.text((x, 40), ch, fill=255, font=font)
            x += a
        m = np.asarray(im, np.float32) / 255
        ys, xs = np.nonzero(m > 0.5)
        n = int(n_per * tw / 2000)
        k = rng.choice(len(xs), n)
        scale = width / 3600                      # every line uses the same glyph scale
        px = (xs[k] + rng.uniform(-0.5, 0.5, n) - W / 2) * scale
        py = -(ys[k] + rng.uniform(-0.5, 0.5, n) - 145) * scale - li * y_gap
        pos = np.c_[px, py, rng.normal(0, 0.03, n)]
        out.append(pack(pos, rng.uniform(0.55, 1.0, n), 0.0, rng.choice([1.0, 1.6], n, p=[0.85, 0.15]),
                        rng.uniform(0, 1, n), li))
    pts = np.concatenate(out)
    pts[:, 1] -= pts[:, 1].mean()
    return pts


def build_title(rng):
    return dict(pts=_text_points(rng, ["DOES  THE  PAST  STILL  EXIST?"], 20_000, 9.0, 0.0))


def build_question(rng):
    return dict(pts=_text_points(rng, ["IF THE PAST NO LONGER EXISTS,", "WHERE DID IT GO?"], 16_000, 6.6, 0.95))


# ── the remembered place: people and a tree (shared by the scene and the block) ──
def _capsule(rng, a, b, r, n):
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = rng.uniform(0, 1, n)
    ax = b - a
    L = np.linalg.norm(ax)
    ax = ax / L
    tmp = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 0, 1.0])
    e1 = np.cross(ax, tmp)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    th = rng.uniform(0, TAU, n)
    rr = r * (1 + rng.normal(0, 0.04, n))
    return a + t[:, None] * (b - a) + rr[:, None] * (np.cos(th)[:, None] * e1 + np.sin(th)[:, None] * e2)


def figure_points(rng, n, scale=1.0, stride=0.0):
    """A standing person (+z faces the viewer), feet at y = 0. stride swings legs/arms."""
    parts = [  # (a, b, radius, weight)
        ((0, 1.60, 0), (0, 1.70, 0), 0.105, 0.11),          # head
        ((0, 1.47, 0), (0, 1.53, 0), 0.05, 0.01),           # neck
        ((0, 1.05, 0), (0, 1.40, 0), 0.155, 0.25),          # torso
        ((-0.19, 1.40, 0), (-0.24 - 0.0, 0.82, 0.12 * stride), 0.045, 0.08),
        ((0.19, 1.40, 0), (0.24, 0.82, -0.12 * stride), 0.045, 0.08),
        ((-0.085, 0.98, 0), (-0.10, 0.04, -0.18 * stride), 0.07, 0.2),
        ((0.085, 0.98, 0), (0.10, 0.04, 0.18 * stride), 0.07, 0.2),
    ]
    w = np.array([p[3] for p in parts])
    cnt = rng.multinomial(n, w / w.sum())
    P = np.concatenate([_capsule(rng, a, b, r, c) for (a, b, r, _), c in zip(parts, cnt)])
    P[:, 0] *= 1.0 + 0.25 * np.exp(-((P[:, 1] - 1.4) / 0.06) ** 2)     # shoulders
    return P * scale


def tree_points(rng, n_branch=26_000, n_leaf=34_000):
    """A lone tree, base at the origin: trunk + branches (cylinder surfaces) and foliage clumps.
    Returns (points (n, 3), leafiness (n,), segments [(a, b, r)])."""
    segs = []

    def grow(a, d, L, r, depth):
        b = a + d * L
        segs.append((a, b, r, depth))
        if depth >= 4:
            return
        k = 2 if depth < 3 else 3
        for i in range(k):
            ang = rng.uniform(0.35, 0.75) * (1 if i % 2 == 0 else -1)
            spin = rng.uniform(0, TAU)
            tmp = np.array([np.cos(spin), 0, np.sin(spin)])
            side = np.cross(d, tmp)
            side /= np.linalg.norm(side) + 1e-9
            nd = d * np.cos(ang) + side * np.sin(ang) + np.array([0, 0.18, 0])
            nd /= np.linalg.norm(nd)
            grow(b, nd, L * rng.uniform(0.62, 0.78), r * 0.62, depth + 1)

    grow(np.array([0.0, 0, 0]), np.array([0.05, 1.0, 0.0]) / np.linalg.norm([0.05, 1, 0]), 1.6, 0.16, 0)
    lens = np.array([np.linalg.norm(b - a) * r for a, b, r, _ in segs])
    cnt = rng.multinomial(n_branch, lens / lens.sum())
    P = [_capsule(rng, a, b, r, c) for (a, b, r, _), c in zip(segs, cnt)]
    tips = [b for a, b, r, dp in segs if dp >= 3]
    tips = np.array(tips)
    m = rng.integers(0, len(tips), n_leaf)
    g = rng.normal(size=(n_leaf, 3))
    rad = rng.uniform(0.35, 0.7, len(tips))[m]
    leaves = tips[m] + g * rad[:, None] * np.r_[1.0, 0.7, 1.0]
    pts = np.concatenate(P + [leaves])
    leafy = np.r_[np.zeros(n_branch), np.ones(n_leaf)]
    return pts, leafy, [(a, b, r) for a, b, r, _ in segs]


TREE_AT = np.array([2.7, 0.0, -2.6])
SUN_AT = np.array([-6.5, 2.4, -15.0])
FIGS = [(np.array([-1.0, 0, -0.6]), 1.0, 0.3), (np.array([-0.15, 0, -1.1]), 1.04, -0.2),
        (np.array([-0.55, 0, -0.25]), 0.62, 0.5)]


def ground_h(x, z):
    """numpy twin of the scene kernel's gentle ground (flat near the people, hills far off)."""
    r = np.sqrt(x * x + z * z)
    return 0.9 * (np.sin(x * 0.31 + 1.0) * np.cos(z * 0.27) * 0.6 + 0.4 * np.sin(x * 0.13 - z * 0.2)) * sst(4.0, 11.0, r)


def build_scene(rng):
    """The remembered moment: ground (Taichi), a tree, three people, a low sun.
    aux = reveal order; b0 = kind (0 ground, 1 tree, 2 person, 3 sun); b1 = fragment id; b2 = rand; b3 = person idx."""
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm, sstep = _noise_funcs(ti)
    N = 520_000
    u = rng.uniform(0, 1, (N, 4)).astype(np.float32)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            r = 17.0 * ti.sqrt(u[i, 0])
            th = 6.283185307 * u[i, 1]
            x, z = r * ti.cos(th), r * ti.sin(th)
            base = 0.9 * (ti.sin(x * 0.31 + 1.0) * ti.cos(z * 0.27) * 0.6 + 0.4 * ti.sin(x * 0.13 - z * 0.2))
            h = base * sstep(4.0, 11.0, r) + 2.4 * (fbm(vec3(x * 0.11, z * 0.11, 3.0)) - 0.3) * sstep(9.0, 16.0, r)
            fine = fbm(vec3(x * 0.9, z * 0.9, 11.0))
            h += 0.12 * (fine - 0.5)
            dens = fbm(vec3(x * 0.25, z * 0.25, 29.0))
            keep = (sstep(0.28, 0.5, dens) * 0.85 + 0.15) * (1.0 - sstep(13.0, 17.0, r) * 0.7)
            out[i, 0] = x
            out[i, 1] = h
            out[i, 2] = z
            out[i, 3] = 0.3 + 0.7 * fine
            out[i, 4] = sstep(0.62, 0.8, dens) * 0.5
            out[i, 5] = 2.4 if u[i, 2] > 0.997 else 1.0
            out[i, 6] = r / 17.0 * 0.8 + 0.2 * u[i, 3]
            out[i, 7] = 1.0 if u[i, 2] < keep else 0.0

    out = np.zeros((N, 8), np.float32)
    gen(u, out)
    ti.reset()
    out = out[out[:, 7] > 0.5]
    gpos = out[:, :3]
    ground = pack(gpos, out[:, 3], out[:, 4], out[:, 5], out[:, 6], 0.0, cell_hash(gpos, 1.3),
                  rng.uniform(0, 1, len(out)))
    # the tree
    tp, leafy, tsegs = tree_points(rng)
    tp = tp + TREE_AT
    tree = pack(tp, np.where(leafy > 0, rng.uniform(0.35, 0.9, len(tp)), rng.uniform(0.7, 1.1, len(tp))),
                leafy * rng.uniform(0.2, 0.7, len(tp)), np.where(rng.uniform(0, 1, len(tp)) < 0.01, 2.2, 1.0),
                0.15 + 0.1 * tp[:, 1] / 6, 1.0, cell_hash(tp, 0.9), rng.uniform(0, 1, len(tp)))
    # the people
    figs = []
    for j, (at, sc, rot) in enumerate(FIGS):
        P = figure_points(rng, 16_000, sc)
        c, s = np.cos(rot), np.sin(rot)
        P = np.c_[c * P[:, 0] + s * P[:, 2], P[:, 1], -s * P[:, 0] + c * P[:, 2]] + at
        figs.append(pack(P, rng.uniform(0.75, 1.15, len(P)), 0.0, 1.0, rng.uniform(0, 1, len(P)), 2.0,
                         cell_hash(P, 0.35), rng.uniform(0, 1, len(P)), float(j)))
    # a low sun on the horizon: disc + sparse halo
    d = rng.normal(size=(9000, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    sun = SUN_AT + d * 0.8
    halo = SUN_AT + rng.normal(size=(5000, 3)) * np.abs(rng.standard_cauchy((5000, 1))).clip(0, 6) * 0.5
    sp = np.concatenate([sun, halo])
    sunp = pack(sp, np.r_[np.full(9000, 1.2), rng.uniform(0.2, 0.6, 5000)], 0.35, 1.0, 0.0, 3.0,
                cell_hash(sp, 1.0), rng.uniform(0, 1, len(sp)))
    # thin lines: tree branches (crisp skeleton) and a faint horizon
    segs = []
    for a, b, r in tsegs:
        P = np.linspace(a, b, 6) + TREE_AT
        A = attrs(6, 0.5, 0.0, 1.0, 0.2, 1.0, 0.0, 0.0)
        A[:, 5] = cell_hash(P, 0.9)
        segs.append(polyline_segments(P, A))
    th = np.linspace(-0.9, 0.9, 200) - np.pi / 2
    for rr, alb in ((15.5, 0.35), (12.0, 0.2)):
        P = np.c_[rr * np.cos(th), 0.0 * th, rr * np.sin(th)]
        P[:, 1] = ground_h(P[:, 0], P[:, 2]) + 0.6 * np.sin(th * 7) * sst(9, 16, rr) + 0.4
        A = attrs(len(P), alb, 0.0, 1.0, 0.9, 0.0)
        A[:, 5] = cell_hash(P, 1.3)
        segs.append(polyline_segments(P, A))
    return dict(pts=np.concatenate([ground, tree] + figs + [sunp]), lines=np.concatenate(segs))


# ── the tunnel of time (Taichi walls), moment rings, rails, streaking dust ───
def tcx(s):
    return 1.4 * np.sin(0.045 * s) + 0.5 * np.sin(0.15 * s + 1.0)


def tcy(s):
    return 0.7 * np.sin(0.06 * s + 2.0)


def tR(s):
    return 3.0 + 0.5 * np.sin(0.08 * s)


S0, S1 = -25.0, 165.0


def build_tunnel(rng):
    """Walls: kind 0 (aux = s). Lines: rings kind 1 (aux = s), rails kind 2, streaks kind 3 (b1 = head/tail).
    Points: floating motes kind 4. b2 = fragment id (cell hash)."""
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm, sstep = _noise_funcs(ti)
    N = 1_250_000
    u = rng.uniform(0, 1, (N, 4)).astype(np.float32)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            s = S0 + (S1 - S0) * u[i, 0]
            th = 6.283185307 * u[i, 1]
            c, sn = ti.cos(th), ti.sin(th)
            n1 = fbm(vec3(c * 1.3, sn * 1.3, s * 0.10))
            n2 = fbm(vec3(c * 4.1, sn * 4.1, s * 0.42) + 5.0)
            r0 = 3.0 + 0.5 * ti.sin(0.08 * s)
            r = r0 * (1.0 + 0.5 * (n1 - 0.5) + 0.16 * (n2 - 0.5))
            # strata: terraces like layered rock, the record of time
            strat = ti.math.fract(s * 0.35 + 2.0 * n1)
            r += 0.12 * sstep(0.85, 1.0, strat)
            r -= 1.0 * u[i, 3] * u[i, 3] * sstep(0.64, 0.78, n2)
            cx = 1.4 * ti.sin(0.045 * s) + 0.5 * ti.sin(0.15 * s + 1.0)
            cy = 0.7 * ti.sin(0.06 * s + 2.0)
            d = fbm(vec3(c * 2.2, sn * 2.2, s * 0.2) + 31.0)
            keep = sstep(0.30, 0.56, d) * 0.92 + 0.08
            # flatten the bottom into a floor
            y = r * sn
            y = ti.max(y, -r0 * 0.78 + 0.08 * (n2 - 0.5))
            out[i, 0] = cx + r * c
            out[i, 1] = cy + y
            out[i, 2] = -s
            out[i, 3] = 0.25 + 0.5 * n2 + 0.3 * sstep(0.85, 1.0, strat)
            out[i, 4] = sstep(0.62, 0.82, n1) * 0.7
            out[i, 5] = 2.6 if u[i, 2] > 0.996 else 1.0
            out[i, 6] = s
            out[i, 7] = 1.0 if u[i, 2] < keep else 0.0

    out = np.zeros((N, 8), np.float32)
    gen(u, out)
    ti.reset()
    out = out[out[:, 7] > 0.5]
    wall = pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], out[:, 6], 0.0, rng.uniform(0, 1, len(out)),
                cell_hash(out[:, :3], 1.6))
    del out, u
    segs = []
    # moment rings: one every 4 units
    th = np.linspace(0, TAU, 97)
    for s in np.arange(S0, S1, 4.0):
        r = tR(s) * 1.02
        P = np.c_[tcx(s) + r * np.cos(th), tcy(s) + np.maximum(r * np.sin(th), -tR(s) * 0.78), np.full(len(th), -s)]
        A = attrs(len(P), 0.8, 0.0, 1.0, s, 1.0)
        A[:, 6] = cell_hash(P, 1.6)
        segs.append(polyline_segments(P, A))
    # thin rails along the floor and walls
    ss = np.arange(S0, S1, 0.6)
    for k in range(10):
        th0 = -np.pi / 2 + (k - 4.5) * 0.32
        r = tR(ss) * (0.8 if abs(k - 4.5) < 2 else 1.1)
        P = np.c_[tcx(ss) + r * np.cos(th0), tcy(ss) + np.maximum(r * np.sin(th0), -tR(ss) * 0.76), -ss]
        A = attrs(len(ss), 0.55, 0.0, 1.0, 0, 2.0)
        A[:, 3] = ss
        A[:, 6] = cell_hash(P, 1.6)
        segs.append(polyline_segments(P, A))
    # streaking dust (kind 3): head (b1 = 0) / tail (b1 = 1); the shader offsets the tail by camera velocity
    m = 6000
    s0 = rng.uniform(S0, S1, m)
    a = rng.uniform(0, TAU, m)
    rr = tR(s0) * np.sqrt(rng.uniform(0.02, 0.8, m))
    P = np.c_[tcx(s0) + rr * np.cos(a), tcy(s0) + rr * np.sin(a), -s0]
    V = np.zeros((m, 2, 11), np.float32)
    for e in range(2):
        V[:, e, :3] = P
        V[:, e, 3:7] = np.c_[rng.uniform(0.5, 1.2, m), (rng.uniform(0, 1, m) < 0.3) * 0.9, np.ones(m), s0]
        V[:, e, 7:11] = np.c_[np.full(m, 3.0), np.full(m, float(e)), cell_hash(P, 1.6), rng.uniform(0, 1, m)]
    segs.append(V.reshape(-1, 11))
    # floating motes inside the tunnel (kind 4)
    m2 = 40_000
    s0 = rng.uniform(S0, S1, m2)
    a = rng.uniform(0, TAU, m2)
    rr = tR(s0) * np.sqrt(rng.uniform(0.0, 0.85, m2))
    P = np.c_[tcx(s0) + rr * np.cos(a), tcy(s0) + rr * np.sin(a), -s0]
    motes = pack(P, rng.uniform(0.2, 0.8, m2), (rng.uniform(0, 1, m2) < 0.25) * 0.8,
                 rng.choice([1.0, 2.0, 3.2], m2, p=[0.7, 0.24, 0.06]), s0, 4.0, rng.uniform(0, 1, m2), cell_hash(P, 1.6))
    return dict(pts=np.concatenate([wall, motes]), lines=np.concatenate(segs))


# ── the cosmos: Sun, Earth, Andromeda, background stars, incoming light shells ──
EARTH = np.array([16.0, 0.0, 0.0])
GAL = np.array([-150.0, 55.0, -330.0])
N_SHELL = 14


def build_cosmos(rng):
    """kind b0: 0 galaxy, 1 sun, 2 earth, 3 stars, 4 shells (b1 = shell phase). Lines: 5 sun→earth, 6 galaxy→earth
    (b1 = position along the path)."""
    pts = []
    # Andromeda: a tilted two-arm spiral with a bright bulge
    n = 160_000
    h1 = rng.uniform(0, 1, n)
    arm = rng.integers(0, 2, n)
    r = 0.6 + 70.0 * h1 ** 0.8
    th = arm * np.pi + 1.9 * np.log(r) + rng.normal(0, 1, n) * 0.55 / np.sqrt(r / 8 + 0.4)
    P = np.c_[r * np.cos(th), rng.normal(0, 1, n) * 1.6 * (1 - r / 75), r * np.sin(th)]
    bulge = rng.uniform(0, 1, n) < 0.16
    P[bulge] = rng.normal(size=(bulge.sum(), 3)) * np.r_[7.0, 4.0, 7.0]
    tilt, yaw = 1.05, 0.5
    c, s = np.cos(tilt), np.sin(tilt)
    P = np.c_[P[:, 0], c * P[:, 1] - s * P[:, 2], s * P[:, 1] + c * P[:, 2]]
    c, s = np.cos(yaw), np.sin(yaw)
    P = np.c_[c * P[:, 0] + s * P[:, 2], P[:, 1], -s * P[:, 0] + c * P[:, 2]] + GAL
    alb = rng.uniform(0.4, 1.0, n) * np.where(bulge, 1.4, 1.0)
    pts.append(pack(P, alb, (rng.uniform(0, 1, n) < 0.18) * 0.7, rng.choice([1.0, 2.0], n, p=[0.97, 0.03]),
                    h1, 0.0, rng.uniform(0, 1, n)))
    # the Sun: a dense shell + corona
    d = rng.normal(size=(24_000, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    cor = np.abs(rng.standard_cauchy(8000)).clip(0, 8) * 0.35 + 1.0
    P = np.concatenate([d[:16_000] * 1.0, d[16_000:] * cor[:, None]])
    pts.append(pack(P, np.r_[np.full(16_000, 1.1), 0.6 / cor], 0.2, 1.0, 0.0, 1.0, rng.uniform(0, 1, 24_000)))
    # Earth: a small sphere
    d = rng.normal(size=(3000, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    pts.append(pack(EARTH + d * 0.16, 1.0, 0.5, 1.0, 0.0, 2.0, rng.uniform(0, 1, 3000)))
    # background stars
    n = 26_000
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    P = d * rng.uniform(120, 420, n)[:, None]
    pts.append(pack(P, rng.uniform(0.3, 1.3, n) ** 2, (rng.uniform(0, 1, n) < 0.1) * 0.8,
                    rng.choice([1.0, 1.6, 2.6], n, p=[0.8, 0.16, 0.04]), 0.0, 3.0, rng.uniform(0, 1, n)))
    # shells of incoming light (unit sphere; radius set in the shader)
    n = N_SHELL * 7000
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    ph = np.repeat(np.arange(N_SHELL) / N_SHELL, 7000)
    pts.append(pack(d, rng.uniform(0.4, 1.0, n), (rng.uniform(0, 1, n) < 0.4) * 0.8, 1.0, rng.uniform(0, 1, n),
                    4.0, ph, rng.uniform(0, 1, n)))
    # light paths
    segs = []
    P = np.linspace([1.0, 0, 0], EARTH - [0.16, 0, 0], 240)
    A = attrs(240, 0.5, 0.0, 1.0, 0.0, 5.0)
    A[:, 5] = np.linspace(0, 1, 240)
    segs.append(polyline_segments(P, A))
    P = np.linspace(GAL, EARTH, 900)
    A = attrs(900, 0.5, 0.3, 1.0, 0.0, 6.0)
    A[:, 5] = np.linspace(0, 1, 900)
    segs.append(polyline_segments(P, A))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── the block: the remembered place as a stack of moments along the time axis ──
N_SL = 16


def build_block(rng):
    """Slice k (aux) is a thin plane of space at one moment: ground band, tree, three walkers, the sun.
    b0 = kind (0 ground, 1 tree, 2 person, 3 sun); b1 = rand; b2 = fragment id. Slices sit at z = 0 here; the
    shader places slice k along the time axis. Lines: slice frames (b0 = 5) and the two 'now' planes (b0 = 6, 7)."""
    tp, leafy, _ = tree_points(rng, 9000, 11_000)
    figs = [figure_points(rng, 2600, sc, stride=0.0) for _, sc, _ in FIGS]
    out = []
    for k in range(N_SL):
        # ground band: a terrain profile with strata below
        n = 9000
        x = rng.uniform(-6, 6, n)
        g = 0.35 * np.sin(x * 0.5 + 0.8) + 0.18 * np.sin(x * 1.3 + k * 0.15)
        dep = rng.uniform(0, 1, n) ** 2.2 * 1.3
        P = np.c_[x, g - dep, rng.normal(0, 0.06, n)]
        alb = (1.0 - 0.6 * dep / 1.3) * rng.uniform(0.5, 1.0, n)
        out.append(pack(P, alb, 0.0, 1.0, float(k), 0.0, rng.uniform(0, 1, n), cell_hash(P + [0, 0, k * 7], 0.8)))
        # tree (projected), swaying a little from moment to moment
        sel = rng.choice(len(tp), 4200, replace=False)
        T = tp[sel] * 0.85
        T[:, 0] += 3.3 + 0.05 * np.sin(k * 0.7) * T[:, 1]
        T[:, 1] += 0.35 * np.sin(3.3 * 0.5 + 0.8) + 0.18 * np.sin(3.3 * 1.3 + k * 0.15)
        T[:, 2] *= 0.08
        out.append(pack(T, np.where(leafy[sel] > 0, 0.55, 0.95), leafy[sel] * 0.5, 1.0, float(k), 1.0,
                        rng.uniform(0, 1, len(T)), cell_hash(T + [0, 0, k * 7], 0.8)))
        # three people walking across, one moment per slice
        for j, (x0, v) in enumerate(((-4.6, 0.42), (-3.6, 0.36), (4.4, -0.38))):
            F = figs[j].copy()
            F[:, 2] *= 0.25
            xx = x0 + v * k
            F[:, 0] += xx
            F[:, 1] += 0.35 * np.sin(xx * 0.5 + 0.8) + 0.18 * np.sin(xx * 1.3 + k * 0.15) + 0.03 * abs(np.sin(k * 1.7 + j))
            out.append(pack(F, rng.uniform(0.8, 1.15, len(F)), 0.0, 1.0, float(k), 2.0, rng.uniform(0, 1, len(F)),
                            cell_hash(F + [0, 0, k * 7], 0.5)))
        # the sun sinks a little each moment
        d = rng.normal(size=(900, 2))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        S = np.c_[d * 0.32 * np.sqrt(rng.uniform(0, 1, 900))[:, None], np.zeros(900)] + [-4.2 + 0.12 * k, 3.6 - 0.11 * k, 0]
        out.append(pack(S, 1.2, 0.3, 1.0, float(k), 3.0, rng.uniform(0, 1, 900), 0.5))
    segs = []
    sq = np.array([[-6.3, -1.5, 0], [6.3, -1.5, 0], [6.3, 4.4, 0], [-6.3, 4.4, 0], [-6.3, -1.5, 0]], np.float32)
    for k in range(N_SL):
        P = np.concatenate([np.linspace(sq[i], sq[i + 1], 40) for i in range(4)])
        A = attrs(len(P), 0.7, 0.0, 1.0, float(k), 5.0)
        A[:, 6] = cell_hash(P + [0, 0, k * 7], 0.8)
        segs.append(polyline_segments(P, A))
    big = np.array([[-6.8, -1.9, 0], [6.8, -1.9, 0], [6.8, 4.9, 0], [-6.8, 4.9, 0], [-6.8, -1.9, 0]], np.float32)
    for b0 in (6.0, 7.0):
        P = np.concatenate([np.linspace(big[i], big[i + 1], 60) for i in range(4)])
        segs.append(polyline_segments(P, attrs(len(P), 1.0, 0.0, 1.0, 0.0, b0)))
    return dict(pts=np.concatenate(out), lines=np.concatenate(segs))


# ── global: dust that wraps around the camera (volumetric particles) ────────
def build_camdust(rng):
    n = 9000
    P = rng.uniform(0, 1, (n, 3))
    size = rng.choice([1.0, 2.0, 3.5, 6.0], n, p=[0.55, 0.3, 0.12, 0.03])
    return dict(pts=pack(P, rng.uniform(0.3, 1.0, n), (rng.uniform(0, 1, n) < 0.2) * 0.8, size, 0.0,
                         rng.uniform(0, 1, n)))


BUILDERS = dict(dust=build_dust, title=build_title, question=build_question, scene=build_scene,
                tunnel=build_tunnel, cosmos=build_cosmos, block=build_block, camdust=build_camdust)

DEPS = dict(title=["_text_points"], question=["_text_points"],
            scene=["tree_points", "figure_points", "_capsule", "cell_hash", "ground_h"],
            block=["tree_points", "figure_points", "_capsule", "cell_hash"], tunnel=["cell_hash"])


def load(name):
    import inspect
    src = inspect.getsource(BUILDERS[name]) + "".join(inspect.getsource(globals()[d]) for d in DEPS.get(name, []))
    key = hashlib.sha1((src + name).encode()).hexdigest()[:10]
    path = OUT / f"geo_{name}_{key}.npz"
    if path.exists():
        z = np.load(path)
        return {k: z[k] for k in z.files}
    t0 = time.time()
    rng = np.random.default_rng(sum(map(ord, name)) * 7919)
    d = BUILDERS[name](rng)
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob(f"geo_{name}_*.npz"):
        old.unlink()
    np.savez(path, **d)
    print(f"  {name:9s} " + "  ".join(f"{k} {len(v):,}" for k, v in d.items()) + f"  ({time.time() - t0:.1f}s)",
          flush=True)
    return d


if __name__ == "__main__":
    import sys
    for nm in (sys.argv[1:] or BUILDERS):
        load(nm)
