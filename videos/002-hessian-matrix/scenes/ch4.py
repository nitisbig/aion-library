"""Chapter 4 builders (scenes 13–16): bending in any direction, the sweep, the eigen-directions.

Every scene rebuilds the previous scene's last frame from these builders, so cuts are
pixel-continuous. All numbers on screen are computed from H = [[2, 3], [3, 2]] here.
"""

from __future__ import annotations

import math

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Axes, Circle, DashedLine, DashedVMobject,
                   DecimalNumber, Dot, Line, MathTex, ValueTracker, VGroup, VMobject, always_redraw)

from aion import style as S
from aion.components.bend_gauge import BendGauge, bend_color
from aion.components.surface_gl import slice_line
import shared as V
import ch2 as L2
import ch3 as L3
from beats import THETA, THETA_ZERO

# ── the math, checked first ───────────────────────────────────────────────
H = np.array([[2.0, 3.0], [3.0, 2.0]])


def unit(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def bend(deg: float) -> float:
    """uᵀHu for the unit vector at angle `deg`: the bending of the puzzle surface that way."""
    u = unit(deg)
    return float(u @ H @ u)


assert all(abs(bend(d) - (2 + 3 * math.sin(math.radians(2 * d)))) < 1e-12 for d in range(0, 181, 3))
assert abs(bend(0) - 2) < 1e-12 and abs(bend(90) - 2) < 1e-12
assert abs(bend(THETA["3"]) - 3) < 1e-9 and abs(bend(THETA["4"]) - 4) < 1e-9
assert abs(bend(45) - 5) < 1e-12 and abs(bend(135) + 1) < 1e-12 and abs(bend(THETA_ZERO)) < 1e-9
_lam, _vec = np.linalg.eigh(H)
assert np.allclose(_lam, [-1, 5])
V1, V2 = unit(45), unit(135)                       # eigenvectors: λ = 5 along (1,1), λ = −1 along (−1,1)
assert np.allclose(H @ V1, 5 * V1) and np.allclose(H @ V2, -V2) and abs(V1 @ V2) < 1e-12
assert np.allclose(H @ unit(0), [2, 3]) and abs(unit(0) @ H @ unit(0) - 2) < 1e-12   # the worked example

# ── scene 13: the map ─────────────────────────────────────────────────────
MAP = L3.S12_PLATE                                 # the flashback plate becomes the map (no cut)
MAP_VIEW = dict(pitch=89.0, yaw=-90.0, dist=7.0, target=(0.0, 0.0, 0.0), grid=(0.0, 0.0),
                contour=1.0, opacity=1.0)
R_U = 0.7                                          # world length of the unit arrow on the map
MAT_S, MAT_C = 0.6, np.array([-4.75, 1.95, 0.0])   # the Hessian, parked top-left
EQ_X = -6.55                                       # left edge of the worked lines


def map_rig(**kw) -> V.Rig:
    return V.puzzle_rig(**{**L3.PUZZLE_KW, **MAP_VIEW, **kw})


def floor(plate, xy) -> np.ndarray:
    return plate.project(float(xy[0]), float(xy[1]), 0.0)


def vec_arrow(plate, vec_fn, color=S.TEXT, width=5, opacity=1.0):
    """Arrow on the floor from the centre to R_U·vec_fn()."""
    def make():
        a, b = floor(plate, (0, 0)), floor(plate, R_U * np.asarray(vec_fn()))
        if np.linalg.norm(b - a) < 0.05:
            return VMobject()
        return Arrow(a, b, buff=0, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.2,
                     max_stroke_width_to_length_ratio=12).set_opacity(opacity)
    return always_redraw(make)


def tip_label(plate, tex: str, vec_fn, color=S.TEXT, out=0.32, size=38, opacity=1.0):
    m = MathTex(tex, font_size=size, color=color).set_opacity(opacity)
    def place(mob):
        v = np.asarray(vec_fn(), float)
        n = np.linalg.norm(v)
        mob.move_to(floor(plate, R_U * v + out * v / max(n, 1e-6)))
    m.add_updater(place)
    return m


def unit_circle(plate) -> VMobject:
    pts = [floor(plate, R_U * unit(d)) for d in np.linspace(0, 360, 97)]
    return VMobject().set_points_smoothly(pts).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.6)


