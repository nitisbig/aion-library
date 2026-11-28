"""ch6_s04 · Where the circle was hiding (Buffon's needle, worked out).

The rectangle from ch6_s03 keeps filling with dots. On 'share' the region under the arch fills (C.change) and
P = under the arch / rectangle writes; a live readout of the crossing share replaces P = ?. On 'Calculus' ∫₀^π sin θ dθ
= 2 writes, its 2 lit on 'exactly two'. On 'half turn' the width brace reads π (gold, C.quantity) and π × 1 = π
writes; on 'two over pi' P = 2/π ≈ 0.6366, while the readout settles on 0.6366 as the stream reaches 30 331 throws. On
'hiding' the floor returns; every stick slides to the centre keeping its angle and grows to the hub's size, so their
tips trace THE circle. On 'pi is what it takes' one stick turns half way round, tracing a gold half circle: π.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import (StickPainter, glow_layer, wood_floor, FL_BOX, HUB_R, N_LOCK, P3, Canvas, Digits, arch_region, dot_stream, dots_n, draw_dots, full_floor,
                 rect_axes, rpt, sans, sine_arch, tex, the_circle, window)

DOT_BOX = (0.55, -2.25, 5.95, 1.45)
LX = -3.5                                   # the left column of equations
N_STICKS = 360


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch6_s04, T.ch6_s05)
def ch6_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    low, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_sh, t_two, t_ht = float(T.ch6_s04_share), float(T.ch6_s04_exactly_two), float(T.ch6_s04_half_turn)
    t_2pi, t_hid, t_hw = float(T.ch6_s04_two_over_pi), float(T.ch6_s04_hiding), float(T.ch6_s04_halfway)
    t_calc, t_area, t_thats = t_two - 3.41, t_ht + 2.16, t_hid - 1.37        # 'Calculus' 'area is pi' 'And that's'
    t_ev, t_lies, t_pi = t_hid + 2.38, t_hid + 4.2, t_hid + 5.8             # 'Every direction' 'lies on' 'pi is'
    U, Q, Ch = C.uncertainty, C.quantity, C.change
    g_out = t_thats - 0.1                                                   # the rectangle part leaves

    # as ch6_s03 left it
    rect, arch = rect_axes(), sine_arch()
    cond = MathTex("x", r"\le", r"\sin\theta", font_size=52, color=C.text)
    cond[0].set_color(C.space)
    cond[2].set_color(Ch)
    cond.move_to(P3(3.25, 1.95))
    ask = MathTex("P", "=", r"\,?", font_size=56, color=C.text)
    ask[0].set_color(U)
    ask.move_to(P3(3.25, 2.95))
    top.add(rect, arch, cond, ask)
    cv = Canvas(DOT_BOX)

    def dots(t):
        c = cv.begin()
        draw_dots(c, cv, dots_n(t), 1.0, alpha=1 - ss((t - g_out) / 0.6))
        return cv.array()

    s.add(FramesLayer(dots, z=1, during=[(t0, g_out + 0.7)], **cv.layer_kw()))

    # 'share': the region under the arch; P as a share of areas; the live readout
    reg = arch_region(opacity=0.09)
    low.play(FadeIn(reg), at=t_sh - 0.1, dur=0.7)
    e0 = MathTex("P", "=", r"\frac{\text{under the arch}}{\text{rectangle}}", font_size=48, color=C.text)
    e0[0].set_color(U)
    e0[2][:12].set_color(Ch)
    e0.move_to(P3(LX, 2.35))
    top.play(Write(e0), at=t_sh + 1.0, dur=1.0)
    top.play(FadeOut(ask), at=t_sh + 0.6, dur=0.4)
    dg = Digits(34)
    st = dot_stream()
    lab = sans("share", 28, C.muted).move_to(P3(2.0, 2.85), aligned_edge=LEFT + DOWN)

    def readout(t):
        f = ss((t - t_sh - 0.9) / 0.4) * (1 - ss((t - g_out) / 0.6))
        n = dots_n(t)
        if f <= 0 or n <= 0:
            return VGroup()
        v = f"{st['H'][n] / n:.4f}"
        return dg.number(v, 4.6, 2.85, color=Q if n >= N_LOCK else U).set_opacity(f)

    top.play(FadeIn(lab), at=t_sh + 0.9, dur=0.4)
    top.redraw(window(readout, t_sh + 0.9, g_out + 0.65), during=(t_sh + 0.9, g_out + 0.7))

    # 'Calculus': the area under one arch is exactly two
    e1 = MathTex(r"\int_0^{\pi}", r"\sin\theta", r"\,d\theta", "=", "2", font_size=52, color=C.text)
    e1[1].set_color(Ch)
    e1[4].set_color(Ch)
    e1.move_to(P3(LX, 0.95))
    top.play(Write(e1), at=t_calc + 0.1, dur=1.2)
    top.play(Indicate(e1[4], color=Ch, scale_factor=1.4), at=t_two, dur=0.7)

    # 'half turn': the rectangle is π wide, so its area is π
    a, b = rpt(0, 0), rpt(math.pi, 0)
    br = BraceBetweenPoints(a + P3(0, -0.55), b + P3(0, -0.55), direction=DOWN, color=Q)
    br_lab = tex(r"\pi", 44, Q).next_to(br, DOWN, buff=0.08)
    top.play(GrowFromCenter(br), FadeIn(br_lab), at=t_ht - 0.1, dur=0.6)
    top.play(rect[1][1].animate.set_color(Q), at=t_ht, dur=0.4)
    e2 = MathTex(r"\pi", r"\times", "1", "=", r"\pi", font_size=52, color=C.text)
    e2[0].set_color(Q)
    e2[2].set_color(C.space)
    e2[4].set_color(Q)
    e2.move_to(P3(LX, -0.3))
    top.play(Write(e2), at=t_area - 0.9, dur=0.9)

    # 'two over pi'
    e3 = MathTex("P", "=", r"\frac{2}{\pi}", r"\approx", "0.6366", font_size=56, color=C.text)
    e3[0].set_color(U)
    e3[2][0].set_color(Ch)
    e3[2][2].set_color(Q)
    e3[4].set_color(U)
    e3.move_to(P3(LX, -1.75))
    top.play(Write(e3), at=t_2pi - 0.1, dur=1.0)
    box = SurroundingRectangle(e3, buff=0.16, color=U, stroke_width=2.2, corner_radius=0.08)
    top.play(Create(box), at=t_2pi + 1.7, dur=0.5)

    # the rectangle part leaves
    top.play(FadeOut(VGroup(rect, arch, cond, e0, lab, e1, br, br_lab, e2, e3, box)), at=g_out, dur=0.6)
    low.play(FadeOut(reg), at=g_out, dur=0.6)

    # 'hiding': the floor; every stick slides to the centre, keeping its angle; the tips trace the circle
    cx, cy, th, hit, lines_y, half = full_floor(N_STICKS)
    fv = Canvas(FL_BOX)
    sk = fv.skia
    t_sl = t_hid + 0.35

    painter = StickPainter(fv)
    wood, wkw = wood_floor(lines_y)
    s.add(ArrayLayer(wood, z=0.5, opacity=fade(t_thats + 0.4, dur=0.6, out=t_sl + 1.4, out_dur=1.2), **wkw))

    def sticks(t):
        u = np.clip((t - t_sl - 0.0012 * np.arange(N_STICKS)) / 2.4, 0, 1)   # a slight ripple through the pile
        u = u * u * (3 - 2 * u)
        fs = 1 - ss((t - t_lies - 0.3) / 0.9)
        c = fv.begin()
        if fs > 0:
            px, py = (1 - u) * cx, (1 - u) * cy
            h = (1 - u) * half + u * HUB_R
            for i in range(N_STICKS):
                painter.stick(c, px[i], py[i], th[i], 2 * h[i], 1.0 if hit[i] else 0.0, (0.95 - 0.35 * u[i]) * fs,
                              w=7.0 * (1 - 0.45 * u[i]))
        return fv.array()

    on = fade(t_thats + 0.4, dur=0.6)
    s.add(FramesLayer(sticks, z=1, opacity=on, during=[(t_thats + 0.35, t_lies + 1.3)], **fv.layer_kw()))
    circ = the_circle(HUB_R).rotate(-math.pi / 2)
    glow_layer(s, z=2.5, color=C.circle, k=0.8).play(Create(circ), at=t_ev + 0.4, dur=1.2, ease="easy_ease")

    # 'pi is what it takes to go halfway around'
    def half_turn(t):
        f = ss((t - t_pi + 0.5) / 0.3)
        if f <= 0:
            return VGroup()
        a_ = math.pi * ss((t - t_pi - 0.1) / 1.6)
        d = HUB_R * P3(math.cos(a_), math.sin(a_))
        g = VGroup(Line(-d, d, stroke_color=C.text, stroke_width=5, stroke_opacity=f),
                   Dot(d, radius=0.08, color=Q).set_opacity(f))
        if a_ > 0.01:
            g.add(Arc(radius=HUB_R, start_angle=0, angle=a_, stroke_color=Q, stroke_width=8))
            g.submobjects.insert(0, g.submobjects.pop())                       # the arc under the stick
        return g

    top.redraw(window(half_turn, t_pi - 0.5, t1 + 1.0), during=(t_pi - 0.5, t1))
    pi_l = tex(r"\pi", 56, Q).move_to(P3(0, HUB_R + 0.5))
    top.play(FadeIn(pi_l, shift=0.08 * DOWN), at=t_hw + 0.1, dur=0.5)
