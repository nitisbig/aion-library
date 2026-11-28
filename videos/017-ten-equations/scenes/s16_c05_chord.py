"""c05_s01 · A chord (hook). Storyboard: plan/scene_plan.md § c05_s01. Layout L1.

Opens on c04_s03's last frame (the probe's jagged trace over the swirls); the trace relaxes flat as the chapter card
shows. On 'Fourier' his hot bar returns from the opening: the exact cosine-series solution cooling (sims.heat_bar).
On 'piano' C, E and G added make one bumpy wave (ch5.chord); on 'three separate notes' it comes apart in depth into
its three sines, labelled with their pitches, and folds back. On 'adding together' a square wave builds from
1, 3, 5, … 25 sines (ch5.square_sum), one added at a time.
"""
import numpy as np
from aion import *

import ch4
import ch5
import sims as sm
from beats import T
from kit import P3, RC, X1, Y0, YH, add_rail, chapter_card, glow, mix, glimpse, polyline, sans, shade, smooth01, tex

XA, XB, YW = -6.0, 6.0, 0.2                      # the wave stage
AMP = 0.55                                       # one note's height
SPLIT = (1.75, 0.0, -1.75)                       # where the three notes sit when apart
WAVES_X = np.linspace(XA, XB, 900)


def _ts():
    return (WAVES_X - XA) / (XB - XA) * ch5.WIN


def _carry(s):
    """c04_s03's last frame: the dimmed swirls, the probe, and its trace, which relaxes flat and fades."""
    t0 = float(s.start)
    t_tu, t_pu = float(T.c04_s03_turbulence), float(T.c04_s03_pull)
    op = fade(t0 - 5, dur=0.1, out=t0 + 0.2, out_dur=0.9)
    s.add(FramesLayer(ch4.turb_frames(lambda t: 0.35 * float(op(t)), t_tu), height=2 * YH, pos=(0, 0), z=-5,
                      parallax=0.0, during=[(s.start, t0 + 1.2)]))
    y_tr, x_a, x_b = ch4.TRACE
    ts, vals = ch4.probe_trace(t_tu, t_pu, t0 - 0.4)
    xs = x_a + (x_b - x_a) * (ts - ts[0]) / (ts[-1] - ts[0])
    shade(s, 0.0, y_tr, 11.2, 1.3, a=0.85, z=6, parallax=0.0, opacity=op)
    calm = lambda t: 1 - float(smooth01((t - t0 - 0.1) / 1.4))
    t_op = fade(t0 - 5, dur=0.1, out=t0 + 1.4, out_dur=0.6)
    glow(s, C.navier, z=8, k=0.4, parallax=0.0).redraw(
        lambda t: polyline(list(zip(xs, y_tr + 0.5 * vals * calm(t))), C.navier, 2.4, float(t_op(t))),
        during=(s.start, t0 + 2.1))
    hm = s.manim(z=9, parallax=0.0, opacity=op)
    hm.add(sans("one point, over time", 22, C.muted).move_to(P3(x_a + 1.25, y_tr + 0.82)),
           Line(P3(x_a, y_tr), P3(x_b, y_tr), stroke_color=C.ghost, stroke_width=1.2))
    glow(s, C.light, z=9, k=1.2, parallax=0.0, opacity=op).add(Dot(P3(*ch4.PROBE), radius=0.07, color=C.light))


def _bar(t, t_on, op):
    """Fourier's hot bar cooling: the exact solution u(x, t) of the heat equation (cosine series)."""
    a = float(op(t))
    g = VGroup()
    if a < 0.01:
        return g
    xs = np.linspace(0, 1, 160)
    th = 0.0005 + 0.006 * max(t - t_on, 0.0)
    u, _ = sm.heat_bar(xs, th, n_modes=40)
    u0, _ = sm.heat_bar(xs, 0.0005, n_modes=40)
    un = u / u0.max()
    bx0, bx1, by, bh = -4.6, 4.6, -0.55, 0.42
    seg = (bx1 - bx0) / len(xs)
    for x, v in zip(xs, un):
        g.add(Rectangle(width=seg * 1.05, height=bh, stroke_width=0, fill_color=ch5.heat_ramp(v, C.fourier, C.light),
                        fill_opacity=a).move_to(P3(bx0 + (bx1 - bx0) * x, by)))
    for yy in (by - bh / 2, by + bh / 2):
        g.add(Line(P3(bx0, yy), P3(bx1, yy), stroke_color=C.ghost, stroke_width=1.2, stroke_opacity=a))
    g.add(polyline([(bx0 + (bx1 - bx0) * x, 0.0 + 1.6 * v) for x, v in zip(xs, un)], C.fourier, 3.5, a))
    return g


