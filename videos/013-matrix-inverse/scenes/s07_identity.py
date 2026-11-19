"""s07 identity: out along the threads and back is a move that does nothing, and doing nothing has a matrix. Taking the way back
first walks the same threads the other way round, so both orders give the identity."""
from aion import *

from beats import T
from film1 import frame
from shots import EASE, carded, mat_label, pin, tex


def order_marks(first, second, c1, c2):
    """`1` under the move made first, `2` under the second, and an arc between them (products read right to left)."""
    y = min(first.get_bottom()[1], second.get_bottom()[1]) - 0.24
    one, two = tex("1", size=38, color=c1).move_to([first.get_x(), y, 0]), tex("2", size=38, color=c2).move_to([second.get_x(), y, 0])
    arc = CurvedArrow(np.array([first.get_x(), y - 0.2, 0]), np.array([second.get_x(), y - 0.2, 0]), angle=-PI * 0.6, color=c2,
                      stroke_width=2.6, tip_length=0.14)
    return VGroup(one, two, arc)


@scene(T.cut_identity, T.cut_rewind)
def s07_identity(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_identity, T.cut_rewind)], z=0))
    mb = s.manim(z=3, parallax=0.0)                   # black cards behind the equations
    m = s.manim(z=5, parallax=0.0)                    # equations

    # ── A⁻¹A, written in the order it happens ──
    sym = pin(carded(tex(r"A^{-1}", size=76, color=C.back), buff=0.12))
    mb.add(sym[0])
    eq1 = pin(tex(r"A^{-1}", "A", "=", "I", size=76, colors={0: C.back, 1: C.fwd, 3: C.home}))
    card1 = BackgroundRectangle(VGroup(eq1), color=C.bg, fill_opacity=0.92, buff=0.12)
    marks1 = order_marks(eq1[1], eq1[0], C.fwd, C.back)
    card1m = BackgroundRectangle(marks1, color=C.bg, fill_opacity=0.92, buff=0.08)
    mb.play(ReplacementTransform(sym[0], card1), at=T.out_back - 0.2, dur=0.6, ease=EASE)
    m.add(eq1[0])
    m.play(FadeIn(eq1[1]), at=T.out_back - 0.2, dur=0.6)
    mb.play(FadeIn(card1m), at=T.out_back + 0.8, dur=0.4)
    m.play(FadeIn(marks1[0]), at=T.out_back + 0.8, dur=0.4)
    m.play(FadeIn(marks1[1]), Create(marks1[2]), at=T.come_back, dur=0.7)

    # ── doing nothing has a matrix ──
    idm = pin(mat_label("I", [["1", "0"], ["0", "1"]], C.home, colors=[C.ihat, C.jhat]), top=1.72)
    boxes = VGroup(idm.mat.col_box(0, C.ihat), idm.mat.col_box(1, C.jhat))
    m.play(FadeIn(idm, shift=0.06 * DOWN), at=T.has_matrix + 0.6, dur=0.6)
    m.play(Create(boxes), at=T.its_cols + 0.4, dur=0.6)
    m.play(FadeOut(boxes), at=T.identity - 0.3, dur=0.4)
    m.play(FadeIn(eq1[2]), FadeIn(eq1[3], shift=0.08 * LEFT), at=T.identity, dur=0.6)

    # ── it behaves like the number one ──
    ix = pin(carded(tex("I", r"\mathbf{x}", "=", r"\mathbf{x}", size=64, colors={0: C.home, 1: C.vec, 3: C.vec}), buff=0.1),
             top=idm.get_bottom()[1] - 0.15)
    m.play(FadeIn(ix, shift=0.06 * DOWN), at=T.mult, dur=0.6)
    m.play(FadeOut(idm), FadeOut(ix), at=T.so_inv - 0.2, dur=0.6)

    # ── after A, then before it ──
    m.play(Indicate(eq1[1], color=C.fwd, scale_factor=1.2), at=T.after_a, dur=0.8)
    m.play(Indicate(eq1[0], color=C.back, scale_factor=1.15), at=T.after_a + 0.8, dur=0.8)

    eq2 = pin(tex("A", r"A^{-1}", "=", "I", size=76, colors={0: C.fwd, 1: C.back, 3: C.home}), top=1.45)
    card2 = BackgroundRectangle(eq2, color=C.bg, fill_opacity=0.92, buff=0.12)
    marks2 = order_marks(eq2[1], eq2[0], C.back, C.fwd)
    card2m = BackgroundRectangle(marks2, color=C.bg, fill_opacity=0.92, buff=0.08)
    mb.play(FadeIn(card2), FadeIn(card2m), at=T.back_first, dur=0.6)
    m.play(FadeIn(eq2[0]), FadeIn(eq2[1]), FadeIn(marks2[0]), at=T.back_first, dur=0.6)
    m.play(FadeIn(marks2[1]), Create(marks2[2]), at=T.gets_home - 1.3, dur=0.7)
    m.play(FadeIn(eq2[2]), FadeIn(eq2[3], shift=0.08 * LEFT), at=T.gets_home + 0.5, dur=0.5)

    # ── either order ──
    s.solid(C.bg, z=4, opacity=key(T.either, 0.0, 0.94, dur=0.8, ease=EASE))
    merged = tex(r"A^{-1}", "A", "=", "A", r"A^{-1}", "=", "I", size=104, colors={0: C.back, 1: C.fwd, 3: C.fwd, 4: C.back, 6: C.home})
    merged.move_to(ORIGIN)
    mb.play(FadeOut(VGroup(card1, card1m, card2, card2m)), at=T.either, dur=0.6)
    m.play(FadeOut(marks1), FadeOut(marks2),
           ReplacementTransform(VGroup(eq1[0], eq1[1], eq1[2]), VGroup(merged[0], merged[1], merged[2])),
           ReplacementTransform(VGroup(eq2[0], eq2[1], eq2[2]), VGroup(merged[3], merged[4], merged[5])),
           ReplacementTransform(VGroup(eq1[3], eq2[3]), merged[6]), at=T.either, dur=1.0, ease=EASE)
    s.solid(C.bg, z=50, opacity=key(T.cut_rewind - 0.42, 0.0, 1.0, dur=0.4, lead=0))
