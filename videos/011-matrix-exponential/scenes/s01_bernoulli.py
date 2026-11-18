"""s01 Bernoulli (1683): a balance of 1 at 100% a year. Compounded once it ends at 2; twice, 2.25; monthly, 2.613;
every instant it follows the smooth curve e^t and ends at 2.718..., a ceiling the staircases creep up to but never
pass. Euler names the ceiling e."""
from aion import *

from beats import T
from shots import E, backdrop, coin, finish, lab, mini_axes, p3, plot, poly, portrait, tex, words

O = np.array([-3.75, -3.1])                           # balance plot origin
XW, YU = 5.3, 1.65                                    # one year wide; balance unit height
PX = -5.65                                            # the portrait column
TX = 4.65                                             # table centre x


def bal(x):
    return O + [XW * x[0], YU * x[1]]


def stairs(n):
    """Balance through the year when 100% interest is added n times: a staircase from 1 to (1 + 1/n)^n."""
    pts, b = [(0.0, 1.0)], 1.0
    for k in range(1, n + 1):
        pts.append((k / n, b))
        b *= 1 + 1 / n
        pts.append((k / n, b))
    return np.array([bal(p) for p in pts])


ROWS = [(1, "1"), (2, "2"), (12, "12"), (365, "365"), (None, r"\infty")]


def value(n):
    return np.e if n is None else (1 + 1 / n) ** n


assert abs(value(12) - 2.613) < 1e-3 and abs(value(365) - 2.7146) < 1e-4


