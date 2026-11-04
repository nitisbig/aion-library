"""Everything that changes with time: camera, billow clock, flashes, bolts, focus, grade."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

DURATION = 30.0


def ss(a, b, x):
    x = np.clip((x - a) / (b - a), 0.0, 1.0)
    return x * x * (3 - 2 * x)


# ── camera ──────────────────────────────────────────────────────────────────────
# t, position, look-at target, vertical fov (deg), roll (deg)
KEYS = [
    (0.0, (0.0, 4.4, 36.0), (0.4, 6.0, 0.0), 38, 0),
    (3.5, (-0.3, 4.4, 34.5), (0.3, 6.1, 0.0), 38, 0),
    (6.5, (-2.4, 4.7, 27.0), (-0.6, 6.4, 0.0), 40, -1),
    (9.0, (-6.0, 4.9, 17.5), (-3.0, 5.6, 0.0), 44, -2),
    (11.0, (-8.6, 4.7, 8.6), (-4.2, 5.1, 2.0), 50, -4),
    (13.0, (-4.4, 5.0, 7.4), (0.4, 5.5, 1.8), 50, -3),
    (15.0, (0.6, 5.4, 6.6), (2.4, 5.4, 1.2), 50, 2),
    (16.6, (2.2, 5.3, 3.4), (1.6, 5.6, -1.2), 54, 6),
    (18.2, (1.6, 5.0, 0.6), (0.2, 4.4, -3.0), 56, 10),
    (19.4, (1.3, 3.4, 0.2), (1.0, 0.0, 1.5), 58, 4),
    (20.4, (2.2, -0.3, 4.2), (-0.4, 1.0, -1.2), 52, 0),
    (21.2, (3.4, -1.6, 9.6), (-0.6, -2.4, -0.6), 48, 0),
    (23.6, (3.9, -1.5, 11.6), (-0.7, -2.6, -0.6), 48, 0),
    (25.5, (4.2, -1.3, 12.8), (-0.5, -2.2, -0.6), 48, 0),
    (28.2, (1.2, 2.8, 30.0), (0.4, 5.0, 0.0), 40, 0),
    (30.0, (0.9, 3.1, 33.0), (0.4, 5.4, 0.0), 39, 0),
]
_kt = np.array([k[0] for k in KEYS])
_pos = PchipInterpolator(_kt, np.array([k[1] for k in KEYS]))
_tgt = PchipInterpolator(_kt, np.array([k[2] for k in KEYS]))
_fov = PchipInterpolator(_kt, np.array([k[3] for k in KEYS], float))
_roll = PchipInterpolator(_kt, np.array([k[4] for k in KEYS], float))


def _drift(t, amp):
    return amp * np.array([np.sin(1.3 * t + 0.4) + 0.5 * np.sin(3.1 * t + 1.7),
                           np.sin(1.7 * t + 2.1) + 0.4 * np.sin(3.7 * t + 0.3),
                           np.sin(1.1 * t + 4.0)])


def camera(t):
    hand = 0.012 + 0.03 * ss(8.5, 10.0, t) * (1 - ss(19.5, 20.5, t)) + 0.012 * ss(20.0, 21.0, t) * (1 - ss(25, 26, t))
    pos = _pos(t) + _drift(t, hand)
    tgt = _tgt(t) + _drift(t + 7.3, hand * 2.5)
    fwd = tgt - pos
    fwd /= np.linalg.norm(fwd)
    r = np.radians(float(_roll(t)))
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    right, up = np.cos(r) * right + np.sin(r) * up, -np.sin(r) * right + np.cos(r) * up
    return dict(pos=pos, fwd=fwd, right=right, up=up, fov=np.radians(float(_fov(t))))


def cavity_path(n=16):
    """Centre line of the tunnel carved through the cloud for the inside shot (follows the camera)."""
    ts = np.linspace(14.6, 20.6, n)
    return np.array([_pos(t) for t in ts], "f4")


# ── billow clock: time-lapse, slowed to ~10 % for the stepped leader ─────────────
_tg = np.linspace(0, DURATION, 3001)
_rate = 1.0 - 0.9 * ss(20.3, 20.9, _tg) * (1 - ss(23.5, 23.75, _tg))
_tb = np.concatenate([[0], np.cumsum(0.5 * (_rate[1:] + _rate[:-1]) * np.diff(_tg))])
BILLOW = 1.6                         # billow-units per second (time-lapse)


def billow(t):
    return float(np.interp(t, _tg, _tb)) * BILLOW


# ── flashes ─────────────────────────────────────────────────────────────────────
def stroke(x, decay=0.11):
    """One return-stroke light curve: ~10 ms rise, exponential decay."""
    x = np.asarray(x, float)
    return np.where(x > 0, (1 - np.exp(-np.maximum(x, 0) / 0.012)) * np.exp(-np.maximum(x, 0) / decay), 0.0)


def curve(t, t0, strokes, decay=0.11):
    return float(sum(a * stroke(t - t0 - dt, decay) for dt, a in strokes))


ST3 = [(0, 1.0), (0.07, 0.55), (0.16, 0.8), (0.29, 0.35)]
ST2 = [(0, 1.0), (0.09, 0.6)]
ST1 = [(0, 1.0)]

# t0, segment a, segment b, light radius, intensity, strokes
FLASHES = [
    (0.9, (0.6, 6.4, -1.4), (0.4, 6.9, -1.0), 0.9, 0.5, ST1),
    (2.4, (-3.8, 4.6, 0.2), (-3.4, 5.2, 0.0), 0.9, 0.9, ST2),
    (3.9, (-6.8, 3.4, -0.9), (-6.0, 4.0, -0.6), 0.9, 2.0, ST3),
    (4.75, (-4.6, 4.6, 0.6), (-4.0, 5.4, 0.8), 0.9, 2.2, ST2),
    (5.6, (-1.2, 5.6, -0.4), (-0.6, 6.6, -0.6), 1.0, 3.2, ST3),
    (6.35, (0.6, 7.6, -1.0), (1.2, 8.2, -1.2), 1.0, 2.6, ST2),
    (8.2, (3.2, 9.5, -1.4), (4.6, 9.8, -1.6), 1.1, 3.0, ST3),
    (8.85, (6.2, 9.7, -0.6), (7.4, 9.9, -0.4), 1.1, 2.0, ST2),
    (9.35, (-9.0, 3.6, -0.6), (-8.4, 4.2, -0.4), 0.8, 1.2, ST2),
    (10.0, (-7.6, 4.0, 0.2), (-7.0, 4.6, 0.6), 0.8, 1.3, ST3),
    (10.9, (-4.6, 5.0, 1.0), (-4.0, 5.6, 1.4), 0.8, 1.2, ST2),
    (11.8, (-1.8, 6.0, -2.6), (-0.8, 6.6, -2.4), 0.9, 4.0, ST3),
    (12.9, (-1.0, 4.6, 1.2), (-0.4, 5.2, 1.6), 0.8, 1.3, ST2),
    (13.7, (2.4, 6.4, -1.8), (3.2, 6.9, -2.0), 0.9, 3.0, ST3),
    (14.6, (3.8, 5.0, 0.4), (4.4, 5.6, 0.8), 0.8, 1.3, ST2),
    (15.6, (3.6, 6.6, 0.6), (4.2, 7.0, 0.2), 0.7, 2.0, ST2),
    (16.4, (0.4, 6.9, 1.6), (0.0, 7.3, 1.0), 0.7, 2.2, ST3),
    (17.05, (3.0, 4.2, -1.2), (3.6, 4.6, -1.6), 0.7, 1.8, ST2),
    (19.0, (-0.2, 3.9, 1.2), (0.4, 4.3, 0.8), 0.7, 1.8, ST2),
    (19.65, (2.6, 2.9, -0.6), (3.2, 3.2, -1.0), 0.7, 1.6, ST1),
    (20.05, (1.0, 2.7, 0.6), (1.6, 3.1, 0.2), 0.7, 0.6, ST3),
    (20.75, (-0.8, 2.6, -0.4), (-0.2, 2.9, -0.6), 0.8, 1.2, ST2),
    (27.6, (4.6, 9.6, -1.2), (6.0, 9.9, -1.0), 1.1, 1.6, ST2),
    (28.7, (-2.0, 6.8, -1.0), (-1.4, 7.2, -1.2), 1.0, 0.7, ST1),
]

# bolt timing: leader growth window, return strokes, colour of the light it casts
BOLT_T = {
    "side": dict(grow=(6.95, 7.15), strokes=[(7.15, 1.0), (7.24, 0.5)], I=4.0, lead=0.25),
    "spider": dict(grow=(17.3, 17.85), strokes=[(17.85, 1.0), (18.0, 0.5), (18.32, 0.7)], I=40.0, lead=0.3),
    "hero": dict(grow=(20.9, 23.55), strokes=[(23.6, 1.0), (23.72, 0.45), (23.9, 0.6), (25.6, 0.7), (26.45, 0.45)],
                 I=30.0, lead=0.5),
}
BOLT_ORDER = ["hero", "spider", "side"]


def bolt_state(name, t):
    b = BOLT_T[name]
    g0, g1 = b["grow"]
    x = np.clip((t - g0) / (g1 - g0), 0, 1)
    grow = x ** 1.4 if t >= g0 else -1.0                      # the leader accelerates as it nears the target
    leader = b["lead"] * (1.0 if g0 <= t < g1 + 0.02 else 0.0) * (0.75 + 0.25 * np.sin(97 * t) ** 2)
    if t < g0:
        grow = -1.0
    ret = sum(a * float(stroke(t - s, 0.10 if name != "hero" else 0.13)) for s, a in b["strokes"])
    first = b["strokes"][0][0]
    branch = float(np.exp(-max(t - first, 0) / 0.2)) if t >= first else 0.0
    glow = 0.0 if (t < first or name != "hero") else float(np.exp(-(t - first) / 0.6)) * 0.12   # residual channel glow
    return dict(grow=float(grow), leader=float(leader), main=float(ret) + glow, branch=branch * (t >= first))


def lights(t, bolts):
    """Up to 4 brightest lights now: (a, b, radius, intensity) arrays."""
    L = []
    for t0, a, b, r, I, st in FLASHES:
        v = I * curve(t, t0, st) * 2.5 * 2.6 ** 2
        r = r * 1.7 * 2.6 / 1.7
        if v > 1e-3:
            L.append((v, a, b, r))
    for name in BOLT_ORDER:
        s = bolt_state(name, t)
        main = bolts[name]["main"]
        if s["grow"] >= 0:
            n = len(main)
            if s["main"] > 1e-3:
                k = n - 1 if name != "hero" else int(0.55 * n)       # hero: light the base from the upper channel
                L.append((BOLT_T[name]["I"] * s["main"], tuple(main[0]), tuple(main[k]), 0.8))
            if s["leader"] > 0:
                tip = main[min(int(s["grow"] * (n - 1)), n - 1)]
                L.append((BOLT_T[name]["I"] * 0.05 * s["leader"], tuple(main[0]), tuple(tip), 0.6))
    L.sort(key=lambda e: -e[0])
    L = L[:4]
    A = np.zeros((4, 4), "f4"); Bv = np.zeros((4, 4), "f4")
    for i, (v, a, b, r) in enumerate(L):
        A[i, :3], A[i, 3] = a, r
        Bv[i, :3], Bv[i, 3] = b, v
    total = sum(e[0] for e in L)
    return A, Bv, total


def events(t):
    fade = ss(0.0, 0.4, t) * (1 - ss(29.0, 30.0, t))
    # return-stroke flash frame: exposure kick + white lift
    hero = bolt_state("hero", t)
    kick = 0.6 * float(stroke(t - 23.6, 0.05)) + 0.25 * float(stroke(t - 25.6, 0.04))
    focus = float(np.interp(t, [0, 9, 10.5, 12, 15, 16.5, 19.5, 20.6, 21.5, 25.5, 28, 30],
                            [34, 22, 5.0, 3.6, 3.6, 2.4, 2.0, 4.0, 11.5, 12.5, 29, 32]))
    aper = float(np.interp(t, [0, 9, 10.5, 15, 19.5, 20.5, 25.5, 28], [0.02, 0.02, 0.05, 0.05, 0.04, 0.03, 0.03, 0.02]))
    return dict(
        tb=billow(t), fade=float(fade), focus=focus, aper=aper,
        exposure=1.0 + 0.9 * kick, lift=0.10 * kick,
        ambient=0.003 * ss(3.0, 6.0, t) * (1 - ss(27.5, 29.5, t)) + 0.0004,
        zoom=0.035 * ss(19.8, 20.4, t) * (1 - ss(20.8, 21.4, t)),
        ca=0.004 + 0.006 * ss(9.5, 11, t) * (1 - ss(19.5, 21, t)) + 0.01 * kick,
        rays=0.3 * (1 - ss(19.8, 20.3, t) * (1 - ss(26.8, 27.4, t))), bloom=1.0, hero=hero,
    )
