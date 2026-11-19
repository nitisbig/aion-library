"""s19 weak: a second powder half as strong as the first folds every possible mix onto one line. A target off the line has no recipe, and a
target on it has endless recipes, whose threads all land on the same mix."""
from aion import *

from beats import T
from film3 import frame
from shots import S_ROWS, carded, lab, mat_label, plated


@scene(T.cut_weak, T.cut_drone)
def s19_weak(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_weak, T.cut_drone)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # labels

    weak = plated(mat_label("S", S_ROWS, C.fwd, colors=[C.ihat, C.jhat], size=40, h_buff=1.0, v_buff=1.0)).scale(0.8).move_to([-5.0, 2.62, 0])
    m.play(FadeIn(weak), at=T.weak, dur=0.6)

    t_none = carded(lab("no recipe", size=36, color=C.wrong).move_to([4.9, 3.2, 0]), buff=0.08)
    m.play(FadeIn(t_none), at=T.norec, dur=0.45)
    m.play(FadeOut(t_none), at=T.on_line - 0.55, dur=0.4)

    t_many = carded(lab("endless recipes", size=36, color=C.null).move_to([-4.6, -3.2, 0]), buff=0.08)
    m.play(FadeIn(t_many), at=T.endless + 0.55, dur=0.45)

    # ── two ways to fail, one collapse ──
    back_tag = carded(lab("no recipe", size=36, color=C.wrong).move_to([4.9, 3.2, 0]), buff=0.08)
    m.play(FadeIn(back_tag), at=T.no_ans - 0.05, dur=0.45)
    m.play(Indicate(t_many, color=C.null, scale_factor=1.12), at=T.too_many, dur=0.9)
    s.solid(C.bg, z=50, opacity=key(T.cut_drone - 0.42, 0.0, 1.0, dur=0.4, lead=0))
