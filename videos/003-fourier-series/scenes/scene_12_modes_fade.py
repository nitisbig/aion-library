"""Scene 12 · Ch3: wigglier waves fade faster (228.117–256.167 s).

"Fourier's move was to break the temperature into simple waves. One that goes around the
ring once, one that goes around three times, then five, and so on. Each of those waves
does something very simple. It keeps its shape, and it just fades. And the wigglier the
wave, the faster it fades. Three times the wiggles, nine times as fast. So the sharp edges
melt away first, the ring settles into one gentle wave, and then into an even warmth."

Exact heat on a ring: mode n decays as e^{−n² τ}. Two heat clocks (the three small mode
rings start on "keeps its shape", the main ring on "sharp edges melt"), each an
exponential ramp so the fast modes are seen to fade before they vanish.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Axes, Create, FadeIn, FadeOut, MathTex, ValueTracker, VGroup,
                   there_and_back)

from aion import style as S
import shared as V
import ch2 as C2
import ch3 as H

START, END = V.scene_range(12)
MAIN_AT = np.array([-3.2, 0.0, 0.0])
SMALL_AT = [np.array([3.6, 0.0, z]) for z in (1.9, 0.0, -1.9)]
SMALL_SCALE = 0.55
SMALL_GAIN = 2.2      # one display gain for all three crowns: their 1 : 1/3 : 1/5 heights stay true
NS = (1, 3, 5)


def tau_ramp(t, t0, a, T):
    return 0.0 if t <= t0 else a * (np.exp((t - t0) / T) - 1)


def modes_state(now, T_keep, T_melt, sp, dist, ghost=0.0, pulses=(0.0, 0.0, 0.0), op=1.0) -> dict:
    """MeshPlate state: the main ring (heat clock from T_melt) and the three mode rings (from T_keep)."""
    tau_m = tau_ramp(now, T_melt, 0.077, 1.8)
    tau_s = tau_ramp(now, T_keep, 0.0645, 4.0)
    meshes, glass = H.ring_parts(H.modes(H.PSI, tau_m), center=sp * MAIN_AT, crown=1.0,
                                 ghost_u=H.modes(H.PSI, tau_m, only=1), ghost_op=ghost)
    if sp > 0:
        for k, (n, at) in enumerate(zip(NS, SMALL_AT)):
            u = H.modes(H.PSI, tau_s, only=n)
            m, g = H.ring_parts(u, center=sp * at + (1 - sp) * MAIN_AT * sp, scale=SMALL_SCALE * sp, crown=1.0,
                                gain=SMALL_GAIN, heat_vis=1.0 + 1.5 * pulses[k])
            meshes += m
            glass += g
    return {**H.CAM, "dist": dist, "meshes": meshes, "glass": glass, "opacity": op}


def end_state(now, op=1.0) -> dict:
    """S12's last picture (the S13 hand-off), at any later time `now`."""
    from aion.sync import Cue
    cue = Cue.load(V.SRT)
    keep = cue.at("keeps its shape", after=START - 0.05) - S.LEAD
    melt = cue.at("sharp edges melt", after=START - 0.05) - S.LEAD
    return modes_state(now, keep, melt, 1.0, 9.6, op=op)


class Scene12ModesFade(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        L = S.LEAD
        T_keep = self.t("keeps its shape") - L
        T_melt = self.t("sharp edges melt") - L
        split = ValueTracker(0.0)
        dist = ValueTracker(7.6)
        pulse = [ValueTracker(0.0) for _ in NS]
        ghost = ValueTracker(0.0)
        self.add(split, dist, ghost, *pulse)

        def state():
            return modes_state(self.now, T_keep, T_melt, split.get_value(), dist.get_value(),
                               ghost.get_value(), [p.get_value() for p in pulse])

        plate = H.MeshPlate(state)
        self.add(plate, C2.corner_marker())             # the red marker stays until S26

        # "simple waves": the main ring steps left, three small rings split out with modes 1, 3, 5
        self.beat("simple waves", split.animate.set_value(1.0), dist.animate.set_value(9.6), rt=1.0)
        labels = VGroup(*[MathTex(str(n), font_size=40, color=S.FWD).move_to(
            plate.project(*(at + np.array([-1.0, 0, 0.3]))) ) for n, at in zip(NS, SMALL_AT)])

        # "once", "three times", "five": each small ring pulses as its number is said
        after = self.t("simple waves")
        for k, key in enumerate(("once", "three times", "five")):
            after = self.t(key, after)
            self.play_at(after, pulse[k].animate(rate_func=there_and_back).set_value(1.0),
                         FadeIn(labels[k], shift=RIGHT * 0.1), run_time=0.5)

        # "keeps its shape": heat-time starts for the small rings (ch3.modes, exact decay)
        # "nine times as fast": the two decays, computed
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 1, 1], x_length=3.4, y_length=1.4, tips=False,
                  axis_config={"stroke_color": S.ARM, "stroke_width": 1.5, "stroke_opacity": 0.6,
                               "include_ticks": False}).move_to([0.2, -2.55, 0])
        slow = ax.plot(lambda t: np.exp(-t), x_range=[0, 3, 0.02], color=S.INK, stroke_width=3)
        fast = ax.plot(lambda t: np.exp(-9 * t), x_range=[0, 3, 0.005], color=S.INK, stroke_width=3)
        l1 = MathTex(r"e^{-t}", font_size=30, color=S.INK).next_to(ax.c2p(1.6, np.exp(-1.6)), UP, buff=0.12)
        l9 = MathTex(r"e^{-9t}", font_size=30, color=S.INK).next_to(ax.c2p(0.12, np.exp(-1.08)), RIGHT, buff=0.15)
        l9 = VGroup(l9, MathTex(r"\times 9", font_size=30, color=S.LABEL).next_to(l9, RIGHT, buff=0.2))
        self.beat("nine times as fast", Create(ax), Create(slow), Create(fast), FadeIn(l1), FadeIn(l9), rt=0.8)

        # "sharp edges melt": the main ring's heat-time starts by itself (ch3 tau ramp)
        # "one gentle wave": a ghost of the pure one-wave crown lies on it: a match
        self.beat("one gentle wave", ghost.animate.set_value(1.0), rt=0.6)

        # "even warmth": everything flattens to one mid-tone (exact decay); the overlays leave
        self.beat("even warmth", ghost.animate.set_value(0.0), FadeOut(VGroup(ax, slow, fast, l1, l9, labels)),
                  rt=1.2)
        self.finish()
