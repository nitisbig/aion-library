"""Ch1 · The puzzle (9.500–21.967 s).

"Here's the puzzle. What number times itself gives minus one? Square two, you
get four. Square minus two, still four. Nothing on the number line works. So we
give it a name, i."

Visual argument: every real square lands at or above zero. The parabola
y = x² (computed, not drawn by hand) never reaches the line y = -1, so no
number on the line solves x² = -1. Then x is renamed i, glowing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V

START, END = V.scene_range("puzzle")

# The math shown on screen, checked before anything is drawn.
assert 2 ** 2 == 4 and (-2) ** 2 == 4
X_MAX = float(np.sqrt(V.Y_RANGE[1]))   # parabola stays inside the y range


class Scene02Puzzle(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.clear()
        ax = V.graph_axes()

        # ── handoff state from the intro: centered number line, arrow at 1 ──
        nl = V.number_line()
        arrow = V.z_arrow(nl.n2p(0), nl.n2p(1))
        self.add(nl, arrow)

        # ── "Here's the puzzle": the line drops and becomes the x-axis ──
        self.play_at(
            self.t("heres the puzzle"),
            FadeOut(arrow, shift=0.1 * DOWN),
            nl.animate.move_to(ax.x_axis),
            lead=0.0, run_time=0.9, rate_func=smooth,
        )
        self.remove(nl)
        self.add(ax.x_axis)

        # ── "What number times itself gives minus one?" ──
        lhs = MathTex("x", r"\cdot", "x", font_size=64, color=S.TEXT)
        rhs = MathTex("=", "-1", font_size=64, color=S.TEXT)
        rhs[1].set_color(S.NEG)
        VGroup(lhs, rhs).arrange(RIGHT, buff=0.25).to_edge(UP, buff=0.55)
        self.play_at(self.t("what number times itself"), Write(lhs), run_time=0.8)
        self.play_at(self.t("minus one"), FadeIn(rhs, shift=0.15 * LEFT), run_time=0.5)

        # x · x → x², in the short breath before "Square two"
        eq = V.sq_eq("x", S.TEXT).to_edge(UP, buff=0.55)
        self.play_at(
            self.t("square two"),
            ReplacementTransform(lhs[0], eq[0]),
            ReplacementTransform(VGroup(lhs[1], lhs[2]), eq[1]),
            ReplacementTransform(rhs[0], eq[2]),
            ReplacementTransform(rhs[1], eq[3]),
            lead=0.57, run_time=0.4,
        )

        # ── "Square two, you get four." ──
        def test_dot(x):
            return Dot(ax.c2p(x, 0), radius=0.11, color=S.REAL).set_z_index(3)

        def riser(dot, x):
            return always_redraw(lambda: DashedLine(
                ax.c2p(x, 0), dot.get_center(), color=S.REAL,
                stroke_width=2.5, dash_length=0.08, stroke_opacity=0.7))

        d2 = test_dot(2)
        self.play_at(self.t("square two"), Create(ax.y_axis),
                     FadeIn(d2, scale=0.4), run_time=0.6)

        r2 = riser(d2, 2)
        self.add(r2)
        self.play_at(self.t("you get"), d2.animate.move_to(ax.c2p(2, 4)),
                     run_time=0.5, rate_func=smooth)
        lab2 = MathTex("2", "^2", "=", "4", font_size=40, color=S.TEXT)
        lab2[0].set_color(S.REAL)
        lab2.next_to(d2, RIGHT, buff=0.25)
        self.play_at(self.t("four"), FadeIn(lab2, shift=0.15 * LEFT),
                     lead=0.1, run_time=0.4)

        # ── "Square minus two, still four." ──
        dm2 = test_dot(-2)
        self.play_at(self.t("square minus two"), FadeIn(dm2, scale=0.4), run_time=0.4)
        rm2 = riser(dm2, -2)
        self.add(rm2)
        self.play_at(self.t("still four"), dm2.animate.move_to(ax.c2p(-2, 4)),
                     lead=0.1, run_time=0.5, rate_func=smooth)
        labm2 = MathTex("(", "-2", ")^2", "=", "4", font_size=40, color=S.TEXT)
        labm2[1].set_color(S.REAL)
        labm2.next_to(dm2, LEFT, buff=0.25)
        mirror = DashedLine(dm2.get_center(), d2.get_center(), color=S.MUTED,
                            stroke_width=2, dash_length=0.1, stroke_opacity=0.6)
        self.play_at(self.t("four", after=self.t("still four")),
                     FadeIn(labm2, shift=0.15 * RIGHT), Create(mirror),
                     lead=0.15, run_time=0.3)

        # ── "Nothing on the number line works." ──
        parabola = ax.plot(lambda x: x ** 2, x_range=[-X_MAX, X_MAX, 0.01],
                           color=S.REAL, stroke_width=5)
        self.play_at(self.t("nothing"), Create(parabola), lead=0.13,
                     run_time=1.1, rate_func=smooth)

        floor = DashedLine(ax.c2p(-3.2, -1), ax.c2p(3.2, -1), color=S.NEG,
                           stroke_width=3.5, dash_length=0.16)
        floor_lab = MathTex("-1", font_size=36, color=S.NEG).next_to(ax.c2p(-3.2, -1), LEFT, buff=0.15)
        gap = Rectangle(width=ax.c2p(3.2, 0)[0] - ax.c2p(-3.2, 0)[0],
                        height=ax.c2p(0, 0)[1] - ax.c2p(0, -1)[1],
                        stroke_width=0, fill_color=S.NEG, fill_opacity=0.10)
        gap.move_to(ax.c2p(0, -0.5)).set_z_index(-1)
        self.play_at(
            self.t("works"),
            FadeIn(floor, shift=0.4 * RIGHT), FadeIn(floor_lab, shift=0.4 * RIGHT),
            FadeIn(gap),
            lead=0.2, run_time=0.5,
        )

        # ── "So we give it a name, i." ──
        graph = VGroup(ax, d2, dm2, r2, rm2, lab2, labm2, mirror, parabola,
                       floor, floor_lab, gap)
        for m in (r2, rm2):
            m.clear_updaters()
        eq_center = V.sq_eq("x", S.TEXT).move_to(V.I_EQ_POS)
        self.play_at(self.t("so we give it a name"),
                     graph.animate.fade(0.8),
                     eq.animate.move_to(eq_center),
                     lead=0.12, run_time=0.8, rate_func=smooth)

        glyph = V.i_glyph()
        halo = V.i_halo(glyph)
        i_eq = V.sq_eq("i", S.I_UNIT).move_to(V.I_EQ_POS)
        self.play_at(
            self.t("i", after=self.t("name")),
            FadeIn(VGroup(glyph), shift=0.2 * UP, scale=0.92),
            FadeIn(halo, shift=0.2 * UP, scale=0.92),
            ReplacementTransform(eq[0], i_eq[0]),
            *[ReplacementTransform(eq[k], i_eq[k]) for k in (1, 2, 3)],
            run_time=0.6, rate_func=smooth,
        )
        self.remove(*i_eq)          # parts were added one by one by the transforms
        self.add(i_eq)
        self.handoff = {"graph": graph, "glyph": glyph, "halo": halo, "i_eq": i_eq}
        self.finish()
