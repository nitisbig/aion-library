"""Scene 23 · Ch5: spin, then average (438.717–483.567 s).

"If you hold on to just one idea from this video, make it this one. To find any circle,
spin the drawing against it, and take the average. Now we can read the line from the
beginning. c n equals the integral from zero to one, of f of t, times e to the minus two pi
i n t, d t. It looks dense, but it's really just two steps. F of t is the pen's position at
time t. Multiplying by e to the minus two pi i n t turns the drawing backward, n times per
loop. If you saw our video on complex numbers, that's just a point turning around a circle.
Then the integral from zero to one takes the average over one trip around. Spin, then
average. That's all it says."

Pays off the intro's muted line (shared.recipe at RECIPE_POS, planted in S03): it returns to
that exact spot, glides to center, and takes its colors term by term.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, UP, Brace, Circle, FadeIn, FadeOut, LaggedStart, Line, ValueTracker, VGroup, VMobject,
                   there_and_back)

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch5 as C
import scene_22_check as S22

START, END = V.scene_range(23)
F_AT = np.array([0.0, 0.35, 0.0])          # the formula's place at center
F_SCALE = 1.7
CARD_BIG = dict(big_center=(0.0, 0.45, 0.0), big_spread=2.3, big_scale=0.95)


def formula(colored: bool = True):
    f = V.recipe(40, muted=not colored).scale(F_SCALE).move_to(F_AT)
    return f


def mini_bean(now: float, at, op: float, dots: float = 0.0, col: float = 0.0) -> VGroup:
    """A tiny bean with its pen going round (and optionally its 24 dots collapsing to the green mean)."""
    if op <= 0:
        return VGroup()
    k = 0.32
    terms = C.bean_terms_zero()
    o = complex(at[0], at[1]) - k * (0.55 + 0.45j)
    t = np.linspace(0, 1, 500)
    g = VGroup(C4.path(o + k * C.z_of(terms, t), op=0.8 * op, width=2.2))
    L = 0.25 * now
    g.add(C4.Dot(C4.to3(o + k * C.z_of(terms, L % 1.0)), radius=0.06, color=S.INK).set_opacity(op))
    if dots > 0:
        pts = o + k * C.z_of(terms, np.arange(24) / 24)
        g.add(C.dot_cloud(pts, collapse=col, op=dots * op, mean_op=dots * op * np.clip((col - 0.6) / 0.4, 0, 1)))
    return g


def turn_icon(at, now: float, op: float) -> VGroup:
    """A small orange ring turning clockwise (the drawing turned backward)."""
    return C.frame_ring(C4.TAU * 0.4 * now, op, complex(at[0], at[1]), 0.38)


def callback(now: float, op: float) -> VGroup:
    """Video 001: a point turning around the unit circle (arrow z, quarter-turn arc in violet)."""
    if op <= 0:
        return VGroup()
    c, r = complex(5.25, 1.75), 0.75
    a = -C4.TAU * 0.4 * now
    g = VGroup(Line(C4.to3(c - 1.05), C4.to3(c + 1.05), color=S.REAL, stroke_width=1.5).set_stroke(opacity=0.5 * op),
               Line(C4.to3(c - 1.05j), C4.to3(c + 1.05j), color=S.IMAG, stroke_width=1.5).set_stroke(opacity=0.5 * op),
               Circle(radius=r, color=S.ARM, stroke_width=2).move_to(C4.to3(c)).set_stroke(opacity=0.6 * op),
               C4.arm(c, c + r * np.exp(1j * a), op, color=S.Z, width=3.5))
    g.add(V.label("video 001", 18, S.LABEL_MUTED).move_to(C4.to3(c - 1.3j)).set_opacity(op))
    return g


class Scene23Recipe(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        L = S.LEAD
        items = S22.end_rack()
        rack = VGroup(*items.values())
        dial = C.dial(2)
        self.add(rack, dial, V.eyebrow("05 · SPIN AND AVERAGE"), C2.corner_marker())
        o22 = ValueTracker(1.0)
        self.add(o22)
        self.add(V.redraw(lambda: S22.picture(self.now, {**S22.END_VALS, "op": o22.get_value()})))

        cu, ring, lift = ValueTracker(1.0), ValueTracker(0.0), ValueTracker(0.0)
        self.add(cu, ring, lift)

        def the_card():
            u = cu.get_value()
            g = C.card_lerp(self.now, u, lift=lift.get_value(), **CARD_BIG)
            if ring.get_value() > 0:
                e = u * u * (3 - 2 * u)
                lc = (1 - e) * (np.array(CARD_BIG["big_center"]) + np.array([-CARD_BIG["big_spread"], 0, 0])) + \
                    e * (C.CARD_DOCK + np.array([-0.95, 0, 0]))
                sc = (1 - e) * CARD_BIG["big_scale"] + e * 0.3
                g.add(C.frame_ring(C4.TAU * 0.4 * self.now, ring.get_value(), complex(lc[0], lc[1]), C.ICON_R * sc + 0.3))
            return g
        self.add(V.redraw(the_card))

        # "just one idea": everything dims except the rule card, which comes to center and grows
        self.beat("just one idea", o22.animate.set_value(0.06), rack.animate.fade(0.7),
                  dial.animate.set_opacity(0.2), cu.animate.set_value(0.0), rt=0.8)

        # "spin the drawing against it": an orange turning ring; "take the average": the averages light
        self.beat("spin the drawing against it", ring.animate.set_value(1.0), rt=0.6)
        self.beat("take the average", lift.animate(rate_func=there_and_back).set_value(1.0), rt=0.8, rate=None)

        # "line from the beginning": the card docks; the intro's muted line returns at its spot, then to center
        muted = V.recipe(40).move_to(V.RECIPE_POS)
        self.beat("line from the beginning", cu.animate.set_value(1.0), ring.animate.set_value(0.0),
                  o22.animate.set_value(0.0), FadeOut(dial), FadeIn(muted), rt=0.8)
        self.play(muted.animate.scale(F_SCALE).move_to(F_AT), run_time=self.snap(0.8))
        f = muted

        # term by term: c_n green, ∫…dt silver, f(t) gold, e^{−2πint} orange
        col = {0: S.STILL, 2: S.ARM, 3: S.INK, 4: S.BWD, 5: S.ARM}
        self.beat("c n", f[0].animate.set_color(col[0]).set_opacity(1.0), f[1].animate.set_color(S.LABEL).set_opacity(1.0),
                  rt=0.4)
        self.beat("integral", f[2].animate.set_color(col[2]).set_opacity(1.0),
                  f[5].animate.set_color(col[5]).set_opacity(1.0), rt=0.4)
        self.beat("f of t", f[3].animate.set_color(col[3]).set_opacity(1.0), rt=0.4)
        self.beat("e to the minus", f[4].animate.set_color(col[4]).set_opacity(1.0), rt=0.4)

        # "two steps": ① under f(t)·e^{−2πint}, ② under the whole integral
        b1 = Brace(VGroup(f[3], f[4]), DOWN, buff=0.12, color=S.LABEL)
        b2 = Brace(VGroup(f[2], f[5]), DOWN, buff=0.75, color=S.ARM)
        n1 = V.label("1", 26, S.LABEL).next_to(b1, DOWN, buff=0.1)
        n2 = V.label("2", 26, S.LABEL_MUTED).next_to(b2, DOWN, buff=0.1)
        self.beat("two steps", FadeIn(VGroup(b1, n1), shift=UP * 0.05), FadeIn(VGroup(b2, n2), shift=UP * 0.05), rt=0.6)

        # "pen's position": f(t) lifts; a tiny pen on the bean beside it
        bo, bd, bc = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        self.add(bo, bd, bc)
        f_top = f[3].get_top() + UP * 1.05
        self.add(V.redraw(lambda: mini_bean(self.now, f_top, bo.get_value(), bd.get_value(), bc.get_value())))
        self.beat("pen's position", f[3].animate(rate_func=there_and_back).shift(UP * 0.15), bo.animate.set_value(1.0),
                  rt=0.8, rate=None)

        # "turns the drawing backward": a small clockwise ring beside e^{−2πint}; "n times per loop": its n pulses blue
        to = ValueTracker(0.0)
        self.add(to)
        e_top = f[4].get_top() + UP * 0.75
        self.add(V.redraw(lambda: turn_icon(e_top, self.now, to.get_value())))
        self.beat("turns the drawing backward", to.animate.set_value(1.0), rt=0.6)
        self.beat("n times per loop", f[4][5].animate(rate_func=there_and_back).scale(1.6).set_color(S.FWD), rt=0.6,
                  rate=None)

        # "complex numbers": callback to video 001: a point turning around a circle (in, then out)
        co = ValueTracker(0.0)
        self.add(co)
        self.add(V.redraw(lambda: callback(self.now, co.get_value())))
        self.beat("complex numbers", co.animate.set_value(1.0), rt=0.6)
        self.play_at(self.t_end("circle", self.t("complex numbers")) + 0.25, co.animate.set_value(0.0), lead=0,
                     run_time=0.6)

        # "takes the average": ② and ∫…dt brighten; the mini bean's dots collapse to their mean
        self.beat("takes the average", VGroup(b2, n2).animate.set_color(S.LABEL), f[2].animate.set_color(S.LABEL),
                  f[5].animate.set_color(S.LABEL), bd.animate.set_value(1.0), rt=0.5)
        self.play(bc.animate.set_value(1.0), run_time=self.snap(1.0))

        # "spin then average": the insets go; a light sweep crosses the formula
        glyphs = [g for part in f for g in part]
        self.beat("spin then average", bo.animate.set_value(0.0), to.animate.set_value(0.0),
                  LaggedStart(*[g.animate(rate_func=there_and_back).set_color(S.LIGHT) for g in glyphs],
                              lag_ratio=0.08), rt=1.2, rate=None)
        self.play(VGroup(b2, n2, f[2], f[5]).animate.set_color(S.ARM), run_time=self.snap(0.5))
        self.finish()


def end_formula():
    """S23's last picture of the formula (colored) with its two braces (S24 starts from it)."""
    f = V.recipe(40, muted=False).scale(F_SCALE).move_to(F_AT)
    b1 = Brace(VGroup(f[3], f[4]), DOWN, buff=0.12, color=S.LABEL)
    b2 = Brace(VGroup(f[2], f[5]), DOWN, buff=0.75, color=S.ARM)
    return VGroup(f, b1, V.label("1", 26, S.LABEL).next_to(b1, DOWN, buff=0.1),
                  b2, V.label("2", 26, S.LABEL_MUTED).next_to(b2, DOWN, buff=0.1))
