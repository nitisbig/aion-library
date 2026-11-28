"""c06_s03 · Straight lines and the scale of everything. Storyboard: plan/scene_plan.md § c06_s03.

An orrery opens it: the six planets circling at their real periods, the far ones crawling. Six planets (NASA fact sheet values, logdata) on linear axes, distance (AU) against period (years); T = a^1.5 draws
through them. On "take the logarithm" every tick and point moves continuously from its linear to its logarithmic
position (u: 0 → 1), and the curve straightens into a line of fitted slope 1.500, shown as a 2-across, 3-up triangle.
Then one ruler of powers of ten in metres carries an atom, a person, the Earth and a galaxy: 31 powers of ten.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from ch6 import atom, earth, galaxy, person
from kit import P3, add_rail, ctex, fit, glow, polyline, ramp, sans, show_tag, smooth01, tex, tint, word_at, Y1

XA, XB, YA, YB = -5.6, 1.4, -2.0, 2.7
CX = 4.3
LA, LT = (-0.6, 1.2), (-0.8, 1.6)            # log10 ranges for a and T


@scene(T.c06_s03, T.out_s01)
def s21_c06_kepler(s):
    s.solid(C.bg, z=-200)
    add_rail(s, 6)
    t0, end = float(T.c06_s03), float(s.end)
    tk, tb = float(T.c06_s03_kepler), float(T.c06_s03_bending_curve)
    tl, t32 = float(T.c06_s03_take_the_logarithm), float(T.c06_s03_three_steps_for_ever)
    tp, tat = float(T.c06_s03_power_law), float(T.c06_s03_atom)
    part1 = Track(lambda t: 1 - ramp(t, tat - 0.6, 0.8))
    m = s.manim(z=4, opacity=part1)
    uu = lambda t: smooth01(min(max((t - tl - 0.2) / 2.4, 0.0), 1.0))  # noqa: E731

    def sx(a, u):
        lin = XA + (XB - XA) * a / 10
        lg = XA + (XB - XA) * (math.log10(a) - LA[0]) / (LA[1] - LA[0])
        return lin + (lg - lin) * u

    def sy(T_, u):
        lin = YA + (YB - YA) * T_ / 30
        lg = YA + (YB - YA) * (math.log10(T_) - LT[0]) / (LT[1] - LT[0])
        return lin + (lg - lin) * u

    # an orrery opens the scene: the six planets on circles, each going round at its real period (one year in
    # 2.5 s), so the far ones visibly crawl; it gives way to the plot as the curve is named
    OC, RS = P3(CX + 0.1, 0.25), 0.62                       # centre, radius scale (radius = RS·√a, compressed)
    orb_op = Track(lambda t: ramp(t, t0 + 0.3, 1.0) * (1 - ramp(t, tb - 1.6, 0.9)))
    orbits = s.manim(z=3, opacity=orb_op)
    orbits.add(VGroup(*[Circle(radius=RS * math.sqrt(a), stroke_color=tint(C.planet, 0.35), stroke_width=1.3)
                        .move_to(OC) for a, _ in ld.PLANETS.values()]), Dot(OC, radius=0.1, color=C.planet))
    spin = glow(s, C.planet, z=3.5, k=0.8, opacity=orb_op)
    rng0 = np.random.default_rng(1619).uniform(0, 2 * math.pi, len(ld.PLANETS))

    def orrery(t):
        g = VGroup()
        for (a, T_), ph in zip(ld.PLANETS.values(), rng0):
            th = ph + 2 * math.pi * (t - t0) / (2.5 * T_)
            g.add(Dot(OC + RS * math.sqrt(a) * np.array([math.cos(th), math.sin(th), 0.0]),
                      radius=0.05 + 0.012 * math.log2(1 + a), color=C.planet))
        return g
    spin.redraw(orrery, during=(t0, tb - 0.6))

    axes = VGroup(Line(P3(XA, YA), P3(XB + 0.15, YA), stroke_color=C.axis, stroke_width=2.4),
                  Line(P3(XA, YA), P3(XA, YB + 0.15), stroke_color=C.axis, stroke_width=2.4))
    m.play(FadeIn(axes), at=tk - 1.0, dur=0.7)
    m.add(sans("distance from the Sun (AU)", 22, C.muted).move_to(P3((XA + XB) / 2, YA - 0.62)),
          sans("period (years)", 22, C.muted).rotate(PI / 2).move_to(P3(XA - 0.75, (YA + YB) / 2)), at=tk - 0.6)
    show_tag(s, "Kepler · 1619", C.planet, tk, dur=4.0, at=P3(0.0, Y1))

    def ticks(t):
        u = uu(t)
        g = VGroup()
        lab_lin, lab_log = 1 - ramp(u, 0.25, 0.3), ramp(u, 0.55, 0.3)
        for a in (0.5, 1, 2, 4, 6, 8, 10):
            x = sx(a, u)
            g.add(Line(P3(x, YA), P3(x, YA - 0.1), stroke_color=C.muted, stroke_width=1.5),
                  Line(P3(x, YA), P3(x, YB), stroke_color=C.grid_minor, stroke_width=1))
            op = (lab_lin if a in (2, 4, 6, 8, 10) else 0) + (lab_log if a in (0.5, 1, 2, 4, 10) else 0)
            if op > 0.01:
                g.add(tex(f"{a:g}", 20, C.muted).set_opacity(min(op, 1)).move_to(P3(x, YA - 0.3)))
        for T_ in (0.5, 1, 2, 5, 10, 20, 30):
            y = sy(T_, u)
            g.add(Line(P3(XA, y), P3(XA - 0.1, y), stroke_color=C.muted, stroke_width=1.5),
                  Line(P3(XA, y), P3(XB, y), stroke_color=C.grid_minor, stroke_width=1))
            op = (lab_lin if T_ in (10, 20, 30) else 0) + (lab_log if T_ in (0.5, 1, 2, 5, 10, 20) else 0)
            if op > 0.01:
                g.add(tex(f"{T_:g}", 20, C.muted).set_opacity(min(op, 1)).move_to(P3(XA - 0.3, y)))
        return g
    bg = s.manim(z=3, opacity=part1)
    bg.redraw(ticks, during=(tk - 1.0, tat + 0.3))

    pl = glow(s, C.planet, z=5, k=0.6, opacity=part1)

    def planets(t):
        u = uu(t)
        g = VGroup()
        for i, (name, (a, T_)) in enumerate(ld.PLANETS.items()):
            if t < tk + 0.3 * i:
                continue
            g.add(Dot(P3(sx(a, u), sy(T_, u)), radius=0.08, color=C.planet))
        return g
    pl.redraw(planets, during=(tk - 0.1, tat + 0.3))

    def names(t):
        u = uu(t)
        g = VGroup()
        for i, (name, (a, T_)) in enumerate(ld.PLANETS.items()):
            show = (name in ("Jupiter", "Saturn")) or u > 0.7
            if t < tk + 0.3 * i + 0.3 or not show:
                continue
            op = 1 if name in ("Jupiter", "Saturn") else ramp(u, 0.7, 0.3)
            g.add(sans(name, 20, C.planet).set_opacity(op).next_to(P3(sx(a, u), sy(T_, u)), RIGHT + DOWN * 0.6,
                                                                    buff=0.08))
        return g
    m.redraw(names, during=(tk, tat + 0.3))

    def curve(t):
        u = uu(t)
        if t < tb - 0.2:
            return VGroup()
        grow = ramp(t, tb - 0.2, 1.2)
        a_s = np.geomspace(0.3, 0.3 + (10.5 - 0.3) * grow, 160)
        pts = [(sx(a, u), sy(a ** 1.5, u)) for a in a_s if a ** 1.5 <= 33]
        return polyline(pts, tint(C.planet, 0.6), 2.5)
    bg.redraw(curve, during=(tb - 0.3, tat + 0.3))
    m.play(FadeIn(ctex([("T", C.planet), ("=", None), ("a^{1.5}", C.planet)], 36).move_to(P3(XA + 1.2, YB - 0.3))),
           at=tb + 0.6, dur=0.5)

    # slope triangle: 2 across, 3 up (in units of 0.2 decades)
    ux, uy = (XB - XA) / (LA[1] - LA[0]), (YB - YA) / (LT[1] - LT[0])
    la0 = 0.25
    p0 = P3(XA + ux * (la0 - LA[0]), YA + uy * (1.5 * la0 - LT[0]))
    p1 = p0 + RIGHT * ux * 0.4
    p2 = p1 + UP * uy * 0.6
    tri = VGroup(Line(p0, p1, stroke_color=C.steps, stroke_width=3), Line(p1, p2, stroke_color=C.value, stroke_width=3),
                 tex("2", 28, C.steps).next_to(Line(p0, p1), DOWN, buff=0.1),
                 tex("3", 28, C.value).next_to(Line(p1, p2), RIGHT, buff=0.1))
    m.play(Create(tri[0]), FadeIn(tri[2]), at=t32 - 0.3, dur=0.5)
    m.play(Create(tri[1]), FadeIn(tri[3]), at=word_at("three", t32 - 0.4) + 0.4, dur=0.5)
    sl = ctex([(r"\text{slope}=", None), (f"{ld.KEPLER_SLOPE:.3f}", C.steps)], 36).move_to(P3(CX, 0.5))
    m.play(FadeIn(sl), at=t32 + 1.2, dur=0.6)
    e1 = ctex([("T^2", C.planet), (r"\propto", None), ("a^3", C.planet)], 46).move_to(P3(CX, 2.5))
    m.play(Write(e1), at=tl - 0.4, dur=0.8)
    e2 = ctex([(r"\log T", C.planet), ("=", None), (r"\tfrac32", C.steps), (r"\log a", C.planet), ("+c", None)], 46)
    m.play(Write(fit(e2, 3.6).move_to(P3(CX, 1.5))), at=tp - 0.3, dur=1.0)

    # one ruler, atom to galaxy
    x_of = lambda p: -6.0 + (p + 10.5) * 0.375  # noqa: E731
    y = -0.9
    m2 = s.manim(z=4)
    r0 = tat - 0.3
    run = 2.2
    reach = lambda p: r0 + run * (p + 10.5) / 32.0  # noqa: E731
    m2.play(Create(Line(P3(x_of(-10.5), y), P3(x_of(21.5), y), stroke_color=C.ruler, stroke_width=2.5)), at=r0,
            dur=run, ease="linear", lead=0.0)
    for p in range(-10, 22):
        major = p % 5 == 0
        tick = Line(P3(x_of(p), y), P3(x_of(p), y - (0.22 if major else 0.12)), stroke_color=C.ruler,
                    stroke_width=2 if major else 1.3)
        anims = [FadeIn(tick)]
        if major:
            anims.append(FadeIn(tex(f"10^{{{p}}}", 24, C.steps).next_to(tick, DOWN, buff=0.1)))
        m2.play(*anims, at=reach(p), dur=0.25, lead=0.0)
    m2.add(sans("metres", 20, C.muted).move_to(P3(x_of(21.5), y - 0.75), aligned_edge=RIGHT), at=r0 + run)
    yo = y + 1.1
    objs = ((atom(), ld.SCALES["atom"], "atom", tat), (person(), ld.SCALES["person"], "person", word_at("person", tat)),
            (earth(), ld.SCALES["Earth"], "Earth", word_at("Earth", tat)),
            (galaxy(), ld.SCALES["Milky Way"], "galaxy", float(T.c06_s03_galaxy)))
    for obj, v, word, when in objs:
        p = math.log10(v)
        obj.move_to(P3(x_of(p), yo))
        lbl = sans(word, 22, C.muted).move_to(P3(x_of(p), yo + 0.85))
        dot = Dot(P3(x_of(p), y), radius=0.06, color=C.value)
        m2.play(FadeIn(obj, scale=0.8), FadeIn(lbl), FadeIn(dot), at=max(when, reach(p) + 0.05), dur=0.5)
    t31 = float(T.c06_s03_thirty_one_powers)
    pa, pg = math.log10(ld.SCALES["atom"]), math.log10(ld.SCALES["Milky Way"])
    span = DoubleArrow(P3(x_of(pa), y - 1.05), P3(x_of(pg), y - 1.05), buff=0, stroke_width=2.5, color=C.steps,
                       tip_length=0.16)
    m2.play(GrowFromCenter(span), at=t31, dur=0.8)
    m2.play(FadeIn(ctex([(f"{round(ld.SCALE_SPAN)}", C.steps), (r"\ \text{powers of ten}", None)], 36)
                   .move_to(P3((x_of(pa) + x_of(pg)) / 2, y - 1.45))), at=t31 + 0.4, dur=0.6)
    s.add(Solid(C.bg, z=50, opacity=Track(lambda t: ramp(t, end - 0.7, 0.6))))
