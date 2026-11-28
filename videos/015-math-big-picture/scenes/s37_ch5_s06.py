"""ch5_s06 · Adding up the rings.

The plain circle from ch5_s05 shrinks to the upper left. On 'other way' it fills with twelve thin rings (two strengths
of C.change, alternating). On 'unroll' each ring, outermost first, is cut and unrolled; each edge keeps its own length,
so a ring flattens into a thin trapezoid, and the trapezoids stack left-aligned, smallest on top. Their slanted ends line
up exactly: the stack is a right triangle, as tall as the radius, with the circumference as its base. On 'triangle' its
outline draws, then braces for r and 2πr. On 'area' ½ · 2πr · r = πr² writes and the empty circle lights. On
'integration' the slices split finer (12 → 24 → 48) and ∫₀ʳ 2πs ds = πr² writes. On 'Archimedes' a lower third reads
Archimedes · c. 250 BC.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, P3, caps, tex, the_circle, tint, window

PZ, PR = P3(-3.75, 0.2), 1.9                  # where ch5_s05 left the circle
DC, R = P3(-3.3, 1.2), 1.3                    # the disk
X0, YB = -4.6, -2.55                          # the triangle: left end of the base, base height
N0 = 12


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def edge(rho, u, base_pt, n=120):
    """A ring edge of radius rho unrolled by u about its bottom point base_pt; it keeps its length 2πρ."""
    L = 2 * math.pi * rho
    s = np.linspace(-L / 2, L / 2, n)
    k = (1 - u) / rho
    if k < 1e-6:
        x, y = s, np.zeros_like(s)
    else:
        x, y = np.sin(k * s) / k, (1 - np.cos(k * s)) / k
    return np.stack([x, y, np.zeros_like(s)], -1) + base_pt


def piece(k, n, u, f, strong):
    """Ring k of n (k = 0 innermost), unrolled by u."""
    r_in, r_out = R * k / n, R * (k + 1) / n
    ue = ss(min(1.0, 1.6 * u))
    y_out = YB + (R - r_out)
    b_out = (1 - ue) * (DC + P3(0, -r_out)) + ue * P3(X0 + math.pi * r_out, y_out)
    b_in = (1 - ue) * (DC + P3(0, -r_in)) + ue * P3(X0 + math.pi * r_in, y_out + (r_out - r_in))
    outer = edge(r_out, u, b_out)
    inner = edge(max(r_in, 1e-3), u, b_in) if k > 0 else np.repeat(b_in[None, :], 2, 0)
    op = (0.62 if strong else 0.3) * f
    return Polygon(*inner, *outer[::-1], stroke_width=0, fill_color=C.change, fill_opacity=op)


@scene(T.ch5_s06, T.ch5_s07)
def ch5_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_ow, t_un, t_tr = float(T.ch5_s06_other_way), float(T.ch5_s06_unroll), float(T.ch5_s06_triangle)
    t_ar, t_in, t_ar2 = float(T.ch5_s06_area), float(T.ch5_s06_integration), float(T.ch5_s06_archimedes)
    t_tall, t_base, t_circ = t_tr + 0.8, t_tr + 2.32, t_ar + 1.4           # 'tall' 'circumference' 'circle'
    Ch = C.change
    out_t = t1 - 0.8

    # the circle shrinks to the upper left
    circ = the_circle(PR).move_to(PZ)
    m.add(circ)
    m.play(circ.animate.scale(R / PR).move_to(DC), at=t0 + 0.2, dur=1.0, ease="easy_ease")

    # the rings: in the disk, then unrolled and stacked; finer at 'integration'
    stag = 0.13

    def u_of(k, n, t):                        # outermost first; k counts from the centre
        order = (n - 1 - k) * (N0 / n)
        return ss((t - t_un - 0.1 - stag * order) / 1.5)

    def n_at(t):
        return 48 if t > t_in - 0.2 else 24 if t > t_in - 0.9 else N0

    def rings(t):
        f = ss((t - t_ow + 0.1) / 0.6) * (1 - ss((t - out_t) / 0.6))
        n = n_at(t)
        return VGroup(*(piece(k, n, u_of(k, n, t), f, k % 2 == 0) for k in range(n)))

    top.redraw(window(rings, t_ow - 0.1, t1 - 0.05), during=(t_ow - 0.1, t1))

    # 'triangle': the outline, its height and its base
    A, B, Cc = P3(X0, YB), P3(X0 + 2 * math.pi * R, YB), P3(X0, YB + R)
    tri = Polygon(A, B, Cc, stroke_color=C.text, stroke_width=2.6, fill_opacity=0)
    m.play(Create(tri), at=t_tr - 0.1, dur=0.9)
    h_br = BraceBetweenPoints(A, Cc, direction=LEFT, color=C.circle)
    h_lab = tex("r", 40, C.circle).next_to(h_br, LEFT, buff=0.1)
    b_br = BraceBetweenPoints(A, B, direction=DOWN, color=C.circle)
    b_lab = tex(r"2\pi r", 40, C.circle).next_to(b_br, DOWN, buff=0.08)
    m.play(GrowFromCenter(h_br), FadeIn(h_lab), at=t_tall, dur=0.5)
    m.play(GrowFromCenter(b_br), FadeIn(b_lab), at=t_base, dur=0.5)

    # 'area': ½ · 2πr · r = πr², and the circle it came from
    e1 = MathTex(r"\tfrac12", r"\cdot", r"2\pi r", r"\cdot", "r", "=", r"\pi r^2", font_size=54, color=C.text)
    e1[2].set_color(C.circle)
    e1[4].set_color(C.circle)
    e1[6].set_color(Ch)
    e1.move_to(P3(3.4, 2.0))
    m.play(Write(e1), at=t_ar - 0.2, dur=1.0)
    glow = Circle(radius=R, stroke_width=0, fill_color=Ch, fill_opacity=0.3).move_to(DC)
    a_lab = tex(r"\pi r^2", 44, Ch).move_to(DC)
    m.play(FadeIn(glow), FadeIn(a_lab), at=t_circ, dur=0.6)

    # 'integration'
    e2 = MathTex(r"\int_0^r", r"2\pi s", r"\,ds", "=", r"\pi r^2", font_size=54, color=C.text)
    e2[1].set_color(C.circle)
    e2[2].set_color(Ch)
    e2[4].set_color(Ch)
    e2.move_to(P3(3.4, 0.6))
    m.play(Write(e2), at=t_in, dur=1.1)

    # 'Archimedes'
    lt = VGroup(caps(r"Archimedes\ \textperiodcentered\ c.\ 250\ BC", 32, C.text),
                Line(ORIGIN, RIGHT * 4.2, stroke_color=C.muted, stroke_width=1.4))
    lt.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(1.3, 3.3), aligned_edge=LEFT)
    m.play(FadeIn(lt, shift=0.08 * LEFT), at=t_ar2 - 0.1, dur=0.6)
    plate(s, m, "archimedes", (5.4, -2.1), 2.5, t_ar2 + 0.2, out_t + 0.6, C.change)

    # out
    m.play(FadeOut(VGroup(circ, tri, h_br, h_lab, b_br, b_lab, e1, glow, a_lab, e2, lt)), at=out_t, dur=0.6)
