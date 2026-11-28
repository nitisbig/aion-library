"""ch5_s04 · The map, explained (L1).

The stage and rail clear and the digit map from the intro returns (1,797 points, ten class hues). On 'two axes' its
axes draw through the origin, PC1 (gold) and PC2 (teal), each with its eigen-digit at the end. On 'each pattern' the
video's 3 is singled out: its drops onto both axes give z1 and z2, its image beside it. On 'share strokes' the class
numerals appear. On 'In practice' the map dims and X = U Σ V^T writes; on 'singular value decomposition' its name;
on 'same directions' V^T is boxed and λ_k = σ_k² / n. On 'greatest spread' the map returns and the axes glow.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (DIGIT_I, P3, STAGE_L2, backed, board, digit_map, digit_map_xy, div_tiles, glow_layer, grey_tiles,
                 rail_recipe, rail_scree, sans, tex)

MB = (-5.5, -2.9, 2.9, 2.75)                      # the map's box
TS = 0.95


@scene(T.ch5_s04, T.ch6_s01)
def ch5_s04(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_map, t_ax, t_pat = float(T.ch5_s04_map_from_the_beginni), float(T.ch5_s04_two_axes), float(T.ch5_s04_each_pattern)
    t_str, t_prac, t_svd = float(T.ch5_s04_share_strokes), float(T.ch5_s04_in_practice), float(T.ch5_s04_singular_value_decom)
    t_same, t_great = float(T.ch5_s04_same_directions), float(T.ch5_s04_greatest_spread)
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))
    D = pd.digits_pca()
    X, y = pd.digits()

    # ---- the rail and stage clear
    old = s.manim(z=0, opacity=keys((t0, 1.0), (t0 + 0.1, 1.0), (t0 + 0.8, 0.0)))
    old.add(board(STAGE_L2), rail_recipe(), rail_scree())

    # ---- the map (the same placement as the intro's)
    dim = keys((t0, 0.0), (t0 + 0.4, 0.0), (t0 + 1.4, 1.0), (t_prac - 0.1, 1.0), (t_prac + 0.8, 0.22),
               (t_great - 0.4, 0.22), (t_great + 0.6, 1.0))
    xy, _ = digit_map(s, MB, dim * end, z=1, size=3.4, start=t0)
    Z = D.Z[:, :2] * np.array([1, -1])
    k = min((MB[2] - MB[0]) / np.ptp(Z[:, 0]), (MB[3] - MB[1]) / np.ptp(Z[:, 1]))
    mc = np.array([(MB[0] + MB[2]) / 2, (MB[3] + MB[1]) / 2])
    O = mc - k * (Z.max(0) + Z.min(0)) / 2          # where the mean digit sits (z = 0)

    # ---- the axes and their patterns
    m = s.manim(z=2, opacity=end)
    ax1 = Line(P3(MB[0], O[1]), P3(MB[2] + 0.1, O[1]), stroke_color=C.pc1, stroke_width=3)
    ax2 = Line(P3(O[0], MB[1]), P3(O[0], MB[3]), stroke_color=C.pc2, stroke_width=3)
    v1t = div_tiles(D.V[:, 0], TS).move_to(P3(MB[2] + 0.75, O[1]))
    v2t = div_tiles(-D.V[:, 1], TS).move_to(P3(O[0] + 0.85, MB[3] - 0.45))   # up the page is -PC2 (as in the intro)
    n1 = sans("PC1", 28, C.pc1).next_to(v1t, DOWN, buff=0.12)
    n2 = sans("PC2", 28, C.pc2).next_to(v2t, RIGHT, buff=0.15)
    m.play(Create(ax1), at=t_ax - 0.1, dur=0.8)
    m.play(Create(ax2), at=t_ax + 0.4, dur=0.8)
    m.play(FadeIn(VGroup(v1t, n1), shift=LEFT * 0.1), at=t_ax + 1.0, dur=0.6)
    m.play(FadeIn(VGroup(v2t, n2), shift=DOWN * 0.1), at=t_ax + 1.6, dur=0.6)

    # ---- one digit: how much of each pattern it contains
    p = xy[DIGIT_I]
    ring = Circle(radius=0.12, stroke_color=C.text, stroke_width=2.6).move_to(P3(*p))
    drops = VGroup(DashedLine(P3(*p), P3(p[0], O[1]), stroke_color=C.pc1, stroke_width=2, dash_length=0.07),
                   DashedLine(P3(*p), P3(O[0], p[1]), stroke_color=C.pc2, stroke_width=2, dash_length=0.07))
    zl = VGroup(backed(MathTex(r"z_1", font_size=36, color=C.pc1), 0.04).move_to(P3(p[0], O[1] - 0.3)),
                backed(MathTex(r"z_2", font_size=36, color=C.pc2), 0.04).move_to(P3(O[0] - 0.32, p[1])))
    cells, fr = grey_tiles(X[DIGIT_I], 0.9)
    me = VGroup(cells, fr).move_to(P3(p[0] + 0.85 * np.sign(p[0] - O[0] or 1), p[1] + 0.55))
    m.play(Create(ring), at=t_pat - 1.2, dur=0.5)
    m.play(FadeIn(me), at=t_pat - 0.8, dur=0.6)
    m.play(Create(drops), at=t_pat - 0.1, dur=0.8)
    m.play(FadeIn(zl), at=t_pat + 0.5, dur=0.6)
    one = VGroup(ring, drops, zl, me)
    m.play(FadeOut(one), at=t_str - 0.4, dur=0.5)

    # ---- digits that share strokes land together: the class numerals
    for d in range(10):
        cen = np.median(xy[y == d], 0)
        disc = VGroup(Circle(radius=0.25, stroke_color=getattr(C, f"d{d}"), stroke_width=2.2, fill_color=C.bg,
                             fill_opacity=1.0), tex(str(d), 40, getattr(C, f"d{d}"))).move_to(P3(*cen))
        m.play(FadeIn(disc, scale=0.8), at=t_str + 0.1 + 0.12 * d, dur=0.5)
        m.play(FadeOut(disc), at=t_prac - 0.2, dur=0.5)

    # ---- in practice: the SVD
    e = MathTex(r"X", "=", r"U", r"\,\Sigma\,", r"V^\top", font_size=72)
    e[3].set_color(C.spread)
    eb = backed(e, 0.14).move_to(P3(-1.3, 0.55))
    m.play(Write(eb), at=t_prac + 0.6, dur=1.4)
    name = backed(sans("singular value decomposition", 32, C.muted), 0.06).next_to(eb, DOWN, buff=0.2)
    m.play(FadeIn(name), at=t_svd - 0.1, dur=0.7)
    bx = SurroundingRectangle(e[4], color=C.pc1, stroke_width=2.6, buff=0.08)
    m.play(Create(bx), at=t_same, dur=0.5)
    lam = backed(Eqn(r"\lambda_k = \sigma_k^2 / n", colors={r"\lambda_k": C.spread, r"\sigma_k": C.spread}, size=50),
                 0.08).next_to(name, DOWN, buff=0.3)
    m.play(FadeIn(lam, shift=DOWN * 0.1), at=t_same + 0.8, dur=0.7)
    m.play(FadeOut(VGroup(eb, name, bx, lam)), at=t_great - 0.6, dur=0.6)
    for ax, col in ((ax1, C.pc1), (ax2, C.pc2)):
        gl = glow_layer(s, z=1.9, color=col, k=0.7, opacity=end * keys((t0, 0.0), (t_great - 0.1, 0.0),
                                                                         (t_great + 0.6, 1.0)))
        gl.add(ax.copy())
