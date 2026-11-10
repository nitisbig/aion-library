"""Scene 02 · Intro: how can circles draw a corner? (13.283–45.900 s).

"Here's what I find strange about this. A circle is about the roundest thing there is.
No corners, no straight edges. And yet the right circles can draw sharp turns, even a
square with four perfect corners. So how does something that only goes round draw a
corner? The answer is something called a Fourier series, named after Joseph Fourier,
who found it about two hundred years ago while studying, of all things, heat. And it
makes a bold claim. Almost any loop you could draw can be built out of spinning circles."

No cut from S01: the same chain keeps turning. Its coefficients blend clef → square
(the chain never reorders, so only the drawing morphs). The pen's clock is scheduled
so it reaches the corner the camera dived into exactly as the picture freezes on
"draw a corner".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from functools import lru_cache

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Dot, Group, DashedVMobject, FadeIn, FadeOut, ImageMobject, Line,
                   VMobject, Square, SurroundingRectangle, Transform, ValueTracker, VGroup, always_redraw,
                   linear, smooth, there_and_back)

from aion import fourier as F
from aion import style as S
from aion.components.title import TitlePlate
import shared as V
from aion.components.term_label import exp_parts, labels
from manim import MathTex, RESAMPLING_ALGORITHMS

START, END = V.scene_range(2)
R = 1 / V.LOOP_S01                                     # loops per second (same pace as S01)

PC, PR = np.array([4.45, 0.0, 0.0]), 1.15
POLY_STAGES = (3, 4, 6, 12, None)                     # None = the circle
POLY_STEP = 0.42                                      # s per stage


def _poly_r(k, phi):
    """Radius of a regular k-gon (circumradius 1, a vertex up) at angle phi; k None = the circle."""
    if k is None:
        return np.ones_like(phi)
    a = (phi - np.pi / 2) % (2 * np.pi / k) - np.pi / k
    return np.cos(np.pi / k) / np.cos(a)


@lru_cache(maxsize=8)
def _ptag(k):
    return MathTex(r"n = %d" % k if k else r"n \to \infty", font_size=34, color=S.LABEL_MUTED)


def polygon_panel(u: float, op: float) -> VGroup:
    """u s after "roundest thing": the polygon morphs stage to stage (vertex radii blended)."""
    if op <= 0 or u < 0:
        return VGroup()
    i = min(int(u / POLY_STEP), len(POLY_STAGES) - 1)
    x = smooth(min(1.0, (u - i * POLY_STEP) / 0.25)) if i else 1.0
    phi = np.linspace(0, 2 * np.pi, 361)
    r = _poly_r(POLY_STAGES[i], phi) if i == 0 else \
        (1 - x) * _poly_r(POLY_STAGES[i - 1], phi) + x * _poly_r(POLY_STAGES[i], phi)
    pts = np.stack([PC[0] + PR * r * np.cos(phi), PC[1] + PR * r * np.sin(phi), 0 * phi], 1)
    shape = VMobject(stroke_color=S.ARM, stroke_width=3).set_points_as_corners(pts).set_stroke(opacity=op)
    k = POLY_STAGES[i]
    tag = _ptag(k).copy().move_to(PC + DOWN * (PR + 0.5)).set_opacity(op)
    return VGroup(shape, tag)


class Scene02Corner(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── the pen's clock: constant pace, then an ease-out that stops ON a corner at the freeze
        T_freeze = self.t("draw a corner") - S.LEAD
        T_resume = self.t("fourier series") - S.LEAD
        tc_all, corners = V.corner_times(V.square_terms())
        cand = [(k + tc, c) for k in range(1, 4) for tc, c in zip(tc_all, corners)]
        # ease-out t = t_c − D(1 − u)², D = R·Δ/2 matches the pace at its start (T1)
        best = None
        for t_c, c in cand:
            T1 = 2 * (t_c - 1) / R + 2 * START - T_freeze
            if START + 8 <= T1 <= T_freeze - 1.5 and (best is None or T1 > best[1]):
                best = (t_c, T1, c)
        t_c, T1, C = best

        def clock(now):
            if now <= T1:
                return 1 + R * (now - START)
            if now <= T_freeze:
                u = (now - T1) / (T_freeze - T1)
                return t_c - R * (T_freeze - T1) / 2 * (1 - u) ** 2
            if now <= T_resume:
                return t_c
            x = now - T_resume                         # slow resume, starting from rest
            return t_c + 0.5 * R * (x - (1 - np.exp(-2 * x)) / 2)

        t = self.drive(ValueTracker(1.0), clock)
        morph, flash = ValueTracker(0.0), ValueTracker(0.0)
        rims, arms, ink = ValueTracker(1.0), ValueTracker(1.0), ValueTracker(1.0)
        zoom, op = ValueTracker(1.0), ValueTracker(1.0)
        camx, camy, follow = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)

        def state():
            a = morph.get_value()
            s = {**V.S01_END, "terms": V.tween_terms(a), "t": t.get_value(), "ink_from": t.get_value() - 1.0,
                 "rim_alpha": rims.get_value(), "arm_alpha": arms.get_value(), "ink_alpha": ink.get_value(),
                 "ink_boost": flash.get_value(), "zoom": zoom.get_value(), "opacity": op.get_value(),
                 "cam": complex(camx.get_value(), camy.get_value())}
            f = follow.get_value()
            if f > 0:                                  # ride along with the pen: circles riding circles
                s["cam"] = (1 - f) * s["cam"] + f * plate.joints(s)[-1]
                s["zoom"] *= 1 + 3.0 * f
            return s

        plate = V.EpicyclePlate(state)
        self.add(plate, morph, flash, rims, arms, ink, zoom, op, camx, camy, follow)

        # the loop has just closed: a flash runs along the whole clef
        self.play(flash.animate.set_value(1.0), run_time=self.snap(0.7), rate_func=there_and_back)

        # "strange about this": the camera rides along with the pen, into the small circles that steer it
        self.beat("strange", follow.animate.set_value(1.0), rt=1.3)
        self.wait_until(self.t("roundest thing") - S.LEAD - 0.85)
        self.play(follow.animate.set_value(0.0), run_time=self.snap(0.8), rate_func=smooth)

        # "roundest thing": the chain steps back; the root circle alone
        r1 = abs(V.clef_terms()[0][1])
        root = Circle(radius=r1, color=S.ARM, stroke_width=3)
        root_arm = always_redraw(lambda: Line([0, 0, 0], plate.project(plate.joints()[1]),
                                              color=S.ARM, stroke_width=3))
        n1 = V.clef_terms()[0][0]
        root_lab = labels([(0j, r1, exp_parts(n1, S.BWD if n1 < 0 else S.FWD), S.ARM, 135.0)], size=34)
        self.beat("roundest thing", rims.animate.set_value(0.15), arms.animate.set_value(0.15),
                  ink.animate.set_value(0.3), FadeIn(root), FadeIn(root_arm), FadeIn(root_lab), rt=0.8)

        # beside it, a polygon gains corners until it becomes the circle: 3, 4, 6, 12 sides, then n → ∞
        T_poly = self.t("roundest thing") - S.LEAD
        pop = ValueTracker(0.0)
        self.add(pop, V.redraw(lambda: polygon_panel(self.now - T_poly, pop.get_value())))
        self.play(pop.animate.set_value(1.0), run_time=self.snap(0.4))

        # "no corners": a ghost square flickers around it, what a circle is not
        ghost = DashedVMobject(Square(side_length=2 * r1, color=S.GHOST_LINE, stroke_width=2.5), num_dashes=40)
        self.beat("no corners", FadeIn(ghost, scale=1.04), rt=0.5)
        self.play(FadeOut(ghost), run_time=self.snap(0.6))

        # "straight edges": a straight line rolls once around the circle, touching it at one point only
        th = ValueTracker(0.0)
        self.add(th)
        def tangent():
            u = np.exp(1j * th.get_value())
            p, d = r1 * u, 1j * u
            line = Line([(p - 1.3 * d).real, (p - 1.3 * d).imag, 0], [(p + 1.3 * d).real, (p + 1.3 * d).imag, 0],
                        color=S.GHOST_LINE, stroke_width=3)
            return VGroup(line, Dot([p.real, p.imag, 0], radius=0.06, color=S.INK))
        tan = always_redraw(tangent)
        self.beat("straight edges", FadeIn(tan), th.animate(rate_func=smooth).set_value(2 * np.pi), rt=1.2)

        # "sharp turns": the chain returns; push in on the clef's sharpest turn and back out
        turn = V.sharpest_turn(V.CLEF_SCALE * V.treble_clef(1000))
        self.beat("sharp turns", rims.animate.set_value(1.0), arms.animate.set_value(1.0),
                  ink.animate.set_value(1.0), FadeOut(root), FadeOut(root_arm), FadeOut(root_lab), FadeOut(tan),
                  pop.animate.set_value(0.0),
                  camx.animate.set_value(turn.real), camy.animate.set_value(turn.imag),
                  zoom.animate.set_value(2.0), rt=0.8)
        self.play(camx.animate.set_value(0.0), camy.animate.set_value(0.0), zoom.animate.set_value(1.0),
                  run_time=self.snap(0.7), rate_func=smooth)

        # "square": no cut, the chain re-tunes; the ink morphs clef → square (1.4 s).
        # "four perfect corners" lands mid-morph: the dive into the corner the pen will stop on
        # starts on its word, inside the same play (1.5 s)
        a0 = self.t("square") - S.LEAD
        d0 = self.t("four perfect corners") - S.LEAD - a0
        total = d0 + 1.5
        self.play_at(self.t("square"), morph.animate(rate_func=V.window(0, 1.4 / total)).set_value(1.0),
                     *[m.animate(rate_func=V.window(d0 / total, 1.0)).set_value(v)
                       for m, v in ((camx, C.real), (camy, C.imag), (zoom, 6.0))], run_time=total)

        # "draw a corner": the pen arrives on the corner and the picture freezes (clock stops here)
        self.beat("draw a corner", rims.animate.set_value(0.25), arms.animate.set_value(0.25), rt=0.4)

        # "fourier series": pull back, the square sits high; the title sets beneath it
        zf, lift = 0.62, 0.95
        sweep = ValueTracker(0.0)
        title = TitlePlate("Fourier Series", size_px=88, sweep=sweep).move_to(DOWN * 2.05)
        self.add(sweep)
        self.play_at(self.t("fourier series"),
                     *[m.animate(rate_func=V.window(0, 0.75)).set_value(v) for m, v in
                       ((camx, 0.0), (camy, -lift / zf), (zoom, zf), (rims, 0.7), (arms, 0.7))],
                     FadeIn(title, shift=UP * 0.12, rate_func=V.window(0.2, 0.9)),
                     sweep.animate(rate_func=V.window(0.25, 1.0, linear)).set_value(1.0), run_time=1.6)

        # "joseph fourier": his portrait at the right (Boilly, public domain: assets/images/CREDITS.md),
        # the series he named at the left, beside the square
        img = ImageMobject(str(Path(__file__).resolve().parents[1] / "assets" / "images" / "fourier_portrait.jpg"))
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])
        img.height = 3.3
        img.move_to([4.75, lift + 0.15, 0])
        frame = SurroundingRectangle(img, buff=0.0, color=S.ARM, stroke_width=1.5).set_stroke(opacity=0.6)
        name = V.label("Joseph Fourier", size=30, color=S.LABEL).next_to(img, DOWN, buff=0.22)
        years = V.label("1768 – 1830", size=22, color=S.LABEL_MUTED).next_to(name, DOWN, buff=0.1)
        portrait = Group(img, frame, name, years)
        series = MathTex(r"f(t)", "=", r"\sum_{n}", r"c_n\,e^{2\pi i n t}", font_size=44)
        series[0].set_color(S.INK)
        series[2].set_color(S.LABEL)
        series[3].set_color(S.STILL)
        series.move_to([-4.5, lift, 0])                 # left of the square, which sits high
        self.play_at(self.t("fourier series") + 0.5, FadeIn(series, shift=RIGHT * 0.1), run_time=0.8)
        self.beat("joseph fourier", FadeIn(img, shift=LEFT * 0.12), FadeIn(frame), FadeIn(name, shift=UP * 0.06),
                  FadeIn(years, shift=UP * 0.06), rt=0.8)

        # "heat": teaser flash of the hot ring (half ember, half ice)
        ring = V.heat_ring(center=UP * lift, rx=2.1, ry=0.8)
        self.beat("heat", FadeIn(ring, scale=0.96), op.animate.set_value(0.25), rt=0.4)
        self.wait(self.snap(0.9))
        self.play(FadeOut(ring), op.animate.set_value(1.0), run_time=self.snap(0.4))

        # "bold claim": the title lifts away, the square goes dark
        self.beat("bold claim", FadeOut(Group(title, series, portrait), shift=UP * 0.25), op.animate.set_value(0.0), rt=0.6)
        self.remove(plate)

        # the gallery wall. "bold claim": a top row of circle art draws (butterfly, rose, fish, ∞, spirograph);
        # "any loop": the five loops below, each with its series and its circle count beneath
        art = [(V.butterfly_terms(), 0.8), (V.rose_terms(), 0.85), (V.fish_terms(), 0.8),
               (V.infinity_terms(), 0.95), (V.spiro_terms(), 0.85)]
        loops = [(V.clef_terms(), 0.3, "clef"), (V.star_terms(), 0.95, "star"), (V.square_terms(), 0.4, "square"),
                 (V.heart_terms(), 0.9, "heart"), (V.bean_gallery(), 0.65, "bean")]
        XS = (-5.4, -2.7, 0.0, 2.7, 5.4)
        TOP_Y, LOW_Y, EQ_Y = 2.2, -0.35, -2.2
        T_art = self.t("bold claim") - S.LEAD + 0.35
        T_g = self.t("any loop") - S.LEAD
        ops, rims_g = [], []

        def wall_plate(terms, k, at, t0, loop_s, h):
            sc = [(n, k * c) for n, c in terms]
            g = self.drive(ValueTracker(0.0), lambda now, t0=t0: max(0.0, (now - t0) / loop_s))
            o, r = ValueTracker(0.0), ValueTracker(1.0)
            ops.append(o)
            rims_g.append(r)
            self.add(o, r)
            return V.EpicyclePlate(lambda: {
                **V.S01_END, "terms": sc, "origin": at, "t": g.get_value(), "ink_from": 0.0,
                "opacity": o.get_value(), "rim_alpha": r.get_value(), "sparks": 0.0, "vignette": 0.0,
                "bloom": 0.45, "ink_width": 1.1, "ink_head": 3.0},
                width=2.7, height=h, center=[at.real, at.imag, 0])

        for i, (terms, k) in enumerate(art):
            self.add(wall_plate(terms, k, complex(XS[i], TOP_Y), T_art + 0.12 * i, 3.2, 2.4))
        for i, (terms, k, _) in enumerate(loops):
            self.add(wall_plate(terms, k, complex(XS[i], LOW_Y), T_g + 0.15 * i, 2.6, 3.0))
        self.play_at(self.t("bold claim") + 0.35, *[o.animate(rate_func=V.window(0.12 * i, 0.12 * i + 0.45))
                                                   .set_value(1.0) for i, o in enumerate(ops[:5])], run_time=1.0)

        def eq(terms, name):
            N = max(abs(n) for n, _ in terms)
            m = MathTex(r"\sum_{n=-%d}^{%d}" % (N, N), r"c_n\,e^{2\pi i n t}", font_size=26)
            m[0].set_color(S.LABEL)
            m[1].set_color(S.STILL)
            cap = V.label(f"{name} \u00b7 {len(terms)} circles", 19, S.LABEL_MUTED)
            return VGroup(m, cap).arrange(DOWN, buff=0.14)
        eqs = [eq(terms, name).move_to([XS[i], EQ_Y - 0.15, 0]) for i, (terms, _, name) in enumerate(loops)]
        self.play_at(self.t("any loop"), *[o.animate(rate_func=V.window(0.1 * i, 0.1 * i + 0.4)).set_value(1.0)
                                           for i, o in enumerate(ops[5:])],
                     *[FadeIn(e, shift=UP * 0.08, rate_func=V.window(0.35 + 0.1 * i, 0.75 + 0.1 * i))
                       for i, e in enumerate(eqs)], run_time=1.2)

        # "spinning circles": rims pulse in a stagger across the wall, then everything fades to black
        self.play_at(self.t("spinning circles"), *[r.animate(rate_func=V.window(0.05 * i, 0.05 * i + 0.5, there_and_back))
                                                   .set_value(2.0) for i, r in enumerate(rims_g)], run_time=0.9)
        self.wait_until(END - 0.6)
        self.play(*[o.animate.set_value(0.0) for o in ops], *[FadeOut(e) for e in eqs], run_time=self.snap(0.55))
        self.finish()


