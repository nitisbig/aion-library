"""Scene 15 · Ch4: circles in the sky (280.783–296.467 s).

"This picture is actually very old. Nearly two thousand years ago, astronomers tracked
the planets with circles riding on circles. They were wrong about how the sky works. But
they were right about the circles. With enough of them, you can follow almost any path."

Mars seen from Earth, computed: geocentric Mars = Mars(helio) − Earth(helio), i.e. a big
circle (Mars's orbit, 1.524 AU, 1.881 yr) carrying a small one (Earth's orbit, 1 AU, 1 yr),
both counterclockwise. Real sizes and periods, time compressed (ch4.years). The aside
re-centers on the Sun: the loops untangle into a plain orbit, then back.
Stars are seeded Manim dots (the storyboard's skia starfield was not needed).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import Dot, FadeOut, ValueTracker, VGroup, VMobject, there_and_back

from aion import style as S
import shared as V
import ch2 as C2
import ch4 as C

START, END = V.scene_range(15)


def s14_end_machine(scene, op: ValueTracker):
    """S14's last picture, still running: the two-circle chain and its gold ink."""
    clk = C.clock14()
    T_ink = C.cue("right on the page", C.S14)

    def draw():
        o = op.get_value()
        if o <= 0:
            return VMobject()
        g, _ = C.chain(C.vecs14(float(clk(scene.now))), C.CC, rim_op=o, arm_op=o, pen_op=o, colors=[S.FWD, S.FWD],
                       ns=[1, 3])
        return VGroup(C.ink14(scene.now, T_ink, op=o), g)
    return V.redraw(draw)


class Scene15Sky(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        marker = C2.corner_marker()
        eb = V.eyebrow("04 · WAVES BECOME DRAWINGS")
        op14 = ValueTracker(1.0)
        self.add(op14, s14_end_machine(self, op14), eb, marker)

        yrs = C.years()
        T_trail = C.cue("circles riding on circles", C.S15)
        tk = {k: ValueTracker(v) for k, v in dict(sky=0.0, mars=0.0, rim=0.0, arm=0.0, trail=0.0, s=0.0,
                                                  sun=0.0, earth=0.0, glow=0.0).items()}
        self.add(*tk.values())
        stars = C.stars().copy()
        for d in stars:
            d.save_state()
        star_op = ValueTracker(0.0)
        self.add(star_op)

        def sky():
            sk = star_op.get_value()
            for d in stars:
                d.restore()
                d.set_opacity(d.get_fill_opacity() * sk)
            y = float(yrs(self.now))
            s = tk["s"].get_value()
            e_now = complex(C.earth_helio(y))
            out = VGroup()
            # gold trail of Mars since "circles riding on circles"
            o_tr = tk["trail"].get_value()
            if o_tr > 0 and self.now > T_trail:
                ys = np.linspace(float(yrs(T_trail)), y, max(2, int(500 * (y - float(yrs(T_trail))))))
                out.add(C.path(C.sky_point(ys, s), op=o_tr, width=3.0))
            # Earth (the speed-zero center), the circles, Mars
            earth = C.SKY_C + C.SKY_K * s * e_now
            r_o, a_o = tk["rim"].get_value(), tk["arm"].get_value()
            if r_o > 0 or a_o > 0:
                m_rel = complex(C.mars_helio(y))
                vecs = [C.SKY_K * m_rel, -C.SKY_K * e_now]
                g, _ = C.chain(vecs, earth, rim_op=r_o, arm_op=a_o, pen_op=0.0, colors=[S.FWD, S.FWD],
                               rim_w=3.0 + 2.5 * tk["glow"].get_value())
                out.add(g)
            if tk["earth"].get_value() > 0:
                out.add(Dot(C.to3(earth), radius=0.09, color=S.STILL).set_opacity(tk["earth"].get_value()))
            if tk["sun"].get_value() > 0:
                sun = C.SKY_C + C.SKY_K * (s - 1) * e_now
                out.add(Dot(C.to3(sun), radius=0.26, color=S.LIGHT).set_opacity(0.2 * tk["sun"].get_value()),
                        Dot(C.to3(sun), radius=0.12, color=S.LIGHT).set_opacity(tk["sun"].get_value()))
            if tk["mars"].get_value() > 0:
                out.add(C.pen(C.sky_point(y, s), tk["mars"].get_value()))
            return out

        self.add(stars, V.redraw(sky))
        self.bring_to_back(stars)

        # "very old": the drawing and the eyebrow go; the stage becomes a night sky with Earth at its center
        self.beat("very old", op14.animate.set_value(0.0), FadeOut(eb), star_op.animate.set_value(1.0),
                  tk["earth"].animate.set_value(1.0), rt=1.0)

        # "astronomers": Mars wanders across the stars (the sky clock starts here)
        self.beat("astronomers", tk["mars"].animate.set_value(1.0), rt=0.8)

        # "circles riding on circles": Mars's circle carries Earth's; the planet traces its retrograde loops
        self.beat("circles riding on circles", tk["rim"].animate.set_value(1.0), tk["arm"].animate.set_value(1.0),
                  tk["trail"].animate.set_value(1.0), rt=0.8)

        # "wrong about how the sky works": re-center on the Sun; the loops untangle into a plain orbit
        self.beat("wrong about how the sky works", tk["s"].animate.set_value(1.0), tk["sun"].animate.set_value(1.0),
                  tk["rim"].animate.set_value(0.0), tk["arm"].animate.set_value(0.0), rt=1.2)
        # … and back to Earth's view, circles and all ("But they were right…")
        self.beat("but", tk["s"].animate.set_value(0.0), tk["sun"].animate.set_value(0.0),
                  tk["rim"].animate.set_value(1.0), tk["arm"].animate.set_value(1.0), rt=1.0)

        # "right about the circles": the rims brighten
        self.beat("right about the circles", tk["glow"].animate(rate_func=there_and_back).set_value(1.0), rt=0.8,
                  rate=None)

        # "almost any path": the stars and the machinery go; the gold loops stay on black
        self.beat("almost any path", star_op.animate.set_value(0.0), tk["rim"].animate.set_value(0.0),
                  tk["arm"].animate.set_value(0.0), tk["earth"].animate.set_value(0.0),
                  tk["mars"].animate.set_value(0.0), rt=1.0)
        self.finish()


def s15_end_trail():
    """S15's last picture: the gold retrograde loops, static (the sky clock has stopped)."""
    yrs = C.years()
    y0, y1 = float(yrs(C.cue("circles riding on circles", C.S15))), float(yrs(C.S15[1]))
    return C.path(C.sky_point(np.linspace(y0, y1, int(500 * (y1 - y0)))), width=3.0)
