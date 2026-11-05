"""Scene 26 · Outro: back to the fog (594.933–604.550 s).

"So the next time you're standing somewhere flat, in the fog, you'll know what to ask.
Not which way is down, but how the ground bends. Thanks for watching."

The recap matrix dissolves into the opening shot: the walker on its flat disc in the
fog. The four probe arrows find no slope; then the fog lifts and the walker stands on a
saddle, its smile and frown lines glowing at right angles. Fade to black.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch7 as C
from scene_01_fog import probe_arrow

START, END = V.scene_range(26)


class Scene26Fog(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 25's last frame ──
        recap = C.s25_end()
        self.add(recap)

        # O-5 · the opening shot again
        clk = ValueTracker(0.0)
        fog = V.intro_rig(clk, **C.FOG, opacity=0.0)
        self.run_clock(fog["time"], clk)
        plate = V.terrain_plate(fog)
        self.add(plate, *fog.trackers())
        self.bring_to_front(recap)
        me = V.walker()
        V.pin(me, plate, V.on_surface(plate, 0, 0, 0.03))
        a = ValueTracker(0.0)
        me.add_updater(lambda m: V.set_walker_alpha(m, a.get_value()))
        self.add(me, a)
        self.beat("next time", FadeOut(recap), *fog.to(opacity=1.0), a.animate.set_value(1.0), rt=1.2)

        # O-6 · not which way is down …
        ks = [ValueTracker(0.0) for _ in range(4)]
        probes = [probe_arrow(plate, d, k) for d, k in zip(((1, 0), (0, 1), (-1, 0), (0, -1)), ks)]
        self.add(*probes, *ks)
        self.beat("which way is down", LaggedStart(*[k.animate(rate_func=there_and_back).set_value(1.0) for k in ks],
                                                   lag_ratio=0.15), rt=1.0, rate=linear)
        self.remove(*probes)

        # … but how the ground bends: the fog lifts on a saddle
        self.beat("how the ground bends", *fog.to(**C.LIFT), rt=1.6)

        # O-7 · thanks for watching: hold, then fade to black on the last frame
        fade_at = END - 0.6
        self.wait_until(fade_at)
        self.play(*fog.to(opacity=0.0), a.animate.set_value(0.0), run_time=self.snap(END - self.now), rate_func=smooth)
        self.finish()
