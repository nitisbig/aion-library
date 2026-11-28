"""ch3_s06 · Multiplying adds angles (worked example).

The point rests at 1 on the unit circle. On 'sixty' it turns 60°, leaving a violet arc on the rim; on 'thirty' a
second, inner arc marks 30°. On 'multiplying' the product writes as e^{iπ/3} e^{iπ/6} = ?; on 'Expanding' it expands
into brackets and then four terms. On 'cancels' i² turns into −1, the two real parts are struck out, and = i lands
while the 30° arc swings round to start where the 60° one ends: the point lands on i, a quarter turn. On 'adds' the
rule e^{ia} e^{ib} = e^{i(a+b)} is boxed; on 'trigonometry' the angle-addition formula for cosine fades in, dimmed.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import PL_O as O, PL_U as U, P3, plane_grid, plane_line, tex, the_circle

XC = 3.9
ROWS = [2.85, 1.8, 0.75, -0.3, -1.4, -2.35]


def on(deg, r=U):
    a = math.radians(deg)
    return O + r * P3(math.cos(a), math.sin(a))


def eq(*parts, size=44):
    return MathTex(*parts, font_size=size, color=C.text)


@scene(T.ch3_s06, T.ch3_s07)
def ch3_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    grid_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t60, t30, t_mul = float(T.ch3_s06_sixty), float(T.ch3_s06_thirty), float(T.ch3_s06_multiplying)
    t_ex, t_can, t_add, t_tri = (float(T.ch3_s06_expanding), float(T.ch3_s06_cancels), float(T.ch3_s06_adds),
                                 float(T.ch3_s06_trigonometry))
    V, E, Q = C.structure, C.change, C.quantity

    # where ch3_s05 left off
    grid = plane_grid(1.0)
    grid_l.add(grid)
    nl = plane_line()
    nl.remove(*nl[2::2])
    circ = the_circle(U).move_to(O)
    track_box = RoundedRectangle(width=1.95, height=0.78, corner_radius=0.14, stroke_color=C.map_off, stroke_width=1.6)
    track_box.move_to(P3(5.75, -3.35))
    tracked = VGroup(tex("e", 40, E), tex("i", 40, V), tex(r"\pi", 40, Q)).arrange(RIGHT, buff=0.38).move_to(track_box)
    rad = Line(O, on(0), stroke_color=V, stroke_width=4)
    pt = Dot(on(0), radius=0.1, color=V)
    m.add(nl, circ, track_box, tracked)
    top.add(rad, pt)

    # 'sixty' and 'thirty'
    a60 = Arc(radius=U, start_angle=0, angle=math.radians(60), arc_center=O, stroke_color=V, stroke_width=9)
    m.play(Create(a60), at=t60, dur=0.9, ease="easy_ease")
    top.play(Rotate(rad, math.radians(60), about_point=O), Rotate(pt, math.radians(60), about_point=O),
             at=t60, dur=0.9, ease="easy_ease")
    l60 = tex(r"60^\circ", 34, V).move_to(on(30, U + 0.45))
    m.play(FadeIn(l60), at=t60 + 0.5, dur=0.4)
    a30 = Arc(radius=0.55 * U, start_angle=0, angle=math.radians(30), arc_center=O, stroke_color=V, stroke_width=6)
    l30 = tex(r"30^\circ", 30, V).move_to(on(15, 0.55 * U + 0.38))
    m.play(Create(a30), FadeIn(l30), at=t30, dur=0.7)

    # the product, expanded
    L1 = eq(r"e^{i\pi/3}", r"e^{i\pi/6}", "=", "?", size=50)
    for k in (0, 1):
        L1[k][0].set_color(E)
        L1[k][1].set_color(V)
    L1.move_to(P3(XC, ROWS[0]))
    m.play(Write(L1), at=t_mul + 0.1, dur=0.9)
    L2 = eq("=", r"\left(\tfrac12 + \tfrac{\sqrt3}{2}i\right)", r"\left(\tfrac{\sqrt3}{2} + \tfrac12 i\right)")
    L2.move_to(P3(XC, ROWS[1]))
    m.play(FadeOut(L1[2:]), at=t_ex - 0.1, dur=0.3)
    m.play(Write(L2), at=t_ex, dur=1.1)
    L3 = eq("=", r"\tfrac{\sqrt3}{4}", r"+\tfrac14 i", r"+\tfrac34 i", r"+\tfrac{\sqrt3}{4}i^2")
    L3.move_to(P3(XC, ROWS[2]))
    m.play(Write(L3), at=t_ex + 1.5, dur=1.2)

    # 'cancels': i² = −1, the real parts strike out, i remains
    neg = eq(r"-\tfrac{\sqrt3}{4}").move_to(L3[4]).align_to(L3[4], LEFT)
    neg_dim = neg.copy().set_opacity(0.35)                      # final state in the target: no second .animate
    m.play(Transform(L3[4], neg_dim), at=t_can - 0.5, dur=0.6)
    strikes = VGroup(*(Line(x_.get_corner(DL) + P3(-0.05, 0.05), x_.get_corner(UR) + P3(0.05, -0.05),
                            stroke_color=C.muted, stroke_width=3) for x_ in (L3[1], neg)))
    top.play(LaggedStart(*(Create(x_) for x_ in strikes), lag_ratio=0.4), at=t_can, dur=0.6)
    m.play(L3[1].animate.set_opacity(0.35), at=t_can + 0.2, dur=0.4)
    L4 = eq("=", "i", size=60)
    L4[1].set_color(V)
    L4.move_to(P3(XC, ROWS[3]))
    m.play(FadeIn(L4, shift=0.1 * UP), at=t_can + 1.0, dur=0.5)

    # the 30° arc swings on to start where the 60° one ends: a quarter turn, landing on i
    a30b = Arc(radius=U, start_angle=math.radians(60), angle=math.radians(30), arc_center=O, stroke_color=V,
               stroke_width=9)
    m.play(Transform(a30, a30b), FadeOut(l30), at=t_can + 1.0, dur=1.0, ease="easy_ease")
    top.play(Rotate(rad, math.radians(30), about_point=O), Rotate(pt, math.radians(30), about_point=O),
             at=t_can + 1.0, dur=1.0, ease="easy_ease")
    i_lab = tex("i", 44, V).move_to(on(90, U + 0.4) + P3(0.3, 0))
    l90 = tex(r"90^\circ", 34, V).move_to(on(45, 0.55 * U))
    m.play(FadeIn(i_lab), FadeIn(l90), at=t_can + 1.9, dur=0.5)

    # 'adds': the rule; 'trigonometry': the formula hiding inside it
    rule = eq(r"e^{ia}", r"e^{ib}", "=", r"e^{i(a+b)}", size=50)
    for k in (0, 1, 3):
        rule[k][0].set_color(E)
        rule[k][1].set_color(V)
    rule.move_to(P3(XC, ROWS[4]))
    box = SurroundingRectangle(rule, buff=0.2, color=V, stroke_width=2.4, corner_radius=0.1)
    m.play(Write(rule), at=t_add - 0.2, dur=0.9)
    m.play(Create(box), at=t_add + 0.6, dur=0.6)
    m.play(VGroup(L1[:2], L2, L3[0], L3[2], L3[3], L4).animate.set_opacity(0.4), at=t_add - 0.2, dur=0.5)
    trig = eq(r"\cos(a+b) = \cos a\cos b - \sin a\sin b", size=36).set_opacity(0.6).move_to(P3(XC, ROWS[5]))
    m.play(FadeIn(trig, shift=0.06 * UP), at=t_tri, dur=0.8)

    # out: everything but the circle (it becomes a gimbal ring)
    out_t = float(s.end) - 0.7
    m.play(FadeOut(VGroup(L1[:2], L2, L3, L4, rule, box, trig, nl, a60, a30, l60, l90, i_lab, track_box, tracked)),
           at=out_t, dur=0.6)
    top.play(FadeOut(VGroup(rad, pt, strikes)), at=out_t, dur=0.6)
    grid_l.play(FadeOut(grid), at=out_t, dur=0.6)
