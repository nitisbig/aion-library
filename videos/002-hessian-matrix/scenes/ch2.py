"""Chapter 2 landscape (scenes 06–07, reused in 16): two hills and the pass between them.

f(x, y) = Σ amp·exp(−|p − c|² / 2σ²). Gradient and Hessian are exact (closed form);
critical points are found with Newton's method from a grid of seeds.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, RIGHT, UP, Arrow, Circle, Dot, Line, Square, VGroup, always_redraw

from aion import style as S

import shared as V
from aion.components.bend_gauge import BendGauge
from aion.components.surface_gl import slice_line, tangent_disc

# The luminous look (Aion design system) for every Ch2 surface: black body, silver
# lines, glow. Full-frame plates also get the vignette + grain finish.
LUMINOUS = dict(lum=1.0, bloom=1.0, vignette=0.5, grain=0.04, fog_color=S.STAGE)
LUMINOUS_PANEL = dict(LUMINOUS, vignette=0.0, grain=0.0)    # small viewports: glow only

HILLS = [(1.15, 0.55, 1.25, 0.72), (-1.05, -0.65, 1.0, 0.8)]
X0, Y0 = 0.25, 0.55              # where the two slices cross (the walker's point)


def f(x, y):
    return sum(a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s)) for cx, cy, a, s in HILLS)


def grad(x, y):
    gx = gy = 0.0
    for cx, cy, a, s in HILLS:
        e = a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
        gx = gx - e * (x - cx) / s ** 2
        gy = gy - e * (y - cy) / s ** 2
    return np.array([gx, gy])


def hess(x, y):
    H = np.zeros((2, 2))
    for cx, cy, a, s in HILLS:
        e = a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
        dx, dy = (x - cx) / s ** 2, (y - cy) / s ** 2
        H += e * np.array([[dx * dx - 1 / s ** 2, dx * dy], [dx * dy, dy * dy - 1 / s ** 2]])
    return H


def critical_points():
    """[(x, y, kind)] with kind in {'peak', 'saddle', 'valley'}, deduplicated."""
    found = []
    for sx in np.linspace(-2.2, 2.2, 23):
        for sy in np.linspace(-2.2, 2.2, 23):
            p = np.array([sx, sy])
            for _ in range(40):
                H = hess(*p)
                if abs(np.linalg.det(H)) < 1e-9:
                    break
                p = p - np.linalg.solve(H, grad(*p))
                if np.abs(p).max() > 3:
                    break
            if np.abs(p).max() > 2.6 or np.linalg.norm(grad(*p)) > 1e-8 or f(*p) < 0.05:
                continue
            if any(np.hypot(p[0] - q[0], p[1] - q[1]) < 1e-3 for q in found):
                continue
            lam = np.linalg.eigvalsh(hess(*p))
            kind = "peak" if lam.max() < 0 else "valley" if lam.min() > 0 else "saddle"
            found.append((float(p[0]), float(p[1]), kind))
    return found


CRIT = critical_points()
assert sorted(k for _, _, k in CRIT) == ["peak", "peak", "saddle"], CRIT


def land_rig(**kw) -> V.Rig:
    st = dict(H=(0.0, 0.0, 0.0), w=(0.0, 1.0, 0.0, 0.0), gauss=HILLS, zs=1.0, zclip=0.0,
              R=2.8, edge=0.78, yaw=-62.0, pitch=28.0, dist=8.6, fov=36.0, target=(0.0, 0.0, 0.35),
              fog=0.015, sky=0.0, grid=(0.22, 0.22), grid_step=0.4, contour=0.0, contour_step=0.1,
              tint=0.0, opacity=1.0, zlo=0.0, zhi=1.25, time=0.0, slices=[], disc=None, **LUMINOUS)
    st.update(kw)
    return V.Rig(**st)


# label anchors for the partials: out along each slice, clear of the other
DFX_AT = (X0 + 0.95, Y0, float(f(X0 + 0.95, Y0)) + 0.45)
DFY_AT = (X0 - 0.95, Y0 - 1.05, float(f(X0, Y0 - 1.05)) + 0.3)     # beside the green cut, not on it


def tangent_3d(plate, x, y, direction, half=0.55, color=S.GRAD):
    """Yellow tangent segment on the surface at (x, y) along floor direction (dx, dy)."""
    d = np.array(direction, float)
    g = grad(x, y)
    def make():
        z = float(plate.height(x, y))
        slope = float(g @ d)
        v = np.array([d[0], d[1], slope])
        v = v / np.linalg.norm(v) * half
        p = np.array([x, y, z])
        return VGroup(V.lit(Line(plate.project(*(p - v)), plate.project(*(p + v))), color, width=4.5),
                      Dot(plate.project(*p), radius=0.06, color=color))
    return always_redraw(make)


TOPDOWN = dict(pitch=89.0, yaw=-90.0, dist=8.2, contour=1.0, grid=(0.0, 0.0), target=(0.0, -0.05, 0.0))


def field_arrows(plate) -> VGroup:
    """True gradient arrows on a grid, drawn on the top-down map (scene 07 → 08)."""
    field = VGroup()
    for x in np.linspace(-2.2, 2.2, 10):
        for y in np.linspace(-2.0, 2.0, 9):
            gx, gy = grad(x, y)
            z = float(f(x, y))
            a, b = plate.project(x, y, z), plate.project(x + 0.45 * gx, y + 0.45 * gy, z)
            if np.linalg.norm(b - a) > 0.08:
                field.add(Arrow(a, b, buff=0, color=S.GRAD, stroke_width=2.5,
                                max_tip_length_to_length_ratio=0.3).set_opacity(0.6))
    return field


def crit_rings(plate) -> VGroup:
    return VGroup(*[V.lit(Circle(radius=0.2), S.TERRAIN_LINE, width=3, halo=12, opacity=0.2).move_to(
        plate.project(x, y, float(f(x, y)))) for x, y, _ in CRIT])


# scene 08 → 09: the saddle x² − y² filling the frame, smiling along x and frowning along y
SADDLE_SPIN = 6.0                               # degrees of yaw per second of the scene clock


def big_saddle(clk, sx, sy, **kw) -> V.Rig:
    st = dict(H=V.H_SADDLE, zs=0.32, zclip=0.0, R=1.55, edge=0.74, yaw=-60.0, pitch=27.0, dist=6.3,
              fov=34.0, target=(0.0, 0.0, 0.0), fog=0.02, grid=(0.25, 0.25), grid_step=0.35,
              zlo=-0.8, zhi=0.8, opacity=0.0, disc_a=0.42, slices=[], disc=None, **LUMINOUS)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + SADDLE_SPIN * clk.get_value()
    r.dyn["disc"] = lambda: tangent_disc(0, 0, 0.32, r.val("disc_a")) if r.val("disc_a") > 0.003 else None
    r.dyn["slices"] = lambda: [slice_line(0, color=S.SMILE, line=sx.get_value(), width=0.018),
                               slice_line(90, color=S.FROWN, line=sy.get_value(), width=0.018)]
    return r


def saddle_gauges(plate, lift):
    """Blue smile over the x slice, orange frown over the y slice, riding `lift` upward."""
    gx = BendGauge(2.0, width=0.9, stroke=7)
    gx.add_updater(lambda m: m.place(plate.surface_point(1.25, 0.0) + UP * (0.45 + lift.get_value())))
    gy = BendGauge(-2.0, width=0.9, stroke=7)
    gy.add_updater(lambda m: m.place(plate.surface_point(0.0, 1.25) + UP * (0.45 + lift.get_value())))
    return gx, gy


def how_many() -> VGroup:
    """'More than one': four faint hairline cells in a 2×2, foreshadowing the Hessian grid
    (no words: the narration asks the question)."""
    cells = VGroup(*[Square(0.36).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.55)
                     .set_fill(S.STAGE_RAISED, 1.0) for _ in range(4)])
    return cells.arrange_in_grid(2, 2, buff=0.1).move_to([-3.6, -2.55, 0])   # clear of both slices
