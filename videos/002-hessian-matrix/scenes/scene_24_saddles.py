"""Scene 24 · Ch6: most flat points are saddles (542.250–559.567 s).

"And the Hessian explains something surprising. In these huge landscapes, most flat points
aren't valleys at all. They're saddles. To be a valley, every single eigenvalue has to be
positive. With millions of them, a few are almost always negative. There's almost always
a way down."

Twelve flat points, each a row of eigenvalue signs (blue +, orange −; seeded coin flips,
captioned as intuition). With 2 eigenvalues three rows are valleys; with 10 none are; with
100 the orange dots are everywhere. One saddle becomes a 3D saddle and the ball rolls off
along its downhill direction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch6 as C

START, END = V.scene_range(24)


class Scene24Saddles(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 23's last frame ──
        e = C.s23_end()
        self.add(e["pitch"], e["alpha"], e["band"], e["e"])
        self.add(e["mos"], e["mil"], e["tri"])

        # 6-9 · twelve flat points, two eigenvalues each: three are valleys
        rows = [C.row_dots(r, 2) for r in range(C.N_ROWS)]
        rings = {r: C.valley_ring(r, 2) for r, v in enumerate(C.VALLEY(2)) if v}
        e["tri"][0].clear_updaters()
        self.beat("something surprising", e["alpha"].animate.set_value(0.0), FadeOut(e["mil"]), FadeOut(e["tri"]),
                  LaggedStart(*[FadeIn(r, scale=0.6) for r in rows], lag_ratio=0.06),
                  LaggedStart(*[Create(b) for b in rings.values()], lag_ratio=0.2), rt=1.0)
        self.remove(e["mos"])

        # huge landscapes: ten eigenvalues each, and the valleys are gone
        more = [C.row_dots(r, 10, j0=2) for r in range(C.N_ROWS)]
        self.beat("huge landscapes", LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in more], lag_ratio=0.04),
                  *[FadeOut(b) for b in rings.values()], rt=0.9)
        for r, m in zip(rows, more):
            r.add(*m)
        first_neg = VGroup(*[next(d for j, d in enumerate(r) if C.SIGNS[i, j] < 0) for i, r in enumerate(rows)])
        self.beat("arent valleys", V.pulse(first_neg, lambda m: [d.scale(1.8) for d in m] and m), rt=0.6)
        tags = C.saddle_tags()
        self.beat("saddles", LaggedStart(*[FadeIn(t, shift=LEFT * 0.08) for t in tags], lag_ratio=0.05), rt=0.6,
                  after=549.0)

        # every single eigenvalue has to be positive
        others = [m for i, r in enumerate(rows) if i != C.HI_ROW for m in (r, tags[i])]
        req = C.requirement()
        hi_neg = VGroup(*[d for j, d in enumerate(rows[C.HI_ROW]) if C.SIGNS[C.HI_ROW, j] < 0])
        self.beat("every single eigenvalue", *[m.animate.set_opacity(0.22) for m in others],
                  FadeIn(req, shift=UP * 0.1), rt=0.6)
        self.play(V.pulse(hi_neg, lambda m: [d.scale(1.8) for d in m] and m), run_time=self.snap(0.7))

        # millions of them: a hundred per row, and the orange is everywhere
        grown = [C.row_dots(r, C.K_MAX) for r in range(C.N_ROWS)]
        cav = C.caveat()
        self.beat("millions of them", *[m.animate.set_opacity(1.0) for m in others], FadeOut(req),
                  *[Transform(rows[r], grown[r][:10]) for r in range(C.N_ROWS)],
                  *[FadeIn(grown[r][10:]) for r in range(C.N_ROWS)], FadeIn(cav), rt=1.0)
        neg = VGroup(*[d for r in range(C.N_ROWS) for j, d in enumerate(grown[r]) if j >= 10 and C.SIGNS[r, j] < 0],
                     *[d for r in range(C.N_ROWS) for j, d in enumerate(rows[r]) if C.SIGNS[r, j] < 0])
        self.beat("almost always negative", V.pulse(neg, lambda m: [d.scale(1.7).set_color(S.LIGHT) for d in m] and m),
                  rt=0.8)

        # 6-10 · there's almost always a way down
        rig = C.saddle_rig()
        plate = rig.plate()
        self.add(plate, *rig.trackers())
        s = ValueTracker(0.0)
        ball = V.walker()
        V.pin(ball, plate, lambda: C.roll_xyz(plate, s.get_value()))
        ba = ValueTracker(0.0)
        ball.add_updater(lambda m: V.set_walker_alpha(m, ba.get_value()))
        self.add(s, ba, ball)
        hi = VGroup(rows[C.HI_ROW], grown[C.HI_ROW][10:])
        everything = [m for i in range(C.N_ROWS) if i != C.HI_ROW for m in (rows[i], grown[i][10:])] + [tags, cav]
        self.beat("theres almost always", *rig.to(opacity=1.0), ba.animate.set_value(1.0),
                  *[FadeOut(m) for m in everything], hi.animate.scale(2.2).set_opacity(0.0), rt=1.0)
        self.remove(hi)
        self.beat("way down", s.animate.set_value(1.0), rt=0.55, rate=rush_into)
        self.finish()
