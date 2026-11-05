"""Ch2 · i is a quarter turn (21.967–35.167 s).  The core insight.

"Watch what multiplying by minus one does. It flips the line, a half turn. So I
should be half of that, a quarter turn. Multiply one by i, and it swings straight
up again, and it lands on minus one."

×(-1) is shown as a 180° ROTATION of the whole line (not a mirror flip). Half of
that rotation is a quarter turn: the number whose square is -1. Doing the quarter
turn twice lands on -1, and the two violet quarter arcs merge into the orange
half arc. The vertical (imaginary) axis is born from the arrow's swing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V
from scene_02_puzzle import Scene02Puzzle

START, END = V.scene_range("quarter_turn")

U = 1.3                                   # Manim units per 1
O3 = np.array([0.0, -0.6, 0.0])           # origin of this chapter's line
BADGE_POS = np.array([5.55, 2.95, 0.0])   # small glowing i, top-right

# The math, checked: (-1) is a half turn, i is a quarter turn, i·i = -1.
assert np.isclose(np.exp(1j * np.pi), -1) and np.isclose(np.exp(1j * np.pi / 2), 1j)
assert 1j * 1j == -1


def p(x, y=0.0):
    """Point x + iy in this chapter's coordinates."""
    return O3 + U * np.array([x, y, 0.0])


