"""ch4_s02 · Stretch, don't tear.

The square band from the hook. On 'Stretching', 'bending', 'squashing' the allowed moves come up as key words; on
'Cutting' and 'gluing' two more appear dimmed and struck out. The band morphs on its words into a triangle, a wobbly
blob and a star (radial functions, all the same area). On 'figure eight' two opposite sides are pulled in towards each
other; just before they meet a dashed ring and a cross flash on the pinch point, and the band springs back to a
circle. On 'every one of these loops' the five loops line up in a row joined by equals signs.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, P3, band, caps, band_theta, r_blob, r_poly, r_star, sans, tex, window

BC, BR = P3(0, -0.1), 1.8
ROW_Y, ROW_R = -2.75, 0.48
ROW_X = (-5.0, -2.5, 0.0, 2.5, 5.0)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch4_s02, T.ch4_s03)
def ch4_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_st, t_cut, t_tri = float(T.ch4_s02_stretching), float(T.ch4_s02_cutting), float(T.ch4_s02_triangle)
    t_blob, t_star, t_fig, t_same = (float(T.ch4_s02_blob), float(T.ch4_s02_star), float(T.ch4_s02_figure_eight),
                                     float(T.ch4_s02_same))
    S = C.space
    th = band_theta()
    shapes = {"circle": np.full_like(th, BR), "square": r_poly(4, BR), "triangle": r_poly(3, BR, -math.pi / 2),
              "blob": r_blob(BR), "star": r_star(BR)}
    # pinch: the top and bottom pulled in towards the centre
    pinch = np.full_like(th, BR) * (1 - 0.93 * np.abs(np.sin(th)) ** 6)
    t_pin0, t_pin1, t_back = t_fig + 0.2, t_fig + 1.9, t_fig + 2.6
    seq = [(t0, "square"), (t_tri - 0.1, "triangle"), (t_blob - 0.1, "blob"), (t_star - 0.1, "star"),
           (t_pin0 - 0.6, "circle")]

    def r_at(t):
        r = shapes[seq[0][1]]
        for (ta, a), (tb, b) in zip(seq, seq[1:]):                     # each morph takes 0.7 s from its word
            if t >= tb:
                u = ss((t - tb) / 0.7)
                r = (1 - u) * shapes[a] + u * shapes[b]
        if t >= t_pin0:                                                # the pinch, then the spring back
            u = ss((t - t_pin0) / (t_pin1 - t_pin0))
            v = 1 - ss((t - t_back) / 0.5)
            k = u * v
            if t >= t_back:                                            # elastic overshoot on release
                k = -0.08 * math.exp(-4 * (t - t_back - 0.5)) * math.sin(14 * (t - t_back - 0.5)) if t > t_back + 0.5 \
                    else k
            r = (1 - k) * shapes["circle"] + k * pinch
        return r

    def loop(t):
        return band(r_at(t), BC)

    t_row = t_same - 2.6
    glow_layer(s, z=1.2, color=C.space, k=0.7).redraw(window(loop, t0, t_row), during=(t0, t_row))

    # the moves: allowed, then not
    ok = VGroup(sans("stretch", 34, C.text), sans("bend", 34, C.text), sans("squash", 34, C.text))
    ok.arrange(RIGHT, buff=0.6).move_to(P3(-3.6, 3.1))
    no = VGroup(sans("cut", 34, C.muted), sans("glue", 34, C.muted)).arrange(RIGHT, buff=0.6).move_to(P3(3.9, 3.1))
    for k, dt in enumerate((0.0, 1.2, 1.9)):
        m.play(FadeIn(ok[k], shift=0.08 * DOWN), at=t_st + dt, dur=0.45)
    strikes = VGroup(*(Line(w.get_left() + P3(-0.08, 0), w.get_right() + P3(0.08, 0), stroke_color=C.muted,
                            stroke_width=3) for w in no))
    m.play(FadeIn(no[0], shift=0.08 * DOWN), at=t_cut, dur=0.45)
    m.play(FadeIn(no[1], shift=0.08 * DOWN), at=t_cut + 0.6, dur=0.45)
    m.play(LaggedStart(*(Create(x_) for x_ in strikes), lag_ratio=0.4), at=t_cut + 1.2, dur=0.6)

    # the forbidden pinch: a dashed ring and a cross on the meeting point
    t_fl = t_pin1 - 0.1
    ring = DashedVMobject(Circle(radius=0.42, stroke_color=C.muted, stroke_width=2.6).move_to(BC), num_dashes=16)
    cross = VGroup(Line(P3(-0.18, -0.18), P3(0.18, 0.18)), Line(P3(-0.18, 0.18), P3(0.18, -0.18)))
    cross.set_stroke(C.text, 4).move_to(BC)
    top.play(FadeIn(ring, scale=1.4), GrowFromCenter(cross), at=t_fl, dur=0.35)
    top.play(FadeOut(VGroup(ring, cross)), at=t_back + 0.1, dur=0.4)
    eight = sans("figure eight", 30, C.muted).move_to(BC + P3(0, -BR - 0.55))
    m.play(FadeIn(eight), at=t_fig, dur=0.4)
    m.play(FadeOut(eight), at=t_back + 0.2, dur=0.4)

    # 'every one of these loops': the row, joined by equals signs
    row = VGroup()
    for x, key in zip(ROW_X, ("circle", "square", "triangle", "blob", "star")):
        row.add(band(shapes[key] * (ROW_R / BR), P3(x, ROW_Y), width=6))
    eqs = VGroup(*(tex("=", 48, C.text).move_to(P3(0.5 * (a + b), ROW_Y)) for a, b in zip(ROW_X, ROW_X[1:])))
    big = band(shapes["circle"], BC)
    m.add(big, at=t_row)
    m.play(Transform(big, row[0]), at=t_row, dur=1.0, ease="easy_ease")
    m.play(LaggedStart(*(GrowFromCenter(r_) for r_ in row[1:]), lag_ratio=0.2), at=t_row + 0.6, dur=1.2)
    m.play(LaggedStart(*(FadeIn(e_) for e_ in eqs), lag_ratio=0.2), at=t_row + 1.2, dur=1.0)
    m.play(FadeOut(VGroup(ok, no, strikes)), at=t_row, dur=0.6)
    same = caps("same circle", 48, S).move_to(P3(0, -1.45))
    m.play(FadeIn(same, shift=0.08 * UP), at=t_same - 0.1, dur=0.6)
