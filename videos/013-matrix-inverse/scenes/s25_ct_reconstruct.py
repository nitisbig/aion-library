"""s25 CT: more and more shadows, and a real least-squares solve at each count. A blur, then an outline, then the key with every tooth in place."""
from aion import *

from beats import T
from film3 import STAGES as stages, frame
from shots import lab, tex


@scene(T.cut_ct, T.cut_outro)
def s25_ct_reconstruct(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_ct, T.cut_outro)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # the counter

    x, y = 5.3, 0.3
    tag = lab("shadows", size=36, color=C.data).move_to([x, y - 0.85, 0])
    m.play(FadeIn(tag), at=T.two, dur=0.45)
    last = None
    for at, n in stages:
        num = tex(str(n), size=104, color=C.data).move_to([x, y, 0])
        anims = [FadeIn(num)] + ([FadeOut(last)] if last is not None else [])
        m.play(*anims, at=at - 0.05, dur=0.3)
        last = num
    s.solid(C.bg, z=50, opacity=key(T.cut_outro - 0.42, 0.0, 1.0, dur=0.4, lead=0))
