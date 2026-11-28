"""s22 cousin (P40): a version that has been proved. y^2 = x^3 + x + 1 counted in clock arithmetic (a 7-hour clock
wraps around), then mod 101: the 104 solutions as lilac dots on the 101 x 101 grid of pairs, mirrored about the middle
row. The count stays within 2 sqrt p of p (Hasse): a gauge for p = 101, then (A_p - p) / 2 sqrt p for every prime below
5000, all inside +-1. Weil (all curves, 1940s), Deligne (far more general, 1974). Their proofs use geometry: a split
frame, clock arithmetic (geometry) vs whole numbers (?). Ends on black: chapter 6 opens with its card.
Every count is computed here (cousin.py; verify.py checks the same)."""
from aion import *

from beats import T
from media_assets import portrait_card
from cousin import P, affine_count, dots, grid_frame, hasse_data
from look import EASE, caps, lab, live, pin, tex
from progress import end_frame

CX, CY, CR = 3.4, 0.6, 1.25                  # the clock
SX0, SX1, SY0, SY1 = 0.7, 6.2, -2.75, 0.3     # the scatter
GL, GLY = (0.7, 6.2), 1.55                   # the gauge: x range and height
G0, G1 = 70.0, 132.0                         # the gauge's value range


@scene(T.cut_cousin, T.cut_meaning)
def s22_cousin(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_meaning - 0.5, T.cut_meaning - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    o1, o2 = s.manim(z=2, parallax=0.0), s.manim(z=6, parallax=0.0)
    ow, oh = end_frame()                   # s21's last frame
    o1.add(*ow)
    o2.add(*oh)
    out = (T.cut_cousin + 0.4, T.cut_cousin + 0.9)
    o1.play(*[FadeOut(m) for m in ow], at=out[0], dur=out[1] - out[0], lead=0)
    o2.play(*[FadeOut(m) for m in oh], at=out[0], dur=out[1] - out[0], lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── a version of the hypothesis has been proved ──
    head = lab("a version that has been proved", 40, C.text)
    h.play(FadeIn(head, shift=0.08 * UP), at=T.c_version + 0.3, dur=0.7)
    h.play(FadeOut(head), at=T.c_take - 0.5, dur=0.4, lead=0)

    # ── take an equation, count its solutions in clock arithmetic ──
    eq = tex(r"y^2", r"=", r"x^3+x+1", size=42, colors={0: C.ffield, 2: C.ffield})
    eqp = tex(r"y^2", r"\equiv", r"x^3+x+1", r"\pmod p", size=42, colors={0: C.ffield, 2: C.ffield})
    pin(eqp, top=3.55, left=-6.0)
    eq.move_to(eqp[:3], aligned_edge=LEFT)
    h.play(Write(eq), at=T.c_take + 0.2, dur=1.0)
    grid = grid_frame()
    w.play(Create(grid.lines), FadeIn(grid.labels), at=T.c_count, dur=1.0)

    # the clock: 4 + 5 wraps around to 2
    face = Circle(radius=CR, color=C.muted, stroke_width=2.0).move_to([CX, CY, 0])
    ang = lambda k: PI / 2 - TAU * k / 7                         # noqa: E731
    nums = VGroup(*[tex(str(k), size=30).move_to([CX + 0.78 * CR * np.cos(ang(k)), CY + 0.78 * CR * np.sin(ang(k)), 0])
                    for k in range(7)])
    hour = keys((T.c_wrap - 0.8, 4.0), *[(T.c_wrap - 0.8 + 0.35 * j + 0.25, 4.0 + j, EASE) for j in range(1, 6)],
                lead=0)

    def hand(t):
        k = float(hour(t))
        tip = np.array([CX + 0.55 * CR * np.cos(ang(k)), CY + 0.55 * CR * np.sin(ang(k)), 0])
        return VGroup(Line([CX, CY, 0], tip, color=C.ffield, stroke_width=4), Dot([CX, CY, 0], radius=0.06,
                                                                                    color=C.ffield))

    mod7 = tex(r"4+5", r"\equiv", r"2", r"\pmod 7", size=34).move_to([CX, CY - CR - 0.45, 0])
    clock = VGroup(face, nums)
    h0 = hand(T.c_clock)
    w.play(Create(face), FadeIn(nums), FadeIn(h0), at=T.c_clock, dur=0.7)
    w.remove(h0, at=T.c_wrap - 0.8)
    held = live(w, hand, (T.c_wrap - 0.8, T.c_wrap - 0.8 + 0.35 * 5 + 0.3))
    h.play(FadeIn(mod7, shift=0.06 * UP), at=T.c_wrap + 0.9, dur=0.5)
    h.play(TransformMatchingTex(eq, eqp), at=T.c_clock + 0.5, dur=0.8)
    gone = T.c_never - 0.3
    w.play(FadeOut(clock), FadeOut(held[-1]), at=gone, dur=0.4, lead=0)
    h.play(FadeOut(mod7), at=gone, dur=0.4, lead=0)

    # the 104 solutions mod 101, row by row
    sol = dots()
    w.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in sol], lag_ratio=0.12), at=T.c_wrap + 1.2, dur=2.2, lead=0)
    w.play(Create(grid.mid), at=T.c_wrap + 3.2, dur=0.6, lead=0)
    count = tex(r"p=101:", r"\ A_p=" + str(affine_count(P)), size=36, colors={1: C.ffield})
    pin(count, top=2.85, left=-6.0)
    h.play(FadeIn(count, shift=0.06 * DOWN), at=T.c_never - 0.2, dur=0.5)

    # ── the count never strays from p by more than 2 sqrt p (Hasse) ──
    gx = lambda v: GL[0] + (GL[1] - GL[0]) * (np.asarray(v, float) - G0) / (G1 - G0)     # noqa: E731
    lo, hi = P - 2 * np.sqrt(P), P + 2 * np.sqrt(P)
    gauge = VGroup(Line([GL[0], GLY, 0], [GL[1], GLY, 0], color=C.muted, stroke_width=2.0),
                   Rectangle(width=float(gx(hi) - gx(lo)), height=0.3, stroke_color=C.crit, stroke_width=1.6,
                             fill_color=C.crit, fill_opacity=0.12).move_to([float(gx(P)), GLY, 0]),
                   Line([float(gx(P)), GLY - 0.2, 0], [float(gx(P)), GLY + 0.2, 0], color=C.text, stroke_width=2),
                   tex(r"p", size=30).move_to([float(gx(P)), GLY + 0.42, 0]),
                   tex(r"p-2\sqrt p", size=26, color=C.crit).move_to([float(gx(lo)), GLY - 0.42, 0]),
                   tex(r"p+2\sqrt p", size=26, color=C.crit).move_to([float(gx(hi)), GLY - 0.42, 0]))
    need = keys((T.c_never - L, float(G0) + 4), (T.c_never + 1.4, float(affine_count(P)), "out_back"), lead=0)

    def needle(t):
        x = float(gx(need(t)))
        return VGroup(Triangle(color=C.ffield, fill_opacity=1.0, stroke_width=0).scale(0.11).rotate(PI)
                      .move_to([x, GLY + 0.3, 0]), Line([x, GLY + 0.2, 0], [x, GLY - 0.15, 0], color=C.ffield,
                                                        stroke_width=3))

    w.play(FadeIn(gauge), at=T.c_never - 0.3, dur=0.5)
    nd = live(w, needle, (T.c_never - L, T.c_never + 1.4))
    bound = tex(r"|A_p-p|", r"\le", r"2\sqrt p", size=42, colors={0: C.ffield, 2: C.crit})
    pin(bound, top=3.55, left=0.6)
    hasse = caps(r"H. Hasse $\cdot$ 1933", 30, C.ink)
    pin(hasse, top=2.85, left=0.6)
    h.play(Write(bound), at=T.c_twice, dur=1.0)
    h.play(FadeIn(hasse), at=T.c_twice + 0.8, dur=0.5)

    # ── the same square-root behavior: every prime below 5000 ──
    ps, r = hasse_data()
    sx = lambda v: SX0 + (SX1 - SX0) * np.asarray(v, float) / 5000                         # noqa: E731
    sy = lambda v: (SY0 + SY1) / 2 + (SY1 - SY0) / 2 * np.asarray(v, float) / 1.25         # noqa: E731
    frame = VGroup(Line([SX0, float(sy(0)), 0], [SX1, float(sy(0)), 0], color=C.muted, stroke_width=1.4),
                   *[DashedLine([SX0, float(sy(v)), 0], [SX1, float(sy(v)), 0], color=C.crit, stroke_width=1.6,
                                dash_length=0.08) for v in (-1, 1)],
                   tex("+1", size=24, color=C.crit).move_to([SX0 - 0.28, float(sy(1)), 0]),
                   tex("-1", size=24, color=C.crit).move_to([SX0 - 0.28, float(sy(-1)), 0]),
                   tex("5000", size=24, color=C.muted).move_to([SX1 + 0.4, float(sy(0)), 0]))
    ylab = tex(r"\frac{A_p-p}{2\sqrt p}", size=30, color=C.ffield)
    ylab.move_to([SX0 + 0.1 + ylab.width / 2, SY0 - 0.6, 0])
    scat_on = keys((T.c_same - L, 0.0), (T.c_same + 1.9, 5000.0, "in_out_sine"), lead=0)

    def scatter(t):
        keep = ps <= float(scat_on(t))
        return VGroup(*[Dot([float(sx(a)), float(sy(b)), 0], radius=0.026, color=C.ffield)
                        for a, b in zip(ps[keep], r[keep])])

    w.play(FadeIn(frame), FadeIn(ylab), at=T.c_same - 0.5, dur=0.4, lead=0)
    sc = live(w, scatter, (T.c_same - L, T.c_same + 1.9))
    every = lab("every prime below 5000", 24, C.muted)
    every.move_to([SX1 - every.width / 2, SY0 - 0.6, 0])
    h.play(FadeIn(every), at=T.c_same + 1.6, dur=0.5)

    # ── Weil (all curves, 1940s), Deligne (far more general, 1974) ──
    w.play(FadeOut(gauge), FadeOut(nd[-1]), at=T.c_weil - 0.6, dur=0.4, lead=0)
    weil = caps(r"A. Weil $\cdot$ 1940s", 32, C.ink)
    deli = caps(r"P. Deligne $\cdot$ 1974", 32, C.ink)
    pin(weil, top=1.95, left=0.6)
    pin(deli, top=1.3, left=0.6)
    h.play(FadeIn(weil, shift=0.06 * DOWN), at=T.c_weil, dur=0.6)
    h.play(FadeIn(deli, shift=0.06 * DOWN), at=T.c_deligne, dur=0.6)
    portrait_card(s, h, "weil", None, T.c_weil, T.c_their + 0.3, (4.55, 1.5), height=1.35)
    portrait_card(s, h, "deligne", None, T.c_deligne, T.c_their + 0.3, (5.75, 1.5), height=1.35)

    # ── their proofs use geometry, with no known counterpart for the whole numbers ──
    split = T.c_their
    h.play(FadeOut(VGroup(eqp, count, bound, hasse, weil, deli, every)), at=split - 0.2, dur=0.5, lead=0)
    w.play(FadeOut(VGroup(grid.lines, grid.labels, grid.mid, frame, ylab, sc[-1])), at=split - 0.2, dur=0.5, lead=0)
    w.remove(*sol, at=split + 0.1)       # the dots were faded in one by one: hand them to one copy
    left = Rectangle(width=5.6, height=4.6, stroke_color=C.text, stroke_width=2.0).move_to([-3.2, -0.4, 0])
    right = DashedVMobject(Rectangle(width=5.6, height=4.6, stroke_width=2.0, stroke_color=C.muted), num_dashes=70,
                           dashed_ratio=0.55).move_to([3.2, -0.4, 0])
    lt = lab("clock arithmetic", 34, C.ffield).next_to(left, UP, buff=0.25)
    rt = lab("whole numbers", 34, C.prime).next_to(right, UP, buff=0.25)
    mini = sol.copy()
    w.play(mini.animate.scale(0.62).move_to([-3.2, -0.15, 0]), FadeIn(left), at=split + 0.1, dur=1.0, lead=0)
    geo = lab("geometry", 32, C.text).move_to([-3.2, -2.3, 0])
    q = tex("?", size=96, color=C.muted).move_to([3.2, -0.4, 0])
    h.play(FadeIn(lt), FadeIn(rt), Create(right), at=split + 0.5, dur=0.7)
    h.play(FadeIn(geo), at=split + 1.1, dur=0.5)
    h.play(FadeIn(q, scale=0.8), at=T.c_noknown, dur=0.6)
