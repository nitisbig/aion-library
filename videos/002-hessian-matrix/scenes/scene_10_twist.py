"""Scene 10 · Ch3: the twist (226.717–257.833 s).

"The other two are more interesting. Picture yourself on the surface facing east. Now,
take a step to the side toward the north. Does the ground ahead of you get steeper or
flatter? That's f x y. It measures twist. The surface z equals x times y shows this
perfectly. Along the x-axis, it's flat. But step north and the ground facing east tilts
upward. Step south and it tilts down. Its bending in x is zero. Its bending in y is zero.
But its twist is one."

z = xy: f_x = y, so the east-facing slope at (0, y) is y (flat on the x-axis, +0.6 after
a step north), f_xy = 1, f_xx = f_yy = 0. Every line y = const is exactly straight (a
ruling) with slope y. Arrows and rulings use the plate's own height function, so they
lie on the rendered surface.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
from aion.components.bend_gauge import TwistGauge
import shared as V
import ch3 as L

START, END = V.scene_range(10)
S09_START, S09_END = V.scene_range(9)
ARROW_L = 0.85                                  # length of the east-facing probe (world x units)


class Scene10Twist(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 09's last frame: the table with f_xx, f_yy; the inset's y slice and frown ──
        g, grid, rows, cols = L.s09_end()
        clk9, sx, sy = ValueTracker(S09_END - S09_START), ValueTracker(0.0), ValueTracker(1.0)
        inset = L.inset_rig(clk9, sx, sy)
        iplate = inset.plate(width=L.INSET_W, height=L.INSET_H, center=L.INSET_C)
        gay = L.inset_gauge(iplate, "y")
        clk = ValueTracker(0.0)
        self.run_clock(clk9, clk)
        self.add(iplate, *inset.trackers(), sx, sy, g, gay)

        # 3-4 · the other two cells; the xy surface; a walker facing east
        self.beat("other two", grid.tint(0, 1, S.TWIST, 0.12), grid.tint(1, 0, S.TWIST, 0.12), rt=0.6)
        rig = L.xy_rig(opacity=0.0)
        rig.dyn["yaw"] = lambda: rig.val("yaw") + L.XY_SPIN * clk.get_value()
        plate = rig.plate(width=L.XY_W, height=L.XY_H, center=L.XY_C)
        self.add(plate, *rig.trackers())
        self.bring_to_front(g, gay)
        k, c = L.placement(g, grid, 1.0, L.CORNER_S, L.CORNER_C)
        self.beat("picture yourself", *inset.to(opacity=0.0), FadeOut(gay), *rig.to(opacity=1.0),
                  g.animate.scale(k).move_to(c), rt=1.0)
        self.remove(iplate)

        wy, tilt = ValueTracker(0.0), ValueTracker(0.0)
        me = V.walker()
        V.pin(me, plate, lambda: (0.0, wy.get_value(), float(plate.height(0.0, wy.get_value())) + 0.02))

        def probe(y_fn, t_fn, color, width=7, opacity=1.0):
            def make():
                y, t = y_fn(), t_fn()
                z0 = float(plate.height(0.0, y))
                z1 = (1 - t) * z0 + t * float(plate.height(ARROW_L, y))
                return Arrow(plate.project(0.0, y, z0 + 0.02), plate.project(ARROW_L, y, z1 + 0.02), buff=0,
                             color=color, stroke_width=width,
                             max_tip_length_to_length_ratio=0.22).set_opacity(opacity)
            return always_redraw(make)

        east = probe(wy.get_value, tilt.get_value, S.HX)
        self.beat("facing east", FadeIn(me, scale=0.5), GrowArrow(east), rt=0.6)
        trail = always_redraw(lambda: DashedLine(plate.project(0, 0, 0.02),
                                                 plate.project(0, max(wy.get_value(), 1e-3), 0.02),
                                                 dash_length=0.06, color=S.MUTED, stroke_width=2.5))
        self.add(trail)
        self.bring_to_front(me, east)
        self.beat("step to the side", wy.animate.set_value(L.STEP_N), rt=1.0)
        ghost = probe(lambda: L.STEP_N, lambda: 0.0, S.HX, width=5, opacity=0.35)
        self.add(ghost)
        self.bring_to_front(me, east)
        self.beat("steeper or flatter", tilt.animate.set_value(1.0), rt=0.8)

        # 3-5 · that change is f_xy: twist
        self.beat("f x y", grid.fill(0, 1, L.entry("xy")), grid.tint(0, 1, S.TWIST, 0.3), rt=0.6)
        rib = TwistGauge(1.0, width=0.95).move_to(L.TWIST_AT)
        rib_lab = V.label("twist", 28, S.TWIST).next_to(rib, RIGHT, buff=0.18)
        self.beat("twist", FadeIn(rib, shift=UP * 0.1), FadeIn(rib_lab, shift=UP * 0.1), rt=0.6, after=239.0)

        # 3-6 · z = xy: straight rulings, flat on the x-axis, tilted either side
        zxy = L.zxy_label()
        self.beat("z equals x times y", Write(zxy), rt=0.8)
        show, h0, hp, hn = (ValueTracker(0.0) for _ in range(4))
        rul = L.xy_rulings(plate, show, h0, hp, hn)
        self.add(rul)
        for m in (me, east, ghost, trail):        # freeze: redraws change the dash/family count mid-fade
            m.clear_updaters()
        self.beat("perfectly", show.animate.set_value(1.0), *rig.to(opacity=0.55, grid=(0.0, 0.0)),
                  FadeOut(me), FadeOut(east), FadeOut(ghost), FadeOut(trail), rt=1.0)
        self.beat("xaxis", h0.animate.set_value(1.0), rt=0.5)
        self.beat("step north", hp.animate.set_value(1.0), rt=0.6)
        self.beat("step south", hn.animate.set_value(1.0), rt=0.6)

        # 3-7 · the three readouts
        ro = L.readouts()
        self.beat("bending in x is zero", FadeIn(ro[0], shift=RIGHT * 0.15), rt=0.5)
        self.beat("bending in y is zero", FadeIn(ro[1], shift=RIGHT * 0.15), rt=0.5)
        self.beat("twist is one", ReplacementTransform(rib, ro[2][0]), FadeOut(rib_lab),
                  FadeIn(ro[2][1], shift=RIGHT * 0.15), rt=0.6)
        self.finish()
