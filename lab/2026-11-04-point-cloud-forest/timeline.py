"""Camera path and every animated quantity as a function of t (seconds, 0–30)."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

import forest as F

DURATION = 30.0
EYE = 1.6


def ss(a, b, t):
    x = np.clip((t - a) / (b - a), 0.0, 1.0)
    return x * x * (3 - 2 * x)


def ground(x, z):
    # camera rides a smoothed ground (average of a few taps) so it doesn't jitter over pebbles
    o = 0.6
    return float(np.mean([F.terrain(x + dx, z + dz) for dx, dz in [(0, 0), (o, 0), (-o, 0), (0, o), (0, -o)]]))


def on_path(z, h, ahead=7.0, look_h=None):
    x = float(F.path_x(z))
    pos = (x, ground(x, z) + h, z)
    za = z - ahead
    xa = float(F.path_x(za))
    tgt = (xa, ground(xa, za) + (h if look_h is None else look_h), za)
    return pos, tgt


# ── sim time: slows to 15% for the break through the canopy (wind, fireflies, water) ──
_TT = np.linspace(0, DURATION, 3001)
_RATE = 1 - 0.85 * np.exp(-((_TT - 24.9) / 0.45) ** 2)
_TAU = np.concatenate([[0], np.cumsum((_RATE[1:] + _RATE[:-1]) / 2 * np.diff(_TT))])


def tau(t):
    return float(np.interp(t, _TT, _TAU))


def _keys():
    P, T, Fv = [], [], []

    def key(t, pos, tgt, fov):
        P.append((t, *pos)); T.append((t, *tgt)); Fv.append((t, fov))

    # 1: macro view of the forest floor, almost still
    for t in (0.0, 2.0, 4.2):
        z = 5.2 - 0.12 * t
        x = float(F.path_x(z))
        key(t, (x, ground(x, z) + 0.5 - 0.02 * t, z), (float(F.path_x(1.0)), ground(F.path_x(1.0), 1.0) + 0.02, 1.0), 56)
    # 2: rise to eye height while the scan sphere grows
    for t, z, h, lh, fov in [(5.6, 4.6, 0.75, 0.5, 57), (7.0, 4.0, 1.15, 2.5, 59), (8.2, 3.5, 1.5, 3.6, 60),
                             (9.0, 3.1, EYE, 3.2, 60)]:
        pos, _ = on_path(z, h)
        za = z - 12
        key(t, pos, (float(F.path_x(za)), ground(F.path_x(za), za) + lh, za), fov)
    # 3: the walk with a speed ramp (slow → fast → slow)
    for t, z in [(10.2, 1.4), (11.5, -1.6), (12.4, -6.0), (13.2, -12.5), (14.0, -20.0), (14.8, -26.0),
                 (15.8, -31.0), (17.0, -35.0)]:
        pos, tgt = on_path(z, EYE, 7.0, EYE - 0.1)
        key(t, pos, tgt, 62 if 12 < t < 15 else 60)
    # 4: into the clearing: crane up and arc round to look over the stream at the giant tree
    G = F.GIANT
    for t, pos, tgt, fov in [(18.2, (0.2, 2.1, -40.0), (0.5, 0.5, -55.0), 54),
                             (19.4, (-2.5, 3.0, -44.5), (0.5, 0.0, -58.5), 48),
                             (20.6, (-6.5, 4.0, -48.5), (1.0, 0.5, -62.0), 44),
                             (21.6, (-9.0, 4.8, -53.0), (G[0], 4.0, G[1]), 42)]:
        key(t, pos, tgt, fov)
    # 5: climb the giant tree in a rising spiral, near-freeze at the break-through (≈24.9 s)
    a0 = np.arctan2(-9.0 - G[0], -53.0 - G[1])
    for t in np.arange(22.2, 26.01, 0.3):
        u = (tau(t) - tau(22.0)) / (tau(26.0) - tau(22.0))
        e = u * u * (3 - 2 * u)
        r = 20 - 13.5 * ss(0, 0.55, u) + 3 * ss(0.75, 1.0, u)
        a = a0 + np.radians(110) * e
        y = 4.5 + 32.5 * e ** 1.5                 # canopy top (~33 m) is crossed near u ≈ 0.8 → the slow-mo
        pos = np.array([G[0] + r * np.sin(a), y, G[1] + r * np.cos(a)])
        out = np.array([np.sin(a), 0, np.cos(a)])
        side = np.array([np.cos(a), 0, -np.sin(a)])
        trunk = np.array([G[0], y + 3.0, G[1]])
        over = pos + 22 * (0.8 * out - 0.6 * side) + [0, -5.0, 0]    # look out across the canopy top
        k = ss(0.55, 0.9, u)
        key(t, pos, tuple(trunk * (1 - k) + over * k), 52 + 8 * ss(0.4, 0.8, u))
    # 6: rise above the canopy and pull back over the whole forest
    for t in np.arange(26.4, 30.01, 0.4):
        u = (t - 26.0) / 4.0
        e = 1 - (1 - u) ** 2.4
        last = np.array(P[-1][1:]) if t < 26.5 else None
        pos = np.array([G[0] + 6 - 4 * e, 40 + 55 * e, G[1] + 14 + 60 * e])
        if last is not None:
            pos = 0.5 * (pos + last)
        key(t, tuple(pos), (0.0, 8 - 6 * e, -60 + 8 * e), 58 - 6 * e)
    P, T, Fv = map(np.array, (P, T, Fv))
    return (PchipInterpolator(P[:, 0], P[:, 1:]), PchipInterpolator(T[:, 0], T[:, 1:]),
            PchipInterpolator(Fv[:, 0], Fv[:, 1]))


POS, TGT, FOV = _keys()


def shake(t, amp):
    w = np.array([0.0, 0.0, 0.0])
    for i, (f, ph) in enumerate([(0.31, 0.2), (0.53, 1.7), (0.87, 4.1), (1.31, 2.3)]):
        w += np.array([np.sin(2 * np.pi * f * t + ph), np.sin(2 * np.pi * f * 1.13 * t + ph * 1.9),
                       np.sin(2 * np.pi * f * 0.91 * t + ph * 2.7)]) / (i + 1)
    return w * amp


def camera(t):
    pos = POS(t) + shake(t, 0.035)
    tgt = TGT(t) + shake(t + 7.3, 0.05)
    fwd = tgt - pos
    fwd /= np.linalg.norm(fwd)
    # bank into the path's curves during the walk
    roll = 0.0
    if 9 < t < 17.5:
        z = float(POS(t)[2])
        curv = (F.path_x(z - 4) - 2 * F.path_x(z) + F.path_x(z + 4)) / 16
        roll = float(np.clip(-curv * 3.0 * speed(t), -0.06, 0.06))
    right = np.cross(fwd, [0, 1, 0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    right, up = right * np.cos(roll) + up * np.sin(roll), up * np.cos(roll) - right * np.sin(roll)
    return dict(pos=pos, fwd=fwd, right=right, up=up, fov=np.radians(float(FOV(t))))


def speed(t):
    return float(np.linalg.norm(POS(t + 0.02) - POS(t - 0.02)) / 0.04)


def events(t):
    c0 = POS(4.2)
    sR = 0.0 if t < 4.2 else 1.5 + 150 * ss(4.2, 9.6, t) ** 2.0
    v = speed(t)
    # focus (m) and aperture (m): shallow macro → infinity → walk → long lens → climb → aerial
    focus = float(np.interp(t, [0, 4.4, 6.0, 8.0, 9.5, 17, 18.5, 21.5, 22.5, 24.0, 25.5, 26.5, 30],
                               [2.6, 2.6, 4.0, 14, 7.0, 7.0, 14, 20, 12, 6.0, 5.0, 40, 95]))
    aper = float(np.interp(t, [0, 4.4, 8, 9.5, 17, 18.5, 22, 26, 27, 30],
                              [0.035, 0.035, 0.02, 0.03, 0.03, 0.04, 0.03, 0.03, 0.015, 0.012]))
    fog = float(np.interp(t, [0, 9, 17, 20, 22, 26, 28, 30], [22, 30, 30, 45, 40, 45, 120, 170]))
    return dict(
        tau=tau(t), t=t,
        line_o=np.array([c0[0], 0, c0[2]]), line_dir=np.array([0, 0, -1.0]),
        line_d=-0.5 + 8.0 * ss(0.5, 3.9, t),
        scan_c=c0, scan_r=sR,
        focus=focus, aper=aper, fog=fog,
        wind=0.7 + 0.5 * ss(13, 16, t) - 0.3 * ss(19, 21, t) + 1.0 * ss(26, 27.5, t),
        gust_t0=26.6,
        refl=1.0 if 16.5 < t < 26.0 else 0.0,
        zoom=float(np.clip((v - 5.5) / 4.0, 0, 1) * 0.022) * float(t < 18),
        ca=0.004 + 0.006 * float(np.clip((v - 5) / 4, 0, 1)) * float(t < 18),
        bloom=0.9 + 0.5 * float(np.exp(-((t - 6.5) / 1.6) ** 2)) + 0.4 * float(np.exp(-((t - 24.9) / 0.5) ** 2)),
        exposure=float(np.interp(t, [0, 4, 5, 22, 23.8, 25.8, 27, 30], [1.5, 1.5, 1.0, 1.0, 0.75, 0.5, 0.75, 0.85])),
        fade=float(ss(0.0, 0.6, t) * (1 - ss(29.2, 30.0, t))),
    )
