"""Procedural point sets for 'What Is Time?'. Taichi bakes the noisy surfaces (tunnel, landscape stack); numpy
builds the rest. Every set is cached as out/geo_<name>_<hash>.npz.

Vertex layout (11 floats): pos(3) | A = (albedo, green, size, aux) | B = (b0, b1, b2, b3).
Lines are the same layout, two vertices per segment. The meaning of aux/B depends on the set's mode
(see shaders/world.vert).

    uv run python lab/2026-11-15-what-is-time/geometry.py      # build all + stats
"""
import hashlib
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TAU = 2 * np.pi


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


# ── tunnel centerline (twin in render.py) ───────────────────────────────────
def tcx(s):
    return 1.2 * np.sin(0.05 * s) + 0.4 * np.sin(0.17 * s + 1.0)


def tcy(s):
    return 0.6 * np.sin(0.07 * s + 2.0)


def tR(s):
    return 2.7 + 0.4 * np.sin(0.09 * s)


S0, S1 = -40.0, 125.0


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

    return h3, vnoise, fbm


# ── 1. dark: sparse particle field that appears one by one ───────────────────
def build_dust(rng):
    n = 70_000
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    r = 2.5 + 42 * rng.uniform(0, 1, n) ** 1.6
    pos = d * r[:, None]
    pos[:, 1] *= 0.55                                   # flattened: reads as a vast dark space, not a ball
    birth = rng.uniform(0, 1, n) ** 0.7                 # few early, many late
    # the very first points: a handful close in front of the camera, so the first seconds have isolated stars
    first = rng.choice(n, 40, replace=False)
    pos[first] = np.c_[rng.uniform(-4, 4, 40), rng.uniform(-2.2, 2.2, 40), -rng.uniform(5, 16, 40)]
    birth[first] = np.sort(rng.uniform(0, 0.06, 40))
    size = rng.choice([1.0, 1.5, 2.3, 3.4], n, p=[0.6, 0.25, 0.11, 0.04])
    size[first] = rng.choice([2.3, 3.4], 40)
    alb = rng.uniform(0.45, 1.2, n)
    alb[first] = 1.4
    grn = (rng.uniform(0, 1, n) < 0.12) * rng.uniform(0.4, 1.0, n)
    return dict(pts=pack(pos, alb, grn, size, birth, rng.uniform(0, 1, n), np.linalg.norm(pos, axis=1)))


# ── 1b. title made of particles ──────────────────────────────────────────────
def build_title(rng, text="WHAT  IS  TIME?"):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(Path.home() / ".local/share/fonts/inter/InterVariable.ttf"), 200)
    try:
        font.set_variation_by_axes([300])                 # light weight
    except Exception:
        pass
    W, H = 2600, 300
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    # letter-spaced: draw glyph by glyph
    x = 0
    xs = []
    for ch in text:
        xs.append(x)
        x += dr.textlength(ch, font=font) + 34
    tw = x - 34
    x0 = (W - tw) / 2
    for ch, xx in zip(text, xs):
        dr.text((x0 + xx, 40), ch, fill=255, font=font)
    m = np.asarray(im, np.float32) / 255
    ys, xs_ = np.nonzero(m > 0.5)
    n = 42_000
    k = rng.choice(len(xs_), n)
    px = (xs_[k] + rng.uniform(-0.5, 0.5, n) - W / 2) / W
    py = -(ys[k] + rng.uniform(-0.5, 0.5, n) - (40 + 105)) / W
    width = 7.6
    pos = np.c_[px * width, py * width, -8.0 + rng.normal(0, 0.035, n)]
    alb = rng.uniform(0.55, 1.0, n)
    size = rng.choice([1.0, 1.6], n, p=[0.85, 0.15])
    return dict(pts=pack(pos, alb, 0.0, size, rng.uniform(0, 1, n)))


