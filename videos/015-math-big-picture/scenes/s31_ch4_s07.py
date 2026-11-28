"""ch4_s07 · What survives a stretch (takeaway, map turn).

The rubber band comes back as a circle; on 'square' it squashes into the square, on 'agree' it springs back, and
'survives a stretch' comes up. On 'Even' the map returns as Chapter 3 left it and the band shrinks onto Space at the
bottom; on 'counting' Space lights and the chords Structure–Space and Quantity–Space draw. On 'lengths come back' the
ring turns its sixth (180° → 240°), carrying Change to the bottom, and Change swells on 'grow'.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, NODE_R, P3, band, band_theta, caps, map_state, node, node_xy, r_poly, the_circle, window, hub_at, turn_view

EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"))
NEW = (("structure", "space"), ("quantity", "space"))
LIT = ("foundations", "quantity", "structure")
BC, BR = P3(0, -0.1), 1.8


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch4_s07, T.ch5_s01)
def ch4_s07(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_ci, t_cnt, t_gr = float(T.ch4_s07_circle), float(T.ch4_s07_counting), float(T.ch4_s07_grow)
    t_sq, t_ag, t_sv = t_ci + 0.52, t_ci + 3.24, t_ci + 4.68                # 'square' 'agree' 'survives'
    t_even, t_next = t_ci + 6.94, t_ci + 11.59                             # 'Even' 'Next,'
    t_back = t_next + 1.37                                                 # 'come back'
    S = C.space
    th = band_theta()
    r_c, r_s = np.full_like(th, BR), r_poly(4, BR)
    sp = node_xy(3, turn=180)

    # the band: circle, square, circle; then onto the Space node
    t_m0, t_m1 = t_even + 0.6, t_even + 2.0

    def rubber(t):
        a = ss((t - t_ci + 0.6) / 0.6)                                       # draws in
        u = ss((t - t_sq - 0.1) / 0.8) * (1 - ss((t - t_ag - 0.1) / 0.8))
        r = (1 - u) * r_c + u * r_s
        if t > t_ag + 0.9:                                                   # an elastic settle
            r = r * (1 + 0.04 * math.exp(-3 * (t - t_ag - 0.9)) * np.sin(3 * th + 0.7)
                     * math.sin(10 * (t - t_ag - 0.9)))
        v = ss((t - t_m0) / (t_m1 - t_m0))                                   # shrink onto the node
        c = (1 - v) * BC + v * sp
        r = r * ((1 - v) + v * (NODE_R / BR))
        b = band(r, c, width=12 - 8 * v)
        if a < 1:
            for sub in b:
                sub.pointwise_become_partial(sub.copy(), 0, max(a, 0.001))
        return b

    glow_layer(s, z=1.2, color=C.space, k=0.7).redraw(window(rubber, t_ci - 0.6, t_cnt + 0.25), during=(t_ci - 0.6, t_cnt + 0.3))
    word = caps("survives a stretch", 52, S).move_to(P3(0, 3.05))
    m.play(FadeIn(word, shift=0.1 * DOWN), at=t_sv, dur=0.6)
    m.play(FadeOut(word), at=t_even - 0.3, dur=0.5)

    # 'Even': the map as Chapter 3 left it
    links, nodes = map_state(180, lit=LIT, edges=EDGES)
    hub = hub_at(180)
    lnk.play(FadeIn(links), at=t_even + 0.2, dur=0.8)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.06), at=t_even + 0.2, dur=0.9)
    m.play(FadeIn(hub), at=t_even + 0.4, dur=0.7)

    # 'counting': Space lights; two chords draw
    nd.play(Transform(nodes[3], node(3, lit=True, turn=180)), at=t_cnt, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=S, stroke_width=3).move_to(sp)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_cnt + 0.05, dur=0.8)
    top.remove(ping, at=t_cnt + 0.9)
    new_edges = map_state(180, edges=NEW)[0][1]
    lnk.play(LaggedStart(*(Create(e_) for e_ in new_edges), lag_ratio=0.4), at=t_cnt + 0.3, dur=0.9)

    # the signature turn, 180° → 240°; Change swells on 'grow'
    t_turn = t_back
    turn_d = t1 - 0.05 - t_turn
    lit = LIT + ("space",)

    def deg(t):
        return 180 + 60 * ss((t - t_turn + 0.15) / turn_d)

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 45, 0)

    def ring_at(t):
        g = map_state(deg(t), lit=lit, view=TV(t))[1]
        sw = ss((t - t_gr + 0.2) / 0.5) * (1 - ss((t - t_gr - 0.6) / 0.9))
        if sw > 0:
            g[4].scale(1 + 0.35 * sw)
        return g

    def links_at(t):
        return map_state(deg(t), edges=EDGES + NEW, view=TV(t))[0]

    lnk.remove(links, *new_edges, at=t_turn - 0.15)               # Create added each chord on its own
    nd.remove(*nodes, at=t_turn - 0.15)
    nd.redraw(window(ring_at, t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
    m.remove(hub, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
    lnk.redraw(window(links_at, t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