def norm_label(plate) -> MathTex:
    return MathTex(r"\lVert u \rVert = 1", font_size=30, color=S.MUTED).move_to(
        floor(plate, R_U * unit(-62)) + DOWN * 0.3 + RIGHT * 0.35)


def hu_parts(plate):
    """(Hu arrow, its label, the drop line, the shadow on u) for u = east, all static."""
    u, hu = unit(0), H @ unit(0)
    foot = (u @ hu) * u                               # the projection of Hu on u: 2u
    arrow = Arrow(floor(plate, (0, 0)), floor(plate, R_U * hu), buff=0, color=S.TEXT, stroke_width=4,
                  max_tip_length_to_length_ratio=0.12).set_opacity(0.5)
    lab = MathTex("Hu", font_size=36, color=S.TEXT).set_opacity(0.6).next_to(floor(plate, R_U * hu), UP, buff=0.12)
    drop = DashedLine(floor(plate, R_U * hu), floor(plate, R_U * foot), dash_length=0.08,
                      color=S.MUTED, stroke_width=2.5).set_opacity(0.8)
    shadow = V.lit(Line(floor(plate, (0, 0)), floor(plate, R_U * foot)), S.SMILE, width=6, halo=18, opacity=0.18)
    return arrow, lab, drop, shadow


def eq_u() -> MathTex:
    return MathTex("u", "=", r"\begin{bmatrix}1\\0\end{bmatrix}", font_size=38, color=S.TEXT).move_to([-1.55, 1.95, 0])


def eq_hu() -> MathTex:
    m = MathTex("H", "u", "=", r"\begin{bmatrix}2&3\\3&2\end{bmatrix}", r"\begin{bmatrix}1\\0\end{bmatrix}",
                "=", r"\begin{bmatrix}2\\3\end{bmatrix}", font_size=38, color=S.TEXT)
    return m.move_to([EQ_X, 0.05, 0], aligned_edge=LEFT)


def eq_dot() -> MathTex:
    m = MathTex(r"u^\top", "(", "H", "u", ")", "=", r"\begin{bmatrix}1&0\end{bmatrix}",
                r"\begin{bmatrix}2\\3\end{bmatrix}", "=", "2", font_size=38, color=S.TEXT)
    m[-1].set_color(S.SMILE)
    return m.move_to([EQ_X, -1.35, 0], aligned_edge=LEFT)


def dot_gauge(eq) -> BendGauge:
    return BendGauge(2.0, width=0.75, stroke=7).place(eq[-1].get_center() + RIGHT * 0.85 + UP * 0.05)


def eq_bending():
    """(glass card, `bending(u) = uᵀHu`)."""
    from aion.components.cards import card_image
    m = MathTex(r"\text{bending}(u)", "=", r"u^\top", "H", "u", font_size=44, color=S.TEXT)
    m.move_to([-3.45, -2.75, 0])
    card = V.panel(m.width + 0.8, m.height + 0.55, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM,
                      border=S.LINE, glow=S.GLASS_TOP).move_to(m)
    return card, m


def s13_end():
    """Everything on screen at the end of scene 13 (u faces east)."""
    mat, grid, nums, halo = L3.s12_end()
    mat.scale(MAT_S).move_to(MAT_C)
    rig = map_rig()
    plate = rig.plate(**MAP)
    th = ValueTracker(0.0)
    u = vec_arrow(plate, lambda: unit(th.get_value()))
    ulab = tip_label(plate, "u", lambda: unit(th.get_value()))
    circ, nl = unit_circle(plate), norm_label(plate)
    hu = hu_parts(plate)
    e0, e1, e2 = eq_u(), eq_hu(), eq_dot()
    card, bnd = eq_bending()
    return dict(mat=mat, grid=grid, rig=rig, plate=plate, th=th, u=u, ulab=ulab, circ=circ, nl=nl,
                hu=hu, e0=e0, e1=e1, e2=e2, gauge=dot_gauge(e2), card=card, bnd=bnd)


# ── scene 14: the sweep ───────────────────────────────────────────────────
SWEEP = dict(width=6.4, height=4.7, center=np.array([-3.25, 0.65, 0.0]))
SWEEP_VIEW = dict(yaw=-58.0, pitch=30.0, dist=9.0, target=(0.0, 0.0, 0.0), contour=0.0, grid=(0.18, 0.18),
                  grid_angle=0.0, tint=0.0, opacity=1.0)
