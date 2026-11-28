"""ch4_s04 · The recipe (L1 board; at the end B_recipe pins into rail slot 0).

The stage clears. A board assembles the method, one numbered key word and its equation per beat: centre, covariance
(the matrix flies out of the rail and becomes its definition), eigenvectors, sort, project. On 'No searching' a gold
rule runs down the steps. Three badges on 'two columns / sixty-four / ten thousand': the people cloud, the digit,
a field of 10,000 dots. The steps then fold into rail slot 0, where they stay through chapter five.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, DIGIT_I, EIG_R, P3, STAGE_L2, backed, board, cen_grid, eig_shape, eig_transform, eq_vlv,
                 glow_layer, grey_tiles, panel, rail_c_parts, rail_heat, rail_obj, rail_recipe_parts, recipe_rows,
                 slot, tex)

RB = (-4.6, -2.08, 4.6, 2.9)                    # the recipe board
X0R, TOP, DY = -4.05, 2.35, 0.99


@scene(T.ch4_s04, T.ch5_s01)
def ch4_s04(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_cen, t_cov, t_eig = float(T.ch4_s04_centre_the_data), float(T.ch4_s04_covariance_matrix), float(T.ch4_s04_eigenvectors)
    t_sort, t_sh, t_ten = float(T.ch4_s04_sort), float(T.ch4_s04_shadows_on_the_top_f), float(T.ch4_s04_ten_thousand)
    t_proj = t_sh - 2.6                           # 'Then describe every point'
    t_no = t_sh + 1.4                             # 'No searching, no guessing.'
    t_two, t_64 = t_ten - 3.0, t_ten - 1.7
    t_pin = t_ten + 0.5

    # ---- the end of ch4_s03 clears, with the rail (B_C stays until its matrix is needed)
    out = keys((t0, 1.0), (t0 + 0.2, 1.0), (t0 + 1.0, 0.0))
    old = s.manim(z=0, opacity=out)
    sh = eig_shape(eig_transform(1, 1, 1), CEN0, EIG_R)
    sh[0].set_stroke(color=C.spread)
    old.add(board(STAGE_L2), cen_grid(), sh, backed(eq_vlv(54), 0.1).move_to(P3(-1.85, -2.62)), rail_obj())
    rail_heat(s, z=0.5, opacity=out, during=[(t0, t0 + 1.1)])
    bc = s.manim(z=0, opacity=keys((t0, 1.0), (t_cov - 0.1, 1.0), (t_cov + 0.6, 0.0)))
    bc.add(board(slot(0)))

    # ---- the recipe board
    rb = s.manim(z=0.5, opacity=keys((t0, 0.0), (t0 + 0.8, 0.0), (t0 + 1.5, 1.0), (t_pin, 1.0), (t_pin + 0.6, 0.0)))
    rb.add(panel(*RB))
    m = s.manim(z=2)
    rows = recipe_rows(size=46, word=34, w_col=2.95, eq_col=4.6, top=TOP, dy=DY, x0=X0R)
    src = rail_c_parts()
    m.add(src)
    for k, at in enumerate((t_cen, t_cov, t_eig, t_sort, t_proj)):
        n, w, e = rows[k]
        m.play(FadeIn(VGroup(n, w), shift=RIGHT * 0.1), at=at - 0.15, dur=0.6)
        if k == 1:
            m.play(FadeTransform(src, e), at=at + 0.1, dur=1.1)
        else:
            m.play(Write(e), at=at + 0.2, dur=0.9)

    # ---- no searching, no guessing: a gold rule down the steps
    rule = Line(P3(X0R - 0.38, TOP + 0.32), P3(X0R - 0.38, TOP - 4 * DY - 0.32), stroke_color=C.pc1, stroke_width=4)
    m.play(Create(rule), at=t_no, dur=1.0)
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.7, opacity=keys((t0, 0.0), (t_no + 0.8, 0.0), (t_no + 1.3, 1.0),
                                                                  (t_no + 2.4, 0.0)))
    gl.add(rule.copy())

    # ---- two columns, sixty-four, ten thousand
    P = pd.people2()
    X, _ = pd.digits()
    rng = np.random.default_rng(1604)
    bw, bh, by = 2.45, 0.8, -2.78
    badges = VGroup()
    for i, (lab, cx) in enumerate((("2", -3.0), ("64", 0.05), (r"10\,000", 3.1))):
        g = VGroup(panel(cx - bw / 2, by - bh / 2, cx + bw / 2, by + bh / 2))
        ic = np.array([cx - 0.55, by])
        if i == 0:
            g.add(*[Dot(P3(*(ic + 0.012 * q)), radius=0.02, color=C.data) for q in P.Xc])
        elif i == 1:
            cells, fr = grey_tiles(X[DIGIT_I], 0.62)
            g.add(VGroup(cells, fr).move_to(P3(*ic)))
        else:
            q = rng.normal(size=(600, 2)) * np.array([0.2, 0.1])
            q = q[(np.abs(q[:, 0]) < 0.45) & (np.abs(q[:, 1]) < 0.3)][:260]
            g.add(*[Dot(P3(*(ic + p)), radius=0.012, color=C.data, fill_opacity=0.7) for p in q])
        g.add(tex(lab, 40).move_to(P3(cx + 0.55, by)))
        badges.add(g)
    for b, at in zip(badges, (t_two, t_64, t_ten - 0.2)):
        m.play(FadeIn(b, shift=UP * 0.1), at=at, dur=0.6)

    # ---- fold the steps into rail slot 0
    rr = rail_recipe_parts()
    m.play(FadeOut(VGroup(badges, rule, *[r[2] for r in rows])), at=t_pin, dur=0.5)
    m.play(*[ReplacementTransform(VGroup(rows[k][0], rows[k][1]), rr[k]) for k in range(5)], at=t_pin + 0.1, dur=1.1)
    s.manim(z=0.4).play(FadeIn(board(slot(0))), at=t_pin + 0.4, dur=0.6)
