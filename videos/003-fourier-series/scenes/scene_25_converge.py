"""Scene 25 · Ch6: one, five, twenty, two hundred (501.733–516.983 s).

"With one circle, we get a loop. With five, a rough blob. By twenty, you can start to see it.
And with two hundred, the circles trace the clef almost perfectly. Up close, even the tiniest
circles are adding detail the others can't."

The clef chain (ch6.clef_terms, biggest first) on the EpicyclePlate. The counter, loop clock,
zoom and camera are pure functions of time in ch6 (n_circles, loop_clock, zoom_amount), so
S24's last frame and S26's first match by construction. Each finished level stays behind as
a faint silver ghost; at two hundred the true outline sits under the ink.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import FadeIn, FadeOut, Integer, UP, ValueTracker, VGroup, VMobject

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch6 as C

START, END = V.scene_range(25)
COUNTER_AT = np.array([4.2, 0.55, 0.0])


def level_path(n: int, op: float):
    z = C.clef_z(np.linspace(0, 1, 2500), n)
    return C4.path(np.append(z, z[0]), S.ARM, 2.0, op)


def counter(now: float, op: float = 1.0) -> VGroup:
    if op <= 0:
        return VGroup()
    n = C.n_circles(now)
    num = Integer(n, font_size=96, color=S.LABEL if n != 150 else S.LABEL_MUTED).move_to(COUNTER_AT)
    word = V.label("circle" if n == 1 else "circles", 28, S.LABEL_MUTED).next_to(num, np.array([0, -1, 0]), buff=0.18)
    return VGroup(num, word).set_opacity(op)


class Scene25Converge(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        rec = V.recipe(40, muted=False).move_to(V.RECIPE_POS)
        self.add(C2.corner_marker(), V.eyebrow("06 · DRAWING ANYTHING"), rec)
        self.add(V.EpicyclePlate(lambda: C.s25_state(self.now)))
        T = C.s25_times()

        # the counter is locked to the spoken numbers (ch6.n_circles); it fades in on "one circle"
        co = ValueTracker(0.0)
        self.add(co)
        self.add(V.redraw(lambda: counter(self.now, co.get_value())))

        # each finished level leaves a faint silver ghost; at "two hundred" the true outline replaces them
        g = {k: ValueTracker(0.0) for k in (1, 5, 20, 200)}
        self.add(*g.values())
        self.add(V.redraw(lambda: VGroup(*[level_path(n, 0.3 * t.get_value()) if n < 200 else
                                          C.clef_outline(0.3 * t.get_value())
                                          for n, t in g.items() if t.get_value() > 0])))

        self.play_at(T["one"], co.animate.set_value(1.0), lead=0, run_time=0.4)
        self.play_at(T["five"], g[1].animate.set_value(1.0), lead=0, run_time=0.4)
        self.play_at(T["twenty"], g[1].animate.set_value(0.0), g[5].animate.set_value(1.0), lead=0, run_time=0.4)
        self.play_at(T["two"], g[5].animate.set_value(0.0), g[20].animate.set_value(1.0), lead=0, run_time=0.4)
        self.play_at(T["two"] + 1.0, g[20].animate.set_value(0.0), g[200].animate.set_value(1.0), lead=0, run_time=0.8)

        # "up close": the ghost and the recipe go first; the plate dives 40× onto the pen (ch6.zoom_amount)
        self.play_at(T["close"] - 0.3, g[200].animate.set_value(0.0), FadeOut(rec), lead=0, run_time=0.4)
        self.finish()
