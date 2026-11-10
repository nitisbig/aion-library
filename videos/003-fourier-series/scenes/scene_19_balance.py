"""Scene 19 · Ch5: speed zero is the balance point (351.300–382.017 s).

"Let's warm up with the easiest circle, speed zero. It never moves, so it should sit at the
center of the drawing. But what does center even mean, for a squiggly shape like this?
Here's a natural answer. Spread dots along the path, evenly in time, and average all their
positions. That average is the balance point of the drawing, and it's exactly where the
speed zero circle sits. That's because every other circle spins all the way around, and a
full turn averages out to nothing."

The bean (beats.BEAN, five known circles). 60 dots evenly in loop time; their mean is
computed, and equals c₀ exactly (the green arm's tip).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (ORIGIN, UP, Create, FadeIn, FadeOut, GrowArrow, MathTex, ValueTracker, VGroup, VMobject,
                   linear, there_and_back)

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch5 as C
import scene_18_rack as R18

START, END = V.scene_range(19)
C0 = V.BEAN[0]
INSET_AT, INSET_R = complex(5.05, 1.0), 0.85


def bean_path(op: float = 1.0):
    t = np.linspace(0, 1, 1500)
    return C4.path(C.O + C.K * C.z_of(C.bean_terms_zero(), t), op=op)


def still_arm(op: float = 1.0, width: float = 3.5):
    return C4.arm(C.O, C.O + C.K * C0, op, color=S.STILL, width=width)


def chain_clock() -> C4.Clock:
    return C4.Clock([(C4.cue("every other circle", C.S19), 1.0, 0.25)], START - 1, C.S20[1] + 5)


CLOCK = chain_clock()


def others(now: float, op: float = 1.0) -> VGroup:
    """The bean's four spinning circles, riding on the still arm's tip (rims faint), with the pen."""
    if op <= 0:
        return VGroup()
    terms = [(n, c) for n, c in C.bean_terms_zero() if n != 0]
    vs = C.vecs(terms, float(CLOCK(now)))
    g, _ = C4.chain(vs, C.O + C.K * C0, rim_op=0.35 * op, arm_op=0.7 * op, pen_op=op, ns=[n for n, _ in terms],
                    label_op=op,
                    colors=[C4.color_of(n) for n, _ in terms])
    return g


def inset(q: float, op: float = 1.0, mean: float = 0.0) -> VGroup:
    """One spinning arm drops 12 dots around its circle (q: 0 → 1 = one turn); their mean is the center."""
    if op <= 0:
        return VGroup()
    c = INSET_AT
    g = VGroup(C4.slot(c, INSET_R, S.FWD, 0.5 * op, 30))
    for j in range(12):
        if j / 12 <= q + 1e-9:
            g.add(C4.Dot(C4.to3(c + INSET_R * np.exp(1j * C4.TAU * j / 12)), radius=0.05, color=S.INK).set_opacity(op))
    g.add(C4.arm(c, c + INSET_R * np.exp(1j * C4.TAU * q), op))
    if mean > 0:
        g.add(C4.Dot(C4.to3(c), radius=0.09, color=S.LABEL_MUTED).set_opacity(mean * op))
    return g


def end_layer(scene, op: ValueTracker) -> VGroup:
    """S19's last picture (S20 starts from it), faded by `op`."""
    m = C.O + C.K * C0

    def draw():
        o = op.get_value()
        if o <= 0:
            return VMobject()
        return VGroup(bean_path(o), still_arm(o), others(scene.now, o),
                      C4.Dot(C4.to3(m), radius=0.2, color=S.STILL).set_opacity(0.25 * o),
                      C4.Dot(C4.to3(m), radius=0.09, color=S.STILL).set_opacity(o),
                      inset(1.0, o, 1.0))
    return V.redraw(draw)


def lit_rack() -> dict:
    items = C.rack_items(small=True)
    items[0][0].set_stroke(opacity=1.0, width=3.5)
    return items


