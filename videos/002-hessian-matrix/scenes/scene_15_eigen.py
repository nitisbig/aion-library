"""Scene 15 · Ch4: the frown was hiding in between (354.267–374.900 s).

"So the surface smiles along one diagonal and frowns along the other. It's a saddle.
The east and north slices showed us two smiles. The frown was hiding in between. Those
two special directions are always at right angles. They're called the eigenvectors of
the Hessian. And the bending along them, five and minus one, are its eigenvalues."

The turning slice stops on the frown diagonal (1,−1) and stays; the smile diagonal (1,1)
joins it in blue. The camera shows the saddle with its bend tint; the east and north
slices smile again (f_xx = f_yy = 2); then the intro's ball rolls down the frown line,
which solves the intro puzzle. Top-down: the two directions meet at a right angle
(V1·V2 = 0), and a small legend names them: v₁, λ₁ = 5 and v₂, λ₂ = −1 (ch4 asserts
Hv₁ = 5v₁, Hv₂ = −v₂).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.bend_gauge import BendGauge
import shared as V
import ch4 as C

START, END = V.scene_range(15)
NW = C.V2                                            # down the frown line, as in the intro


class Scene15Eigen(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 14's last frame ──
        e = C.s14_end()
        th, sp = e["th"], e["sp"]
        d1, xs, ys = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        rig = C.sweep_rig(th, sp, d1=d1, xs=xs, ys=ys)
        plate = rig.plate(**C.SWEEP)
        graph = VGroup(e["ax"], e["labels"], e["trace"], e["dot"], e["peak"], e["formula"])
        under = VGroup(e["ring"], e["arrow"], e["tags"], e["gauge"], e["read"])
        self.add(plate, *rig.trackers(), th, sp, d1, xs, ys, e["k"], graph, under)

        # 4-6 · the frown stays where the sweep stopped; the smile diagonal joins it
        for m in (*graph, *under):
            m.clear_updaters()
        self.beat("smiles along one diagonal", FadeOut(graph), FadeOut(under), sp.animate.set_value(0.0),
                  d1.animate.set_value(1.0), rt=0.8)
        self.beat("frowns along the other", sp.animate(rate_func=there_and_back).set_value(0.8), rt=0.8)
        self.beat("its a saddle", *rig.to(**C.SADDLE_VIEW), rt=1.2)

        # the east and north slices: two smiles
        gx = BendGauge(2.0, width=0.75, stroke=6)
        gx.add_updater(lambda m: m.place(plate.surface_point(C.GAUGE_AT, 0.0) + UP * 0.5))
        gy = BendGauge(2.0, width=0.75, stroke=6)
        gy.add_updater(lambda m: m.place(plate.surface_point(0.0, C.GAUGE_AT) + UP * 0.5))
        self.beat("east and north slices", xs.animate.set_value(1.0), ys.animate.set_value(1.0),
                  FadeIn(gx, scale=0.6), FadeIn(gy, scale=0.6), rt=0.6)

        # the frown was hiding in between: the intro's ball rolls down it
        roll = ValueTracker(0.0)
        ball = V.walker()
        V.pin(ball, plate, V.on_surface(plate, lambda: roll.get_value() * NW[0],
                                        lambda: roll.get_value() * NW[1], 0.03))
        trail = always_redraw(lambda: VMobject().set_points_smoothly(
            [plate.surface_point(*(r * NW), 0.03) for r in np.linspace(0, max(roll.get_value(), 1e-3), 24)]
        ).set_stroke(S.GRAD, 3, opacity=0.75) if roll.get_value() > 0.02 else VMobject())
        ball.add_updater(lambda m: V.set_walker_alpha(m, float(np.clip((2.2 - roll.get_value()) / 0.5, 0, 1))))
        self.add(roll, trail)
        self.beat("hiding in between", xs.animate.set_value(0.0), ys.animate.set_value(0.0),
                  FadeOut(gx), FadeOut(gy), FadeIn(ball, scale=0.5), rt=0.5)
        self.play(roll.animate.set_value(2.3), run_time=self.snap(2.0), rate_func=rush_into)
        self.remove(ball)

        # 4-7 · top-down: the two directions meet at a right angle; name them
        trail.clear_updaters()
        self.beat("right angles", *rig.to(**C.TOP_VIEW), FadeOut(trail), rt=1.2)
        ra = C.right_angle(plate)
        self.play(Create(ra), run_time=self.snap(0.4))
        rows, ev, ew = C.legend()
        self.beat("eigenvectors", FadeIn(ev, shift=DOWN * 0.1),
                  LaggedStart(*[FadeIn(VGroup(r[0], r[1]), shift=LEFT * 0.15) for r in rows], lag_ratio=0.3), rt=0.7)
        self.beat("five and minus one", LaggedStart(*[FadeIn(r[2], shift=LEFT * 0.15) for r in rows],
                                                    lag_ratio=0.4), rt=0.7)
        self.beat("eigenvalues", FadeIn(ew, shift=DOWN * 0.1), rt=0.5, after=373.5)
        self.finish()
