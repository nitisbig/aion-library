"""Scene 11 · Ch3: a hot ring (204.617–228.117 s).

"Now you might be wondering why anyone would build waves out of circles in the first
place. The short answer is heat. In eighteen oh seven, Fourier was trying to describe how
heat spreads through a solid. Take a metal ring, heat one half with a flame, cool the other
half with ice, and let it go. Hot on one side, cold on the other. Unroll the ring, and
that's our square wave."

MeshPlate (moderngl): one tube that is a bar (v = 1) or a ring (v = 0), temperature on its
arc (ch3). The bar's hot spot spreads by the 1D heat kernel. Flame and frost are stateless
particles. The crown is the temperature profile; unrolled, it is the square wave.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import UP, DOWN, FadeIn, FadeOut, ValueTracker, there_and_back

from aion import style as S
from aion.components.title import TitlePlate
import shared as V
import ch2 as C2
import ch3 as H

START, END = V.scene_range(11)


class Scene11HotRing(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        L = S.LEAD
        # ── S10's last frame: the floating square wave + the red corner marker
        wave = C2.final_wave()
        marker = C2.corner_marker()
        self.add(wave, marker)

        tk = {k: ValueTracker(v) for k, v in dict(op=0.0, v=0.0, hot=1.0, cold=1.0, spot=0.0, crown=0.0,
                                                  dist=7.6, tz=0.25).items()}
        self.add(*tk.values())
        T_spread = self.t("spreads through a solid") - L
        T_flame, T_ice, T_go = self.t("flame") - L, self.t("ice") - L, self.t("let it go") - L

        def temperature():
            T = H.SQUARE * np.where(H.SQUARE > 0, tk["hot"].get_value(), tk["cold"].get_value())
            a = tk["spot"].get_value()
            if a > 0:                                      # bar: one hot spot spreading (1D heat kernel)
                age = max(0.0, self.now - T_spread)
                s = H.R * H.PSI
                w2 = 0.09 + 4 * 0.55 * age
                T = T + a * 1.15 * np.exp(-s * s / w2) * np.sqrt(0.09 / w2)
            return T

        def state():
            v = tk["v"].get_value()
            m, g = H.ring_parts(temperature(), v=v, crown=tk["crown"].get_value())
            xyz, rgba, size = [], [], []
            for kind, t_on, t_off in (("flame", T_flame, T_go), ("frost", T_ice, T_go)):
                p = H.particles(self.now, t_on, t_off, kind, v=v)
                xyz.append(p[0]); rgba.append(p[1]); size.append(p[2])
            return {**H.CAM, "dist": tk["dist"].get_value(), "target": (0.0, -H.R * v * 0.0, tk["tz"].get_value()),
                    "meshes": m, "glass": g, "opacity": tk["op"].get_value(),
                    "points": (np.concatenate(xyz), np.concatenate(rgba), np.concatenate(size))}

        plate = H.MeshPlate(state)
        self.add(plate)
        self.bring_to_back(plate)

        # "wondering": chapter eyebrow; the square wave steps back
        eb = V.eyebrow("03 · FOURIER'S HOT RING")
        self.beat("wondering", FadeIn(eb, shift=UP * 0.08), wave.animate.set_stroke(opacity=0.3), rt=0.6)

        # "heat": the intro's teaser ring returns, larger, then leaves; the wave goes too
        self.beat("heat", tk["op"].animate.set_value(1.0), wave.animate.set_stroke(opacity=0.0), FadeOut(eb), rt=0.8)
        self.wait(self.snap(0.5))

        # "eighteen oh seven": a large faint year behind everything; the teaser ring goes
        year = TitlePlate("1807", size_px=300, weight=500, glow=0.0).set_opacity(0.0)
        self.add(year)
        self.bring_to_back(year)
        self.beat("eighteen oh seven", year.animate.set_opacity(0.12), tk["op"].animate.set_value(0.0), rt=0.8)

        # "spreads through a solid": a straight bar with one hot spot; the heat spreads along it
        for k, val in dict(v=1.0, hot=0.0, cold=0.0, spot=1.0, dist=9.6).items():
            tk[k].set_value(val)
        self.beat("spreads through a solid", tk["op"].animate.set_value(1.0), rt=0.6)

        # "metal ring": the bar bends round into a ring; its heat has spread out to nothing
        self.beat("metal ring", tk["v"].animate.set_value(0.0), tk["spot"].animate.set_value(0.0),
                  tk["dist"].animate.set_value(7.6), year.animate.set_opacity(0.0), rt=1.2)

        # "flame" / "ice": each half takes its temperature (particles are scheduled by time)
        self.beat("flame", tk["hot"].animate.set_value(1.0), rt=1.0)
        self.beat("ice", tk["cold"].animate.set_value(1.0), rt=1.0)

        # "hot on one side": the temperature crown rises
        self.beat("hot on one side", tk["crown"].animate.set_value(1.0), rt=0.8)

        # "unroll the ring": it unrolls into a bar: the crown is the square wave; then rolls back up
        self.beat("unroll the ring", tk["v"].animate.set_value(1.0), tk["dist"].animate.set_value(9.6), rt=1.2)
        self.wait_until(END - 1.05)
        self.play(tk["v"].animate.set_value(0.0), tk["dist"].animate.set_value(7.6), run_time=self.snap(1.0))
        self.remove(year)
        self.finish()
