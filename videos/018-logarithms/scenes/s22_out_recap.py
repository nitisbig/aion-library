"""out_s01 · What we covered. Storyboard: plan/scene_plan.md § out_s01.

A six-step staircase climbs across the frame, dim. As each lesson is spoken its step lights in that chapter's hue,
a small line drawing of the chapter's picture settles on the tread with one key word beneath, and the step's equation
shows above the stairs until the next one. The rail completes and fades on "galaxies".
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import P3, word_at, add_rail, ctex, glow, polyline, ramp, sans, tex, tint
from theme import CHAPTERS

X0S, Y0S, SW, SH = -5.75, -2.75, 1.9, 0.78
WORDS = ["count", "add", "ruler", "mirror", "e", "scales"]
EQS = [[(r"\log_2 8", None), ("=", None), ("3", C.steps)],
       [(r"\log(ab)", None), ("=", None), (r"\log a+\log b", None)],
       [(r"\log 2+\log 3", None), ("=", None), (r"\log 6", None)],
       [("y=2^x", C.value), (r"\ \longleftrightarrow\ ", None), (r"y=\log_2 x", C.steps)],
       [(r"\ln e", C.natural), ("=", None), ("1", None)],
       [(r"\log T", C.planet), ("=", None), (r"\tfrac32\log a+c", None)]]


def _icon(k, hue):
    """A small line drawing of chapter k's picture, about 1.3 × 0.8, centred on the origin."""
    if k == 0:                                     # a little doubling staircase
        pts = [(-0.6, -0.35)]
        for i in range(3):
            x, y = pts[-1]
            pts += [(x + 0.4, y), (x + 0.4, y + 0.25)]
        return VGroup(polyline(pts, hue, 2.5), Dot(P3(*pts[-1]), radius=0.05, color=hue))
    if k == 1:                                     # two lengths laid end to end
        return VGroup(Line(P3(-0.65, -0.1), P3(-0.05, -0.1), stroke_color=C.steps, stroke_width=5),
                      Line(P3(-0.05, -0.1), P3(0.65, -0.1), stroke_color=C.value, stroke_width=5),
                      tex("+", 26, hue).move_to(P3(-0.05, 0.2)))
    if k == 2:                                     # two log scales, one slid
        g = VGroup()
        for dy, off in ((0.12, 0.3), (-0.18, 0.0)):
            g.add(Line(P3(-0.65 + off, dy), P3(0.65, dy), stroke_color=C.ruler, stroke_width=2))
            for v in range(1, 11):
                x = -0.65 + off + (1.3 - off) * math.log10(v)
                g.add(Line(P3(x, dy), P3(x, dy - 0.1), stroke_color=hue, stroke_width=1.5))
        return g
    if k == 3:                                     # 2^x and its mirror
        xs = np.linspace(-1.5, 1.2, 40)
        u = 0.28
        return VGroup(polyline([(u * x, u * 2 ** x - 0.4) for x in xs if 2 ** x < 3.2], C.value, 2.2),
                      polyline([(u * 2 ** x, u * x - 0.4) for x in xs if 2 ** x < 3.2], C.steps, 2.2),
                      DashedLine(P3(-0.3, -0.7), P3(0.6, 0.2), stroke_color=C.muted, stroke_width=1.2,
                                 dash_length=0.05))
    if k == 4:                                     # area under 1/x up to e
        u = 0.3
        xs = np.linspace(1, math.e, 30)
        pts = [P3(u * x - 0.9, u / x * 2.2 - 0.4) for x in xs]
        reg = Polygon(*pts, P3(u * math.e - 0.9, -0.4), P3(u - 0.9, -0.4), stroke_width=0, fill_color=C.area,
                      fill_opacity=0.45)
        hy = polyline([(u * x - 0.9, u / x * 2.2 - 0.4) for x in np.geomspace(0.75, 4.6, 60)], C.text, 2)
        return VGroup(reg, hy, Dot(P3(u * math.e - 0.9, -0.4), radius=0.05, color=C.natural))
    g = VGroup(Line(P3(-0.65, -0.3), P3(0.65, -0.3), stroke_color=C.ruler, stroke_width=2))   # atom → galaxy
    for i, r in enumerate((0.03, 0.05, 0.08, 0.13)):
        x = -0.55 + 0.37 * i
        g.add(Circle(radius=r, stroke_color=hue, stroke_width=1.8).move_to(P3(x, -0.1 + r)),
              Line(P3(x, -0.3), P3(x, -0.38), stroke_color=C.ruler, stroke_width=1.5))
    return g


@scene(T.out_s01, T.out_s02)
def s22_out_recap(s):
    s.solid(C.bg, z=-200)
    t0, end = float(T.out_s01), float(s.end)
    cues = [float(c) for c in (T.out_s01_count_of_multiplicat, T.out_s01_products_become_sums, T.out_s01_slide_rule,
                               T.out_s01_mirror, T.out_s01_is_e)]
    cues.append(word_at("sound", cues[4]))
    add_rail(s, 6, opacity=Track(lambda t: 1 - ramp(t, float(T.out_s01_galaxies), 0.8)))
    out = Track(lambda t: 1 - ramp(t, end - 0.5, 0.45))
    m = s.manim(z=3, opacity=out)

    def tread(k):
        y = Y0S + (k + 1) * SH
        return P3(X0S + k * SW, y), P3(X0S + (k + 1) * SW, y)

    dim = VGroup()
    for k in range(6):
        a, b = tread(k)
        dim.add(Line(a + DOWN * SH, a, stroke_color=tint(C.muted, 0.35), stroke_width=2),
                Line(a, b, stroke_color=tint(C.muted, 0.35), stroke_width=2))
    m.play(Create(dim), at=t0 + 0.3, dur=1.6, ease="linear")

    hold = P3(-2.7, 2.55)
    prev = None
    for k in range(6):
        hue = getattr(C, CHAPTERS[k])
        a, b = tread(k)
        when = cues[k]
        gl = glow(s, hue, z=4, k=0.6, opacity=out)
        gl.play(Create(VGroup(Line(a + DOWN * SH, a, stroke_color=hue, stroke_width=4),
                              Line(a, b, stroke_color=hue, stroke_width=4))), at=when, dur=0.6)
        mid = (a + b) / 2
        icon = _icon(k, hue).move_to(mid + UP * 0.55)
        word = sans(WORDS[k], 24, hue).move_to(mid + DOWN * 0.3)
        m.play(FadeIn(icon, shift=0.2 * DOWN), FadeIn(word), at=when + 0.2, dur=0.6)
        eq = ctex(EQS[k], 46).move_to(hold)
        if prev is not None:
            m.play(FadeOut(prev, shift=0.15 * UP), at=when, dur=0.4)
        m.play(FadeIn(eq, shift=0.15 * UP), at=when + 0.3, dur=0.5)
        prev = eq
    m.play(FadeOut(prev), at=end - 0.9, dur=0.4)
