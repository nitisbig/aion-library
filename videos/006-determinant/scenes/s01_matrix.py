"""Ch1 · A matrix moves space: the columns say where i-hat and j-hat land, and the grid follows."""
from aion import *

from beats import T
from shots import (A_MAIN, FRAME, I2, Mat, _clip, backdrop, backing, basis_arrows, chapter_card, finish, grid_lines,
                   live, pt, rail, span_area, tex)

O, U = (-1.0, -1.4), 0.9                              # where the origin sits, and one grid step
E = "easy_ease"


@scene(T.cut_ch1, T.cut_ch2)
def s01_matrix(s):
    backdrop(s)
    ghost = s.manim(z=0)                              # the original grid, left behind for reference
    m = s.manim(z=1)                                  # the moving grid
    hi = s.manim(z=2)                                 # highlights on the grid
    g = s.manim(z=3)                                  # arrows
    lab = s.manim(z=4)                                # symbols that live on the grid
    hud = s.manim(z=5, parallax=0.0)                  # matrix, chapter card

    # ── the score: when each column moves ──
    A_I = np.array([[3.0, 0.0], [1.0, 1.0]])          # i-hat has landed, j-hat has not moved yet
    ti0, ti1 = T.i_moves - 0.15, T.i_moves + 1.5
    tj0, tj1 = T.j_moves - 0.15, T.j_moves + 1.3
    f0, f1 = T.follows - 0.15, T.follows + 2.4        # everything else follows
    r0, r1 = T.all_it_is - 0.15, T.all_it_is + 1.6    # back to rest
    p0, p1 = T.movement - 0.15, T.movement + 1.9      # once more, all together: "a movement of space"
    Marr = keys((ti0, I2), (ti1, A_I, E), (tj0, A_I), (tj1, A_MAIN, E), (r0, A_MAIN), (r1, I2, E), (p0, I2),
                (p1, A_MAIN, E), lead=0)
    Mgrid = keys((f0, I2), (f1, A_MAIN, E), (r0, A_MAIN), (r1, I2, E), (p0, I2), (p1, A_MAIN, E), lead=0)

    # ── chapter card ──
    chapter_card(hud, 1, T.cut_ch1 + 0.3, T.grid - 0.7)
    rail(hud, 1)

    # ── a flat grid, drawn outward from the origin ──
    base = grid_lines(I2, O, U, FRAME)
    o3 = pt(O, U, (0, 0))

    def dist(ln):
        d = ln.get_end() - ln.get_start()
        return float(np.linalg.norm(np.cross(d, o3 - ln.get_start())) / np.linalg.norm(d))
    dim, major, axis = base
    m.play(LaggedStart(*[Create(ln) for ln in sorted(dim, key=dist)], lag_ratio=0.02), at=T.grid, dur=1.6)
    m.play(LaggedStart(*[Create(ln) for ln in sorted(major, key=dist)], lag_ratio=0.04), at=T.grid + 0.2, dur=1.6)
    m.play(LaggedStart(*[Create(ln) for ln in axis], lag_ratio=0.3), at=T.grid + 0.5, dur=1.2)
    m.remove(base, *dim, *major, *axis, at=f0)
    live(m, lambda t: grid_lines(Mgrid(t), O, U, FRAME), (f0, f1), (r0, p1))
    ghost.add(grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False), at=f0)

    # ── two arrows ──
    a0 = basis_arrows(I2, O, U)
    g.play(GrowArrow(a0[0]), at=T.ihat, dur=0.8)
    g.play(GrowArrow(a0[1]), at=T.jhat, dur=0.8)
    g.remove(a0[0], a0[1], at=ti0)
    live(g, lambda t: basis_arrows(Marr(t), O, U), (ti0, tj1), (r0, p1))

    def li_pos(t):
        return pt(O, U, Marr(t)[:, 0]) + np.array([0.15, -0.42, 0])

    def lj_pos(t):
        return pt(O, U, Marr(t)[:, 1]) + np.array([-0.45, 0.22, 0])
    li = tex(r"\hat{\imath}", size=56, color=C.ihat).move_to(li_pos(ti0))
    lj = tex(r"\hat{\jmath}", size=56, color=C.jhat).move_to(lj_pos(ti0))
    lab.play(FadeIn(li, shift=0.15 * UP), at=T.ihat_name, dur=0.5)
    lab.play(FadeIn(lj, shift=0.15 * RIGHT), at=T.jhat_name, dur=0.5)
    for a, b in ((ti0, tj1), (r0, p1)):
        lab.drive(li, lambda mob, t: mob.move_to(li_pos(t)), during=(a, b))
        lab.drive(lj, lambda mob, t: mob.move_to(lj_pos(t)), during=(a, b))

    # ── the matrix: one column per arrow. Symbols over the columns say which arrow each column moves ──
    M = Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat], size=64).move_to([-5.05, 1.95, 0])
    hat_i = tex(r"\hat{\imath}", size=44, color=C.ihat).next_to(M.cols[0], UP, buff=0.42)
    hat_j = tex(r"\hat{\jmath}", size=44, color=C.jhat).next_to(M.cols[1], UP, buff=0.42)
    hat_j.align_to(hat_i, DOWN)
    s1, s2 = M.col_box(0, C.ihat), M.col_box(1, C.jhat)
    back = backing(VGroup(M, hat_i, hat_j, s1, s2), pad=0.3)

    hud.play(FadeIn(back), at=T.instructions, dur=0.5)
    hud.play(Create(M.br), at=T.instructions + 0.2, dur=0.8)
    hud.play(FadeIn(s1), FadeIn(hat_i, shift=0.1 * DOWN), at=T.col1, dur=0.6)
    hud.play(FadeIn(s2), FadeIn(hat_j, shift=0.1 * DOWN), at=T.col2, dur=0.6)
    hud.play(Indicate(M.br, color=C.text, scale_factor=1.06), at=T.take, dur=0.8)
    hud.play(Write(M.cols[0]), at=T.c31 + 0.5, dur=0.9)
    hud.play(Write(M.cols[1]), at=T.c12 + 0.5, dur=0.9)
    hud.play(FadeOut(VGroup(s1, s2)), at=f0 + 0.3, dur=0.6)

    # where each arrow lands, tagged with its coordinates
    tag_i = tex("(", "3", ",", "1", ")", size=40, colors={1: C.ihat, 3: C.ihat})
    tag_i.move_to(pt(O, U, A_MAIN[:, 0]) + np.array([0.9, 0.05, 0]))
    tag_j = tex("(", "1", ",", "2", ")", size=40, colors={1: C.jhat, 3: C.jhat})
    tag_j.move_to(pt(O, U, A_MAIN[:, 1]) + np.array([0.25, 0.5, 0]))
    lab.play(FadeIn(tag_i, shift=0.15 * RIGHT), at=ti1, dur=0.5, lead=0)
    lab.play(FadeIn(tag_j, shift=0.15 * UP), at=tj1, dur=0.5, lead=0)
    lab.play(FadeOut(VGroup(tag_i, tag_j)), at=f0 + 0.3, dur=0.6)

    # ── what the grid keeps: straight, parallel, evenly spaced ──
    def gridline(k):                                   # the k-th line of the family running along i-hat
        a, b = _clip(pt(O, U, k * A_MAIN[:, 1])[:2], A_MAIN[:, 0], FRAME)
        return Line([*a, 0], [*b, 0], color=C.text, stroke_width=C.stroke - 1)
    l1, l2 = gridline(1), gridline(2)
    hi.play(Create(l1), at=T.straight + 0.5, dur=0.9)
    hi.play(Create(l2), at=T.parallel, dur=0.8)
    lattice = [pt(O, U, A_MAIN @ np.array([i, j])) for j in (1, 2) for i in range(-3, 4)]
    dots = VGroup(*[Dot(p, radius=0.065, color=C.text) for p in lattice if abs(p[0]) < 7.0 and abs(p[1]) < 3.9])
    hi.play(LaggedStart(*[FadeIn(d, scale=2.5) for d in dots], lag_ratio=0.12), at=T.even, dur=1.0)
    hi.play(FadeOut(VGroup(l1, l2, dots)), at=T.leans + 0.4, dur=0.8)
    hi.remove(l1, l2, dots, at=T.leans + 1.4)

    # ── the question that opens chapter 2 ──
    unit = DashedVMobject(Square(side_length=U, color=C.text, stroke_width=C.thin).move_to(pt(O, U, (0.5, 0.5))),
                          num_dashes=24)
    area = span_area(A_MAIN, O, U, opacity=0.25)
    q = tex("?", size=80, color=C.area).move_to(pt(O, U, (A_MAIN[:, 0] + A_MAIN[:, 1]) / 2))
    hi.play(Create(unit), at=T.question + 0.4, dur=0.9)
    hi.play(FadeIn(area), at=T.how_much, dur=0.9)
    lab.play(FadeIn(q, scale=1.6), at=T.how_much + 0.8, dur=0.6)
    lab.play(Indicate(q, color=C.area, scale_factor=1.25), at=T.how_much + 1.7, dur=0.8)

    s.camera.push(T.follows, zoom=1.04, dur=8.0, ease="in_out_sine")
    s.camera.push(T.all_it_is, zoom=1.0, dur=3.0, ease="in_out_sine")
    finish(s)
