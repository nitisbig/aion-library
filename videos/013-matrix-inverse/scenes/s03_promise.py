"""s03 the promise: the twins side by side, four worlds that depend on the difference, and the key to be rebuilt from its shadows."""
from aion import *

from beats import T
from film import frame
from shots import C, caps, carded, tex


@scene(T.cut_promise, T.cut_simple)
def s03_promise(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_promise, T.cut_simple)], z=0))
    m = s.manim(z=5, parallax=0.0)

    names = VGroup(carded(tex("A", size=64, color=C.fwd).move_to([-4.2, 3.0, 0])), carded(tex("S", size=64, color=C.fwd).move_to([4.2, 3.0, 0])))
    m.play(FadeIn(names), at=T.why + 0.1, dur=0.5)
    m.play(FadeOut(names), at=T.game - 1.0, dur=0.35)

    title = caps("What Matrix Inverses Actually Mean", size=60).move_to([0, 3.1, 0])
    rule = Line([-3.4, 2.55, 0], [3.4, 2.55, 0], color=C.key, stroke_width=2.4)
    m.play(FadeIn(title, shift=0.06 * DOWN), at=T.impossible + 0.5, dur=1.0)
    m.play(Create(rule), at=T.impossible + 0.9, dur=1.0, ease="easy_ease")
    s.solid(C.bg, z=50, opacity=key(T.cut_simple - 0.42, 0.0, 1.0, dur=0.4, lead=0))
