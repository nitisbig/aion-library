"""Procedural night city as 3D Gaussian splats.

Every splat carries the real 3DGS parameters (Kerbl et al. 2023): a mean μ, a covariance
Σ = R S Sᵀ Rᵀ (built here from three orthonormal axes and three standard deviations), an opacity,
and a view-dependent colour term (a degree-1 SH-like lobe along the surface normal, used for glass).

Units are metres, y is up. The city is a 90 m street grid; the avenue (x = 0) and the boulevard (z = 0)
are 32 m wide and meet at a round plaza with the hero tower at its centre.

    uv run python lab/2026-11-04-gaussian-splat-city/city.py      # stats + asserts
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

SEED = 11
PITCH = 90.0
LINES = np.arange(-5, 6) * PITCH            # street centre lines, both directions
WIDE, NARROW, SIDEWALK = 32.0, 20.0, 4.0
CITY_R = 400.0                              # beyond this the city dissolves into the void
PLAZA_R = 56.0
FLOOR = 3.6
LAMP_Y = 7.6
HERO = [(16.0, 0.0, 92.0), (13.0, 92.0, 158.0), (10.0, 158.0, 208.0), (7.0, 208.0, 238.0)]   # half-width, y0, y1
SPIRE_TOP = 300.0

KINDS = ["BODY", "WIN_WARM", "WIN_COOL", "GLASS", "RIM", "ROOF", "NEON_A", "NEON_B", "STREET", "SIDEWALK",
         "LANE", "POLE", "LAMP", "GROUND", "TREE", "TRUNK", "CAR_BODY", "CAR_HEAD", "CAR_TAIL", "BEAM",
         "SPIRE", "BEACON", "FLOATER", "PLAZA", "SHOP"]
K = {k: i for i, k in enumerate(KINDS)}
G_STATIC, G_SPIRE, G_FLOAT, G_CAR, G_BEACON = 0, 1, 2, 3, 4

# how strongly each kind picks up warm light from the street lamps
LIT_GAIN = {K["STREET"]: 0.9, K["SIDEWALK"]: 1.0, K["GROUND"]: 0.6, K["PLAZA"]: 0.8, K["TREE"]: 1.1,
            K["TRUNK"]: 0.8, K["BODY"]: 0.35, K["RIM"]: 0.3, K["POLE"]: 0.6}

EX, EY, EZ = np.eye(3)


def width(L):
    return WIDE if abs(L) < 1 else NARROW


def smax(a, b, k=4.0):
    h = np.clip(0.5 + 0.5 * (a - b) / k, 0, 1)
    return a * h + b * (1 - h) + k * h * (1 - h)


def edge_fade(r):
    x = np.clip((r - (CITY_R - 80)) / 130.0, 0, 1)
    return 1 - x * x * (3 - 2 * x)


def rand_rot(rng, n):
    q = rng.normal(size=(n, 4))
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    w, x, y, z = q.T
    R = np.stack([np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                  np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                  np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], 1)
    return np.transpose(R, (0, 2, 1))       # rows = axes


class Splats:
    FIELDS = ("pos", "cov", "alpha", "kind", "var", "normal", "shk", "group")

    def __init__(self):
        self.parts = {f: [] for f in self.FIELDS}

    def add(self, pos, s, axes, kind, alpha, var=1.0, normal=None, shk=0.0, group=G_STATIC):
        pos = np.asarray(pos, float).reshape(-1, 3)
        n = len(pos)
        if n == 0:
            return
        s = np.broadcast_to(np.asarray(s, float), (n, 3))
        axes = np.asarray(axes, float)
        axes = np.broadcast_to(axes, (n, 3, 3)) if axes.ndim == 2 else axes
        cov = np.einsum("nk,nki,nkj->nij", s * s, axes, axes)          # Σ = Σ_k s_k² a_k a_kᵀ
        P = self.parts
        P["pos"].append(pos)
        P["cov"].append(cov[:, [0, 0, 0, 1, 1, 2], [0, 1, 2, 1, 2, 2]])
        P["alpha"].append(np.broadcast_to(np.asarray(alpha, float), (n,)).copy())
        P["kind"].append(np.full(n, K[kind] if isinstance(kind, str) else kind, int) if np.ndim(kind) == 0
                         else np.asarray(kind, int))
        P["var"].append(np.broadcast_to(np.asarray(var, float), (n,)).copy())
        P["normal"].append(np.zeros((n, 3)) if normal is None else np.broadcast_to(np.asarray(normal, float), (n, 3)).copy())
        P["shk"].append(np.broadcast_to(np.asarray(shk, float), (n,)).copy())
        P["group"].append(np.full(n, group, int))

    def arrays(self):
        return {f: np.concatenate(v) for f, v in self.parts.items()}


# ── buildings ────────────────────────────────────────────────────────────────
FACE_LIGHT = DIR = np.array([-0.6, 0.0, 0.8]) / 1.0


def faces(x0, x1, z0, z1):
    """(origin corner, u axis, width, outward normal) for the four walls, u running left→right seen from outside."""
    return [(np.array([x0, 0, z1]), EX, x1 - x0, EZ), (np.array([x1, 0, z0]), -EX, x1 - x0, -EZ),
            (np.array([x1, 0, z1]), -EZ, z1 - z0, EX), (np.array([x0, 0, z0]), EZ, z1 - z0, -EX)]


def face_shade(n):
    return 0.5 + 0.5 * max(0.0, float(n @ DIR) / np.linalg.norm(DIR))


def box_tier(S, rng, b, x0, x1, z0, z1, y0, y1, top, hero=False):
    for o, u, W, n in faces(x0, x1, z0, z1):
        Hh = y1 - y0
        shade = face_shade(n) * (1.3 if hero else 1.0)
        ax = np.array([u, EY, n])
        # body: overlapping flat discs tiling the wall
        nu, nv = max(1, round(W / 2.0)), max(1, round(Hh / 2.0))
        uu, vv = np.meshgrid((np.arange(nu) + 0.5) * W / nu, (np.arange(nv) + 0.5) * Hh / nv)
        uu, vv = uu.ravel(), vv.ravel()
        pos = o + uu[:, None] * u + (y0 + vv)[:, None] * EY + rng.normal(0, 0.08, (len(uu), 3))
        street_bounce = 1.0 + 0.8 * np.exp(-(y0 + vv) / 14.0)
        S.add(pos, (0.72 * W / nu, 0.72 * Hh / nv, 0.06), ax, "BODY", 0.7,
              shade * street_bounce * rng.uniform(0.8, 1.15, len(uu)), n, 0.25)
        # windows
        style = b["style"]
        nf = int((Hh - 1.5) // FLOOR)
        if nf >= 1 and W > 4:
            fl = np.arange(nf)
            fy = y0 + 0.9 + (fl + 0.5) * FLOOR
            if style == "bands":
                nb = max(1, int(W / 1.6))
                rw, rh, sub = 0.95 * W / nb, 1.4, (2, 2)
            else:
                nb = max(1, int(W / 3.2))
                rw, rh, sub = ((0.6 * W / nb, 2.0, (3, 2)) if style == "grid" else (0.88 * W / nb, 2.6, (3, 3)))
            bu = (np.arange(nb) + 0.5) * W / nb
            U, F = np.meshgrid(bu, fl)
            U, F = U.ravel(), F.ravel()
            fmul = b["floor_mul"][np.clip(F + int(y0 / FLOOR), 0, len(b["floor_mul"]) - 1)]
            if style == "bands":                       # whole floors light up together
                lit = (b["floor_rnd"][np.clip(F + int(y0 / FLOOR), 0, 199)] < b["lit"] * fmul)
            else:
                lit = rng.random(len(U)) < b["lit"] * fmul
            warm = rng.random(len(U)) < b["warm"]
            kind = np.where(lit, np.where(warm, K["WIN_WARM"], K["WIN_COOL"]), K["GLASS"])
            var = np.where(lit, rng.uniform(0.55, 1.25, len(U)), rng.uniform(0.7, 1.1, len(U)))
            # each window is a small grid of tighter Gaussians, so it keeps a crisp rectangle up close
            # (a trained capture densifies exactly there: high-frequency edges get more, smaller splats)
            su = ((np.arange(sub[0]) + 0.5) / sub[0] - 0.5) * rw
            sv = ((np.arange(sub[1]) + 0.5) / sub[1] - 0.5) * rh
            SU, SV = (a.ravel() for a in np.meshgrid(su, sv))
            m = len(SU)
            ctr = o + U[:, None] * u + fy[F][:, None] * EY + n * 0.09
            pos = (ctr[:, None, :] + SU[None, :, None] * u + SV[None, :, None] * EY).reshape(-1, 3)
            rep = lambda a: np.repeat(a, m)          # noqa: E731
            S.add(pos, (0.62 * rw / sub[0], 0.62 * rh / sub[1], 0.04), ax, rep(kind), rep(np.where(lit, 0.85, 0.75)),
                  rep(var), n, rep(np.where(lit, 0.15, 1.0)))
            if style == "curtain":                     # mullions
                mu = np.arange(0, nb + 1, 2) * W / nb
                mv = np.arange(y0 + 1.0, y1, 1.6)
                MU, MV = np.meshgrid(mu, mv)
                pos = o + MU.ravel()[:, None] * u + MV.ravel()[:, None] * EY + n * 0.14
                S.add(pos, (0.08, 0.9, 0.05), ax, "RIM", 0.6, 0.45 * shade, n)
        # shop fronts on the ground floor
        if y0 == 0 and not hero and rng.random() < b["shops"] and W > 8:
            ns = max(1, int(W / 1.4))
            pu = (np.arange(ns) + 0.5) * W / ns
            pos = o + pu[:, None] * u + 2.0 * EY + n * 0.15
            S.add(pos, (0.62 * W / ns, 1.1, 0.05), ax, "SHOP", 0.85, rng.uniform(0.6, 1.2, ns), n, 0.1)
            if rng.random() < 0.55:                    # a neon sign above the door
                c = rng.uniform(0.2, 0.8) * W
                ln = rng.uniform(2.5, 5.0)
                m = int(ln / 0.4)
                pos = o + (c + np.linspace(-ln / 2, ln / 2, m))[:, None] * u + 4.6 * EY + n * 0.25
                S.add(pos, (0.25, 0.12, 0.06), ax, "NEON_A" if rng.random() < 0.5 else "NEON_B", 0.95, 1.0, n)
    # vertical corner rims
    rk = "SPIRE" if hero and y0 >= 92 else "RIM"
    rg = G_SPIRE if rk == "SPIRE" else G_STATIC
    ys = np.arange(y0 + 0.8, y1, 1.6)
    for cx, cz in ((x0, z0), (x0, z1), (x1, z0), (x1, z1)):
        pos = np.column_stack([np.full(len(ys), cx), ys, np.full(len(ys), cz)])
        S.add(pos, (0.14, 1.0, 0.14), np.eye(3), rk, 0.85, 1.0, group=rg)
    # roof edge rims
    for (a, bb, fixed, along_x) in ((x0, x1, z0, True), (x0, x1, z1, True), (z0, z1, x0, False), (z0, z1, x1, False)):
        t = np.arange(a + 0.8, bb, 1.6)
        pos = (np.column_stack([t, np.full(len(t), y1), np.full(len(t), fixed)]) if along_x
               else np.column_stack([np.full(len(t), fixed), np.full(len(t), y1), t]))
        S.add(pos, (1.0, 0.13, 0.13), np.eye(3) if along_x else np.array([EZ, EY, EX]), rk, 0.85, 1.2, group=rg)
    # roof
    gx = np.arange(x0 + 1.3, x1, 2.6)
    gz = np.arange(z0 + 1.3, z1, 2.6)
    GX, GZ = np.meshgrid(gx, gz)
    GX, GZ = GX.ravel(), GZ.ravel()
    keep = np.ones(len(GX), bool)
    if top is not None:                               # not under the next tier
        tx0, tx1, tz0, tz1 = top
        keep = ~((GX > tx0) & (GX < tx1) & (GZ > tz0) & (GZ < tz1))
    pos = np.column_stack([GX, np.full(len(GX), y1), GZ])[keep]
    S.add(pos, (1.25, 1.25, 0.06), np.array([EX, EZ, EY]), "ROOF", 0.75, rng.uniform(0.7, 1.1, keep.sum()), EY)


def building(S, rng, x0, x1, z0, z1, H):
    b = dict(style=rng.choice(["grid", "curtain", "bands"], p=[0.45, 0.3, 0.25]),
             lit=rng.uniform(0.12, 0.5), warm=rng.uniform(0.15, 0.9), shops=0.5 if H < 140 else 0.3,
             floor_mul=rng.choice([0.2, 1.0, 1.7], 200, p=[0.25, 0.5, 0.25]), floor_rnd=rng.random(200))
    tiers = [(x0, x1, z0, z1, 0.0, H)]
    if H > 70 and rng.random() < 0.65:
        nt = 2 if H < 140 else 3
        cuts = np.sort(rng.uniform(0.45, 0.85, nt - 1))[::-1] if nt == 3 else [rng.uniform(0.55, 0.8)]
        cuts = sorted(cuts)
        tiers, y = [], 0.0
        bx0, bx1, bz0, bz1 = x0, x1, z0, z1
        for i, c in enumerate([*cuts, 1.0]):
            y1 = H * c
            tiers.append((bx0, bx1, bz0, bz1, y, y1))
            ins = rng.uniform(2.5, 6.0)
            if bx1 - bx0 - 2 * ins < 8 or bz1 - bz0 - 2 * ins < 8:
                tiers[-1] = (bx0, bx1, bz0, bz1, y, H)
                break
            bx0, bx1, bz0, bz1, y = bx0 + ins, bx1 - ins, bz0 + ins, bz1 - ins, y1
    for i, t in enumerate(tiers):
        top = tiers[i + 1][:4] if i + 1 < len(tiers) else None
        box_tier(S, rng, b, *t, top)
    tx0, tx1, tz0, tz1, _, yt = tiers[-1]
    # neon accents
    if rng.random() < 0.2:
        ys = np.arange(8.0, 0.75 * H, 0.7)
        cx, cz = [(tx0, tz1), (tx1, tz1), (tx0, tz0), (tx1, tz0)][rng.integers(4)]
        pos = np.column_stack([np.full(len(ys), cx), ys, np.full(len(ys), cz)])
        S.add(pos, (0.2, 0.55, 0.2), np.eye(3), "NEON_A" if rng.random() < 0.5 else "NEON_B", 0.95, 1.0)
    elif rng.random() < 0.18:
        for o, u, W, n in faces(tx0, tx1, tz0, tz1):
            t = np.arange(0.5, W, 0.7)
            pos = o + t[:, None] * u + (yt - 1.6) * EY + n * 0.25
            S.add(pos, (0.5, 0.16, 0.05), np.array([u, EY, n]), "NEON_B", 0.95, 1.0, n)
    # rooftop plant and antenna with a beacon
    if rng.random() < 0.7 and tx1 - tx0 > 10:
        for _ in range(rng.integers(1, 4)):
            cx, cz = rng.uniform(tx0 + 3, tx1 - 3), rng.uniform(tz0 + 3, tz1 - 3)
            w, h = rng.uniform(1.5, 3.5), rng.uniform(1.5, 3.0)
            pos = np.array([cx, yt, cz]) + rng.uniform([-w, 0, -w], [w, h, w], (14, 3))
            S.add(pos, (0.8, 0.6, 0.8), np.eye(3), "BODY", 0.8, 0.7)
    if H > 110 and rng.random() < 0.8:
        cx, cz = (tx0 + tx1) / 2, (tz0 + tz1) / 2
        ah = rng.uniform(10, 22)
        ys = np.arange(yt, yt + ah, 1.0)
        S.add(np.column_stack([np.full(len(ys), cx), ys, np.full(len(ys), cz)]), (0.1, 0.6, 0.1), np.eye(3),
              "POLE", 0.8, 0.8)
        S.add([cx, yt + ah, cz], (0.45, 0.45, 0.45), np.eye(3), "BEACON", 1.0, 1.0, group=G_BEACON)


def hero_tower(S, rng):
    b = dict(style="curtain", lit=0.32, warm=0.25, shops=0.0, floor_mul=rng.choice([0.4, 1.0, 1.5], 200),
             floor_rnd=rng.random(200))
    for i, (hw, y0, y1) in enumerate(HERO):
        top = None
        if i + 1 < len(HERO):
            h2 = HERO[i + 1][0]
            top = (-h2, h2, -h2, h2)
        box_tier(S, rng, b, -hw, hw, -hw, hw, y0, y1, top, hero=True)
    # spire: a tapering needle of elongated splats
    ys = np.arange(HERO[-1][2], SPIRE_TOP, 0.9)
    f = (ys - ys[0]) / (SPIRE_TOP - ys[0])
    r = 0.9 * (1 - f) + 0.08
    S.add(np.column_stack([np.zeros(len(ys)), ys, np.zeros(len(ys))]),
          np.column_stack([r, np.full(len(ys), 0.8), r]), np.eye(3), "SPIRE", 0.95, 1.0, group=G_SPIRE)
    S.add([0, SPIRE_TOP + 0.6, 0], (0.6, 0.6, 0.6), np.eye(3), "BEACON", 1.0, 1.4, group=G_BEACON)
    # podium lights at the base
    a = np.linspace(0, 2 * np.pi, 160, endpoint=False)
    S.add(np.column_stack([19.5 * np.cos(a), np.full(160, 0.4), 19.5 * np.sin(a)]), (0.35, 0.12, 0.35), np.eye(3),
          "LANE", 0.9, 1.2)


def blocks(S, rng):
    n_b = 0
    for i in range(len(LINES) - 1):
        for j in range(len(LINES) - 1):
            bx0 = LINES[i] + width(LINES[i]) / 2 + SIDEWALK
            bx1 = LINES[i + 1] - width(LINES[i + 1]) / 2 - SIDEWALK
            bz0 = LINES[j] + width(LINES[j]) / 2 + SIDEWALK
            bz1 = LINES[j + 1] - width(LINES[j + 1]) / 2 - SIDEWALK
            rc = np.hypot((bx0 + bx1) / 2, (bz0 + bz1) / 2)
            if rc > CITY_R + 40:
                continue
            split = rng.choice([1, 2, 3], p=[0.15, 0.35, 0.5])
            xs = [bx0, bx1] if split == 1 else [bx0, (bx0 + bx1) / 2, bx1]
            zs = [bz0, bz1] if split < 3 else [bz0, (bz0 + bz1) / 2, bz1]
            if split == 2 and rng.random() < 0.5:
                xs, zs = [bx0, bx1], [bz0, (bz0 + bz1) / 2, bz1]
            for a in range(len(xs) - 1):
                for c in range(len(zs) - 1):
                    x0, x1, z0, z1 = xs[a], xs[a + 1], zs[c], zs[c + 1]
                    x0, x1 = x0 + rng.uniform(0.5, 3), x1 - rng.uniform(0.5, 3)
                    z0, z1 = z0 + rng.uniform(0.5, 3), z1 - rng.uniform(0.5, 3)
                    # keep the plaza clear: pull the footprint back from the centre
                    for _ in range(12):
                        nx = np.clip(0, x0, x1)
                        nz = np.clip(0, z0, z1)
                        if np.hypot(nx, nz) >= PLAZA_R + 2:
                            break
                        if abs(nx) > abs(nz) or (abs(nx) == abs(nz) and x0 > 0):
                            if x0 > 0:
                                x0 += 3
                            else:
                                x1 -= 3
                        else:
                            if z0 > 0:
                                z0 += 3
                            else:
                                z1 -= 3
                    if x1 - x0 < 9 or z1 - z0 < 9 or np.hypot(np.clip(0, x0, x1), np.clip(0, z0, z1)) < PLAZA_R:
                        continue
                    r = np.hypot((x0 + x1) / 2, (z0 + z1) / 2)
                    hmax = 26 + 165 * np.exp(-(r / 210) ** 2)
                    H = FLOOR * max(3, round(hmax * (0.35 + 0.65 * rng.random() ** 1.6) / FLOOR)) + 1.0
                    building(S, rng, x0, x1, z0, z1, H)
                    n_b += 1
    return n_b


# ── streets ──────────────────────────────────────────────────────────────────
def nearest_line(v):
    i = np.clip(np.round(v / PITCH).astype(int) + 5, 0, len(LINES) - 1)
    L = LINES[i]
    return L, np.abs(v - L), np.where(np.abs(L) < 1, WIDE, NARROW) / 2


def ground(S, rng):
    g = np.arange(-CITY_R - 60, CITY_R + 60 + 1e-6, 2.5)
    X, Z = np.meshgrid(g, g)
    X, Z = X.ravel() + rng.normal(0, 0.2, X.size), Z.ravel() + rng.normal(0, 0.2, X.size)
    r = np.hypot(X, Z)
    keep = r < CITY_R + 60
    X, Z, r = X[keep], Z[keep], r[keep]
    _, dx, hx = nearest_line(X)
    _, dz, hz = nearest_line(Z)
    street = (dx < hx) | (dz < hz)
    walk = ~street & ((dx < hx + SIDEWALK) | (dz < hz + SIDEWALK))
    plaza = r < PLAZA_R
    kind = np.where(plaza, K["PLAZA"], np.where(street, K["STREET"], np.where(walk, K["SIDEWALK"], K["GROUND"])))
    pos = np.column_stack([X, rng.normal(0, 0.03, len(X)), Z])
    var = rng.uniform(0.65, 1.1, len(X))
    var = np.where(plaza, var * (1.0 + 0.4 * (np.cos(np.arctan2(Z, X) * 24) > 0.85)), var)   # radial paving
    S.add(pos, (1.6, 1.6, 0.05), np.array([EX, EZ, EY]), kind, 0.8, var, EY, 0.0)

    # lane markings
    marks = []
    for L in LINES:
        hw = width(L) / 2
        t = np.arange(-CITY_R - 40, CITY_R + 40, 1.2)
        cross_ok = nearest_line(t)[1] > nearest_line(t)[2] + 1.5
        for off, dash in ([(-0.25, False), (0.25, False), (-8.0, True), (8.0, True)] if hw > 12 else [(0.0, True)]):
            ok = cross_ok & ((np.mod(t, 9.0) < 3.0) if dash else True)
            for along_z in (True, False):
                tt = t[ok]
                pos = (np.column_stack([np.full(len(tt), L + off), np.full(len(tt), 0.04), tt]) if along_z
                       else np.column_stack([tt, np.full(len(tt), 0.04), np.full(len(tt), L + off)]))
                pos = pos[np.hypot(pos[:, 0], pos[:, 2]) > PLAZA_R + 2]
                marks.append((pos, along_z))
    for pos, along_z in marks:
        S.add(pos, (0.08, 0.75, 0.03), np.array([EX, EZ, EY]) if along_z else np.array([EZ, EX, EY]), "LANE", 0.8,
              0.8)
    # zebra crossings where the avenue / boulevard meet the side streets
    for L in LINES:
        if abs(L) < 1:
            continue
        for along_z in (True, False):
            for side in (-1, 1):
                c = L + side * (NARROW / 2 + 2.5)
                xs = np.arange(-14.5, 15, 1.6)
                pos = (np.column_stack([xs, np.full(len(xs), 0.05), np.full(len(xs), c)]) if along_z
                       else np.column_stack([np.full(len(xs), c), np.full(len(xs), 0.05), xs]))
                S.add(pos, (0.35, 1.6, 0.03), np.array([EX, EZ, EY]) if along_z else np.array([EZ, EX, EY]), "LANE", 0.75,
                      0.6)
    # plaza: two rings of light
    for R in (30.0, 52.0):
        a = np.arange(0, 2 * np.pi, 1.4 / R)
        S.add(np.column_stack([R * np.cos(a), np.full(len(a), 0.08), R * np.sin(a)]), (0.3, 0.3, 0.05),
              np.array([EX, EZ, EY]), "LANE", 0.95, 1.6)


def lamps_and_trees(S, rng):
    lamps = []
    for L in LINES:
        hw = width(L) / 2
        step = 24.0 if hw > 12 else 36.0
        t = np.arange(-CITY_R, CITY_R + 1, step) + (step / 2 if hw > 12 else 0)
        t = t[nearest_line(t)[1] > nearest_line(t)[2] + 3]
        sides = (-1, 1) if hw > 12 else (1,)
        for sd in sides:
            for along_z in (True, False):
                for v in t:
                    p = (L + sd * (hw + 0.8), v) if along_z else (v, L + sd * (hw + 0.8))
                    if np.hypot(*p) < PLAZA_R + 1 or np.hypot(*p) > CITY_R + 20:
                        continue
                    lamps.append((p[0], p[1], -sd if along_z else 0, 0 if along_z else -sd))
    lamps = np.array(lamps)
    # plaza lamps around the ring
    a = np.arange(0, 2 * np.pi, 2 * np.pi / 16) + 0.1
    lamps = np.vstack([lamps, np.column_stack([48 * np.cos(a), 48 * np.sin(a), -np.cos(a), -np.sin(a)])])
    ys = np.arange(0.4, LAMP_Y, 0.8)
    for x, z, ux, uz in lamps:
        S.add(np.column_stack([np.full(len(ys), x), ys, np.full(len(ys), z)]), (0.09, 0.5, 0.09), np.eye(3), "POLE",
              0.85, 0.8)
        arm = np.array([x, LAMP_Y, z]) + np.linspace(0, 1.6, 3)[:, None] * np.array([ux, 0, uz])
        S.add(arm, (0.4, 0.07, 0.07), np.array([[ux, 0, uz], EY, [-uz, 0, ux]]) if (ux or uz) else np.eye(3), "POLE",
              0.85, 0.8)
        S.add(arm[-1] - [0, 0.15, 0], (0.42, 0.18, 0.42), np.eye(3), "LAMP", 1.0, 1.0)
    heads = np.column_stack([lamps[:, 0] + 1.6 * lamps[:, 2], np.full(len(lamps), LAMP_Y - 0.2),
                             lamps[:, 1] + 1.6 * lamps[:, 3]])

    # trees along the avenue and boulevard sidewalks, and around the plaza
    trees = []
    for along_z in (True, False):
        for sd in (-1, 1):
            t = np.arange(-CITY_R + 6, CITY_R, 12.0)
            t = t[(nearest_line(t)[1] > NARROW / 2 + 5) & (np.abs(t) > PLAZA_R + 4)]
            for v in t:
                trees.append((sd * (WIDE / 2 + 2.6), v) if along_z else (v, sd * (WIDE / 2 + 2.6)))
    a = np.arange(0, 2 * np.pi, 2 * np.pi / 22)
    trees += list(zip(41 * np.cos(a), 41 * np.sin(a)))
    trees = np.array(trees)
    trees = trees[np.hypot(trees[:, 0], trees[:, 1]) < CITY_R + 10]
    for x, z in trees:
        n = 90
        c = np.array([x, 6.4 + rng.normal(0, 0.5), z])
        d = rng.normal(size=(n, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        p = c + d * rng.random((n, 1)) ** 0.45 * np.array([3.0, 2.5, 3.0])
        var = 0.6 + 0.5 * (p[:, 1] - c[1] + 2.5) / 5
        S.add(p, (0.6, 0.45, 0.13), rand_rot(rng, n), "TREE", 0.8, var * rng.uniform(0.8, 1.2, n))
        tys = np.arange(0.5, 4.5, 0.9)
        S.add(np.column_stack([np.full(len(tys), x), tys, np.full(len(tys), z)]), (0.16, 0.55, 0.16), np.eye(3),
              "TRUNK", 0.9, 0.8)
    return heads, len(trees)


def floaters(S, rng, n=4500):
    r = rng.uniform(CITY_R - 40, 1100, n)
    a = rng.uniform(0, 2 * np.pi, n)
    y = rng.uniform(-80, 420, n) * (0.4 + 0.6 * rng.random(n))
    pos = np.column_stack([r * np.cos(a), y, r * np.sin(a)])
    s = rng.uniform(0.5, 3.0, n) ** 1.3
    S.add(pos, np.column_stack([s, s * rng.uniform(0.5, 1, n), s * rng.uniform(0.3, 1, n)]), rand_rot(rng, n),
          "FLOATER", rng.uniform(0.15, 0.6, n), rng.uniform(0.3, 1.2, n), group=G_FLOAT)


def lamp_light(pos, heads):
    """Warm light received from the street lamps (soft inverse-square with a 30 m cut-off)."""
    lit = np.zeros(len(pos))
    low = np.where(pos[:, 1] < 30)[0]
    if len(low) == 0:
        return lit
    D = cKDTree(pos[low]).sparse_distance_matrix(cKDTree(heads), 30.0, output_type="coo_matrix")
    d = D.data
    w = 1.0 / (1.0 + (d / 5.5) ** 2) * (1 - d / 30.0) ** 2
    np.add.at(lit, low[D.row], w)
    return np.minimum(lit, 2.5)


def build(seed=SEED):
    rng = np.random.default_rng(seed)
    S = Splats()
    ground(S, rng)
    heads, n_trees = lamps_and_trees(S, rng)
    hero_tower(S, rng)
    n_b = blocks(S, rng)
    floaters(S, rng)
    A = S.arrays()
    r = np.hypot(A["pos"][:, 0], A["pos"][:, 2])
    fade = np.where(A["group"] == G_FLOAT, 1.0, edge_fade(r))
    A["alpha"] = A["alpha"] * fade
    keep = A["alpha"] > 0.02
    A = {k: v[keep] for k, v in A.items()}
    gain = np.zeros(len(KINDS))
    for k, v in LIT_GAIN.items():
        gain[k] = v
    A["lit"] = lamp_light(A["pos"], heads) * gain[A["kind"]]
    A["h"] = rng.random(len(A["alpha"]))
    A["meta"] = dict(buildings=n_b, lamps=len(heads), trees=n_trees)
    return A


# ── cars (dynamic, rebuilt every frame from sim time τ) ─────────────────────
def _car_template():
    """Local frame: x right, y up, z forward. Returns pos, sigmas, kind, var."""
    P, Sg, Kd, V = [], [], [], []
    for x in (-0.55, 0.55):
        for z in (-1.6, -0.55, 0.55, 1.6):
            P.append((x, 0.55, z)); Sg.append((0.5, 0.33, 0.7)); Kd.append("CAR_BODY"); V.append(1.0)
    for z in (-0.6, 0.4):
        P.append((0, 1.15, z)); Sg.append((0.6, 0.25, 0.7)); Kd.append("CAR_BODY"); V.append(1.3)
    for x in (-0.68, 0.68):
        P.append((x, 0.65, 2.2)); Sg.append((0.16, 0.12, 0.08)); Kd.append("CAR_HEAD"); V.append(1.0)
        P.append((x, 0.75, -2.2)); Sg.append((0.18, 0.1, 0.08)); Kd.append("CAR_TAIL"); V.append(1.0)
    P.append((0, 0.06, 7.0)); Sg.append((1.5, 0.04, 4.2)); Kd.append("BEAM"); V.append(1.0)
    return np.array(P), np.array(Sg), np.array([K[k] for k in Kd]), np.array(V)


class Traffic:
    def __init__(self, seed=SEED + 1):
        rng = np.random.default_rng(seed)
        self.tpl = _car_template()
        self.lanes = []
        t = np.arange(-470, 470.01, 2.0)
        for L in LINES:
            hw = width(L) / 2
            offs = (-11.0, -4.5, 4.5, 11.0) if hw > 12 else (-4.5, 4.5)
            for along_z in (True, False):
                for off in offs:
                    lat = L + off
                    if abs(L) < 1:     # detour around the plaza on a ring road
                        Rr = 36.0 + abs(off)
                        lat = np.sign(off) * smax(np.full(len(t), abs(off)), np.sqrt(np.maximum(Rr ** 2 - t ** 2, 0)))
                    else:
                        lat = np.full(len(t), lat)
                    pts = (np.column_stack([lat, np.zeros(len(t)), t]) if along_z
                           else np.column_stack([t, np.zeros(len(t)), lat]))
                    if off > 0:
                        pts = pts[::-1]
                    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
                    cum = np.concatenate([[0], np.cumsum(seg)])
                    spacing = (28, 70) if hw > 12 else (55, 160)
                    s0 = np.cumsum(rng.uniform(*spacing, 40))
                    s0 = s0[s0 < cum[-1]] + rng.uniform(0, 30)
                    v = rng.uniform(10, 15) * rng.uniform(0.9, 1.1, len(s0))
                    self.lanes.append((pts, cum, s0, v))
        self.n_cars = sum(len(l[2]) for l in self.lanes)
        self.n = self.n_cars * len(self.tpl[0])
        self.h = rng.random(self.n)

    def at(self, tau):
        P, Sg, Kd, V = self.tpl
        cps, tans = [], []
        for pts, cum, s0, v in self.lanes:
            s = np.mod(s0 + v * tau, cum[-1])
            p = np.column_stack([np.interp(s, cum, pts[:, i]) for i in range(3)])
            q = np.column_stack([np.interp(s + 1.5, cum, pts[:, i]) for i in range(3)])
            d = q - p
            d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
            cps.append(p); tans.append(d)
        c = np.vstack(cps)
        f = np.vstack(tans)
        rgt = np.column_stack([f[:, 2], np.zeros(len(f)), -f[:, 0]])   # up × fwd... right-handed x
        ax = np.stack([rgt, np.broadcast_to(EY, rgt.shape), f], 1)    # (cars, 3 axes, 3)
        pos = c[:, None, :] + np.einsum("tk,cki->cti", P, ax)
        cov = np.einsum("tk,cki,ckj->ctij", Sg ** 2, ax, ax)
        n = self.n
        pos = pos.reshape(n, 3)
        cov = cov.reshape(n, 3, 3)[:, [0, 0, 0, 1, 1, 2], [0, 1, 2, 1, 2, 2]]
        kind = np.tile(Kd, self.n_cars)
        var = np.tile(V, self.n_cars)
        alpha = np.where(kind == K["BEAM"], 0.22, 0.9) * edge_fade(np.hypot(pos[:, 0], pos[:, 2]))
        return dict(pos=pos, cov=cov, alpha=alpha, kind=kind, var=var, normal=np.zeros((n, 3)), shk=np.zeros(n),
                    group=np.full(n, G_CAR), lit=np.zeros(n), h=self.h)


if __name__ == "__main__":
    import time
    t0 = time.time()
    A = build()
    T = Traffic()
    print(f"built in {time.time() - t0:.1f}s: {len(A['alpha']):,} static splats, {T.n:,} car splats "
          f"({T.n_cars} cars), {A['meta']}")
    for k in KINDS:
        c = int((A["kind"] == K[k]).sum())
        if c:
            print(f"  {k:<9} {c:>9,}")
    # Σ must be symmetric positive-definite for every splat
    c = A["cov"]
    M = np.stack([np.stack([c[:, 0], c[:, 1], c[:, 2]], -1), np.stack([c[:, 1], c[:, 3], c[:, 4]], -1),
                  np.stack([c[:, 2], c[:, 4], c[:, 5]], -1)], 1)
    ev = np.linalg.eigvalsh(M)
    assert ev.min() > 0, ev.min()
    cars = T.at(3.0)
    assert np.isfinite(cars["pos"]).all()
    print(f"min eigenvalue {ev.min():.2e} m², max σ {np.sqrt(ev.max()):.2f} m. OK")
