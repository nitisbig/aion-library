"""Scene 04 · Ch1: smile, frown, and a flat spot (80.017–107.450 s).

"A positive second derivative means the slope is rising. The curve bends upward like
a smile. Flip it over to minus x squared, and the second derivative is minus two. The
curve bends down like a frown. So the second derivative measures bending, and that's
exactly what we need at a flat spot. Take cosine of x. At zero, it's flat. Top or
bottom? The second derivative there is minus one. It bends down. A peak."

The BendGauge is born here: blue smile for f'' > 0, orange frown for f'' < 0.
cos''(0) = −cos(0) = −1 (checked below).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
from aion.components.bend_gauge import BendGauge
import shared as V
import ch1 as C

START, END = V.scene_range(4)
_h = 1e-4
assert abs((math.cos(_h) - 2 * math.cos(0) + math.cos(-_h)) / _h ** 2 + 1) < 1e-3


class Scene04Smile(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── rebuild scene 03's last frame ──
        ax = V.ch1_axes()
        s = ValueTracker(1.0)
        C.split(VGroup(ax), ax)
        par = always_redraw(lambda: C.parabola(ax, s.get_value()))
        lab = C.eq_label()
        x0 = ValueTracker(0.4)
        ro = C.readout(x0, lambda: s.get_value()).move_to(C.READOUT_FULL)
        x0.set_value(2.0)
        ro.update()
        tan = C.tangent(ax, x0, lambda: s.get_value())
        ax2 = C.slope_axes()
        ax2_lab = C.slope_axes_label(ax2)
        line = always_redraw(lambda: Line(ax2.c2p(-2, -4 * s.get_value()), ax2.c2p(2, 4 * s.get_value()),
                                          color=S.GRAD, stroke_width=5))
        tdot = always_redraw(lambda: Dot(ax2.c2p(x0.get_value(), 2 * s.get_value() * x0.get_value()),
                                         radius=0.07, color=S.GRAD))
        guide = always_redraw(lambda: DashedLine(ax.c2p(x0.get_value(), s.get_value() * x0.get_value() ** 2),
                                                 ax2.c2p(x0.get_value(), 2 * s.get_value() * x0.get_value()),
                                                 color=S.MUTED, stroke_width=1.5, dash_length=0.06).set_opacity(0.5))
        tri = C.rise_run(ax2, -1.5)
        fpp = MathTex("f''(x)", "=", "2", font_size=46, color=S.TEXT).move_to(C.FPP_POS)
        self.add(ax, par, lab, ro, tan, ax2, ax2_lab, line, guide, tdot, tri, fpp)

        # 1-6 · positive: the slope rises; the curve smiles
        self.beat("positive second derivative", fpp[2].animate.set_color(S.SMILE), rt=0.5)
        self.beat("slope is rising", ShowPassingFlash(line.copy().clear_updaters().set_stroke(S.GRAD, 12),
                                                     time_width=0.5), rt=0.8)
        k = ValueTracker(2.0)
        g_at = ValueTracker(0.0)
        gauge = BendGauge(k, width=1.15, stroke=8)
        gauge.add_updater(lambda m: m.place(interpolate(C.GAUGE_POS, C.GAUGE_FULL, g_at.get_value())))
        gop = ValueTracker(0.0)
        glow = always_redraw(lambda: C.parabola(ax, s.get_value(), S.SMILE).set_stroke(opacity=gop.get_value())
                             .set_stroke(opacity=0.3 * gop.get_value(), background=True))
        self.add(glow, gop)
        self.beat("smile", GrowFromCenter(gauge), gop.animate(rate_func=there_and_back).set_value(0.8),
                  rt=0.65, after=85.0)
        self.remove(glow)
        self.add(gauge)

        # 1-7 · flip to −x²: slope line tilts down, f'' = −2, the gauge frowns
        lab2 = MathTex("y", "=", "-", "x^2", font_size=48, color=S.TEXT).move_to(lab, aligned_edge=LEFT)
        # the top panel's origin rises so −x² hangs inside the top half; x₀ eases to 1
        self.beat("flip it over", s.animate.set_value(-1.0), TransformMatchingTex(lab, lab2),
                  ax.animate.shift(UP * C.FLIP_RISE), x0.animate.set_value(1.0),
                  tri.animate.become(C.rise_run(ax2, -1.5, -1.0)), rt=1.2)
        # separately: animating ax.y_axis in the same play overrides ax's shift for it,
        # which left c2p (and so −x²) behind
        self.play(ax.y_axis.animate.set_opacity(0.0), run_time=self.snap(0.3))
        fpp2 = MathTex("f''(x)", "=", "-2", font_size=46, color=S.TEXT).move_to(C.FPP_POS)
        fpp2[2].set_color(S.FROWN)
        self.beat("minus two", TransformMatchingTex(fpp, fpp2), rt=0.5)
        self.beat("frown", k.animate.set_value(-2.0), rt=0.7, after=91.0)

        # 1-8 · bending at a flat spot
        tag = V.label("bending", 24, S.MUTED)
        tag.add_updater(lambda m: m.move_to(gauge.get_center() + UP * 0.85))
        self.beat("measures bending", FadeIn(tag, shift=DOWN * 0.1), rt=0.6)
        bottom = VGroup(ax2, ax2_lab, tri)
        self.remove(line, guide, tdot)
        frozen = VGroup(line.copy().clear_updaters(), guide.copy().clear_updaters(), tdot.copy().clear_updaters())
        self.add(frozen)
        o = ax.c2p(0, 0)
        ro.clear_updaters()                    # freeze the live number before fading it
        self.beat("flat spot", FadeOut(bottom, shift=DOWN * 0.4), FadeOut(frozen, shift=DOWN * 0.4), FadeOut(ro),
                  ax.animate.scale(1 / C.SPLIT_SCALE, about_point=o).shift(C.PEAK_ORIGIN - o),
                  x0.animate.set_value(0.0), g_at.animate.set_value(1.0),
                  fpp2.animate.move_to(C.FPP_FULL), rt=0.8)

        # cos x: flat at 0. top or bottom?
        cax = C.cos_axes()
        self.remove(par, tan)
        par_s = C.parabola(ax, -1.0)
        ft = C.flat_tangent(ax, 0, 0)
        self.add(par_s, ft)
        clab = C.cos_label()
        self.beat("cosine of x", Transform(ax, cax), Transform(par_s, C.cos_plot(cax)),
                  Transform(ft, C.flat_tangent(cax, 0, 1)), TransformMatchingTex(lab2, clab), rt=1.0)
        self.beat("its flat", ShowPassingFlash(ft[0].copy().set_stroke(S.GRAD, 10), time_width=0.6),
                  rt=0.5, after=100.0)
        # "top or bottom?": no on-screen question; two pings leave the flat point instead
        pings = VGroup(*[Circle(radius=0.12).set_stroke(S.GRAD, 2.5).move_to(cax.c2p(0, 1)) for _ in range(2)])
        self.beat("top or bottom", LaggedStart(*[p.animate.scale(6).set_stroke(opacity=0) for p in pings],
                                               lag_ratio=0.35), rt=1.0, rate=rush_from)
        self.remove(pings)

        # 1-9 · f''(0) = −1: it bends down, a peak
        self.beat("minus one", TransformMatchingTex(fpp2, C.fpp_peak()), k.animate.set_value(-1.0),
                  rt=0.6, after=103.0)
        down = V.lit(cax.plot(math.cos, x_range=[-1.1, 1.1]), S.FROWN, 5, 18, 0.18)
        self.beat("bends down", Create(down), rt=0.5, after=105.0)
        ring = Circle(radius=0.22, color=S.FROWN, stroke_width=4).move_to(cax.c2p(0, 1))
        self.beat("peak", Create(ring), rt=0.5, after=106.5)
        self.finish()
