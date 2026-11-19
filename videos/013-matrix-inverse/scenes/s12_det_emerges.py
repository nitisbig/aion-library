"""s12 determinant: slides keep area and the squash takes it to a quarter, so the determinant was hiding in the list of moves. The same
steps done with letters give the recipe for any two by two inverse, and leave a denominator that could be zero."""
from aion import *

from beats import T
from film2 import frame
from shots import A_ROWS, EASE, E_TAGS, carded, lab, tex


@scene(T.cut_det, T.cut_tilt)
def s12_det_emerges(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_det, T.cut_tilt)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # the list and the formula

    # ── what each move does to area ──
    factors = (r"\times 1", r"\times 1", r"\times \tfrac{1}{4}", r"\times 1")
    rows = VGroup()
    for i, (word, f) in enumerate(zip(E_TAGS, factors)):
        y = 3.05 - 0.82 * i
        w = lab(word, size=34, color=C.back)
        w.move_to([-6.5 + w.width / 2, y, 0])
        v = tex(f, size=46, color=C.det).move_to([-3.75, y, 0])
        rows.add(VGroup(BackgroundRectangle(VGroup(w, v), color=C.bg, fill_opacity=0.92, buff=0.1), w, v))
    m.play(LaggedStart(*[FadeIn(r, shift=0.06 * RIGHT) for r in rows], lag_ratio=0.2), at=T.hiding, dur=1.0)
    m.play(Indicate(rows[2][2], color=C.home, scale_factor=1.3), at=T.squash_again + 0.2, dur=1.0)

    def area(v):
        return carded(tex(r"\text{area}", "=", v, size=60, colors={0: C.det, 2: C.det}).move_to([-4.6, -0.42, 0]), buff=0.12)
    a4, a1, a4b = area("4"), area("1"), area("4")
    m.play(FadeIn(a4), at=T.hiding + 0.3, dur=0.6)
    m.play(FadeOut(a4), FadeIn(a1), at=T.squash_again + 0.75, dur=0.4)
    m.play(FadeOut(a1), FadeIn(a4b), at=T.four + 1.75, dur=0.5)
    det = carded(tex(r"\det A", "=", "4", size=72, colors={0: C.det, 2: C.det}).move_to([-4.5, -1.85, 0]), buff=0.14)
    m.play(FadeIn(det, shift=0.08 * UP), at=T.det, dur=0.7)
    m.play(FadeOut(VGroup(rows, a4b, det)), at=T.det + 1.0, dur=0.6)

    # ── the same steps, in letters ──
    size, y0 = 66, 0.45
    sym_a = tex("A", "=", size=size + 6, colors={0: C.fwd})
    nums = Mat(A_ROWS, colors=[C.ihat, C.jhat], size=size, h_buff=1.15, v_buff=1.25, pad=0.26)
    lets = Mat([["a", "b"], ["c", "d"]], colors=[C.ihat, C.jhat], size=size, h_buff=1.15, v_buff=1.25, pad=0.26)
    left = VGroup(sym_a, nums).arrange(RIGHT, buff=0.26).move_to([-4.5, y0, 0])
    lets.move_to(nums)
    m.play(FadeIn(left), at=T.run - 0.25, dur=0.6)
    m.play(*[ReplacementTransform(nums.cell(i, j), lets.cell(i, j)) for i in range(2) for j in range(2)], at=T.letters, dur=0.8, ease=EASE)

    # ── the recipe ──
    goal = Mat([["d", "-b"], ["-c", "a"]], colors=C.back, size=size, h_buff=1.35, v_buff=1.25, pad=0.26)
    frac = tex(r"\frac{1}{ad-bc}", size=size, color=C.det)
    head = tex(r"A^{-1}", "=", size=size + 6, colors={0: C.back})
    right = VGroup(head, frac, goal).arrange(RIGHT, buff=0.28).move_to([2.55, y0, 0])
    toks = {n: tex(n, size=size, color=C.back).move_to(goal.cell(i, j)) for n, (i, j) in {"a": (0, 0), "b": (0, 1), "c": (1, 0), "d": (1, 1)}.items()}
    m.play(FadeIn(head), FadeIn(goal.br), *[FadeIn(v) for v in toks.values()], at=T.recipe, dur=0.7)

    arc = dict(path_arc=PI * 0.8)
    pair1 = VGroup(SurroundingRectangle(toks["a"], color=C.home, buff=0.1, stroke_width=2.2), SurroundingRectangle(toks["d"], color=C.home, buff=0.1, stroke_width=2.2))
    m.play(Create(pair1), at=T.swap - 0.1, dur=0.35)
    m.play(FadeOut(pair1), Transform(toks["a"], goal.cell(1, 1).copy(), **arc), Transform(toks["d"], goal.cell(0, 0).copy(), **arc), at=T.swap + 0.45, dur=0.8, ease=EASE)
    pair2 = VGroup(SurroundingRectangle(toks["b"], color=C.home, buff=0.1, stroke_width=2.2), SurroundingRectangle(toks["c"], color=C.home, buff=0.1, stroke_width=2.2))
    m.play(Create(pair2), at=T.negate - 0.1, dur=0.3)
    m.play(FadeOut(pair2), ReplacementTransform(toks["b"], goal.cell(0, 1)), ReplacementTransform(toks["c"], goal.cell(1, 0)), at=T.negate + 0.4, dur=0.55, ease=EASE)
    m.play(FadeIn(frac, shift=0.3 * RIGHT), at=T.divide, dur=0.7, ease=EASE)

    # ── and what if that is zero? ──
    worry = tex("ad-bc", "=", "0", "?", size=72, colors={0: C.det, 2: C.det, 3: C.home}).move_to([0, -2.6, 0])
    m.play(FadeIn(worry, shift=0.08 * UP), at=T.what_h, dur=0.6)
    m.play(Indicate(frac, color=C.det, scale_factor=1.12), at=T.nothing_div - 0.2, dur=0.9)
    s.solid(C.bg, z=50, opacity=key(T.cut_tilt - 0.42, 0.0, 1.0, dur=0.4, lead=0))
