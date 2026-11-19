"""s18 solve: which recipe landed on the target? The inverse follows the thread home to (2, 1), and two of the first plus one of the second
walk out to the target to confirm it."""
from aion import *

from beats import T
from film3 import frame
from shots import ask_x, heading5, powder_table, tex

EQ_AT = np.array([-4.2, 3.05, 0.0])


@scene(T.cut_solve, T.cut_weak)
def s18_solve(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_solve, T.cut_weak)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # table and equations

    # ── exactly where s17 stopped ──
    table = powder_table()
    head, ask = heading5(), ask_x()
    m.add(table, head, ask, at=T.cut_solve)

    # ── the table gives way to the plane of recipes ──
    m.play(FadeOut(table), FadeOut(ask), at=T.geo - 0.2, dur=0.5)
    system = VGroup(tex("3", "x", "+", "y", "=", "7", size=46, colors={1: C.ihat, 3: C.jhat, 5: C.vec}),
                    tex("2", "x", "+", "2", "y", "=", "6", size=46, colors={1: C.ihat, 4: C.jhat, 6: C.vec})).arrange(DOWN, buff=0.2, aligned_edge=RIGHT).move_to(EQ_AT)
    m.play(FadeOut(head), FadeIn(system), at=T.geo + 0.5, dur=0.5)

    # ── the way back ──
    solve = tex(r"\mathbf{x}", "=", r"A^{-1}", r"\mathbf{b}", size=62, colors={0: C.vec, 2: C.back, 3: C.vec}).move_to(EQ_AT)
    m.play(FadeOut(system), FadeIn(solve), at=T.apply - 0.1, dur=0.5)

    # ── two of the first, one of the second ──
    found = tex(r"\mathbf{x}", "=", "(", "2", r",\,", "1", ")", size=62, colors={0: C.vec, 3: C.ihat, 5: C.jhat}).move_to(EQ_AT)
    m.play(FadeOut(solve), FadeIn(found), at=T.answer - 0.85, dur=0.5)
    m.play(FadeOut(found), at=T.cut_weak - 0.4, dur=0.3, lead=0)
