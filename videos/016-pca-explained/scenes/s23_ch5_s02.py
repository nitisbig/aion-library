"""ch5_s02 · How much we keep (L2, rail: B_recipe, then B_scree pins into slot 1).

The people's three eigenvalues stand as bars (gold, teal, violet). On 'add up to the total' they stack into one bar:
λ1 + λ2 + λ3 = total variance. On 'share' each part gets its share (86.8 %, 11.3 %, 1.8 %). Then the digits: 64
share bars (C.spread) and the cumulative 'kept' curve (C.pc1). On 'first two directions' the first two bars and
the curve at k = 2 (28.5 %); on 'nine tenths' the 90 % line meets the curve at k = 21; on 'nothing at all' the last
three bars are empty (0), and on 'every scan' a small tile marks the three always-blank pixels. The notes clear; ch5_s03
pins the scree into rail slot 1.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (P3, STAGE_L2, backed, board, grey_tiles, rail_recipe, rail_scree, sans, scree, scree_geom, slot,
                 tex, DIGIT_I)

SB = (-5.7, -2.35, 1.75, 2.15)                    # the scree on the stage
BX, BW, BASE, BH = (-5.1, -4.25, -3.4), 0.55, -2.35, 3.9


@scene(T.ch5_s02, T.ch5_s03)
def ch5_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_eig, t_tot, t_share = float(T.ch5_s02_eigenvalues), float(T.ch5_s02_add_up_to_the_total), float(T.ch5_s02_share)
    t_first, t_ninety, t_zero, t_scan = float(T.ch5_s02_first_two_directions), float(T.ch5_s02_nine_tenths), float(T.ch5_s02_nothing_at_all), float(T.ch5_s02_every_scan)
    t_dig = t_first - 2.2                         # 'For the digits'
    Q = pd.people3()
    D = pd.digits_pca()
    lam = Q.lam
    cols = (C.pc1, C.pc2, C.pc3)

    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_recipe())
    m = s.manim(z=2)

    # ---- the people: three eigenvalues, then their total
    bars = VGroup(*[Rectangle(width=BW, height=float(l / lam[0]) * BH, stroke_width=0, fill_color=c, fill_opacity=0.9)
                    .move_to(P3(x, BASE + float(l / lam[0]) * BH / 2)) for x, l, c in zip(BX, lam, cols)])
    labs = VGroup(*[MathTex(rf"\lambda_{k + 1}", font_size=38, color=c).move_to(P3(x, BASE - 0.32))
                    for k, (x, c) in enumerate(zip(BX, cols))])
    base = Line(P3(-5.6, BASE), P3(-1.2, BASE), stroke_color=C.axis, stroke_width=2)
    m.play(Create(base), at=t0 + 0.3, dur=0.6)
    m.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.3), FadeIn(labs), at=t_eig, dur=1.2)
    tot = float(lam.sum())
    hs = [float(l / tot) * BH for l in lam]
    TX = -2.0
    stack, y = VGroup(), BASE
    for h, c in zip(hs, cols):
        stack.add(Rectangle(width=BW, height=h, stroke_width=0, fill_color=c, fill_opacity=0.9).move_to(P3(TX, y + h / 2)))
        y += h
    m.play(*[ReplacementTransform(bars[k].copy(), stack[k]) for k in range(3)], at=t_tot, dur=1.2)
    m.play(FadeOut(VGroup(bars, labs)), at=t_tot + 0.4, dur=0.8)
    e1 = backed(Eqn(r"\lambda_1+\lambda_2+\lambda_3 = \textsf{total variance}",
                    colors={r"\lambda_1": C.pc1, r"\lambda_2": C.pc2, r"\lambda_3": C.pc3}, size=40), 0.08)
    e1.move_to(P3(-2.1, 2.55))
    m.play(Write(e1), at=t_tot + 0.2, dur=1.2)
    pct = VGroup()
    y = BASE
    for k, (h, c) in enumerate(zip(hs, cols)):
        yy = y + h / 2 if k < 2 else y + h + 0.12
        pct.add(tex(rf"{100 * Q.share[k]:.1f}\,\%", 36, c).move_to(P3(TX + 0.55, yy), aligned_edge=LEFT))
        y += h
    pct[2].shift(UP * 0.12)
    m.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.1) for p in pct], lag_ratio=0.3), at=t_share, dur=1.2)
    m.play(FadeOut(VGroup(stack, pct, e1, base)), at=t_dig - 0.5, dur=0.6)

    # ---- the digits: the scree and the kept curve
    sc = scree(SB)
    sbase, sbars, curve = sc
    w, hb, hc = scree_geom(SB)
    m.play(Create(sbase), at=t_dig - 0.1, dur=0.5)
    m.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in sbars], lag_ratio=0.03), at=t_dig + 0.1, dur=1.4)
    m.play(Create(curve), at=t_dig + 1.0, dur=1.4)
    tg = VGroup(sans("share", 26, C.spread).move_to(P3(SB[0] + 2.7, SB[1] + 0.6)),
                sans("kept", 26, C.pc1).move_to(P3(SB[0] + 13 * w, SB[1] + hc + 0.05)))
    m.play(FadeIn(tg), at=t_dig + 1.6, dur=0.6)

    def on_curve(k):
        return P3(SB[0] + k * w, SB[1] + float(np.cumsum(D.share)[k - 1]) * hc)

    two = VGroup(SurroundingRectangle(VGroup(sbars[0], sbars[1]), color=C.pc1, stroke_width=2.2, buff=0.05),
                 Dot(on_curve(2), radius=0.08, color=C.pc1),
                 backed(tex(rf"{100 * D.share[:2].sum():.1f}\,\%", 38, C.pc1), 0.05).next_to(on_curve(2), RIGHT, buff=0.15))
    m.play(Create(two[0]), at=t_first, dur=0.5)
    m.play(FadeIn(VGroup(two[1], two[2])), at=t_first + 0.6, dur=0.6)
    k90 = pd.k_for(D.share, 0.9)
    y90 = SB[1] + 0.9 * hc
    ninety = VGroup(DashedLine(P3(SB[0], y90), P3(SB[2], y90), stroke_color=C.muted, stroke_width=1.8, dash_length=0.08),
                    tex(r"90\,\%", 32, C.muted).move_to(P3(SB[2] - 0.35, y90 + 0.25)),
                    DashedLine(on_curve(k90), P3(SB[0] + k90 * w, SB[1]), stroke_color=C.pc1, stroke_width=1.8,
                               dash_length=0.08),
                    Dot(on_curve(k90), radius=0.08, color=C.pc1),
                    backed(tex(str(k90), 38, C.pc1), 0.05).move_to(P3(SB[0] + k90 * w, SB[1] - 0.3)))
    m.play(FadeOut(two[0]), at=t_ninety - 0.6, dur=0.4)
    m.play(Create(ninety[0]), FadeIn(ninety[1]), at=t_ninety - 0.3, dur=0.6)
    m.play(Create(ninety[2]), FadeIn(VGroup(ninety[3], ninety[4])), at=t_ninety + 0.3, dur=0.7)
    zeros = VGroup(*[Rectangle(width=w * 0.72, height=0.32, stroke_color=C.muted, stroke_width=1.4)
                     .move_to(P3(SB[0] + (k + 0.5) * w, SB[1] + 0.16)) for k in (61, 62, 63)])
    zl = tex("0", 34, C.muted).move_to(P3(SB[0] + 62.5 * w, SB[1] + 0.6))
    m.play(Create(zeros), FadeIn(zl), at=t_zero + 0.4, dur=0.6)
    X, _ = pd.digits()
    cells, fr = grey_tiles(X[DIGIT_I], 1.1)
    tile = VGroup(cells, fr).move_to(P3(SB[2] - 0.7, SB[1] + 1.6))
    marks = VGroup()
    for i in (0, 32, 39):
        r, c = divmod(i, 8)
        p = tile.get_center() + P3((c - 3.5) * 1.1 / 8, (3.5 - r) * 1.1 / 8)
        marks.add(Square(side_length=1.1 / 8, stroke_color=C.muted, stroke_width=2.2).move_to(p))
    m.play(FadeIn(tile), at=t_scan - 0.3, dur=0.5)
    m.play(Create(marks), at=t_scan + 0.2, dur=0.5)

    # ---- the notes clear; the scree stays (ch5_s03 pins it into rail slot 1)
    m.play(FadeOut(VGroup(tg, two[1], two[2], ninety, zeros, zl, tile, marks)), at=t1 - 0.6, dur=0.5)
