"""ch6_s03 · Each throw is a dot (geometric probability).

Left: one stick, enlarged, between three cracks. On 'as long as' a copy of it stands upright between two cracks: its
length is the board width. On 'how far' the distance from its middle to the nearest crack is drawn (x, C.space); on
'angle' its angle with the boards (θ, C.structure). On 'rectangle' the rectangle of possibilities appears on the
right, θ from 0 to π across and x from 0 to 1 up (in half-board widths); this stick's dot flies into it, then the
stream's throws land as dots. On 'crosses' the sine arch (C.change) draws: dots under it light pink, the rest dim,
and the stick (which crosses) turns pink; x ≤ sin θ writes. On 'what share' P = ? waits while dots keep arriving.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import HERO, P3, Canvas, draw_dots, dots_n, rect_axes, rpt, sine_arch, tex, window

M = P3(-3.7, 0.5)                          # the stick's middle
D = 2.4                                    # board width = stick length (screen units)
CR = (2.0 - D, 2.0, 2.0 - 2 * D)           # crack heights: the one below the stick, the one above, the next
X0, X1 = -6.7, -0.9
DOT_BOX = (0.55, -2.25, 5.95, 1.45)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch6_s03, T.ch6_s04)
def ch6_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lp, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_al, t_hf, t_an = float(T.ch6_s03_as_long_as), float(T.ch6_s03_how_far), float(T.ch6_s03_angle)
    t_re, t_cr, t_ws = float(T.ch6_s03_rectangle), float(T.ch6_s03_crosses), float(T.ch6_s03_what_share)
    t_under = t_cr + 2.48                                                    # 'under this curve'
    U = C.uncertainty
    out_t = t1 - 0.8
    th, xh = HERO

    # the stick between the cracks
    cracks = VGroup(*(Line(P3(X0, y), P3(X1, y), stroke_color=C.map_off, stroke_width=2.4) for y in CR))
    d = (D / 2) * P3(math.cos(th), math.sin(th))
    stick = Line(M - d, M + d, stroke_color=C.text, stroke_width=7)
    lp.play(Create(cracks), at=t0 + 0.3, dur=0.8)
    lp.play(Create(stick), at=t0 + 0.9, dur=0.7)

    # 'as long as': a copy stands upright between two cracks
    ghost = stick.copy().set_stroke(opacity=0.6)
    xg = -1.55
    up = Line(P3(xg, CR[0]), P3(xg, CR[1]), stroke_color=C.text, stroke_width=7, stroke_opacity=0.6)
    lp.add(ghost, at=t_al - 0.2)
    lp.play(Transform(ghost, up), at=t_al - 0.2, dur=1.0, ease="easy_ease")
    ends = VGroup(*(Dot(P3(xg, y), radius=0.08, color=C.text) for y in CR[:2]))
    lp.play(FadeIn(ends, scale=1.6), at=t_al + 0.9, dur=0.4)
    lp.play(FadeOut(VGroup(ghost, ends)), at=t_hf - 1.9, dur=0.6)

    # 'how far': x, from the middle down to the nearest crack
    mid = Dot(M, radius=0.09, color=C.text)
    xd = DashedLine(M, P3(M[0], CR[0]), dash_length=0.12, stroke_color=C.space, stroke_width=4)
    x_lab = tex("x", 46, C.space).move_to(P3(M[0] + 0.32, (M[1] + CR[0]) / 2))
    lp.play(FadeIn(mid, scale=1.5), at=t_hf - 0.1, dur=0.4)
    lp.play(Create(xd), FadeIn(x_lab), at=t_hf + 0.3, dur=0.7)

    # 'angle': θ, against the boards
    ref = DashedLine(M, M + P3(1.75, 0), dash_length=0.12, stroke_color=C.muted, stroke_width=2.4)
    arc = Arc(radius=0.75, start_angle=0, angle=th, arc_center=M, stroke_color=C.structure, stroke_width=4)
    th_lab = tex(r"\theta", 44, C.structure).move_to(M + 1.08 * P3(math.cos(th / 2), math.sin(th / 2)))
    lp.play(Create(ref), at=t_an - 0.2, dur=0.5)
    lp.play(Create(arc), FadeIn(th_lab), at=t_an + 0.1, dur=0.6)

    # 'rectangle': the rectangle of possibilities; this throw is a dot in it
    rect = rect_axes()
    top.play(Create(rect[0]), FadeIn(rect[1]), at=t_re - 0.3, dur=0.8)
    hero = Dot(M, radius=0.1, color=C.text)
    top.add(hero, at=t_re + 0.45)
    top.play(hero.animate.move_to(rpt(th, xh)), at=t_re + 0.45, dur=0.9, ease="easy_ease")
    guides = VGroup(DashedLine(rpt(th, 0), rpt(th, xh), dash_length=0.08, stroke_color=C.structure, stroke_width=2),
                    DashedLine(rpt(0, xh), rpt(th, xh), dash_length=0.08, stroke_color=C.space, stroke_width=2))
    top.play(Create(guides), at=t_re + 1.35, dur=0.5)
    top.play(FadeOut(guides), at=t_cr - 1.0, dur=0.5)

    # the stream of throws, as dots
    cv = Canvas(DOT_BOX)

    def lit(t):
        return ss((t - t_cr - 0.6) / 1.0)

    def dots(t):
        c = cv.begin()
        draw_dots(c, cv, dots_n(t), lit(t))
        return cv.array()

    s.add(FramesLayer(dots, z=1, during=[(t_re + 0.9, t1)], **cv.layer_kw()))

    # 'crosses': the arch; this stick crosses
    arch = sine_arch()
    top.play(Create(arch), at=t_cr - 0.1, dur=1.3, ease="easy_ease")
    lp.play(stick.animate.set_stroke(color=U), at=t_cr + 0.6, dur=0.6)
    top.play(hero.animate.set_color(U), at=t_cr + 0.6, dur=0.6)
    cond = MathTex("x", r"\le", r"\sin\theta", font_size=52, color=C.text)
    cond[0].set_color(C.space)
    cond[2].set_color(C.change)
    cond.move_to(P3(3.25, 1.95))
    top.play(Write(cond), at=t_under - 0.2, dur=0.8)

    # 'what share': P = ?
    ask = MathTex("P", "=", r"\,?", font_size=56, color=C.text)
    ask[0].set_color(U)
    ask.move_to(P3(3.25, 2.95))
    top.play(FadeIn(ask, shift=0.08 * DOWN), at=t_ws - 0.1, dur=0.5)

    # out: the stick panel leaves; the rectangle stays for ch6_s04
    lp.play(FadeOut(VGroup(cracks, stick, mid, xd, x_lab, ref, arc, th_lab)), at=out_t, dur=0.6)
    top.play(FadeOut(hero), at=out_t, dur=0.6)
