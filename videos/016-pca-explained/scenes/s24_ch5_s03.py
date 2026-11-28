"""ch5_s03 · Rebuilding a digit (L2, rail: B_recipe, B_scree).

The scree pins into rail slot 1. On 'draw it as an image' the first four principal components appear as 8x8 tiles
(C.spread +, C.data -). On 'average digit' the mean digit joins them: μ + z1 v1 + z2 v2 + ... Below, the video's 3
is rebuilt: it starts as the average, and on 'one at a time' the patterns are added largest first (k counts up; the
pattern being added is outlined while k <= 4). k = 3 'a blur', k = 10 'you can read it', k = 20, and the original
appears beside it. On 'lose very little': 64 -> 20.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (DIGIT_I, P3, STAGE_L2, backed, board, div_tiles, grey_tiles, rail_recipe, rail_scree, sans, scree,
                 slot, tex)

SB = (-5.7, -2.35, 1.75, 2.15)                    # as in ch5_s02
TS, TY = 0.95, 1.95                               # the pattern row
BS, BY = 2.5, -1.35                               # the rebuilt digit and the original
RX, OX = -3.75, 0.35


@scene(T.ch5_s03, T.ch5_s04)
def ch5_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_img, t_avg, t_one = float(T.ch5_s03_draw_it_as_an_image), float(T.ch5_s03_average_digit), float(T.ch5_s03_one_at_a_time)
    t_blur, t_ten, t_20, t_lose = float(T.ch5_s03_blur), float(T.ch5_s03_with_ten), float(T.ch5_s03_with_twenty), float(T.ch5_s03_lose_very_little)
    t_start = t_one - 2.4                         # 'Start from the average'
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))
    D = pd.digits_pca()
    X, _ = pd.digits()
    x = X[DIGIT_I]

    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_recipe())
    m = s.manim(z=2, opacity=end)

    # ---- the scree pins into rail slot 1
    sc = scree(SB)
    m.add(sc)
    m.play(ReplacementTransform(sc, rail_scree()[1]), at=t0 + 0.1, dur=1.1)
    s.manim(z=0.4).play(FadeIn(board(slot(1))), at=t0 + 0.4, dur=0.6)

    # ---- the pattern row: μ + z1 v1 + z2 v2 + z3 v3 + z4 v4 + ...
    mu_t = VGroup(*grey_tiles(D.mu, TS))
    vs = [div_tiles(D.V[:, k], TS) for k in range(4)]
    ops = [MathTex("+", font_size=40)] + [MathTex(rf"+\,z_{k + 2}", font_size=36) for k in range(3)] + [MathTex(r"+\;\cdots", font_size=40)]
    z1 = MathTex(r"z_1", font_size=36)
    row = VGroup(mu_t, ops[0], z1, vs[0], ops[1], vs[1], ops[2], vs[2], ops[3], vs[3], ops[4]).arrange(RIGHT, buff=0.14)
    row.scale(min(1.0, 8.1 / row.width)).move_to(P3(-2.05, TY))
    vlab = VGroup(*[MathTex(rf"v_{k + 1}", font_size=32, color=C.muted).next_to(vs[k], DOWN, buff=0.1) for k in range(4)])
    mlab = MathTex(r"\mu", font_size=34, color=C.mean).next_to(mu_t, DOWN, buff=0.1)
    m.play(LaggedStart(*[FadeIn(v, shift=DOWN * 0.1) for v in vs], lag_ratio=0.25), FadeIn(vlab), at=t_img - 0.2, dur=1.4)
    m.play(FadeIn(VGroup(mu_t, mlab), shift=RIGHT * 0.1), at=t_avg, dur=0.7)
    m.play(LaggedStart(*[FadeIn(o) for o in (ops[0], z1, *ops[1:])], lag_ratio=0.12), at=t_avg + 1.2, dur=1.2)

    # ---- rebuilding the 3, one pattern at a time
    kk = keys((t0, 0.0), (t_one + 0.3, 0.0), (t_one + 3.6, 3.99, "linear"), (t_ten - 0.3, 3.99),
              (t_ten + 0.4, 10.0, "linear"), (t_20 - 0.3, 10.0), (t_20 + 0.5, 20.0, "linear"))
    rec_on = keys((t0, 0.0), (t_start - 0.2, 0.0), (t_start + 0.6, 1.0))

    def k_at(t):
        return int(float(kk(t)))

    def rebuilt(t):
        a = float(rec_on(t))
        if a <= 0.001:
            return VGroup()
        k = k_at(t)
        r = np.clip(D.reconstruct(x, k), 0, 16)
        cells, fr = grey_tiles(r, BS)
        g = VGroup(cells, fr).move_to(P3(RX, BY))
        cells.set_opacity(a)
        fr.set_stroke(opacity=a)
        g.add(MathTex(rf"k = {k}", font_size=42).set_opacity(a).next_to(fr, RIGHT, buff=0.45))
        if 1 <= k <= 4:
            g.add(SurroundingRectangle(vs[k - 1], color=C.pc1, stroke_width=2.6, buff=0.05))
        return g

    rm = s.manim(z=2.1, opacity=end)
    rm.redraw(rebuilt, during=(t_start - 0.3, t1))
    oc, ofr = grey_tiles(x, BS)
    orig = VGroup(oc, ofr).move_to(P3(OX + 0.45, BY))
    olab = sans("original", 26, C.muted).next_to(orig, UP, buff=0.12)
    rlab = sans("rebuilt", 26, C.muted).move_to(P3(RX, BY + BS / 2 + 0.24))
    m.play(FadeIn(rlab), at=t_start + 0.4, dur=0.5)
    m.play(FadeIn(VGroup(orig, olab), shift=LEFT * 0.1), at=t_20 + 0.6, dur=0.7)
    e = backed(Eqn(r"64 \;\to\; 20", size=42), 0.08).move_to(P3(OX + 0.45, BY - BS / 2 - 0.32))
    m.play(Write(e), at=t_lose - 0.2, dur=0.9)
