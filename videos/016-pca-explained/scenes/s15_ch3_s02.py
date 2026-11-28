"""ch3_s02 · What is inside C (L2, rail: B_C pinned at the end, B_varu, B_dial).

The cloud comes back on a plane at the left of the stage; u^T C u opens into C = [2x2]. The variances fill the
diagonal (67.1, 84.8: the same spreads as ch1). The empty off-diagonal slots are outlined: the covariance,
sigma_ha = (1/n) sum h~_i a~_i. Each person's deviation rectangle draws from the centre to their dot: tall with long
arms (upper right) and short with short arms (lower left) fill C.spread (+), the mixed ones C.residual (-). On
'Average the products' they dim and their signed average draws as one square (area 58.4 cm^2), which flies into
both off-diagonal slots. On 'symmetric' a mirror line crosses the diagonal and the two entries swap places; the
matrix pins into rail slot 1 (B_C).
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (P3, STAGE_L2, backed, board, c_matrix, dial_pinned, dots, grid_lines, rail_c_parts, rail_obj, sans,
                 slot, tex)

CC = np.array([-3.85, -0.1])
KC = 0.092
PBOX = (STAGE_L2[0] + 0.05, STAGE_L2[1] + 0.05, STAGE_L2[0] + 5.1, STAGE_L2[3] - 0.05)
MX = 0.5                                          # the matrix column


def p(x, y):
    return P3(CC[0] + KC * x, CC[1] + KC * y)


@scene(T.ch3_s02, T.ch3_s03)
def ch3_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_diag, t_cov, t_mul = float(T.ch3_s02_diagonal), float(T.ch3_s02_covariance), float(T.ch3_s02_multiply)
    t_tall, t_short, t_mixed = float(T.ch3_s02_tall_person_with_lon), float(T.ch3_s02_short_person_with_sh), float(T.ch3_s02_mixed_cases)
    t_avg, t_sym = float(T.ch3_s02_average_the_products), float(T.ch3_s02_symmetric)
    t_inside = t0 + 0.9                            # "What's inside it?"
    t_sh_h, t_sh_a = t_diag + 3.0, t_diag + 4.1     # 'spread of height', 'spread of arm span'
    t_off = t_cov - 2.5                             # 'Off the diagonal'
    t_each = t_cov + 1.4                            # 'For each person'
    t_pin = t_sym + 2.6
    P = pd.people2()
    Xc = P.Xc
    cov = float(P.C[0, 1])

    # ---- stage, rail, plane and cloud
    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_obj(), dial_pinned())
    pl = s.manim(z=0.2, opacity=keys((t0, 0.0), (t0 + 0.2, 0.0), (t0 + 1.2, 1.0)))
    pl.add(grid_lines(np.eye(2), CC, KC * 10, PBOX, n=10, minor=2),
           backed(sans("height", 24, C.muted)).move_to(p(21, -3)),
           backed(sans("arm span", 24, C.muted)).move_to(p(-8.5, 31)))
    cl = s.manim(z=2, opacity=keys((t0, 0.2), (t0 + 0.3, 0.2), (t0 + 1.1, 1.0)))
    cl.add(dots([p(*q) for q in Xc], C.data))

    # ---- u^T C u opens into the matrix
    m = s.manim(z=3)
    L4 = MathTex(r"u^\top", r"C", r"\,u", font_size=60)
    L4[1].set_color(C.spread)
    L4.scale(min(1.0, 3.75 / L4.width)).move_to(P3(0.32, 0.35))
    m.add(L4)
    G = c_matrix(44)
    G.scale(min(1.0, 3.4 / G.width)).move_to(P3(MX, 1.2))
    lhs, M = G
    m.play(ReplacementTransform(L4[1], lhs), FadeOut(VGroup(L4[0], L4[2])), at=t_inside, dur=1.0)
    m.play(FadeIn(M.br), at=t_inside + 0.5, dur=0.7)
    m.play(Write(M.cell(0, 0)), Write(M.cell(1, 1)), at=t_diag, dur=0.9)

    def flash(mob, at, color=C.spread):
        r = SurroundingRectangle(mob, color=color, stroke_width=2.2, buff=0.08)
        m.play(FadeIn(r), at=at, dur=0.3)
        m.play(FadeOut(r), at=at + 1.0, dur=0.4)

    flash(M.cell(0, 0), t_sh_h)
    flash(M.cell(1, 1), t_sh_a)
    slots = VGroup(*[DashedVMobject(SurroundingRectangle(M.cell(i, j), buff=0.1, stroke_width=2.0, color=C.spread),
                                    num_dashes=18) for i, j in ((0, 1), (1, 0))])
    m.play(Create(slots), at=t_off + 0.4, dur=0.8)
    eq = Eqn(r"\sigma_{ha} = \tfrac{1}{n}\sum_i \tilde h_i\,\tilde a_i", colors={r"\sigma_{ha}": C.spread}, size=44)
    eq.scale(min(1.0, 3.5 / eq.width)).move_to(P3(MX, -0.75))
    m.play(Write(eq), at=t_each, dur=1.4)

    # ---- the deviation rectangles, signed
    rm = s.manim(z=1)

    def rect(x, y, col, op=0.08):
        return Polygon(p(0, 0), p(x, 0), p(x, y), p(0, y), stroke_color=col, stroke_width=1.1, stroke_opacity=0.75,
                       fill_color=col, fill_opacity=op)

    prod = Xc[:, 0] * Xc[:, 1]
    J = int(np.argmax(prod))
    first = rect(*Xc[J], C.spread, 0.2)
    rm.play(Create(first), at=t_mul, dur=0.9)
    ur = [i for i in range(len(Xc)) if Xc[i, 0] > 0 and Xc[i, 1] > 0 and i != J]
    ll = [i for i in range(len(Xc)) if Xc[i, 0] < 0 and Xc[i, 1] < 0]
    mx = [i for i in range(len(Xc)) if prod[i] < 0]
    groups = []
    for idx, at, col in ((ur, t_tall, C.spread), (ll, t_short, C.spread), (mx, t_mixed, C.residual)):
        g = VGroup(*[rect(*Xc[i], col) for i in sorted(idx, key=lambda i: -abs(prod[i]))])
        rm.play(LaggedStart(*[FadeIn(r_) for r_ in g], lag_ratio=0.06), at=at, dur=1.3)
        groups.append(g)
    signs = VGroup(backed(tex("+", 44, C.spread)).move_to(p(22, 26)), backed(tex("+", 44, C.spread)).move_to(p(-22, -26)),
                   backed(tex("-", 44, C.residual)).move_to(p(22, -26)), backed(tex("-", 44, C.residual)).move_to(p(-22, 26)))
    rm.play(FadeIn(signs[0]), at=t_tall + 0.5, dur=0.5)
    rm.play(FadeIn(signs[1]), at=t_short + 0.5, dur=0.5)
    rm.play(FadeIn(VGroup(signs[2], signs[3])), at=t_mixed + 0.5, dur=0.5)

    # ---- the average: one square of area 58.4 cm^2; it becomes both off-diagonal entries
    allr = VGroup(first, *groups)
    rm.play(allr.animate.set_fill(opacity=0.02).set_stroke(opacity=0.25), at=t_avg, dur=0.7)
    side = math.sqrt(cov)
    sq = Polygon(p(0, 0), p(side, 0), p(side, side), p(0, side), stroke_color=C.spread, stroke_width=3.5,
                 fill_color=C.spread, fill_opacity=0.35)
    rm.play(GrowFromPoint(sq, p(0, 0)), at=t_avg + 0.4, dur=0.8)
    c1, c2 = sq.copy(), sq.copy()
    m.add(c1, c2, at=t_avg + 1.9)
    m.play(ReplacementTransform(c1, M.cell(0, 1)), ReplacementTransform(c2, M.cell(1, 0)), FadeOut(slots),
           at=t_avg + 2.0, dur=1.1)

    # ---- symmetric: a mirror line and the two entries swap; pin to rail slot 1
    mir = DashedLine(M.cell(0, 0).get_center() + P3(-0.35, 0.3), M.cell(1, 1).get_center() + P3(0.35, -0.3),
                     stroke_color=C.muted, stroke_width=2, dash_length=0.08)
    m.play(Create(mir), at=t_sym, dur=0.6)
    m.play(CyclicReplace(M.cell(0, 1), M.cell(1, 0), path_arc=math.pi / 2), at=t_sym + 0.8, dur=1.0)
    m.play(FadeOut(mir), at=t_sym + 2.0, dur=0.4)
    m.play(FadeOut(eq), at=t_pin - 0.3, dur=0.5)
    rm.play(FadeOut(VGroup(allr, sq, signs)), at=t_pin, dur=0.7)
    m.play(FadeIn(board(slot(0))), at=t_pin, dur=0.6)
    G2 = c_matrix(44)
    G2.scale(min(1.0, 3.4 / G2.width)).move_to(P3(MX, 1.2))
    for part in (lhs, M.br, M.cell(0, 0), M.cell(0, 1), M.cell(1, 0), M.cell(1, 1)):
        m.remove(part, at=t_pin - 0.02)
    m.add(G2, at=t_pin - 0.02)
    m.play(ReplacementTransform(G2, rail_c_parts()), at=t_pin, dur=1.0)
