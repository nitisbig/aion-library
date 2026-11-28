"""c02_s03 · Putting the rules to work. Storyboard: plan/scene_plan.md § c02_s03.

A worked example: how many digits does 2¹⁰⁰ have? A ten-by-ten block of a hundred 2s fills in with a running count, and
on the power rule the hundred twos gather into the coefficient of 100 · log₁₀ 2; log₁₀ 2 ≈ 0.30103, so log₁₀ 2¹⁰⁰ ≈ 30.103 (logdata). A
ruler from 10³⁰ to 10³¹ (its ticks on a log scale) takes a marker at 30.103, and the 31-digit number types out with its
digits counted underneath. Napier's page comes up faintly behind on "twenty years".
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from kit import P3, X0, Y1, add_rail, chapter_break, ctex, glow, paper_page, ramp, sans, tex, tint, word_at

RX = 3.3


@scene(T.c02_s03, T.c03_s01)
def s09_c02_digits(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 2)
    chapter_break(s, 3, T.c03_s01)
    hud = s.manim(z=10, parallax=0.0)                     # screen-locked: the column stays while the camera dollies

    # the question
    th = float(T.c02_s03_hard_questions)
    q = VGroup(ctex([("2", C.base), ("^{100}", C.steps)], 80), sans("how many digits?", 26, C.muted))
    q.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(P3(X0 + 0.2, Y1 - 0.55), aligned_edge=UL)
    hud.play(FadeIn(q[0], shift=0.1 * UP), at=th + 1.2, dur=0.7)
    hud.play(FadeIn(q[1]), at=word_q(th), dur=0.6)

    # a hundred twos, as a ten-by-ten block with a running count down its right edge
    t2 = float(T.c02_s03_hundred_twos)
    row = s.manim(z=5, parallax=0.0)
    gx, gy, dx, dy = 0.35, 1.75, 0.5, 0.42
    twos, dots, counts = VGroup(), VGroup(), VGroup()
    for i in range(100):
        r, c = divmod(i, 10)
        twos.add(tex("2", 34, C.base).move_to(P3(gx + dx * c, gy - dy * r)))
        if i < 99:
            dots.add(tex(r"\cdot", 30, C.muted).move_to(P3(gx + dx * (c + 0.5), gy - dy * r)))
    for r in range(10):
        counts.add(tex(str(10 * (r + 1)), 22, C.steps).move_to(P3(gx + dx * 9 + 0.75, gy - dy * r), aligned_edge=LEFT))
    rows = [VGroup(*twos[10 * r:10 * r + 10], *dots[10 * r:min(10 * r + 10, 99)]) for r in range(10)]
    row.play(LaggedStart(*[FadeIn(g, shift=0.15 * RIGHT) for g in rows], lag_ratio=0.35), at=t2 - 0.4, dur=2.4)
    row.play(LaggedStart(*[FadeIn(g) for g in counts], lag_ratio=0.35), at=t2 - 0.1, dur=2.4)
    tw = word_at("nobody", th)                                   # "Nobody wants to multiply that out"
    row.play(LaggedStart(*[Indicate(g, color=C.text, scale_factor=1.08) for g in rows], lag_ratio=0.15), at=tw,
             dur=1.6)

    # the power rule: the hundred twos gather into the coefficient 100
    tp = float(T.c02_s03_power_rule)
    row.play(FadeOut(VGroup(dots, counts)), at=tp + 0.1, dur=0.5)
    l1 = ctex([(r"\log_{10}", None), ("2", C.base), ("^{100}", C.steps), ("=", None), ("100", C.steps),
               (r"\,\log_{10}", None), ("2", C.base)], 52).move_to(P3(RX, 2.6))
    gather = l1[4].get_center()
    row.play(LaggedStart(*[t.animate.move_to(gather).scale(0.3).set_opacity(0) for t in twos], lag_ratio=0.012),
             at=tp + 0.3, dur=1.4, lead=0.0)
    hud.play(Write(VGroup(*l1[:4], *l1[5:])), at=tp + 0.8, dur=1.2)
    hud.play(FadeIn(l1[4], scale=1.6), at=tp + 1.5, dur=0.5, lead=0.0)
    tz = float(T.c02_s03_zero_point_three_zer)
    l2 = ctex([(r"\log_{10}", None), ("2", C.base), (r"\approx", None), (f"{ld.LOG10_2:.5f}", C.steps)], 48)
    l2.move_to(P3(RX, 1.65))
    hud.play(Write(l2), at=tz, dur=0.9)
    tt = float(T.c02_s03_thirty_point_one)
    l3 = ctex([("100", C.steps), (r"\times", None), (f"{ld.LOG10_2:.5f}", C.steps), ("=", None),
               (f"{ld.TWO_100_LOG:.3f}", C.steps)], 48).move_to(P3(RX, 0.75))
    hud.play(TransformFromCopy(l1[4], l3[0]), TransformFromCopy(l2[3], l3[2]), at=tt - 0.9, dur=0.8)
    hud.play(Write(VGroup(l3[1], l3[3], l3[4])), at=tt - 0.1, dur=0.8)

    # between 10^30 and 10^31: a decade ruler with the marker at 30.103
    tb = float(T.c02_s03_between_ten_to_the_t)
    xa, xb, yr = -4.4, 4.4, -0.55
    X = lambda e: xa + (xb - xa) * (e - 30)  # noqa: E731
    hud.play(VGroup(l1, l2).animate.set_opacity(0.6), at=tb - 0.3, dur=0.6)
    ruler = VGroup(Line(P3(xa, yr), P3(xb, yr), stroke_color=C.ruler, stroke_width=2.5))
    for k in range(1, 11):
        x = X(30 + math.log10(k))
        ruler.add(Line(P3(x, yr), P3(x, yr - (0.24 if k in (1, 10) else 0.13)), stroke_color=C.ruler,
                       stroke_width=2 if k in (1, 10) else 1.3))
        if 1 < k < 10:
            ruler.add(tex(str(k), 20, tint(C.ruler, 0.7)).move_to(P3(x, yr - 0.3)))
    ruler.add(tex("10^{30}", 30, C.ruler).move_to(P3(xa, yr - 0.5)), tex("10^{31}", 30, C.ruler).move_to(P3(xb, yr - 0.5)))
    hud.play(Create(ruler[0]), FadeIn(ruler[1:]), at=tb, dur=1.0)
    xm = X(ld.TWO_100_LOG)
    mk = glow(s, C.value, z=11, k=0.8, parallax=0.0)
    mk.play(FadeIn(VGroup(Line(P3(xm, yr + 0.35), P3(xm, yr - 0.05), stroke_color=C.value, stroke_width=3),
                          Dot(P3(xm, yr + 0.35), radius=0.07, color=C.value)), shift=0.3 * DOWN), at=tb + 1.2, dur=0.6)
    hud.play(FadeIn(ctex([("2", C.base), ("^{100}", C.steps)], 34).move_to(P3(xm, yr + 0.7))), at=tb + 1.4, dur=0.5)
    ineq = ctex([("10^{30}", C.ruler), ("<", None), ("2", C.base), ("^{100}", C.steps), ("<", None),
                 ("10^{31}", C.ruler)], 44).move_to(P3(RX, -0.1))
    hud.play(FadeIn(ineq), at=tb + 2.0, dur=0.7)
    hud.play(VGroup(l3).animate.set_opacity(0.6), at=tb + 2.0, dur=0.6)

    # thirty one digits, typed out and counted
    td = float(T.c02_s03_thirty_one_digits)
    digits = str(ld.TWO_100)
    num = tex(digits, 44, C.value).move_to(P3(0, -1.95))
    glyphs = num[0]
    hud.play(LaggedStart(*[FadeIn(g) for g in glyphs], lag_ratio=0.6), at=td - 1.6, dur=1.8, lead=0.0)
    unders = VGroup(*[Line(g.get_corner(DL) + DOWN * 0.12, g.get_corner(DR) + DOWN * 0.12, stroke_color=C.steps,
                           stroke_width=2.5) for g in glyphs])
    hud.play(LaggedStart(*[Create(u) for u in unders], lag_ratio=0.6), at=td + 0.2, dur=1.4, lead=0.0)
    hud.play(FadeIn(VGroup(tex(str(len(digits)), 44, C.steps), sans("digits", 24, C.muted)).arrange(RIGHT, buff=0.15)
                    .next_to(num, DOWN, buff=0.35)), at=td + 1.5, dur=0.6)

    # Napier's twenty years: the page, faint, behind
    ty = float(T.c02_s03_twenty_years)
    page = paper_page()
    page[..., :3] = (page[..., :3] * 0.16).astype(np.uint8)
    s.add(ArrayLayer(page, height=7.6, pos=(-3.3, 0.0), z=-20, parallax=0.0, opacity=fade(ty - 1.2, dur=1.4)))


def word_q(after):
    from kit import word_at
    return word_at("many", after)
