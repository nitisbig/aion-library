"""Ch3 · The columns are the whole story: an arrow is a recipe in i-hat and j-hat, a move keeps the recipe,
so where i-hat and j-hat land (the columns) decides everything, and matrix times vector is that recipe in numbers."""
from aion import *

from beats import T
from shots import (FRAME, GENTLE, I2, O3, U3, VEC, Mat, arrow, backdrop, backing, basis_arrows, finish, grid_lines,
                   live, pt, tex)

O, U = O3, U3
E = "smooth"


def hat_pos(M, j, t_off=0.42):
    """Label spot beside the tip of column j of M: off to the side away from the other arrow."""
    d = M[:, j] / max(np.linalg.norm(M[:, j]), 1e-9)
    side = np.array([d[1], -d[0]]) if j == 0 else np.array([-d[1], d[0]])
    return pt(O, U, M[:, j]) + np.array([*(t_off * side + 0.12 * d), 0])


@scene(T.cut_ch3, T.cut_read)
def s06_columns(s):
    backdrop(s)
    ghost = s.manim(z=0)                              # the grid before the move
    m = s.manim(z=1)                                  # the grid
    dots = s.manim(z=2)                               # "every single point"
    lo = s.manim(z=2.2)                               # our arrow, its recipe and the chain (dimmed later)
    dim = s.manim(z=2.5)                              # the dimmer: everything but the two arrows
    g = s.manim(z=3)                                  # i-hat, j-hat, and lit copies over the dimmer
    lab = s.manim(z=4)                                # hats
    hb = s.manim(z=4.9, parallax=0.0)                 # the panel behind the product (its own layer, always below)
    hud = s.manim(z=5, parallax=0.0)                  # the matrix and the product


    # ── the score: one move, landing as "the grid lines stay parallel" ──
    t0, t1 = T.apply + 0.55, T.apply + 2.55
    Mg = keys((t0, I2), (t1, GENTLE, E), lead=0)

    base = grid_lines(I2, O, U, FRAME)
    m.add(base)
    m.remove(base, at=t0)
    live(m, lambda t: grid_lines(Mg(t), O, U, FRAME), (t0, t1))
    ghost.add(grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False), at=t0)

    # ── two special arrows ──
    a0 = basis_arrows(I2, O, U)
    g.play(GrowArrow(a0[0]), at=T.one_right + 0.2, dur=0.8)
    g.play(GrowArrow(a0[1]), at=T.one_up + 0.25, dur=0.8)
    li = tex(r"\hat{\imath}", size=56, color=C.ihat).move_to(hat_pos(I2, 0))
    lj = tex(r"\hat{\jmath}", size=56, color=C.jhat).move_to(hat_pos(I2, 1))
    lab.play(FadeIn(li, shift=0.15 * UP), at=T.ihat + 0.3, dur=0.5, ease="out_back")
    lab.play(FadeIn(lj, shift=0.15 * RIGHT), at=T.jhat + 0.3, dur=0.5, ease="out_back")

    # ── our arrow is a recipe: two i-hats, then one j-hat, tip to tail ──
    def vec(M):
        return arrow(pt(O, U, (0, 0)), pt(O, U, M @ VEC), C.vec, width=C.stroke + 1)

    def chain(M, width=C.stroke - 0.5):
        i, j = M[:, 0], M[:, 1]
        return VGroup(arrow(pt(O, U, 0 * i), pt(O, U, i), C.ihat, width=width),
                      arrow(pt(O, U, i), pt(O, U, 2 * i), C.ihat, width=width),
                      arrow(pt(O, U, 2 * i), pt(O, U, 2 * i + j), C.jhat, width=width))

    def recipe(M):
        r = tex("2", r"\hat{\imath}", "+", "1", r"\hat{\jmath}", size=48,
                colors={0: C.vec, 1: C.ihat, 3: C.vec, 4: C.jhat})
        return r.move_to(pt(O, U, M @ VEC) + np.array([0.35 + r.width / 2, 0.05, 0]))

    v0, c0, r0 = vec(I2), chain(I2), recipe(I2)
    lo.play(GrowArrow(v0), at=T.our_arrow + 0.25, dur=0.8)
    lo.play(GrowArrow(c0[0]), at=T.recipe, dur=0.35)
    lo.play(GrowArrow(c0[1]), at=T.recipe + 0.3, dur=0.35)
    lo.play(GrowArrow(c0[2]), at=T.plus_one + 0.2, dur=0.4)
    lo.play(FadeIn(r0[:2], shift=0.1 * LEFT), at=T.recipe + 0.55, dur=0.5)
    lo.play(FadeIn(r0[2:], shift=0.1 * LEFT), at=T.plus_one + 0.45, dur=0.5)

    # ── apply a move: the grid, both arrows and our arrow ride together ──
    lo.play(FadeOut(c0), at=T.apply, dur=0.4)
    g.remove(a0[0], a0[1], at=t0)
    lo.remove(v0, *c0, r0, *r0, at=t0)
    mv = live(g, lambda t: basis_arrows(Mg(t), O, U), (t0, t1))
    mv += live(lo, lambda t: VGroup(vec(Mg(t)), recipe(Mg(t))), (t0, t1))
    a1, v1, r1, c1 = basis_arrows(GENTLE, O, U), vec(GENTLE), recipe(GENTLE), chain(GENTLE)
    g.remove(mv[0], at=t1)
    lo.remove(mv[1], at=t1)
    g.add(a1, at=t1)
    lo.add(v1, r1, at=t1)
    lab.drive(li, lambda mob, t: mob.move_to(hat_pos(Mg(t), 0)), during=(t0, t1))
    lab.drive(lj, lambda mob, t: mob.move_to(hat_pos(Mg(t), 1)), during=(t0, t1))

    # the recipe survives: the same chain, built from the new arrows
    lo.play(Indicate(r1, color=C.text, scale_factor=1.12), at=T.survives + 0.5, dur=0.9)
    lo.play(GrowArrow(c1[0]), at=T.new_i, dur=0.35)
    lo.play(GrowArrow(c1[1]), at=T.new_i + 0.3, dur=0.35)
    lo.play(GrowArrow(c1[2]), at=T.new_j + 0.3, dur=0.4)

    # ── every point follows; you only need two arrows ──
    pts = [pt(O, U, GENTLE @ np.array([i, j])) for i in range(-12, 13) for j in range(-12, 13)]
    pts = [p for p in pts if abs(p[0]) < 6.9 and abs(p[1]) < 3.8]
    pts.sort(key=lambda p: np.linalg.norm(p - pt(O, U, (0, 0))))
    field = VGroup(*[Dot(p, radius=0.055, color=C.text) for p in pts])
    dots.play(LaggedStart(*[FadeIn(d, scale=2.0) for d in field], lag_ratio=0.03), at=T.every_point + 0.6, dur=1.4)
    dimmer = Rectangle(width=16, height=10, stroke_width=0, fill_color=C.bg, fill_opacity=0.8)
    dim.play(FadeIn(dimmer), at=T.follow_two, dur=0.8)
    g.play(Indicate(a1[0], color=C.ihat, scale_factor=1.15), Indicate(a1[1], color=C.jhat, scale_factor=1.15),
           at=T.follow_two + 0.5, dur=0.8)

    # ── write down where they land: the landing spots become the columns ──
    M = Mat(GENTLE, size=44, h_buff=0.85, v_buff=0.72)
    V = Mat([[VEC[0]], [VEC[1]]], colors=[C.vec], size=44, v_buff=0.72)
    eq1, plus, eq2 = tex("="), tex("+"), tex("=")
    s1, s2 = tex(fmt_(VEC[0]), color=C.vec), tex(fmt_(VEC[1]), color=C.vec)
    k1 = Mat([[GENTLE[0, 0]], [GENTLE[1, 0]]], colors=[C.ihat], size=44, v_buff=0.72)
    k2 = Mat([[GENTLE[0, 1]], [GENTLE[1, 1]]], colors=[C.jhat], size=44, v_buff=0.72)
    out = GENTLE @ VEC
    R = Mat([[out[0]], [out[1]]], colors=[C.vec], size=44, v_buff=0.72)
    row = VGroup(M, V, eq1, VGroup(s1, k1).arrange(RIGHT, buff=0.08), plus, VGroup(s2, k2).arrange(RIGHT, buff=0.08),
                 eq2, R).arrange(RIGHT, buff=0.22)
    row.move_to([-7.11 + C.margin + 0.3 + row.width / 2, 2.3, 0])
    back = backing(M, pad=0.25)
    back_v = backing(VGroup(M, V), pad=0.25).align_to(back, LEFT)
    back_all = backing(row, pad=0.25)

    hb.play(FadeIn(back), at=T.write_down + 0.3, dur=0.5)
    hud.play(Create(M.br), at=T.write_down + 0.5, dur=0.7)
    for j, (beat, land) in enumerate(((T.where_i, T.first_col), (T.where_j, T.second_col))):
        c = GENTLE[:, j]
        col = (C.ihat, C.jhat)[j]
        tag = tex("(", fmt_(c[0]), ",", fmt_(c[1]), ")", size=40, colors={1: col, 3: col})
        tag.move_to(hat_pos(GENTLE, j, t_off=0.95))
        hud.play(FadeIn(tag, scale=0.8), at=beat + 0.35, dur=0.4)
        hud.play(ReplacementTransform(tag[1], M.cell(0, j)), ReplacementTransform(tag[3], M.cell(1, j)),
                 FadeOut(VGroup(tag[0], tag[2], tag[4])), at=land + 0.3, dur=0.8, ease=E)
    hud.play(Indicate(M, color=C.text, scale_factor=1.08), at=T.are_matrix + 0.6, dur=0.8)

    # ── matrix times vector is the recipe, written in numbers ──
    hb.play(Transform(back, back_v), at=T.mult + 0.5, dur=0.5)
    hud.play(FadeIn(V, shift=0.2 * LEFT), at=T.mult + 0.75, dur=0.6)
    hb.play(Transform(back, back_all), at=T.scale1, dur=0.5)
    hud.play(FadeIn(eq1), at=T.scale1, dur=0.5)
    hud.play(TransformFromCopy(M.cols[0], k1.cols[0]), FadeIn(k1.br), at=T.scale1 + 0.4, dur=0.8, ease=E)
    hud.play(TransformFromCopy(V.cell(0, 0), s1), at=T.scale1 + 1.4, dur=0.6, ease=E)
    lit = chain(GENTLE)
    g.play(FadeIn(lit[0]), FadeIn(lit[1]), at=T.scale1 + 1.4, dur=0.6)
    hud.play(FadeIn(plus), TransformFromCopy(M.cols[1], k2.cols[0]), FadeIn(k2.br), at=T.scale2 + 0.2, dur=0.8, ease=E)
    hud.play(TransformFromCopy(V.cell(1, 0), s2), at=T.scale2 + 1.3, dur=0.6, ease=E)
    g.play(FadeIn(lit[2]), at=T.scale2 + 1.3, dur=0.6)
    hud.play(FadeIn(eq2), FadeIn(R, shift=0.15 * LEFT), at=T.add + 0.2, dur=0.6)
    dim.play(FadeOut(dimmer), at=T.add + 0.2, dur=0.7)
    dots.play(FadeOut(field), at=T.add + 0.2, dur=0.7)
    hud.play(Indicate(R, color=C.vec, scale_factor=1.12), at=T.lands + 0.4, dur=0.8)
    g.play(Flash(pt(O, U, GENTLE @ VEC), color=C.vec, line_length=0.25, flash_radius=0.3), at=T.lands + 0.4, dur=0.7)

    # ── clear the board for s07: the moved grid and its two arrows stay ──
    hud.play(FadeOut(row), at=T.lands + 1.25, dur=0.5)
    hb.play(FadeOut(back), at=T.lands + 1.25, dur=0.5)
    lo.play(FadeOut(VGroup(v1, c1, r1)), at=T.lands + 1.25, dur=0.5)
    g.play(FadeOut(lit), at=T.lands + 1.25, dur=0.5)
    finish(s)


def fmt_(x):
    return str(int(round(x)))
