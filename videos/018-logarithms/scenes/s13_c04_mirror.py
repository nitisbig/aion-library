"""c04_s01 · The mirror. Storyboard: plan/scene_plan.md § c04_s01.

On the Classic grid, y = 2ˣ draws and its doubling points light. (3, 8) and its mirror (8, 3) light with dashed guides.
The diagonal draws and a copy of the curve flips in 3D about it, landing as y = log₂ x. Points then travel from
(x, 2ˣ) to (2ˣ, x) straight across the diagonal with short glowing trails, while the table on the right swaps its two columns: x beside 2ˣ becomes x
beside log₂ x.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import P3, add_rail, ctex, fit, glow, mirror_point, plane, polyline, ramp, sans, tex, tint

OX, OY, U = -5.7, -2.5, 0.62


@scene(T.c04_s01, T.c04_s02)
def s13_c04_mirror(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 4)
    out = Track(lambda t: 1 - ramp(t, float(s.end) - 0.7, 0.6))
    m = s.manim(z=3, opacity=out)
    g, X, Y = plane(OX, OY, U, (-1, 9.2), (-0.4, 9.2))
    t0 = float(T.c04_s01)
    m.play(FadeIn(g), at=t0 + 0.4, dur=1.0)
    labels = VGroup(*[tex(str(i), 20, C.muted).next_to(P3(X(i), OY), DOWN, buff=0.08) for i in range(2, 10, 2)])
    m.play(FadeIn(labels), at=t0 + 0.8, dur=0.6)

    xs = np.linspace(-1, math.log2(9.15), 200)
    exp_curve = polyline([(X(x), Y(2 ** x)) for x in xs], C.value, 4)
    m.play(Create(exp_curve), at=T.c04_s01_two_to_the_x, dur=1.6)
    m.play(FadeIn(tex("y=2^x", 34, C.value).next_to(P3(X(2.55), Y(6.0)), LEFT, buff=0.15)),
           at=float(T.c04_s01_two_to_the_x) + 1.0, dur=0.5)
    dots = VGroup(*[Dot(P3(X(k), Y(2 ** k)), radius=0.065, color=C.value) for k in range(4)])
    m.play(LaggedStart(*[FadeIn(d, scale=1.6) for d in dots], lag_ratio=0.4), at=T.c04_s01_every_step, dur=1.4)

    # the same points as a table on the right: x (steps) beside 2ˣ (value), a row per lit point
    CL, CR, YH = 3.25, 4.85, 0.95
    ry = lambda k: YH - 0.62 - 0.5 * k  # noqa: E731
    h_x, h_v = tex("x", 36, C.steps).move_to(P3(CL, YH)), tex("2^x", 36, C.value).move_to(P3(CR, YH))
    frame = VGroup(Line(P3(CL - 0.65, YH - 0.3), P3(CR + 0.75, YH - 0.3), stroke_color=tint(C.muted, 0.6),
                        stroke_width=1.4),
                   Line(P3((CL + CR) / 2, YH + 0.25), P3((CL + CR) / 2, ry(3) - 0.25), stroke_color=tint(C.muted, 0.6),
                        stroke_width=1.4))
    col_s = VGroup(*[tex(str(k), 34, C.steps).move_to(P3(CL, ry(k))) for k in range(4)])
    col_v = VGroup(*[tex(str(2 ** k), 34, C.value).move_to(P3(CR, ry(k))) for k in range(4)])
    m.play(FadeIn(VGroup(frame, h_x, h_v)), at=float(T.c04_s01_every_step) - 0.3, dur=0.6)
    m.play(LaggedStart(*[FadeIn(VGroup(a, b), shift=0.1 * LEFT) for a, b in zip(col_s, col_v)], lag_ratio=0.4),
           at=T.c04_s01_every_step, dur=1.4)

    # (3, 8) and its mirror (8, 3)
    t38 = float(T.c04_s01_three_to_eight)
    g38 = VGroup(DashedLine(P3(X(3), Y(0)), P3(X(3), Y(8)), stroke_color=tint(C.value, 0.6), stroke_width=1.6,
                            dash_length=0.07),
                 DashedLine(P3(X(0), Y(8)), P3(X(3), Y(8)), stroke_color=tint(C.value, 0.6), stroke_width=1.6,
                            dash_length=0.07))
    p38 = Dot(P3(X(3), Y(8)), radius=0.09, color=C.value)
    l38 = tex("(3,8)", 28, C.value).next_to(p38, LEFT, buff=0.15)
    m.play(Create(g38), FadeIn(p38, scale=1.5), at=t38, dur=0.7)
    m.play(FadeIn(l38), at=t38 + 0.5, dur=0.4)
    m.play(Indicate(VGroup(col_s[3], col_v[3]), color=C.text, scale_factor=1.2), at=t38 + 0.2, dur=0.8)
    t83 = float(T.c04_s01_eight_back_to_three)
    g83 = VGroup(DashedLine(P3(X(8), Y(0)), P3(X(8), Y(3)), stroke_color=tint(C.steps, 0.6), stroke_width=1.6,
                            dash_length=0.07),
                 DashedLine(P3(X(0), Y(3)), P3(X(8), Y(3)), stroke_color=tint(C.steps, 0.6), stroke_width=1.6,
                            dash_length=0.07))
    p83 = Dot(P3(X(8), Y(3)), radius=0.09, color=C.steps)
    l83 = tex("(8,3)", 28, C.steps).next_to(p83, DOWN + RIGHT, buff=0.1)
    m.play(Create(g83), FadeIn(p83, scale=1.5), at=t83, dur=0.7)
    m.play(FadeIn(l83), at=t83 + 0.5, dur=0.4)

    # the diagonal, and the flip
    tr = float(T.c04_s01_reflected)
    diag = DashedLine(P3(X(-0.4), Y(-0.4)), P3(X(9.0), Y(9.0)), stroke_color=C.muted, stroke_width=2,
                      dash_length=0.1)
    m.play(Create(diag), FadeOut(VGroup(g38, g83)), at=tr - 0.6, dur=0.8)
    m.play(FadeIn(tex("y=x", 26, C.muted).move_to(P3(X(8.2), Y(8.9)))), at=tr, dur=0.5)
    f0, f1 = tr + 0.3, tr + 2.6
    xl = np.linspace(0.8, 9.1, 300)
    log_curve = polyline([(X(x), Y(math.log2(x))) for x in xl], C.steps, 4)

    def flip(t):
        q = math.pi * ramp(t, f0, f1 - f0)
        pts = [mirror_point(x, 2 ** x, q) for x in xs]
        col = C.value if q < math.pi / 2 else C.steps
        return polyline([(X(x), Y(y)) for x, y in pts], col, 4, opacity=0.5 + 0.5 * abs(math.cos(q)))
    m.redraw(flip, during=(f0 - 0.05, f1))
    m.add(log_curve, at=f1)
    m.play(FadeIn(tex(r"y=\log_2 x", 34, C.steps).move_to(P3(X(6.6), Y(1.7)))), at=f1 - 0.2, dur=0.5)
    e = ctex([("y=2^x", C.value), (r"\ \longleftrightarrow\ ", None), (r"y=\log_2 x", C.steps)], 50)
    e = fit(e, 4.2).move_to(P3(3.95, 2.6))
    m.play(Write(e), at=f1 + 0.2, dur=1.0)

    # swaps: points travel across the diagonal
    ts = float(T.c04_s01_swaps)
    m.play(FadeIn(sans("swap x and y", 24, C.muted).move_to(P3(3.95, 1.85))), at=ts, dur=0.5)
    h_x2, h_l = tex("x", 36, C.value).move_to(P3(CL, YH)), tex(r"\log_2 x", 36, C.steps).move_to(P3(CR, YH))
    m.play(*[a.animate(path_arc=-PI / 2).move_to(P3(CR, a.get_y())) for a in col_s],
           *[b.animate(path_arc=-PI / 2).move_to(P3(CL, b.get_y())) for b in col_v],
           ReplacementTransform(h_x, h_l, path_arc=-PI / 2), ReplacementTransform(h_v, h_x2, path_arc=-PI / 2),
           at=ts + 0.3, dur=1.3)
    starts = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    tl = glow(s, C.text, z=5, k=0.7, opacity=out)

    def trails(t):
        grp = VGroup()
        for i, x in enumerate(starts):
            a = (X(x), Y(2 ** x))
            b = (X(2 ** x), Y(x))
            u = ramp(t, ts + 0.15 * i, 1.1)
            if u <= 0:
                continue
            u0 = max(0.0, u - 0.35)
            pa = P3(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0)
            pb = P3(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            fadeout = 1 - ramp(t, ts + 0.15 * i + 1.1, 0.6)
            grp.add(Line(pa, pb, stroke_color=C.text, stroke_width=2, stroke_opacity=0.7 * fadeout))
            col = C.value if u < 0.5 else C.steps
            grp.add(Dot(pb, radius=0.06, color=col))
        return grp
    tl.redraw(trails, during=(ts - 0.1, float(s.end)))