@scene(T.cut_bernoulli, T.cut_tangled)
def s01_bernoulli(s):
    backdrop(s)
    m = s.manim(z=1)

    # ── following money: one coin, which becomes the starting balance ──
    c = coin((-1.0, -0.2), r=0.32, color=C.money).scale(2.2)
    m.play(FadeIn(c, scale=0.9), at=T.cut_bernoulli + 0.4, dur=0.6)

    # ── Jacob Bernoulli, 1683 (portrait column, left) ──
    PH_ = 2.1
    b_op = keys((T.bernoulli - 0.3, 0.0), (T.bernoulli + 0.4, 1.0), (T.cut_tangled - 0.55, 1.0),
                (T.cut_tangled - 0.05, 0.0), lead=0)
    b_fr = portrait(s, "bernoulli", (PX, 1.95), PH_, opacity=b_op, start=T.bernoulli - 0.4)
    b_nm = VGroup(words(r"\textsc{Jacob Bernoulli}", size=26), lab("1683", 28, C.money)).arrange(DOWN, buff=0.1)
    b_nm.next_to(b_fr, DOWN, buff=0.18)
    head = VGroup(b_fr, b_nm)
    m.play(Create(b_fr), FadeIn(b_nm, shift=0.1 * UP), at=T.bernoulli + 0.15, dur=0.6)

    ax = mini_axes(O, XW + 0.2, YU * 3.05)
    ticks = VGroup(*[Line(p3(bal((0, y)) + [-0.08, 0]), p3(bal((0, y)) + [0.08, 0]), color=C.muted,
                          stroke_width=C.thin) for y in (1, 2)],
                   Line(p3(bal((1, 0)) + [0, -0.08]), p3(bal((1, 0)) + [0, 0.08]), color=C.muted, stroke_width=C.thin))
    tl = VGroup(tex("1", size=28, color=C.muted).next_to(p3(bal((0, 1))), LEFT, buff=0.15),
                tex("2", size=28, color=C.muted).next_to(p3(bal((0, 2))), LEFT, buff=0.15),
                lab("1 year", 26).next_to(p3(bal((1, 0))), DOWN, buff=0.15))
    start = Dot(p3(bal((0, 1))), radius=0.09, color=C.vec)
    m.play(Create(ax), FadeIn(ticks), FadeIn(tl), at=T.bernoulli + 0.8, dur=1.0)
    m.play(ReplacementTransform(c, start), at=T.bernoulli + 1.0, dur=0.9, ease=E)

    # ── the table ──
    hdr = VGroup(tex("n", size=36, color=C.muted).move_to([TX - 1.1, 2.35, 0]),
                 tex(r"\left(1+\tfrac{1}{n}\right)^{n}", size=36, color=C.muted).move_to([TX + 0.9, 2.35, 0]))
    rule = Line(p3([TX - 1.8, 1.95]), p3([TX + 2.0, 1.95]), color=C.muted, stroke_width=C.thin)
    rows = []
    for k, (n, nlab) in enumerate(ROWS):
        y = 1.45 - 0.72 * k
        v = r"2.71828\ldots" if n is None else (r"2" if n == 1 else f"{value(n):.4f}".rstrip("0"))
        col = C.flow if n is None else C.money
        rows.append(VGroup(tex(nlab, size=38, color=col).move_to([TX - 1.1, y, 0]),
                           tex(v, size=38, color=col).move_to([TX + 0.9, y, 0])))
    m.play(FadeIn(hdr), Create(rule), at=T.hundred, dur=0.6)

    # ── staircases: once, twice, monthly ──
    prev, steps = None, []
    for k, (n, beat) in enumerate(((1, T.hundred + 1.0), (2, T.twice), (12, T.monthly))):
        st = poly(stairs(n), C.money, C.stroke)
        anims = [Create(st), FadeIn(rows[k], shift=0.1 * UP)]
        if prev is not None:
            anims.append(prev.animate.set_stroke(color=C.data, opacity=0.3))
        m.play(*anims, at=beat, dur=0.8 if n < 12 else 0.9, ease=E)
        prev = st
        steps.append(st)

    # ── every instant: the smooth curve e^t ──
    smooth = plot(np.exp, 0, 1, O, XW, YU, C.flow, width=C.stroke + 0.5)
    m.play(Create(smooth), prev.animate.set_stroke(color=C.data, opacity=0.3), at=T.instant + 0.3, dur=1.4, ease=E)
    m.play(FadeIn(rows[3], shift=0.1 * UP), at=T.instant + 0.9, dur=0.5)
    m.play(FadeIn(rows[4], shift=0.1 * UP), at=T.instant + 1.6, dur=0.5)
    end = Dot(p3(bal((1, np.e))), radius=0.09, color=C.vec)
    m.play(FadeIn(end, scale=0.5), at=T.instant + 1.7, dur=0.3)

    # ── a ceiling ──
    ceil = DashedLine(p3(bal((0, np.e))), p3(bal((1.05, np.e))), color=C.flow, stroke_width=C.thin + 0.4,
                      dash_length=0.12)
    m.play(Create(ceil), at=T.ceiling, dur=0.8)
    m.play(Indicate(rows[4], color=C.flow, scale_factor=1.08), at=T.ceiling + 1.2, dur=0.8)

    # ── Euler gives it a letter ──
    e_op = keys((T.euler - 0.3, 0.0), (T.euler + 0.4, 1.0), (T.cut_tangled - 0.55, 1.0), (T.cut_tangled - 0.05, 0.0),
                lead=0)
    e_fr = portrait(s, "euler", (PX, -1.45), PH_, opacity=e_op, start=T.euler - 0.4)
    e_nm = VGroup(words(r"\textsc{Leonhard Euler}", size=26), lab("names it $e$", 26, C.flow)).arrange(DOWN, buff=0.1)
    e_nm.next_to(e_fr, DOWN, buff=0.18)
    eul = VGroup(e_fr, e_nm)
    e = tex("e", size=64, color=C.flow).next_to(p3(bal((1.05, np.e))), RIGHT, buff=0.18)
    e_tab = tex("e", size=44, color=C.flow).move_to(rows[4][1])
    m.play(Create(e_fr), FadeIn(e_nm, shift=0.1 * UP), at=T.euler + 0.15, dur=0.6)
    m.play(Write(e), ReplacementTransform(rows[4][1], e_tab), at=T.euler + 1.4, dur=0.8)

    m.play(FadeOut(VGroup(head, eul, ax, ticks, tl, start, hdr, rule, *rows[:4], rows[4][0], e_tab, smooth, end, ceil,
                          e, *steps)), at=T.cut_tangled - 0.4, dur=0.5)
    finish(s)
