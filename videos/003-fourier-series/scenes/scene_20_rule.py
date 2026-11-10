"""Scene 20 · Ch5: spin averages to zero (382.017–389.317 s).

"That gives us the key idea. Things that spin average out to zero. Things that stand still
don't."

Two icons, then they shrink into the rule card docked top-left for the rest of Ch5.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import ValueTracker, VGroup

import shared as V
import ch2 as C2
import ch5 as C
import scene_19_balance as S19

START, END = V.scene_range(20)


class Scene20Rule(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        items = S19.lit_rack()
        eb = V.eyebrow("05 · SPIN AND AVERAGE")
        op19 = ValueTracker(1.0)
        self.add(op19, VGroup(*items.values()), eb, C2.corner_marker(), S19.end_layer(self, op19))

        # "key idea": the stage clears
        self.beat("key idea", op19.animate.set_value(0.0), rt=0.5)

        tk = {k: ValueTracker(0.0) for k in ("l", "r", "u")}
        self.add(*tk.values())
        self.add(V.redraw(lambda: C.card_lerp(self.now, tk["u"].get_value(), left=tk["l"].get_value(),
                                              right=tk["r"].get_value())))

        # "things that spin": a spinning arm whose dots average to its center (grey)
        self.beat("things that spin", tk["l"].animate.set_value(1.0), rt=0.6)
        # "stand still": a still arm whose dots all sit at its tip (green)
        self.beat("stand still", tk["r"].animate.set_value(1.0), rt=0.6)
        # "don't": both shrink into the rule card, docked top-left
        self.beat("don't", tk["u"].animate.set_value(1.0), rt=0.6)
        self.finish()
