"""c05_s02 · The sieve (equation). Storyboard: plan/scene_plan.md § c05_s02. Layout L2; frame 07 for the epicycles.

The transform writes in the right column, its parts tagged 'signal', 'test wave', 'total'. On the stage: the chord
(the same windowed C + E + G as c05_s01), a test wave whose frequency sweeps, and their product, its area shaded
above and below zero. The column's spectrum is |∫ f(t) e^{−iωt} dt| computed at each frequency the sweep has passed
(ch5.transform), so it rises into three spikes at C, E and G. On 'drawing' the stage turns into epicycles: 90
circles (the largest Fourier terms of a π outline) whose tip draws π, the column showing their sizes by frequency.
"""
import numpy as np
from aion import *

import ch5
import sims as sm
from beats import T
from kit import chapter_backdrop, COL, P3, RC, X1, add_rail, fit, glow, mix, polyline, sans, smooth01, tag_under

XA, XB = -6.2, 1.8
ROWS = {"sig": 1.75, "test": 0.15, "prod": -1.45}
AMP = 0.32
SX0, SX1, SY0, SH = COL[0] + 0.15, COL[1], -1.35, 1.75        # the spectrum box in the column
F0, F1 = 200.0, 450.0
C0 = np.array([-2.2, -0.1])                       # the π's centre


def omega(t):
    """The test frequency (Hz) over time: sweeps up, waits on E as the narration says 'matches', sweeps on."""
    a, b = float(T.c05_s02_tests), float(T.c05_s02_matches)
    c, d = b + 1.2, float(T.c05_s02_list) - 0.3
    if t < a:
        return F0
    if t < b - 0.3:
        return F0 + (ch5.NOTES[1] - F0) * (t - a) / (b - 0.3 - a)
    if t < c:
        return ch5.NOTES[1]
    return min(ch5.NOTES[1] + (F1 - ch5.NOTES[1]) * (t - c) / (d - c), F1)


def _sx(f):
    return SX0 + (SX1 - SX0) * (f - F0) / (F1 - F0)


