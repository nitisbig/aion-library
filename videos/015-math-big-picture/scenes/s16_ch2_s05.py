"""ch2_s05 · Pi joins them.

The word 'irrational' carries over from the proof and π takes its place beside it, under a 'J. H. Lambert · 1761'
caption. π's first 120 decimals stream in, six rows of twenty. On 'repeating' a six-digit block is marked and its
copy is checked along the rows, failing each time. On 'In practice' everything past the fortieth decimal falls away. On
'fifteen' the first fifteen light gold and a spacecraft flies an Earth-to-Mars transfer orbit below. On 'Forty' the
next twenty-five light too, and the view pulls back: the orbit shrinks to a point inside a circle round the visible
universe. On 'atom' a lens on its rim shows the gap left by forty decimals: one atom wide.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, P3, caps, pi_digits, sans, tex, the_circle

N, ROW = 120, 20
X0, DX = -3.1, 0.38
YR = [2.35, 1.7, 1.05, 0.4, -0.25, -0.9]
SUN = P3(-1.2, -1.45)


def pos(i):
    """Centre of decimal i (1-based)."""
    r, c = divmod(i - 1, ROW)
    return P3(X0 + c * DX, YR[r])


def lower_third(name, x=2.15, y=3.3):
    g = VGroup(caps(name, 34, C.text), Line(ORIGIN, RIGHT * 3.6, stroke_color=C.muted, stroke_width=1.4))
    return g.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(x, y), aligned_edge=LEFT)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch2_s05, T.ch2_s06)
def ch2_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_lam, t_rep, t_15 = float(T.ch2_s05_lambert), float(T.ch2_s05_repeating), float(T.ch2_s05_fifteen)
    t_40, t_atom = float(T.ch2_s05_forty), float(T.ch2_s05_atom)
    Q = C.quantity

    # where ch2_s04 left off: the short number line with √2, and 'irrational'
    YN = -2.85

    def xn(v):
        return -6.0 + (v - 1) * 8.0

    nl = VGroup(Line(P3(xn(0.97), YN), P3(xn(1.63), YN), stroke_color=C.muted, stroke_width=2))
    for v, lab in ((1, "1"), (1.5, "1.5")):
        nl.add(Line(P3(xn(v), YN - 0.12), P3(xn(v), YN + 0.12), stroke_color=C.muted, stroke_width=2),
               tex(lab, 28, C.muted).move_to(P3(xn(v), YN - 0.42)))
    fr = sorted({p / q for q in range(2, 13) for p in range(q + 1, 2 * q) if math.gcd(p, q) == 1 and p / q < 1.6})
    nl.add(*(Line(P3(xn(v), YN - 0.09), P3(xn(v), YN + 0.09), stroke_color=C.text, stroke_width=1.4,
                  stroke_opacity=0.7) for v in fr))
    nl.add(Dot(P3(xn(math.sqrt(2)), YN), radius=0.08, color=Q),
           tex(r"\sqrt{2}", 32, Q).move_to(P3(xn(math.sqrt(2)), YN + 0.45)))
    irr = sans("irrational", 34, Q).move_to(P3(3.6, -3.45))
    m.add(nl, irr)
    m.play(FadeOut(nl), at=t0 + 0.2, dur=0.6)

    # π takes its place, with Lambert's name
    pi_l = tex(r"\pi = 3.", 52, Q).move_to(pos(1) + P3(-0.25, 0), aligned_edge=RIGHT).shift(LEFT * 0.25)
    m.play(irr.animate.move_to(P3(pi_l.get_center()[0] - 0.25, YR[1])), at=t0 + 0.6, dur=1.0, ease="easy_ease")
    lt = lower_third(r"J.\ H.\ Lambert\ \textperiodcentered\ 1761")
    m.play(FadeIn(lt, shift=0.08 * LEFT), at=t_lam - 0.1, dur=0.6)
    m.play(Write(pi_l), at=t0 + 1.2, dur=0.8)

    # the decimals stream in
    dg = pi_digits(N)[2:]                                         # '3.' then the decimals
    assert len(dg) == N and dg.startswith("14159265358979")
    glyph = {d: tex(d, 36, C.text) for d in "0123456789"}
    digits = [glyph[d].copy().move_to(pos(i + 1)) for i, d in enumerate(dg)]
    m.play(LaggedStart(*(FadeIn(d_, shift=0.06 * DOWN) for d_ in digits), lag_ratio=0.03), at=t_lam + 1.4, dur=3.6)
    dots = tex(r"\ldots", 36, C.muted).move_to(pos(N) + P3(0.45, -0.05))
    m.play(FadeIn(dots), at=t_lam + 4.8, dur=0.4)

    # 'repeating': a block of six, its copy checked along the rows
    def under(i, n, col, w=3):
        a, b = pos(i), pos(i + n - 1)
        return Line(a + P3(-0.17, -0.3), b + P3(0.17, -0.3), stroke_color=col, stroke_width=w)

    blk = under(1, 6, Q)
    top.play(Create(blk), at=t_rep - 0.1, dur=0.35)
    starts = [7, 13, 21, 27, 33, 41, 47, 53]
    t_s0, step = t_rep + 0.35, 0.26

    def scan(t):
        k = min(int((t - t_s0) / step), len(starts) - 1)
        i = starts[k]
        g = VGroup(under(i, 6, C.muted, 2.4))
        x_ = VGroup(Line(P3(-0.09, -0.09), P3(0.09, 0.09)), Line(P3(-0.09, 0.09), P3(0.09, -0.09)))
        g.add(x_.set_stroke(C.muted, 2.4).move_to(pos(i + 6) + P3(-0.19, -0.3)))
        return g

    t_s1 = t_s0 + step * len(starts) + 0.3
    top.redraw(window_fn(scan, t_s0, t_s1), during=(t_s0, t_s1))
    top.play(FadeOut(blk), at=t_s1 - 0.1, dur=0.3)

    # 'In practice': everything past the fortieth decimal falls away
    t_pr = t_s1 + 0.2
    m.play(LaggedStart(*(FadeOut(d_, shift=0.25 * DOWN) for d_ in digits[40:][::-1]), lag_ratio=0.01),
           FadeOut(dots), at=t_pr, dur=1.0)
    m.play(FadeOut(lt), at=t_pr, dur=0.5)
    plate(s, m, "lambert", (5.6, -2.2), 2.2, t_lam + 0.2, t_pr, C.quantity)
    dots40 = tex(r"\ldots", 36, C.muted).move_to(pos(40) + P3(0.45, -0.05))
    m.play(FadeIn(dots40), at=t_pr + 0.9, dur=0.3)

    # 'fifteen': the first fifteen light; a transfer orbit, Earth to Mars
    m.play(*(d_.animate.set_color(Q) for d_ in digits[:15]), at=t_15 - 0.1, dur=0.5)
    br15 = under(1, 15, Q, 2.6)
    tag15 = sans("15 places", 28, Q).move_to(P3(5.55, YR[0]))
    top.play(Create(br15), FadeIn(tag15), at=t_15 + 0.3, dur=0.5)
    r1, r2 = 0.85, 1.4
    a_, c_ = (r1 + r2) / 2, (r2 - r1) / 2
    b_ = math.sqrt(a_ ** 2 - c_ ** 2)
    orb = VGroup(Dot(SUN, radius=0.09, color=C.text),
                 Circle(radius=r1, stroke_color=C.muted, stroke_width=1.6).move_to(SUN),
                 Circle(radius=r2, stroke_color=C.muted, stroke_width=1.6).move_to(SUN),
                 Dot(SUN + P3(-r1, 0), radius=0.06, color=C.space), Dot(SUN + P3(r2, 0), radius=0.07, color=C.change))
    m.play(FadeIn(orb, scale=0.9), at=t_15 + 0.5, dur=0.6)
    t_f0, t_f1 = t_15 + 1.0, t_40 - 0.6

    def flight(t):
        u = ss((t - t_f0) / (t_f1 - t_f0))
        E = np.linspace(math.pi, math.pi * (1 - u), 60)
        pts = [SUN + P3(c_ + a_ * math.cos(e), b_ * math.sin(e)) for e in E]
        g = VGroup()
        if u > 0.01:
            g.add(VMobject(stroke_color=Q, stroke_width=2.6).set_points_smoothly(pts))
        g.add(Dot(pts[-1], radius=0.06, color=Q))
        return g

    t_pb = t_40 + 0.2                                             # the pull-back
    m.redraw(window_fn(flight, t_f0, t_pb), during=(t_f0, t_pb))
    fl_end = flight(t_f1)
    m.add(fl_end, at=t_pb)
    shrink = VGroup(orb, fl_end)
    m.play(shrink.animate.scale(0.03, about_point=SUN).set_opacity(0.6), at=t_pb, dur=1.6, ease="easy_ease")

    # 'Forty': the next twenty-five light; a circle round the visible universe
    m.play(*(d_.animate.set_color(Q) for d_ in digits[15:40]), at=t_40 - 0.1, dur=0.6)
    br40 = under(21, 20, Q, 2.6)
    tag40 = sans("40 places", 28, Q).move_to(P3(5.55, YR[1]))
    top.play(FadeOut(VGroup(br15, tag15)), at=t_40 - 0.1, dur=0.4)
    top.play(Create(br40), FadeIn(tag40), at=t_40 + 0.2, dur=0.5)
    RU = 2.05
    uni = the_circle(RU).move_to(SUN)
    rg = np.random.default_rng(1761)
    gal = VGroup()
    while len(gal) < 150:
        p = rg.uniform(-RU, RU, 2)
        if np.hypot(*p) < RU - 0.12 and np.hypot(*p) > 0.25:
            gal.add(Dot(SUN + P3(*p), radius=0.022 + 0.02 * rg.random(), color=C.muted))
    m.play(GrowFromPoint(uni, SUN), at=t_pb + 0.6, dur=1.4, ease="easy_ease")
    m.play(LaggedStart(*(FadeIn(g_) for g_ in gal), lag_ratio=0.005), at=t_pb + 1.0, dur=1.2)
    vu = sans("visible universe", 28, C.muted).move_to(SUN + P3(0, -RU - 0.35))
    m.play(FadeIn(vu), at=t_pb + 1.6, dur=0.5)

    # 'atom': a lens on the rim, the gap one atom wide
    rim = SUN + P3(RU, 0)
    lc, lr = P3(4.6, -1.5), 1.1
    lens = Circle(radius=lr, stroke_color=C.text, stroke_width=2.2).move_to(lc)
    spot = Circle(radius=0.14, stroke_color=C.text, stroke_width=2).move_to(rim)
    con = VGroup(Line(rim + P3(0.1, 0.1), lc + lr * P3(-0.77, 0.64), stroke_color=C.muted, stroke_width=1.4),
                 Line(rim + P3(0.1, -0.1), lc + lr * P3(-0.77, -0.64), stroke_color=C.muted, stroke_width=1.4))
    true_rim = Line(lc + P3(-0.2, -0.95), lc + P3(-0.2, 0.95), stroke_color=C.circle, stroke_width=4)
    est = Line(lc + P3(0.2, -0.95), lc + P3(0.2, 0.95), stroke_color=Q, stroke_width=4)
    atom = VGroup(Dot(lc, radius=0.04, color=C.text),
                  *(Ellipse(width=0.3, height=0.11, stroke_color=C.text, stroke_width=1.4).rotate(a).move_to(lc)
                    for a in (0, math.pi / 3, -math.pi / 3)))
    m.play(Create(spot), Create(con), Create(lens), at=t_atom - 1.6, dur=0.6)
    m.play(Create(true_rim), Create(est), at=t_atom - 1.0, dur=0.5)
    m.play(GrowFromCenter(atom), at=t_atom - 0.2, dur=0.5, ease="out_back")
    one = sans("one atom", 28, C.text).next_to(lens, DOWN, buff=0.15)
    m.play(FadeIn(one), at=t_atom, dur=0.4)

    out = VGroup(irr, pi_l, dots40, *digits[:40], uni, gal, vu, shrink, spot, con, lens, true_rim, est, atom, one)
    t_out = float(s.end) - 0.55
    m.play(FadeOut(out), at=t_out, dur=0.5)
    top.play(FadeOut(VGroup(br40, tag40)), at=t_out, dur=0.5)


def window_fn(fn, a, b):
    from kit import window
    return window(fn, a, b)
