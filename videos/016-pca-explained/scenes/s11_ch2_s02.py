"""ch2_s02 · Two ways to say best (L3 split, as in in_s05: Pearson left, Hotelling right).

The rail clears; the stage folds into the right board (Hotelling: the shadows) and its grid fades. A left board
(Pearson) shows the same cloud and line with every gap drawn (C.residual). The line leaves PC1 and goes back to
searching, the same line on both boards. On 'one point' the right board singles out one person: the distance
from the centre (C.mean), the shadow leg (C.pc1) and the gap leg (C.residual), a right-angle mark, then squares on
all three sides and ||x~||^2 = (x~.u)^2 + d^2. On 'shadows grow' the line turns toward PC1: the shadow square grows,
the gap square shrinks, the big one never changes; a stacked bar on the left board shows the totals for all forty
people trading height at a fixed sum. Both lines lock at PC1 and glow gold together on 'same'.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, KP, PHI1, STAGE_L2, X0, X1, Y1, P3, backed, board, caps, cen_grid, cen_names, dial_pinned,
                 drops_shadows, feet, glow_layer, grid_lines, mean_ring, panel, probe_line, rail_cloud, rail_var, smoothstep, tint,
                 udir)

LB, RB = (X0, -2.55, -0.125, Y1), (0.125, -2.55, X1, Y1)
CL, CR = np.array([-3.26, 0.33]), np.array([3.26, 0.33])


def sq_on(p1, p2, color, other, grow=1.0, alpha=1.0):
    """Square on side p1-p2 on the side away from `other`, grown out by `grow` (0..1)."""
    d = p2 - p1
    n3 = np.array([-d[1], d[0], 0.0])
    if np.dot(n3, other - p1) > 0:
        n3 = -n3
    n3 = n3 * grow
    return Polygon(p1, p2, p2 + n3, p1 + n3, stroke_color=color, stroke_width=2.2, stroke_opacity=alpha,
                   fill_color=tint(color, 0.2), fill_opacity=alpha)


@scene(T.ch2_s02, T.ch2_s03)
def ch2_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_close, t_one, t_dist = float(T.ch2_s02_closest_to_the_point), float(T.ch2_s02_one_point), float(T.ch2_s02_distance_from_the_ce)
    t_tri, t_pyth, t_grow = float(T.ch2_s02_right_triangle), float(T.ch2_s02_pythagoras), float(T.ch2_s02_shadows_grow)
    t_fits, t_same = float(T.ch2_s02_fits_closest), float(T.ch2_s02_same)
    t_shadow_w, t_gap_w = t_dist + 2.9, t_dist + 3.6            # 'Its shadow', 'its gap'
    t_pear, t_hot = t_same - 2.45, t_same - 1.35                # "Pearson's line", "Hotelling's direction"
    t_out = t1 - 0.9
    P = pd.people2()
    Xc = P.Xc
    n = len(Xc)
    u1 = udir(PHI1)
    nrm = np.array([-u1[1], u1[0]])
    sh, gp = Xc @ u1, np.abs(Xc @ nrm)
    I = 36                                                       # one person: shadow and gap trade 4 cm <-> 11 cm
    total = float((Xc ** 2).sum())

    # ---- the rail clears; the stage folds into the right board; the grid fades
    rail = s.manim(z=0, opacity=keys((t0, 1.0), (t0 + 0.1, 1.0), (t0 + 0.7, 0.0)))
    rail.add(rail_cloud(), rail_var(), dial_pinned())
    fold = keys((t0, 0.0), (t0 + 0.3, 0.0), (t0 + 1.5, 1.0))

    def cr_at(t):
        u = float(smoothstep(min(max(fold(t), 0.0), 1.0)))
        return CEN0 + (CR - CEN0) * u, u

    def right_board(t):
        c0, u = cr_at(t)
        bx = tuple(STAGE_L2[i] + (RB[i] - STAGE_L2[i]) * u for i in range(4))
        g = VGroup(panel(*bx))
        if u < 0.999:
            inner = (bx[0] + 0.05, bx[1] + 0.05, bx[2] - 0.05, bx[3] - 0.05)
            g.add(grid_lines(np.eye(2), c0, KP * 10, inner, n=12, minor=2, opacity=1 - u), cen_names(c0).set_opacity(1 - u))
        return g

    bm = s.manim(z=0)
    bm.redraw(right_board, during=(t0, t1))
    tags = s.manim(z=3, opacity=keys((t_out, 1.0), (t1 - 0.1, 0.0)))
    tags.play(FadeIn(caps("Hotelling", 28, C.muted).move_to(P3(RB[0] + 0.18, RB[3] - 0.2), aligned_edge=UL)),
              at=t0 + 1.6, dur=0.6)
    left_on = keys((t0, 0.0), (t0 + 1.4, 0.0), (t0 + 2.2, 1.0), (t_out, 1.0), (t1 - 0.1, 0.0))
    lb = s.manim(z=0, opacity=left_on)
    lb.add(panel(*LB), caps("Pearson", 28, C.muted).move_to(P3(LB[0] + 0.18, LB[3] - 0.2), aligned_edge=UL))

    # ---- the shared angle
    A = PHI1 - 50
    th = keys((t0, PHI1), (t0 + 1.6, PHI1), (t0 + 3.4, A), (t_grow - 0.2, A), (t_fits - 0.2, PHI1))
    gold = keys((t0, 1.0), (t0 + 1.6, 1.0), (t0 + 2.4, 0.0), (t_pear - 0.1, 0.0), (t_pear + 0.6, 1.0))
    gold_r = keys((t0, 1.0), (t0 + 1.6, 1.0), (t0 + 2.4, 0.0), (t_hot - 0.1, 0.0), (t_hot + 0.6, 1.0))
    gaps = keys((t0, 0.0), (t_close - 0.1, 0.0), (t_close + 2.0, 1.0, "linear"))
    focus = keys((t0, 0.0), (t_one - 0.1, 0.0), (t_one + 0.6, 1.0), (t_out, 1.0), (t1 - 0.1, 0.0))

    def col(g_):
        return interpolate_color(ManimColor(C.probe), ManimColor(C.pc1), g_)

    def right(t):
        c0, _ = cr_at(t)
        deg = float(th(t))
        f = float(focus(t))
        g = drops_shadows(c0, deg, Xc, 1.0, 1.0 - 0.6 * f, drop_op=0.5 * (1 - 0.6 * f))
        for i, p in enumerate(Xc):
            g.add(bead(P3(*(c0 + KP * p)), a=1.0 - 0.65 * f if i != I else 1.0))
        g.add(mean_ring(P3(*c0)))
        g.add(probe_line(c0, deg, L_cm=28, color=col(float(gold_r(t))), width=3.5 + float(gold_r(t))))
        return g

    def left(t):
        a = float(left_on(t))
        if a <= 0.001:
            return VGroup()
        deg = float(th(t))
        F = feet(Xc, deg)
        gg = float(gaps(t))
        g = VGroup()
        for i, (x, f_) in enumerate(zip(Xc, F)):
            loc = min(max(gg * 1.5 - 0.5 * i / n, 0.0), 1.0)
            if loc > 0.001:
                g.add(Line(P3(*(CL + KP * x)), P3(*(CL + KP * (x + (f_ - x) * loc))), stroke_color=C.residual,
                           stroke_width=2.4))
        g.add(*[bead(P3(*(CL + KP * p))) for p in Xc])
        g.add(probe_line(CL, deg, L_cm=28, color=col(float(gold(t))), width=3.5 + float(gold(t))))
        return g

    rm = s.manim(z=1)
    rm.redraw(right, during=(t0, t1))
    lm = s.manim(z=1, opacity=left_on)
    lm.redraw(left, during=(t0 + 1.3, t1))
    for c_, gtrack in ((CL, gold), (CR, gold_r)):
        gl = glow_layer(s, z=1.2, color=C.pc1, k=0.45 * 1.6, opacity=keys((t0, 0.0), (t_same - 0.2, 0.0),
                        (t_same + 0.3, 1.0), (t_same + 1.0, 0.0)))
        gl.add(probe_line(c_, PHI1, L_cm=28, color=C.pc1, width=4.5))
    g0 = glow_layer(s, z=1.2, color=C.pc1, k=0.45, opacity=keys((t0, 1.0), (t0 + 1.6, 1.0), (t0 + 2.4, 0.0)))
    g0.redraw(lambda t: probe_line(cr_at(t)[0], PHI1, color=C.pc1, width=4.5), during=(t0, t0 + 2.5))

    # ---- one person's right triangle and the three squares (pure functions of the angle)
    hyp = keys((t0, 0.0), (t_dist - 0.1, 0.0), (t_dist + 0.8, 1.0))
    legs_s = keys((t0, 0.0), (t_shadow_w - 0.1, 0.0), (t_shadow_w + 0.6, 1.0))
    legs_g = keys((t0, 0.0), (t_gap_w - 0.1, 0.0), (t_gap_w + 0.6, 1.0))
    ra = keys((t0, 0.0), (t_tri, 0.0), (t_tri + 0.5, 1.0))
    sqs = keys((t0, 0.0), (t_pyth - 0.1, 0.0), (t_pyth + 1.2, 1.0))

    def triangle(t):
        f = float(focus(t))
        if f <= 0.001:
            return VGroup()
        c0 = CR
        deg = float(th(t))
        x = Xc[I]
        q = feet(Xc[I:I + 1], deg)[0]
        O, A_, B = P3(*c0), P3(*(c0 + KP * q)), P3(*(c0 + KP * x))
        g = VGroup()
        gs = float(sqs(t))
        if gs > 0.001:
            g.add(sq_on(O, B, C.mean, A_, gs, f).set_fill(opacity=0), sq_on(O, A_, C.pc1, B, gs, f),
                  sq_on(A_, B, C.residual, O, gs, f))
        h_, ls, lg = float(hyp(t)), float(legs_s(t)), float(legs_g(t))
        if h_ > 0.001:
            g.add(Line(O, O + (B - O) * h_, stroke_color=C.mean, stroke_width=3.5, stroke_opacity=f))
        if ls > 0.001:
            g.add(Line(O, O + (A_ - O) * ls, stroke_color=C.pc1, stroke_width=5, stroke_opacity=f))
        if lg > 0.001:
            g.add(Line(A_, A_ + (B - A_) * lg, stroke_color=C.residual, stroke_width=4, stroke_opacity=f))
        r_ = float(ra(t))
        if r_ > 0.001 and np.linalg.norm(B - A_) > 0.2 and np.linalg.norm(A_ - O) > 0.2:
            g.add(RightAngle(Line(A_, O), Line(A_, B), length=0.14, stroke_color=C.text, stroke_width=1.6,
                             stroke_opacity=r_ * f))
        g.add(bead(B, r=0.08, a=f))
        return g

    tm = s.manim(z=2)
    tm.redraw(triangle, during=(t_one - 0.2, t1))
    eq = Eqn(r"\lVert \tilde x\rVert^2 = (\tilde x\cdot u)^2 + d^2",
             colors={r"\lVert \tilde x\rVert^2": C.mean, r"(\tilde x\cdot u)^2": C.pc1, r"d^2": C.residual}, size=46)
    eq.move_to(P3(0, -2.95))
    em = s.manim(z=3, opacity=keys((t_out, 1.0), (t1 - 0.1, 0.0)))
    em.play(Write(eq), at=t_pyth + 0.8, dur=2.0)

    # ---- the totals for everyone: a stacked bar at a fixed height on Pearson's board
    bar_on = keys((t0, 0.0), (t_grow - 0.7, 0.0), (t_grow - 0.1, 1.0), (t_out, 1.0), (t1 - 0.1, 0.0))
    bx, by0, bh, bw = LB[0] + 0.42, LB[1] + 0.35, 4.6, 0.3

    def bar(t):
        a = float(bar_on(t))
        if a <= 0.001:
            return VGroup()
        deg = float(th(t))
        kept = float(((Xc @ udir(deg)) ** 2).sum()) / total
        hk = bh * kept
        return VGroup(
            Rectangle(width=bw, height=hk, stroke_width=0, fill_color=C.pc1, fill_opacity=a).move_to(P3(bx, by0 + hk / 2)),
            Rectangle(width=bw, height=bh - hk, stroke_width=0, fill_color=C.residual, fill_opacity=a)
            .move_to(P3(bx, by0 + hk + (bh - hk) / 2)),
            Rectangle(width=bw + 0.08, height=bh + 0.08, stroke_color=C.mean, stroke_width=1.6, stroke_opacity=a)
            .move_to(P3(bx, by0 + bh / 2)))

    bb = s.manim(z=2)
    bb.redraw(bar, during=(t_grow - 0.8, t1))
