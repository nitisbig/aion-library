"""ch5_s04 · Growing the radius.

The circle comes back with its radius r. On 'Grow' the radius stretches by a nudge dr and the new area, a thin ring
(C.change, drawn thick so it can be seen), fills in. On 'Cut' the ring is cut at the top; on 'unroll' it opens out and
lies flat below the circle: each edge keeps its own length, so the strip is a slight trapezoid, 2πr along its inner
edge. On 'circumference' a brace reads 2πr; on 'thick' the end reads dr. On 'rate' dA ≈ 2πr dr writes; on 'derivative'
d/dr (πr²) = 2πr, and the 2πr is boxed on 'circumference'.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, tex, the_circle, window

CC, R, DR = P3(-3.0, 0.65), 1.6, 0.22
STRIP = P3(0.0, -2.45)                        # where the inner edge's midpoint lands


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def layer(h, u, n=180):
    """Edge h (0 = inner, DR = outer) of the ring, unrolled by u ∈ [0, 1] about its bottom point, which is (0, -h)
    relative to the inner bottom. The edge keeps its length 2π(R + h); its curvature falls to 0."""
    L = 2 * math.pi * (R + h)
    s = np.linspace(-L / 2, L / 2, n)
    k = (1 - u) / (R + h)
    if k < 1e-6:
        x, y = s, np.zeros_like(s)
    else:
        x, y = np.sin(k * s) / k, (1 - np.cos(k * s)) / k
    return np.stack([x, y - h, np.zeros_like(s)], -1)


@scene(T.ch5_s04, T.ch5_s05)
def ch5_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_ci, t_gr, t_un = float(T.ch5_s04_circle), float(T.ch5_s04_grow), float(T.ch5_s04_unroll)
    t_cf, t_rt, t_dv = float(T.ch5_s04_circumference), float(T.ch5_s04_rate), float(T.ch5_s04_derivative)
    t_cut, t_thick, t_cf2 = t_un - 0.81, t_cf + 1.2, t_dv + 2.0            # 'Cut' 'thick' 'circumference.'
    Ch = C.change
    out_t = t1 - 0.8

    # the circle and its radius
    circ = the_circle(R).move_to(CC)
    m.play(Create(circ), at=t_ci - 0.9, dur=0.9, ease="easy_ease")
    rad = Line(CC, CC + P3(R, 0), stroke_color=C.circle, stroke_width=3)
    r_lab = tex("r", 40, C.circle).move_to(CC + P3(R / 2, 0.3))
    m.play(Create(rad), FadeIn(r_lab), at=t_ci, dur=0.5)

    # 'Grow': the nudge dr, and the thin ring
    g_k = lambda t: ss((t - t_gr) / 1.0)
    u_k = lambda t: ss((t - t_un) / 2.2)
    bottom0 = CC + P3(0, -R)

    def ring(t):
        g, u = g_k(t), u_k(t)
        f = 1 - ss((t - out_t) / 0.6)
        if g <= 0:
            return VGroup()
        ua = ss(min(1.0, 1.7 * u))                               # it moves clear of the circle early
        anchor = (1 - ua) * bottom0 + ua * STRIP
        if u <= 0:                                               # still a ring (the cut shows as a hairline gap)
            a = Annulus(inner_radius=R, outer_radius=R + DR * g, fill_color=Ch, fill_opacity=0.55 * f,
                        stroke_color=Ch, stroke_width=2, stroke_opacity=f).move_to(CC)
            return VGroup(a)
        inner, outer = layer(0.0, u) + anchor, layer(DR, u) + anchor
        poly = Polygon(*inner, *outer[::-1], fill_color=Ch, fill_opacity=0.55 * f, stroke_color=Ch, stroke_width=2,
                       stroke_opacity=f)
        return VGroup(poly)

    top.redraw(window(ring, t_gr, t1 - 0.05), during=(t_gr, t1))
    nudge = Line(CC + P3(R, 0), CC + P3(R + DR, 0), stroke_color=Ch, stroke_width=4)
    dr_lab = tex("dr", 36, Ch).move_to(CC + P3(R + DR + 0.4, 0.0))
    m.play(Create(nudge), FadeIn(dr_lab), at=t_gr + 0.1, dur=0.6)
    m.play(FadeOut(VGroup(nudge, dr_lab)), at=t_un - 0.1, dur=0.4)

    # 'Cut': a mark at the top
    cut = Line(CC + P3(0, R - 0.15), CC + P3(0, R + DR + 0.15), stroke_color=C.text, stroke_width=3)
    top.play(Create(cut), at=t_cut, dur=0.3)
    top.play(FadeOut(cut), at=t_un, dur=0.3)

    # 'circumference', 'thick': the strip's sizes
    L0 = 2 * math.pi * R
    left, right = STRIP + P3(-L0 / 2, 0), STRIP + P3(L0 / 2, 0)
    brace = BraceBetweenPoints(left, right, direction=UP, color=C.circle).shift(0.08 * UP)
    b_lab = tex(r"2\pi r", 40, C.circle).next_to(brace, UP, buff=0.1)
    m.play(GrowFromCenter(brace), FadeIn(b_lab), at=t_cf - 0.1, dur=0.6)
    L1 = 2 * math.pi * (R + DR)
    end_x = STRIP[0] + L1 / 2
    d_lab = tex("dr", 36, Ch).move_to(P3(end_x + 0.45, STRIP[1] - DR / 2))
    m.play(FadeIn(d_lab, shift=0.06 * LEFT), at=t_thick, dur=0.5)

    # 'rate' and 'derivative'
    e1 = MathTex("dA", r"\approx", r"2\pi r", r"\,dr", font_size=54, color=C.text)
    e1[0].set_color(Ch)
    e1[2].set_color(C.circle)
    e1[3].set_color(Ch)
    e1.move_to(P3(3.3, 1.5))
    m.play(Write(e1), at=t_rt - 0.2, dur=0.9)
    e2 = MathTex(r"\frac{d}{dr}", r"\left(\pi r^2\right)", "=", r"2\pi r", font_size=54, color=C.text)
    e2[3].set_color(C.circle)
    e2.move_to(P3(3.3, 0.1))
    m.play(Write(e2), at=t_dv - 0.1, dur=1.0)
    box = SurroundingRectangle(e2[3], buff=0.12, color=C.circle, stroke_width=2.4, corner_radius=0.08)
    m.play(Create(box), at=t_cf2, dur=0.5)

    # out: all but the circle
    m.play(FadeOut(VGroup(rad, r_lab, brace, b_lab, d_lab, e1, e2, box)), at=out_t, dur=0.6)
