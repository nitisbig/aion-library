"""c02_s01 · Napier's trick. Storyboard: plan/scene_plan.md § c02_s01.

Chapter one's staircase comes back and is written out as a table: each tread's value lifts into the top row and each
step count slides from the axis into the row beneath, while the stairs themselves fade. To multiply 8 × 32, look up
their steps (3 and 5), add them (8), and read across: eight steps up is 256, which lights with a ring. Then the same
sum as motion: hops along the steps row (+3, then +5) run in step with hops along the value row (×8, then ×32), and
each pair merges into one hop (+8 below, ×256 above): adding below is multiplying above. The identity writes last.
"""
from aion import *

import logdata as ld
from beats import T
from ch1 import DEPTH, N, SH, SW, X0S, Y0S, stair10, stair_depth
from ch2 import identity
from kit import P3, X0, add_rail, chapter_break, ctex, glow, mix, sans, tex, tint, word_at

A, B = ld.NAPIER_A, ld.NAPIER_B            # 8, 32
KA, KB = 3, 5
COLX = [-5.35 + 1.12 * k for k in range(11)]
YV, YS = 1.95, 0.85                        # value row, steps row


def hop(k0, k1, y, up, color, h=0.55, width=4):
    """An arc from column k0 to k1 bulging `h` above (up) or below the row at y, with a dot where it lands."""
    a, b = P3(COLX[k0], y), P3(COLX[k1], y)
    th = 8 * h / (b[0] - a[0])
    arc = ArcBetweenPoints(a, b, angle=-th if up else th, stroke_color=color, stroke_width=width)
    return VGroup(arc, Dot(b, radius=0.05, color=color))


