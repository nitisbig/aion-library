"""Ch1 (cont.): functions behave like vectors. Add two curves point by point, exactly like adding two columns; scale a
curve by three and every entry scales. Then the derivative respects both: the slope of a sum is the sum of the slopes,
the slope of 3f is 3 times the slope (tangents at one point, with the real numbers). Those are the rules every matrix
obeys, so the derivative should be a matrix."""
from aion import *

from beats import T
from shots import (COL_X, GO1, GUX1, GUY1, backdrop, bar_column, col_brackets, fmt, plot, pt, samples, tex)

GO, GUX, GUY = GO1, GUX1, 0.62                               # the graph, flatter so 3f fits
f = np.sin
g = lambda x: 0.5 * np.cos(2 * x)                           # noqa: E731
df = np.cos
dg = lambda x: -np.sin(2 * x)                               # noqa: E731
X0 = 2.0                                                    # where the tangents touch
assert abs(df(X0) + dg(X0) - 0.341) < 5e-4 and abs(3 * df(X0) + 1.248) < 5e-4

CY, CH = -0.2, 3.4                                          # the three columns: centre y, body height
CX = [1.55, 3.65, 5.75]
X8 = samples(8)


def cy(k):
    return CY + CH / 2 - CH * (k + 0.5) / 8


def column(vals, x, color):
    return VGroup(*[tex(fmt(round(v, 2)), size=26, color=color).move_to([x, cy(k), 0]) for k, v in enumerate(vals)])


def dashed(mob):
    return DashedVMobject(mob, num_dashes=60, dashed_ratio=0.55)


def tangent(fn, dfn, x0, uy, half=0.75, color=None):
    """The tangent segment to y = fn(x) at x0 on the graph (graph units, so the drawn slope is the real slope)."""
    y0, k = fn(x0), dfn(x0)
    a = pt(GO, 1, (GUX * (x0 - half), uy * (y0 - k * half)))
    b = pt(GO, 1, (GUX * (x0 + half), uy * (y0 + k * half)))
    return VGroup(Line(a, b, color=color or C.dfn, stroke_width=C.stroke),
                  Dot(pt(GO, 1, (GUX * x0, uy * y0)), radius=0.06, color=color or C.dfn))


