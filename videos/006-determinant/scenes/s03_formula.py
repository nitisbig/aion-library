"""Ch3 · Where the formula comes from: the bounding rectangle minus six pieces leaves ad − bc."""
from aion import *

from beats import T
from shots import (A_SHEAR, FRAME, I2, Mat, backdrop, backing, basis_arrows, finish, grid_lines, lettered,
                   matrix_panel, pt, rail, strike, tex)

O3, U3 = np.array([-0.9, -2.3]), 1.4                 # where Ch2 left the grid
a, b, c, d = 3.0, 1.0, 1.0, 2.0                      # the drawing uses our matrix's numbers; the labels stay letters
G, UG = np.array([-6.3, -2.4]), 1.35                 # origin and unit of the drawing


def P(x, y):
    return pt(G, UG, (x, y))


@scene(T.cut_ch3, T.cut_ch4)
def s03_formula(s):
    backdrop(s)
    old = s.manim(z=0)                                # Ch2's leftovers, cleared at the start
    geo = s.manim(z=1)                                # parallelogram, rectangle, pieces
    arr = s.manim(z=2)                                # arrows and their coordinates
    eq = s.manim(z=3)                                 # the working, right-hand side
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 3)
    t0 = T.cut_ch3

    # ── Ch2's last frame, cleared ──
    grid = grid_lines(I2, O3, U3, FRAME, n=16)
    ghost = grid_lines(I2, O3, U3, FRAME, n=16, color=C.ghost, axes=False)
    sq = Polygon(pt(O3, U3, (0, 0)), pt(O3, U3, (1, 0)), pt(O3, U3, (1, 1)), pt(O3, U3, (0, 1)),
                 stroke_color=C.area, stroke_width=C.thin + 0.6, fill_color=C.area, fill_opacity=0.3)
    one = tex("1", size=72, color=C.area).move_to(pt(O3, U3, (0.5, 0.5)))
    ar0 = basis_arrows(I2, O3, U3)
    rd = tex(r"\det", "=", "1", size=56, colors={2: C.area})
    M0, hats0, back0 = matrix_panel([["1", "1"], ["0", "1"]], below=rd)
    old.add(ghost, grid, sq, one, ar0, back0, M0, hats0, rd)
    old.play(FadeOut(VGroup(ghost, grid, sq, one, ar0)), at=t0 + 0.9, dur=1.1, lead=0)
    old.play(FadeOut(VGroup(back0, M0, hats0, rd)), at=t0 + 0.6, dur=0.8, lead=0)
    old.remove(ghost, grid, sq, one, ar0, back0, M0, hats0, rd, at=t0 + 2.1)

    # ── "Why A times D, minus B times C?" ──
    q = lettered("ad", "-", "bc", size=96)
    q[1].set_color(C.text)
    qm = tex("?", size=96, color=C.area)
    VGroup(q, qm).arrange(RIGHT, buff=0.35).move_to([0, 0.3, 0])
    eq.play(Write(q), at=T.why, dur=1.2)
    eq.play(FadeIn(qm, scale=1.4), at=T.why + 1.3, dur=0.5)
    eq.play(FadeOut(VGroup(q, qm), shift=0.3 * UP), at=T.letters - 0.3, dur=0.6)

    # ── the matrix with letters, top right ──
    M = Mat([["a", "b"], ["c", "d"]], colors=[C.ihat, C.jhat], size=56).move_to([4.6, 2.7, 0])
    eq.play(Create(M.br), at=T.letters, dur=0.7)
    eq.play(Write(M.cols[0]), at=T.ac, dur=0.7)
    eq.play(Write(M.cols[1]), at=T.bd, dur=0.7)

    # ── the two columns as arrows, and the parallelogram between them ──
    o = P(0, 0)
    ai = Arrow(o, P(a, c), buff=0, color=C.ihat, stroke_width=C.stroke + 1, tip_length=0.26)
    aj = Arrow(o, P(b, d), buff=0, color=C.jhat, stroke_width=C.stroke + 1, tip_length=0.26)
    ti = lettered("(", "a", ",", "c", ")", size=44).next_to(P(a, c), DR, buff=0.08)
    tj = lettered("(", "b", ",", "d", ")", size=44).next_to(P(b, d), UL, buff=0.08)
    para = Polygon(o, P(a, c), P(a + b, c + d), P(b, d), stroke_color=C.area, stroke_width=C.thin + 0.6,
                   fill_color=C.area, fill_opacity=0.3)
    arr.play(GrowArrow(ai), at=T.ac + 0.2, dur=0.8)
    arr.play(FadeIn(ti, shift=0.1 * RIGHT), at=T.ac + 0.8, dur=0.5)
    arr.play(GrowArrow(aj), at=T.bd + 0.2, dur=0.8)
    arr.play(FadeIn(tj, shift=0.1 * UP), at=T.bd + 0.8, dur=0.5)
    geo.play(FadeIn(para), at=T.want, dur=0.8)
    geo.play(para.animate.set_fill(opacity=0.5), at=T.want + 0.8, dur=0.4)
    geo.play(para.animate.set_fill(opacity=0.3), at=T.want + 1.3, dur=0.5)

    # ── the bounding rectangle, its width a + b and its height c + d ──
    rect = Polygon(o, P(a + b, 0), P(a + b, c + d), P(0, c + d), stroke_color=C.text, stroke_width=C.thin + 0.6,
                   fill_opacity=0)
    geo.play(Create(rect), at=T.rect, dur=1.3)

    def brace(p0, p1, direction, label):
        br = Brace(Line(p0, p1), direction, buff=0.1, color=C.text)
        lb = lettered(label, size=44).next_to(br, direction, buff=0.1)
        return br, lb
    bra, la = brace(P(0, 0), P(a, 0), DOWN, "a")
    brb, lb_ = brace(P(a, 0), P(a + b, 0), DOWN, "b")
    brc, lc = brace(P(a + b, 0), P(a + b, c), RIGHT, "c")
    brd, ld = brace(P(a + b, c), P(a + b, c + d), RIGHT, "d")
    eq.play(LaggedStart(GrowFromCenter(bra), FadeIn(la), GrowFromCenter(brb), FadeIn(lb_), lag_ratio=0.25),
            at=T.width, dur=1.1)
    eq.play(LaggedStart(GrowFromCenter(brc), FadeIn(lc), GrowFromCenter(brd), FadeIn(ld), lag_ratio=0.25),
            at=T.height, dur=1.1)
    tj_fade = T.tri_ac - 0.4                          # the coordinate tags make way for the pieces
    arr.play(FadeOut(VGroup(ti, tj)), at=tj_fade, dur=0.5)

    # ── the working: the rectangle, minus what does not belong ──
    X0 = 0.45                                         # left edge of the working
    r1 = lettered("(a+b)(c+d)", "-ac", "-bd", "-2bc", size=44)
    r1.move_to([X0, 1.15, 0], aligned_edge=LEFT)
    eq.play(Write(r1[0]), at=T.too_big - 0.3, dur=1.1)
    eq.play(Indicate(rect, color=C.text, scale_factor=1.0), at=T.too_big, dur=0.8)

    def piece(*pts):
        return Polygon(*pts, stroke_color=C.cutaway, stroke_width=C.thin, fill_color=C.cutaway, fill_opacity=0.55)
    tri_ac = VGroup(piece(P(0, 0), P(a, 0), P(a, c)), piece(P(b, d), P(a + b, c + d), P(b, c + d)))
    tri_bd = VGroup(piece(P(0, 0), P(b, d), P(0, d)), piece(P(a, c), P(a + b, c), P(a + b, c + d)))
    rects = VGroup(piece(P(a, 0), P(a + b, 0), P(a + b, c), P(a, c)), piece(P(0, d), P(b, d), P(b, c + d), P(0, c + d)))
    bc_tags = VGroup(*[lettered("bc", size=36).move_to(r_) for r_ in rects])
    for grp, beat, val, k in ((tri_ac, T.tri_ac, T.ac_val, 1), (tri_bd, T.tri_bd, T.bd_val, 2), (rects, T.corners, T.bc_val, 3)):
        geo.play(LaggedStart(*[FadeIn(p_) for p_ in grp], lag_ratio=0.4), at=beat, dur=0.9)
        eq.play(TransformFromCopy(grp, r1[k]), at=val - 0.1, dur=1.0)
    geo.play(FadeIn(bc_tags), at=T.corners + 0.9, dur=0.5)

    # ── expand, cancel, and what survives ──
    r2 = lettered("=", "ac", "+ad", "+bc", "+bd", size=44)
    r2.move_to([X0, 0.1, 0], aligned_edge=LEFT)
    r3 = lettered("-ac", "-bd", "-2bc", size=44)
    r3.next_to(r2[1], DOWN, buff=0.35, aligned_edge=LEFT)
    eq.play(TransformFromCopy(r1[0], VGroup(r2[1], r2[2], r2[3], r2[4])), FadeIn(r2[0]), at=T.expand, dur=1.2)
    eq.play(TransformFromCopy(VGroup(r1[1], r1[2], r1[3]), r3), at=T.expand + 1.0, dur=1.0)
    s_ac, s_ac2 = strike(r2[1]), strike(r3[0])
    s_bd, s_bd2 = strike(r2[4]), strike(r3[1])
    s_bc = strike(r2[3])
    r3b = lettered("-bc", size=44).move_to(r3[2], aligned_edge=LEFT)
    eq.play(Create(s_ac), Create(s_ac2), at=T.cancels - 0.5, dur=0.5)
    eq.play(Create(s_bd), Create(s_bd2), at=T.cancels, dur=0.5)
    eq.play(Create(s_bc), Transform(r3[2], r3b), at=T.cancels + 0.5, dur=0.6)
    dim = VGroup(r2[1], r3[0], r2[4], r3[1], r2[3], s_ac, s_ac2, s_bd, s_bd2, s_bc)
    eq.play(dim.animate.set_opacity(0.3), at=T.cancels + 1.1, dur=0.5)

    r4 = lettered("=", "ad", "-bc", size=72)
    r4.move_to([X0, -2.05, 0], aligned_edge=LEFT)
    r4box = SurroundingRectangle(VGroup(r4[1], r4[2]), color=C.area, buff=0.18, stroke_width=C.thin + 0.4)
    eq.play(FadeIn(r4[0]), TransformFromCopy(VGroup(r2[2], r3[2]), VGroup(r4[1], r4[2])), at=T.survives + 0.3, dur=1.2)
    eq.play(Create(r4box), at=T.survives + 1.9, dur=0.7)

    # ── "the area of a parallelogram": the pieces go, the answer sits on the shape it measures ──
    pieces = VGroup(tri_ac, tri_bd, rects, bc_tags)
    geo.play(FadeOut(pieces), at=T.never_arb, dur=0.8)
    inside = lettered("ad", "-bc", size=64).move_to(P((a + b) / 2, (c + d) / 2))
    inside.set_stroke(C.bg, width=5, background=True)          # a dark rim keeps the colours readable on yellow
    eq.play(TransformFromCopy(VGroup(r4[1], r4[2]), inside), at=T.area_para, dur=1.3)

    # ── try it on our matrix ──
    work = VGroup(r1, r2, r3, s_ac, s_ac2, s_bd, s_bd2, s_bc)
    XE = 1.85                                         # where the "=" signs line up
    eq.play(FadeOut(work), FadeOut(r4box), r4.animate.move_to([XE, 1.15, 0], aligned_edge=LEFT), at=T.try_it - 0.2, dur=0.9)
    dl = tex(r"\det", size=72)
    dl.move_to([XE - 0.25 - dl.width / 2, 1.15, 0])   # left of the "=", on the row's centre line
    eq.play(FadeIn(dl, shift=0.1 * RIGHT), at=T.try_it + 0.6, dur=0.6)
    M2 = Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat], size=56).move_to(M)
    eq.play(FadeOut(VGroup(M.cols[0], M.cols[1])), FadeIn(VGroup(M2.cols[0], M2.cols[1])), at=T.try_it + 0.4, dur=0.8)
    labels = VGroup(la, lb_, lc, ld)
    nums = VGroup(*[tex(v, size=44, color=col).move_to(l_) for v, col, l_ in
                    (("3", C.ihat, la), ("1", C.jhat, lb_), ("1", C.ihat, lc), ("2", C.jhat, ld))])
    eq.play(FadeOut(labels), FadeIn(nums), at=T.try_it + 0.6, dur=0.8)

    n1 = tex("=", "3", r"\cdot", "2", "-", "1", r"\cdot", "1", size=64,
             colors={1: C.ihat, 3: C.jhat, 5: C.jhat, 7: C.ihat})
    n1.move_to([XE, 0.0, 0], aligned_edge=LEFT)
    n2 = tex("=", "6", "-", "1", size=64).move_to([XE, -1.15, 0], aligned_edge=LEFT)
    n3 = tex("=", "5", size=80, colors={1: C.area}).move_to([XE, -2.35, 0], aligned_edge=LEFT)
    eq.play(FadeIn(n1[0]), Write(VGroup(n1[1], n1[2], n1[3])), at=T.six, dur=0.8)
    eq.play(Write(VGroup(n1[4], n1[5], n1[6], n1[7])), at=T.one, dur=0.8)
    eq.play(Write(n2), at=T.minus, dur=0.8)
    eq.play(Write(n3), at=T.five, dur=0.6)
    five = tex("5", size=96, color=C.area).move_to(inside).set_stroke(C.bg, width=5, background=True)
    eq.play(ReplacementTransform(inside, five), at=T.same5, dur=0.8)
    eq.play(Indicate(five, color=C.area, scale_factor=1.25), at=T.same5 + 0.9, dur=0.8)

    finish(s)
