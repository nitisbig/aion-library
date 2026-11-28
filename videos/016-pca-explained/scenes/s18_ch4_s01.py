"""ch4_s01 · Directions that don't turn (L2, rail: B_C, B_varu, B_heat).

Chapter card (carry-over strip: the matrix C). A fan of 12 unit arrows (C.probe) on the centred grid, each with a
faint dashed line through it (its own line). C acts (scaled to fit; a pure function of the blend): almost every
arrow is stretched and turned off its line. Two directions only stretch: they light up gold (v1) and teal (v2),
the rest dim. The blend replays on 'exactly where they were'. Cv = λv, then λ1 = 135.0, λ2 = 16.9. On 'long and
short axes' the cloud returns along them.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, KP, P3, PHI1, STAGE_L2, backed, board, cen_grid, chapter_card, glow_layer, people_v, rail_c,
                 rail_c_parts, rail_heat, rail_obj, udir)

R = 1.3                                           # unit arrow length on screen
ANG = PHI1 - 45 + 15 * np.arange(12)              # the fan: includes PHI1 (k=3) and PHI1 + 90 (k=9)
E1, E2 = 3, 9


def arrow(a, b, col, w=3.0, op=1.0, tip=0.16):
    return Arrow(P3(*a), P3(*b), buff=0, stroke_color=col, color=col, stroke_width=w,
                 max_tip_length_to_length_ratio=tip, max_stroke_width_to_length_ratio=30).set_opacity(op)


@scene(T.ch4_s01, T.ch4_s02)
def ch4_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_fan, t_str, t_two = float(T.ch4_s01_fan_of_arrows), float(T.ch4_s01_stretched_and_turned), float(T.ch4_s01_two_directions)
    t_ex, t_eig, t_val, t_ax = float(T.ch4_s01_exactly_where_they_w), float(T.ch4_s01_eigenvectors), float(T.ch4_s01_eigenvalue), float(T.ch4_s01_long_and_short_axes)
    P, V = people_v()
    lam = P.lam
    M = P.C * (2.0 / float(lam[0]))               # v1 stretches to 2x, v2 to 2 * 16.9 / 135.0

    # ---- card; strip = the matrix C
    on = chapter_card(s, t0, t0 + 2.6, "chapter four", "Eigenvectors")
    strip = s.manim(z=20, opacity=on * 0.5)
    strip.add(rail_c().move_to(P3(0, -2.35)))
    back = keys((t0, 0.0), (t0 + 2.2, 0.0), (t0 + 3.0, 1.0))
    st = s.manim(z=0, opacity=back)
    st.add(board(STAGE_L2), cen_grid(), rail_c(), rail_obj())
    rail_heat(s, z=0.5, opacity=back)

    # ---- the fan, its own lines, the action of C
    grow = keys((t0, 0.0), (t_fan - 0.4, 0.0), (t_fan + 0.6, 1.0))
    blend = keys((t0, 0.0), (t_fan + 0.9, 0.0), (t_str + 0.2, 1.0), (t_ex - 0.2, 1.0), (t_ex + 0.6, 0.0),
                 (t_ex + 1.0, 0.0), (t_ex + 2.0, 1.0))
    own = keys((t0, 0.0), (t_str - 0.2, 0.0), (t_str + 0.6, 1.0))
    pick = keys((t0, 0.0), (t_two - 0.1, 0.0), (t_two + 0.8, 1.0))
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))     # all but the two eigenvectors clear

    def fan(t):
        gw = float(grow(t))
        if gw <= 0.001:
            return VGroup()
        b, ow, pk, en = float(blend(t)), float(own(t)), float(pick(t)), float(end(t))
        A = np.eye(2) * (1 - b) + M * b
        g = VGroup()
        for k, d in enumerate(ANG):
            u = udir(d)
            eig = k in (E1, E2)
            if ow > 0.001:
                lc = C.muted if not eig else interpolate_color(ManimColor(C.muted), ManimColor(C.pc1 if k == E1 else C.pc2), pk)
                g.add(DashedLine(P3(*(CEN0 - 3.0 * u)), P3(*(CEN0 + 3.0 * u)), dash_length=0.07,
                                 stroke_color=lc, stroke_width=1.1 + 0.6 * pk * eig,
                                 stroke_opacity=en * ow * (0.5 * (1 - pk) + (0.8 if eig else 0.12) * pk)))
            if eig:
                col = interpolate_color(ManimColor(C.probe), ManimColor(C.pc1 if k == E1 else C.pc2), pk)
                g.add(arrow(CEN0, CEN0 + R * gw * (A @ u), col, 3.0 + 1.5 * pk, tip=0.16 + 0.3 * pk * (k == E2)))
            else:
                g.add(arrow(CEN0, CEN0 + R * gw * (A @ u), C.probe, 2.4, en * (0.9 - 0.65 * pk)))
        return g

    fm = s.manim(z=2)
    fm.redraw(fan, during=(t_fan - 0.5, t1))
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.6, opacity=keys((t0, 0.0), (t_two + 0.2, 0.0), (t_two + 1.0, 1.0)))
    gl.redraw(lambda t: arrow(CEN0, CEN0 + R * ((np.eye(2) * (1 - float(blend(t))) + M * float(blend(t))) @ udir(ANG[E1])),
                              C.pc1, 4.5), during=(t_two, t1))

    # ---- names and numbers
    m = s.manim(z=3, opacity=end)
    u1, u2 = udir(ANG[E1]), udir(ANG[E2])
    l1 = MathTex(r"v_1", font_size=44, color=C.pc1).move_to(P3(*(CEN0 + 2.0 * R * u1 + 0.38 * u2)))
    l2 = MathTex(r"v_2", font_size=44, color=C.pc2).move_to(P3(*(CEN0 + 0.75 * u2 + 0.3 * u1)))
    eq = backed(Eqn(r"C\,v = \lambda\,v", colors={r"C": C.spread, r"\lambda": C.spread}, size=50), 0.08)
    eq.move_to(P3(-4.65, 2.7))
    m.play(Write(eq), at=t_eig, dur=1.0)
    m.play(FadeIn(l1), FadeIn(l2), at=t_eig + 0.8, dur=0.6)
    vals = VGroup(Eqn(rf"\lambda_1 = {lam[0]:.1f}", colors={r"\lambda_1": C.pc1}, size=40),
                  Eqn(rf"\lambda_2 = {lam[1]:.1f}", colors={r"\lambda_2": C.pc2}, size=40)).arrange(DOWN, buff=0.18,
                                                                                                  aligned_edge=LEFT)
    vals = backed(vals, 0.08).move_to(P3(-4.85, 1.75))
    m.play(FadeIn(vals, shift=DOWN * 0.1), at=t_val, dur=0.8)

    # ---- the cloud, along the long and short axes
    cl = s.manim(z=1.5, opacity=end * keys((t0, 0.0), (t_ax - 0.2, 0.0), (t_ax + 0.8, 0.85)))
    cl.add(*[bead(P3(*(CEN0 + KP * q)), r=0.055) for q in P.Xc])
