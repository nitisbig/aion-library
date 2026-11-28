"""c06_s02 · Earth and water. Storyboard: plan/scene_plan.md § c06_s02.

A wireframe ground with a ring ripple running out from the epicentre; a magnitude ruler 4…8 climbs with ×31.6 per
step (10^1.5, logdata) and the ripple grows. Worked example: magnitude 7 against 5, 31.6² ≈ 1000. Then a pH ruler 0…14
with four glasses at their pH; lemon juice (2) against water (7) is five ×10 steps, 10⁵. On "even steps" a magnitude
ruler with the same step length lines up above it.
"""
from aion import *

import logdata as ld
from beats import T
from ch6 import glass, ground, vruler
from kit import P3, add_rail, ctex, fit, glow, ramp, sans, tex, tint, word_at

RX, CX = 1.95, 4.75
Ym = lambda v: -2.2 + (v - 4) * 1.05  # noqa: E731
PX = lambda v: -5.6 + v * 0.8  # noqa: E731
PY = -1.6


@scene(T.c06_s02, T.c06_s03)
def s20_c06_earth(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 6)
    t0, end = float(T.c06_s02), float(s.end)
    tg, t32, t2 = float(T.c06_s02_ground), float(T.c06_s02_thirty_two_times), float(T.c06_s02_two_steps)
    ta = float(T.c06_s02_acidity)
    part1 = Track(lambda t: ramp(t, t0 + 0.4, 0.8) * (1 - ramp(t, ta - 0.9, 0.7)))

    def mag(t):
        if t >= t2:                                   # the worked example: 5, then two steps to 7
            return 5 + sum(1.0 * (t >= t2 + 0.6 + 0.7 * i) for i in range(2))
        return 4 + sum(1.0 * (t >= t32 + 0.1 + 0.7 * i) for i in range(4))

    def amp(t):
        return 0.1 * 1.5 ** (mag(t) - 4)
    gr = glow(s, C.quake, z=2, k=0.35, opacity=part1)
    gr.redraw(lambda t: ground(t, amp(t), tg - 0.2), during=(t0 + 0.3, ta + 0.3))

    m = s.manim(z=4, opacity=part1)
    ruler = vruler(RX, Ym, [4, 5, 6, 7, 8])
    m.play(Create(ruler[0]), FadeIn(ruler[1:], lag_ratio=0.1), at=t32 - 1.2, dur=1.0)
    m.add(sans("magnitude", 22, C.muted).move_to(P3(RX, Ym(8) + 0.45)), at=t32 - 0.6)
    m.redraw(lambda t: VGroup(Line(P3(RX, Ym(4)), P3(RX, Ym(mag(t))), stroke_color=C.quake, stroke_width=5),
                              Dot(P3(RX, Ym(mag(t))), radius=0.09, color=C.quake)), during=(t32 - 0.2, ta + 0.3))
    tags = VGroup()
    for i in range(4):
        a, b = Ym(4 + i), Ym(5 + i)
        tags.add(VGroup(ArcBetweenPoints(P3(RX + 0.15, a + 0.06), P3(RX + 0.15, b - 0.06), angle=0.9,
                                         stroke_color=C.quake, stroke_width=2.2, fill_opacity=0),
                        tex(rf"\times{ld.QUAKE_STEP_ENERGY:.1f}", 24, C.quake).move_to(P3(RX + 0.95, (a + b) / 2))))
        m.play(FadeIn(tags[-1]), at=t32 + 0.1 + 0.7 * i, dur=0.4)
    e1 = ctex([("E", C.quake), (r"\propto", None), ("10^{1.5M}", C.steps)], 44)
    m.play(Write(e1.move_to(P3(CX, 2.5))), at=t32 + 0.6, dur=0.9)

    # magnitude 7 against 5
    m.play(FadeOut(VGroup(tags[0], tags[3])), at=t2, dur=0.5)
    q = ctex([("M7", C.quake), (r"\ \text{vs}\ ", None), ("M5", C.quake)], 40).move_to(P3(CX, 1.45))
    m.play(FadeIn(q), at=t2, dur=0.5)
    k2 = ctex([(f"{ld.QUAKE_STEP_ENERGY:.1f}", C.quake), ("^2", C.steps), (r"\approx", None),
               (f"{round(ld.QUAKE_7_VS_5, -2):.0f}", C.value)], 46).move_to(P3(CX, 0.45))
    m.play(Write(k2), at=word_at("thousand", t2) - 0.3, dur=0.9)

    # pH
    m2 = s.manim(z=4)
    ph = VGroup(Line(P3(PX(0), PY), P3(PX(14), PY), stroke_color=C.ruler, stroke_width=2.5))
    for v in range(15):
        ph.add(Line(P3(PX(v), PY), P3(PX(v), PY - 0.15), stroke_color=C.ruler, stroke_width=2),
               tex(str(v), 24, C.ruler).move_to(P3(PX(v), PY - 0.38)))
    ph.add(sans("pH", 24, C.muted).move_to(P3(PX(14) + 0.45, PY)))
    m2.play(Create(ph[0]), FadeIn(ph[1:], lag_ratio=0.02), at=ta - 0.05, dur=1.0)
    e2 = ctex([(r"\mathrm{pH}", C.acid), ("=-", None), (r"\log_{10}", None), (r"[\mathrm{H^+}]", C.value)], 46)
    m2.play(Write(e2.move_to(P3(0, 2.7))), at=ta + 0.5, dur=1.0)
    tl = float(T.c06_s02_lemon_juice)
    names = {"lemon juice": "lemon", "coffee": "coffee", "water": "water", "baking soda": "baking soda"}
    for i, (name, v) in enumerate(ld.PH.items()):
        liquid = C.acid if v < 7 else (tint(C.text, 0.8) if v == 7 else tint(C.steps, 0.9))
        g = glass(liquid).move_to(P3(PX(v), PY + 0.62))
        lbl = sans(names[name], 20, C.muted).next_to(g, UP, buff=0.12)
        when = tl - 0.3 + 0.35 * i
        m2.play(FadeIn(g, shift=0.5 * DOWN), FadeIn(lbl), at=when, dur=0.6)
    th = float(T.c06_s02_hundred_thousand)
    for i in range(5):
        a, b = PX(2 + i), PX(3 + i)
        m2.play(Create(ArcBetweenPoints(P3(b - 0.04, PY - 0.75), P3(a + 0.04, PY - 0.75), angle=-1.2,
                                        stroke_color=C.acid, stroke_width=2.2)),
                FadeIn(tex(r"\times10", 20, C.acid).move_to(P3((a + b) / 2, PY - 1.12))), at=th - 0.6 + 0.25 * i,
                dur=0.4)
    k5 = ctex([(r"10^5", C.value), ("=", None), (f"{round(ld.LEMON_VS_WATER):,}".replace(",", r"\,"), C.value)], 44)
    m2.play(Write(k5.move_to(P3(0, 1.75))), at=th + 0.4, dur=0.9)

    # even steps: a magnitude ruler with the same step lines up above
    te = float(T.c06_s02_even_steps)
    yq = 0.9
    mq = VGroup(Line(P3(PX(4), yq), P3(PX(8), yq), stroke_color=C.quake, stroke_width=2.5))
    for v in range(4, 9):
        mq.add(Line(P3(PX(v), yq), P3(PX(v), yq - 0.15), stroke_color=C.quake, stroke_width=2),
               tex(f"M{v}", 22, C.quake).move_to(P3(PX(v), yq + 0.3)))
    m2.play(FadeOut(k5), FadeIn(mq, shift=0.3 * DOWN), at=te - 0.6, dur=0.7)
    guides = VGroup(*[DashedLine(P3(PX(v), yq - 0.18), P3(PX(v), PY + 0.05), stroke_color=tint(C.muted, 0.4),
                                 stroke_width=1.2, dash_length=0.06) for v in range(4, 9)])
    m2.play(Create(guides), at=te + 0.1, dur=0.6)
    s.add(Solid(C.bg, z=50, opacity=Track(lambda t: ramp(t, end - 0.7, 0.6))))
