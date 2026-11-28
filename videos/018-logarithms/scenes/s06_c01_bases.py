"""c01_s03 · Other bases, in-between steps. Storyboard: plan/scene_plan.md § c01_s03.

The ten-step staircase gives way to base ten: three ×10 steps to 10, 100, 1000, whose zeros light in the steps colour
(the logarithm counts the zeros). Try one yourself: a base-three staircase with its values hidden, log₃ 81 = ? and a
countdown ring through the pause, then 3, 9, 27, 81 on the spoken numbers and the ? becomes 4. Then base two on a value
axis: the staircase is y = ⌊log₂ x⌋, 6 sits on the tread between 4 and 8, a partial step fills to log₂ 6 = 2.585
(logdata), and filling in every number smooths the steps into the curve y = log₂ x.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from ch1 import DEPTH, N, SH, SW, X0S, Y0S, lift, stair10, stair_depth
from kit import P3, add_rail, chapter_break, ctex, glow, polyline, ramp, sans, staircase, tex, tint, word_at

CX = 4.4


@scene(T.c01_s03, T.c02_s01)
def s06_c01_bases(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 1)
    m = s.manim(z=5)
    t_in = float(T.c01_s03)

    # opening: c01_s02's last picture, which clears for base ten
    st, steps_lbl, e1, iff, e2, legend = stair10()
    old = VGroup(stair_depth(N, X0S, Y0S, SW, SH, d=DEPTH), st, steps_lbl)
    m.add(old, e1, iff, e2, legend)
    m.play(FadeOut(VGroup(e1, iff, e2, legend)), at=t_in + 0.5, dur=0.7)
    ts = float(T.c01_s03_size_of_each_step)
    m.play(FadeOut(old, shift=0.4 * LEFT), at=ts - 0.4, dur=0.8)

    # base ten
    b10 = lift(staircase(3, -5.2, -2.3, 1.75, 1.15, base=10, label_size=46), (0.3, 0.22))
    m.play(FadeIn(b10.floor), Create(b10.path), at=ts + 0.2, dur=1.4)
    d10 = stair_depth(3, -5.2, -2.3, 1.75, 1.15, d=(0.3, 0.22))
    m.play(FadeIn(d10), at=ts + 1.2, dur=0.8)
    m.play(FadeIn(b10.vals[0]), FadeIn(b10.axis), at=ts + 0.6, dur=0.8)
    m.play(LaggedStart(*[FadeIn(g, scale=1.4) for g in b10.tags], lag_ratio=0.4), at=ts + 1.0, dur=1.4)
    t1k = float(T.c01_s03_one_thousand)
    for k, w in ((1, "ten"), (2, "hundred")):
        m.play(FadeIn(b10.vals[k], shift=0.1 * UP), at=word_at(w, ts + 2.0), dur=0.5)
    m.play(FadeIn(b10.vals[3], shift=0.1 * UP), at=t1k + 0.3, dur=0.5)
    tz = float(T.c01_s03_counts_the_zeros)
    zeros = [b10.vals[k][0][1:] for k in (1, 2, 3)]
    m.play(LaggedStart(*[z.animate.set_color(C.steps) for z in zeros], lag_ratio=0.5), at=tz, dur=1.2)
    q10 = ctex([(r"\log_{", None), ("10", C.base), ("}", None), ("1000", C.value), ("=", None), ("3", C.steps)], 60)
    q10.move_to(P3(CX, 1.4))
    m.play(Write(q10), at=tz + 0.3, dur=0.9)
    zl = sans("counts the zeros", 22, C.muted).next_to(q10, DOWN, buff=0.35)
    m.play(FadeIn(zl), at=tz + 0.9, dur=0.6)

    # try one: base three
    tt = float(T.c01_s03_try)
    m.play(FadeOut(VGroup(d10, b10, q10, zl)), at=tt + 0.1, dur=0.7)
    b3 = lift(staircase(4, -5.3, -2.5, 1.4, 0.95, base=3, label_size=42), (0.26, 0.19))
    m.play(FadeIn(b3.floor), Create(b3.path), FadeIn(b3.vals[0]), at=tt + 0.9, dur=1.2)
    d3 = stair_depth(4, -5.3, -2.5, 1.4, 0.95, d=(0.26, 0.19))
    m.play(FadeIn(d3), at=tt + 1.8, dur=0.8)
    m.play(LaggedStart(*[FadeIn(g) for g in b3.tags], lag_ratio=0.3), FadeIn(b3.axis), at=tt + 1.5, dur=1.0)
    q3 = ctex([(r"\log_{", None), ("3", C.base), ("}", None), ("81", C.value), (r"=\;", None), ("{?}", C.steps)], 64)
    q3.move_to(P3(CX, 1.4))
    t81 = word_at("eighty", tt)
    m.play(Write(q3), at=t81, dur=0.9)
    t3 = float(T.c01_s03_three_times_three)
    ring_c = P3(CX + 2.1, 1.4)
    r0, r1 = t81 + 0.9, t3 - 0.1

    def ring(t):
        u = min(max((t - r0) / (r1 - r0), 0.0), 1.0)
        fade_ = 1 - ramp(t, r1, 0.3)
        if u >= 1 and fade_ <= 0.01:
            return VGroup()
        g = VGroup(Circle(radius=0.2, arc_center=ring_c, stroke_color=tint(C.muted, 0.35), stroke_width=2,
                          stroke_opacity=fade_, fill_opacity=0))
        if u < 1:
            g.add(Arc(radius=0.2, start_angle=PI / 2, angle=-2 * PI * (1 - u), arc_center=ring_c,
                      stroke_color=C.steps, stroke_width=3.5, stroke_opacity=fade_, fill_opacity=0))
        return g
    m.redraw(ring, during=(r0 - 0.1, r1 + 0.4))
    hits = [t3, word_at("nine", t3), word_at("twenty", t3), word_at("eighty", t3)]
    for k, th in enumerate(hits, start=1):
        m.play(FadeIn(b3.vals[k], shift=0.1 * UP, scale=1.2), Indicate(b3.tags[k - 1], color=C.base), at=th, dur=0.5)
    four = tex("4", 64, C.steps).move_to(q3[5])
    m.play(Transform(q3[5], four), at=T.c01_s03_is_four, dur=0.6)
    m.play(Indicate(b3.axis[-1], color=C.steps, scale_factor=1.5), at=T.c01_s03_is_four + 0.4, dur=1.0)

    # base two on a value axis: room between the steps
    tr = float(T.c01_s03_room_between)
    m.play(FadeOut(VGroup(d3, b3, q3)), at=tr - 0.6, dur=0.7)
    ox, oy, ux, uy = -4.9, -2.3, 0.98, 1.1
    X = lambda x: ox + ux * x  # noqa: E731
    Y = lambda y: oy + uy * y  # noqa: E731
    ax = VGroup(Line(P3(X(0), Y(0)), P3(X(8.7), Y(0)), stroke_color=C.muted, stroke_width=1.6),
                Line(P3(X(0), Y(0)), P3(X(0), Y(3.25)), stroke_color=C.steps, stroke_width=2))
    xt = VGroup()
    for v in range(1, 9):
        xt.add(Line(P3(X(v), Y(0)), P3(X(v), Y(0) - 0.08), stroke_color=C.muted, stroke_width=1.5),
               tex(str(v), 28, C.value).move_to(P3(X(v), Y(0) - 0.34)))
    yt = VGroup()
    for k in range(4):
        yt.add(Line(P3(X(0) - 0.07, Y(k)), P3(X(0) + 0.07, Y(k)), stroke_color=C.steps, stroke_width=2),
               tex(str(k), 26, C.steps).next_to(P3(X(0) - 0.07, Y(k)), LEFT, buff=0.08))
    xs = np.linspace(1, 8.7, 400)
    floor_pts = []
    for k, (a, b) in enumerate(((1, 2), (2, 4), (4, 8), (8, 8.7))):
        floor_pts += [(X(a), Y(k)), (X(b), Y(k))]
    stair = polyline(floor_pts, C.text, 3)
    tags = VGroup(*[tex(r"\times2", 24, C.base).move_to(P3(X(v) + 0.32, Y(k + 0.5))) for k, v in enumerate((2, 4, 8))])
    m.play(FadeIn(ax), FadeIn(xt, lag_ratio=0.1), FadeIn(yt), at=tr, dur=1.0)
    m.play(Create(stair), at=tr + 0.5, dur=1.4)
    m.play(FadeIn(tags, lag_ratio=0.3), at=tr + 1.0, dur=1.0)
    gaps = VGroup(*[Line(P3(X(a), Y(k) + 0.06), P3(X(b), Y(k) + 0.06), stroke_color=tint(C.steps, 0.5),
                         stroke_width=8) for k, (a, b) in enumerate(((1, 2), (2, 4), (4, 8)))])
    m.play(FadeIn(gaps, lag_ratio=0.3), at=tr + 1.6, dur=0.8)
    m.play(FadeOut(gaps), at=tr + 3.0, dur=0.6)

    t6 = float(T.c01_s03_six)
    six = xt[2 * 5 + 1]
    m.play(six.animate.scale(1.35), at=t6, dur=0.4)
    drop = Dot(P3(X(6), Y(2)), radius=0.08, color=C.value)
    m.play(FadeIn(drop, shift=0.6 * DOWN), at=t6 + 0.2, dur=0.5)
    m.play(Create(DashedLine(P3(X(6), Y(0)), P3(X(6), Y(2)), stroke_color=tint(C.value, 0.6), stroke_width=2,
                             dash_length=0.08)), at=t6 + 0.6, dur=0.6)
    btw = VGroup(tex("2", 30, C.steps), tex("<", 30, C.text), tex(r"\log_2 6", 30, C.text), tex("<", 30, C.text),
                 tex("3", 30, C.steps)).arrange(RIGHT, buff=0.15).move_to(P3(CX + 0.4, 2.0))
    m.play(FadeIn(btw), at=word_at("between", t6), dur=0.6)
    tp = float(T.c01_s03_two_point_five_eight)
    L6 = ld.LOG2_6
    bar_lay = glow(s, C.steps, z=6, k=0.8)
    bar_lay.redraw(lambda t: Line(P3(X(6), Y(2)), P3(X(6), Y(2 + (L6 - 2) * ramp(t, tp - 1.0, 1.2))),
                                  stroke_color=C.steps, stroke_width=7) if t > tp - 1.0 else VGroup(),
                   during=(tp - 1.2, float(s.end)))
    m.play(Create(DashedLine(P3(X(6), Y(L6)), P3(X(0), Y(L6)), stroke_color=tint(C.steps, 0.7), stroke_width=2,
                             dash_length=0.08)), at=tp + 0.2, dur=0.7)
    m.play(FadeIn(tex(f"{L6:.3f}", 26, C.steps).next_to(P3(X(0) - 0.07, Y(L6)), LEFT, buff=0.08)), at=tp + 1.2,
           dur=0.5)
    m.play(drop.animate.move_to(P3(X(6), Y(L6))), at=tp - 0.2, dur=0.8)
    q6 = ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("6", C.value), (r"\approx", None),
               (f"{L6:.3f}", C.steps)], 60).move_to(P3(CX + 0.4, 2.85))
    m.play(Write(q6), at=tp + 0.4, dur=0.9)
    m.play(btw.animate.next_to(q6, DOWN, buff=0.3).set_opacity(0.6), at=tp + 1.8, dur=0.8)

    # smooth: points rain onto the curve, the steps become y = log₂ x
    tc = float(T.c01_s03_smooths_into_a_curve)
    pts = [v for v in np.arange(1.0, 8.51, 0.25)]
    dots = VGroup(*[Dot(P3(X(v), Y(math.log2(v))), radius=0.045, color=C.steps) for v in pts])
    m.play(LaggedStart(*[FadeIn(d, shift=0.25 * DOWN) for d in dots], lag_ratio=0.12), at=tc - 1.4, dur=1.6)
    t_m0, t_m1 = tc - 0.2, tc + 1.4

    def morph(t):
        u = ramp(t, t_m0, t_m1 - t_m0)
        ys = [(1 - u) * math.floor(math.log2(x) + 1e-9) + u * math.log2(x) for x in xs]
        return polyline([(X(x), Y(y)) for x, y in zip(xs, ys)], C.text if u < 0.5 else C.steps, 3 + u)
    m.play(FadeOut(VGroup(tags, drop)), at=t_m0, dur=0.5)
    m.remove(stair, at=t_m0)
    glow(s, C.steps, z=5.5, k=0.6).redraw(morph, during=(t_m0, float(s.end)))
    m.play(FadeOut(dots), at=t_m1, dur=0.6)
    m.play(FadeIn(tex(r"y=\log_2 x", 36, C.steps).move_to(P3(X(7.2), Y(3.4)))), at=t_m1 - 0.2, dur=0.6)
    s.camera.push(tc - 0.5, zoom=1.04, dur=3.0)
    chapter_break(s, 2, T.c02_s01)
