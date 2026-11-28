"""c05_s01 · The area under 1/x. Storyboard: plan/scene_plan.md § c05_s01.

y = 1/x draws on the grid and the area from 1 sweeps out and back. A small tag (Saint-Vincent · de Sarasa · 1647).
The regions [1, 2] and [1, 3] fill, then [1, 6]; the readouts are computed by quadrature (logdata):
0.693 + 1.099 = 1.792, and the same three areas as bars: on "add" the two shorter bars slide end to end into
the outline of the third and fill it exactly. Beside the area rule, log 2 + log 3 = log 6 from chapter three.
"""
from aion import *

import logdata as ld
from beats import T
from ch5 import COLW, CX, col, edge, hyper_plane, hyperbola, region
from kit import P3, Y1, add_rail, chapter_break, ctex, glow, mix, ramp, show_tag, word_at


@scene(T.c05_s01, T.c05_s02)
def s16_c05_area(s):
    s.solid(C.bg, z=-200)
    chapter_break(s, 5, T.c05_s01)
    add_rail(s, 5)
    m = s.manim(z=3)
    grid, X, Y = hyper_plane()
    t0 = float(T.c05_s01)
    m.play(FadeIn(grid), at=t0 + 1.2, dur=0.8)
    hyp = hyperbola(X, Y)
    m.play(Create(hyp), at=T.c05_s01_one_over_x, dur=1.4)

    # the area from 1 sweeps out and back
    tsh = float(T.c05_s01_shade_the_area)
    sweep = lambda t: 1 + 3.0 * ramp(t, tsh, 2.2) - 3.0 * ramp(t, tsh + 4.5, 1.6)  # noqa: E731
    out = Track(lambda t: 1 - ramp(t, float(s.end) - 0.7, 0.6))
    a = s.manim(z=2, opacity=out)
    a.redraw(lambda t: region(X, Y, 1, sweep(t)), during=(tsh - 0.1, tsh + 6.2))
    ge = glow(s, C.natural, z=4, k=0.9)
    ge.redraw(lambda t: edge(X, Y, sweep(t)) if sweep(t) > 1.01 else VGroup(), during=(tsh - 0.1, tsh + 6.2))
    show_tag(s, "Saint-Vincent · de Sarasa · 1647", C.area, T.c05_s01_sixteen_forties, dur=4.0, at=P3(-1.0, Y1))

    # [1,2], [1,3], then [1,6]
    t12, t13, t16 = float(T.c05_s01_one_to_two), float(T.c05_s01_one_to_three), float(T.c05_s01_one_to_six)
    r12 = region(X, Y, 1, 2, opacity=0.38)
    r13 = region(X, Y, 1, 3, color=mix(C.area, C.text, 0.35), opacity=0.16)
    r16 = region(X, Y, 1, 6, opacity=0.32)
    a.play(FadeIn(r12), at=t12, dur=0.6)
    e2 = glow(s, C.natural, z=4, k=0.8, opacity=out)
    e2.play(Create(edge(X, Y, 2)), at=t12, dur=0.5)
    a.play(FadeIn(r13), at=t13, dur=0.6)
    e2.play(Create(edge(X, Y, 3, color=mix(C.natural, C.text, 0.35))), at=t13, dur=0.5)
    a.play(FadeIn(r16), at=t16, dur=0.8)
    e2.play(Create(edge(X, Y, 6)), at=t16, dur=0.6)
    rule = ctex([("A(1,2)", C.area), ("+", None), ("A(1,3)", C.area), ("=", None), ("A(1,6)", C.area)], 40)
    col(rule, 2.6)
    m.play(Write(rule), at=t16 + 0.5, dur=1.0)

    # check the numbers
    tc = float(T.c05_s01_check_the_numbers)
    nums = ctex([(f"{ld.A12:.3f}", C.steps), ("+", None), (f"{ld.A13:.3f}", C.steps), ("=", None),
                 (f"{ld.A16:.3f}", C.steps)], 44)
    col(nums, 1.85)
    m.play(FadeIn(nums[0], shift=0.1 * UP), at=word_at("nine", tc), dur=0.5)
    m.play(FadeIn(VGroup(nums[1], nums[2]), shift=0.1 * UP), at=word_at("one", word_at("nine", tc) + 0.3), dur=0.5)
    m.play(FadeIn(VGroup(nums[3], nums[4]), shift=0.1 * UP), at=word_at("together", tc), dur=0.5)
    # the areas as lengths: two bars, an outline the length of A(1,6), and the bars laid end to end fill it
    k, x0, h = COLW / ld.A16, CX - COLW / 2, 0.2
    soft = mix(C.area, C.text, 0.35)

    def bar(w, y, color, fill=0.75):
        return Rectangle(width=w, height=h, stroke_width=0, fill_color=color, fill_opacity=fill) \
            .move_to(P3(x0 + w / 2, y))
    b12, b13 = bar(k * ld.A12, -0.25, C.area), bar(k * ld.A13, -0.65, soft)
    slot = Rectangle(width=k * ld.A16, height=h + 0.1, stroke_color=C.area, stroke_width=2, fill_opacity=0) \
        .move_to(P3(x0 + k * ld.A16 / 2, -1.3))
    for bb, w in ((b12, "nine"), (b13, "one")):
        m.play(GrowFromEdge(bb, LEFT), at=word_at(w, tc), dur=0.6)
    m.play(Create(slot), at=word_at("together", tc), dur=0.7)
    ta = word_at("add", tc)
    m.play(b12.animate.move_to(P3(x0 + k * ld.A12 / 2, -1.3)), at=ta, dur=0.8)
    m.play(b13.animate.move_to(P3(x0 + k * ld.A12 + k * ld.A13 / 2, -1.3)), at=ta + 0.35, dur=0.8)
    hit = glow(s, C.area, z=4, k=1.0, opacity=out)
    hit.play(Succession(FadeIn(slot.copy().set_stroke(width=4)), FadeOut(slot.copy().set_stroke(width=4))),
             at=ta + 1.2, dur=1.0)

    tb = float(T.c05_s01_behave_exactly_like_)
    logs = ctex([(r"\log ", None), ("2", C.value), ("+", None), (r"\log ", None), ("3", C.value), ("=", None),
                 (r"\log ", None), ("6", C.value)], 44)
    col(logs, 0.95)
    m.play(Write(logs), at=tb, dur=1.0)

    m.play(FadeOut(VGroup(rule, nums, logs, b12, b13, slot)), at=float(s.end) - 0.7, dur=0.6)
