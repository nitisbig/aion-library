"""Seeded cumulonimbus built from millions of droplet particles.

The cloud is a hierarchy of blobs (tower → column → turret → sub-turret), the cauliflower fractal of a
convective cloud. Every particle belongs to one blob and stores its offset in that blob's frame, so the
whole cloud billows by animating only a few thousand blob transforms per frame (`blob_state`):
towers rise, turrets swell and roll outward (the overturning of a convective thermal).

    uv run python lab/2026-11-04-storm-cloud/cloud.py      # build + stats
"""

from __future__ import annotations

import numpy as np

SEED = 7
# world box of the density volume (units ~ km): x, y, z
BOX_MIN = np.array([-14.0, -4.0, -9.0])
BOX_MAX = np.array([14.0, 13.0, 9.0])
VOXEL = 0.125
GRID = np.round((BOX_MAX - BOX_MIN) / VOXEL).astype(int)          # 224 × 136 × 144
BASE_Y = 2.0                                                        # flat cloud base
RHO = 2600.0                                                        # particles per unit³ in a solid blob
KIND_CLOUD, KIND_HAZE, KIND_RAIN = 0, 1, 2
RAIN = dict(x=(1.6, 5.8), z=(-2.2, 1.8), top=BASE_Y + 0.2, bottom=-4.0)


class Blobs:
    def __init__(self):
        self.parent, self.rel, self.r, self.ell, self.level = [], [], [], [], []
        self.grow, self.axis, self.omega, self.vel, self.surface = [], [], [], [], []

    def add(self, parent, rel, r, ell=(1, 1, 1), level=0, grow=0.0, axis=(1, 0, 0), omega=0.0,
            vel=(0, 0, 0), surface=True):
        self.parent.append(parent); self.rel.append(rel); self.r.append(r); self.ell.append(ell)
        self.level.append(level); self.grow.append(grow); self.axis.append(axis); self.omega.append(omega)
        self.vel.append(vel); self.surface.append(surface)
        return len(self.r) - 1

    def arrays(self):
        return {k: np.asarray(v, dtype=np.float64 if k not in ("parent", "level", "surface") else None)
                for k, v in vars(self).items()}


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _dirs(rng, n, up_bias):
    """Random directions on the sphere, biased upward/outward (turrets don't grow out of the base)."""
    d = _unit(rng.normal(size=(n, 3)))
    d[:, 1] = np.abs(d[:, 1]) * (1 - up_bias) + up_bias * (0.3 + 0.7 * rng.random(n))
    d[:, 1] -= 0.25 * (1 - up_bias)
    return _unit(d)


def _roll_axis(world_dir):
    """Horizontal axis ⟂ to the outward direction: rotating about it rolls the top outward and down."""
    a = np.cross([0.0, 1.0, 0.0], world_dir)
    n = np.linalg.norm(a)
    return a / n if n > 1e-6 else np.array([1.0, 0.0, 0.0])


def _turrets(B, rng, parent, center, r, levels, ell=(1, 1, 1), up_bias=0.35, k=(13, 6)):
    """Recursive cauliflower: children on the parent's surface."""
    if levels == 0:
        return
    n = k[0]
    dirs = _dirs(rng, n, up_bias)
    for d in dirs:
        frac = rng.uniform(0.34, 0.52) if levels == 2 else rng.uniform(0.32, 0.5)
        dist = rng.uniform(0.62, 0.82) * r
        rel = d * dist * np.array(ell)
        world = center + rel
        if world[1] - frac * r * ell[1] < BASE_Y - 0.15:          # keep the base flat
            continue
        cr = frac * r
        ax = _roll_axis(_unit(rel))
        idx = B.add(parent, rel, cr, ell, level=B.level[parent] + 1, grow=rng.uniform(0.002, 0.008),
                    axis=ax, omega=rng.uniform(0.004, 0.012), surface=True)
        _turrets(B, rng, idx, world, cr, levels - 1, ell, up_bias, (k[1], k[1]))


def _tower(B, rng, x, z, top, R, lean):
    """A convective tower: a column of blobs from the base to `top`, each covered in turrets."""
    root = B.add(-1, np.array([x, BASE_Y, z]), R, level=0, vel=(0.004, 0.006, 0.0), surface=False)
    n = int(np.ceil((top - BASE_Y - R * 0.4) / (0.75 * R))) + 1
    for i in range(n):
        s = i / max(n - 1, 1)
        y = R * 0.55 + s * (top - BASE_Y - R * 0.95)
        rc = R * (1.0 - 0.22 * s) * rng.uniform(0.92, 1.05)
        rel = np.array([lean * y + rng.normal(0, 0.12) * R, y, rng.normal(0, 0.12) * R])
        col = B.add(root, rel, rc, level=1, grow=0.002, axis=(1, 0, 0), omega=0.0, surface=False)
        _turrets(B, rng, col, np.array([x, BASE_Y, z]) + rel, rc, 2, up_bias=0.2 + 0.4 * s)