@scene(T.c05_s01, T.c05_s02)
def s16_c05_chord(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_f, t_p, t_n, t_a = T.c05_s01_fourier, T.c05_s01_piano, T.c05_s01_three_separate_notes, T.c05_s01_adding_together
    _carry(s)
    chapter_card(s, 5, at=t0 + 1.4, out=t_f - 0.2)
    add_rail(s, 5, opacity=fade(t0 + 0.7, dur=0.8))
    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "fourier", t_f, C.fourier)

    # his bar of hot metal, cooling
    b_op = fade(t_f - 0.1, dur=0.6, out=t_p - 0.7, out_dur=0.5)
    s.manim(z=3).redraw(lambda t: _bar(t, float(t_f), b_op), during=(t_f - 0.2, t_p))
    m = s.manim(z=10)
    hb = sans("a hot bar, cooling", 24, C.muted).move_to(P3(0, -1.2))
    m.play(FadeIn(hb), at=t_f + 0.5, dur=0.5)
    m.play(FadeOut(hb), at=t_p - 0.7, dur=0.5)

    # the chord, its three notes apart in depth, and back
    ts = _ts()
    parts = [ch5.chord(ts, (i,)) for i in range(3)]
    total = ch5.chord(ts)
    cols = [mix(C.fourier, C.light, k) for k in (0.0, 0.3, 0.6)]
    t_pf = float(t_p)

    def split(t):
        up = float(smooth01((t - float(t_n) + 0.2) / 1.0))
        down = float(smooth01((t - float(t_a) + 1.6) / 1.0))
        return up * (1 - down)

    def chord_draw(t):
        k = int(len(ts) * float(smooth01((t - t_pf + 0.1) / 1.6)))
        g = VGroup()
        if k < 2:
            return g
        u = split(t)
        out = 1 - float(smooth01((t - float(t_a) + 0.45) / 0.4))
        if u < 0.999:
            g.add(polyline(list(zip(WAVES_X[:k], YW + AMP * total[:k])), C.fourier, 3.2, (1 - u) * out))
        if u > 0.001:
            for i, (p, c) in enumerate(zip(parts, cols)):
                dx, sc = 0.35 * i * u, 1 - 0.07 * i * u                    # back layers sit up-right, a little smaller
                y0 = YW + SPLIT[i] * u
                g.add(polyline(list(zip(WAVES_X[:k] * sc + dx, y0 + AMP * p[:k] * sc)), c, 2.8, u * (1 - 0.15 * i)))
        return g
    glow(s, C.fourier, z=5, k=0.5).redraw(chord_draw, during=(t_p - 0.2, t_a + 0.2))
    labs = VGroup(*[sans(f"{n}  {f:.1f} Hz", 22, C.muted).move_to(P3(XB + 0.3, YW + SPLIT[i] + 0.62),
                                                                       aligned_edge=RIGHT)
                    for i, (n, f) in enumerate(zip("CEG", ch5.NOTES))])
    m.play(FadeIn(labs, lag_ratio=0.2), at=t_n + 0.7, dur=0.8)
    m.play(FadeOut(labs), at=t_a - 1.7, dur=0.5)
    one = sans("one sound wave", 24, C.muted).move_to(P3(0, -1.6))
    m.play(FadeIn(one), at=t_p + 1.4, dur=0.5)
    m.play(FadeOut(one), at=t_n - 0.3, dur=0.4)

    # adding together: a square wave from odd sines
    xs = np.linspace(XA, XB, 1200)
    ph = (xs - XA) / (XB - XA) * 2.5 * 2 * np.pi + np.pi / 2
    t_s = float(t_a) - 0.1
    n_of = lambda t: int(np.clip(1 + (t - t_s) / 0.17, 0, 13))

    def squares(t):
        n = n_of(t)
        g = VGroup()
        if n < 1:
            return g
        a = float(smooth01((t - t_s) / 0.3))
        g.add(polyline(list(zip(xs, YW + 0.9 * ch5.square_sum(ph, n))), C.fourier, 3.2, a))
        return g
    ghost = polyline(list(zip(xs, YW + 0.9 * np.sign(np.sin(ph)))), C.ghost, 1.4)
    m.play(FadeIn(ghost), at=t_a - 0.2, dur=0.5)
    glow(s, C.fourier, z=6, k=0.5).redraw(squares, during=(t_a - 0.2, s.end))
    cnt = s.manim(z=10)
    cnt.redraw(lambda t: sans(f"{n_of(t)} sine{'s' if n_of(t) > 1 else ''}", 24, C.muted)
               .move_to(P3(0, -1.6)).set_opacity(float(smooth01((t - t_s) / 0.3))), during=(t_a - 0.1, s.end))
    e = Eqn(r"f(t)=\sum_k a_k\sin(k\omega t)", colors={"f(t)": C.fourier}).scale(0.8)
    e.move_to(P3(X1, 2.55), aligned_edge=RIGHT)
    hud.play(FadeIn(e, shift=0.06 * UP), at=t_a + 0.1, dur=0.6)
