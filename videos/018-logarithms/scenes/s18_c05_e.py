"""c05_s03 · e, and doubling time. Storyboard: plan/scene_plan.md § c05_s03.

The right edge slides out from 1 with a big readout of the area (ln x, exact), easing to a stop at the point where the
area is 1: x = e = 2.71828 (logdata, brentq). ln x = ∫₁ˣ dt/t writes. On "slope", y = ln x draws on the same axes and a
tangent slides along it; a dashed link drops to the hyperbola at the same x and the slope readout equals its height.
Then the frame clears to a worked example: growth e^{0.07t}, doubling line, t = ln 2 / 0.07 ≈ 9.9, rule of seventy.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from ch5 import CX, col, edge, hyper_plane, hyperbola, region
from kit import P3, add_rail, chapter_break, ctex, glow, polyline, ramp, smooth01, tex, tint, word_at

E = ld.E_FROM_AREA


@scene(T.c05_s03, T.c06_s01)
def s18_c05_e(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 5)
    chapter_break(s, 6, T.c06_s01)
    t0, end = float(T.c05_s03), float(s.end)
    t7 = float(T.c05_s03_seven_percent)
    part1 = Track(lambda t: 1 - ramp(t, t7 - 0.9, 0.7))
    grid, X, Y = hyper_plane()
    m = s.manim(z=3, opacity=part1)
    m.add(grid, hyperbola(X, Y), at=t0)
    a = s.manim(z=2, opacity=part1)

    # the edge slides out until the area is exactly 1
    tsl, t1 = float(T.c05_s03_slide_the_right_edge), float(T.c05_s03_exactly_one)
    s0, s1 = tsl - 0.2, t1 + 0.35

    def xe(t):
        u = min(max((t - s0) / (s1 - s0), 0.0), 1.0)
        return 1 + (E - 1) * (1 - (1 - u) ** 3)       # ease out: lands at e as the readout reaches 1.000
    a.redraw(lambda t: region(X, Y, 1, xe(t), opacity=0.36), during=(s0, t7))
    ge = glow(s, C.natural, z=4, k=0.9, opacity=part1)
    ge.redraw(lambda t: edge(X, Y, xe(t)) if xe(t) > 1.005 else VGroup(), during=(s0, t7))

    def readout(t):
        v = math.log(xe(t))
        col = C.natural if t >= s1 else C.steps
        return ctex([(r"\text{area}=", C.area), (f"{v:.3f}", col)], 54).move_to(P3(CX, 2.55))
    m.redraw(readout, during=(s0, t7))

    te = float(T.c05_s03_two_point_seven_one_)
    eg = glow(s, C.natural, z=4, k=1.0, opacity=part1)
    eg.play(FadeIn(Dot(P3(X(E), Y(0)), radius=0.09, color=C.natural), scale=1.8), at=te, dur=0.5)
    m.play(FadeIn(tex("e", 36, C.natural).next_to(P3(X(E), Y(0)), DOWN, buff=0.36)), at=te + 0.2, dur=0.4)
    ev = ctex([("x=", None), ("e", C.natural), (r"=2.71828\ldots", None)], 44).move_to(P3(CX, 1.75))
    m.play(Write(ev), at=te, dur=1.6)

    # the natural logarithm
    tn = float(T.c05_s03_natural_logarithm)
    ln_def = ctex([(r"\ln x", C.natural), ("=", None), (r"\int_1^x\frac{dt}{t}", C.area)], 46).move_to(P3(CX, 0.65))
    m.play(Write(ln_def), at=tn, dur=1.2)

    # slope: y = ln x on the same axes, a tangent linked to the height of 1/x
    tsp = float(T.c05_s03_slope)
    xl = np.geomspace(1, 7.2, 200)
    lnc = polyline([(X(x), Y(math.log(x))) for x in xl], C.natural, 4)
    m.play(Create(lnc), at=tsp - 0.3, dur=1.4)
    m.play(FadeIn(tex(r"y=\ln x", 30, C.natural).move_to(P3(X(6.2), Y(math.log(6.2)) + 0.38))), at=tsp + 0.6, dur=0.5)
    a0, a1 = tsp + 1.2, t7 - 1.6
    x0 = lambda t: 1.2 + 3.8 * smooth01(min(max((t - a0) / (a1 - a0), 0.0), 1.0))  # noqa: E731

    def tangent(t):
        x = x0(t)
        k = 1 / x
        h = 0.75 / math.sqrt(1 + k * k)
        p = P3(X(x), Y(math.log(x)))
        q = P3(X(x), Y(1 / x))
        g = VGroup(Line(P3(X(x - h), Y(math.log(x) - k * h)), P3(X(x + h), Y(math.log(x) + k * h)),
                        stroke_color=C.base, stroke_width=3),
                   DashedLine(p, q, stroke_color=tint(C.text, 0.4), stroke_width=1.5, dash_length=0.06),
                   Dot(p, radius=0.06, color=C.base), Dot(q, radius=0.06, color=C.text),
                   ctex([(r"\text{slope}=", C.base), (f"{k:.2f}", C.base)], 26).next_to(p, UP + LEFT, buff=0.1),
                   ctex([(r"\tfrac1x=", None), (f"{k:.2f}", None)], 26).next_to(q, UP + RIGHT, buff=0.08))
        return g
    m.redraw(tangent, during=(a0 - 0.1, t7))
    dd = ctex([(r"\frac{d}{dx}", None), (r"\ln x", C.natural), ("=", None), (r"\frac1x", None)], 46)
    dd.move_to(P3(CX, -0.65))
    m.play(Write(dd), at=a0 + 1.4, dur=1.0)

    # worked example: doubling time at 7 % a year
    g2 = s.manim(z=3)
    GX, GY, UT, UA = -6.0, -2.55, 0.56, 1.55
    TX = lambda v: GX + UT * v  # noqa: E731
    AY = lambda v: GY + UA * v  # noqa: E731
    ax = VGroup()
    for v in range(0, 15, 2):
        ax.add(Line(P3(TX(v), AY(0)), P3(TX(v), AY(2.8)), stroke_color=C.grid_minor if v % 4 else C.grid,
                    stroke_width=1.2),
               tex(str(v), 22, C.muted).next_to(P3(TX(v), AY(0)), DOWN, buff=0.08))
    for v in (0.5, 1.0, 1.5, 2.0, 2.5):
        ax.add(Line(P3(TX(0), AY(v)), P3(TX(14), AY(v)), stroke_color=C.grid if v % 1 == 0 else C.grid_minor,
                    stroke_width=1.2))
    ax.add(Line(P3(TX(0), AY(0)), P3(TX(14.3), AY(0)), stroke_color=C.axis, stroke_width=2.4),
           Line(P3(TX(0), AY(0)), P3(TX(0), AY(2.9)), stroke_color=C.axis, stroke_width=2.4),
           tex(r"t\ \text{(years)}", 24, C.muted).next_to(P3(TX(14.3), AY(0)), UP, buff=0.12).shift(LEFT * 0.4),
           tex("1", 22, C.muted).next_to(P3(TX(0), AY(1)), LEFT, buff=0.1),
           tex("2", 22, C.value).next_to(P3(TX(0), AY(2)), LEFT, buff=0.1))
    g2.play(FadeIn(ax), at=t7 - 0.2, dur=0.7)
    r = ld.GROWTH_RATE
    gc = polyline([(TX(v), AY(math.exp(r * v))) for v in np.linspace(0, 14, 150)], C.natural, 4)
    g2.play(Create(gc), at=t7 + 0.2, dur=1.6)
    g2.play(FadeIn(tex(r"A=e^{0.07t}", 32, C.natural).move_to(P3(TX(4.0), AY(1.75)))), at=t7 + 1.0, dur=0.5)
    dbl = DashedLine(P3(TX(0), AY(2)), P3(TX(14), AY(2)), stroke_color=tint(C.value, 0.7), stroke_width=2,
                     dash_length=0.09)
    g2.play(Create(dbl), at=t7 + 1.3, dur=0.8)

    th = float(T.c05_s03_how_long)
    pc = P3(TX(ld.DOUBLING_T), AY(2))
    q = ctex([("e^{0.07t}", C.natural), ("=", None), ("2", C.value)], 50).move_to(P3(CX, 2.5))
    g2.play(Write(q), at=th, dur=0.8)
    qm = tex("?", 36, C.steps).next_to(pc, UP + LEFT, buff=0.12)
    g2.play(FadeIn(qm), at=th + 0.5, dur=0.4)
    pg = glow(s, C.steps, z=4, k=0.9)
    pg.redraw(lambda t: Dot(pc, radius=0.07 + 0.03 * (0.5 + 0.5 * math.sin(2 * math.pi * 1.2 * (t - th))),
                            color=C.steps), during=(th + 0.4, end))

    tl2 = float(T.c05_s03_natural_logarithm_of)
    st1 = ctex([("0.07t", C.steps), ("=", None), (r"\ln 2", C.natural), (r"\approx", None), (f"{math.log(2):.3f}",
                                                                                             C.natural)], 46)
    col(st1, 1.4)
    g2.play(Write(st1), at=tl2 - 0.3, dur=1.0)
    td = word_at("divided", tl2)
    st2 = ctex([("t", C.steps), ("=", None), (r"\frac{0.693}{0.07}", None)], 46)
    g2.play(Write(st2), at=td - 1.4, dur=1.0)
    tt = float(T.c05_s03_close_to_ten_years)
    st3 = ctex([(r"\approx", None), (f"{ld.DOUBLING_T:.1f}", C.steps), (r"\ \text{years}", None)], 46)
    col(VGroup(st2, st3).arrange(RIGHT, buff=0.18), 0.2)
    g2.play(Write(st3), at=tt, dur=0.8)
    drop = DashedLine(pc, P3(TX(ld.DOUBLING_T), AY(0)), stroke_color=tint(C.steps, 0.7), stroke_width=2,
                      dash_length=0.08)
    g2.play(Create(drop), FadeOut(qm), at=tt, dur=0.7)
    g2.play(FadeIn(tex(f"{ld.DOUBLING_T:.1f}", 26, C.steps).next_to(P3(TX(ld.DOUBLING_T), AY(0)), UP + RIGHT,
                                                                     buff=0.08)), at=tt + 0.5, dur=0.4)
    t70 = float(T.c05_s03_rule_of_seventy)
    g2.play(FadeIn(ctex([(r"70\div 7=10", None)], 38).set_color(C.muted).move_to(P3(CX, -1.1))), at=t70, dur=0.6)
