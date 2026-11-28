"""ch4_s02 · Why the top one wins (L2, rail: B_C, B_varu, B_heat).

The plane slides to the left of the stage; v1 (gold) and v2 (teal) return to unit length. On 'eigenvectors as axes'
the grid turns until its lines run along them, and a unit arrow u (C.probe) gets its coordinates a, b (drops onto
both axes). u^T C u = λ1 a² + λ2 b² writes, then a² + b² = 1. A number line from λ2 to λ1: the mix is a pointer at
the end of a gold bar of length a² (the weight on λ1). As u turns the pointer moves, but never past λ1 (a wall on
'largest ingredient'). On 'all the weight' u turns onto v1 and the pointer reaches λ1 (glow). On 'Lagrange' u steps
off again and Cu (C.spread) shows: off the line of u; as u turns back to v1, Cu swings until it lies along u.
Cu = λu.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, KP, P3, PHI1, STAGE_IN, STAGE_L2, X0, Y0, Y1, backed, board, glow_layer, grid_lines, people_v,
                 rail_c, rail_heat, rail_obj, sans, smoothstep, udir)

R = 1.3
CP = np.array([-3.75, -0.15])
PB = (X0 + 0.05, Y0 + 0.05, -1.2, Y1 - 0.05)
EX = 0.55                                         # the equation column
BL, BR, BY = -0.85, 2.0, -1.55                    # the number line


def arrow(a, b, col, w=3.0, op=1.0, tip=0.18):
    return Arrow(P3(*a), P3(*b), buff=0, stroke_color=col, color=col, stroke_width=w,
                 max_tip_length_to_length_ratio=tip, max_stroke_width_to_length_ratio=30).set_opacity(op)


@scene(T.ch4_s02, T.ch4_s03)
def ch4_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_axes, t_mix, t_one = float(T.ch4_s02_eigenvectors_as_axes), float(T.ch4_s02_mix), float(T.ch4_s02_add_up_to_one)
    t_large, t_all, t_lag, t_itself = float(T.ch4_s02_largest_ingredient), float(T.ch4_s02_all_the_weight), float(T.ch4_s02_lagrange_multipliers), float(T.ch4_s02_arrow_itself)
    P, V = people_v()
    lam1, lam2 = float(P.lam[0]), float(P.lam[1])
    v1, v2 = udir(PHI1), udir(PHI1 + 90)
    M = P.C * (2.0 / lam1)                        # as in ch4_s01
    M2 = P.C * (1.55 / lam1)                      # Cu at the end: 1.55 R along v1
    G, G2 = PHI1 + 55, PHI1 + 40

    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_c(), rail_obj())
    rail_heat(s, z=0.5)

    # ---- the plane slides left; the grid turns to the eigen-axes
    slide = keys((t0, 0.0), (t0 + 0.3, 0.0), (t0 + 1.6, 1.0))
    turn = keys((t0, 0.0), (t_axes - 0.3, 0.0), (t_axes + 1.6, 1.0))

    def frame(t):
        u = float(smoothstep(min(max(slide(t), 0.0), 1.0)))
        return CEN0 + (CP - CEN0) * u, tuple(STAGE_IN[i] + (PB[i] - STAGE_IN[i]) * u for i in range(4))

    def plane(t):
        c0, bx = frame(t)
        a = math.radians(PHI1) * float(turn(t))
        Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        return grid_lines(Rm, c0, KP * 10, bx, n=12, minor=2)

    pm = s.manim(z=0.2)
    pm.redraw(plane, during=(t0, t1))

    # ---- v1, v2 back to unit length; the probe u and its coordinates
    unit = keys((t0, 1.0), (t0 + 0.3, 1.0), (t0 + 1.5, 0.0))
    u_on = keys((t0, 0.0), (t_axes - 1.4, 0.0), (t_axes - 0.6, 1.0))
    coords = keys((t0, 0.0), (t_axes + 1.4, 0.0), (t_axes + 2.2, 1.0))
    th = keys((t0, G), (t_one + 0.8, G), (t_large - 0.4, PHI1 + 100), (t_large + 1.6, PHI1 + 72),
              (t_all - 0.2, PHI1 + 72), (t_all + 1.4, PHI1), (t_lag - 0.3, PHI1), (t_lag + 0.6, G2),
              (t_lag + 2.4, G2), (t_lag + 5.0, PHI1))
    cu_on = keys((t0, 0.0), (t_lag + 0.6, 0.0), (t_lag + 1.3, 1.0))

    def vecs(t):
        c0, _ = frame(t)
        b = float(unit(t))
        A = np.eye(2) * (1 - b) + M * b
        g = VGroup(arrow(c0, c0 + R * (A @ v2), C.pc2, 4.0, tip=0.18 + 0.3 * b),
                   arrow(c0, c0 + R * (A @ v1), C.pc1, 4.5))
        ua = float(u_on(t))
        if ua > 0.001:
            u = udir(float(th(t)))
            a_, b_ = float(u @ v1), float(u @ v2)
            tip = c0 + R * u
            co = float(coords(t))
            if co > 0.001:
                f1, f2 = c0 + R * a_ * v1, c0 + R * b_ * v2
                g.add(DashedLine(P3(*tip), P3(*f1), stroke_color=C.pc1, stroke_width=1.8, dash_length=0.06,
                                 stroke_opacity=0.8 * co),
                      DashedLine(P3(*tip), P3(*f2), stroke_color=C.pc2, stroke_width=1.8, dash_length=0.06,
                                 stroke_opacity=0.8 * co))
                if abs(a_) > 0.15 and abs(b_) > 0.15:
                    g.add(MathTex("a", font_size=36, color=C.pc1).set_opacity(co)
                          .move_to(P3(*(c0 + R * a_ * v1 - 0.28 * np.sign(b_ or 1) * v2))))
                if abs(b_) > 0.15:
                    g.add(MathTex("b", font_size=36, color=C.pc2).set_opacity(co)
                          .move_to(P3(*(c0 + R * b_ * v2 - 0.28 * np.sign(a_ or 1) * v1))))
            ca = float(cu_on(t))
            if ca > 0.001:
                g.add(arrow(c0, c0 + R * (M2 @ u), C.spread, 3.4, ca))
            g.add(arrow(c0, tip, C.probe, 3.6, ua))
            g.add(MathTex("u", font_size=40, color=C.probe).set_opacity(ua).move_to(P3(*(tip + 0.3 * u))))
        return g

    vm = s.manim(z=2)
    vm.redraw(vecs, during=(t0, t1))

    # ---- the equations
    m = s.manim(z=3)
    e1 = MathTex(r"u^\top C\,u", "=", r"\lambda_1", r"a^2", "+", r"\lambda_2", r"b^2", font_size=46)
    e1[0][2].set_color(C.spread)
    for i, col in ((2, C.pc1), (3, C.pc1), (5, C.pc2), (6, C.pc2)):
        e1[i].set_color(col)
    e1.scale(min(1.0, 3.3 / e1.width)).move_to(P3(EX, 2.35))
    e2 = MathTex(r"a^2", "+", r"b^2", "= 1", font_size=46)
    e2[0].set_color(C.pc1)
    e2[2].set_color(C.pc2)
    e2.move_to(P3(EX, 1.45))
    m.play(Write(e1), at=t_mix - 0.4, dur=1.4)
    m.play(Write(e2), at=t_one - 0.5, dur=1.0)

    # ---- the number line: the mix lies between λ2 and λ1
    W = BR - BL
    line = VGroup(Line(P3(BL, BY), P3(BR, BY), stroke_color=C.axis, stroke_width=2),
                  Line(P3(BL, BY - 0.1), P3(BL, BY + 0.1), stroke_color=C.axis, stroke_width=2),
                  Line(P3(BR, BY - 0.1), P3(BR, BY + 0.1), stroke_color=C.axis, stroke_width=2),
                  MathTex(r"\lambda_2", font_size=38, color=C.pc2).move_to(P3(BL, BY - 0.42)),
                  MathTex(r"\lambda_1", font_size=38, color=C.pc1).move_to(P3(BR, BY - 0.42)))
    bar_on = keys((t0, 0.0), (t_one + 0.2, 0.0), (t_one + 1.0, 1.0))
    m.play(FadeIn(line), at=t_mix + 0.6, dur=0.8)

    def mix(t):
        ba = float(bar_on(t))
        if ba <= 0.001:
            return VGroup()
        u = udir(float(th(t)))
        a2 = float(u @ v1) ** 2
        x = BL + a2 * W
        g = VGroup(Rectangle(width=max(a2 * W, 1e-3), height=0.16, stroke_width=0, fill_color=C.pc1,
                             fill_opacity=0.85 * ba).move_to(P3(BL + a2 * W / 2, BY + 0.42)),
                   Rectangle(width=max((1 - a2) * W, 1e-3), height=0.16, stroke_width=0, fill_color=C.pc2,
                             fill_opacity=0.6 * ba).move_to(P3(x + (1 - a2) * W / 2, BY + 0.42)),
                   Triangle(fill_color=C.spread, fill_opacity=ba, stroke_width=0).scale(0.11).rotate(math.pi)
                   .move_to(P3(x, BY + 0.14)))
        g.add(MathTex(r"u^\top C\,u", font_size=32, color=C.spread).set_opacity(ba).move_to(P3(min(x, BR - 0.5), BY + 0.85)))
        return g

    mm = s.manim(z=3.1)
    mm.redraw(mix, during=(t_one, t1))
    wall = Line(P3(BR, BY - 0.15), P3(BR, BY + 1.15), stroke_color=C.pc1, stroke_width=3.5)
    m.play(Create(wall), at=t_large, dur=0.6)
    gw = glow_layer(s, z=2.9, color=C.pc1, k=0.8, opacity=keys((t0, 0.0), (t_all + 0.9, 0.0), (t_all + 1.5, 1.0),
                                                                   (t_all + 3.2, 1.0), (t_all + 4.0, 0.0)))
    gw.add(wall.copy(), Dot(P3(BR, BY), radius=0.09, color=C.pc1))
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.5, opacity=keys((t0, 0.0), (t_all + 0.9, 0.0), (t_all + 1.5, 1.0)))
    gl.redraw(lambda t: arrow(frame(t)[0], frame(t)[0] + R * v1, C.pc1, 4.5), during=(t_all, t1))

    # ---- Lagrange: the best arrow is one that C does not turn
    m.play(FadeOut(VGroup(e1, e2)), at=t_lag - 0.5, dur=0.5)
    tag = sans("Lagrange", 28, C.muted).move_to(P3(EX, 2.65))
    lg = MathTex(r"C", r"\,u", "=", r"\lambda", r"\,u", font_size=58)
    lg[0].set_color(C.spread)
    lg[3].set_color(C.spread)
    lg.move_to(P3(EX, 1.75))
    m.play(FadeIn(tag), at=t_lag, dur=0.6)
    m.play(Write(lg), at=t_lag + 0.8, dur=1.0)
    box = SurroundingRectangle(lg, color=C.pc1, stroke_width=2.4, buff=0.14)
    m.play(Create(box), at=t_itself - 0.6, dur=0.7)
