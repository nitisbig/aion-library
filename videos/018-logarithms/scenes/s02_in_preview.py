"""in_s02 · Preview (promise). Storyboard: plan/scene_plan.md § in_s02.

The word log (written at the end of in_s01) holds, then parks faint in the top-left. Six short pictures follow, each
crossfaded through black on its cue word and each the real thing the chapter will build: the staircase climbing to
1024, two boxwood rulers sliding to 2 × 3 = 6, 2ˣ flipping about y = x into log₂ x, the area under 1/x growing until it
reads exactly 1 at e, sound rings beside a decibel ruler, and an atom and a galaxy on one ruler of powers of ten.
"""
import math

import numpy as np
from aion import *

import logdata as ld
from beats import T
from kit import (P3, X0, Y1, caps, ctex, feather, glow, log_mark, log_scale_marks, mirror_point, plane, polyline, ramp,
                 sans, staircase, tex, tint, wood_body, lin_rgb)


SLIDE = 15.5                       # one picture's width on the strip (a little more than the frame)


def _dx(a, b):
    """x offset of a picture on the strip: it slides in from the right on cue a and out to the left on cue b."""
    a, b = float(a), float(b)
    return lambda t: SLIDE * (1 - ramp(t, a - 0.45, 0.8)) - SLIDE * ramp(t, b - 0.35, 0.8)


def _win(a, b):
    """Opacity for a picture on the strip: on while it is anywhere near the frame."""
    return fade(float(a) - 0.5, dur=0.15, out=float(b) + 0.45, out_dur=0.15)


def _at(a, b, x=0.0, y=0.0):
    """A layer position on the strip (for layers placed at (x, y))."""
    d = _dx(a, b)
    return Track(lambda t: (x + d(t), y))


def _lay(a, b):
    """Keyword arguments that put a Manim layer on the strip."""
    return dict(opacity=_win(a, b), pos=_at(a, b))


def _stairs(s, a, b):
    m = s.manim(z=5, **_lay(a, b))
    st = staircase(10, -4.9, -2.75, 0.8, 0.5, label_size=26)
    m.add(st.floor)
    m.play(Create(st.path), at=float(a) + 0.2, dur=1.7, ease="linear")
    m.play(LaggedStart(*[FadeIn(v, shift=0.08 * UP) for v in st.vals], lag_ratio=0.5), at=float(a) + 0.2, dur=1.7,
           lead=0.0)
    m.play(LaggedStart(*[FadeIn(v) for v in st.tags], lag_ratio=0.5), at=float(a) + 0.3, dur=1.6, lead=0.0)
    m.play(FadeIn(st.axis), at=float(a) + 1.4, dur=0.5)
    m.add(ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 56).move_to(P3(4.7, -1.2)))


def _rulers(s, a, b):
    L, xl, bh = 10.2, -5.1, 0.85
    lo, up = -0.6, -0.6 + bh + 0.02
    off = L * ld.LOG10_2
    op = _win(a, b)
    slide = lambda t: off * ramp(t, float(a) + 0.15, 1.2)  # noqa: E731
    d = _dx(a, b)
    s.add(ArrayLayer(wood_body(L, bh)[0], height=bh, pos=_at(a, b, xl + L / 2, lo), z=-2, opacity=op))
    s.add(ArrayLayer(wood_body(L, bh, seed=1623)[0], height=bh, z=-2, opacity=op,
                     pos=Track(lambda t: (xl + L / 2 + slide(t) + d(t), up))))
    m = s.manim(z=4, **_lay(a, b))
    m.add(log_scale_marks(xl, L, lo + bh / 2, up=False, label_size=24))
    top = log_scale_marks(xl, L, up - bh / 2, up=True, label_size=24)
    m.add(top)
    c0 = top.get_center()
    m.drive(top, lambda g, t: g.move_to(c0 + RIGHT * slide(t)), during=(float(a) - 0.1, float(b)))
    xc = xl + L * math.log10(6)
    t_hit = float(a) + 1.55
    cur = glow(s, C.ruler, z=5, k=0.7, **_lay(a, b))
    cur.play(FadeIn(Line(P3(xc, up + bh / 2 + 0.2), P3(xc, lo - bh / 2 - 0.2), stroke_color=C.ruler,
                         stroke_width=1.8)), at=t_hit, dur=0.35)
    m.play(FadeIn(tex("3", 44, C.value).move_to(P3(xc + 0.3, up + bh / 2 + 0.36)), scale=1.3),
           FadeIn(tex("6", 44, C.value).move_to(P3(xc + 0.3, lo - bh / 2 - 0.36)), scale=1.3), at=t_hit + 0.15,
           dur=0.4)
    m.add(ctex([("2", C.value), (r"\times", None), ("3", C.value), ("=", None), ("6", C.value)], 50)
          .move_to(P3(0, 2.6)))


