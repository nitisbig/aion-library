"""ch3_s05 · Any turn at all (Euler).

The arrow left at i keeps turning and sweeps out the unit circle, coming to rest at 1, where it becomes a point.
'L. Euler · 1748' comes up; on 'power' e^{iθ} writes, e in orange (it belongs to Change) and i in violet. On 'sweeps'
the point goes once round the circle: its shadows slide along both axes, and they unroll as graphs, sine to the side
and cosine downward, while the formula completes, = cos θ + i sin θ. On 'Keep an eye' the glyphs e, i and π lift out
and pulse on their words, then park in a small tracker in the corner, to be called back at the end of the video.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, PL_O as O, PL_U as U, P3, caps, plane_grid, plane_line, tex, the_circle, window

XC = 4.45
GX0, KX = O[0] + U + 0.5, 0.3          # sine graph: θ = 0 at GX0, KX per radian
GY0, KY = O[1] - U - 0.4, 0.26           # cosine graph, downward


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lower_third(name, x=2.0, y=3.3):
    g = VGroup(caps(name, 34, C.text), Line(ORIGIN, RIGHT * 3.6, stroke_color=C.muted, stroke_width=1.4))
    return g.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(x, y), aligned_edge=LEFT)


def on(a, r=U):
    return O + r * P3(math.cos(a), math.sin(a))


@scene(T.ch3_s05, T.ch3_s06)
def ch3_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    grid_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_eu, t_pw, t_sw = float(T.ch3_s05_euler), float(T.ch3_s05_power), float(T.ch3_s05_sweeps)
    t_cos, t_eye, t_one = float(T.ch3_s05_cosine), float(T.ch3_s05_keep_an_eye), float(T.ch3_s05_one)
    V, E, Q = C.structure, C.change, C.quantity

    # where ch3_s04 left off
    grid_l.add(plane_grid(1.0))
    nl = plane_line()
    i_lab = tex("i", 48, V).move_to(O + P3(0.32, U + 0.2))
    m.add(nl, i_lab)
    m.play(FadeOut(VGroup(*nl[2::2])), at=t0 + 0.3, dur=0.5)        # the tick labels would sit on the circle

    # the arrow keeps turning and sweeps out the unit circle
    t_a, t_b = t0 + 0.3, t_eu + 0.3

    def sweep(t):
        u = ss((t - t_a) / (t_b - t_a))
        deg = 90 + 270 * u
        g = VGroup(Arc(radius=U, start_angle=0, angle=math.radians(90 * ss((t - t0) / 0.5)), arc_center=O,
                       stroke_color=C.circle, stroke_width=5))
        if deg > 90.2:
            g.add(Arc(radius=U, start_angle=math.pi / 2, angle=math.radians(deg - 90), arc_center=O,
                      stroke_color=C.circle, stroke_width=5))
        a = math.radians(deg)
        g.add(Arrow(O, on(a), buff=0, stroke_width=6, color=V, max_tip_length_to_length_ratio=0.16))
        return g

    top.redraw(window(sweep, t0, t_b + 0.02), during=(t0, t_b + 0.02))
    circ = the_circle(U).move_to(O)
    m.add(circ, at=t_b)
    m.play(FadeOut(i_lab), at=t_a + 0.4, dur=0.4)
    lt = lower_third(r"L.\ Euler\ \textperiodcentered\ 1748")
    m.play(FadeIn(lt, shift=0.08 * LEFT), at=t_eu, dur=0.6)
    plate(s, m, "euler", (2.9, -0.6), 2.6, t_eu + 0.2, t_sw - 1.0, C.structure)
    plate(s, m, "euler_introductio", (5.2, -0.6), 2.6, t_eu + 0.8, t_sw - 1.0, C.structure, caption="Introductio \\textperiodcentered\\ 1748")
    m.play(FadeOut(lt), at=t_sw - 1.0, dur=0.5)

    # the point at angle θ, its shadows and their graphs
    t_s0, t_s1 = t_sw - 0.1, t_sw + 6.2

    def theta(t):
        return 2 * math.pi * ss((t - t_s0) / (t_s1 - t_s0))

    def point(t):
        th = theta(t)
        p = on(th)
        cx, sy = O + P3(U * math.cos(th), 0), O + P3(0, U * math.sin(th))
        g = VGroup(Line(O, p, stroke_color=V, stroke_width=4))
        sh = ss((t - t_s0) / 0.4) * (1 - ss((t - t_s1 - 0.6) / 0.6))
        if sh > 0:
            g.add(DashedLine(p, cx, stroke_color=C.text, stroke_width=2, dash_length=0.08, stroke_opacity=sh),
                  DashedLine(p, sy, stroke_color=C.text, stroke_width=2, dash_length=0.08, stroke_opacity=sh),
                  Dot(cx, radius=0.07, color=C.text, fill_opacity=sh), Dot(sy, radius=0.07, color=C.text, fill_opacity=sh))
        if t > t_s0 and th > 0.02:
            ts = np.linspace(0, th, max(int(th * 24), 3))
            sine = VMobject(stroke_color=C.text, stroke_width=3).set_points_smoothly(
                [P3(GX0 + KX * a, O[1] + U * math.sin(a)) for a in ts])
            cosine = VMobject(stroke_color=C.text, stroke_width=3).set_points_smoothly(
                [P3(O[0] + U * math.cos(a), GY0 - KY * a) for a in ts])
            fg = 1 - ss((t - float(s.end) + 0.7) / 0.6)        # the graphs leave with the formula
            sine.set_stroke(opacity=fg)
            cosine.set_stroke(opacity=fg)
            g.add(sine, cosine)
            if sh > 0:
                g.add(DashedLine(sy, P3(GX0 + KX * th, sy[1]), stroke_color=C.muted, stroke_width=1.4,
                                 dash_length=0.06, stroke_opacity=sh),
                      DashedLine(cx, P3(cx[0], GY0 - KY * th), stroke_color=C.muted, stroke_width=1.4,
                                 dash_length=0.06, stroke_opacity=sh))
        g.add(Dot(p, radius=0.1, color=V))
        return g

    top.redraw(window(point, t_b, float(s.end)), during=(t_b, float(s.end)))
    th_lab = tex(r"\theta", 40, V).move_to(O + P3(0.75, 0.32))
    m.play(FadeIn(th_lab), at=t_sw, dur=0.4)
    m.play(FadeOut(th_lab), at=t_s1 - 0.4, dur=0.4)
    g_axes = VGroup(Line(P3(GX0, O[1]), P3(GX0 + KX * 2 * math.pi + 0.2, O[1]), stroke_color=C.muted, stroke_width=1.6),
                    Line(P3(O[0], GY0), P3(O[0], GY0 - KY * 2 * math.pi - 0.15), stroke_color=C.muted, stroke_width=1.6))
    m.play(Create(g_axes), at=t_sw - 0.3, dur=0.5)
    sin_l = tex(r"\sin\theta", 32, C.text).move_to(P3(GX0 + KX * 2 * math.pi + 0.55, O[1] + 0.3))
    cos_l = tex(r"\cos\theta", 32, C.text).move_to(P3(O[0] - U - 0.75, GY0 - KY * math.pi))

    # Euler's formula
    F = MathTex(r"e^{i\theta}", "=", r"\cos\theta", "+", r"i\sin\theta", font_size=52, color=C.text)
    F[0][0].set_color(E)
    F[0][1].set_color(V)
    F[4][0].set_color(V)
    F.move_to(P3(XC, 1.9))
    m.play(Write(F[0]), at=t_pw, dur=0.8)
    m.play(Write(F[1:]), at=t_cos - 0.2, dur=1.4)
    m.play(FadeIn(cos_l), Indicate(F[2], color=C.text), at=t_cos, dur=0.6)
    m.play(FadeIn(sin_l), Indicate(F[4], color=C.text), at=t_cos + 2.4, dur=0.6)

    # 'Keep an eye on e, i and π': three glyphs lift, pulse on their words, then park in a tracker
    gl = VGroup(tex("e", 84, E), tex("i", 84, V), tex(r"\pi", 84, Q)).arrange(RIGHT, buff=0.7).move_to(P3(XC, -0.4))
    m.play(LaggedStart(*(FadeIn(g_, shift=0.15 * UP) for g_ in gl), lag_ratio=0.25), at=t_eye - 0.7, dur=0.6)
    for g_, dt in zip(gl, (0.32, 0.96, 1.2)):
        m.play(Indicate(g_, scale_factor=1.25, color=g_.get_color()), at=t_eye + dt, dur=0.5)
    track_box = RoundedRectangle(width=1.95, height=0.78, corner_radius=0.14, stroke_color=C.map_off, stroke_width=1.6)
    track_box.move_to(P3(5.75, -3.35))
    tracked = VGroup(tex("e", 40, E), tex("i", 40, V), tex(r"\pi", 40, Q)).arrange(RIGHT, buff=0.38)
    tracked.move_to(track_box)
    m.play(Create(track_box), at=t_one + 2.6, dur=0.5)
    m.play(ReplacementTransform(gl, tracked), at=t_one + 2.8, dur=1.0, ease="easy_ease")

    out_t = float(s.end) - 0.7
    m.play(FadeOut(VGroup(F, sin_l, cos_l, g_axes)), at=out_t, dur=0.6)
