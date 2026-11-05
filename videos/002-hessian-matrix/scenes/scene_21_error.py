"""Scene 21 · Ch6: landscapes of error (480.417–496.817 s).

"So why does this matter outside a math class? Because so much of the modern world is
about finding the bottom of a valley. Training a neural network means searching a
landscape for its lowest point. The height is the error. And the landscape has not two
dimensions, but millions."

A rugged seeded landscape rises out of black and the camera flies slowly over it. Its
deepest pit (the global minimum, asserted in ch6) glows; a ball spirals into it. The two
floor axes through the pit light up, then burst into a fan of hundreds of faint axes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch6 as C

START, END = V.scene_range(21)


class Scene21Error(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # scene 20 ends on black
        clk = ValueTracker(0.0)
        self.run_clock(clk)
        rig = C.land_rig(clk)
        plate = rig.plate()
        self.add(plate, *rig.trackers())

        # 6-1 · a landscape of error, flown over slowly
        self.beat("why does this matter", *rig.to(opacity=1.0), rt=1.8)
        ring = C.ring_at(plate, *C.PIT)
        ring.set_stroke(opacity=0.0)
        self.add(ring)
        self.beat("bottom of a valley", ring.animate.set_stroke(opacity=1.0), rt=0.8)

        eb = C.eyebrow()
        self.beat("neural network", FadeIn(eb, shift=RIGHT * 0.1), rt=0.6)

        k = ValueTracker(0.0)
        ball = V.walker()
        V.pin(ball, plate, lambda: (*C.settle_xy(k.get_value()),
                                    float(plate.height(*C.settle_xy(k.get_value()))) + 0.03))
        self.add(k)
        self.beat("lowest point", FadeIn(ball), k.animate.set_value(1.0), rt=1.2)

        cap = C.height_caption(eb)
        self.beat("height is the error", FadeIn(cap, shift=UP * 0.08), rt=0.6)

        # 6-2 · not two dimensions, but millions
        axes = C.floor_axes(plate)
        self.beat("not two dimensions", *[Create(a) for a in axes], rt=0.5)
        g = ValueTracker(0.0)
        self.add(g, C.fan(plate, g))
        self.bring_to_front(axes, ring, ball)
        self.beat("but millions", g.animate.set_value(1.0), rt=0.6, rate=rush_from)
        self.finish()
