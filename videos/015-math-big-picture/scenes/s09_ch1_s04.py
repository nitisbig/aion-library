"""ch1_s04 · Is it on the circle? (worked example)

The set equation moves to the corner, dimmed. The leash is five grid units: the x axis gets its numbers and a radius
is marked 5. Three points appear with their coordinates, (3, 4), (2, 4) and (4, 4), and nothing moves for the
predict beat. Each test then computes beside the grid (3² + 4² = 9 + 16 = 25; 2² + 4² = 20 < 25; 4² + 4² = 32 > 25)
while the point's legs are drawn dashed in their colors, and the point takes its verdict: on (the circle's color),
inside (blue), outside (grey). On 'sorts' the plane splits into three regions with key words; on 'left over' they
pulse in turn. At the end everything but the circle leaves.
"""
import math

import numpy as np
from aion import *
from aion.components.linalg import grid_lines

from beats import T
from hud import progress
from kit import A0, COL, GRID_C, P3, R1, UNIT1, eq_parts, post, sans, tex, the_circle, tint, triangle

PTS = [(3, 4), (2, 4), (4, 4)]
VERDICT = [("on", C.circle), ("inside", C.foundations), ("outside", C.muted)]
ROWS = [("3^2", "+", "4^2", "=", "9", "+", "16", "=", "25"),
        ("2^2", "+", "4^2", "=", "4", "+", "16", "=", "20", "<", "25"),
        ("4^2", "+", "4^2", "=", "16", "+", "16", "=", "32", ">", "25")]


def G(x, y):
    return GRID_C + UNIT1 * P3(x, y)


def row(parts, x, y):
    m = MathTex(*parts, font_size=34, color=C.text)
    m[0].set_color(COL["x"])
    m[2].set_color(COL["y"])
    m[-1].set_color(C.circle)
    return m.move_to(P3(x, y), aligned_edge=LEFT)


