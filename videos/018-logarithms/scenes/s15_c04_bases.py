"""c04_s03 · One shape, many bases. Storyboard: plan/scene_plan.md § c04_s03.

log₁₀ x, ln x and log₂ x on one grid. A copy of log₁₀ x stretches upward by 1/log₁₀ 2 = 3.32 (logdata) until it lands
on log₂ x, with the same ratio at x = 2, 4, 8; the change-of-base formula writes. Then a worked example: which power of
two gives ten? A countdown ring runs through the pause; a dashed line rises from x = 10 to log₂ x and across to the
y-axis at 3.32, while x = log₂ 10 = 1 / log₁₀ 2 ≈ 3.32 builds in the column. The other curves dim, ln x stays, e marks
(e, 1), and the hyperbola y = 1/x fades in beneath for chapter five.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from kit import P3, add_rail, chapter_break, ctex, glow, plane, polyline, ramp, tex, tint, word_at

OX, OY, U = -6.0, -1.2, 0.78
CX = 4.55
K = ld.STRETCH_10_TO_2


@scene(T.c04_s03, T.c05_s01)
def s15_c04_bases(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 4)
    chapter_break(s, 5, T.c05_s01)
    m = s.manim(z=3)
    g, X, Y = plane(OX, OY, U, (0, 10.4), (-1.5, 4.1))
    t0 = float(T.c04_s03)
    m.play(FadeIn(g), at=t0 + 0.3, dur=0.8)
    m.add(*[tex(str(i), 20, C.muted).next_to(P3(X(i), OY), DOWN, buff=0.08) for i in (2, 4, 6, 8, 10)], at=t0 + 0.3)
    xs = np.geomspace(0.06, 10.4, 300)

    def curve(f, color, width=4, opacity=1.0):
        pts = [(X(x), Y(f(x))) for x in xs if -1.5 <= f(x) <= 4.1]
        return polyline(pts, color, width, opacity)
    c10 = curve(math.log10, C.muted)
    cln = curve(math.log, C.natural)
    c2 = curve(math.log2, C.steps)
    ts = float(T.c04_s03_share_one_shape)
    m.play(LaggedStart(Create(c10), Create(cln), Create(c2), lag_ratio=0.4), at=ts - 0.3, dur=2.0)
    labs = VGroup(tex(r"\log_{10}x", 28, C.muted).move_to(P3(X(9.6), Y(1.0) - 0.3)),
                  tex(r"\ln x", 28, C.natural).move_to(P3(X(9.6), Y(math.log(9.6)) - 0.32)),
                  tex(r"\log_2 x", 28, C.steps).move_to(P3(X(8.6), Y(math.log2(8.6)) + 0.35)))
    m.play(FadeIn(labs, lag_ratio=0.3), at=ts + 1.4, dur=0.8)

    # stretch log10 onto log2
    tst = float(T.c04_s03_stretched_upward)
    gl = glow(s, C.base, z=4, k=0.6)
    stretch = lambda t: 1 + (K - 1) * ramp(t, tst, 2.2)  # noqa: E731
    gl.redraw(lambda t: curve(lambda x: stretch(t) * math.log10(x), C.base, 3,
                              opacity=1 - ramp(t, tst + 2.6, 0.7)), during=(tst - 0.1, tst + 3.4))
    arrows = VGroup(*[Arrow(P3(X(x), Y(math.log10(x))), P3(X(x), Y(math.log2(x))), buff=0.04, stroke_width=3,
                            color=C.base, max_tip_length_to_length_ratio=0.2) for x in (2, 4, 8)])
    m.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3), at=tst + 1.6, dur=1.0)
    kx = tex(rf"\times{K:.2f}", 30, C.base).next_to(arrows[2], LEFT, buff=0.1)
    m.play(FadeIn(kx), at=tst + 2.4, dur=0.5)
    tc = float(T.c04_s03_change_base)
    cb = ctex([(r"\log_2 x", C.steps), ("=", None), (r"\frac{\log_{10}x}{\log_{10}2}", None)], 46).move_to(P3(CX, 2.6))
    m.play(Write(cb), at=tc, dur=1.0)
    m.play(FadeOut(VGroup(arrows, kx)), at=tc + 3.0, dur=0.6)

    # worked example: which power of two gives ten?
    tu = float(T.c04_s03_unknown_exponent)
    q = ctex([("2", C.base), ("^x", C.steps), ("=", None), ("10", C.value)], 52).move_to(P3(CX, 1.35))
    m.play(Write(q), at=tu, dur=0.8)
    tw = float(T.c04_s03_which_power)
    ring_c = P3(CX + 1.45, 1.35)
    r0, r1 = tw + 1.2, tw + 2.5

    def ring(t):
        u = min(max((t - r0) / (r1 - r0), 0.0), 1.0)
        a = 1 - ramp(t, r1, 0.3)
        g2 = VGroup(Circle(radius=0.2, arc_center=ring_c, stroke_color=tint(C.muted, 0.35), stroke_width=2,
                           stroke_opacity=a, fill_opacity=0))
        if u < 1:
            g2.add(Arc(radius=0.2, start_angle=PI / 2, angle=-2 * PI * (1 - u), arc_center=ring_c,
                       stroke_color=C.steps, stroke_width=3.5, stroke_opacity=a, fill_opacity=0))
        return g2
    m.redraw(ring, during=(r0 - 0.1, r1 + 0.4))
    x10 = Dot(P3(X(10), Y(0)), radius=0.08, color=C.value)
    up = DashedLine(P3(X(10), Y(0)), P3(X(10), Y(math.log2(10))), stroke_color=tint(C.value, 0.7), stroke_width=2,
                    dash_length=0.08)
    m.play(FadeIn(x10, scale=1.5), at=tw + 0.3, dur=0.4)
    m.play(Create(up), at=tw + 0.8, dur=0.7)
    qm = tex("?", 40, C.steps).next_to(P3(X(0), Y(math.log2(10))), LEFT, buff=0.15)
    across = DashedLine(P3(X(10), Y(math.log2(10))), P3(X(0), Y(math.log2(10))), stroke_color=tint(C.steps, 0.7),
                        stroke_width=2, dash_length=0.08)
    m.play(Create(across), FadeIn(qm), at=tw + 1.4, dur=0.8)

    ta = word_at("answer", tw)
    l1 = ctex([("x", C.steps), ("=", None), (r"\log_2", None), ("10", C.value)], 46)
    l2 = ctex([("=", None), (r"\frac{1}{\log_{10}2}", None)], 46)
    l3 = ctex([(r"\approx", None), (f"{ld.SOLVE_2X_10:.2f}", C.steps)], 46)
    l1.move_to(P3(CX, 0.35))
    VGroup(l2, l3).arrange(RIGHT, buff=0.18).next_to(l1, DOWN, buff=0.3).align_to(l1[1], LEFT)
    blk = VGroup(l1, l2, l3)
    blk.shift(LEFT * max(0.0, blk.get_right()[0] - 6.3))
    m.play(Write(l1), at=ta, dur=0.9)
    m.play(Write(l2), at=word_at("divided", ta), dur=0.9)
    t332 = float(T.c04_s03_three_point_three_tw)
    m.play(Write(l3), at=t332, dur=0.7)
    val = tex(f"{ld.SOLVE_2X_10:.2f}", 30, C.steps).next_to(P3(X(0), Y(math.log2(10))), LEFT, buff=0.12)
    m.play(Transform(qm, val), at=t332 + 0.2, dur=0.6)
    hp = glow(s, C.steps, z=4, k=0.8)
    hp.play(FadeIn(Dot(P3(X(10), Y(math.log2(10))), radius=0.08, color=C.steps), scale=1.6), at=t332 + 0.2, dur=0.4)

    # one base above the others: e
    to = float(T.c04_s03_one_base)
    m.play(c10.animate.set_stroke(opacity=0.2), c2.animate.set_stroke(opacity=0.2),
           FadeOut(VGroup(labs[0], labs[2], x10, up, across, qm)), VGroup(cb, q, l1, l2, l3).animate.set_opacity(0.35),
           at=to, dur=0.8)
    te = float(T.c04_s03_called_e)
    E = math.e
    pe = P3(X(E), Y(1))
    eg = glow(s, C.natural, z=4, k=0.9)
    eg.play(FadeIn(Dot(pe, radius=0.09, color=C.natural), scale=1.6), at=te - 0.4, dur=0.5)
    m.play(Create(DashedLine(P3(X(E), Y(0)), pe, stroke_color=tint(C.natural, 0.6), stroke_width=1.6,
                             dash_length=0.07)),
           Create(DashedLine(P3(X(0), Y(1)), pe, stroke_color=tint(C.natural, 0.6), stroke_width=1.6,
                             dash_length=0.07)), at=te - 0.2, dur=0.6)
    m.play(FadeIn(tex("e", 34, C.natural).next_to(P3(X(E), Y(0)), DOWN, buff=0.38)), at=te, dur=0.4)
    m.play(FadeIn(ctex([("e", C.natural), (r"\approx 2.718", None)], 52).move_to(P3(CX, -2.0))), at=te + 0.2, dur=0.6)
    tg = float(T.c04_s03_piece_of_geometry)
    hy = [(X(x), Y(1 / x)) for x in np.geomspace(0.25, 10.4, 200)]
    m.play(Create(polyline(hy, tint(C.text, 0.5), 3)), at=tg - 0.4, dur=1.4)