def _finish(B):
    A = B.arrays()
    A["parent"] = np.asarray(A["parent"], int)
    A["level"] = np.asarray(A["level"], int)
    A["surface"] = np.asarray(A["surface"], bool)
    return A


# the dusk "massif": a long squall line of towers on a thick shared base, with a continuous anvil
MASSIF_BOX = (np.array([-44.0, -4.0, -16.0]), np.array([44.0, 17.5, 11.0]), 0.2)
MASSIF_PEAKS = [(-15.0, 7.0), (13.0, 6.0)]        # x, width of the two giant cells


def _env(x):
    """Skyline envelope: two giant cells rising out of a lower, lumpy line."""
    return sum(np.exp(-((x - c) / w) ** 2) for c, w in MASSIF_PEAKS)


def build_massif(seed=SEED):
    rng = np.random.default_rng(seed + 100)
    B = Blobs()
    xs = np.linspace(-37, 37, 19) + rng.normal(0, 1.0, 19)
    tops = []
    for x in xs:                                                     # main line: varied skyline
        top = BASE_Y + 3.0 + 8.6 * _env(x) + rng.uniform(0.0, 2.6)
        R = 1.8 + 0.2 * (top - BASE_Y)
        _tower(B, rng, x, rng.normal(0, 1.4), top, R, rng.normal(0, 0.05))
        tops.append(top)
    for x in np.linspace(-34, 34, 10) + rng.normal(0, 2, 10):        # back row: depth
        top = BASE_Y + 3.5 + 6.0 * _env(x) + rng.uniform(0.0, 2.0)
        _tower(B, rng, x, rng.uniform(-10, -6.5), top, 1.8 + 0.16 * (top - BASE_Y), 0.0)
    for x in np.linspace(-39, 39, 15) + rng.normal(0, 1.5, 15):      # foothills: low cumulus in front
        top = BASE_Y + rng.uniform(1.6, 3.6)
        _tower(B, rng, x, rng.uniform(3.8, 6.4), top, rng.uniform(1.2, 1.8), 0.0)
    for x in np.arange(-41, 42, 3.2):                                # thick shared base
        for z in (-7.0, -3.0, 1.0):
            r = rng.uniform(2.0, 2.6)
            ell = (1.3, 0.5, 1.1)
            c = np.array([x + rng.normal(0, 0.6), BASE_Y + r * ell[1] * 0.85, z + rng.normal(0, 0.6)])
            sh = B.add(-1, c, r, ell, level=1, vel=(0.004, 0.0, 0.0), surface=False)
            _turrets(B, rng, sh, c, r, 1, ell=ell, up_bias=0.5, k=(8, 0))
    for (cx, cw), ht in zip(MASSIF_PEAKS, (14.6, 13.8)):              # an anvil on each giant cell
        for i in range(44):
            u = rng.uniform(-1, 1)
            x = cx + u * cw * 1.6 + 2.5                              # sheared downwind (+x)
            fall = abs(u) ** 1.5
            y = ht - 1.4 * fall + rng.normal(0, 0.45)                    # thick, sagging toward the edges
            r = rng.uniform(1.8, 2.8) * (1 - 0.3 * fall)
            ell = (1.4, rng.uniform(0.5, 0.68), 1.3)
            c = np.array([x, y, rng.normal(-1.0, 2.0 + 1.5 * abs(u))])
            a = B.add(-1, c, r, ell, level=1, vel=(0.012, 0.0, -0.004), surface=False)
            _turrets(B, rng, a, c, r, 2, ell=ell, up_bias=0.45, k=(8, 4))
    for i in np.argsort(tops)[-2:]:                                  # overshooting tops
        c = np.array([xs[i], tops[i] + 1.0, 0.0])
        ot = B.add(-1, c, 1.6, level=1, vel=(0.004, 0.006, 0.0), grow=0.003, surface=False)
        _turrets(B, rng, ot, c, 1.6, 2, up_bias=0.6)
    return _finish(B)


