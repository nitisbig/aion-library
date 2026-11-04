"""Seeded procedural night forest → one big point cloud.

Every point carries: position, area it represents (m², for energy-conserving additive rendering), normal,
wind weight (0 at roots → 1 at leaf tips), colour variation, material id, height above ground, world radius.

Trees are grown with space colonization (Runions et al. 2007) into templates, then instanced with random
rotation/scale. Branch radii follow the pipe model r_parent^2.5 = Σ r_child^2.5.

    uv run python lab/2026-11-04-point-cloud-forest/forest.py      # build + stats
"""

from __future__ import annotations

import time

import numpy as np
from scipy.spatial import cKDTree

SEED = 7
MATS = ["GROUND", "LITTER", "PATH", "BARK", "TWIG", "LEAF", "NEEDLE", "FERN", "GRASS", "MOSS", "ROCK", "LOG",
        "FUNGI", "FLOWER", "WATER", "MIST", "FIREFLY", "GBARK", "GLEAF"]
M = {k: i for i, k in enumerate(MATS)}

# ── world layout (metres, y up; the walk goes toward −z) ────────────────────
X0, X1, Z0, Z1 = -62.0, 62.0, -118.0, 26.0
CLEAR_C = np.array([0.0, -60.0])
CLEAR_R = 14.0
GIANT = np.array([2.0, -71.0])
YW = -0.35                                  # water surface height
PATH_Z = (-50.0, 26.0)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


_r = np.random.default_rng(11)
_OCT = []
for amp, wl in [(1.3, 70), (0.7, 32), (0.32, 15), (0.12, 6), (0.05, 2.4), (0.025, 1.0)]:
    for _ in range(2):
        th, ph = _r.uniform(0, 2 * np.pi, 2)
        k = 2 * np.pi / wl
        _OCT.append((amp, k * np.cos(th), k * np.sin(th), ph))


def _base(x, z, fine_only=False):
    h = 0.0
    for i, (a, kx, kz, ph) in enumerate(_OCT):
        if fine_only and i < 6:
            continue
        h = h + a * np.sin(kx * x + kz * z + ph)
    return h


def stream_z(x):
    return -60.0 + 2.5 * np.sin(x / 9.0 + 0.5)


def stream_hw(x):
    return 2.0 + 0.4 * np.sin(x / 5.0)


def path_x(z):
    return (2.8 * np.sin(0.085 * z + 0.3) + 1.2 * np.sin(0.19 * z + 2.0)) * smooth(-50, -32, z)


def terrain(x, z):
    x, z = np.asarray(x, float), np.asarray(z, float)
    h = _base(x, z) + 0.035 * np.minimum(np.abs(z + 60), 50)
    d = np.hypot(x - CLEAR_C[0], z - CLEAR_C[1])
    wc = smooth(CLEAR_R + 12, CLEAR_R - 3, d)
    h = h * (1 - wc) + (0.25 + _base(x, z, True)) * wc
    h = np.maximum(h, YW + 0.3)
    dz = np.abs(z - stream_z(x))
    hw = stream_hw(x)
    k = smooth(hw + 1.8, hw - 0.3, dz)
    return h * (1 - k) + (YW - 0.35) * k


def path_dist(x, z):
    d = np.abs(x - path_x(z))
    return np.where((z > PATH_Z[0]) & (z < PATH_Z[1]), d, 1e3)


def route_dist(x, z):
    """Distance to where the camera goes (path, clearing, giant tree). Drives LOD and ground density."""
    dc = np.hypot(x - CLEAR_C[0], z - CLEAR_C[1]) - CLEAR_R
    return np.maximum(np.minimum(path_dist(x, z), dc), 0)


def _unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def _basis(d):
    helper = np.where(np.abs(d[:, 1:2]) < 0.9, [[0, 1, 0]], [[1, 0, 0]])
    u = _unit(np.cross(d, helper))
    return u, np.cross(d, u)


