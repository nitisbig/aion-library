"""ch4_s01 · Halfway, and a rubber band (Chapter 4 hook).

The map as Chapter 3 left it (turned three times; Foundations, Quantity and Structure lit). On 'halfway' a tag reads
3 / 6; on 'sticks' the Uncertainty node flickers with a tiny floor of needles, the debt still owed. On 'So, shape' Space,
now at the bottom, opens into Chapter 4's card. The circle comes back; on 'rubber band' it thickens into a teal band
with an elastic wobble; on 'square' it squashes into a square of the same area. On 'geometer' the measurements pop on
(a length, a right angle, four corners); on 'topologist' they fall away, leaving the word 'same'.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import (glow_layer, P3, band, band_theta, caps, chapter_card, map_state, node_xy, r_poly, sans, tex, the_circle, tint,
                 window)
from kit import hub_at

EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"))
LIT = ("foundations", "quantity", "structure")
BC, BR = P3(0, -0.1), 1.8


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch4_s01, T.ch4_s02)
def ch4_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    card_l = s.manim(z=3, parallax=0)
    t0 = float(s.start)
    t_hw, t_st, t_sh = float(T.ch4_s01_halfway), float(T.ch4_s01_sticks), float(T.ch4_s01_so_shape)
    t_rb, t_sq, t_ge, t_to = (float(T.ch4_s01_rubber_band), float(T.ch4_s01_square), float(T.ch4_s01_geometer),
                              float(T.ch4_s01_topologist))
    S = C.space

    # the map as Chapter 3 left it
    links, nodes = map_state(180, lit=LIT, edges=EDGES)
    hub = hub_at(180)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)
    tag = tex(r"3\,/\,6", 52, C.text).move_to(P3(5.2, 3.0))
    m.play(FadeIn(tag, shift=0.08 * DOWN), at=t_hw, dur=0.6)

    # 'sticks': the Uncertainty node flickers with a tiny floor of needles
    u_at = node_xy(5, turn=180)
    rg = np.random.default_rng(1777)

    def needles(t):
        g = VGroup()
        k = int((t - t_st) / 0.12)
        r_ = np.random.default_rng(1777 + k)
        for y in (-0.16, 0.0, 0.16):
            g.add(Line(u_at + P3(-0.3, y), u_at + P3(0.3, y), stroke_color=C.map_off, stroke_width=1.2))
        f = ss((t - t_st + 0.1) / 0.3) * (1 - ss((t - t_st - 2.6) / 0.4))
        for _ in range(9):
            p = r_.uniform(-0.22, 0.22, 2)
            a = r_.uniform(0, math.pi)
            d = 0.08 * P3(math.cos(a), math.sin(a))
            g.add(Line(u_at + P3(*p) - d, u_at + P3(*p) + d, stroke_color=C.uncertainty, stroke_width=2,
                       stroke_opacity=f))
        g[0:3].set_stroke(opacity=0.8 * f)
        return g

    top.redraw(window(needles, t_st - 0.1, t_st + 3.1), during=(t_st - 0.1, t_st + 3.1))

    # 'So, shape': the map gives way to the Space card
    lnk.play(FadeOut(links), at=t_sh - 0.2, dur=0.5)
    nd.play(FadeOut(VGroup(*(nodes[k] for k in (0, 1, 2, 4, 5)))), at=t_sh - 0.2, dur=0.5)
    nd.play(FadeOut(nodes[3], scale=1.6), at=t_sh - 0.15, dur=0.5)
    m.play(FadeOut(hub), FadeOut(tag), at=t_sh - 0.2, dur=0.5)
    card = chapter_card("space", "shape and topology")
    origin = node_xy(3, turn=180)
    card_l.play(GrowFromPoint(card, origin), at=t_sh - 0.1, dur=0.8, ease="easy_ease")
    card_l.play(card.animate.scale(0.05).move_to(origin).set_opacity(0), at=t_rb - 1.5, dur=0.6, ease="easy_ease")
    card_l.remove(card, at=t_rb - 0.85)

    # the circle becomes a rubber band, then a square
    circ = the_circle(BR).move_to(BC)
    m.play(Create(circ), at=t_rb - 0.85, dur=0.7, ease="easy_ease")
    m.remove(circ, at=t_rb - 0.1)
    th = band_theta()
    r_c, r_s = np.full_like(th, BR), r_poly(4, BR)
    t_m0, t_m1 = t_sq + 0.1, t_sq + 1.6

    def rubber(t):
        u = ss((t - t_m0) / (t_m1 - t_m0))
        k = ss((t - t_rb + 0.1) / 0.6)
        w = 0.05 * math.exp(-1.6 * max(t - t_rb - 0.3, 0)) * math.sin(9 * max(t - t_rb - 0.3, 0)) * k
        r = (1 - u) * r_c + u * r_s
        r = r * (1 + w * np.sin(3 * th + 0.7))
        col = interpolate_color(ManimColor(C.circle), ManimColor(S), k)
        return band(r, BC, color=col, width=5 + 7 * k)

    glow_layer(s, z=1.2, color=C.space, k=0.7).redraw(window(rubber, t_rb - 0.1, float(s.end)), during=(t_rb - 0.1, float(s.end)))

    # 'geometer': length, angle, corners
    a = BR * math.sqrt(math.pi) / 2                                   # half the side of the equal-area square
    yb = BC[1] - a - 0.4
    dim_ = VGroup(Line(P3(-a, yb), P3(a, yb), stroke_color=C.text, stroke_width=2),
                  Line(P3(-a, yb - 0.12), P3(-a, yb + 0.12), stroke_color=C.text, stroke_width=2),
                  Line(P3(a, yb - 0.12), P3(a, yb + 0.12), stroke_color=C.text, stroke_width=2))
    l_len = sans("length", 30, C.text).next_to(dim_, DOWN, buff=0.15)
    cx, cy = a, BC[1] + a
    ang = VGroup(Line(P3(cx - 0.35, cy), P3(cx - 0.35, cy - 0.35), stroke_color=C.text, stroke_width=2),
                 Line(P3(cx - 0.35, cy - 0.35), P3(cx, cy - 0.35), stroke_color=C.text, stroke_width=2))
    l_ang = sans("angle", 30, C.text).move_to(P3(cx + 1.0, cy - 0.15))
    dots = VGroup(*(Dot(P3(sx * a, BC[1] + sy * a), radius=0.09, color=C.text) for sx in (-1, 1) for sy in (-1, 1)))
    l_cor = sans("corners", 30, C.text).move_to(P3(-a - 1.15, BC[1] + a))
    m.play(Create(dim_), FadeIn(l_len), at=t_ge + 0.75, dur=0.5)
    m.play(Create(ang), FadeIn(l_ang), at=t_ge + 2.75, dur=0.5)
    top.play(LaggedStart(*(GrowFromCenter(d) for d in dots), lag_ratio=0.15), at=t_ge + 3.75, dur=0.6)
    m.play(FadeIn(l_cor), at=t_ge + 3.85, dur=0.5)

    # 'topologist': the measurements fall away; 'same'
    m.play(*(FadeOut(x_, shift=0.6 * DOWN) for x_ in (dim_, l_len, ang, l_ang, l_cor)), at=t_to + 0.2, dur=0.7,
           ease="in_cubic")
    top.play(FadeOut(dots, shift=0.6 * DOWN), at=t_to + 0.2, dur=0.7, ease="in_cubic")
    same = caps("same", 60, S).move_to(P3(0, 3.05))
    m.play(FadeIn(same, shift=0.1 * DOWN), at=t_to + 1.1, dur=0.6)
    m.play(FadeOut(same), at=float(s.end) - 0.6, dur=0.5)
