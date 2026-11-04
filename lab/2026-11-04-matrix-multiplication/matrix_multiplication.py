"""30-second exploration: how matrix multiplication works (silent, captioned).

Story: A (2x3) times B (3x2) -> inner sizes must match -> each entry of C is
row i of A dotted with column j of B. The first entry is computed slowly, term by
term; later entries speed up, so the viewer learns the rhythm and then sees it
repeat. It ends on the general formula c_ij = sum_k a_ik b_kj.

All numbers come from numpy (C = A @ B), so nothing on screen is typed by hand.
"""

import numpy as np
from manim import *

from aion import style as S
from aion.progress import ProgressScene

A = np.array([[1, 2, 3], [4, 5, 6]])
B = np.array([[7, 8], [9, 10], [11, 12]])
C = A @ B  # [[58, 64], [139, 154]]

ROW = S.ACCENT   # rows of A, and the index i
COL = S.VEC      # columns of B, and the index j
RES = S.I_HAT    # finished entries of C

TOTAL = 30.0


def mat(values, **kw):
    return Matrix(
        [[str(v) for v in row] for row in values],
        element_to_mobject_config={"font_size": S.MATH_SIZE, "color": S.TEXT},
        bracket_config={"color": S.MUTED},
        h_buff=1.0,
        **kw,
    )


