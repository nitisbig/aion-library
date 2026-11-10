"""Scene 03 · Intro: a chord, and a recipe (45.900–64.283 s).

"Think of a chord on a piano. You hear one sound, but it's really a few notes played
together. A Fourier series lets you take a shape and pick out the circles inside it.
By the end, you and I will have a recipe that finds the circles for any drawing. I'll
put it on screen now, just so you'll recognize it later."

The analogy before any math: three notes (C4, E4, G4 at their real pitch ratios) sum
to one waveform, and the same move on a shape splits the rounded square into its two
circles. The recipe is planted muted at RECIPE_POS, where S23 will bring it back.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, AnimationGroup, Circle, Create, FadeIn, FadeOut, LaggedStart,
                   Line, ReplacementTransform, Transform, VGroup, Write, always_redraw)

from aion import style as S
import shared as V
from aion.components.term_label import exp_parts, labels

START, END = V.scene_range(3)
WAVE_Y = 0.9


class Scene03Chord(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # "chord on a piano": a line-art octave; C, E, G press down in turn
        keys = V.piano(center=DOWN * 2.45)
        whites, blacks = keys
        self.beat("chord on a piano", LaggedStart(*[FadeIn(k, shift=UP * 0.1) for k in [*whites, *blacks]],
                                                  lag_ratio=0.04), rt=0.8)
        chord = [whites[i] for i in (0, 2, 4)]
        # (the black keys animate last so they stay drawn on top of the pressed whites)
        self.play(LaggedStart(*[k.animate.set_fill(S.INK, 0.22).shift(DOWN * 0.06) for k in chord],
                              lag_ratio=0.35), blacks.animate.set_stroke(opacity=0.55),
                  run_time=self.snap(0.8))

        # "one sound": three silver note waves rise from the keys and merge into one gold wave
        notes = VGroup(*[V.note_wave(hz, center=UP * y, amp=0.24, color=S.ARM, width=2.2)
                         for hz, y in zip(V.CHORD_HZ, (-0.35, 0.65, 1.65))])
        for n, k in zip(notes, chord):
            n.save_state()
            n.stretch(0.04, 0).move_to(k.get_top() + UP * 0.1).set_opacity(0)
        rise = AnimationGroup(*[n.animate.restore() for n in notes], lag_ratio=0.15)
        total = V.chord_wave(center=UP * WAVE_Y, amp=0.24)
        # each note's name and pitch at its wave's left end (C4, E4, G4: the real frequencies)
        tags = VGroup(*[V.label(f"{nm}  {hz:.0f} Hz", 22, S.LABEL_MUTED).next_to(n.get_left(), LEFT, buff=0.0)
                        .move_to([-5.6, n.get_center()[1] + 0.48, 0], aligned_edge=LEFT)
                        for nm, hz, n in zip("CEG", V.CHORD_HZ, [m.copy().restore() for m in notes])])
        key_tags = VGroup(*[V.label(nm, 24, S.INK).move_to(k.get_bottom() + UP * 0.35) for nm, k in zip("CEG", chord)])
        self.add(key_tags.set_opacity(0))
        self.play_at(self.t("one sound"), rise, FadeIn(tags, rate_func=V.window(0.3, 1.0)),
                     key_tags.animate.set_opacity(1.0), run_time=0.8)
        copies = [total.copy() for _ in notes]
        chord_tag = V.label("C + E + G", 22, S.INK).move_to([-5.6, WAVE_Y + 0.95, 0], aligned_edge=LEFT)
        self.play(*[ReplacementTransform(n, c) for n, c in zip(notes, copies)], ReplacementTransform(tags, chord_tag),
                  run_time=self.snap(0.7))
        merged = total.copy()
        self.remove(*copies)
        self.add(merged)

        # "few notes": it splits back into its three notes, then merges again
        split = VGroup(*[V.note_wave(hz, center=UP * y, amp=0.24, color=S.ARM, width=2.2)
                         for hz, y in zip(V.CHORD_HZ, (-0.35, 0.65, 1.65))])
        self.beat("few notes", ReplacementTransform(merged, split), rt=0.6)
        merged = total.copy()
        self.play(ReplacementTransform(split, merged), run_time=self.snap(0.6))

        # "take a shape": keys and wave give way to a gold rounded square
        R = 1.8
        rs = V.rounded_square(R=R, center=UP * 0.2)
        self.beat("take a shape", FadeOut(VGroup(keys, key_tags), shift=DOWN * 0.2), FadeOut(merged), FadeOut(chord_tag),
                  Create(rs), rt=1.0)

        # "pick out the circles": it splits into its two circles (blue r, orange r/9), then re-merges
        big = Circle(radius=R, color=S.FWD, stroke_width=3).move_to(LEFT * 2.3 + UP * 0.2)
        small = Circle(radius=R / 9, color=S.BWD, stroke_width=3).move_to(RIGHT * 2.6 + UP * 0.2)
        tags = VGroup(labels([(complex(-2.3, 0.2), R, exp_parts(1, S.FWD, coef=""), S.FWD, -90.0)], size=40),
                      labels([(complex(2.6, 0.2), R / 9, exp_parts(-3, S.BWD, coef=r"-\tfrac{1}{9}"), S.BWD, -90.0)], size=40))
        self.beat("pick out the circles", ReplacementTransform(rs, VGroup(big, small)),
                  FadeIn(tags, rate_func=V.window(0.5, 1.0)), rt=1.0)
        rs2 = V.rounded_square(R=R, center=UP * 0.2)
        # the two terms hold until just before "recipe", then the circles merge back as the terms fade
        self.wait_until(self.t("recipe") - S.LEAD - 1.0)
        self.play(ReplacementTransform(VGroup(big, small), rs2), FadeOut(tags, rate_func=V.window(0.4, 1.0)),
                  run_time=self.snap(1.0))

        # "recipe": everything fades except one circle, which settles at the left third
        one = V.one_circle()
        self.beat("recipe", ReplacementTransform(rs2, one), rt=0.8)

        # "any drawing": the recipe writes on, muted, upper right, and holds to the end of the scene
        formula = V.recipe(muted=True).move_to(V.RECIPE_POS)
        self.beat("any drawing", Write(formula), rt=1.4)
        self.wait_until(END - 0.6)
        self.play(FadeOut(formula), run_time=self.snap(0.55))
        self.finish()
        self.handoff = {"circle": one}