def _mirror(s, a, b):
    ox, oy, u = -1.6, -2.75, 0.6
    m = s.manim(z=3, **_lay(a, b))
    g, X, Y = plane(ox, oy, u, (-0.6, 9.2), (-0.6, 9.2))
    m.add(g, DashedLine(P3(X(-0.5), Y(-0.5)), P3(X(9.1), Y(9.1)), stroke_color=C.muted, stroke_width=2,
                        dash_length=0.1))
    xs = np.linspace(-0.6, math.log2(9.15), 160)
    m.add(polyline([(X(x), Y(2 ** x)) for x in xs], C.value, 4))
    t0 = float(a) + 0.5
    th = lambda t: math.pi * ramp(t, t0, 2.0)  # noqa: E731

    def flip(t):
        q = th(t)
        pts = [mirror_point(x, 2 ** x, q) for x in xs]
        col = C.value if q < math.pi / 2 else C.steps
        return polyline([(X(x), Y(y)) for x, y in pts], col, 4, opacity=0.55 + 0.45 * abs(math.cos(q)))
    m.redraw(flip, during=(t0 - 0.2, float(b)))
    m.play(FadeIn(tex("y=2^x", 34, C.value).move_to(P3(X(1.1), Y(6.6)))), at=float(a) + 0.1, dur=0.4)
    m.play(FadeIn(tex(r"y=\log_2 x", 34, C.steps).move_to(P3(X(6.6), Y(1.5)))), at=t0 + 2.0, dur=0.5)


def _area(s, a, e_at, b):
    ox, oy, u = -5.2, -2.5, 1.2
    m = s.manim(z=3, **_lay(a, b))
    g, X, Y = plane(ox, oy, u, (-0.3, 5.3), (-0.2, 3.7))
    m.add(g)
    for i in range(1, 6):
        m.add(tex(str(i), 22, C.muted).next_to(P3(X(i), oy), DOWN, buff=0.08))
    xh = np.linspace(0.28, 5.3, 260)
    m.add(polyline([(X(x), Y(1 / x)) for x in xh], C.text, 3.5))
    m.add(tex(r"y=\frac1x", 34, C.text).move_to(P3(X(1.4), Y(2.6))))
    E = ld.E_FROM_AREA
    edge = lambda t: 1 + (E - 1) * ramp(t, float(a) + 0.2, float(e_at) - float(a) - 0.2)  # noqa: E731

    def region(t):
        x1 = edge(t)
        if x1 < 1.005:
            return VGroup()
        xs = np.linspace(1, x1, 80)
        return Polygon(*[P3(X(x), Y(1 / x)) for x in xs], P3(X(x1), Y(0)), P3(X(1), Y(0)), stroke_width=0,
                       fill_color=C.area, fill_opacity=0.32)
    m.redraw(region, during=(float(a), float(b)))
    gl = glow(s, C.natural, z=4, k=1.0, **_lay(a, b))
    gl.redraw(lambda t: Line(P3(X(edge(t)), Y(0)), P3(X(edge(t)), Y(1 / edge(t))), stroke_color=C.natural,
                             stroke_width=3), during=(float(a), float(b)))
    m.redraw(lambda t: ctex([(r"\text{area}=", C.muted), (f"{ld.area(1, edge(t)):.3f}", C.steps)], 40)
             .move_to(P3(1.75, 1.0), aligned_edge=LEFT), during=(float(a), float(b)))
    m.play(FadeIn(ctex([("e", C.natural), (r"\approx 2.71828", None)], 52).move_to(P3(1.75, -0.2), aligned_edge=LEFT),
                  shift=0.1 * UP), at=e_at, dur=0.5)
    gl.play(FadeIn(Dot(P3(X(E), Y(0)), radius=0.09, color=C.natural), scale=1.6), at=e_at, dur=0.4)
    m.play(FadeIn(tex("e", 40, C.natural).move_to(P3(X(E), Y(0) - 0.62))), at=e_at, dur=0.4)


