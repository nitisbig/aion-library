"""s19 series gap (ch5): the series says why. e^A e^B has AB among its second-order terms; e^{A+B} has (AB + BA)/2
there instead. Matching terms dim pair by pair until only those two remain; they agree only if AB = BA. The difference
AB − BA = [A, B] is the commutator; for the two shears it is diag(1, −1)."""
from aion import *

from beats import T
from shots import E, backdrop, finish, lab, p3, tex
from verify import B, N

C_ = N @ B - B @ N
assert np.allclose(C_, [[1, 0], [0, -1]])

P1 = [r"e^{A}e^{B}", "=", "I", "+", "A", "+", "B", "+", r"\tfrac{A^2}{2}", "+", r"AB", "+", r"\tfrac{B^2}{2}", "+",
      r"\cdots"]
P2 = [r"e^{A+B}", "=", "I", "+", "A", "+", "B", "+", r"\tfrac{A^2}{2}", "+", r"\tfrac{AB+BA}{2}", "+",
      r"\tfrac{B^2}{2}", "+", r"\cdots"]
COLS = {0: C.flow, 4: C.gen, 6: C.gen_b}


@scene(T.cut_gap, T.cut_loop)
def s19_series_gap(s):
    backdrop(s)
    m = s.manim(z=2)
    r1 = tex(*P1, size=42, colors=COLS)
    r2 = tex(*P2, size=42, colors=COLS)
    # align the two rows term by term: one column per part, as wide as the wider of the pair
    x = 0.0
    for a_, b_ in zip(r1, r2):
        w = max(a_.width, b_.width)
        a_.move_to([x + w / 2, 2.0, 0])
        b_.move_to([x + w / 2, 0.4, 0])
        x += w + 0.14
    VGroup(r1, r2).move_to([0, 1.2, 0])

    m.play(Write(r1), at=T.multiply + 0.3, dur=1.6)
    hl1 = SurroundingRectangle(r1[10], color=C.comm, buff=0.1, stroke_width=C.thin + 0.8)
    m.play(r1[10].animate.set_color(C.comm), Create(hl1), at=T.AB_term + 0.3, dur=0.5)
    m.play(Write(r2), at=T.expand_sum + 0.3, dur=1.6)
    hl2 = SurroundingRectangle(r2[10], color=C.comm, buff=0.1, stroke_width=C.thin + 0.8)
    m.play(r2[10].animate.set_color(C.comm), Create(hl2), at=T.half_half + 0.4, dur=0.5)

    # matching terms dim pair by pair
    same = [2, 4, 6, 8, 12]
    m.play(LaggedStart(*[AnimationGroup(r1[i].animate.set_opacity(0.2), r2[i].animate.set_opacity(0.2)) for i in same],
                       lag_ratio=0.3), *[r.animate.set_opacity(0.2) for r in (*r1[1:2], *r2[1:2])],
           *[g[i].animate.set_opacity(0.2) for g in (r1, r2) for i in (3, 5, 7, 9, 11, 13, 14)],
           at=T.match - 0.4, dur=1.6)

    # they match only if AB = BA; the difference is the commutator
    d = tex(r"AB", "-", r"\tfrac{AB+BA}{2}", "=", r"\tfrac12", r"\left(AB-BA\right)", size=46,
            colors={0: C.comm, 2: C.comm, 5: C.comm}).move_to([0, -1.25, 0])
    m.play(FadeIn(d, shift=0.1 * DOWN), at=T.match + 1.6, dur=0.7)
    cm = VGroup(tex(r"[A,B]", "=", r"AB-BA", "=", size=52, colors={0: C.comm, 2: C.comm}),
                Mat([["1", "0"], ["0", "-1"]], colors=C.comm, size=44, h_buff=0.9, v_buff=0.72)).arrange(RIGHT, buff=0.2)
    cm.move_to([0, -2.85, 0])
    m.play(FadeIn(cm[0], shift=0.1 * UP), at=T.commutator - 1.6, dur=0.6)
    tag = lab("the commutator", 26, C.comm).next_to(cm, RIGHT, buff=0.4)
    m.play(FadeIn(cm[1]), FadeIn(tag), at=T.commutator + 0.2, dur=0.5)
    m.play(FadeOut(VGroup(r1, r2, hl1, hl2, d)), at=T.cut_loop - 0.5, dur=0.5)
    m.play(FadeOut(VGroup(cm, tag)), at=T.cut_loop - 0.4, dur=0.4)
    finish(s)
