"""Dusk variant: a calm squall line of thunderstorm towers at sunset, seen from cruising altitude.

One continuous, stable glide (no handheld, no speed ramps) roughly perpendicular to the sun line, so the main
tower slides across the low sun: sun to the right of the tower → eclipse with light shafts (~15 s) → sun
reappears on the left. A few soft lightning pulses deep in the core are the storm's quiet heartbeat.
Same API as `timeline.py`, so `render.py` can drive either.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from timeline import ST2, ST3, curve, ss

DURATION = 30.0
SUN_DIR = np.array([0.62, 0.07, -0.78])            # low sun, side-back light from the right
SUN_DIR = SUN_DIR / np.linalg.norm(SUN_DIR)

# one long, stable glide along the squall line at cruising altitude, eased at both ends. The sun sits behind
# the wall, so towers slide across it one after another: rims flare, shafts fan out through the gaps.
_kt = np.array([0.0, 10.0, 20.0, 30.0])
_px = PchipInterpolator(_kt, [-26.0, -10.0, 7.0, 22.0])
_pz = PchipInterpolator(_kt, [48.0, 45.0, 42.5, 41.0])
_py = PchipInterpolator(_kt, [12.0, 12.5, 13.0, 13.6])
_fov = PchipInterpolator(_kt, [42.0, 40.0, 38.5, 40.0])


def camera(t):
    t = float(np.clip(t, 0, DURATION))
    pos = np.array([float(_px(t)), float(_py(t)), float(_pz(t))])
    tgt = np.array([pos[0] + 9.0, 6.4, -2.0])
    fwd = tgt - pos
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    r = np.radians(-1.0)                        # a gentle, constant bank: you're in a plane
    right, up = np.cos(r) * right + np.sin(r) * up, -np.sin(r) * right + np.cos(r) * up
    return dict(pos=pos, fwd=fwd, right=right, up=up, fov=np.radians(float(_fov(t))))


def cavity_path(n=16):
    return np.zeros((n, 3), "f4")


def billow(t):
    return 0.12 * float(t)                      # stable: barely-perceptible evolution


# soft pulses deep in the core: big radius so they glow through rather than spark
FLASHES = [   # deep inside towers along the line, roughly following the camera
    (3.2, (-22.0, 6.0, -0.6), (-21.4, 6.8, -0.8), 3.0, 1.0, ST3),
    (7.9, (-12.5, 7.4, -0.4), (-11.8, 8.2, -0.6), 3.2, 1.2, ST3),
    (11.6, (-4.0, 5.6, 0.0), (-3.4, 6.4, -0.2), 2.8, 0.8, ST2),
    (15.2, (3.5, 7.8, -0.8), (4.2, 8.6, -1.0), 3.2, 1.2, ST3),
    (19.4, (11.5, 6.8, -0.4), (12.2, 7.6, -0.6), 3.0, 1.1, ST3),
    (23.1, (17.0, 5.6, 0.2), (17.6, 6.4, 0.0), 2.8, 0.8, ST2),
    (26.6, (24.0, 6.4, -0.6), (24.6, 7.2, -0.8), 3.0, 1.0, ST3),
]
BOLT_T = {n: dict(I=0.0) for n in ("hero", "spider", "side")}
BOLT_ORDER = ["hero", "spider", "side"]


def bolt_state(name, t):
    return dict(grow=-1.0, leader=0.0, main=0.0, branch=0.0)


def lights(t, bolts):
    L = []
    for t0, a, b, r, I, st in FLASHES:
        v = I * curve(t, t0, st, decay=0.16) * 40.0
        if v > 1e-3:
            L.append((v, a, b, r))
    L.sort(key=lambda e: -e[0])
    A = np.zeros((4, 4), "f4"); B = np.zeros((4, 4), "f4")
    for i, (v, a, b, r) in enumerate(L[:4]):
        A[i, :3], A[i, 3] = a, r
        B[i, :3], B[i, 3] = b, v
    return A, B, sum(e[0] for e in L)


def events(t):
    return dict(
        tb=billow(t), fade=float(ss(0.0, 1.2, t) * (1 - ss(28.6, 30.0, t))),
        focus=45.0, aper=0.003,
        exposure=1.0, lift=0.0, ambient=1.0, zoom=0.0, ca=0.003, rays=0.4, bloom=1.0, cav=0.0, sun=True,
    )
