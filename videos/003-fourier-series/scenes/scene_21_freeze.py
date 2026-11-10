"""Scene 21 · Ch5: turn the drawing backward (389.317–417.983 s).

"Now, the speed one circle spins, so the average can't see it. Unless we can make it stand
still. Here's the trick. As the pen goes around, turn the whole drawing backward, one full
turn per loop. The speed one circle was turning forward once, and now it's also turned
backward once, so it stops. Every other circle is still spinning, so when we average, they
all wash out. What's left is the speed one circle, frozen in place."

Rotating frame (ch5.Frame): k eases 0 → 1 on "turn the whole drawing backward". Every arm
turns at n − k; the pen's ink is w(τ) = z(L(τ))·e^{−iΦ(τ)}, so after one loop it is the
wound shape. Its 60 dots average to exactly c₁: the frozen arm's tip (the bean's speed-1
circle is drawn first, from O).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import (Arc, DashedLine, Dot, FadeIn, Line, ManimColor, MathTex, ValueTracker, VGroup, VMobject)

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C4
import ch5 as C

START, END = V.scene_range(21)
TERMS = C.bean_terms_size()                     # [(1, …), (0, …), (−1, …), (2, …), (−2, …)]
C1 = dict(TERMS)[1]
FRAME = C.Frame([(C4.cue("speed one circle", C.S21), 1.0, 0.25)],
                [(C4.cue("turn the whole drawing backward", C.S21), 2.0, 1.0)], START - 1, C.S23[1] + 5)
_LABELS: dict = {}


def _lab(n: int) -> MathTex:
    key = n
    if key not in _LABELS:
        txt = "0" if n == 0 else (f"+{n}" if n > 0 else f"-{-n}")
        _LABELS[key] = MathTex(txt, font_size=36, color=C4.color_of(n))
    return _LABELS[key].copy()


def picture(now: float, v: dict) -> VGroup:
    """S21's whole stage at `now`. v: op, hl (speed-1 glow), green, ring, lab, new, mean, mark."""
    op = v.get("op", 1.0)
    if op <= 0:
        return VGroup()
    L, phi = float(FRAME.loops(now)), float(FRAME.angle(now))
    vs = C.vecs(TERMS, L, phi)
    cols = []
    for n, _ in TERMS:
        if n == 1:
            cols.append(ManimColor(S.FWD).interpolate(ManimColor(S.STILL), v.get("green", 0.0)))
        else:
            cols.append(ManimColor(C4.color_of(n)).interpolate(ManimColor(C4.color_of(n - 1)), v.get("new", 0.0)))
    g = VGroup(C.frame_ring(phi, v.get("ring", 0.0) * op), C.ink(TERMS, FRAME, now, op=op))
    hl = v.get("hl", 0.0)
    if hl > 0:
        a, b = C.O, C.O + vs[0]
        col = cols[0]
        g.add(Line(C4.to3(a), C4.to3(b), color=col, stroke_width=14).set_stroke(opacity=0.25 * hl * op))
    ch, _ = C4.chain(vs, C.O, rim_op=0.7 * op, arm_op=op, pen_op=op, colors=cols)
    g.add(ch)
    lab = v.get("lab", 0.0)
    if lab > 0:
        p = C.O
        for (n, _), w in zip(TERMS, vs):
            mid = p + w / 2
            off = 0.3 * 1j * w / (abs(w) + 1e-9)
            at = C4.to3(mid + off)
            new = v.get("new", 0.0)
            if new < 1:
                g.add(_lab(n).move_to(at).set_opacity(lab * (1 - new) * op))
            if new > 0:
                g.add(_lab(n - 1).move_to(at).set_opacity(lab * new * op))
            p = p + w
    mean = v.get("mean", 0.0)
    tip = C.O + C.K * C1
    if mean > 0:
        g.add(Dot(C4.to3(tip), radius=0.2, color=S.STILL).set_opacity(0.25 * mean * op),
              Dot(C4.to3(tip), radius=0.09, color=S.STILL).set_opacity(mean * op))
    mark = v.get("mark", 0.0)
    if mark > 0:
        g.add(marks(mark * op))
    return g