@scene(T.c02_s01, T.c02_s02)
def s07_c02_trick(s):
    s.solid(C.bg, z=-200)
    chapter_break(s, 2, T.c02_s01)
    add_rail(s, 2)
    m = s.manim(z=5)
    end = float(s.end)

    # the staircase returns, then is written out as a table
    st, steps_lbl, *_ = stair10()
    depth = stair_depth(N, X0S, Y0S, SW, SH, d=DEPTH)
    t_in = word_at("straight", float(T.c02_s01))
    m.play(FadeIn(VGroup(depth, st, steps_lbl)), at=t_in - 0.3, dur=0.9)
    vals = VGroup(*[tex(str(2 ** k), 38, C.value).move_to(P3(COLX[k], YV)) for k in range(11)])
    steps = VGroup(*[tex(str(k), 38, C.steps).move_to(P3(COLX[k], YS)) for k in range(11)])
    rule = Line(P3(COLX[0] - 0.45, (YV + YS) / 2), P3(COLX[-1] + 0.5, (YV + YS) / 2), stroke_color=tint(C.muted, 0.5),
                stroke_width=1.2)
    lv = sans("value", 20, C.muted).move_to(P3(X0, YV), aligned_edge=LEFT)
    ls = sans("steps", 20, C.steps).move_to(P3(X0, YS), aligned_edge=LEFT)
    tp, tsx = float(T.c02_s01_powers_of_two), float(T.c02_s01_steps)
    m.play(LaggedStart(*[ReplacementTransform(a, b) for a, b in zip(st.vals, vals)], lag_ratio=0.12), at=tp, dur=1.8)
    m.play(FadeOut(VGroup(st.tags, depth), shift=0.2 * DOWN), at=tp + 0.4, dur=0.8)
    m.play(Create(rule), at=tsx - 0.4, dur=0.6)
    labels = [st.axis[2 + 2 * k] for k in range(N + 1)]
    m.play(LaggedStart(*[ReplacementTransform(a, b) for a, b in zip(labels, steps)], lag_ratio=0.12), at=tsx, dur=1.8)
    m.play(FadeIn(VGroup(lv, ls)), at=tsx + 1.2, dur=0.6)
    m.play(FadeOut(VGroup(st.path, st.floor, steps_lbl, *[a for a in st.axis if all(a is not b for b in labels)])),
           at=tsx + 0.3, dur=0.8)

    # look up 8 and 32
    t8 = float(T.c02_s01_eight_by_thirty_two)
    arrows = VGroup(*[Arrow(P3(COLX[k], YV - 0.24), P3(COLX[k], YS + 0.26), buff=0, stroke_width=2.5, color=C.muted,
                            max_tip_length_to_length_ratio=0.25) for k in (KA, KB)])
    m.play(vals[KA].animate.scale(1.3), vals[KB].animate.scale(1.3), at=t8, dur=0.5)
    m.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.4), at=word_at("look", t8), dur=0.8)
    m.play(steps[KA].animate.scale(1.3), steps[KB].animate.scale(1.3), at=word_at("three", t8), dur=0.5)

    # add the steps
    ta = float(T.c02_s01_add_them)
    add = ctex([("3", C.steps), ("+", None), ("5", C.steps), ("=", None), ("8", C.steps)], 60).move_to(P3(-1.2, -1.15))
    m.play(TransformFromCopy(steps[KA], add[0]), TransformFromCopy(steps[KB], add[2]), at=ta, dur=0.9)
    m.play(FadeIn(add[1]), at=ta + 0.5, dur=0.4)
    m.play(Write(VGroup(add[3], add[4])), at=ta + 0.9, dur=0.6)

    # read across: 8 steps → 256
    tr = float(T.c02_s01_read_across)
    m.play(TransformFromCopy(add[4], steps[8].copy().scale(1.3)), at=tr, dur=1.0)
    m.play(steps[8].animate.scale(1.3), at=tr + 0.9, dur=0.3)
    up = Arrow(P3(COLX[8], YS + 0.26), P3(COLX[8], YV - 0.26), buff=0, stroke_width=2.5, color=C.value,
               max_tip_length_to_length_ratio=0.25)
    m.play(GrowArrow(up), at=word_at("steps", tr), dur=0.6)
    m.play(vals[8].animate.scale(1.35), at=word_at("hundred", tr), dur=0.5)
    ring = Circle(radius=0.45, stroke_color=C.value, stroke_width=2.5).move_to(vals[8])
    gl = glow(s, C.value, z=4, k=1.0)
    gl.play(Create(ring), at=word_at("hundred", tr) + 0.2, dur=0.7)

    # the same thing as motion: hops that add below are hops that multiply above
    tc = float(T.c02_s01_climbing_three_steps)
    m.play(FadeOut(VGroup(arrows, up)), at=tc - 0.6, dur=0.5)
    soft_s, soft_v = mix(C.steps, C.text, 0.45), mix(C.value, C.text, 0.4)
    hs = [hop(0, 3, YS - 0.3, False, C.steps), hop(3, 8, YS - 0.3, False, soft_s)]
    hv = [hop(0, 3, YV + 0.3, True, C.value), hop(3, 8, YV + 0.3, True, soft_v)]
    ls_ = [tex("+3", 28, C.steps).move_to(P3((COLX[0] + COLX[3]) / 2, YS - 1.17)),
           tex("+5", 28, soft_s).move_to(P3((COLX[3] + COLX[8]) / 2, YS - 1.17))]
    lv_ = [tex(r"\times 8", 28, C.value).move_to(P3((COLX[0] + COLX[3]) / 2, YV + 1.17)),
           tex(r"\times 32", 28, soft_v).move_to(P3((COLX[3] + COLX[8]) / 2, YV + 1.17))]
    hl, hu = glow(s, C.steps, z=6, k=0.6), glow(s, C.value, z=6, k=0.6)
    for j, w in enumerate(("three", "five")):
        tj = word_at(w, tc)
        hl.play(Create(hs[j]), at=tj, dur=0.7)
        hu.play(Create(hv[j]), at=tj, dur=0.7)
        m.play(FadeIn(ls_[j]), FadeIn(lv_[j]), at=tj + 0.3, dur=0.4)
    t_all = word_at("eight", tc)
    one_s, one_v = hop(0, 8, YS - 0.3, False, C.steps, h=0.75), hop(0, 8, YV + 0.3, True, C.value, h=0.75)
    lab_s = tex("+8", 30, C.steps).move_to(P3(COLX[4], YS - 1.42))
    lab_v = tex(r"\times 256", 30, C.value).move_to(P3(COLX[4], YV + 1.42))
    hl.play(ReplacementTransform(VGroup(*hs), one_s), at=t_all, dur=0.9)
    hu.play(ReplacementTransform(VGroup(*hv), one_v), at=t_all, dur=0.9)
    m.play(ReplacementTransform(VGroup(*ls_), lab_s), ReplacementTransform(VGroup(*lv_), lab_v), at=t_all, dur=0.9)

    idt = identity()
    m.play(FadeOut(add, shift=0.2 * DOWN), at=T.c02_s01_addition - 1.0, dur=0.5)
    m.play(Write(idt), at=T.c02_s01_addition - 0.6, dur=1.4)
    m.play(FadeOut(VGroup(vals, steps, rule, lv, ls, lab_s, lab_v)), at=end - 0.2, dur=0.6)
    hl.play(FadeOut(one_s), at=end - 0.2, dur=0.6)
    hu.play(FadeOut(one_v), at=end - 0.2, dur=0.6)
    gl.play(FadeOut(ring), at=end - 0.2, dur=0.6)