class Cloud:
    """Accumulates point blocks."""

    def __init__(self):
        self.blocks = []

    def add(self, pos, mat, area, normal=None, wind=0.0, var=None, hag=None, rad=0.0, rng=None):
        n = len(pos)
        if n == 0:
            return
        b = dict(pos=np.asarray(pos, "f4"), area=np.broadcast_to(np.asarray(area, "f4"), (n,)).copy(),
                 normal=np.zeros((n, 3), "f4") + ([0, 1, 0] if normal is None else normal),
                 wind=np.broadcast_to(np.asarray(wind, "f4"), (n,)).copy(),
                 var=(rng.random(n) if var is None else np.broadcast_to(var, (n,))).astype("f4"),
                 mat=np.broadcast_to(np.asarray(mat, "f4"), (n,)).copy(),
                 hag=(np.zeros(n) if hag is None else np.broadcast_to(hag, (n,))).astype("f4"),
                 rad=np.broadcast_to(np.asarray(rad, "f4"), (n,)).copy())
        self.blocks.append(b)

    def merge(self):
        return {k: np.concatenate([b[k] for b in self.blocks]) for k in self.blocks[0]}


# ── sampling primitives ──────────────────────────────────────────────────────
def sample_cyl(rng, A, B, rA, rB, density, ridges=True):
    """Points on the surfaces of truncated cones A→B. Returns pos, normal, t (along), seg index."""
    L = np.linalg.norm(B - A, axis=1)
    keep = L > 1e-6
    A, B, rA, rB, L = A[keep], B[keep], rA[keep], rB[keep], L[keep]
    n = rng.poisson(np.pi * (rA + rB) * L * density)
    seg = np.repeat(np.arange(len(A)), n)
    m = len(seg)
    t = rng.random(m)
    th = rng.random(m) * 2 * np.pi
    d = (B - A) / L[:, None]
    u, v = _basis(d)
    nrm = np.cos(th)[:, None] * u[seg] + np.sin(th)[:, None] * v[seg]
    r = rA[seg] + (rB[seg] - rA[seg]) * t
    p = A[seg] + d[seg] * (L[seg] * t)[:, None]
    if ridges:   # vertical bark furrows
        r = r * (1 + 0.07 * np.sin(13 * th + 2.5 * np.sin(1.7 * p[:, 1])))
    return p + r[:, None] * nrm, nrm, seg


def colonize(rng, attr, D, di, dk, max_iter=260):
    nodes, par = [np.zeros(3)], [-1]
    kda = cKDTree(attr)
    while kda.query(nodes[-1])[0] > di and len(nodes) < 400:   # trunk until the crown is in reach
        w = rng.normal(0, 0.06, 3)
        nodes.append(nodes[-1] + D * _unit(np.array([w[0], 1.0, w[2]])))
        par.append(len(nodes) - 2)
    N, P = np.array(nodes), list(par)
    alive = np.ones(len(attr), bool)
    for _ in range(max_iter):
        ia = np.nonzero(alive)[0]
        if len(ia) == 0:
            break
        kd = cKDTree(N)
        d, ni = kd.query(attr[ia], distance_upper_bound=di)
        ok = np.isfinite(d)
        if not ok.any():
            break
        ni = ni[ok]
        v = _unit(attr[ia[ok]] - N[ni])
        acc = np.zeros_like(N)
        np.add.at(acc, ni, v)
        g = np.unique(ni)
        dirs = _unit(_unit(acc[g]) + [0, 0.1, 0] + rng.normal(0, 0.07, (len(g), 3)))
        new = N[g] + D * dirs
        dd, _ = kd.query(new)
        fresh = dd > 0.3 * D
        if not fresh.any():
            break
        new, g = new[fresh], g[fresh]
        N = np.vstack([N, new])
        P += list(g)
        dk_, _ = cKDTree(new).query(attr[ia], distance_upper_bound=dk)
        alive[ia[np.isfinite(dk_)]] = False
    return N, np.array(P)


def pipe_radii(P, r_base):
    n = len(P)
    has_child = np.zeros(n, bool)
    has_child[P[1:]] = True
    acc = np.where(has_child, 0.0, 1.0)
    for i in range(n - 1, 0, -1):
        acc[P[i]] += acc[i]
    r = acc ** (1 / 2.5)
    r *= r_base / r[0]
    return np.maximum(r, 0.012), ~has_child


