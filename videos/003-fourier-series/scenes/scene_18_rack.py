"""Scene 18 · Ch4: every whole number speed (330.717–351.300 s).

"In general, we line up circles of every whole number speed. Zero, one, minus one, two,
minus two, and so on. Each has two settings left to choose, its size and its starting
angle. So here's the real question. If I hand you a drawing, how do you find the size
and starting angle of every circle?"

The rack: one empty dashed slot per speed (−5…5, sorted on the line, colored by sign),
each with a faint empty radius knob and a violet angle tick. It stays empty: the open
question Ch5 answers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import DOWN, LEFT, RIGHT, FadeIn, FadeOut, LaggedStart, MathTex, ValueTracker, VGroup, VMobject, \
    there_and_back

from aion import style as S
from aion.drawings import treble_clef
import shared as V
import ch2 as C2
import ch4 as C
from scene_17_rounded_square import friend_picture

START, END = V.scene_range(18)
TOP = complex(0.0, 1.75)          # where the drawing sits above the rack
TOP_K = 0.55
FIRST = (0, 1, -1, 2, -2)         # the speeds named aloud, in order
MORE = [n for k in range(3, C.RACK_N + 1) for n in (k, -k)]


def rack(ns) -> dict[int, VGroup]:
    return {n: VGroup(C.rack_slot(n), C.rack_label(n)) for n in ns}


def ellipses() -> VGroup:
    x = C.rack_x(C.RACK_N) + 0.85
    return VGroup(*[MathTex(r"\cdots", font_size=40, color=S.LABEL_MUTED).move_to([s * x, C.RACK_Y, 0]) for s in (-1, 1)])


def clef_ghost(op: float = 0.55) -> VMobject:
    z = treble_clef(1000)
    z = z - z.mean()
    z = TOP + z * (3.1 / (z.imag.max() - z.imag.min()))
    return C.path(np.append(z, z[0]), S.INK, 3.0, op)


def end_picture() -> VGroup:
    """S18's last frame (S19 starts from it): the full empty rack with knobs and ticks, the clef ghost above."""
    ns = sorted(FIRST + tuple(MORE))
    r = rack(ns)
    for n in FIRST:
        r[n][0].set_stroke(opacity=0.85)
    return VGroup(*r.values(), ellipses(), *[C.rack_knob(n) for n in ns], *[C.rack_tick(n) for n in ns], clef_ghost())


class Scene18Rack(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.add(C2.corner_marker())
        # ── S17's last picture: the friendly example (moving), its ghost square, the lit inset
        tk = {k: ValueTracker(v) for k, v in dict(u=0.0, op=1.0, inset=1.0).items()}
        self.add(*tk.values())

        def top():
            u = tk["u"].get_value()
            o, k = u * TOP, 1 + u * (TOP_K - 1)
            op = tk["op"].get_value()
            if op <= 0:
                return VMobject()
            return VGroup(C.square_ghost(o, k, 0.5 * op), friend_picture(self.now, o, k, op, ink_w=3.5 - 1.0 * u))
        self.add(V.redraw(top))
        self.add(V.redraw(lambda: C.square_inset(1.0, tk["inset"].get_value()) if tk["inset"].get_value() > 0
                          else VMobject()))

        # "every whole number speed": the drawing moves up; below it, a row of empty slots
        r = rack(FIRST)
        self.beat("every whole number speed", tk["u"].animate.set_value(1.0), tk["inset"].animate.set_value(0.0),
                  LaggedStart(*[FadeIn(r[n][0]) for n in sorted(FIRST)], lag_ratio=0.12), rt=0.8)

        # "zero, one, minus one, two, minus two": each slot gets its label as it is said
        after = self.t("every whole number speed")
        for n, key in zip(FIRST, ("zero", "one", "minus one", "two", "minus two")):
            after = self.t(key, after)
            self.play_at(after, FadeIn(r[n][1], shift=DOWN * 0.08), r[n][0].animate.set_stroke(opacity=0.85),
                         run_time=0.4)

        # "and so on": more slots fade in toward both edges
        more = rack(MORE)
        dots = ellipses()
        self.beat("and so on", LaggedStart(*[FadeIn(more[n]) for n in MORE], lag_ratio=0.15), FadeIn(dots), rt=0.9)
        ns = sorted(FIRST + tuple(MORE))
        slots = VGroup(*[(r | more)[n][0] for n in ns])

        # "its size": each slot gets a faint empty radius knob; "starting angle": a faint violet tick
        knobs = VGroup(*[C.rack_knob(n) for n in ns])
        ticks = VGroup(*[C.rack_tick(n) for n in ns])
        self.beat("its size", LaggedStart(*[FadeIn(k) for k in knobs], lag_ratio=0.06), rt=0.6)
        self.beat("starting angle", LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.06), rt=0.6)

        # "real question": everything dims except the rack
        self.beat("real question", tk["op"].animate.set_value(0.25), rt=0.6)

        # "hand you a drawing": the clef ghost slides in above the rack; the rounded square goes
        clef = clef_ghost()
        self.beat("hand you a drawing", tk["op"].animate.set_value(0.0), FadeIn(clef, shift=LEFT * 0.6), rt=0.8)

        # "every circle": all slots pulse once, still empty
        self.beat("every circle", LaggedStart(*[s.animate(rate_func=there_and_back).scale(1.18) for s in slots],
                                              lag_ratio=0.05), rt=0.8, rate=None)
        self.finish()
