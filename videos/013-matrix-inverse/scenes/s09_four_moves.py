"""s09 four moves: the bent plane from the cold open comes home in four simple moves. Each arrow returns to the outline that marks
where it belongs, and each move joins the list on the left."""
from aion import *

from beats import T
from film2 import frame
from shots import A_ROWS, chapter_card, four_rows, mat_label, pin, plated, tex


@scene(T.cut_four, T.cut_record)
def s09_four_moves(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_four, T.cut_record)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # matrices
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    # ── chapter card ──
    chapter_card(mh, tex(r"[\,", "A", r"\mid", "I", r"\,]", size=104, colors={1: C.fwd, 3: C.home}), "Finding the way back", T.cut_four, T.bent - 0.65)

    # ── A, then the list of moves that undoes it ──
    a = pin(plated(mat_label("A", A_ROWS, C.fwd, colors=[C.ihat, C.jhat])))
    m.play(FadeIn(a), at=T.bent, dur=0.6)
    m.play(FadeOut(a), at=T.move1 - 0.5, dur=0.45)
    rows = four_rows()
    for r, at in zip(rows, (T.move1, T.move2, T.move3, T.move4)):
        m.play(FadeIn(r, shift=0.06 * RIGHT), at=at, dur=0.5)

    # ── four moves, and the key is home ──
    m.play(LaggedStart(*[Indicate(r.tag, color=C.home, scale_factor=1.15) for r in rows], lag_ratio=0.25), at=T.four_home, dur=1.1)