# ── tree templates (relative coords, base at origin) ─────────────────────────
def broadleaf(rng, H, giant=False):
    crown_bot = H * rng.uniform(0.32, 0.45) if not giant else H * 0.27
    cr = H * rng.uniform(0.27, 0.36) if not giant else 14.0
    ry = (H - crown_bot) / 2
    n_attr = int((2600 if giant else 520) * rng.uniform(0.85, 1.15))
    v = _unit(rng.normal(size=(n_attr, 3)))
    rr = rng.random(n_attr) ** (1 / 3)
    A = v * rr[:, None] * [cr, ry, cr] + [0, crown_bot + ry, 0]
    A[:, 1] -= 0.25 * ry * (A[:, 0] ** 2 + A[:, 2] ** 2) / cr ** 2       # droopy dome
    s = H / 16
    D, di, dk = (0.55, 5.5, 1.3) if giant else (0.33 * s, 3.4 * s, 0.75 * s)
    N, P = colonize(rng, A, D, di, dk)
    r, tip = pipe_radii(P, (1.35 if giant else rng.uniform(0.18, 0.3) * s))
    r = r * (1 + (1.2 if giant else 0.5) * np.exp(-N[:, 1] / (1.6 if giant else 0.5)))     # root flare
    i = np.arange(1, len(N))
    pos, nrm, seg = sample_cyl(rng, N[P[i]], N[i], r[P[i]], r[i], 70.0 if giant else 55.0)
    ri = r[i][seg]
    wood = dict(pos=pos, normal=nrm,
                wind=np.clip((pos[:, 1] / H) ** 2 * 0.3 + 0.7 * (ri < 0.06) * pos[:, 1] / H, 0, 1),
                mat=np.where(ri < 0.06, M["TWIG"], M["GBARK" if giant else "BARK"]),
                area=1 / (70.0 if giant else 55.0))
    # leaves around tips and the thin twigs
    L = N[tip | (r < 0.04)]
    k = rng.poisson(90 if giant else 19, len(L))
    cl = np.repeat(L, k, axis=0)
    lp = cl + rng.normal(0, 1, (len(cl), 3)) * ([0.5, 0.32, 0.5] if giant else [0.38, 0.25, 0.38])
    ln = _unit(rng.normal(0, 1, (len(cl), 3)) + [0, 1.6, 0])
    leaves = dict(pos=lp, normal=ln, wind=np.clip(0.55 + 0.45 * lp[:, 1] / H, 0, 1),
                  mat=np.full(len(lp), M["GLEAF" if giant else "LEAF"]), area=0.03)
    return [wood, leaves]


def conifer(rng, H):
    rb = rng.uniform(0.16, 0.26) * H / 16
    ys = np.arange(0, H, 0.3)
    wig = np.cumsum(rng.normal(0, 0.012, (len(ys), 2)), 0)
    T = np.c_[wig[:, 0], ys, wig[:, 1]]
    rt = rb * (1 - ys / H) ** 1.1 + 0.012
    rt = rt * (1 + 0.6 * np.exp(-ys / 0.4))
    pos, nrm, _ = sample_cyl(rng, T[:-1], T[1:], rt[:-1], rt[1:], 60.0)
    wood = [dict(pos=pos, normal=nrm, wind=(pos[:, 1] / H) ** 2 * 0.25, mat=np.full(len(pos), M["BARK"]), area=1 / 60)]
    nd_p, nd_w = [], []
    y = H * rng.uniform(0.15, 0.28)
    while y < H - 0.25:
        kb = rng.integers(5, 8)
        a0 = rng.uniform(0, 2 * np.pi)
        for j in range(kb):
            az = a0 + 2 * np.pi * j / kb + rng.normal(0, 0.2)
            Lb = (H - y) * 0.36 * rng.uniform(0.8, 1.1) + 0.25
            n = int(Lb * 26)
            s = rng.random(n)
            dirv = np.array([np.cos(az), 0, np.sin(az)])
            c = s[:, None] * Lb * dirv + np.c_[0 * s, y - 0.28 * Lb * s ** 2 + 0.12 * Lb * s, 0 * s]
            spread = 0.04 + 0.12 * (1 - s)
            nd_p.append(c + rng.normal(0, 1, (n, 3)) * spread[:, None] * [1, 0.5, 1])
            nd_w.append(0.35 + 0.65 * s)
        y += rng.uniform(0.38, 0.55)
    p = np.concatenate(nd_p)
    needles = dict(pos=p, normal=_unit(rng.normal(0, 1, (len(p), 3)) + [0, 1.2, 0]), wind=np.concatenate(nd_w),
                   mat=np.full(len(p), M["NEEDLE"]), area=0.035)
    return wood + [needles]


