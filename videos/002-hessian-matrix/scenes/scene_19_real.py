"""Scene 19 · Ch5: a real landscape (439.267–463.133 s).

"Now a real landscape. F equals x cubed minus three x plus y squared. It has two flat
points at x equals one and x equals minus one. At x equals one, the Hessian is six,
zero, zero, two. Both positive, a valley. At x equals minus one, it's minus six, zero,
zero, two. One of each, a saddle. The pass that leads out of the valley."

f = x³ − 3x + y²: ∇f = (3x² − 3, 2y) = 0 at (±1, 0); H = [[6x, 0], [0, 2]] (ch5 asserts).
The Hessians fill in above each point on the words; a ball settles into the valley; a
dashed gold path climbs from the valley over the pass and out.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import math

import numpy as np
from manim import *

from aion import style as S
import shared as V
import ch5 as C

START, END = V.scene_range(19)


class Scene19Real(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 18's last frame ──
        e = C.s18_end()
        rows = e["rows"]
        board = Group(e["quads"], e["ax"], e["labels"], e["qlabels"], e["card"], e["head"],
                       *[m for r in rows for m in r], e["pz"], e["calc"])
        self.add(e["l1"], e["l2"], board, e["dot"])

        # 5-8 · a real landscape rises; it turns slowly for the rest of the scene
        clk = ValueTracker(0.0)
        self.run_clock(clk)
        rig = C.real_rig(clk)
        plate = rig.plate()
        self.add(plate, *rig.trackers())
        self.bring_to_front(board, e["dot"])
        e["dot"].clear_updaters()
        self.beat("real landscape", FadeOut(board), FadeOut(e["dot"]), *rig.to(opacity=1.0), rt=1.2)
        form = C.real_formula()
        self.beat("x cubed", Write(form), rt=1.2)

        # the two flat points
        rv, rs = C.crit_ring(plate, 1.0), C.crit_ring(plate, -1.0)
        for r in (rv, rs):
            r.set_stroke(opacity=0.45)
        self.beat("two flat points", FadeIn(rv, scale=0.5), FadeIn(rs, scale=0.5), rt=0.6)
        self.beat("x equals one", rv.animate.set_stroke(opacity=1.0), rt=0.4)
        self.beat("x equals minus one", rs.animate.set_stroke(opacity=1.0), rt=0.4)

        # 5-9 · at x = 1: [[6, 0], [0, 2]], a valley
        hv, gv, nv = C.mini_matrix(plate, 1.0, C.ENTRIES_V)
        self.beat("the hessian is", FadeIn(hv, shift=UP * 0.1), rt=0.5)
        cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
        t0 = self.t("six", after=449.4)
        for (i, j), n, w in zip(cells, nv, ("six", "zero", "zero", "two")):
            t0 = self.t(w, after=t0 - 0.01)
            self.play_at(t0, gv.fill(i, j, n), lead=0.05, run_time=0.15)   # words 0.15 s apart
            t0 += 0.05
        vl = V.label("valley", 26, S.SMILE, weight="MEDIUM")
        vl.add_updater(lambda m: m.next_to(hv, RIGHT, buff=0.2))
        s = ValueTracker(0.0)
        ball = V.walker()
        start = np.array([1.75, 0.95])
        def where():
            k = s.get_value()
            ang = 4.0 * math.pi * k
            off = (1 - k) * np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]]) @ (start - [1, 0])
            return 1.0 + off[0], off[1]
        V.pin(ball, plate, lambda: (*where(), float(plate.height(*where())) + 0.03))
        self.add(s)
        self.beat("valley", FadeIn(vl), FadeIn(ball), s.animate.set_value(1.0), rt=1.2, rate=smooth, after=454.0)

        # 5-10 · at x = −1: [[−6, 0], [0, 2]], a saddle; the pass out of the valley
        hs, gs, ns = C.mini_matrix(plate, -1.0, C.ENTRIES_S)
        self.beat("minus one", FadeIn(hs, shift=UP * 0.1), rt=0.5, after=455.0)
        t0 = self.t("minus six", after=456.0)
        for (i, j), n, w in zip(cells, ns, ("minus six", "zero", "zero", "two")):
            t0 = self.t(w, after=t0 - 0.01)
            self.play_at(t0, gs.fill(i, j, n), lead=0.05, run_time=0.15)
            t0 += 0.05
        sl = V.label("saddle", 26, S.TEXT, weight="MEDIUM")
        sl.add_updater(lambda m: m.next_to(hs, RIGHT, buff=0.2))
        self.beat("saddle", FadeIn(sl), rt=0.4, after=460.0)
        p = ValueTracker(0.0)
        self.add(p, C.path_out(plate, p))
        self.bring_to_front(ball)
        self.beat("pass that leads out", p.animate.set_value(1.0), rt=1.6, rate=linear)
        self.finish()