@scene(T.cut_linear, T.cut_ch2)
def s03_linear(s):
    backdrop(s)
    m = s.manim(z=1)
    t0 = T.cut_linear

    # the state s02 left: the curve, its axis and the 1000-entry column
    axis = Line(pt(GO, 1, (-0.25, 0)), pt(GO, 1, (GUX * 2 * np.pi + 0.3, 0)), color=C.axis, stroke_width=C.thin)
    big = plot(f, 0, 2 * np.pi, GO1, GUX1, GUY1, C.fn, n=200)
    from shots import COL_H
    col_old = VGroup(col_brackets(COL_X, -0.2, width=1.35), bar_column(np.sin(samples(1000)), COL_X, -0.2, width=0.6),
                     tex(r"\in", r"\mathbb{R}^{1000}", size=44, colors={1: C.fn}).next_to([COL_X + 0.6, -0.2, 0], RIGHT,
                                                                                            buff=0.25))
    m.add(axis, big, col_old, at=t0)
    assert COL_H > 0

    # ── functions behave like vectors: f and its column ──
    cf = plot(f, 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200)
    m.play(FadeOut(col_old), Transform(big, cf), at=T.behave, dur=1.0)
    m.remove(big, at=T.behave + 1.1)
    m.add(cf, at=T.behave + 1.1)
    dots_f = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * f(x))), radius=0.06, color=C.fn) for x in X8])
    colf = column(f(X8), CX[0], C.fn)
    brf = col_brackets(CX[0], CY, CH, width=1.25)
    m.play(FadeIn(dots_f), FadeIn(brf), LaggedStart(*[TransformFromCopy(d, c) for d, c in zip(dots_f, colf)],
                                                   lag_ratio=0.08), at=T.behave + 0.9, dur=1.1)

    # ── add two curves: heights add point by point, exactly like the columns ──
    cg = dashed(plot(g, 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200, opacity=0.8))
    sticks_g = VGroup(*[Line(pt(GO, 1, (GUX * x, 0)), pt(GO, 1, (GUX * x, GUY * g(x))), color=C.fn,
                             stroke_width=C.thin * 1.4) for x in X8])
    stacked_g = VGroup(*[Line(pt(GO, 1, (GUX * x, GUY * f(x))), pt(GO, 1, (GUX * x, GUY * (f(x) + g(x)))),
                              color=C.text, stroke_width=C.thin * 1.4) for x in X8])
    colg = column(g(X8), CX[1], C.fn)
    brg = col_brackets(CX[1], CY, CH, width=1.25)
    plus = tex("+", size=44).move_to([(CX[0] + CX[1]) / 2, CY, 0])
    ta = T.add
    m.play(Create(cg), at=ta, dur=0.9)
    m.play(LaggedStart(*[Create(sk) for sk in sticks_g], lag_ratio=0.08), FadeIn(brg), FadeIn(plus),
           LaggedStart(*[FadeIn(c) for c in colg], lag_ratio=0.08), at=ta + 0.7, dur=1.0)
    m.play(*[ReplacementTransform(a, b) for a, b in zip(sticks_g, stacked_g)], at=ta + 1.9, dur=1.0)
    csum = plot(lambda x: f(x) + g(x), 0, 2 * np.pi, GO, GUX, GUY, C.text, n=200)
    m.play(Create(csum), at=ta + 3.0, dur=1.0)
    cols = column(f(X8) + g(X8), CX[2], C.text)
    brs = col_brackets(CX[2], CY, CH, width=1.25)
    eq = tex("=", size=44).move_to([(CX[1] + CX[2]) / 2, CY, 0])
    m.play(FadeIn(brs), FadeIn(eq), at=ta + 3.1, dur=0.5)
    m.play(LaggedStart(*[ReplacementTransform(VGroup(a.copy(), b.copy()), c)
                         for a, b, c in zip(colf, colg, cols)], lag_ratio=0.1), at=ta + 3.4, dur=1.4)
    for c in cols:                                          # re-file the cells under their column, so it can fade
        m.remove(c, at=ta + 4.75)
    m.add(cols, at=ta + 4.75)

    # ── scale a curve by three: every entry scales by three ──
    tsc = T.scale
    assert ta + 3.4 - C.lead + 1.4 < ta + 4.75 < tsc - C.lead      # the re-filing sits between the sum and the fade
    gone = VGroup(cg, stacked_g, csum, colg, brg, plus, cols, brs, eq)
    m.play(FadeOut(gone), at=tsc, dur=0.5)
    c3 = plot(lambda x: 3 * f(x), 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200)
    ghost = plot(f, 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200, opacity=0.25)
    dots_3 = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * 3 * f(x))), radius=0.06, color=C.fn) for x in X8])
    col3 = column(3 * f(X8), CX[0], C.fn)
    x3 = tex(r"\times 3", size=40).next_to(brf, UP, buff=0.25)
    m.add(ghost, at=tsc + 0.2)
    m.play(Transform(cf, c3), Transform(dots_f, dots_3), at=tsc + 0.3, dur=1.2)
    m.play(FadeIn(x3, shift=0.1 * RIGHT), at=tsc + 0.3, dur=0.5)
    m.play(*[Transform(a, b) for a, b in zip(colf, col3)], at=tsc + 1.0, dur=1.0)

    # ── the derivative respects both: tangents at one point ──
    tw = T.watch
    m.play(FadeOut(VGroup(cf, dots_f, ghost, colf, brf, x3)), at=tw - 0.3, dur=0.5)
    f1 = plot(f, 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200)
    g1 = dashed(plot(g, 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200, opacity=0.8))
    s1 = plot(lambda x: f(x) + g(x), 0, 2 * np.pi, GO, GUX, GUY, C.text, n=200)
    m.play(FadeIn(VGroup(f1, g1, s1)), at=tw + 0.1, dur=0.7)
    marker = DashedLine(pt(GO, 1, (GUX * X0, -1.9)), pt(GO, 1, (GUX * X0, 1.9)), color=C.muted,
                        stroke_width=C.thin, dash_length=0.08)
    tf, tg, ts = (tangent(f, df, X0, GUY), tangent(g, dg, X0, GUY), tangent(lambda x: f(x) + g(x),
                                                                            lambda x: df(x) + dg(x), X0, GUY))
    tsum = T.slope_sum
    m.play(Create(marker), at=tsum - 0.6, dur=0.5)
    m.play(LaggedStart(Create(tf), Create(tg), Create(ts), lag_ratio=0.3), at=tsum, dur=1.2)

    R1 = tex(r"(f+g)'", r"=", r"f'", r"+", r"g'", size=50, colors={0: C.dfn, 2: C.dfn, 4: C.dfn})
    R1.move_to([3.6, 1.7, 0])
    N1 = tex(fmt(round(df(X0) + dg(X0), 2)), r"=", fmt(round(df(X0), 2)), r"+", fmt(round(dg(X0), 2)), size=40,
             color=C.muted)
    N1.next_to(R1, DOWN, buff=0.3)
    N1.shift((R1[1].get_center()[0] - N1[1].get_center()[0]) * RIGHT)
    m.play(Write(R1), at=tsum + 0.5, dur=1.0)
    m.play(FadeIn(N1, shift=0.1 * UP), at=tsum + 1.4, dur=0.6)

    t3 = T.slope_three
    m.play(FadeOut(VGroup(g1, s1, tg, ts)), at=t3 - 0.4, dur=0.5)
    f3 = plot(lambda x: 3 * f(x), 0, 2 * np.pi, GO, GUX, GUY, C.fn, n=200)
    m.play(f1.animate.set_stroke(opacity=0.25), FadeIn(f3), at=t3, dur=0.8)
    t3t = tangent(lambda x: 3 * f(x), lambda x: 3 * df(x), X0, GUY)
    m.play(Create(t3t), at=t3 + 0.7, dur=0.7)
    R2 = tex(r"(3f)'", r"=", r"3", r"f'", size=50, colors={0: C.dfn, 3: C.dfn})
    R2.move_to([3.6, -0.6, 0])
    R2.shift((R1[1].get_center()[0] - R2[1].get_center()[0]) * RIGHT)
    N2 = tex(fmt(round(3 * df(X0), 2)), r"=", r"3 \cdot (" + fmt(round(df(X0), 2)) + ")", size=40, color=C.muted)
    N2.next_to(R2, DOWN, buff=0.3)
    N2.shift((R2[1].get_center()[0] - N2[1].get_center()[0]) * RIGHT)
    m.play(Write(R2), at=t3 + 1.0, dur=1.0)
    m.play(FadeIn(N2, shift=0.1 * UP), at=t3 + 1.8, dur=0.6)

    # ── those two rules ... are the rules every matrix obeys ──
    tr = T.two_rules
    m.play(FadeOut(VGroup(axis, f1, f3, tf, t3t, marker, N1, N2)), at=tr - 0.3, dur=0.6)
    L1 = R1.copy().move_to([-3.3, 1.0, 0])
    L2 = R2.copy()
    L2.move_to([-3.3, -0.6, 0]).shift((L1[1].get_center()[0] - L2[1].get_center()[0]) * RIGHT)
    m.play(Transform(R1, L1), Transform(R2, L2), at=tr + 0.1, dur=1.0)
    A1 = tex(r"A", r"(u+v)", r"=", r"A", r"u", r"+", r"A", r"v", size=50, colors={0: C.op, 3: C.op, 6: C.op})
    A2 = tex(r"A", r"(3u)", r"=", r"3", r"A", r"u", size=50, colors={0: C.op, 4: C.op})
    A1.move_to([3.4, 1.0, 0])
    A2.move_to([3.4, -0.6, 0]).shift((A1[2].get_center()[0] - A2[2].get_center()[0]) * RIGHT)
    te = T.every_matrix
    m.play(FadeIn(A1, shift=0.15 * LEFT), at=te, dur=0.7)
    m.play(FadeIn(A2, shift=0.15 * LEFT), at=te + 0.5, dur=0.7)

    # ── so the derivative should be a matrix ──
    ts_ = T.should_be
    D1 = tex(r"D", r"(f+g)", r"=", r"D", r"f", r"+", r"D", r"g", size=50, colors={0: C.op, 3: C.op, 6: C.op})
    D2 = tex(r"D", r"(3f)", r"=", r"3", r"D", r"f", size=50, colors={0: C.op, 4: C.op})
    D1.move_to(L1).shift((L1[1].get_center()[0] - D1[2].get_center()[0]) * RIGHT)
    D2.move_to(L2).shift((L1[1].get_center()[0] - D2[2].get_center()[0]) * RIGHT)
    m.play(ReplacementTransform(R1, D1), ReplacementTransform(R2, D2), at=ts_ - 1.6, dur=1.0)
    Dq = tex(r"D", r"=", size=60, colors={0: C.op})
    from shots import brackets
    brq = brackets(1.3, 0.9)
    qm = tex("?", size=56, color=C.muted)
    Dg = VGroup(Dq, VGroup(brq, qm)).arrange(RIGHT, buff=0.3).move_to([0, -2.6, 0])
    qm.move_to(brq)
    m.play(FadeIn(Dg, shift=0.15 * UP), at=ts_ + 0.6, dur=0.8)
    m.play(Indicate(Dg, color=C.op, scale_factor=1.08), at=T.build_it, dur=0.8)
    # clear the stage in the pause before chapter 2
    m.play(FadeOut(VGroup(D1, D2, A1, A2, Dg)), at=T.build_it + 1.0, dur=0.5)
    assert T.build_it + 1.0 - C.lead + 0.5 < T.cut_ch2