def _rings_frame(a):
    w, h = 720, 540
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot(xx - 0.5 * w, yy - 0.5 * h) / h
    col = lin_rgb(C.sound)
    env = np.exp(-r * 1.8) * np.clip((r - 0.012) / 0.03, 0, 1)

    def frame(t):
        k = min(max((t - float(a) - 0.3) / 0.45, 0.0), 6.0)       # loudness climbs one 10 dB step per 0.45 s
        gain = 0.35 + 0.11 * k
        wave = 0.5 + 0.5 * np.cos(2 * math.pi * (r * 9.0 - 0.9 * (t - float(a))))
        I = (wave ** 6) * env * gain * 1.6
        lin = I[..., None] * col + np.exp(-r * 30)[..., None] * col
        srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
        al = np.clip(I * 1.6 + np.exp(-r * 30), 0, 1)
        return feather(np.dstack([np.clip(srgb * 255, 0, 255), al * 255]).astype(np.uint8), 0.1, 0.1, 0.1, 0.1)
    return frame


def _sound(s, a, b):
    s.add(FramesLayer(_rings_frame(a), height=7.6, pos=_at(a, b, -2.4, 0.0), z=-2, opacity=_win(a, b),
                      during=[(float(a) - 0.6, float(b) + 0.5)]))
    m = s.manim(z=4, **_lay(a, b))
    rx, y30, du = 3.6, -2.6, 0.075
    Yd = lambda d: y30 + (d - 30) * du  # noqa: E731
    m.add(Line(P3(rx, Yd(30)), P3(rx, Yd(100)), stroke_color=C.ruler, stroke_width=2.5))
    for d in range(30, 101, 10):
        m.add(Line(P3(rx - 0.14, Yd(d)), P3(rx, Yd(d)), stroke_color=C.ruler, stroke_width=2),
              tex(str(d), 24, C.ruler).next_to(P3(rx - 0.14, Yd(d)), LEFT, buff=0.1))
    m.add(tex(r"\mathrm{dB}", 26, C.muted).move_to(P3(rx - 0.4, Yd(100) + 0.4)))
    lvl = lambda t: 30 + 10 * math.floor(min(max((t - float(a) - 0.3) / 0.45, 0.0), 6.0))  # noqa: E731
    m.redraw(lambda t: VGroup(Dot(P3(rx, Yd(lvl(t))), radius=0.085, color=C.value),
                              Line(P3(rx, Yd(30)), P3(rx, Yd(lvl(t))), stroke_color=C.value, stroke_width=4)),
             during=(float(a) - 0.2, float(b)))


def _scales(s, a, b):
    """Powers of ten in metres, one equal step each, from an atom to a galaxy."""
    x_of = lambda p: -6.0 + (p + 10.5) * 0.375  # noqa: E731
    y = -0.9
    m = s.manim(z=4, **_lay(a, b))
    t0 = float(a) - 0.1
    run = 1.3
    reach = lambda p: t0 + run * (p + 10.5) / 32.0  # noqa: E731
    m.play(Create(Line(P3(x_of(-10.5), y), P3(x_of(21.5), y), stroke_color=C.ruler, stroke_width=2.5)), at=t0,
           dur=run, ease="linear", lead=0.0)
    for p in range(-10, 22):
        major = p % 5 == 0
        tick = Line(P3(x_of(p), y), P3(x_of(p), y - (0.22 if major else 0.12)), stroke_color=C.ruler,
                    stroke_width=2 if major else 1.3)
        anims = [FadeIn(tick)]
        if major:
            anims.append(FadeIn(tex(f"10^{{{p}}}", 24, C.steps).next_to(tick, DOWN, buff=0.1)))
        m.play(*anims, at=reach(p), dur=0.25, lead=0.0)
    m.add(sans("metres", 20, C.muted).move_to(P3(x_of(21.5), y - 0.75), aligned_edge=RIGHT))
    yo = y + 0.95
    atom = VGroup(Dot(P3(0, 0), radius=0.07, color=C.ruler),
                  *[Ellipse(width=0.9, height=0.3, stroke_color=C.ruler, stroke_width=1.5).rotate(k * PI / 3)
                    for k in range(3)])
    person = VGroup(Circle(radius=0.11, stroke_color=C.ruler, stroke_width=2).move_to(P3(0, 0.42)),
                    Line(P3(0, 0.31), P3(0, -0.12), stroke_color=C.ruler, stroke_width=2),
                    Line(P3(-0.2, 0.15), P3(0.2, 0.15), stroke_color=C.ruler, stroke_width=2),
                    Line(P3(0, -0.12), P3(-0.14, -0.45), stroke_color=C.ruler, stroke_width=2),
                    Line(P3(0, -0.12), P3(0.14, -0.45), stroke_color=C.ruler, stroke_width=2))
    earth = VGroup(Circle(radius=0.38, stroke_color=C.ruler, stroke_width=2),
                   Ellipse(width=0.76, height=0.24, stroke_color=tint(C.ruler, 0.5), stroke_width=1.2),
                   Line(P3(0, -0.38), P3(0, 0.38), stroke_color=tint(C.ruler, 0.5), stroke_width=1.2))
    rng = np.random.default_rng(1806)
    pts = []
    for arm in range(2):
        for i in range(90):
            th = 0.25 + i * 0.06
            rr = 0.06 * math.exp(0.22 * th * 1.6)
            ang = th + arm * PI
            pts.append((rr * math.cos(ang) + rng.normal(0, 0.025), 0.55 * rr * math.sin(ang) + rng.normal(0, 0.02)))
    galaxy = VGroup(*[Dot(P3(px, py), radius=0.018, color=C.star, fill_opacity=0.85) for px, py in pts],
                    Dot(P3(0, 0), radius=0.07, color=C.star))
    for obj, p, word in ((atom, math.log10(1.06e-10), "atom"), (person, math.log10(1.7), "person"),
                         (earth, math.log10(1.274e7), "Earth"), (galaxy, math.log10(9.5e20), "galaxy")):
        obj.move_to(P3(x_of(p), yo + 0.15))
        lbl = sans(word, 22, C.muted).move_to(P3(x_of(p), yo + 1.0))
        dot = Dot(P3(x_of(p), y), radius=0.06, color=C.value)
        m.play(FadeIn(obj, scale=0.8), FadeIn(lbl), FadeIn(dot), at=reach(p) + 0.1, dur=0.45, lead=0.0)


