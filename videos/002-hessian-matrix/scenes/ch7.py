"""Outro builders (scenes 25–26): the recap cards and the return to the fog.

Scene 26 rebuilds scene 25's last frame from these builders. The numbers on the cards
are computed and asserted here.
"""

from __future__ import annotations

import math

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Axes, Circle, Line, MathTex, ParametricFunction, ValueTracker,
                   VGroup, VMobject, always_redraw)

from aion import style as S
from aion.components.bend_gauge import BendGauge
from aion.components.cards import card_image
from aion.components.matrix_grid import HessianGrid
import shared as V
import ch3 as L3
import ch5 as C5

# ── the math on the cards ─────────────────────────────────────────────────
PUZ = np.array([[2.0, 3.0], [3.0, 2.0]])


def bend(deg: float) -> float:
    """uᵀHu for the unit vector at angle deg: 2 + 3 sin 2θ for the puzzle surface."""
    t = math.radians(deg)
    u = np.array([math.cos(t), math.sin(t)])
    return float(u @ PUZ @ u)


assert all(abs(bend(d) - (2 + 3 * math.sin(2 * math.radians(d)))) < 1e-12 for d in range(0, 360, 7))
_w, _v = np.linalg.eigh(PUZ)
assert np.allclose(_w, [-1, 5])
assert np.allclose(abs(_v[:, 1]), [math.sqrt(0.5)] * 2) and _v[0, 0] * _v[1, 0] < 0   # λ=5 at 45°, λ=−1 at 135°
assert abs(bend(45) - 5) < 1e-12 and abs(bend(135) + 1) < 1e-12

# ── the 2×2 of cards ──────────────────────────────────────────────────────
CARD_W, CARD_H = 5.8, 3.3
CARD_C = [np.array(p, float) for p in ((-3.2, 1.9, 0), (3.2, 1.9, 0), (-3.2, -1.9, 0), (3.2, -1.9, 0))]
EYEBROWS = ("ON A LINE", "ON A SURFACE", "ANY DIRECTION", "AT A FLAT POINT")


def card(i: int) -> VGroup:
    c = CARD_C[i]
    bg = card_image(CARD_W, CARD_H, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM, border=S.LINE,
                    glow=S.GLASS_TOP).move_to(c)
    eb = V.label(EYEBROWS[i], 18, S.MUTED, weight="BOLD")
    eb.move_to(c + np.array([-CARD_W / 2 + 0.35, CARD_H / 2 - 0.36, 0]), aligned_edge=LEFT)
    return bg, eb


def body(i: int) -> np.ndarray:
    return CARD_C[i] + DOWN * 0.18


# card 1 · on a line: the parabola, a smile and a frown
def parabola() -> VMobject:
    c = body(0) + LEFT * 1.15
    p = ParametricFunction(lambda t: c + np.array([0.95 * t, 0.95 * (t * t - 0.55), 0]), t_range=[-1.15, 1.15])
    return V.lit(p, S.TERRAIN_LINE, width=3, halo=12, opacity=0.12)


def line_gauge(sign: int) -> VGroup:
    c = body(0) + RIGHT * 0.75 + (UP * 0.42 if sign > 0 else DOWN * 0.55)
    g = BendGauge(2.0 * sign, width=0.9, stroke=6).place(c)
    t = MathTex("f''", ">" if sign > 0 else "<", "0", font_size=32, color=S.TEXT)
    t[0].set_color(S.SMILE if sign > 0 else S.FROWN)
    t.next_to(c, RIGHT, buff=0.7)
    return VGroup(g, t)


# card 2 · on a surface: the colored grid
def hgrid() -> tuple[HessianGrid, list, MathTex]:
    g = L3.glass(HessianGrid(cell=0.6, gap=0.08, center=body(1) + RIGHT * 0.45, tint_scale=L3.TINT))
    ents = [MathTex(t, font_size=30, color=col) for t, col in
            ((r"f_{xx}", S.HX), (r"f_{xy}", S.TWIST), (r"f_{yx}", S.TWIST), (r"f_{yy}", S.HY))]
    lab = MathTex("H", "=", font_size=40, color=S.TEXT)
    return g, ents, lab


CELLS = ((0, 0), (0, 1), (1, 0), (1, 1))
CELL_COL = (S.HX, S.TWIST, S.TWIST, S.HY)


def fill_grid(g, ents, lab):
    """Static final state of card 2 (entries, tints, brackets, 'H =')."""
    for (i, j), m, col in zip(CELLS, ents, CELL_COL):
        g.fill(i, j, m)
        c = g.cells[i][j]
        c.set_fill(col, 0.35 * g.tint_scale).set_stroke(col, 2.5, opacity=1.0)
    g.show_brackets()
    g.brackets.set_stroke(width=2.5)
    lab.next_to(g.brackets, LEFT, buff=0.18)
    return VGroup(g, lab)


# card 3 · any direction: the dial, the eigen-axes, the eigenvalues
DIAL_C = body(2) + LEFT * 0.55
DIAL_R = 0.95
GAUGE_C = body(2) + RIGHT * 1.85


def dial() -> Circle:
    c = Circle(radius=DIAL_R).move_to(DIAL_C)
    return c.set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.5)


