"""Ch3 · The complex plane (35.167–46.317 s).

"Now the line opens into a plane. Three plus two i is three steps right, two
steps up. Multiply by i, and the arrow turns 90 degrees to minus two plus three i."

The two axes from Ch2 become a full grid. 3 + 2i is walked out as three blue
steps and two red steps. Multiplying by i rotates the whole grid (and the arrow,
and both step-legs) a quarter turn about 0: the blue leg turns vertical and the
red leg horizontal, landing on -2 + 3i.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V
from scene_03_quarter_turn import Scene03QuarterTurn

START, END = V.scene_range("plane")

U = 0.95                                  # Manim units per 1
O4 = np.array([0.5, -0.45, 0.0])          # origin of the plane
Z0, Z1 = 3 + 2j, 1j * (3 + 2j)            # the number, and the number times i

# Math check: i(3+2i) = 3i + 2i² = -2 + 3i, same length, 90° apart.
assert Z1 == -2 + 3j
assert np.isclose(abs(Z0), abs(Z1)) and np.isclose(np.angle(Z1) - np.angle(Z0), np.pi / 2)


def p(x, y=0.0):
    return O4 + U * np.array([x, y, 0.0])


class Scene04Plane(V.VideoScene):
    SCENE_START, SCENE_END = START, END
    PREVIOUS = Scene03QuarterTurn

    def timeline(self):
        h = self.handoff

        plane = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-5, 5, 1], x_length=10 * U, y_length=10 * U,
            axis_config={"stroke_color": S.AXIS, "stroke_width": 2.5},
            background_line_style={"stroke_width": 1.5, "stroke_opacity": 0.45},
            faded_line_ratio=0,
        ).shift(O4)
        grid = plane.background_lines
        for ln in grid:   # vertical lines (Re = const) blue, horizontal (Im = const) red
            vertical = abs(ln.get_start()[0] - ln.get_end()[0]) < 1e-6
            ln.set_stroke(color=S.REAL if vertical else S.IMAG, opacity=0.6 if vertical else 0.45)

        def axis_dist(ln):
            c = ln.get_center()
            vertical = abs(ln.get_start()[0] - ln.get_end()[0]) < 1e-6
            return abs(c[0] - O4[0]) if vertical else abs(c[1] - O4[1])

        # ── "Now the line…" : Ch2 clears, its two axes become the plane's axes ──
        self.play_at(
            self.t("now the line"),
            FadeOut(h["fade"]), FadeOut(h["arrow"]),
            ReplacementTransform(h["line"], plane.x_axis),
            ReplacementTransform(h["v_axis"], plane.y_axis),
            lead=0.0, run_time=0.6, rate_func=smooth,
        )

        # ── "opens into a plane" ──
        ordered = sorted(grid, key=axis_dist)
        self.play_at(self.t("opens"), LaggedStart(*[Create(l) for l in ordered], lag_ratio=0.06),
                     run_time=1.2)
        re_lab = MathTex(r"\mathrm{Re}", font_size=36, color=S.REAL).move_to(p(5.0, -0.42))
        im_lab = MathTex(r"\mathrm{Im}", font_size=36, color=S.IMAG).move_to(p(0.55, 3.95))
        self.play_at(self.t("plane"), FadeIn(re_lab), FadeIn(im_lab), lead=0.0, run_time=0.3)

        # ── label panel (sized for the final equation, so it never resizes) ──
        full = MathTex("i", r"\cdot", "(", "3", "+", "2i", ")", "=", "-2", "+", "3i",
                       font_size=52, color=S.TEXT)
        for k, c in ((0, S.I_UNIT), (3, S.REAL), (5, S.IMAG), (8, S.REAL), (10, S.IMAG)):
            full[k].set_color(c)
        full.to_corner(UL, buff=0.6)
        def panel_for(m):   # masks the grid behind the label; grows with it
            return BackgroundRectangle(m, color=V.BG, fill_opacity=0.85, buff=0.22)

        lbl1 = MathTex("3", "+", "2i", font_size=52, color=S.TEXT)
        lbl1[0].set_color(S.REAL); lbl1[2].set_color(S.IMAG)
        lbl1.move_to(full[3:6])
        panel = panel_for(lbl1)

        # ── "Three plus two i" ──
        self.play_at(self.t("three plus two i"), FadeIn(panel), Write(lbl1), lead=0.12, run_time=0.8)

        # ── "three steps right" : three blue hops ──
        dot = Dot(p(0), radius=0.09, color=S.Z).set_z_index(5)
        leg_re = VGroup(*[DashedLine(p(k), p(k + 1), color=S.REAL, stroke_width=4, dash_length=0.09)
                          for k in range(3)])
        hops_re = [AnimationGroup(MoveAlongPath(dot, ArcBetweenPoints(p(k), p(k + 1), angle=-PI / 2)),
                                  Create(leg_re[k]), run_time=0.35) for k in range(3)]
        self.add(dot)
        self.play_at(self.t("three steps right"), Succession(*hops_re), lead=0.12, run_time=1.05)

        # ── "two steps up" : two red hops, then the arrow ──
        leg_im = VGroup(*[DashedLine(p(3, k), p(3, k + 1), color=S.IMAG, stroke_width=4, dash_length=0.09)
                          for k in range(2)])
        hops_im = [AnimationGroup(MoveAlongPath(dot, ArcBetweenPoints(p(3, k), p(3, k + 1), angle=PI / 2)),
                                  Create(leg_im[k]), run_time=0.35) for k in range(2)]
        self.play_at(self.t("two steps up"), Succession(*hops_im), lead=0.08, run_time=0.7)
        arrow = V.z_arrow(p(0), p(Z0.real, Z0.imag))
        self.play(GrowArrow(arrow), run_time=self.snap(0.35), rate_func=smooth)

        # ── "Multiply by i" ──
        lbl2 = MathTex(*[m.tex_string for m in full[0:7]], font_size=52, color=S.TEXT)
        for k, c in ((0, S.I_UNIT), (3, S.REAL), (5, S.IMAG)):
            lbl2[k].set_color(c)
        lbl2.move_to(full[0:7])
        ghost = VGroup(arrow.copy(), dot.copy()).set_opacity(0.3)
        self.play_at(self.t("multiply by i"),
                     TransformMatchingTex(lbl1, lbl2), FadeIn(ghost),
                     Transform(panel, panel_for(lbl2)),
                     lead=0.11, run_time=0.6)

        # ── "the arrow turns 90 degrees" : the whole plane turns a quarter ──
        a0 = np.angle(Z0)
        arc90 = Arc(radius=0.6, start_angle=a0, angle=PI / 2, arc_center=O4, color=S.I_UNIT, stroke_width=5)
        mid = a0 + PI / 4
        deg90 = MathTex(r"90^\circ", font_size=34, color=S.I_UNIT).move_to(
            O4 + 1.0 * np.array([np.cos(mid), np.sin(mid), 0]))
        turning = VGroup(grid, arrow, dot, leg_re, leg_im)
        self.play_at(
            self.t("arrow"),
            AnimationGroup(
                Rotate(turning, PI / 2, about_point=O4, run_time=1.4, rate_func=smooth),
                Create(arc90, run_time=1.4, rate_func=smooth),
                Succession(Wait(0.85), FadeIn(deg90, scale=0.8, run_time=0.4)),
            ),
            lead=0.14, run_time=1.4,
        )
        assert np.allclose(arrow.get_end(), p(Z1.real, Z1.imag), atol=1e-6)

        # ── "to minus two plus three i" ──
        rhs = full[7:11]
        self.play_at(self.t("minus two plus three i"),
                     FadeIn(rhs, shift=0.15 * LEFT), Indicate(dot, color=S.Z, scale_factor=1.6),
                     Transform(panel, panel_for(full)),
                     lead=0.12, run_time=0.7)

        self.remove(*lbl2)
        label = VGroup(*lbl2, *rhs)
        self.add(label)
        self.handoff = {
            "arrow": arrow, "dot": dot, "rhs_value": rhs, "label_rest": lbl2,
            "fade": Group(plane, re_lab, im_lab, panel, ghost, leg_re, leg_im, arc90, deg90),
        }
        self.finish()
