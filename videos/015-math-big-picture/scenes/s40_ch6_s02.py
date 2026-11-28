"""ch6_s02 · Many coin flips (the law of large numbers).

The edge-on coin from ch6_s01 flips again, lands heads and drops to the start of a chart: the running share of heads
(C.uncertainty) against flips on a log axis from 1 to a million (one seeded run), with a dashed one-half line. Early on
it zigzags; after a thousand flips it hugs one half; on 'closer' a band of ±1/(2√n) narrows around it. On 'Bernoulli'
a lower third J. Bernoulli · 1713. On 'One flip' the first point is ringed, on 'million' the last, with the counter at
1 000 000 and the share within a whisker of 0.5.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, P3, Digits, coin, grouped, lower_third, sans, tex, window

CC = P3(2.8, 0.75)                               # where ch6_s01 left the coin
GX0, GXS, GY0, GYS = -5.6, 1.45, -2.6, 4.6       # chart: log10(flips) 0..6 across, share 0..1 up
NF = 1_000_000


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def gp(g, sh):
    return P3(GX0 + GXS * g, GY0 + GYS * sh)


flips = np.random.default_rng(1713).random(NF) < 0.5
flips[0] = True                                  # the coin on screen lands heads
cum = np.cumsum(flips)
NS = np.unique(np.concatenate([np.arange(1, 101), np.round(np.logspace(2, 6, 700)).astype(int)]))
GS, SH = np.log10(NS), cum[NS - 1] / NS


@scene(T.ch6_s02, T.ch6_s03)
def ch6_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    ax_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_sh, t_j, t_th = float(T.ch6_s02_share_of_heads), float(T.ch6_s02_jumps), float(T.ch6_s02_thousand)
    t_cl, t_be, t_mi = float(T.ch6_s02_closer), float(T.ch6_s02_bernoulli), float(T.ch6_s02_million)
    t_one = t_mi - 2.75                                                        # 'One flip'
    U = C.uncertainty
    out_t = t1 - 0.7

    # the coin flips once more, lands heads, and drops to the chart's first point
    t_f = t0 + 0.7
    first = gp(0, 1.0)

    def coin_at(t):
        u = min(max((t - t_f) / 1.7, 0.0), 1.0)
        ph = math.pi / 2 + 7.5 * math.pi * (1 - (1 - u) ** 2.2)
        w = ss((t - t_sh + 1.2) / 0.9)
        f = 1 - ss((t - t_sh) / 0.3)
        if f <= 0:
            return VGroup()
        return coin((1 - w) * CC + w * first, ph).scale(1 - 0.7 * w).set_opacity(f)

    top.redraw(window(coin_at, t0, t_sh + 0.3), during=(t0, t_sh + 0.35))

    # the chart
    axes = VGroup(Line(gp(0, 0), gp(6.15, 0), stroke_color=C.axis, stroke_width=2.6),
                  Line(gp(0, 0), gp(0, 1.08), stroke_color=C.axis, stroke_width=2.6))
    ticks = VGroup()
    for g in range(7):
        ticks.add(Line(gp(g, 0), gp(g, 0) + P3(0, -0.1), stroke_color=C.axis, stroke_width=2))
        ticks.add(tex("1" if g == 0 else "10" if g == 1 else f"10^{g}", 30, C.muted).move_to(gp(g, 0) + P3(0, -0.4)))
    for sh, lab in ((0, "0"), (0.5, r"\tfrac12"), (1, "1")):
        ticks.add(tex(lab, 30, C.muted).move_to(gp(0, sh) + P3(-0.35, 0)))
    names = VGroup(sans("flips", 28, C.muted).move_to(gp(3, 0) + P3(0, -0.95)),
                   sans("share of heads", 28, C.muted).move_to(gp(0, 1.08) + P3(0, 0.38), aligned_edge=LEFT))
    half = DashedLine(gp(0, 0.5), gp(6.05, 0.5), dash_length=0.12, stroke_color=C.muted, stroke_width=2.2)
    ax_l.play(Create(axes), FadeIn(ticks), FadeIn(names), at=t_sh - 0.9, dur=0.8)
    ax_l.play(Create(half), at=t_sh - 0.3, dur=0.7)

    gk = keys((t_sh + 0.1, 0.0), (t_j, 1.0), (t_j + 1.4, 1.7), (t_th + 0.1, 3.0), (t_cl, 4.4), (t_be + 3.0, 5.3),
              (t_mi, 6.0), default_ease="linear")

    def g_at(t):
        return float(gk(t)) if t >= t_sh + 0.1 else 0.0

    def curve(t):
        f = 1 - ss((t - out_t) / 0.6)
        g = g_at(t)
        k = int(np.searchsorted(GS, g, side="right"))
        pts = [gp(a, b) for a, b in zip(GS[:k], SH[:k])]
        out = VGroup()
        if len(pts) > 1:
            out.add(VMobject(stroke_color=U, stroke_width=3.6, stroke_opacity=f).set_points_as_corners(pts))
        if pts:
            out.add(Dot(pts[-1], radius=0.07, color=U).set_opacity(f))
        return out

    m.redraw(window(curve, t_sh + 0.05, t1 - 0.05), during=(t_sh + 0.05, t1))

    def band(t):
        f = ss((t - t_cl + 0.2) / 0.8) * (1 - ss((t - out_t) / 0.6))
        g = g_at(t)
        if f <= 0 or g <= 0.05:
            return VGroup()
        gg = np.linspace(0, g, 140)
        e = 0.5 / np.sqrt(10 ** gg)
        hi = [gp(a, min(1.0, 0.5 + b)) for a, b in zip(gg, e)]
        lo = [gp(a, max(0.0, 0.5 - b)) for a, b in zip(gg, e)]
        poly = Polygon(*hi, *lo[::-1], stroke_width=0, fill_color=U, fill_opacity=0.055 * f)
        edges = VGroup(*(VMobject(stroke_color=U, stroke_width=1.4, stroke_opacity=0.5 * f).set_points_as_corners(p)
                         for p in (hi, lo)))
        return VGroup(poly, edges)

    ax_l.redraw(window(band, t_cl - 0.2, t1 - 0.05), during=(t_cl - 0.2, t1))

    # the counter: flips and the share so far
    dg = Digits(34)
    lab = VGroup(sans("flips", 28, C.muted).move_to(P3(3.95, 0.05), aligned_edge=LEFT + DOWN),
                 sans("share", 28, C.muted).move_to(P3(3.95, -0.85), aligned_edge=LEFT + DOWN))

    def numbers(t):
        f = ss((t - t_sh + 0.3) / 0.4) * (1 - ss((t - out_t) / 0.6))
        if f <= 0:
            return VGroup()
        g = g_at(t)
        k = max(int(np.searchsorted(GS, g, side="right")), 1)
        n = int(NS[k - 1])
        g_ = VGroup(dg.number(grouped(n), 6.35, 0.05), dg.number(f"{SH[k - 1]:.4f}", 6.35, -0.85, color=U))
        return g_.set_opacity(f)

    top.play(FadeIn(lab), at=t_sh - 0.3, dur=0.4)
    top.redraw(window(numbers, t_sh - 0.3, t1 - 0.05), during=(t_sh - 0.3, t1))

    # heads / flips → ½
    eq = MathTex(r"\frac{\text{heads}}{\text{flips}}", r"\to", r"\tfrac12", font_size=52, color=C.text)
    eq[0].set_color(U)
    eq.move_to(P3(5.15, 1.85))
    m.play(Write(eq), at=t_th + 1.0, dur=0.9)

    # 'Bernoulli'
    lt = lower_third(r"J.\ Bernoulli\ \textperiodcentered\ 1713", P3(-6.3, 3.3), width=3.6)
    top.play(FadeIn(lt, shift=0.08 * LEFT), at=t_be - 0.4, dur=0.6)
    plate(s, top, "bernoulli", (4.6, -2.75), 1.6, t_be, t_one - 0.6, C.uncertainty)
    plate(s, top, "ars_conjectandi", (6.0, -2.75), 1.3, t_be + 0.5, t_one - 0.6, C.uncertainty)
    top.play(FadeOut(lt), at=t_one - 0.6, dur=0.5)

    # 'One flip' and 'million': the first point, then the last
    r1 = Circle(radius=0.22, stroke_color=C.text, stroke_width=3).move_to(gp(0, 1.0))
    top.play(Create(r1), at=t_one, dur=0.5)
    top.play(FadeOut(r1), at=t_mi - 0.6, dur=0.4)
    r2 = Circle(radius=0.22, stroke_color=C.text, stroke_width=3).move_to(gp(6, SH[-1]))
    top.play(Create(r2), at=t_mi + 0.2, dur=0.5)
    box = SurroundingRectangle(VGroup(*lab, dg.number("0.5000", 6.35, -0.85)), buff=0.16, color=U, stroke_width=2,
                               corner_radius=0.08)
    top.play(Create(box), at=t_mi + 0.6, dur=0.5)

    # out
    top.play(FadeOut(VGroup(lab, r2, box)), at=out_t, dur=0.6)
    m.play(FadeOut(eq), at=out_t, dur=0.6)
    ax_l.play(FadeOut(VGroup(axes, ticks, names, half)), at=out_t, dur=0.6)
