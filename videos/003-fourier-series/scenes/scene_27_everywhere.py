"""Scene 27 · Ch6: sound and pictures (540.800–564.500 s).

"That's why this idea shows up everywhere. Think back to the piano chord. A sound is a wave,
so it has circles too. A singer and a violin playing the same note spin their slowest circle
at the same speed. It's the faster circles on top that make them sound different. And your
phone uses a cousin of this idea to shrink photos and music, keeping the big circles and
dropping the tiny ones you won't notice."

Pays off S03's piano chord. The two voices are seeded syntheses with the same fundamental
(ch6.VOICES). The photo is the clef rasterized at 128 px; its 8×8 block DCT (scipy.fft) keeps
the biggest 10 % of coefficients and is rebuilt with idctn: real numbers, not a fake blur.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, UP, Create, DashedLine, FadeIn, FadeOut, Group, ImageMobject, LaggedStart, Line,
                   ReplacementTransform, Square, ValueTracker, VGroup, there_and_back)
from manim.constants import RESAMPLING_ALGORITHMS

from aion import style as S
import shared as V
import ch6 as C
import scene_26_smooth_sharp as S26

START, END = V.scene_range(27)
WAVE_Y = 0.9                                  # S03's chord wave height
IMG_AT, IMG_H = np.array([-3.0, -0.25, 0.0]), 5.2
BARS_X0, BARS_W, BARS_Y, BARS_H = 0.9, 5.4, -2.4, 3.6


def image(a: np.ndarray, op: float = 1.0) -> ImageMobject:
    m = ImageMobject(C.tinted(a))
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return m.set(height=IMG_H).move_to(IMG_AT).set_opacity(op)


def block_grid(op: float) -> VGroup:
    n = C.IMG_N // C.BLOCK
    x0, y0 = IMG_AT[0] - IMG_H / 2, IMG_AT[1] - IMG_H / 2
    g = VGroup()
    for i in range(n + 1):
        u = IMG_H * i / n
        g.add(Line([x0 + u, y0, 0], [x0 + u, y0 + IMG_H, 0]), Line([x0, y0 + u, 0], [x0 + IMG_H, y0 + u, 0]))
    return g.set_stroke(S.ARM, 0.8, op)


def block_square(rc) -> Square:
    n = C.IMG_N // C.BLOCK
    s = IMG_H / n
    r, c = rc
    x = IMG_AT[0] - IMG_H / 2 + (c + 0.5) * s
    y = IMG_AT[1] + IMG_H / 2 - (r + 0.5) * s
    return Square(side_length=s, color=S.LIGHT, stroke_width=3).move_to([x, y, 0])


def block_bars() -> tuple:
    """The busy block's 64 coefficients, biggest first, as bars (height ∝ |c|, sqrt scale for legibility)."""
    d = C.photo_dct()[C.busy_block()].ravel()
    order = np.argsort(-np.abs(d))
    mags = np.abs(d[order])
    top = np.sqrt(mags[0])
    bars, kept = VGroup(), []
    for i, m in enumerate(mags):
        x = BARS_X0 + BARS_W * i / 63
        h = BARS_H * np.sqrt(m) / top
        bars.add(Line([x, BARS_Y, 0], [x, BARS_Y + max(h, 0.01), 0], color=S.INK, stroke_width=4))
        kept.append(m >= C.keep_threshold())
    return bars, np.array(kept), BARS_Y + BARS_H * np.sqrt(C.keep_threshold()) / top


