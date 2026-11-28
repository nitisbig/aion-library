"""c03_s03 · Equal ratios, equal steps. Storyboard: plan/scene_plan.md § c03_s03.

A three-decade log ruler, 1 to 1000: equal ×10 brackets over each decade on the spoken words. On "the same multiplication" a
lit dot hops the three decades in three equal hops. A keyboard (an ivory and ebony raster)
rises below with every A from 55 to 880 Hz (logdata) on a log frequency axis at equal spacing, each octave a ×2
bracket. A linear axis underneath shows the same five As bunched to the left. On "ears" a sine leaves the 440.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from kit import P3, add_rail, chapter_break, glow, piano, polyline, ramp, sans, soft_shadow, tex, tint, word_at

XA, XB = -5.4, 5.4
W = XB - XA


@scene(T.c03_s03, T.c04_s01)
def s12_c03_octaves(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 3)
    chapter_break(s, 4, T.c04_s01)
    m = s.manim(z=4)

    # 1 … 1000 on a log ruler
    yr = 2.0
    X = lambda v: XA + W * math.log10(v) / 3  # noqa: E731
    ruler = VGroup(Line(P3(XA, yr), P3(XB, yr), stroke_color=C.ruler, stroke_width=2.5))
    for d in range(3):
        for k in range(1, 10):
            v = k * 10 ** d
            ruler.add(Line(P3(X(v), yr), P3(X(v), yr - (0.28 if k == 1 else 0.13)), stroke_color=C.ruler,
                           stroke_width=2 if k == 1 else 1.2))
    ruler.add(Line(P3(XB, yr), P3(XB, yr - 0.28), stroke_color=C.ruler, stroke_width=2))
    for v in (1, 10, 100, 1000):
        ruler.add(tex(str(v), 30, C.value).move_to(P3(X(v), yr - 0.55)))
    m.play(Create(ruler[0]), FadeIn(ruler[1:], lag_ratio=0.02), at=float(T.c03_s03) + 0.4, dur=1.0)
    for d, cue in enumerate((T.c03_s03_one_to_ten, T.c03_s03_ten_to_a_hundred, T.c03_s03_a_hundred_to_a_thous)):
        a, b = X(10 ** d), X(10 ** (d + 1))
        arc = ArcBetweenPoints(P3(b - 0.05, yr + 0.12), P3(a + 0.05, yr + 0.12), angle=1.0, stroke_color=C.base,
                               stroke_width=2.5)
        m.play(Create(arc), FadeIn(tex(r"\times10", 28, C.base).move_to(P3((a + b) / 2, yr + 0.85))), at=cue, dur=0.7)

    # each decade is the same multiplication: a dot hops them in three equal hops
    th = word_at("same", float(T.c03_s03_a_hundred_to_a_thous))
    hops = [(th - 0.2 + 0.7 * d, X(10 ** d), X(10 ** (d + 1))) for d in range(3)]

    def hopper(t):
        a = max(0.0, min(1.0, (t - hops[0][0]) / 0.6))
        if t < hops[0][0] - 0.3 or t > hops[-1][0] + 1.6:
            return VGroup()
        x, y = hops[0][1], yr + 0.12
        for t0, xa, xb in hops:
            if t >= t0:
                u = min(1.0, (t - t0) / 0.6)
                u = u * u * (3 - 2 * u)
                x, y = xa + (xb - xa) * u, yr + 0.12 + 1.6 * u * (1 - u)
        op = min(1.0, (t - hops[0][0] + 0.3) / 0.3) * (1 - ramp(t, hops[-1][0] + 1.0, 0.5))
        return Dot(P3(x, y), radius=0.08, color=C.base).set_opacity(max(0.0, op))
    glow(s, C.base, z=5, k=0.9).redraw(hopper, during=(hops[0][0] - 0.4, hops[-1][0] + 1.7))

    # the keyboard and every A on a log frequency axis
    tp = float(T.c03_s03_piano)
    kh, kw = 1.05, W / 29
    rise = lambda t: (0.0, -1.55 + kh / 2 - 0.3 * (1 - ramp(t, tp - 0.15, 0.8)))  # noqa: E731
    sh, shh = soft_shadow(W, kh, blur=0.1, a=0.7)
    s.add(ArrayLayer(sh, height=shh, pos=Track(lambda t: (0.05, rise(t)[1] - 0.09)), z=2,
                     opacity=fade(tp - 0.15, dur=0.8)))
    s.add(ArrayLayer(piano(29, kw=60, h=round(60 * 29 * kh / W)), height=kh, pos=Track(rise), z=3,
                     opacity=fade(tp - 0.15, dur=0.8)))
    ya = -0.15
    xa_of = lambda k: XA + (7 * k + 0.5) * kw  # noqa: E731   the A keys sit 7 white keys apart
    fx = VGroup(Line(P3(XA, ya), P3(XB, ya), stroke_color=tint(C.muted, 0.7), stroke_width=1.5))
    adots = VGroup()
    for k, f in enumerate(ld.A_FREQS):
        x = xa_of(k)
        adots.add(Dot(P3(x, ya), radius=0.07, color=C.value))
        fx.add(tex(f"{f}", 26, C.value).move_to(P3(x, ya + 0.32)),
               Line(P3(x, ya), P3(x, -0.5), stroke_color=tint(C.value, 0.5), stroke_width=1.2))
    fx.add(sans("Hz", 20, C.muted).move_to(P3(XB + 0.35, ya)))
    m.play(FadeIn(fx), FadeIn(adots, lag_ratio=0.2), at=tp + 0.9, dur=1.0)
    tw = float(T.c03_s03_same_width)
    for k in range(4):
        a, b = xa_of(k), xa_of(k + 1)
        m.play(Create(ArcBetweenPoints(P3(b - 0.05, ya + 0.6), P3(a + 0.05, ya + 0.6), angle=0.8,
                                       stroke_color=C.base, stroke_width=2.2)),
               FadeIn(tex(r"\times2", 24, C.base).move_to(P3((a + b) / 2, ya + 1.1))), at=tw - 0.4 + 0.3 * k, dur=0.5)

    # the same As on a linear axis bunch up
    tl = float(T.c03_s03_logarithmic_scale)
    yl = -2.35
    lin = lambda f: XA + W * f / 900  # noqa: E731
    lax = VGroup(Line(P3(XA, yl), P3(XB, yl), stroke_color=tint(C.muted, 0.7), stroke_width=1.5))
    for f in (0, 300, 600, 900):
        lax.add(Line(P3(lin(f), yl), P3(lin(f), yl - 0.1), stroke_color=C.muted, stroke_width=1.2),
                tex(str(f), 22, C.muted).move_to(P3(lin(f), yl - 0.3)))
    lax.add(sans("linear", 20, C.muted).move_to(P3(XB, yl + 0.3), aligned_edge=RIGHT))
    m.play(FadeIn(lax), at=tl - 0.2, dur=0.6)
    m.play(LaggedStart(*[TransformFromCopy(adots[k], Dot(P3(lin(f), yl), radius=0.07, color=C.value))
                         for k, f in enumerate(ld.A_FREQS)], lag_ratio=0.15), at=tl + 0.3, dur=1.2)

    # ears: a sine leaves the 440
    t_e = float(T.c03_s03_ears)
    x440 = xa_of(3)

    def sine(t):
        u = ramp(t, t_e - 0.1, 1.6)
        if u <= 0:
            return VGroup()
        xs = np.linspace(0, 2.4 * u, 120)
        pts = [(x440 + 0.2 + x, ya + 0.15 + 0.18 * math.sin(2 * math.pi * (x * 2.2 - (t - t_e)))) for x in xs]
        return polyline(pts, C.sound, 2.5, opacity=1 - 0.6 * ramp(t, t_e + 1.4, 0.6))
    m.redraw(sine, during=(t_e - 0.2, float(s.end)))
