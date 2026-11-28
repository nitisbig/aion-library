"""ch3_s01 · What stays the same (Chapter 3 hook).

The map (turned twice, Foundations and Quantity lit) gives way: Structure, now at the bottom, opens into Chapter 3's
card, which shrinks away. A violet square stands beside the circle, each over a dashed ghost of where it started. On
'a little' the square turns 20° and visibly misses its ghost; on 'quarter' it goes on to 90° and lands back on it,
the ghost flashing. On 'turn the circle' the circle turns on and on, a rim dot proving it moves, and always matches its
ghost. On 'symmetry' the word comes up in small caps; on 'four' four quarter-turn arrows ring the square; on 'every' a
fan of turn marks sweeps all the way round the circle.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, P3, caps, chapter_card, map_state, node_xy, tex, the_circle, window, hub_at

SQ_C, SQ_S = P3(-3.3, 0.0), 2.5
CI_C, CI_R = P3(3.3, 0.0), 1.45
FQ = (("foundations", "quantity"),)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ramp(t, keys):
    """Piecewise smoothstep through (t, value) keys."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if t <= tb:
            return va + (vb - va) * ss((t - ta) / (tb - ta))
    return keys[-1][1]


@scene(T.ch3_s01, T.ch3_s02)
def ch3_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    mp_, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    card_l = s.manim(z=3, parallax=0)
    t0 = float(s.start)
    t_lit, t_q, t_tc = float(T.ch3_s01_a_little), float(T.ch3_s01_quarter), float(T.ch3_s01_turn_the_circle)
    t_sym, t_4, t_ev = float(T.ch3_s01_symmetry), float(T.ch3_s01_four), float(T.ch3_s01_every)
    V = C.structure

    # where Chapter 2 left the map; Structure (now at the bottom) opens into the card
    links, nodes = map_state(120, lit=("foundations", "quantity"), edges=FQ)
    hub = hub_at(120)
    mp_.add(links)
    nd.add(nodes)
    m.add(hub)
    mp_.play(FadeOut(links), at=t0 + 0.1, dur=0.5)
    nd.play(FadeOut(VGroup(*(nodes[k] for k in (0, 1, 3, 4, 5)))), at=t0 + 0.1, dur=0.5)
    nd.play(FadeOut(nodes[2], scale=1.6), at=t0 + 0.15, dur=0.5)
    m.play(FadeOut(hub), at=t0 + 0.1, dur=0.5)
    card = chapter_card("structure", "symmetry and algebra")
    origin = node_xy(2, turn=120)
    card_l.play(GrowFromPoint(card, origin), at=t0 + 0.2, dur=0.7, ease="easy_ease")
    card_l.play(card.animate.scale(0.05).move_to(origin).set_opacity(0), at=t_lit - 1.0, dur=0.6, ease="easy_ease")
    card_l.remove(card, at=t_lit - 0.35)

    # the ghosts: where each shape started
    g_sq = DashedVMobject(Square(SQ_S, stroke_color=C.map_off, stroke_width=2.4).move_to(SQ_C), num_dashes=48)
    g_ci = DashedVMobject(Circle(radius=CI_R, stroke_color=C.map_off, stroke_width=2.4).move_to(CI_C), num_dashes=60)
    m.play(FadeIn(g_sq), FadeIn(g_ci), at=t_lit - 0.6, dur=0.5)

    sq_keys = [(t_lit - 0.1, 0.0), (t_lit + 0.6, 20.0), (t_q - 0.2, 20.0), (t_q + 1.0, 90.0)]
    ci_keys = [(t_tc + 0.1, 0.0), (t_tc + 4.6, 250.0)]

    def shapes(t):
        a = math.radians(ramp(t, sq_keys))
        sq = Square(SQ_S, stroke_color=V, stroke_width=5, fill_color=V, fill_opacity=0.08).move_to(SQ_C).rotate(a)
        d = SQ_S / math.sqrt(2)
        mark = Dot(SQ_C + d * P3(math.cos(a + math.pi / 4), math.sin(a + math.pi / 4)), radius=0.08, color=C.text)
        b = math.radians(ramp(t, ci_keys))
        ci = the_circle(CI_R).move_to(CI_C)
        dot = Dot(CI_C + CI_R * P3(math.cos(b + math.pi / 4), math.sin(b + math.pi / 4)), radius=0.08, color=V)
        f = 1 - ss((t - float(s.end) + 0.7) / 0.6)              # the square and the rim dot leave; the circle stays
        if f < 1:
            for mob in (sq, mark, dot):
                mob.set_stroke(opacity=mob.get_stroke_opacity() * f)
                mob.set_fill(opacity=mob.get_fill_opacity() * f)
        return VGroup(sq, mark, ci, dot)

    t_in = t_lit - 1.2
    sh0 = shapes(t_in)
    m.play(FadeIn(sh0, scale=0.9), at=t_in, dur=0.6)
    m.remove(sh0, at=t_in + 0.62)
    top.redraw(window(shapes, t_in + 0.6, float(s.end)), during=(t_in + 0.6, float(s.end)))

    # the square lands back on its ghost: the ghost flashes
    flash = Square(SQ_S, stroke_color=C.text, stroke_width=3).move_to(SQ_C)
    m.play(flash.animate.scale(1.12).set_stroke(opacity=0), at=t_q + 1.0, dur=0.6)
    m.remove(flash, at=t_q + 1.7)

    # 'symmetry'
    word = caps("symmetry", 56, V).move_to(P3(0, 3.0))
    m.play(FadeIn(word, shift=0.1 * DOWN), at=t_sym - 0.1, dur=0.6)

    # 'four': four quarter-turn arrows round the square
    RA = SQ_S / math.sqrt(2) + 0.35
    arrows = VGroup(*(Arc(radius=RA, start_angle=math.radians(90 * k + 55), angle=math.radians(70), arc_center=SQ_C,
                          stroke_color=V, stroke_width=3).add_tip(tip_length=0.18, tip_width=0.16) for k in range(4)))
    n4 = tex("4", 52, V).move_to(SQ_C + P3(0, -RA - 0.55))
    m.play(LaggedStart(*(Create(a_) for a_ in arrows), lag_ratio=0.25), at=t_4, dur=1.0)
    m.play(FadeIn(n4, shift=0.06 * UP), at=t_4 + 0.6, dur=0.5)

    # 'every': a fan of turn marks all the way round the circle
    fan = VGroup(*(Line(CI_C + (CI_R + 0.18) * P3(math.cos(a), math.sin(a)),
                        CI_C + (CI_R + 0.42) * P3(math.cos(a), math.sin(a)), stroke_color=V, stroke_width=2)
                   for a in np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, 90, endpoint=False)))
    ninf = tex(r"\infty", 56, V).move_to(CI_C + P3(0, -CI_R - 0.95))
    m.play(LaggedStart(*(FadeIn(f_) for f_ in fan), lag_ratio=0.02), at=t_ev - 0.3, dur=1.0)
    m.play(FadeIn(ninf, shift=0.06 * UP), at=t_ev + 0.3, dur=0.5)
    m.play(FadeOut(VGroup(g_sq, g_ci, word, arrows, n4, fan, ninf)), at=float(s.end) - 0.7, dur=0.6)

