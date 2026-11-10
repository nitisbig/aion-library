"""Scene 05 · Ch1: size, speed, start (84.433–114.283 s).

"What you get is a sine wave. ... it's just a circle seen from the side. A spinning
circle has only three settings. There's its size. ... its speed. ... And there's where
it starts. Start the arrow a quarter turn ahead, and the whole wave slides over. Size,
speed, and starting point. That's everything one circle can do."

Each setting changes exactly one thing, with a dim ghost of the wave before the change.
The whole wave is always drawn from the current settings, so it reshapes in place.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, UP, FadeIn, FadeOut, LaggedStart, MathTex, ReplacementTransform, RoundedRectangle,
                   VGroup, Write, smooth)

from aion import style as S
import shared as V
import ch1 as C

START, END = V.scene_range(5)
LABEL_POS = C.LABEL_POS
CHIPS = (("size", S.ARM), ("speed", S.FWD), ("start", S.PHASE))


def chip(text, color, x):
    box = RoundedRectangle(corner_radius=0.2, width=1.5, height=0.5).set_fill(S.STAGE_RAISED, 1)
    box.set_stroke(S.ARM, 1.4, 0.3)
    t = V.label(text, 22, S.LABEL_MUTED).set_opacity(0.5)
    g = VGroup(box, t).move_to([x, -3.05, 0])
    t.move_to(box)
    g.accent = color
    return g


def lit(c, on=True):
    """Animations that light (or dim) one chip."""
    box, t = c
    if on:
        return [box.animate.set_stroke(c.accent, 2.0, 1.0), t.animate.set_color(c.accent).set_opacity(1.0)]
    return [box.animate.set_stroke(S.ARM, 1.4, 0.3), t.animate.set_color(S.LABEL_MUTED).set_opacity(0.5)]


class Scene05Settings(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        m = C.OneCircle(self, C.S04_END)

        # "sine wave": its name
        sin_t = MathTex(r"\sin", "t", font_size=48, color=S.INK).move_to(LABEL_POS)
        self.beat("sine wave", Write(sin_t), rt=0.6)

        # "seen from the side": the circle turns edge-on (a vertical line), then back
        self.beat("seen from the side", *m.to(tilt=0.02), rt=1.0)
        self.wait(self.snap(0.6))
        self.play(*m.to(tilt=1.0), run_time=self.snap(0.8), rate_func=smooth)

        # "three settings": three chips under the stage
        chips = VGroup(*[chip(t, c, x) for (t, c), x in zip(CHIPS, (0.5, 2.3, 4.1))])
        self.beat("three settings", LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in chips], lag_ratio=0.15), rt=0.8)

        # "its size": bigger circle, taller wave; the old wave stays as a ghost
        m.set(gr=C.R0, gn=1.0, gphi=0.0)
        self.beat("its size", *lit(chips[0]), *m.to(ghost_op=1.0, r=1.5 * C.R0), rt=1.0)

        # "its speed": ghost out, then twice the turns, twice the wiggles
        T_sp = self.t("its speed")
        self.wait_until(T_sp - S.LEAD - 0.4)
        self.play(*m.to(ghost_op=0.0), run_time=self.snap(0.35))
        m.set(gr=1.5 * C.R0, gn=1.0, gphi=0.0)
        self.play_at(T_sp, *lit(chips[0], False), *lit(chips[1]), *m.to(ghost_op=1.0, n=2.0), run_time=1.0)

        # "where it starts": chip 3
        self.beat("where it starts", *lit(chips[1], False), *lit(chips[2]), *m.to(ghost_op=0.0), rt=0.4)

        # "quarter turn ahead": a violet arc, the arm jumps ahead, the wave slides over
        m.set(gr=1.5 * C.R0, gn=2.0, gphi=0.0)
        self.beat("quarter turn ahead", m.arc_op.animate(rate_func=V.window(0, 0.45)).set_value(1.0),
                  *[a for a in m.to(ghost_op=1.0, phi=np.pi / 2)], rt=0.9)

        # "size, speed, and starting point": the chips light again with the words
        T_size = self.t("size", self.t("slides over"))
        self.wait_until(T_size - S.LEAD - 0.5)
        self.play(m.arc_op.animate.set_value(0.0), *m.to(ghost_op=0.0), *lit(chips[2], False),
                  run_time=self.snap(0.4))
        after = T_size - 0.01
        for c, word in zip(chips, ("size", "speed", "starting point")):
            after = self.t(word, after)
            self.play_at(after, *lit(c), run_time=0.3)

        # "everything one circle can do": the formula assembles from the chips
        f = C.formula()
        self.beat("everything one circle can do",
                  ReplacementTransform(sin_t[0], f[1]), ReplacementTransform(sin_t[1], f[3]),
                  *[ReplacementTransform(chips[k][1].copy(), f[i]) for k, i in ((0, 0), (1, 2), (2, 5))],
                  FadeIn(VGroup(f[4], f[6])), FadeOut(chips, shift=DOWN * 0.1), rt=1.2)
        self.finish()
        self.handoff = {"machine": m, "formula": f}
