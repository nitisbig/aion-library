"""Chapter 5 builders (scenes 17–20): read the signs, the determinant, a real landscape, can't tell.

Every scene rebuilds the previous scene's last frame from these builders. All numbers on
screen are computed and asserted here.
"""

from __future__ import annotations

import math

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Axes, Circle, MathTex, Polygon, ValueTracker, VGroup,
                   VMobject, always_redraw)

from aion import style as S
from aion.components.bend_gauge import BendGauge
from aion.components.matrix_grid import HessianGrid
import shared as V
import ch2 as L2
import ch3 as L3

# ── the math, checked first ───────────────────────────────────────────────
PUZ = np.array([[2.0, 3.0], [3.0, 2.0]])
assert np.isclose(np.linalg.det(PUZ), 2 * 2 - 3 ** 2) and np.isclose(np.linalg.det(PUZ), -5)
assert np.isclose(np.prod(np.linalg.eigvalsh(PUZ)), np.linalg.det(PUZ))     # det = λ₁λ₂
PUZ_EIG = (5.0, -1.0)


def real_f(x, y):
    return x ** 3 - 3 * x + y ** 2


def real_grad(x, y):
    return np.array([3 * x * x - 3, 2 * y])


def real_hess(x, y):
    return np.array([[6 * x, 0.0], [0.0, 2.0]])


REAL_CRIT = ((1.0, 0.0), (-1.0, 0.0))
assert all(np.allclose(real_grad(*p), 0) for p in REAL_CRIT)
assert np.allclose(real_hess(1, 0), [[6, 0], [0, 2]]) and np.allclose(real_hess(-1, 0), [[-6, 0], [0, 2]])
assert real_f(1, 0) == -2 and real_f(-1, 0) == 2


def _num_hess(fn, h=1e-3):
    e = np.eye(2) * h
    return np.array([[(fn(*(e[i] + e[j])) - fn(*(e[i] - e[j])) - fn(*(-e[i] + e[j])) + fn(*(-e[i] - e[j])))
                      / (4 * h * h) for j in range(2)] for i in range(2)])


assert np.allclose(_num_hess(lambda x, y: x ** 4 + y ** 4), 0, atol=1e-5)          # can't tell: all zeros
assert np.allclose(_num_hess(lambda x, y: x ** 3 - 3 * x * y * y), 0, atol=1e-5)

# ── scene 17: the sign chart and the mini surface ─────────────────────────
CH_C = np.array([-3.25, -0.2, 0.0])
CH_R = 6.0                                          # chart spans λ ∈ [−6, 6]²
MINI = dict(width=5.2, height=4.4, center=np.array([3.85, 0.5, 0.0]))
RING_R, RING_N = 1.25, 8
Q_POS = {1: (3.3, 4.3), 2: (-3.3, 4.3), 3: (-3.3, -4.3), 4: (3.3, -4.3)}


def chart() -> Axes:
    ax = Axes(x_range=[-CH_R, CH_R, 2], y_range=[-CH_R, CH_R, 2], x_length=5.6, y_length=5.6, tips=False,
              axis_config={"tick_size": 0.04}).move_to(CH_C)
    return V.hairline(ax)


def chart_labels(ax) -> VGroup:
    return VGroup(MathTex(r"\lambda_1", font_size=34, color=S.MUTED).next_to(ax.c2p(CH_R, 0), RIGHT, buff=0.15),
                  MathTex(r"\lambda_2", font_size=34, color=S.MUTED).next_to(ax.c2p(0, CH_R), UP, buff=0.12))


def _poly(ax, pts, col, op=0.13):
    return Polygon(*[ax.c2p(*p) for p in pts]).set_fill(col, op).set_stroke(width=0)


def quadrant(ax, q: int) -> VGroup:
    """Tint for quadrant q: one colour for Q1/Q3, a blue/orange split for Q2/Q4."""
    R = CH_R
    if q == 1:
        return VGroup(_poly(ax, [(0, 0), (R, 0), (R, R), (0, R)], S.SMILE))
    if q == 3:
        return VGroup(_poly(ax, [(0, 0), (-R, 0), (-R, -R), (0, -R)], S.FROWN))
    if q == 4:       # λ₁ > 0 > λ₂: blue beside the +λ₁ axis, orange beside the −λ₂ axis
        return VGroup(_poly(ax, [(0, 0), (R, 0), (R, -R)], S.SMILE), _poly(ax, [(0, 0), (R, -R), (0, -R)], S.FROWN))
    return VGroup(_poly(ax, [(0, 0), (0, R), (-R, R)], S.SMILE), _poly(ax, [(0, 0), (-R, R), (-R, 0)], S.FROWN))


