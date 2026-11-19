"""s15 columns: the first column of S is twice the second, so the columns are dependent. That dependence is the crushed arrow: one of the
first minus two of the second walks out and comes back to the origin, so S sends (1, -2) to nothing."""
from aion import *

from beats import T
from film2 import frame
from shots import S_ROWS, carded, lab, mat_label, tex


@scene(T.cut_columns, T.cut_fact)
def s15_columns(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_columns, T.cut_fact)], z=0))
    mb = s.manim(z=4, parallax=0.0)                   # the plate behind the equations
    m = s.manim(z=5, parallax=0.0)                    # equations

    plate = Rectangle(width=4.5, height=7.1, stroke_color=C.frame, stroke_width=1.6, fill_color=C.bg, fill_opacity=0.96).move_to([4.42, 0, 0])
    mb.play(FadeIn(plate), at=T.cut_columns + 0.05, dur=0.4, lead=0)

    x = 4.42
    mat = mat_label("S", S_ROWS, C.fwd, colors=[C.ihat, C.jhat], size=46, h_buff=1.0, v_buff=1.1).move_to([x, 2.35, 0])
    m.play(FadeIn(mat), at=T.read_cols - 0.2, dur=0.6)

    eq1 = carded(tex("c_1", "=", "2", "c_2", size=58, colors={0: C.ihat, 3: C.jhat}).move_to([x, 0.55, 0]), buff=0.1)
    m.play(FadeIn(eq1, shift=0.06 * DOWN), at=T.twice + 0.3, dur=0.6)
    m.play(Indicate(eq1[1][3], color=C.jhat, scale_factor=1.3), at=T.nothing_new, dur=0.9)

    t_dep = carded(lab("linearly dependent", size=38, color=C.text).move_to([x, -2.95, 0]), buff=0.1)
    m.play(FadeIn(t_dep), at=T.dependent, dur=0.6)

    eq2 = carded(tex("1", r"\,", "c_1", "-", "2", r"\,", "c_2", "=", "0", size=52, colors={0: C.null, 2: C.ihat, 4: C.null, 6: C.jhat}).move_to([x, -0.55, 0]), buff=0.1)
    m.play(FadeIn(eq2, shift=0.06 * DOWN), at=T.recipe_cols, dur=0.6)
    eq3 = carded(tex("S", r"(1,\,-2)", "=", "0", size=58, colors={0: C.fwd, 1: C.null}).move_to([x, -1.65, 0]), buff=0.1)
    m.play(FadeIn(eq3, shift=0.06 * DOWN), at=T.makes_nothing - 0.05, dur=0.6)
    s.solid(C.bg, z=50, opacity=key(T.cut_fact - 0.42, 0.0, 1.0, dur=0.4, lead=0))
