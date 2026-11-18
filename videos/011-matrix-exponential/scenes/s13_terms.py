"""s13 terms (ch3): the series as arrows. For A = πJ and v = (1, 0), the terms A^k v / k! go tip to tail: v, Av (π, up),
A²v/2! (4.93, left), A³v/3! (5.17, down), ... They swing out, overshoot and spiral in onto −v = e^A v. The sizes π^k/k!
grow to k = 3, then the factorials win; the top-left entry's partial sums settle on −1. And the element-wise guess
never stood a chance: A² mixes every entry with every other (row times column), not each entry squared."""
from math import factorial

from aion import *

from beats import T
from shots import E, HOOK, arrow, backdrop, backed, finish, lab, live, p3, tex
from verify import series

O, U = np.array([-2.25, -0.45]), 0.95                  # the spiral's origin and unit
V0 = np.array([1.0, 0.0])
K = 12
TERMS = [np.linalg.matrix_power(HOOK, k) @ V0 / factorial(k) for k in range(K)]
SUMS = np.cumsum(TERMS, axis=0)
assert np.allclose(SUMS[-1], [-1, 0], atol=2e-3)
TL = [float(series(HOOK, k)[0, 0]) for k in range(K)]  # top-left entry partial sums
SIZES = [np.pi ** k / factorial(k) for k in range(K)]
BX0, BY0, BW, BS = 1.55, -3.25, 0.4, 0.4             # bar chart: left, base, pitch, height per unit


def W(v):
    return O + U * np.asarray(v, float)


