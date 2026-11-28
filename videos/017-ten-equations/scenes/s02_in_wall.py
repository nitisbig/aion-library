"""in_s02 · Ten windows (promise). Storyboard: plan/scene_plan.md § in_s02. Layout L4.

Opens on in_s01's last frame: framed on T5 (lit), its nine neighbours dim. 'ten of them': the view pulls back to the
whole 5x2 wall (intro.view), T5's name and year write under it, and a thin timeline 1763 → 1973 draws beneath the
wall. Each tile then lights in the order the narration names it (Bayes 1763 on 'probability', Black–Scholes 1973 on
'pricing', then light, gravity, the atom, air, clocks, learning, the wire), lifting a little as it does; its name and
year write beneath it and its tick lands on the timeline in its hue.
"""
import numpy as np
from aion import *

import intro as I
import outro as O
from beats import T
from kit import P3, caps, glow, polyline
from theme import CHAPTERS


@scene(T.in_s02, T.in_s03)
def s02_in_wall(s):
    s.solid(C.bg, z=-200)
    t_ten = float(T.in_s02_ten_of_them)
    t_on = [0.0] * 10
    t_on[4] = t_ten + 0.4
    for w, i in I.LIGHT:
        t_on[i] = float(getattr(T, f"in_s02_{w}"))

    def lit(i, t):
        return 1.0 if i == 4 else I.ease(t, t_on[i] - 0.1, t_on[i] + 0.5)

    def bump(i, t):
        if i == 4:
            return 0.0
        x = (t - t_on[i] + 0.1) / 0.9
        return 0.0 if x <= 0 or x >= 1 else float(np.sin(np.pi * x)) ** 2

    for i in range(10):
        O.tile_layer(s, i, lambda t, i=i: I.tile_place(i, t, grow=1 + 0.05 * bump(i, t)),
                     Track(lambda t, i=i: 0.25 + 0.75 * lit(i, t)), z=1)

    # names and years, written as each tile lights
    names = [O.wall_labels(i)[0] for i in range(10)]

    def labels(t):
        g = VGroup()
        for i in range(10):
            a = I.ease(t, t_on[i] + 0.1, t_on[i] + 0.7)
            if a > 0.01:
                g.add(names[i].copy().set_opacity(a))
        return I.apply_view(g, t)
    s.manim(z=20).redraw(labels, during=(s.start, s.end))

    # the timeline: 1763 to 1973, a tick in each tile's hue as it lights
    def timeline(t):
        u = I.ease(t, t_ten, t_ten + 1.4)
        g = VGroup()
        if u <= 0:
            return g
        y = I.TL_Y
        g.add(Line(P3(I.TL_X0, y), P3(I.TL_X0 + (I.TL_X1 - I.TL_X0) * u, y), stroke_color=C.ghost, stroke_width=1.5))
        g.add(caps("1763", 20, C.muted).set_opacity(u).next_to(P3(I.TL_X0, y), LEFT, buff=0.15),
              caps("1973", 20, C.muted).set_opacity(u).next_to(P3(I.TL_X1, y), RIGHT, buff=0.15))
        for i in range(10):
            a = I.ease(t, t_on[i], t_on[i] + 0.4)
            if a > 0.01:
                x = I.tl_x(I.YEARS[i])
                g.add(Line(P3(x, y - 0.1 * a), P3(x, y + 0.1 * a), stroke_color=getattr(C, CHAPTERS[i]),
                           stroke_width=3))
        return I.apply_view(g, t)
    s.manim(z=20).redraw(timeline, during=(t_ten - 0.1, s.end))

    # as each tile lights, a streak of its hue runs along its base and settles into the short rule
    def streaks(t):
        g = VGroup()
        for i in range(10):
            if i == 4:
                continue
            u = I.ease(t, t_on[i] - 0.05, t_on[i] + 0.55)
            back = I.ease(t, t_on[i] + 0.6, t_on[i] + 1.2)
            if u <= 0 or back >= 1:
                continue
            x, y = I.pic_centre(i)
            x0, yb = x - O.TW / 2, y - O.TH / 2 - O.RULE_GAP - 0.03
            x1 = x0 + O.TW * u
            hue = getattr(C, CHAPTERS[i])
            g.add(polyline([(x0, yb), (x1, yb)], hue, 2.4, 1 - back))
            g.add(Dot(P3(x1, yb), radius=0.035, color=hue).set_opacity(1 - back))
        return I.apply_view(g, t)
    glow(s, C.light, z=15, k=0.7).redraw(streaks, during=(s.start, s.end))
