"""Ch7: the exponential of the derivative. e^x = 1 + x + x^2/2! + ...; the same series works for matrices, so put
hD in the exponent. Applied to a cubic, e^{hD} p = p + h p' + h^2/2 p'' + h^3/6 p''' (D^4 p = 0, so it stops), which
is exactly p(x + h): a shift. The asterisk: it needs the Taylor series to add back up to f; e^{-1/x^2} is smooth, every
derivative at 0 is 0, so its Taylor series at 0 is the zero function."""
import sympy as sp

from aion import *

from beats import T
from shots import chapter_header, backdrop, finish, plot, pt, tex

E = "easy_ease"
HH = sp.Rational(6, 5)                                   # the shift h = 1.2, exact for the sympy check
_x = sp.symbols("x")
_p = sp.Rational(3, 10) * _x ** 3 - _x + sp.Rational(1, 2)
_sums = [sum(HH ** k / sp.factorial(k) * sp.diff(_p, _x, k) for k in range(n + 1)) for n in range(4)]
assert sp.expand(_sums[3] - _p.subs(_x, _x + HH)) == 0 and sp.diff(_p, _x, 4) == 0
_b = sp.exp(-1 / _x ** 2)
assert all(sp.limit(sp.diff(_b, _x, n), _x, 0) == 0 for n in range(4))
H = float(HH)
SUMS = [sp.lambdify(_x, s_, "numpy") for s_ in _sums]
p = SUMS[0]

GO, GUX, GUY = (0.3, -1.1), 1.1, 0.5                     # the cubic's graph
XA, XB = -3.0, 2.6
YL = (-3.6, 4.0)


def graph(f, color, width=None, dashed=False, a=XA, b=XB):
    xs = np.linspace(a, b, 2000)                          # draw only where it stays on the axes (no clipped stubs)
    ok = xs[(f(xs) >= YL[0]) & (f(xs) <= YL[1])]
    c = plot(f, float(ok.min()), float(ok.max()), GO, GUX, GUY, color, width=width)
    return DashedVMobject(c, num_dashes=60) if dashed else c