def build_blobs(seed=SEED):
    rng = np.random.default_rng(seed)
    B = Blobs()
    towers = [  # x, z, top, radius, lean-x
        (0.0, 0.0, 9.0, 2.6, 0.05), (1.6, -3.4, 8.0, 2.0, 0.08), (-4.8, 1.2, 6.2, 1.9, -0.03),
        (4.4, -0.8, 7.2, 2.0, 0.06), (-8.4, -1.4, 4.6, 1.45, 0.0), (7.8, 1.0, 5.0, 1.35, 0.04),
        (-2.4, -2.6, 7.0, 1.8, 0.0),
    ]
    for x, z, top, R, lean in towers:
        _tower(B, rng, x, z, top, R, lean)
    # base shelf joining the towers: flattened blobs
    for x in np.linspace(-10.0, 9.0, 15):
        z = rng.uniform(-3.0, 1.5)
        r = rng.uniform(1.5, 2.0)
        ell = (1.25, 0.42, 1.0)
        c = np.array([x, BASE_Y + r * ell[1] * 0.9, z])
        sh = B.add(-1, c, r, ell, level=1, vel=(0.004, 0.0, 0.0), surface=False)
        _turrets(B, rng, sh, c, r, 1, ell=ell, up_bias=0.5, k=(9, 0))
    # anvil: thick, ragged, spreading downwind (+x) from the main updraft, widening as it goes
    for i in range(40):
        u = (i + rng.random()) / 40
        x = -3.5 + 19.0 * u ** 0.85
        spread = 1.2 + 0.28 * (x + 3.5)
        z = rng.normal(0, 0.45) * spread
        y = 9.55 + 0.35 * np.tanh(x / 3) - 0.04 * max(0, x - 8) ** 1.3 + rng.normal(0, 0.18)
        r = rng.uniform(1.5, 2.3) * (1 - 0.35 * max(0, x - 8) / 8)
        ell = (1.55, rng.uniform(0.36, 0.5), 1.3)
        c = np.array([x, y, z])
        a = B.add(-1, c, r, ell, level=1, vel=(0.018, 0.0, 0.0), surface=False)
        _turrets(B, rng, a, c, r, 2, ell=ell, up_bias=0.45, k=(8, 4))
    # overshooting top above the main updraft
    c = np.array([0.3, 10.15, -0.3])
    ot = B.add(-1, c, 1.35, level=1, vel=(0.004, 0.01, 0.0), grow=0.004, surface=False)
    _turrets(B, rng, ot, c, 1.35, 2, up_bias=0.6)
    A = B.arrays()
    A["parent"] = np.asarray(A["parent"], int)
    A["level"] = np.asarray(A["level"], int)
    A["surface"] = np.asarray(A["surface"], bool)
    return A


def _qaxis(axis, ang):
    h = 0.5 * ang[:, None]
    return np.concatenate([axis * np.sin(h), np.cos(h)], axis=1)


def _qmul(a, b):
    ax, ay, az, aw = a.T
    bx, by, bz, bw = b.T
    return np.stack([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz], axis=1)


def _qrot(q, v):
    u, w = q[:, :3], q[:, 3:4]
    return v + 2.0 * np.cross(u, np.cross(u, v) + w * v)


def blob_state(A, tb):
    """Per-blob (centre, scale, quaternion) at billow time tb → float32 (N, 8) for the SSBO."""
    n = len(A["r"])
    C = np.zeros((n, 3)); S = np.ones(n); Q = np.zeros((n, 4)); Q[:, 3] = 1
    own_q = _qaxis(A["axis"], A["omega"] * tb)
    own_s = 1.0 + A["grow"] * tb
    for lvl in range(A["level"].max() + 1):
        m = A["level"] == lvl
        par = A["parent"][m]
        roots = par < 0
        idx = np.nonzero(m)[0]
        ri, ci = idx[roots], idx[~roots]
        C[ri] = A["rel"][ri] + A["vel"][ri] * tb
        S[ri] = own_s[ri]
        Q[ri] = own_q[ri]
        p = A["parent"][ci]
        C[ci] = C[p] + _qrot(Q[p], A["rel"][ci] * S[p][:, None])
        S[ci] = S[p] * own_s[ci]
        Q[ci] = _qmul(Q[p], own_q[ci])
    return np.c_[C, S, Q].astype("f4")


