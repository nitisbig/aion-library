"""Outro · recap (46.317–58.850 s, incl. the 2.0 s silent tail).

"A complex number is a point with a direction. i is a quarter turn, and two
quarter turns face backward. That's why I squared is minus one, not imaginary,
just rotation."

Three skia cards light up one per phrase (a point with a direction / a quarter
turn / two quarter turns = half turn → i² = -1). "imaginary" is struck through,
then a single arrow makes one slow full turn while the domain-coloring plate
blooms back in behind it, bookending the intro.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.cards import card_image
import shared as V
from scene_04_plane import Scene04Plane

START, END = V.scene_range("outro")

CARD_W, CARD_H = 3.9, 3.0
CARD_Y = 0.35
CARD_X = (-4.35, 0.0, 4.35)
R = 1.1                       # radius of the quarter-turn diagrams inside cards 2 and 3
R_FINAL = 1.6                 # radius of the closing spin

assert np.isclose(np.exp(1j * np.pi / 2) ** 2, -1)   # two quarter turns = -1


def faint_axes(o, w=1.6, up=1.3, down=0.35):
    return VGroup(
        Line(o + w * LEFT, o + w * RIGHT, color=S.AXIS, stroke_width=2, stroke_opacity=0.5),
        Line(o + down * DOWN, o + up * UP, color=S.AXIS, stroke_width=2, stroke_opacity=0.5),
    )


class Scene05Outro(V.VideoScene):
    SCENE_START, SCENE_END = START, END
    PREVIOUS = Scene04Plane

    def timeline(self):
        h = self.handoff
        centers = [np.array([x, CARD_Y, 0.0]) for x in CARD_X]
        cards = [card_image(CARD_W, CARD_H).move_to(c).set_z_index(-10) for c in centers]
        for c in cards[1:]:
            c.set_opacity(0.3)

        # ── card 1 content: a point with a direction (the -2 + 3i from Ch3) ──
        u1 = 0.5
        o1 = centers[0] + np.array([0.55, -1.05, 0])
        axes1 = faint_axes(o1, w=1.25, up=2.0, down=0.3)
        tip1 = o1 + u1 * np.array([-2, 3, 0])
        arrow1 = V.z_arrow(o1, tip1)
        dot1 = Dot(tip1, radius=0.07, color=S.Z).set_z_index(5)
        val1 = MathTex("-2", "+", "3i", font_size=34, color=S.TEXT)
        val1[0].set_color(S.REAL); val1[2].set_color(S.IMAG)
        val1.next_to(tip1, LEFT, buff=0.15)

        # ── "A complex number…" : Ch3's plane condenses into card 1 ──
        rhs = h["rhs_value"]
        self.play_at(
            self.t("a complex number"),
            FadeOut(h["fade"]), FadeOut(h["label_rest"]), FadeOut(rhs[0]),
            ReplacementTransform(h["arrow"], arrow1),
            ReplacementTransform(h["dot"], dot1),
            ReplacementTransform(rhs[1:], val1),
            FadeIn(cards[0], scale=0.96), FadeIn(axes1),
            *[FadeIn(c, scale=0.96) for c in cards[1:]],
            lead=0.0, run_time=1.0, rate_func=smooth,
        )
        self.play_at(self.t("point"), Flash(dot1, color=S.Z, flash_radius=0.22, line_length=0.12),
                     lead=0.11, run_time=0.5)
        self.play_at(self.t("direction"), Indicate(arrow1, color=S.Z, scale_factor=1.08),
                     lead=0.14, run_time=0.5)

        # ── "i is a quarter turn" : card 2 ──
        o2 = centers[1] + np.array([0, -0.75, 0])
        axes2 = faint_axes(o2)
        arrow2 = V.z_arrow(o2, o2 + R * RIGHT)
        arc2 = Arc(radius=R, start_angle=0, angle=PI / 2, arc_center=o2, color=S.I_UNIT, stroke_width=6)
        xi = MathTex(r"\times", "i", font_size=44, color=S.I_UNIT).move_to(centers[1] + np.array([-1.3, 1.05, 0]))
        self.play_at(
            self.t("i is a quarter turn", after=48.5),
            AnimationGroup(
                cards[1].animate(run_time=0.4).set_opacity(1.0),
                FadeIn(VGroup(axes2, arrow2), run_time=0.3),
                Succession(Wait(0.3), AnimationGroup(
                    Rotate(arrow2, PI / 2, about_point=o2, rate_func=smooth),
                    Create(arc2, rate_func=smooth), run_time=0.6)),
                Succession(Wait(0.55), FadeIn(xi, shift=0.1 * RIGHT, run_time=0.35)),
            ),
            lead=0.14, run_time=0.9,
        )

        # ── "two quarter turns" : card 3 ──
        o3 = centers[2] + np.array([0, -0.75, 0])
        axes3 = faint_axes(o3)
        arrow3 = V.z_arrow(o3, o3 + R * RIGHT)
        a3 = [Arc(radius=R, start_angle=k * PI / 2, angle=PI / 2, arc_center=o3,
                  color=S.I_UNIT, stroke_width=6) for k in (0, 1)]
        self.play_at(
            self.t("two quarter turns"),
            AnimationGroup(
                cards[2].animate(run_time=0.35).set_opacity(1.0),
                FadeIn(VGroup(axes3, arrow3), run_time=0.25),
                Succession(
                    Wait(0.25),
                    AnimationGroup(Rotate(arrow3, PI / 2, about_point=o3), Create(a3[0]), run_time=0.4),
                    AnimationGroup(Rotate(arrow3, PI / 2, about_point=o3), Create(a3[1]), run_time=0.4),
                ),
            ),
            lead=0.11, run_time=1.05,
        )
        assert np.allclose(arrow3.get_end(), o3 + R * LEFT, atol=1e-6)

        # ── "face backward" : the two quarter arcs are one half turn ──
        half3 = Arc(radius=R, start_angle=0, angle=PI, arc_center=o3, color=S.NEG, stroke_width=6)
        self.play_at(
            self.t("backward"),
            ReplacementTransform(VGroup(*a3), half3),
            Flash(o3 + R * LEFT, color=S.NEG, flash_radius=0.25, line_length=0.14),
            lead=0.13, run_time=0.6,
        )

        # ── "That's why I squared is minus one" ──
        eq = V.sq_eq("i", S.I_UNIT).scale(0.85).next_to(cards[2], DOWN, buff=0.35)
        content1 = VGroup(axes1, arrow1, dot1, val1)
        content2 = VGroup(axes2, arrow2, arc2, xi)
        self.play_at(
            self.t("squared"),
            Write(eq),
            cards[0].animate.set_opacity(0.5), cards[1].animate.set_opacity(0.5),
            content1.animate.fade(0.5), content2.animate.fade(0.5),
            lead=0.31, run_time=0.9,
        )

        # ── "not imaginary" ──
        word = Text("imaginary", font="Noto Serif", slant=ITALIC, font_size=72, color=S.MUTED)
        content3 = VGroup(axes3, arrow3, half3)
        everything = Group(*cards, content1, content2, content3, eq)
        self.play_at(
            self.t("not", after=54.0),
            AnimationGroup(FadeOut(everything, scale=0.97), FadeIn(word, scale=1.04), lag_ratio=0.5),
            lead=0.09, run_time=0.7,
        )
        strike = Line(word.get_left() + 0.15 * LEFT, word.get_right() + 0.15 * RIGHT,
                      color=S.TEXT, stroke_width=4)
        self.play_at(self.t("imaginary") + 0.5, Create(strike), lead=0.0, run_time=0.35)

        # ── "just rotation" : one slow full turn, the color plate blooms back ──
        theta = ValueTracker(0.0)
        a_op = ValueTracker(0.0)
        plate_op = ValueTracker(0.0)
        plate = V.domain_plate(theta, plate_op, origin=(0.0, 0.0), unit=R_FINAL)
        circle = Circle(radius=R_FINAL, color=S.GHOST, stroke_width=2)
        arrow = always_redraw(lambda: V.polar_arrow(ORIGIN, R_FINAL, theta.get_value(), a_op.get_value()))
        trail = V.trailing_arc(ORIGIN, lambda: R_FINAL, theta)
        self.add(plate, trail, arrow)
        self.play_at(
            self.t("rotation"),
            AnimationGroup(
                FadeOut(VGroup(word, strike), run_time=0.4),
                FadeIn(circle, run_time=0.5),
                a_op.animate(run_time=0.4).set_value(1.0),
                theta.animate(run_time=2.0, rate_func=smooth).set_value(TAU),
                Succession(Wait(0.1), plate_op.animate(run_time=1.0, rate_func=smooth).set_value(0.28)),
            ),
            lead=0.12, run_time=2.0,
        )

        # ── tail: hold, then fade to black ──
        trail.clear_updaters()
        self.play_at(
            END - 0.65,
            FadeOut(circle), FadeOut(trail),
            a_op.animate.set_value(0.0), plate_op.animate.set_value(0.0),
            lead=0.0, run_time=0.65, rate_func=smooth,
        )
        self.finish()
