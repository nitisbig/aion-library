"""c06_s01 · Senses. Storyboard: plan/scene_plan.md § c06_s01.

Sound rings from a point source; a vertical decibel ruler at even 10 dB steps tracks the level while the rings brighten
(tone-mapped power). Worked example: a 60 dB conversation against a 90 dB concert, three ×10 brackets, 10³ = 1000.
Then the rings give way to a seeded star field: five magnitudes are ×100 of light, 2.512⁵ ≈ 100 (logdata).
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from ch6 import rings_frame, vruler
from kit import P3, shade, add_rail, chapter_break, ctex, fit, glow, ramp, sans, tex, tint, word_at

RX, CX = 0.9, 5.0
Yd = lambda d: -2.4 + (d - 30) * 0.07  # noqa: E731


@scene(T.c06_s01, T.c06_s02)
def s19_c06_senses(s):
    s.solid(C.bg, z=-200)
    chapter_break(s, 6, T.c06_s01)
    add_rail(s, 6)
    t0, end = float(T.c06_s01), float(s.end)
    tf, td = float(T.c06_s01_fixed_factor), float(T.c06_s01_decibels)
    tn, t3 = float(T.c06_s01_ninety_decibel_conce), float(T.c06_s01_three_steps_of_ten)
    tk, tstar = float(T.c06_s01_thousand_times), float(T.c06_s01_star_brightness)

    def lvl(t):
        d = 40 + 10 * (t >= tf + 0.3)
        d += sum(10 * (t >= td + 0.6 + 0.5 * i) for i in range(4))        # climbs to 90 in even steps
        if t >= tn + 0.2:
            d = 60 + sum(10 * (t >= t3 + 0.2 + 0.7 * i) for i in range(3))  # back to 60, then three steps of ten
        return d
    part1 = Track(lambda t: ramp(t, t0 + 0.6, 1.0) * (1 - ramp(t, tstar - 1.1, 0.9)))
    s.add(FramesLayer(rings_frame(lambda t: (lvl(t) - 30) / 60, C.sound), height=6.6, pos=(-3.3, 0.1), z=-2,
                      opacity=part1, during=[(t0, tstar + 1.2)]))
    m = s.manim(z=4, opacity=part1)
    ruler = vruler(RX, Yd, list(range(30, 101, 10)))
    m.play(Create(ruler[0]), FadeIn(ruler[1:], lag_ratio=0.05), at=tf - 0.4, dur=1.0)
    m.add(tex(r"\mathrm{dB}", 26, C.muted).move_to(P3(RX, Yd(100) + 0.4)), at=tf)
    m.redraw(lambda t: VGroup(Line(P3(RX, Yd(30)), P3(RX, Yd(lvl(t))), stroke_color=C.sound, stroke_width=5),
                              Dot(P3(RX, Yd(lvl(t))), radius=0.09, color=C.sound)), during=(tf - 0.2, tstar + 1.2))
    x10 = tex(r"\times10", 26, C.base).move_to(P3(RX + 0.6, Yd(45)))
    m.play(FadeIn(x10), at=tf + 0.3, dur=0.4)
    m.play(FadeOut(x10), at=td, dur=0.5)
    eq = ctex([("L", C.sound), ("=10", None), (r"\log_{10}", None), (r"\frac{P}{P_0}", C.value),
               (r"\ \mathrm{dB}", C.muted)], 46)
    m.play(Write(fit(eq, 2.7).move_to(P3(CX, 2.5))), at=td, dur=1.2)

    # worked example: conversation against concert
    conv = VGroup(Dot(P3(RX, Yd(60)), radius=0.07, color=C.text), sans("conversation", 22, C.text)
                  .next_to(P3(RX + 0.75, Yd(60)), RIGHT, buff=0.1))
    conc = VGroup(Dot(P3(RX, Yd(90)), radius=0.07, color=C.text), sans("concert", 22, C.text)
                  .next_to(P3(RX + 0.75, Yd(90)), RIGHT, buff=0.1))
    m.play(FadeIn(conv), at=word_at("sixty", tn), dur=0.5)
    m.play(FadeIn(conc), at=tn, dur=0.5)
    q = ctex([("90", C.sound), (r"\ \mathrm{dB}\ \text{vs}\ ", None), ("60", C.sound), (r"\ \mathrm{dB}", None)], 40)
    fit(q, 2.6).move_to(P3(CX, 1.45))
    m.play(FadeIn(q), at=tn + 0.6, dur=0.6)
    qm = tex("?", 40, C.steps).next_to(q, RIGHT, buff=0.2)
    m.redraw(lambda t: qm.copy().set_opacity(0.55 + 0.45 * math.cos(2 * math.pi * 1.1 * (t - tn))),
             during=(tn + 1.4, t3 - 0.1))
    for i in range(3):
        a, b = Yd(60 + 10 * i), Yd(70 + 10 * i)
        when = t3 + 0.2 + 0.7 * i
        m.play(Create(ArcBetweenPoints(P3(RX + 0.12, a + 0.03), P3(RX + 0.12, b - 0.03), angle=-1.6,
                                       stroke_color=C.base, stroke_width=2.4)),
               FadeIn(tex(r"\times10", 24, C.base).move_to(P3(RX + 0.62, (a + b) / 2))), at=when, dur=0.5)
    d1 = ctex([("90-60", C.sound), ("=", None), ("30", C.sound), (r"\ \mathrm{dB}", None)], 40)
    fit(d1, 2.7).move_to(P3(CX, 0.5))
    m.play(Write(d1), at=t3 - 0.6, dur=0.8)
    d2 = ctex([(r"10\times10\times10", C.base), ("=", None), (f"{round(ld.CONCERT_RATIO)}", C.value),
               (r"\times", None)], 40)
    fit(d2, 2.7).move_to(P3(CX, -0.45))
    m.play(Write(d2), at=tk - 0.3, dur=0.9)

    # stars: five magnitudes, a hundred times the light
    rng = np.random.default_rng(1807)
    n = 110
    xs, ys = rng.uniform(-6.2, 6.2, n), rng.uniform(-2.9, 3.2, n)
    mags = np.clip(rng.exponential(1.4, n) + 1, 1, 6)
    shade(s, 0, 0.05, 7.0, 2.2, a=0.85, z=4, opacity=Track(lambda t: ramp(t, tstar + 0.3, 0.6) * (1 - ramp(t, end - 0.8, 0.7))))
    st = glow(s, C.star, z=3, k=0.4, opacity=Track(lambda t: ramp(t, tstar - 0.1, 1.2) * (1 - ramp(t, end - 0.8, 0.7))))
    st.add(VGroup(*[Dot(P3(x, y), radius=0.008 + 0.009 * (6 - mg), color=C.star,
                        fill_opacity=0.3 + 0.12 * (6 - mg)) for x, y, mg in zip(xs, ys, mags)]), at=tstar - 0.2)
    m2 = s.manim(z=5)
    sh = VGroup(ctex([(r"\text{5 magnitudes}", C.star), (r"\ =\ ", None), (r"\times100", C.value),
                      (r"\ \text{light}", None)], 40))
    m2.play(FadeIn(sh.move_to(P3(0, 0.5))), at=tstar + 0.6, dur=0.7)
    pg = ctex([(f"{ld.POGSON:.3f}", C.star), ("^5", C.steps), (r"\approx", None), ("100", C.value)], 48)
    m2.play(Write(pg.move_to(P3(0, -0.45))), at=float(T.c06_s01_hundred_times), dur=0.8)
    m2.play(FadeOut(VGroup(sh, pg)), at=end - 0.7, dur=0.6)