def build(seed=SEED, rho=RHO, rain=True, haze=220_000, free=90_000, layout="single"):
    A = build_massif(seed) if layout == "massif" else build_blobs(seed)
    bmin, bmax, vox = MASSIF_BOX if layout == "massif" else (BOX_MIN, BOX_MAX, VOXEL)
    rng = np.random.default_rng(seed + 1)
    r, ell = A["r"], A["ell"]
    vol = 4 / 3 * np.pi * r ** 3 * ell.prod(axis=1)
    surf = A["surface"]
    # interior blobs carry fewer, heavier particles (they are never seen directly)
    heavy = np.where(surf, 1.0, 4.0)
    cnt = np.maximum(8, np.round(vol * rho / heavy)).astype(int)
    bid = np.repeat(np.arange(len(r)), cnt).astype(np.int32)
    m = len(bid)
    if layout == "massif":       # ~12M particles on a 3.8 GB machine: sample in float32
        d = rng.standard_normal((m, 3), dtype=np.float32)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        d *= ((rng.random(m, dtype=np.float32) ** np.float32(1 / 3)) * r[bid].astype(np.float32))[:, None]
        d *= ell[bid].astype(np.float32)
        off = d
    else:
        d = _unit(rng.normal(size=(m, 3)))
        rad = rng.random(m) ** (1 / 3)
        off = d * (rad * r[bid])[:, None] * ell[bid]
    w = heavy[bid].astype(np.float32)
    # reject particles below the base (blob frames are unrotated at tb = 0, so world = centre + off)
    st = blob_state(A, 0.0)
    keep = (st[bid, 1] + off[:, 1]) > BASE_Y - 0.1 + 0.08 * rng.random(m)
    bid, off, w = bid[keep], off[keep], w[keep]
    kind = np.zeros(len(bid))
    # haze: sparse droplets in a loose shell around the surface turrets (bokeh near the lens)
    leaf = np.nonzero(surf & (A["level"] >= 3))[0]
    hb = rng.choice(leaf, haze)
    hd = _unit(rng.normal(size=(len(hb), 3)))
    hoff = hd * (r[hb] * rng.uniform(1.0, 2.6, len(hb)))[:, None]
    hw = st[hb, 1] + hoff[:, 1]
    hk = hw > BASE_Y - 0.4
    hb, hoff = hb[hk], hoff[hk]
    # rain shaft: falling particles under the base (attached to a static rain blob, kind 2)
    rain_blob = len(r)
    nr = 260_000 if rain else 0
    rx = rng.uniform(*RAIN["x"], nr); rz = rng.uniform(*RAIN["z"], nr)
    ry = rng.uniform(RAIN["bottom"], RAIN["top"], nr)
    roff = np.c_[rx, ry, rz]
    # free droplets drifting in the air along the close-up camera route (foreground bokeh); weight 0, so they
    # are drawn but don't add to the cloud volume
    nf = free
    foff = np.c_[rng.uniform(-11, 5, nf), rng.uniform(2.6, 7.8, nf), rng.uniform(1.0, 10.0, nf)]
    P_off = np.r_[off, hoff, roff, foff]
    P_bid = np.r_[bid, hb, np.full(nr, rain_blob), np.full(nf, rain_blob)]
    P_w = np.r_[w, np.full(len(hb), 0.06), np.full(nr, 0.0), np.full(nf, 0.0)]
    P_kind = np.r_[kind, np.full(len(hb), KIND_HAZE), np.full(nr, KIND_RAIN), np.full(nf, KIND_HAZE)]
    P_seed = rng.random(len(P_bid))
    parts = np.zeros((len(P_bid), 8), "f4")
    parts[:, :3], parts[:, 3] = P_off, P_w
    parts[:, 4], parts[:, 5], parts[:, 6] = P_bid, P_seed, P_kind
    parts[:, 7] = rng.random(len(P_bid)) ** 9                        # glint strength: a few droplets sparkle
    # density normalisation: count units per voxel inside a solid blob
    ref = rho * vox ** 3
    grid = np.round((bmax - bmin) / vox).astype(int)
    return dict(parts=parts, blobs=A, rain_blob=rain_blob, ref=ref, box_min=bmin, box_max=bmax, grid=grid)


def blob_buffer(A, tb):
    st = blob_state(A, tb)
    rain = np.array([[0, 0, 0, 1, 0, 0, 0, 1]], "f4")                 # identity blob for the rain particles
    return np.r_[st, rain]


def stats(C):
    p = C["parts"]
    k = p[:, 6].astype(int)
    print(f"blobs: {len(C['blobs']['r']):,}")
    print(f"particles: {len(p):,}  (cloud {np.sum(k == 0):,}, haze {np.sum(k == 1):,}, rain {np.sum(k == 2):,})")
    print(f"grid {GRID.tolist()} = {GRID.prod() / 1e6:.2f}M voxels, solid-blob count/voxel = {C['ref']:.1f}")


if __name__ == "__main__":
    import time
    t0 = time.time()
    C = build()
    stats(C)
    st = blob_buffer(C["blobs"], 30.0)
    assert np.allclose(np.linalg.norm(st[:, 4:], axis=1), 1, atol=1e-4), "quaternions must stay unit"
    print(f"built in {time.time() - t0:.1f}s")
