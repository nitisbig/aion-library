"""ch3_s04 · A quarter turn is a number.

A number line, −2 to 2, and a violet arrow from 0 to 1. On 'minus one' it swings through a half turn to −1 and
(−1)·1 = −1 writes. On 'quarter turn' a grey ghost arrow lifts and hesitates at 90° with a question mark. On 'i' the
arrow itself lifts off the line to the top, labelled i, and the plane's grid fades in behind. On 'twice' a second
quarter turn lands on −1, each quarter marked by its own arc, and i · i = i² = −1 writes. On 'square root' i = √−1
joins; the arrow makes its quarter turn once more and on 'plane' the grid brightens to full.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import glow_layer, PL_O as O, PL_U as U, P3, plane_grid, plane_line, tex, window
XC = 3.9


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ramp(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if t <= tb:
            return va + (vb - va) * ss((t - ta) / max(tb - ta, 1e-6))
    return keys[-1][1]


def arrow_at(deg, col=None, opacity=1.0):
    a = math.radians(deg)
    return Arrow(O, O + U * P3(math.cos(a), math.sin(a)), buff=0, stroke_width=6, color=col or C.structure,
                 max_tip_length_to_length_ratio=0.16, stroke_opacity=opacity, fill_opacity=opacity)


@scene(T.ch3_s04, T.ch3_s05)
def ch3_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    grid_l, m = s.manim(z=-1), s.manim(z=0)
    top = glow_layer(s, z=1, color=C.structure)                     # the arrow is the lit thing here
    t0 = float(s.start)
    t_m1, t_qt, t_i = float(T.ch3_s04_minus_one), float(T.ch3_s04_quarter_turn), float(T.ch3_s04_i)
    t_tw, t_pl = float(T.ch3_s04_twice), float(T.ch3_s04_plane)
    V = C.structure

    nl = plane_line()
    m.play(Create(nl[0]), at=t0 + 0.3, dur=0.8)
    m.play(LaggedStart(*(FadeIn(x_) for x_ in nl[1:]), lag_ratio=0.05), at=t0 + 0.6, dur=0.7)

    # the arrow: one angle track, with two resets hidden by a quick fade
    tj1, tj2 = t_qt - 1.6, t_pl - 2.9
    keys = [(t0, 0), (t_m1 + 0.6, 0), (t_m1 + 2.6, 180), (tj1 - 0.01, 180), (tj1, 0), (t_i - 0.6, 0), (t_i + 0.2, 90),
            (t_tw + 0.05, 90), (t_tw + 1.25, 180), (tj2 - 0.01, 180), (tj2, 0), (tj2 + 0.6, 0), (tj2 + 1.6, 90)]

    def arrow(t):
        deg = ramp(t, keys)
        f = min(1.0, abs(t - tj1) / 0.3, abs(t - tj2) / 0.3, ss((t - t0 - 1.0) / 0.4))
        g = VGroup()
        if t < tj1 and deg > 0.5:                                     # the half turn's arc
            g.add(Arc(radius=0.55 * U, start_angle=0, angle=math.radians(deg), arc_center=O, stroke_color=V,
                      stroke_width=3, stroke_opacity=0.8 * f))
        if t_i - 0.6 < t < tj2:                                       # each quarter turn its own arc
            g.add(Arc(radius=0.4 * U, start_angle=0, angle=math.radians(min(deg, 90)), arc_center=O, stroke_color=V,
                      stroke_width=3, stroke_opacity=0.9 * f))
            if deg > 90.5:
                g.add(Arc(radius=0.55 * U, start_angle=math.pi / 2, angle=math.radians(deg - 90), arc_center=O,
                          stroke_color=V, stroke_width=3, stroke_opacity=0.9 * f))
        lag = ramp(t - 0.3, keys)                                     # a comet tail along the tip's path
        if f > 0.01 and abs(deg - lag) > 2 and abs(deg - lag) < 120:
            n = 8
            for k in range(n):
                a0 = lag + (deg - lag) * k / n
                g.add(Arc(radius=U, start_angle=math.radians(a0), angle=math.radians((deg - lag) / n), arc_center=O,
                          stroke_color=V, stroke_width=2 + 4 * k / n, stroke_opacity=f * (k + 1) / n))
        if f > 0.01:
            g.add(arrow_at(deg, opacity=f))
        return g

    top.redraw(window(arrow, t0 + 1.0, float(s.end)), during=(t0 + 1.0, float(s.end)))

    E1 = tex(r"(-1)\cdot 1 = -1", 50, C.text).move_to(P3(XC, 2.5))
    m.play(Write(E1), at=t_m1 + 0.9, dur=0.9)

    # 'quarter turn': a ghost arrow lifts and hesitates
    def ghost(t):
        u = ss((t - t_qt - 0.1) / 0.6)
        h = 0.08 * math.sin(6 * max(t - t_qt - 0.7, 0)) * math.exp(-1.5 * max(t - t_qt - 0.7, 0))
        deg = 90 * u * (0.92 + h) if u < 1 else 90 * (0.92 + h)
        return arrow_at(deg, C.muted, opacity=0.8)

    gh_end = t_i - 0.6
    m.redraw(window(ghost, t_qt, gh_end), during=(t_qt, gh_end))
    q = tex("?", 56, C.muted).move_to(O + P3(0.45, U + 0.35))
    m.play(FadeIn(q, scale=0.7), at=t_qt + 0.6, dur=0.4)
    m.play(FadeOut(q), at=gh_end - 0.3, dur=0.3)

    # 'i': the arrow lifts into the plane
    grid_dim, grid_full = plane_grid(0.35), plane_grid(1.0)
    grid_l.play(FadeIn(grid_dim), at=t_i - 0.3, dur=0.9)
    i_lab = tex("i", 48, V).move_to(O + P3(0.32, U + 0.2))
    m.play(FadeIn(i_lab, scale=0.7), at=t_i, dur=0.4)

    # 'twice': i · i = −1
    E2 = MathTex("i", r"\cdot", "i", "=", "i^2", "=", "-1", font_size=50, color=C.text).move_to(P3(XC, 1.3))
    for k in (0, 2, 4):
        E2[k].set_color(V)
    m.play(Write(E2), at=t_tw + 1.4, dur=1.1)
    m.play(E1.animate.set_opacity(0.45), at=t_tw + 1.4, dur=0.5)
    E3 = MathTex("i", "=", r"\sqrt{-1}", font_size=50, color=C.text).move_to(P3(XC, 0.1))
    E3[0].set_color(V)
    m.play(Write(E3), at=tj2 - 1.1, dur=0.9)

    # 'plane': the grid at full strength
    grid_l.play(FadeIn(grid_full), at=t_pl - 0.6, dur=0.9)
    grid_l.remove(grid_dim, at=t_pl + 0.35)
    m.play(FadeOut(VGroup(E1, E2, E3)), at=float(s.end) - 0.6, dur=0.5)
