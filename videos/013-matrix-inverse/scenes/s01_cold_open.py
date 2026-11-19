"""s01 cold open: a machined key on a grid in 3D. Four moves carry the sheet away, one matrix brings every point straight home."""
from aion import *

from beats import T
from film import frame
from shots import AINV_ROWS, A_ROWS, C, mat_label, pin, plated


@scene(0.0, T.cut_crush)
def s01_cold_open(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(0.0, T.cut_crush)], z=0))
    m = s.manim(z=5, parallax=0.0)

    a = pin(plated(mat_label("A", A_ROWS, C.fwd, colors=[C.ihat, C.jhat])))
    m.play(FadeIn(a.card), FadeIn(a.border), FadeIn(a.sym), FadeIn(a.eq), FadeIn(a.mat.br), at=T.four_mv + 0.4, dur=0.6)
    m.play(FadeIn(a.mat.cols[0], shift=0.08 * DOWN), at=T.single, dur=0.5)
    m.play(FadeIn(a.mat.cols[1], shift=0.08 * DOWN), at=T.single + 0.45, dur=0.5)

    inv = pin(plated(mat_label(r"A^{-1}", AINV_ROWS, C.back, size=38, h_buff=1.25, v_buff=1.02)), top=a.get_bottom()[1] - 0.14)
    m.play(FadeIn(inv, shift=0.08 * DOWN), at=T.one_more, dur=0.7)
    m.play(Indicate(inv.sym, color=C.back, scale_factor=1.25), at=T.inverse_word + 0.3, dur=1.0)
