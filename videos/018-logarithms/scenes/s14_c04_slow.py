"""c04_s02 · Slow growth. Storyboard: plan/scene_plan.md § c04_s02.

y = log₁₀ x on a linear x-axis whose right end runs out by powers of ten (exponential zoom, so each decade takes equal
time): at a million the curve has reached 6, at a billion 9 (markers and readouts, logdata). 1 000 000 000 writes with
its ten digits underlined. The zoom keeps running and the curve keeps creeping up.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from kit import P3, add_rail, ctex, glow, polyline, ramp, sans, tex, tint

XA, XB = -5.6, 5.6
YA, UY = -2.75, 0.45


def _fmt(v):
    k = int(math.floor(math.log10(v) + 1e-9))
    a = v / 10 ** k
    if round(a, 1) >= 10:
        a, k = a / 10, k + 1
    if k < 4:
        return f"{v:,.0f}".replace(",", r"\,")
    return (f"{a:.1f}" if abs(a - round(a)) > 0.05 else f"{round(a)}") + rf"\times10^{{{k}}}"


@scene(T.c04_s02, T.c04_s03)
def s14_c04_slow(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 4)
    out = Track(lambda t: 1 - ramp(t, float(s.end) - 0.7, 0.6))
    m = s.manim(z=3, opacity=out)
    t0, tv, tm, tb = float(T.c04_s02), float(T.c04_s02_very_slow), float(T.c04_s02_million), float(T.c04_s02_billion)
    tn = float(T.c04_s02_never_stops_climbing)
    end = float(s.end)

    # right end of the x-axis, as a power of ten: 1 → 6.3 at "million", 9.3 at "billion", creeping on after
    def kmax(t):
        k = 1.0 + 5.3 * ramp(t, tv - 0.2, tm - tv + 0.4)
        k += 3.0 * ramp(t, tm + 0.6, tb - tm - 0.4)
        k += 0.9 * min(max((t - tn + 0.5) / (end - tn), 0.0), 1.0)
        return k
    Y = lambda y: YA + UY * y  # noqa: E731
    grid = VGroup(*[Line(P3(XA, Y(k)), P3(XB, Y(k)), stroke_color=C.grid_minor if k % 3 else C.grid, stroke_width=1.2)
                    for k in range(1, 11)])
    axes = VGroup(Line(P3(XA, Y(0)), P3(XB + 0.2, Y(0)), stroke_color=C.axis, stroke_width=2.4),
                  Line(P3(XA, Y(0)), P3(XA, Y(10.2)), stroke_color=C.axis, stroke_width=2.4))
    ylab = VGroup(*[tex(str(k), 24, C.steps).next_to(P3(XA, Y(k)), LEFT, buff=0.12) for k in (3, 6, 9)])
    m.play(FadeIn(grid), FadeIn(axes), FadeIn(ylab), at=t0 + 0.4, dur=0.8)
    m.add(tex(r"y=\log_{10}x", 34, C.steps).move_to(P3(-3.6, Y(3.8))), at=t0 + 0.4)

    def frame(t):
        xm = 10 ** kmax(t)
        X = lambda v: XA + (XB - XA) * v / xm  # noqa: E731
        g = VGroup()
        xs = np.unique(np.concatenate([np.logspace(0, kmax(t), 400), [xm]]))
        g.add(polyline([(X(v), Y(math.log10(v))) for v in xs], C.steps, 4))
        for f in (0.5, 1.0):
            v = f * xm
            g.add(Line(P3(X(v), Y(0)), P3(X(v), Y(0) - 0.1), stroke_color=C.muted, stroke_width=1.5),
                  tex(_fmt(v), 22, C.muted).move_to(P3(X(v) - (0.25 if f == 1 else 0), Y(0) - 0.35)))
        for when, v, k in ((tm, 1e6, 6), (tb, 1e9, 9)):
            a = ramp(t, when - 0.1, 0.5)
            if a <= 0 or X(v) < XA + 0.05:
                continue
            p = P3(X(v), Y(k))
            g.add(Dot(P3(X(v), Y(0)), radius=0.07, color=C.value).set_opacity(a),
                  DashedLine(P3(X(v), Y(0)), p, stroke_color=tint(C.value, 0.6), stroke_width=1.5,
                             dash_length=0.07).set_stroke(opacity=a),
                  DashedLine(p, P3(XA, Y(k)), stroke_color=tint(C.steps, 0.6), stroke_width=1.5,
                             dash_length=0.07).set_stroke(opacity=a),
                  Dot(p, radius=0.07, color=C.steps).set_opacity(a))
        return g
    m.redraw(frame, during=(t0 + 0.3, end))
    hl = glow(s, C.steps, z=4, k=0.5, opacity=out)
    hl.redraw(lambda t: Dot(P3(XB, Y(kmax(t))), radius=0.08, color=C.steps), during=(tv, end))

    e6 = ctex([(r"\log_{10}", None), ("10^6", C.value), ("=", None), ("6", C.steps)], 44).move_to(P3(2.9, 2.95))
    e9 = ctex([(r"\log_{10}", None), ("10^9", C.value), ("=", None), ("9", C.steps)], 44).move_to(P3(2.9, 2.3))
    m.play(FadeIn(e6, shift=0.1 * LEFT), at=tm + 0.4, dur=0.6)
    m.play(FadeIn(e9, shift=0.1 * LEFT), at=tb + 0.4, dur=0.6)

    # digits
    td = float(T.c04_s02_digits)
    num = tex(r"1\,000\,000\,000", 44, C.value).move_to(P3(-2.0, 2.85))
    m.play(Write(num), at=td - 1.2, dur=1.0)
    gl = [g for g in num[0]]
    unders = VGroup(*[Line(g.get_corner(DL) + DOWN * 0.1, g.get_corner(DR) + DOWN * 0.1, stroke_color=C.steps,
                           stroke_width=2.5) for g in gl])
    m.play(LaggedStart(*[Create(u) for u in unders], lag_ratio=0.5), at=td, dur=1.2)
    cnt = VGroup(tex("10", 34, C.steps), sans("digits", 22, C.muted), tex(r"=9+1", 30, C.muted)) \
        .arrange(RIGHT, buff=0.15).next_to(num, DOWN, buff=0.35)
    m.play(FadeIn(cnt), at=td + 1.2, dur=0.6)
