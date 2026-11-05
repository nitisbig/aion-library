"""Scene 06 · Ch2: from a curve to a landscape (132.367–158.750 s).

"Now, let's step off the line and onto a surface. A function of two inputs, x and y,
gives a height above every point on the floor. Together, those heights form a
landscape. To measure slope on a landscape, we slice it. Hold y fixed and cut along
the x direction. The cut is an ordinary curve and its slope is the partial derivative
with respect to x. Cut along y instead and you get the partial derivative with respect to y."

The floor tilts back from the 2D graph; pins (true heights of f) rise and skin into
the surface. A vertical plane y = y₀ cuts it in an ordinary curve whose slope at the
walker's point is ∂f/∂x (exact, from ch2.grad); likewise x = x₀ gives ∂f/∂y.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.surface_gl import slice_line
import shared as V
import ch1 as C1
import ch2 as L

START, END = V.scene_range(6)
GX, GY = L.grad(L.X0, L.Y0)
DFX_AT, DFY_AT, tangent_3d = L.DFX_AT, L.DFY_AT, L.tangent_3d


def pins(plate, rise: ValueTracker, n=13, R=2.4):
    xs = np.linspace(-R, R, n)
    pts = [(x, y) for x in xs for y in xs if (x * x + y * y) ** 0.5 < R * 1.05]
    def make():
        k = rise.get_value()
        g = VGroup()
        for x, y in pts:
            h = float(L.f(x, y)) * k
            if h < 0.01:
                continue
            g.add(Line(plate.project(x, y, 0.0), plate.project(x, y, h), color=S.TERRAIN_LINE, stroke_width=1.6))
        g.set_stroke(opacity=min(1.0, 3 * k) * 0.7)
        return g
    return always_redraw(make)


class Scene06Slices(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 05's last frame (x³ board, glass test card), from the same builders ──
        cax = C1.cube_axes()
        old = VGroup(cax, C1.cube_plot(cax), C1.flat_tangent(cax, 0, 0, half=0.55),
                     MathTex("y", "=", "x^3", font_size=48, color=S.TEXT).to_corner(UP + LEFT, buff=0.55))
        card, head = C1.test_card()
        rows = VGroup(head)
        for i in range(3):
            g, fa, lab = C1.test_row(i)
            rows.add(g.clear_updaters(), fa, lab)
        self.add(old, card, rows)

        # 1-13 · the floor tilts back: a flat 3D floor seen edge-on, then from above
        xl, yl, xs_, ys_ = (ValueTracker(0.0) for _ in range(4))
        rig = L.land_rig(w=(0.0, 0.0, 0.0, 0.0), pitch=3.0, yaw=-90.0, dist=9.5, opacity=0.0, grid=(0.0, 0.0))
        rig.dyn["slices"] = lambda: [
            slice_line(0, color=S.HX, line=xl.get_value(), width=0.02),
            slice_line(90, color=S.HY, line=yl.get_value(), width=0.02),
            slice_line(0, offset=L.Y0, color=S.HX, line=xs_.get_value(), plane=0.4 * xs_.get_value()),
            slice_line(90, offset=-L.X0, color=S.HY, line=ys_.get_value(), plane=0.4 * ys_.get_value())]
        plate = rig.plate()
        self.add(plate, *rig.trackers())
        self.bring_to_front(old, card, rows)
        self.beat("step off the line", FadeOut(card), FadeOut(rows), FadeOut(old, shift=DOWN * 0.3),
                  *rig.to(opacity=1.0, pitch=26.0, yaw=-62.0, dist=8.6, grid=(0.22, 0.22)),
                  xl.animate.set_value(1.0), rt=1.6)
        xlab = MathTex("x", font_size=40, color=S.HX)
        V.pin(xlab, plate, lambda: (2.75, 0.0, 0.0), offset=UP * 0.25)
        ylab = MathTex("y", font_size=40, color=S.HY)
        V.pin(ylab, plate, lambda: (0.0, 2.75, 0.0), offset=UP * 0.25)
        self.beat("two inputs", yl.animate.set_value(1.0), FadeIn(xlab), FadeIn(ylab), rt=0.8)

        # 2-1 · heights: pins rise, then skin into the landscape
        rise = ValueTracker(0.0)
        pn = pins(plate, rise)
        self.add(pn)
        self.beat("height", rise.animate.set_value(1.0), rt=1.6, after=138.0)
        self.beat("landscape", *rig.to(w=(0.0, 1.0, 0.0, 0.0)), xl.animate.set_value(0.0),
                  yl.animate.set_value(0.0), FadeOut(xlab), FadeOut(ylab), rt=1.0, after=142.0)
        self.remove(pn)

        # 2-2 · slice along x at y = y0
        self.beat("slice it", xs_.animate.set_value(0.35), rt=0.8)
        tag = MathTex(r"y = \text{const}", font_size=34, color=S.HX)
        V.pin(tag, plate, lambda: (-2.3, L.Y0, 0.95), offset=UP * 0.1)
        self.beat("hold y fixed", FadeIn(tag), rt=0.5)
        self.beat("x direction", xs_.animate.set_value(1.0), rt=0.7)
        self.beat("ordinary curve", *rig.to(yaw=-90.0, pitch=6.0, dist=8.0), rt=1.4)
        tx = tangent_3d(plate, L.X0, L.Y0, (1, 0))
        dfx = MathTex(r"\frac{\partial f}{\partial x}", font_size=44, color=S.HX)
        V.pin(dfx, plate, lambda: DFX_AT)
        self.beat("with respect to x", Create(tx), FadeIn(dfx, shift=UP * 0.1), rt=0.7)

        # 2-3 · and along y at x = x0
        ty = tangent_3d(plate, L.X0, L.Y0, (0, 1))
        dfy = MathTex(r"\frac{\partial f}{\partial y}", font_size=44, color=S.HY)
        V.pin(dfy, plate, lambda: DFY_AT)
        self.beat("cut along y", *rig.to(yaw=-62.0, pitch=28.0, dist=8.6), ys_.animate.set_value(1.0),
                  FadeOut(tag), rt=1.2)
        self.play(Create(ty), FadeIn(dfy, shift=UP * 0.1), run_time=self.snap(0.7))
        self.finish()
