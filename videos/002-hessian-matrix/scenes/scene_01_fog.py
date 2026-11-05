"""Scene 01 · Intro: the foggy mountain (0.000–28.167 s). Chapter 0 redesign.

"You're standing on a hill, in thick fog. The ground under your feet is perfectly
flat. No slope in any direction. So where are you? Maybe at the top of the hill.
Maybe at the bottom of a valley. Or somewhere stranger... a mountain pass, where the
ground rises ahead of you, and falls away on both sides. The slope can't tell you.
Here, the slope is zero. To know where you are, you need to know how the ground bends."

Visual argument: the viewer first sees the whole luminous range, then the fog rolls
in and shrinks the world to the walker's small circle: we become as blind as they
are. Under the still walker and its flat disc the ground becomes a summit, a basin,
a pass. Up close, in the fog, all three look the same (slope zero); pulling back,
the blue/orange bend tint is what tells them apart. No on-screen text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V

START, END = V.scene_range(1)


def probe_arrow(plate, direction, s: ValueTracker):
    """A short gold arrow from the walker along `direction`, lying on the ground."""
    d = np.array(direction, float)

    def make():
        k = s.get_value()
        if k < 0.03:
            return VMobject()
        a = plate.surface_point(0, 0, 0.02)
        b = plate.surface_point(*(0.95 * k * d), 0.02)
        return Arrow(a, b, buff=0, color=S.GRAD, stroke_width=4,
                     max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=10)
    return always_redraw(make)


class Scene01Fog(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        clk = ValueTracker(0.0)
        rig = V.intro_rig(clk, form=0.0, grid=0.35, **V.SPLAT_LOOK)
        self.run_clock(rig["time"], clk)
        plate = V.terrain_plate(rig, splats=V.SPLATS)
        self.add(plate, *rig.trackers())

        me = V.walker()
        V.set_walker_alpha(me, 0.0)
        V.pin(me, plate, V.on_surface(plate, 0, 0, 0.03))
        self.add(me)
        a = ValueTracker(0.0)
        me.add_updater(lambda m: V.set_walker_alpha(m, a.get_value()))
        self.add(a)

        # I-1 · a spiral galaxy of Gaussian splats hangs over the valley; it rains down
        # in a wave from the walker outward and every splat lands as a sliver of the
        # mountain range, while the camera descends to stand beside them. On "fog." the
        # fog rolls in (one move until "perfectly flat", each part on its own window of it)
        T1 = self.t("perfectly flat") - S.LEAD
        fog_at = (self.t("fog") - S.LEAD) / T1
        self.play(rig["opacity"].animate(rate_func=V.window(0.0, 0.1)).set_value(1.0),
                  rig["form"].animate(rate_func=V.window(0.12, 0.8)).set_value(1.0),
                  rig["reveal"].animate(rate_func=V.window(0.1, 0.8, rush_from)).set_value(60.0),
                  *[t.animate(rate_func=smooth).set_value(v) for t, v in
                    ((rig["dist"], 6.2), (rig["pitch"], 10.0), (rig["yaw"], 200.0),
                     (rig["target"][2], 0.7))],
                  a.animate(rate_func=V.window(0.22, 0.45)).set_value(1.0),
                  *[rig[k].animate(rate_func=V.window(fog_at, min(1.0, fog_at + 0.55))).set_value(v)
                    for k, v in (("fog", 0.34), ("fognear", 1.8), ("mist", 1.0), ("haze", 0.9))],
                  run_time=self.snap(T1))

        # I-2 · flat: the tangent disc, then four probes that find no slope
        self.beat("perfectly flat", *rig.to(disc_a=0.8, disc_r=V.DISC_R), rt=0.7)
        ks = [ValueTracker(0.0) for _ in range(4)]
        probes = [probe_arrow(plate, d, k) for d, k in zip(((1, 0), (0, 1), (-1, 0), (0, -1)), ks)]
        self.add(*probes, *ks)
        self.beat("no slope", LaggedStart(*[k.animate(rate_func=there_and_back).set_value(1.0) for k in ks],
                                          lag_ratio=0.15), rt=1.4, rate=linear)
        self.remove(*probes)

        # "where are you": a sonar ping leaves the walker and dies in the fog
        self.add(rig["ping_r"], rig["ping_a"])
        rig["ping_a"].set_value(1.0)
        self.play_at(self.t("where are you"), rig["ping_r"].animate(rate_func=rush_from).set_value(6.0),
                     rig["ping_a"].animate(rate_func=linear).set_value(0.0), run_time=1.8)

        # I-3 · the fog thins; the ground under the still disc becomes a summit, a basin, a pass
        self.beat("top of the hill", *rig.to(fog=0.16, fognear=2.4, haze=0.6, H=V.H_DOME, pitch=13.0), rt=0.9)
        self.beat("bottom of a valley", *rig.to(H=V.H_BOWL), rt=0.9)
        self.beat("mountain pass", *rig.to(H=V.H_SADDLE, fog=0.09, fognear=3.0, haze=0.4), rt=0.9)
        self.beat("rises ahead", *rig.to(fwd=1.0), rt=0.6)
        self.beat("falls away", *rig.to(side=1.0), rt=0.6)

        # I-4 · push in, fog closes: at this scale every shape looks the same
        self.beat("cant tell you", *rig.to(dist=2.8, pitch=32.0, fog=0.9, fognear=2.2, haze=0.9,
                                           contour=0.0, grid=0.4, fwd=0.0, side=0.0, target=(0.0, 0.0, 0.0)), rt=1.4)
        self.play(*rig.to(H=V.H_DOME), run_time=self.snap(0.6))
        self.play(*rig.to(H=V.H_BOWL), run_time=self.snap(0.6))
        self.beat("zero", *rig.to(H=V.H_SADDLE, gold=1.0), rt=0.6, after=22.0)

        # I-5 · pull back: the fog lifts and the bend tint shows how the ground bends
        e = V.S01_END
        self.beat("how the ground bends", *rig.to(**{k: e[k] for k in (
            "dist", "pitch", "yaw", "target", "fog", "fognear", "mist", "haze", "contour", "grid",
            "tint", "disc_a", "gold")}), rt=1.2)
        self.finish()
