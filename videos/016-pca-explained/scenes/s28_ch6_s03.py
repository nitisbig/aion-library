"""ch6_s03 · Spread isn't meaning (L2, rail: B_recipe, B_scree).

Two long thin groups lying side by side (C.data and C.pc3). On 'first component' PC1 (gold) draws along their
length. On 'piles both groups' every point slides to its shadow on a wall parallel to PC1 (below the cloud): the two
colours pile on top of each other. On 'separates them' PC2 (teal) and its own wall beyond the cloud's end: the
shadows fall in two clean clumps. On 'ranks it last' the two eigenvalues: λ1 = 4.18, λ2 = 0.32. On 'keeps the most
variation' the PC1 wall glows; everything clears for the outro.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import CEN0, P3, STAGE_L2, backed, bead, board, glow_layer, rail_recipe, rail_scree, smoothstep

KG = 0.6
CG = CEN0 + np.array([-0.55, 0.45])               # the cloud's centre


@scene(T.ch6_s03, T.out_s01)
def ch6_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_lt, t_pc1, t_pile = float(T.ch6_s03_long_and_thin), float(T.ch6_s03_first_component), float(T.ch6_s03_piles_both_groups)
    t_sep, t_last, t_keep, t_call = float(T.ch6_s03_separates_them), float(T.ch6_s03_ranks_it_last), float(T.ch6_s03_keeps_the_most_varia), float(T.ch6_s03_your_call)
    X, lab = pd.two_groups()
    Q = pd.pca(X)
    Xc = Q.Xc
    u1, u2 = Q.V[:, 0], Q.V[:, 1]
    if u1[0] < 0:
        u1 = -u1
    u2 = np.array([-u1[1], u1[0]])
    z1, z2 = Xc @ u1, Xc @ u2
    cols = (C.data, C.pc3)
    end = keys((t0, 1.0), (t1 - 0.9, 1.0), (t1 - 0.1, 0.0))

    st = s.manim(z=0, opacity=end)
    st.add(board(STAGE_L2), rail_recipe(), rail_scree())

    W1 = CG - 1.7 * u2                         # the PC1 wall's centre (below the cloud)
    W2 = CG + 3.55 * u1                         # the PC2 wall's centre (beyond the cloud's end)
    grp = [keys((t0, 0.0), (t_lt - 0.3 + 0.6 * g, 0.0), (t_lt + 0.6 + 0.6 * g, 1.0)) for g in (0, 1)]
    sh1 = keys((t0, 0.0), (t_pile - 0.2, 0.0), (t_pile + 1.6, 1.0))
    sh2 = keys((t0, 0.0), (t_sep + 0.5, 0.0), (t_sep + 2.1, 1.0))
    n = len(X)
    rank = np.argsort(np.argsort(z1))

    def cloud(t):
        g = VGroup()
        s1, s2 = float(sh1(t)), float(sh2(t))
        for k in range(n):
            a = float(grp[lab[k]](t))
            if a <= 0.001:
                continue
            p = CG + KG * Xc[k]
            g.add(bead(P3(*p), r=0.045, color=cols[lab[k]], a=0.9 * a))
            lag = 0.5 * rank[k] / n
            for sv, W, uu, z in ((s1, W1, u1, z1[k]), (s2, W2, u2, z2[k])):
                loc = min(max(sv * 1.5 - lag, 0.0), 1.0)
                if loc > 0.001:
                    f = W + KG * z * uu
                    q = p + (f - p) * float(smoothstep(loc))
                    if loc < 0.999:
                        g.add(Line(P3(*p), P3(*q), stroke_color=C.muted, stroke_width=0.8, stroke_opacity=0.3 * (1 - loc)))
                    g.add(bead(P3(*q), r=0.04, color=cols[lab[k]], a=0.75))
        return g

    cm = s.manim(z=2, opacity=end)
    cm.redraw(cloud, during=(t_lt - 0.4, t1))

    # ---- the two directions and their walls
    m = s.manim(z=1.5, opacity=end)
    pc1 = Line(P3(*(CG - 3.2 * u1)), P3(*(CG + 3.2 * u1)), stroke_color=C.pc1, stroke_width=4)
    pc2 = Line(P3(*(CG - 1.2 * u2)), P3(*(CG + 1.2 * u2)), stroke_color=C.pc2, stroke_width=4)
    wall1 = Line(P3(*(W1 - 3.1 * u1)), P3(*(W1 + 3.1 * u1)), stroke_color=C.pc1, stroke_width=2.2, stroke_opacity=0.7)
    wall2 = Line(P3(*(W2 - 1.0 * u2)), P3(*(W2 + 1.0 * u2)), stroke_color=C.pc2, stroke_width=2.2, stroke_opacity=0.7)
    m.play(Create(pc1), at=t_pc1, dur=0.8)
    m.play(Create(wall1), at=t_pile - 0.6, dur=0.6)
    m.play(Create(pc2), at=t_sep - 0.1, dur=0.6)
    m.play(Create(wall2), at=t_sep + 0.3, dur=0.5)
    gl = glow_layer(s, z=1.4, color=C.pc1, k=0.6, opacity=end * keys((t0, 0.0), (t_pc1 + 0.4, 0.0), (t_pc1 + 1.0, 1.0),
                                                                       (t_pile, 1.0), (t_pile + 0.6, 0.0),
                                                                       (t_keep - 0.1, 0.0), (t_keep + 0.6, 1.0)))
    gl.add(pc1.copy())

    # ---- the eigenvalues: the separating direction comes last
    t = Eqn(rf"\lambda_1 = {Q.lam[0]:.2f}", colors={r"\lambda_1": C.pc1}, size=40)
    t.move_to(P3(*(W1 + 0.9 * u1 - 0.75 * u2)))
    t2 = Eqn(rf"\lambda_2 = {Q.lam[1]:.2f}", colors={r"\lambda_2": C.pc2}, size=40)
    t2.move_to(P3(*(W2 + 0.9 * u2 - 1.35 * u1)))
    mm = s.manim(z=3, opacity=end)
    mm.play(FadeIn(t), at=t_last - 0.4, dur=0.6)
    mm.play(FadeIn(t2), at=t_last + 0.3, dur=0.6)
