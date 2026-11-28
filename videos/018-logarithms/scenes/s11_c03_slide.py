"""c03_s02 · Multiplying by sliding. Storyboard: plan/scene_plan.md § c03_s02.

2 × 3 on the slide rule: the upper scale slides until its 1 sits over the lower 2; the cursor (a faint glowing ivory
line) moves to the upper 3 and reads 6 beneath. Two periwinkle bars, log 2 then log 3, lie end to end and land on 6:
log 2 + log 3 = log 6. On "Engineers" the frame pulls back and a second product runs silently (3.5 × 2.4 = 8.4), then
three line drawings in ivory: a truss bridge, a wing and a Saturn V.
"""
import math

import numpy as np
from aion import *

from beats import T
from ch3 import BH, L, LO, OFF2, UP, XL, slide_rule, xpos
from kit import P3, add_rail, ctex, glow, mix, polyline, ramp, tex, tint, word_at

OFF35 = L * math.log10(3.5)


def _bridge():
    g = VGroup()
    w, h, n = 3.0, 0.7, 6
    xs = np.linspace(-w / 2, w / 2, n + 1)
    g.add(Line(P3(xs[0], 0), P3(xs[-1], 0), stroke_color=C.ruler, stroke_width=2.5),
          Line(P3(xs[1], h), P3(xs[-2], h), stroke_color=C.ruler, stroke_width=2.5))
    for i, x in enumerate(xs):
        if 0 < i < n:
            g.add(Line(P3(x, 0), P3(x, h), stroke_color=C.ruler, stroke_width=1.6))
        if i < n:
            a, b = (P3(x, 0), P3(xs[i + 1], h)) if i < n / 2 else (P3(x, h), P3(xs[i + 1], 0))
            if i == 0:
                a, b = P3(x, 0), P3(xs[1], h)
            if i == n - 1:
                a, b = P3(x, h), P3(xs[-1], 0)
            g.add(Line(a, b, stroke_color=C.ruler, stroke_width=1.6))
    return g


def _wing():
    top = [(-1.5, 0.0), (-1.2, 0.18), (-0.6, 0.26), (0.3, 0.2), (1.5, 0.02)]
    bot = [(1.5, 0.02), (0.3, -0.06), (-0.6, -0.1), (-1.2, -0.08), (-1.5, 0.0)]
    g = VGroup(polyline(top, C.ruler, 2.5, smooth=True), polyline(bot, C.ruler, 2.5, smooth=True))
    for k in range(1, 5):
        g.add(DashedLine(P3(-1.5 + 0.6 * k, -0.4), P3(-1.5 + 0.6 * k + 0.4, 0.5), stroke_color=tint(C.ruler, 0.45),
                         stroke_width=1.2, dash_length=0.06))
    return g


def _rocket():
    pts = [(0, 1.15), (0.12, 0.9), (0.16, 0.6), (0.16, -0.2), (0.2, -0.3), (0.2, -0.85), (0.32, -1.05),
           (-0.32, -1.05), (-0.2, -0.85), (-0.2, -0.3), (-0.16, -0.2), (-0.16, 0.6), (-0.12, 0.9), (0, 1.15)]
    g = VGroup(polyline(pts, C.ruler, 2.2))
    for y in (0.6, -0.2, -0.85):
        g.add(Line(P3(-0.2, y), P3(0.2, y), stroke_color=tint(C.ruler, 0.6), stroke_width=1.4))
    return g


