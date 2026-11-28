"""ch6_s01 · Back to the floor (Chapter 6 hook).

The map as Chapter 5 left it gives way to Uncertainty's card, which shrinks into the floor: the intro's boards return,
filling the frame. On 'One throw' a single stick tumbles in slow motion (seen from above, so it shrinks as it falls)
and on 'cross' it hangs over a crack with a '?' tag. On 'coin' a coin flips and freezes edge-on. On 'many throws' the
stick lands (it crosses, so it turns pink) and sticks rain at full rate. On 'probability' the key word comes up.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import (glow_layer, FL_BOX, P3, Canvas, backed, caps, chapter_card, coin, full_floor, map_state, node_xy, tex, the_circle,
                 window)
from kit import StickPainter, hub_at, wood_floor

LIT = ("foundations", "quantity", "structure", "space", "change")
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"))
HC, HTH = P3(-2.8, 0.75), 0.9              # where the stick hangs (crack at y = 0.9), and its angle: it crosses
CC = P3(2.8, 0.75)                         # the coin
N_RAIN = 1000


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch6_s01, T.ch6_s02)
def ch6_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=1), s.manim(z=2)
    card_l = s.manim(z=3, parallax=0)
    t0, t1 = float(s.start), float(s.end)
    t_fl, t_one, t_cr = float(T.ch6_s01_floor), float(T.ch6_s01_one_throw), float(T.ch6_s01_cross)
    t_coin, t_many, t_pr = float(T.ch6_s01_coin), float(T.ch6_s01_many_throws), float(T.ch6_s01_probability)
    U = C.uncertainty
    out_t = t1 - 0.5

    # the map as Chapter 5 left it; Uncertainty's card; it shrinks into the floor
    links, nodes = map_state(300, lit=LIT, edges=EDGES)
    hub = hub_at(300)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)
    lnk.play(FadeOut(links), at=t0 + 0.1, dur=0.45)
    nd.play(FadeOut(VGroup(*(nodes[k] for k in range(5)))), at=t0 + 0.1, dur=0.45)
    nd.play(FadeOut(nodes[5], scale=1.6), at=t0 + 0.15, dur=0.45)
    m.play(FadeOut(hub), at=t0 + 0.1, dur=0.45)
    card = chapter_card("uncertainty", "probability")
    card_l.play(GrowFromPoint(card, node_xy(5, turn=300)), at=t0 + 0.2, dur=0.7, ease="easy_ease")
    card_l.play(card.animate.scale(0.03).set_opacity(0), at=t_fl - 0.75, dur=0.55, ease="easy_ease")
    card_l.remove(card, at=t_fl - 0.15)

    # the floor; later the rain
    cx, cy, th, hit, lines_y, half = full_floor(N_RAIN)
    cv = Canvas(FL_BOX)
    sk = cv.skia

    def n_rain(t):
        u = min(max((t - t_many + 0.1) / (t_pr - t_many), 0.0), 1.0)
        return int(round(N_RAIN * u ** 2))

    def seg_pts(idx):
        pts = []
        for n_ in idx:
            dx, dy = half * math.cos(th[n_]), half * math.sin(th[n_])
            pts += [sk.Point(*cv.T(cx[n_] - dx, cy[n_] - dy)), sk.Point(*cv.T(cx[n_] + dx, cy[n_] + dy))]
        return pts

    start = P3(-4.9, 3.3)                                    # 'One throw': where the hero stick falls from
    painter = StickPainter(cv)
    order = np.arange(N_RAIN)

    def draw(t):
        c = cv.begin()
        L = n_rain(t)
        if L:
            for i in order[:L]:
                fresh = i >= L - 30
                painter.stick(c, cx[i], cy[i], th[i], 2 * half, 1.0 if hit[i] else 0.0, 1.0 if fresh else 0.8)
        # the hero stick, tumbling down and hanging over a crack
        f = ss((t - t_one + 0.3) / 0.4) * (1 - ss((t - out_t) / 0.45))
        if f > 0:
            u = ss((t - t_one + 0.2) / (t_cr - t_one + 0.2))
            land = ss((t - t_many) / 0.35)
            pos = (1 - u) * start + u * HC
            k = 2.5 - 1.2 * u - 0.3 * land
            ang = HTH - 3.2 * (1 - u) ** 1.5
            painter.stick(c, pos[0], pos[1], ang, 0.9 * k, land, f, lift=max(0.0, (k - 1) / 1.5), w=7.0 * k)
        return cv.array()

    on = fade(t_fl - 0.35, dur=0.6, out=out_t, out_dur=0.45)
    s.add(FramesLayer(draw, z=0, opacity=on, during=[(t_fl - 0.4, t1)], **cv.layer_kw()))  # the hero stays at f
    wood, wkw = wood_floor(lines_y)
    s.add(ArrayLayer(wood, z=-0.5, opacity=on, **wkw))



    crack = Line(HC + P3(-1.0, 0.15), HC + P3(1.0, 0.15), stroke_color=C.text, stroke_width=2.6)
    q = backed(tex("?", 56, C.text)).move_to(HC + P3(0.95, 0.75))
    m.play(Create(crack), at=t_cr - 0.1, dur=0.5)
    m.play(FadeIn(q, scale=1.3), at=t_cr + 0.1, dur=0.4)
    m.play(FadeOut(VGroup(q, crack)), at=t_many - 0.2, dur=0.4)

    # 'coin': a coin flips and freezes edge-on (it stays for ch6_s02)
    def phi(t):
        u = min(max((t - t_coin + 0.5) / 1.6, 0.0), 1.0)
        return 6.5 * math.pi * (1 - (1 - u) ** 2.2)

    def coin_at(t):
        f = ss((t - t_coin + 0.75) / 0.3)
        return coin(CC, phi(t)).set_opacity(f) if f > 0 else VGroup()

    top.redraw(window(coin_at, t_coin - 0.75, t1 + 1.0), during=(t_coin - 0.75, t1))

    # 'probability'
    word = backed(caps("probability", 46, U), pad=0.1).move_to(P3(0, 3.2))
    top.play(FadeIn(word, shift=0.08 * DOWN), at=t_pr - 0.55, dur=0.5)
    top.play(FadeOut(word), at=out_t, dur=0.45)
