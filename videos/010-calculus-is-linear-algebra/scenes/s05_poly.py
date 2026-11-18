"""Ch2 (cont.): no approximation needed. A cubic is four numbers in the basis 1, x, x^2, x^3. The derivative sends
1 → 0, x → 1, x^2 → 2x, x^3 → 3x^2; written as columns that's an exact 4 x 4 matrix with 1, 2, 3 just above the
diagonal. It turns p = 2 + 3x − x^2 + 4x^3 into p' = 3 − 2x + 12x^2. No limits, no approximation."""
from aion import *

from beats import T
from shots import (cos_tracer, D_POLY, P_COEF, PCOL_X, PDCOL_X, PEQ_X, POLY_C, backdrop, coef_col, finish, plot, poly_mat, pt,
                   tex)

_XS = 2 * np.pi * (np.arange(1000) + 0.5) / 1000            # s04's forward difference, same numbers as there
ERR = np.max(np.abs((np.roll(np.sin(_XS), -1) - np.sin(_XS)) / (2 * np.pi / 1000) - np.cos(_XS)))
assert 0.003 < ERR < 0.0032

BASIS = [r"1", r"x", r"x^2", r"x^3"]
IMAGES = [r"0", r"1", r"2x", r"3x^2"]
PX = [-4.95, -1.65, 1.65, 4.95]                             # the four basis panels (centres)
PY = 2.45
p = lambda x: 2 + 3 * x - x ** 2 + 4 * x ** 3               # noqa: E731
dp = lambda x: 3 - 2 * x + 12 * x ** 2                      # noqa: E731
GO, GUX, GUY = (-5.15, -1.3), 1.25, 0.11                     # the cubic's graph, lower left (y from -6 to 8 ... 17)


