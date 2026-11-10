"""Scene 24 · Ch6: two hundred and one circles (483.567–501.733 s).

"So let's give it a real test. Here's our treble clef, as one continuous line. We place a
thousand dots along it, and for every speed from minus one hundred to one hundred, we spin
and average. Out come two hundred and one circles. Sort them from biggest to smallest, and
chain them tip to tail."

The recipe run for real: the 1,000 dots, wound by the sweeping speed n; the strip is
shared.clef_coeffs() (aion.fourier, the same numbers the intro's chain uses). The biggest
bars curl into circles at their chain joints; the EpicyclePlate chain takes over.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (UP, Circle, FadeIn, FadeOut, Integer, LaggedStart, MathTex, ReplacementTransform, ValueTracker,
                   VGroup, VMobject, linear)

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch5 as C5
import ch6 as C
from ch4 import TAU
import scene_22_check as S22
import scene_23_recipe as S23

START, END = V.scene_range(24)
N_CURL = 40


class Scene24Compute(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── S23's last picture
        marker = C2.corner_marker()
        items = S22.end_rack()
        rack = VGroup(*items.values()).fade(0.7)
        eb5 = V.eyebrow("05 · SPIN AND AVERAGE")
        fml = S23.end_formula()
        card_op = ValueTracker(1.0)
        self.add(rack, eb5, fml, marker, card_op)
        self.add(V.redraw(lambda: C5.card_docked(self.now, card_op.get_value())))

        # "real test": new eyebrow; the formula shrinks to the top-right (its intro spot) and stays
        eb6 = V.eyebrow("06 · DRAWING ANYTHING")
        f_small = V.recipe(40, muted=False).move_to(V.RECIPE_POS)
        self.beat("real test", FadeOut(eb5), FadeIn(eb6, shift=UP * 0.08), FadeOut(fml[1:]), FadeOut(rack),
                  card_op.animate.set_value(0.0), ReplacementTransform(fml[0], f_small), rt=0.8)

        # "treble clef": its outline as a silver ghost; "one continuous line": a spark runs along it once
        outline = C.clef_outline(0.5)
        self.beat("treble clef", FadeIn(outline), rt=0.8)
        sp = ValueTracker(-1.0)
        self.add(sp)
        pts = C.clef_outline_pts()

        def spark():
            u = sp.get_value()
            if u < 0 or u > 1:
                return VMobject()
            i = int(u * (len(pts) - 1))
            seg = pts[max(0, i - 160): i + 1]
            return VGroup(C4.path(seg, S.LIGHT, 4.0, 0.9), C4.pen(pts[i]))
        self.add(V.redraw(spark))
        self.beat("one continuous line", sp.animate.set_value(1.0), rt=1.2, rate=linear)
        sp.set_value(-1.0)

        # "thousand dots": 1,000 gold dots sprinkle along it
        dz = C.clef_dots()
        dots = VGroup(*[C4.Dot(C4.to3(z), radius=0.018, color=S.INK) for z in dz])
        self.beat("thousand dots", LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.002), rt=1.0)
        self.remove(*dots)
        self.add(dots)                      # the group itself, so its updater runs

        # "minus one hundred": n sweeps −100 → 100; the dots wind by n; the strip fills bar by bar
        n_val = ValueTracker(-100.0)
        self.add(n_val)
        t_j = np.arange(len(dz)) / len(dz)
        base = dz - C.CLEF_AT
        spin = ValueTracker(0.0)              # 0: the clef as drawn; 1: wound by n
        self.add(spin)

        def wind(g, dt):
            k = n_val.get_value() * spin.get_value()
            w = C.CLEF_AT + base * np.exp(-1j * TAU * k * t_j)
            for d, z in zip(g, w):
                d.move_to(C4.to3(z))
        dots.add_updater(wind)

        label = MathTex("n", "=", font_size=44, color=S.LABEL).move_to([2.6, 1.15, 0])
        num = Integer(-100, font_size=44, color=S.LABEL).next_to(label, np.array([1, 0, 0]), buff=0.2)
        num.add_updater(lambda m, dt: m.set_value(int(round(n_val.get_value()))).next_to(label, np.array([1, 0, 0]),
                                                                                          buff=0.2))
        bars = {n: C.bar(n, c, C.strip_x(i)) for i, (n, c) in enumerate(C.coeff_list())}
        shown = VGroup()
        self.add(shown)

        def grow(g, dt):
            k = n_val.get_value()
            want = [n for n in bars if n <= k + 1e-6]
            if len(want) != len(g):
                g.submobjects = [bars[n] for n in want]
        shown.add_updater(grow)
        axis = C4.Line([C.STRIP_X0 - 0.15, C.STRIP_Y, 0], [C.STRIP_X1 + 0.15, C.STRIP_Y, 0], color=S.ARM,
                       stroke_width=1.5).set_stroke(opacity=0.5)
        T_sweep = self.t("minus one hundred") - S.LEAD
        T_out = self.t("two hundred and one") - S.LEAD
        self.play_at(T_sweep, FadeIn(VGroup(label, num, axis)), spin.animate.set_value(1.0), lead=0, run_time=0.4)
        self.add(num)
        self.play(n_val.animate.set_value(100.0), run_time=self.snap(T_out - self.now - 0.1), rate_func=linear)

        # "two hundred and one": the strip complete; the dots settle back onto the clef and go
        shown.clear_updaters()
        self.beat("two hundred and one", spin.animate.set_value(0.0), FadeOut(dots), FadeOut(VGroup(label, num)),
                  rt=0.5)
        dots.clear_updaters()

        # "biggest to smallest": the bars re-order by height, biggest first
        rank = C.size_rank()
        moves = [b.animate.set_x(C.strip_x(rank[n])) for n, b in bars.items()]
        self.beat("biggest to smallest", *moves, rt=1.2)

        # "tip to tail": the biggest bars lift off, curl into circles and snap onto the chain; the plate takes over
        terms = C.clef_terms()
        joints = C.CLEF_AT + C.CLEF_K * np.concatenate([[0], np.cumsum([c for _, c in terms])])
        by_rank = sorted(bars.items(), key=lambda nb: rank[nb[0]])
        circles = [Circle(radius=C.CLEF_K * abs(c), color=C4.color_of(n), stroke_width=2.5).move_to(C4.to3(joints[k]))
                   for k, (n, c) in enumerate(terms[:N_CURL])]
        plate_op = ValueTracker(0.0)
        self.add(plate_op)
        plate = V.EpicyclePlate(lambda: C.s25_state(self.now, opacity=plate_op.get_value()))
        self.add(plate)
        self.bring_to_back(plate)
        self.beat("tip to tail", LaggedStart(*[ReplacementTransform(b, c) for (n, b), c in zip(by_rank, circles)],
                                             lag_ratio=0.03),
                  FadeOut(VGroup(*[b for _, b in by_rank[N_CURL:]]), shift=UP * 0.3), FadeOut(axis), FadeOut(outline),
                  rt=1.0)
        self.play(plate_op.animate.set_value(1.0), FadeOut(VGroup(*circles)), run_time=self.snap(END - self.now - 0.02))
        self.finish()
