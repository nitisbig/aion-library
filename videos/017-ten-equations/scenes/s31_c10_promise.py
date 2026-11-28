"""c10_s01 · A promise (hook). Storyboard: plan/scene_plan.md § c10_s01. Layout L1.

Opens on c09_s03's last frame (a belief about a price, on its side a year ahead), which gives way to the chapter
card. 'right': a ticket: the right to buy at $100 in a year. Payoff axes: price in a year against what the right is
worth. 'one fifty': a price marker slides to 150 and the right is worth 50; 'falls': it slides to 70 and the right
is worth nothing. 'option': the whole payoff max(S − K, 0) traces, the hockey stick, and its formula writes.
'today': the payoff gives way to a price chart, and the first price paths (risk-neutral GBM, seeded) set out from
today's 100 towards a year from now.
"""
import math

import numpy as np
from aion import *

import ch9
import ch10
from beats import T
from kit import P3, RC, add_rail, chapter_card, glow, polyline, sans, smooth01, tag_under, tint


def _carry(s, out):
    """c09_s03's last frame: the chart with today's price and the widened belief on its side."""
    op = fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.7)
    a7, b7 = ch9.belief(ch9.N_CURVES - 1)
    mu = a7 / (a7 + b7)
    OX, TX, PY0, PY1 = -4.6, 2.2, -2.3, 2.2
    xs = np.linspace(0, 1, 160)
    y = np.exp(-0.5 * ((xs - mu) / 0.2) ** 2) / (0.2 * math.sqrt(2 * math.pi))
    glow(s, C.bayes, z=6, k=0.8, parallax=0.0, opacity=op).add(
        polyline(list(zip(TX + 0.38 * y, PY0 + (PY1 - PY0) * xs)), C.bayes, 3.0))
    today = P3(OX, PY0 + (PY1 - PY0) * mu)
    s.manim(z=5, parallax=0.0, opacity=op).add(
        Line(P3(OX, PY0), P3(OX, PY1 + 0.1), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
        Line(P3(OX, PY0), P3(TX + 1.4, PY0), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
        sans("price", 22, C.muted).next_to(P3(OX, PY1 + 0.1), UP, buff=0.1),
        sans("time", 22, C.muted).next_to(P3(TX + 1.4, PY0), RIGHT, buff=0.12),
        DashedLine(P3(TX, PY0), P3(TX, PY1), dash_length=0.08, stroke_color=tint(C.muted, 0.5), stroke_width=1.2),
        sans("a year from now", 20, C.muted).next_to(P3(TX, PY0), DOWN, buff=0.15),
        Dot(today, radius=0.07, color=C.light), sans("today", 20, C.text).next_to(today, LEFT, buff=0.15),
        DashedLine(today, P3(TX, PY0 + (PY1 - PY0) * mu), dash_length=0.08, stroke_color=tint(C.muted, 0.6),
                   stroke_width=1.2))


def ticket():
    w, h, n = 3.3, 1.45, 0.16
    pts = [(-w / 2 + n, h / 2), (w / 2 - n, h / 2), (w / 2, h / 2 - n), (w / 2, -h / 2 + n), (w / 2 - n, -h / 2),
           (-w / 2 + n, -h / 2), (-w / 2, -h / 2 + n), (-w / 2, h / 2 - n)]
    edge = Polygon(*[P3(*p) for p in pts], stroke_color=C.payoff, stroke_width=2.2)
    perf = DashedLine(P3(-w / 2 + 0.55, h / 2), P3(-w / 2 + 0.55, -h / 2), dash_length=0.07, stroke_color=C.payoff,
                      stroke_width=1.4)
    txt = VGroup(sans("the right to buy", 26, C.text), sans("at $100", 26, C.payoff), sans("in one year", 22, C.muted)) \
        .arrange(DOWN, buff=0.1).move_to(P3(0.3, 0))
    return VGroup(edge, perf, txt)


@scene(T.c10_s01, T.c10_s02)
def s31_c10_promise(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_ri, t_of, t_fa, t_op, t_to = (T.c10_s01_right, T.c10_s01_one_fifty, T.c10_s01_falls, T.c10_s01_option,
                                    T.c10_s01_today)
    _carry(s, t0 + 0.25)
    chapter_card(s, 10, at=t0 + 0.55, out=t_ri + 0.5)
    add_rail(s, 10, opacity=fade(t0 + 0.4, dur=0.8))
    hud = s.manim(z=50, parallax=0.0)

    # the promise
    tk = ticket().move_to(P3(RC, 2.05))
    hud.play(FadeIn(tk, shift=0.1 * DOWN), at=t_ri + 0.9, dur=0.7)

    # the payoff axes: price in a year, and what the right is then worth
    p_op = fade(t_of - 1.7, dur=0.7, out=t_to - 0.3, out_dur=0.6)
    pa = s.manim(z=4, parallax=0.0, opacity=p_op)
    x0, y0 = ch10.ppt(0, 0)
    xe, ye = ch10.ppt(ch10.S_MAX, ch10.V_MAX)
    pa.add(Line(P3(x0, y0), P3(xe + 0.15, y0), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
           Line(P3(x0, y0), P3(x0, ye + 0.1), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
           sans("price in a year", 22, C.muted).next_to(P3(xe + 0.15, y0), RIGHT, buff=0.15),
           sans("worth", 22, C.muted).next_to(P3(x0, ye + 0.1), UP, buff=0.1))
    for S_ in (50, 100, 150, 200):
        q = ch10.ppt(S_, 0)
        pa.add(Line(P3(q[0], y0), P3(q[0], y0 - 0.08), stroke_color=tint(C.muted, 0.7), stroke_width=1.4),
               sans(f"{S_}", 18, C.muted).next_to(P3(q[0], y0 - 0.08), DOWN, buff=0.06))
    q = ch10.ppt(0, 50)
    pa.add(Line(P3(x0 - 0.08, q[1]), P3(x0, q[1]), stroke_color=tint(C.muted, 0.7), stroke_width=1.4),
           sans("50", 18, C.muted).next_to(P3(x0 - 0.08, q[1]), LEFT, buff=0.06))

    def price(t):
        S = 100.0
        S += 50.0 * float(smooth01((t - float(t_of) + 0.3) / 0.9))
        S -= 80.0 * float(smooth01((t - float(t_fa) + 0.2) / 0.9))
        return S

    def slider(t):
        a = float(p_op(t)) * float(fade(t_of - 0.6, dur=0.4, out=t_op + 0.1, out_dur=0.5)(t))
        if a < 0.01:
            return VGroup()
        S = price(t)
        v = max(S - ch10.K, 0.0)
        b = ch10.ppt(S, 0)
        g = VGroup(Dot(P3(b[0], y0), radius=0.08, color=C.light, fill_opacity=a),
                   sans(f"${S:.0f}", 22, C.text).set_opacity(a).next_to(P3(b[0], y0), DOWN, buff=0.5))
        h = ch10.ppt(S, v)[1] - y0
        if h > 0.01:
            g.add(Rectangle(width=0.18, height=h, stroke_width=0, fill_color=C.payoff, fill_opacity=a)
                  .move_to(P3(b[0], y0 + h / 2)))
        g.add(sans(f"worth ${v:.0f}", 24, C.payoff).set_opacity(a).next_to(P3(b[0], y0 + max(h, 0)), UP, buff=0.15))
        return g
    s.manim(z=6, parallax=0.0).redraw(slider, during=(t_of - 0.8, t_op + 0.8))

    # the option: the whole payoff, the hockey stick
    stick = polyline([tuple(ch10.ppt(0, 0)), tuple(ch10.ppt(ch10.K, 0)), tuple(ch10.ppt(ch10.S_MAX, ch10.S_MAX - ch10.K))],
                     C.payoff, 4.0)
    sk = glow(s, C.payoff, z=5, k=0.8, parallax=0.0, opacity=p_op)
    sk.play(Create(stick), at=t_op, dur=1.2)
    pa.play(FadeIn(sans("option", 26, C.payoff).next_to(P3(*ch10.ppt(160, 60)), LEFT, buff=0.25)), at=t_op + 0.6,
            dur=0.5)
    hud.play(FadeOut(tk), at=t_op - 0.2, dur=0.5)
    e = Eqn(r"\max(S-K,\,0)", colors={"S": C.text, "K": C.text})
    e.scale(1.1).move_to(P3(RC, 1.6))
    hud.play(Write(e), at=t_op + 0.3, dur=1.0)
    hud.play(FadeIn(VGroup(tag_under(e, "S", "price", C.muted), tag_under(e, "K", "100", C.muted)), shift=0.05 * UP),
             at=t_op + 1.0, dur=0.5)

    # today: nobody knows where the price will go
    s.manim(z=4, parallax=0.0, opacity=fade(t_to - 0.1, dur=0.6)).add(ch10.chart_axes())
    s.manim(z=3, parallax=0.0).redraw(lambda t: ch10.few_paths(t, float(t_to) + 0.3), during=(t_to, s.end))
