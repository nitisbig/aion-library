"""Everything as a function of t (seconds): two worlds, their cameras, and the story events.

World "cell" is in µm (raymarched), world "mol" is in nm (instanced spheres). The hand-offs between them happen
inside a zoom blur + bloom flash while the camera is moving fast.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

import anatomy as AN

DURATION = 45.0


def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def sss(a, b, x):                       # smootherstep
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * t * (t * (6 * t - 15) + 10)


def bump(c, w, x):
    return float(np.exp(-((x - c) / w) ** 2))


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def yawpitch(yaw, pitch):
    y, p = np.deg2rad(yaw), np.deg2rad(pitch)
    return np.array([np.sin(y) * np.cos(p), np.sin(p), np.cos(y) * np.cos(p)])


class Keys:
    """PCHIP through keyed rows: t, target(3), dir(3), log dist, fov, focus multiplier."""

    def __init__(self, rows):
        rows = np.array(rows, float)
        self.t = rows[:, 0]
        self.f = PchipInterpolator(self.t, rows[:, 1:], axis=0, extrapolate=False)

    def __call__(self, t):
        t = float(np.clip(t, self.t[0], self.t[-1]))
        return self.f(t)


# ── cell world (µm) ──────────────────────────────────────────────────────────
PORE_P, PORE_N = AN.hero_pore()
_m = AN.LAYOUT["mito"]
_mc = (_m[:, :3] + _m[:, 4:7]) / 2
_v10 = yawpitch(100, 8)
MITO_HERO = int(np.argmax(_mc @ _v10 - 0.15 * np.linalg.norm(_mc, axis=1)))    # a mitochondrion facing the 10 s camera
MITO_C = _mc[MITO_HERO]


def _row(t, tgt, d, dist, fov, fm=1.0):
    return [t, *tgt, *unit(d), np.log(dist), fov, fm]


Z3 = np.zeros(3)
_pn = PORE_N
_pt = unit(np.cross(_pn, [0, 1, 0]))
CELL_KEYS = Keys([
    _row(0.0, Z3, yawpitch(-10, 12), 72, 30, 0.55),
    _row(2.0, Z3, yawpitch(-4, 12), 58, 30, 0.62),
    _row(4.0, Z3, yawpitch(5, 14), 44, 31, 1.0),
    _row(6.5, Z3, yawpitch(40, 10), 36, 32, 1.0),
    _row(8.5, MITO_C * 0.55, yawpitch(78, 6), 22, 34, 1.0),
    _row(10.2, MITO_C, yawpitch(96, 4), 5.2, 38, 1.0),
    _row(11.6, MITO_C * 0.6 + PORE_P * 0.4, unit(yawpitch(110, 6) * 0.6 + _pn * 0.4), 10, 38, 1.0),
    _row(13.0, PORE_P + _pn * 1.5, unit(_pn * 0.8 + _pt * 0.6 + [0, 0.15, 0]), 8.0, 38, 1.0),
    _row(14.8, PORE_P + _pn * 0.2, unit(_pn * 0.95 + _pt * 0.3), 2.0, 40, 1.0),
    _row(16.2, PORE_P, unit(_pn + _pt * 0.08), 0.42, 42, 1.0),
    _row(17.1, PORE_P - _pn * 0.08, _pn, 0.17, 44, 1.0),
    _row(17.8, PORE_P - _pn * 0.4, _pn, 0.2, 46, 1.0),
    _row(18.9, PORE_P - _pn * 1.2, _pn, 0.18, 48, 1.0),
    # (the molecular world plays 18.9 → 41.6)
    _row(41.6, PORE_P - _pn * 0.75, _pn, 0.15, 48, 1.0),
    _row(42.3, PORE_P - _pn * 0.3, _pn, 0.35, 44, 1.0),
    _row(43.0, PORE_P - _pn * 0.1, unit(_pn + _pt * 0.2), 3.0, 38, 1.0),
    _row(43.8, PORE_P * 0.4, unit(_pn * 0.6 + yawpitch(150, 10)), 22, 32, 1.0),
    _row(45.0, Z3, yawpitch(170, 14), 66, 30, 1.0),
])


def camera_cell(t):
    k = CELL_KEYS(t)
    tgt, d, dist, fov, fm = k[:3], unit(k[3:6]), float(np.exp(k[6])), float(k[7]), float(k[8])
    return look(tgt + d * dist, tgt, fov, dist * fm)


def look(pos, tgt, fov, focus, up=(0, 1, 0)):
    fwd = unit(tgt - pos)
    right = unit(np.cross(fwd, up))
    upv = np.cross(right, fwd)
    return dict(pos=pos, fwd=fwd, right=right, up=upv, fov=np.deg2rad(fov), focus=focus)


# ── molecular world (nm) ─────────────────────────────────────────────────────
# directions are given in the hero basis (T0, N0, B0) of the straightened DNA
_MOL_ROWS = [
    [18.0, 0, 0, 0, 0.30, 0.60, 0.74, np.log(300), 44, 1.0],
    [21.2, 0, 0, 0, 0.10, 0.80, 0.60, np.log(130), 42, 1.0],
    [24.6, "face", np.log(30), 40, 1.0],
    [26.2, "orbit", np.log(25), 40, 1.0],
    [27.6, 0, 0, 0, -0.65, 0.50, 0.58, np.log(26), 40, 1.0],
    [29.3, 0, 0, 0, -0.50, 0.75, 0.40, np.log(19), 40, 1.0],
    [31.0, 0, 0, 0, -0.65, 0.60, 0.45, np.log(12), 40, 1.0],
    [32.9, 0, 0, 0, -0.55, 0.70, 0.45, np.log(8.5), 40, 1.0],
    [34.5, 0, 0, 0, -0.40, 0.80, 0.43, np.log(8.5), 40, 1.0],
    [37.0, 0, 0, 0, 0.00, 0.92, 0.39, np.log(10.5), 40, 1.0],
    [39.6, 0, 0, 0, 0.12, 0.90, 0.42, np.log(11.5), 40, 1.0],
    [41.0, 0, 0, 0, 0.30, 0.70, 0.65, np.log(80), 42, 1.0],
    [42.4, 0, 0, 0, 0.35, 0.60, 0.72, np.log(300), 44, 1.0],
]
MOL_KEYS = None


def set_nucleosome_axis(nax):
    """Face-on / orbit views of the hero nucleosome, given its superhelix axis in the hero basis."""
    global MOL_KEYS
    nax = unit(nax)
    if nax @ unit([0.1, 0.8, 0.6]) < 0:          # look at the face that points toward the approach
        nax = -nax
    side = unit(np.cross(nax, [1.0, 0, 0]))
    rows = []
    for r in _MOL_ROWS:
        if r[1] == "face":
            d = unit(nax * 0.92 + side * 0.4)
            rows.append([r[0], 0, 0, 0, *d, *r[2:]])
        elif r[1] == "orbit":
            d = unit(nax * 0.55 + side * 0.6 + unit(np.cross(nax, side)) * 0.45)
            rows.append([r[0], 0, 0, 0, *d, *r[2:]])
        else:
            rows.append(r)
    MOL_KEYS = Keys(rows)


# target sources by time: (t0, t1, name), blended over BLEND seconds at the joins
MOL_TARGETS = [(18.0, 24.2, "fibre"), (24.2, 27.4, "histone"), (27.4, 30.8, "peel"),
               (30.8, 34.4, "glide"), (34.4, 39.6, "fork"), (39.6, 42.4, "histone")]
BLEND = 0.9


def mol_weights(t):
    ws = []
    for i, (a, b, _) in enumerate(MOL_TARGETS):
        lo = ss(a - BLEND / 2, a + BLEND / 2, t) if i > 0 else 1.0
        hi = 1 - ss(b - BLEND / 2, b + BLEND / 2, t) if i < len(MOL_TARGETS) - 1 else 1.0
        ws.append(lo * hi)
    ws = np.array(ws)
    return ws / max(ws.sum(), 1e-9)


# ── story events ─────────────────────────────────────────────────────────────
def events(t):
    e = {}
    e["fade"] = float(ss(0.0, 1.6, t) * (1 - ss(44.0, 45.0, t)))
    e["w_mol"] = float(ss(18.15, 18.85, t) * (1 - ss(41.55, 42.25, t)))
    e["w_cell"] = 1.0 - e["w_mol"]
    e["zoom"] = float(0.05 * ss(15.0, 16.5, t) * (1 - ss(17.0, 17.5, t)) + 0.32 * bump(18.5, 0.45, t)
                      + 0.28 * bump(41.9, 0.5, t) + 0.12 * bump(40.8, 0.6, t))
    e["flash"] = float(0.9 * bump(18.5, 0.22, t) + 0.7 * bump(41.9, 0.25, t))
    e["fibre"] = float((1 - ss(25.2, 28.6, t)) + ss(40.0, 41.3, t))
    e["unwrap"] = float(sss(27.2, 30.8, t) * (1 - sss(39.9, 41.2, t)))
    e["unzip"] = float(sss(34.6, 38.6, t) * (1 - sss(39.4, 40.3, t)))
    e["dof"] = 1.0
    e["ca"] = float(0.0025 + 0.004 * e["zoom"] / 0.3)
    return e


def molecular_target(t, src):
    """src(name) → point; blended."""
    w = mol_weights(t)
    p = np.zeros(3)
    for wi, (_, _, name) in zip(w, MOL_TARGETS):
        if wi > 1e-6:
            p = p + wi * src(name)
    return p


def camera_mol(t, target, basis):
    k = MOL_KEYS(t)
    d = unit(basis @ unit(k[3:6]))
    dist, fov, fm = float(np.exp(k[6])), float(k[7]), float(k[8])
    up = basis[:, 1]
    return look(target + d * dist, target, fov, dist * fm, up=tuple(up))
