"""c09_s02 · The rule (equation). Storyboard: plan/scene_plan.md § c09_s02. Layout L2.

Opens on c09_s01's last frame (the 98 positives, 9 of them ill, and 9 / (9 + 89) ≈ 9 %), which gives way to a
unit square of everyone. 'Bayes': name tag; the square splits by the prior (the ill strip, 1 %, drawn 8× wider and
tagged so), then each column by test result, and the positive areas light (90 % of the ill, 9 % of the healthy).
'update': Bayes' rule writes in the right column, with A = ill and B = positive. 'before': P(A) lights with the ill
strip; 'explains': P(B|A) with its positive part; 'every way': P(B) with both positive areas, and then P(A|B), the
belief after: the ill share of all the positive area (computed, ≈ 9 %).
"""
import numpy as np
from aion import *

import ch9
from beats import T
from kit import chapter_backdrop, P3, RC, add_rail, fit, glow, glimpse, sans, tag_under, tex


def _carry(s, out):
    ill, pos = ch9.people()
    F = ch9.positives_xy(ch9.split_xy())
    op = fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.7)
    m = s.manim(z=50, parallax=0.0, opacity=op)
    m.add(*[Dot(P3(*F[i]), radius=0.045, color=C.ill if ill[i] else C.muted) for i in np.where(pos)[0]])
    m.add(*[Circle(radius=0.08, stroke_color=C.positive, stroke_width=2.2).move_to(P3(*F[i])) for i in np.where(pos)[0]],
          VGroup(sans("98", 26, C.text), sans("positive", 26, C.positive)).arrange(RIGHT, buff=0.18)
          .move_to(P3(ch9.POS_C[0], ch9.POS_C[1] + 1.55)))
    e = Eqn(r"\frac{9}{9+89}\approx 9\%").scale(1.1).move_to(P3(RC, 0.6))
    m.add(e, sans("about 1 in 11", 28, C.text).next_to(e, DOWN, buff=0.45))


def rect(r, **kw):
    x0, x1, y0, y1 = r
    return Rectangle(width=x1 - x0, height=y1 - y0, **kw).move_to(P3((x0 + x1) / 2, (y0 + y1) / 2))