@scene(T.in_s02, T.in_s03)
def s02_in_preview(s):
    s.solid(C.bg, z=-200)
    hud = s.manim(z=60, parallax=0.0)
    mark = log_mark()
    hud.add(mark)

    # the title, under the word log, while "that idea turned out to be much larger" is said
    t0 = float(T.in_s02_that_idea)
    park = float(T.in_s02_how_many_times) - 1.4
    title = caps("What Logarithms Actually Are", 40, C.text).move_to(P3(0, -1.0))
    rule = Line(P3(-title.width / 2, -1.45), P3(title.width / 2, -1.45), stroke_color=tint(C.muted, 0.6),
                stroke_width=1.2)
    hud.play(FadeIn(title, shift=0.12 * UP), at=t0, dur=0.9)
    hud.play(Create(rule), at=t0 + 0.4, dur=0.9)
    hud.play(FadeOut(VGroup(title, rule), shift=0.12 * DOWN), at=park - 0.15, dur=0.6)
    hud.play(mark.animate.scale(0.42).move_to(P3(X0 + 0.45, Y1 - 0.35)).set_color(C.muted), at=park, dur=1.1)

    # what each picture shows, read as a sentence after the parked log
    cues = [T.in_s02_how_many_times, T.in_s02_ruler, T.in_s02_mirror_image, T.in_s02_area, T.in_s02_ears,
            T.in_s02_atom, float(T.in_s03) - 0.45]
    says = ["counts multiplications", "turns a ruler into a calculator", "mirrors exponential growth",
            "is an area, and gives e", "is how we hear", "spans atoms to galaxies"]
    for k, text in enumerate(says):
        a, b = float(cues[k]), float(cues[k + 1])
        cap = sans(text, 26, C.muted).move_to(P3(X0 + 1.05, Y1 - 0.38), aligned_edge=LEFT)
        hud.play(FadeIn(cap, shift=0.1 * LEFT), at=a + 0.15, dur=0.45)
        hud.play(FadeOut(cap, shift=0.1 * LEFT), at=b - 0.35, dur=0.35)
    _stairs(s, T.in_s02_how_many_times, T.in_s02_ruler)
    _rulers(s, T.in_s02_ruler, T.in_s02_mirror_image)
    _mirror(s, T.in_s02_mirror_image, T.in_s02_area)
    _area(s, T.in_s02_area, T.in_s02_number_e, T.in_s02_ears)
    _sound(s, T.in_s02_ears, T.in_s02_atom)
    _scales(s, T.in_s02_atom, float(T.in_s03) - 0.45)
    hud.play(FadeOut(mark), at=float(T.in_s03) - 0.3, dur=0.6)
