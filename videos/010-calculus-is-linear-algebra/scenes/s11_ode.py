"""Ch5 (cont.): a differential equation is a null space. y'' + y = 0 reads (D^2 + 1) y = 0, so its solutions are the
null space of D^2 + 1: the whole (cos, sin) plane. Two numbers, y(0) and y'(0), pick one point, e.g. (1, 0.5) is
cos x + 0.5 sin x, and that drives the spring. Fourier and Laplace rewrite functions in D's own eigenbasis, where D is
diagonal: each piece is just multiplied by its λ."""
import sympy as sp

from aion import *

from beats import T
from shots import Mat, arrow, backdrop, finish, grid_lines, pt, tex

E = "easy_ease"
PO, PU = (2.9, -0.9), 1.3                                 # the (cos, sin) plane, right
PBOX = (0.2, -3.7, 6.7, 2.0)
AB = np.array([1.0, 0.5])                                 # y(0) = 1, y'(0) = 0.5
SX, TOPY = -4.6, 2.3                                     # the spring: x, ceiling y
REST, AMP = -0.6, 1.0                                    # the mass's rest height, metres per unit of y
W = 2.2                                                  # rad/s on screen

_x, _a, _b = sp.symbols("x a b")
_y = _a * sp.cos(_x) + _b * sp.sin(_x)
assert sp.simplify(sp.diff(_y, _x, 2) + _y) == 0
assert _y.subs({_a: 1, _b: 0.5, _x: 0}) == 1 and sp.diff(_y, _x).subs({_a: 1, _b: 0.5, _x: 0}) == 0.5


def y_of(t, t0):
    s_ = W * max(t - t0, 0.0)
    return AB[0] * np.cos(s_) + AB[1] * np.sin(s_)


def spring_at(yv, op=1.0):
    """A zig-zag from the ceiling to a mass whose centre sits at REST - AMP * y (y up = mass up)."""
    my = REST + AMP * yv
    top, bot = TOPY - 0.05, my + 0.35
    n = 12
    ys = np.linspace(top, bot, 2 * n + 1)
    xs = [SX] + [SX + (0.28 if k % 2 else -0.28) for k in range(1, 2 * n)] + [SX]
    zig = VMobject(stroke_color=C.text, stroke_width=C.stroke, stroke_opacity=op).set_points_as_corners(
        [[x, y, 0] for x, y in zip(xs, ys)])
    mass = Square(0.7, stroke_color=C.fn, stroke_width=C.stroke, fill_color=C.fn, fill_opacity=0.25 * op,
                  stroke_opacity=op).move_to([SX, my, 0])
    return VGroup(zig, mass)


