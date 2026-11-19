"""s06 threads: one point draws a thread from where it started to where it landed. Every point does the same, and that web is
the move. The way back is the same web walked in the opposite direction."""
from aion import *

from beats import T
from film1 import frame
from shots import carded, pin, tex


@scene(T.cut_threads, T.cut_identity)
def s06_threads(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_threads, T.cut_identity)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # symbols

    # ── the symbol that names the web ──
    sym_b = pin(carded(tex(r"A^{-1}", size=76, color=C.back), buff=0.12))
    sym_a = carded(tex("A", size=76, color=C.fwd).move_to(sym_b[1][0][0]), buff=0.12)
    m.play(FadeIn(sym_a), at=T.web, dur=0.5)
    m.play(FadeOut(sym_a), FadeIn(sym_b), at=T.opposite - 0.15, dur=0.7)
    m.play(Indicate(sym_b[1], color=C.back, scale_factor=1.15), at=T.reversed_, dur=1.0)
