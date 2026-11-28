"""out_s01 · So, what is a circle? (recap)

The full map from ch7_s04 starts one slow last turn on 'what is a circle'. On each line a small sign of that chapter
shows inside the hub and the hub's rim gains a 60° arc in that branch's color, at its node: x² + y² = r² (Foundations),
π ≠ p/q (Quantity), a point sweeping round (Structure), a square relaxing into a circle (Space), d/dr πr² = 2πr
(Change), needles meeting at the centre (Uncertainty). The six arcs close into one whole circle. On 'landscape' the
arcs cross-fade to the plain circle and the whole map draws back into a small emblem at the centre.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import glow_layer, HUB_R, P3, PILLARS, finale_view, hub_at, hue, map_state, tex, the_circle, window

EDGES = tuple((PILLARS[i], PILLARS[j]) for i in range(6) for j in range(i + 1, 6))
EMBLEM = 0.5
T_EV = float(T.ch7_s04_every_lens)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.out_s01, T.out_s02)
def out_s01(s):
    s.solid(C.bg, z=-200)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), glow_layer(s, z=0, k=0.6), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_wh, t_la = float(T.out_s01_what_is_a_circle), float(T.out_s01_landscape)
    beats_ = [float(T.out_s01_rule), float(T.out_s01_no_fraction), float(T.out_s01_every_turn),
              float(T.out_s01_survives), float(T.out_s01_grows), float(T.out_s01_random_sticks)]
    t_ta, t_tb = t_wh - 0.3, beats_[-1] + 1.4                              # the last turn

    def deg(t):
        return 360 * ss((t - t_ta) / (t_tb - t_ta))

    def k_at(t):
        return 1 - (1 - EMBLEM) * ss((t - t_la + 0.2) / 2.4)

    def ring(t, part):
        k = k_at(t)
        g = map_state(deg(t), lit=PILLARS, edges=EDGES, view=finale_view(t, T_EV, t_wh))[part]
        return g.scale(k, about_point=ORIGIN)

    lnk.redraw(window(lambda t: ring(t, 0), t0, t1 + 1.0), during=(t0, t1))      # chords glow
    nd.redraw(window(lambda t: ring(t, 1), t0, t1 + 1.0), during=(t0, t1))       # nodes and labels stay crisp

    # the hub, and the six arcs on its rim
    def hub(t):
        k = k_at(t)
        g = VGroup(hub_at(deg(t), finale_view(t, T_EV, t_wh), k))
        f = 1 - ss((t - t_la + 0.3) / 0.9)
        for j, b in enumerate(beats_):
            u = ss((t - b + 0.1) / 0.7)
            if u <= 0 or f <= 0:
                continue
            mid = math.radians(-90 - 60 * j + deg(t))
            g.add(Arc(radius=HUB_R * k, start_angle=mid - math.radians(30) * u, angle=math.radians(60) * u,
                      stroke_color=hue(PILLARS[j]), stroke_width=9, stroke_opacity=f))
        return g

    m.redraw(window(hub, t0, t1 + 1.0), during=(t0, t1))

    # one sign per line, inside the hub
    ends = beats_[1:] + [t_la - 1.0]
    signs = [tex(r"x^2 + y^2 = r^2", 30, C.foundations),
             tex(r"\pi \ne \tfrac{p}{q}", 52, C.quantity),
             None,
             None,
             tex(r"\tfrac{d}{dr}\,\pi r^2 = 2\pi r", 28, C.change),
             None]
    for j, (b, e) in enumerate(zip(beats_, ends)):
        if signs[j] is not None:
            top.play(FadeIn(signs[j], scale=0.9), at=b - 0.15, dur=0.4)
            top.play(FadeOut(signs[j]), at=e - 0.35, dur=0.3)

    # Structure: a point sweeping round
    b2, e2 = beats_[2], ends[2]

    def sweep(t):
        f = ss((t - b2 + 0.15) / 0.3) * (1 - ss((t - e2 + 0.35) / 0.3))
        if f <= 0:
            return VGroup()
        a = 2 * math.pi * ss((t - b2) / 2.2)
        r = 0.7
        p = r * P3(math.cos(a), math.sin(a))
        g = VGroup(Circle(radius=r, stroke_color=C.structure, stroke_width=2, stroke_opacity=0.5 * f),
                   Line(ORIGIN, p, stroke_color=C.structure, stroke_width=3, stroke_opacity=f),
                   Dot(p, radius=0.08, color=C.structure).set_opacity(f))
        return g

    top.redraw(window(sweep, b2 - 0.2, e2), during=(b2 - 0.2, e2 + 0.05))

    # Space: a square relaxes into a circle
    b3, e3 = beats_[3], ends[3]
    sq = Square(side_length=1.15, stroke_color=C.space, stroke_width=4)
    top.play(FadeIn(sq), at=b3 - 0.15, dur=0.3)
    top.play(Transform(sq, Circle(radius=0.62, stroke_color=C.space, stroke_width=4)), at=b3 + 0.3, dur=1.2,
             ease="easy_ease")
    top.play(FadeOut(sq), at=e3 - 0.35, dur=0.3)

    # Uncertainty: needles meeting at the centre
    b5, e5 = beats_[5], ends[5]
    rg = np.random.default_rng(1777)
    th = rg.uniform(0, math.pi, 14)
    c0 = rg.uniform(-0.6, 0.6, (14, 2))

    def needles(t):
        f = ss((t - b5 + 0.15) / 0.3) * (1 - ss((t - e5 + 0.35) / 0.3))
        if f <= 0:
            return VGroup()
        u = ss((t - b5 - 0.2) / 1.4)
        g = VGroup()
        for a, c in zip(th, c0):
            cc = (1 - u) * P3(*c)
            h = 0.18 + u * (0.75 - 0.18)
            d = h * P3(math.cos(a), math.sin(a))
            g.add(Line(cc - d, cc + d, stroke_color=C.uncertainty, stroke_width=3, stroke_opacity=f))
        return g

    top.redraw(window(needles, b5 - 0.2, e5), during=(b5 - 0.2, e5 + 0.05))
