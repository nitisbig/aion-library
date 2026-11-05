"""Scene 16 · Ch4: line up the grid (374.900–392.967 s).

"Turn the grid to line up with those directions and the twist disappears. The Hessian
becomes just its two eigenvalues sitting on the diagonal. And this is how any smooth
surface looks up close. The height plus a tilt from the gradient plus a bend from the
Hessian. Just like the parabola from before, one dimension up."

The floor grid turns 45° onto the eigen-directions while the view turns with it, so v₁
points up and v₂ across. In those coordinates H = diag(5, −1): the violet 3s drain to 0
and the diagonal becomes 5 and −1 (ch4 asserts the eigen-pairs). Then the Ch2 landscape:
at a point on a slope, the local model f(p) + ∇f·h + ½hᵀHh (exact ∇f and H from ch2)
builds term by term as a small patch: flat, tilted, bent. Inset: Ch1's cosine and its
parabola 1 − x²/2.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.glow import glow_halo
import shared as V
import ch2 as L2
import ch4 as C

START, END = V.scene_range(16)


class Scene16Diagonal(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 15's last frame ──
        e = C.s15_end()
        rig, plate = e["rig"], e["plate"]
        legend = VGroup(*[m for r in e["rows"] for m in r], e["ev"], e["ew"])
        self.add(plate, *rig.trackers(), e["th"], e["sp"], e["d1"], e["ra"], legend)

        # 4-8 · turn the grid onto the eigen-directions; the matrix arrives
        mat, grid, nums = C.m16()
        ra = e["ra"]
        ra.add_updater(lambda m: m.become(C.right_angle(plate)))
        self.beat("turn the grid", *rig.to(**C.TURNED), FadeOut(legend), FadeIn(mat, shift=LEFT * 0.2), rt=1.6)
        ra.clear_updaters()

        zero = {ij: MathTex("0", font_size=66, color=S.MUTED).move_to(grid.cells[ij[0]][ij[1]]) for ij in ((0, 1), (1, 0))}
        self.beat("twist disappears",
                  *[Transform(nums[ij], zero[ij]) for ij in zero],
                  *[grid.cells[i][j].animate.set_fill(S.STAGE_RAISED, 1.0).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.4)
                    for i, j in zero], rt=0.8)
        diag = {(0, 0): ("5", S.SMILE), (1, 1): ("-1", S.FROWN)}
        new = {ij: MathTex(s, font_size=66, color=c).move_to(grid.cells[ij[0]][ij[1]]) for ij, (s, c) in diag.items()}
        self.beat("two eigenvalues", *[Transform(nums[ij], new[ij]) for ij in new],
                  *[grid.tint(i, j, c, 0.3) for (i, j), (_, c) in diag.items()], rt=0.8)
        halo = glow_halo(VGroup(*new.values()), S.LIGHT, core_alpha=0.3, bloom_alpha=0.3)
        halo.set_opacity(0)
        self.add(halo)
        self.bring_to_front(mat)
        self.beat("diagonal", halo.animate.set_opacity(1.0), rt=0.5, after=382.0)

        # 4-9 · any smooth surface, up close: height + tilt + bend
        land = L2.land_rig(opacity=0.0)
        lplate = land.plate()
        self.add(lplate, *land.trackers())
        self.bring_to_front(mat, halo)
        self.beat("any smooth surface", *rig.to(opacity=0.0), FadeOut(mat), FadeOut(halo), FadeOut(ra),
                  *land.to(opacity=1.0, **C.CLOSE), rt=1.4)
        self.remove(plate)
        a, b = ValueTracker(0.0), ValueTracker(0.0)
        pt = C.patch(lplate, a, b)
        self.add(a, b)
        self.beat("up close", FadeIn(pt), rt=0.6)
        tl = C.taylor()
        self.beat("height", FadeIn(tl[:3], shift=UP * 0.1), rt=0.4, after=386.0)
        self.beat("tilt from the gradient", a.animate.set_value(1.0), FadeIn(tl[3:5], shift=UP * 0.1), rt=0.6)
        self.beat("bend from the hessian", b.animate.set_value(1.0), FadeIn(tl[5:], shift=UP * 0.1), rt=0.6)

        # 4-10 · just like the parabola from before
        card, cosc, par = C.parabola_inset()
        self.beat("parabola from before", FadeIn(card, shift=LEFT * 0.2), FadeIn(cosc, shift=LEFT * 0.2),
                  FadeIn(par, shift=LEFT * 0.2), rt=0.8)
        glow = VGroup(par.copy().set_stroke(width=9, opacity=0.25))
        self.beat("one dimension up", par.animate(rate_func=there_and_back).set_stroke(width=6),
                  FadeIn(glow), rt=0.8)
        self.finish()
