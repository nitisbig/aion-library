"""s22 pill curve (ch6): each molecule makes its own random hop, but the crowd follows the exponential. The state dot
x(t) = e^{tA} x₀ curves through the plane from (1, 0) toward the origin, bulging up into the blood first; the blood
level b(t) draws below over 12 h (peak at 1.85 h, a tick, no number) with the shown molecules' blood fraction tracking
it. The eigenvalues −1 and −1/4 are the two rates: the rising flank (absorb) and the long tail (clear)."""
from aion import *

import ch6
from beats import T
from ch6 import BH, BO, BW, H_PEAK, HMAX, PO2, PU, b_level, hero, pill_field, pill_matrix, plane_axes, state
from shots import Molecules, backdrop, backed, compartments, finish, lab, live, p3, plot, poly, tex


def bx(h, b):
    return BO + [BW * h / HMAX, BH * b]


@scene(T.cut_curve, T.cut_earth)
def s22_pill_curve(s):
    backdrop(s)
    mf = s.manim(z=1)
    m = s.manim(z=3)
    body, ax, field, M, h_ = compartments(), plane_axes(), pill_field(), pill_matrix(), hero()
    m.add(body, ax, M, h_)
    mf.add(field)
    t0 = T.cut_curve + 0.3
    mol = Molecules(n=400, seed=11, t0=t0, sec_per_hour=ch6.SEC_PER_HOUR)
    out = keys((T.cut_earth - 0.5, 1.0), (T.cut_earth - 0.05, 0.0), lead=0)
    s.add(PointsLayer(mol.pos, color=C.vec, size=3.2, glow=0.0, alpha=out, additive=False, z=2, end=T.cut_earth))

    # ── the state dot curves through the plane ──
    def hours(t):
        return min(mol.hours(t), HMAX)

    def traj(t):
        h = hours(t)
        a = float(out(t))
        hs = np.linspace(0, max(h, 1e-3), 120)
        P = [PO2 + PU * state(x) for x in hs]
        return VGroup(poly(P, C.flow, C.stroke + 0.5, opacity=a), Dot(p3(P[-1]), radius=0.11, color=C.vec).set_opacity(a))
    live(m, traj, (t0, T.cut_earth))
    m.play(FadeOut(M), at=T.cut_curve + 0.2, dur=0.5)
    m.play(h_.animate.scale(0.8).move_to([4.65, 2.9, 0]), at=T.cut_curve + 0.3, dur=0.7)

    # ── the blood level b(t), and the molecule count tracking it ──
    axes = VGroup(Line(p3(BO), p3(BO + [BW, 0]), color=C.muted, stroke_width=C.thin),
                  Line(p3(BO), p3(BO + [0, BH * 0.75]), color=C.muted, stroke_width=C.thin),
                  lab("hours", 22, C.muted).move_to(p3(BO + [BW / 2, -0.3])),
                  lab("blood", 22, C.flow).move_to(p3(BO + [0.45, BH * 0.75 + 0.2])))
    m.play(FadeIn(axes), at=T.cut_curve + 0.2, dur=0.5)
    hk = np.linspace(0, HMAX, 97)
    frac = np.array([mol.counts(t0 + x * ch6.SEC_PER_HOUR + 1e-6)[1] / 400 for x in hk])

    def curves(t):
        h = hours(t)
        a = float(out(t))
        g = VGroup()
        if h > 0.05:
            g.add(plot(b_level, 0, h, BO, BW / HMAX, BH, C.flow, width=C.stroke + 0.5, opacity=a))
            k = int(np.searchsorted(hk, h))
            if k > 1:
                g.add(poly([bx(x, f) for x, f in zip(hk[:k], frac[:k])], C.vec, C.thin + 0.4, opacity=0.8 * a))
        return g
    live(m, curves, (t0, T.cut_earth))
    peak = Line(p3(bx(H_PEAK, 0) + [0, -0.1]), p3(bx(H_PEAK, b_level(H_PEAK)) + [0, 0.25]), color=C.muted,
                stroke_width=C.thin)
    m.play(Create(peak), at=T.climbs + 1.0, dur=0.5)
    lg = VGroup(VGroup(Line(ORIGIN, 0.4 * RIGHT, color=C.flow, stroke_width=C.stroke), lab(r"$e^{tA}$ level", 20, C.flow)
                       ).arrange(RIGHT, buff=0.1),
                VGroup(Line(ORIGIN, 0.4 * RIGHT, color=C.vec, stroke_width=C.thin + 0.4), lab("molecules", 20, C.vec)
                       ).arrange(RIGHT, buff=0.1)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    lg.move_to(p3(BO + [BW - 0.9, BH * 0.68]))
    m.play(FadeIn(lg), at=T.crowd + 0.3, dur=0.5)

    # ── the two eigenvalues are the two rates ──
    lam = tex(r"\lambda", "=", r"-1", ",", r"\;-\tfrac14", size=48, colors={0: C.eigen, 2: C.eigen, 4: C.eigen})
    lam.move_to([4.65, 1.35, 0])
    m.play(FadeIn(lam, shift=0.1 * DOWN), at=T.eigen2 + 0.2, dur=0.6)
    rise = plot(b_level, 0, H_PEAK, BO, BW / HMAX, BH, C.eigen, width=C.stroke + 3)
    tail = plot(b_level, H_PEAK + 0.6, HMAX, BO, BW / HMAX, BH, C.eigen, width=C.stroke + 3)
    t_ab = backed(VGroup(tex("-1", size=32, color=C.eigen), lab("absorb", 22, C.eigen)).arrange(RIGHT, buff=0.1),
                  buff=0.04).move_to(p3(bx(3.6, 0.72)))
    t_cl = backed(VGroup(tex(r"-\tfrac14", size=32, color=C.eigen), lab("clear", 22, C.eigen)).arrange(RIGHT, buff=0.1),
                  buff=0.04).move_to(p3(bx(7.0, 0.42)))
    m.play(Create(rise), FadeIn(t_ab), Indicate(lam[2], color=C.eigen), at=T.absorb + 0.2, dur=0.7)
    m.play(Create(tail), FadeIn(t_cl), Indicate(lam[4], color=C.eigen), at=T.clear + 0.1, dur=0.8)
    m.play(FadeOut(VGroup(body, ax, h_, axes, peak, lg, lam, rise, tail, t_ab, t_cl)), at=T.cut_earth - 0.45, dur=0.5)
    mf.play(FadeOut(field), at=T.cut_earth - 0.45, dur=0.5)
    finish(s)
