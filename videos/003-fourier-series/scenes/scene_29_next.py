"""Scene 29 · Outro: what comes next (596.900–615.050 s).

"There's one thing we quietly assumed, though. Our drawings repeat. The pen always comes back
to where it started. What about a sound that never repeats? Then you need circles of every
possible speed, not just whole numbers. That's the Fourier transform, and it's where we'll go
next."

The bean closes its loop (it is periodic by construction); a sum of incommensurate sines has no
period; the integer speed rack's bars multiply and thicken into one continuous band.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import RIGHT, UP, FadeIn, FadeOut, ValueTracker, VGroup, VMobject, linear, smooth, there_and_back

from aion import style as S
import shared as V
import ch4 as C4
import ch5 as C5
import outro as O
import scene_28_recap as S28

START, END = V.scene_range(29)
BEAN_AT, BEAN_K = complex(0.0, 0.2), 1.35


def bean(u: float, op: float) -> VGroup:
    """The bean drawn by its pen from t = 0 to u (one loop = 1)."""
    if op <= 0:
        return VGroup()
    terms = C5.bean_terms_zero()
    z0 = C5.z_of(terms, np.linspace(0, 1, 800))
    off = BEAN_AT - 0.5 * complex(z0.real.max() + z0.real.min(), z0.imag.max() + z0.imag.min()) * BEAN_K
    g = VGroup()
    if u > 0.002:
        z = off + BEAN_K * C5.z_of(terms, np.linspace(0, min(u, 1.0), max(2, int(800 * min(u, 1.0)))))
        g.add(C4.path(z, S.INK, 3.5, op))
    g.add(C4.pen(off + BEAN_K * C5.z_of(terms, u % 1.0 if u < 1 else 0.0), op))
    return g


def bean_start() -> complex:
    terms = C5.bean_terms_zero()
    z0 = C5.z_of(terms, np.linspace(0, 1, 800))
    off = BEAN_AT - 0.5 * complex(z0.real.max() + z0.real.min(), z0.imag.max() + z0.imag.min()) * BEAN_K
    return off + BEAN_K * C5.z_of(terms, 0.0)


class Scene29Next(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # S28's last picture
        cs = S28.cards()
        rec = S28.recipe()
        o = ValueTracker(1.0)
        self.add(*cs, rec, o)
        self.add(V.redraw(lambda: S28.picture(self.now, {k: val * o.get_value() for k, val in S28.END_VALS.items()})))

        # "quietly assumed": the cards and the recipe fade
        self.beat("quietly assumed", o.animate.set_value(0.0), *[FadeOut(c) for c in cs], FadeOut(rec), rt=0.7)

        # "drawings repeat": a pen draws the bean once; "where it started": it lands on its start, which pings
        u, bo, pu = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        self.add(u, bo, pu)
        self.add(V.redraw(lambda: bean(u.get_value(), bo.get_value())))
        self.add(V.redraw(lambda: C5.ping(bean_start(), pu.get_value(), S.INK)))
        t_land = self.t("where it started") - S.LEAD
        self.beat("drawings repeat", bo.animate.set_value(1.0), rt=0.3)
        self.play(u.animate.set_value(1.0), run_time=self.snap(t_land - self.now), rate_func=smooth)
        self.play(pu.animate.set_value(1.0), run_time=self.snap(0.9), rate_func=linear)

        # "never repeats": the bean goes; a gold wave with no period scrolls past
        t_nr = self.t("never repeats") - S.LEAD
        wo = ValueTracker(0.0)
        self.add(wo)
        shift = ValueTracker(0.0)
        self.add(shift)
        self.add(V.redraw(lambda: O.never_wave(self.now, t_nr, wo.get_value()).shift(RIGHT * shift.get_value())))
        self.beat("never repeats", bo.animate.set_value(0.0), wo.animate.set_value(1.0), rt=1.0)

        # "need circles": the whole-number speeds as bars; "every possible speed": they melt into one band
        m, bando = ValueTracker(0.0), ValueTracker(0.0)
        self.add(m, bando)
        self.add(V.redraw(lambda: O.band(m.get_value(), bando.get_value()).shift(RIGHT * shift.get_value())))
        self.beat("need circles", bando.animate.set_value(1.0), rt=0.6)
        self.beat("every possible speed", m.animate.set_value(1.0), rt=1.8)

        # "Fourier transform": its name under the band, with a light sweep
        name = V.label("Fourier transform", 34, S.LABEL).move_to([0, O.BAND_Y - 0.5, 0])
        self.beat("fourier transform", FadeIn(name, shift=UP * 0.08), rt=0.6)
        self.play(name.animate(rate_func=there_and_back).set_color(S.LIGHT), run_time=self.snap(0.8))

        # "go next": everything drifts right and fades to black before the finale
        self.beat("go next", shift.animate.set_value(1.2), wo.animate.set_value(0.0), bando.animate.set_value(0.0),
                  FadeOut(name, shift=RIGHT * 1.2), rt=self.snap(END - self.t("go next") + S.LEAD - 0.07))
        self.finish()