# ── 2. road: the tunnel of time ──────────────────────────────────────────────
def build_tunnel(rng):
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm = _noise_funcs(ti)
    N = 900_000
    u = rng.uniform(0, 1, (N, 4)).astype(np.float32)

    @ti.func
    def sstep(e0, e1, x):
        t = ti.math.clamp((x - e0) / (e1 - e0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            s = S0 + (S1 - S0) * u[i, 0]
            th = 6.283185307 * u[i, 1]
            c, sn = ti.cos(th), ti.sin(th)
            n1 = fbm(vec3(c * 1.3, sn * 1.3, s * 0.10))
            n2 = fbm(vec3(c * 4.1, sn * 4.1, s * 0.42) + 5.0)
            r0 = 2.7 + 0.4 * ti.sin(0.09 * s)
            r = r0 * (1.0 + 0.42 * (n1 - 0.5) + 0.12 * (n2 - 0.5))
            # strata: a fraction of points sits on crisp terraced shells (geometric fragments)
            terr = sstep(0.55, 0.62, fbm(vec3(c * 2.0, sn * 2.0, s * 0.07) + 21.0))
            r = ti.math.mix(r, r0 * 1.08 + ti.floor((r - r0) * 3.0) / 3.0, terr * 0.8)
            # inward depth for a few clumps
            r -= 0.9 * u[i, 3] * u[i, 3] * sstep(0.62, 0.75, n2)
            cx = 1.2 * ti.sin(0.05 * s) + 0.4 * ti.sin(0.17 * s + 1.0)
            cy = 0.6 * ti.sin(0.07 * s + 2.0)
            d = fbm(vec3(c * 2.2, sn * 2.2, s * 0.2) + 31.0)
            keep = sstep(0.30, 0.55, d) * 0.92 + 0.08
            out[i, 0] = cx + r * c
            out[i, 1] = cy + r * sn
            out[i, 2] = -s
            out[i, 3] = 0.3 + 0.45 * n2 + 0.25 * terr      # albedo
            out[i, 4] = sstep(0.6, 0.8, n1) * 0.8         # green
            out[i, 5] = 2.6 if u[i, 2] > 0.996 else 1.0   # size (sparkles)
            out[i, 6] = s
            out[i, 7] = 0.0                               # kind 0 = wall
            out[i, 8] = 1.0 if u[i, 2] < keep else 0.0

    out = np.zeros((N, 9), np.float32)
    gen(u, out)
    ti.reset()
    out = out[out[:, 8] > 0.5]
    wall = pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], out[:, 6], out[:, 7])
    del out, u

    # time rings: a clean circle of points every 1.5 s-units; every 4th is a major tick
    rings = []
    for j, s in enumerate(np.arange(S0, S1, 1.5)):
        major = j % 4 == 0
        m = 520 if major else 300
        th = np.sort(rng.uniform(0, TAU, m))
        r = tR(s) * (1.12 if major else 1.1)
        p = np.c_[tcx(s) + r * np.cos(th), tcy(s) + r * np.sin(th), np.full(m, -s)]
        rings.append(pack(p, 0.9 if major else 0.55, 0.0, 1.0, s, 2.0 if major else 1.0))
    rings = np.concatenate(rings)

    # thin perspective lines along the tunnel (8 rails at fixed angles)
    segs = []
    ss = np.arange(S0, S1, 0.6)
    for k in range(10):
        th = TAU * k / 10 + 0.3
        r = tR(ss) * 1.16
        P = np.c_[tcx(ss) + r * np.cos(th), tcy(ss) + r * np.sin(th), -ss]
        A = np.zeros((len(ss), 8), np.float32)
        A[:, 0], A[:, 2], A[:, 3], A[:, 4] = 0.8, 1.0, ss, 3.0
        segs.append(polyline_segments(P, A))
    return dict(pts=np.concatenate([wall, rings]), lines=np.concatenate(segs))


