"""Scene 16 · Ch4: plus, minus, zero (296.467–310.767 s).

"On a page, direction matters. A circle can turn counterclockwise, which we'll call a
positive speed, or clockwise, a negative speed. A circle with speed zero doesn't turn at
all. It just sets where the drawing sits."

Plants the color code used from here on: blue +, orange −, green 0.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import DOWN, Create, FadeIn, FadeOut, MathTex, ValueTracker, VGroup

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C
from scene_15_sky import s15_end_trail

START, END = V.scene_range(16)
TURN = 0.25                                  # loops per second
T_CCW = C.cue("counterclockwise", C.S16)
T_CW = C.cue("clockwise", C.S16, after=C.S16[0] + 4.5)     # (after "counterclockwise")
CLOCKS = (C.Clock([(T_CCW, 0.8, TURN)], START - 1, END + 30), C.Clock([(T_CW, 0.8, TURN)], START - 1, END + 30))
END_OPS = dict(a=1.0, b=1.0, z=1.0, stretch=1.0, swing=1.0, loop=1.0)


def live(now: float, val: dict) -> VGroup:
    """The three circles at absolute time `now`. val: a, b, z (opacities), stretch, swing, loop."""
    ccw, cw = CLOCKS
    A, B, Z = C.SLOTS16
    R = C.R16
    g = VGroup()
    for key, c0, clk, sign, col in (("a", A, ccw, 1, S.FWD), ("b", B, cw, -1, S.BWD)):
        o = val[key]
        if o > 0:
            v = R * np.exp(1j * C.TAU * sign * float(clk(now)))
            m, _ = C.chain([v], c0, rim_op=o, arm_op=o, pen_op=0.0, colors=[col], ns=[sign], label_angles=[-90.0])
            g.add(m)
    o = val["z"]
    if o > 0:
        v = R * (1 + 0.45 * val["stretch"]) * np.exp(1j * np.deg2rad(55) * val["swing"])
        g.add(C.slot(Z, R, S.STILL, 0.45 * o), C.arm(Z, Z + v, o, color=S.STILL, width=3.5))
        if val["loop"] > 0:
            g.add(C.rounded_loop(Z + v, 0.42).set_stroke(opacity=val["loop"] * o))
    return g


def lab(txt, at, col):
    return MathTex(txt, font_size=48, color=col).move_to(C.to3(at) + DOWN * (C.R16 + 0.6))


def statics() -> VGroup:
    """Arrows (0, 1) and labels (2, 3, 4) of S16's picture."""
    A, B, Z = C.SLOTS16
    return VGroup(C.turn_arrow(A, C.R16, +1, S.FWD), C.turn_arrow(B, C.R16, -1, S.BWD),
                  lab("+1", A, S.FWD), lab("-1", B, S.BWD), lab("0", Z, S.STILL))


class Scene16Direction(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.add(C2.corner_marker())
        loops = s15_end_trail()
        self.add(loops)

        # "direction matters": the loops go; three empty slots
        slots = VGroup(*[C.slot(c) for c in C.SLOTS16])
        self.beat("direction matters", FadeOut(loops), FadeIn(slots), rt=0.6)

        ops = {k: ValueTracker(0.0) for k in END_OPS}
        self.add(*ops.values())
        self.add(V.redraw(lambda: live(self.now, {k: v.get_value() for k, v in ops.items()})))
        st = statics()

        # "counterclockwise": left, a blue circle turning counterclockwise; "positive speed": +1
        self.beat("counterclockwise", ops["a"].animate.set_value(1.0), FadeOut(slots[0]), Create(st[0]), rt=0.8)
        self.beat("positive speed", FadeIn(st[2], shift=DOWN * 0.1), rt=0.4)

        # "clockwise": middle, an orange one turning clockwise; "negative speed": −1
        self.play_at(T_CW + S.LEAD, ops["b"].animate.set_value(1.0), FadeOut(slots[1]), Create(st[1]), run_time=0.8)
        self.beat("negative speed", FadeIn(st[3], shift=DOWN * 0.1), rt=0.4)

        # "speed zero": right, a green arm that doesn't turn
        self.beat("speed zero", ops["z"].animate.set_value(1.0), FadeOut(slots[2]),
                  FadeIn(st[4], shift=DOWN * 0.1), rt=0.6)

        # "where the drawing sits": it stretches and swings, carrying a small gold loop: it only places the drawing
        self.beat("where the drawing sits", ops["loop"].animate.set_value(1.0), ops["stretch"].animate.set_value(1.0),
                  ops["swing"].animate.set_value(1.0), rt=1.2)
        self.finish()
