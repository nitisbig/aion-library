"""Scene 22 · Ch5: sanity check (417.983–438.717 s).

"As a sanity check, let's try our rounded square, where we know the answer. Turn it backward
once and average, and the balance point lands right on the tip of the big circle. Turn it
forward three times, and it finds the small circle, one ninth the size, just as it should.
Try speed two, and the average falls to zero. There's no circle there."

The rounded square (beats.ROUNDED_SQUARE: 1 and −1/9 at speed −3), spun against n = 1, −3, 2
(ch5.Frame, k eased between them). The 60 dots are the drawing wound n times; their mean
is computed every frame: exactly 1, −1/9 and 0 (checked in beats.verify_math).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import Arc, FadeIn, FadeOut, LaggedStart, ValueTracker, VGroup, VMobject

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch5 as C
import scene_21_freeze as S21

START, END = V.scene_range(22)
TERMS = C.rs_terms()
KS = C.K_RS
FRAME = C.Frame([(START - 4.5, 0.01, 0.25)],
                [(C4.cue("backward once", C.S22), 1.4, 1.0), (C4.cue("forward three times", C.S22), 1.4, -3.0),
                 (C4.cue("speed two", C.S22), 1.2, 2.0)], START - 6, C.S23[1] + 5)


def picture(now: float, v: dict) -> VGroup:
    """v: op, dots, col (collapse), mean, mean_grey, arm (green result arm + violet half-turn arc)."""
    op = v.get("op", 1.0)
    if op <= 0:
        return VGroup()
    L, phi = float(FRAME.loops(now)), float(FRAME.angle(now))
    k = FRAME.k_at(now)
    vs = C.vecs(TERMS, L, phi, KS)
    g = VGroup(C.ink(TERMS, FRAME, now, KS, op=0.35 * op, width=3.0))
    ch, _ = C4.chain(vs, C.O, rim_op=0.7 * op, arm_op=op, pen_op=op, colors=[S.FWD, S.BWD])
    g.add(ch)
    d = v.get("dots", 0.0)
    pts = C.dots_at(TERMS, k, KS)
    if d > 0:
        mean = v.get("mean", 0.0)
        col = S.LABEL_MUTED if v.get("mean_grey", 0.0) > 0.5 else S.STILL
        g.add(C.dot_cloud(pts, collapse=v.get("col", 0.0), op=d * op, lines=0.0, mean_col=col, mean_op=mean * op))
    a = v.get("arm", 0.0)
    if a > 0:
        m = pts.mean()
        g.add(C4.arm(C.O, m, a * op, color=S.STILL, width=3.5),
              Arc(radius=0.42, start_angle=0, angle=np.pi, arc_center=C4.to3(C.O), color=S.PHASE,
                  stroke_width=3).set_stroke(opacity=a * op))
    return g


END_VALS = dict(op=1.0, dots=1.0, col=1.0, mean=1.0, mean_grey=1.0, arm=0.0)


def end_rack() -> dict:
    """The rack after S22: slot 0 lit, slots 1 and −3 filled with the rounded square's circles, slot 2 dim."""
    import scene_19_balance as S19
    items = S19.lit_rack()
    items[2][0].set_stroke(opacity=0.2)
    items["fill1"] = C.rack_fill(1, 1.0, 1.0)
    items["fill-3"] = C.rack_fill(-3, -1 / 9, 1.0)
    return items


class Scene22Check(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        items = S21.end_rack()
        fill_bean = items.pop("fill1")
        self.add(VGroup(*items.values()), fill_bean, V.eyebrow("05 · SPIN AND AVERAGE"), C2.corner_marker())
        self.add(V.redraw(lambda: C.card_docked(self.now)))
        o21 = ValueTracker(1.0)
        self.add(o21)
        self.add(V.redraw(lambda: S21.picture(self.now, {**S21.END_VALS, "op": o21.get_value()})))

        v = {k: ValueTracker(0.0) for k in END_VALS}
        self.add(*v.values())
        self.add(V.redraw(lambda: picture(self.now, {k: t.get_value() for k, t in v.items()})))

        # "sanity check": the bean goes (and its rack entry); the rounded square returns; the speed dial
        dial = C.dial(0)
        self.beat("sanity check", o21.animate.set_value(0.0), FadeOut(fill_bean), v["op"].animate.set_value(1.0),
                  FadeIn(dial), rt=0.8)

        def set_dial(n):
            new = C.dial(n)
            return FadeOut(dial), FadeIn(new), new

        # "backward once": n = 1; the stage turns backward and the dots wind
        a1, a2, dial = set_dial(1)
        self.beat("backward once", a1, a2, v["dots"].animate.set_value(1.0), rt=0.6)

        # "tip of the big circle": they collapse onto the big circle's tip (green); slot 1 fills
        f1 = C.rack_fill(1, 1.0, 1.0)
        self.beat("tip of the big circle", v["col"].animate.set_value(1.0),
                  v["mean"].animate(rate_func=V.window(0.6, 1.0)).set_value(1.0), FadeIn(f1, scale=0.8), rt=1.0,
                  rate=None)

        # "forward three times": n = −3; the dots spread and wind again
        a1, a2, dial = set_dial(-3)
        self.beat("forward three times", a1, a2, v["col"].animate.set_value(0.0), v["mean"].animate.set_value(0.0),
                  rt=0.8)

        # "one ninth": a ninth of the size, pointing the opposite way (violet half turn); slot −3 fills
        f3 = C.rack_fill(-3, -1 / 9, 1.0)
        self.beat("one ninth", v["col"].animate.set_value(1.0),
                  v["mean"].animate(rate_func=V.window(0.6, 1.0)).set_value(1.0),
                  v["arm"].animate(rate_func=V.window(0.5, 1.0)).set_value(1.0), FadeIn(f3, scale=0.8), rt=1.0,
                  rate=None)

        # "just as it should": both filled slots pulse green
        pu = ValueTracker(0.0)
        self.add(pu)
        self.add(V.redraw(lambda: VGroup(*[C.ping(complex(*C.rack_center(n)[:2]), pu.get_value(), S.STILL)
                                           for n in (1, -3)])))
        self.beat("just as it should", pu.animate.set_value(1.0), rt=0.6)

        # "speed two": n = 2; spread and wind again
        a1, a2, dial = set_dial(2)
        self.beat("speed two", a1, a2, v["col"].animate.set_value(0.0), v["mean"].animate.set_value(0.0),
                  v["arm"].animate.set_value(0.0), rt=0.8)

        # "falls to zero": the mean lands at the center: grey
        v["mean_grey"].set_value(1.0)
        pg = ValueTracker(0.0)
        self.add(pg)
        self.add(V.redraw(lambda: C.ping(C.O, pg.get_value(), S.LABEL_MUTED)))
        self.beat("falls to zero", v["col"].animate.set_value(1.0),
                  v["mean"].animate(rate_func=V.window(0.6, 1.0)).set_value(1.0),
                  pg.animate(rate_func=V.window(0.5, 1.0)).set_value(1.0), rt=1.0, rate=None)

        # "no circle there": slot 2 stays empty and dims
        self.beat("no circle there", items[2][0].animate.set_stroke(opacity=0.2), rt=0.4)
        self.finish()
