"""s29 stepanov (P50): where the claimed idea comes from. The s22 grid of solutions mod 101 returns (clock arithmetic,
where S. Stepanov's 1969 method works). The method needs functions that vanish many times over at each solution: one
solution ringed, and beside it a curve that crosses the axis (order 1), touches it (order 2), flattens through it
(order 3): f = 0, f' = 0, f'' = 0. That takes derivatives; whole numbers, dots on a line, have no obvious d/dn. The new
argument, per the note, finds a stand-in: an amber outline, claimed. Ends on black."""
from aion import *

from beats import T
from cousin import dots, grid_frame, solutions
from look import EASE, caps, lab, live, tex

AX, AY = 3.4, 0.35                         # the solution a, on the curve panel's axis
HW = 1.45                                  # half-width of the curve panel


def curve(m):
    """y = 1.4 (d / 1.4)^k blended between the whole orders around m, d = x - a."""
    k = int(np.clip(np.floor(m), 1, 2))
    u = float(np.clip(m - k, 0, 1))
    d = np.linspace(-HW, HW, 160)
    g = lambda j: 1.25 * np.sign(d) ** j * (np.abs(d) / HW) ** j          # noqa: E731
    y = (1 - u) * g(k) + u * g(k + 1)
    return VMobject(stroke_color=C.text, stroke_width=3).set_points_smoothly(
        [[AX + a, AY + b, 0] for a, b in zip(d, y)])


@scene(T.cut_stepanov, T.cut_status)
def s29_stepanov(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_status - 0.5, T.cut_status - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── a descendant of Stepanov's method ──
    who = caps(r"S. Stepanov $\cdot$ 1969", 34, C.ink)
    who.move_to([-6.3 + who.width / 2, 3.2, 0])
    h.play(FadeIn(who, shift=0.06 * DOWN), at=T.st_stepanov, dur=0.5)
    desc = lab("the new argument: a descendant", 24, C.muted).next_to(who, DOWN, buff=0.15, aligned_edge=LEFT)
    h.play(FadeIn(desc), at=T.st_stepanov + 0.6, dur=0.5)

    # ── for the clock-arithmetic version: the grid of solutions returns ──
    gf, sol = grid_frame(), dots()
    grid = VGroup(gf.lines, gf.mid, sol)
    grid.scale(0.62).move_to([-3.7, -0.75, 0])
    glab = lab("clock arithmetic", 28, C.ffield).next_to(grid, UP, buff=0.18)
    w.play(FadeIn(grid, scale=0.97), FadeIn(glab), at=T.st_clock - 0.4, dur=0.6, lead=0)

    # ── functions that vanish many times over at each solution ──
    pts = solutions()
    k = len(pts) // 2 + 3
    pick = sol[k]
    ring = Circle(radius=0.12, color=C.text, stroke_width=2.2).move_to(pick)
    axis = Line([AX - HW - 0.3, AY, 0], [AX + HW + 0.3, AY, 0], color=C.muted, stroke_width=1.8)
    adot = Dot([AX, AY, 0], radius=0.07, color=C.ffield)
    alab = tex("a", size=30, color=C.ffield).move_to([AX + 0.05, AY - 0.32, 0])
    link = DashedLine(pick.get_center(), [AX - HW - 0.35, AY, 0], color=C.faint, stroke_width=1.4, dash_length=0.08)
    w.play(Create(ring), at=T.st_needs - 0.1, dur=0.4, lead=0)
    w.play(Create(axis), FadeIn(adot), FadeIn(alab), Create(link), at=T.st_needs, dur=0.6)
    m = keys((T.st_vanish, 1.0), (T.st_vanish + 0.75, 2.0, EASE), (T.st_vanish + 1.6, 3.0, EASE), lead=0)
    c0 = curve(1.0)
    w.play(Create(c0), at=T.st_needs + 0.4, dur=0.6)
    w.remove(c0, at=T.st_vanish)
    live(w, lambda t: curve(float(m(t))), (T.st_vanish, T.st_vanish + 1.6))
    tags = VGroup(tex("f=0", size=30), tex("f'=0", size=30), tex("f''=0", size=30)).arrange(RIGHT, buff=0.45)
    tags.move_to([AX, AY + 1.75, 0])
    for i, at in enumerate((T.st_vanish - 0.2, T.st_vanish + 0.6, T.st_vanish + 1.45)):
        h.play(FadeIn(tags[i], shift=0.06 * DOWN), at=at, dur=0.4, lead=0)
    eq = tex(r"f(a)=f'(a)=\cdots=f^{(m-1)}(a)=0", size=36).move_to([AX - 0.4, 3.2, 0])
    h.play(Write(eq), at=T.st_each, dur=1.0)

    # ── that takes derivatives; whole numbers have no obvious one ──
    ddx = tex(r"\frac{d}{dx}", size=34, color=C.ffield).move_to([AX + HW + 0.75, AY + 0.9, 0])
    h.play(FadeIn(ddx, scale=0.9), at=T.st_deriv, dur=0.5)
    ny = -3.05
    nl = Line([-6.0, ny, 0], [1.6, ny, 0], color=C.muted, stroke_width=1.6)
    nd = VGroup(*[Dot([-5.7 + 0.37 * i, ny, 0], radius=0.06, color=C.prime) for i in range(20)])
    nlab = lab("whole numbers", 24, C.prime).move_to([-4.9, ny + 0.35, 0])
    w.play(Create(nl), LaggedStart(*[FadeIn(d, scale=0.5) for d in nd], lag_ratio=0.05), FadeIn(nlab),
           at=T.st_whole - 0.3, dur=0.8, lead=0)
    ddn = tex(r"\frac{d}{dn}\ ?", size=36, color=C.muted).move_to([2.55, ny, 0])
    h.play(FadeIn(ddn, shift=0.06 * LEFT), at=T.st_noobv + 0.2, dur=0.5)

    # ── the new argument finds a stand-in (claimed) ──
    st = lab("stand-in (claimed)", 28, C.claimed)
    sbox = DashedVMobject(RoundedRectangle(width=st.width + 0.5, height=st.height + 0.4, corner_radius=0.1,
                                           stroke_color=C.claimed, stroke_width=2.2), num_dashes=40, dashed_ratio=0.6)
    stand = VGroup(sbox, st.move_to(sbox)).move_to([5.0, ny, 0])
    w.play(Create(sbox), FadeIn(st), at=T.st_new + 1.5, dur=0.8)
