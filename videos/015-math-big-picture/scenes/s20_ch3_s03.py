"""ch3_s03 · Why the map turns (C6).

The map comes back as it was left: turned twice, Foundations and Quantity lit. On 'Remember' a ghost ring replays the
two turns made so far, and each leaves a 60° violet arc outside the ring. On 'sixth' the first arc is tagged 60°; on
'six of those' four dim arcs complete the circle and 6 × 60° = 360° writes. On 'cyclic group' the word C6 lands and
all six arcs light once. On 'snowflake' a six-armed snowflake turns 60° onto its dashed ghost. On 'all six' the four
turns still to come pulse: two done, four to go.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, MAP_R, NODE_R, P3, PILLARS, map_state, node, sans, tex, the_circle, window, hub_at

FQ = (("foundations", "quantity"),)
RA = MAP_R + NODE_R + 0.35
SNOW_C, SNOW_R = P3(4.75, -1.35), 0.85
MC = P3(-1.75, 0.0)                    # the map sits left of centre; the right column carries the words


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def seg(j, col, w=5, opacity=1.0):
    """The j-th sixth of the turn track, counter-clockwise from the top."""
    a0 = math.radians(90 + 60 * j + 4)
    return Arc(radius=RA, arc_center=MC, start_angle=a0, angle=math.radians(52), stroke_color=col, stroke_width=w,
               stroke_opacity=opacity).add_tip(tip_length=0.2, tip_width=0.18)


def snowflake(c, r, turn_deg, col, w=3):
    g = VGroup()
    for k in range(6):
        a = math.radians(90 + 60 * k + turn_deg)
        u = P3(math.cos(a), math.sin(a))
        g.add(Line(c, c + r * u, stroke_color=col, stroke_width=w))
        for f, L in ((0.45, 0.32), (0.75, 0.24)):
            p = c + f * r * u
            for side in (1, -1):
                b = a + side * math.radians(55)
                g.add(Line(p, p + L * P3(math.cos(b), math.sin(b)), stroke_color=col, stroke_width=w))
        g.add(Line(c + 0.18 * r * u, c + 0.18 * r * P3(math.cos(a + math.pi / 3), math.sin(a + math.pi / 3)),
                   stroke_color=col, stroke_width=w))
    return g


@scene(T.ch3_s03, T.ch3_s04)
def ch3_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, gh, m, nd, top = glow_layer(s, z=-3, k=0.55), s.manim(z=-2), s.manim(z=0), s.manim(z=1), s.manim(z=2)
    t0 = float(s.start)
    t_rem, t_6th, t_6 = float(T.ch3_s03_remember), float(T.ch3_s03_sixth), float(T.ch3_s03_six_of_those)
    t_cg, t_sf, t_all = float(T.ch3_s03_cyclic_group), float(T.ch3_s03_snowflake), float(T.ch3_s03_all_six)
    V = C.structure

    # the map as Chapter 2 left it
    links = map_state(120, lit=("foundations", "quantity"), edges=FQ)[0]
    nodes = VGroup(*(node(k, lit=PILLARS[k] in ("foundations", "quantity"), turn=120, label=False) for k in range(6)))
    links.shift(MC)
    nodes.shift(MC)
    hub = hub_at(120).shift(MC)
    lnk.play(FadeIn(links), at=t0 + 0.1, dur=0.6)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.05), at=t0 + 0.1, dur=0.7)
    m.play(GrowFromCenter(hub), at=t0 + 0.1, dur=0.6, ease="out_back")

    # 'Remember': a ghost of the ring replays the two turns, each leaving an arc
    t_g0 = t_rem + 0.5
    t_g1, t_g2 = t_g0 + 1.3, t_g0 + 2.6

    def ghost(t):
        u1 = ss((t - t_g0) / 1.0)
        u2 = ss((t - t_g1) / 1.0)
        deg = 60 * (u1 + u2)
        g = VGroup()
        for k in range(6):
            a = math.radians(-90 - 60 * k + deg)
            g.add(DashedVMobject(Circle(radius=NODE_R, stroke_color=V, stroke_width=2).move_to(
                MC + MAP_R * P3(math.cos(a), math.sin(a))), num_dashes=14))
        f = 1 - ss((t - t_g2) / 0.5)
        g.set_stroke(opacity=f)
        return g

    gh.redraw(window(ghost, t_g0 - 0.2, t_g2 + 0.55), during=(t_g0 - 0.2, t_g2 + 0.55))
    arcs = [seg(j, V) for j in range(6)]
    m.play(Create(arcs[0]), at=t_g0, dur=1.0)
    m.play(Create(arcs[1]), at=t_g1, dur=1.0)
    tag = tex(r"60^\circ", 36, V).move_to(MC + (RA + 0.5) * P3(math.cos(math.radians(120)), math.sin(math.radians(120))))
    m.play(FadeIn(tag, scale=0.8), at=t_6th, dur=0.5)

    # 'six of those': four more complete the circle
    dim = [seg(j, C.map_off, 4) for j in range(2, 6)]
    m.play(LaggedStart(*(Create(a_) for a_ in dim), lag_ratio=0.25), at=t_6, dur=1.4)
    eq = tex(r"6 \times 60^\circ = 360^\circ", 44, C.text).move_to(P3(4.75, 3.0))
    m.play(Write(eq), at=t_6 + 0.4, dur=1.0)

    # 'cyclic group': C6
    c6 = tex(r"C_6", 88, V).move_to(P3(4.75, 1.55))
    m.play(FadeIn(c6, scale=0.8), at=t_cg, dur=0.6, ease="out_back")
    lab = sans("cyclic group", 30, C.muted).next_to(c6, DOWN, buff=0.25)
    m.play(FadeIn(lab), at=t_cg + 0.5, dur=0.5)
    lit_all = VGroup(*(seg(j, V, 5) for j in range(2, 6)))
    top.play(FadeIn(lit_all), at=t_cg + 0.4, dur=0.4)
    top.play(FadeOut(lit_all), at=t_cg + 1.5, dur=0.6)

    # 'snowflake': six arms, turned 60° onto its ghost
    g_sf = VGroup(*(DashedVMobject(l_, num_dashes=4) for l_ in snowflake(SNOW_C, SNOW_R, 0, C.map_off, 2)))
    m.play(FadeIn(g_sf), at=t_sf - 0.4, dur=0.4)

    def flake(t):
        u = ss((t - t_sf - 0.5) / 1.4)
        g = snowflake(SNOW_C, SNOW_R, 60 * u, C.circle)
        g.set_stroke(opacity=1 - ss((t - float(s.end) + 0.65) / 0.55))
        return g

    f0 = flake(t_sf - 0.4)
    m.play(FadeIn(f0, scale=0.85), at=t_sf - 0.4, dur=0.5)
    m.remove(f0, at=t_sf + 0.3)
    top.redraw(window(flake, t_sf + 0.3, float(s.end)), during=(t_sf + 0.3, float(s.end)))

    # 'all six': two done, four to go
    m.play(LaggedStart(*(Indicate(a_, color=V, scale_factor=1.04) for a_ in dim), lag_ratio=0.2), at=t_all - 0.2,
           dur=1.0)
    cnt = tex(r"2\,/\,6", 44, V).move_to(P3(4.75, -2.95))
    m.play(FadeIn(cnt, shift=0.06 * UP), at=t_all - 0.2, dur=0.5)

    out_t = float(s.end) - 0.65
    gone = VGroup(hub, tag, eq, c6, lab, g_sf, cnt, *arcs[:2], *dim)
    m.play(FadeOut(gone), at=out_t, dur=0.55)
    lnk.play(FadeOut(links), at=out_t, dur=0.55)
    nd.play(FadeOut(nodes), at=out_t, dur=0.55)
