"""Scene 02 · Intro: the puzzle and the promise (28.167–55.467 s). Chapter 0 redesign.

"And here's a puzzle. This surface curves upward if you walk east. It curves upward
if you walk north. And yet, the point in the middle is not a valley. The answer
lives in a small grid of four numbers. It's called the Hessian Matrix. Over the next
few minutes, we'll build it from nothing, see what each number means, and see why
the same idea helps computers search landscapes with millions of dimensions. All you
need is the idea of a slope."

No cut from scene 01: the mountain range sinks away and the ground under the walker
becomes the puzzle surface f = x² + 3xy + y² (H = [[2,3],[3,2]], eigenvalues 5 along
(1,1) and −1 along (1,−1)), a luminous plate on the black stage. Both axis slices
smile (f_xx = f_yy = 2), yet the walker, now a ball, rolls off along the north-west
diagonal, the direction of the −1 eigenvalue. Left unexplained here; solved in Ch4.
The only on-screen words are the title.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.bend_gauge import BendGauge
from aion.components.title import TitlePlate
import shared as V

START, END = V.scene_range(2)

# The math on screen, checked first.
H = np.array([[2.0, 3.0], [3.0, 2.0]])
lam, vec = np.linalg.eigh(H)
assert np.allclose(lam, [-1, 5])
NW = np.array([-1.0, 1.0]) / math.sqrt(2)          # eigenvector of −1: the ball's path
assert np.allclose(H @ NW, -NW)
BEND = lambda t: 2 + 3 * math.sin(2 * t)           # uᵀHu for u = (cos t, sin t)
Z1 = (math.pi + math.asin(2 / 3)) / 2              # bending crosses zero here …
Z2 = (2 * math.pi - math.asin(2 / 3)) / 2          # … and back
assert abs(BEND(Z1)) < 1e-12 and abs(BEND(Z2)) < 1e-12

ENTRY = {(0, 0): ("f_{xx}", S.HX), (0, 1): ("f_{xy}", S.TWIST),
         (1, 0): ("f_{yx}", S.TWIST), (1, 1): ("f_{yy}", S.HY)}


def entry(i, j, size=50):
    t, c = ENTRY[(i, j)]
    return MathTex(t, font_size=size, color=c)


def swell(start: float, end: float, extreme: float):
    """Rate function for a tracker going start → end that passes through `extreme`
    half-way (a fog bank that swells, a dip to dark), smooth at both ends."""
    def f(u):
        v = start + (end - start) * smooth(u) + (extreme - 0.5 * (start + end)) * math.sin(math.pi * u) ** 2
        return (v - start) / (end - start)
    return f


class Scene02Puzzle(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── hand-off: scene 01's last frame, rebuilt from the same numbers ──
        s1, e1 = V.scene_range(1)
        clk = ValueTracker(e1 - s1)
        rig = V.intro_rig(clk, **V.S01_END, time=e1 - s1)
        self.run_clock(rig["time"], clk)
        plate = V.terrain_plate(rig, splats=V.SPLATS)
        self.add(plate, *rig.trackers())
        roll = ValueTracker(0.0)
        me = V.walker()
        V.pin(me, plate, V.on_surface(plate, lambda: roll.get_value() * NW[0],
                                      lambda: roll.get_value() * NW[1], 0.03))
        self.add(me, roll)

        # I-6 · a fog bank rolls through; the range sinks away and the ground under
        # the walker becomes the puzzle surface (one continuous move, no cut)
        rt = 1.8
        t_end = self.t("heres a puzzle") - S.LEAD + rt
        pv = dict(V.PUZZLE_VIEW)
        pv["yaw"] = pv["yaw"] - V.YAW_DRIFT * (t_end - s1)     # land on the view, drift included
        haze0 = rig.val("haze")
        # the plate dims to 12% mid-move (the fog bank), so the morph happens behind it
        anims = [rig["haze"].animate(rate_func=swell(haze0, 0.0001, 1.3)).set_value(0.0001),
                 rig["opacity"].animate(rate_func=swell(1.0, 0.999, 0.12)).set_value(0.999),
                 rig["wm"].animate(rate_func=V.window(0.0, 0.7)).set_value(0.0),
                 # the splat range tears off the sinking ground and rises as sparks
                 rig["lift"].animate(rate_func=V.window(0.0, 0.75)).set_value(1.0),
                 rig["splat"].animate(rate_func=V.window(0.8, 1.0)).set_value(0.0),
                 rig["edge"].animate(rate_func=V.window(0.0, 0.55)).set_value(pv.pop("edge")),
                 rig["win"].animate(rate_func=V.window(0.35, 1.0)).set_value(pv.pop("win"))]
        pv.pop("haze")
        anims += rig.to(**pv)
        # play_at, not beat: beat() sets one rate_func for all, which would override the windows
        self.play_at(self.t("heres a puzzle"), *anims, run_time=rt)

        # walking east: the red slice smiles; walking north: the green slice smiles
        g_x = BendGauge(2.0, width=0.75, stroke=6)
        g_x.add_updater(lambda m: m.place(plate.surface_point(2.15, 0.0) + UP * 0.55))
        g_y = BendGauge(2.0, width=0.75, stroke=6)
        g_y.add_updater(lambda m: m.place(plate.surface_point(0.0, 2.15) + UP * 0.55))
        self.beat("east", *rig.to(xs=1.0), FadeIn(g_x, scale=0.6), rt=0.8, after=29.8)
        self.beat("north", *rig.to(ys=1.0), FadeIn(g_y, scale=0.6), rt=0.8, after=32.6)

        # I-7 · and yet: the ball rolls off along the north-west diagonal, leaving a trail
        self.beat("middle", *rig.to(xs=0.3, ys=0.3), rt=0.4, after=34.8)
        trail = always_redraw(lambda: VMobject().set_points_smoothly(
            [plate.surface_point(*(r * NW), 0.03) for r in np.linspace(0, max(roll.get_value(), 1e-3), 24)]
        ).set_stroke(S.GRAD, 3, opacity=0.75) if roll.get_value() > 0.02 else VMobject())
        self.add(trail)
        me.add_updater(lambda m: V.set_walker_alpha(m, float(np.clip((2.3 - roll.get_value()) / 0.6, 0, 1))))
        self.beat("not a valley", roll.animate.set_value(2.4), rt=2.2, rate=rush_into)
        self.remove(me)

        # I-8 · the surface recedes; four glass cells; the Hessian
        grid = V.glass_grid(cell=1.15, center=UP * 0.45)
        trail.clear_updaters()
        self.beat("small grid", *rig.to(dist=13.0, opacity=0.16, xs=0.0, ys=0.0, mist=0.0),
                  FadeOut(g_x), FadeOut(g_y), FadeOut(trail), grid.appear(), rt=0.6)
        self.add(grid)
        self.play(LaggedStart(*[c.animate(rate_func=there_and_back).scale(1.08)
                                for c in grid.boxes], lag_ratio=0.12), run_time=self.snap(0.8))
        sweep = ValueTracker(0.0)
        title = TitlePlate("The Hessian Matrix", size_px=72, sweep=sweep).next_to(grid, DOWN, buff=0.5)
        self.add(sweep)
        self.beat("hessian matrix", *[grid.fill(i, j, entry(i, j)) for i in range(2) for j in range(2)],
                  FadeIn(title, shift=UP * 0.12), rt=0.8)
        self.play(sweep.animate.set_value(1.0), run_time=self.snap(1.1), rate_func=smooth)

        # I-9 · trailer: build it · what each number means · millions of dimensions
        self.beat("build it from nothing", *[FadeOut(grid.entries[i][j]) for i in range(2) for j in range(2)],
                  rt=0.4)
        for i in range(2):
            for j in range(2):
                grid.entries[i][j] = None
        self.play(LaggedStart(*[grid.fill(i, j, entry(i, j)) for i in range(2) for j in range(2)],
                              lag_ratio=0.35), run_time=self.snap(0.8))

        dial, curve_grp, th = self._dial()
        title.clear_updaters()
        self.beat("what each number means", FadeOut(grid), FadeOut(title), *rig.to(opacity=0.0),
                  FadeIn(dial), FadeIn(curve_grp[0]), rt=0.5)
        self.add(curve_grp[1], curve_grp[2])
        self.play(th.animate.set_value(PI), run_time=self.snap(3.9), rate_func=linear)

        gd = self._descent()
        dial.clear_updaters()                 # freeze the redraw-driven pieces before fading
        curve_grp.clear_updaters()
        self.beat("millions of dimensions", FadeOut(dial), FadeOut(curve_grp), FadeIn(gd[0]), rt=0.5)
        self.play(Create(gd[1]), run_time=self.snap(1.3), rate_func=linear)
        self.play(Create(gd[2]), FadeIn(gd[3], scale=0.5), run_time=self.snap(0.7))

        # I-10 · everything collapses to one tangent line on a curve
        tan = V.handoff_tangent()
        self.beat("idea of a slope", FadeOut(gd, scale=0.6), FadeIn(tan, scale=1.4), rt=1.0)
        self.finish()

    # ── trailer pieces (luminous: hairlines on black, colour only where it means something) ──
    def _dial(self):
        th = ValueTracker(0.0)
        c = LEFT * 3.2 + DOWN * 0.1
        ring = Circle(radius=1.35).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.5).move_to(c)
        u = always_redraw(lambda: Arrow(c, c + 1.35 * np.array([math.cos(th.get_value()), math.sin(th.get_value()), 0]),
                                        buff=0, color=S.TEXT, stroke_width=4,
                                        max_tip_length_to_length_ratio=0.16))
        ax = V.hairline(Axes(x_range=[0, PI, PI / 4], y_range=[-1.5, 5.5, 1], x_length=5.0, y_length=3.6,
                             tips=False, axis_config={"include_ticks": False}).move_to(RIGHT * 2.6 + DOWN * 0.1))

        def trace():
            t = th.get_value()
            out = VGroup()
            for lo, hi, col in ((0, Z1, S.SMILE), (Z1, Z2, S.FROWN), (Z2, PI, S.SMILE)):
                if t > lo + 1e-3:
                    out.add(V.lit(ax.plot(BEND, x_range=[lo, min(t, hi)]), col, width=4.5))
            return out
        dot = always_redraw(lambda: Dot(ax.c2p(th.get_value(), BEND(th.get_value())), radius=0.07,
                                        color=S.SMILE if BEND(th.get_value()) >= 0 else S.FROWN))
        return VGroup(ring, u), VGroup(ax, always_redraw(trace), dot), th

    def _descent(self):
        k = 0.95                                          # map units per math unit
        c = ORIGIN + DOWN * 0.1
        to = lambda x, y: c + k * np.array([x, y, 0.0])
        ells = VGroup(*[Ellipse(width=2 * k * math.sqrt(v), height=2 * k * math.sqrt(v / 10))
                        .set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.5).move_to(c)
                        for v in (1, 3, 6, 10, 19)])      # 19 = f(3, 1): the start sits on it
        pts = V.gd_path()
        path = VMobject(color=S.GRAD, stroke_width=3).set_points_as_corners([to(x, y) for x, y in pts])
        newton = ArcBetweenPoints(to(3, 1), to(0, 0), angle=-PI / 3, color=S.SMILE, stroke_width=4)
        target = Dot(to(0, 0), radius=0.09, color=S.SMILE)
        return VGroup(ells, path, newton, target)
