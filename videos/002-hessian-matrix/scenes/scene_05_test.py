"""Scene 05 · Ch1: every curve is a parabola up close (107.450–132.367 s).

"Zoom in close and any curve starts to look like a parabola. Near zero, cosine looks
almost exactly like one, minus x squared over two. The second derivative decides which
way that parabola opens. That's the second derivative test. Flat and bending up, a
valley. Flat and bending down, a peak. And when the bending is zero, like x cubed at
zero, the test simply can't tell."

cos x = 1 − x²/2 + O(x⁴): near 0 the dashed parabola hugs the cosine (max gap on
|x| ≤ 0.5 is below 3e-3, checked below). x³ has f'(0) = f''(0) = 0 yet is neither
a peak nor a valley.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.bend_gauge import BendGauge
import shared as V
import ch1 as C

START, END = V.scene_range(5)
_xs = np.linspace(-0.5, 0.5, 101)
assert np.max(np.abs(np.cos(_xs) - (1 - _xs ** 2 / 2))) < 3e-3
ZOOM = 4.2
ZOOM_AT = np.array([-1.1, 0.6, 0.0])           # where the peak sits while zoomed


class Scene05Test(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        b = C.cos_board()                         # scene 04's last frame
        k = ValueTracker(-1.0)
        gauge = BendGauge(k, width=1.15, stroke=8).place(C.GAUGE_FULL)
        ax, curve, tan = b["ax"], b["curve"], b["tan"]
        self.add(ax, curve, b["label"], tan, b["down"], b["ring"], b["fpp"], b["tag"], gauge)

        # 1-10 · zoom into the peak: a parabola hugs the cosine
        P = ax.c2p(0, 1)
        board = VGroup(curve, tan[0])               # the dot moves but keeps its size
        self.beat("zooming close", board.animate.scale(ZOOM, about_point=P).shift(ZOOM_AT - P),
                  ax.animate.scale(ZOOM, about_point=P).shift(ZOOM_AT - P).set_opacity(0.0),
                  tan[1].animate.move_to(ZOOM_AT),
                  FadeOut(b["down"]), FadeOut(b["ring"]), rt=1.8)
        hug = DashedVMobject(ax.plot(lambda x: 1 - x * x / 2, x_range=[-0.75, 0.75]),
                             num_dashes=36).set_stroke(S.FROWN, 6)
        self.beat("parabola", Create(hug), rt=1.0, after=107.5)
        approx = MathTex(r"\cos x", r"\approx", "1", r"-\tfrac{x^2}{2}", font_size=50, color=S.TEXT)
        approx[3].set_color(S.FROWN)
        approx.next_to(b["label"], DOWN, buff=0.35, aligned_edge=LEFT)
        self.beat("one", Write(approx[:3]), rt=0.25, after=113.0)
        self.beat("minus x squared over two", Write(approx[3]), rt=0.8)

        # zoom back out; a ghost of the other opening flickers once
        self.remove(hug)
        board.add(hug)
        self.add(hug)
        Q = ZOOM_AT
        self.beat("which way that parabola opens",
                  board.animate.shift(P - Q).scale(1 / ZOOM, about_point=P),
                  ax.animate.shift(P - Q).scale(1 / ZOOM, about_point=P),
                  tan[1].animate.move_to(P), rt=1.0)
        board.remove(hug)
        self.remove(hug)
        hug = DashedVMobject(ax.plot(lambda x: 1 - x * x / 2, x_range=[-2.0, 2.0]),
                             num_dashes=40).set_stroke(S.FROWN, 5)
        ghost = DashedVMobject(ax.plot(lambda x: 1 + x * x / 2, x_range=[-1.2, 1.2]),
                               num_dashes=30).set_stroke(S.SMILE, 5, opacity=0)
        self.add(hug, ghost)
        self.play(ghost.animate(rate_func=there_and_back).set_stroke(opacity=0.7),
                  ax.animate(rate_func=smooth).set_opacity(1.0), run_time=self.snap(0.9))
        self.remove(ghost)

        # 1-11 · the test card
        left = VGroup(ax, curve, tan, hug)
        card, head = C.test_card()
        self.beat("second derivative test",
                  left.animate.scale(C.BOARD_SMALL, about_point=ax.c2p(0, 0)).shift(C.BOARD_LEFT - ax.c2p(0, 0)),
                  FadeOut(gauge), FadeOut(b["fpp"]), FadeOut(b["tag"]), FadeOut(approx),
                  FadeIn(card, shift=UP * 0.4), FadeIn(head, shift=UP * 0.2), rt=0.8)

        (g1, a1, l1), (g2, a2, l2), (g3, a3, l3) = (C.test_row(i) for i in range(3))
        self.beat("bending up", FadeIn(a1), GrowFromCenter(g1), rt=0.4)
        self.beat("valley", FadeIn(l1, shift=LEFT * 0.15), rt=0.4, after=124.0)
        self.beat("bending down", FadeIn(a2), GrowFromCenter(g2), rt=0.4)
        self.beat("peak", FadeIn(l2, shift=LEFT * 0.15), rt=0.4, after=126.0)

        # 1-12 · x³: flat, no bending, neither
        cax = C.cube_axes()
        self.remove(hug)
        cube_lab = MathTex("y", "=", "x^3", font_size=48, color=S.TEXT).move_to(b["label"], aligned_edge=LEFT)
        self.beat("bending is zero", FadeIn(a3), GrowFromCenter(g3), Transform(ax, cax),
                  TransformMatchingTex(b["label"], cube_lab),
                  Transform(curve, C.cube_plot(cax)), FadeOut(tan), rt=0.8)
        ft = C.flat_tangent(cax, 0, 0, half=0.55)
        self.beat("x cubed", Create(ft[0]), FadeIn(ft[1], scale=0.5), rt=0.6)
        self.beat("cant tell", FadeIn(l3, shift=LEFT * 0.15), rt=0.5)
        self.finish()
