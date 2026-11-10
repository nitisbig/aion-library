"""Scene 00 · Cold open: Fourier drawn by his own circles (15 s, before the narration).

No voice. A calm, wide view: 601 circles (speeds −300…300, σ-smoothed) draw Boilly's portrait
of Joseph Fourier as one flowing gold line while his line from the Théorie analytique de la
chaleur (1822) writes on at the right. The chain fades, the line dissolves into the engraving
itself in gold light, which warms into the real portrait. Then everything goes to black for
S01's fade-up.

render.py lays PREVIEW_S of silence under this scene, so S01 still starts at audio time 0.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import DOWN, LEFT, UP, FadeIn, ImageMobject, LaggedStart, Tex, ValueTracker, VGroup, linear, smooth

from aion import style as S
import shared as V

PREVIEW_S = 15.0
AT, K = complex(-3.6, -0.05), 4.25                     # portrait center and scale (≈ 6.6 units tall)
T0, T1 = 0.4, 8.6                                       # the one loop, from T0 to T1 (s)
QUOTE = (("``The", "deep", "study", "of", "nature"),
         ("is", "the", "most", "fruitful", "source"),
         ("of", "mathematical", "discoveries.''"))
GOLD_WORDS = {"nature", "discoveries.''"}
T_CHAIN_OUT = T1 - 0.1                                  # the chain fades as the loop closes
T_GOLD, T_REAL = 9.7, 11.5                              # line → gold engraving → real portrait
T_BLACK = PREVIEW_S - 0.8


def loop_t(now: float) -> float:
    """0 → 1 over [T0, T1]: an unhurried start, an even middle, a soft landing."""
    x = min(1.0, max(0.0, (now - T0) / (T1 - T0)))
    return x - 0.3 * np.sin(2 * np.pi * x) / (2 * np.pi)


def zoom_at(now: float) -> float:
    """A slow, steady push in over the whole scene."""
    return 0.94 + 0.07 * smooth(min(1.0, max(0.0, now / PREVIEW_S)))


def quote() -> VGroup:
    lines = VGroup()
    for words in QUOTE:
        line = Tex(*[r"\textit{%s}" % w for w in words], arg_separator=r"\ ", font_size=50)
        for w, m in zip(words, line):
            m.set_color(S.INK if w in GOLD_WORDS else S.LABEL)
        lines.add(line)
    lines.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    lines[0][0][:1].set_color(S.INK)                    # the opening “ in gold; the closing ” is in gold already
    name = V.label("Joseph Fourier", 24, S.LABEL_MUTED).next_to(lines, DOWN, aligned_edge=LEFT, buff=0.45)
    return VGroup(lines, name).move_to([3.8, 0.1, 0])


class Scene00Preview(V.VideoScene):
    AUDIO = None                                       # silent: the narration starts with S01
    SCENE_START, SCENE_END = 0.0, PREVIEW_S

    def timeline(self):
        terms = [(n, K * c) for n, c in V.portrait_terms()]
        t = self.drive(ValueTracker(0.0), loop_t)
        zoom = self.drive(ValueTracker(1.0), zoom_at)
        op, chain, ink, boost = ValueTracker(0.0), ValueTracker(1.0), ValueTracker(1.0), ValueTracker(0.0)
        self.add(op, chain, ink, boost)

        plate = V.EpicyclePlate(lambda: {
            **V.S01_END, "terms": terms, "origin": AT, "t": t.get_value(), "ink_from": 0.0,
            "ink_samples": 16000, "ink_width": 1.3, "ink_head": 2.5, "ink_fade": 0.85,
            "ink_alpha": ink.get_value(), "ink_boost": boost.get_value(),
            "opacity": op.get_value(), "rim_alpha": 0.8 * chain.get_value(), "rim_count": 60,
            "arm_alpha": 0.35 * chain.get_value(), "pen_alpha": chain.get_value(), "sparks": 0.0,
            "bloom": 0.6, "cam": 0j, "zoom": zoom.get_value()})
        self.add(plate)

        # the engraving under the line, in two looks (aligned to the drawing; scaled with the same zoom)
        gold_a, real_a, c, w = V.portrait_images()
        def image(arr):
            m = ImageMobject(arr)
            m.width = K * w
            m.move_to([AT.real + K * c.real, AT.imag + K * c.imag, 0])
            return m
        gold, real = image(gold_a), image(real_a)
        gold_op, real_op = ValueTracker(0.0), ValueTracker(0.0)
        self.add(gold_op, real_op)
        for m, o in ((gold, gold_op), (real, real_op)):     # follow the plate's zoom; fade by tracker
            m.add_updater(lambda m, dt, o=o, w0=m.width, p0=m.get_center():
                          m.set_width(w0 * zoom.get_value()).move_to(p0 * zoom.get_value())
                          .set_opacity(o.get_value() * op.get_value()))
        self.add(gold, real)

        # frame 0: up from black, wide and still; the chain is already turning
        self.play(op.animate.set_value(1.0), run_time=self.snap(1.0), rate_func=smooth)

        # the quote writes on, word by word
        q = quote()
        lines, name = q
        words = [m for line in lines for m in line]
        self.wait_until(2.6)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.06) for m in words], lag_ratio=0.25),
                  run_time=self.snap(3.2))
        self.play(FadeIn(name, shift=UP * 0.05), run_time=self.snap(0.7))

        # the loop closes: the chain fades away, a light runs through the finished line
        self.wait_until(T_CHAIN_OUT)
        self.play(chain.animate.set_value(0.0), boost.animate.set_value(0.6), run_time=self.snap(1.0),
                  rate_func=smooth)

        # the line dissolves into the engraving itself, drawn in gold light ...
        self.wait_until(T_GOLD)
        self.play(gold_op.animate.set_value(1.0), ink.animate.set_value(0.0), boost.animate.set_value(0.0),
                  run_time=self.snap(1.5), rate_func=smooth)
        # ... which warms into the real portrait
        self.wait_until(T_REAL)
        self.play(real_op.animate.set_value(1.0), gold_op.animate(rate_func=lambda u: smooth(min(1, 1.6 * u))).set_value(0.35),
                  run_time=self.snap(1.6), rate_func=smooth)

        # to black, for S01's fade-up
        self.wait_until(T_BLACK)
        self.play(op.animate.set_value(0.0), q.animate.set_opacity(0.0),
                  run_time=self.snap(0.8 - 1 / self.fps), rate_func=smooth)
        self.finish()
