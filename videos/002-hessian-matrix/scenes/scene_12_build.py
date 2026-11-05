"""Scene 12 · Ch3: building the puzzle Hessian (286.867–303.700 s).

"Let's build one. F equals x squared plus three x y plus y squared. The bending in x is
two. The bending in y is two. The twist is three. So the Hessian is two, three, three,
two. Hold on to that one. It's the puzzle surface from the start."

f = x² + 3xy + y²: f_x = 2x + 3y, f_y = 3x + 2y, f_xx = 2, f_yy = 2, f_xy = f_yx = 3,
so H = [[2, 3], [3, 2]] (checked numerically below). The flashback is scene 02's
puzzle surface with the ball rolling off along (−1, 1), its downhill (λ = −1) direction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.glow import glow_halo
import shared as V
import ch3 as L

START, END = V.scene_range(12)


def _hess_fd(fn, p, h=1e-3):
    e = np.eye(2) * h
    return np.array([[(fn(p + e[i] + e[j]) - fn(p + e[i] - e[j]) - fn(p - e[i] + e[j]) + fn(p - e[i] - e[j]))
                      / (4 * h * h) for j in range(2)] for i in range(2)])


_H = _hess_fd(lambda p: p[0] ** 2 + 3 * p[0] * p[1] + p[1] ** 2, np.array([0.3, -0.7]))
assert np.allclose(_H, [[2, 3], [3, 2]], atol=1e-6) and np.allclose((_H[0, 0], _H[0, 1], _H[1, 1]), V.H_PUZZLE)
BUILD_C = np.array([-3.3, -0.55, 0.0])        # matrix centre while the worked lines are up
LEFT_C = L.S12_LEFT_C                          # matrix centre beside the flashback
WORK_X = -0.75                                # left edge of the worked lines
NW = np.array([-1.0, 1.0]) / np.sqrt(2)


class Scene12Build(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        grid, hl, dg = L.s11_end()                # scene 11's last frame
        self.add(dg, grid, hl)

        # 3-11 · symbols become corner tags; the matrix steps aside; f writes
        D = BUILD_C - L.HC
        tags = [grid.entries[i][j] for i in range(2) for j in range(2)]
        spots = [L.tag_spot(grid.cells[i][j]) + D for i in range(2) for j in range(2)]
        self.bring_to_front(grid, hl)
        self.beat("lets build one", FadeOut(dg), VGroup(grid.boxes, grid.brackets, hl).animate.shift(D),
                  *[t.animate.scale(L.TAG_S).move_to(p) for t, p in zip(tags, spots)], rt=0.6)
        self.remove(dg)
        f = MathTex("f", "=", "x^2", "+", "3xy", "+", "y^2", font_size=62, color=S.TEXT)
        f[2].set_color(S.HX)
        f[4].set_color(S.TWIST)
        f[6].set_color(S.HY)
        f.move_to(UP * 2.85)
        self.beat("x squared", Write(f[:3]), rt=0.6, after=288.0)
        self.beat("three x y", Write(f[3:5]), rt=0.6)
        self.beat("y squared", Write(f[5:]), rt=0.6, after=290.0)

        # 3-12 · the three worked lines; numbers fly into the cells
        def line(parts, colors, y):
            m = MathTex(*parts, font_size=46, color=S.TEXT)
            for k, c in colors.items():
                m[k].set_color(c)
            return m.move_to([WORK_X, y, 0], aligned_edge=LEFT)

        l1 = line(["f_x", "=", "2x+3y", r"\;\Rightarrow\;", "f_{xx}", "=", "2"], {0: S.HX, 4: S.HX, 6: S.HX}, 1.1)
        l2 = line(["f_y", "=", "3x+2y", r"\;\Rightarrow\;", "f_{yy}", "=", "2"], {0: S.HY, 4: S.HY, 6: S.HY}, 0.0)
        l3 = line(["f_{xy}", "=", r"\tfrac{\partial}{\partial y}(2x+3y)", "=", "3"], {0: S.TWIST, 4: S.TWIST}, -1.1)
        nums = {}

        def num(i, j, s, c):
            m = MathTex(s, font_size=76, color=c).move_to(grid.cells[i][j])
            nums[(i, j)] = m
            grid.add(m)
            return m

        self.beat("bending in x is two", Write(l1), rt=0.7)
        self.play(TransformFromCopy(l1[6], num(0, 0, "2", S.HX)), run_time=self.snap(0.6))
        self.beat("bending in y is two", Write(l2), rt=0.7)
        self.play(TransformFromCopy(l2[6], num(1, 1, "2", S.HY)), run_time=self.snap(0.6))
        self.beat("twist is three", Write(l3), rt=0.6)
        self.play(TransformFromCopy(l3[4], num(0, 1, "3", S.TWIST)),
                  TransformFromCopy(l3[4], num(1, 0, "3", S.TWIST)), run_time=self.snap(0.6))

        # 3-13 · so the Hessian is 2, 3, 3, 2
        mat = VGroup(grid, hl)
        self.beat("so the hessian is", FadeOut(l1), FadeOut(l2), FadeOut(l3),
                  mat.animate.shift(L.HC - BUILD_C), rt=0.6)
        t, order = self.t("two three three two") - 0.15, [(0, 0), (0, 1), (1, 0), (1, 1)]
        words = [t + 0.15]
        for w in ("three", "three", "two"):
            words.append(self.t(w, after=words[-1] + 0.05))
        for k, (ij, tw) in enumerate(zip(order, words)):
            nxt = words[k + 1] if k + 1 < len(words) else tw + 0.6
            self.play_at(tw, Indicate(nums[ij], scale_factor=1.3, color=nums[ij].get_color()),
                         run_time=min(0.35, nxt - tw - 0.02))
        halo = glow_halo(VGroup(*nums.values(), grid.brackets), S.GRAD, core_alpha=0.35, bloom_alpha=0.3)
        halo.set_opacity(0)
        self.add(halo)
        self.bring_to_front(mat)
        self.beat("hold on to that one", halo.animate.set_opacity(1.0), rt=0.8)

        # 3-14 · it's the puzzle surface from the start
        s = ValueTracker(0.0)
        rig = V.puzzle_rig(opacity=0.0, **L.PUZZLE_KW)
        plate = rig.plate(**L.S12_PLATE)
        self.add(plate, *rig.trackers(), s)
        ball = V.walker()
        V.pin(ball, plate, V.on_surface(plate, lambda: s.get_value() * NW[0], lambda: s.get_value() * NW[1], 0.03))
        late = lambda t: smooth(max(0.0, (t - 0.35) / 0.65))     # the plate waits for the matrix to clear
        self.play_at(self.t("puzzle surface", after=301.0),
                     Group(mat, halo).animate(rate_func=smooth).shift(LEFT_C - L.HC),
                     rig.vt["opacity"].animate(rate_func=late).set_value(0.8), FadeIn(ball, rate_func=late),
                     run_time=1.0)
        self.play(s.animate(rate_func=rush_into).set_value(1.5), run_time=self.snap(END - self.now))
        self.finish()
