"""c02_s01 · Gravity as shape (hook). Storyboard: plan/scene_plan.md § c02_s01. Layout L1.

Opens on c01_s03's last frame (the ray and the mass), which gives way to the chapter card. Newton's picture first:
a pull along a line from the Earth to the Sun. Then Einstein's: a grid sheet seen in perspective; the Sun drops onto
it and the sheet sinks into the weak-field well (ch2.depth); a marble rolls in and keeps to a precessing orbit (a
Schwarzschild geodesic, ch2._orbit_table). On 'straightest' the view drops low along the orbit and its path lights.
"""
import math

import numpy as np
from aion import *

import ch2
from beats import T
from kit import P3, XW, add_rail, chapter_card, glimpse, polyline, sans, smooth01, sphere_rgba

RAY_Y = 0.95                                     # c01_s03's last frame


def _geodesic(t, op):
    """The whole orbit so far, lit: the straightest path open to it through the curved sheet (graphic glow)."""
    if op < 0.01:
        return VGroup()
    v = ch2.view(t)
    path = ch2.orbit_path(t, 4.0)
    rr = np.hypot(path[:, 0], path[:, 1])
    PX, PY, _ = ch2.project(path[:, 0], path[:, 1], ch2.depth(rr, ch2.amount(t)) + 0.02, v)
    return polyline(list(zip(PX, PY)), C.einstein, 3.0, op)


@scene(T.c02_s01, T.c02_s02)
def s07_c02_shape(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    # c01_s03's last frame, giving way to the card
    leave = fade(t0 - 5, dur=0.1, out=t0 + 0.5, out_dur=0.6)
    ray = s.manim(z=10, fx=[Glow(C.light, strength=C.glow * 0.55, radius=C.glow_r)], opacity=leave)
    ray.add(Line(P3(-XW - 0.4, RAY_Y), P3(XW + 0.4, RAY_Y), stroke_color=C.light, stroke_width=2.4))
    s.add(ArrayLayer(sphere_rgba(C.mass), height=1.75, pos=(2.7, -0.5), z=4, opacity=leave))
    chapter_card(s, 2, at=T.c02_s01 + 0.9, out=T.c02_s01_pull - 0.5)
    add_rail(s, 2, opacity=fade(T.c02_s01 + 0.9, dur=0.8), busy=True)

    # Newton: a pull along the line between them
    hud = s.manim(z=50, parallax=0.0)
    m = s.manim(z=5)
    sun2d = Circle(radius=0.55, stroke_width=0, fill_color=C.mass, fill_opacity=1).move_to(P3(-1.2, -0.2))
    earth2d = Circle(radius=0.13, stroke_width=0, fill_color=C.einstein, fill_opacity=1).move_to(P3(2.6, 0.5))
    pull = Arrow(P3(2.42, 0.47), P3(-0.55, -0.09), buff=0, stroke_width=3, color=C.muted,
                 max_tip_length_to_length_ratio=0.06)
    newton = VGroup(sun2d, earth2d, pull)
    t_pull = T.c02_s01_pull
    m.play(FadeIn(VGroup(sun2d, earth2d)), at=t_pull - 0.5, dur=0.6)
    m.play(GrowArrow(pull), at=t_pull, dur=0.8)
    glimpse(s, "newton", t_pull - 0.2, C.mass, dur=min(3.8, float(T.c02_s01_einstein) - 0.9 - float(t_pull)))
    m.play(FadeOut(newton), at=T.c02_s01_einstein - 0.5, dur=0.8)
    glimpse(s, "einstein_1921", T.c02_s01_einstein + 0.1, C.einstein)

    # Einstein: the sheet; the Sun drops onto it and it sinks
    sheet_op = fade(T.c02_s01_einstein, dur=1.2)
    s.manim(z=-6).redraw(lambda t: ch2.sheet(t, float(sheet_op(t)))[0], during=(T.c02_s01_einstein - 0.7, s.end))
    s.manim(z=-2).redraw(lambda t: ch2.sheet(t, float(sheet_op(t)))[1], during=(T.c02_s01_einstein - 0.7, s.end))

    def sun_pos(t):
        return ch2.sun_screen(t)[0]

    def sun_size(t):
        return ch2.sun_screen(t)[1]
    s.add(ArrayLayer(sphere_rgba(C.mass), height=1.0, pos=sun_pos, scale=sun_size, z=-4,
                     opacity=fade(T.c02_s01_bends - 0.6, dur=0.5), start=T.c02_s01_bends - 1.2))

    # the marble rolls in and keeps to its orbit
    m_op = fade(ch2.orbit_t0(), dur=0.6)
    s.manim(z=-5).redraw(lambda t: ch2.marble(t, float(m_op(t)), True), during=(ch2.orbit_t0() - 0.2, s.end))
    s.manim(z=-1).redraw(lambda t: ch2.marble(t, float(m_op(t)), False), during=(ch2.orbit_t0() - 0.2, s.end))

    # Earth and Sun named
    tags = s.manim(z=40, parallax=0.0)

    def names(t):
        a = float(smooth01((t - float(T.c02_s01_earth) + 0.15) / 0.5)) * \
            (1 - float(smooth01((t - float(T.c02_s01_straightest) + 0.3) / 0.5)))
        g = VGroup()
        if a < 0.01:
            return g
        v = ch2.view(t)
        (sx, sy), dia = ch2.sun_screen(t)
        x, y = ch2.marble_xy(t)
        X, Y, _ = ch2.project(x, y, float(ch2.depth(math.hypot(x, y), ch2.amount(t))) + 0.11, v)
        g.add(sans("Sun", 24, C.muted).set_opacity(a).move_to(P3(sx, sy + dia / 2 + 0.28)),
              sans("Earth", 24, C.einstein).set_opacity(a).move_to(P3(X, Y + 0.36)))
        return g
    tags.redraw(names, during=(T.c02_s01_earth - 0.8, T.c02_s01_straightest + 0.6))

    # straightest: the path lights (glow on the graphic only), a key word under it
    geo_op = fade(T.c02_s01_straightest, dur=0.9, out=s.end - 0.2, out_dur=0.5)
    s.manim(z=-1.5, fx=[Glow(C.einstein, strength=C.glow * 0.8, radius=C.glow_r)]) \
        .redraw(lambda t: _geodesic(t, float(geo_op(t))), during=(T.c02_s01_straightest - 0.5, s.end))
    word = sans("the straightest path", 28, C.einstein).move_to(P3(1.4, -2.95))
    tags.play(FadeIn(word, shift=0.08 * UP), at=T.c02_s01_straightest + 0.5, dur=0.6)
    tags.play(FadeOut(word), at=s.end - 0.4, dur=0.4)
