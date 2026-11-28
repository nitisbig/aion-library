"""c02_s02 · Every rule from one picture. Storyboard: plan/scene_plan.md § c02_s02.

One base-2 staircase (1 … 128) and three walks on it, each paired with its rule in the column (kept, a stack of three):
two climbs end to end (4 then 8 make 32: log ab = log a + log b), a climb to 32 and a walk back down 8 (to 4:
log a/b = log a − log b), and one climb of 4 repeated three times (to 64: log aⁿ = n log a). Braces on the right count
the steps, and a bright dot runs along the front of every climb. On "different side" the three rules light in turn.
"""
from aion import *

from beats import T
from kit import P3, add_rail, ctex, glow, mix, polyline, ramp, staircase, tex, tint
from ch1 import lift, stair_depth
from ch2 import identity

X0S, Y0S, SW, SH, N = -5.0, -2.6, 0.66, 0.6, 7
BX = X0S + (N + 1) * SW + 0.25                       # braces stand right of the stairs
RX = 4.25                                           # rule column


def climb(k0, k1, color, width=6):
    """Path along the staircase from level k0 to level k1 (either direction)."""
    lo, hi = min(k0, k1), max(k0, k1)
    pts = [(X0S + (lo + 0.5) * SW, Y0S + lo * SH)]
    for k in range(lo, hi):
        pts += [(X0S + (k + 1) * SW, Y0S + k * SH), (X0S + (k + 1) * SW, Y0S + (k + 1) * SH)]
    pts.append((X0S + (hi + 0.5) * SW, Y0S + hi * SH))
    if k0 > k1:
        pts = pts[::-1]
    return polyline(pts, color, width)


def brace(k0, k1, label, color, shift=0.0):
    b = BraceBetweenPoints(P3(BX + shift, Y0S + k1 * SH), P3(BX + shift, Y0S + k0 * SH), direction=RIGHT, color=color)
    return VGroup(b, tex(label, 28, color).next_to(b, RIGHT, buff=0.1))


def rule(parts, y):
    return ctex(parts, 40).move_to(P3(RX, y))


