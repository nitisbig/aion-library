"""c05_s02 · Stretch and squash. Storyboard: plan/scene_plan.md § c05_s02.

The region [1, 2] is cut into eight strips that tile it exactly. Stretched sideways by s (1 → 3), each strip lands
exactly under the curve again: x ↦ s·x and height 1/x ↦ 1/(s·x). The region slides to [3, 6] while an area readout,
computed by quadrature at every frame, holds at 0.693. Then A(3,6) = A(1,2), [1,3] + [3,6] = [1,6], the general rule,
and a "?" on the x-axis for the base the curve chooses.
"""
from aion import *

import logdata as ld
from beats import T
from ch5 import CX, col, edge, hyper_plane, hyperbola, region
from kit import P3, add_rail, ctex, glow, mix, ramp, tex, tint

N = 8


@scene(T.c05_s02, T.c05_s03)
def s17_c05_stretch(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 5)
    t0, end = float(T.c05_s02), float(s.end)
    out = Track(lambda t: 1 - ramp(t, end - 0.7, 0.6))
    grid, X, Y = hyper_plane()
    hyp = hyperbola(X, Y)
    base = s.manim(z=3)
    base.add(grid, hyp, at=t0)
    m = s.manim(z=3, opacity=out)
    a = s.manim(z=2, opacity=out)

    # the strips
    tr = float(T.c05_s02_simple_reason)
    tst = float(T.c05_s02_stretch_it_sideways)
    sx = lambda t: 1 + 2 * ramp(t, tst + 0.2, 3.6)  # noqa: E731
    cut = lambda t: ramp(t, tr, 0.8)  # noqa: E731
    xs = [1 + i / N for i in range(N + 1)]

    def strips(t):
        k, c = sx(t), cut(t)
        g = VGroup()
        for i in range(N):
            r = region(X, Y, xs[i], xs[i + 1], opacity=0.4, n=12, sx=k)
            r.set_stroke(C.bg, width=2.5 * c)
            g.add(r)
        return g
    a.redraw(strips, during=(tr - 0.1, end))
    ghost = region(X, Y, 1, 2, color=tint(C.area, 0.5), opacity=0.08)
    a.add(ghost, at=tst)
    ge = glow(s, C.natural, z=4, k=0.8, opacity=out)
    ge.redraw(lambda t: VGroup(edge(X, Y, sx(t)), edge(X, Y, 2 * sx(t))), during=(tr - 0.1, end))

    # the area readout holds while the region stretches
    def readout(t):
        k = sx(t)
        v = ld.area(k, 2 * k)
        return ctex([(r"\text{area}=", C.area), (f"{v:.3f}", C.steps)], 40).move_to(P3(CX, -1.0))
    m.redraw(readout, during=(tr + 0.6, end))

    # ×3 sideways, ÷3 down
    t3 = tst + 3.9
    wid = VGroup(DoubleArrow(P3(X(3), Y(0.5)), P3(X(6), Y(0.5)), buff=0, stroke_width=2.5, color=C.base,
                             tip_length=0.15),
                 tex(r"\times3\ \text{wider}", 26, C.base).move_to(P3(X(4.5), Y(0.5) + 0.3)))
    m.play(FadeIn(wid), at=t3, dur=0.6)
    tl = float(T.c05_s02_three_times_lower)
    drop = VGroup(DashedLine(P3(X(1), Y(1)), P3(X(3), Y(1)), stroke_color=tint(C.value, 0.6), stroke_width=1.6,
                             dash_length=0.07),
                  Arrow(P3(X(3), Y(1)), P3(X(3), Y(1 / 3)), buff=0, stroke_width=3, color=C.value,
                        max_tip_length_to_length_ratio=0.25),
                  tex(r"\div3\ \text{lower}", 26, C.value).next_to(P3(X(3), Y(0.68)), LEFT, buff=0.15))
    m.play(Create(drop[0]), GrowArrow(drop[1]), FadeIn(drop[2]), at=tl, dur=0.8)

    # A(3,6) = A(1,2), and [1,3] + [3,6] = [1,6]
    t36 = float(T.c05_s02_three_to_six)
    e1 = ctex([("A(3,6)", C.area), ("=", None), ("A(1,2)", C.area)], 42)
    col(e1, 2.6)
    m.play(Write(e1), at=t36, dur=0.9)
    t16 = float(T.c05_s02_makes_one_to_six)
    r13 = region(X, Y, 1, 3, color=mix(C.area, C.text, 0.35), opacity=0.2)
    a.play(FadeIn(r13), at=t16 - 1.6, dur=0.8)
    m.play(FadeOut(VGroup(drop, wid)), at=t16 - 1.6, dur=0.6)
    e3 = glow(s, C.natural, z=4, k=0.8, opacity=out)
    e3.play(Create(edge(X, Y, 3, color=mix(C.natural, C.text, 0.35))), at=t16 - 1.6, dur=0.5)
    e2 = ctex([("A(1,3)", C.area), ("+", None), ("A(3,6)", C.area), ("=", None), ("A(1,6)", C.area)], 42)
    col(e2, 1.85)
    m.play(Write(e2), at=t16, dur=1.0)
    gen = ctex([("A(1,", C.area), ("ab", C.value), (")", C.area), ("=", None), ("A(1,", C.area), ("a", C.value),
                (")", C.area), ("+", None), ("A(1,", C.area), ("b", C.value), (")", C.area)], 44)
    col(gen, 0.85)
    m.play(Write(gen), at=t16 + 1.6, dur=1.2)

    # the curve chooses its base: a ? on the axis, just past 2
    tc = float(T.c05_s02_chooses_its_base)
    q = tex("?", 40, C.natural).move_to(P3(X(2.72), Y(1 / 2.72) + 0.45))
    m.play(FadeIn(q, scale=1.4), Indicate(gen, color=C.text, scale_factor=1.04), at=tc, dur=0.7)
