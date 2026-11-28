"""ch2_s03 · Write it down (L2, rail: B_cloud, B_var -> B_varu, B_dial).

Hotelling's board unfolds back into the stage and the rail returns. The line leaves PC1 for a general direction.
A unit arrow u (C.probe) with a dashed unit circle. One person's shadow length is the dot product x~.u (a thick
C.data segment from the centre to the foot). On 'Square each shadow' every shadow grows its square (C.spread, as
in B_var), the variance in that direction writes, and on 'one sentence' it becomes the whole problem:
max over ||u|| = 1 of (1/n) sum (x~_i.u)^2. On 'as big as possible' it pins into rail slot 2 (B_varu), replacing B_var.
The line then returns to PC1 and goes gold for ch2_s04.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, KP, PHI1, STAGE_L2, P3, backed, board, cen_grid, cen_names, dial_pinned, eq_obj, feet,
                 glow_layer, grid_lines, mean_ring, panel, probe_line, rail_cloud, rail_obj_parts, rail_var_parts, slot,
                 smoothstep, udir)

RB = (0.125, -2.55, 6.40, 3.29)
CR = np.array([3.26, 0.33])
U = 10.0                                         # the unit arrow is drawn 10 cm (one grid square) long


@scene(T.ch2_s03, T.ch2_s04)
def ch2_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_arrow, t_dot, t_sq = float(T.ch2_s03_arrow_one_unit_long), float(T.ch2_s03_dot_product), float(T.ch2_s03_square_each_shadow)
    t_var, t_one, t_big = float(T.ch2_s03_variance_in_that_dir), float(T.ch2_s03_one_sentence), float(T.ch2_s03_as_big_as_possible)
    t_among = t_one + 1.5                        # 'Among all arrows of length one'
    P = pd.people2()
    Xc = P.Xc
    I = 36
    G = PHI1 - 35

    # ---- Hotelling's board unfolds into the stage; grid, names and rail return
    unf = keys((t0, 0.0), (t0 + 0.2, 0.0), (t0 + 1.4, 1.0))

    def c_at(t):
        u = float(smoothstep(min(max(unf(t), 0.0), 1.0)))
        return CR + (CEN0 - CR) * u, u

    def stage(t):
        c0, u = c_at(t)
        bx = tuple(RB[i] + (STAGE_L2[i] - RB[i]) * u for i in range(4))
        g = VGroup(panel(*bx))
        if u > 0.001:
            inner = (bx[0] + 0.05, bx[1] + 0.05, bx[2] - 0.05, bx[3] - 0.05)
            g.add(grid_lines(np.eye(2), c0, KP * 10, inner, n=12, minor=2, opacity=u), cen_names(c0).set_opacity(u))
        return g

    st = s.manim(z=0)
    st.redraw(stage, during=(t0, t0 + 1.5))
    st.add(board(STAGE_L2), cen_grid(), cen_names(), at=t0 + 1.5)
    rail_on = keys((t0, 0.0), (t0 + 1.0, 0.0), (t0 + 1.7, 1.0))
    rl = s.manim(z=0, opacity=rail_on)
    rl.add(board(slot(0)), board(slot(1)), rail_cloud(), dial_pinned())
    vsq, veq = rail_var_parts()
    rl.add(vsq, veq)

    # ---- the line: from PC1 to a general direction, and back to PC1 (gold) at the end
    th = keys((t0, PHI1), (t0 + 1.4, PHI1), (t0 + 3.0, G), (t_big + 0.9, G), (t1 - 0.4, PHI1))
    gold = keys((t0, 1.0), (t0 + 1.4, 1.0), (t0 + 2.2, 0.0), (t_big + 1.0, 0.0), (t1 - 0.3, 1.0))
    shadows = keys((t0, 1.0), (t0 + 1.4, 1.0), (t0 + 2.0, 0.0))
    focus = keys((t0, 0.0), (t_dot - 0.2, 0.0), (t_dot + 0.4, 1.0), (t_big + 0.5, 1.0), (t_big + 1.2, 0.0))

    def cloud(t):
        c0, _ = c_at(t)
        deg = float(th(t))
        f = float(focus(t))
        g = VGroup()
        sh = float(shadows(t))
        if sh > 0.001:
            for x, q in zip(Xc, feet(Xc, deg)):
                g.add(Line(P3(*(c0 + KP * x)), P3(*(c0 + KP * q)), stroke_color=C.muted, stroke_width=1.4,
                           stroke_opacity=0.5 * sh))
                g.add(Circle(radius=0.05, stroke_color=C.data, stroke_width=2.2, stroke_opacity=sh).move_to(P3(*(c0 + KP * q))))
        for i, p in enumerate(Xc):
            g.add(bead(P3(*(c0 + KP * p)), r=0.062 if i != I else 0.085,
                      a=1.0 - 0.6 * f if i != I else 1.0))
        g.add(mean_ring(P3(*c0)))
        gg = float(gold(t))
        g.add(probe_line(c0, deg, color=interpolate_color(ManimColor(C.probe), ManimColor(C.pc1), gg),
                         width=3.5 + gg))
        return g

    cm = s.manim(z=2)
    cm.redraw(cloud, during=(t0, t1))
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.45, opacity=keys((t0, 1.0), (t0 + 1.4, 1.0), (t0 + 2.2, 0.0),
                                                                    (t1 - 0.5, 0.0), (t1 - 0.1, 1.0)))
    gl.redraw(lambda t: probe_line(c_at(t)[0], PHI1, color=C.pc1, width=4.5), during=(t0, t1))

    # ---- the unit arrow and circle, ||u|| = 1
    m = s.manim(z=3)
    O = P3(*CEN0)
    tip = P3(*(CEN0 + KP * U * udir(G)))
    circ = DashedVMobject(Circle(radius=KP * U, stroke_color=C.muted, stroke_width=1.8).move_to(O), num_dashes=36)
    arr = Arrow(O, tip, buff=0, stroke_color=C.probe, stroke_width=6, max_tip_length_to_length_ratio=0.22,
                color=C.probe)
    ul = tex_u = MathTex(r"u", font_size=44, color=C.probe).move_to(tip + P3(*(0.3 * udir(G + 90))))
    m.play(Create(circ), at=t_arrow - 0.2, dur=1.0)
    m.play(GrowArrow(arr), FadeIn(ul), at=t_arrow, dur=0.8)
    norm = backed(Eqn(r"\lVert u\rVert = 1", size=42), 0.08).move_to(P3(1.15, 2.75))
    m.play(FadeIn(norm), at=t_arrow + 1.1, dur=0.7)

    # ---- one shadow is the dot product
    x = Xc[I]
    q = feet(Xc[I:I + 1], G)[0]
    drop = DashedLine(P3(*(CEN0 + KP * x)), P3(*(CEN0 + KP * q)), stroke_color=C.muted, stroke_width=1.8,
                      dash_length=0.08)
    seg = Line(O, P3(*(CEN0 + KP * q)), stroke_color=C.data, stroke_width=7)
    lab = backed(Eqn(r"\tilde x\cdot u", colors={r"\tilde x": C.data, r"u": C.probe}, size=42), 0.06)
    lab.move_to(P3(*(CEN0 + KP * q / 2 - 0.42 * udir(G + 90))))
    m.play(Create(drop), at=t_dot - 0.3, dur=0.5)
    m.play(Create(seg), at=t_dot, dur=0.7)
    m.play(FadeIn(lab), at=t_dot + 0.5, dur=0.6)

    # ---- square each shadow (every person), the variance in that direction
    nv = udir(G + 90)                            # the squares stand on the far side from the label
    sqs = VGroup()
    for p in Xc:
        f_ = float(p @ udir(G))
        a_, b_ = CEN0, CEN0 + KP * f_ * udir(G)
        side = abs(f_) * KP
        sqs.add(Polygon(P3(*a_), P3(*b_), P3(*(b_ + side * nv)), P3(*(a_ + side * nv)), stroke_color=C.spread,
                        stroke_width=1.1, stroke_opacity=0.55, fill_color=C.spread, fill_opacity=0.02))
    order = np.argsort(np.abs(Xc @ udir(G)))
    m.play(LaggedStart(*[FadeIn(sqs[i], scale=0.4) for i in order], lag_ratio=0.03), at=t_sq + 0.9, dur=1.6)
    flash = Rectangle(width=slot(1)[2] - slot(1)[0], height=slot(1)[3] - slot(1)[1], stroke_color=C.spread,
                      stroke_width=3).move_to(P3((slot(1)[0] + slot(1)[2]) / 2, (slot(1)[1] + slot(1)[3]) / 2))
    m.play(FadeIn(flash), at=t_sq + 1.6, dur=0.4)
    m.play(FadeOut(flash), at=t_sq + 2.6, dur=0.6)
    var = Eqn(r"\mathrm{Var}(u) = \tfrac{1}{n}\sum_i \left(\tilde x_i\cdot u\right)^2",
              colors={r"\mathrm{Var}(u)": C.spread}, size=44)
    vb = backed(var, 0.08).move_to(P3(-2.05, -2.62))
    m.play(Write(vb), at=t_var, dur=1.3)

    # ---- one sentence: the objective; it pins into rail slot 2
    obj = backed(eq_obj(46), 0.08).move_to(P3(-2.05, -2.62))
    m.play(FadeOut(VGroup(seg, drop, lab)), at=t_one, dur=0.6)
    m.play(FadeTransform(vb, obj), FadeOut(norm), at=t_among, dur=1.2)
    m.play(FadeOut(sqs), at=t_big - 0.4, dur=0.7)
    req = rail_obj_parts()
    rl.play(FadeOut(VGroup(vsq, veq)), at=t_big, dur=0.5)
    m.play(FadeOut(obj[0]), at=t_big, dur=0.3)
    m.play(ReplacementTransform(obj[1], req), at=t_big, dur=1.0)
    m.play(FadeOut(VGroup(arr, ul, circ)), at=t1 - 1.3, dur=0.6)