ROW_Y = -2.7                                       # dial · gauge · readout under the 3D view
DIAL_C, DIAL_R = np.array([-5.35, ROW_Y, 0.0]), 0.5
GAUGE_C = np.array([-3.65, ROW_Y, 0.0])
READ_C = np.array([-1.95, ROW_Y, 0.0])
GR_C = np.array([3.55, 0.35, 0.0])


def sweep_rig(th, sp, d1=None, d2=None, xs=None, ys=None, **kw) -> V.Rig:
    """The puzzle surface with the turning slice at θ (strength sp) and the four fixed slices."""
    r = V.puzzle_rig(**{**SWEEP_VIEW, **kw})
    get = lambda t: 0.0 if t is None else t.get_value()

    def slices():
        out = [slice_line(th.get_value(), color=bend_color(bend(th.get_value())), line=1.0,
                          plane=0.35 * get(sp), width=0.026)] if sp is not None and get(sp) >= 0 else []
        for t, ang, col, pl in ((d1, 45, S.SMILE, 0.0), (d2, 135, S.FROWN, 0.0),
                                (xs, 0, S.HX, 0.3), (ys, 90, S.HY, 0.3)):
            if get(t) > 0.003:
                out.append(slice_line(ang, color=col, line=get(t), plane=pl * get(t), width=0.024))
        return out[:4]
    r.dyn["slices"] = slices
    return r


def sweep_axes() -> Axes:
    ax = Axes(x_range=[0, 180, 45], y_range=[-1.5, 5.5, 1], x_length=5.6, y_length=3.9, tips=False,
              axis_config={"tick_size": 0.05}).move_to(GR_C)
    return V.hairline(ax)


def sweep_labels(ax) -> VGroup:
    degs = VGroup(*[V.label(f"{d}°", 18, S.MUTED).next_to(ax.c2p(d, -1.5), DOWN, buff=0.18)
                    for d in (0, 45, 90, 135, 180)])
    yl = MathTex(r"u^\top H u", font_size=32, color=S.MUTED).next_to(ax.c2p(0, 5.5), UP, buff=0.15)
    xl = MathTex(r"\theta", font_size=32, color=S.MUTED).next_to(ax.c2p(180, 0), RIGHT, buff=0.2)
    return VGroup(degs, yl, xl)


def sweep_trace(ax, th) -> VMobject:
    def make():
        t = th.get_value()
        g = VGroup()
        for lo, hi, col in ((0.0, THETA_ZERO, S.SMILE), (THETA_ZERO, 180.0, S.FROWN)):
            if t > lo + 0.25:
                g.add(V.lit(ax.plot(bend, x_range=[lo, min(t, hi), 0.5]), col, width=4, halo=14, opacity=0.16))
        return g
    return always_redraw(make)


def sweep_dot(ax, th) -> VMobject:
    return always_redraw(lambda: Dot(ax.c2p(th.get_value(), bend(th.get_value())), radius=0.075,
                                     color=bend_color(bend(th.get_value()))))


def peak_ring(ax) -> Circle:
    return Circle(radius=0.14).set_stroke(S.SMILE, 2.5).move_to(ax.c2p(45, 5))


def sweep_formula(ax) -> MathTex:
    return MathTex("2", "+", r"3\sin 2\theta", font_size=38, color=S.TEXT).move_to(ax.c2p(138, 4.6))


def dial(th):
    """(ring + E/N letters, the turning arrow)."""
    ring = Circle(radius=DIAL_R).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.55).move_to(DIAL_C)
    e = V.label("E", 16, S.MUTED).move_to(DIAL_C + RIGHT * (DIAL_R + 0.22))
    n = V.label("N", 16, S.MUTED).move_to(DIAL_C + UP * (DIAL_R + 0.2))
    arrow = always_redraw(lambda: Arrow(DIAL_C, DIAL_C + DIAL_R * np.array([*unit(th.get_value()), 0]), buff=0,
                                        color=S.TEXT, stroke_width=4, max_tip_length_to_length_ratio=0.28))
    return VGroup(ring, e, n), arrow


