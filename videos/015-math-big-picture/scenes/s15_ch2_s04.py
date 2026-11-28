"""ch2_s04 · The square inside the circle (√2 is not a fraction).

A circle of radius one, its radius marked 1. On 'square' a gold square is fitted inside; on 'diagonal' its diagonal
is drawn straight across, two radii long, tagged 2. On 'Pythagoras' the half-square triangle fills, its two sides
marked s, and the column on the right writes s² + s² = 2² ⇒ s = √2. Then the proof, one line per step, each older
line dimming: √2 = p/q ? ('lowest terms'), p² = 2q² (p ringed: 'p even'), p = 2k ⇒ q² = 2k² (q ringed: 'q even').
On 'both numbers even' the clash is struck in red, the only red in the video, across 'lowest terms'; the assumption is
crossed out and the boxed result √2 ≠ p/q lands. On 'irrational' a short number line under the circle shows the
fractions between 1 and 1.6 with √2 falling between them all.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import P3, sans, tex, the_circle, tint

CC, R = P3(-3.6, 0.45), 2.0
XC = 3.6                                  # derivation column centre
ROWS = [3.15, 2.05, 0.95, -0.15, -1.25, -2.45]


def corner(deg):
    a = math.radians(deg)
    return CC + R * P3(math.cos(a), math.sin(a))


def eq(*parts, size=46, colors=None):
    m = MathTex(*parts, font_size=size, color=C.text)
    for i, col in (colors or {}).items():
        m[i].set_color(col)
    return m


@scene(T.ch2_s04, T.ch2_s05)
def ch2_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    fills, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_sq, t_dg, t_py = float(T.ch2_s04_square), float(T.ch2_s04_diagonal), float(T.ch2_s04_pythagoras)
    t_fr, t_lt, t_sqr = float(T.ch2_s04_fraction), float(T.ch2_s04_lowest_terms), float(T.ch2_s04_squaring)
    t_fd, t_be, t_irr = float(T.ch2_s04_feed), float(T.ch2_s04_both_numbers_even), float(T.ch2_s04_irrational)
    Q = C.quantity

    # the circle of radius one
    circ = the_circle(R).move_to(CC)
    m.play(Create(circ), at=t0 + 0.2, dur=1.0, ease="easy_ease")
    rad = VGroup(Line(CC, CC + P3(R, 0), stroke_color=C.text, stroke_width=2.2), Dot(CC, radius=0.05, color=C.text),
                 tex("1", 36, C.text).move_to(CC + P3(R / 2, 0.3)))
    m.play(Create(rad[0]), FadeIn(rad[1:]), at=t0 + 2.6, dur=0.6)

    # the square, then its diagonal: two radii, so length 2
    sq = Polygon(*(corner(d) for d in (45, 135, 225, 315)), stroke_color=Q, stroke_width=4)
    m.play(Create(sq), at=t_sq + 0.1, dur=1.0, ease="easy_ease")
    m.play(FadeOut(rad), at=t_dg - 0.4, dur=0.4)
    diag = Line(corner(225), corner(45), stroke_color=C.text, stroke_width=3)
    m.play(Create(diag), at=t_dg, dur=0.9, ease="easy_ease")
    halves = VGroup(tex("1", 32, C.muted).move_to(CC + 0.5 * R * P3(-0.707, -0.707) + P3(0.25, -0.25)),
                    tex("1", 32, C.muted).move_to(CC + 0.5 * R * P3(0.707, 0.707) + P3(0.25, -0.25)))
    two = tex("2", 40, C.text).move_to(CC + P3(0.4, -0.4))
    m.play(FadeIn(halves, shift=0.06 * UP), at=t_dg + 1.0, dur=0.5)
    m.play(ReplacementTransform(halves, two), at=t_dg + 2.9, dur=0.7, ease="easy_ease")

    # Pythagoras: the half-square triangle, its sides s
    tri = Polygon(corner(225), corner(135), corner(45), stroke_width=0, fill_color=Q, fill_opacity=0.18)
    fills.play(FadeIn(tri), at=t_py - 0.1, dur=0.5)
    h = R / math.sqrt(2)
    s_left = tex("s", 40, Q).move_to(CC + P3(-h + 0.42, 0.1))
    s_top = tex("s", 40, Q).move_to(CC + P3(-0.1, h - 0.38))
    m.play(FadeIn(s_left, shift=0.08 * RIGHT), FadeIn(s_top, shift=0.08 * DOWN), at=t_py + 0.2, dur=0.5)
    L0 = eq("s^2", "+", "s^2", "=", "2^2", r"\;\Rightarrow\;", "s", "=", r"\sqrt{2}", colors={0: Q, 2: Q, 6: Q, 8: Q})
    L0.move_to(P3(XC, ROWS[0]))
    m.play(Write(L0[:5]), at=t_py + 0.7, dur=0.9)
    m.play(Write(L0[5:]), at=t_py + 1.7, dur=0.8)
    r2l = tex(r"\sqrt{2}", 40, Q).move_to(s_left)
    r2t = tex(r"\sqrt{2}", 40, Q).move_to(s_top)
    m.play(ReplacementTransform(s_left, r2l), ReplacementTransform(s_top, r2t), at=t_py + 2.3, dur=0.6)

    # the proof, one line per step; older lines dim
    def dim(at, *mobs):
        m.play(*(x.animate.set_stroke(opacity=0.4) if isinstance(x, Circle) else x.animate.set_opacity(0.4)
                 for x in mobs), at=at, dur=0.5)

    L1 = eq(r"\sqrt{2}", "=", r"\tfrac{p}{q}", r"\,?", colors={0: Q, 3: Q}).move_to(P3(XC - 0.9, ROWS[1]))
    m.play(Write(L1), at=t_fr - 0.2, dur=0.8)
    dim(t_fr - 0.2, L0)
    lt = sans("lowest terms", 30, C.muted).next_to(L1, RIGHT, buff=0.5)
    m.play(FadeIn(lt, shift=0.06 * LEFT), at=t_lt, dur=0.5)

    L2 = eq("2", "=", r"\tfrac{p^2}{q^2}", r"\;\Rightarrow\;", "p^2", "=", "2q^2").move_to(P3(XC, ROWS[2]))
    m.play(Write(L2), at=t_sqr + 0.1, dur=1.2)
    dim(t_sqr + 0.1, L1, lt)
    ring_p = Circle(radius=0.33, stroke_color=Q, stroke_width=2.6).move_to(L2[4])
    p_even = sans("p even", 30, Q).next_to(L2, RIGHT, buff=0.35)
    m.play(Create(ring_p), at=t_sqr + 3.9, dur=0.5)
    m.play(FadeIn(p_even, shift=0.06 * LEFT), at=t_sqr + 4.8, dur=0.5)

    L3 = eq("p", "=", "2k", r"\;\Rightarrow\;", "q^2", "=", "2k^2").move_to(P3(XC, ROWS[3]))
    m.play(Write(L3), at=t_fd, dur=1.1)
    dim(t_fd, L2, ring_p, p_even)
    ring_q = Circle(radius=0.33, stroke_color=Q, stroke_width=2.6).move_to(L3[4])
    q_even = sans("q even", 30, Q).next_to(L3, RIGHT, buff=0.35)
    m.play(Create(ring_q), at=t_fd + 1.5, dur=0.5)
    m.play(FadeIn(q_even, shift=0.06 * LEFT), at=t_fd + 2.4, dur=0.5)

    # the clash: 'lowest terms' comes back up, and both-even strikes it (the one red of the video)
    lt_hi = lt.copy().set_opacity(1).set_color(C.text)
    top.play(FadeIn(lt_hi), at=t_be - 2.0, dur=0.4)
    L4 = eq(r"p,\ q\ \text{both even}", colors={0: C.alert}).move_to(P3(XC, ROWS[4]))
    m.play(FadeIn(L4, shift=0.1 * UP), at=t_be, dur=0.5)
    dim(t_be, L3, ring_q, q_even)
    strike = Line(lt_hi.get_left() + P3(-0.1, 0), lt_hi.get_right() + P3(0.1, 0), stroke_color=C.alert, stroke_width=4)
    top.play(Create(strike), at=t_be + 0.3, dur=0.4)
    clash = VGroup(Line(P3(-0.16, -0.16), P3(0.16, 0.16)), Line(P3(-0.16, 0.16), P3(0.16, -0.16)))
    clash.set_stroke(C.alert, 4).next_to(lt_hi, RIGHT, buff=0.25)
    top.play(GrowFromCenter(clash), at=t_be + 0.5, dur=0.4, ease="out_back")

    # the assumption fails: cross out line 1, box the result
    t_fail = t_be + 2.1
    cross = Line(L1.get_left() + P3(-0.1, -0.05), L1.get_right() + P3(0.1, 0.05), stroke_color=C.muted, stroke_width=3)
    top.play(Create(cross), at=t_fail, dur=0.4)
    L5 = eq(r"\sqrt{2}", r"\neq", r"\tfrac{p}{q}", size=52, colors={0: Q}).move_to(P3(XC, ROWS[5]))
    box = SurroundingRectangle(L5, buff=0.22, color=Q, stroke_width=2.6, corner_radius=0.1)
    m.play(Write(L5), at=t_fail + 1.2, dur=0.8)
    m.play(Create(box), at=t_fail + 2.0, dur=0.6)
    top.play(FadeOut(VGroup(lt_hi, strike, clash)), at=t_fail + 1.2, dur=0.5)
    dim(t_fail + 1.2, L4)

    # 'irrational': fractions between 1 and 1.6, and √2 between them all
    YN = -2.85

    def xn(v):
        return -6.0 + (v - 1) * 8.0

    nl = VGroup(Line(P3(xn(0.97), YN), P3(xn(1.63), YN), stroke_color=C.muted, stroke_width=2))
    for v, lab in ((1, "1"), (1.5, "1.5")):
        nl.add(Line(P3(xn(v), YN - 0.12), P3(xn(v), YN + 0.12), stroke_color=C.muted, stroke_width=2),
               tex(lab, 28, C.muted).move_to(P3(xn(v), YN - 0.42)))
    fr = sorted({p / q for q in range(2, 13) for p in range(q + 1, 2 * q) if math.gcd(p, q) == 1 and p / q < 1.6})
    ticks = VGroup(*(Line(P3(xn(v), YN - 0.09), P3(xn(v), YN + 0.09), stroke_color=C.text, stroke_width=1.4,
                          stroke_opacity=0.7) for v in fr))
    m.play(Create(nl[0]), FadeIn(nl[1:]), at=t_irr - 2.2, dur=0.6)
    m.play(LaggedStart(*(FadeIn(x_) for x_ in ticks), lag_ratio=0.02), at=t_irr - 1.6, dur=0.8)
    r2 = VGroup(Dot(P3(xn(math.sqrt(2)), YN), radius=0.08, color=Q),
                tex(r"\sqrt{2}", 32, Q).move_to(P3(xn(math.sqrt(2)), YN + 0.45)))
    top.play(FadeIn(r2[0], shift=0.3 * DOWN), FadeIn(r2[1]), at=t_irr - 0.6, dur=0.5)
    irr = sans("irrational", 34, Q).move_to(P3(XC, -3.45))
    m.play(FadeIn(irr, shift=0.08 * UP), at=t_irr + 0.05, dur=0.5)
    out = VGroup(circ, sq, diag, two, r2l, r2t, L0, L1, lt, L2, ring_p, p_even, L3, ring_q, q_even, L4, L5, box)
    m.play(FadeOut(out), at=float(s.end) - 0.6, dur=0.5)
    fills.play(FadeOut(tri), at=float(s.end) - 0.6, dur=0.5)
    top.play(FadeOut(cross), at=float(s.end) - 0.6, dur=0.5)
