"""Intro (in_s01 … in_s03): the wall of ten tiles, seen through a simple 2.5D view, and what the three scenes share.

The wall is outro.py's (same tiles, same 5x2 layout, same labels), so the intro plants exactly what the outro
returns to. The view is (zoom, centre): a wall point w appears on screen at (w − centre) · zoom. The intro starts
framed on T5 (zoom 1.5), pulls back to the whole wall during in_s02, and dives into T1 at the end of in_s03.
Moving the geometry ourselves (instead of the 2.5D camera) keeps strokes and type at their designed weights.
"""
from __future__ import annotations

import numpy as np

import outro as O
from beats import T
from kit import smooth01

PIC_DY = O.pic_dy()                            # the picture's centre sits this far above the tile image's centre


def pic_centre(i):
    x, y = O.wall(i)
    return x, y + PIC_DY


Z0 = 1.5                                       # in_s01 ends framed on T5 at this zoom
C0 = pic_centre(4)
C_WALL = (0.0, 0.1)                            # the whole wall, labels included
Z_DIVE = 2 * (64 / 9) / O.TW                   # T1's picture fills the frame width
K_SHRINK = O.TW * Z0 / (2 * 64 / 9)            # in_s01's frame shrinks to T5's picture at Z0

# the order the narration names the tiles in in_s02 (T5 is already lit from the opening)
LIGHT = [("probability", 8), ("pricing", 9), ("light", 0), ("gravity", 1), ("atom", 2), ("air", 3), ("clocks", 5),
         ("learn", 6), ("wire", 7)]
YEARS = [1865, 1915, 1926, 1845, 1807, 1905, 1847, 1948, 1763, 1973]


def ease(t, a, b):
    return float(smooth01(min(max((t - a) / (b - a), 0.0), 1.0)))


def view(t):
    """(zoom, centre x, centre y) at time t, over the whole intro."""
    u = ease(t, float(T.in_s02_ten_of_them) - 0.2, float(T.in_s02_pricing) - 1.2)          # pull back
    d = ease(t, float(T.in_s03_begin_with_light) + 0.2, float(T.c01_s01) - 0.15)           # dive into T1
    z = Z0 + (1.0 - Z0) * u
    cx, cy = C0[0] + (C_WALL[0] - C0[0]) * u, C0[1] + (C_WALL[1] - C0[1]) * u
    if d > 0:
        t1 = pic_centre(0)
        zd = z * (Z_DIVE / z) ** d                                          # zoom geometrically: steady speed
        w = (zd - z) / (Z_DIVE - z)
        cx, cy, z = cx + (t1[0] - cx) * w, cy + (t1[1] - cy) * w, zd
    return z, cx, cy


def to_screen(p, t):
    z, cx, cy = view(t)
    return (p[0] - cx) * z, (p[1] - cy) * z, z


def tile_place(i, t, grow=1.0):
    x, y, z = to_screen(O.wall(i), t)
    return x, y, z * grow, 0.0


def apply_view(mob, t):
    """A Manim mobject drawn in wall coordinates, moved onto the screen through the view (type scales with it)."""
    from manim import ORIGIN
    z, cx, cy = view(t)
    return mob.shift(np.array([-cx, -cy, 0.0])).scale(z, about_point=ORIGIN)


# ------------------------------------------------------------------------------------------------ timeline
TL_X0, TL_X1, TL_Y = -5.6, 5.6, -3.15


def tl_x(year):
    return TL_X0 + (TL_X1 - TL_X0) * (year - 1763) / (1973 - 1763)


# ------------------------------------------------------------------------------------------------ link arcs
def link_pts(i, n=40):
    """The arc from tile i to tile i+1 in wall coordinates: from the top of one tile to the top of the next, bowing
    up; from T5 (end of the top row) to T6 (start of the bottom row) it sweeps back through the space between rows."""
    x0, y0 = O.wall(i)
    x1, y1 = O.wall(i + 1)
    yc0, yc1 = y0 + PIC_DY, y1 + PIC_DY
    if i == 4:                                     # down the right margin, across between the rows, down into T6
        xr, xl, ym = x0 + O.TW / 2 + 0.28, x1 - O.TW / 2 - 0.28, -0.2
        pts = np.array([(x0 + O.TW / 2, yc0), (xr, yc0), (xr, ym), (xl, ym), (xl, yc1), (x1 - O.TW / 2, yc1)])
        for _ in range(4):                         # Chaikin corner cutting: rounded corners, ends kept
            q = [pts[0]]
            for p0, p1 in zip(pts[:-1], pts[1:]):
                q += [0.75 * p0 + 0.25 * p1, 0.25 * p0 + 0.75 * p1]
            pts = np.array(q + [pts[-1]])
        L = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
        u = np.linspace(0, L[-1], n * 3)
        return np.c_[np.interp(u, L, pts[:, 0]), np.interp(u, L, pts[:, 1])]
    else:
        a, b = np.array((x0 + 0.3, yc0 + O.TH / 2 + 0.04)), np.array((x1 - 0.3, yc1 + O.TH / 2 + 0.04))
        bow = 0.42 if i < 4 else 0.28                  # lower under the top row's equations
        P = [a, a + (0.4, bow), b + (-0.4, bow), b]
    u = np.linspace(0, 1, n)[:, None]
    return (1 - u) ** 3 * P[0] + 3 * (1 - u) ** 2 * u * P[1] + 3 * (1 - u) * u ** 2 * P[2] + u ** 3 * P[3]
