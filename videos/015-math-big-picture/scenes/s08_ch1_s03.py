"""ch1_s03 · From rule to equation.

The post and circle slide left and the Classic grid comes up under them, post at the origin. A point on the circle
drops a right triangle: x along, y up, the leash r as the long side. Pythagoras writes x² + y² = r² term by term, each
term in its side's color; then the point runs once round the circle with the triangle redrawn live, and a readout
shows x, y and x² + y² (always 25.00: the leash is five grid units). On 'braces' the equation slides into set-builder
braces. Lower third: G. Cantor · 1874. Then 'on the circle' and 'passes the test' with an arrow each way; the right
arrow lights on 'if and only if', the left on 'both directions'.
"""
import math

import numpy as np
from aion import *
from aion.components.linalg import grid_lines

from beats import T
from hud import progress
from kit import plate, A0, COL, GRID_C, P3, R1, UNIT1, Digits, caps, eq_parts, post, sans, tex, the_circle, triangle, window

@scene(T.ch1_s03, T.ch1_s04)
def ch1_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    gl, m, top = s.manim(z=-2), s.manim(z=0), s.manim(z=1)
    t_grid, t_tri, t_py = float(T.ch1_s03_grid), float(T.ch1_s03_right_triangle), float(T.ch1_s03_pythagoras)
    t_br, t_can = float(T.ch1_s03_braces), float(T.ch1_s03_cantor)
    t_iff, t_both = float(T.ch1_s03_if_and_only_if), float(T.ch1_s03_both_directions)
    s.camera.push(t_grid, zoom=1.04, dur=float(s.end) - t_grid, ease="smooth")

    circle, p = the_circle(R1), post()
    m.add(circle, p)
    m.play(VGroup(circle, p).animate.move_to(GRID_C), at=t_grid - 1.5, dur=1.3, ease="easy_ease")
    grid = grid_lines(np.eye(2), center=tuple(GRID_C[:2]), unit=UNIT1, box=(-7.4, -4.4, 1.25, 4.4), minor=1,
                      opacity=0.6)
    gl.play(FadeIn(grid), at=t_grid, dur=1.0)

    # the triangle drops from the point (3, 4)
    tri = triangle(A0)
    pdot = tri[-1]
    top.play(GrowFromCenter(pdot), at=t_tri - 0.4, dur=0.35, ease="out_back")
    top.play(Create(tri[1]), at=t_tri, dur=0.5)                          # y drops to the axis
    top.play(Create(tri[0]), at=t_tri + 0.4, dur=0.5)                    # x along
    top.play(Create(tri[2]), FadeIn(tri[3:-1]), at=t_tri + 0.9, dur=0.6)  # the leash, labels, right angle

    # Pythagoras, term by term
    eq = eq_parts("x^2", "+", "y^2", "=", "r^2").move_to(P3(4.15, 1.9))
    for j, (part, dt) in enumerate(((eq[0], 0.0), (VGroup(eq[1], eq[2]), 0.6), (VGroup(eq[3], eq[4]), 1.3))):
        m.play(Write(part), at=t_py + dt, dur=0.5)

    # 'a test you can run on any point': the point runs once round the circle; a live readout
    t_run0, t_run1 = t_py + 2.4, t_br - 0.7

    def ang(t):
        u = min(max((t - t_run0) / (t_run1 - t_run0), 0.0), 1.0)
        return A0 + 2 * math.pi * (u * u * (3 - 2 * u))

    top.remove(*tri, at=t_run0)
    top.redraw(window(lambda t: triangle(ang(t)), t_run0, t_run1 + 1.2), during=(t_run0, t_run1 + 1.25))
    top.add(triangle(A0), at=t_run1 + 1.2)

    digits = Digits(34)
    labs = VGroup(tex("x", 40, COL["x"]), tex("y", 40, COL["y"]), eq_parts("x^2", "+", "y^2", size=40))
    rows_y = [0.75, 0.15, -0.45]
    for lab, y in zip(labs, rows_y):
        lab.move_to(P3(2.55, y), aligned_edge=LEFT)
    right = 5.9

    def readout(t):
        a = ang(t)
        x, y = 5 * math.cos(a), 5 * math.sin(a)
        k = min(1.0, (t - t_run0 + 0.3) / 0.4, (t_br + 0.2 - t) / 0.4)
        g = VGroup(digits.number(f"{x:.2f}".replace("-", "-"), right, rows_y[0] - 0.15),
                   digits.number(f"{y:.2f}", right, rows_y[1] - 0.15),
                   digits.number(f"{x * x + y * y:.2f}", right, rows_y[2] - 0.15, color=C.circle))
        return g.set_opacity(max(k, 0.0))

    m.play(FadeIn(labs), at=t_run0 - 0.3, dur=0.4)
    m.redraw(window(readout, t_run0 - 0.3, t_br + 0.2), during=(t_run0 - 0.3, t_br + 0.25))
    m.play(FadeOut(labs), at=t_br - 0.2, dur=0.4)

    # 'braces': the test becomes a set
    setb = eq_parts(r"\{", "(x,y)", ":", "x^2", "+", "y^2", "=", "r^2", r"\}", size=46).move_to(P3(3.95, 1.9))
    setb[1].set_color(C.text)
    m.play(TransformMatchingTex(eq, setb), at=t_br, dur=1.0, ease="easy_ease")
    m.play(circle.animate(rate_func=there_and_back).set_stroke(color=C.foundations, width=7), at=t_br + 0.6, dur=1.0)

    # lower third
    lt = VGroup(Line(ORIGIN, RIGHT * 3.2, stroke_color=C.muted, stroke_width=1.4),
                caps(r"G.\ Cantor\ \textperiodcentered\ 1874", 36, C.text))
    lt.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to(P3(2.3, -3.2), aligned_edge=LEFT)
    m.play(Create(lt[0]), FadeIn(lt[1], shift=0.1 * UP), at=t_can, dur=0.6)
    plate(s, m, "cantor", (4.0, -1.35), 2.6, t_can + 0.2, t_iff - 1.6, C.foundations)
    m.play(FadeOut(lt), at=t_iff - 1.6, dur=0.5)

    # if and only if: an arrow each way
    w_on = sans("on the circle", 32, C.circle)
    w_pass = sans("passes the test", 32, C.foundations)
    w_on.move_to(P3(2.35, 0.15), aligned_edge=LEFT)
    w_pass.move_to(P3(2.35, -1.75), aligned_edge=LEFT)
    xa = w_on.get_center()[0]
    r_arr = Arrow(P3(xa - 0.35, -0.2), P3(xa - 0.35, -1.4), buff=0, stroke_width=4, color=C.map_off,
                  max_tip_length_to_length_ratio=0.22)
    l_arr = Arrow(P3(xa + 0.35, -1.4), P3(xa + 0.35, -0.2), buff=0, stroke_width=4, color=C.map_off,
                  max_tip_length_to_length_ratio=0.22)
    t_bel = t_iff - 1.8                                                   # 'A point belongs'
    m.play(FadeIn(w_on), FadeIn(w_pass), FadeIn(r_arr), FadeIn(l_arr), at=t_bel, dur=0.6)
    m.play(r_arr.animate.set_color(C.foundations), at=t_iff, dur=0.4)
    m.play(Indicate(w_pass, color=C.foundations, scale_factor=1.06), at=t_iff + 0.4, dur=0.6)
    m.play(l_arr.animate.set_color(C.foundations), at=t_both, dur=0.4)
    m.play(Indicate(w_on, color=C.circle, scale_factor=1.06), at=t_both + 0.3, dur=0.5)
