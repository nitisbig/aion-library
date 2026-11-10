"""Smoke test: EpicyclePlate inside Manim, with a Manim label pinned via project()."""
from manim import *
from aion import fourier as F, style as S
from aion.drawings import treble_clef
from aion.components.epicycle_gl import EpicyclePlate
from aion.progress import ProgressScene

TERMS = F.order_terms(F.coefficients(3.3 * treble_clef(1000), 100), keep_zero_first=False)


class PlateSmoke(ProgressScene):
    TOTAL_DURATION = 2.0

    def construct(self):
        self.camera.background_color = S.STAGE
        t = ValueTracker(0.0)
        plate = EpicyclePlate(lambda: {"terms": TERMS, "t": t.get_value(), "ink_from": 0.0, "sparks": 1.0})
        dot = always_redraw(lambda: Circle(0.18, color=S.STILL, stroke_width=2).move_to(plate.project(plate.pen())))
        self.add(plate, t, dot)
        self.play(t.animate.set_value(0.8), run_time=2, rate_func=linear)
