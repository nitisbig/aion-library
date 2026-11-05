"""Scene 23 · Ch6: one Newton jump, and a trillion numbers (520.917–542.250 s).

"Now bring in the Hessian. Newton's method treats the ground around you as a bowl, built
from the gradient and the Hessian, and jumps straight to the bottom of that bowl. On this
valley, one jump lands exactly on the minimum. The catch? With a million inputs, the
Hessian is a million by a million, a trillion numbers. So real methods only estimate
pieces of it."

The bowl appears as a luminous inset; one arc carries the ball from (3, 1) to the
minimum (p − H⁻¹∇f = 0, asserted in ch6). Then the 2×2 grid becomes the centre of an
endless mosaic of cells, a counter rolls to 10¹², and only a band along the diagonal
stays lit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import math

from manim import *

from aion import style as S
import shared as V
import ch6 as C

START, END = V.scene_range(23)


class Scene23Newton(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 22's last frame ──
        e = C.s22_end()
        self.add(e["co"], e["cont"], e["s"], e["path"], e["hm"], e["gs"], e["ax"], e["ratio"], e["rlab"], e["gl"],
                 e["cnt"], e["ball"])

        # 6-7 · bring in the Hessian: Newton's method
        op = ValueTracker(1.0)
        self.remove(e["path"])
        path = C.path_mob(C.NARROW_PTS, e["s"], op)
        self.add(op, path)
        self.bring_to_front(e["ball"])
        grid = e["hm"][1]
        self.beat("bring in the hessian", op.animate.set_value(0.3), FadeOut(e["gs"]), FadeOut(e["ax"]),
                  FadeOut(e["ratio"]), FadeOut(e["rlab"]),
                  *[V.pulse(b, lambda m: m.set_stroke(S.TERRAIN_LINE, 2.6, opacity=1.0)) for b in grid.boxes],
                  rt=0.7)
        nl = C.newton_label()
        self.beat("newtons method", FadeIn(nl, shift=RIGHT * 0.1), rt=0.5)

        # the bowl built from the gradient and the Hessian (here it is the valley itself)
        bowl = C.bowl_rig()
        inset = bowl.plate(**C.INSET)
        self.add(inset, *bowl.trackers())
        hop = ValueTracker(0.0)

        def ball_xyz():
            k = hop.get_value()
            x, y = C.START[0] * (1 - k), C.START[1] * (1 - k)
            return x, y, float(inset.height(x, y)) + 0.04 + 0.9 * 4 * k * (1 - k)
        ib = V.walker(radius=0.06)
        V.pin(ib, inset, ball_xyz)
        ib_a = ValueTracker(0.0)
        ib.add_updater(lambda m: V.set_walker_alpha(m, ib_a.get_value()))
        self.add(hop, ib_a, ib)
        self.beat("as a bowl", *bowl.to(opacity=1.0), ib_a.animate.set_value(1.0),
                  *[V.pulse(c, lambda m: m.set_stroke(S.SMILE, opacity=0.9)) for c in e["cont"]], rt=0.9)

        # one arc, straight to the bottom
        arc = C.newton_arc()
        ball = e["ball"]
        self.beat("jumps straight", Create(arc), MoveAlongPath(ball, arc.copy()), hop.animate.set_value(1.0),
                  rt=1.0, rate=smooth)
        flash = Circle(radius=0.12).move_to(C.m2p(0, 0))
        V.lit(flash, S.LIGHT, width=3, halo=12, opacity=0.2)
        cnt1 = C.newton_count()
        self.beat("one jump", FadeIn(cnt1, shift=UP * 0.08),
                  flash.animate(rate_func=rush_from).scale(4.5).set_stroke(opacity=0.0), rt=0.7)
        self.remove(flash)

        # 6-8 · the catch: a million by a million
        target = C.grid_at_mosaic(e["hm"])
        rest = [e["cont"], path, ball, arc, e["gl"], nl, cnt1, ib]
        ib.clear_updaters()
        self.beat("the catch", *bowl.to(opacity=0.0), *[FadeOut(m) for m in rest], FadeOut(e["hm"][0]), e["co"].animate.set_value(0.0),
                  Transform(grid, target), rt=0.9)
        self.remove(inset, path, op)

        p, a, b = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)    # p: zoom exponent 0 → 1
        mos = C.Mosaic(lambda: C.mosaic_pitch(p.get_value()), a, b)
        self.add(p, a, b)
        self.add(mos)
        self.bring_to_back(mos)
        mil = C.million()
        # the grid hands over to the aligned mosaic, then the view pulls back exponentially
        self.beat("million by a million", a.animate.set_value(1.0), FadeOut(grid), rt=0.4, after=536.3)
        self.play(p.animate.set_value(1.0), FadeIn(mil, shift=UP * 0.1, rate_func=smooth),
                  run_time=self.snap(1.15), rate_func=rush_into)
        ex, eo = ValueTracker(0.0), ValueTracker(0.0)
        tri = C.trillion(ex, eo)
        self.add(ex, eo, tri)
        self.beat("trillion numbers", eo.animate.set_value(1.0), ex.animate.set_value(1.0), rt=1.0)

        # only pieces of it are estimated: a band along the diagonal
        self.beat("estimate pieces", b.animate.set_value(1.0), rt=0.8)
        self.finish()
