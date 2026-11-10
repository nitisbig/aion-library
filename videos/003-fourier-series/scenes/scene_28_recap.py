"""Scene 28 · Outro: what we built (564.500–596.900 s).

"So let's step back and look at what we've built. One spinning circle gives you the simplest
wave, with a size, a speed, and a starting point. Stack circles tip to tail, and their motions
add up. With the right sizes and speeds, smooth circles can build sharp corners. Fourier's
insight was that almost any repeating shape can be built this way. And once the tip moves in
two directions, those waves become drawings. To find the circles, you spin the drawing
backward and take the average. Whatever stands still is the circle you were looking for."

Four glass cards (aion.components.cards), each a live miniature of its chapter (outro.card1…4).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import UP, FadeIn, FadeOut, LaggedStart, ValueTracker, VGroup, Write, there_and_back

from aion import style as S
from aion.components.cards import card_image
import shared as V
import ch4 as C4
import outro as O
import scene_27_everywhere as S27

START, END = V.scene_range(28)

END_VALS = dict(c1=1.0, c2=1.0, c3=1.0, c4=1.0, ghost=1.0, glow=1.0, size=1.0, speed=1.0, start=1.0)


def cards():
    return [card_image(O.CARD_W, O.CARD_H).move_to(C4.to3(O.center(i))).set_z_index(-10) for i in range(4)]


def picture(now: float, v: dict) -> VGroup:
    """All four cards' contents (v: c1…c4, ghost, glow, size/speed/start opacities)."""
    return VGroup(O.card1(now, v["c1"]), O.chips((v["size"], v["speed"], v["start"]), v["c1"]),
                  O.card2(now, v["c2"]), O.card3_ghost(v["ghost"]) if v["ghost"] > 0 else VGroup(),
                  O.card3(now, v["c3"]), O.card4(now, v["c4"], v["glow"]))


def recipe():
    return V.recipe(40, muted=False).move_to(O.RECIPE_AT)


class Scene28Recap(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        eb = V.eyebrow("06 · DRAWING ANYTHING")
        last = S27.end_picture()
        self.add(eb, last)

        v = {k: ValueTracker(0.0) for k in END_VALS}
        self.add(*v.values())
        self.add(V.redraw(lambda: picture(self.now, {k: t.get_value() for k, t in v.items()})))

        # "step back": the photo goes; four empty glass cards fade up in a row
        cs = cards()
        for c in cs:
            c.set_opacity(0.45)
        self.beat("step back", FadeOut(eb), FadeOut(last, scale=0.9),
                  LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cs], lag_ratio=0.15), rt=0.9)

        # card 1: "simplest wave": one circle and its wave; the three chips on their words
        self.beat("simplest wave", cs[0].animate.set_opacity(1.0), v["c1"].animate.set_value(1.0), rt=0.8)
        self.beat("size", v["size"].animate.set_value(1.0), rt=0.4)
        self.beat("a speed", v["speed"].animate.set_value(1.0), rt=0.4)
        self.beat("starting point", v["start"].animate.set_value(1.0), rt=0.4)

        # card 2: "stack circles": two circles; with "the right sizes" more join, building sharp corners
        self.beat("stack circles", cs[1].animate.set_opacity(1.0), v["c2"].animate.set_value(1.0), rt=0.8)

        # card 3: "Fourier's insight" lights it with the square's ghost; "two directions": the chain draws
        self.beat("fouriers insight", cs[2].animate.set_opacity(1.0), v["ghost"].animate.set_value(1.0), rt=0.5)
        self.beat("two directions", v["c3"].animate.set_value(1.0), rt=0.8)

        # card 4: "spin the drawing backward": the bean turns backward; the recipe writes under the cards
        rec = recipe()
        self.beat("spin the drawing backward", cs[3].animate.set_opacity(1.0), v["c4"].animate.set_value(1.0),
                  Write(rec), rt=1.0)

        # "stands still": the frozen speed-one arm glows green
        self.beat("stands still", v["glow"].animate.set_value(1.0), rt=0.5)

        # "looking for": all four cards glow once
        rims = VGroup(*[O.card_frame(i, 0.0) for i in range(4)])
        self.add(rims)
        self.beat("looking for", LaggedStart(*[r.animate(rate_func=there_and_back).set_stroke(opacity=0.8)
                                               for r in rims], lag_ratio=0.15), rt=0.9, rate=None)
        self.finish()
