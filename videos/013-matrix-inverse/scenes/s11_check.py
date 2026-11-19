"""s11 check: A^-1 times A, entry by entry, gives the identity. Then the four moves of the rewind turn out to be the four moves of the
cold open, read in the opposite direction."""
from aion import *

from beats import T
from film2 import frame
from shots import AINV_ROWS, A_ROWS, EASE, E_TAGS, lab, tex, varrow

STEP = 1.1
LINES = {(0, 0): (r"\frac{1}{2}", "3", "-", r"\frac{1}{4}", "2", "1"), (0, 1): (r"\frac{1}{2}", "1", "-", r"\frac{1}{4}", "2", "0"),
         (1, 0): (r"-\frac{1}{2}", "3", "+", r"\frac{3}{4}", "2", "0"), (1, 1): (r"-\frac{1}{2}", "1", "+", r"\frac{3}{4}", "2", "1")}
HOOK_TAGS = ("lean", "pull", "lean", "lean")


def line(i, j):
    a, p, op, b, q, r = LINES[i, j]
    t = tex(a, r"\cdot", p, op, b, r"\cdot", q, "=", r, size=46, colors={0: C.back, 2: C.fwd, 4: C.back, 6: C.fwd, 8: C.home})
    return t.move_to([-3.35 + 6.7 * j, -1.05 - 1.3 * i, 0])


@scene(T.cut_check, T.cut_det)
def s11_check(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_check, T.cut_det)], z=0))
    m = s.manim(z=5, parallax=0.0)

    # ── the product ──
    kw = dict(size=54, h_buff=1.4, v_buff=1.62, pad=0.28)
    inv, a = Mat(AINV_ROWS, colors=C.back, **kw), Mat(A_ROWS, colors=C.fwd, **kw)
    res = Mat([["1", "0"], ["0", "1"]], colors=C.home, **kw)
    eq = tex("=", size=64)
    row = VGroup(inv, a, eq, res).arrange(RIGHT, buff=0.34).move_to([0, 1.72, 0])
    m.play(FadeIn(inv, shift=0.08 * DOWN), FadeIn(a, shift=0.08 * DOWN), at=T.check, dur=0.7)
    m.play(FadeIn(eq), FadeIn(res.br), at=T.multiply + 0.5, dur=0.6)

    # ── one entry at a time: a row of the inverse against a column of A ──
    t0 = T.cancel - 0.3
    box_r, box_c = None, None
    lines = []
    for k, (i, j) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        at = t0 + k * STEP
        nr = SurroundingRectangle(VGroup(inv.cell(i, 0), inv.cell(i, 1)), color=C.back, buff=0.12, stroke_width=2.6)
        nc = SurroundingRectangle(VGroup(a.cell(0, j), a.cell(1, j)), color=C.fwd, buff=0.12, stroke_width=2.6)
        if box_r is None:
            m.play(Create(nr), Create(nc), at=at - 0.25, dur=0.3)
        else:
            m.play(ReplacementTransform(box_r, nr), ReplacementTransform(box_c, nc), at=at - 0.25, dur=0.3, ease=EASE)
        box_r, box_c = nr, nc
        ln = line(i, j)
        lines.append(ln)
        m.play(FadeIn(ln, shift=0.05 * UP), FadeIn(res.cell(i, j)), at=at, dur=0.45)
    m.play(FadeOut(box_r), FadeOut(box_c), at=t0 + 4 * STEP - 0.2, dur=0.4)
    m.play(FadeOut(VGroup(inv, a, eq, res, *lines)), at=T.recognize - 0.75, dur=0.6)

    # ── the same four moves, read in both directions ──
    xs = np.linspace(-5.25, 5.25, 5)

    def link(k, y, color, word, rightward):
        a_, b_ = xs[k] + 0.78, xs[k + 1] - 0.78
        arrow = varrow((a_, y), (b_, y), color, width=3.0, tip=0.2) if rightward else varrow((b_, y), (a_, y), color, width=3.0, tip=0.2)
        off = 0.36 if y > 0 else -0.36
        return VGroup(arrow, lab(word, size=30, color=color).move_to([(xs[k] + xs[k + 1]) / 2, y + off, 0]))

    top = VGroup(*[link(k, 1.5, C.fwd, HOOK_TAGS[k], True) for k in range(4)])
    low = [link(k, -1.5, C.back, E_TAGS[3 - k], False) for k in range(4)]
    m.play(LaggedStart(*[FadeIn(g) for g in top], lag_ratio=0.2), at=T.recognize + 0.5, dur=1.1)
    m.play(LaggedStart(*[FadeIn(g, shift=0.08 * LEFT) for g in reversed(low)], lag_ratio=0.28), at=T.same_four + 0.9, dur=1.6)
    s.solid(C.bg, z=50, opacity=key(T.cut_det - 0.42, 0.0, 1.0, dur=0.4, lead=0))
