"""Outro: where the analogy breaks. A real function has a value at every point: the column grows past the frame, R^∞.
D is no longer a finite matrix, so there is no det. On smooth functions every λ is an eigenvalue (e^{λx} works for any
λ). Going from a thousand points to every point takes a limit. Making it rigorous is functional analysis, the maths
under quantum mechanics, where observables are operators: Ĥψ = Eψ."""
from aion import *

from beats import T
from shots import chapter_header, backdrop, bar_column, col_brackets, finish, plot, pt, samples, tex

E = "easy_ease"
CX, CY, CHT = -3.6, -0.3, 4.0                            # the column


@scene(T.cut_outro, T.cut_recap)
def s15_infinity(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 0, T.cut_outro)                     # chapter badge row + title (fills the cut)

    # ── is calculus secretly linear algebra? mostly ──
    q = tex(r"\text{calculus}", r"\;\overset{?}{=}\;", r"\text{linear algebra}", size=56,
            colors={0: C.fn, 2: C.op}).move_to([0, 0.4, 0])
    m.play(FadeIn(q, shift=0.1 * DOWN), at=T.secretly + 0.3, dur=0.8)
    approx = tex(r"\text{calculus}", r"\;\approx\;", r"\text{linear algebra}", size=56,
                 colors={0: C.fn, 2: C.op}).move_to(q)
    m.play(TransformMatchingTex(q, approx), at=T.mostly + 0.2, dur=0.8)
    m.play(FadeOut(approx, shift=0.4 * UP), at=T.every_point2 - 1.0, dur=0.6)

    # ── a value at every point: the column grows past the frame ──
    xs = samples(1000)
    col = VGroup(col_brackets(CX, CY, CHT, width=1.2), bar_column(np.sin(xs), CX, CY, height=CHT, width=0.6))
    dim = tex(r"\in", r"\mathbb{R}^{1000}", size=48, colors={1: C.fn}).next_to([CX + 0.7, CY, 0], RIGHT, buff=0.25)
    m.play(FadeIn(col), FadeIn(dim), at=T.every_point2 - 0.3, dur=0.8)
    dinf = tex(r"\in", r"\mathbb{R}^{\infty}", size=48, colors={1: C.fn}).move_to(dim, aligned_edge=LEFT)
    m.play(col.animate.stretch(3.2, 1), ReplacementTransform(dim, dinf), at=T.infinite + 0.2, dur=1.8, ease=E)
    # then it scrolls, endlessly: there is always more of it
    t1, te0 = T.infinite + 2.1, T.every_eigenvalue - 0.6
    m.remove(col[1], at=t1)
    bop = keys((te0, 1.0), (te0 + 0.5, 0.0), lead=0)
    m.redraw(lambda t: bar_column(np.sin(xs + 0.55 * (t - t1)), CX, CY, height=CHT * 3.2, width=0.6,
                                  opacity=float(bop(t))), during=(t1, te0 + 0.5))

    # ── D is no longer a finite matrix: no determinant ──
    det = tex(r"\det D", size=60, color=C.op).move_to([3.0, 0.6, 0])
    m.play(FadeIn(det), at=T.no_det - 0.6, dur=0.5)
    strike = Line(det.get_corner(DL) + 0.12 * DL, det.get_corner(UR) + 0.12 * UR, color=C.text, stroke_width=C.stroke)
    m.play(Create(strike), at=T.no_det + 0.3, dur=0.5)

    # ── every number is an eigenvalue: e^{λx} for any λ ──
    te = T.every_eigenvalue
    m.play(FadeOut(VGroup(col[0], dinf, det, strike)), at=te - 0.6, dur=0.5)
    FO, FUX, FUY = (0.0, -2.2), 1.6, 0.9
    ax = VGroup(Line(pt(FO, 1, (-3.0 * FUX, 0)), pt(FO, 1, (3.0 * FUX, 0)), color=C.axis, stroke_width=C.thin),
                Line(pt(FO, 1, (0, -0.2)), pt(FO, 1, (0, 4.6)), color=C.axis, stroke_width=C.thin))
    lams = np.linspace(-1.5, 1.5, 13)
    fan = VGroup()
    for lam in lams:
        xs_ = np.linspace(-3, 3, 400)
        ok = xs_[np.exp(lam * xs_) <= 4.8]
        fan.add(plot(lambda x, lam=lam: np.exp(lam * x), float(ok.min()), float(ok.max()), FO, FUX, FUY, C.eigen,
                     width=C.stroke - 0.5, opacity=0.85))
    eig = tex(r"D", r"\,e^{\lambda x}", r"=", r"\lambda", r"\,e^{\lambda x}", r"\quad", r"\lambda \in \mathbb{C}",
              size=48, colors={0: C.op, 1: C.eigen, 3: C.eigen, 4: C.eigen, 6: C.eigen}).move_to([0, 3.1, 0])
    m.play(FadeIn(ax), LaggedStart(*[Create(c) for c in fan], lag_ratio=0.08), at=te - 0.1, dur=2.0)
    m.play(FadeIn(eig, shift=0.1 * DOWN), at=te + 0.9, dur=0.7)

    # ── a thousand points to every point: a limit ──
    tl = T.takes_limit
    m.play(FadeOut(VGroup(ax, fan, eig)), at=tl - 2.4, dur=0.6)
    GO, GUX, GUY = (-3.2, -0.6), 1.0, 1.3
    curve = plot(np.sin, 0, 2 * np.pi, GO, GUX, GUY, C.fn)
    d8 = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * np.sin(x))), radius=0.07, color=C.fn) for x in samples(8)])
    d50 = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * np.sin(x))), radius=0.04, color=C.fn) for x in samples(50)])
    gax = Line(pt(GO, 1, (-0.2, 0)), pt(GO, 1, (GUX * 2 * np.pi + 0.2, 0)), color=C.axis, stroke_width=C.thin)
    m.play(FadeIn(gax), LaggedStart(*[FadeIn(d, scale=0.5) for d in d8], lag_ratio=0.08), at=tl - 1.7, dur=0.8)
    m.play(FadeOut(d8), FadeIn(d50), at=tl - 0.6, dur=0.6)
    m.play(FadeOut(d50), Create(curve), at=tl + 0.2, dur=1.0)
    lim = tex(r"\lim_{h\to 0}", size=60).move_to([-2.4 + 2.6, 2.6, 0])
    m.play(FadeIn(lim, shift=0.1 * DOWN), at=tl, dur=0.6)
    m.play(Indicate(lim, color=C.shift, scale_factor=1.15), at=T.cant_do + 0.2, dur=0.9)

    # ── functional analysis: operators on infinite-dimensional spaces; quantum mechanics ──
    tf = T.functional
    m.play(FadeOut(VGroup(gax, curve)), lim.animate.move_to([-3.8, 2.6, 0]), at=tf - 0.6, dur=0.7, ease=E)
    op = tex(r"D", r":", r"C^\infty", r"\to", r"C^\infty", size=56, colors={0: C.op, 2: C.fn, 4: C.fn}).move_to(
        [0, 0.8, 0])
    m.play(FadeIn(op, shift=0.1 * UP), at=tf + 0.4, dur=0.7)
    qm = tex(r"\hat H", r"\,\psi", r"=", r"E", r"\,\psi", size=60, colors={0: C.op, 1: C.eigen, 3: C.eigen,
                                                                              4: C.eigen}).move_to([0, -1.2, 0])
    m.play(FadeIn(qm, shift=0.1 * UP), at=T.quantum + 0.3, dur=0.7)
    m.play(FadeOut(VGroup(lim, op, qm)), at=T.cut_recap - 0.6, dur=0.5)
    finish(s)
