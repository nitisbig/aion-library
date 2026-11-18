"""s03 history: mathematicians wrote e^A down anyway. A timeline with two breaks: Bernoulli's 1683 compounding, then
Laguerre's series (1867), Peano's linear systems (1888) and Lie's continuous groups (1870s–1890s), each with a
public-domain portrait (assets/portraits/SOURCES.md); then today, where the same object runs inside flight software,
robot controllers, circuit simulators, dosing models and quantum hardware."""
from aion import *

from beats import T
from shots import (E, arm_icon, backdrop, circuit_icon, finish, lab, lie_icon, p3, pill_curve_icon, poly, portrait,
                   qwire_icon, satellite_icon, tex, words)

Y = 0.15                                               # the timeline's height
X0, X1 = -6.6, 6.6
BREAKS = (-4.55, 3.35)                                 # zig-zag gaps in the time axis
PY, PH = Y + 1.35, 1.6                                 # portraits above the line: centre y, height
FY = Y + 2.95                                          # formulas above the portraits


def year_x(y):
    """Piecewise time axis: 1683 alone on the left, 1860–1900 stretched in the middle, today on the right."""
    if y < 1700:
        return -5.6
    if y > 1950:
        return 5.25
    return -3.3 + (y - 1862) * 0.152


def axis_line():
    W = C.thin + 0.6
    out = VGroup()
    xs = [X0, *[v for b in BREAKS for v in (b - 0.12, b + 0.12)], X1]
    for a, b in zip(xs[::2], xs[1::2]):
        out.add(Line(p3((a, Y)), p3((b, Y)), color=C.muted, stroke_width=W))
    for b in BREAKS:
        out.add(poly([(b - 0.12, Y), (b - 0.05, Y + 0.14), (b + 0.05, Y - 0.14), (b + 0.12, Y)], C.muted, W))
    return out


def tick(x, h=0.16):
    return Line(p3((x, Y - h)), p3((x, Y + h)), color=C.text, stroke_width=C.thin + 0.8)


def stem(x):
    return Line(p3((x, Y + 0.18)), p3((x, PY - PH / 2 - 0.05)), color=C.muted, stroke_width=C.thin)


def label(name, year, x, col):
    """Year (sans, in the era's colour) and name (small caps) under the tick."""
    return VGroup(lab(year, 26, col).move_to(p3((x, Y - 0.4))),
                  words(r"\textsc{" + name + "}", size=30).move_to(p3((x, Y - 0.85))))


