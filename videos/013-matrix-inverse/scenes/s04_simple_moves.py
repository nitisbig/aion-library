"""s04 simple moves: the columns say where the arrows land and the plane follows. Then three moves whose way back is obvious
(turn, stretch, slide), each parked in a ledger with its way back beneath the tag."""
from aion import *

from beats import T
from film1 import frame
from shots import A_ROWS, caps, ledger, mat_label, pin, plated, tex


@scene(T.cut_simple, T.cut_wrong)
def s04_simple_moves(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_simple, T.cut_wrong)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # matrices and the ledger
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    # ── chapter card ──
    sym, name = tex(r"A^{-1}", size=112, color=C.back), caps("The way back", size=56)
    rule = Line([-2.1, 0, 0], [2.1, 0, 0], color=C.key, stroke_width=2.4)
    card = VGroup(sym, rule, name).arrange(DOWN, buff=0.34)
    mh.play(FadeIn(sym), FadeIn(name), at=T.cut_simple + 0.05, dur=0.3, lead=0)
    mh.play(Create(rule), at=T.cut_simple + 0.1, dur=0.6, ease="easy_ease", lead=0)
    mh.play(FadeOut(card), at=T.move + 0.2, dur=0.4)

    # ── A, read by its columns ──
    a = pin(plated(mat_label("A", A_ROWS, C.fwd, colors=[C.ihat, C.jhat])))
    boxes = VGroup(a.mat.col_box(0, C.ihat), a.mat.col_box(1, C.jhat))
    m.play(FadeIn(a), at=T.columns - 0.35, dur=0.5)
    m.play(Create(boxes), at=T.columns + 0.1, dur=0.5)
    m.play(FadeOut(boxes), at=T.rest + 0.2, dur=0.4)
    m.play(FadeOut(a), at=T.easy - 0.3, dur=0.5)

    # ── the ledger fills up as each move is made ──
    rows = ledger()
    for name_, go, ret in (("turn", T.turn, T.turn_back), ("stretch", T.stretch, T.shrinks), ("slide", T.slide, T.deck - 0.4)):
        r = rows[name_]
        m.play(FadeIn(r.card), FadeIn(r.tag), FadeIn(r.fwd, shift=0.06 * RIGHT), at=go, dur=0.5)
        m.play(FadeIn(r.back, shift=0.06 * RIGHT), at=ret, dur=0.5)
