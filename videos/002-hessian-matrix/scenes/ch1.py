"""Chapter 1 board (scenes 03–05): the parabola, its tangent, the split-screen slope
graph. Every layout is a pure function of a few numbers, so scene N can rebuild the
exact last frame of scene N−1."""

from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Axes, DecimalNumber, Line, MathTex, Polygon,
                   VGroup, VMobject, always_redraw)

from aion import style as S
import shared as V

SPLIT_SCALE = 0.56
TOP_ORIGIN = np.array([-1.7, 0.55, 0.0])
BOT_ORIGIN = np.array([-1.7, -2.2, 0.0])
READOUT_FULL = np.array([3.6, 2.9, 0.0])
READOUT_SPLIT = np.array([3.3, 2.3, 0.0])
FPP_POS = np.array([3.3, -1.6, 0.0])         # where "f''(x) = 2" sits (right of the slope panel)
GAUGE_POS = np.array([3.3, -0.35, 0.0])
FLIP_RISE = 2.55                              # top panel origin 0.55 → 3.1 for −x²
PEAK_ORIGIN = np.array([0.0, 1.2, 0.0])       # full-size −x² with its peak on screen


def parabola(ax: Axes, s: float = 1.0, color=S.TERRAIN_LINE):
    return V.lit(ax.plot(lambda x: s * x * x, x_range=[-2.1, 2.1]), color)


def eq_label(s: float = 1.0) -> MathTex:
    m = MathTex("y", "=", "-" if s < 0 else "", "x^2", font_size=48, color=S.TEXT)
    return m.to_corner(UP + LEFT, buff=0.55)


def split(group: VGroup, ax: Axes) -> VGroup:
    """Apply the split-screen transform: shrink about the origin, move to the top panel."""
    o = ax.c2p(0, 0)
    group.scale(SPLIT_SCALE, about_point=o)
    group.shift(TOP_ORIGIN - o)
    return group


def slope_axes() -> Axes:
    ax = Axes(x_range=(-3, 3, 1), y_range=(-4.5, 4.5, 1), x_length=V.CH1_XL * SPLIT_SCALE,
              y_length=2.9, tips=False, axis_config={"tick_size": 0.05})
    ax.shift(BOT_ORIGIN - ax.c2p(0, 0))
    return V.hairline(ax)


def slope_axes_label(ax2: Axes):
    return V.label("slope", 24, S.GRAD).next_to(ax2.c2p(-3, 4.5), LEFT, buff=0.25)   # outside the plot


def readout(x0, s: float = 1.0) -> VGroup:
    """'slope = f'(x0) = <value>' that follows the x0 tracker."""
    head = MathTex(r"f'(x_0)", "=", font_size=40, color=S.TEXT)
    head[0].set_color(S.GRAD)
    sv = s if callable(s) else (lambda: s)
    num = DecimalNumber(2 * sv() * x0.get_value(), num_decimal_places=1, include_sign=False,
                        font_size=40, color=S.GRAD)
    num.add_updater(lambda m: m.set_value(2 * sv() * x0.get_value()).next_to(head, RIGHT, buff=0.18))
    return VGroup(head, num)


def tangent(ax: Axes, x0, s=lambda: 1.0, half: float = 0.8) -> VMobject:
    def make():
        a, k = x0.get_value(), s() if callable(s) else s
        line = V.tangent_line(ax, lambda x: k * x * x, lambda x: 2 * k * x, a, half=half)
        dot = V.lit(V.Dot(ax.c2p(a, k * a * a), radius=0.07, color=S.GRAD), S.GRAD, 0, 10, 0.25)
        return VGroup(line, dot)
    return always_redraw(make)


def rise_run(ax2: Axes, x_a: float, s: float = 1.0) -> VGroup:
    """Run 1, rise 2s triangle on the slope line y = 2s x, starting at x_a."""
    p0, p1, p2 = ax2.c2p(x_a, 2 * s * x_a), ax2.c2p(x_a + 1, 2 * s * x_a), ax2.c2p(x_a + 1, 2 * s * (x_a + 1))
    tri = Polygon(p0, p1, p2, stroke_width=0).set_fill(S.GRAD, 0.18)
    run = Line(p0, p1, color=S.MUTED, stroke_width=3)
    rise = Line(p1, p2, color=S.SMILE if s > 0 else S.FROWN, stroke_width=4)
    l1 = MathTex("1", font_size=28, color=S.MUTED).next_to(run, DOWN if s > 0 else UP, buff=0.08)
    l2 = MathTex(f"{2 * s:g}", font_size=28, color=S.SMILE if s > 0 else S.FROWN).next_to(rise, RIGHT, buff=0.08)
    return VGroup(tri, run, rise, l1, l2)


# ── right-hand column used once the board is full-size again (scenes 04–05) ──
COL_X = 5.35
GAUGE_FULL = np.array([COL_X, 0.9, 0.0])
FPP_FULL = np.array([COL_X, -0.25, 0.0])

