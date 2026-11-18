"""Ch3 (cont.): integration is solving D F = f. A crushed system's answer is one particular solution plus anything
from the null space; here that's the constants, so ∫2x dx = x^2 + C. Then the matrix's other habit: each application
slides every coefficient one slot up and drops the top one, so four applications send any cubic to zero."""
from aion import *

from beats import T
from shots import D_POLY, P_COEF, Mat, plot, poly_mat, pt, tex, backdrop, finish

MAT_TO = np.array([-3.6, 0.6, 0])                        # where s06 left the 4 x 4
FX, EX, OX = -1.35, -0.25, 0.8                           # the product line: F column, "=", f column
TOP = np.array([-2.2, 2.9, 0])                           # the equation above it
QO, QUX, QUY = (4.4, -1.9), 0.9, 0.3                     # the family x^2 + C on the right
CS = [-1, 0, 1, 2, 3]

CASC = [P_COEF]                                          # p, p', p'', p''', p''''
for _ in range(4):
    CASC.append(D_POLY @ CASC[-1])
assert [list(c) for c in CASC] == [[2, 3, -1, 4], [3, -2, 12, 0], [-2, 24, 0, 0], [24, 0, 0, 0], [0, 0, 0, 0]]
assert np.allclose(np.linalg.matrix_power(D_POLY, 4), 0) and np.allclose(D_POLY @ [0, 0, 1, 0], [0, 2, 0, 0])
CX = [-3.0, -1.0, 1.0, 3.0, 5.0]                         # the cascade's columns
CY = 0.6


def col(entries, x, colors, size=40):
    """A 4-entry column at (x, CY), each entry in its own colour."""
    c = Mat([[e] for e in entries], colors=C.text, size=size, v_buff=0.64).move_to([x, CY, 0])
    for i, k in enumerate(colors):
        c.cell(i, 0).set_color(k)
    return c


def pink_mat():
    M = poly_mat().move_to(MAT_TO)
    for i in range(4):
        M.cell(i, 0).set_color(C.null)
    return M