class Scene19Balance(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        self.add(C2.corner_marker())
        items = C.rack_items(small=False)
        rack = VGroup(*items.values())
        clef = R18.clef_ghost()
        self.add(rack, clef)

        # "warm up": chapter eyebrow; the clef goes; the rack docks small along the bottom
        eb = V.eyebrow("05 · SPIN AND AVERAGE")
        self.beat("warm up", FadeIn(eb, shift=UP * 0.08), FadeOut(clef),
                  rack.animate.scale(C.RACK_SCALE, about_point=ORIGIN).shift(C.RACK_SHIFT), rt=0.8)
        # "speed zero": its slot lights green
        self.beat("speed zero", items[0][0].animate.set_stroke(opacity=1.0, width=3.5), rt=0.5)

        # "never moves": a still green arm from the origin
        arm = still_arm()
        self.beat("never moves", GrowArrow(arm), rt=0.6)

        # "center of the drawing": the bean
        bean = bean_path()
        self.beat("center of the drawing", Create(bean), rt=1.0)

        # "squiggly shape": it wobbles once; a dim ? at its middle
        mid = bean.get_center()
        q = MathTex("?", font_size=80, color=S.LABEL_MUTED).move_to(mid + 0.35 * UP)
        self.beat("squiggly shape", bean.animate(rate_func=there_and_back).scale(1.04), FadeIn(q, scale=0.8), rt=0.6,
                  rate=None)
        self.beat("natural answer", FadeOut(q), rt=0.4)

        # "spread dots": the pen goes round once, dropping 60 dots evenly in time
        u, m = ValueTracker(0.0), ValueTracker(0.0)
        self.add(u, m)
        pts = C.dots_at(C.bean_terms_zero(), 0.0)

        def cloud():
            if u.get_value() <= 0:
                return VMobject()
            if m.get_value() <= 0:
                shown = pts[: int(np.floor(u.get_value() * C.N_DOTS + 1e-9)) + 1]
                pen = C4.pen(C.O + C.K * C.z_of(C.bean_terms_zero(), u.get_value())) if u.get_value() < 1 else VMobject()
                return VGroup(C.dot_cloud(shown), pen)
            mv = m.get_value()
            return C.dot_cloud(pts, collapse=mv, lines=min(1.0, mv / 0.2), mean_op=np.clip((mv - 0.6) / 0.4, 0, 1))
        self.add(V.redraw(cloud))
        self.beat("spread dots", u.animate.set_value(1.0), rt=2.0, rate=linear)

        # "average all their positions": lines to the mean; the dots slide in and merge: the balance point
        self.beat("average all their positions", m.animate.set_value(1.0), rt=1.6)

        # "balance point": it pulses; the still arm's tip is exactly there
        pu = ValueTracker(0.0)
        self.add(pu)
        mean_pt = C.O + C.K * C0
        self.add(V.redraw(lambda: C.ping(mean_pt, pu.get_value(), S.STILL)))
        self.beat("balance point", pu.animate.set_value(1.0), arm.animate(rate_func=there_and_back).set_stroke(width=7),
                  rt=0.9, rate=None)

        # "every other circle": the bean's other four circles appear, spinning on the still arm's tip
        oo = ValueTracker(0.0)
        self.add(oo)
        self.add(V.redraw(lambda: others(self.now, oo.get_value())))
        self.beat("every other circle", oo.animate.set_value(1.0), rt=0.6)

        # "averages out to nothing": one spinning arm drops 12 dots round a circle; their mean is the center
        iq, io, im = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        self.add(iq, io, im)
        self.add(V.redraw(lambda: inset(iq.get_value(), io.get_value(), im.get_value())))
        self.play_at(self.t("averages out to nothing") - 0.5, io.animate.set_value(1.0), run_time=0.3)
        self.play(iq.animate.set_value(1.0), run_time=self.snap(1.2), rate_func=linear)
        self.play(im.animate.set_value(1.0), run_time=self.snap(0.4))
        self.finish()