@scene(T.c03_s02, T.c03_s03)
def s11_c03_slide(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 3)
    ts, t3, t6 = float(T.c03_s02_slide_the_upper_scal), float(T.c03_s02_three), float(T.c03_s02_six)
    te = float(T.c03_s02_engineers)
    tb = float(T.c03_s02_bridges)
    end = float(s.end)

    def off(t):
        return OFF2 * ramp(t, ts, 1.6) + (OFF35 - OFF2) * ramp(t, te + 0.8, 1.2)
    rule_op = Track(lambda t: 1.0 - 0.75 * ramp(t, tb - 0.4, 0.6) - 0.25 * ramp(t, end - 0.7, 0.6))
    slide_rule(s, off, opacity=rule_op)

    # the cursor: on the lower 2 while sliding, then on upper 3 = lower 6; later 2.4 → 8.4
    def cur_x(t):
        x = xpos(2)
        x += (xpos(6) - xpos(2)) * ramp(t, t3, 0.9)
        x += (xpos(8.4) - xpos(6)) * ramp(t, te + 2.0, 1.0)
        return x
    top, bot = UP + BH / 2 + 0.2, LO - BH / 2 - 0.2
    cur = glow(s, C.ruler, z=5, k=0.7, opacity=Track(lambda t: ramp(t, ts + 1.2, 0.4) * rule_op(t)))
    cur.redraw(lambda t: Line(P3(cur_x(t), top), P3(cur_x(t), bot), stroke_color=C.ruler, stroke_width=1.8),
               during=(ts + 1.0, end))
    m = s.manim(z=6)
    one = Circle(radius=0.2, stroke_color=C.base, stroke_width=2.5).move_to(P3(xpos(2), UP - BH / 2 + 0.5))
    m.play(Create(one), at=ts + 1.6, dur=0.5)
    m.play(FadeOut(one), at=t3 - 0.3, dur=0.4)
    three = tex("3", 44, C.value).move_to(P3(xpos(6) + 0.32, top + 0.25))
    six = tex("6", 44, C.value).move_to(P3(xpos(6) + 0.32, bot - 0.25))
    m.play(FadeIn(three, scale=1.3), at=t3 + 0.6, dur=0.4)
    m.play(FadeIn(six, scale=1.3), at=t6, dur=0.4)
    gl = glow(s, C.value, z=5, k=0.8)
    dot6 = Dot(P3(xpos(6), LO + BH / 2), radius=0.07, color=C.value)
    gl.play(FadeIn(dot6), at=t6, dur=0.4)

    # lengths add: log 2 then log 3, end to end
    ta = float(T.c03_s02_added_end_to_end)
    by = LO - BH / 2 - 0.85
    b2 = Line(P3(XL, by), P3(xpos(2), by), stroke_color=C.steps, stroke_width=8)
    b3 = Line(P3(xpos(2), by), P3(xpos(6), by), stroke_color=mix(C.steps, C.text, 0.45), stroke_width=8)
    l2 = tex(r"\log 2", 30, C.steps).next_to(b2, DOWN, buff=0.15)
    l3 = tex(r"\log 3", 30, mix(C.steps, C.text, 0.45)).next_to(b3, DOWN, buff=0.15)
    m.play(Create(b2), FadeIn(l2), at=ta, dur=0.7)
    m.play(Create(b3), FadeIn(l3), at=ta + 0.8, dur=0.8)
    eq = ctex([(r"\log ", None), ("2", C.value), ("+", None), (r"\log ", None), ("3", C.value), ("=", None),
               (r"\log ", None), ("6", C.value)], 58).move_to(P3(2.6, 2.6))
    m.play(Write(eq), at=T.c03_s02_multiplies, dur=1.0)
    sub = ctex([("2", C.value), (r"\times", None), ("3", C.value), ("=", None), ("6", C.value)], 42)
    m.play(FadeIn(sub.next_to(eq, DOWN, buff=0.3)), at=float(T.c03_s02_multiplies) + 0.8, dur=0.6)
    sm = VGroup(b2, b3, l2, l3, three, six)
    m.play(FadeOut(sm), at=te - 0.3, dur=0.5)
    gl.play(FadeOut(dot6), at=te - 0.3, dur=0.5)

    # engineers: pull back, a second product runs silently, then three drawings
    s.camera.push(te, zoom=0.88, dur=2.0)
    ex = tex(r"3.5\times2.4=8.4", 34, C.muted).move_to(P3(-3.6, 1.6))
    m.play(FadeIn(ex), at=te + 0.9, dur=0.6)
    hud = s.manim(z=8, parallax=0.0)
    draws = [(_bridge(), "bridges", -4.3), (_wing(), "aircraft", 0.0), (_rocket(), "rockets", 4.2)]
    for d, w, x in draws:
        d.move_to(P3(x, 2.1))
        hud.play(Create(d, lag_ratio=0.05), at=word_at(w, tb - 0.5), dur=1.0)
    hud.play(FadeOut(VGroup(*[d for d, _, _ in draws])), at=end - 0.3, dur=0.5)
    m.play(FadeOut(VGroup(eq, sub, ex)), at=tb - 0.4, dur=0.5)