def marks(op: float) -> VGroup:
    """The frozen arm's two settings: a silver size bracket and a violet starting-angle arc."""
    tip = C.O + C.K * C1
    u = (tip - C.O) / abs(tip - C.O)
    n = -1j * u * 0.32
    a, b = C.O + n, tip + n
    br = VGroup(Line(C4.to3(a), C4.to3(b)), Line(C4.to3(a - 0.4 * n), C4.to3(a + 0.4 * n)),
                Line(C4.to3(b - 0.4 * n), C4.to3(b + 0.4 * n))).set_stroke(S.ARM, 2.5, op)
    ref = DashedLine(C4.to3(C.O), C4.to3(C.O + 1.1), dash_length=0.07, color=S.PHASE, stroke_width=2).set_stroke(opacity=0.8 * op)
    arc = Arc(radius=0.75, start_angle=0, angle=float(np.angle(C1)), arc_center=C4.to3(C.O), color=S.PHASE,
              stroke_width=3.5).set_stroke(opacity=op)
    return VGroup(br, ref, arc)


END_VALS = dict(op=1.0, hl=0.0, green=1.0, ring=1.0, lab=1.0, new=1.0, mean=1.0, mark=1.0)


def end_rack() -> dict:
    """The rack after S21: slot 0 lit (S19), slot 1 filled with the bean's c₁."""
    import scene_19_balance as S19
    items = S19.lit_rack()
    items["fill1"] = C.rack_fill(1, C1, 1.0)
    return items


class Scene21Freeze(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        import scene_19_balance as S19
        items = S19.lit_rack()
        self.add(VGroup(*items.values()), V.eyebrow("05 · SPIN AND AVERAGE"), C2.corner_marker())
        self.add(V.redraw(lambda: C.card_docked(self.now)))

        v = {k: ValueTracker(0.0) for k in END_VALS}
        self.add(*v.values())
        self.add(V.redraw(lambda: picture(self.now, {k: t.get_value() for k, t in v.items()})))

        # "speed one circle": the bean's chain; its speed-1 arm gets a soft highlight
        self.beat("speed one circle", v["op"].animate.set_value(1.0), v["hl"].animate.set_value(0.6), rt=0.6)

        # "can't see it": its dots would average to nothing: a grey ping at its center
        pg = ValueTracker(0.0)
        self.add(pg)
        self.add(V.redraw(lambda: C.ping(C.O, pg.get_value(), S.LABEL_MUTED)))
        self.beat("can't see it", pg.animate.set_value(1.0), rt=0.8)

        # "stand still": the speed-1 arm glows (the hope)
        self.beat("stand still", v["hl"].animate.set_value(1.0), rt=0.4)

        # "turn the whole drawing backward": the stage turns backward, one turn per loop (ch5.FRAME)
        self.beat("turn the whole drawing backward", v["ring"].animate.set_value(1.0), rt=0.6)

        # "so it stops": in the turning view the speed-1 arm is frozen: it turns green, its glow steadies
        self.beat("so it stops", v["green"].animate.set_value(1.0), v["hl"].animate.set_value(0.6), rt=0.6)

        # "still spinning": the other arms' speeds, then minus one each (0 → −1, +2 → +1, −1 → −2, −2 → −3)
        self.beat("still spinning", v["lab"].animate.set_value(1.0), rt=0.4)
        self.play(v["new"].animate.set_value(1.0), run_time=self.snap(0.6))

        # "wash out": the 60 dots of the wound shape collapse to their mean: the frozen arm's tip
        pts = C.dots_at(TERMS, 1.0)
        dop, col = ValueTracker(0.0), ValueTracker(0.0)
        self.add(dop, col)
        self.add(V.redraw(lambda: C.dot_cloud(pts, collapse=col.get_value(), op=dop.get_value(),
                                              lines=dop.get_value() * min(1.0, col.get_value() / 0.2))
                          if dop.get_value() > 0 and col.get_value() < 1 else VMobject()))
        self.play_at(self.t("wash out") - 0.3, dop.animate.set_value(1.0), run_time=0.3)
        self.play(col.animate.set_value(1.0), v["mean"].animate(rate_func=V.window(0.6, 1.0)).set_value(1.0),
                  run_time=self.snap(1.4))

        # "frozen in place": its size (silver bracket) and starting angle (violet arc); rack slot 1 fills
        fill = C.rack_fill(1, C1, 1.0)
        self.beat("frozen in place", v["mark"].animate.set_value(1.0), v["hl"].animate.set_value(0.0),
                  FadeIn(fill, scale=0.8), rt=0.6)
        self.finish()
