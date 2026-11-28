"""ch4_s03 · Eigenvalues are spreads (L2, rail: B_C, B_varu, B_heat).

The Lagrange board clears; the plane slides back to the centre and the grid turns back square. The cloud returns.
On 'variance of the data' its shadows fall on v1 (λ1 = Var(v1)), then on v2 (λ2 = Var(v2)). On 'symmetric' the
matrix in the rail flashes with its mirror line; on 'right angles' a right-angle mark between v1 and v2, and they
are named PC1 and PC2. 'Put it together': C = V Λ V^T, and a circle carrying v1 and v2 makes the three moves, each
factor boxed on its word: turn to the eigen-axes (V^T), stretch (Λ), turn back (V). It lands as C's own ellipse.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, EIG_R, KP, P3, PHI1, STAGE_IN, STAGE_L2, X0, Y0, Y1, backed, board, drops_shadows,
                 eig_shape, eig_transform, eq_vlv, glow_layer, grid_lines, people_v, rail_c, rail_c_parts, rail_heat,
                 rail_obj, sans, slot, smoothstep, tex, udir)

R = EIG_R
CP = np.array([-3.75, -0.15])
PB = (X0 + 0.05, Y0 + 0.05, -1.2, Y1 - 0.05)
EX, BL, BR, BY = 0.55, -0.85, 2.0, -1.55


@scene(T.ch4_s03, T.ch4_s04)
def ch4_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_plain, t_var, t_sym, t_ra = float(T.ch4_s03_plain_meaning), float(T.ch4_s03_variance_of_the_data), float(T.ch4_s03_symmetric), float(T.ch4_s03_right_angles)
    t_turn, t_str, t_back = float(T.ch4_s03_turn_to_the_eigenvec), float(T.ch4_s03_stretch), float(T.ch4_s03_turn_back)
    t_why = t_ra + 1.9                            # "That's why the principal components come out perpendicular"
    t_put = t_turn - 4.2                          # 'Put it together'
    P, V = people_v()
    Xc = P.Xc
    v1, v2 = udir(PHI1), udir(PHI1 + 90)

    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_c(), rail_obj())
    rail_heat(s, z=0.5)

    # ---- the end of ch4_s02 clears
    old = s.manim(z=3)
    lg = MathTex(r"C", r"\,u", "=", r"\lambda", r"\,u", font_size=58)
    lg[0].set_color(C.spread)
    lg[3].set_color(C.spread)
    lg.move_to(P3(EX, 1.75))
    bar = VGroup(Line(P3(BL, BY), P3(BR, BY), stroke_color=C.axis, stroke_width=2),
                 Line(P3(BL, BY - 0.1), P3(BL, BY + 0.1), stroke_color=C.axis, stroke_width=2),
                 MathTex(r"\lambda_2", font_size=38, color=C.pc2).move_to(P3(BL, BY - 0.42)),
                 MathTex(r"\lambda_1", font_size=38, color=C.pc1).move_to(P3(BR, BY - 0.42)),
                 Rectangle(width=BR - BL, height=0.16, stroke_width=0, fill_color=C.pc1, fill_opacity=0.85)
                 .move_to(P3((BL + BR) / 2, BY + 0.42)),
                 Line(P3(BR, BY - 0.15), P3(BR, BY + 1.15), stroke_color=C.pc1, stroke_width=3.5),
                 Triangle(fill_color=C.spread, fill_opacity=1, stroke_width=0).scale(0.11).rotate(math.pi)
                 .move_to(P3(BR, BY + 0.14)),
                 MathTex(r"u^\top C\,u", font_size=32, color=C.spread).move_to(P3(BR - 0.5, BY + 0.85)))
    stale = VGroup(sans("Lagrange", 28, C.muted).move_to(P3(EX, 2.65)), lg,
                   MathTex("u", font_size=40, color=C.probe).move_to(P3(*(CP + (R + 0.3) * v1))),
                   SurroundingRectangle(lg, color=C.pc1, stroke_width=2.4, buff=0.14), bar,
                   Arrow(P3(*CP), P3(*(CP + 1.55 * R * v1)), buff=0, stroke_color=C.spread, color=C.spread,
                         stroke_width=3.4, max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=30))
    old.add(stale)
    old.play(FadeOut(stale), at=t0 + 0.05, dur=0.6)

    # ---- the plane slides back; the grid turns square again
    slide = keys((t0, 0.0), (t0 + 0.5, 0.0), (t0 + 1.9, 1.0))
    a1 = keys((t0, 0.0), (t_turn - 0.1, 0.0), (t_turn + 1.2, 1.0))
    a2 = keys((t0, 0.0), (t_str - 0.1, 0.0), (t_str + 1.2, 1.0))
    a3 = keys((t0, 0.0), (t_back - 0.1, 0.0), (t_back + 1.2, 1.0))
    circ_on = keys((t0, 0.0), (t_put + 0.6, 0.0), (t_put + 1.4, 1.0))

    def frame(t):
        u = float(smoothstep(min(max(slide(t), 0.0), 1.0)))
        return CP + (CEN0 - CP) * u, tuple(PB[i] + (STAGE_IN[i] - PB[i]) * u for i in range(4)), u

    def plane(t):
        c0, bx, u = frame(t)
        a = math.radians(PHI1) * (1 - u)
        Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        return grid_lines(Rm, c0, KP * 10, bx, n=12, minor=2)

    pm = s.manim(z=0.2)
    pm.redraw(plane, during=(t0, t1))

    def shape(t):
        c0, _, _ = frame(t)
        A = eig_transform(float(a1(t)), float(a2(t)), float(a3(t)))
        g = eig_shape(A, c0, R)
        g[0].set_stroke(color=interpolate_color(ManimColor(C.probe), ManimColor(C.spread), float(a3(t))),
                        opacity=float(circ_on(t)))
        return g

    vm = s.manim(z=2)
    vm.redraw(shape, during=(t0, t1))

    # ---- each eigenvalue is a spread: the shadows on v1, then on v2
    cl_on = keys((t0, 0.0), (t_plain - 0.6, 0.0), (t_plain + 0.4, 1.0), (t_put - 0.2, 1.0), (t_put + 0.6, 0.0))
    sh1 = keys((t0, 0.0), (t_var - 0.1, 0.0), (t_var + 1.2, 1.0), (t_var + 2.6, 1.0), (t_var + 3.0, 0.0))
    sh2 = keys((t0, 0.0), (t_var + 2.9, 0.0), (t_var + 3.8, 1.0), (t_sym - 0.5, 1.0), (t_sym, 0.0))

    def cloud(t):
        c = float(cl_on(t))
        if c <= 0.001:
            return VGroup()
        g = VGroup(*[bead(P3(*(CEN0 + KP * q)), r=0.055, a=c) for q in Xc])
        for tr, d in ((sh1, PHI1), (sh2, PHI1 + 90)):
            a = float(tr(t))
            if a > 0.001:
                g.add(drops_shadows(CEN0, d, Xc, a, a * c, drop_op=0.4 * a * c))
        return g

    cm = s.manim(z=1.5)
    cm.redraw(cloud, during=(t_plain - 0.7, t_put + 0.7))
    m = s.manim(z=3)
    l1 = backed(Eqn(r"\lambda_1 = \mathrm{Var}(v_1)", colors={r"\lambda_1": C.pc1, r"v_1": C.pc1}, size=42), 0.08)
    l2 = backed(Eqn(r"\lambda_2 = \mathrm{Var}(v_2)", colors={r"\lambda_2": C.pc2, r"v_2": C.pc2}, size=42), 0.08)
    l1.move_to(P3(-4.55, 2.72))
    l2.move_to(P3(-4.55, 2.1))
    m.play(FadeIn(l1), at=t_var + 0.6, dur=0.7)
    m.play(FadeIn(l2), at=t_var + 3.3, dur=0.7)

    # ---- symmetric: the rail matrix and its mirror line; right angles: PC1, PC2
    G = rail_c_parts()
    Mx = G[1]
    fl = SurroundingRectangle(Mx, color=C.spread, stroke_width=2.4, buff=0.1)
    mir = DashedLine(Mx.cell(0, 0).get_center() + P3(-0.25, 0.2), Mx.cell(1, 1).get_center() + P3(0.25, -0.2),
                     stroke_color=C.muted, stroke_width=2, dash_length=0.07)
    m.play(Create(fl), Create(mir), at=t_sym, dur=0.6)
    m.play(FadeOut(VGroup(fl, mir)), at=t_ra + 0.4, dur=0.5)
    mark = RightAngle(Line(P3(*CEN0), P3(*(CEN0 + v1))), Line(P3(*CEN0), P3(*(CEN0 + v2))), length=0.24,
                      stroke_color=C.text, stroke_width=2.4)
    m.play(Create(mark), at=t_ra - 0.2, dur=0.6)
    n1 = sans("PC1", 30, C.pc1).move_to(P3(*(CEN0 + (R + 0.45) * v1)))
    n2 = sans("PC2", 30, C.pc2).move_to(P3(*(CEN0 + (R + 0.45) * v2)))
    m.play(FadeIn(n1), FadeIn(n2), at=t_why, dur=0.7)
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.6, opacity=keys((t0, 0.0), (t_ra - 0.2, 0.0), (t_ra + 0.4, 1.0),
                                                                  (t_why + 2.2, 1.0), (t_why + 3.0, 0.0)))
    gl.add(VGroup(mark.copy(), *eig_shape(np.eye(2), CEN0, R)[1:]))
    m.play(FadeOut(VGroup(mark, n1, n2, l1, l2)), at=t_put - 0.2, dur=0.6)

    # ---- C = V Λ V^T: turn, stretch, turn back
    e = eq_vlv(54)
    eb = backed(e, 0.1).move_to(P3(-1.85, -2.62))
    m.play(Write(eb), at=t_put + 0.2, dur=1.2)
    for at, idx in ((t_turn, 4), (t_str, 3), (t_back, 2)):
        r = SurroundingRectangle(e[idx], color=C.pc1, stroke_width=2.2, buff=0.07)
        m.play(Create(r), at=at - 0.1, dur=0.4)
        m.play(FadeOut(r), at=at + 1.4 if idx != 2 else t1 - 0.25, dur=0.3 if idx != 2 else 0.2)