@scene(T.cut_terms, T.cut_ch4)
def s13_terms(s):
    backdrop(s)
    m = s.manim(z=2)

    # ── A² means do A, then do A again ──
    hd = tex(r"A^2\mathbf v", "=", r"A\,(A\mathbf v)", size=50, colors={0: C.gen, 2: C.gen}).move_to([0, 3.3, 0])
    m.play(FadeIn(hd[:2], shift=0.1 * DOWN), at=T.powers + 0.4, dur=0.6)
    m.play(FadeIn(hd[2:], shift=0.1 * DOWN), at=T.do_twice + 0.4, dur=0.6)
    hero = tex(r"e^{A}\mathbf v", "=", r"\mathbf v", "+", r"A\mathbf v", "+", r"\tfrac{A^2\mathbf v}{2!}", "+",
               r"\tfrac{A^3\mathbf v}{3!}", "+", r"\cdots", size=46,
               colors={0: C.flow, 2: C.vec, 4: C.gen, 6: C.gen, 8: C.gen}).move_to([0, 3.3, 0])
    m.play(FadeOut(hd, shift=0.1 * UP), FadeIn(hero, shift=0.1 * UP), at=T.arrows - 0.2, dur=0.7)

    # ── the plane and the target −v ──
    ax = VGroup(Line(p3(W((-4.6, 0))), p3(W((2.0, 0))), color=C.muted, stroke_width=C.thin),
                Line(p3(W((0, -2.4))), p3(W((0, 3.4))), color=C.muted, stroke_width=C.thin))
    goal = Circle(radius=0.16, color=C.flow, stroke_width=C.stroke).move_to(p3(W((-1, 0))))
    exact = Arc(radius=U, start_angle=0, angle=PI, arc_center=p3(O), color=C.flow, stroke_width=C.thin + 0.4,
                stroke_opacity=0.5)
    m.play(Create(ax), at=T.arrows, dur=0.7)
    m.play(FadeIn(goal), Create(exact), at=T.arrows + 0.8, dur=0.8)

    # ── terms tip to tail on a steady cadence ──
    ats = [T.first_v + 0.2, T.Av_term + 0.2] + [T.each_after + 0.4 + 1.1 * (k - 2) for k in range(2, K)]
    arrows = VGroup()
    names = [r"\mathbf v", r"A\mathbf v", r"\tfrac{A^2\mathbf v}{2!}", r"\tfrac{A^3\mathbf v}{3!}"]
    offs = [DOWN, RIGHT, UP, LEFT]
    labs = VGroup()
    for k in range(K):
        a = np.zeros(2) if k == 0 else SUMS[k - 1]
        b = SUMS[k]
        col = C.vec if k == 0 else C.gen
        ar = arrow(W(a), W(b), col, width=C.stroke + (1 if k < 6 else 0), tip=0.22)
        arrows.add(ar)
        m.play(GrowArrow(ar), at=ats[k], dur=0.5 if k < 6 else 0.35, ease=E)
        if k < 4:
            lb = backed(tex(names[k], size=36, color=col), buff=0.04).next_to(ar, offs[k], buff=0.1)
            labs.add(lb)
            m.play(FadeIn(lb), at=ats[k] + 0.35, dur=0.4)
    m.play(FadeOut(labs), at=ats[6], dur=0.6)

    def head(t):
        k = sum(1 for a in ats if t >= a + 0.45) - 1
        if k < 0 or t > T.elementwise - 0.7:
            return VGroup()
        return Dot(p3(W(SUMS[k])), radius=0.1, color=C.flow)
    live(m, head, (ats[0], ats[-1] + 0.6), (T.elementwise - 0.75, T.elementwise - 0.6))
    s.camera.push(at=T.each_after, zoom=0.94, dur=1.5)
    s.camera.push(at=T.landing, zoom=1.0, dur=1.5)
    land = backed(tex(r"e^{A}\mathbf v", "=", r"-\mathbf v", size=40, colors={0: C.flow, 2: C.flow}),
                  buff=0.05).next_to(goal, DL, buff=0.15)
    m.play(FadeIn(land, shift=0.1 * UP), at=T.landing + 0.6, dur=0.6)

    # ── term sizes π^k/k!: up to k = 3, then the factorials win ──
    bars = VGroup()
    for k in range(K):
        h = max(BS * SIZES[k], 0.02)
        bars.add(Rectangle(width=BW * 0.72, height=h, stroke_width=0, fill_color=C.gen if k else C.vec,
                           fill_opacity=0.9).move_to(p3((BX0 + BW * k, BY0 + h / 2))))
    base = Line(p3((BX0 - 0.3, BY0)), p3((BX0 + BW * K, BY0)), color=C.muted, stroke_width=C.thin)
    bt = lab("size of each term", 24, C.muted).next_to(base, DOWN, buff=0.18)
    m.play(Create(base), FadeIn(bt), at=T.first_v, dur=0.5)
    for k in range(K):
        m.play(GrowFromEdge(bars[k], DOWN), at=ats[k] + 0.2, dur=0.35)
    gtag = lab("grow", 26, C.gen).move_to(p3((BX0 + BW * 1.5, BY0 + BS * 5.6)))
    ctag = lab("collapse", 26, C.muted).move_to(p3((BX0 + BW * 7.5, BY0 + BS * 2.3)))
    m.play(FadeIn(gtag), *[Indicate(b, color=C.gen, scale_factor=1.08) for b in bars[1:4]], at=T.grow + 0.3, dur=0.8)
    m.play(FadeIn(ctag), *[b.animate.set_fill(color=C.muted) for b in bars[4:]], at=T.factorials + 0.4, dur=0.8)

    # the top-left entry's partial sums
    tl = VGroup(tex(r"\big(e^{A}\big)_{11}", r"\approx", size=42, colors={0: C.flow}),
                DecimalNumber(TL[0], num_decimal_places=2, font_size=42, color=C.flow)).arrange(RIGHT, buff=0.2)
    tl.move_to([4.15, 0.55, 0])
    m.play(FadeIn(tl), at=T.first_v + 0.2, dur=0.5)

    def tick(g, t):
        k = max(sum(1 for a in ats if t >= a + 0.45) - 1, 0)
        g[1].set_value(TL[k])
    m.drive(tl, tick, during=(ats[0], ats[-1] + 0.6))
    m.play(Circumscribe(tl[1], color=C.flow, buff=0.08), at=T.settles + 0.8, dur=1.0)
    conv = backed(lab("any square matrix: the series always converges", 28, C.text)).move_to([2.6, 2.3, 0])
    m.play(FadeIn(conv, shift=0.1 * DOWN), at=T.converges + 0.2, dur=0.6)

    # ── why the element-wise guess failed: A² mixes every entry with every other ──
    spiral = VGroup(ax, goal, exact, arrows, land, bars, base, bt, gtag, ctag, tl, conv, hero)
    m.play(FadeOut(spiral), at=T.elementwise - 0.7, dur=0.6)
    entries = [["0", r"-\pi"], [r"\pi", "0"]]
    Ma = Mat(entries, colors=C.gen, size=40, h_buff=0.9, v_buff=0.7)
    Mb = Mat(entries, colors=C.gen, size=40, h_buff=0.9, v_buff=0.7)
    Mr = Mat([[r"-\pi^2", "0"], ["0", r"-\pi^2"]], colors=C.gen, size=40, h_buff=1.1, v_buff=0.7)
    left = VGroup(Ma, Mb, tex("=", size=44), Mr).arrange(RIGHT, buff=0.22).move_to([-3.3, 0.3, 0])
    Mw = Mat([["0", r"\pi^2"], [r"\pi^2", "0"]], colors=C.wrong, size=40, h_buff=1.0, v_buff=0.7)
    right = VGroup(Mw, lab("each entry squared", 26, C.wrong)).arrange(DOWN, buff=0.35).move_to([4.6, 0.1, 0])
    ne = tex(r"\ne", size=60, color=C.wrong).move_to([1.85, 0.3, 0])
    lt = lab("row times column", 26, C.gen).next_to(left, DOWN, buff=0.45)
    m.play(FadeIn(left, shift=0.1 * UP), at=T.elementwise + 0.3, dur=0.7)
    rb = SurroundingRectangle(VGroup(Ma.cell(0, 0), Ma.cell(0, 1)), color=C.vec, buff=0.12, stroke_width=C.thin + 0.8)
    cb = SurroundingRectangle(VGroup(Mb.cell(0, 0), Mb.cell(1, 0)), color=C.vec, buff=0.12, stroke_width=C.thin + 0.8)
    eb = SurroundingRectangle(Mr.cell(0, 0), color=C.vec, buff=0.1, stroke_width=C.thin + 0.8)
    m.play(Create(rb), Create(cb), FadeIn(lt), at=T.mixes + 0.2, dur=0.6)
    m.play(TransformFromCopy(VGroup(rb, cb), eb), at=T.mixes + 1.0, dur=0.7, ease=E)
    m.play(FadeIn(ne), FadeIn(right, shift=0.1 * LEFT), at=T.mixes + 1.9, dur=0.6)
    m.play(FadeOut(VGroup(left, right, ne, lt, rb, cb, eb)), at=T.cut_ch4 - 0.4, dur=0.5)
    finish(s)
