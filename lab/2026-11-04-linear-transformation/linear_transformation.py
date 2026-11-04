"""45-second exploration: what a linear transformation is (silent, captioned).

Story: basis vectors -> v as a recipe of î, ĵ -> transform space -> v follows the
same recipe -> where î and ĵ land *is* the matrix -> A v computed column-wise.

Every moving object is driven by one ValueTracker t in [0, 1] through
M(t) = (1 - t) I + t A, which is exactly the path ApplyMatrix would take. So the
grid, vectors and labels can never drift out of sync.
"""

import numpy as np
from manim import *

from aion import style as S
from aion.progress import ProgressScene

A = np.array([[2.0, -1.0], [1.0, 1.0]])
I2 = np.eye(2)
I_VEC = np.array([1.0, 0.0])
J_VEC = np.array([0.0, 1.0])
V = np.array([2.0, 1.0])  # v = 2 î + 1 ĵ  ->  A v = (3, 3)

TOTAL = 45.0


def to3(p):
    return np.array([p[0], p[1], 0.0])


def tex_colored(*parts, size=S.MATH_SIZE):
    """MathTex with semantic colors applied per substring."""
    colors = {r"\hat{\imath}": S.I_HAT, r"\hat{\jmath}": S.J_HAT, r"\vec{v}": S.VEC}
    m = MathTex(*parts, font_size=size, color=S.TEXT)
    for sub in m.submobjects:
        if sub.tex_string in colors:
            sub.set_color(colors[sub.tex_string])
    return m


