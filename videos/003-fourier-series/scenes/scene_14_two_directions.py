"""Scene 14 · Ch4: use both directions (272.283–280.783 s).

"So far, we've only watched the height of the tip. But it also moves left and right. So
let's use both, and let the tip draw right on the page."

Starts on S13's last picture (ch3.drawing_seed). A second circle (speed 3, a quarter the
size) grows on the tip, the chain turns (ch4.clock14), and its height writes a wave to
the right as in Ch1. Then its left-right motion writes a second wave running down the
screen. Both projections pull back into the pen, and the pen draws on the page.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import UP, FadeIn, ValueTracker, VGroup, VMobject, there_and_back

from aion import style as S
from aion.drawings import treble_clef
import shared as V
import ch2 as C2
import ch3 as H
import ch4 as C

START, END = V.scene_range(14)


class Scene14TwoDirections(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.add(C2.corner_marker())
        clk = C.clock14()
        T_ink = C.cue("right on the page", C.S14)
        tk = {k: ValueTracker(v) for k, v in dict(r2=0.0, hw=0.0, lw=0.0, pull=0.0, ink=0.0).items()}
        self.add(*tk.values())

        def now_c():
            return float(clk(self.now))

        def machine():
            c, r2 = now_c(), tk["r2"].get_value()
            g, p = C.chain(C.vecs14(c, r2), C.CC, colors=[S.FWD, S.FWD], ns=[1, 3])
            out = VGroup()
            pull = tk["pull"].get_value()
            for key, horiz in (("hw", True), ("lw", False)):
                o = tk[key].get_value() * (1 - pull)
                if o <= 0:
                    continue
                if horiz:                                   # height → wave to the right
                    tgt = complex(C.X0, p.imag)
                    end = p + (1 - pull) * (tgt - p)
                    ax = C.dashed_h(C.CC.imag, C.X0, C.X_END, 0.35 * o)
                    tau = self._hist(C.X_END - C.X0, self._t_wave[key])
                    z = complex(C.X0, 0) + (self.now - tau) * C.V_SCROLL + 1j * (C.CC.imag + C.z14(clk(tau), r2).imag)
                else:                                       # left-right → wave running down
                    tgt = complex(p.real, C.Y0)
                    end = p + (1 - pull) * (tgt - p)
                    ax = C.DashedLine([C.CC.real, C.Y0, 0], [C.CC.real, C.Y_END, 0], dash_length=0.08,
                                      color=S.ARM, stroke_width=1.5).set_stroke(opacity=0.35 * o)
                    tau = self._hist(C.Y0 - C.Y_END, self._t_wave[key])
                    z = (C.CC.real + C.z14(clk(tau), r2).real) + 1j * (C.Y0 - (self.now - tau) * C.V_SCROLL)
                conn = C.DashedLine(C.to3(p), C.to3(end), dash_length=0.08, color=S.ARM,
                                    stroke_width=1.5).set_stroke(opacity=0.7 * o) if abs(end - p) > 0.02 else VMobject()
                out.add(ax, C.path(z, op=o), conn, C.pen(end, o) if abs(end - p) > 0.02 else VMobject())
            ink = C.ink14(self.now, T_ink, op=tk["ink"].get_value()) if self.now >= T_ink else VMobject()
            return VGroup(out, ink, g)

        self._t_wave = {"hw": C.cue("height of the tip", C.S14), "lw": C.cue("left and right", C.S14)}
        self.add(V.redraw(machine))

        # "height of the tip": eyebrow; a second circle grows on the tip; the height wave runs right
        eb = V.eyebrow("04 · WAVES BECOME DRAWINGS")
        self.beat("height of the tip", FadeIn(eb, shift=UP * 0.08), tk["r2"].animate.set_value(1.0),
                  tk["hw"].animate.set_value(1.0), rt=0.8)

        # "left and right": a second projection runs down; the left-right motion writes its own wave
        self.beat("left and right", tk["lw"].animate.set_value(1.0), rt=1.0)

        # "use both": both projections pull back into the pen; the waves go
        self.beat("use both", tk["pull"].animate.set_value(1.0), rt=0.6)

        # "right on the page": the pen draws in gold; a faint clef flashes behind it
        clef = treble_clef(1000)
        clef = clef - clef.mean()
        clef = C.CC + clef * (2.8 / (clef.imag.max() - clef.imag.min()))
        ghost = C.path(np.append(clef, clef[0]), S.INK, 2.5, 1.0).set_stroke(opacity=0.0)
        self.add(ghost)
        self.bring_to_back(ghost)
        tk["ink"].set_value(1.0)
        self.beat("right on the page", ghost.animate(rate_func=there_and_back).set_stroke(opacity=0.18), rt=0.6, rate=None)
        self.remove(ghost)
        self.finish()

    def _hist(self, span: float, t0: float) -> np.ndarray:
        """Past times whose wave samples are on screen: from the wave's start (or span ago) to now."""
        return np.linspace(min(self.now, max(self.now - span / C.V_SCROLL, t0)), self.now, 500)