@scene(T.ch1_s04, T.ch1_s05)
def ch1_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    gl, reg, m, top = s.manim(z=-3), s.manim(z=-2), s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_five, t_which = float(T.ch1_s04_five_units), float(T.ch1_s04_which)
    t_v = [float(T.ch1_s04_first), float(T.ch1_s04_second), float(T.ch1_s04_third)]
    t_sort, t_left = float(T.ch1_s04_sorts), float(T.ch1_s04_left_over)
    s.camera.base["zoom"] = 1.04

    # where ch1_s03 left off
    grid = grid_lines(np.eye(2), center=tuple(GRID_C[:2]), unit=UNIT1, box=(-7.4, -4.4, 1.25, 4.4), minor=1,
                      opacity=0.6)
    circle, p = the_circle(R1).move_to(GRID_C), post(GRID_C)
    tri = triangle(A0)
    setb = eq_parts(r"\{", "(x,y)", ":", "x^2", "+", "y^2", "=", "r^2", r"\}", size=46).move_to(P3(3.95, 1.9))
    setb[1].set_color(C.text)
    w_on = sans("on the circle", 32, C.circle).move_to(P3(2.35, 0.15), aligned_edge=LEFT)
    w_pass = sans("passes the test", 32, C.foundations).move_to(P3(2.35, -1.75), aligned_edge=LEFT)
    xa = w_on.get_center()[0]
    arrows = VGroup(*(Arrow(P3(xa + dx, a), P3(xa + dx, b), buff=0, stroke_width=4, color=C.foundations,
                            max_tip_length_to_length_ratio=0.22) for dx, a, b in ((-0.35, -0.2, -1.4), (0.35, -1.4, -0.2))))
    gl.add(grid)
    m.add(circle, p, setb)
    top.add(tri, w_on, w_pass, arrows)
    top.play(FadeOut(VGroup(tri, w_on, w_pass, arrows)), at=t0 + 0.3, dur=0.7)
    small = eq_parts(r"\{", "(x,y)", ":", "x^2", "+", "y^2", "=", "r^2", r"\}", size=34).move_to(P3(4.2, 3.2))
    small[1].set_color(C.text)
    small.set_opacity(0.55)
    m.play(Transform(setb, small), at=t0 + 0.5, dur=1.0, ease="easy_ease")

    # 'five units': numbers on the x axis and a radius marked 5
    nums = VGroup(*(tex(str(k), 26, C.muted).next_to(G(k, 0), DOWN, buff=0.1) for k in range(1, 6)))
    for n_ in nums:
        n_.shift(RIGHT * 0.1)
    a_r = math.radians(155)
    rad = Line(GRID_C, GRID_C + R1 * P3(math.cos(a_r), math.sin(a_r)), stroke_color=C.circle, stroke_width=3)
    five = tex("5", 40, C.circle).move_to(rad.get_center() + 0.28 * P3(-math.sin(a_r), math.cos(a_r)))
    m.play(LaggedStart(*(FadeIn(n_, shift=0.05 * UP) for n_ in nums), lag_ratio=0.12), at=t_five - 0.2, dur=0.8)
    m.play(Create(rad), FadeIn(five), at=t_five + 0.2, dur=0.6)

    # 'Which': three points and their coordinates; then the predict beat
    dots = [Dot(G(*q), radius=0.085, color=C.text) for q in PTS]
    labs = [tex(rf"({q[0]},{q[1]})", 30, C.text) for q in PTS]
    labs[0].next_to(dots[0], UP, buff=0.14)
    labs[1].next_to(dots[1], LEFT, buff=0.14)
    labs[2].next_to(dots[2], RIGHT, buff=0.14)
    for j, (d, l_) in enumerate(zip(dots, labs)):
        top.play(GrowFromCenter(d), FadeIn(l_), at=t_which + 0.25 * j, dur=0.4, ease="out_back")

    # each test computes; the point takes its verdict
    xs, ys = 1.7, [1.75, 0.45, -0.85]
    shown, verdicts = [], []
    for j, (q, tv) in enumerate(zip(PTS, t_v)):
        r_ = row(ROWS[j], xs, ys[j])
        word, col = VERDICT[j]
        verdict = sans(word, 28, col).next_to(r_, DOWN, buff=0.16, aligned_edge=LEFT)
        legs = VGroup(DashedLine(G(0, 0), G(q[0], 0), stroke_color=COL["x"], stroke_width=3, dash_length=0.08),
                      DashedLine(G(q[0], 0), G(*q), stroke_color=COL["y"], stroke_width=3, dash_length=0.08))
        top.play(Create(legs), at=tv - 0.1, dur=0.5)
        shown.append(r_)
        verdicts.append(verdict)
        m.play(Write(r_[:3]), at=tv, dur=0.5)
        m.play(Write(r_[3:]), at=tv + 0.6, dur=0.8)
        top.play(dots[j].animate.set_color(col).scale(1.25), FadeIn(verdict, shift=0.08 * UP), at=tv + 1.5, dur=0.4)
        if j == 0:
            ping = Circle(radius=0.1, stroke_color=C.circle, stroke_width=3).move_to(G(*q))
            top.play(ping.animate.scale(4).set_stroke(opacity=0), at=tv + 1.5, dur=0.8)
            top.remove(ping, at=tv + 2.4)
        top.play(FadeOut(legs), at=tv + 2.6, dur=0.5)

    # 'sorts': the plane splits into three sets
    box = Rectangle(width=8.65, height=8.8).move_to(P3((-7.4 + 1.25) / 2, 0))
    disk = Circle(radius=R1).move_to(GRID_C)
    outside = Difference(box, disk, stroke_width=0, fill_color=C.muted, fill_opacity=0.16)
    inside = Circle(radius=R1, stroke_width=0, fill_color=C.foundations, fill_opacity=0.24).move_to(GRID_C)
    k_in = sans("inside", 34, C.foundations).move_to(G(-1.2, -1.6))
    k_on = sans("on", 34, C.circle).move_to(GRID_C + (R1 + 0.4) * P3(math.cos(-0.75), math.sin(-0.75)))
    k_out = sans("outside", 34, C.muted).move_to(P3(-6.2, -3.35))
    reg.play(GrowFromCenter(inside), at=t_sort, dur=0.8, ease="easy_ease")
    reg.play(FadeIn(outside), at=t_sort + 0.5, dur=0.8)
    m.play(circle.animate.set_stroke(width=7), at=t_sort + 0.9, dur=0.4)
    m.play(LaggedStart(FadeIn(k_in), FadeIn(k_on), FadeIn(k_out), lag_ratio=0.35), at=t_sort + 0.4, dur=1.4)

    # 'nothing left over': each region pulses in turn
    reg.play(inside.animate(rate_func=there_and_back).set_fill(opacity=0.45), at=t_left - 0.4, dur=0.6)
    m.play(circle.animate(rate_func=there_and_back).set_stroke(width=12), at=t_left + 0.2, dur=0.6)
    reg.play(outside.animate(rate_func=there_and_back).set_fill(opacity=0.36), at=t_left + 0.8, dur=0.6)

    # hand-off: everything but the circle leaves
    t_out = float(s.end) - 1.1
    m.play(FadeOut(VGroup(setb, nums, rad, five, k_in, k_on, k_out, p, *shown)), circle.animate.set_stroke(width=5),
           at=t_out, dur=0.8)
    top.play(FadeOut(VGroup(*dots, *labs, *verdicts)), at=t_out, dur=0.8)
    gl.play(FadeOut(grid), at=t_out, dur=0.8)
    reg.play(FadeOut(inside), FadeOut(outside), at=t_out, dur=0.8)
