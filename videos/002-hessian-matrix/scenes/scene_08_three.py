"""Scene 08 · Ch2: bowl, dome, saddle (178.783–200.017 s).

"Look at these three surfaces. A bowl, a dome, and a saddle, shaped like a mountain
pass. At the center of each one, the gradient is zero. But the bowl is a valley. The
dome is a peak and the saddle is neither. It's low one way and high the other way. To
tell them apart, we need second derivatives again. But on a surface, there's more than one."

Bowl H = diag(2, 2), dome diag(−2, −2), saddle diag(2, −2): ∇f(0, 0) = 0 for all three,
and identical flat tangent discs sit on them. The saddle's x-slice smiles (f_xx = 2) and
its y-slice frowns (f_yy = −2).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.surface_gl import tangent_disc
import shared as V
import ch2 as L

START, END = V.scene_range(8)
PEAK = next((x, y) for x, y, k in L.CRIT if k == "peak" and x > 0)
PANEL_W, PANEL_H, PANEL_Y = 4.6, 4.3, 0.35
XS = (-4.6, 0.0, 4.6)
KINDS = ((V.H_BOWL, "valley", S.SMILE), (V.H_DOME, "peak", S.FROWN), (V.H_SADDLE, "neither", None))


def mini_rig(clk, **kw):
    st = dict(H=(0.0, 0.0, 0.0), zs=0.32, zclip=0.0, R=1.55, edge=0.74, yaw=-60.0, pitch=27.0, dist=6.5,
              fov=34.0, target=(0.0, 0.0, 0.0), fog=0.02, grid=(0.25, 0.25), grid_step=0.35,
              zlo=-0.8, zhi=0.8, opacity=0.0, disc_a=0.0, gold=0.0, slices=[], disc=None, **L.LUMINOUS_PANEL)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + 6.0 * clk.get_value()          # co-rotation
    # keep each shape vertically centred in its viewport: aim at its mean height
    r.dyn["target"] = lambda: (0.0, 0.0, 0.1 * (r.val("H")[0] + r.val("H")[2]))
    # the disc turns gold on "gradient is zero" (gold = slope, as in the intro)
    r.dyn["disc"] = lambda: tangent_disc(0, 0, 0.32, r.val("disc_a"),
                                         color=interpolate_color(ManimColor(S.TEXT), ManimColor(S.GRAD), r.val("gold"))
                                         ) if r.val("disc_a") > 0.003 else None
    return r


class Scene08Three(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 07's last frame: the top-down map, field, rings, walker on the peak ──
        land = L.land_rig(**L.TOPDOWN)
        lplate = land.plate()
        field, rings = L.field_arrows(lplate), L.crit_rings(lplate)
        me = V.walker().move_to(lplate.project(*PEAK, float(L.f(*PEAK))))
        self.add(lplate, *land.trackers(), field, rings, me)

        # 2-7 · the triptych: three viewports, slowly co-rotating
        clk = ValueTracker(0.0)
        self.run_clock(clk)
        rigs = [mini_rig(clk) for _ in range(3)]
        plates = [r.plate(width=PANEL_W, height=PANEL_H, center=np.array([x, PANEL_Y, 0])) for r, x in zip(rigs, XS)]
        for r, p in zip(rigs, plates):
            self.add(p, *r.trackers())
        self.beat("three surfaces", *land.to(opacity=0.0), FadeOut(field), FadeOut(rings), FadeOut(me),
                  *[a for r in rigs for a in r.to(opacity=1.0)], rt=1.0)
        self.remove(lplate)
        for word, after, r, (H, _, _) in zip(("bowl", "dome", "saddle"), (180.0, 181.0, 182.0), rigs, KINDS):
            self.beat(word, *r.to(H=H), rt=0.6, after=after)

        # 2-8 · a flat disc and a walker at every centre: the gradient is zero everywhere
        walkers = VGroup()
        for p in plates:
            w = V.walker(radius=0.06)
            V.pin(w, p, V.on_surface(p, 0, 0, 0.02))
            walkers.add(w)
        self.beat("center of each one", *[a for r in rigs for a in r.to(disc_a=0.42)],
                  LaggedStart(*[FadeIn(w) for w in walkers], lag_ratio=0.2), rt=0.8)
        # one ∇f = 0 for all three, while every disc turns gold
        zeros = MathTex(r"\nabla f = 0", font_size=44, color=S.GRAD).move_to([0, 3.05, 0])
        self.beat("gradient is zero", FadeIn(zeros, shift=DOWN * 0.1),
                  LaggedStart(*[a for r in rigs for a in r.to(gold=1.0)], lag_ratio=0.15), rt=0.6)
        words = []
        for (H, word, col), x in zip(KINDS, XS):
            t = V.label(word, 32, col or S.TEXT, weight=MEDIUM).move_to([x, -2.45, 0])
            if col is None:                                   # "neither": half blue, half orange
                t[:4].set_color(S.SMILE)
                t[4:].set_color(S.FROWN)
            words.append(t)
        self.beat("valley", FadeIn(words[0], shift=UP * 0.1), rt=0.4, after=188.0)
        self.beat("peak", FadeIn(words[1], shift=UP * 0.1), rt=0.4, after=189.5)
        self.beat("neither", FadeIn(words[2], shift=UP * 0.1), rt=0.4)

        # 2-9 · the saddle fills the frame: it smiles one way and frowns the other
        sx, sy = ValueTracker(0.0), ValueTracker(0.0)
        big = L.big_saddle(clk, sx, sy)
        bplate = big.plate()
        self.add(bplate, *big.trackers(), sx, sy)
        self.bring_to_front(walkers)
        bw = V.walker()
        V.pin(bw, bplate, V.on_surface(bplate, 0, 0, 0.02))
        lift = ValueTracker(0.0)
        gx, gy = L.saddle_gauges(bplate, lift)
        self.beat("low one way", *[a for r in rigs for a in r.to(opacity=0.0)], FadeOut(walkers),
                  FadeOut(zeros), *[FadeOut(w) for w in words], *big.to(opacity=1.0), FadeIn(bw),
                  sx.animate.set_value(1.0), rt=0.75)
        for p in plates:
            self.remove(p)
        self.play(FadeIn(gx, scale=0.6), run_time=self.snap(0.3))
        self.beat("high the other", sy.animate.set_value(1.0), FadeIn(gy, scale=0.6), rt=0.5)

        # 2-10 · second derivatives again, but how many?
        self.beat("second derivatives again", lift.animate.set_value(0.5), rt=0.8)
        how = L.how_many()
        self.beat("more than one", FadeIn(how, shift=UP * 0.1), rt=0.5)
        self.finish()
