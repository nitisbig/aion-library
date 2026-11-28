"""c01_s02 · The staircase. Storyboard: plan/scene_plan.md § c01_s02.

The doubling chain from c01_s01 climbs into place: each value lifts onto its tread and each ×2 onto its riser, then
the staircase draws in under them, with a faint back edge so it reads as a solid object. The motif: each step up is one more ×2, treads carry the value, the left axis counts the steps. 2¹⁰ = 1024 writes in
the column and its three coloured parts slide into log₂ 1024 = 10; ⇕ joins them. A light climbs the stairs (read from
the steps) and runs back down (read from the result).
"""
from aion import *

from beats import T
from ch1 import DEPTH, N, SH, SW, X0S, Y0S, chain, stair10, stair_depth
from kit import P3, add_rail, glow, ramp


@scene(T.c01_s02, T.c01_s03)
def s05_c01_staircase(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 1)
    m = s.manim(z=5)
    st, steps_lbl, e1, iff, e2, legend = stair10()
    ts = float(T.c01_s02_staircase)
    vals, tags = chain()                                   # as c01_s01 left it: every ×2 counted (lit, enlarged)
    for g in tags:
        g.set_color(C.steps).scale(1.25)
    m.add(vals, tags)
    m.play(LaggedStart(*[ReplacementTransform(a, b, path_arc=0.3) for a, b in zip(vals, st.vals)], lag_ratio=0.12),
           LaggedStart(*[ReplacementTransform(a, b, path_arc=0.3) for a, b in zip(tags, st.tags)], lag_ratio=0.12),
           at=ts - 0.9, dur=2.2, lead=0.0)
    m.play(FadeIn(st.floor), at=ts + 0.4, dur=0.5)
    m.play(Create(st.path), at=ts + 0.5, dur=2.4, ease="linear", lead=0.0)
    s.manim(z=4).play(FadeIn(stair_depth(N, X0S, Y0S, SW, SH, d=DEPTH)), at=ts + 2.2, dur=1.2)
    m.play(LaggedStart(*[Indicate(g, color=C.base, scale_factor=1.35) for g in st.tags], lag_ratio=0.25),
           at=T.c01_s02_multiplication_by_tw, dur=2.0)
    m.play(FadeIn(st.axis, lag_ratio=0.1), FadeIn(steps_lbl), at=T.c01_s02_height, dur=1.2)
    m.play(Write(e1), at=T.c01_s02_ten_twos, dur=1.0)
    tl = float(T.c01_s02_logarithm)
    m.play(TransformFromCopy(e1[0], e2[1]), TransformFromCopy(e1[1], e2[5]), TransformFromCopy(e1[3], e2[3]),
           at=tl, dur=1.1)
    m.play(Write(VGroup(e2[0], e2[2], e2[4])), at=tl + 0.9, dur=0.7)
    m.play(FadeIn(iff, scale=0.8), at=T.c01_s02_same_fact, dur=0.6)
    m.play(FadeIn(legend), at=T.c01_s02_same_fact + 0.6, dur=0.8)

    up, down = float(T.c01_s02_number_of_steps), float(T.c01_s02_from_the_result)
    path = st.path

    def runner(t):
        if t < down - 0.1:
            u, col = ramp(t, up - 0.1, 1.5), C.steps
        else:
            u, col = 1 - ramp(t, down - 0.1, 1.4), C.value
        if (t > down + 1.4) or u <= 0.001:
            return VGroup()
        a0 = max(0.0, u - 0.12)
        seg = path.copy().pointwise_become_partial(path, a0, u).set_stroke(color=col, width=6)
        return VGroup(seg, Dot(path.point_from_proportion(min(u, 1.0)), radius=0.08, color=col))
    glow(s, C.steps, z=6, k=0.8).redraw(runner, during=(up - 0.3, min(down + 1.5, float(s.end))))
    m.play(Indicate(e2[5], color=C.steps, scale_factor=1.15), at=up + 0.8, dur=0.8)
    m.play(Indicate(e1[3], color=C.value, scale_factor=1.15), at=down + 0.6, dur=0.8)