@scene(T.cut_ode, T.cut_ch6)
def s11_ode(s):
    backdrop(s)
    m = s.manim(z=1)

    # ── y'' + y = 0, the spring ──
    eq = tex(r"y''", r"+", r"y", r"=", r"0", size=60, colors={0: C.fn, 2: C.fn}).move_to([0, 3.1, 0])
    m.play(FadeIn(eq, shift=0.1 * DOWN), at=T.diffeq + 0.3, dur=0.7)
    ceil = VGroup(Line([SX - 0.9, TOPY, 0], [SX + 0.9, TOPY, 0], color=C.text, stroke_width=C.stroke),
                  *[Line([SX - 0.8 + 0.2 * k, TOPY, 0], [SX - 0.65 + 0.2 * k, TOPY + 0.15, 0], color=C.muted,
                         stroke_width=C.thin) for k in range(9)])
    rest = DashedLine([SX - 1.1, REST, 0], [SX + 1.1, REST, 0], color=C.muted, stroke_width=C.thin, dash_length=0.08)
    ts0, ts1 = T.spring, T.channel + 1.1
    sop = keys((ts0 - 0.2, 0.0), (ts0 + 0.4, 1.0), (ts1 - 0.6, 1.0), (ts1, 0.0), lead=0)
    m.play(FadeIn(ceil), FadeIn(rest), at=ts0 - 0.2, dur=0.6)
    m.redraw(lambda t: spring_at(y_of(t, ts0 + 0.4), float(sop(t))), during=(ts0 - 0.2, ts1))

    # ── read it as an operator: (D^2 + 1) y = 0 ──
    opq = tex(r"(", r"D^2", r"+", r"1", r")", r"\,y", r"=", r"0", size=60,
              colors={1: C.op, 3: C.op, 5: C.fn}).move_to(eq)
    m.play(TransformMatchingTex(eq, opq), at=T.operator + 0.3, dur=1.0)

    # ── its solutions are the null space: a whole plane ──
    grid = grid_lines(np.eye(2), PO, PU, PBOX, n=6, opacity=0.6)
    lc = tex(r"\cos x", size=36, color=C.b1).next_to(pt(PO, PU, (2.15, 0)), UP, buff=0.12)
    ls = tex(r"\sin x", size=36, color=C.b2).next_to(pt(PO, PU, (0, 2.0)), RIGHT, buff=0.12)
    m.play(FadeIn(grid), FadeIn(lc), FadeIn(ls), at=T.solutions + 0.3, dur=0.8)
    nul = tex(r"\text{null}", r"(D^2+1)", size=40, colors={0: C.null, 1: C.op}).move_to([PO[0] + 0.2, 1.65 + 0.25, 0])
    nul.move_to([3.45, 2.4, 0])
    m.play(FadeIn(nul, shift=0.1 * DOWN), at=T.solutions + 1.2, dur=0.6)
    fill = Rectangle(width=PBOX[2] - PBOX[0], height=PBOX[3] - PBOX[1], stroke_width=0, fill_color=C.null,
                     fill_opacity=0.08).move_to([(PBOX[0] + PBOX[2]) / 2, (PBOX[1] + PBOX[3]) / 2, 0])
    m.play(FadeIn(fill), at=T.plane2, dur=0.8)
    gen = tex(r"a", r"\cos x", r"+", r"b", r"\sin x", size=44, colors={1: C.b1, 4: C.b2}).move_to([3.45, -3.35, 0])
    m.play(FadeIn(gen, shift=0.1 * UP), at=T.plane2 + 0.6, dur=0.6)

    # ── two numbers pick one solution ──
    tip = pt(PO, PU, AB)
    z = pt(PO, 1.0, (0, 0))
    va = arrow(z, tip, C.fn, width=C.stroke + 1.5)
    dx = DashedLine(tip, pt(PO, PU, (AB[0], 0)), color=C.b1, stroke_width=C.thin * 1.5, dash_length=0.08)
    dy = DashedLine(tip, pt(PO, PU, (0, AB[1])), color=C.b2, stroke_width=C.thin * 1.5, dash_length=0.08)
    m.play(GrowArrow(va), at=T.two_numbers, dur=0.7)
    m.play(Create(dx), Create(dy), at=T.two_numbers + 0.8, dur=0.6)
    one = tex(r"\cos x", r"+", r"0.5", r"\sin x", size=44, colors={0: C.b1, 2: C.b2, 3: C.b2}).move_to(gen)
    m.play(ReplacementTransform(gen, one), at=T.two_numbers + 1.0, dur=0.8)
    y0 = tex(r"y(0)", r"=", r"1", size=36, colors={0: C.b1}).next_to(pt(PO, PU, (AB[0], 0)), DOWN, buff=0.18)
    y1 = tex(r"y'(0)", r"=", r"0.5", size=36, colors={0: C.b2}).next_to(pt(PO, PU, (0, AB[1])), LEFT, buff=0.18)
    m.play(FadeIn(y0, shift=0.1 * UP), at=T.conditions - 0.3, dur=0.5)
    m.play(FadeIn(y1, shift=0.1 * LEFT), at=T.conditions + 0.6, dur=0.5)

    # ── Fourier and Laplace: the derivative's own eigenbasis, where D is diagonal ──
    tc = T.channel
    m.play(FadeOut(VGroup(grid, lc, ls, nul, fill, one, va, dx, dy, y0, y1, ceil, rest, opq)), at=tc + 0.5, dur=0.6)
    rows = [[r"\lambda_1", "0", "0", r"\cdots"], ["0", r"\lambda_2", "0", r"\cdots"], ["0", "0", r"\lambda_3", r"\cdots"],
            [r"\vdots", r"\vdots", r"\vdots", r"\ddots"]]
    Dm = Mat(rows, colors=C.faint, size=50, h_buff=1.15, v_buff=0.8)
    for i in range(3):
        Dm.cell(i, i).set_color(C.eigen)
    for i in range(3):
        Dm.cell(i, 3).set_color(C.muted)
        Dm.cell(3, i).set_color(C.muted)
    Dm.cell(3, 3).set_color(C.muted)
    dl = tex(r"D", r"=", size=56, colors={0: C.op})
    dg = VGroup(dl, Dm).arrange(RIGHT, buff=0.3).move_to([0, -0.5, 0])
    heads = VGroup(*[tex(rf"e^{{\lambda_{k + 1} x}}", size=36, color=C.eigen).move_to(
        [Dm.cell(0, k).get_center()[0], Dm.get_top()[1] + 0.45, 0]) for k in range(3)])
    four = tex(r"\mathcal{F}", r",\;", r"\mathcal{L}", size=56).move_to([0, 2.9, 0])
    m.play(FadeIn(four, shift=0.1 * DOWN), at=T.fourier - 0.3, dur=0.6)
    m.play(FadeIn(dg), at=T.fourier + 1.8, dur=0.8)
    m.play(LaggedStart(*[FadeIn(h, shift=0.1 * DOWN) for h in heads], lag_ratio=0.25), at=T.eigenbasis, dur=1.0)
    diag = VGroup(*[Dm.cell(i, i) for i in range(3)])
    m.play(LaggedStart(*[Indicate(c, color=C.eigen, scale_factor=1.35) for c in diag], lag_ratio=0.3),
           at=T.multiplied - 0.2, dur=1.4)

    # ── calculus becomes algebra: diagonalizing D ──
    alg = tex(r"\frac{d}{dx}", r"\;\longrightarrow\;", r"\times\lambda", size=52, colors={0: C.op, 2: C.eigen})
    alg.move_to([0, -3.1, 0])
    m.play(FadeIn(alg, shift=0.1 * UP), at=T.algebra, dur=0.7)
    m.play(Indicate(Dm, color=C.eigen, scale_factor=1.04), at=T.diagonalizing + 0.3, dur=1.0)
    m.play(FadeOut(VGroup(four, dg, heads, alg)), at=T.cut_ch6 - 0.7, dur=0.6)
    finish(s)
