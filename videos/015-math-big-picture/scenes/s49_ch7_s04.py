"""ch7_s04 · Every lens (Wiles 1994, the chapter's takeaway).

The map steps back. On 'connections' Fermat's equation xⁿ + yⁿ = zⁿ (C.quantity) comes up; on 'question about whole
numbers' its claim, no whole-number solutions for n > 2; on 'three hundred and fifty years' 1637 → 1994. On 'Wiles' a
lower third (A. Wiles · 1994). On 'geometry' an elliptic curve y² = x³ − x (its real points computed, C.space) and on
'algebra' a symmetry glyph (C.structure) link to the equation with lit lines. On 'Every lens' the full map returns:
all six nodes, all fifteen chords lit, held for the outro.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import glow_layer, plate, P3, PILLARS, dim, face_of, finale_view, hub_at, lower_third, map_state, partial, sans, tex, the_circle, window

ALL = PILLARS
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"), ("change", "uncertainty"),
         ("space", "uncertainty"), ("quantity", "uncertainty"), ("foundations", "space"), ("foundations", "change"),
         ("foundations", "uncertainty"), ("structure", "change"), ("structure", "uncertainty"))
EC, ES = P3(-5.0, -1.6), 0.5                     # the elliptic curve: centre (x = 0, y = 0) and scale
HX = P3(4.9, -1.6)                               # the symmetry glyph


def curve_pts():
    u = np.linspace(0, math.pi, 90)
    xo = -0.5 - 0.5 * np.cos(u)                                   # the oval, x ∈ [−1, 0]
    yo = np.sqrt(np.maximum(xo ** 3 - xo, 0))
    oval = np.concatenate([np.stack([xo, yo], 1), np.stack([xo[::-1], -yo[::-1]], 1)])
    v = np.linspace(-0.95, 0.95, 120)
    xb = 1 + v * v                                                # the branch, x ≥ 1
    yb = np.sign(v) * np.sqrt(np.maximum(xb ** 3 - xb, 0))
    return oval, np.stack([xb, yb], 1)


@scene(T.ch7_s04, T.out_s01)
def ch7_s04(s):
    s.solid(C.bg, z=-200)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_co, t_wi, t_ge, t_ev = float(T.ch7_s04_connections), float(T.ch7_s04_wiles), float(T.ch7_s04_geometry), float(
        T.ch7_s04_every_lens)
    t_q, t_350, t_alg = t_wi + 1.07, t_wi + 4.0, t_ge + 0.96                 # 'question' 'three hundred' 'algebra'
    Q, Sp, St = C.quantity, C.space, C.structure

    links, nodes = map_state(0, lit=ALL, edges=EDGES)
    hub = the_circle(fill_color=C.bg, fill_opacity=1.0)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)
    lnk.play(FadeOut(links), at=t0 + 0.15, dur=0.6)
    nd.play(FadeOut(nodes), at=t0 + 0.15, dur=0.6)
    m.play(FadeOut(hub), at=t0 + 0.15, dur=0.6)

    # Fermat
    fe = MathTex(r"x^n + y^n = z^n", font_size=76, color=Q).move_to(P3(0, 1.55))
    top.play(Write(fe), at=t_co - 0.3, dur=1.0)
    claim = sans(r"no whole-number solutions for $n > 2$", 32, C.muted).move_to(P3(0, 0.55))
    top.play(FadeIn(claim, shift=0.06 * UP), at=t_q, dur=0.5)
    yrs = tex(r"1637 \;\longrightarrow\; 1994", 36, C.text).move_to(P3(0, -0.25))
    top.play(FadeIn(yrs, shift=0.06 * UP), at=t_350, dur=0.5)
    lt = lower_third(r"A.\ Wiles\ \textperiodcentered\ 1994", P3(-6.3, 3.3), width=3.2)
    top.play(FadeIn(lt, shift=0.08 * LEFT), at=t_wi - 0.2, dur=0.6)
    plate(s, top, "fermat", (-4.9, 0.75), 2.6, t_co + 0.3, t_ge - 0.5, C.quantity)
    plate(s, top, "fermat_diophantus", (4.9, 0.75), 2.6, t_q + 0.3, t_ge - 0.5, C.quantity, caption="Arithmetica \\textperiodcentered\\ 1670")

    # 'geometry': an elliptic curve; 'algebra': symmetry
    oval, branch = curve_pts()
    ec = VGroup(*(VMobject(stroke_color=Sp, stroke_width=4).set_points_smoothly([EC + ES * P3(a, b) for a, b in pts])
                  for pts in (oval, branch)))
    ax = VGroup(Line(EC + P3(-0.8, 0), EC + P3(1.3, 0), stroke_color=C.grid, stroke_width=1.4),
                Line(EC + P3(0, -1.4), EC + P3(0, 1.4), stroke_color=C.grid, stroke_width=1.4))
    ec_l = tex(r"y^2 = x^3 - x", 38, Sp).move_to(EC + P3(2.75, 0))
    m.play(FadeIn(ax), Create(ec), at=t_ge - 0.3, dur=1.0)
    m.play(FadeIn(ec_l), at=t_ge + 0.1, dur=0.5)
    hexa = RegularPolygon(6, radius=0.75, stroke_color=St, stroke_width=4).move_to(HX)
    turn = Arc(radius=1.05, start_angle=math.pi / 6, angle=math.pi / 3, arc_center=HX, stroke_color=St,
               stroke_width=3).add_tip(tip_length=0.16, tip_width=0.14)
    hx_l = sans("symmetry", 30, St).move_to(HX + P3(-2.0, 0))
    m.play(Create(hexa), Create(turn), FadeIn(hx_l), at=t_alg - 0.3, dur=0.8)
    m.play(Rotate(hexa, math.pi / 3, about_point=HX), at=t_alg + 0.5, dur=0.9, ease="easy_ease")
    l1 = Line(ec_l.get_top() + P3(0, 0.12), P3(-1.3, -0.6), stroke_color=Sp, stroke_width=3)
    l2 = Line(hx_l.get_top() + P3(0, 0.12), P3(1.3, -0.6), stroke_color=St, stroke_width=3)
    m.play(Create(l1), at=t_ge + 0.3, dur=0.6)
    m.play(Create(l2), at=t_alg + 0.1, dur=0.6)

    # 'Every lens': the full map, every chord lit
    top.play(FadeOut(VGroup(fe, claim, yrs, lt)), at=t_ev - 0.5, dur=0.5)
    m.play(FadeOut(VGroup(ax, ec, ec_l, hexa, turn, hx_l, l1, l2)), at=t_ev - 0.5, dur=0.5)
    # the map draws in and lifts into 3D (the finale camera, continued by out_s01)
    t_wh = float(T.out_s01_what_is_a_circle)

    def ss(x):
        x = min(max(x, 0.0), 1.0)
        return x * x * (3 - 2 * x)

    def TV(t):
        return finale_view(t, t_ev, t_wh)

    def links_f(t):
        g = map_state(0, edges=EDGES, view=TV(t))[0]
        a = ss((t - t_ev) / 1.0)
        return dim(g, a) if a < 1 else g

    def nodes_f(t):
        g = map_state(0, lit=ALL, view=TV(t))[1]
        pulse = math.sin(math.pi * min(max((t - t_ev - 2.3) / 0.8, 0.0), 1.0))
        for k, n_ in enumerate(g):
            u = ss((t - t_ev - 0.08 * k) / 0.6)
            n_.scale(max(u * (1 + 0.12 * pulse), 1e-3), about_point=face_of(n_).get_center())
        return g

    def hub_f(t):
        return partial(hub_at(0, TV(t)), (t - t_ev) / 1.0)

    lnk.redraw(window(links_f, t_ev, t1 + 1.0), during=(t_ev, t1))
    nd.redraw(window(nodes_f, t_ev, t1 + 1.0), during=(t_ev, t1))
    m.redraw(window(hub_f, t_ev, t1 + 1.0), during=(t_ev, t1))