COS_ORIGIN = np.array([-1.1, -1.2, 0.0])


def cos_axes() -> Axes:
    import math
    ax = Axes(x_range=(-2 * math.pi, 2 * math.pi, math.pi / 2), y_range=(-1.5, 1.5, 0.5),
              x_length=9.0, y_length=4.2, tips=False, axis_config={"tick_size": 0.06})
    ax.shift(COS_ORIGIN - ax.c2p(0, 0))
    return V.hairline(ax)


def cos_plot(ax: Axes, color=S.TERRAIN_LINE):
    import math
    return V.lit(ax.plot(math.cos, x_range=[-2 * math.pi, 2 * math.pi]), color)


def cos_label() -> MathTex:
    return MathTex("y", "=", r"\cos x", font_size=48, color=S.TEXT).to_corner(UP + LEFT, buff=0.55)


def flat_tangent(ax: Axes, x0: float, y0: float, half: float = 0.9) -> VGroup:
    return VGroup(V.lit(Line(ax.c2p(x0 - half, y0), ax.c2p(x0 + half, y0)), S.GRAD, 4.5),
                  V.Dot(ax.c2p(x0, y0), radius=0.08, color=S.GRAD))


def fpp_peak() -> MathTex:
    m = MathTex("f''(0)", "=", "-1", font_size=46, color=S.TEXT).move_to(FPP_FULL)
    m[2].set_color(S.FROWN)
    return m


BEND_TAG_FULL = np.array([COL_X, 1.75, 0.0])


def cos_board() -> dict:
    """Scene 04's last frame: cos x with a flat tangent at its peak, the peak marked."""
    import math
    ax = cos_axes()
    d = dict(ax=ax, curve=cos_plot(ax), label=cos_label(), tan=flat_tangent(ax, 0, 1),
             down=V.lit(ax.plot(math.cos, x_range=[-1.1, 1.1]), S.FROWN, 5, 18, 0.18),
             ring=V.Circle(radius=0.22, color=S.FROWN, stroke_width=4).move_to(ax.c2p(0, 1)),
             fpp=fpp_peak(),
             tag=V.label("bending", 24, S.MUTED).move_to(BEND_TAG_FULL))
    return d


# ── scene 05: the test card and x³ ──
BOARD_SMALL = 0.62                     # the left board after "second derivative test"
BOARD_LEFT = np.array([-3.55, -0.2, 0.0])
CARD_C = np.array([3.45, -0.25, 0.0])
CARD_W, CARD_H = 5.4, 4.4
ROW_Y = (0.85, -0.35, -1.55)           # rows relative to the card centre


def cube_axes() -> Axes:
    """x³ board on the left, same footprint as the shrunken cosine board."""
    ax = Axes(x_range=(-1.6, 1.6, 0.5), y_range=(-3.0, 3.0, 1), x_length=5.4, y_length=4.4, tips=False,
              axis_config={"tick_size": 0.06})
    ax.shift(BOARD_LEFT - ax.c2p(0, 0))
    return V.hairline(ax)


def cube_plot(ax: Axes):
    return V.lit(ax.plot(lambda x: x ** 3, x_range=[-1.44, 1.44]), S.TERRAIN_LINE)


# ── the second-derivative test card (scene 05 builds it, scene 06 starts on it) ──
TEST_ROWS = ((2.0, "valley", S.SMILE), (-2.0, "peak", S.FROWN), (0.0, "can't tell", S.FLAT))


def test_card():
    """(card, head): a design-system glass card with its uppercase eyebrow, at CARD_C."""
    from aion.components.cards import card_image
    card = V.panel(CARD_W, CARD_H, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM, border=S.LINE,
                      glow=S.GLASS_TOP).move_to(CARD_C)
    head = V.hush(V.label("SECOND DERIVATIVE TEST", 20, S.MUTED, weight="BOLD"))
    head.move_to(CARD_C + UP * (CARD_H / 2 - 0.5))
    return card, head


def test_row(i: int):
    """(gauge, VGroup(f'=0, →), word) for row i of the card."""
    from aion.components.bend_gauge import BendGauge
    kv, word, color = TEST_ROWS[i]
    y = ROW_Y[i]
    g = BendGauge(kv, width=0.8, stroke=7).place(CARD_C + np.array([-1.0, y, 0]))
    flat = MathTex(r"f'=0", font_size=30, color=S.GRAD).set_opacity(0.8).move_to(CARD_C + np.array([-2.15, y, 0]))
    arrow = MathTex(r"\rightarrow", font_size=34, color=S.MUTED).move_to(CARD_C + np.array([-0.2, y, 0]))
    lab = V.label(word, 32, color, weight="MEDIUM")
    lab.shift(CARD_C + np.array([0.25, y, 0]) - lab.get_left())
    return g, VGroup(flat, arrow), lab
