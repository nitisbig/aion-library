"""c03_s02 · The wave (equation). Storyboard: plan/scene_plan.md § c03_s02. Composition: design frame 05.

ψ across the frame as a helix: height and depth are its real and imaginary parts, colour its phase (an even-
lightness hue wheel, legend bottom right). It is the split-step solution of Schrödinger's equation for a packet
meeting a barrier whose height is above the packet's energy (ch3._psi_table; same physics as sims.schrodinger_1d).
The equation writes top right; 'change' and 'energy' tag its two sides. On 'tall' |ψ|² fills below as the chance of
finding the electron. On 'wall' the barrier shows; most of the wave reflects and a small part comes through, which
glows, with its share of the probability computed from the solution.
"""
import math

import numpy as np
from aion import *

import ch3
from beats import T
from kit import chapter_backdrop, P3, RC, X1, Y0, add_rail, glow, glimpse, sans, tag_under

XA, XB, YAX, YB = ch3.XA, ch3.XB, ch3.YAX, ch3.YB
_X, K2 = ch3.wave_x, ch3.K2


def tau(t):
    """Scene time → sim time: at rest, drifting, then sped up through the barrier so it lands on 'tunnelling'."""
    t0, t1, t2 = 280.0, float(T.c03_s02_changes), float(T.c03_s02_wall) - 0.2
    if t < t0:
        return 0.0
    if t < t1:
        return 0.6 * (t - t0) / (t1 - t0)
    if t < t2:
        return 0.6 + 0.62 * (t - t1)
    return min(0.6 + 0.62 * (t2 - t1) + 1.85 * (t - t2), 15.0)


def _helix(t, part):
    return ch3.helix(tau(t), part)


def _prob(t, op):
    return ch3.prob(tau(t), op)


@scene(T.c03_s02, T.c03_s03)
def s11_c03_wave(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 3)
    add_rail(s, 3)
    t_s, t_ch, t_en, t_tall, t_wall, t_tun = (T.c03_s02_schr_dinger, T.c03_s02_changes, T.c03_s02_energy,
                                              T.c03_s02_tall, T.c03_s02_wall, T.c03_s02_tunnelling)
    op = fade(s.start + 0.1, dur=0.8)
    m = s.manim(z=5)
    m.add(Line(P3(XA, YAX), P3(XB, YAX), stroke_color=C.ghost, stroke_width=1.2))
    s.manim(z=6, opacity=op).redraw(lambda t: _helix(t, 0), during=(s.start, s.end))
    glow(s, C.schrod, z=7, k=0.4).redraw(lambda t: _helix(t, 1), during=(s.start, s.end))

    # the equation, its two sides tagged in words
    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "schrodinger", t_s, C.schrod, at_xy=(RC, 0.75))   # the open column, under the equation
    e = Eqn(r"i\hbar\,\partial_t\psi=\hat H\psi", colors={r"\psi": C.schrod, r"\partial_t": C.text, r"\hat H": C.text})
    e.scale(0.85).move_to(P3(RC + 0.6, 2.7))
    tc, tn = tag_under(e, r"\partial_t", "change", C.schrod), tag_under(e, r"\hat H", "energy", C.schrod)
    m.play(Write(e), at=t_s + 0.4, dur=1.2)
    m.play(e.part(r"\partial_t").animate.set_color(C.schrod), at=t_ch, dur=0.4)
    m.play(FadeIn(tc, shift=0.06 * UP), at=t_ch + 0.1, dur=0.5)
    m.play(e.part(r"\hat H").animate.set_color(C.schrod), at=t_en, dur=0.4)
    m.play(FadeIn(tn, shift=0.06 * UP), at=t_en + 0.1, dur=0.5)

    # phase legend
    wheel = VGroup(*[Line(P3(0, 0), P3(0.26 * math.cos(a), 0.26 * math.sin(a)), stroke_width=4,
                          stroke_color=ch3.phase_color(a)) for a in np.linspace(0, 2 * np.pi, 48, endpoint=False)])
    leg = VGroup(wheel, sans("phase", 22, C.muted)).arrange(RIGHT, buff=0.18).move_to(P3(X1, Y0 + 0.2),
                                                                                      aligned_edge=RIGHT)
    m.play(FadeIn(leg), at=s.start + 1.0, dur=0.8)

    # tall: the chance of finding it, |ψ|²
    p_op = fade(t_tall - 0.2, dur=0.8)
    s.manim(z=4).redraw(lambda t: _prob(t, float(p_op(t))), during=(t_tall - 0.4, s.end))
    m.add(Line(P3(XA, YB), P3(XB, YB), stroke_color=C.ghost, stroke_width=1.2))
    p = Eqn(r"P=|\psi|^2", colors={r"\psi": C.schrod}).scale(0.8)
    pg = VGroup(p, sans("chance", 22, C.schrod)).arrange(DOWN, buff=0.12).move_to(P3(5.55, -0.75))
    m.play(FadeIn(pg, shift=0.08 * UP), at=t_tall + 0.2, dur=0.6)

    # wall: the barrier rises; a small part comes through
    wall_w = (XB - XA) * 1.4 / (ch3.WIN[1] - ch3.WIN[0])
    slab = Rectangle(width=wall_w, height=4.75, stroke_width=0, fill_color=C.muted, fill_opacity=0.12) \
        .move_to(P3(_X(0), -0.4))
    m.play(GrowFromEdge(slab, DOWN), at=t_wall, dur=0.7)
    m.play(FadeIn(sans("wall", 22, C.muted).move_to(P3(_X(0), 2.6))), at=t_wall + 0.3, dur=0.5)
    x, psi = ch3.psi_at(15.0)
    p2 = np.abs(psi) ** 2
    tr = x > 0.8
    frac = float(np.trapezoid(p2[tr], x[tr]))
    pct = sans(f"{frac * 100:.0f}%", 28, C.schrod)
    pct_op = fade(t_tun + 0.3, dur=0.6)

    def pct_at(t):
        xs, ps = ch3.psi_at(tau(t))
        q = np.abs(ps) ** 2
        m_ = xs > 0.8
        xc = float(np.trapezoid(xs[m_] * q[m_], xs[m_]) / max(np.trapezoid(q[m_], xs[m_]), 1e-9))
        return pct.copy().set_opacity(float(pct_op(t))).move_to(P3(_X(xc), YB + K2 * q[m_].max() + 0.3))
    s.manim(z=8).redraw(pct_at, during=(t_tun, s.end))
