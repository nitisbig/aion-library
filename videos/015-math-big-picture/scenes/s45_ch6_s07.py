"""ch6_s07 · Numbers you can trust (takeaway, map turn).

Hero callback: on 'random' the rectangle and its arch come back at the centre and fill with dots at full rate; on
'pi' 2N/H ≈ π (π gold) writes under it. On 'And to get there' the map returns as Chapter 5 left it and the rectangle
shrinks into Uncertainty at the bottom, which lights on 'every branch'; the chords Change–, Space– and
Quantity–Uncertainty draw, and in the closing words the ring makes its sixth turn (300° → 360°): Foundations is back at
the bottom with all six lit.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, P3, Canvas, draw_dots, map_state, node, node_xy, the_circle, window, hub_at, turn_view

LIT = ("foundations", "quantity", "structure", "space", "change")
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"))
NEW = (("change", "uncertainty"), ("space", "uncertainty"), ("quantity", "uncertainty"))
O0, SX0, SY0 = P3(-2.2, -0.4), 1.4, 2.0          # the rectangle at the centre: θ 0..π across, x 0..1 up
RC = O0 + P3(SX0 * math.pi / 2, SY0 / 2)         # its centre
FULL = (-64 / 9, -4.0, 64 / 9, 4.0)
N_FILL = 4000


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch6_s07, T.ch7_s01)
def ch6_s07(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_ra, t_eb = float(T.ch6_s07_random), float(T.ch6_s07_every_branch)
    t_pi, t_get, t_so = t_ra + 5.79, t_eb - 2.06, t_eb + 2.47                # 'pi' 'And to get there' 'So let's'
    U, Q = C.uncertainty, C.quantity
    tgt = node_xy(5, turn=300)
    t_s0, t_s1 = t_get + 0.5, t_get + 1.7                                   # the shrink

    # the rectangle, its arch and the dots, drawn together so they shrink as one
    cv = Canvas(FULL)
    sk = cv.skia

    def k_at(t):
        return ss((t - t_s0) / (t_s1 - t_s0))

    def geom(t):
        w = k_at(t)
        k = 1 - 0.93 * w
        c = (1 - w) * RC + w * tgt
        return c + (O0 - RC) * k, SX0 * k, SY0 * k

    def n_at(t):
        u = min(max((t - t_ra + 0.6) / 5.0, 0.0), 1.0)
        return int(round(N_FILL * u ** 2.2))

    def draw(t):
        c = cv.begin()
        f = ss((t - t0 - 0.2) / 0.6) * (1 - ss((t - t_s1 + 0.3) / 0.4))
        if f <= 0:
            return cv.array()
        o, sx, sy = geom(t)
        draw_dots(c, cv, n_at(t), 1.0, o=o, sx=sx, sy=sy, alpha=f)
        pr = sk.Path()
        pr.addRect(sk.Rect(*cv.T(o[0], o[1] + sy), *cv.T(o[0] + sx * math.pi, o[1])))
        c.drawPath(pr, cv.paint(C.space, f, 3.0))
        th = np.linspace(0, math.pi, 120)
        pa = sk.Path()
        pa.moveTo(*cv.T(o[0], o[1]))
        for a in th[1:]:
            pa.lineTo(*cv.T(o[0] + sx * a, o[1] + sy * math.sin(a)))
        c.drawPath(pa, cv.paint(C.change, f, 4.5))
        return cv.array()

    s.add(FramesLayer(draw, z=1, during=[(t0, t_s1 + 0.2)], **cv.layer_kw()))

    # 'pi': the old friend
    eq = MathTex(r"\frac{2N}{H}", r"\approx", r"\pi", font_size=56, color=C.text)
    eq[0].set_color(U)
    eq[2].set_color(Q)
    eq.move_to(P3(0, -1.45))
    top.play(Write(eq), at=t_pi - 0.4, dur=0.8)
    top.play(FadeOut(eq), at=t_get - 0.1, dur=0.5)

    # the map returns; Uncertainty lights; three chords
    links, nodes = map_state(300, lit=LIT, edges=EDGES)
    hub = hub_at(300)
    t_map = t_get + 0.4
    lnk.play(FadeIn(links), at=t_map, dur=0.8)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.06), at=t_map, dur=0.9)
    m.play(Create(hub), at=t_map, dur=0.9)
    nd.play(Transform(nodes[5], node(5, lit=True, turn=300)), at=t_eb, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=U, stroke_width=3).move_to(tgt)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_eb + 0.05, dur=0.8)
    top.remove(ping, at=t_eb + 0.9)
    new_edges = map_state(300, edges=NEW)[0][1]
    lnk.play(LaggedStart(*(Create(e_) for e_ in new_edges), lag_ratio=0.35), at=t_eb + 0.4, dur=1.2)

    # the sixth turn, 300° → 360°
    t_turn = t_so - 0.1
    turn_d = t1 - 0.05 - t_turn
    lit = LIT + ("uncertainty",)

    def deg(t):
        return 300 + 60 * ss((t - t_turn + 0.15) / turn_d)

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 55, 14)

    def ring_at(t):
        return map_state(deg(t), lit=lit, view=TV(t))[1]

    def links_at(t):
        return map_state(deg(t), edges=EDGES + NEW, view=TV(t))[0]

    lnk.remove(links, *new_edges, at=t_turn - 0.15)               # Create added each chord on its own
    nd.remove(*nodes, at=t_turn - 0.15)
    nd.redraw(window(ring_at, t_turn - 0.15, t1 + 1.0), during=(t_turn - 0.15, t1))
    m.remove(hub, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, t1 + 1.0), during=(t_turn - 0.15, t1))
    lnk.redraw(window(links_at, t_turn - 0.15, t1 + 1.0), during=(t_turn - 0.15, t1))
