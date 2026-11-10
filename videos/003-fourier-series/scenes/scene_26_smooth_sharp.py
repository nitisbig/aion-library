"""Scene 26 · Ch6: why sharp corners are expensive (516.983–540.800 s).

"Remember how I said sharp corners are expensive? Smooth curves come from the first few
circles. Sharp turns need all the rest. When the pen jumps, like in the square wave, the
circles shrink slowly. One third, one fifth. When the pen only turns a corner, like our
square, they shrink much faster. One ninth, one twenty fifth. The smoother the shape, the
fewer circles it takes."

Pays off S10's red corner marker. The 20-circle clef is compared point by point (same t)
with the 200-circle one: within EPS it lights, beyond it flashes red. The panels' bars are
computed: square wave 4/(πn) → 1/n, the intro square's own cₙ/c₁ → 1/n², a 3-circle oval.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (UP, Create, FadeIn, FadeOut, LaggedStart, ValueTracker, VGroup, VMobject, there_and_back)

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch6 as C
import scene_25_converge as S25

START, END = V.scene_range(26)
N_FEW, EPS = 20, 0.12
MARK_AT = np.array([0.0, 3.2, 0.0])


def runs(mask: np.ndarray, z: np.ndarray) -> list:
    """Contiguous stretches of z where mask holds (as point arrays)."""
    out, i = [], 0
    while i < len(z):
        if mask[i]:
            j = i
            while j < len(z) and mask[j]:
                j += 1
            if j - i > 2:
                out.append(z[max(0, i - 1): j + 1])
            i = j
        else:
            i += 1
    return out


def few_split():
    t = np.linspace(0, 1, 3000)
    z10, z200 = C.clef_z(t, N_FEW), C.clef_z(t, 200)
    near = np.abs(z10 - z200) < EPS
    return z10, runs(near, z10), runs(~near, z10)


class Scene26SmoothSharp(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        marker = C2.corner_marker()
        eb = V.eyebrow("06 · DRAWING ANYTHING")
        self.add(marker, eb)
        po = ValueTracker(1.0)
        self.add(po)
        self.add(V.EpicyclePlate(lambda: C.s25_state(self.now, opacity=po.get_value())))
        co = ValueTracker(1.0)
        self.add(co)
        self.add(V.redraw(lambda: S25.counter(self.now, co.get_value())))
        self.bring_to_front(marker)

        # "remember": the red corner marker pulses and flies to the top center
        self.beat("remember", marker.animate.scale(1.5).move_to(MARK_AT), co.animate.set_value(0.0),
                  rt=0.8)

        # "smooth curves": the 200-circle chain fades; the 20-circle clef in gold over the true outline
        z10, near, far = few_split()
        outline = C.clef_outline(0.3)
        few = C4.path(np.append(z10, z10[0]), S.INK, 2.5, 0.55)
        self.beat("smooth curves", po.animate.set_value(0.0), FadeIn(outline), FadeIn(few), rt=0.9)

        # "first few circles": where it already matches, it lights; "all the rest": the sharp turns flash red
        lit = VGroup(*[C4.path(r, S.INK, 5.0, 1.0) for r in near])
        red = VGroup(*[C4.path(r, S.SPIKE, 5.0, 1.0) for r in far])
        self.beat("first few circles", Create(lit, lag_ratio=0.0), rt=1.0)
        self.beat("all the rest", FadeIn(red), rt=0.4)
        self.play(red.animate(rate_func=there_and_back).set_stroke(width=8), run_time=self.snap(0.6))

        # "pen jumps": the clef clears; the square wave panel and its strip (1/n)
        bars = [C.panel_bars(i) for i in range(3)]
        labels = [C.panel_labels(i) for i in range(3)]

        def show_panel(i):
            return (FadeIn(C.panel_drawing(i), shift=UP * 0.1), FadeIn(C.panel_axis(C.PANEL_X[i])),
                    LaggedStart(*[Create(b) for b in bars[i]], lag_ratio=0.15))
        self.beat("pen jumps", FadeOut(VGroup(outline, few, lit, red)), *show_panel(0), rt=1.2)

        # "one third", "one fifth"
        self.beat("one third", FadeIn(labels[0][0], shift=UP * 0.08), rt=0.4)
        self.beat("one fifth", FadeIn(labels[0][1], shift=UP * 0.08), rt=0.4)

        # "turns a corner": the square loop and its strip (1/n²): visibly faster
        self.beat("turns a corner", *show_panel(1), rt=1.2)
        self.beat("one ninth", FadeIn(labels[1][0], shift=UP * 0.08), rt=0.4)
        self.beat("one twenty fifth", FadeIn(labels[1][1], shift=UP * 0.08), rt=0.4)

        # "fewer circles": a smooth oval with only 3 bars; the red marker dissolves (promise kept)
        self.beat("fewer circles", *show_panel(2), FadeOut(marker, scale=0.6), rt=1.0)
        self.finish()


def end_picture() -> VGroup:
    """S26's last picture (S27 starts from it): the three panels."""
    return VGroup(*[C.panel(i) for i in range(3)])
