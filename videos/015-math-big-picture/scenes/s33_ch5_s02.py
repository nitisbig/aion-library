"""ch5_s02 · Zoom until it's straight.

On 'speedometer' a short drive is drawn as distance against time (C.change), with a speedometer beside it; a point
rides the curve and the needle follows its speed. On 'average' a dashed chord across the whole trip gives the average
(48 km/h), then dims. On 'right now' the point stops. On 'zoom' the view zooms ×5, then ×100 on that point (the curve
redrawn at every scale, so it stays crisp) until the curve and its tangent are one straight line. On 'derivative' a
rise-over-run triangle reads the slope, the same number as the dial, and the limit formula writes. On 'Newton' a
lower third reads I. Newton · G. W. Leibniz · 1680s.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, P3, caps, sans, tex, window

X0, Y0, SX, SY = -6.3, -2.5, 0.8, 0.55            # graph origin; world units per minute and per km
BOX = (-6.9, -3.0, 2.3, 2.6)                      # the graph's clip box
T_END = 10.0
T_STAR = 3.0                                      # 'right now'
DC, DR = P3(4.75, 1.0), 1.45                      # the dial
V_MAX = 120.0


def s_of(t):
    u = np.clip(np.asarray(t, float) / T_END, 0, 1)
    return 8 * (u - 0.9 * np.sin(4 * np.pi * u) / (4 * np.pi))          # stop and go: two slow-downs


def v_of(t):                                      # km/h
    h = 1e-4
    return float((s_of(t + h) - s_of(t - h)) / (2 * h)) * 60


V_AVG = float(s_of(T_END)) / T_END * 60
V_STAR = v_of(T_STAR)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def to_screen(t, s):
    return np.array([X0 + SX * t, Y0 + SY * s, 0.0])


P_S = to_screen(T_STAR, float(s_of(T_STAR)))


def dial(v, op=1.0):
    g = VGroup(Arc(radius=DR, start_angle=math.radians(-45), angle=math.radians(270), arc_center=DC,
                   stroke_color=C.circle, stroke_width=3, stroke_opacity=op))
    for k in range(0, 121, 10):
        a = math.radians(225 - 270 * k / V_MAX)
        d = P3(math.cos(a), math.sin(a))
        ln = 0.2 if k % 20 == 0 else 0.1
        g.add(Line(DC + (DR - ln) * d, DC + DR * d, stroke_color=C.circle, stroke_width=2.4, stroke_opacity=op))
        if k % 20 == 0:
            g.add(sans(str(k), 22, C.muted).move_to(DC + (DR - 0.42) * d).set_opacity(op))
    a = math.radians(225 - 270 * min(max(v, 0), V_MAX) / V_MAX)
    g.add(Line(DC, DC + (DR - 0.25) * P3(math.cos(a), math.sin(a)), stroke_color=C.change, stroke_width=5,
               stroke_opacity=op), Dot(DC, radius=0.08, color=C.change).set_opacity(op))
    g.add(VGroup(tex(f"{v:.0f}", 50, C.change), sans("km/h", 28, C.muted)).arrange(RIGHT, buff=0.15,
                                                                                    aligned_edge=DOWN)
          .move_to(DC + P3(0, -DR - 0.15)).set_opacity(op))
    return g


@scene(T.ch5_s02, T.ch5_s03)
def ch5_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    ax_l, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_sp, t_av, t_zo = float(T.ch5_s02_speedometer), float(T.ch5_s02_average), float(T.ch5_s02_zoom)
    t_str, t_der, t_nw = float(T.ch5_s02_straight), float(T.ch5_s02_derivative), float(T.ch5_s02_newton)
    t_now, t_pt = t_av + 2.88, t_der + 2.24                                 # 'right now' 'single point'
    Ch = C.change
    out_t = t1 - 0.8

    # the word from ch5_s01
    word = caps("calculus", 60, Ch).move_to(P3(0, 3.3))
    m.add(word)
    m.play(FadeOut(word), at=t0 + 0.1, dur=0.5)

    # axes, a faint grid, labels
    xs = np.arange(0, T_END + 0.1, 1.0)
    ys = np.arange(0, 8.1, 1.0)
    grid = VGroup(*(Line(to_screen(x, 0), to_screen(x, 8.6), stroke_color=C.grid, stroke_width=1.2,
                         stroke_opacity=0.45) for x in xs[1:]),
                  *(Line(to_screen(0, y), to_screen(T_END + 0.6, y), stroke_color=C.grid, stroke_width=1.2,
                         stroke_opacity=0.45) for y in ys[1:]))
    axes = VGroup(Arrow(to_screen(0, 0), to_screen(T_END + 0.9, 0), buff=0, stroke_width=3, color=C.axis,
                        tip_length=0.2),
                  Arrow(to_screen(0, 0), to_screen(0, 9.1), buff=0, stroke_width=3, color=C.axis, tip_length=0.2))
    labs = VGroup(sans("time", 28, C.muted).next_to(to_screen(T_END + 0.9, 0), DOWN, buff=0.15).shift(0.3 * LEFT),
                  sans("distance", 28, C.muted).next_to(to_screen(0, 9.1), RIGHT, buff=0.15))
    ax_l.play(FadeIn(grid), Create(axes), FadeIn(labs), at=t_sp - 0.6, dur=0.8)

    # the drive, and the dial
    ts = np.linspace(0, T_END, 241)
    trip = VMobject(stroke_color=Ch, stroke_width=5).set_points_smoothly([to_screen(t, s_of(t)) for t in ts])
    m.play(Create(trip), at=t_sp - 0.2, dur=1.2, ease="easy_ease")
    t_ride0 = t_sp + 0.8

    def ride_t(t):
        return T_STAR * ss((t - t_ride0) / (t_now - t_ride0))

    def ride(t):
        tt = ride_t(t)
        f = 1 - ss((t - t_zo + 0.3) / 0.4)
        return Dot(to_screen(tt, float(s_of(tt))), radius=0.1, color=C.text).set_opacity(f)

    top.redraw(window(ride, t_ride0, t_zo + 0.2), during=(t_ride0, t_zo + 0.25))

    def dial_at(t):
        tt = ride_t(t)
        v = v_of(tt) if tt > 0.02 else 0.0
        f = ss((t - t_sp + 0.4) / 0.6) * (1 - ss((t - out_t) / 0.6))
        return dial(v, f)

    m.redraw(window(dial_at, t_sp - 0.4, t1 - 0.05), during=(t_sp - 0.4, t1))

    # 'average': a chord across the whole trip, then set aside
    chord = DashedLine(to_screen(0, 0), to_screen(T_END, float(s_of(T_END))), dash_length=0.14, stroke_color=C.text,
                       stroke_width=2.6)
    avg = VGroup(sans("average", 28, C.text), tex(rf"{V_AVG:.0f}", 36, C.text), sans("km/h", 28, C.muted))
    avg.arrange(RIGHT, buff=0.14, aligned_edge=DOWN).move_to(to_screen(5.2, 6.4))
    m.play(Create(chord), FadeIn(avg), at=t_av - 0.1, dur=0.7)
    m.play(chord.animate.set_stroke(opacity=0.25), avg.animate.set_opacity(0.3), at=t_av + 1.6, dur=0.6)
    m.play(FadeOut(VGroup(chord, avg)), at=t_zo - 0.4, dur=0.4)

    # 'zoom': ×10, then ×100, anchored on the point; the curve redrawn at each scale
    lz = keys((t_zo - 0.1, 0.0), (t_zo + 1.0, math.log10(5), "easy_ease"), (t_zo + 1.4, math.log10(5)),
              (t_str + 0.1, 2.0, "easy_ease"))
    ax_l.play(FadeOut(VGroup(grid, axes, labs)), at=t_zo - 0.1, dur=0.5)
    m.remove(trip, at=t_zo - 0.1)

    def zoomed(t):
        Z = 10 ** lz(t)
        g = VGroup()
        f = 1 - ss((t - out_t) / 0.6)
        x_lo, x_hi = BOX[0], BOX[2]
        tt = T_STAR + (np.linspace(x_lo, x_hi, 300) - P_S[0]) / (SX * Z)
        pts = [P_S + (to_screen(a, float(s_of(a))) - P_S) * Z for a in tt if 0.0 <= a <= T_END]
        pts = [p for p in pts if BOX[1] <= p[1] <= BOX[3]]
        if len(pts) > 2:
            g.add(VMobject(stroke_color=Ch, stroke_width=5, stroke_opacity=f).set_points_as_corners(pts))
        g.add(Dot(P_S, radius=0.1, color=C.text).set_opacity(f))
        return g

    m.redraw(window(zoomed, t_zo - 0.1, t1 - 0.05), during=(t_zo - 0.1, t1))

    def ztag(t):
        z = lz(t)
        f = ss((t - t_zo) / 0.3) * (1 - ss((t - t_der + 0.5) / 0.5))
        lab = r"\times 100" if z > 1.6 else r"\times 5" if z > 0.35 else r"\times 1"
        return tex(lab, 40, C.muted).move_to(P_S + P3(1.3, -1.0)).set_opacity(f)

    top.redraw(window(ztag, t_zo, t_der), during=(t_zo, t_der + 0.05))

    # 'straight': the tangent lies on the curve
    slope = (SY / SX) * V_STAR / 60                    # screen slope
    d = np.array([1.0, slope, 0.0]) / math.hypot(1, slope)
    tan = Line(P_S - 3.2 * d, P_S + 3.2 * d, stroke_color=C.text, stroke_width=2.2)
    top.play(Create(tan), at=t_str + 0.2, dur=0.8)

    # 'derivative': rise over run; it reads the dial's number
    run = 1.6
    A, B, Cc = P_S, P_S + P3(run, 0), P_S + P3(run, run * slope)
    tri = VGroup(Line(A, B, stroke_color=C.text, stroke_width=2.6), Line(B, Cc, stroke_color=C.text, stroke_width=2.6))
    l_run = sans("run", 28, C.muted).next_to(Line(A, B), DOWN, buff=0.14)
    l_rise = sans("rise", 28, C.muted).next_to(Line(B, Cc), RIGHT, buff=0.14)
    top.play(Create(tri), FadeIn(l_run), FadeIn(l_rise), at=t_der - 0.1, dur=0.7)
    stag = VGroup(sans("slope", 30, C.text), tex(rf"= {V_STAR:.0f}", 40, Ch), sans("km/h", 28, C.muted))
    stag.arrange(RIGHT, buff=0.14, aligned_edge=DOWN).move_to(P_S + P3(-1.9, 1.6))
    top.play(FadeIn(stag, shift=0.08 * UP), at=t_der + 0.5, dur=0.5)
    ring = Circle(radius=0.55, stroke_color=Ch, stroke_width=3).move_to(DC + P3(-0.1, -DR - 0.15))
    top.play(Create(ring), at=t_der + 0.9, dur=0.5)
    top.play(FadeOut(ring), at=t_der + 2.0, dur=0.5)
    lim = MathTex(r"\frac{dy}{dx}", "=", r"\lim_{h\to 0}", r"\frac{y(x+h)-y(x)}{h}", font_size=38, color=C.text)
    lim[0].set_color(Ch)
    lim.move_to(P3(4.25, -2.55))
    m.play(Write(lim), at=t_pt - 0.2, dur=1.2)

    # 'Newton'
    lt = VGroup(caps(r"I.\ Newton\ \textperiodcentered\ G.\ W.\ Leibniz\ \textperiodcentered\ 1680s", 32, C.text),
                Line(ORIGIN, RIGHT * 5.2, stroke_color=C.muted, stroke_width=1.4))
    lt.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(-6.3, 3.3), aligned_edge=LEFT)
    top.play(FadeIn(lt, shift=0.08 * LEFT), at=t_nw - 0.1, dur=0.6)
    plate(s, top, "newton", (1.25, 1.55), 1.9, t_nw + 0.2, out_t + 0.6, C.change)
    plate(s, top, "leibniz", (1.25, -0.55), 1.9, t_nw + 0.6, out_t + 0.6, C.change)

    # out
    top.play(FadeOut(VGroup(tan, tri, l_run, l_rise, stag, lt)), at=out_t, dur=0.6)
    m.play(FadeOut(lim), at=out_t, dur=0.6)
