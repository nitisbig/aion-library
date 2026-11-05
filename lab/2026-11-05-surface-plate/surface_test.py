"""SurfacePlate lab test (video 002 prerequisite).

    uv run manim -sql lab/2026-11-05-surface-plate/surface_test.py FogLook      # still
    uv run manim -sql lab/2026-11-05-surface-plate/surface_test.py PuzzleLook
    uv run manim -sql lab/2026-11-05-surface-plate/surface_test.py RulingsLook
    uv run manim -ql  lab/2026-11-05-surface-plate/surface_test.py MotionTest   # 6 s
"""

import numpy as np
from manim import DOWN, UP, Dot, MathTex, ValueTracker, smooth

from aion import style as S
from aion.components.surface_gl import SurfacePlate, slice_line, tangent_disc
from aion.progress import ProgressScene

BLACK = "#000000"


class _Base(ProgressScene):
    def setup(self):
        super().setup()
        self.camera.background_color = BLACK


class FogLook(_Base):
    """Intro: walker on a flat point in thick fog (saddle under it)."""
    TOTAL_DURATION = 0.1

    def construct(self):
        st = {"H": (2.0, 0.0, -2.0), "yaw": -70, "pitch": 13, "dist": 6.5, "fov": 40,
              "target": (0, 0, 0.35), "R": 10.0, "edge": 0.8, "fog": 0.11, "fog_height": 0.8,
              "time": 3.0, "sky": 0.9, "fog_color": "#4A5468", "zlo": -2, "zhi": 2,
              "grid": (0.10, 0.10), "zs": 0.07, "zclip": 1.1, "disc": tangent_disc(0, 0, 0.45, 0.4)}
        plate = SurfacePlate(lambda: st)
        walker = Dot(plate.surface_point(0, 0, 0.06), radius=0.07, color=S.GRAD)
        self.add(plate, walker)
        self.wait(0.1)


class PuzzleLook(_Base):
    """Puzzle surface: red and green slices with planes, bend tint, contours."""
    TOTAL_DURATION = 0.1

    def construct(self):
        st = {"H": (2.0, 3.0, 2.0), "yaw": -58, "pitch": 30, "dist": 8.5, "R": 2.6,
              "zs": 0.3, "zclip": 1.6, "contour": 0.5, "contour_step": 0.2, "tint": 0.0,
              "fog": 0.02, "grid": (0.18, 0.18),
              "slices": [slice_line(0, color=S.HX, plane=0.4), slice_line(90, color=S.HY, plane=0.4)]}
        plate = SurfacePlate(lambda: st)
        eq = MathTex(r"f = x^2 + 3xy + y^2", font_size=40).to_edge(UP)
        eq[0][2:4].set_color(S.HX)
        eq[0][5:8].set_color(S.TWIST)
        eq[0][9:11].set_color(S.HY)
        self.add(plate, eq)
        self.wait(0.1)


class RulingsLook(_Base):
    """z = xy shown as its straight-line rulings (fill → 0, additive lines)."""
    TOTAL_DURATION = 0.1

    def construct(self):
        st = {"H": (0.0, 1.0, 0.0), "yaw": -40, "pitch": 26, "dist": 8.0, "R": 2.6,
              "zs": 0.45, "fill": 0.18, "grid": (1.0, 0.0), "grid_step": 0.2, "fog": 0.02}
        self.add(SurfacePlate(lambda: st))
        self.wait(0.1)


class MotionTest(_Base):
    """6 s: dome → bowl → saddle under a still disc while the camera orbits; a Manim
    dot pinned to the surface checks that project() stays locked."""
    TOTAL_DURATION = 6.0

    def construct(self):
        a, c = ValueTracker(-2.0), ValueTracker(-2.0)
        yaw = ValueTracker(-80.0)
        t = ValueTracker(0.0)
        plate = SurfacePlate(lambda: {
            "H": (a.get_value(), 0.0, c.get_value()), "yaw": yaw.get_value(), "pitch": 22,
            "dist": 7.0, "R": 4.0, "zs": 0.3, "fog": 0.06, "fog_height": 0.6,
            "time": t.get_value(), "grid": (0.15, 0.15), "tint": 0.7,
            "disc": tangent_disc(0, 0, 0.5, 0.35)})
        walker = Dot(radius=0.07, color=S.GRAD)
        walker.add_updater(lambda m: m.move_to(plate.surface_point(0, 0, 0.05)))
        probe = Dot(radius=0.05, color=S.HX)
        probe.add_updater(lambda m: m.move_to(plate.surface_point(1.2, 0.0, 0.02)))
        self.add(plate, walker, probe)
        self.play(yaw.animate.set_value(-20), t.animate.set_value(6),
                  a.animate.set_value(2.0), run_time=2.0, rate_func=smooth)
        self.play(yaw.animate.set_value(20), t.animate.set_value(12),
                  c.animate.set_value(2.0), run_time=2.0, rate_func=smooth)
        self.play(yaw.animate.set_value(50), t.animate.set_value(18),
                  c.animate.set_value(-2.0), run_time=2.0, rate_func=smooth)
