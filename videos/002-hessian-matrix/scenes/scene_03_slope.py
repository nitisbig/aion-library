"""Scene 03 · Ch1: slope, and the slope of the slope (55.467–80.017 s).

"Let's start with a single curve. Y equals x squared. At every point, it has a slope.
That's the first derivative. On the left, the slope is negative. On the right, it's
positive, and right at the bottom, it's zero. Now, watch the slope itself. As we move
to the right, it keeps rising steadily. The rate at which the slope changes is the
second derivative. For x squared, it's two everywhere."

Visual argument: a tangent rides y = x² with a live slope readout (2x₀, computed).
The screen splits and the slope is traced as its own graph: the straight line 2x.
Its own slope (rise 2 per run 1, the same everywhere) is the second derivative, 2.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch1 as C

START, END = V.scene_range(3)
assert all(abs(2 * x - (((x + 1e-6) ** 2 - (x - 1e-6) ** 2) / 2e-6)) < 1e-6 for x in (-1.5, 0, 1.5))


class Scene03Slope(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        hand = V.handoff_tangent()                 # scene 02's last frame
        self.add(hand)

        ax = V.ch1_axes()
        self.beat("single curve", FadeIn(ax, shift=UP * 0.1), rt=0.8)
        par = C.parabola(ax)
        lab = C.eq_label()
        self.beat("why equals x squared", Create(par), FadeOut(hand[0]), Write(lab), rt=1.2)

        # 1-2 · the tangent rides the curve; readout of the slope
        x0 = ValueTracker(V.X0_HANDOFF)
        tan = C.tangent(ax, x0)
        self.remove(hand, *hand)                   # FadeOut(hand[0]) promoted the rest to top level
        self.add(tan)
        self.beat("every point", x0.animate.set_value(0.4), rt=1.2)
        ro = C.readout(x0).move_to(C.READOUT_FULL)
        self.beat("first derivative", FadeIn(ro, shift=LEFT * 0.15), rt=0.6)

        # 1-3 · negative on the left, positive on the right, zero at the bottom
        self.beat("left", x0.animate.set_value(-1.5), rt=0.9, after=63.0)
        self.beat("negative", Indicate(ro[1], color=S.GRAD, scale_factor=1.25), rt=0.5)
        self.beat("right", x0.animate.set_value(1.5), rt=1.0, after=65.0)
        self.beat("bottom", x0.animate.set_value(0.0), rt=0.8, after=67.0)
        self.beat("zero", Flash(ax.c2p(0, 0), color=S.GRAD, line_length=0.25, flash_radius=0.35),
                  V.punch(VGroup(ax, par), ax.c2p(0, 0), 1.12),
                  rt=0.4, after=67.5)

        # 1-4 · split: the slope gets its own graph
        top = VGroup(ax, par)
        ax2 = C.slope_axes()
        ax2_lab = C.slope_axes_label(ax2)
        self.beat("watch the slope itself", top.animate.scale(C.SPLIT_SCALE, about_point=ax.c2p(0, 0))
                  .shift(C.TOP_ORIGIN - ax.c2p(0, 0)),
                  x0.animate.set_value(-2.0), FadeIn(ax2, shift=UP * 0.2), FadeIn(ax2_lab), rt=1.0)
        trace = always_redraw(lambda: Line(ax2.c2p(-2, -4), ax2.c2p(x0.get_value(), 2 * x0.get_value()),
                                           color=S.GRAD, stroke_width=5)
                              if x0.get_value() > -1.999 else VMobject())
        tdot = always_redraw(lambda: Dot(ax2.c2p(x0.get_value(), 2 * x0.get_value()), radius=0.07, color=S.GRAD))
        guide = always_redraw(lambda: DashedLine(ax.c2p(x0.get_value(), x0.get_value() ** 2),
                                                 ax2.c2p(x0.get_value(), 2 * x0.get_value()),
                                                 color=S.MUTED, stroke_width=1.5, dash_length=0.06)
                              .set_opacity(0.5))
        self.add(trace, guide, tdot)
        self.beat("move to the right", x0.animate.set_value(2.0), rt=3.0, rate=linear)

        # 1-5 · its own slope: rise 2 per run 1, everywhere
        tri = C.rise_run(ax2, 0.5)
        self.beat("rate", FadeIn(tri), rt=0.8, after=74.0)
        fpp = MathTex("f''(x)", "=", "2", font_size=46, color=S.TEXT).move_to(C.FPP_POS)
        self.beat("second derivative", Write(fpp[:2]), rt=0.8, after=76.0)
        self.beat("two everywhere", Write(fpp[2]), rt=0.5)
        self.play(tri.animate.become(C.rise_run(ax2, -1.5)), run_time=self.snap(0.6))
        self.finish()
