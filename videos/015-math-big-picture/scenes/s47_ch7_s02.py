"""ch7_s02 · One short line (Euler's identity).

The e, i, π tracker from Chapters 3 and 5 sits in the corner. The map steps back and the hub grows into the unit
circle, with 1 on its right. On 'promised' the three glyphs leave the tracker. On 'half turn' a point sweeps from 1 to
−1 along a violet arc (C.structure), π (gold) labels the turn, and e^{iπ} = −1 writes. On 'Euler's identity' it becomes
e^{iπ} + 1 = 0 in pillar colors (e change, i structure, π quantity, 1 and 0 foundations). The circle shrinks back to
the hub, the map returns, and the identity settles in the hub. On 'change', 'turning', 'Pi' copies of e, i, π fly to
their nodes, and 1 and 0 to Foundations. On 'every part' the chord Structure–Change draws and the identity glows once.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import glow_layer, HUB_R, P3, PILLARS, map_state, node_xy, tex, the_circle, window

ALL = PILLARS
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"), ("change", "uncertainty"),
         ("space", "uncertainty"), ("quantity", "uncertainty"), ("foundations", "space"), ("foundations", "change"),
         ("foundations", "uncertainty"))
NEW = (("structure", "change"),)
UC = P3(-1.6, 0.0)                              # the unit circle's centre
R2 = 2.3


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch7_s02, T.ch7_s03)
def ch7_s02(s):
    s.solid(C.bg, z=-200)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_pr, t_ht, t_eu = float(T.ch7_s02_promised), float(T.ch7_s02_half_turn), float(T.ch7_s02_euler_s_identity)
    t_ch, t_tu, t_pi, t_ep = float(T.ch7_s02_change), float(T.ch7_s02_turning), float(T.ch7_s02_pi), float(
        T.ch7_s02_every_part)
    t_one, t_minus = t_pi + 1.94, t_ht + 1.96                           # 'one and zero' 'minus one'
    Ch, St, Q, F = C.change, C.structure, C.quantity, C.foundations

    links, nodes = map_state(0, lit=ALL, edges=EDGES)
    hub = the_circle(fill_color=C.bg, fill_opacity=1.0)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)

    # the tracker in its corner
    tb = RoundedRectangle(width=1.95, height=0.78, corner_radius=0.14, stroke_color=C.map_off, stroke_width=1.6)
    tb.move_to(P3(5.75, -3.35))
    tracked = VGroup(tex("e", 40, Ch), tex("i", 40, St), tex(r"\pi", 40, Q)).arrange(RIGHT, buff=0.38).move_to(tb)
    top.play(FadeIn(tb), FadeIn(tracked), at=t0 + 0.2, dur=0.5)

    # the map steps back; the hub becomes the unit circle
    t_back = t0 + 0.8
    lnk.play(FadeOut(links), at=t_back, dur=0.6)
    nd.play(FadeOut(nodes), at=t_back, dur=0.6)
    unit = the_circle(R2, fill_color=C.bg, fill_opacity=1.0).move_to(UC)
    m.play(Transform(hub, unit), at=t_back + 0.2, dur=1.0, ease="easy_ease")
    axes = VGroup(Line(UC + P3(-R2 - 0.5, 0), UC + P3(R2 + 0.5, 0), stroke_color=C.grid, stroke_width=1.6),
                  Line(UC + P3(0, -R2 - 0.5), UC + P3(0, R2 + 0.5), stroke_color=C.grid, stroke_width=1.6))
    one = tex("1", 40, C.text).move_to(UC + P3(R2 + 0.35, -0.35))
    m.play(FadeIn(axes), FadeIn(one), at=t_back + 1.0, dur=0.5)

    # 'promised': the glyphs leave the tracker
    row = VGroup(tex("e", 60, Ch), tex("i", 60, St), tex(r"\pi", 60, Q)).arrange(RIGHT, buff=0.5).move_to(P3(4.4, 2.6))
    fly = tracked.copy()
    top.add(fly, at=t_pr - 0.1)
    top.play(Transform(fly, row), at=t_pr - 0.1, dur=1.0, ease="easy_ease")
    top.play(FadeOut(VGroup(tb, tracked)), at=t_pr + 0.5, dur=0.5)

    # 'half turn': 1 → −1
    def half(t):
        a = math.pi * ss((t - t_ht + 0.2) / 1.6)
        f = 1 - ss((t - t_eu - 1.3) / 0.6)
        if t < t_ht - 0.4 or f <= 0:
            return VGroup()
        p = UC + R2 * P3(math.cos(a), math.sin(a))
        g = VGroup()
        if a > 0.01:
            g.add(Arc(radius=R2, start_angle=0, angle=a, arc_center=UC, stroke_color=St, stroke_width=7,
                      stroke_opacity=f))
        g.add(Line(UC, p, stroke_color=C.text, stroke_width=3, stroke_opacity=f),
              Dot(p, radius=0.1, color=C.text).set_opacity(f))
        return g

    top.redraw(window(half, t_ht - 0.4, t_eu + 2.0), during=(t_ht - 0.4, t_eu + 2.05))
    pl = tex(r"\pi", 52, Q).move_to(UC + P3(0, R2 + 0.45))
    mo = tex("-1", 40, C.text).move_to(UC + P3(-R2 - 0.5, -0.35))
    m.play(FadeIn(pl, shift=0.06 * DOWN), at=t_ht + 0.8, dur=0.5)
    m.play(FadeIn(mo), at=t_minus, dur=0.4)
    e1 = MathTex(r"e^{i\pi}", "=", "-1", font_size=64, color=C.text)
    for k_, c_ in ((0, Ch), (1, St), (2, Q)):
        e1[0][k_].set_color(c_)
    e1.move_to(P3(4.4, 0.9))
    top.play(Transform(fly, e1[0]), FadeIn(e1[1:]), at=t_minus + 0.2, dur=0.9)

    # 'Euler's identity'
    e2 = MathTex(r"e^{i\pi}", "+", "1", "=", "0", font_size=72, color=C.text)
    for k_, c_ in ((0, Ch), (1, St), (2, Q)):
        e2[0][k_].set_color(c_)
    e2[2].set_color(F)
    e2[4].set_color(F)
    e2.move_to(P3(4.4, 0.9))
    top.remove(fly, *e1[1:], at=t_eu - 0.3)
    top.add(e1, at=t_eu - 0.3)
    top.play(TransformMatchingTex(e1, e2), at=t_eu - 0.3, dur=1.0)
    m.play(FadeOut(VGroup(axes, one, pl, mo)), at=t_eu + 1.3, dur=0.5)

    # the circle back to the hub; the map returns; the identity settles in the hub
    t_ret = t_eu + 1.5
    small = the_circle(fill_color=C.bg, fill_opacity=1.0)
    m.play(Transform(hub, small), at=t_ret, dur=1.0, ease="easy_ease")
    links2, nodes2 = map_state(0, lit=ALL, edges=EDGES)
    lnk.play(FadeIn(links2), at=t_ret + 0.5, dur=0.7)
    nd.play(FadeIn(nodes2), at=t_ret + 0.5, dur=0.7)
    top.play(e2.animate.scale(0.52).move_to(ORIGIN), at=t_ret, dur=1.0, ease="easy_ease")

    # each symbol to its branch (copies taken from the identity as it sits in the hub)
    e2s = e2.copy().scale(0.52).move_to(ORIGIN)
    def send(parts, k, at):
        cp = VGroup(*(p_.copy() for p_ in parts))
        top.add(cp, at=at - 0.15)
        target = node_xy(k)
        top.play(cp.animate.scale(1.5).move_to(target).set_opacity(0), at=at - 0.15, dur=0.9, ease="easy_ease")
        top.remove(cp, at=at + 0.8)
        ping = Circle(radius=0.4, stroke_color=nodes2[k][0].get_stroke_color(), stroke_width=3).move_to(target)
        top.play(ping.animate.scale(1.9).set_stroke(opacity=0), at=at + 0.6, dur=0.7)
        top.remove(ping, at=at + 1.35)

    send([e2s[0][0]], PILLARS.index("change"), t_ch - 0.2)
    send([e2s[0][1]], PILLARS.index("structure"), t_tu - 0.2)
    send([e2s[0][2]], PILLARS.index("quantity"), t_pi)
    send([e2s[2], e2s[4]], PILLARS.index("foundations"), t_one)

    # 'every part': Structure–Change; the identity glows once
    new_edges = map_state(0, edges=NEW)[0][1]
    lnk.play(Create(new_edges[0]), at=t_ep - 0.3, dur=0.8)
    top.play(Indicate(e2, color=None, scale_factor=1.12), at=t_ep + 0.2, dur=0.8)
    top.play(FadeOut(e2), at=t1 - 0.55, dur=0.45)
