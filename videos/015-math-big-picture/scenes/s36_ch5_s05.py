"""ch5_s05 · A slightly bigger pizza (worked example).

The circle from ch5_s04 slides left and becomes a pizza (C.change crust, faint slices) with its radius tagged 10 cm. On
'millimeter' the 1 mm ring is drawn, exaggerated and tagged 'not to scale'; on 'How much' ΔA = ? waits through the
pause. On 'edge times' the estimate writes, 2π·10·0.1 ≈ 6.28; on 'exactly' π(10.1² − 10²) ≈ 6.31; then the difference,
π(0.1)² ≈ 0.03. On 'outer edge' and 'inner edge' the ring's two edges light in turn. On 'ten times smaller' the rows
fold into a table and a second row (nudge 0.01 cm) shows the difference a hundred times smaller.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, sans, tex, the_circle, tint

CC0, R0 = P3(-3.0, 0.65), 1.6               # where ch5_s04 left the circle
PZ, PR, RING = P3(-3.75, 0.2), 1.9, 0.26    # the pizza, and the exaggerated ring
LX, RX = 0.55, 6.35                         # row label left edge, equation right edge


def eq(*parts, size=42):
    return MathTex(*parts, font_size=size, color=C.text)


@scene(T.ch5_s05, T.ch5_s06)
def ch5_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_pz, t_mm, t_hm = float(T.ch5_s05_pizza), float(T.ch5_s05_millimeter), float(T.ch5_s05_how_much)
    t_et, t_ex, t_oe = float(T.ch5_s05_edge_times), float(T.ch5_s05_exactly), float(T.ch5_s05_outer_edge)
    t_10 = float(T.ch5_s05_ten_times_smaller)
    t_diff, t_in = t_oe - 1.84, t_oe + 1.92                                 # 'difference' 'inner edge'
    Ch = C.change
    out_t = t1 - 0.8

    # the circle becomes a pizza
    circ = the_circle(R0).move_to(CC0)
    m.add(circ)
    m.play(circ.animate.scale(PR / R0).move_to(PZ), at=t0 + 0.2, dur=0.9, ease="easy_ease")
    cheese = Circle(radius=PR - 0.08, stroke_width=0, fill_color=tint(Ch, 0.16), fill_opacity=1).move_to(PZ)
    crust = Circle(radius=PR - 0.04, stroke_color=Ch, stroke_width=12).move_to(PZ)
    slices = VGroup(*(Line(PZ, PZ + (PR - 0.12) * P3(math.cos(a), math.sin(a)), stroke_color=Ch, stroke_width=1.6,
                           stroke_opacity=0.5) for a in np.arange(8) * math.pi / 4 + math.pi / 8))
    pizza = VGroup(cheese, slices, crust)
    m.play(FadeIn(pizza), at=t_pz - 0.2, dur=0.7)
    m.play(FadeOut(circ), at=t_pz + 0.4, dur=0.4)
    rad = Line(PZ, PZ + P3(PR, 0), stroke_color=C.text, stroke_width=3)
    r_lab = sans("10 cm", 30, C.text).move_to(PZ + P3(PR / 2, 0.3))
    top.play(Create(rad), FadeIn(r_lab), at=t_pz + 0.4, dur=0.6)

    # 'millimeter': the ring, exaggerated
    ring = Annulus(inner_radius=PR, outer_radius=PR + RING, fill_color=Ch, fill_opacity=0.55, stroke_color=Ch,
                   stroke_width=2).move_to(PZ)
    m.play(GrowFromCenter(ring), at=t_mm - 0.6, dur=0.7, ease="out_back")
    nts = sans("not to scale", 26, C.muted).move_to(PZ + P3(0, -PR - RING - 0.4))
    m.play(FadeIn(nts), at=t_mm, dur=0.5)
    mm = sans("1 mm", 26, Ch).move_to(PZ + P3(PR + RING + 0.55, 0.0))
    m.play(FadeIn(mm), at=t_mm - 0.2, dur=0.5)

    # 'How much': ΔA = ?
    ask = eq(r"\Delta A", "=", "?", size=54)
    ask[0].set_color(Ch)
    ask.move_to(P3(3.45, 2.75))
    m.play(FadeIn(ask, shift=0.08 * DOWN), at=t_hm, dur=0.5)

    # estimate, exact, difference
    ys = (1.45, 0.35, -0.75)

    def row(label, e, y, col=C.text):
        lab = sans(label, 30, C.muted).move_to(P3(LX, y), aligned_edge=LEFT)
        e.move_to(P3(RX, y), aligned_edge=RIGHT)
        return VGroup(lab, e)

    est = eq(r"2\pi", r"\cdot 10", r"\cdot", r"0.1", r"\approx", r"6.28")
    est[3].set_color(Ch)
    est[5].set_color(Ch)
    r1 = row(r"edge $\times$ nudge", est, ys[0])
    exa = eq(r"\pi\left(10.1^2 - 10^2\right)", r"\approx", r"6.31")
    exa[2].set_color(Ch)
    r2 = row("exact", exa, ys[1])
    dif = eq(r"\pi\,(0.1)^2", r"\approx", r"0.03")
    dif[2].set_color(Ch)
    r3 = row("difference", dif, ys[2])
    m.play(FadeIn(r1[0]), Write(r1[1]), at=t_et, dur=1.2)
    m.play(FadeIn(r2[0]), Write(r2[1]), at=t_ex, dur=1.2)
    m.play(FadeIn(r3[0]), Write(r3[1]), at=t_diff, dur=1.0)

    # the two edges, in turn
    outer = Circle(radius=PR + RING, stroke_color=C.text, stroke_width=4).move_to(PZ)
    inner = Circle(radius=PR, stroke_color=C.text, stroke_width=4).move_to(PZ)
    top.play(Create(outer), at=t_oe, dur=0.8)
    top.play(FadeOut(outer), at=t_in - 0.2, dur=0.4)
    top.play(Create(inner), at=t_in, dur=0.8)
    top.play(FadeOut(inner), at=t_10 - 0.5, dur=0.4)

    # 'ten times smaller': a table, and a second nudge
    m.play(FadeOut(VGroup(r1, r2, r3, ask)), at=t_10 - 0.5, dur=0.5)
    cols = (0.75, 2.4, 4.0, 5.55)
    hy, ry = 2.1, (1.1, 0.1)
    head = VGroup(*(sans(h, 28, C.muted).move_to(P3(x, hy)) for h, x in
                    zip(("nudge", r"edge $\times$ nudge", "exact", "difference"), cols)))
    rule = Line(P3(0.3, hy - 0.4), P3(6.6, hy - 0.4), stroke_color=C.map_off, stroke_width=1.4)
    vals = []
    for dr, y in zip((0.1, 0.01), ry):
        a_, b_ = 2 * math.pi * 10 * dr, math.pi * ((10 + dr) ** 2 - 100)
        nd = 4 if dr < 0.05 else 3
        vals.append(VGroup(tex(f"{dr:g}", 40, Ch).move_to(P3(cols[0], y)),
                           tex(f"{a_:.{nd}f}", 40, C.text).move_to(P3(cols[1], y)),
                           tex(f"{b_:.{nd}f}", 40, C.text).move_to(P3(cols[2], y)),
                           tex(f"{b_ - a_:.3g}", 40, Ch).move_to(P3(cols[3], y))))
    m.play(FadeIn(head), Create(rule), at=t_10 - 0.1, dur=0.5)
    m.play(FadeIn(vals[0]), at=t_10 + 0.1, dur=0.5)
    m.play(LaggedStart(*(FadeIn(v_) for v_ in vals[1]), lag_ratio=0.25), at=t_10 + 0.7, dur=1.0)
    arr = CurvedArrow(vals[0][3].get_right() + P3(0.1, 0), vals[1][3].get_right() + P3(0.1, 0), angle=-1.6,
                      color=C.muted, stroke_width=2.4, tip_length=0.16)
    hund = tex(r"\div 100", 34, Ch).next_to(vals[1][3], DOWN, buff=0.3)
    m.play(Create(arr), FadeIn(hund), at=t_10 + 2.3, dur=0.6)
    ten = CurvedArrow(vals[0][0].get_left() + P3(-0.1, 0), vals[1][0].get_left() + P3(-0.1, 0), angle=1.6,
                      color=C.muted, stroke_width=2.4, tip_length=0.16)
    tenl = tex(r"\div 10", 34, Ch).next_to(ten, LEFT, buff=0.08)
    m.play(Create(ten), FadeIn(tenl), at=t_10 + 0.7, dur=0.5)

    # out: the pizza returns to the plain circle for ch5_s06
    circ2 = the_circle(PR).move_to(PZ)
    m.add(circ2, at=out_t)
    m.play(FadeOut(VGroup(pizza, ring, nts, mm, head, rule, *vals, arr, hund, ten, tenl)), at=out_t, dur=0.6)
    top.play(FadeOut(VGroup(rad, r_lab)), at=out_t, dur=0.6)
