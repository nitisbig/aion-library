"""Scene 08 · Ch2: one third, one fifth, one seventh (146.967–168.800 s).

"Now let's be more deliberate. Make the first circle a little taller than the wave
we're aiming for. The second spins three times as fast, at one third the size. The
next, five times as fast, at one fifth. Then seven times, at one seventh. Before I keep
going, take a moment to guess. What do you think this is turning into?"

Reset to one circle on the target (hairlines ±H), then 4/π·H, then the odd circles at
1/n. The spectrum strip ("the list") appears for the first time. On the guess, the
whole machine slows to a crawl (ch2.clock) and nothing new appears.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import UP, FadeIn, Line, ValueTracker, VGroup, VMobject

from aion import style as S
import shared as V
import ch2 as C

START, END = V.scene_range(8)


class Scene08OddCircles(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        m = C.Stack(self, C.S07_END)
        fr = C.frac_labels(m)

        # "deliberate": back to one circle, sized to the target; the list appears with one bar
        self.beat("deliberate", *m.to(ghost_op=0.0, hair_op=1.0, strip_op=1.0),
                  FadeIn(fr[0], rate_func=V.window(0.5, 1.0)), rt=0.8, rate=None)

        # "a little taller": the circle grows past the hairline; a small bracket shows the extra
        br_op = ValueTracker(0.0)
        self.add(br_op)

        def bracket():
            o = br_op.get_value()
            if o <= 0:
                return VMobject()
            a0, x = C.amps(self.now)[0], C.X0 + 0.2
            if a0 - C.H < 0.01:
                return VMobject()
            return VGroup(Line([x, C.H, 0], [x, a0, 0]), Line([x - 0.07, a0, 0], [x + 0.07, a0, 0]),
                          Line([x - 0.07, C.H, 0], [x + 0.07, C.H, 0])).set_stroke(S.LABEL, 2, o)
        self.add(V.redraw(bracket))
        self.beat("a little taller", br_op.animate.set_value(1.0), rt=0.6)

        # the odd circles arrive on their words (sizes from ch2.amps); each fraction flashes in
        after = self.t("a little taller")
        for k, (speed_key, frac_key) in enumerate((("three times as fast", "one third"),
                                                   ("five times as fast", "one fifth"),
                                                   ("seven times", "one seventh")), start=1):
            after = self.t(speed_key, after)
            if k == 1:
                self.play_at(after, br_op.animate.set_value(0.0), run_time=0.5)
            after = self.t(frac_key, after)
            self.play_at(after, FadeIn(fr[k], shift=UP * 0.08, scale=1.2), run_time=0.3)

        # "take a moment to guess": the machine slows to a crawl by itself (ch2.clock); hold
        self.finish()
