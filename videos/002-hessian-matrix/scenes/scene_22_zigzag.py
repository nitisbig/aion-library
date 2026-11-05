"""Scene 22 · Ch6: gradient descent zigzags (496.817–520.917 s).

"The simplest way down is to follow the gradient, one small step at a time. That's
gradient descent. But watch it in a long narrow valley. Here, the eigenvalues are two
and 20. The walls are 10 times steeper than the floor. Each step overshoots and the path
zigzags back and forth, crawling toward the bottom. That ratio, 20 over two, is called
the condition number."

A top-down map with exact level sets. On a round bowl (H = 2I) gradient descent glides
in. The contours then stretch into the narrow valley x² + 10y² (H = diag(2, 20)) and the
same rule zigzags for 21 steps (all computed and asserted in ch6).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch6 as C

START, END = V.scene_range(22)


class Scene22Zigzag(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 21's last frame ──
        s0, e0 = V.scene_range(21)
        clk = ValueTracker(e0 - s0)
        self.run_clock(clk)
        e = C.s21_end(clk)
        land = [e["ring"], e["axes"], e["fan"], e["ball"], e["eb"], e["cap"]]
        self.add(e["plate"], *e["rig"].trackers(), e["g"], *land)

        # 6-3 · the simplest way down: a round bowl
        rnd = C.contours(C.ROUND)
        ball = V.walker().move_to(C.m2p(*C.START))
        for m in (e["ring"], *e["axes"], e["ball"]):
            m.clear_updaters()
        self.beat("simplest way down", *e["rig"].to(opacity=0.0), *[FadeOut(m) for m in land],
                  LaggedStart(*[Create(c) for c in rnd], lag_ratio=0.08), FadeIn(ball, scale=0.6), rt=1.0)
        self.remove(e["plate"])
        arrow = C.grad_arrow()
        self.beat("follow the gradient", GrowArrow(arrow), rt=0.6)

        s = ValueTracker(0.0)
        path = C.path_mob(C.ROUND_PTS, s)
        self.add(s, path)
        ball.add_updater(lambda m: m.move_to(C.path_pos(C.ROUND_PTS, s.get_value())))
        self.bring_to_front(ball)
        self.beat("one small step", s.animate.set_value(1.0), FadeOut(arrow), rt=0.6)
        self.beat("at a time", s.animate.set_value(len(C.ROUND_PTS) - 1), rt=1.2, rate=linear, after=500.5)
        gl = C.gd_label()
        self.beat("gradient descent", FadeIn(gl, shift=RIGHT * 0.1), rt=0.5, after=502.0)

        # 6-4 · a long narrow valley: the same contours, stretched; H = diag(2, 20)
        nar = C.contours(C.NARROW)
        ball.clear_updaters()
        self.beat("long narrow valley", Transform(rnd, nar), FadeOut(path), ball.animate.move_to(C.m2p(*C.START)),
                  rt=1.0)
        self.remove(path, s)
        hm = C.h_matrix()
        gs = C.gauges()
        ax = C.map_axes()
        self.beat("eigenvalues are two", FadeIn(hm, shift=UP * 0.1), rt=0.6)
        self.beat("two", FadeIn(gs[0], shift=UP * 0.1), Create(ax[0]), rt=0.4, after=507.7)
        self.beat("20", FadeIn(gs[1], shift=UP * 0.1), Create(ax[1]), rt=0.5, after=508.2)
        self.beat("steeper", V.pulse(gs[1][0], lambda m: m.set_stroke(width=9)),
                  V.pulse(ax[1], lambda m: m.set_stroke(width=5, opacity=1.0)), rt=0.8)

        # 6-5 · each step overshoots: 21 zigzag steps
        s2 = ValueTracker(0.0)
        path2 = C.path_mob(C.NARROW_PTS, s2)
        co = ValueTracker(0.0)
        cnt = C.gd_counter(s2, co)
        self.add(s2, co, path2, cnt)
        ball.add_updater(lambda m: m.move_to(C.path_pos(C.NARROW_PTS, s2.get_value())))
        self.bring_to_front(ball)
        self.beat("overshoots", s2.animate.set_value(2.0), co.animate.set_value(1.0), rt=1.3, rate=linear)
        self.beat("zigzags", s2.animate.set_value(21.0), rt=2.8, rate=linear)

        # 6-6 · the condition number
        rt_, rl = C.ratio()
        self.beat("20 over two", FadeIn(rt_, shift=UP * 0.1), rt=0.8, after=518.0)
        self.beat("condition number", FadeIn(rl, shift=UP * 0.08), rt=0.5)
        self.finish()
