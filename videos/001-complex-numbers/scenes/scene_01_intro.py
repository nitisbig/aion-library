"""Intro · hook (0.000–9.500 s).

"What if a number could turn, not just grow or shrink but spin? That's a complex
number, and in one minute you'll see it isn't complex at all."

A number arrow does what numbers "can't": it turns. The domain-coloring plate
(moderngl, hue = argument) blooms behind it with its hue locked to the arrow's
angle. Then a 3-shot trailer of the payoffs: the line folds into a plane,
i² = -1, the plane rotates 90°. Everything collapses back to the quiet number
line that Ch1 starts from.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V

START, END = V.scene_range("intro")
U = V.X_LEN / (V.X_RANGE[1] - V.X_RANGE[0])      # 1.3 Manim units per 1


class Scene01Intro(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.clear()
        nl = V.number_line()
        O = nl.n2p(0)

        # Arrow is driven by (length, angle) trackers, so the plate can follow it.
        length = ValueTracker(1.0)
        theta = ValueTracker(0.0)
        arrow = always_redraw(lambda: V.polar_arrow(O, U * length.get_value(), theta.get_value()))

        # ── "What if a number…" : the line and the arrow ──
        start_arrow = V.z_arrow(O, O + U * RIGHT)
        self.play_at(
            self.t("what"),
            LaggedStart(FadeIn(nl, shift=0.2 * UP), GrowArrow(start_arrow), lag_ratio=0.35),
            lead=0.06, run_time=1.0, rate_func=smooth,
        )
        self.remove(start_arrow)
        self.add(arrow)

        # ── "could turn" : a small tease of a turn ──
        self.play_at(self.t("turn"), theta.animate.set_value(15 * DEGREES),
                     run_time=0.6, rate_func=there_and_back)

        # ── "grow" / "shrink" : what a number usually does ──
        self.play_at(self.t("grow"), length.animate.set_value(2.0), run_time=0.5, rate_func=smooth)
        self.play_at(self.t("shrink"), length.animate.set_value(0.5), lead=0.13,
                     run_time=0.5, rate_func=smooth)

        # ── "but spin" : full turn, trail, color plate blooms in ──
        plate_op = ValueTracker(0.0)
        plate = V.domain_plate(theta, plate_op, origin=O[:2], unit=U)
        trail = V.trailing_arc(O, lambda: U * length.get_value(), theta)
        self.add(plate, trail)
        self.bring_to_front(arrow)
        self.play_at(
            self.t("spin"),
            theta.animate(rate_func=rush_from).set_value(TAU),
            length.animate(rate_func=smooth).set_value(1.0),
            plate_op.animate(rate_func=smooth).set_value(0.25),
            run_time=1.0,
        )
        # freeze: from here the arrow is a plain mobject (can fade / transform)
        arrow.clear_updaters()
        trail.clear_updaters()
        self.play(FadeOut(trail), run_time=self.snap(0.3))

        # ── trailer 1 · "That's a complex…" : the line folds into a plane ──
        grid = NumberPlane(
            x_range=[-6, 6, 1], y_range=[-6, 6, 1], x_length=12 * U, y_length=12 * U,
            background_line_style={"stroke_color": S.GRID, "stroke_width": 1.5, "stroke_opacity": 0.55},
            axis_config={"stroke_color": S.AXIS, "stroke_width": 2.5},
            faded_line_ratio=0,
        ).shift(O)
        v_axis = Line(O + 3.4 * DOWN, O + 3.4 * UP, color=S.AXIS, stroke_width=2.5)
        self.play_at(
            self.t("complex"),
            AnimationGroup(
                GrowFromCenter(v_axis),
                LaggedStart(*[Create(l) for l in grid.background_lines], lag_ratio=0.02),
                lag_ratio=0.25,
            ),
            run_time=1.0,
        )

        # ── trailer 2 · "in one minute" : i² = -1 ──
        teaser = V.sq_eq("i", S.I_UNIT).scale(1.5).move_to(ORIGIN)
        teaser_halo = V.i_halo(teaser[0])
        shot1 = VGroup(grid.background_lines, v_axis, nl, arrow)
        self.play_at(
            self.t("one minute"),
            FadeOut(shot1, scale=1.04),
            FadeIn(Group(teaser_halo, teaser), scale=0.94),
            plate_op.animate.set_value(0.12),
            lead=0.34, run_time=0.6, rate_func=smooth,
        )

        # ── trailer 3 · "see" : the whole plane turns a quarter ──
        plane3 = NumberPlane(
            x_range=[-6, 6, 1], y_range=[-6, 6, 1], x_length=12 * U, y_length=12 * U,
            background_line_style={"stroke_color": S.GRID, "stroke_width": 1.5, "stroke_opacity": 0.55},
            axis_config={"stroke_color": S.AXIS, "stroke_width": 2.5},
            faded_line_ratio=0,
        ).shift(O)
        z3 = V.z_arrow(O, O + U * np.array([2.0, 1.0, 0.0]))
        shot3 = VGroup(plane3, z3)
        self.play_at(
            self.t("see"),
            FadeOut(Group(teaser_halo, teaser), scale=1.04),
            FadeIn(shot3, scale=0.96),
            plate_op.animate.set_value(0.25),
            lead=0.25, run_time=0.3,
        )
        self.play(
            Rotate(shot3, PI / 2, about_point=O),
            theta.animate.increment_value(PI / 2),
            run_time=self.snap(0.6), rate_func=smooth,
        )

        # ── "isn't complex at all" : collapse back to the quiet line ──
        end_arrow = V.z_arrow(O, O + U * RIGHT)
        self.play_at(
            self.t("complex", after=8.0),
            FadeOut(shot3, scale=0.92),
            FadeIn(nl, shift=0.1 * UP),
            GrowArrow(end_arrow),
            plate_op.animate.set_value(0.0),
            lead=0.08, run_time=0.7, rate_func=smooth,
        )
        self.remove(plate)
        self.handoff = {"nl": nl, "arrow": end_arrow}
        self.finish()
