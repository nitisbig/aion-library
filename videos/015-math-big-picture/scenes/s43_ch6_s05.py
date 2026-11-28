"""ch6_s05 · Buffon, and a lucky result.

The circle and its gold half turn from ch6_s04 fade. On 'Buffon' a lower third (G.-L. Leclerc de Buffon · 1777) and a
log-log plot: the error |estimate − π| against throws, with thirty seeded honest runs drawn faint pink. On 'Lazzarini'
his lower third (M. Lazzarini · 1901); on 'suspiciously' his point (3 408 throws, error 0.0000003) drops far below the
honest runs, tagged 'too lucky'. On 'slowly' the 1/√N line and a step on it: ×100 throws for one more digit, and
error ∼ 1/√N writes. On 'Zu Chongzhi's' 5680/1808 = 355/113 (gold) and the name from Chapter 2.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, HUB_R, P3, backed, buffon, caps, lower_third, sans, tex, the_circle

LX0, LXS, LY0, LYS = -5.6, 1.75, -2.7, 0.72      # plot: log10(throws) 1..5 across, log10(error) −7..0 up
SD = (math.pi ** 2 / 2) * math.sqrt((2 / math.pi) * (1 - 2 / math.pi))   # error ≈ SD/√N (one standard deviation)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lp(lx, ly):
    return P3(LX0 + LXS * (lx - 1), LY0 + LYS * (ly + 7))


def runs(k=30, n=100_000):
    lxs = np.linspace(1, 5, 170)
    ns = np.round(10 ** lxs).astype(int)
    out = []
    for j in range(k):
        _, _, hit = buffon(n, seed=4000 + j)
        h = np.cumsum(hit)[ns - 1]
        err = np.abs(2 * ns / np.maximum(h, 1) - math.pi)
        out.append(np.log10(np.clip(err, 1e-7, 1.0)))
    return lxs, out


@scene(T.ch6_s05, T.ch6_s06)
def ch6_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    ax_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_bu, t_la, t_su = float(T.ch6_s05_buffon), float(T.ch6_s05_lazzarini), float(T.ch6_s05_suspiciously)
    t_sl, t_zu = float(T.ch6_s05_slowly), float(T.ch6_s05_zu_chongzhi_s)
    t_his = t_zu - 1.61                                                     # 'His answer'
    U, Q = C.uncertainty, C.quantity
    out_t = t1 - 0.7

    # as ch6_s04 left it
    circ = the_circle(HUB_R)
    arc = Arc(radius=HUB_R, start_angle=0, angle=math.pi, stroke_color=Q, stroke_width=8)
    dia = VGroup(Line(P3(HUB_R, 0), P3(-HUB_R, 0), stroke_color=C.text, stroke_width=5),
                 Dot(P3(-HUB_R, 0), radius=0.08, color=Q))
    pi_l = tex(r"\pi", 56, Q).move_to(P3(0, HUB_R + 0.5))
    old = VGroup(circ, arc, dia, pi_l)
    m.add(old)
    m.play(FadeOut(old), at=t0 + 0.15, dur=0.6)

    # 'Buffon': the log-log plot of the error, and thirty honest runs
    axes = VGroup(Line(lp(1, -7), lp(5.15, -7), stroke_color=C.axis, stroke_width=2.6),
                  Line(lp(1, -7), lp(1, 0.2), stroke_color=C.axis, stroke_width=2.6))
    ticks = VGroup()
    for g in range(1, 6):
        ticks.add(Line(lp(g, -7), lp(g, -7) + P3(0, -0.1), stroke_color=C.axis, stroke_width=2))
        ticks.add(tex("10" if g == 1 else f"10^{g}", 30, C.muted).move_to(lp(g, -7) + P3(0, -0.4)))
    for e in (0, -2, -4, -6):
        ticks.add(Line(lp(1, e), lp(1, e) + P3(-0.1, 0), stroke_color=C.axis, stroke_width=2))
        ticks.add(tex("1" if e == 0 else f"10^{{{e}}}", 30, C.muted).move_to(lp(1, e) + P3(-0.55, 0)))
    names = VGroup(sans("throws", 28, C.muted).move_to(lp(3, -7) + P3(0, -0.95)),
                   sans("error", 28, C.muted).move_to(lp(1, 0.2) + P3(0, 0.35), aligned_edge=LEFT))
    ax_l.play(Create(axes), FadeIn(ticks), FadeIn(names), at=t_bu + 0.2, dur=0.8)
    lxs, rs = runs()
    curves = VGroup(*(VMobject(stroke_color=U, stroke_width=1.5, stroke_opacity=0.2).set_points_as_corners(
        [lp(a, b) for a, b in zip(lxs, r)]) for r in rs))
    m.play(LaggedStart(*(Create(c_) for c_ in curves), lag_ratio=0.03), at=t_bu + 1.0, dur=3.0)

    lt1 = lower_third(r"G.-L.\ Leclerc\ de\ Buffon\ \textperiodcentered\ 1777", P3(-6.3, 3.3), width=5.6, size=30)
    top.play(FadeIn(lt1, shift=0.08 * LEFT), at=t_bu - 0.2, dur=0.6)
    plate(s, top, "buffon", (4.2, 0.6), 2.8, t_bu + 0.2, t_la - 0.5, C.uncertainty)
    top.play(FadeOut(lt1), at=t_la - 0.5, dur=0.4)
    lt2 = lower_third(r"M.\ Lazzarini\ \textperiodcentered\ 1901", P3(-6.3, 3.3), width=3.8, size=30)
    top.play(FadeIn(lt2, shift=0.08 * LEFT), at=t_la - 0.1, dur=0.6)
    top.play(FadeOut(lt2), at=t_sl - 0.4, dur=0.4)

    # 'suspiciously': Lazzarini's point, far below the honest runs
    lzx, lzy = math.log10(3408), math.log10(abs(355 / 113 - math.pi))
    lz = Dot(lp(lzx, math.log10(SD / math.sqrt(3408))), radius=0.11, color=Q)
    top.add(lz, at=t_su - 0.5)
    top.play(FadeIn(lz, scale=1.5), at=t_su - 0.5, dur=0.3)
    top.play(lz.animate.move_to(lp(lzx, lzy)), at=t_su - 0.1, dur=0.9, ease="out_back")
    ring = Circle(radius=0.24, stroke_color=Q, stroke_width=2.6).move_to(lp(lzx, lzy))
    tag = backed(sans("too lucky", 30, Q)).next_to(ring, RIGHT, buff=0.15)
    top.play(Create(ring), FadeIn(tag, shift=0.06 * LEFT), at=t_su + 0.8, dur=0.5)

    # 'slowly': error ∼ 1/√N, and a hundred times more throws for one more digit
    trend = DashedLine(lp(1, math.log10(SD / math.sqrt(10))), lp(5, math.log10(SD / math.sqrt(1e5))),
                       dash_length=0.14, stroke_color=C.text, stroke_width=2.6)
    m.play(Create(trend), at=t_sl - 0.1, dur=0.8)
    y2 = math.log10(SD / 10)
    step = VGroup(Line(lp(2, y2), lp(4, y2), stroke_color=C.text, stroke_width=3),
                  Line(lp(4, y2), lp(4, y2 - 1), stroke_color=C.text, stroke_width=3))
    s_l = VGroup(backed(tex(r"\times 100", 34, C.text)).next_to(step[0], UP, buff=0.1),
                 backed(sans("one digit", 28, C.text)).next_to(step[1], RIGHT, buff=0.12))
    m.play(Create(step), at=t_sl + 0.9, dur=0.9)
    m.play(FadeIn(s_l), at=t_sl + 1.6, dur=0.5)
    e1 = MathTex(r"\text{error}", r"\sim", r"\frac{1}{\sqrt{N}}", font_size=50, color=C.text)
    e1[0].set_color(U)
    e1.move_to(P3(4.6, 1.75))
    top.play(Write(e1), at=t_sl + 0.3, dur=0.9)

    # 'Zu Chongzhi's': his fraction
    e2 = MathTex(r"\frac{5680}{1808}", "=", r"\frac{355}{113}", font_size=52, color=C.text)
    e2[2].set_color(Q)
    e2.move_to(P3(4.6, -0.35))
    top.play(Write(e2), at=t_his - 0.1, dur=1.0)
    zu = caps(r"Zu\ Chongzhi\ \textperiodcentered\ c.\ 480", 28, Q).move_to(P3(4.6, -1.45))
    top.play(FadeIn(zu, shift=0.06 * UP), at=t_zu, dur=0.5)
    top.play(Indicate(e2[2], color=Q, scale_factor=1.2), at=t_zu + 0.3, dur=0.7)

    # out
    top.play(FadeOut(VGroup(lz, ring, tag, e1, e2, zu)), at=out_t, dur=0.6)
    m.play(FadeOut(VGroup(curves, trend, step, s_l)), at=out_t, dur=0.6)
    ax_l.play(FadeOut(VGroup(axes, ticks, names)), at=out_t, dur=0.6)
