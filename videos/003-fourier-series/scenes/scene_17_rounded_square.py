"""Scene 17 · Ch4: the friendly example (310.767–330.717 s).

"Here's a friendly example we'll keep coming back to. Take a big circle turning forward
once, and add a small one, one ninth the size, turning backward three times as fast. The
tip traces out a rounded square. And the square from the beginning? Its first two circles
are exactly these."

Drawn at the intro square's own numbers: c₁ = 2.522 and c₋₃ = −0.2802 = −c₁/9 (from the
square's FFT, aion.fourier). So the intro square (half side 2.2) fits around the rounded
square exactly, and the inset's first two circles are these two, at the same ratio.
The big circle makes exactly one turn alone ("turning forward once"), stopping as the
small one arrives, so the small one's half-turn start can be marked against it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import Arc, FadeIn, FadeOut, ValueTracker, VGroup, VMobject, there_and_back

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C
import scene_16_direction as S16

START, END = V.scene_range(17)


def friend_picture(now: float, origin=0j, scale: float = 1.0, op: float = 1.0, r2: float = 1.0,
                   big_op: float = 1.0, ink_op: float = 1.0, ink_w: float = 3.5) -> VGroup:
    """The two-circle chain and its last loop of ink, at absolute time `now`."""
    v = [scale * w for w in C.friend_vecs(now, r2)]
    cols = [S.FWD, S.BWD]
    if r2 <= 0:
        v, cols = v[:1], cols[:1]
    g, _ = C.chain(v, origin, rim_op=op * big_op, arm_op=op * big_op, pen_op=op * big_op, colors=cols,
                   ns=[1, -3][:len(v)] if scale >= 0.7 else None, label_angles=[-50.0, 130.0])
    return VGroup(C.friend_ink(now, origin, scale, op * ink_op, ink_w), g)


class Scene17RoundedSquare(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.add(C2.corner_marker())
        # ── S16's last picture
        s16_op = ValueTracker(1.0)
        self.add(s16_op)
        st = S16.statics()
        self.add(st, V.redraw(lambda: S16.live(self.now, {k: v * s16_op.get_value() if k in "abz" else v
                                                           for k, v in S16.END_OPS.items()})))

        # "friendly example": the stage clears
        self.beat("friendly example", s16_op.animate.set_value(0.0), FadeOut(st), rt=0.6)

        tk = {k: ValueTracker(v) for k, v in dict(big=0.0, r2=0.0, ink_w=3.5, inset=0.0, lit=0.0).items()}
        self.add(*tk.values())
        self.add(V.redraw(lambda: friend_picture(self.now, r2=tk["r2"].get_value(), big_op=tk["big"].get_value(),
                                                 ink_w=tk["ink_w"].get_value())
                          if tk["big"].get_value() > 0 else VMobject()))

        # "big circle": a blue circle, speed +1 (it turns once on "turning forward once")
        self.beat("big circle", tk["big"].animate.set_value(1.0), rt=0.8)

        # "one ninth": an orange circle a ninth the size on its tip, starting half a turn round (violet arc)
        joint = C.C1
        arc = Arc(radius=0.48, start_angle=0, angle=np.pi, arc_center=C.to3(joint), color=S.PHASE, stroke_width=3)
        ref = C.DashedLine(C.to3(joint), C.to3(joint + 0.6), dash_length=0.06, color=S.PHASE, stroke_width=2)
        self.beat("one ninth", tk["r2"].animate.set_value(1.0), FadeIn(VGroup(arc, ref)), rt=0.8)

        # "backward three times": both turn (ch4.friend_clock starts here); the half-turn marks go
        self.beat("backward", FadeOut(VGroup(arc, ref)), rt=0.5)

        # "rounded square": the first loop of ink closes; it brightens once
        self.beat("rounded square", tk["ink_w"].animate(rate_func=there_and_back).set_value(6.0), rt=0.8, rate=None)

        # "square from the beginning": the intro square, as a dashed ghost around it
        ghost = C.square_ghost(0j, 1.0, 0.5)
        self.beat("square from the beginning", FadeIn(ghost), rt=0.8)

        # "first two circles": an inset of the intro's square chain; its first two circles light up: these two
        self.add(V.redraw(lambda: C.square_inset(tk["lit"].get_value(), tk["inset"].get_value())
                          if tk["inset"].get_value() > 0 else VMobject()))
        self.play_at(self.t("first two circles") - 0.6, tk["inset"].animate.set_value(1.0), run_time=0.5)
        self.beat("first two circles", tk["lit"].animate.set_value(1.0), rt=0.8)
        self.finish()