class Scene03QuarterTurn(V.VideoScene):
    SCENE_START, SCENE_END = START, END
    PREVIOUS = Scene02Puzzle

    def timeline(self):
        h = self.handoff

        # ── the clean number line for this chapter ──
        line = NumberLine(x_range=[-3, 3, 1], length=6 * U, color=S.AXIS, stroke_width=2.5,
                          include_numbers=False, tick_size=0.08)
        line.shift(O3 - line.n2p(0))
        nums = VGroup(*[
            MathTex(str(k).replace("-", "{-}"), font_size=30, color=S.MUTED).next_to(p(k), DOWN, buff=0.25)
            for k in (-3, -2, -1, 1, 2, 3)
        ])
        arrow = V.z_arrow(p(0), p(1))
        riders = VGroup(*[Dot(p(k), radius=0.09, color=S.REAL) for k in (2, 3)])
        spinning = VGroup(line, riders, arrow)

        # ── "Watch…" : Ch1's graph gives way; the i shrinks to a corner badge ──
        badge = Group(h["halo"], h["glyph"])
        badge_target_scale = 0.32
        i_eq = h["i_eq"]
        self.play_at(
            self.t("watch") + 0.24,
            FadeOut(h["graph"], shift=0.1 * DOWN),
            badge.animate.scale(badge_target_scale).move_to(BADGE_POS),
            i_eq.animate.scale(0.55).move_to(BADGE_POS + 0.95 * DOWN),
            FadeIn(VGroup(line, nums), shift=0.15 * UP),
            FadeIn(riders), GrowArrow(arrow),
            lead=0.0, run_time=0.9, rate_func=smooth,
        )

        # ── "…multiplying by minus one" ──
        times_neg = MathTex(r"\times", "(-1)", font_size=56, color=S.NEG).to_corner(UL, buff=0.6)
        self.play_at(self.t("minus", after=23.0), FadeIn(times_neg, shift=0.15 * RIGHT), run_time=0.5)

        # ── "It flips the line" : a half TURN, traced by an orange semicircle ──
        half = Arc(radius=U, start_angle=0, angle=PI, arc_center=O3, color=S.NEG, stroke_width=5)
        self.play_at(
            self.t("flips"),
            Rotate(spinning, PI, about_point=O3),
            Create(half),
            run_time=1.3, rate_func=smooth,
        )
        deg180 = MathTex(r"180^\circ", font_size=36, color=S.NEG).move_to(
            O3 + 1.45 * U * np.array([np.cos(0.78 * PI), np.sin(0.78 * PI), 0]))
        self.play_at(self.t("half turn"), FadeIn(deg180, scale=0.8), lead=0.17, run_time=0.4)

        # ── "So I should be half of that" : line resets, the half turn stays as a ghost ──
        reset = VGroup(line.copy(), riders.copy(), arrow.copy()).rotate(-PI, about_point=O3)
        self.play_at(
            self.t("so", after=26.5),
            FadeOut(spinning), FadeIn(reset),
            half.animate.set_stroke(opacity=0.3), deg180.animate.set_opacity(0.45),
            lead=0.0, run_time=0.5,
        )
        line, riders, arrow = reset
        tick = Line(O3 + (U - 0.2) * UP, O3 + (U + 0.2) * UP, color=S.I_UNIT, stroke_width=6)
        self.play_at(self.t("half of that"), Create(tick), run_time=0.4)

        # ── "a quarter turn" ──
        q1 = Arc(radius=U, start_angle=0, angle=PI / 2, arc_center=O3, color=S.I_UNIT, stroke_width=6)
        times_i = MathTex(r"\times", "i", font_size=56, color=S.I_UNIT)
        times_i.next_to(times_neg, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play_at(
            self.t("quarter turn"),
            AnimationGroup(Create(q1), FadeIn(times_i, shift=0.15 * RIGHT), lag_ratio=0.5),
            run_time=0.8,
        )

        # ── "Multiply one by i" ──
        self.play_at(self.t("one", after=30.0), Indicate(arrow, color=S.Z, scale_factor=1.15),
                     lead=0.11, run_time=0.6)

        # ── "it swings straight up" : the imaginary axis is born from the swing ──
        v_axis = VGroup(
            Line(O3, O3 + 2.6 * U * UP, color=S.AXIS, stroke_width=2.5),
            Line(O3, O3 + 1.6 * U * DOWN, color=S.AXIS, stroke_width=2.5),
            *[Line(p(-0.06, k), p(0.06, k), color=S.AXIS, stroke_width=2.5) for k in (-1, 1, 2)],
        )
        lab_i = MathTex("i", font_size=44, color=S.I_UNIT).next_to(p(0, 1), LEFT, buff=0.3).shift(0.3 * UP)
        self.play_at(
            self.t("swings"),
            AnimationGroup(
                Rotate(arrow, PI / 2, about_point=O3, run_time=1.0, rate_func=smooth),
                Succession(Wait(0.3), Create(v_axis, run_time=0.8)),
                Succession(Wait(0.75), FadeIn(lab_i, run_time=0.35)),
            ),
            lead=0.13, run_time=1.1,
        )

        # ── "again, and it lands on minus one" ──
        q2 = Arc(radius=U, start_angle=PI / 2, angle=PI / 2, arc_center=O3, color=S.I_UNIT, stroke_width=6)
        self.play_at(self.t("again"), Rotate(arrow, PI / 2, about_point=O3), Create(q2),
                     lead=0.1, run_time=1.0, rate_func=smooth)
        assert np.allclose(arrow.get_end(), p(-1), atol=1e-6)   # 1 · i · i = -1
        self.play_at(self.t("lands"), Flash(p(-1), color=S.NEG, flash_radius=0.3, line_length=0.18),
                     lead=0.0, run_time=0.4)

        # ── "minus one" : 1 → i → i·i = -1, and two quarter turns = one half turn ──
        def chain(last):
            m = MathTex("1", r"\to", "i", r"\to", last, "=", "-1", font_size=50, color=S.TEXT)
            m[0].set_color(S.REAL); m[2].set_color(S.I_UNIT); m[4].set_color(S.I_UNIT)
            m[6].set_color(S.NEG)
            return m.move_to(np.array([0, -3.3, 0]))

        row = chain(r"i \cdot i")
        self.play_at(self.t("minus one", after=34.0), FadeIn(row, shift=0.15 * UP),
                     lead=0.4, run_time=0.5)
        row2 = chain("i^2")
        half_bright = Arc(radius=U, start_angle=0, angle=PI, arc_center=O3, color=S.NEG, stroke_width=6)
        self.play(
            ReplacementTransform(VGroup(q1, q2), half_bright),
            *[ReplacementTransform(row[k], row2[k]) for k in range(len(row))],
            run_time=self.snap(0.55), rate_func=smooth,
        )
        self.remove(*row2)
        self.add(row2)

        self.handoff = {
            "line": line, "v_axis": v_axis, "arrow": arrow,
            "fade": Group(nums, riders, half, deg180, tick, half_bright, times_neg, times_i,
                          lab_i, row2, badge, i_eq),
        }
        self.finish()