@scene(T.cut_history, T.cut_guess)
def s03_history(s):
    backdrop(s)
    m = s.manim(z=4)

    line = axis_line()
    m.play(Create(line), at=T.anyway, dur=1.4, ease=E)
    t_dim, t_out = T.today + 0.6, T.cut_guess - 0.55

    def p_op(at):
        return keys((at - 0.2, 0.0), (at + 0.5, 1.0), (t_dim, 1.0), (t_dim + 0.8, 0.35), (t_out, 0.35),
                    (t_out + 0.5, 0.0), lead=0)

    # ── 1683: where e came from ──
    xb = year_x(1683)
    fb = portrait(s, "bernoulli", (xb, PY), PH, opacity=p_op(T.anyway + 0.6), start=T.anyway)
    b = VGroup(tick(xb), stem(xb), fb, label("Bernoulli", "1683", xb, C.money),
               tex(r"\left(1+\tfrac{1}{n}\right)^{n}", size=36, color=C.money).move_to(p3((xb, FY))))
    m.play(FadeIn(b, shift=0.1 * UP), at=T.anyway + 0.6, dur=0.7)

    # ── 1867: Laguerre puts e^A in print, as a series ──
    xl = year_x(1867)
    fl = portrait(s, "laguerre", (xl, PY), PH, opacity=p_op(T.laguerre), start=T.laguerre - 0.3)
    lag = tex(r"e^{A}", "=", "I", "+", "A", "+", r"\frac{A^2}{2!}", "+", r"\frac{A^3}{3!}", "+", r"\cdots", size=38,
              colors={0: C.flow, 4: C.gen})
    for g in (lag[0][1], lag[6][0], lag[6][1], lag[8][0], lag[8][1]):
        g.set_color(C.gen)
    lag.move_to(p3((xl + 0.6, FY)))
    lab_l = label("Laguerre", "1867", xl, C.gen)
    m.play(Create(tick(xl)), Create(stem(xl)), Create(fl), FadeIn(lab_l), at=T.laguerre, dur=0.6)
    m.play(Write(lag), at=T.laguerre + 2.6, dur=1.3)

    # ── 1888: Peano solves the tangled systems ──
    xp = year_x(1888)
    fp = portrait(s, "peano", (xp, PY), PH, opacity=p_op(T.peano), start=T.peano - 0.3)
    pea = tex(r"\dot{\mathbf x}", "=", "A", r"\,\mathbf x", size=44, colors={0: C.vec, 2: C.gen, 3: C.vec})
    pea.next_to(fp, RIGHT, buff=0.4)
    lab_p = label("Peano", "1888", xp, C.vec)
    m.play(Create(tick(xp)), Create(stem(xp)), Create(fp), FadeIn(lab_p), at=T.peano, dur=0.6)
    m.play(FadeIn(pea, shift=0.1 * UP), at=T.peano + 2.4, dur=0.8)

    # ── 1870s–1890s: Lie's continuous symmetry ──
    xa, xz = year_x(1873), year_x(1893)
    SY = Y - 1.35
    span = VGroup(Line(p3((xa, SY)), p3((xz, SY)), color=C.flow, stroke_width=C.thin + 0.6),
                  *[Line(p3((x, SY + 0.1)), p3((x, SY - 0.1)), color=C.flow, stroke_width=C.thin + 0.6)
                    for x in (xa, xz)])
    LX = (xa + xz) / 2 - 0.85
    fi = portrait(s, "lie", (LX, SY - 1.05), 1.5, opacity=p_op(T.lie), start=T.lie - 0.3)
    lie_n = VGroup(words(r"\textsc{Sophus Lie}", size=30), lab("1870s--1890s", 24, C.flow)).arrange(
        DOWN, aligned_edge=LEFT, buff=0.1).next_to(fi, RIGHT, buff=0.3).shift(0.3 * UP)
    lie_i = lie_icon(lie_n.get_bottom()[:2] + [0.2, -0.55], s=0.32)
    m.play(Create(span), Create(fi), FadeIn(lie_n), at=T.lie, dur=0.7)
    m.play(Create(lie_i), at=T.lie + 0.9, dur=1.0)

    # ── today ──
    xt = year_x(2025)
    now = VGroup(tick(xt), lab("today", 28, C.text).move_to(p3((xt, Y - 0.4))))
    m.play(Create(now[0]), FadeIn(now[1]), at=T.today, dur=0.6)
    past = VGroup(b, lag, pea, lab_l, lab_p, span, lie_n, lie_i, fl, fp, fi)
    strokes = VGroup(b[0], b[1], b[2], span, lie_i, fl, fp, fi)
    fills = VGroup(*b[3:], lag, pea, lie_n, lab_l, lab_p, lie_i[1])
    m.play(strokes.animate.set_stroke(opacity=0.35), fills.animate.set_fill(opacity=0.35), at=t_dim, dur=0.8)
    spots = [(4.2, Y + 1.95), (5.95, Y + 1.95), (4.2, Y - 1.75), (5.95, Y - 1.75), (5.1, Y - 3.15)]
    makers = [(satellite_icon, "flight", C.cool, T.flight), (arm_icon, "robots", C.gen_b, T.robots),
              (circuit_icon, "circuits", C.eigen, T.circuits), (pill_curve_icon, "dosing", C.flow, T.dosing),
              (qwire_icon, "quantum", C.comm, T.quantum_pc)]
    icons = VGroup()
    for (x, y), (mk, word, col, at) in zip(spots, makers):
        ic = mk((x, y + 0.2), s=0.5)
        if mk is not pill_curve_icon:
            ic.set_stroke(color=col)
        tag = lab(word, 24, col).move_to(p3((x, y - 0.55)))
        icons.add(VGroup(ic, tag))
        m.play(Create(ic), FadeIn(tag, shift=0.08 * UP), at=at, dur=0.7, ease=E)

    m.play(FadeOut(VGroup(line, past, now, icons)), at=T.cut_guess - 0.4, dur=0.5)
    finish(s)
