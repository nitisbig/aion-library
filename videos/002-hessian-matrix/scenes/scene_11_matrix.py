"""Scene 11 · Ch3: the Hessian, and its mirror (257.833–286.867 s).

"The last one, f y x, asks the same question the other way around. For any smooth
surface, it always matches f x y. The twist is the same from both sides. Now arrange all
four in a square. Bending in x on the top left, bending in y on the bottom right, and the
twist in the other two corners. That's the Hessian matrix, named after the German
mathematician Otto Hess. Because the twist appears twice, the grid is symmetric. A mirror
image across its diagonal."

Symmetry of mixed partials (Schwarz/Clairaut): for C² f, ∂²f/∂y∂x = ∂²f/∂x∂y. The caption
gives the mathematician's full name, Ludwig Otto Hesse (1811–1874).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.cards import card_image
import shared as V
import ch3 as L

START, END = V.scene_range(11)
S10_START, S10_END = V.scene_range(10)


def order_icon(first, second):
    """'slope in <first>, then move in <second>': two small arrows."""
    arrows = []
    for axis in (first, second):
        d, c = (RIGHT, S.HX) if axis == "x" else (UP, S.HY)
        arrows.append(Arrow(ORIGIN, d * 0.55, buff=0, color=c, stroke_width=6,
                            max_tip_length_to_length_ratio=0.32))
    return VGroup(arrows[0], V.label("then", 24, S.MUTED), arrows[1]).arrange(RIGHT, buff=0.15)


class Scene11Matrix(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 10's last frame: xy surface with rulings, corner table, z = xy, readouts ──
        clk = ValueTracker(S10_END - S10_START)
        self.run_clock(clk)
        rig = L.xy_rig(opacity=0.55, grid=(0.0, 0.0))
        rig.dyn["yaw"] = lambda: rig.val("yaw") + L.XY_SPIN * clk.get_value()
        plate = rig.plate(width=L.XY_W, height=L.XY_H, center=L.XY_C)
        show, h0, hp, hn = (ValueTracker(1.0) for _ in range(4))
        rul = L.xy_rulings(plate, show, h0, hp, hn)
        g, grid, rows, cols = L.s10_table()
        zxy, ro = L.zxy_label(), L.readouts()
        self.add(plate, *rig.trackers(), rul, g, zxy, ro)

        # 3-8 · back to the table; the last cell, f_yx
        k, c = L.placement(g, grid, L.CORNER_S, 1.0, L.MID_C)
        self.beat("the last one", *rig.to(opacity=0.0), show.animate.set_value(0.0), FadeOut(zxy), FadeOut(ro),
                  g.animate.scale(k).move_to(c), rt=0.8)
        self.remove(plate, rul)
        self.beat("f y x", grid.fill(1, 0, L.entry("yx")), grid.tint(1, 0, S.TWIST, 0.3), rt=0.6)
        ixy = order_icon("x", "y").next_to(grid.cells[0][1], RIGHT, buff=0.3)
        iyx = order_icon("y", "x").next_to(grid.cells[1][0], DOWN, buff=0.3)
        self.beat("other way around", FadeIn(ixy, shift=LEFT * 0.1), FadeIn(iyx, shift=UP * 0.1), rt=0.8)
        eq = MathTex(r"\frac{\partial^2 f}{\partial y\,\partial x}", "=",
                     r"\frac{\partial^2 f}{\partial x\,\partial y}", font_size=48, color=S.TWIST)
        eq[1].set_color(S.TEXT)
        eq.move_to(L.MID_C + DOWN * 3.3)          # clear of the "then" icon under f_yx
        self.beat("always matches", Indicate(grid.entries[0][1], color=S.TWIST, scale_factor=1.25),
                  Indicate(grid.entries[1][0], color=S.TWIST, scale_factor=1.25), Write(eq), rt=0.8)

        # 3-9 · arrange all four in a square
        moves = []
        for i in range(2):
            for j in range(2):
                tgt = L.tight_center(i, j)
                moves += [grid.cells[i][j].animate.move_to(tgt), grid.entries[i][j].animate.move_to(tgt)]
        self.beat("arrange all four", FadeOut(rows), FadeOut(cols), FadeOut(ixy), FadeOut(iyx), FadeOut(eq),
                  *moves, rt=1.0)
        grid.gap = L.TIGHT
        self.beat("top left", Indicate(grid.entries[0][0], color=S.HX, scale_factor=1.25), rt=0.5)
        self.beat("bottom right", Indicate(grid.entries[1][1], color=S.HY, scale_factor=1.25), rt=0.5)
        self.beat("other two corners", Indicate(grid.entries[0][1], color=S.TWIST, scale_factor=1.25),
                  Indicate(grid.entries[1][0], color=S.TWIST, scale_factor=1.25), rt=0.5)
        br = grid.show_brackets()
        hl = L.h_label(grid)
        self.beat("hessian matrix", br, Write(hl), rt=0.8)

        # 3-10 · Hesse; symmetric across the diagonal
        cap_c = np.array([L.HC[0] - 0.5, -2.85, 0])
        card = V.panel(6.4, 0.95, top=S.GLASS_TOP, bottom=S.GLASS_BOTTOM, border=S.LINE,
                          glow=S.GLASS_TOP).move_to(cap_c)
        name = VGroup(V.label("Ludwig Otto Hesse", 32, S.TEXT), V.label("1811–1874", 26, S.MUTED))
        name.arrange(RIGHT, buff=0.35).move_to(cap_c)
        self.beat("otto hess", FadeIn(card, shift=UP * 0.15), FadeIn(name, shift=UP * 0.15), rt=0.6)
        self.play_at(283.0, FadeOut(card), FadeOut(name), lead=0.0, run_time=0.5)
        dg = L.diagonal(grid)
        self.add(dg)
        self.bring_to_front(grid)                 # the diagonal runs behind the entries
        self.beat("symmetric", Create(dg), rt=0.8)
        a, b = grid.entries[0][1].copy(), grid.entries[1][0].copy()
        self.beat("mirror image",
                  a.animate(path_arc=PI * 0.6).move_to(grid.entries[1][0]).set_opacity(0),
                  b.animate(path_arc=PI * 0.6).move_to(grid.entries[0][1]).set_opacity(0), rt=1.0)
        self.remove(a, b)
        self.finish()
