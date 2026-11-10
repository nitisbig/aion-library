"""Scene 10 · Ch2: the spike that never shrinks (186.217–204.617 s).

"But look closely at a corner. Right before every jump, there's a small spike. Add more
circles, and the spike gets thinner, but it never gets any shorter. It stays at about
nine percent of the jump. This is called the Gibbs phenomenon, and it's telling us
something. Sharp corners are expensive."

The clock eases to a stop as the scene starts (ch2.clock), the machinery fades, and we
zoom 6× onto the top of one falling jump. Partial sums are computed exactly at high
resolution in the zoom window. The overshoot crest is found numerically every frame.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (LEFT, RIGHT, UP, DashedLine, Dot, FadeIn, FadeOut, Line, MathTex, ReplacementTransform,
                   ValueTracker, VGroup, VMobject)

from aion import style as S
from aion import fourier as F
import shared as V
import ch2 as C

START, END = V.scene_range(10)
Z = 6.0
F_SCREEN = np.array([1.2, 0.5])
PEAK = float(F.gibbs_peak(200))           # 1.1790: the crest every version touches


def amps_n(N: float) -> np.ndarray:
    k = np.arange(C.K)
    return C.A1 / C.NS * np.clip(N - k, 0.0, 1.0)


class Scene10Gibbs(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── the S09 picture, as it ended
        plate_op, count_op = ValueTracker(1.0), ValueTracker(1.0)
        self.add(plate_op, count_op)
        C.make_plate(self, plate_op)
        m = C.Stack(self, C.S09_END)
        self.add(C.counter(self, count_op))

        # ── the falling jump nearest x ≈ 2 once the clock has stopped (fixed in wave time)
        c_end = float(C.clock(START + 3.0))
        tau_t = c_end - (2.0 - C.X0) / C.V_SCROLL
        th = float(C.theta_tau(tau_t))
        tau_j = tau_t + (2 * np.pi * round(th / (2 * np.pi)) - th) / C1_OMEGA

        z, N, gN, g_op = ValueTracker(1.0), ValueTracker(200.0), ValueTracker(200.0), ValueTracker(0.0)
        w_op = ValueTracker(0.0)
        self.add(z, N, gN, g_op, w_op)

        def x_jump():
            return C.X0 + (float(C.clock(self.now)) - tau_j) * C.V_SCROLL

        def to_screen(x, y):
            zz = z.get_value()
            u = (zz - 1) / (Z - 1)
            fw = np.array([x_jump(), C.H])
            f = (1 - u) * fw + u * F_SCREEN
            return f[0] + zz * (x - fw[0]), f[1] + zz * (y - fw[1])

        def window():
            zz, xj = z.get_value(), x_jump()
            if zz <= 1.0001:
                return C.X0, C.X_END
            u = (zz - 1) / (Z - 1)
            fx = (1 - u) * xj + u * F_SCREEN[0]
            lo, hi = xj + (-7.4 - fx) / zz, xj + (7.4 - fx) / zz
            return max(C.X0, lo), min(C.X_END, hi)

        def curve(n_val, op, width, color=S.INK):
            if op <= 0:
                return VMobject()
            lo, hi = window()
            x = np.linspace(lo, hi, 6000 if z.get_value() > 1.5 else 3000)
            c = float(C.clock(self.now))
            y = C.square_sum(C.theta_tau(c - (x - C.X0) / C.V_SCROLL), amps_n(n_val))
            sx, sy = to_screen(x, y)
            return VMobject().set_points_as_corners(np.column_stack([sx, sy, 0 * sx])).set_stroke(color, width, op)

        def crest():
            """(x, y) of the overshoot crest just left of the jump, for the current N."""
            xj = x_jump()
            n_val = N.get_value()
            span = min(0.6, 2.5 * 4.0 / (2 * n_val))
            x = np.linspace(xj - span, xj, 3000)
            y = C.square_sum(C.theta_tau(float(C.clock(self.now)) - (x - C.X0) / C.V_SCROLL), amps_n(n_val))
            i = int(np.argmax(y))
            return x[i], y[i]

        wave = V.redraw(lambda: curve(N.get_value(), w_op.get_value(), 3.5))
        ghost = V.redraw(lambda: curve(gN.get_value(), 0.35 * g_op.get_value(), 2.5))
        self.add(ghost, wave)

        # swap: the Stack's wave → this zoomable wave (identical at z = 1)
        self.wait_until(self.t("closely") - S.LEAD - 0.1)
        w_op.set_value(1.0)
        m.v["trail_op"].set_value(0.0)

        # "closely": the machinery goes, zoom 6× onto one jump; meanwhile N drops to 10
        self.beat("closely", z.animate.set_value(Z), N.animate.set_value(10.0),
                  *m.to(conn_op=0.0, track_op=0.0, axis_op=0.0, hair_op=0.0, strip_op=0.0, sq_op=0.0),
                  plate_op.animate.set_value(0.0), count_op.animate.set_value(0.0), rt=1.2)

        # "small spike": a red dot on the overshoot crest (it follows the crest as N changes)
        d_op = ValueTracker(0.0)
        self.add(d_op)
        dot = V.redraw(lambda: VMobject() if d_op.get_value() <= 0 else VGroup(
            Dot(np.array([*to_screen(*crest()), 0]), radius=0.22, color=S.SPIKE).set_opacity(0.25 * d_op.get_value()),
            Dot(np.array([*to_screen(*crest()), 0]), radius=0.08, color=S.SPIKE).set_opacity(d_op.get_value())))
        self.add(dot)
        self.beat("small spike", d_op.animate.set_value(1.0), rt=0.4)

        # "more circles": 10 → 50, the old version fades as a ghost; "thinner": 50 → 200
        for key, n_new in (("more circles", 50.0), ("thinner", 200.0)):
            gN.set_value(N.get_value())
            g_op.set_value(1.0)
            self.beat(key, N.animate.set_value(n_new), g_op.animate(rate_func=V.window(0.3, 1.0)).set_value(0.0),
                      rt=0.7, rate=None)

        # "never gets any shorter": a red hairline at the crest height
        h_op = ValueTracker(0.0)
        self.add(h_op)

        def hairline():
            o = h_op.get_value()
            if o <= 0:
                return VMobject()
            y = to_screen(0, C.H * PEAK)[1]
            return DashedLine([-7.4, y, 0], [7.4, y, 0], dash_length=0.12, color=S.SPIKE, stroke_width=1.6).set_stroke(opacity=0.8 * o)
        self.add(V.redraw(hairline))
        self.beat("never gets any shorter", h_op.animate.set_value(1.0), rt=0.6)

        # "nine percent": a bracket from the top of the wave up to the hairline
        xb = to_screen(x_jump() - 0.7, 0)[0]
        y0, y1 = to_screen(0, C.H)[1], to_screen(0, C.H * PEAK)[1]
        br = VGroup(Line([xb, y0, 0], [xb, y1, 0]), Line([xb - 0.1, y0, 0], [xb + 0.1, y0, 0]),
                    Line([xb - 0.1, y1, 0], [xb + 0.1, y1, 0])).set_stroke(S.LABEL, 2)
        pct = MathTex(r"\approx 9\%", font_size=40, color=S.LABEL)
        pct.next_to(br, LEFT, buff=0.2).set_y(y0 + 0.72 * (y1 - y0))
        jump_word = V.label("of the jump", 22, S.LABEL_MUTED).next_to(pct, np.array([0, -1, 0]), buff=0.1)
        jump_word.align_to(pct, RIGHT)
        self.beat("nine percent", FadeIn(br), FadeIn(pct, shift=RIGHT * 0.1), FadeIn(jump_word), rt=0.6)

        # "gibbs phenomenon": its name, small, beside the bracket
        name = V.label("Gibbs phenomenon", 30, S.LABEL).next_to(np.array([xb, y1, 0]), UP, buff=0.45)
        name.align_to(pct, LEFT)
        self.beat("gibbs phenomenon", FadeIn(name, shift=UP * 0.08), rt=0.6)

        # "expensive": zoom out; the red dot docks top-right as the corner marker; the wave floats free
        marker = C.corner_marker()
        flyer = Dot(np.array([*to_screen(*crest()), 0]), radius=0.08, color=S.SPIKE)
        d_op.set_value(0.0)
        self.add(flyer)
        self.beat("expensive", z.animate.set_value(1.0), h_op.animate.set_value(0.0),
                  FadeOut(VGroup(br, pct, jump_word, name)), ReplacementTransform(flyer, marker),
                  *m.to(axis_op=0.0), rt=0.8)
        self.finish()
        self.handoff = {"marker": marker}


C1_OMEGA = 2 * np.pi / 4.0
