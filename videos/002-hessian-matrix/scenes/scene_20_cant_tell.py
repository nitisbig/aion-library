"""Scene 20 · Ch5: when the test can't tell (463.133–480.417 s).

"And just like on the line, sometimes the test can't tell. X to the fourth plus y to the
fourth is a valley. But at its center, the Hessian is all zeros. So is the Hessian of
the monkey saddle with room for two legs and a tail. When an eigenvalue is zero, you
have to look closer."

An echo of the Ch1 card's last row (flat gauge → can't tell), then two viewports:
x⁴ + y⁴ (a flat-bottomed valley) and the monkey saddle x³ − 3xy² (turning), each with
an all-zero Hessian at the centre (ch5 asserts both numerically). The monkey saddle's
three low lobes (θ = 60°, 180°, 300°) trace one by one. A slow push-in; fade to black.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.bend_gauge import BendGauge
import shared as V
import ch5 as C

START, END = V.scene_range(20)


class Scene20CantTell(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 19's last frame ──
        s1, e1 = V.scene_range(19)
        clk = ValueTracker(e1 - s1)
        self.run_clock(clk)
        rig = C.real_rig(clk, opacity=1.0)
        plate = rig.plate()
        form = C.real_formula()
        rv, rs = C.crit_ring(plate, 1.0), C.crit_ring(plate, -1.0)
        hv, gv, nv = C.mini_matrix(plate, 1.0, C.ENTRIES_V)
        hs, gs, ns = C.mini_matrix(plate, -1.0, C.ENTRIES_S)
        for g, nums in ((gv, nv), (gs, ns)):
            for (i, j), n in zip(((0, 0), (0, 1), (1, 0), (1, 1)), nums):
                g.fill(i, j, n)
        vl = V.label("valley", 26, S.SMILE, weight="MEDIUM")
        vl.add_updater(lambda m: m.next_to(hv, RIGHT, buff=0.2))
        sl = V.label("saddle", 26, S.TEXT, weight="MEDIUM")
        sl.add_updater(lambda m: m.next_to(hs, RIGHT, buff=0.2))
        ball = V.walker()
        V.pin(ball, plate, lambda: (1.0, 0.0, float(plate.height(1.0, 0.0)) + 0.03))
        p = ValueTracker(1.0)
        path = C.path_out(plate, p)
        self.add(plate, *rig.trackers(), p, form, rv, rs, hv, hs, vl, sl, path, ball)

        # 5-11 · just like on the line: the Ch1 card's last row
        echo = C.echo_row()
        over = [rv, rs, hv, hs, vl, sl, path, ball]
        plate.update()              # the plate's camera first (scene 19's final yaw) …
        for m in over:              # … then place the overlays once, as in scene 19's last frame, and freeze
            m.update()
            m.clear_updaters()
        self.beat("just like on the line", *rig.to(opacity=0.0), FadeOut(form), *[FadeOut(m) for m in over],
                  FadeIn(echo, shift=UP * 0.15), rt=0.9)
        self.remove(plate)

        # x⁴ + y⁴: a valley, but its Hessian is all zeros
        left = C.quartic_rig()
        lplate = left.plate(**C.LEFT_P)
        self.add(lplate, *left.trackers())
        self.beat("cant tell", echo.animate.set_opacity(0.0), rt=0.6, after=466.0)
        self.remove(echo)
        lx = C.LEFT_P["center"][0]
        lf = MathTex("x^4", "+", "y^4", font_size=44, color=S.TEXT).move_to([lx, C.FORM_Y, 0])
        lf[0].set_color(S.HX)
        lf[2].set_color(S.HY)
        self.beat("x to the fourth", *left.to(opacity=1.0), FadeIn(lf, shift=UP * 0.1), rt=1.0)
        vtag = V.label("valley", 26, S.SMILE, weight="MEDIUM").next_to(lf, RIGHT, buff=0.35)
        self.beat("valley", FadeIn(vtag, shift=LEFT * 0.1), rt=0.4, after=469.0)
        lz = C.zero_matrix(np.array([lx - 0.55, C.ZERO_Y, 0]))
        lg = BendGauge(0.0, width=0.7, stroke=6).place(np.array([lx + 0.9, C.ZERO_Y, 0]))
        self.beat("all zeros", FadeIn(lz, shift=UP * 0.1), GrowFromCenter(lg), rt=0.6)

        # the monkey saddle x³ − 3xy²: two legs and a tail, and also all zeros
        mclk = ValueTracker(0.0)
        self.run_clock(mclk)
        right = C.monkey_rig(mclk)
        rplate = right.plate(**C.RIGHT_P)
        self.add(rplate, *right.trackers())
        rx = C.RIGHT_P["center"][0]
        rf = MathTex("x^3", "-", "3xy^2", font_size=44, color=S.TEXT).move_to([rx, C.FORM_Y, 0])
        rz = C.zero_matrix(np.array([rx - 0.55, C.ZERO_Y, 0]))
        rg = BendGauge(0.0, width=0.7, stroke=6).place(np.array([rx + 0.9, C.ZERO_Y, 0]))
        self.beat("monkey saddle", *right.to(opacity=1.0), FadeIn(rf, shift=UP * 0.1), FadeIn(rz, shift=UP * 0.1),
                  GrowFromCenter(rg), rt=1.0)
        gs3 = [ValueTracker(0.0) for _ in C.LOBES]
        self.add(*gs3, *[C.lobe(rplate, d, g) for d, g in zip(C.LOBES, gs3)])
        self.beat("two legs and a tail", LaggedStart(*[g.animate.set_value(1.0) for g in gs3], lag_ratio=0.35), rt=1.3)

        # 5-13 · an eigenvalue is zero: look closer (push in, fade to black)
        self.beat("eigenvalue is zero", *[V.pulse(c, lambda m: m.set_stroke(S.TEXT, 2.5, opacity=1.0))
                                          for z in (lz, rz) for c in z.boxes], rt=0.5)
        push = END - self.now
        self.play(*left.to(dist=3.9), *right.to(dist=3.9), run_time=self.snap(push - 0.75), rate_func=linear)
        rest = [m for m in self.mobjects if isinstance(m, VMobject)]
        self.play(*left.to(dist=3.75, opacity=0.0), *right.to(dist=3.75, opacity=0.0), *[FadeOut(m) for m in rest],
                  run_time=self.snap(END - self.now - 0.1), rate_func=linear)
        self.finish()