class Scene27Everywhere(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        eb = V.eyebrow("06 · DRAWING ANYTHING")
        panels = S26.end_picture()
        self.add(eb, panels)

        # "everywhere": the three panels shrink into a small icon top-left, then step aside
        self.beat("everywhere", panels.animate.scale(0.22).move_to([-5.3, 2.25, 0]).set_opacity(0.6), rt=0.6)

        # "piano chord": the intro's keys (C, E, G pressed) and its gold chord wave return
        keys = V.piano(center=DOWN * 2.45)
        whites, blacks = keys
        for i in (0, 2, 4):
            whites[i].set_fill(S.INK, 0.22).shift(DOWN * 0.06)
        chord = V.chord_wave(center=UP * WAVE_Y, amp=0.24)
        self.beat("piano chord", FadeOut(panels), FadeIn(keys, shift=UP * 0.1), Create(chord), rt=0.8)

        # "sound is a wave": the keys go; the chord wave becomes the singer's wave
        singer = C.voice_wave("singer")
        self.beat("sound is a wave", FadeOut(keys, shift=DOWN * 0.2), ReplacementTransform(chord, singer), rt=0.8)

        # "singer and a violin": the violin's wave below; each voice's strip of circles on the right
        violin = C.voice_wave("violin")
        names = VGroup(V.label("singer", 24, S.LABEL_MUTED).next_to(singer, UP, buff=0.12).align_to(singer, LEFT),
                       V.label("violin", 24, S.LABEL_MUTED).next_to(violin, UP, buff=0.12).align_to(violin, LEFT))
        bars = {k: C.voice_bars(k) for k in C.VOICES}
        axes = VGroup(*[C.voice_axis(k) for k in C.VOICES])
        self.beat("singer and a violin", Create(violin), FadeIn(names), FadeIn(axes),
                  LaggedStart(*[Create(b) for k in C.VOICES for b in bars[k] if b.get_length() > 0.02],
                              lag_ratio=0.05), rt=1.0)

        # "slowest circle": both first bars light, joined by a dashed line: the same speed
        first = VGroup(bars["singer"][0], bars["violin"][0])
        x = bars["singer"][0].get_x()
        tie = DashedLine([x, bars["violin"][0].get_bottom()[1] - 0.15, 0], [x, bars["singer"][0].get_top()[1] + 0.2, 0],
                         color=S.STILL, stroke_width=2, dash_length=0.08)
        rest = VGroup(*[b for k in C.VOICES for b in bars[k][1:]])
        self.beat("slowest circle", first.animate.set_color(S.STILL).set_stroke(width=9), rest.animate.set_opacity(0.35),
                  Create(tie), rt=0.6)

        # "faster circles on top": the others glow back, different in each voice
        self.beat("faster circles on top", rest.animate.set_opacity(1.0), rt=0.4)
        self.play(rest.animate(rate_func=there_and_back).set_color(S.LIGHT), run_time=self.snap(0.7))

        # "shrink photos": the sound goes; the clef as a 128-px photo, split into 8×8 blocks
        sound = VGroup(singer, violin, names, axes, first, rest, tie)
        orig = image(C.photo())
        grid = block_grid(0.35)
        self.beat("shrink photos", FadeOut(sound), FadeIn(orig), rt=0.6)
        self.play(Create(grid, lag_ratio=0.01), run_time=self.snap(0.6))

        # "keeping the big circles": one busy block's 64 coefficients, biggest first; a threshold rises
        sq = block_square(C.busy_block())
        cbars, kept, y_cut = block_bars()
        cut = DashedLine([BARS_X0 - 0.2, BARS_Y, 0], [BARS_X0 + BARS_W + 0.2, BARS_Y, 0], color=S.ARM, stroke_width=2)
        self.beat("keeping the big circles", Create(sq), LaggedStart(*[Create(b) for b in cbars], lag_ratio=0.02),
                  FadeIn(cut), rt=0.8)
        drop = VGroup(*[b for b, k in zip(cbars, kept) if not k])
        self.play(cut.animate.set_y(y_cut), drop.animate.set_opacity(0.12), run_time=self.snap(0.9))

        # "wont notice": a thin wipe replaces the photo with its 10 % rebuild: nearly the same
        wipe = ValueTracker(0.0)
        self.add(wipe)
        a0, a1 = C.photo(), C.photo_kept()

        def composite():
            k = int(round(wipe.get_value() * C.IMG_N))
            a = a0.copy()
            a[:, :k] = a1[:, :k]
            m = image(a)
            if 0 < k < C.IMG_N:
                x = IMG_AT[0] - IMG_H / 2 + IMG_H * k / C.IMG_N
                return Group(m, Line([x, IMG_AT[1] - IMG_H / 2, 0], [x, IMG_AT[1] + IMG_H / 2, 0],
                                     color=S.LIGHT, stroke_width=2))
            return Group(m)
        self.remove(orig)
        self.add(V.redraw(composite))
        self.bring_to_front(grid, sq)
        tag = V.label("10 % of the circles", 24, S.LABEL_MUTED).next_to(orig, DOWN, buff=0.12)
        self.beat("wont notice", wipe.animate.set_value(1.0), FadeIn(tag), grid.animate.set_stroke(opacity=0.0),
                  rt=0.9)
        self.finish()


def end_picture() -> Group:
    """S27's last picture (S28 starts from it): the 10 % photo, its tag, the block, its bars and the cut."""
    orig = image(C.photo_kept())
    cbars, kept, y_cut = block_bars()
    for b, k in zip(cbars, kept):
        if not k:
            b.set_opacity(0.12)
    cut = DashedLine([BARS_X0 - 0.2, y_cut, 0], [BARS_X0 + BARS_W + 0.2, y_cut, 0], color=S.ARM, stroke_width=2)
    tag = V.label("10 % of the circles", 24, S.LABEL_MUTED).next_to(orig, DOWN, buff=0.12)
    return Group(orig, block_square(C.busy_block()), cbars, cut, tag)
