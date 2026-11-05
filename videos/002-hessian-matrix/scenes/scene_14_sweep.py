"""Scene 14 · Ch4: the sweep ★ (325.717–354.267 s).

"Let's watch it on the puzzle surface. Facing east, the bending is two. A smile. Now
slowly turn. Toward the northeast, the bending grows. Three, four. At 45 degrees, it
reaches five. The strongest smile on the surface. Keep turning, the bending falls. Back
to two, facing north. And it keeps falling through zero and past it. Facing northwest,
the bending is minus one, a frown."

Left: the puzzle surface with a vertical slice plane at θ through the centre; its cut
curve is tinted by the sign of the bending. Right: uᵀHu = 2 + 3 sin 2θ traced live.
Under the surface: a compass dial, the bend gauge and the readout. θ(t) passes through
the narration's keyframes exactly (bend 3, 4, 5, 2, 0, −1 on the words; ch4 asserts
the angles) on a monotone cubic, so it never overshoots and holds still at 45°.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *
from scipy.interpolate import PchipInterpolator

from aion import style as S
import shared as V
import ch4 as C
from beats import THETA, THETA_ZERO

START, END = V.scene_range(14)


class Scene14Sweep(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 13's last frame ──
        e = C.s13_end()
        hu = e["hu"]
        left = VGroup(e["mat"], e["e0"], e["e1"], e["e2"], e["gauge"], e["bnd"])
        mapped = VGroup(e["u"], e["ulab"], e["circ"], e["nl"], *hu)
        self.add(e["plate"], *e["rig"].trackers(), e["th"], e["circ"], e["nl"], *hu, e["u"], e["ulab"],
                 e["mat"], e["e0"], e["e1"], e["e2"], e["gauge"], e["card"], e["bnd"])

        # 4-3 · the new layout: the surface with a turning slice (left), the bending graph (right)
        th, sp = ValueTracker(0.0), ValueTracker(1.0)
        k = ValueTracker(C.bend(0.0))
        k.add_updater(lambda m: m.set_value(C.bend(th.get_value())))
        rig = C.sweep_rig(th, sp, opacity=0.0)
        plate = rig.plate(**C.SWEEP)
        self.add(plate, *rig.trackers(), th, sp, k)
        ax = C.sweep_axes()
        labels = C.sweep_labels(ax)
        ring, arrow = C.dial(th)
        for m in mapped:
            m.clear_updaters()
        self.beat("watch it on the puzzle surface", FadeOut(left), FadeOut(e["card"]), FadeOut(mapped),
                  *e["rig"].to(opacity=0.0), *rig.to(opacity=1.0),
                  FadeIn(ax), FadeIn(labels), FadeIn(ring), FadeIn(arrow), rt=1.2)
        self.remove(e["plate"])

        trace, dot = C.sweep_trace(ax, th), C.sweep_dot(ax, th)
        self.add(trace)
        self.beat("facing east", FadeIn(dot, scale=0.5), rt=0.5, after=327.5)
        read = C.sweep_readout(th)
        self.beat("two", FadeIn(read, shift=UP * 0.1), rt=0.3, after=329.5)
        gauge = C.sweep_gauge(k)
        self.beat("smile", GrowFromCenter(gauge), rt=0.4, after=330.4)

        # 4-4 / 4-5 · θ(t): through every number on its word, holding at 45°
        key = lambda w, after=None, lead=0.1: self.t(w, after) - lead
        knots = [(key("slowly turn", lead=0.15), 0.0), (key("three", 335.5), THETA["3"]),
                 (key("four", 336.5), THETA["4"]), (key("five", 339.5), 45.0),
                 (key("keep turning", lead=0.15), 45.0), (key("two", 345.0), 90.0),
                 (key("zero", 348.8), THETA_ZERO), (key("northwest"), 135.0)]
        ts, vs = zip(*knots)
        assert all(b > a for a, b in zip(ts, ts[1:])), knots
        # sampled into plain arrays: Manim's cache hashes updater closures, and can't hash scipy objects
        TT = np.linspace(ts[0], ts[-1], 4000)
        VV = PchipInterpolator(ts, vs)(TT)
        th.add_updater(lambda m: m.set_value(float(np.interp(self.now, TT, VV))))

        self.beat("northeast", FadeIn(C.dial_tag("NE", 45)), rt=0.4)
        peak = C.peak_ring(ax)
        self.beat("five", Create(peak), rt=0.4, after=339.5)
        self.beat("strongest smile", peak.animate(rate_func=there_and_back).scale(1.6).set_stroke(width=4), rt=0.6)
        formula = C.sweep_formula(ax)
        self.beat("past it", Write(formula), rt=0.8)
        self.beat("northwest", FadeIn(C.dial_tag("NW", 135)), rt=0.4)
        self.beat("frown", gauge.animate(rate_func=there_and_back).scale(1.25), rt=0.5, after=353.5)
        th.clear_updaters()                      # θ has been clamped at 135° since "northwest"
        th.set_value(135.0)
        self.finish()
