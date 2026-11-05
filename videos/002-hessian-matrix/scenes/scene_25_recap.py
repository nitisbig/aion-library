"""Scene 25 · Outro: recap (559.567–594.933 s).

"Let's walk back through it. On a line, the second derivative measures bending. Positive
is a smile. Negative is a frown. On a surface, there are four second derivatives,
bending in x, bending in y, and the twist, which shows up twice. Arrange them in a grid
and you have the Hessian. Give it any direction, and it tells you the bending that way.
Its eigenvectors point along the strongest smile and the deepest frown. Its eigenvalues
say how strong they are. And at a flat point, their signs decide everything. All
positive, a valley, all negative, a peak, mixed, a saddle."

Four glass cards fill a 2×2, one idea each; on "signs decide everything" brackets close
around them, so the recap itself is a matrix. Card 3 uses the puzzle surface (bend =
2 + 3 sin 2θ, λ = 5 at 45°, −1 at 135°; asserted in ch7).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *

from aion import style as S
import shared as V
import ch5 as C5
import ch6 as C6
import ch7 as C

START, END = V.scene_range(25)


class Scene25Recap(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 24's last frame ──
        e = C6.s24_end()
        self.add(e["plate"], *e["rig"].trackers(), e["ball"])
        e["ball"].update()

        # O-1 · on a line
        bg, eb = C.card(0)
        e["ball"].clear_updaters()
        self.beat("walk back through it", *e["rig"].to(opacity=0.0), FadeOut(e["ball"]),
                  FadeIn(bg, shift=UP * 0.12), FadeIn(eb, shift=UP * 0.12), rt=0.8)
        self.remove(e["plate"])
        self.beat("on a line", Create(C.parabola()), rt=0.6)
        self.beat("smile", FadeIn(C.line_gauge(1), shift=UP * 0.08), rt=0.4)
        self.beat("frown", FadeIn(C.line_gauge(-1), shift=UP * 0.08), rt=0.4)

        # O-2 · on a surface: four second derivatives in a grid
        bg, eb = C.card(1)
        g, ents, lab = C.hgrid()
        self.beat("on a surface", FadeIn(bg, shift=UP * 0.12), FadeIn(eb, shift=UP * 0.12), g.appear(), rt=0.8)
        fills = [g.fill(i, j, m) for (i, j), m in zip(C.CELLS, ents)]
        tints = [g.tint(i, j, col) for (i, j), col in zip(C.CELLS, C.CELL_COL)]
        self.beat("four second derivatives", LaggedStart(*[AnimationGroup(f, t) for f, t in zip(fills, tints)],
                                                         lag_ratio=0.25), rt=1.0)
        twist = [g.cells[0][1], g.cells[1][0], ents[1], ents[2]]
        self.beat("shows up twice", *[V.pulse(m, lambda x: x.scale(1.15)) for m in twist], rt=0.6)
        g.show_brackets()
        g.brackets.set_stroke(width=2.5)
        g.remove(g.brackets)
        lab.next_to(g.brackets, LEFT, buff=0.18)
        self.beat("you have the hessian", *[Create(b) for b in g.brackets], FadeIn(lab, shift=RIGHT * 0.08), rt=0.6)
        g.add(g.brackets)

        # O-3 · any direction: the dial sweeps, then the eigen-axes and eigenvalues
        bg, eb = C.card(2)
        th = ValueTracker(0.0)
        arrow = C.u_arrow(th)
        dg, k = C.dial_gauge(th)
        self.add(th, k)
        self.beat("any direction", FadeIn(bg, shift=UP * 0.12), FadeIn(eb, shift=UP * 0.12), Create(C.dial()),
                  FadeIn(arrow), FadeIn(dg), rt=0.7)
        self.play(th.animate.set_value(405.0), run_time=self.snap(self.t("eigenvectors") - 0.25 - self.now),
                  rate_func=smooth)
        self.beat("eigenvectors", *[Create(a) for a in C.eigen_axes()], rt=0.6)
        self.beat("eigenvalues", FadeIn(C.eigen_labels(), shift=UP * 0.06), rt=0.5)

        # O-4 · at a flat point: the signs decide, and the four cards become a matrix
        bg, eb = C.card(3)
        ax = C.mini_chart()
        quads = {q: C5.quadrant(ax, q).set_opacity(0) for q in (1, 2, 3, 4)}
        self.add(*quads.values())
        self.beat("flat point", FadeIn(bg, shift=UP * 0.12), FadeIn(eb, shift=UP * 0.12), Create(ax),
                  FadeIn(C.mini_axis_labels(ax)), rt=0.8)
        self.bring_to_front(*quads.values(), ax)      # above the card's glass, under the axes
        self.beat("signs decide everything", *[Create(b) for b in C.big_brackets()], rt=1.0)
        show = lambda q: [quads[q].animate.set_fill(opacity=0.13), FadeIn(C.mini_word(ax, q), scale=0.9)]
        self.beat("all positive", *show(1), rt=0.4)
        self.beat("all negative", *show(3), rt=0.4)
        self.beat("mixed", *show(2), *show(4), rt=0.4)
        self.finish()
