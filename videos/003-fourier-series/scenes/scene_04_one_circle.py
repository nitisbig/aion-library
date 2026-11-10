"""Scene 04 · Ch1: one circle (64.283–84.433 s).

"As with anything new, it's best to start easy. So let's begin with a single circle.
Picture an arrow pinned at the center, turning steadily. For now, ignore everything
except how high its tip is. Up, down, up, down. Now let time move to the right, and
let that height leave a trail."

S03 leaves one blue circle at the left third; it never cuts. An arrow grows, turns
(one turn per 4 s, tip on top exactly on "up"), its height rides a track, and on
"trail" the height starts writing the wave (ch1.OneCircle, stateless in time).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import UP, Dot, FadeIn, FadeOut, VGroup, there_and_back

from aion import style as S
import shared as V
import ch1 as C

START, END = V.scene_range(4)


def pulse_dot(p):
    return VGroup(Dot(p, radius=0.32, color=S.INK).set_opacity(0.18),
                  Dot(p, radius=0.12, color=S.INK).set_opacity(0.9))


class Scene04OneCircle(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        m = C.OneCircle(self, C.S04_START_STATE)

        # "start easy": chapter eyebrow
        eb = V.eyebrow("01 · ONE CIRCLE")
        self.beat("start easy", FadeIn(eb, shift=UP * 0.08), rt=0.6)

        # "single circle": the circle breathes, its hub appears; the eyebrow leaves
        self.beat("single circle", *m.to(arm_op=1.0), m.v["r"].animate(rate_func=there_and_back).set_value(C.R0 * 1.06),
                  FadeOut(eb, rate_func=V.window(0.4, 1.0)), rt=1.0, rate=None)

        # "arrow": it grows from the hub to the rim (its clock turns it from "turning steadily" on)
        self.beat("arrow", *m.to(grow=1.0), rt=0.6)

        # "how high its tip is": the circle dims, the tip's height rides a track
        self.beat("how high its tip is", *m.to(circle_op=0.4, conn_op=1.0, track_op=1.0), rt=0.6)

        # "up, down, up, down": the track's ends glow on each word
        top, bottom = m.track_ends()
        after = self.t("how high its tip is")
        for word, p in (("up", top), ("down", bottom), ("up", top), ("down", bottom)):
            after = self.t(word, after + 0.01)
            d = pulse_dot(p)
            d.set_opacity(0)
            self.add(d)
            self.play_at(after, d[0].animate(rate_func=there_and_back).set_opacity(0.2),
                         d[1].animate(rate_func=there_and_back).set_opacity(0.95), run_time=0.45)
            self.remove(d)

        # "time move to the right": the time axis draws out
        self.beat("time move to the right", *m.to(axis_op=1.0), rt=0.8)

        # "trail": the height writes the wave (it starts by itself at ch1.T_TRAIL)
        self.finish()