def q_label(ax, q: int) -> VGroup:
    if q in (1, 3):
        word, sub, col = ("valley", "local minimum", S.SMILE) if q == 1 else ("peak", "local maximum", S.FROWN)
        g = VGroup(V.label(word, 28, col, weight="MEDIUM"), V.label(sub, 18, S.MUTED)).arrange(DOWN, buff=0.08)
    else:
        g = VGroup(V.label("saddle", 28, S.TEXT, weight="MEDIUM"))
    return g.move_to(ax.c2p(*Q_POS[q]))


def chart_dot(ax, l1, l2):
    me = V.walker()
    me.add_updater(lambda m: m.move_to(ax.c2p(l1.get_value(), l2.get_value())))
    return me


def mini_rig(l1, l2, **kw) -> V.Rig:
    st = dict(zs=0.16, zclip=0.0, R=1.55, edge=0.74, yaw=-60.0, pitch=27.0, dist=6.4,
              fov=34.0, target=(0.0, 0.0, 0.0), fog=0.02, grid=(0.25, 0.25), grid_step=0.35, zlo=-0.8,
              zhi=0.8, opacity=0.0, tint=1.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["H"] = lambda: (l1.get_value(), 0.0, l2.get_value())
    return r


def ring(plate, l1, l2):
    """(gauges, trackers): bend gauges around the mini surface, live: direction φ bends by
    λ₁cos²φ + λ₂sin²φ (uᵀ diag(λ₁, λ₂) u). Add the trackers to the scene too."""
    g, ks = VGroup(), []
    for n in range(RING_N):
        phi = 2 * math.pi * n / RING_N
        k = ValueTracker(0.0)
        k.add_updater(lambda m, p=phi: m.set_value(l1.get_value() * math.cos(p) ** 2 + l2.get_value() * math.sin(p) ** 2))
        gg = BendGauge(k, width=0.42, stroke=5, gain=0.12)
        gg.add_updater(lambda m, p=phi: m.place(plate.surface_point(RING_R * math.cos(p), RING_R * math.sin(p)) + UP * 0.28))
        g.add(gg)
        ks.append(k)
    return g, ks


def s17_end():
    ax = chart()
    l1, l2 = ValueTracker(-2.0), ValueTracker(2.0)
    rig = mini_rig(l1, l2, opacity=1.0)
    plate = rig.plate(**MINI)
    return dict(ax=ax, labels=chart_labels(ax), quads=VGroup(*[quadrant(ax, q) for q in (1, 2, 3, 4)]),
                qlabels=VGroup(*[q_label(ax, q) for q in (1, 2, 3, 4)]), l1=l1, l2=l2, dot=chart_dot(ax, l1, l2),
                rig=rig, plate=plate, ring=ring(plate, l1, l2))


# ── scene 18: the determinant ─────────────────────────────────────────────
EQ_C = np.array([3.75, 2.75, 0.0])
CARD_C, CARD_W, CARD_H = np.array([3.75, -0.85, 0.0]), 5.9, 2.75


def eq_det() -> MathTex:
    m = MathTex(r"\det H", "=", "f_{xx}", "f_{yy}", "-", "f_{xy}^2", font_size=46, color=S.TEXT)
    m[2].set_color(S.HX)
    m[3].set_color(S.HY)
    m[5].set_color(S.TWIST)
    return m.move_to(EQ_C)


def eq_lams(eq) -> MathTex:
    m = MathTex("=", r"\lambda_1", r"\lambda_2", font_size=46, color=S.TEXT)
    return m.shift(eq[1].get_center() - m[0].get_center() + DOWN * 0.95)


def det_card():
    """(glass card, eyebrow, rows [(math, arrow, word)]): the 2D second-derivative test."""
    from aion.components.cards import card_image
    card = card_image(CARD_W, CARD_H, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM, border=S.LINE,
                      glow=S.GLASS_TOP).move_to(CARD_C)
    head = V.label("THE TEST AT A FLAT POINT", 18, S.MUTED, weight="BOLD").move_to(CARD_C + UP * (CARD_H / 2 - 0.38))
    rows = []
    x0 = CARD_C[0] - CARD_W / 2 + 0.35
    for i, (tex, word, col) in enumerate(((r"\det H < 0", "saddle", S.TEXT),
                                          (r"\det H > 0,\ f_{xx} > 0", "valley", S.SMILE),
                                          (r"\det H > 0,\ f_{xx} < 0", "peak", S.FROWN))):
        y = CARD_C[1] + 0.45 - 0.68 * i
        m = MathTex(tex, font_size=34, color=S.TEXT).move_to([x0, y, 0], aligned_edge=LEFT)
        ar = MathTex(r"\rightarrow", font_size=32, color=S.MUTED).move_to([CARD_C[0] + 1.0, y, 0])
        w = V.label(word, 28, col, weight="MEDIUM")
        w.shift(np.array([CARD_C[0] + 1.4, y, 0]) - w.get_left())
        rows.append((m, ar, w))
    return card, head, rows


def eq_puzzle() -> MathTex:
    return MathTex("H", "=", r"\begin{bmatrix}2&3\\3&2\end{bmatrix}", font_size=42, color=S.TEXT).move_to(EQ_C + UP * 0.05)


def eq_calc() -> MathTex:
    m = MathTex(r"\det H", "=", r"2\cdot 2", "-", "3^2", "=", "4", "-", "9", "=", "-5", font_size=36, color=S.TEXT)
    m[-1].set_color(S.FROWN)
    return m.move_to(EQ_C + DOWN * 1.15)


def s18_end():
    e = s17_end()
    e["l1"].set_value(PUZ_EIG[0])
    e["l2"].set_value(PUZ_EIG[1])
    card, head, rows = det_card()
    e.update(card=card, head=head, rows=rows, pz=eq_puzzle(), calc=eq_calc())
    return e


# ── scene 19: a real landscape ────────────────────────────────────────────
REAL_SPIN = 2.0                                     # degrees of yaw per second


def real_rig(clk, **kw) -> V.Rig:
    st = dict(H=(0.0, 0.0, 0.0), w=(0.0, 0.0, 1.0, 0.0), zs=0.3, zclip=1.5, R=2.3, edge=0.78, yaw=-70.0,
              pitch=30.0, dist=8.6, fov=36.0, target=(0.0, 0.0, -0.1), fog=0.02, grid=(0.2, 0.2), grid_step=0.35,
              contour=0.6, contour_step=0.15, zlo=-1.5, zhi=1.5, tint=0.0, opacity=0.0, slices=[], disc=None,
              **L2.LUMINOUS)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + REAL_SPIN * clk.get_value()
    return r


def real_formula() -> MathTex:
    m = MathTex("f", "=", "x^3", "-", "3x", "+", "y^2", font_size=52, color=S.TEXT)
    m[2].set_color(S.HX)
    m[4].set_color(S.HX)
    m[6].set_color(S.HY)
    return m.to_corner(UP + RIGHT, buff=0.55)


def crit_ring(plate, x: float):
    c = V.lit(Circle(radius=0.17), S.TERRAIN_LINE, width=3, halo=12, opacity=0.2)
    return V.pin(c, plate, lambda: (x, 0.0, float(plate.height(x, 0.0)) + 0.01))


MINI_CELL = 0.46


def mini_matrix(plate, x: float, entries, lift=1.15):
    """A small glass Hessian floating above (x, 0); entries are filled on the words."""
    g = L3.glass(HessianGrid(cell=MINI_CELL, gap=0.05, tint_scale=L3.TINT))
    g.show_brackets()
    g.brackets.set_stroke(width=2.5)
    nums = [MathTex(s, font_size=30, color=c) for s, c in entries]
    holder = VGroup(g)
    holder.add_updater(lambda m: m.move_to(plate.project(x, 0.0, float(plate.height(x, 0.0))) + UP * lift))
    return holder, g, nums


ENTRIES_V = (("6", S.HX), ("0", S.TWIST), ("0", S.TWIST), ("2", S.HY))
ENTRIES_S = (("-6", S.HX), ("0", S.TWIST), ("0", S.TWIST), ("2", S.HY))


def path_out(plate, s: ValueTracker):
    """Dashed gold path from the valley (1, 0) over the pass (−1, 0) and out (to x = −2.1)."""
    xs = np.linspace(1.0, -2.1, 60)

    def make():
        k = max(2, int(round(s.get_value() * len(xs))))
        if s.get_value() < 0.02:
            return VMobject()
        pts = [plate.project(x, 0.0, float(plate.height(x, 0.0)) + 0.03) for x in xs[:k]]
        from manim import DashedVMobject
        return DashedVMobject(VMobject().set_points_smoothly(pts), num_dashes=max(2, k // 2)).set_stroke(S.GRAD, 3.5)
    return always_redraw(make)


# ── scene 20: when the test can't tell ────────────────────────────────────
LEFT_P = dict(width=6.6, height=4.6, center=np.array([-3.5, 0.65, 0.0]))
RIGHT_P = dict(width=6.6, height=4.6, center=np.array([3.5, 0.65, 0.0]))
FORM_Y, ZERO_Y = -2.0, -3.05


def quartic_rig(**kw) -> V.Rig:
    st = dict(H=(0.0, 0.0, 0.0), w=(0.0, 0.0, 0.0, 1.0), zs=0.3, zclip=1.1, R=1.45, edge=0.76, yaw=-60.0,
              pitch=28.0, dist=4.9, fov=34.0, target=(0.0, 0.0, 0.25), fog=0.02, grid=(0.22, 0.22), grid_step=0.25,
              zlo=-1.0, zhi=1.0, tint=0.0, opacity=0.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    return V.Rig(**st)


MONKEY_SPIN = 8.0


def monkey_rig(clk, **kw) -> V.Rig:
    st = dict(H=(0.0, 0.0, 0.0), w=(0.0, 0.0, 0.0, 0.0), wm=1.0, zs=0.35, zclip=1.0, R=1.4, edge=0.76,
              yaw=-60.0, pitch=30.0, dist=4.9, fov=34.0, target=(0.0, 0.0, 0.0), fog=0.02, grid=(0.22, 0.22),
              grid_step=0.25, zlo=-1.0, zhi=1.0, tint=0.0, opacity=0.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + MONKEY_SPIN * clk.get_value()
    return r


LOBES = (60.0, 180.0, 300.0)                       # x³ − 3xy² = r³cos 3θ < 0 around these angles
assert all(math.cos(math.radians(3 * t)) < -0.99 for t in LOBES)


def lobe(plate, deg: float, g: ValueTracker):
    u = np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])

    def make():
        k = g.get_value()
        if k < 0.02:
            return VMobject()
        pts = [plate.surface_point(*(r * u), 0.02) for r in np.linspace(0.0, 1.3 * k, 24)]
        return V.lit(VMobject().set_points_smoothly(pts), S.FROWN, width=4, halo=14, opacity=0.18)
    return always_redraw(make)


def zero_matrix(center):
    g = L3.glass(HessianGrid(cell=0.5, gap=0.05, center=center))
    for c in g.boxes:
        c.set_stroke(S.FLAT, 1.6, opacity=0.6)
    for i in range(2):
        for j in range(2):
            g.add(MathTex("0", font_size=30, color=S.FLAT).move_to(g.cells[i][j]))
    g.show_brackets()
    g.brackets.set_stroke(S.FLAT, 2.5)
    return g


def echo_row():
    """The Ch1 test card's last row, small: flat gauge → can't tell."""
    g = BendGauge(0.0, width=0.8, stroke=7).place(np.array([-1.4, 0.0, 0.0]))
    ar = MathTex(r"\rightarrow", font_size=34, color=S.MUTED).move_to([-0.45, 0.0, 0])
    w = V.label("can't tell", 34, S.FLAT, weight="MEDIUM")
    w.shift(np.array([0.0, 0.0, 0.0]) - w.get_left())
    return VGroup(g, ar, w)
