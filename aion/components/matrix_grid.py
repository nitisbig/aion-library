"""HessianGrid: a 2×2 matrix built from four rounded cells.

Cells can light up, fill one at a time, swap contents, and grow brackets, so the
matrix can be *assembled* on screen instead of appearing as a finished bmatrix.

    g = HessianGrid(cell=1.3)
    self.play(g.appear())                                  # four empty cells
    self.play(g.fill(0, 0, MathTex("f_{xx}", color=S.HX)))
    self.play(g.show_brackets())
"""

from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Create, FadeIn,
                   FadeOut, GrowFromCenter, LaggedStart, Line, Mobject, RoundedRectangle,
                   Transform, VGroup, VMobject)

from .. import style as S


class HessianGrid(VGroup):
    def __init__(self, cell: float = 1.25, gap: float = 0.18, center=ORIGIN,
                 stroke=S.SURF_LINE, tint_scale: float = 1.0):
        super().__init__()
        self.cell, self.gap = cell, gap
        self.tint_scale = tint_scale         # < 1: quieter colour fills (glass look)
        self.cells = [[None, None], [None, None]]
        self.entries: list[list[Mobject | None]] = [[None, None], [None, None]]
        self.boxes = VGroup()
        for i in range(2):
            for j in range(2):
                r = RoundedRectangle(width=cell, height=cell, corner_radius=0.16 * cell)
                r.set_stroke(stroke, 2, opacity=0.9).set_fill(S.SURF_LO, 0.55)
                r.move_to(self.cell_center(i, j, center))
                self.cells[i][j] = r
                self.boxes.add(r)
        self.add(self.boxes)
        self.brackets = self._make_brackets(center)

    def cell_center(self, i: int, j: int, center=None) -> np.ndarray:
        c = self.get_center() if center is None else np.array(center, float)
        step = self.cell + self.gap
        return c + (j - 0.5) * step * RIGHT + (0.5 - i) * step * UP

    def _make_brackets(self, center) -> VGroup:
        c = np.array(center, float)
        h = 2 * self.cell + self.gap + 0.3
        x = self.cell + self.gap / 2 + 0.22
        hook = 0.18
        left = VMobject().set_points_as_corners([c + LEFT * (x - hook) + UP * h / 2, c + LEFT * x + UP * h / 2,
                                                 c + LEFT * x + DOWN * h / 2, c + LEFT * (x - hook) + DOWN * h / 2])
        right = VMobject().set_points_as_corners([c + RIGHT * (x - hook) + UP * h / 2, c + RIGHT * x + UP * h / 2,
                                                  c + RIGHT * x + DOWN * h / 2, c + RIGHT * (x - hook) + DOWN * h / 2])
        return VGroup(left, right).set_stroke(S.TEXT, 4)

    # ── animations ─────────────────────────────────────────────
    def appear(self, lag: float = 0.12):
        return LaggedStart(*[GrowFromCenter(self.cells[i][j]) for i in range(2) for j in range(2)],
                           lag_ratio=lag)

    def fill(self, i: int, j: int, mob: Mobject, scale: float = 1.0):
        """Animate `mob` into cell (i, j), replacing what is there."""
        box = self.cells[i][j]
        mob.move_to(box.get_center())
        if mob.height > 0.62 * box.height * scale:          # the grid may have been rescaled
            mob.scale_to_fit_height(0.62 * box.height * scale)
        old = self.entries[i][j]
        self.entries[i][j] = mob
        self.add(mob)
        if old is None:
            return FadeIn(mob, scale=0.8)
        self.remove(old)
        return AnimationGroup(FadeOut(old, scale=0.8), FadeIn(mob, scale=0.8))

    def tint(self, i: int, j: int, color, opacity: float = 0.35):
        c = self.cells[i][j]
        return c.animate.set_fill(color, opacity * self.tint_scale).set_stroke(color, 2.5, opacity=1.0)

    def show_brackets(self):
        k = self.boxes.height / (2 * self.cell + self.gap)  # follow any rescaling of the grid
        self.brackets = self._make_brackets(ORIGIN).scale(k).move_to(self.boxes.get_center())
        self.add(self.brackets)
        return AnimationGroup(*[Create(b) for b in self.brackets])
