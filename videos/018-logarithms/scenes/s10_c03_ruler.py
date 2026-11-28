"""c03_s01 · The logarithmic ruler. Storyboard: plan/scene_plan.md § c03_s01.

A boxwood rule fades up (a small tag: Gunter · 1620). The numbers 1 … 10 stand evenly spaced above it, then each drops
to its logarithm's distance along the rule, engraving its tick as it lands (x = log₁₀ n). A bracket measures 2 at
0.301 of the length, the number from c02. The minor ticks fill in and the camera runs along the rule to show them
crowding towards 10. A second, identical rule slides in above: a slide rule.
"""
import math

from aion import *

import logdata as ld
from beats import T
from ch3 import BH, L, LO, UP, XL, xpos
from kit import (P3, RULE_INK, X0, Y1, add_rail, chapter_break, ctex, log_scale_marks, ramp, sans, show_tag, tex,
                 soft_shadow, tint, wood_body)


@scene(T.c03_s01, T.c03_s02)
def s10_c03_ruler(s):
    s.solid(C.bg, z=-200)
    chapter_break(s, 3, T.c03_s01)
    add_rail(s, 3)
    tw = float(T.c03_s01_wooden_rule)
    sh, shh = soft_shadow(L + 0.7, BH)
    s.add(ArrayLayer(sh, height=shh, pos=(XL + L / 2 + 0.06, LO - 0.11), z=-3, opacity=fade(tw, dur=1.0)))
    s.add(ArrayLayer(wood_body(L, BH)[0], height=BH, pos=(XL + L / 2, LO), z=-2, opacity=fade(tw, dur=1.0)))
    show_tag(s, "Gunter · 1620", C.ruler, tw + 0.3, dur=4.0, at=P3(X0, Y1))
    m = s.manim(z=4)
    edge = LO + BH / 2

    # the numbers drop from even spacing onto their logarithms
    td = float(T.c03_s01_distance_from_the_st)
    lin = lambda n: XL + L * (n - 1) / 9  # noqa: E731
    nums = VGroup(*[tex(str(n), 34, C.value).move_to(P3(lin(n), 1.75)) for n in range(1, 11)])
    m.play(LaggedStart(*[FadeIn(n, shift=0.1 * DOWN) for n in nums], lag_ratio=0.15), at=td - 1.4, dur=1.2)
    eq = ctex([("x", C.steps), ("=", None), (r"\log_{10}", None), ("n", C.value)], 50).move_to(P3(3.6, 2.85))
    hud = s.manim(z=6, parallax=0.0)
    hud.play(Write(eq), at=td + 0.2, dur=0.8)
    for n in range(1, 11):
        x = xpos(n)
        t0 = td + 0.5 + 0.55 * (n - 1)
        drop = DashedLine(P3(lin(n), 1.5), P3(x, edge + 0.05), stroke_color=tint(C.value, 0.55), stroke_width=1.5,
                          dash_length=0.07)
        tick = Line(P3(x, edge), P3(x, edge - 0.3), stroke_color=RULE_INK, stroke_width=2)
        lab = tex(str(n), 26, RULE_INK).move_to(P3(x + (0.14 if n == 1 else (-0.18 if n == 10 else 0)), edge - 0.5))
        m.play(Create(drop), at=t0, dur=0.4, lead=0.0)
        m.play(nums[n - 1].animate.move_to(P3(x, edge + 0.32)).scale(0.8), at=t0 + 0.2, dur=0.6, lead=0.0)
        m.play(FadeIn(tick), FadeIn(lab), at=t0 + 0.6, dur=0.3, lead=0.0)
        m.play(FadeOut(drop), at=t0 + 0.9, dur=0.4, lead=0.0)

    # 2 sits 0.301 of the way along
    tz = float(T.c03_s01_zero_point_three_zer)
    by = LO - BH / 2 - 0.3
    br = BraceBetweenPoints(P3(XL, by), P3(xpos(2), by), direction=DOWN, color=C.steps)
    full = DashedLine(P3(XL, by - 0.75), P3(XL + L, by - 0.75), stroke_color=tint(C.muted, 0.7), stroke_width=1.5)
    m.play(GrowFromCenter(br), at=tz - 0.6, dur=0.6)
    brl = tex(f"{ld.LOG10_2:.3f}", 30, C.steps).next_to(br, DOWN, buff=0.08)
    one = tex("1", 24, C.muted).next_to(full, RIGHT, buff=0.12)
    m.play(FadeIn(brl), at=tz - 0.2, dur=0.5)
    m.play(Create(full), FadeIn(one), at=tz + 0.6, dur=0.8)
    eq2 = ctex([(r"\log_{10}", None), ("2", C.value), (r"\approx", None), (f"{ld.LOG10_2:.3f}", C.steps)], 44)
    hud.play(FadeIn(eq2.next_to(eq, DOWN, buff=0.3), shift=0.2 * LEFT), at=tz + 0.4, dur=0.7)

    # the marks crowd together
    tc = float(T.c03_s01_crowd_together)
    m.play(FadeOut(VGroup(br, brl, full, one)), at=tc - 0.5, dur=0.4)
    minor = log_scale_marks(XL, L, edge, up=False, label_size=24, skip=tuple(range(1, 11)))
    m.play(FadeIn(minor, lag_ratio=0.02), at=tc, dur=1.2)
    gaps = VGroup(Line(P3(xpos(1), by), P3(xpos(2), by), stroke_color=C.base, stroke_width=6),
                  Line(P3(xpos(9), by), P3(xpos(10), by), stroke_color=C.base, stroke_width=6))
    m.play(FadeIn(gaps), at=tc + 1.0, dur=0.5)
    s.camera.frame(tc + 0.9, center=(-3.0, LO), zoom=1.6, dur=1.0)
    s.camera.frame(tc + 2.1, center=(3.4, LO), zoom=1.6, dur=1.1)
    s.camera.frame(tc + 3.4, center=(0, 0), zoom=1.0, dur=0.9)
    m.play(FadeOut(gaps), at=tc + 3.8, dur=0.4)

    # a second scale above: a slide rule
    ts = float(T.c03_s01_side_by_side)
    slide_in = lambda t: -14.0 * (1 - ramp(t, ts - 0.2, 1.4))  # noqa: E731
    s.add(ArrayLayer(sh, height=shh, z=-1.9, opacity=fade(ts - 0.3, dur=0.3),
                     pos=Track(lambda t: (XL + L / 2 + slide_in(t) + 0.06, UP - 0.11))))
    s.add(ArrayLayer(wood_body(L, BH, seed=1623)[0], height=BH, z=-1.8,
                     pos=Track(lambda t: (XL + L / 2 + slide_in(t), UP)), opacity=fade(ts - 0.3, dur=0.3)))
    upper = log_scale_marks(XL, L, UP - BH / 2, up=True, label_size=24)
    c0 = upper.get_center()
    mu = s.manim(z=4, opacity=fade(ts - 0.3, dur=0.3))
    mu.add(upper)
    mu.drive(upper, lambda g, t: g.move_to(c0 + RIGHT * slide_in(t)), during=(ts - 0.4, float(s.end)))
    m.play(nums.animate.set_opacity(0), at=ts - 0.5, dur=0.4)
    hud.play(FadeOut(VGroup(eq, eq2)), at=float(s.end) - 0.3, dur=0.5)
