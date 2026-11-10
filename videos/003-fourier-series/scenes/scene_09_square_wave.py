"""Scene 09 · Ch2: a square wave (168.800–186.217 s).

"Watch the top flatten out, and the sides get steeper. Here it is with ten circles...
fifty... two hundred. It's a square wave. Flat on top, flat on the bottom, with straight
walls in between. Smooth circles, adding up to sharp corners."

The answer to the guess. The chain hands over from Manim to the GPU EpicyclePlate as
circles keep arriving; the counter is locked to the spoken numbers (ch2.n_circles).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import Dot, FadeOut, ValueTracker, VGroup, VMobject, linear, there_and_back

from aion import style as S
import shared as V
import ch2 as C

START, END = V.scene_range(9)


class Scene09SquareWave(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        plate_op, count_op = ValueTracker(0.0), ValueTracker(0.0)
        self.add(plate_op, count_op)
        C.make_plate(self, plate_op)
        m = C.Stack(self, C.S08_END)
        fr = C.frac_labels(m)
        self.add(fr, C.counter(self, count_op))

        # the chain hands over to the plate while the strip starts to compress
        self.play(*m.to(rim_op=0.0, arm_op=0.0), plate_op.animate.set_value(1.0), FadeOut(fr),
                  run_time=self.snap(0.6))

        # "top flatten": circles keep arriving; the counter comes up
        self.beat("top flatten", count_op.animate.set_value(1.0), rt=1.0)

        # "square wave": the ideal square wave as a dashed ghost under the gold trace
        self.beat("square wave", *m.to(sq_op=1.0), rt=0.6)
        for key in ("tops", "bottoms", "walls"):
            word = {"tops": "flat on top", "bottoms": "flat on the bottom", "walls": "straight walls"}[key]
            self.beat(word, m.v[key].animate(rate_func=there_and_back).set_value(1.0), rt=0.8, rate=None)

        # "sharp corners": a light runs from the chain along the wave into a corner
        T = self.t("sharp corners") - S.LEAD
        u = ValueTracker(0.0)
        self.add(u)
        tau_c = None

        def spark():
            nonlocal tau_c
            v = u.get_value()
            if v <= 0 or v >= 1:
                return VMobject()
            c = C.clock(self.now)
            if tau_c is None:          # the first corner past the middle of the screen, fixed in wave time
                xs = np.linspace(1.5, C.X_END - 0.5, 2000)
                y = C.ideal_square(C.theta_tau(c - (xs - C.X0) / C.V_SCROLL))
                j = np.nonzero(np.diff(y) != 0)[0][0]
                tau_c = c - (xs[j] - C.X0) / C.V_SCROLL
            xc = C.X0 + (c - tau_c) * C.V_SCROLL
            x = C.X0 + v * (xc - C.X0)
            y = C.square_sum(np.array([C.theta_tau(c - (x - C.X0) / C.V_SCROLL)]), C.amps(self.now))[0]
            fade = np.sin(np.pi * v) ** 0.5
            return VGroup(Dot([x, y, 0], radius=0.3, color=S.LABEL).set_opacity(0.18 * fade),
                          Dot([x, y, 0], radius=0.09, color=S.LABEL).set_opacity(0.95 * fade))
        self.add(V.redraw(spark))
        self.play_at(T + S.LEAD, u.animate.set_value(0.999), run_time=0.9, rate_func=linear)
        self.finish()