# ── ground cover ─────────────────────────────────────────────────────────────
def fern(rng, n_fronds, size):
    out = []
    for j in range(n_fronds):
        az = 2 * np.pi * j / n_fronds + rng.normal(0, 0.25)
        L = size * rng.uniform(0.7, 1.1)
        elev = rng.uniform(0.7, 1.1)
        d = np.array([np.cos(az), 0, np.sin(az)])
        side = np.array([-np.sin(az), 0, np.cos(az)])
        n = int(L * 160)
        s = rng.random(n)
        spine = s[:, None] * L * d * 0.85 + np.c_[0 * s, L * (elev * np.sin(np.pi * s * 0.75) * 0.55 - 0.15 * s), 0 * s]
        pin = (1 - s) ** 0.8 * 0.22 * L * rng.choice([-1, 1], n) * rng.random(n) ** 0.7
        p = spine + pin[:, None] * side - (np.abs(pin) * 0.4)[:, None] * [0, 1, 0]
        out.append(np.c_[p, 0.3 + 0.7 * s])
    return np.concatenate(out)


def build(verbose=True):
    rng = np.random.default_rng(SEED)
    C = Cloud()
    t0 = time.time()

    # trees: jittered grid, kept off the path / clearing / stream
    sp = 6.2
    gx, gz = np.meshgrid(np.arange(X0 + 2, X1 - 2, sp), np.arange(Z0 + 2, Z1 - 2, sp))
    tx = gx.ravel() + rng.uniform(-0.45, 0.45, gx.size) * sp
    tz = gz.ravel() + rng.uniform(-0.45, 0.45, gz.size) * sp
    ok = path_dist(tx, tz) > 2.6
    ok &= np.hypot(tx - CLEAR_C[0], tz - CLEAR_C[1]) > CLEAR_R - 1.5
    ok &= np.abs(tz - stream_z(tx)) > stream_hw(tx) + 1.6
    ok &= np.hypot(tx - GIANT[0], tz - GIANT[1]) > 9
    ok &= np.hypot(tx - path_x(4.0), tz - 4.0) > 4.5            # keep the opening shot's floor clear
    tx, tz = tx[ok], tz[ok]
    nT = len(tx)
    temps_b = [broadleaf(rng, rng.uniform(13, 21)) for _ in range(14)]
    temps_c = [conifer(rng, rng.uniform(12, 20)) for _ in range(8)]
    if verbose:
        print(f"templates {time.time() - t0:.1f}s")
    kind = rng.random(nT) < 0.28
    for i in range(nT):
        tmpl = temps_c[rng.integers(len(temps_c))] if kind[i] else temps_b[rng.integers(len(temps_b))]
        a = rng.uniform(0, 2 * np.pi)
        sc = rng.uniform(0.82, 1.18)
        R = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
        rd = route_dist(tx[i], tz[i])
        keep = float(np.clip(1.15 - rd / 35, 0.35, 1.0))       # LOD for trees far from the route
        base = np.array([tx[i], terrain(tx[i], tz[i]) - 0.1, tz[i]])
        for part in tmpl:
            m = rng.random(len(part["pos"])) < keep
            p = (part["pos"][m] * sc) @ R.T
            C.add(p + base, part["mat"][m], part["area"] * sc * sc / keep, part["normal"][m] @ R.T,
                  part["wind"][m], hag=p[:, 1], rng=rng)

    # giant tree on the far bank, with buttress roots
    g = broadleaf(np.random.default_rng(99), 34.0, giant=True)
    gb = np.array([GIANT[0], terrain(*GIANT) - 0.2, GIANT[1]])
    for part in g:
        C.add(part["pos"] + gb, part["mat"], part["area"], part["normal"], part["wind"], hag=part["pos"][:, 1], rng=rng)
    for j in range(9):
        az = 2 * np.pi * j / 9 + rng.normal(0, 0.15)
        d = np.array([np.cos(az), 0, np.sin(az)])
        s = np.linspace(0, 1, 14)
        pts = gb + (0.8 + 5.5 * s)[:, None] * d + np.c_[0 * s, 1.6 * (1 - s) ** 2 - 0.25, 0 * s]
        pts[:, 1] = np.maximum(pts[:, 1], terrain(pts[:, 0], pts[:, 2]) - 0.15 + 0.6 * (1 - s) ** 2)
        rr = 0.55 * (1 - s) ** 1.3 + 0.06
        p, nrm, _ = sample_cyl(rng, pts[:-1], pts[1:], rr[:-1], rr[1:], 80.0)
        C.add(p, M["GBARK"], 1 / 80, nrm, 0.0, hag=p[:, 1] - gb[1], rng=rng)

    # ground: denser near the route, very dense on the opening shot's patch
    area = (X1 - X0) * (Z1 - Z0)
    n = int(area * 260)
    gx = rng.uniform(X0, X1, n)
    gz = rng.uniform(Z0, Z1, n)
    dens = 40 + 220 * smooth(16, 2, route_dist(gx, gz))
    keepg = rng.random(n) < dens / 260
    gx, gz, dens = gx[keepg], gz[keepg], dens[keepg]
    # the opening shot's floor patch gets an extra dense layer
    extra = int(14 * 14 * 900)                 # square, then cut to the r = 7 disc → 900/m²
    ex = rng.uniform(-7, 7, (extra, 2))
    ex = ex[np.hypot(*ex.T) < 7]
    gx = np.r_[gx, ex[:, 0] + path_x(4.0)]
    gz = np.r_[gz, ex[:, 1] + 3.0]
    dens = np.r_[dens, np.full(len(ex), 260.0)]
    dens = np.where(np.hypot(gx - path_x(4.0), gz - 3.0) < 7, dens + 900.0, dens)   # both layers share the area
    gy = terrain(gx, gz) + rng.normal(0, 0.012, len(gx))
    e = 0.05
    nx = terrain(gx - e, gz) - terrain(gx + e, gz)
    nz = terrain(gx, gz - e) - terrain(gx, gz + e)
    gn = _unit(np.c_[nx, np.full(len(gx), 2 * e), nz])
    pd = path_dist(gx, gz)
    sd = np.abs(gz - stream_z(gx)) - stream_hw(gx)
    mat = np.where(rng.random(len(gx)) < 0.35, M["LITTER"], M["GROUND"])
    mat = np.where(pd < 0.85 + 0.15 * np.sin(gz * 1.3), M["PATH"], mat)
    mat = np.where((sd < 0.6) & (sd > -0.1) & (rng.random(len(gx)) < 0.5), M["MOSS"], mat)
    under = sd < -0.1                                          # stream bed under the water: sparse
    keepb = ~under | (rng.random(len(gx)) < 0.25)
    gy = np.where(mat == M["LITTER"], gy + rng.random(len(gx)) * 0.04, gy)
    C.add(np.c_[gx, gy, gz][keepb], mat[keepb], (1 / dens)[keepb], gn[keepb], 0.0, hag=0.0, rng=rng)

    # ferns and grass near the path and clearing edge
    def scatter(nn, rmin, rmax, zone_w):
        out = []
        while len(out) < nn:
            x = rng.uniform(X0 + 3, X1 - 3, 4000)
            z = rng.uniform(-52, Z1 - 3, 4000)
            rd = route_dist(x, z)
            w = smooth(rmax + zone_w, rmax, rd) * smooth(rmin - 0.3, rmin, rd)
            w *= np.abs(z - stream_z(x)) > stream_hw(x) + 0.4
            m = rng.random(4000) < w * 0.6
            out += list(zip(x[m], z[m]))
        return np.array(out[:nn])

    for (x, z) in scatter(520, 1.15, 7.0, 8.0):
        f = fern(rng, rng.integers(6, 10), rng.uniform(0.5, 1.05))
        a = rng.uniform(0, 2 * np.pi)
        R = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
        p = f[:, :3] @ R.T
        C.add(p + [x, terrain(x, z), z], M["FERN"], 0.004, _unit(rng.normal(0, 1, (len(p), 3)) + [0, 2, 0]),
              f[:, 3], hag=p[:, 1], rng=rng)
    gpos = scatter(1800, 0.9, 5.0, 10.0)
    for (x, z) in gpos:
        nb = rng.integers(6, 12)
        hgt = rng.uniform(0.15, 0.45, nb)
        az = rng.uniform(0, 2 * np.pi, nb)
        lean = rng.uniform(0.1, 0.5, nb)
        s = np.tile(np.linspace(0, 1, 10), nb)
        b = np.repeat(np.arange(nb), 10)
        p = np.c_[np.cos(az[b]) * lean[b] * hgt[b] * s ** 2, hgt[b] * s, np.sin(az[b]) * lean[b] * hgt[b] * s ** 2]
        p += rng.normal(0, 0.01, (len(p), 3))
        C.add(p + [x, terrain(x, z), z], M["GRASS"], 0.003, [0, 1, 0], s, hag=p[:, 1], rng=rng)

    # rocks (a few as stepping stones in the stream) and fallen logs
    rocks = [(x, z, rng.uniform(0.25, 1.1)) for x, z in zip(rng.uniform(X0, X1, 70), rng.uniform(Z0, Z1, 70))
             if path_dist(x, z) > 1.5]
    for xs in (-2.4, -0.6, 1.3, 3.0):
        rocks.append((xs, float(stream_z(xs)) + rng.normal(0, 0.3), rng.uniform(0.3, 0.45)))
    for x, z, rr in rocks:
        nn = int(4 * np.pi * rr * rr * 260)
        v = _unit(rng.normal(size=(nn, 3)))
        bump = 1 + 0.18 * np.sin(5 * v[:, 0] + 3 * v[:, 2]) * np.cos(4 * v[:, 1] + 2 * v[:, 0])
        p = v * bump[:, None] * rr * [1.2, 0.65, 1.0]
        keep = p[:, 1] > -0.25 * rr
        C.add(p[keep] + [x, terrain(x, z), z], np.where(v[keep, 1] > 0.55, M["MOSS"], M["ROCK"]), 1 / 260,
              v[keep], 0.0, hag=p[keep, 1], rng=rng)
    for _ in range(14):
        while True:
            x, z = rng.uniform(X0 + 6, X1 - 6), rng.uniform(-50, Z1 - 6)
            if 2.2 < path_dist(x, z) < 22:
                break
        a = rng.uniform(0, 2 * np.pi)
        L = rng.uniform(4, 8)
        r = rng.uniform(0.22, 0.4)
        d = np.array([np.cos(a), 0, np.sin(a)])
        s = np.linspace(-0.5, 0.5, 10)
        pts = np.array([x, 0, z]) + s[:, None] * L * d
        pts[:, 1] = terrain(pts[:, 0], pts[:, 2]) + r * 0.8
        p, nrm, _ = sample_cyl(rng, pts[:-1], pts[1:], np.full(9, r), np.full(9, r * 0.9), 220.0)
        C.add(p, np.where(nrm[:, 1] > 0.6, M["MOSS"], M["LOG"]), 1 / 220, nrm, 0.0,
              hag=p[:, 1] - terrain(p[:, 0], p[:, 2]), rng=rng)
        for _ in range(rng.integers(2, 5)):        # bracket fungi on the log
            c = pts[rng.integers(1, 9)] + rng.normal(0, 0.15, 3)
            q = c + np.c_[rng.normal(0, 0.06, 40), rng.normal(0, 0.012, 40), rng.normal(0, 0.06, 40)]
            C.add(q, M["FUNGI"], 0.0015, [0, 1, 0], 0.0, hag=0.3, rng=rng)

    # fungi at tree bases near the route, flowers along the path
    near = np.nonzero(route_dist(tx, tz) < 12)[0]
    for i in rng.choice(near, min(90, len(near)), replace=False):
        a = rng.uniform(0, 2 * np.pi)
        c = np.array([tx[i] + 0.45 * np.cos(a), terrain(tx[i], tz[i]) + 0.05, tz[i] + 0.45 * np.sin(a)])
        for _ in range(rng.integers(3, 8)):
            o = c + [rng.normal(0, 0.15), 0, rng.normal(0, 0.15)]
            hh = rng.uniform(0.04, 0.12)
            st = np.c_[np.zeros(6), np.linspace(0, hh, 6), np.zeros(6)]
            th = rng.uniform(0, 2 * np.pi, 22)
            cap = np.c_[np.cos(th) * 0.035 * rng.random(22) ** 0.5, hh + 0.01 * rng.random(22),
                        np.sin(th) * 0.035 * rng.random(22) ** 0.5]
            C.add(np.r_[st, cap] + o, M["FUNGI"], 0.0012, [0, 1, 0], 0.0, hag=hh, rng=rng)
    for (x, z) in scatter(420, 0.9, 3.0, 4.0):
        th = rng.uniform(0, 2 * np.pi, 10)
        hgt = rng.uniform(0.12, 0.3)
        q = np.c_[np.cos(th) * 0.025, hgt + rng.normal(0, 0.008, 10), np.sin(th) * 0.025]
        C.add(q + [x, terrain(x, z), z], M["FLOWER"], 0.0015, [0, 1, 0], 0.8, hag=hgt, rng=rng)

    # water (stored as x0 / lateral offset, positioned in the shader), mist, fireflies
    nw = int(140 * 4.4 * 140)
    C.add(np.c_[rng.uniform(-70, 70, nw), np.zeros(nw), rng.uniform(-1, 1, nw)], M["WATER"], 1 / 140, [0, 1, 0],
          0.0, hag=0.0, rng=rng)
    nm = 30000
    mx = np.r_[rng.normal(0, 13, nm // 2), path_x(np.linspace(-45, 20, nm // 2)) + rng.normal(0, 5, nm // 2)]
    mz = np.r_[rng.normal(-60, 7, nm // 2), np.linspace(-45, 20, nm // 2) + rng.normal(0, 2, nm // 2)]
    my = terrain(mx, mz) + rng.uniform(0.1, 1.4, nm) ** 1.5
    C.add(np.c_[mx, my, mz], M["MIST"], 0.06, [0, 1, 0], 0.0, hag=0.0, rad=0.45, rng=rng)
    nf = 420
    fz = rng.uniform(-80, 14, nf)
    fx = np.where(fz > -48, path_x(fz) + rng.normal(0, 7, nf), rng.normal(0, 16, nf))
    fy = terrain(fx, fz) + rng.uniform(0.4, 3.2, nf)
    C.add(np.c_[fx, fy, fz], M["FIREFLY"], 0.004, [0, 1, 0], 0.0, hag=1.0, rad=0.06, rng=rng)

    P = C.merge()
    P["meta"] = dict(trees=nT, giant=GIANT, n=len(P["pos"]))
    if verbose:
        counts = np.bincount(P["mat"].astype(int), minlength=len(MATS))
        print(f"{nT} trees, {len(P['pos']):,} points ({time.time() - t0:.1f}s)")
        for k, c in zip(MATS, counts):
            print(f"  {k:8s} {c:>10,}")
    return P


if __name__ == "__main__":
    build()
