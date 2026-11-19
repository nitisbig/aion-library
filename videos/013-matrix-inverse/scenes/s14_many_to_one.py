"""s14 many to one: every point on a whole line lands on one spot. The source sheet floats above the line it collapses onto, so the fan of threads is
real geometry, and the way back would need that one spot to climb to all of them at once."""
from aion import *

from beats import T
from film2 import frame
from shots import carded, lab


@scene(T.cut_many, T.cut_columns)
def s14_many_to_one(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_many, T.cut_columns)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # the tag
    tag = carded(lab("many to one", size=38, color=C.fwd).move_to([4.6, -3.0, 0]), buff=0.1)
    m.play(FadeIn(tag), at=T.entire, dur=0.5)
    s.solid(C.bg, z=50, opacity=key(T.cut_columns - 0.42, 0.0, 1.0, dur=0.4, lead=0))
