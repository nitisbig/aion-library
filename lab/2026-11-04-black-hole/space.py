"""Geometry for acts 1 and 3 (seeded, deterministic).

dust():  particles scattered around the camera's flight path for the travel shot. Their lateral
         spread is proportional to the distance from the hole, so the field is scale-invariant and
         streams past at a steady rate while the camera covers 3000M → 80M in log-distance.
grid():  Flamm's paraboloid, the exact embedding of the Schwarzschild equatorial space slice,
         z(r) = √(8M(r − 2M)). Circles are spaced equally in proper radial distance
         ds = dr / √(1 − 2M/r), so the visible crowding near the throat is the real stretching of space.
"""

from __future__ import annotations

import numpy as np

import timeline as TL


def dust(n_dust=5200, n_star=70, seed=7):
    rng = np.random.default_rng(seed)
    out = []
    for kind, n in ((0, n_dust), (1, n_star)):
        ts = rng.uniform(0.0, 13.0, n)
        P = np.array([TL.camera(t)[0] for t in ts])
        P2 = np.array([TL.camera(t + 0.05)[0] for t in ts])
        mot = P2 - P
        mot /= np.linalg.norm(mot, axis=1, keepdims=True)
        d = np.linalg.norm(P, axis=1)
        rnd = rng.normal(size=(n, 3))
        lat = rnd - (rnd * mot).sum(1, keepdims=True) * mot
        lat /= np.linalg.norm(lat, axis=1, keepdims=True)
        spread = (0.012 + 0.22 * rng.random(n) ** 1.7) if kind == 0 else (0.02 + 0.12 * rng.random(n))
        pos = P + lat * (d * spread)[:, None] + mot * (d * rng.uniform(-0.04, 0.04, n))[:, None]
        keep = np.linalg.norm(pos, axis=1) > 150.0          # stay out of the strong-lensing zone
        pos = pos[keep]
        m = len(pos)
        if kind == 0:
            bright = 0.25 + 0.75 * rng.random(m) ** 3
            temp = rng.uniform(5500, 9000, m)
            size = np.full(m, 1.0)
        else:
            bright = 3.0 + 6.0 * rng.random(m) ** 2
            temp = np.exp(rng.uniform(np.log(3200), np.log(14000), m))
            size = rng.uniform(1.6, 2.6, m)
        out.append(np.column_stack([pos, bright, temp, size, np.full(m, kind)]))
    return np.vstack(out).astype("f4")


# ── act 3: Flamm's paraboloid ───────────────────────────────────────────────
def proper_radii(r0=2.0, r1=TL.GRID_R, ds=1.25):
    """Radii spaced equally in proper distance from the horizon,
    s(r) = ∫₂^r dr/√(1−2/r) = √(r(r−2)) + 2 ln((√r + √(r−2)) / √2)   (closed form, M = 1)."""
    r = np.linspace(r0, r1, 20001)
    s = np.sqrt(r * (r - 2.0)) + 2.0 * np.log((np.sqrt(r) + np.sqrt(r - 2.0)) / np.sqrt(2.0))
    return np.interp(np.arange(ds, s[-1], ds), s, r)


# per-vertex layout: x, z, r, s, t0, dur, kind, phase, R, G, B
#   kind: 0 circle, 1 radial line, 2 photon sphere, 3 horizon, 4 ISCO
def grid(cols):
    verts = []

    def poly(pts_xz, rs, t0, dur, kind, phase, col):
        seg = np.linalg.norm(np.diff(pts_xz, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        s /= s[-1]
        for i in range(len(pts_xz) - 1):
            for j in (i, i + 1):
                verts.append([pts_xz[j, 0], pts_xz[j, 1], rs[j], s[j], t0, dur, kind, phase, *col])

    def circle(r, t0, dur, kind, col, a0=0.0, n=None):
        n = n or int(120 + 10 * r)
        th = a0 + np.linspace(0, 2 * np.pi, n)
        poly(np.stack([r * np.cos(th), r * np.sin(th)], 1), np.full(n, r), t0, dur, kind, 0.0, col)

    # highlighted circles first: photon sphere (continuity with the ring), horizon, ISCO
    circle(3.0, 44.3, 1.3, 2, cols["sphere"], a0=np.pi / 2)
    circle(2.0, 45.1, 1.1, 3, cols["horizon"], a0=np.pi / 2)
    circle(6.0, 45.5, 1.3, 4, cols["isco"], a0=np.pi / 2)
    # radial lines grow outward from the horizon
    n_rad = 64
    rng = np.random.default_rng(3)
    rr = 2.0 + (TL.GRID_R - 2.0) * np.linspace(0, 1, 240) ** 1.6
    for k in range(n_rad):
        a = 2 * np.pi * k / n_rad
        delay = 46.0 + 0.9 * ((k * 37) % n_rad) / n_rad
        poly(np.stack([rr * np.cos(a), rr * np.sin(a)], 1), rr, delay, 1.6, 1, rng.random(), cols["grid"])
    # circles equally spaced in proper distance, revealed inside → out
    radii = [r for r in proper_radii() if abs(r - 3.0) > 0.25 and abs(r - 6.0) > 0.35]
    for i, r in enumerate(radii):
        circle(r, 46.4 + 2.0 * i / len(radii), 1.1, 0, cols["grid"], a0=0.37 * i)
    return np.asarray(verts, "f4")
