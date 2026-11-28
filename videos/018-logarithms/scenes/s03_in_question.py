"""in_s03 · One question. Storyboard: plan/scene_plan.md § in_s03.

A calculator key labelled log slides in (continuing the preview strip), is pressed, and prints 0.903089987: an answer
with no meaning attached. Half-remembered rules drift in around it and fall away. Then a glowing dot climbs three ×2
steps (values 2, 4, 8; counts 1, 2, 3) as the staircase draws under it. On the question the staircase's own parts
become log₂ 8 = 3 (the ×2 gives the base, the top tread the value, the step count the answer), the progress rail
draws in, and the chapter one card follows in the silence.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import P3, add_rail, chapter_card, ctex, glow, ramp, sans, stair_points, staircase, tex, tint


@scene(T.in_s03, T.c01_s01)
def s03_in_question(s):
    s.solid(C.bg, z=-200)
    t0, tb, tr = float(T.in_s03), float(T.in_s03_button), float(T.in_s03_rules)
    ts, tq = float(T.in_s03_step_by_step), float(T.in_s03_how_many_times)
    slide = Track(lambda t: (15.5 * (1 - ramp(t, t0 - 0.05, 0.9)), 0.0))
    m = s.manim(z=5, pos=slide)

    # the key: slides in, is pressed, prints a number nobody explained
    press = lambda t: 0.06 * math.sin(math.pi * min(max((t - tb - 0.1) / 0.3, 0.0), 1.0))  # noqa: E731
    base = RoundedRectangle(width=1.7, height=1.15, corner_radius=0.2, stroke_color=tint(C.muted, 0.6),
                            stroke_width=2).move_to(P3(0, -0.47))
    m.add(base, at=t0)
    face = VGroup(RoundedRectangle(width=1.7, height=1.15, corner_radius=0.2, stroke_color=C.muted, stroke_width=2.4,
                                   fill_color=C.bg, fill_opacity=1),
                  sans("log", 44, C.text)).move_to(P3(0, -0.4))
    m.add(face, at=t0)
    m.drive(face, lambda g, t: g.move_to(P3(0, -0.4 - press(t))), during=(tb, tb + 0.5))
    digits = "0.903089987"
    m.redraw(lambda t: sans(digits[:max(0, min(len(digits), int((t - tb - 0.35) / 0.06)))], 40, C.muted)
             .set_opacity(1 - ramp(t, ts - 0.9, 0.4)).move_to(P3(0, 0.75)), during=(tb + 0.3, ts - 0.4))
    m.play(FadeOut(VGroup(face, base), scale=0.9), at=ts - 0.6, dur=0.5)

    # half-remembered rules drift in and fall away
    dim = tint(C.muted, 0.8)
    spots = [(-3.9, 2.1, 0.05), (3.8, 1.9, -0.04), (-3.4, -1.9, -0.03), (3.5, -1.7, 0.04)]
    texts = [r"\log(ab)=\log a+\log b", r"\log\frac{a}{b}=\log a-\log b", r"\log a^n=n\log a",
             r"\log_b x=\frac{\ln x}{\ln b}"]
    for i, ((x, y, r), tx) in enumerate(zip(spots, texts)):
        rule = tex(tx, 36, dim).rotate(r).move_to(P3(x, y))
        a = tr + 0.3 * i
        m.play(FadeIn(rule, scale=0.94), at=a, dur=0.6)
        m.drive(rule, lambda g, t, x=x, y=y, a=a: g.move_to(P3(x + 0.05 * (t - a), y + 0.06 * (t - a))),
                during=(a, tr + 3.2))
        m.play(FadeOut(rule, shift=0.8 * DOWN), at=tr + 2.9 + 0.15 * i, dur=0.8)

    # step by step: a dot climbs as the staircase draws under it
    x0, y0, sw, sh = -2.6, -1.9, 1.35, 0.9
    st = staircase(3, x0, y0, sw, sh, label_size=40)
    pts = np.array(stair_points(3, x0, y0, sw, sh))
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    c0, c1 = ts + 0.5, ts + 2.9

    def along(t):
        d = seg[-1] * min(max((t - c0) / (c1 - c0), 0.0), 1.0)
        k = min(int(np.searchsorted(seg, d, side="right")) - 1, len(pts) - 2)
        u = (d - seg[k]) / max(seg[k + 1] - seg[k], 1e-9)
        x, y = pts[k] + u * (pts[k + 1] - pts[k])
        return P3(x, y)
    m.play(FadeIn(st.floor), at=ts, dur=0.5)
    m.play(Create(st.path), at=c0, dur=c1 - c0, ease="linear", lead=0.0)
    runner = glow(s, C.value, z=6, k=0.9)
    runner.redraw(lambda t: Dot(along(t), radius=0.075, color=C.value).set_opacity(1 - ramp(t, tq + 0.1, 0.5)),
                  during=(ts, tq + 0.7))
    m.play(LaggedStart(*[FadeIn(v, shift=0.1 * UP) for v in st.vals], lag_ratio=0.75), at=ts + 0.4, dur=2.6,
           lead=0.0)
    m.play(LaggedStart(*[FadeIn(v) for v in st.tags], lag_ratio=0.75), at=ts + 0.9, dur=2.2, lead=0.0)
    m.play(FadeIn(st.axis), at=ts + 3.0, dur=0.8)

    # the question: the staircase's own parts become log₂ 8 = 3
    eq = ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("8", C.value), ("=", None), ("3", C.steps)], 84)
    eq.move_to(P3(0, 0.25))
    base_src, val_src, cnt_src = st.tags[-1], st.vals[-1], st.axis[-1]
    rest = VGroup(st.path, st.floor, *[v for v in st.vals if v is not val_src], *[g for g in st.tags if g is not base_src],
                  *[a for a in st.axis if a is not cnt_src])
    m.play(FadeOut(rest, scale=0.9), at=tq + 0.1, dur=0.7)
    m.play(ReplacementTransform(base_src, eq[1]), ReplacementTransform(val_src, eq[3]),
           ReplacementTransform(cnt_src, eq[5]), at=tq + 0.3, dur=1.0)
    m.play(Write(VGroup(eq[0], eq[2], eq[4])), at=tq + 0.9, dur=0.7)
    m.play(FadeOut(eq), at=float(T.c01_s01) - 0.95, dur=0.5)

    add_rail(s, 1, opacity=fade(tq + 0.4, dur=1.0))
    chapter_card(s, 1, at=float(T.c01_s01) - 0.45, out=float(T.c01_s01) + 0.95)