def u_arrow(th: ValueTracker):
    def make():
        t = math.radians(th.get_value())
        tip = DIAL_C + DIAL_R * np.array([math.cos(t), math.sin(t), 0])
        from manim import Arrow
        return Arrow(DIAL_C, tip, buff=0, stroke_width=4, color=S.TEXT, max_tip_length_to_length_ratio=0.22)
    return always_redraw(make)


def dial_gauge(th: ValueTracker) -> VGroup:
    k = ValueTracker(bend(th.get_value()))
    k.add_updater(lambda m: m.set_value(bend(th.get_value())))
    g = BendGauge(k, width=1.0, gain=0.12, stroke=6, readout=True, decimals=1, font_size=30).place(GAUGE_C)
    return VGroup(g), k


def eigen_axes() -> VGroup:
    out = VGroup()
    for deg, col in ((45.0, S.SMILE), (135.0, S.FROWN)):
        d = np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0])
        out.add(V.lit(Line(DIAL_C - 1.2 * DIAL_R * d, DIAL_C + 1.2 * DIAL_R * d), col, width=3, halo=12,
                      opacity=0.15))
    return out


def eigen_labels() -> VGroup:
    a = MathTex(r"\lambda_1", "=", "5", font_size=30, color=S.TEXT)
    a[2].set_color(S.SMILE)
    b = MathTex(r"\lambda_2", "=", "-1", font_size=30, color=S.TEXT)
    b[2].set_color(S.FROWN)
    d1 = np.array([math.cos(math.radians(45)), math.sin(math.radians(45)), 0])
    d2 = np.array([math.cos(math.radians(135)), math.sin(math.radians(135)), 0])
    a.next_to(DIAL_C + 1.2 * DIAL_R * d1, RIGHT, buff=0.08)
    b.next_to(DIAL_C + 1.2 * DIAL_R * d2, LEFT, buff=0.08)
    return VGroup(a, b)


# card 4 · at a flat point: the sign chart
def mini_chart() -> Axes:
    ax = Axes(x_range=[-C5.CH_R, C5.CH_R, 2], y_range=[-C5.CH_R, C5.CH_R, 2], x_length=2.5, y_length=2.5,
              tips=False, axis_config={"include_ticks": False}).move_to(body(3))
    return V.hairline(ax)


def mini_axis_labels(ax) -> VGroup:
    return VGroup(MathTex(r"\lambda_1", font_size=26, color=S.MUTED).next_to(ax.c2p(C5.CH_R, 0), RIGHT, buff=0.1),
                  MathTex(r"\lambda_2", font_size=26, color=S.MUTED).next_to(ax.c2p(0, C5.CH_R), RIGHT, buff=0.1))


def mini_word(ax, q: int):
    word, col = {1: ("valley", S.SMILE), 2: ("saddle", S.TEXT), 3: ("peak", S.FROWN), 4: ("saddle", S.TEXT)}[q]
    pos = {1: (3, 3), 2: (-3, 3), 3: (-3, -3), 4: (3, -3)}[q]
    return V.label(word, 18, col, weight="MEDIUM").move_to(ax.c2p(*pos))


def big_brackets() -> VGroup:
    """The 2×2 of cards closed into a matrix."""
    h, x, hook = 2 * CARD_H + 0.8, 6.3, 0.3
    l = VMobject().set_points_as_corners([[-x + hook, h / 2, 0], [-x, h / 2, 0], [-x, -h / 2, 0], [-x + hook, -h / 2, 0]])
    r = VMobject().set_points_as_corners([[x - hook, h / 2, 0], [x, h / 2, 0], [x, -h / 2, 0], [x - hook, -h / 2, 0]])
    return VGroup(*[V.lit(b, S.TERRAIN_LINE, width=3.5, halo=14, opacity=0.12) for b in (l, r)])


def s25_end() -> VGroup:
    """Every card complete, the brackets closed, the chart tinted."""
    out = VGroup()
    cards = [card(i) for i in range(4)]
    g, ents, lab = hgrid()
    th = ValueTracker(45.0)
    dg, _k = dial_gauge(th)
    _k.clear_updaters()
    ax = mini_chart()
    quads = VGroup(*[C5.quadrant(ax, q) for q in (1, 2, 3, 4)])
    from manim import Group
    out = Group(*[m for c in cards for m in c],
                parabola(), line_gauge(1), line_gauge(-1),
                fill_grid(g, ents, lab),
                dial(), eigen_axes(), u_arrow(th), dg, eigen_labels(),
                quads, ax, mini_axis_labels(ax), *[mini_word(ax, q) for q in (1, 2, 3, 4)],
                big_brackets())
    return out


# ── scene 26: back to the fog ─────────────────────────────────────────────
FOG = dict(H=(0.0, 0.0, 0.0), reveal=60.0, dist=6.2, pitch=10.0, yaw=200.0, target=(0.0, 0.0, 0.7),
           fog=0.34, fognear=1.8, mist=1.0, haze=0.9, disc_r=V.DISC_R, disc_a=0.8)
LIFT = dict(H=V.H_SADDLE, dist=7.0, pitch=22.0, yaw=215.0, target=(0.0, 0.0, 0.3), fog=0.06, fognear=3.0,
            mist=0.5, haze=0.25, contour=1.0, grid=0.22, tint=1.0, disc_a=0.6, fwd=1.0, side=1.0)