@scene(T.c09_s02, T.c09_s03)
def s29_c09_rule(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 9)
    t0 = float(s.start)
    t_ba, t_up, t_be, t_ex, t_ev = (T.c09_s02_bayes, T.c09_s02_update, T.c09_s02_before, T.c09_s02_explains,
                                    T.c09_s02_every_way)
    _carry(s, t_ba + 0.2)
    add_rail(s, 9)
    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "bayes", t_ba + 0.4, C.bayes, at_xy=(RC, 1.0))   # the column is empty until "update"

    # the square of everyone
    x0, x1, y0, y1 = ch9.SQ
    R = ch9.sq_regions()
    xs = R["ill_pos"][1]
    m = s.manim(z=4, parallax=0.0)
    t_sq = float(t_ba) + 0.9
    m.play(Create(rect(ch9.SQ, stroke_color=C.muted, stroke_width=2)), at=t_sq, dur=1.0)
    m.play(Create(Line(P3(xs, y0), P3(xs, y1), stroke_color=C.muted, stroke_width=2)), at=t_sq + 1.0, dur=0.6)
    labs = VGroup(sans("ill", 24, C.text).move_to(P3((x0 + xs) / 2, y0 - 0.3)),
                  sans("healthy", 24, C.text).move_to(P3((xs + x1) / 2, y0 - 0.3)))
    m.play(FadeIn(labs), at=t_sq + 1.2, dur=0.5)
    nts = sans("1 %, drawn 8 times wider", 20, C.muted).move_to(P3(x0, y1 + 0.3), aligned_edge=LEFT)
    m.play(FadeIn(nts), at=t_sq + 1.5, dur=0.5)
    yi, yh = R["ill_pos"][2], R["h_pos"][2]
    m.play(Create(Line(P3(x0, yi), P3(xs, yi), stroke_color=C.muted, stroke_width=2)), at=t_sq + 2.3, dur=0.4)
    m.play(Create(Line(P3(xs, yh), P3(x1, yh), stroke_color=C.muted, stroke_width=2)), at=t_sq + 2.5, dur=0.6)
    lit = VGroup(rect(R["ill_pos"], stroke_width=0, fill_color=C.positive, fill_opacity=0.55),
                 rect(R["h_pos"], stroke_width=0, fill_color=C.positive, fill_opacity=0.55))
    s.manim(z=3, parallax=0.0).play(FadeIn(lit), at=t_sq + 3.2, dur=0.8)
    pl = VGroup(sans("positive", 22, C.positive), sans("90 %", 20, C.muted), sans("9 %", 20, C.muted))
    pl[0].move_to(P3(x1, y1 + 0.3), aligned_edge=RIGHT)
    pl[1].move_to(P3((x0 + xs) / 2 - 0.0, yi - 0.25)).next_to(P3(x0, (yi + y1) / 2), LEFT, buff=0.15)
    pl[2].next_to(P3(x1, (yh + y1) / 2), RIGHT, buff=0.15)
    m.play(FadeIn(pl, lag_ratio=0.2), at=t_sq + 3.6, dur=0.8)

    # the rule
    keys = {r"P(A\mid B)": C.text, r"P(B\mid A)": C.text, "P(A)": C.text, "P(B)": C.text}
    e = Eqn(r"P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)}", colors=keys)
    fit(e).move_to(P3(RC, 1.0))
    hud.play(Write(e), at=t_up - 0.1, dur=1.2)
    legend = VGroup(VGroup(tex("A", 30, C.text), sans("ill", 24, C.text)).arrange(RIGHT, buff=0.25),
                    VGroup(tex("B", 30, C.text), sans("positive", 24, C.positive)).arrange(RIGHT, buff=0.25)) \
        .arrange(RIGHT, buff=0.7).move_to(P3(RC, -1.3))
    hud.play(FadeIn(legend, shift=0.05 * UP), at=t_up + 0.9, dur=0.6)

    # before: the prior
    hud.play(e.part("P(A)").animate.set_color(C.prior), at=t_be, dur=0.4)
    hud.play(FadeIn(sans("before", 22, C.prior).next_to(e.part("P(A)"), UP, buff=0.22)), at=t_be + 0.1, dur=0.4)
    glow(s, C.prior, z=5, k=0.7, parallax=0.0, opacity=fade(t_be, dur=0.4, out=t_ex - 0.1, out_dur=0.4)).add(
        rect((x0, xs, y0, y1), stroke_color=C.prior, stroke_width=3.5, fill_opacity=0))

    # explains: how often the ill test positive
    hud.play(e.part(r"P(B\mid A)").animate.set_color(C.positive), at=t_ex, dur=0.4)
    hud.play(FadeIn(sans("explains", 22, C.positive).next_to(e.part(r"P(B\mid A)"), UP, buff=0.22)), at=t_ex + 0.1,
             dur=0.4)
    glow(s, C.positive, z=5, k=0.7, parallax=0.0, opacity=fade(t_ex, dur=0.4, out=t_ev - 0.1, out_dur=0.4)).add(
        rect(R["ill_pos"], stroke_color=C.positive, stroke_width=3.5, fill_opacity=0))

    # every way: all the positive area; and the belief after
    hud.play(e.part("P(B)").animate.set_color(C.positive), at=t_ev, dur=0.4)
    hud.play(FadeIn(tag_under(e, "P(B)", "all positives", C.positive)), at=t_ev + 0.1, dur=0.4)
    glow(s, C.positive, z=5, k=0.7, parallax=0.0, opacity=fade(t_ev, dur=0.4)).add(
        rect(R["ill_pos"], stroke_color=C.positive, stroke_width=3.5, fill_opacity=0),
        rect(R["h_pos"], stroke_color=C.positive, stroke_width=3.5, fill_opacity=0))
    t_af = float(t_ev) + 0.9
    hud.play(e.part(r"P(A\mid B)").animate.set_color(C.bayes), at=t_af, dur=0.4)
    hud.play(FadeIn(tag_under(e, r"P(A\mid B)", "after", C.bayes)), at=t_af + 0.1, dur=0.4)
    hud.play(FadeIn(tex(rf"\approx {100 * ch9.posterior():.0f}\%", 34, C.bayes).next_to(e, RIGHT, buff=0.0)
                    .next_to(legend, UP, buff=0.35)), at=t_af + 0.3, dur=0.4)
