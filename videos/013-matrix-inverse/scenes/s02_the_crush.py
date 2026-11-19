"""s02 the crush: a near twin flattens the sheet to a line. Hung under the light, the key can flip any tooth and its shadow never changes."""
from aion import *

from beats import T
from film import frame
from shots import AINV_ROWS, A_ROWS, C, S_ROWS, carded, lab, mat_label, pin, plated, tex


@scene(T.cut_crush, T.cut_promise)
def s02_the_crush(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_crush, T.cut_promise)], z=0))
    m = s.manim(z=5, parallax=0.0)

    a = pin(plated(mat_label("A", A_ROWS, C.fwd, colors=[C.ihat, C.jhat])))
    inv = pin(plated(mat_label(r"A^{-1}", AINV_ROWS, C.back, size=38, h_buff=1.25, v_buff=1.02)), top=a.get_bottom()[1] - 0.14)
    b = pin(plated(mat_label("S", S_ROWS, C.fwd, colors=[C.ihat, C.jhat])), left=a.get_right()[0] + 0.3)
    m.add(a, inv)
    m.play(FadeOut(inv), at=T.cut_crush + 0.4, dur=0.6)
    m.play(FadeIn(b, shift=0.08 * RIGHT), at=T.twin, dur=0.7)
    boxes = VGroup(*[SurroundingRectangle(x.mat.cols[1], color=C.null, buff=0.1, stroke_width=2.2, fill_color=C.null, fill_opacity=0.14) for x in (a, b)])
    m.play(Create(boxes), at=T.second_col, dur=0.6)
    m.play(FadeOut(a), FadeOut(boxes), at=T.flat + 1.0, dur=0.7)
    m.play(b.animate.move_to([-6.6 + b.width / 2, b.get_y(), 0]), at=T.streak, dur=0.9, ease="easy_ease")

    q = VGroup(tex(r"S^{-1}", size=48, color=C.back), tex("=", size=48), tex("?", size=56, color=C.back)).arrange(RIGHT, buff=0.2)
    q.next_to(b, DOWN, buff=0.3).align_to(b, LEFT)
    q_card = BackgroundRectangle(q, color=C.bg, fill_opacity=0.92, buff=0.12)
    m.add(q_card, at=T.put_back)
    m.play(FadeIn(q), at=T.put_back + 0.3, dur=0.7)
    m.play(q.animate.set_color(C.wrong), at=T.no_hold, dur=0.8)
    m.play(FadeOut(b), FadeOut(q), FadeOut(q_card), at=T.this_key - 1.1, dur=0.6)

    t16 = carded(lab("16 keys", size=40, color=C.key).move_to([4.36, 2.62, 0]))
    t1 = carded(lab("1 shadow", size=40, color=C.shadow).move_to([-1.6, -2.1, 0]))
    m.play(FadeIn(t16), at=T.sixteen, dur=0.5)
    m.play(FadeIn(t1), at=T.same_mark + 0.5, dur=0.5)
    m.play(FadeOut(t16), FadeOut(t1), at=T.shadow + 1.4, dur=0.6)
