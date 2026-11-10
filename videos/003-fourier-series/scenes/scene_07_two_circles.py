"""Scene 07 · Ch2: two circles (129.267–146.967 s).

"One circle gives you one smooth wave. So let's add a second. Put a smaller circle on
the tip of the first, and let it spin three times as fast. Now the tip rides on two
motions at once, so its height is the first height plus the second. The wave picks up
a little ripple."

Continues S06's flat sine (same clock, same layout). The plain sine stays as a dim
ghost; the second circle (⅓ size, 3× speed) arrives on its word (ch2.amps schedule).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import UP, FadeIn, FadeOut, there_and_back

import shared as V
import ch2 as C

START, END = V.scene_range(7)


class Scene07TwoCircles(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        m = C.Stack(self, C.S07_START)

        # "one smooth wave": chapter eyebrow; the sine stays behind as a ghost
        eb = V.eyebrow("02 · STACKING CIRCLES")
        self.beat("one smooth wave", FadeIn(eb, shift=UP * 0.08), *m.to(ghost_op=1.0), rt=0.6)

        # "add a second": a dashed empty circle rides the tip (anticipation)
        self.beat("add a second", *m.to(dash_op=1.0), FadeOut(eb), rt=0.4)

        # "smaller circle": it fills in (its size comes from ch2.amps), the dashes go
        self.beat("smaller circle", *m.to(dash_op=0.0), rt=0.7)

        # "two motions": the rims brighten for a moment
        self.beat("two motions", m.v["rim_op"].animate(rate_func=there_and_back).set_value(0.95), rt=0.8, rate=None)

        # "first height" + "plus the second": two stacked bars land on the marker
        self.beat("first height", *m.to(bar1_op=1.0), rt=0.5)
        self.beat("plus the second", *m.to(bar2_op=1.0), rt=0.5)

        # "little ripple": the bars leave; the rippled wave runs over the ghost sine
        self.beat("little ripple", *m.to(bar1_op=0.0, bar2_op=0.0), rt=0.5)
        self.finish()