# ── 3. fabric: stacked space-grids woven with time threads ──────────────────
def build_fabric(rng):
    L = 7
    ext, step = 34.0, 2.0
    g = np.arange(-ext, ext + 1e-6, step)
    pts, segs = [], []
    t = np.linspace(-ext, ext, 140)
    for k in range(L):
        y = (k - (L - 1) / 2) * 2.4
        for c in g:
            for P in (np.c_[t, np.full_like(t, y), np.full_like(t, c)], np.c_[np.full_like(t, c), np.full_like(t, y), t]):
                A = np.zeros((len(t), 8), np.float32)
                A[:, 0], A[:, 2], A[:, 3], A[:, 4] = 0.55, 1.0, k, 0.0
                segs.append(polyline_segments(P[::2], A[::2]))
                pts.append(pack(P + rng.normal(0, 0.02, P.shape), rng.uniform(0.5, 0.9, len(P)), 0.0, 1.0, k, 0.0))
        # loose dust inside each slice
        m = 6000
        P = np.c_[rng.uniform(-ext, ext, m), y + rng.normal(0, 0.25, m), rng.uniform(-ext, ext, m)]
        pts.append(pack(P, rng.uniform(0.2, 0.6, m), 0.0, 1.0, k, 2.0))
    # time threads: wavy worldlines rising through every slice
    nT = 260
    yy = np.linspace(-9.5, 9.5, 120)
    for i in range(nT):
        x0, z0 = rng.uniform(-ext * 0.8, ext * 0.8, 2)
        ph = rng.uniform(0, TAU, 2)
        a = rng.uniform(0.3, 1.3)
        P = np.c_[x0 + a * np.sin(0.35 * yy + ph[0]), yy, z0 + a * np.sin(0.29 * yy + ph[1])]
        uu = (yy - yy[0]) / (yy[-1] - yy[0])
        A = np.zeros((len(yy), 8), np.float32)
        A[:, 0], A[:, 1], A[:, 2], A[:, 3], A[:, 4], A[:, 5] = 0.9, rng.uniform(0, 1) < 0.3, 1.0, -1, 1.0, uu
        segs.append(polyline_segments(P, A))
        pts.append(pack(P[::3], 1.0, A[::3, 1], 1.6, -1, 1.0, uu[::3]))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── 4. bend: one big space-grid sheet, clocks, an orbit ─────────────────────
N_CLOCK = 12


def build_well(rng):
    ext = 42.0
    g = np.arange(-ext, ext + 1e-6, 1.5)
    t = np.linspace(-ext, ext, 280)
    pts, segs = [], []
    for c in g:
        for P in (np.c_[t, np.zeros_like(t), np.full_like(t, c)], np.c_[np.full_like(t, c), np.zeros_like(t), t]):
            A = np.zeros((len(t), 8), np.float32)
            A[:, 0], A[:, 2] = 0.7, 1.0
            segs.append(polyline_segments(P[::2], A[::2]))
            pts.append(pack(P, rng.uniform(0.5, 1.0, len(P)), 0.0, 1.0, 0.0, 0.0))
    m = 160_000
    r = ext * np.sqrt(rng.uniform(0, 1, m))
    a = rng.uniform(0, TAU, m)
    P = np.c_[r * np.cos(a), rng.normal(0, 0.04, m), r * np.sin(a)]
    pts.append(pack(P, rng.uniform(0.15, 0.55, m), (rng.uniform(0, 1, m) < 0.1) * 0.8,
                    rng.choice([1.0, 2.2], m, p=[0.993, 0.007]), 0.0, 1.0))
    # clocks: ring of points + a hand (positions resolved in the shader from u_clk[id])
    for cid in range(N_CLOCK):
        nr = 220
        ang = np.linspace(0, TAU, nr, endpoint=False)
        pts.append(pack(np.zeros((nr, 3)), 0.9, 0.0, 1.3, cid, 2.0, ang))
        tick = np.linspace(0, TAU, 12, endpoint=False)
        pts.append(pack(np.zeros((12, 3)), 1.0, 0.0, 2.2, cid, 2.0, tick, 1.0))          # hour ticks
        nh = 40
        pts.append(pack(np.zeros((nh, 3)), 1.0, 0.6, 1.4, cid, 3.0, np.linspace(0.0, 0.85, nh)))
    # orbit ring (kind 4): angle in b1
    nr = 1400
    ang = np.linspace(0, TAU, nr, endpoint=False)
    pts.append(pack(np.zeros((nr, 3)), 0.8, 0.3, 1.0, 0.0, 4.0, ang))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── 5. block: a stack of landscapes, one per moment ─────────────────────────
N_SLAB = 18


