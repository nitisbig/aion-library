"""Scene 13 · Ch4: bending in any direction (303.700–325.717 s).

"A surface can bend in any direction, not just east or north. So what about the
directions in between? Here's the beautiful part. You don't need any new derivatives.
Pick a direction as a little arrow of length one. Multiply the Hessian by that arrow.
Then take the dot product with the same arrow again. The number that comes out is the
bending in that direction."

No cut from scene 12: the flashback plate tilts up into a top-down contour map of the
puzzle surface and the Hessian parks top-left. A unit arrow u turns on the map. The
worked example u = east: Hu = (2, 3) (the first column), uᵀ(Hu) = 2, the shadow of Hu
on u is exactly 2u, and 2 is the bending east (a smile). All values asserted in ch4.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V
import ch3 as L3
import ch4 as C

START, END = V.scene_range(13)
NW = np.array([-1.0, 1.0]) / np.sqrt(2)


class Scene13Direction(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 12's last frame: the numeric Hessian with its halo, f, the puzzle plate, the ball ──
        mat, grid, nums, halo = L3.s12_end()
        f = L3.puzzle_f()
        rig = V.puzzle_rig(opacity=0.8, **L3.PUZZLE_KW)
        plate = rig.plate(**C.MAP)
        ball = V.walker()
        V.pin(ball, plate, V.on_surface(plate, 1.5 * NW[0], 1.5 * NW[1], 0.03))
        self.add(plate, *rig.trackers(), halo, mat, f, ball)

        # 4-1 · the plate becomes a top-down map; a unit arrow turns on it
        th = ValueTracker(40.0)
        u = C.vec_arrow(plate, lambda: C.unit(th.get_value()))
        ulab = C.tip_label(plate, "u", lambda: C.unit(th.get_value()))
        self.add(th)
        self.beat("any direction", FadeOut(f), FadeOut(ball), FadeOut(halo),
                  mat.animate.scale(C.MAT_S).move_to(C.MAT_C), *rig.to(**C.MAP_VIEW),
                  FadeIn(u), FadeIn(ulab), rt=1.0)
        self.play(th.animate.set_value(62.0), run_time=self.snap(self.t("east") - 0.15 - self.now), rate_func=linear)
        self.beat("east", th.animate.set_value(0.0), rt=0.3)          # "east" and "north" are 0.22 s apart
        self.beat("north", th.animate.set_value(90.0), rt=0.6, after=306.8, lead=0.0)
        self.beat("in between", th.animate.set_value(30.0), rt=0.8)

        # 4-2 · nothing new needed: the Hessian already holds it
        self.beat("new derivatives", LaggedStart(*[c.animate(rate_func=there_and_back).set_stroke(width=4.5)
                                                   for c in grid.boxes], lag_ratio=0.12), rt=0.8)
        e0 = C.eq_u()
        self.beat("pick a direction", th.animate.set_value(0.0), FadeIn(e0, shift=LEFT * 0.15), rt=0.8)
        circ, nl = C.unit_circle(plate), C.norm_label(plate)
        self.beat("length one", Create(circ), FadeIn(nl), rt=0.6)
        self.bring_to_front(u, ulab)

        # multiply: Hu is the first column, (2, 3); a faint arrow on the map
        e1 = C.eq_hu()
        hu, hlab, drop, shadow = C.hu_parts(plate)
        self.beat("multiply the hessian", Write(e1), GrowArrow(hu), FadeIn(hlab), rt=0.9)

        # dot with u again: the shadow of Hu on u is 2u
        e2 = C.eq_dot()
        self.beat("dot product", Write(e2[:-1]), Create(drop), rt=0.8)
        self.play(Create(shadow), run_time=self.snap(0.5))
        self.bring_to_front(u, ulab)
        gauge = C.dot_gauge(e2)
        self.beat("number that comes out", FadeIn(e2[-1], scale=1.5), GrowFromCenter(gauge), rt=0.5)
        card, bnd = C.eq_bending()
        self.beat("in that direction", FadeIn(card, shift=UP * 0.1), Write(bnd), rt=0.6)
        self.finish()
