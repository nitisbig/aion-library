"""Scene 09 · Ch3: four second derivatives (200.017–226.717 s).

"We have two slopes, the slope in x and the slope in y. And each slope can change in two
ways. As you move in x or as you move in y. Two slopes, two directions, four second
derivatives. How the x slope changes as you move in x. That's the bending of the x slice.
We write it f x x. How the y slope changes as you move in y. The bending of the y slice, f y y."

Rows are the two slopes (∂f/∂x, ∂f/∂y), columns the two directions of motion. The inset
is scene 08's saddle x² − y²: its x slice has f_xx = 2 (smile), its y slice f_yy = −2 (frown).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch2 as L2
import ch3 as L

START, END = V.scene_range(9)
S08_START, S08_END = V.scene_range(8)


class Scene09Four(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 08's last frame: the saddle, both slices, both gauges lifted, "how many?" ──
        clk8 = ValueTracker(S08_END - S08_START)
        sx8, sy8, lift = ValueTracker(1.0), ValueTracker(1.0), ValueTracker(0.5)
        big = L2.big_saddle(clk8, sx8, sy8, opacity=1.0)
        bplate = big.plate()
        bw = V.walker()
        V.pin(bw, bplate, V.on_surface(bplate, 0, 0, 0.02))
        gx, gy = L2.saddle_gauges(bplate, lift)
        how = L2.how_many()
        clk = ValueTracker(0.0)
        self.run_clock(clk8, clk)
        self.add(bplate, *big.trackers(), sx8, sy8, lift, bw, gx, gy, how)
        self.play(*big.to(opacity=0.0), FadeOut(bw), FadeOut(gx), FadeOut(gy), FadeOut(how),
                  run_time=self.snap(0.55), rate_func=smooth)
        self.remove(bplate)

        # 3-1 · two slopes × two directions
        g, grid, rows, cols = L.table()
        self.beat("two slopes", FadeIn(rows[0], shift=RIGHT * 0.2), rt=0.6)
        self.beat("slope in x", Indicate(rows[0], color=S.HX, scale_factor=1.15), rt=0.5)
        self.beat("slope in y", FadeIn(rows[1], shift=RIGHT * 0.2), rt=0.5)
        self.add(grid)
        self.beat("two ways", grid.appear(), rt=0.6)
        self.beat("move in x", FadeIn(cols[0], shift=DOWN * 0.15), rt=0.4, after=206.8)
        self.beat("move in y", FadeIn(cols[1], shift=DOWN * 0.15), rt=0.4, after=207.5)
        self.beat("four second derivatives",
                  LaggedStart(*[L.lit(b.animate) for b in grid.boxes], lag_ratio=0.12), rt=0.8)

        # 3-2 · f_xx: the bending of the x slice
        sx, sy = ValueTracker(0.0), ValueTracker(0.0)
        rig = L.inset_rig(clk, sx, sy, opacity=0.0)
        plate = rig.plate(width=L.INSET_W, height=L.INSET_H, center=L.INSET_C)
        self.add(plate, *rig.trackers(), sx, sy)
        self.bring_to_front(g)
        self.beat("as you move in x", grid.tint(0, 0, S.HX, 0.3), rt=0.4, after=213.6)
        gax = L.inset_gauge(plate, "x")
        self.beat("bending of the x slice", *rig.to(opacity=1.0), sx.animate.set_value(1.0), rt=0.8)
        self.play(FadeIn(gax, scale=0.6), run_time=self.snap(0.4))
        self.beat("f x x", grid.fill(0, 0, L.entry("xx")), rt=0.6)

        # 3-3 · f_yy: the bending of the y slice
        self.beat("y slope changes", grid.tint(1, 1, S.HY, 0.3), rt=0.4)
        gay = L.inset_gauge(plate, "y")
        self.beat("y slice", sx.animate.set_value(0.0), sy.animate.set_value(1.0), FadeOut(gax),
                  FadeIn(gay, scale=0.6), rt=0.6)
        self.beat("f y y", grid.fill(1, 1, L.entry("yy")), rt=0.6)
        self.finish()