def dial_tag(text: str, deg: float):
    return V.label(text, 16, S.MUTED).move_to(DIAL_C + (DIAL_R + 0.3) * np.array([*unit(deg), 0]))


def sweep_gauge(k) -> BendGauge:
    return BendGauge(k, width=0.95, stroke=8).place(GAUGE_C)


def sweep_readout(th) -> DecimalNumber:
    d = DecimalNumber(bend(th.get_value()), num_decimal_places=1, font_size=56, color=S.TEXT)
    def upd(m):
        k = bend(th.get_value())
        m.set_value(k)
        m.set_color(bend_color(k))
        m.move_to(READ_C, aligned_edge=LEFT)
    d.add_updater(upd)
    upd(d)
    return d


def s14_end():
    """Everything on screen at the end of scene 14 (θ = 135°)."""
    th, sp = ValueTracker(135.0), ValueTracker(1.0)
    k = ValueTracker(bend(135.0))
    rig = sweep_rig(th, sp)
    plate = rig.plate(**SWEEP)
    ax = sweep_axes()
    ring, arrow = dial(th)
    return dict(th=th, sp=sp, k=k, rig=rig, plate=plate, ax=ax, labels=sweep_labels(ax),
                trace=sweep_trace(ax, th), dot=sweep_dot(ax, th), peak=peak_ring(ax), formula=sweep_formula(ax),
                ring=ring, arrow=arrow, tags=VGroup(dial_tag("NE", 45), dial_tag("NW", 135)),
                gauge=sweep_gauge(k), read=sweep_readout(th))


# ── scene 15: the hidden frown, the eigen-directions ──────────────────────
SADDLE_VIEW = dict(yaw=-100.0, pitch=34.0, dist=10.0, target=(0.0, 0.0, 0.9), tint=1.0)
TOP_VIEW = dict(pitch=89.0, yaw=-90.0, dist=7.4, target=(0.0, 0.0, 0.0), contour=1.0, grid=(0.0, 0.0))
GAUGE_AT = 1.75                                     # where the east / north smile gauges float


def right_angle(plate, a: float = 0.26) -> VMobject:
    pts = [floor(plate, a * V1), floor(plate, a * (V1 + V2)), floor(plate, a * V2)]
    return VMobject().set_points_as_corners(pts).set_stroke(S.TEXT, 2.5, opacity=0.9)


LEG_X = (1.55, 2.45, 4.0)                           # icon · v label · λ (left edge)
LEG_Y = (0.75, -0.55)


def legend():
    """(rows [(icon, v, λ)], eyebrow EIGENVECTOR, eyebrow EIGENVALUE)."""
    rows = []
    for y, d, col, v, lam in ((LEG_Y[0], V1, S.SMILE, "v_1", r"\lambda_1 = 5"),
                              (LEG_Y[1], V2, S.FROWN, "v_2", r"\lambda_2 = -1")):
        c = np.array([LEG_X[0], y, 0])
        off = 0.32 * np.array([*d, 0])
        icon = V.lit(Line(c - off, c + off), col, width=4, halo=14, opacity=0.18)
        vm = MathTex(v, font_size=44, color=col).move_to([LEG_X[1], y, 0])
        lm = MathTex(lam, font_size=44, color=col).move_to([LEG_X[2], y, 0], aligned_edge=LEFT)
        rows.append((icon, vm, lm))
    top = LEG_Y[0] + 0.85
    ev = V.hush(V.label("EIGENVECTOR", 18, S.MUTED, weight="BOLD")).move_to([0.5 * (LEG_X[0] + LEG_X[1]), top, 0])
    ew = V.hush(V.label("EIGENVALUE", 18, S.MUTED, weight="BOLD")).move_to([LEG_X[2], top, 0], aligned_edge=LEFT)
    return rows, ev, ew


def s15_end():
    th, sp = ValueTracker(135.0), ValueTracker(0.0)
    d1 = ValueTracker(1.0)
    rig = sweep_rig(th, sp, d1=d1, **SADDLE_VIEW)
    rig.set(**TOP_VIEW)
    plate = rig.plate(**SWEEP)
    rows, ev, ew = legend()
    return dict(th=th, sp=sp, d1=d1, rig=rig, plate=plate, ra=right_angle(plate), rows=rows, ev=ev, ew=ew)


