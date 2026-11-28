"""ch2_s02 · Hunting for the fraction.

The rolled wheel rises and grows; the number line sinks. A ghost fraction tick hovers near π. On 'Archimedes' regular
polygons with 6, 12, 24, 48 and 96 sides are drawn inside and outside the circle (his doubling), with a readout of
each one's perimeter over the diameter: the inner value climbs, the outer falls, π trapped between (lower third
'Archimedes · c. 250 BC'). Then the camera dives into the number line around π, ×10 at a time, the line relabelling
itself as it zooms: 223/71 and 22/7 land either side of π; on 'four eighty' the zoom goes on to ×10^6 and
355/113 lands a hair to the right (lower third 'Zu Chongzhi · c. 480'), with both decimals shown. At the deepest
zoom, the gap that remains between the tick and π is bracketed and tagged.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, P3, Digits, caps, sans, tex, the_circle, window, zline

X0, SC, YL = -5.0, 2.0, -1.0            # ch2_s01's number line
RW = SC / 2
BIG_C, BIG_R = P3(-3.3, 0.85), 1.85     # the circle for the polygons
Y2 = -2.4                               # where the number line sinks to
NS = (6, 12, 24, 48, 96)
FRACS = [(22, 7), (223, 71), (355, 113)]


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lower_third(name, x=2.15, y=3.3):
    g = VGroup(caps(name, 34, C.text), Line(ORIGIN, RIGHT * 3.6, stroke_color=C.muted, stroke_width=1.4))
    return g.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(x, y), aligned_edge=LEFT)


def polygon(n, r, outer, c):
    R = r / math.cos(math.pi / n) if outer else r
    pts = [c + R * P3(math.cos(math.pi / 2 + (2 * k + (1 if outer else 0)) * math.pi / n),
                      math.sin(math.pi / 2 + (2 * k + (1 if outer else 0)) * math.pi / n)) for k in range(n)]
    return Polygon(*pts, stroke_color=C.quantity, stroke_width=2.2 if not outer else 1.6,
                   stroke_opacity=1.0 if not outer else 0.7)


@scene(T.ch2_s02, T.ch2_s03)
def ch2_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top, hud = s.manim(z=0), s.manim(z=1), s.manim(z=3, parallax=0)
    t0 = float(s.start)
    t_fr, t_arc, t_22 = float(T.ch2_s02_fraction), float(T.ch2_s02_archimedes), float(T.ch2_s02_twenty_two_sevenths)
    t_480, t_355, t_gap = float(T.ch2_s02_four_eighty), float(T.ch2_s02_three_hundred), float(T.ch2_s02_gap)
    s.camera.base.update(x=1.2, y=0.0)
    s.camera.frame(t0 + 0.4, center=(0.0, 0.0), zoom=1.0, dur=1.6)

    # where ch2_s01 left off
    xp = X0 + math.pi * SC
    nl = VGroup(Line(P3(X0 - 0.7, YL), P3(X0 + 8.6, YL), stroke_color=C.muted, stroke_width=2.4))
    for k in range(5):
        nl.add(Line(P3(X0 + k * SC, YL - 0.14), P3(X0 + k * SC, YL + 0.14), stroke_color=C.muted, stroke_width=2.4),
               tex(str(k), 36, C.muted).move_to(P3(X0 + k * SC, YL - 0.5)))
    for k in range(1, 41):
        if k % 10:
            nl.add(Line(P3(X0 + k / 10 * SC, YL - 0.06), P3(X0 + k / 10 * SC, YL + 0.06), stroke_color=C.map_off,
                        stroke_width=1.4))
    seg = Line(P3(X0, YL), P3(xp, YL), stroke_color=C.quantity, stroke_width=6)
    cyc = VMobject(stroke_color=C.quantity, stroke_width=2.2, stroke_opacity=0.8).set_points_smoothly(
        [P3(X0 + a * RW - RW * math.sin(a), YL + RW - RW * math.cos(a)) for a in np.linspace(0, 2 * math.pi, 90)])
    wheel = the_circle(RW).move_to(P3(xp, YL + RW))
    spokes = VGroup(*(Line(P3(xp, YL + RW), P3(xp, YL + RW) + 0.85 * RW * P3(math.cos(a), math.sin(a)),
                           stroke_color=C.map_off, stroke_width=1.6)
                      for a in (math.pi / 2 + 2 * math.pi * k / 3 for k in range(3))))
    hubdot = Dot(P3(xp, YL + RW), radius=0.05, color=C.text)
    rimdot = Dot(P3(xp, YL), radius=0.085, color=C.quantity)
    tick = Line(P3(xp, YL - 0.26), P3(xp, YL + 0.26), stroke_color=C.quantity, stroke_width=4)
    pi_l = tex(r"\pi = 3.14159\ldots", 44, C.quantity).move_to(P3(xp, YL - 1.25))
    m.add(nl, seg, cyc, wheel, spokes, hubdot, rimdot, tick, pi_l)

    # the wheel rises and grows into the polygon circle; the line sinks
    m.play(FadeOut(VGroup(seg, cyc, spokes, hubdot, rimdot, pi_l)), at=t0 + 0.3, dur=0.7)
    m.play(wheel.animate.scale(BIG_R / RW).move_to(BIG_C), at=t0 + 0.6, dur=1.6, ease="easy_ease")
    m.play(VGroup(nl, tick).animate.shift(UP * (Y2 - YL)), at=t0 + 0.6, dur=1.6, ease="easy_ease")
    pi_mark = tex(r"\pi", 40, C.quantity).move_to(P3(xp, Y2 + 0.6))
    m.play(FadeIn(pi_mark, shift=0.1 * DOWN), at=t0 + 2.0, dur=0.5)

    # 'fraction': a ghost fraction hovers near π
    ghost = VGroup(DashedLine(P3(xp + 0.18, Y2 - 0.2), P3(xp + 0.18, Y2 + 0.32), stroke_color=C.muted, stroke_width=2,
                              dash_length=0.06),
                   tex(r"\tfrac{p}{q}\,?", 34, C.muted).move_to(P3(xp + 0.6, Y2 + 1.25)))
    m.play(FadeIn(ghost, shift=0.1 * DOWN), at=t_fr, dur=0.5)
    m.play(ghost.animate.shift(LEFT * 0.36), at=t_fr + 0.8, dur=1.2, ease="easy_ease")
    m.play(ghost.animate.shift(RIGHT * 0.2), at=t_fr + 2.1, dur=1.0, ease="easy_ease")
    m.play(FadeOut(ghost), at=t_arc - 1.2, dur=0.5)

    # 'Archimedes': polygons inside and outside, doubling the sides; the readout traps π
    lt1 = lower_third(r"Archimedes\ \textperiodcentered\ c.\ 250\ BC")
    m.play(FadeIn(lt1, shift=0.1 * UP), at=t_arc, dur=0.6)
    t_n = [t_arc + 0.3 + 0.85 * j for j in range(len(NS))]
    digits = Digits(34)
    heads = VGroup(sans("sides", 28, C.muted), sans("inside", 28, C.muted), sans("outside", 28, C.muted))
    xs_r = [0.9, 2.95, 5.15]
    for h, x in zip(heads, xs_r):
        h.move_to(P3(x, 2.15), aligned_edge=RIGHT)
    m.play(FadeIn(heads), at=t_n[0], dur=0.4)

    def polys(t):
        j = max(i for i in range(len(NS)) if t >= t_n[i] - 0.05) if t >= t_n[0] - 0.05 else -1
        g = VGroup()
        if j < 0:
            return g
        n = NS[j]
        a = ss((t - t_n[j] + 0.05) / 0.35)
        g.add(polygon(n, BIG_R, False, BIG_C).set_stroke(opacity=a), polygon(n, BIG_R, True, BIG_C).set_stroke(
            opacity=0.7 * a))
        for i in range(j + 1):                                       # the readout table grows a row per doubling
            nn = NS[i]
            y = 1.55 - 0.52 * i
            col = C.quantity if i == j else C.muted
            g.add(digits.number(str(nn), xs_r[0], y, color=col),
                  digits.number(f"{nn * math.sin(math.pi / nn):.5f}", xs_r[1], y, color=col),
                  digits.number(f"{nn * math.tan(math.pi / nn):.5f}", xs_r[2], y, color=col))
        return g

    t_poly_end = t_22 - 0.4
    top.redraw(window(polys, t_n[0] - 0.05, t_poly_end), during=(t_n[0] - 0.05, t_poly_end + 0.05))
    trap = tex(r"3.14103 < \pi < 3.14271", 40, C.quantity).move_to(P3(3.0, -1.0))
    m.play(Write(trap), at=t_n[-1] + 0.9, dur=0.8)
    m.play(FadeOut(VGroup(heads, trap, lt1)), FadeOut(wheel), at=t_poly_end - 0.1, dur=0.5)
    plate(s, m, "archimedes", (5.6, -1.9), 2.5, t_arc + 0.2, t_poly_end - 0.1, C.quantity)

    # the dive: the number line re-draws itself through a zoom centred on π
    t_z0 = t_22 - 0.5
    keys = [(t_z0, 2.0), (t_z0 + 1.7, 1500.0), (t_480, 1500.0), (t_480 + 2.6, 4.0e6), (t_gap - 2.2, 4.0e6),
            (t_gap - 0.1, 1.0e7)]

    def scale_at(t):
        if t <= keys[0][0]:
            return keys[0][1]
        for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
            if t <= tb:
                u = ss((t - ta) / (tb - ta))
                return math.exp(math.log(sa) + u * (math.log(sb) - math.log(sa)))
        return keys[-1][1]

    def centre_at(t):
        return 2.5 + (math.pi - 2.5) * ss((t - t_z0) / 1.0)

    def ypos(t):
        return Y2 + (-0.3 - Y2) * ss((t - t_z0) / 1.2)

    frac_tex = {f: tex(rf"\tfrac{{{f[0]}}}{{{f[1]}}}", 40, C.text) for f in FRACS}
    pi_t = tex(r"\pi", 44, C.quantity)
    t_frac = {(22, 7): t_22 + 0.3, (223, 71): t_22 + 0.6, (355, 113): t_355}

    def dive(t):
        sc, c, y = scale_at(t), centre_at(t), ypos(t)
        g = zline(c, sc, y, size=24, spacing=2.6)
        xpi = (math.pi - c) * sc
        g.add(Line(P3(xpi, y - 0.32), P3(xpi, y + 0.55), stroke_color=C.quantity, stroke_width=4),
              pi_t.copy().move_to(P3(xpi, y + 0.9)))
        for f, tf in t_frac.items():
            a = ss((t - tf) / 0.4)
            x = (f[0] / f[1] - c) * sc
            if a <= 0 or abs(x) > 7.4:
                continue
            g.add(Line(P3(x, y - 0.22), P3(x, y + 0.4 + 0.5 * (1 - a)), stroke_color=C.text, stroke_width=3,
                       stroke_opacity=a),
                  frac_tex[f].copy().move_to(P3(x, y + 1.05)).set_opacity(a))
        return g

    m.remove(nl, tick, pi_mark, at=t_z0)
    m.redraw(window(dive, t_z0, float(s.end)), during=(t_z0, float(s.end)))

    # the zoom factor, screen-locked
    zt = {}

    def zoom_tag(t):
        k = int(math.floor(math.log10(scale_at(t) / 2.0) + 1e-6))
        if k < 1:
            return VGroup()
        if k not in zt:
            zt[k] = tex(rf"\times\,10^{{{k}}}", 34, C.muted).move_to(P3(5.9, -3.45))
        return zt[k].copy()

    hud.redraw(window(zoom_tag, t_z0, float(s.end)), during=(t_z0, float(s.end)))

    ineq = tex(r"\tfrac{223}{71} < \pi < \tfrac{22}{7}", 44, C.text).move_to(P3(0, 2.6))
    ineq[0][7].set_color(C.quantity)
    m.play(Write(ineq), at=t_22 + 1.3, dur=0.8)
    m.play(FadeOut(ineq), at=t_480 - 0.3, dur=0.4)

    lt2 = lower_third(r"Zu\ Chongzhi\ \textperiodcentered\ c.\ 480")
    hud.play(FadeIn(lt2, shift=0.1 * UP), at=t_480 + 0.2, dur=0.6)
    hud.play(FadeOut(lt2), at=t_gap - 2.6, dur=0.5)
    dec = VGroup(tex(r"\tfrac{355}{113} = 3.141592\mathbf{9}\ldots", 40, C.text),
                 tex(r"\pi = 3.141592\mathbf{6}\ldots", 40, C.quantity)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    dec.move_to(P3(0, 2.55))
    hud.play(FadeIn(dec[0], shift=0.08 * UP), at=t_355 + 1.4, dur=0.5)
    hud.play(FadeIn(dec[1], shift=0.08 * UP), at=t_355 + 2.0, dur=0.5)

    # 'gap': bracket between the tick and π, tagged with its width
    yb = -0.3 - 0.95
    xg = (355 / 113 - math.pi) * 1.0e7
    gap = VGroup(Line(P3(0, yb), P3(xg, yb), stroke_color=C.quantity, stroke_width=3),
                 Line(P3(0, yb - 0.12), P3(0, yb + 0.12), stroke_color=C.quantity, stroke_width=3),
                 Line(P3(xg, yb - 0.12), P3(xg, yb + 0.12), stroke_color=C.quantity, stroke_width=3))
    gtag = tex(r"\text{gap} \approx 0.00000027", 36, C.quantity).next_to(gap, DOWN, buff=0.2)
    top.play(Create(gap), FadeIn(gtag, shift=0.08 * UP), at=t_gap, dur=0.6)
