"""ch3_s01 · From a sum to a matrix (L2, rail: -, B_varu, B_dial).

Chapter card (carry-over strip: the dial). On 'sixty-four' a 64-spoke star of directions turns and flickers on the
stage, then greys: far too many to try. The objective's sum flies out of the rail onto the stage, beside the
centred cloud, and rewrites line by line: each square becomes u^T x~ x~^T u, the u's move outside the sum, the
middle is boxed (C.spread) and collapses into the single symbol C: u^T C u. On 'never need' the points fade to 20%.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (P3, STAGE_L2, board, chapter_card, dial_pinned, dots, rail_obj, rail_obj_parts, slot, tex)

CC = np.array([-3.85, -0.1])                    # the cloud's centre on the stage (as in ch3_s02's plane)
KC = 0.092
EQ_X, EQ_Y, EQ_W = 0.32, 0.35, 3.75             # the equation column on the right of the stage


def fit(mob, w=EQ_W):
    return mob.scale(min(1.0, w / mob.width)).move_to(P3(EQ_X, EQ_Y))


@scene(T.ch3_s01, T.ch3_s02)
def ch3_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t64, t_var, t_prod = float(T.ch3_s01_sixty_four), float(T.ch3_s01_variance_along_an_ar), float(T.ch3_s01_small_matrix_product)
    t_reg, t_mid, t_cov, t_never = float(T.ch3_s01_regroup), float(T.ch3_s01_the_middle), float(T.ch3_s01_covariance_matrix), float(T.ch3_s01_never_need)
    t_out = t_reg + 1.6                          # 'The arrow moves to the outside'
    t_single = t_mid + 3.2                       # 'a single matrix'
    P = pd.people2()
    Xc = P.Xc

    # ---- card; strip = the dial
    on = chapter_card(s, t0, t0 + 2.6, "chapter three", "The Covariance Matrix")
    strip = s.manim(z=20, opacity=on * 0.5)
    strip.add(dial_pinned().move_to(P3(0, -2.35)))

    # ---- the stage and the rail (slot 1 empty for now)
    back = keys((t0, 0.0), (t0 + 2.2, 0.0), (t0 + 3.0, 1.0))
    st = s.manim(z=0, opacity=back)
    st.add(board(STAGE_L2), rail_obj(), dial_pinned())

    # ---- 'sixty-four': a star of 64 directions turns, flickers and greys
    rng = np.random.default_rng(1604)
    dirs = rng.normal(size=(64, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    lens = rng.uniform(0.8, 1.0, 64) * 2.4
    ph = rng.uniform(0, 2 * math.pi, 64)
    st_on = keys((t0, 0.0), (t64 - 0.3, 0.0), (t64 + 0.6, 1.0), (t_var - 2.4, 1.0), (t_var - 1.6, 0.0))
    grey_ = keys((t0, 0.0), (t64 + 2.0, 0.0), (t64 + 3.0, 1.0))
    sc = np.array([(STAGE_L2[0] + STAGE_L2[2]) / 2, 0.0])

    def star(t):
        a = float(st_on(t))
        if a <= 0.001:
            return VGroup()
        ang = 0.35 * (t - t64)
        ca, sa = math.cos(ang), math.sin(ang)
        R = np.array([[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]]) @ np.array([[1, 0, 0], [0, math.cos(0.4), -math.sin(0.4)], [0, math.sin(0.4), math.cos(0.4)]])
        q = (dirs * lens[:, None]) @ R.T
        gy = float(grey_(t))
        g = VGroup()
        for j in range(64):
            fl = 0.55 + 0.45 * math.sin(7.0 * t + ph[j])
            op = a * ((1 - gy) * (0.35 + 0.65 * fl) + gy * 0.22) * (0.6 + 0.4 * (q[j, 2] / 2.4 + 1) / 2)
            g.add(Line(P3(*sc), P3(sc[0] + q[j, 0], sc[1] + q[j, 1]), stroke_color=C.axis if gy < 0.5 else C.muted,
                       stroke_width=1.6, stroke_opacity=op))
        return g

    sm = s.manim(z=1)
    sm.redraw(star, during=(t64 - 0.4, t_var - 1.5))

    # ---- the cloud on the left of the stage
    cl = s.manim(z=1, opacity=keys((t0, 0.0), (t_var - 1.2, 0.0), (t_var - 0.4, 1.0), (t_never - 0.1, 1.0),
                                    (t_never + 0.8, 0.2)))
    cl.add(dots([P3(*(CC + KC * p)) for p in Xc], C.data))

    # ---- the rewrite chain (TransformMatchingTex on named parts)
    S, Q = r"\tfrac{1}{n}\sum_i", r"\left(\tilde x_i\cdot u\right)^2"
    L1 = fit(MathTex(S, Q, font_size=48))
    L2 = fit(MathTex(S, r"u^\top", r"\tilde x_i\,\tilde x_i^\top", r"u", font_size=48))
    L3 = fit(MathTex(r"u^\top", r"\Big(", S, r"\tilde x_i\,\tilde x_i^\top", r"\Big)", r"u", font_size=48))
    L4 = fit(MathTex(r"u^\top", r"C", r"\,u", font_size=60))
    L4[1].set_color(C.spread)
    m = s.manim(z=2)
    src = rail_obj_parts()
    m.add(src, at=t_var - 0.35)
    m.play(ReplacementTransform(src, L1), at=t_var, dur=1.1)
    m.play(TransformMatchingTex(L1, L2), at=t_prod, dur=1.2)
    m.play(TransformMatchingTex(L2, L3, key_map={}), at=t_out, dur=1.4)
    box = SurroundingRectangle(VGroup(L3[1], L3[2], L3[3], L3[4]), color=C.spread, stroke_width=2.2, buff=0.08,
                               fill_color=C.spread, fill_opacity=0.07)
    m.play(Create(box), at=t_mid, dur=0.8)
    m.play(FadeOut(box), FadeTransform(VGroup(L3[1], L3[2], L3[3], L3[4]), L4[1]),
           ReplacementTransform(L3[0], L4[0]), ReplacementTransform(L3[5], L4[2]), at=t_single, dur=1.2)
    m.play(Indicate(L4[1], color=C.spread, scale_factor=1.2), at=t_cov, dur=1.0)