# ── scene 16: line up the grid; any smooth surface ────────────────────────
M16_C = np.array([3.6, 0.35, 0.0])
TURNED = dict(grid=(0.3, 0.3), grid_angle=45.0, yaw=-135.0)


def m16():
    """The glass Hessian [[2,3],[3,2]] with its numbers, at M16_C. Returns (group, grid, nums)."""
    from aion.components.matrix_grid import HessianGrid
    grid = L3.glass(HessianGrid(cell=1.25, gap=L3.TIGHT, center=M16_C, tint_scale=L3.TINT))
    nums = {}
    for (i, j), s, c in L3.S12_NUMS:
        nums[(i, j)] = MathTex(s, font_size=66, color=c).move_to(grid.cells[i][j])
        grid.cells[i][j].set_fill(c, 0.3 * L3.TINT).set_stroke(c, 2.5, opacity=1.0)
        grid.add(nums[(i, j)])
    grid.show_brackets()
    hl = L3.h_label(grid)
    return VGroup(grid, hl), grid, nums


P = np.array([L2.X0, L2.Y0])                       # the point we zoom onto (on a slope: ∇f ≠ 0)
PATCH_H = 0.5                                       # half-size of the quadratic patch (world units)
CLOSE = dict(dist=4.3, pitch=32.0, yaw=-62.0, target=(float(P[0]), float(P[1]), float(L2.f(*P))))


def patch(plate, a, b, n=7):
    """Lines of the local model f(p) + a·∇f·h + b·½hᵀHh over a small square around p."""
    g0, H0, f0 = L2.grad(*P), L2.hess(*P), float(L2.f(*P))

    def q(hx, hy):
        h = np.array([hx, hy])
        return f0 + a.get_value() * float(g0 @ h) + b.get_value() * 0.5 * float(h @ H0 @ h) + 0.012

    def make():
        s = np.linspace(-PATCH_H, PATCH_H, n)
        t = np.linspace(-PATCH_H, PATCH_H, 25)
        g = VGroup()
        for c in s:
            for pts in ([(P[0] + c, P[1] + v) for v in t], [(P[0] + v, P[1] + c) for v in t]):
                g.add(VMobject().set_points_smoothly(
                    [plate.project(x, y, q(x - P[0], y - P[1])) for x, y in pts]))
        return g.set_stroke(S.LIGHT, 2.2, opacity=0.9)
    return always_redraw(make)


def taylor() -> MathTex:
    m = MathTex("f(p+h)", r"\approx", "f(p)", "+", r"\nabla f\cdot h", "+", r"\tfrac{1}{2}\,h^\top H\,h",
                font_size=46, color=S.TEXT)
    m[0].set_color(S.MUTED)
    m[4].set_color(S.GRAD)
    return m.move_to(DOWN * 3.15)


def parabola_inset():
    """(glass card, cos curve, dashed 1 − x²/2): the Ch1 picture, small, top-right."""
    from aion.components.cards import card_image
    c = np.array([4.75, 2.55, 0.0])
    card = V.panel(3.3, 1.9, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM, border=S.LINE, glow=S.GLASS_TOP).move_to(c)
    ax = Axes(x_range=[-2.6, 2.6], y_range=[-0.9, 1.25], x_length=2.9, y_length=1.5, tips=False).move_to(c)
    cosc = V.lit(ax.plot(np.cos, x_range=[-2.6, 2.6]), S.TERRAIN_LINE, width=3, halo=10)
    par = DashedVMobject(ax.plot(lambda x: 1 - x * x / 2, x_range=[-1.25, 1.25]), num_dashes=22)
    par.set_stroke(S.FROWN, 3.5)
    return card, cosc, par


def s16_end():
    """Scene 16's last frame: the landscape up close, the full patch and formula, the parabola inset."""
    land = L2.land_rig(opacity=1.0, **CLOSE)
    plate = land.plate()
    a, b = ValueTracker(1.0), ValueTracker(1.0)
    card, cosc, par = parabola_inset()
    glow = VGroup(par.copy().set_stroke(width=9, opacity=0.25))
    return dict(land=land, plate=plate, a=a, b=b, patch=patch(plate, a, b), taylor=taylor(),
                card=card, cosc=cosc, par=par, glow=glow)