@scene(T.cut_ch7, T.cut_outro)
def s14_shift(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 7, T.cut_ch7)                     # chapter badge row + title (fills the cut)

    # ── e^x as a series; the same series for matrices ──
    ex = tex(r"e^x", r"=", r"1", r"+", r"x", r"+", r"\frac{x^2}{2!}", r"+", r"\cdots", size=54).move_to([0, 3.0, 0])
    m.play(Write(ex), at=T.exp_series + 0.2, dur=1.4)
    eA = tex(r"e^A", r"=", r"I", r"+", r"A", r"+", r"\frac{A^2}{2!}", r"+", r"\cdots", size=54,
             colors={0: C.op, 4: C.op, 6: C.op}).move_to([0, 1.6, 0])
    m.play(FadeIn(eA, shift=0.1 * DOWN), at=T.for_matrices + 0.3, dur=0.8)

    # ── put the derivative in the exponent ──
    ehd = tex(r"e^{hD}", r"=", r"1", r"+", r"hD", r"+", r"\frac{h^2D^2}{2!}", r"+", r"\cdots", size=54,
              colors={0: C.op, 4: C.op, 6: C.op}).move_to([0, 3.0, 0])
    for i in (0, 4, 6):
        ehd[i].set_color(C.op)
    m.play(Indicate(eA[0], color=C.op, scale_factor=1.3), at=T.exponent + 0.6, dur=0.8)
    m.play(FadeOut(ex, shift=0.3 * UP), ReplacementTransform(eA, ehd), at=T.ehd - 0.2, dur=1.0)
    for j, i in enumerate((2, 4, 6, 8)):                  # read the series term by term
        m.play(Indicate(ehd[i], color=C.op if i in (4, 6) else C.text, scale_factor=1.2), at=T.ehd + 1.7 + 1.0 * j,
               dur=0.8)

    # ── apply it to a cubic: the Taylor series ──
    ta = T.apply
    app = tex(r"e^{hD}p", r"=", r"p", r"+", r"h\,p'", r"+", r"\tfrac{h^2}{2}p''", r"+", r"\tfrac{h^3}{6}p'''",
              size=48, colors={0: C.op, 2: C.fn, 4: C.fn, 6: C.fn, 8: C.fn}).move_to([0, 1.9, 0])
    ax = VGroup(Line(pt(GO, 1, (XA * GUX - 0.2, 0)), pt(GO, 1, (XB * GUX + 0.3, 0)), color=C.axis, stroke_width=C.thin),
                Line(pt(GO, 1, (0, YL[0] * GUY)), pt(GO, 1, (0, YL[1] * GUY)), color=C.axis, stroke_width=C.thin))
    cp = graph(p, C.fn)
    pl = tex(r"p", size=40, color=C.fn).next_to(pt(GO, 1, (XB * GUX, p(XB) * GUY)), RIGHT, buff=0.12)
    pieces = [app[0:3]] + [app[2 * n + 1:2 * n + 3] for n in (1, 2, 3)]
    m.play(FadeIn(ax), Create(cp), FadeIn(pl), FadeIn(pieces[0]), at=ta - 0.2, dur=1.0)
    run = graph(p, C.shift)
    m.add(run, at=ta + 0.85)
    term_t = [ta + 1.6, ta + 3.6, T.taylor + 0.2]
    for n, tn in enumerate(term_t, start=1):
        m.play(FadeIn(pieces[n]), Transform(run, graph(SUMS[n], C.shift)), at=tn, dur=1.0, ease=E)
    m.remove(*pieces, at=T.taylor + 1.25)                 # re-file the pieces as one formula
    m.add(app, at=T.taylor + 1.25)
    m.play(Indicate(app[2:], color=C.fn, scale_factor=1.04), at=T.taylor + 1.4, dur=0.9)
    stop = tex(r"D^4 p", r"=", r"0", size=36, colors={0: C.op}).next_to(app, DOWN, buff=0.25).align_to(app, RIGHT)
    m.play(FadeIn(stop), at=T.taylor + 2.2, dur=0.5)

    # ── it adds up to p(x + h) exactly ──
    tx = T.x_plus_h
    tgt = graph(lambda x: p(x + H), C.text, width=C.thin * 1.6, dashed=True)
    tl = tex(r"p(x+h)", size=40, color=C.shift).next_to(pt(GO, 1, (-2.0 * GUX, p(-2.0 + H) * GUY)), UP, buff=0.2)
    m.play(Create(tgt), FadeIn(tl), at=tx, dur=1.0)

    # ── so e^{hD} is a shift: the graph slides by h ──
    tsft = T.shift
    res = tex(r"e^{hD}", r"\,p(x)", r"=", r"p(x+h)", size=54, colors={0: C.op, 1: C.fn, 3: C.shift}).move_to(app)
    m.play(FadeOut(ehd, shift=0.3 * UP), ReplacementTransform(app, res), at=tsft + 0.2, dur=1.0)
    m.play(res.animate.move_to([0, 3.0, 0]), at=tsft + 1.4, dur=0.6)
    res2 = res
    x0 = 2.2                                             # the slide: the point at x0 moves to x0 - h
    a0 = pt(GO, 1, (x0 * GUX, p(x0) * GUY))
    harr = Arrow(a0, a0 + np.array([-H * GUX, 0, 0]), buff=0, color=C.shift, stroke_width=C.stroke + 1,
                 tip_length=0.2)
    hl = tex(r"h", size=40, color=C.shift).next_to(harr, UP, buff=0.1)
    slide = cp.copy().set_stroke(color=C.fn, opacity=0.9)
    m.play(GrowArrow(harr), FadeIn(hl), at=T.slides_h + 0.2, dur=0.6)
    m.add(slide, at=T.slides_h + 0.8)
    m.play(slide.animate.shift(H * GUX * LEFT), at=T.slides_h + 0.9, dur=1.6, ease=E)
    m.play(Indicate(run, color=C.shift, scale_factor=1.0), Indicate(res2[3], color=C.shift), at=T.tiny + 0.4, dur=1.0)

    # ── the asterisk: functions whose Taylor series adds back up ──
    tk = T.asterisk
    m.play(FadeOut(VGroup(ax, cp, pl, run, tgt, tl, harr, hl, slide, stop)), at=tk - 0.4, dur=0.6)
    star = tex(r"{}^{*}", size=90, color=C.shift).next_to(res2.copy().move_to([0, 3.0, 0]), RIGHT, buff=0.08,
                                                           aligned_edge=UP)
    m.play(FadeIn(star, scale=0.6), at=tk + 0.2, dur=0.5)
    ok = VGroup(*[tex(sx, size=44, color=C.fn).move_to([x, 1.8, 0]) for sx, x in
                  ((r"p(x)", -2.4), (r"e^x", 0.0), (r"\sin x", 2.4))],
                tex(r"\checkmark", size=48, color=C.dfn).move_to([3.9, 1.8, 0]))
    m.play(FadeIn(ok, shift=0.1 * DOWN), at=T.only_works + 0.8, dur=0.7)
    minis = VGroup()
    for j, (i, fn, a, b, sy) in enumerate(((0, lambda x: 0.3 * x ** 3 - x + 0.5, -2.2, 2.0, 0.16),
                                           (1, np.exp, -2.5, 1.3, 0.12), (2, np.sin, -np.pi, np.pi, 0.3))):
        c = ok[i].get_center()
        o, wd = (c[0], 0.75), 1.5                           # each mini graph sits under its name, 0.95 wide
        ux = wd / (b - a)
        mini = VGroup(Line(pt(o, 1, (-wd / 2, 0)), pt(o, 1, (wd / 2, 0)), color=C.axis, stroke_width=C.thin * 0.8),
                      plot(fn, a, b, (o[0] - ux * (a + b) / 2, o[1]), ux, sy, C.fn, width=C.stroke - 1.5))
        minis.add(mini)
        m.play(FadeIn(mini[0]), Create(mini[1]), at=T.only_works + 1.8 + 0.7 * j, dur=0.7)

    # ── a smooth function where it fails: e^{−1/x²} ──
    BO, BUX, BUY = (0.0, -2.2), 1.05, 2.0
    bax = VGroup(Line(pt(BO, 1, (-5.2, 0)), pt(BO, 1, (5.2, 0)), color=C.axis, stroke_width=C.thin),
                 Line(pt(BO, 1, (0, -0.4)), pt(BO, 1, (0, 2.9)), color=C.axis, stroke_width=C.thin))
    f = lambda x: np.exp(-1 / np.maximum(x * x, 1e-9))           # noqa: E731
    bc = plot(f, -4.8, 4.8, BO, BUX, BUY, C.fn, n=400)
    bl = tex(r"f(x)", r"=", r"e^{-1/x^2}", size=44, colors={0: C.fn, 2: C.fn}).move_to([3.4, 1.7, 0])
    tf = T.fails
    m.play(FadeOut(ok), FadeOut(minis), FadeIn(bax), at=tf - 0.2, dur=0.6)
    m.play(Create(bc), at=tf + 0.4, dur=1.4)
    m.play(FadeIn(bl, shift=0.1 * LEFT), at=T.bump + 0.2, dur=0.6)
    der = tex(r"f^{(n)}(0)", r"=", r"0", size=40, colors={0: C.fn}).next_to(bl, DOWN, buff=0.35, aligned_edge=LEFT)
    m.play(FadeIn(der, shift=0.1 * UP), at=T.bump + 3.2, dur=0.6)
    tz = T.zero_series
    zl = DashedVMobject(Line(pt(BO, 1, (-4.8 * BUX, 0)), pt(BO, 1, (4.8 * BUX, 0)), color=C.shift,
                             stroke_width=C.stroke + 1), num_dashes=50)
    tl0 = tex(r"T(x)", r"=", r"0", size=40, colors={0: C.shift}).next_to(pt(BO, 1, (-4.6 * BUX, 0)), UP, buff=0.2)
    neq = tex(r"T(x)", r"\neq", r"f(x)", size=40, colors={0: C.shift, 2: C.fn}).next_to(der, DOWN, buff=0.35,
                                                                                      aligned_edge=LEFT)
    m.play(Create(zl), FadeIn(tl0), at=tz - 0.3, dur=0.9)
    m.play(FadeIn(neq, shift=0.1 * UP), at=tz + 1.0, dur=0.6)
    m.play(FadeOut(VGroup(res2, star, bax, bc, bl, der, zl, tl0, neq)), at=T.cut_outro - 0.7, dur=0.6)
    finish(s)
