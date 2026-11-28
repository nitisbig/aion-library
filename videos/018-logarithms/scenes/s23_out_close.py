"""out_s02 · Napier's question. Storyboard: plan/scene_plan.md § out_s02.

Napier's page (the intro's skia raster) fades up, dim, at the left. On "Four centuries" a log scale 1…10 draws across
it; on "quiet question" the scale gathers into log₂ 8 = 3; on "how many" the 3 lights in the steps hue. On "Thanks"
the title fades in above with a thin rule, and the frame holds for the end screen with the right two thirds empty.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import P3, caps, ctex, paper_page, ramp, tex, tint

LX = -3.85                                   # the left third's centre


@scene(T.out_s02, T.end)
def s23_out_close(s):
    s.solid(C.bg, z=-200)
    t0 = float(T.out_s02)
    tq, tf = float(T.out_s02_quiet_question), float(T.out_s02_four_centuries)
    img = paper_page(seed=1614)
    img[..., :3] = (img[..., :3] * 0.55).astype(np.uint8)
    s.add(ArrayLayer(img, height=5.2, pos=(LX, 0.0), z=-5,
                     opacity=Track(lambda t: 0.75 * ramp(t, t0 + 0.3, 1.5) * (1 - ramp(t, tq - 0.4, 1.2)))))
    m = s.manim(z=3)

    # a log scale draws over the page
    xa, L, y = LX - 2.1, 4.2, -0.1
    scale = VGroup(Line(P3(xa, y), P3(xa + L, y), stroke_color=C.ruler, stroke_width=2.5))
    for v in range(1, 11):
        x = xa + L * math.log10(v)
        scale.add(Line(P3(x, y), P3(x, y + (0.25 if v in (1, 10) else 0.15)), stroke_color=C.ruler, stroke_width=2),
                  *([tex(str(v), 24, C.value).move_to(P3(x, y - 0.3))] if v in (1, 2, 3, 4, 5, 10) else []))
    m.play(Create(scale[0]), at=tf, dur=1.0)
    m.play(LaggedStart(*[FadeIn(p) for p in scale[1:]], lag_ratio=0.05), at=tf + 0.4, dur=1.4)

    eq = ctex([(r"\log_2", None), ("8", C.value), ("=", None), ("3", C.text)], 72).move_to(P3(LX, 0.0))
    m.play(ReplacementTransform(scale, eq), at=tq, dur=1.2)
    th = float(T.out_s02_how_many)
    m.play(eq[3].animate.set_color(C.steps).scale(1.15), at=th, dur=0.6)

    tt = float(T.out_s02_thanks)
    title = caps("What Logarithms Actually Are", 30, C.text).move_to(P3(LX, 1.35))
    rule = Line(P3(LX - title.width / 2, 1.0), P3(LX + title.width / 2, 1.0), stroke_color=tint(C.muted, 0.6),
                stroke_width=1.2)
    m.play(FadeIn(title, shift=0.1 * DOWN), Create(rule), at=tt, dur=0.9)