class MatrixMultiplication(ProgressScene):
    TOTAL_DURATION = TOTAL

    def wait_until(self, t):
        dt = t - self.renderer.time
        if dt > 1e-3:
            self.wait(dt)

    def caption(self, text):
        c = Text(text, font_size=S.CAPTION_SIZE, color=S.TEXT)
        return c.to_edge(DOWN, buff=0.45)

    def swap_caption(self, old, new, run_time=S.FADE):
        anims = [FadeIn(new, shift=0.15 * UP)]
        if old is not None:
            anims.insert(0, FadeOut(old, shift=0.15 * UP))
        self.play(*anims, run_time=run_time)
        return new

    # ── one entry of C ───────────────────────────────────────────────
    def compute_entry(self, i, j, speed, row_box, col_box):
        """Highlight row i / column j, build the dot product, drop the result into C.

        speed: 1.0 = slow and term-by-term, smaller = faster.
        """
        a_row = self.mA.get_rows()[i]
        b_col = self.mB.get_columns()[j]
        target_row = SurroundingRectangle(a_row, color=ROW, buff=0.12, corner_radius=0.08)
        target_col = SurroundingRectangle(b_col, color=COL, buff=0.12, corner_radius=0.08)
        slot = self.mC.get_rows()[i][j]
        slot_box = SurroundingRectangle(slot, color=S.MUTED, buff=0.1, corner_radius=0.06)

        # move the highlight boxes (continuity: the same boxes slide around)
        if row_box is None:
            row_box, col_box = target_row, target_col
            self.play(Create(row_box), Create(col_box), FadeIn(slot_box), run_time=0.8 * speed + 0.2)
        else:
            self.play(
                Transform(row_box, target_row), Transform(col_box, target_col), FadeIn(slot_box),
                run_time=0.6 * speed + 0.3,
            )

        # the dot-product expression: a·b + a·b + a·b = c
        n = A.shape[1]
        parts = []
        for k in range(n):
            parts += [str(A[i, k]), r"\cdot", str(B[k, j])]
            if k < n - 1:
                parts.append("+")
        parts += ["=", str(C[i, j])]
        expr = MathTex(*parts, font_size=S.MATH_SIZE + 4, color=S.TEXT)
        expr.next_to(self.mats, DOWN, buff=1.0)
        for k in range(n):
            expr[4 * k].set_color(ROW)
            expr[4 * k + 2].set_color(COL)
        result = expr[-1].set_color(RES)

        a_entries = a_row
        b_entries = b_col
        if speed >= 0.99:
            # slow: one product at a time, with the pair pulsing as it flies down
            for k in range(n):
                group = [
                    TransformFromCopy(a_entries[k], expr[4 * k], path_arc=-0.4),
                    TransformFromCopy(b_entries[k], expr[4 * k + 2], path_arc=0.4),
                    FadeIn(expr[4 * k + 1]),
                    Indicate(a_entries[k], color=ROW, scale_factor=1.25),
                    Indicate(b_entries[k], color=COL, scale_factor=1.25),
                ]
                if k > 0:
                    group.append(FadeIn(expr[4 * k - 1]))
                self.play(*group, run_time=1.1)
        else:
            products = []
            for k in range(n):
                products.append(AnimationGroup(
                    TransformFromCopy(a_entries[k], expr[4 * k]),
                    TransformFromCopy(b_entries[k], expr[4 * k + 2]),
                    FadeIn(expr[4 * k + 1]),
                    *( [FadeIn(expr[4 * k - 1])] if k > 0 else [] ),
                ))
            self.play(LaggedStart(*products, lag_ratio=0.25), run_time=1.6 * speed + 0.4)

        self.play(Write(expr[-2]), FadeIn(result, scale=1.4), run_time=0.5 * speed + 0.2)

        # the result flies up into its slot in C
        q = self.question_marks[i][j]
        slot.set_color(RES)
        self.play(
            ReplacementTransform(result.copy(), slot),
            FadeOut(q, scale=0.5),
            FadeOut(slot_box),
            run_time=0.7 * speed + 0.3,
        )
        self.play(FadeOut(expr, shift=0.2 * DOWN), run_time=0.3 * speed + 0.2)
        return row_box, col_box

    # ── the scene ────────────────────────────────────────────────────
    def construct(self):
        self.camera.background_color = S.BG

        # 0–3 s: title
        title = Text("Matrix multiplication", font_size=S.TITLE_SIZE, color=S.TEXT)
        sub = Text("row  ×  column", font_size=S.CAPTION_SIZE, color=S.MUTED)
        sub.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.9)
        self.play(FadeIn(sub, shift=0.15 * UP), run_time=0.6)
        self.wait_until(2.4)
        self.play(FadeOut(title, shift=0.2 * UP), FadeOut(sub, shift=0.2 * UP), run_time=0.6)

        # 3–6 s: A · B = C, with C still unknown
        self.mA, self.mB, self.mC = mat(A), mat(B), mat(C)
        dot = MathTex(r"\cdot", font_size=S.MATH_SIZE + 10, color=S.TEXT)
        eq = MathTex("=", font_size=S.MATH_SIZE + 10, color=S.TEXT)
        self.mats = VGroup(self.mA, dot, self.mB, eq, self.mC).arrange(RIGHT, buff=0.45)
        self.mats.move_to(UP * 1.0)

        labels = VGroup(*[
            MathTex(name, font_size=S.MATH_SIZE, color=S.MUTED).next_to(m, UP, buff=0.25)
            for name, m in zip("ABC", (self.mA, self.mB, self.mC))
        ])

        # C starts as brackets with "?" in each slot
        self.question_marks = [
            [MathTex("?", font_size=S.MATH_SIZE, color=S.MUTED).move_to(e) for e in row]
            for row in self.mC.get_rows()
        ]
        qs = VGroup(*[q for row in self.question_marks for q in row])

        self.play(
            LaggedStart(
                FadeIn(self.mA, shift=0.2 * RIGHT), FadeIn(dot), FadeIn(self.mB, shift=0.2 * RIGHT),
                FadeIn(eq), FadeIn(self.mC.get_brackets()), FadeIn(qs),
                lag_ratio=0.2,
            ),
            FadeIn(labels, shift=0.1 * DOWN),
            run_time=1.6,
        )

        # sizes: 2×3 · 3×2 → 2×2, inner sizes match
        def size(r, c, inner_first):
            m = MathTex(str(r), r"\times", str(c), font_size=S.CAPTION_SIZE + 4, color=S.MUTED)
            m[2 if inner_first else 0].set_color(S.TEXT)
            return m

        sA = size(2, 3, True).next_to(self.mA, DOWN, buff=0.3)
        sB = size(3, 2, False).next_to(self.mB, DOWN, buff=0.3)
        sC = MathTex("2", r"\times", "2", font_size=S.CAPTION_SIZE + 4, color=S.MUTED)
        sC.next_to(self.mC, DOWN, buff=0.3)
        y = self.mB.get_bottom()[1] - 0.45
        for m in (sA, sB, sC):
            m.set_y(y)
        sC[0].set_color(ROW)
        sC[2].set_color(COL)
        sA[0].set_color(ROW)
        sB[2].set_color(COL)
        cap = self.swap_caption(None, self.caption("The inner sizes must match"))
        self.play(FadeIn(sA, shift=0.1 * UP), FadeIn(sB, shift=0.1 * UP), run_time=0.6)
        self.play(Indicate(sA[2], color=RES), Indicate(sB[0], color=RES), run_time=0.8)
        self.play(
            TransformFromCopy(sA[0], sC[0]), TransformFromCopy(sB[2], sC[2]), FadeIn(sC[1]),
            run_time=0.8,
        )
        self.wait_until(7.6)
        sizes = VGroup(sA, sB, sC)

        # 8–15.5 s: first entry, slowly
        self.play(FadeOut(sizes, shift=0.1 * DOWN), run_time=0.4)
        cap = self.swap_caption(cap, self.caption("Each entry = a row of A  ·  a column of B"))
        boxes = self.compute_entry(0, 0, 1.0, None, None)
        self.wait_until(15.4)

        # 15.5–25 s: the rest, faster each time
        cap = self.swap_caption(cap, self.caption("Same move for every entry"))
        boxes = self.compute_entry(0, 1, 0.5, *boxes)
        boxes = self.compute_entry(1, 0, 0.3, *boxes)
        boxes = self.compute_entry(1, 1, 0.2, *boxes)
        self.play(FadeOut(VGroup(*boxes)), run_time=0.4)
        self.play(
            LaggedStart(*[Indicate(e, color=RES, scale_factor=1.2) for e in self.mC.get_entries()],
                        lag_ratio=0.15),
            run_time=1.0,
        )
        self.wait_until(25.3)

        # 25.3–30 s: the general rule
        formula = MathTex(
            "c_{", "i", "j", "}", "=", r"\sum_{k}", "a_{", "i", "k", "}", "b_{", "k", "j", "}",
            font_size=S.MATH_SIZE + 12, color=S.TEXT,
        )
        formula.next_to(self.mats, DOWN, buff=0.9)
        for idx in (1, 7):
            formula[idx].set_color(ROW)
        for idx in (2, 12):
            formula[idx].set_color(COL)
        for idx in (8, 11):
            formula[idx].set_color(RES)
        cap = self.swap_caption(cap, self.caption("row i  ·  column j  →  entry (i, j)"))
        self.play(Write(formula), run_time=1.5)
        self.wait_until(28.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.wait_until(TOTAL)
