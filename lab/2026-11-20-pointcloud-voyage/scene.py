"""Point cloud for Dido's voyage: sea, sky dome, clouds, sun, coast ridges, a hilltop city and the galley.

Every point row is 13 floats: pos(3) nrm(3) col(3, linear) attr(4) = (kind, area m², p1, p2).
Kinds: 0 sea (y from the wave field in the shader), 1 lit static (land, city), 2 emissive (p2: 0 sky, 1 star,
2 sun, 3 cloud), 3 ship (p1: 0 rigid, 1 sail, 2 oar, 3 flag), 4 city window (p1 = turn-on time 0..1),
5 foam (nrm = side, hull x, jitter; p1 = age phase), 6 gull (nrm = span u, id, 0).
Ship points are in the galley's local frame (x toward the bow, y up, z to starboard, waterline y = 0).
Everything is seeded, so the cloud is identical on every run.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = HERE / "out" / "cloud.npy"

# ── shared world constants (keep in sync with shaders/common.glsl and render.py) ──
SUN_DIR = np.array([0.22, 0.095, -1.0]) / np.linalg.norm([0.22, 0.095, -1.0])
WD = np.array([[0.92, -0.38], [0.6, 0.8], [-0.3, 0.95], [0.99, 0.1], [-0.7, 0.7]])
WD = WD / np.linalg.norm(WD, axis=1, keepdims=True)
WL = np.array([34.0, 19.0, 10.5, 5.6, 2.9])
WA = np.array([0.32, 0.2, 0.1, 0.05, 0.025])
WP = np.array([0.0, 1.7, 4.1, 2.3, 5.5])


def lin(hx, k=1.0):
    h = hx.lstrip("#")
    return np.array([((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4)])


PAL = dict(
    sea=lin("#0f5a78"), sea2=lin("#1f9aa6"), foam=lin("#d8f1ff"),
    zenith=lin("#1b1446"), mid=lin("#5a2a74"), rose=lin("#e0527a"), horizon=lin("#ff8a5c"), gold=lin("#ffc86b"),
    sun=lin("#fff1c9"), ember=lin("#ff8f45"), star=lin("#dfe8ff"),
    far=lin("#7a4a8c"), midl=lin("#553a7c"), near=lin("#3a2f68"), stone=lin("#d9b48a"), window=lin("#ffd27a"),
    hull=lin("#b8743a"), plank=lin("#f0b46a"), deck=lin("#7a4a2a"), tyrian=lin("#c2185b"), cream=lin("#f4e6cf"),
    emblem=lin("#ffc24a"), shield_a=lin("#f2b544"), shield_b=lin("#a0205e"), oar=lin("#eadcc0"), rope=lin("#c9a27a"),
    dido=lin("#c2185b"), cloak=lin("#ff7aa2"),
)


def wave_h(x, z, t):
    h = 0.0
    for d, L, A, P in zip(WD, WL, WA, WP):
        k = 2 * np.pi / L
        w = np.sqrt(9.81 * k) * 0.8
        h = h + A * np.sin(k * (d[0] * x + d[1] * z) - w * t + P)
    return h


def rows(pos, nrm, col, kind, area, p1=0.0, p2=0.0):
    n = len(pos)
    out = np.zeros((n, 13), np.float32)
    out[:, 0:3] = pos
    out[:, 3:6] = nrm
    out[:, 6:9] = col
    out[:, 9] = kind
    out[:, 10] = area
    out[:, 11] = p1
    out[:, 12] = p2
    return out


D = 2.0          # density: point counts scale by D, areas by 1/D, so brightness is unchanged


def surf(F, n, r, **kw):
    """n random samples of the parametric surface F(u, v) on [0,1]², with normals and the area each point covers."""
    u, v = r.uniform(0, 1, n), r.uniform(0, 1, n)
    e = 1e-3
    P = F(u, v, **kw)
    Fu = (F(np.clip(u + e, 0, 1), v, **kw) - F(np.clip(u - e, 0, 1), v, **kw)) / (np.clip(u + e, 0, 1) - np.clip(u - e, 0, 1))[:, None]
    Fv = (F(u, np.clip(v + e, 0, 1), **kw) - F(u, np.clip(v - e, 0, 1), **kw)) / (np.clip(v + e, 0, 1) - np.clip(v - e, 0, 1))[:, None]
    N = np.cross(Fu, Fv)
    a = np.linalg.norm(N, axis=1)
    return P, N / (a[:, None] + 1e-9), a / n, u, v


def noise1(x, seed):
    r = np.random.default_rng(seed)
    out = np.zeros_like(x, dtype=float)
    for o in range(5):
        f = 0.004 * 2.1**o
        out += (0.55**o) * np.sin(f * x * r.uniform(0.8, 1.2) + r.uniform(0, 6.28))
    return out / 1.9


# ── the world ──
def sea(r):
    out = []
    # a dense band along the voyage, a sparse field everywhere else
    n1 = int(230_000 * D * 1.5)
    x, z = r.uniform(-45, 45, n1), r.uniform(-130, 45, n1)
    out.append((x, z, 90 * 175 / n1))
    n2 = int(160_000 * D)
    x, z = r.uniform(-320, 320, n2), r.uniform(-300, 70, n2)
    keep = ~((np.abs(x) < 45) & (z > -130) & (z < 45))
    out.append((x[keep], z[keep], 640 * 370 / n2))
    res = []
    for x, z, a in out:
        pos = np.column_stack([x, np.zeros_like(x), z])
        mix_ = r.uniform(0, 1, len(x))[:, None]
        col = PAL["sea"] * (1 - mix_) + PAL["sea2"] * mix_
        res.append(rows(pos, np.tile([0, 1, 0], (len(x), 1)), col, 0, a))
    return np.concatenate(res)


def sky(r):
    res = []
    n = int(380_000 * D * 1.6)
    az = r.uniform(-np.pi, np.pi, n)
    el = np.arcsin(r.uniform(0, 1, n) ** 2.2 * 0.85)          # denser toward the horizon
    R = 620.0
    d = np.column_stack([np.cos(el) * np.sin(az), np.sin(el), -np.cos(el) * np.cos(az)])
    pos = d * R + [0, -6, -60]
    sunw = np.clip(d @ SUN_DIR, 0, 1) ** 16
    e = np.clip(el / 0.5, 0, 1)[:, None]
    base = PAL["horizon"] * (1 - e) ** 3 + PAL["rose"] * 3 * e * (1 - e) ** 2 + PAL["mid"] * 3 * e**2 * (1 - e) + PAL["zenith"] * e**3
    col = (base + PAL["gold"] * sunw[:, None] * 1.2) * 0.32
    res.append(rows(pos, -d, col, 2, 2 * np.pi * R * R * 0.85 / n * 0.9, r.uniform(0, 6.28, n), 0))
    # stars
    n = 2600
    az, el = r.uniform(-np.pi, np.pi, n), np.arcsin(r.uniform(0.12, 1, n))
    d = np.column_stack([np.cos(el) * np.sin(az), np.sin(el), -np.cos(el) * np.cos(az)])
    res.append(rows(d * 600 + [0, 0, -60], -d, PAL["star"] * r.uniform(0.3, 1.0, (n, 1)), 2, 6.0, r.uniform(0, 6.28, n), 1))
    # the sun: a dense disc and a soft halo
    c = SUN_DIR * 560 + [0, 0, -60]
    a_ = np.cross(SUN_DIR, [0, 1, 0])
    a_ /= np.linalg.norm(a_)
    b_ = np.cross(a_, SUN_DIR)
    n = 16_000
    rr = 24 * np.sqrt(r.uniform(0, 1, n))
    th = r.uniform(0, 2 * np.pi, n)
    pos = c + (rr * np.cos(th))[:, None] * a_ + (rr * np.sin(th))[:, None] * b_
    k = (rr / 24)[:, None]
    res.append(rows(pos, np.tile(-SUN_DIR, (n, 1)), PAL["sun"] * (1 - k) + PAL["gold"] * k, 2, np.pi * 24**2 / n * 1.5, 0, 2))
    n = 9000
    rr = np.abs(r.normal(0, 55, n)) + 22
    th = r.uniform(0, 2 * np.pi, n)
    pos = c + (rr * np.cos(th))[:, None] * a_ + (rr * np.sin(th))[:, None] * b_ + SUN_DIR * 5
    res.append(rows(pos, np.tile(-SUN_DIR, (n, 1)), PAL["ember"] * np.exp(-(rr - 22) / 50)[:, None] * 0.9, 2, 3.0, 0, 2))
    # cloud banks: flattened clumps, lit gold underneath
    for i in range(12):
        az0 = r.uniform(-1.1, 1.1)
        el0 = r.uniform(0.03, 0.2)
        d0 = np.array([np.cos(el0) * np.sin(az0), np.sin(el0), -np.cos(el0) * np.cos(az0)])
        c0 = d0 * r.uniform(420, 560) + [0, 0, -60]
        n = 6000
        L = r.uniform(60, 170)
        blobs = r.normal(0, 1, (7, 3)) * [L * 0.45, 4, 8]
        idx = r.integers(0, 7, n)
        p = blobs[idx] + r.normal(0, 1, (n, 3)) * [L * 0.18, 3.0, 6.0]
        ylow = (p[:, 1] < blobs[idx, 1]).astype(float)[:, None]
        near_sun = np.clip(d0 @ SUN_DIR, 0, 1) ** 3
        col = PAL["mid"] * 0.5 * (1 - ylow) + (PAL["horizon"] * 0.7 + PAL["gold"] * near_sun) * ylow
        res.append(rows(c0 + p, np.tile(-d0, (n, 1)), col * 0.55, 2, 1.6, 0, 3))
    return np.concatenate(res)


def land(r):
    res = []
    layers = [(-500, 500, -430, -400, 46, PAL["far"], int(70_000 * D), 3), (-420, -10, -345, -315, 40, PAL["midl"], int(60_000 * D), 7),
              (-320, -40, -292, -268, 22, PAL["near"], int(60_000 * D), 12)]
    for x0, x1, zf, zb, H, col, n, seed in layers:
        def F(u, v):
            x = x0 + (x1 - x0) * u
            z = zb + (zf - zb) * v
            env = np.clip((x - x0) / 60, 0, 1) * np.clip((x1 - x) / 140, 0, 1) ** 0.7
            h = H * env * (0.7 + 0.3 * noise1(x, seed)) * (1 - v**2.2)
            return np.column_stack([x, h, z])
        P, N, a, u, v = surf(F, n, r)
        N[N[:, 2] < 0] *= -1
        res.append(rows(P, N, col * r.uniform(0.75, 1.1, (n, 1)), 1, a))
    # the hilltop city on the near ridge, and its windows
    rr = np.random.default_rng(31)
    for i in range(14):
        x = -230 + i * 9.5 + rr.uniform(-2, 2)
        w, d, h = rr.uniform(5, 9), rr.uniform(5, 9), rr.uniform(6, 20)
        z = -276 + rr.uniform(-3, 3)
        base = 22 * 0.8 * np.clip((x + 320) / 60, 0, 1) * np.clip((-40 - x) / 140, 0, 1) ** 0.7 * 0.92
        for F, nrm in ((lambda u, v: np.column_stack([x + w * u, base + h * v, np.full_like(u, z + d / 2)]), [0, 0, 1]),
                       (lambda u, v: np.column_stack([np.full_like(u, x + w), base + h * v, z - d / 2 + d * u]), [1, 0, 0]),
                       (lambda u, v: np.column_stack([x + w * u, np.full_like(u, base + h), z - d / 2 + d * v]), [0, 1, 0])):
            P, N, a, u, v = surf(F, 2400, rr)
            res.append(rows(P, np.tile(nrm, (len(P), 1)), PAL["stone"] * 0.6, 1, a))
        nw = int(h * w / 6)
        u, v = rr.uniform(0.1, 0.9, nw), rr.uniform(0.15, 0.85, nw)
        P = np.column_stack([x + w * u, base + h * v, np.full(nw, z + d / 2 + 0.2)])
        P = np.repeat(P, 20, axis=0) + rr.normal(0, 0.18, (nw * 20, 3)) * [1, 1, 0]
        res.append(rows(P, np.tile([0, 0, 1], (len(P), 1)), PAL["window"], 4, 0.05, np.repeat(rr.uniform(0, 0.8, nw), 20), 0))
    return np.concatenate(res)


# ── the galley ──
def sheer(u):
    return 1.25 + 1.3 * (2 * u - 1) ** 4


def halfw(u):
    return 1.9 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.7


def ship(r):
    res = []

    def hull(u, v, side=1):
        x = -8 + 16 * u
        d = 0.9 * np.sin(np.pi * u) ** 0.5
        y = -d + (sheer(u) + d) * v
        z = side * halfw(u) * np.sin(np.pi / 2 * np.clip(v * 1.7, 0, 1))
        return np.column_stack([x, y, z])
    for side in (-1, 1):
        P, N, a, u, v = surf(hull, int(45_000 * D), r, side=side)
        N *= np.sign(N[:, 2:3] * side + 1e-9)
        plank = (np.abs(((v * 7) % 1) - 0.5) > 0.42)[:, None]
        col = PAL["hull"] * (0.55 + 0.45 * v[:, None]) * (1 - plank) + PAL["plank"] * plank
        res.append(rows(P, N, col, 3, a, 0))
        # the gunwale shields
        for i in range(13):
            uu = 0.12 + i * 0.063
            c = np.array([-8 + 16 * uu, sheer(uu) + 0.2, side * (halfw(uu) + 0.06)])
            m = 700
            rr_ = 0.38 * np.sqrt(r.uniform(0, 1, m))
            th = r.uniform(0, 2 * np.pi, m)
            P = c + np.column_stack([rr_ * np.cos(th), rr_ * np.sin(th), np.zeros(m)])
            ring = (rr_ > 0.3)[:, None]
            col = (PAL["shield_a"] if i % 2 else PAL["shield_b"]) * (1 - ring) + PAL["shield_a"] * ring
            res.append(rows(P, np.tile([0, 0, side], (m, 1)), col, 3, np.pi * 0.38**2 / m, 0))
    # deck
    def deck(u, v):
        uu = 0.06 + 0.88 * u
        return np.column_stack([-8 + 16 * uu, sheer(uu) - 0.25, halfw(uu) * (2 * v - 1) * 0.92])
    P, N, a, u, v = surf(deck, int(16_000 * D), r)
    res.append(rows(P, np.tile([0, 1, 0], (len(P), 1)), PAL["deck"], 3, a, 0))

    def tube(path, rad, n, col):
        s = r.uniform(0, 1, n)
        th = r.uniform(0, 2 * np.pi, n)
        p = path(s)
        t = (path(np.clip(s + 1e-3, 0, 1)) - path(np.clip(s - 1e-3, 0, 1)))
        t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
        a_ = np.cross(t, [0, 0, 1])
        a_ /= np.linalg.norm(a_, axis=1, keepdims=True) + 1e-9
        b_ = np.cross(t, a_)
        nn = np.cos(th)[:, None] * a_ + np.sin(th)[:, None] * b_
        L = np.sum(np.linalg.norm(np.diff(path(np.linspace(0, 1, 200)), axis=0), axis=1))
        return rows(p + rad * nn, nn, col, 3, 2 * np.pi * rad * L / n, 0)

    def bez(s, pts):
        pts = np.asarray(pts, float)
        s = s[:, None]
        return (1 - s) ** 3 * pts[0] + 3 * (1 - s) ** 2 * s * pts[1] + 3 * (1 - s) * s**2 * pts[2] + s**3 * pts[3]
    res.append(tube(lambda s: bez(s, [[7.7, 2.3, 0], [9.4, 3.0, 0], [9.9, 4.6, 0], [9.0, 5.3, 0]]), 0.24, 6000, PAL["hull"]))
    head = r.normal(0, 1, (2500, 3)) * [0.55, 0.32, 0.25] + [9.3, 5.45, 0]
    res.append(rows(head, (head - [9.3, 5.45, 0]) / (np.linalg.norm(head - [9.3, 5.45, 0], axis=1, keepdims=True) + 1e-9), PAL["hull"], 3, 0.0012, 0))
    res.append(tube(lambda s: np.column_stack([-8.5 + (2.3 - 1.7 * s) * np.cos(-np.pi / 2 + 1.9 * np.pi * s), 4.0 + (2.3 - 1.7 * s) * np.sin(-np.pi / 2 + 1.9 * np.pi * s), np.zeros_like(s)]),
                    0.26, 9000, PAL["hull"]))
    res.append(tube(lambda s: np.column_stack([np.full_like(s, 0.5), 0.2 + 10.6 * s, np.zeros_like(s)]), 0.15, 5000, PAL["deck"] * 1.3))
    res.append(tube(lambda s: np.column_stack([np.full_like(s, 0.75), np.full_like(s, 9.6), -4.7 + 9.4 * s]), 0.13, 4000, PAL["deck"] * 1.3))
    # rigging
    for a_, b_ in (([0.5, 10.7, 0], [7.6, 2.2, 0]), ([0.5, 10.7, 0], [-7.6, 2.4, 0]), ([0.75, 9.6, -4.6], [-2.0, 2.4, -1.7]), ([0.75, 9.6, 4.6], [-2.0, 2.4, 1.7])):
        s = r.uniform(0, 1, 1200)[:, None]
        P = np.array(a_) * (1 - s) + np.array(b_) * s
        res.append(rows(P, np.tile([0, 0, 1], (1200, 1)), PAL["rope"] * 0.7, 3, 0.002, 0))
    # Dido at the bow
    m = 3000
    hgt = r.uniform(0, 1.7, m)
    th = r.uniform(0, 2 * np.pi, m)
    rad = 0.38 * (1 - hgt / 1.9)
    P = np.column_stack([6.2 + rad * np.cos(th), sheer(0.89) - 0.25 + hgt, rad * np.sin(th)])
    res.append(rows(P, np.column_stack([np.cos(th), np.zeros(m), np.sin(th)]), PAL["dido"], 3, 0.0015, 0))
    hd = r.normal(0, 0.14, (600, 3)) + [6.2, sheer(0.89) + 1.6, 0]
    res.append(rows(hd, np.tile([0, 1, 0], (600, 1)), PAL["deck"] * 1.6, 3, 0.0008, 0))
    # sail: flat coords, billow and furl in the shader
    n = int(60_000 * D)
    y, z = r.uniform(3.0, 9.5, n), r.uniform(-4.3, 4.3, n)
    stripe = np.floor((z + 4.3) / 8.6 * 9).astype(int) % 2
    col = np.where(stripe[:, None] == 1, PAL["tyrian"], PAL["cream"])
    dc = np.hypot(y - 6.7, z)
    emb = (dc < 1.0) | ((np.hypot(y - 6.2, z) > 1.25) & (np.hypot(y - 6.2, z) < 1.55) & (y < 6.4))
    col = np.where(emb[:, None], PAL["emblem"], col)
    res.append(rows(np.column_stack([np.full(n, 0.95), y, z]), np.tile([1, 0, 0], (n, 1)), col, 3, 6.5 * 8.6 / n, 1))
    # oars: pivot in pos, (side, index, distance along) in nrm
    for side in (-1, 1):
        for i in range(10):
            uu = 0.18 + i * 0.065
            piv = [-8 + 16 * uu, sheer(uu) + 0.02, side * halfw(uu)]
            m = 260
            s = r.uniform(0, 5.0, m)
            blade = (s > 4.0)
            P = np.tile(piv, (m, 1)) + r.normal(0, 0.035, (m, 3)) * (1 + 2.5 * blade[:, None])
            res.append(rows(P, np.column_stack([np.full(m, side), np.full(m, i), s]), PAL["oar"], 3, 0.003, 2))
    # flag
    m = 2500
    fx, fy = r.uniform(0, 1.7, m), r.uniform(0, 0.8, m)
    res.append(rows(np.column_stack([fx, fy, np.zeros(m)]), np.tile([0, 0, 1], (m, 1)), PAL["emblem"], 3, 1.7 * 0.8 / m, 3))
    return np.concatenate(res)


def foam(r):
    n = int(46_000 * D)
    side = r.choice([-1.0, 1.0], n)
    xh = r.uniform(-7.5, 7.0, n)
    jit = r.uniform(-1, 1, n)
    return rows(np.zeros((n, 3)), np.column_stack([side, xh, jit]), PAL["foam"] * r.uniform(0.5, 1.0, (n, 1)), 5, 0.02 / D, r.uniform(0, 1, n))


def gulls(r):
    res = []
    for g in range(6):
        m = 220
        u = r.uniform(-1, 1, m)
        res.append(rows(r.normal(0, 0.05, (m, 3)), np.column_stack([u, np.full(m, g), np.zeros(m)]), PAL["cream"] * 0.8, 6, 0.004))
    return np.concatenate(res)


def build():
    r = np.random.default_rng(12)
    import overlays
    parts = [sea(r), sky(r), land(r), ship(r), foam(r), gulls(r), overlays.build(rows)]
    P = np.concatenate(parts).astype(np.float32)
    return P[np.argsort(P[:, 9], kind="stable")]             # grouped by kind, so passes can draw ranges


def cached():
    if CACHE.exists():
        return np.load(CACHE)
    CACHE.parent.mkdir(exist_ok=True)
    P = build()
    np.save(CACHE, P)
    return P


if __name__ == "__main__":
    P = build()
    CACHE.parent.mkdir(exist_ok=True)
    np.save(CACHE, P)
    for k in range(8):
        print(k, int((P[:, 9] == k).sum()))
    print(f"{len(P):,} points")
