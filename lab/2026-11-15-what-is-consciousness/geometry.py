"""Procedural point sets for 'What Is Consciousness?'. Taichi bakes the noisy surfaces (cortex, tunnel, memory
islands); numpy builds the rest. Every set is cached as out/geo_<name>_<hash>.npz.

Vertex layout (11 floats): pos(3) | A = (albedo, green, size, aux) | B = (b0, b1, b2, b3).
Lines use the same layout, two vertices per segment. aux/B mean different things per set (see shaders/world.vert).

    uv run python lab/2026-11-15-what-is-consciousness/geometry.py      # build all + stats
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


def bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


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


# ── DARK: a vast sparse field; points awaken one by one, a third gather into stars ──
N_STARS = 70


def build_dust(rng):
    n = 80_000
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    r = 2.5 + 46 * rng.uniform(0, 1, n) ** 1.5
    pos = d * r[:, None]
    pos[:, 1] *= 0.55
    birth = rng.uniform(0, 1, n) ** 0.75
    first = rng.choice(n, 36, replace=False)          # the very first: isolated sparks in front of the camera
    pos[first] = np.c_[rng.uniform(-4, 4, 36), rng.uniform(-2.2, 2.2, 36), -rng.uniform(5, 16, 36)]
    birth[first] = np.sort(rng.uniform(0, 0.05, 36))
    size = rng.choice([1.0, 1.5, 2.3, 3.4], n, p=[0.6, 0.25, 0.11, 0.04])
    size[first] = rng.choice([2.3, 3.4], 36)
    alb = rng.uniform(0.45, 1.2, n)
    alb[first] = 1.4
    grn = (rng.uniform(0, 1, n) < 0.1) * rng.uniform(0.4, 1.0, n)
    # gather targets: star clusters (b1..b3); points that do not gather keep their own position
    sc = rng.normal(size=(N_STARS, 3))
    sc /= np.linalg.norm(sc, axis=1, keepdims=True)
    sc *= (8 + 34 * rng.uniform(0, 1, N_STARS) ** 1.2)[:, None]
    sc[:, 1] *= 0.5
    near = np.argmin(((pos[:, None, :] - sc[None]) ** 2).sum(-1), axis=1)
    g = rng.uniform(0, 1, n) < 0.42
    g[first] = False
    tgt = pos.copy()
    rr = rng.standard_cauchy(size=(n, 1)).clip(-6, 6) * 0.12
    tgt[g] = sc[near[g]] + rng.normal(size=(g.sum(), 3)) * np.abs(rr[g]) * np.r_[1, 0.7, 1]
    return dict(pts=pack(pos, alb, grn, size, birth, rng.uniform(0, 1, n), tgt[:, 0], tgt[:, 1], tgt[:, 2]))


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
    return dict(pts=_text_points(rng, ["WHAT  IS  CONSCIOUSNESS?"], 20_000, 9.0, 0.0))


def build_question(rng):
    return dict(pts=_text_points(rng, ["IS CONSCIOUSNESS SOMETHING THE UNIVERSE CREATED?",
                                       "OR A WAY FOR THE UNIVERSE TO EXPERIENCE ITSELF?"], 9_000, 5.6, 0.62))


# ── MATTER: neurons, dendrites, axons, synapses ─────────────────────────────
N_NEURON = 520


def build_neurons(rng):
    n = N_NEURON
    C = rng.normal(size=(n, 3)) * np.r_[11.0, 5.5, 8.0]
    C[0] = (0, 0, 0)                                     # the close-up neuron sits at the origin
    order = np.argsort(np.linalg.norm(C, axis=1))
    C = C[order]
    rank = np.arange(n) / n                              # near ones first: the network grows outward
    pts, segs = [], []
    for i in range(n):
        c = C[i]
        big = 1.4 if i == 0 else 1.0
        rs = rng.uniform(0.22, 0.4) * big
        m = 3500 if i == 0 else 110
        d = rng.normal(size=(m, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        P = c + d * rs * (0.75 + 0.25 * rng.uniform(0, 1, (m, 1)) ** 0.3)
        pts.append(pack(P, rng.uniform(0.8, 1.3, m), 0.15, 1.0, rank[i], 0.0, 0.0, rng.uniform(), i))
        # dendrites: persistent random walks that branch
        stack = [(c + rng.normal(size=3) * 0.05, rng.normal(size=3), 0.0, 1.0)
                 for _ in range(rng.integers(4, 8) + (3 if i == 0 else 0))]
        while stack:
            p0, v, dist, wgt = stack.pop()
            v = v / np.linalg.norm(v)
            L = int(rng.integers(10, 26) * wgt)
            path = [p0]
            dd = [dist]
            for _ in range(L):
                v = v + rng.normal(size=3) * 0.35
                v /= np.linalg.norm(v)
                path.append(path[-1] + v * 0.13)
                dd.append(dd[-1] + 0.13)
                if rng.uniform() < 0.07 and wgt > 0.45:
                    stack.append((path[-1], v + rng.normal(size=3) * 0.8, dd[-1], wgt * 0.6))
            path = np.array(path)
            dd = np.array(dd) / (3.2 * big)  # growth parameter
            A = attrs(len(path), 0.55 * wgt + 0.2, 0.0, 1.0, rank[i], 3.0, 0, 0, i)
            A[:, 5] = dd
            segs.append(polyline_segments(path, A))
            q = np.repeat(path, 2, 0) + rng.normal(size=(2 * len(path), 3)) * 0.03
            Aq = np.repeat(A, 2, 0)
            pts.append(np.concatenate([q, Aq], 1).astype(np.float32))
    # axons: curved paths to two neighbours each
    D = ((C[:, None] - C[None]) ** 2).sum(-1)
    np.fill_diagonal(D, 1e9)
    for i in range(n):
        nb = np.argsort(D[i])[:9]
        for j in rng.choice(nb, 2, replace=False):
            p0, p3 = C[i], C[j]
            L = np.linalg.norm(p3 - p0)
            p1 = p0 + (p3 - p0) * 0.3 + rng.normal(size=3) * L * 0.3
            p2 = p0 + (p3 - p0) * 0.7 + rng.normal(size=3) * L * 0.3
            k = max(int(L * 7), 16)
            P = bezier(p0, p1, p2, p3, k)
            ph = rng.uniform()
            A = attrs(k, 0.6, 0.0, 1.0, rank[i], 1.0, 0, ph, L)
            A[:, 5] = np.linspace(0, 1, k)
            segs.append(polyline_segments(P, A))
            q = np.repeat(P, 2, 0) + rng.normal(size=(2 * k, 3)) * 0.05
            Aq = np.repeat(A, 2, 0)
            Aq[:, 0] = 0.45
            pts.append(np.concatenate([q, Aq], 1).astype(np.float32))
            m = 26                                        # synapse: a small puff where the axon lands
            P = p3 + (P[-3] - p3) * 0.5 + rng.normal(size=(m, 3)) * 0.12
            pts.append(pack(P, 1.0, 0.8, rng.choice([1.0, 2.0], m, p=[0.8, 0.2]), rank[i], 2.0, 1.0, ph, L))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── BRAIN: folded cortex (Taichi), cerebellum, stem, fibre tracts ───────────
def build_brain(rng):
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm, sstep = _noise_funcs(ti)
    N = 1_000_000
    u = rng.uniform(0, 1, (N, 4)).astype(np.float32)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            z = 2.0 * u[i, 0] - 1.0
            a = 6.283185307 * u[i, 1]
            rr = ti.sqrt(1.0 - z * z)
            d = vec3(rr * ti.cos(a), z, rr * ti.sin(a))
            part = u[i, 3]
            p = vec3(0.0)
            alb, grn, keep, kind = 0.0, 0.0, 1.0, 0.0
            if part < 0.84:                                   # cerebral hemispheres
                side = 1.0 if u[i, 2] < 0.5 else -1.0
                e = vec3(4.6, 4.6, 7.4)
                dd = d
                if dd.x * side < 0.0:
                    e.x = 0.75                                # flat-ish medial wall at the fissure
                if dd.y < 0.0:
                    e.y = 3.2                                 # flatter underside
                # temporal lobe bulge (lower side, front half), frontal lobe roundness
                bump = 0.16 * ti.exp(-((dd.x * side - 0.75) ** 2 + (dd.y + 0.45) ** 2 + (dd.z - 0.15) ** 2) / 0.12)
                R = 1.0 / ti.sqrt((dd.x / e.x) ** 2 + (dd.y / e.y) ** 2 + (dd.z / e.z) ** 2) * (1.0 + bump)
                q = dd * 3.0 + vec3(side * 7.0, 0.0, 0.0)
                g = fbm(q) * 0.7 + fbm(q * 2.3 + 11.0) * 0.3
                # sulci = meandering contour lines of the noise; gyri = the broad ridges between them
                crease = ti.max(ti.exp(-((g - 0.5) / 0.035) ** 2), ti.exp(-((g - 0.4) / 0.03) ** 2))
                crease = ti.max(crease, ti.exp(-((g - 0.6) / 0.03) ** 2))
                ridge = 1.0 - crease
                R *= 1.0 - 0.07 * crease + 0.02 * (g - 0.5)
                p = dd * R
                p.x += side * 0.95
                p.y += 0.6
                alb = 0.95 - 0.8 * crease
                grn = 0.0
                keep = 0.25 + 0.75 * sstep(0.32, 0.6, fbm(q * 0.7 + 40.0))
                if dd.x * side < 0.0:                         # the medial wall: sparse and dim
                    keep *= 0.18
                    alb *= 0.5
                kind = 0.0
            elif part < 0.95:                                 # cerebellum with fine folia
                e = vec3(3.7, 1.6, 2.3)
                R = 1.0 / ti.sqrt((d.x / e.x) ** 2 + (d.y / e.y) ** 2 + (d.z / e.z) ** 2)
                p = d * R
                f = ti.sin(p.y * 13.0 + 2.0 * fbm(p * 1.5))
                p = p * (1.0 + 0.025 * f)
                p += vec3(0.0, -2.4, -5.0)
                alb = 0.25 + 0.3 * (0.5 + 0.5 * f)
                keep = 0.55
                kind = 1.0
            else:                                             # brainstem
                h = u[i, 0]
                ang = 6.283185307 * u[i, 1]
                rad = 1.05 - 0.25 * h
                p = vec3(rad * ti.cos(ang), -1.5 - 4.2 * h, -2.6 - 1.0 * h + rad * ti.sin(ang))
                alb = 0.35
                keep = 0.6
                kind = 2.0
            out[i, 0] = p.x
            out[i, 1] = p.y
            out[i, 2] = p.z
            out[i, 3] = alb
            out[i, 4] = grn
            out[i, 5] = 2.4 if u[i, 2] * 997.0 % 1.0 > 0.996 else 1.0
            out[i, 6] = kind
            out[i, 7] = 1.0 if (u[i, 2] * 131.0 % 1.0) < keep else 0.0

    out = np.zeros((N, 8), np.float32)
    gen(u, out)
    ti.reset()
    out = out[out[:, 7] > 0.5]
    if len(out) > 520_000:
        out = out[rng.choice(len(out), 520_000, replace=False)]
    surf = pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], rng.uniform(0, 1, len(out)), out[:, 6])
    # fibre tracts: arcs through the white matter, many crossing the corpus callosum
    segs, fpts = [], []
    for k in range(240):
        cross = k < 140
        s1 = 1.0 if rng.uniform() < 0.5 else -1.0
        s2 = -s1 if cross else s1
        a = np.array([s1 * rng.uniform(1.0, 3.0), rng.uniform(-1.5, 3.5), rng.uniform(-5.5, 6.0)])
        b = np.array([s2 * rng.uniform(1.0, 3.0), rng.uniform(-1.5, 3.5), rng.uniform(-5.5, 6.0)])
        mid = (a + b) / 2
        mid[1] = rng.uniform(1.2, 2.2) if cross else mid[1] - rng.uniform(0.5, 1.5)
        if cross:
            mid[0] = 0.0
        P = bezier(a, a * 0.6 + mid * 0.4 + rng.normal(size=3) * 0.4, b * 0.6 + mid * 0.4 + rng.normal(size=3) * 0.4,
                   b, 50)
        A = attrs(50, 0.55, 0.35, 1.0, rng.uniform(), 4.0, 0, rng.uniform(), 0)
        A[:, 5] = np.linspace(0, 1, 50)
        segs.append(polyline_segments(P, A))
        fpts.append(np.concatenate([P[::2] + rng.normal(size=(25, 3)) * 0.04, A[::2]], 1).astype(np.float32))
    return dict(pts=np.concatenate([surf] + fpts), lines=np.concatenate(segs))


# ── TUNNEL: perception (Taichi walls), rails, signal streaks ────────────────
def tcx(s):
    return 1.4 * np.sin(0.045 * s) + 0.5 * np.sin(0.15 * s + 1.0)


def tcy(s):
    return 0.7 * np.sin(0.06 * s + 2.0)


def tR(s):
    return 3.0 + 0.5 * np.sin(0.08 * s)


S0, S1 = -12.0, 110.0


def build_tunnel(rng):
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm, sstep = _noise_funcs(ti)
    N = 900_000
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
            r = r0 * (1.0 + 0.45 * (n1 - 0.5) + 0.14 * (n2 - 0.5))
            # organic folds: a fraction of the wall sits on ridged folds (cortex-like)
            rid = 1.0 - ti.abs(2.0 * fbm(vec3(c * 2.4, sn * 2.4, s * 0.16) + 21.0) - 1.0)
            r -= 0.35 * (1.0 - sstep(0.2, 0.5, rid))
            r -= 1.0 * u[i, 3] * u[i, 3] * sstep(0.64, 0.78, n2)
            cx = 1.4 * ti.sin(0.045 * s) + 0.5 * ti.sin(0.15 * s + 1.0)
            cy = 0.7 * ti.sin(0.06 * s + 2.0)
            d = fbm(vec3(c * 2.2, sn * 2.2, s * 0.2) + 31.0)
            keep = sstep(0.30, 0.56, d) * 0.92 + 0.08
            out[i, 0] = cx + r * c
            out[i, 1] = cy + r * sn
            out[i, 2] = -s
            out[i, 3] = 0.25 + 0.5 * n2 + 0.3 * sstep(0.5, 0.9, rid)
            out[i, 4] = sstep(0.62, 0.82, n1) * 0.8
            out[i, 5] = 2.6 if u[i, 2] > 0.996 else 1.0
            out[i, 6] = s
            out[i, 7] = 1.0 if u[i, 2] < keep else 0.0

    out = np.zeros((N, 8), np.float32)
    gen(u, out)
    ti.reset()
    out = out[out[:, 7] > 0.5]
    wall = pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], out[:, 6], 0.0, rng.uniform(0, 1, len(out)))
    del out, u
    # thin rails along the tunnel
    segs = []
    ss = np.arange(S0, S1, 0.6)
    for k in range(12):
        th = TAU * k / 12 + 0.2
        r = tR(ss) * 1.15
        P = np.c_[tcx(ss) + r * np.cos(th), tcy(ss) + r * np.sin(th), -ss]
        A = attrs(len(ss), 0.7, 0.0, 1.0, 0, 1.0)
        A[:, 3] = ss
        segs.append(polyline_segments(P, A))
    # signal streaks (kind 3): two vertices each, b1 = 0 head / 1 tail; aux = start s; b2 = speed; b3 = radius
    m = 2600
    s0 = rng.uniform(S0, S1, m)
    th = rng.uniform(0, TAU, m)
    rr = tR(s0) * np.sqrt(rng.uniform(0.02, 0.7, m))
    sp = rng.uniform(0.6, 1.4, m)
    V = np.zeros((m, 2, 11), np.float32)
    for e in range(2):
        V[:, e, 0] = rr * np.cos(th)
        V[:, e, 1] = rr * np.sin(th)
        V[:, e, 3:7] = np.c_[rng.uniform(0.6, 1.2, m), (rng.uniform(0, 1, m) < 0.35) * 0.9, np.ones(m), s0]
        V[:, e, 7:11] = np.c_[np.full(m, 3.0), np.full(m, float(e)), sp, rr]
    segs.append(V.reshape(-1, 11))
    return dict(pts=wall, lines=np.concatenate(segs))


# ── a face (heightmap mask) — used in the tunnel and in FLUX ───────────────
def face_height(x, y):
    """Mask-like face relief on x∈[-1, 1], y∈[-1.3, 1.3]; returns (z, inside-mask m)."""
    def g(cx, cy, sx, sy):
        return np.exp(-((x - cx) / sx) ** 2 - ((y - cy) / sy) ** 2)

    m = 1 - (x / 0.8) ** 2 - ((y + 0.05 * (y < 0)) / 1.12) ** 2 - 0.25 * (y < -0.4) * ((x / 0.8) ** 2)
    z = 0.5 * np.sqrt(np.clip(m, 0, None))
    nose_w = 0.07 + 0.09 * np.clip((0.25 - y) / 0.6, 0, 1)
    z += 0.3 * np.exp(-(x / nose_w) ** 2) * sst(-0.42, -0.3, y) * (1 - sst(0.18, 0.32, y)) * (0.4 + 0.6 * np.clip((0.3 - y) / 0.6, 0, 1))
    for s in (-1, 1):
        z -= 0.16 * g(s * 0.32, 0.12, 0.17, 0.1)
        z += 0.06 * g(s * 0.32, 0.11, 0.08, 0.05)
        z += 0.06 * g(s * 0.46, -0.12, 0.14, 0.14)
        z -= 0.05 * g(s * 0.42, -0.42, 0.12, 0.16)
    z += 0.08 * np.exp(-((y - 0.3) / 0.07) ** 2) * np.exp(-(x / 0.55) ** 2)
    z += 0.07 * np.exp(-(x / 0.2) ** 2) * (np.exp(-((y + 0.54) / 0.04) ** 2) + np.exp(-((y + 0.66) / 0.045) ** 2))
    z -= 0.05 * g(0, -0.6, 0.18, 0.012)
    z += 0.08 * g(0, -0.95, 0.24, 0.12)
    return z, m


def face_points(rng, n):
    x = rng.uniform(-1, 1, n * 3)
    y = rng.uniform(-1.3, 1.3, n * 3)
    z, m = face_height(x, y)
    inside = m > 0
    x, y = x[inside], y[inside]
    k = rng.choice(len(x), n, replace=len(x) < n)
    x, y = x[k], y[k]
    z, m = face_height(x, y)
    e = 0.004
    nx = -(face_height(x + e, y)[0] - face_height(x - e, y)[0]) / (2 * e)
    ny = -(face_height(x, y + e)[0] - face_height(x, y - e)[0]) / (2 * e)
    N = np.c_[nx, ny, np.ones_like(x)]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    L = np.array([-0.55, 0.45, 0.7])
    L /= np.linalg.norm(L)
    lam = np.clip(N @ L, 0, 1) ** 1.5
    alb = (0.08 + 1.0 * lam) * sst(0.0, 0.12, m)
    pos = np.c_[x, y, z] * 3.2
    return pos, alb


def build_face(rng):
    pos, alb = face_points(rng, 70_000)
    pos = pos + rng.normal(size=pos.shape) * 0.01
    return dict(pts=pack(pos, alb, 0.0, rng.choice([1.0, 1.8], len(pos), p=[0.9, 0.1]), rng.uniform(0, 1, len(pos))))


# ── MEMORY: floating fragments of landscape (Taichi), thought rings ─────────
N_ISLAND = 24


def island_layout(rng):
    zs = np.linspace(4, -78, N_ISLAND) + rng.uniform(-2, 2, N_ISLAND)
    side = np.where(np.arange(N_ISLAND) % 2 == 0, 1, -1)
    xs = side * rng.uniform(3.5, 11, N_ISLAND)
    ys = rng.uniform(-2.5, 2.5, N_ISLAND)
    rad = rng.uniform(2.2, 4.2, N_ISLAND)
    return np.c_[xs, ys, zs], rad


def build_islands(rng):
    ti = _ti()
    vec3 = ti.math.vec3
    h3, vnoise, fbm, sstep = _noise_funcs(ti)
    C, R = island_layout(rng)
    per = 15_000
    N = N_ISLAND * per
    u = rng.uniform(0, 1, (N, 4)).astype(np.float32)
    Cf = C.astype(np.float32)
    Rf = R.astype(np.float32)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), C: ti.types.ndarray(dtype=ti.f32, ndim=2),
            R: ti.types.ndarray(dtype=ti.f32, ndim=1), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            k = i // per
            rad = R[k]
            a = 6.283185307 * u[i, 0]
            r = ti.sqrt(u[i, 1])
            x, z = r * ti.cos(a), r * ti.sin(a)
            edge = 0.75 + 0.35 * fbm(vec3(ti.cos(a) * 2.0, ti.sin(a) * 2.0, float(k) * 3.1))   # ragged outline
            top = u[i, 2] < 0.72
            px, py, pz = x * rad, 0.0, z * rad
            alb, grn, kind = 0.0, 0.0, 0.0
            keep = 1.0 if r < edge else 0.0
            if top:
                h = 1.6 * (fbm(vec3(px * 0.35 + float(k) * 7.0, pz * 0.35, 2.0)) - 0.45)
                h += 0.35 * (fbm(vec3(px * 1.2, pz * 1.2, float(k))) - 0.5)
                py = h * rad * 0.35
                alb = 0.4 + 0.7 * ti.math.clamp(h + 0.4, 0.0, 1.0)
                grn = 0.6 * sstep(0.55, 0.75, fbm(vec3(px * 0.8, pz * 0.8, 9.0 + float(k))))
                kind = 0.0
            else:                                         # underside: rock hanging down, tapering
                depth = (1.0 - r / edge) * rad * (0.9 + 0.5 * fbm(vec3(px * 0.6, pz * 0.6, float(k) + 4.0)))
                py = -depth * u[i, 3] ** 0.5 - 0.1
                alb = 0.18 + 0.2 * u[i, 3]
                kind = 1.0
            out[i, 0] = C[k, 0] + px
            out[i, 1] = C[k, 1] + py
            out[i, 2] = C[k, 2] + pz
            out[i, 3] = alb
            out[i, 4] = grn
            out[i, 5] = 2.3 if u[i, 3] > 0.995 else 1.0
            out[i, 6] = float(k)
            out[i, 7] = kind
            out[i, 8] = keep

    out = np.zeros((N, 9), np.float32)
    gen(u, Cf, Rf, out)
    ti.reset()
    out = out[out[:, 8] > 0.5]
    pts = [pack(out[:, :3], out[:, 3], out[:, 4], out[:, 5], out[:, 6], out[:, 7], C[out[:, 6].astype(int), 1])]
    # photographs (kind 2): a flat rectangular frame under each fragment
    segs = []
    for k in range(N_ISLAND):
        w = R[k] * 1.15
        sq = np.array([[-w, 0, -w * 0.75], [w, 0, -w * 0.75], [w, 0, w * 0.75], [-w, 0, w * 0.75], [-w, 0, -w * 0.75]])
        P = np.concatenate([np.linspace(sq[i], sq[i + 1], 24) for i in range(4)]) + C[k]
        A = attrs(len(P), 0.9, 0.0, 1.0, k, 2.0, 0, C[k, 1])
        segs.append(polyline_segments(P, A))
        pts.append(np.concatenate([P + rng.normal(size=P.shape) * 0.01, A], 1).astype(np.float32))
    # thought rings (kind 3): stacks of rings above some fragments; b1 = ring phase, b2 = ring radius
    for k in range(0, N_ISLAND, 2):
        for j in range(6):
            m = 260
            a = np.linspace(0, TAU, m, endpoint=False)
            rr = R[k] * rng.uniform(0.25, 0.55)
            P = np.c_[C[k, 0] + rr * np.cos(a), np.full(m, C[k, 1] + 0.8), C[k, 2] + rr * np.sin(a)]
            pts.append(pack(P, 1.0, 0.7, 1.2, k, 3.0, j / 6 + rng.uniform(0, 0.05), C[k, 1]))
    # a sparse fragmented ground far below
    m = 90_000
    gx = rng.uniform(-60, 60, m)
    gz = rng.uniform(-110, 30, m)
    gy = -11 + 1.5 * np.sin(gx * 0.11) * np.cos(gz * 0.09) + rng.normal(0, 0.1, m)
    keep = (np.sin(gx * 0.3 + np.sin(gz * 0.21) * 2) * np.cos(gz * 0.27) > -0.1)
    pts.append(pack(np.c_[gx, gy, gz][keep], rng.uniform(0.15, 0.4, keep.sum()), 0.0, 1.0, -1.0, 4.0))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── GAP: the map (a lattice) with an empty chamber at its heart ─────────────
LAT_N, LAT_S, VOID_R = 21, 2.0, 7.5


def build_lattice(rng):
    g = (np.arange(LAT_N) - (LAT_N - 1) / 2) * LAT_S
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    nodes = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    rn = np.linalg.norm(nodes, axis=1)
    nodes = nodes[rn > VOID_R]
    pts = [pack(nodes, rng.uniform(0.7, 1.2, len(nodes)), 0.0, 2.0, rng.uniform(0, 1, len(nodes)), 0.0,
                np.round(nodes[:, 1] / LAT_S), np.linalg.norm(nodes, axis=1))]
    segs = []
    for ax in range(3):
        e = np.zeros(3)
        e[ax] = LAT_S
        a = nodes
        b = nodes + e
        ok = (np.abs(b) <= g[-1] + 1e-6).all(1) & (np.linalg.norm(b, axis=1) > VOID_R)
        a, b = a[ok], b[ok]
        for f in (0.2, 0.4, 0.6, 0.8):                   # dotted edges (point-cloud look)
            P = a * (1 - f) + b * f + rng.normal(size=a.shape) * 0.02
            pts.append(pack(P, rng.uniform(0.25, 0.5, len(P)), 0.0, 1.0, rng.uniform(0, 1, len(P)), 1.0,
                            np.round(P[:, 1] / LAT_S), np.linalg.norm(P, axis=1)))
        sel = rng.uniform(0, 1, len(a)) < 0.16           # some edges as thin lines
        for i in np.nonzero(sel)[0]:
            V = np.stack([a[i], b[i]])
            A = attrs(2, 0.5, 0.0, 1.0, 0, 1.0, round(a[i, 1] / LAT_S), np.linalg.norm(a[i]))
            segs.append(polyline_segments(V, A))
    # traced pathways (kind 2): random lattice walks avoiding the chamber; b1 = along, b2 = order, b3 = layer
    lim = g[-1]
    for k in range(70):
        while True:
            p = rng.choice(g, 3)
            if np.linalg.norm(p) > VOID_R + 2:
                break
        path = [p.copy()]
        for _ in range(45):
            for _try in range(12):
                d = np.zeros(3)
                d[rng.integers(3)] = rng.choice([-1, 1]) * LAT_S
                q = path[-1] + d
                if (np.abs(q) <= lim).all() and np.linalg.norm(q) > VOID_R:
                    path.append(q)
                    break
        P = np.array(path)
        n = len(P)
        A = attrs(n, 1.0, 0.6, 1.0, rng.uniform(), 2.0, 0, k / 70, 0)
        A[:, 5] = np.linspace(0, 1, n)
        A[:, 7] = np.round(P[:, 1] / LAT_S)
        segs.append(polyline_segments(P, A))
    # the inner light (kind 3): a faint cloud inside the chamber, lit only on 'experience'
    m = 5000
    d = rng.normal(size=(m, 3))
    P = d * (rng.uniform(0, 1, (m, 1)) ** 2) * 1.3
    pts.append(pack(P, rng.uniform(0.5, 1.2, m), 1.0, rng.choice([1.0, 2.5], m, p=[0.9, 0.1]), rng.uniform(0, 1, m),
                    3.0, 0, 0))
    return dict(pts=np.concatenate(pts), lines=np.concatenate(segs))


# ── FLUX: one cloud that becomes many shapes. pos = brain, b0..2 = face ────
def build_flux(rng):
    n = 180_000
    br = load("brain")["pts"]
    br = br[br[:, 7] < 0.5]                               # cortex only
    B = br[rng.choice(len(br), n, replace=len(br) < n), :3] * 0.62
    F, falb = face_points(rng, n)
    F = F * 1.0 + rng.normal(size=F.shape) * 0.01
    alb = rng.uniform(0.6, 1.0, n) * (0.15 + 0.85 * falb)
    return dict(pts=pack(B, alb, (rng.uniform(0, 1, n) < 0.1) * 0.8, rng.choice([1.0, 2.2], n, p=[0.985, 0.015]),
                         rng.uniform(0, 1, n), F[:, 0], F[:, 1], F[:, 2], rng.uniform(0, 1, n)))


# ── global: dust that wraps around the camera (volumetric particles) ────────
def build_camdust(rng):
    n = 9000
    P = rng.uniform(0, 1, (n, 3))
    size = rng.choice([1.0, 2.0, 3.5, 6.0], n, p=[0.55, 0.3, 0.12, 0.03])
    return dict(pts=pack(P, rng.uniform(0.3, 1.0, n), (rng.uniform(0, 1, n) < 0.2) * 0.8, size, 0.0,
                         rng.uniform(0, 1, n)))


BUILDERS = dict(dust=build_dust, title=build_title, question=build_question, neurons=build_neurons,
                brain=build_brain, tunnel=build_tunnel, face=build_face, islands=build_islands,
                lattice=build_lattice, flux=build_flux, camdust=build_camdust)


DEPS = dict(face=["face_points", "face_height"], flux=["face_points", "face_height", "build_brain"], dust=[], title=["_text_points"],
            question=["_text_points"])


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