def build_block(rng):
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm = _noise_funcs(ti)
    per = 26_000
    N = N_SLAB * per
    u = rng.uniform(0, 1, (N, 3)).astype(np.float32)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            k = float(i // per)
            x = (u[i, 0] - 0.5) * 16.0
            z = (u[i, 1] - 0.5) * 16.0
            # the landscape drifts and a dune travels across as k advances (moment to moment)
            h = 1.4 * (fbm(vec3(x * 0.16 + k * 0.05, z * 0.16, 1.0)) - 0.5)
            h += 0.35 * (fbm(vec3(x * 0.6, z * 0.6 + k * 0.12, 7.0)) - 0.5)
            dune = x - (-6.0 + k * 0.75)
            h += 0.55 * ti.exp(-dune * dune / 1.6) * (0.6 + 0.4 * ti.sin(z * 0.4))
            out[i, 0] = x
            out[i, 1] = h * 0.55
            out[i, 2] = z
            out[i, 3] = 0.35 + 0.6 * ti.math.clamp(h + 0.5, 0.0, 1.0)
            out[i, 4] = 0.25 * ti.exp(-dune * dune / 1.6)
            out[i, 5] = 2.4 if u[i, 2] > 0.997 else 1.0
            out[i, 6] = k

    out = np.zeros((N, 7), np.float32)
    gen(u, out)
    ti.reset()
    pts = pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], out[:, 6], 0.0, out[:, 1])
    # thin frame around every slab (kind 1)
    segs = []
    sq = np.array([[-8, 0, -8], [8, 0, -8], [8, 0, 8], [-8, 0, 8], [-8, 0, -8]], np.float32)
    for k in range(N_SLAB):
        P = np.concatenate([np.linspace(sq[i], sq[i + 1], 30) for i in range(4)])
        A = np.zeros((len(P), 8), np.float32)
        A[:, 0], A[:, 2], A[:, 3], A[:, 4] = 0.8, 1.0, k, 1.0
        segs.append(polyline_segments(P, A))
    return dict(pts=pts, lines=np.concatenate(segs))


# ── 6. arrow: an ordered crystal that diffuses into disorder ────────────────
def build_crystal(rng):
    pts = []
    for j, r in enumerate(np.linspace(1.0, 4.2, 8)):
        n = int(5200 * r * r / 4)
        i = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * i / n)
        th = np.pi * (1 + 5 ** 0.5) * i + j
        P = np.c_[np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)] * r
        pts.append(pack(P, 0.45 + 0.07 * j, 0.0, 1.0, j, 0.0, rng.uniform(0, 1, n)))
    # latitude and meridian rings on the outer shell: crisp order
    R = 4.5
    for lat in np.linspace(-1.35, 1.35, 13):
        n = 700
        a = np.linspace(0, TAU, n, endpoint=False)
        P = np.c_[R * np.cos(lat) * np.cos(a), np.full(n, R * np.sin(lat)), R * np.cos(lat) * np.sin(a)]
        pts.append(pack(P, 1.0, 0.3, 1.0, 8, 1.0, rng.uniform(0, 1, n)))
    for lon in np.linspace(0, np.pi, 8, endpoint=False):
        n = 700
        a = np.linspace(0, TAU, n, endpoint=False)
        P = np.c_[R * np.cos(a) * np.cos(lon), R * np.sin(a), R * np.cos(a) * np.sin(lon)]
        pts.append(pack(P, 1.0, 0.3, 1.0, 8, 1.0, rng.uniform(0, 1, n)))
    # stars: bright sparkles scattered through the volume (burn out one by one)
    n = 900
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    P = d * rng.uniform(0.5, 4.4, n)[:, None]
    pts.append(pack(P, 2.2, 0.5, 2.8, 9, 2.0, rng.uniform(0, 1, n)))
    return dict(pts=np.concatenate(pts))


# ── global: dust that wraps around the camera (volumetric particles) ────────
def build_camdust(rng):
    n = 9000
    P = rng.uniform(0, 1, (n, 3))
    size = rng.choice([1.0, 2.0, 3.5, 6.0], n, p=[0.55, 0.3, 0.12, 0.03])
    return dict(pts=pack(P, rng.uniform(0.3, 1.0, n), (rng.uniform(0, 1, n) < 0.2) * 0.8, size, 0.0,
                         rng.uniform(0, 1, n)))


BUILDERS = dict(dust=build_dust, title=build_title, tunnel=build_tunnel, fabric=build_fabric, well=build_well,
                block=build_block, crystal=build_crystal, camdust=build_camdust)


def load(name):
    src = (HERE / "geometry.py").read_bytes()
    key = hashlib.sha1(src + name.encode()).hexdigest()[:10]
    path = OUT / f"geo_{name}_{key}.npz"
    if path.exists():
        z = np.load(path)
        return {k: z[k] for k in z.files}
    t0 = time.time()
    rng = np.random.default_rng(abs(hash(name)) % 1 if False else sum(map(ord, name)) * 7919)
    d = BUILDERS[name](rng)
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob(f"geo_{name}_*.npz"):
        old.unlink()
    np.savez(path, **d)
    print(f"  {name:8s} " + "  ".join(f"{k} {len(v):,}" for k, v in d.items()) + f"  ({time.time() - t0:.1f}s)")
    return d


if __name__ == "__main__":
    for nm in BUILDERS:
        load(nm)