class LinearTransformation(ProgressScene):
    TOTAL_DURATION = TOTAL
    def wait_until(self, t):
        dt = t - self.renderer.time
        if dt > 1e-3:
            self.wait(dt)

    def caption(self, text):
        c = Text(text, font_size=S.CAPTION_SIZE, color=S.TEXT)
        c.add_background_rectangle(color=S.PANEL, opacity=S.PANEL_OPACITY, buff=0.15)
        return c.to_edge(DOWN, buff=0.35)

    def swap_caption(self, old, new, *extra, run_time=S.FADE):
        anims = [FadeIn(new, shift=0.15 * UP), *extra]
        if old is not None:
            anims.insert(0, FadeOut(old, shift=0.15 * UP))
        self.play(*anims, run_time=run_time)
        return new

    def construct(self):
        self.camera.background_color = S.BG
        t = ValueTracker(0.0)

        def mat():
            return (1 - t.get_value()) * I2 + t.get_value() * A

        def tracked_arrow(p, q, color, opacity=1.0, width=S.VECTOR_STROKE):
            p, q = np.asarray(p, float), np.asarray(q, float)

            def build():
                m = mat()
                return Arrow(
                    to3(m @ p), to3(m @ q), buff=0, color=color,
                    stroke_width=width, max_tip_length_to_length_ratio=0.22,
                ).set_opacity(opacity)

            return always_redraw(build)

        def tracked_label(tex, coords, color, direction):
            lbl = MathTex(tex, color=color, font_size=44)
            lbl.add_updater(lambda m: m.next_to(to3(mat() @ coords), direction, buff=0.15))
            return lbl.update()

        # ── 0–5 s: title ──────────────────────────────────────────────
        title = Text("Linear Transformations", font_size=S.TITLE_SIZE, weight=BOLD, color=S.TEXT)
        sub = Text("what a matrix does to space", font_size=30, color=S.MUTED)
        sub.next_to(title, DOWN, buff=0.35)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub, shift=0.2 * UP), run_time=1.0)
        self.wait_until(4.0)
        self.play(FadeOut(VGroup(title, sub), shift=0.2 * UP), run_time=1.0)

        # ── 5–15 s: the plane, basis vectors, v as a recipe ───────────
        plane_kw = dict(
            x_range=[-10, 10, 1], y_range=[-10, 10, 1],
            background_line_style={"stroke_color": S.GRID, "stroke_width": 2, "stroke_opacity": 0.8},
            axis_config={"stroke_color": S.AXIS, "stroke_width": 3},
        )
        base = NumberPlane(**plane_kw)
        ghost = NumberPlane(**plane_kw).set_stroke(color=S.GHOST, width=1.5, opacity=0.35)
        plane = base.copy()
        self.play(Create(plane, lag_ratio=0.05), run_time=2.0)
        plane.add_updater(lambda m: m.become(base.copy().apply_matrix(mat(), about_point=ORIGIN)))

        i_arrow = tracked_arrow([0, 0], I_VEC, S.I_HAT)
        j_arrow = tracked_arrow([0, 0], J_VEC, S.J_HAT)
        i_lbl = tracked_label(r"\hat{\imath}", I_VEC, S.I_HAT, DOWN)
        j_lbl = tracked_label(r"\hat{\jmath}", J_VEC, S.J_HAT, RIGHT)
        cap = self.caption("Two basis vectors:  î  and  ĵ")
        self.play(
            GrowArrow(i_arrow), GrowArrow(j_arrow),
            FadeIn(i_lbl), FadeIn(j_lbl), FadeIn(cap, shift=0.15 * UP),
            run_time=1.5,
        )
        self.wait_until(10.0)

        v_arrow = tracked_arrow([0, 0], V, S.VEC, width=8)
        step_i = tracked_arrow([0, 0], 2 * I_VEC, S.I_HAT, opacity=0.5, width=5)
        step_j = tracked_arrow(2 * I_VEC, V, S.J_HAT, opacity=0.5, width=5)
        cap = self.swap_caption(cap, self.caption("Every vector is a recipe of î and ĵ"),
                                GrowArrow(v_arrow), run_time=1.0)
        self.play(Create(step_i), run_time=0.8)
        self.play(Create(step_j), run_time=0.8)

        # Build the whole top-left panel up front so its background fits everything.
        eq1 = tex_colored(r"\vec{v}", "=", "2", r"\hat{\imath}", "+", "1", r"\hat{\jmath}")
        eq2 = tex_colored("T(", r"\vec{v}", ")", "=", "2", "T(", r"\hat{\imath}", ")",
                          "+", "1", "T(", r"\hat{\jmath}", ")")
        a_matrix = Matrix([[2, -1], [1, 1]], element_to_mobject_config={"color": S.TEXT})
        a_matrix.scale(0.75)
        a_matrix.get_columns()[0].set_color(S.I_HAT)
        a_matrix.get_columns()[1].set_color(S.J_HAT)
        a_eq = MathTex("A", "=", font_size=S.MATH_SIZE, color=S.TEXT)
        a_row = VGroup(a_eq, a_matrix).arrange(RIGHT, buff=0.2)
        panel_layout = VGroup(eq2, a_row).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        panel_layout.to_corner(UL, buff=0.45)
        eq1.move_to(eq2, aligned_edge=LEFT)
        def panel_around(mob):
            r = SurroundingRectangle(mob, buff=0.25, corner_radius=0.12)
            return r.set_fill(S.PANEL, S.PANEL_OPACITY).set_stroke(S.MUTED, 1, opacity=0.4)

        panel = panel_around(eq2)               # grows to fit the matrix later
        panel_full = panel_around(panel_layout)
        self.play(FadeIn(panel), Write(eq1), run_time=1.2)
        self.wait_until(15.0)

        # ── 15–24 s: transform space ─────────────────────────────────
        self.add(ghost)
        self.bring_to_back(ghost)
        cap = self.swap_caption(cap, self.caption("Now apply a linear transformation T"))
        self.wait_until(16.0)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.wait_until(20.5)
        cap = self.swap_caption(
            cap, self.caption("Grid lines stay straight, parallel, evenly spaced. The origin stays put."),
        )
        self.play(Flash(ORIGIN, color=S.TEXT, flash_radius=0.4), run_time=1.0)
        self.wait_until(24.5)

        # ── 24.5–29 s: v follows the same recipe ──────────────────────
        cap = self.swap_caption(cap, self.caption("v follows the same recipe, with the new î and ĵ"))
        self.play(TransformMatchingTex(eq1, eq2), run_time=1.2)
        self.play(Indicate(step_i, scale_factor=1.05), Indicate(step_j, scale_factor=1.05),
                  run_time=1.0)
        self.wait_until(29.0)

        # ── 29–35 s: where î, ĵ land = the columns of the matrix ──────
        i_coords = Matrix([[2], [1]], element_to_mobject_config={"color": S.I_HAT}).scale(0.6)
        j_coords = Matrix([[-1], [1]], element_to_mobject_config={"color": S.J_HAT}).scale(0.6)
        i_coords.next_to(to3(A @ I_VEC), RIGHT, buff=0.25)
        j_coords.next_to(to3(A @ J_VEC), LEFT, buff=0.25)
        new_cap = self.caption("î lands on (2, 1).   ĵ lands on (−1, 1).")
        self.play(FadeOut(step_i), FadeOut(step_j), FadeOut(cap, shift=0.15 * UP),
                  FadeIn(new_cap, shift=0.15 * UP), FadeIn(i_coords), FadeIn(j_coords),
                  run_time=1.0)
        cap = new_cap
        self.wait_until(31.5)

        cap = self.swap_caption(cap, self.caption("Those landing spots are the columns of the matrix"))
        self.play(Transform(panel, panel_full), run_time=0.5)
        self.play(
            Write(a_eq), FadeIn(a_matrix.get_brackets()),
            TransformFromCopy(i_coords.get_entries(), a_matrix.get_columns()[0]),
            TransformFromCopy(j_coords.get_entries(), a_matrix.get_columns()[1]),
            run_time=1.5,
        )
        self.wait_until(35.0)

        # ── 35–45 s: compute A v column by column ────────────────────
        prod = MathTex(
            r"\begin{bmatrix}2 & -1\\ 1 & 1\end{bmatrix}", r"\begin{bmatrix}2\\ 1\end{bmatrix}",
            "=", "2", r"\begin{bmatrix}2\\ 1\end{bmatrix}", "+", "1",
            r"\begin{bmatrix}-1\\ 1\end{bmatrix}", "=", r"\begin{bmatrix}3\\ 3\end{bmatrix}",
            font_size=S.MATH_SIZE, color=S.TEXT,
        )
        prod[1].set_color(S.VEC)
        prod[4].set_color(S.I_HAT)
        prod[7].set_color(S.J_HAT)
        prod[9].set_color(S.VEC)
        prod.move_to(2.2 * DOWN)
        prod_bg = BackgroundRectangle(prod, color=S.PANEL, fill_opacity=S.PANEL_OPACITY, buff=0.2)
        self.play(FadeOut(cap, shift=0.15 * UP), FadeIn(prod_bg), Write(prod), run_time=2.0)
        cap = None
        self.wait_until(38.0)
        tip = Dot(to3(A @ V), color=S.VEC, radius=0.09)
        self.play(Indicate(prod[9], color=S.VEC), FadeIn(tip, scale=2),
                  Flash(to3(A @ V), color=S.VEC), run_time=1.2)
        self.wait_until(41.0)

        final = self.caption("A matrix is just a record of where î and ĵ land.")
        self.swap_caption(None, final, run_time=1.0)
        self.wait_until(TOTAL)
