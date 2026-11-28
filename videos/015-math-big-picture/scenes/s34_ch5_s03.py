"""ch5_s03 · The curve that is its own slope.

y = eˣ (C.change) on a Classic grid. On 'steepness' a slope triangle rides the curve: its tangent meets the x-axis one
unit back, so the run is 1 and the rise is the height itself; the tags read slope = height (1.00, 2.72, 4.48 at
x = 0, 1, 1.5). On 'height' d/dx eˣ = eˣ writes. On 'savings' a card compounds $1 at 100% for a year: yearly 2.00,
monthly 2.61, daily 2.71; on 'two point seven' every instant: 2.71828…. On 'e' the curve is labelled eˣ; on 'Euler' the
glyph e flies to the e, i, π tracker from Chapter 3.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, sans, tex, window

EO, SX, SY = P3(-3.3, -2.6), 1.3, 1.0           # graph origin and scale
X_LO, X_HI = -2.5, 1.7
CARD_C = P3(3.95, -0.25)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def to_s(x, y):
    return EO + P3(SX * x, SY * y)


@scene(T.ch5_s03, T.ch5_s04)
def ch5_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    g_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_st, t_sv, t_27 = float(T.ch5_s03_steepness), float(T.ch5_s03_savings), float(T.ch5_s03_two_point_seven)
    t_e, t_eu = float(T.ch5_s03_e), float(T.ch5_s03_euler)
    t_h = t_st + 1.36                                                        # 'height'
    Ch = C.change
    out_t = t1 - 0.8

    # the Classic grid and axes
    grid = VGroup()
    for x in range(-2, 2):
        grid.add(Line(to_s(x, 0), to_s(x, 5.4), stroke_color=C.grid, stroke_width=1.4))
    for y in range(1, 6):
        grid.add(Line(to_s(X_LO, y), to_s(X_HI, y), stroke_color=C.grid, stroke_width=1.4))
    axes = VGroup(Arrow(to_s(X_LO, 0), to_s(X_HI + 0.25, 0), buff=0, stroke_width=3, color=C.axis, tip_length=0.2),
                  Arrow(to_s(0, -0.25), to_s(0, 5.6), buff=0, stroke_width=3, color=C.axis, tip_length=0.2))
    nums = VGroup(*(tex(str(x), 30, C.muted).move_to(to_s(x, 0) + P3(0, -0.35)) for x in (-2, -1, 1)),
                  *(tex(str(y), 30, C.muted).move_to(to_s(0, y) + P3(-0.3, 0)) for y in (1, 2, 3, 4, 5)))
    g_l.play(FadeIn(grid), Create(axes), FadeIn(nums), at=t0 + 0.3, dur=0.8)
    xs = np.linspace(X_LO, X_HI, 200)
    curve = VMobject(stroke_color=Ch, stroke_width=5).set_points_smoothly([to_s(x, math.exp(x)) for x in xs])
    m.play(Create(curve), at=t0 + 0.7, dur=1.4, ease="easy_ease")

    # 'steepness': the slope triangle riding the curve; its run is 1, so its rise is the height
    xk = keys((t_st - 0.2, 0.0), (t_st + 0.9, 0.0), (t_st + 1.9, 1.0, "easy_ease"), (t_st + 2.9, 1.0),
              (t_st + 3.7, 1.5, "easy_ease"))

    def tri(t):
        x = xk(t)
        y = math.exp(x)
        f = ss((t - t_st + 0.2) / 0.4) * (1 - ss((t - t_sv + 0.6) / 0.5)) * 1.0
        if f <= 0:
            return VGroup()
        p, foot, back = to_s(x, y), to_s(x, 0), to_s(x - 1, 0)
        d = (p - back) / np.linalg.norm(p - back)
        g = VGroup(Line(back - 0.4 * d, p + 0.9 * d, stroke_color=C.text, stroke_width=2.6, stroke_opacity=f),
                   Line(back, foot, stroke_color=C.text, stroke_width=3, stroke_opacity=f),
                   Line(foot, p, stroke_color=C.circle, stroke_width=5, stroke_opacity=f),
                   Dot(p, radius=0.09, color=C.text).set_opacity(f))
        g.add(tex("1", 30, C.text).move_to((back + foot) / 2 + P3(0.12, 0.28)).set_opacity(f))
        g.add(tex(f"{y:.2f}", 34, C.circle).next_to(Line(foot, p), RIGHT, buff=0.14).set_opacity(f))
        return g

    top.redraw(window(tri, t_st - 0.2, t_sv), during=(t_st - 0.2, t_sv + 0.05))
    tag = VGroup(sans("slope", 30, C.text), tex("=", 36, C.text), sans("height", 30, C.circle))
    tag.arrange(RIGHT, buff=0.16).move_to(P3(3.95, 0.9))
    m.play(FadeIn(tag, shift=0.08 * DOWN), at=t_st + 0.2, dur=0.5)
    deq = MathTex(r"\frac{d}{dx}", "e^x", "=", "e^x", font_size=56, color=C.text)
    deq[1].set_color(Ch)
    deq[3].set_color(Ch)
    deq.move_to(P3(3.95, 2.75))
    m.play(Write(deq), at=t_h, dur=0.9)

    # 'savings': $1 at 100% for a year, compounded more and more often
    box = RoundedRectangle(width=5.0, height=3.6, corner_radius=0.16, stroke_color=C.map_off, stroke_width=1.8)
    box.move_to(CARD_C)
    head = sans(r"\$1 at 100\% for a year", 28, C.muted).move_to(CARD_C + P3(0, 1.4))
    rows = []
    for k, (lab, n) in enumerate((("yearly", 1), ("monthly", 12), ("daily", 365))):
        y = CARD_C[1] + 0.65 - 0.66 * k
        val = (1 + 1 / n) ** n
        r_ = VGroup(sans(lab, 28, C.text).move_to(P3(1.95, y), aligned_edge=LEFT),
                    tex(rf"\left(1+\tfrac{{1}}{{{n}}}\right)^{{{n}}}" if n > 1 else r"(1+1)^1", 34, C.muted)
                    .move_to(P3(4.15, y)),
                    tex(f"{math.floor(val * 100) / 100:.2f}", 36, Ch).move_to(P3(6.0, y), aligned_edge=RIGHT))
        rows.append(r_)
    y4 = CARD_C[1] - 1.35
    cont = VGroup(sans("every instant", 28, C.text).move_to(P3(1.95, y4), aligned_edge=LEFT),
                  tex(r"2.71828\ldots", 40, Ch).move_to(P3(6.0, y4), aligned_edge=RIGHT))
    rule = Line(P3(1.85, y4 + 0.36), P3(6.05, y4 + 0.36), stroke_color=C.map_off, stroke_width=1.4)
    m.play(Create(box), FadeIn(head), at=t_sv - 0.3, dur=0.6)
    for k, r_ in enumerate(rows):
        m.play(FadeIn(r_, shift=0.06 * UP), at=t_sv + 0.4 + 1.1 * k, dur=0.5)
    m.play(Create(rule), at=t_27 - 0.3, dur=0.4)
    m.play(FadeIn(cont, shift=0.06 * UP), at=t_27, dur=0.6)

    # 'e': the curve's name
    name = MathTex("y", "=", "e^x", font_size=48, color=C.text)
    name[2].set_color(Ch)
    name.move_to(to_s(0.78, 4.6))
    m.play(FadeOut(tag), at=t_sv - 0.3, dur=0.4)
    m.play(Write(name), at=t_e - 0.1, dur=0.7)
    big_e = tex("e", 60, Ch).move_to(P3(2.15, y4))
    eq_ = tex("=", 44, C.text).move_to(P3(2.75, y4))
    m.play(FadeOut(cont[0]), at=t_e - 0.2, dur=0.3)
    m.play(FadeIn(big_e, scale=1.4), FadeIn(eq_), at=t_e, dur=0.5)

    # 'Euler': the glyph joins the e, i, π tracker
    tb = RoundedRectangle(width=1.95, height=0.78, corner_radius=0.14, stroke_color=C.map_off, stroke_width=1.6)
    tb.move_to(P3(5.75, -3.35))
    tracked = VGroup(tex("e", 40, Ch), tex("i", 40, C.structure), tex(r"\pi", 40, C.quantity))
    tracked.arrange(RIGHT, buff=0.38).move_to(tb)
    m.play(FadeIn(tb), FadeIn(tracked[1:]), at=t_eu - 0.6, dur=0.5)
    fly = big_e.copy()
    top.add(fly, at=t_eu)
    top.play(Transform(fly, tracked[0]), at=t_eu, dur=0.8, ease="easy_ease")
    top.play(Indicate(fly, color=Ch, scale_factor=1.3), at=t_eu + 0.9, dur=0.6)

    # out
    m.play(FadeOut(VGroup(curve, deq, box, head, *rows, rule, cont, name, big_e, eq_, tb, tracked[1:])), at=out_t,
           dur=0.6)
    top.play(FadeOut(fly), at=out_t, dur=0.6)
    g_l.play(FadeOut(VGroup(grid, axes, nums)), at=out_t, dur=0.6)
