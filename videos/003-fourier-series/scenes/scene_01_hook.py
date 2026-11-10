"""Scene 01 · Intro: what you're looking at (0.000–13.283 s).

"What you're looking at is a chain of circles. Each one rides on the edge of the one
before, spinning at its own steady speed. Follow the tip of the very last circle, and
it draws a treble clef."

The finished picture first: the 201-circle clef chain (the same coefficients S24–S25
compute and S30 replays) is already turning as the video opens. One loop takes the
whole scene, so the clef is ~90 % drawn on "clef" and closes in the pause, at the cut.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, FadeIn, FadeOut, LaggedStart, MathTex, ReplacementTransform, ValueTracker, VGroup,
                   linear, smooth, there_and_back)

from aion import style as S
import shared as V
from aion.components.term_label import exp_part

START, END = V.scene_range(1)


class Scene01Hook(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        t = self.drive(ValueTracker(0.0), lambda now: (now - START) / V.LOOP_S01)
        op, zoom, focus = ValueTracker(0.0), ValueTracker(0.93), ValueTracker(0.0)
        sweep, rims = ValueTracker(-1.0), ValueTracker(1.0)
        pen, sparks, bloom = ValueTracker(0.45), ValueTracker(0.0), ValueTracker(0.7)

        def state():
            s = V.clef_state(t.get_value(), opacity=op.get_value(), rim_vivid=1.0, rim_alpha=rims.get_value(),
                             pen_glow=V.S01_END["pen_glow"], pen_alpha=pen.get_value(), sparks=sparks.get_value(),
                             bloom=bloom.get_value(),
                             sweep=sweep.get_value() if sweep.get_value() >= 0 else None)
            f = focus.get_value()
            if f > 0:                       # follow joint 3 (a circle riding the rim of the one before)
                j = plate.joints(s)[2]
                s["cam"] = f * j
            s["zoom"] = zoom.get_value() * (1 + 1.6 * f)
            return s

        plate = V.EpicyclePlate(state)
        self.add(plate, op, zoom, focus, sweep, rims, pen, sparks, bloom)

        # each of the three biggest circles carries its term (pinned to the GL rims)
        lab = ValueTracker(0.0)
        self.add(lab)
        self.add(V.redraw(lambda: V.plate_labels(plate, plate.state(), V.clef_terms(), 3, lab.get_value(), size=30, vivid=True)))

        # frame 0: fade up on a chain already in motion; a slow drift in for the whole scene
        self.play(op.animate.set_value(1.0), zoom.animate(rate_func=linear).set_value(0.945),
                  run_time=self.snap(0.4), rate_func=smooth)
        zoom.add_updater(lambda m, dt: m.set_value(0.945 + 0.055 * smooth(min(1.0, (self.now - 0.4) / (END - 0.4)))))

        # "chain of circles": a light sweep runs from the root joint to the pen; the three biggest
        # circles show their terms, and keep them until the clef is named
        self.beat("chain of circles", sweep.animate.set_value(1.0), lab.animate(rate_func=smooth).set_value(1.0),
                  rt=1.2, rate=linear)
        sweep.set_value(-1.0)

        # "edge of the one before": the camera follows one circle riding the rim of the one before
        self.beat("edge of the one before", focus.animate.set_value(1.0), rt=1.0)
        self.play(focus.animate.set_value(0.0), run_time=self.snap(0.8), rate_func=smooth)

        # "own steady speed": every rim brightens once
        self.beat("own steady speed", rims.animate(rate_func=there_and_back).set_value(1.6), rt=0.8)

        # "very last circle": the pen ignites
        self.beat("very last circle", pen.animate.set_value(1.0), sparks.animate.set_value(1.0),
                  bloom.animate.set_value(V.S01_END["bloom"]), rt=0.8)

        # "treble clef": the labels step back so the drawing reads alone
        self.beat("treble clef", lab.animate.set_value(0.0), rt=0.6)

        # the loop closes at the cut (t = 1 exactly on the last frame)
        self.finish()
        self.handoff = {"plate": plate}
