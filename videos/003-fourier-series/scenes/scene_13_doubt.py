"""Scene 13 · Ch3: nobody believed it (256.167–272.283 s).

"But for this to work, any starting temperature, even one with sudden jumps, had to be a
sum of smooth waves. Some of the best mathematicians of his day didn't buy it. Well, you
and I just watched it happen. Now let's bring all this back to our drawing."

A jagged (piecewise-constant) temperature profile around the ring, its first three
Fourier components (exact closed forms for a step function), the doubt (= → ?=), and the
answer: its partial sums, N = 1 → 200, closing onto the jumps. Then the converged line
winds up into one circle with its arm, the picture Ch4 starts from (ch3.drawing_seed).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (ManimColor, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, MathTex, ReplacementTransform, ValueTracker,
                   VGroup, VMobject)

from aion import style as S
import shared as V
import ch2 as C2
import ch3 as H
import scene_12_modes_fade as S12

START, END = V.scene_range(13)

# the jagged profile: levels on arcs of the ring (θ ∈ [0, 2π)), mean removed
BREAKS = np.array([0.0, 0.9, 1.75, 2.6, 3.3, 4.4, 5.3, 2 * np.pi])
LEVELS = np.array([0.75, -0.2, 0.6, -0.85, 0.15, -0.6, 0.35])
LEVELS = LEVELS - np.sum(LEVELS * np.diff(BREAKS)) / (2 * np.pi)
X_L, W, GAIN = -6.4, 5.0, 1.15            # profile box: x ∈ [X_L, X_L + W], y = GAIN · f
X_R = 0.75                                # sine column: same width and gain, so heights compare truly
ROWS = (1.6, 0.35, -0.9)


def coeffs(n_max: int):
    """Exact Fourier coefficients (a_n, b_n), n = 1..n_max, of the step profile."""
    n = np.arange(1, n_max + 1)[:, None]
    a0, b0 = BREAKS[:-1][None, :], BREAKS[1:][None, :]
    a = (LEVELS * (np.sin(n * b0) - np.sin(n * a0))).sum(1) / (np.pi * n[:, 0])
    b = (LEVELS * (np.cos(n * a0) - np.cos(n * b0))).sum(1) / (np.pi * n[:, 0])
    return a, b


A, B = coeffs(200)
TH = np.linspace(0, 2 * np.pi, 2400)


def partial(N: float, th=TH) -> np.ndarray:
    """S_N with a fractional last term (so N can be animated smoothly)."""
    w = np.clip(N - np.arange(200), 0.0, 1.0)
    n = np.arange(1, 201)[:, None]
    return ((w * A)[:, None] * np.cos(n * th) + (w * B)[:, None] * np.sin(n * th)).sum(0)


def to_xy(th, y, x0=X_L, y0=0.0):
    return np.column_stack([x0 + th / (2 * np.pi) * W, y0 + GAIN * y, 0 * th])


def profile() -> VMobject:
    pts = []
    for k, lv in enumerate(LEVELS):
        pts += [(BREAKS[k], lv), (BREAKS[k + 1], lv)]
    th, y = np.array(pts).T
    return VMobject().set_points_as_corners(to_xy(th, y)).set_stroke(S.INK, 3.5)


class Scene13Doubt(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        L = S.LEAD
        # ── S12's last picture (its heat clocks keep running) + the corner marker
        op = ValueTracker(1.0)
        self.add(op)
        plate = H.MeshPlate(lambda: S12.end_state(self.now, op=op.get_value()))
        self.add(plate, C2.corner_marker())

        # "But": the rings go
        self.beat("but", op.animate.set_value(0.0), rt=1.0)
        self.remove(plate)

        # "sudden jumps": a jagged temperature profile draws in on the left
        prof = profile()
        self.beat("sudden jumps", Create(prof), rt=1.0)

        # "sum of smooth waves": = and its first three waves (exact coefficients), + …
        eq = MathTex("=", font_size=60, color=S.LABEL).move_to([X_L + W + 0.55, 0, 0])
        sines = VGroup(*[VMobject().set_points_smoothly(to_xy(TH[::8], A[n - 1] * np.cos(n * TH[::8])
                                                              + B[n - 1] * np.sin(n * TH[::8]), X_R, y))
                         .set_stroke(S.INK, 3) for n, y in zip((1, 2, 3), ROWS)])
        plus = VGroup(*[MathTex("+", font_size=40, color=S.LABEL_MUTED).move_to([X_R - 0.4, y, 0]) for y in ROWS[1:]],
                      MathTex(r"+\ \cdots", font_size=40, color=S.LABEL_MUTED).move_to([X_R + 0.15, ROWS[2] - 1.15, 0]))
        self.beat("sum of smooth waves", FadeIn(eq, shift=RIGHT * 0.1),
                  *[Create(s) for s in sines], FadeIn(plus), rt=0.8)

        # "didn't buy it": the = becomes a dim ?=
        doubt = MathTex(r"\overset{?}{=}", font_size=60, color=S.LABEL_MUTED).move_to(eq)
        self.beat("didn't buy it", ReplacementTransform(eq, doubt), rt=0.6)

        # "watched it happen": its partial sums, N = 1 → 200, close onto the jumps; the ? goes
        N = ValueTracker(1.0)
        self.add(N)
        s_op = ValueTracker(0.0)
        self.add(s_op)
        summ = V.redraw(lambda: VMobject().set_points_as_corners(to_xy(TH, partial(N.get_value())))
                        .set_stroke(S.INK, 3.5, s_op.get_value()))
        self.add(summ)
        eq2 = MathTex("=", font_size=60, color=S.LABEL).move_to(eq)
        self.beat("watched it happen", s_op.animate.set_value(1.0), prof.animate.set_stroke(opacity=0.3),
                  ReplacementTransform(doubt, eq2), rt=0.5)
        self.play(N.animate(rate_func=lambda u: (200 ** u - 1) / 199).set_value(200.0), run_time=self.snap(2.0))

        # "back to our drawing": the rest goes; the converged line winds into one circle with its arm
        line_pts = to_xy(TH, partial(200.0))
        Lc = 2 * np.pi * H.SEED_R                            # straight segment of the circle's length …
        s_arc = (TH / (2 * np.pi) - 0.5) * Lc
        anchor = H.SEED_CENTER - np.array([0.0, H.SEED_R, 0.0])
        straight = anchor + np.column_stack([s_arc, 0 * s_arc, 0 * s_arc])
        wind = ValueTracker(0.0)
        self.add(wind)

        def winding():
            u = wind.get_value()
            a = min(1.0, u / 0.4)                             # 0–0.4: flatten into the straight segment
            a = a * a * (3 - 2 * a)
            pts = (1 - a) * line_pts + a * straight
            v = 0.0 if u <= 0.4 else ((u - 0.4) / 0.6) ** 1.5    # 0.4–1: curl shut (arc length kept)
            if v > 1e-4:
                rho = H.SEED_R / v
                pts = anchor + np.column_stack([rho * np.sin(s_arc / rho), rho * (1 - np.cos(s_arc / rho)), 0 * s_arc])
            col = ManimColor(S.INK).interpolate(ManimColor(S.FWD), u)
            return VMobject().set_points_as_corners(pts).set_stroke(col, 3.5 - 0.5 * u)
        self.remove(summ)
        wound = V.redraw(winding)
        self.add(wound)
        seed = H.drawing_seed()
        self.beat("back to our drawing", wind.animate.set_value(1.0),
                  FadeOut(VGroup(prof, eq2, sines, plus)), rt=1.1)
        self.remove(wound)
        self.add(seed[0])
        self.play(FadeIn(seed[1:], scale=0.6), run_time=self.snap(0.3))
        self.finish()