@scene(T.cut_plus_c, T.cut_ch4)
def s07_plus_c(s):
    backdrop(s)
    m = s.manim(z=1)
    t0 = T.cut_plus_c

    # what s06 left: the matrix with its pink column, det 0, and the line 2x
    M = pink_mat()
    box = Rectangle(width=0.62, height=M.br.height - 0.1, stroke_color=C.null, stroke_width=C.thin).move_to(
        M.cols[0].get_center())
    det = tex(r"\det D", r"=", r"0", size=50, colors={2: C.null}).next_to(M, DOWN, buff=0.45)
    PO2, PUX2, PUY2 = (2.9, -1.2), 1.15, 0.33
    ax = VGroup(Line(pt(PO2, 1, (-2.4 * PUX2, 0)), pt(PO2, 1, (2.4 * PUX2, 0)), color=C.axis, stroke_width=C.thin),
                Line(pt(PO2, 1, (0, -1.4)), pt(PO2, 1, (0, 4.4)), color=C.axis, stroke_width=C.thin))
    line = plot(lambda x: 2 * x, -2.0, 2.0, PO2, PUX2, PUY2, C.dfn)
    l2 = tex(r"2x", size=40, color=C.dfn).next_to(pt(PO2, 1, (2.0 * PUX2, PUY2 * 4)), RIGHT, buff=0.1)
    m.add(M, box, det, ax, line, l2, at=t0)

    # ── integration asks: find F with F' = f ──
    m.play(FadeOut(det), at=T.integration, dur=0.5)
    ask = tex(r"F'", r"=", r"2x", size=56, colors={0: C.fn, 2: C.dfn}).move_to(TOP)
    m.play(FadeIn(ask, shift=0.1 * DOWN), Indicate(VGroup(line, l2), color=C.dfn, scale_factor=1.05),
           at=T.find + 0.4, dur=0.8)

    # ── that's a matrix equation: D F = f ──
    td = T.dff
    m.play(FadeOut(VGroup(ax, line, l2)), at=td - 0.6, dur=0.5)
    dff = tex(r"D", r"F", r"=", r"f", size=56, colors={0: C.op, 1: C.fn, 3: C.dfn}).move_to(TOP)
    m.play(ReplacementTransform(ask, dff), at=td, dur=0.8)
    Fq = col(["?"] * 4, FX, [C.fn] * 4)
    eq = tex("=", size=52).move_to([EX, CY, 0])
    fc = col(["0", "2", "0", "0"], OX, [C.dfn] * 4)
    m.play(FadeIn(Fq, shift=0.2 * LEFT), at=td + 0.5, dur=0.6)
    m.play(FadeIn(eq), FadeIn(fc, shift=0.2 * LEFT), at=td + 1.1, dur=0.6)

    # ── a crushed system's answer: one particular solution + the null space ──
    bot = tex(r"F", r"=", r"F_p", r"+", r"\text{null space}", size=48, colors={0: C.fn, 2: C.fn, 4: C.null})
    bot.move_to([TOP[0], -2.2, 0])
    m.play(FadeIn(bot, shift=0.1 * UP), at=T.crushed_system + 0.6, dur=0.7)
    tp = T.particular
    F1 = col(["0", "0", "1", "0"], FX, [C.fn] * 4)
    sq = tex(r"x^2", size=36, color=C.fn).next_to(F1, DOWN, buff=0.25)
    m.play(ReplacementTransform(Fq, F1), FadeIn(sq), Indicate(bot[2], color=C.fn, scale_factor=1.25),
           at=tp + 0.2, dur=0.9)
    m.play(Indicate(bot[4], color=C.null, scale_factor=1.15), Indicate(box, color=C.null, scale_factor=1.05),
           at=tp + 2.4, dur=0.9)

    # ── here the null space is the constants: that's the + C ──
    tc = T.constants
    F2 = col(["C", "0", "1", "0"], FX, [C.null, C.fn, C.fn, C.fn])
    sq2 = tex(r"x^2", r"+", r"C", size=36, colors={0: C.fn, 2: C.null}).next_to(F2, DOWN, buff=0.25)
    m.play(ReplacementTransform(F1, F2), ReplacementTransform(sq, sq2), at=tc + 0.3, dur=0.9)
    integ = tex(r"\int 2x\,dx", r"=", r"x^2", r"+", r"C", size=56, colors={0: C.dfn, 2: C.fn, 4: C.null})
    integ.move_to(bot)
    m.play(ReplacementTransform(bot, integ), at=T.plus_c, dur=0.9)
    # the family x^2 + C: one shape, slid up and down
    qax = VGroup(Line(pt(QO, 1, (-2.2 * QUX, 0)), pt(QO, 1, (2.2 * QUX, 0)), color=C.axis, stroke_width=C.thin),
                 Line(pt(QO, 1, (0, -0.6)), pt(QO, 1, (0, 2.2)), color=C.axis, stroke_width=C.thin))
    fam = VGroup(*[plot(lambda x, c=c: x ** 2 + c, -1.9, 1.9, QO, QUX, QUY, C.fn, opacity=1.0 if c == 0 else 0.45)
                   for c in CS])
    m.play(FadeIn(qax), LaggedStart(*[Create(f) for f in fam], lag_ratio=0.15), at=tc + 0.6, dur=1.6)
    sh = DoubleArrow(pt(QO, 1, (2.15 * QUX, QUY * (3.61 - 1))), pt(QO, 1, (2.15 * QUX, QUY * (3.61 + 3))), buff=0,
                     color=C.null, stroke_width=C.stroke, tip_length=0.18)
    shl = tex(r"C", size=40, color=C.null).next_to(sh, RIGHT, buff=0.12)
    m.play(GrowFromCenter(sh), FadeIn(shl), at=T.plus_c + 0.6, dur=0.7)
    # one bold member slides through the family: choosing C is choosing a height
    ta, tb = T.plus_c + 1.4, T.odd_habit - 0.4
    sop = keys((ta, 0.0), (ta + 0.5, 1.0), (tb, 1.0), (tb + 0.6, 0.0), lead=0)

    def slider(t):
        c = 1.0 + 2.0 * np.sin(2 * np.pi * (t - ta) / 6.0)
        o = float(sop(t))
        return VGroup(plot(lambda x: x ** 2 + c, -1.9, 1.9, QO, QUX, QUY, C.fn, width=C.stroke + 1.5, opacity=o),
                      Dot(pt(QO, 1, (2.15 * QUX, QUY * (3.61 + c))), radius=0.07, color=C.null).set_opacity(o))
    m.redraw(slider, during=(ta, tb + 0.6))

    # ── not a rule to memorize: the null space, where linear algebra says it must be ──
    m.play(Circumscribe(integ[4], color=C.null, buff=0.08), at=T.memorize + 0.6, dur=1.0)
    m.play(Indicate(M.cols[0], color=C.null, scale_factor=1.15), Indicate(F2.cell(0, 0), color=C.null,
                                                                          scale_factor=1.3),
           at=T.must + 0.4, dur=1.0)

    # ── one more habit: every coefficient slides one slot up ──
    to = T.odd_habit
    m.play(FadeOut(VGroup(dff, F2, sq2, eq, fc, integ, qax, fam, sh, shl, box)), at=to - 0.4, dur=0.6)
    m.play(M.animate.scale(0.72).move_to([-5.45, CY, 0]), at=to + 0.3, dur=1.0, ease="easy_ease")
    cols = [col(CASC[0], CX[0], [C.fn] * 4)]
    m.play(FadeIn(cols[0], shift=0.2 * UP), at=to + 1.2, dur=0.6)
    arrows = VGroup()
    starts = [T.slides + 0.3, T.slides + 2.0, T.four_times, T.four_times + 1.5]
    for k, ts in enumerate(starts):
        P = cols[-1]
        colors = [C.dfn if CASC[k + 1][i] != 0 else C.null for i in range(4)]
        Q = col(CASC[k + 1], CX[k + 1], colors)
        ar = tex(r"\xrightarrow{\;D\;}", size=40, color=C.op).move_to([(CX[k] + CX[k + 1]) / 2 + 0.05, CY, 0])
        arrows.add(ar)
        drop = P.cell(0, 0).copy()
        m.play(FadeIn(ar), FadeIn(Q.br), *[TransformFromCopy(P.cell(i + 1, 0), Q.cell(i, 0)) for i in range(3)],
               FadeIn(Q.cell(3, 0), shift=0.3 * UP),
               FadeOut(drop, target_position=Q.cell(0, 0).get_center() + 0.7 * UP), at=ts, dur=1.0)
        m.remove(Q.br, *[Q.cell(i, 0) for i in range(4)], at=ts + 1.05)
        m.add(Q, at=ts + 1.05)
        cols.append(Q)

    # ── four times: every cubic is gone ──
    d4 = tex(r"D^4", r"=", r"0", size=56, colors={0: C.op, 2: C.null}).move_to([1.0, -2.2, 0])
    m.play(FadeIn(d4, shift=0.1 * UP), at=T.four_times + 2.7, dur=0.7)
    m.play(Indicate(cols[-1], color=C.null, scale_factor=1.12), at=T.nothing_left + 0.1, dur=0.9)
    m.play(FadeOut(VGroup(M, *cols, arrows, d4)), at=T.cut_ch4 - 0.75, dur=0.6)
    finish(s)