@scene(T.c05_s02, T.c05_s03)
def s17_c05_sieve(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 5)
    add_rail(s, 5)
    t0 = float(s.start)
    t_r, t_te, t_ma, t_li, t_dr, t_ci = (T.c05_s02_reverse, T.c05_s02_tests, T.c05_s02_matches, T.c05_s02_list,
                                         T.c05_s02_drawing, T.c05_s02_circles)
    hud = s.manim(z=50, parallax=0.0)

    # c05_s01's last frame: the square wave from 13 sines, and its sum, fading
    xs = np.linspace(-6.0, 6.0, 1200)
    ph = (xs + 6.0) / 12.0 * 2.5 * 2 * np.pi + np.pi / 2
    op_c = fade(t0 - 5, dur=0.1, out=t0 + 0.1, out_dur=0.7)
    glow(s, C.fourier, z=6, k=0.5, opacity=op_c).add(polyline(list(zip(xs, 0.2 + 0.9 * ch5.square_sum(ph, 13))),
                                                              C.fourier, 3.2))
    old = s.manim(z=7, opacity=op_c, parallax=0.0)
    old.add(polyline(list(zip(xs, 0.2 + 0.9 * np.sign(np.sin(ph)))), C.ghost, 1.4),
            sans("13 sines", 24, C.muted).move_to(P3(0, -1.6)),
            Eqn(r"f(t)=\sum_k a_k\sin(k\omega t)", colors={"f(t)": C.fourier}).scale(0.8)
            .move_to(P3(X1, 2.55), aligned_edge=RIGHT))

    # the transform, tagged
    Ft, ft, ex, it = r"F(\omega)", r"f(t)", r"e^{-i\omega t}", r"\int"
    e = Eqn(r"F(\omega)=\int f(t)\,e^{-i\omega t}\,dt", colors={Ft: C.fourier, ft: C.fourier, ex: C.data, it: C.text})
    fit(e.scale(0.85)).move_to(P3(RC, 2.45))
    tags = VGroup(tag_under(e, ft, "signal", C.fourier), tag_under(e, ex, "test wave", C.data),
                  tag_under(e, Ft, "total", C.fourier))
    hud.play(Write(e), at=t_r - 0.1, dur=1.2)
    hud.play(FadeIn(tags[0], shift=0.06 * UP), at=t_r + 0.9, dur=0.5)
    hud.play(FadeIn(tags[1], shift=0.06 * UP), at=t_te + 0.2, dur=0.5)
    hud.play(FadeIn(tags[2], shift=0.06 * UP), at=t_ma + 0.3, dur=0.5)

    # stage: signal, test wave, product
    X = np.linspace(XA, XB, 800)
    tt = (X - XA) / (XB - XA) * ch5.WIN
    sig = ch5.chord(tt)
    st_op = fade(t0 + 0.8, dur=0.8, out=t_dr - 0.7, out_dur=0.5)
    lab_op = fade(t_te, dur=0.6, out=t_dr - 0.7, out_dur=0.5)
    m = s.manim(z=8)
    rl = VGroup(sans("signal", 22, C.fourier).move_to(P3(XA, ROWS["sig"] + 0.62), aligned_edge=LEFT),
                sans("test wave", 22, C.data).move_to(P3(XA, ROWS["test"] + 0.55), aligned_edge=LEFT),
                sans("signal × test", 22, C.muted).move_to(P3(XA, ROWS["prod"] + 0.62), aligned_edge=LEFT))
    m.play(FadeIn(rl[0]), at=t0 + 1.0, dur=0.5)
    m.play(FadeIn(rl[1:]), at=t_te, dur=0.5)
    m.play(FadeOut(rl), at=t_dr - 0.7, dur=0.5)
    glow(s, C.fourier, z=5, k=0.35).redraw(
        lambda t: polyline(list(zip(X, ROWS["sig"] + AMP * sig)), C.fourier, 2.6, float(st_op(t))),
        during=(t0, t_dr))

    def test_prod(t):
        a = float(lab_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        w = omega(t)
        test = np.cos(2 * np.pi * w * tt)
        g.add(polyline(list(zip(X, ROWS["test"] + 0.45 * test)), C.data, 2.0, a))
        p = sig * test
        y0 = ROWS["prod"]
        g.add(Line(P3(XA, y0), P3(XB, y0), stroke_color=C.ghost, stroke_width=1, stroke_opacity=a))
        for sgn, col, fo in ((1, C.fourier, 0.45), (-1, C.data, 0.22)):
            q = np.clip(sgn * p, 0, None) * sgn
            pts = [P3(XA, y0)] + [P3(x, y0 + 0.42 * v) for x, v in zip(X[::2], q[::2])] + [P3(XB, y0)]
            g.add(Polygon(*pts, stroke_width=0, fill_color=col, fill_opacity=fo * a))
        return g
    s.manim(z=6).redraw(test_prod, during=(t_te - 0.2, t_dr))

    # the column: the spectrum, built as the sweep passes each frequency
    fgrid = np.linspace(F0, F1, 500)
    spec = ch5.transform(fgrid)
    sp_op = fade(t_te, dur=0.6, out=t_dr - 0.4, out_dur=0.5)
    axis = VGroup(Line(P3(SX0, SY0), P3(SX1, SY0), stroke_color=C.muted, stroke_width=1.2),
                  sans("frequency", 20, C.muted).move_to(P3(SX1, SY0 - 0.5), aligned_edge=UR))
    hud.play(FadeIn(axis), at=t_te, dur=0.5)

    def spectrum(t):
        a = float(sp_op(t))
        g = VGroup()
        k = int(np.searchsorted(fgrid, omega(t)))
        if a < 0.01 or k < 2:
            return g
        g.add(polyline([(_sx(f), SY0 + SH * v) for f, v in zip(fgrid[:k], spec[:k])], C.fourier, 3.0, a))
        v = float(ch5.transform(np.array([omega(t)]))[0])
        if t < float(t_li):
            g.add(Dot(P3(_sx(omega(t)), SY0 + SH * v), radius=0.05, color=C.light, fill_opacity=a))
        return g
    glow(s, C.fourier, z=52, k=0.5, parallax=0.0).redraw(spectrum, during=(t_te - 0.2, t_dr))
    notes = VGroup(*[sans(n, 22, C.fourier).move_to(P3(_sx(f), SY0 - 0.25)) for n, f in zip("CEG", ch5.NOTES)])
    hud.play(FadeIn(notes, lag_ratio=0.25), at=t_li + 0.1, dur=0.8)
    hud.play(FadeOut(notes), at=t_dr - 0.4, dur=0.5)

    # a drawing, rebuilt from circles (frame 07)
    fr, co = ch5.pi_terms()
    t_go, period = float(t_dr) - 0.1, 4.2
    phase = lambda t: float(np.clip((t - t_go) / period, 0, 1))
    full = ch5.pi_trace(1.0)
    ep_op = fade(t_dr - 0.3, dur=0.6)
    s.manim(z=2, opacity=ep_op).add(polyline([(C0[0] + z.real, C0[1] + z.imag) for z in full], C.ghost, 1.4))

    def chain(t):
        a = float(ep_op(t))
        joints = sm.epicycles(fr, co, phase(t))
        g = VGroup()
        for i in range(1, 34):
            p0, p1 = joints[i - 1], joints[i]
            r = abs(co[i - 1])
            if r > 0.02:
                g.add(Circle(radius=r, stroke_color=C.muted, stroke_width=1.0, stroke_opacity=0.55 * a)
                      .move_to(P3(C0[0] + p0.real, C0[1] + p0.imag)))
            g.add(Line(P3(C0[0] + p0.real, C0[1] + p0.imag), P3(C0[0] + p1.real, C0[1] + p1.imag),
                       stroke_color=mix(C.fourier, C.light, 0.35), stroke_width=1.8, stroke_opacity=a))
        tip = joints[-1]
        g.add(Dot(P3(C0[0] + tip.real, C0[1] + tip.imag), radius=0.06, color=C.light, fill_opacity=a))
        return g
    s.manim(z=4).redraw(chain, during=(t_dr - 0.4, s.end))

    def drawn(t):
        z = ch5.pi_trace(phase(t))
        return polyline([(C0[0] + q.real, C0[1] + q.imag) for q in z], C.fourier, 4.4, float(ep_op(t)))
    glow(s, C.fourier, z=3, k=0.8).redraw(drawn, during=(t_dr - 0.2, s.end))

    # the column: the circles' sizes by frequency (bare stems)
    ks = np.arange(-18, 19)
    mags = np.array([np.abs(co[fr == k][0]) if (fr == k).any() else 0 for k in ks])
    stems = VGroup(*[Line(P3(SX0 + (SX1 - SX0) * (k + 18) / 36, SY0),
                          P3(SX0 + (SX1 - SX0) * (k + 18) / 36, SY0 + SH * v / mags.max()),
                          stroke_color=C.fourier, stroke_width=3.2) for k, v in zip(ks, mags)])
    hud.play(LaggedStart(*[Create(x) for x in stems], lag_ratio=0.04), at=t_dr + 0.2, dur=1.4)
    s.camera.frame(t_ci + 0.1, center=(C0[0] + 0.3, C0[1]), zoom=1.15, dur=2.2)
