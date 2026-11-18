"""Ch3: why plus C exists. The 4 x 4's first column is all zeros: a constant goes in, nothing comes out. In the plane
of a + bx (D sends (a, b) to (b, 0)) the whole line of constants lands on the origin: the null space. A matrix that
crushes a direction can't be undone (det 0): x^2 + 5 and x^2 - 2 both have derivative 2x."""
from aion import *

from beats import T
from shots import (chapter_header, D_POLY, P_COEF, PCOL_X, PDCOL_X, PEQ_X, POLY_C, backdrop, coef_col, finish, plot, poly_mat, pt,
                   tex)

assert np.linalg.matrix_rank(D_POLY) == 3 and abs(np.linalg.det(D_POLY)) < 1e-12
MAT_TO = np.array([-3.6, 0.6, 0])                        # where the 4 x 4 sits in this chapter
PO, PU = (3.0, 0.3), 0.55                                # the (1, x) plane on the right


@scene(T.cut_ch3, T.cut_plus_c)
def s06_null(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 3, T.cut_ch3 + 0.45)                     # chapter badge row + title (fills the cut)
    t0 = T.cut_ch3

    # what s05 left: the product line, the graphs, the struck lim and approx
    M = poly_mat()
    pc = coef_col(P_COEF, PCOL_X, C.fn)
    eq = tex("=", size=56).move_to([PEQ_X, POLY_C[1], 0])
    dc = coef_col(D_POLY @ P_COEF, PDCOL_X, C.dfn)
    GO, GUX, GUY = (-5.15, -1.3), 1.25, 0.11
    rest = VGroup(pc, eq, dc,
                  VGroup(Line(pt(GO, 1, (-1.35, 0)), pt(GO, 1, (1.35, 0)), color=C.axis, stroke_width=C.thin),
                         Line(pt(GO, 1, (0, -0.75)), pt(GO, 1, (0, 1.75)), color=C.axis, stroke_width=C.thin)),
                  plot(lambda x: 2 + 3 * x - x ** 2 + 4 * x ** 3, -0.95, 1.0, GO, GUX, GUY, C.fn, ylim=(-6.5, 15.5)),
                  plot(lambda x: 3 - 2 * x + 12 * x ** 2, -0.95, 1.0, GO, GUX, GUY, C.dfn, ylim=(-6.5, 15.5)),
                  tex(r"p", r"=", r"2 + 3x - x^2 + 4x^3", size=40, colors={0: C.fn, 2: C.fn}).move_to([-5.0, -3.35, 0]))
    rest.add(tex(r"p'", r"=", r"3 - 2x + 12x^2", size=40, colors={0: C.dfn, 2: C.dfn}).next_to(rest[-1], UP, buff=0.25,
                                                                                            aligned_edge=LEFT))
    for x0, sym in ((-1.0, r"\lim"), (1.0, r"\approx")):
        t = tex(sym, size=56, color=C.muted).move_to([x0, 2.5, 0])
        rest.add(t, Line(t.get_corner(DL) + 0.1 * DL, t.get_corner(UR) + 0.1 * UR, color=C.text, stroke_width=C.stroke))
    m.add(M, rest, at=t0)

    # ── look at the first column: all zeros ──
    tf = T.first_col
    m.play(FadeOut(rest), at=tf - 0.5, dur=0.5)
    M2 = poly_mat().move_to(MAT_TO)                           # built in place, so its columns stay addressable
    m.play(ReplacementTransform(M, M2), at=tf, dur=1.0, ease="easy_ease")
    M = poly_mat().move_to(MAT_TO)                            # the same matrix with its zero column in pink
    for i in range(4):
        M.cell(i, 0).set_color(C.null)
    zc = VGroup(*[M.cell(i, 0).copy() for i in range(4)])
    m.play(FadeIn(zc), at=T.all_zeros, dur=0.6)
    m.remove(M2, zc, at=T.all_zeros + 0.7)
    m.add(M, at=T.all_zeros + 0.7)
    box = Rectangle(width=0.62, height=M.br.height - 0.1, stroke_color=C.null, stroke_width=C.thin).move_to(
        M.cols[0].get_center())
    m.play(Create(box), at=T.all_zeros + 0.1, dur=0.6)

    # ── feed it a constant: nothing comes out ──
    tc = T.constant
    cin = coef_col([5, 0, 0, 0], 0, C.fn, size=40)
    cin.move_to(MAT_TO + np.array([2.25, 0, 0]))
    ceq = tex("=", size=52).move_to(MAT_TO + np.array([3.35, 0, 0]))
    cout = coef_col([0, 0, 0, 0], 0, C.null, size=40)
    cout.move_to(MAT_TO + np.array([4.4, 0, 0]))
    five = tex(r"5", size=40, color=C.fn).next_to(cin, UP, buff=0.25)
    m.play(FadeIn(cin, shift=0.3 * LEFT), FadeIn(five), at=tc, dur=0.7)
    m.play(FadeIn(ceq), FadeIn(cout), at=tc + 1.0, dur=0.7)

    # ── in the plane of a + bx: the line of constants lands on one point ──
    tcr = T.crushed
    m.play(FadeOut(VGroup(cin, ceq, cout, five)), at=tcr - 0.6, dur=0.5)
    box3 = (PO[0] - 3.2, PO[1] - 2.6, PO[0] + 3.4, PO[1] + 2.6)
    from shots import grid_lines
    grid = grid_lines(np.eye(2), PO, PU, box3, n=8, opacity=0.5)
    lab_a = tex(r"1", size=34, color=C.data).move_to(pt(PO, PU, (5.9, -0.45)))
    lab_b = tex(r"x", size=34, color=C.data).move_to(pt(PO, PU, (-0.45, 4.4)))
    m.play(FadeIn(grid), FadeIn(lab_a), FadeIn(lab_b), at=tcr - 0.2, dur=0.8)
    cline = Line(pt(PO, PU, (-5.8, 0)), pt(PO, PU, (6.2, 0)), color=C.null, stroke_width=C.stroke + 1)
    m.play(Create(cline), at=tcr + 0.5, dur=0.9)
    vals = [(5, "5"), (-2, "-2")]
    dots = VGroup(*[Dot(pt(PO, PU, (v, 0)), radius=0.09, color=C.fn) for v, _ in vals])
    labs = VGroup(*[tex(sv, size=32, color=C.fn).next_to(d, UP, buff=0.15) for (v, sv), d in zip(vals, dots)])
    big = Arrow(pt(PO, PU, (4.6, 0.9)), pt(PO, PU, (6.3, 0.9)), buff=0, color=C.fn, stroke_width=C.stroke,
                tip_length=0.2)
    bigl = tex(r"10^6", size=32, color=C.fn).next_to(big, UP, buff=0.1)
    te = T.every_constant
    m.play(LaggedStart(*[AnimationGroup(FadeIn(d, scale=0.5), FadeIn(l)) for d, l in zip(dots, labs)],
                       lag_ratio=0.4), at=te, dur=1.0)
    m.play(GrowArrow(big), FadeIn(bigl), at=te + 1.6, dur=0.6)
    tsp = T.same_point
    origin = pt(PO, PU, (0, 0))
    m.play(*[d.animate.move_to(origin) for d in dots], FadeOut(labs), FadeOut(VGroup(big, bigl)),
           at=tsp - 0.6, dur=1.0, ease="easy_ease")
    zero = tex(r"0", size=36, color=C.null).next_to(origin, DL, buff=0.12)
    m.play(FadeIn(zero), Flash(origin, color=C.null, line_length=0.2, flash_radius=0.25), at=tsp + 0.5, dur=0.6)
    nul = tex(r"\text{null space}", size=40, color=C.null).next_to(cline, DOWN, buff=0.25).shift(1.6 * RIGHT)
    m.play(FadeIn(nul, shift=0.1 * UP), Indicate(cline, color=C.null, scale_factor=1.0), at=T.null_space + 0.3, dur=0.8)

    # ── it can never be undone: det 0 ──
    tu = T.undone
    plane = VGroup(grid, lab_a, lab_b, cline, dots, zero, nul)
    m.play(FadeOut(plane), at=tu, dur=0.6)
    det = tex(r"\det D", r"=", r"0", size=50, colors={2: C.null}).next_to(M, DOWN, buff=0.45).shift(
        (MAT_TO - POLY_C) * 0)
    m.play(FadeIn(det, shift=0.1 * UP), at=T.det_zero, dur=0.6)
    inv = tex(r"D^{-1}", r"=", r"\;?", size=60, colors={0: C.op, 2: C.muted}).move_to([2.9, 1.2, 0])
    m.play(FadeIn(inv, shift=0.1 * DOWN), at=T.undone + 0.6, dur=0.7)
    m.play(Wiggle(inv[2], scale_value=1.25, rotation_angle=0.05 * TAU), at=T.det_zero + 2.0, dur=1.2)
    xk = Line(inv.get_corner(DL) + 0.12 * DL, inv.get_corner(UR) + 0.12 * UR, color=C.null, stroke_width=C.stroke + 1)
    m.play(Create(xk), at=T.no_way + 0.3, dur=0.5)
    m.play(FadeOut(VGroup(inv, xk), shift=0.2 * UP), at=T.parabolas - 0.7, dur=0.5)

    # ── two inputs, one output: no way back ──
    QO, QUX, QUY = (2.9, -1.2), 1.15, 0.33
    ax = VGroup(Line(pt(QO, 1, (-2.4 * QUX, 0)), pt(QO, 1, (2.4 * QUX, 0)), color=C.axis, stroke_width=C.thin),
                Line(pt(QO, 1, (0, -1.4)), pt(QO, 1, (0, 4.4)), color=C.axis, stroke_width=C.thin))
    pa = plot(lambda x: x ** 2 + 5, -2.0, 2.0, QO, QUX, QUY, C.fn)
    pb = plot(lambda x: x ** 2 - 2, -2.0, 2.0, QO, QUX, QUY, C.fn)
    la = tex(r"x^2 + 5", size=36, color=C.fn).next_to(pt(QO, 1, (2.0 * QUX, QUY * 9)), RIGHT, buff=0.1)
    lb = tex(r"x^2 - 2", size=36, color=C.fn).next_to(pt(QO, 1, (2.0 * QUX, QUY * 2)), RIGHT, buff=0.1)
    tp = T.parabolas
    m.play(FadeIn(ax), Create(pa), FadeIn(la), at=tp - 0.2, dur=0.8)
    m.play(Create(pb), FadeIn(lb), at=tp + 1.0, dur=0.8)
    line = plot(lambda x: 2 * x, -2.0, 2.0, QO, QUX, QUY, C.dfn)
    l2 = tex(r"2x", size=40, color=C.dfn).next_to(pt(QO, 1, (2.0 * QUX, QUY * 4)), RIGHT, buff=0.1)
    m.play(ReplacementTransform(pa, line), ReplacementTransform(pb, line.copy()), FadeOut(VGroup(la, lb)),
           FadeIn(l2), at=T.two_x, dur=1.2, ease="easy_ease")
    assert box is not None
    finish(s)