@scene(T.cut_poly, T.cut_ch3)
def s05_poly(s):
    backdrop(s)
    m = s.manim(z=1)
    t0 = T.cut_poly

    # what s04 left
    PO, PUX, PUY = (-3.1, -0.5), 1.0, 1.35
    xs = 2 * np.pi * (np.arange(1000) + 0.5) / 1000
    out = (np.sin(np.roll(xs, -1)) - np.sin(xs)) / (2 * np.pi / 1000)
    out[-1] = (np.sin(xs[0]) - np.sin(xs[-1])) / (2 * np.pi / 1000)
    left = VGroup(
        Line(pt(PO, 1, (-0.2, 0)), pt(PO, 1, (PUX * 2 * np.pi + 0.2, 0)), color=C.axis, stroke_width=C.thin),
        VMobject(stroke_color=C.dfn, stroke_width=C.stroke + 1).set_points_as_corners(
            np.stack([PO[0] + PUX * xs, PO[1] + PUY * out, 0 * xs], -1)),
        DashedVMobject(plot(np.cos, 0, 2 * np.pi, PO, PUX, PUY, C.text, width=C.thin * 1.4), num_dashes=70),
        tex(r"\approx", r"\cos x", size=48).next_to(pt(PO, 1, (PUX * 2 * np.pi, PUY)), UP, buff=0.1))
    took = tex(r"D", r"\,\sin", r"\;\approx\;", r"\cos", size=56, colors={0: C.op, 1: C.fn, 3: C.dfn}).move_to(
        [0, 2.9, 0])
    m.add(left, took, at=t0)

    # ── an approximation, better as the points get closer ──
    err = tex(r"\max\,|D\sin - \cos|", r"\approx", f"{ERR:.3f}", size=40, color=C.muted).next_to(took, DOWN, buff=0.3)
    m.play(FadeIn(err, shift=0.1 * UP), at=T.approximation + 0.6, dur=0.6)
    t_out = T.polys - 0.7                                   # hold the approximation until the building blocks arrive
    m.play(FadeOut(VGroup(left, took, err)), at=t_out, dur=0.6)
    trop = keys((t_out, 1.0), (t_out + 0.6, 0.0), lead=0)
    m.redraw(lambda t: cos_tracer(t, T.took + 1.4, float(trop(t))), during=(t0, t_out + 0.6))

    # ── the polynomials up to x cubed: four building blocks ──
    panels, labels = VGroup(), []
    for k, x0 in enumerate(PX):
        o = (x0, PY)
        ax = VGroup(Line(pt(o, 1, (-1.05, 0)), pt(o, 1, (1.05, 0)), color=C.axis, stroke_width=C.thin * 0.8),
                    Line(pt(o, 1, (0, -0.6)), pt(o, 1, (0, 0.6)), color=C.axis, stroke_width=C.thin * 0.8))
        cv = plot(lambda x, k=k: x ** k, -1, 1, o, 0.95, 0.55, C.text, width=C.stroke - 1)
        panels.add(VGroup(ax, cv))
        labels.append(tex(BASIS[k], size=44, color=C.data).move_to([x0, PY - 1.0, 0]))
    tp = T.polys
    m.play(LaggedStart(*[AnimationGroup(FadeIn(pn[0]), Create(pn[1]), FadeIn(lb)) for pn, lb in zip(panels, labels)],
                       lag_ratio=0.25), at=tp, dur=1.8)
    m.play(LaggedStart(*[Indicate(lb, color=C.text, scale_factor=1.2) for lb in labels], lag_ratio=0.2),
           at=T.blocks, dur=1.2)

    # ── a cubic is really just four numbers ──
    axp = VGroup(Line(pt(GO, 1, (-1.35, 0)), pt(GO, 1, (1.35, 0)), color=C.axis, stroke_width=C.thin),
                 Line(pt(GO, 1, (0, -0.75)), pt(GO, 1, (0, 1.75)), color=C.axis, stroke_width=C.thin))
    cp = plot(p, -0.95, 1.0, GO, GUX, GUY, C.fn, ylim=(-6.5, 15.5))
    peq = tex(r"p", r"=", r"2 + 3x - x^2 + 4x^3", size=40, colors={0: C.fn, 2: C.fn}).move_to([-5.0, -3.35, 0])
    pcol = coef_col(P_COEF, PCOL_X, C.fn)
    rowlab = VGroup(*[tex(b, size=30, color=C.muted).move_to([PCOL_X + 0.95, pcol.cell(i, 0).get_center()[1], 0])
                      for i, b in enumerate(BASIS)])
    tf = T.four_numbers
    m.play(FadeIn(axp), Create(cp), FadeIn(peq), at=tf - 1.2, dur=1.0)
    m.play(FadeIn(pcol.br), LaggedStart(*[TransformFromCopy(peq[2], pcol.cell(i, 0)) for i in range(4)],
                                        lag_ratio=0.15), FadeIn(rowlab), at=tf + 0.2, dur=1.2)

    # ── the derivative sends 1 → 0, x → 1, x^2 → 2x, x^3 → 3x^2 ──
    ts = T.sends
    imgs = []
    for k in range(4):
        arr = tex(r"\to", IMAGES[k], size=44, colors={1: C.dfn})
        arr.next_to(labels[k], RIGHT, buff=0.18)
        imgs.append(arr)
        m.play(VGroup(labels[k]).animate.shift(0.45 * LEFT), FadeIn(arr.shift(0.45 * LEFT), shift=0.1 * RIGHT),
               at=ts + 1.6 * k, dur=0.6)

    # ── each image, as a column: an exact 4 x 4 matrix ──
    M = poly_mat()
    tl = T.lands
    m.play(FadeIn(M.br), at=tl, dur=0.5)
    for j in range(4):
        m.play(TransformFromCopy(imgs[j][1], M.cols[j]), at=tl + 0.3 + 0.45 * j, dur=0.8)
    m.play(Indicate(M, color=C.op, scale_factor=1.04), at=T.four_by_four + 0.3, dur=0.9)
    sup = VGroup(M.cell(0, 1), M.cell(1, 2), M.cell(2, 3))
    m.play(LaggedStart(*[Indicate(c, color=C.op, scale_factor=1.5) for c in sup], lag_ratio=0.25),
           at=T.above_diag, dur=1.2)

    # ── multiply by the cubic's four numbers: out come its derivative's ──
    tm = T.mult_cubic
    eq = tex("=", size=56).move_to([PEQ_X, POLY_C[1], 0])
    dcol = coef_col(D_POLY @ P_COEF, PDCOL_X, C.dfn)
    m.play(FadeOut(rowlab), FadeIn(eq), FadeIn(dcol.br), at=tm, dur=0.5)
    for i in range(4):
        m.play(TransformFromCopy(VGroup(M.cells[i][0], M.cells[i][1], M.cells[i][2], M.cells[i][3]), dcol.cell(i, 0)),
               at=tm + 0.4 + 0.35 * i, dur=0.7)
    cdp = plot(dp, -0.95, 1.0, GO, GUX, GUY, C.dfn, ylim=(-6.5, 15.5))
    dpeq = tex(r"p'", r"=", r"3 - 2x + 12x^2", size=40, colors={0: C.dfn, 2: C.dfn}).next_to(peq, UP, buff=0.25,
                                                                                       aligned_edge=LEFT)
    m.play(Create(cdp), FadeIn(dpeq), at=tm + 2.0, dur=1.0)

    # ── no limits, no approximation ──
    tn = T.no_limits
    m.play(FadeOut(VGroup(panels, *labels, *imgs)), at=tn - 0.5, dur=0.5)
    lim = tex(r"\lim", size=56, color=C.muted).move_to([-1.0, 2.5, 0])
    apx = tex(r"\approx", size=56, color=C.muted).move_to([1.0, 2.5, 0])
    m.play(FadeIn(lim), at=tn, dur=0.4)
    m.play(Create(Line(lim.get_corner(DL) + 0.1 * DL, lim.get_corner(UR) + 0.1 * UR, color=C.text,
                       stroke_width=C.stroke)), at=tn + 0.4, dur=0.4)
    m.play(FadeIn(apx), at=tn + 1.1, dur=0.4)
    m.play(Create(Line(apx.get_corner(DL) + 0.1 * DL, apx.get_corner(UR) + 0.1 * UR, color=C.text,
                       stroke_width=C.stroke)), at=tn + 1.4, dur=0.4)
    m.play(Indicate(M, color=C.op, scale_factor=1.05), at=T.by_matrix + 0.3, dur=1.0)
    assert np.allclose(D_POLY @ P_COEF, [3, -2, 12, 0])
    finish(s)