@scene(T.c02_s02, T.c02_s03)
def s08_c02_rules(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 2)
    m = s.manim(z=5)
    idt = identity()
    m.add(idt)
    m.play(FadeOut(idt, shift=0.3 * DOWN), at=T.c02_s02_main_rule - 0.4, dur=0.6)

    st = lift(staircase(N, X0S, Y0S, SW, SH, label_size=26), (0.12, 0.09))
    m.play(FadeIn(st.floor), Create(st.path), at=T.c02_s02 + 0.6, dur=1.0)
    s.manim(z=4).play(FadeIn(stair_depth(N, X0S, Y0S, SW, SH, d=(0.12, 0.09))), at=T.c02_s02 + 1.2, dur=0.8)
    m.play(FadeIn(VGroup(st.vals, st.tags, st.axis)), at=T.c02_s02 + 1.0, dur=0.8)
    hl = glow(s, C.steps, z=6, k=0.6)
    soft = mix(C.steps, C.text, 0.45)
    walkers = VGroup()

    def walk(path, at, dur, color):
        """Draw a climb with a bright dot running along its front edge."""
        dot = Dot(path.get_start(), radius=0.075, color=color)
        walkers.add(dot)
        hl.play(Create(path), MoveAlongPath(dot, path), at=at, dur=dur)
        return dot

    # (1) product: climb a = 4 (2 steps), then b = 8 (3 steps) to ab = 32
    t1 = float(T.c02_s02_main_rule)
    ca, cb = climb(0, 2, C.steps), climb(2, 5, soft)
    w1 = walk(ca, t1 + 0.2, 0.8, C.text)
    hl.play(MoveAlongPath(w1, cb), Create(cb), at=t1 + 1.1, dur=1.0)
    ba, bb = brace(0, 2, r"\log a", C.steps), brace(2, 5, r"\log b", soft)
    m.play(FadeIn(ba), at=t1 + 0.8, dur=0.4)
    m.play(FadeIn(bb), at=t1 + 2.0, dur=0.4)
    m.play(*[st.vals[k].animate.scale(1.3) for k in (2, 5)], at=t1 + 2.2, dur=0.4)
    r1 = rule([(r"\log(", None), ("ab", C.value), (r")=\log ", None), ("a", C.value), (r"+\log ", None),
               ("b", C.value)], 2.35)
    m.play(Write(r1), at=T.c02_s02_sum_of_the_logarithm, dur=1.0)
    tag1 = tex(r"4\cdot 8=32", 28, C.muted).next_to(r1, DOWN, buff=0.15)
    m.play(FadeIn(tag1), at=float(T.c02_s02_sum_of_the_logarithm) + 0.8, dur=0.5)

    # (2) quotient: from 32 walk back down 3 steps (÷ 8) to 4
    t2 = float(T.c02_s02_walks_back)
    m.play(*[st.vals[k].animate.scale(1 / 1.3) for k in (2, 5)], at=t2 - 0.6, dur=0.4)
    hl.play(FadeOut(VGroup(ca, cb, w1)), at=t2 - 0.6, dur=0.5)
    m.play(FadeOut(VGroup(ba, bb)), at=t2 - 0.6, dur=0.5)
    up5 = climb(0, 5, C.steps)
    dn3 = climb(5, 2, C.value, 5)
    w2 = walk(up5, t2 - 0.1, 0.9, C.text)
    hl.play(Create(dn3), MoveAlongPath(w2, dn3), at=t2 + 1.0, dur=1.2)
    divs = VGroup(*[tex(r"\div2", 26, C.value).move_to(st.tags[k], aligned_edge=LEFT) for k in (4, 3, 2)])
    m.play(LaggedStart(*[FadeOut(st.tags[k]) for k in (4, 3, 2)], lag_ratio=0.5), at=t2 + 1.0, dur=1.1)
    m.play(LaggedStart(*[FadeIn(d) for d in divs], lag_ratio=0.5), at=t2 + 1.1, dur=1.1)
    bA, bB = brace(0, 5, r"\log a", C.steps, shift=1.15), brace(2, 5, r"\log b", C.value)
    m.play(FadeIn(bA), at=t2 + 0.6, dur=0.4)
    m.play(FadeIn(bB), at=t2 + 2.0, dur=0.4)
    r2 = rule([(r"\log", None), (r"\frac{a}{b}", C.value), (r"=\log ", None), ("a", C.value), (r"-\log ", None),
               ("b", C.value)], 1.1)
    m.play(Write(r2), at=T.c02_s02_difference, dur=1.0)
    tag2 = tex(r"32\div 8=4", 28, C.muted).next_to(r2, DOWN, buff=0.12)
    m.play(FadeIn(tag2), at=float(T.c02_s02_difference) + 0.8, dur=0.5)

    # (3) power: the climb of a = 4 (2 steps) three times, to 4³ = 64
    t3 = float(T.c02_s02_repeats_the_same_cli)
    hl.play(FadeOut(VGroup(up5, dn3, w2)), at=t3 - 0.7, dur=0.5)
    m.play(FadeOut(VGroup(divs, bA, bB)), at=t3 - 0.7, dur=0.5)
    m.play(FadeIn(VGroup(*[st.tags[k] for k in (4, 3, 2)])), at=t3 - 0.5, dur=0.5)
    copies = [climb(0, 2, C.steps), climb(2, 4, soft), climb(4, 6, C.steps)]
    brs = VGroup()
    w3 = Dot(copies[0].get_start(), radius=0.075, color=C.text)
    walkers.add(w3)
    for j, c in enumerate(copies):
        hl.play(Create(c), MoveAlongPath(w3, c), at=t3 + 0.1 + 1.0 * j, dur=0.8)
        b = brace(2 * j, 2 * j + 2, r"\log a", C.steps if j != 1 else soft)
        brs.add(b)
        m.play(FadeIn(b), at=t3 + 0.6 + 1.0 * j, dur=0.4)
    m.play(st.vals[6].animate.scale(1.3), at=t3 + 3.0, dur=0.4)
    r3 = rule([(r"\log ", None), ("a", C.value), ("^n", C.steps), ("=", None), ("n", C.steps), (r"\log ", None),
               ("a", C.value)], -0.15)
    m.play(Write(r3), at=T.c02_s02_many_copies, dur=1.0)
    tag3 = tex(r"4^3=64", 28, C.muted).next_to(r3, DOWN, buff=0.15)
    m.play(FadeIn(tag3), at=float(T.c02_s02_many_copies) + 0.8, dur=0.5)

    # every rule is the staircase seen from a different side
    td = float(T.c02_s02_different_side)
    unders = VGroup(*[Line(r.get_corner(DL) + DOWN * 0.08, r.get_corner(DR) + DOWN * 0.08, stroke_color=C.steps,
                           stroke_width=2.5) for r in (r1, r2, r3)])
    for tg in (tag1, tag2, tag3):
        m.play(FadeOut(tg), at=td - 0.9, dur=0.4)
    hl.play(LaggedStart(*[Create(u) for u in unders], lag_ratio=0.5), at=td - 0.3, dur=1.4)
    end = float(s.end)
    hl.play(FadeOut(VGroup(*copies, unders, w3)), at=end - 0.2, dur=0.6)
    m.play(FadeOut(VGroup(st, brs, r1, r2, r3, tag1, tag2, tag3)), at=end - 0.2, dur=0.6)
