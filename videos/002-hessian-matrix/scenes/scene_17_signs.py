"""Scene 17 · Ch5: read the signs (392.967–413.117 s).

"Now we can answer the question from the foggy hill. At a flat point, look at the two
eigenvalues. Both positive, the surface smiles in every direction. A valley, a local
minimum. Both negative, it frowns in every direction. A peak, a local maximum. One of
each, it smiles one way and frowns the other. A saddle."

A short return to the intro: the walker on its flat disc in the fog. The fog clears
into the sign chart: the λ₁–λ₂ plane, the walker as the point (λ₁, λ₂), and a mini
surface with H = diag(λ₁, λ₂) ringed by live bend gauges (λ₁cos²φ + λ₂sin²φ).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V
import ch4 as C4
import ch5 as C

START, END = V.scene_range(17)
FOG = dict(H=(0.0, 0.0, 0.0), reveal=60.0, dist=6.2, pitch=10.0, yaw=200.0, target=(0.0, 0.0, 0.7),
           fog=0.34, fognear=1.8, mist=1.0, haze=0.9, disc_r=V.DISC_R, disc_a=0.8)


class Scene17Signs(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 16's last frame ──
        e = C4.s16_end()
        self.add(e["plate"], *e["land"].trackers(), e["a"], e["b"], e["patch"], e["taylor"],
                 e["card"], e["cosc"], e["par"], e["glow"])

        # 5-1 · back to the foggy hill: the walker on its flat disc
        clk = ValueTracker(0.0)
        fog = V.intro_rig(clk, **FOG, opacity=0.0)
        self.run_clock(fog["time"], clk)
        fplate = V.terrain_plate(fog)
        self.add(fplate, *fog.trackers())
        me = V.walker()
        V.pin(me, fplate, V.on_surface(fplate, 0, 0, 0.03))
        a = ValueTracker(0.0)
        me.add_updater(lambda m: V.set_walker_alpha(m, a.get_value()))
        self.add(me, a)
        e["patch"].clear_updaters()
        self.beat("answer the question", *e["land"].to(opacity=0.0), *fog.to(opacity=1.0), a.animate.set_value(1.0),
                  FadeOut(e["patch"]), FadeOut(e["taylor"]), FadeOut(e["card"]), FadeOut(e["cosc"]),
                  FadeOut(e["par"]), FadeOut(e["glow"]), rt=1.0)
        self.remove(e["plate"])

        # 5-2 · the fog clears into the sign chart; the walker becomes the point (λ₁, λ₂)
        ax = C.chart()
        labels = C.chart_labels(ax)
        l1, l2 = ValueTracker(0.0), ValueTracker(0.0)
        dot = C.chart_dot(ax, l1, l2)
        rig = C.mini_rig(l1, l2)
        plate = rig.plate(**C.MINI)
        self.add(plate, *rig.trackers(), l1, l2)
        me.clear_updaters()
        self.beat("two eigenvalues", *fog.to(opacity=0.0), *rig.to(opacity=1.0), FadeIn(ax), FadeIn(labels),
                  Transform(me, dot), rt=1.2, after=395.0)
        self.remove(fplate, me)
        self.add(dot)
        gauges, ks = C.ring(plate, l1, l2)
        self.add(*ks)

        # 5-3 · both positive: a valley
        q = {n: C.quadrant(ax, n) for n in (1, 2, 3, 4)}
        lab = {n: C.q_label(ax, n) for n in (1, 2, 3, 4)}
        self.add(*q.values())
        for g in q.values():
            g.set_opacity(0)
        self.bring_to_front(ax, dot)
        self.beat("both positive", l1.animate.set_value(2.0), l2.animate.set_value(2.0),
                  q[1].animate.set_fill(opacity=0.13), rt=1.0)
        self.beat("every direction", LaggedStart(*[FadeIn(g, scale=0.5) for g in gauges], lag_ratio=0.08), rt=0.7)
        self.beat("local minimum", FadeIn(lab[1], shift=UP * 0.1), rt=0.5)

        # 5-4 · both negative: a peak
        self.beat("both negative", l1.animate.set_value(-2.0), l2.animate.set_value(-2.0),
                  q[3].animate.set_fill(opacity=0.13), rt=1.2)
        self.beat("local maximum", FadeIn(lab[3], shift=UP * 0.1), rt=0.5)

        # 5-5 · one of each: a saddle, in both mixed quadrants
        self.beat("one of each", l1.animate.set_value(2.0), l2.animate.set_value(-2.0),
                  q[4].animate.set_fill(opacity=0.13), rt=0.8)
        self.play(l1.animate.set_value(-2.0), l2.animate.set_value(2.0), q[2].animate.set_fill(opacity=0.13),
                  run_time=self.snap(1.0))
        self.beat("saddle", FadeIn(lab[2], shift=UP * 0.1), FadeIn(lab[4], shift=UP * 0.1), rt=0.4, after=412.0)
        self.finish()
