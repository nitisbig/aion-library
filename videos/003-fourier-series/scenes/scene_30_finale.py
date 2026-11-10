"""Scene 30 · Outro: just circles, going round (615.050–621.567 s).

"For now, let's watch it one more time. Just circles, going round. Thanks for watching."

S01's chain (shared.clef_state: the same 201 coefficients), the plane tilted into perspective
with a slow yaw orbit. One loop runs from "for now" to the end of "round" (beats.FINALE_LOOP),
linear with a 0.4 s ease out, so the clef closes as the word ends.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import ValueTracker, linear, smooth, there_and_back

from aion import style as S
import shared as V

START, END = V.scene_range(30)
TILT, YAW_RATE = 25.0, 7.0                 # degrees; degrees per second once the orbit starts


def loop_t(now: float, t0: float, t1: float, ease: float = 0.4) -> float:
    """0 → 1 between t0 and t1: constant speed, then a smooth stop over the last `ease` s."""
    T = t1 - t0
    v = 1.0 / (T - ease / 2)                 # area = v·(T − ease) + v·ease/2 = 1
    u = now - t0
    if u <= 0:
        return 0.0
    if u <= T - ease:
        return v * u
    if u <= T:
        x = (u - (T - ease)) / ease
        return v * (T - ease) + v * ease * (x - x * x / 2)
    return 1.0


def yaw_at(now: float, t0: float) -> float:
    u = now - t0
    if u <= 0:
        return 0.0
    e = 1.0                                   # ease into the orbit over 1 s
    return YAW_RATE * (u * u / (2 * e) if u < e else u - e / 2)


class Scene30Finale(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        t0 = self.t("for now")
        t1 = self.t_end("round", t0)
        t_orbit = self.t("one more time") - S.LEAD
        op, tilt, chain, bloom = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(1.0), ValueTracker(1.0)
        self.add(op, tilt, chain, bloom)

        def state():
            now = self.now
            t = loop_t(now, t0, t1)
            return V.clef_state(t, opacity=op.get_value(), tilt=tilt.get_value(), yaw=yaw_at(now, t_orbit),
                                rim_alpha=chain.get_value(), arm_alpha=chain.get_value(), pen_alpha=chain.get_value(),
                                sparks=0.6 * chain.get_value(), bloom=0.85 * bloom.get_value(), ink_from=0.0, zoom=0.92,
                                rim_vivid=1.0, pen_glow=V.S01_END["pen_glow"])

        self.add(V.EpicyclePlate(state))

        # frame 0: the chain fades up from black and the plane tilts into perspective
        self.play(op.animate.set_value(1.0), tilt.animate.set_value(TILT), run_time=self.snap(1.2), rate_func=smooth)

        # end of "round": the clef closes; a soft flash of bloom runs through it
        self.play_at(t1, bloom.animate(rate_func=there_and_back).set_value(1.8), lead=0.0, run_time=0.5)

        # "thanks for watching": the chain fades; the gold clef holds
        self.beat("thanks for watching", chain.animate.set_value(0.0), rt=0.8)

        # end of "watching": fade to black, landing on the last frame of the audio
        t_end = self.t_end("watching", t1)
        self.play_at(t_end, op.animate.set_value(0.0), lead=0.0, run_time=self.snap(END - t_end - 1 / self.fps))
        self.finish()
