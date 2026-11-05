"""Scene 18 · Ch5: the determinant shortcut (413.117–439.267 s).

"There's even a shortcut. Multiply the two bending numbers and subtract the twist
squared. That's the determinant and it equals the two eigenvalues multiplied together.
If it's negative, they have opposite signs. A saddle. If it's positive, they share a
sign and the bending in x tells you which. For the puzzle surface, two times two is
four. Three squared is nine. Four minus nine is minus five. A saddle, confirmed."

The mini surface gives way to the formula det H = f_xx f_yy − f_xy² = λ₁λ₂ and a glass
card with the 2D test (the Ch1 card, one dimension up). The puzzle surface: 2·2 − 3² =
−5 < 0, and the walker lands on its eigenvalues (5, −1) in a saddle quadrant
(ch5 asserts det = −5 = λ₁λ₂).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
import shared as V
import ch5 as C

START, END = V.scene_range(18)


class Scene18Det(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 17's last frame ──
        e = C.s17_end()
        ax, l1, l2, dot = e["ax"], e["l1"], e["l2"], e["dot"]
        gauges, ks = e["ring"]
        self.add(e["plate"], *e["rig"].trackers(), l1, l2, *ks, e["quads"], ax, e["labels"], e["qlabels"],
                 gauges, dot)
        q = {n: e["quads"][n - 1] for n in (1, 2, 3, 4)}

        # 5-6 · the shortcut: det H = f_xx f_yy − f_xy² = λ₁λ₂
        for g in gauges:
            g.clear_updaters()
        self.beat("shortcut", *e["rig"].to(opacity=0.0), FadeOut(gauges), rt=0.6)
        self.remove(e["plate"])
        eq = C.eq_det()
        self.beat("multiply the two bending numbers", FadeIn(eq[2:4], shift=UP * 0.1), rt=0.8)
        self.beat("subtract the twist squared", FadeIn(eq[4:], shift=UP * 0.1), rt=0.6)
        self.beat("determinant", FadeIn(eq[:2], shift=RIGHT * 0.1), rt=0.6)
        lam = C.eq_lams(eq)
        self.beat("multiplied together", FadeIn(lam, shift=UP * 0.1), rt=0.6)

        # the test, as a glass card; each row lights its quadrants
        card, head, rows = C.det_card()
        pulse = lambda *ns: [V.pulse(q[n], lambda m: m.set_fill(opacity=0.32)) for n in ns]
        self.beat("negative", FadeIn(card, shift=UP * 0.1), FadeIn(head), FadeIn(VGroup(*rows[0][:2])),
                  *pulse(2, 4), rt=0.7, after=423.0)
        self.beat("saddle", FadeIn(rows[0][2], shift=LEFT * 0.1), rt=0.4, after=425.0)
        self.beat("positive", FadeIn(VGroup(*rows[1][:2])), FadeIn(VGroup(*rows[2][:2])), *pulse(1, 3),
                  rt=0.7, after=426.0)
        self.beat("tells you which", FadeIn(rows[1][2], shift=LEFT * 0.1), FadeIn(rows[2][2], shift=LEFT * 0.1),
                  rt=0.6)

        # 5-7 · the puzzle surface: 2·2 − 3² = 4 − 9 = −5
        pz, calc = C.eq_puzzle(), C.eq_calc()
        self.beat("puzzle surface", FadeOut(eq), FadeOut(lam), FadeIn(pz, shift=UP * 0.1), rt=0.6)
        self.beat("two times two", FadeIn(calc[:3], shift=UP * 0.1), rt=0.6)
        self.beat("three squared", FadeIn(calc[3:5], shift=UP * 0.1), rt=0.6)
        self.beat("four minus nine", FadeIn(calc[5:9], shift=UP * 0.1), rt=0.5)
        self.beat("minus five", FadeIn(calc[9:], scale=1.3), rt=0.5)
        self.beat("confirmed", l1.animate.set_value(C.PUZ_EIG[0]), l2.animate.set_value(C.PUZ_EIG[1]),
                  V.pulse(rows[0][2], lambda m: m.scale(1.25)), *pulse(4), rt=0.7, after=437.0)
        self.finish()
