"""s03: Fermat's rule. A tangent rides the curve and goes flat at the top; every flat place is a candidate."""
from scipy.optimize import brentq

from aion import *

from beats import T
from cards import card, pop
from shots import E, backdrop, curtain, lab, live, p3, poly, sc, walker


def f(x):
    return 1.15 * np.sin(1.1 * x) + 0.2 * x


def df(x):
    return 1.265 * np.cos(1.1 * x) + 0.2


PEAK = brentq(df, 0.5, 2.5)
VALLEY = brentq(df, -2.5, -0.5)
O, UX, UY = np.array([0.0, -0.45]), 1.75, 1.45


def pt(x):
    return O + [UX * x, UY * f(x)]


def tangent(x, L=1.5):
    d = np.array([UX, UY * df(x)])
    d /= np.linalg.norm(d)
    return poly([pt(x) - L * d, pt(x) + L * d], C.tang, 5)


@scene(T.cut_fermat, T.cut_trail)
def s03_fermat(s):
    backdrop(s)
    m = s.manim(z=0)
    xs = np.linspace(-3.6, 3.6, 300)
    curve = poly([pt(x) for x in xs], C.gold, 6).set_stroke([C.dusk, C.gold, C.ember, C.gold, C.dusk], 6)
    ground = Line([-6.4, -2.75, 0], [6.4, -2.75, 0], color=C.frame, stroke_width=2)
    land = Polygon(*[p3(pt(x)) for x in xs], [6.3, -2.75, 0], [-6.3, -2.75, 0], fill_color=C.gold, fill_opacity=0.09, stroke_width=0)
    m.play(FadeIn(land), Create(ground), at=T.fermat + 0.9, dur=1.6, ease=E)
    pop(m, card("fermat", "Fermat", "c. 1636", h=2.4, tilt=-1.5, pos=[-5.4, 1.95, 0]), T.fermat + 0.9)
    m.play(Create(curve), at=T.fermat + 0.5, dur=2.2, ease=E)
    x_t = keys((T.no_hold - 0.6, -0.5), (T.flat + 0.5, PEAK))

    def ride(t):
        x = float(x_t(t))
        return VGroup(tangent(x), walker(pt(x)))
    live(m, ride, (T.no_hold - 1.0, T.flat + 0.6))
    flat = lab("flat", 36, C.tang).move_to(p3(pt(PEAK)) + [0, 0.62, 0])
    m.play(FadeIn(flat, shift=0.08 * UP), at=T.flat + 0.45, dur=0.5)
    t2, d2 = tangent(VALLEY), walker(pt(VALLEY))
    flat2 = lab("flat", 36, C.tang).move_to(p3(pt(VALLEY)) + [0, -0.62, 0])
    m.play(Create(t2), FadeIn(d2), FadeIn(flat2), at=T.flats + 0.6, dur=0.7, ease=E)
    cand = lab("candidates", 40, C.you).move_to([4.2, 3.0, 0])
    m.play(FadeIn(cand, shift=0.1 * UP), at=T.candidates + 0.8, dur=0.5)
    curtain(s)
