"""Chapter 3's orbital clouds as one additive raster (c03_s03), shared so c04_s01 can open on their last frame.

Example:
    from atoms import frames; img = frames()(328.0)
"""
import math

import numpy as np
from aion import C

import ch3
from beats import T
from kit import XW, YH, mix, smooth01

PPU = 100
NX, NY = int(2 * XW * PPU), int(2 * YH * PPU)
CY = 0.35                                        # the row of clouds
SC = {"1s": 0.62, "2p": 0.2, "3d": 0.105}        # screen units per Bohr radius
TILT = {"1s": 0.0, "2p": 0.55, "3d": 0.4}        # each lobe axis leans this far from vertical (rad)
EL = math.radians(20)                            # the view looks down this much
SPIN = 0.25                                      # rad/s about the vertical
B_SC = 0.7                                       # the H₂ pair, units per Bohr radius
N1 = 15000                                       # points per 1s atom


def _rot(P, spin, tilt):
    """Lean the lobe axis (z) by `tilt` about y, spin about the vertical, tip toward the viewer by EL → (x, y_up)."""
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    ct, st = math.cos(tilt), math.sin(tilt)
    x, z = x * ct + z * st, -x * st + z * ct
    cs, ss = math.cos(spin), math.sin(spin)
    x, y = x * cs - y * ss, x * ss + y * cs
    ce, se = math.cos(EL), math.sin(EL)
    return x, z * ce + y * se


def _setup():
    p1 = ch3.orbital_points("1s")[0][:2 * N1]
    bond = ch3.bond_points()[:, [2, 1, 0]]           # the bond axis along screen x
    side = bond[:, 0] > 0
    a_t, b_t = bond[side], bond[~side]
    a_s, b_s = p1[:len(a_t)], p1[len(a_t):len(a_t) + len(b_t)]

    def order(P):                                # pair source and target points by direction in the view plane
        return np.argsort(np.arctan2(P[:, 0], P[:, 2]))
    tgt = np.concatenate([a_t[order(a_t - [0.7, 0, 0])], b_t[order(b_t + [0.7, 0, 0])]])
    src = np.concatenate([a_s[order(a_s)], b_s[order(b_s)]])
    na = len(a_t)
    rng = np.random.default_rng(1926)
    vort = [(rng.uniform(-1.3, 1.3), CY + rng.uniform(-0.8, 0.8), sg * rng.uniform(0.7, 1.0), rng.uniform(0.6, 0.9))
            for sg in (1, -1, 1, -1, 1)]
    return p1, src, tgt, na, vort


P1, SRC, TGT, NA, VORT = _setup()


def _blur(a, k):
    for _ in range(k):
        a = 0.5 * a + 0.125 * (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1))
    return a


def _flow(x, y, s):
    """Seeded vortices: each point turns about each centre by an angle that falls off with distance (pure in s)."""
    for cx, cy, g, r in VORT:
        dx, dy = x - cx, y - cy
        th = g * s * np.exp(-(dx * dx + dy * dy) / (r * r))
        c, sn = np.cos(th), np.sin(th)
        x, y = cx + (dx * c - dy * sn) * (1 + 0.015 * s), cy + (dx * sn + dy * c) * (1 + 0.015 * s)
    return x, y


def frames():
    """FramesLayer source for the clouds (pure in absolute time)."""
    t_n, t_sh, t_ch = float(T.c03_s03_nucleus), float(T.c03_s03_shapes), float(T.c03_s03_chemistry)
    t_sw, t_lg = float(T.c03_s03_swirls), float(T.c03_s03_larger)
    sch, neg, nav = C.schrod, C.e_field, C.navier

    def put(img, x, y, w, color):
        ch3.splat(img, x, y, w, color, PPU, (0.0, 0.0))

    def cloud(img, kind, cx, g, spin):
        if g <= 0.01:
            return
        P, sg = ch3.orbital_points(kind)
        if kind == "1s":
            P, sg = P1[:N1], np.ones(N1, np.float32)
        x, y = _rot(P, spin, TILT[kind])
        k = SC[kind] * (0.35 + 0.65 * g)
        w = 0.5 * g * (30000 / len(P))
        pos = sg > 0
        put(img, cx + k * x[pos], CY + k * y[pos], w, sch)
        put(img, cx + k * x[~pos], CY + k * y[~pos], w, neg)

    def frame(t):
        img = np.zeros((NY, NX, 3), np.float32)
        spin = SPIN * (t - t_n)
        go = lambda a, d=1.2: float(smooth01((t - a) / d))
        g1 = go(t_n - 0.1)
        x1 = -4.2 * go(t_sh - 0.1, 1.3)
        merge = go(t_ch - 1.6, 0.8)                         # the row gives way to two atoms
        if merge < 1:
            cloud(img, "1s", x1, g1 * (1 - merge), spin)
            cloud(img, "2p", 0.0, go(t_sh + 0.1) * (1 - merge), spin)
            cloud(img, "3d", 4.2, go(t_sh + 0.7) * (1 - merge), spin)
        if merge > 0:
            # two hydrogen atoms approach, then their clouds become one bond
            d = 2.3 + (0.7 * B_SC - 2.3) * go(t_ch - 0.7, 1.0)
            u = go(t_ch - 0.05, 1.1)
            sx, sy = _rot(SRC, 0.0, 0.0)
            tx, ty = _rot(TGT, 0.0, 0.0)
            ax = np.where(np.arange(len(SRC)) < NA, d, -d)
            x = (ax + B_SC * sx) * (1 - u) + B_SC * tx * u
            y = CY + B_SC * (sy * (1 - u) + ty * u)
            s = 0.8 * max(t - t_sw + 0.2, 0) ** 1.15
            if s > 0:
                x, y = _flow(x, y, s)
            c = go(t_sw + 0.8, t_lg + 1.0 - t_sw - 0.8)
            put(img, x, y, 0.55 * merge, mix(sch, nav, c))
            img = _blur(img, 2 + int(6 * c)) * (1 + 2.5 * c)
        else:
            img = _blur(img, 2)
        lin = 1 - np.exp(-1.6 * img)
        a = lin.max(axis=2)
        rgb = lin / np.maximum(a, 1e-6)[..., None]
        srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.maximum(rgb, 0) ** (1 / 2.4) - 0.055)
        out = np.empty((NY, NX, 4), np.uint8)
        out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
        out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        return out
    return frame


