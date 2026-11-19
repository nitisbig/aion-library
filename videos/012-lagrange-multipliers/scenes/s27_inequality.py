"""s27: tangency is only a candidate, a trail can run off forever, and a limit you aren't pressing against has a price of zero."""
from aion import *

from beats import T
from classic import *

O, UX, UY = np.array([0.0, -2.6]), 2.5, 2.6


def f(x):
    return 1.6 * np.exp(-(x**2) / 1.5)


def df(x):
    return -2 * x / 1.5 * f(x)


def pt(x):
    return O + [UX * x, UY * f(x)]


@scene(T.cut_ineq, T.cut_outro)
def s27_inequality(s):
    plain(s, (0.0, O[1]), 1.25, 0.5)
    progress(s, 8)
    m = s.manim(z=0)
    a = np.linspace(-1.8, 1.8, 120)
    A0, B0 = np.array([-3.6, 0.3]), np.array([1.2, -0.7])
    fr1 = Rectangle(width=6.2, height=5.2, fill_color=C.bg, fill_opacity=1, stroke_color=C.frame, stroke_width=C.thin).move_to([-3.6, 0.1, 0])
    fr2 = Rectangle(width=6.2, height=5.2, fill_color=C.bg, fill_opacity=1, stroke_color=C.frame, stroke_width=C.thin).move_to([3.6, 0.1, 0])
    wig = poly([A0 + [1.4 * u, 0.55 * u**3 - 0.66 * u] for u in a], C.obj, 4.5)
    d0 = A0 + [1.4 * 0.63, 0.55 * 0.63**3 - 0.66 * 0.63]
    tl = poly([d0 - [1.5, 0], d0 + [1.5, 0]], C.tang, 3.5)
    grp1 = VGroup(fr1, wig, tl, walker(d0), lab("only a candidate", 34, C.you).move_to([-3.6, -1.9, 0]))
    m.play(FadeIn(grp1, shift=0.1 * UP), at=T.tangency, dur=0.6)
    b = np.linspace(0.32, 3.2, 100)
    hy = poly([[B0[0] + 1.4 * u - 0.1, B0[1] + 1.1 / u] for u in b], C.con, 5)
    inf = arrow([5.7, -0.35, 0], [6.3, -0.37, 0], C.con, tip=0.24)
    grp2 = VGroup(fr2, hy, inf, lab("no best point", 34, C.wrong).move_to([3.6, -1.9, 0]))
    m.play(FadeIn(grp2, shift=0.1 * UP), at=T.infinity, dur=0.6)
    m.play(FadeOut(grp1), FadeOut(grp2), at=T.ineq - 0.2, dur=0.5)
    xs = np.linspace(-1.75, 1.75, 180)
    m.play(Create(poly([pt(x) for x in xs], C.obj, 5)), at=T.ineq + 0.3, dur=1.0, ease=E)
    c_t = keys((T.at_most + 1.0, -0.95), (T.lovely, -0.55), (T.zero_price + 1.6, 1.2), default_ease=E)
    show = fade(T.ineq + 0.8, dur=0.5)

    def wall(t):
        c = float(c_t(t))
        top, bot = O[1] + 4.75, O[1] - 0.2
        wx = O[0] + UX * c
        a = float(show(t))
        zone = Rectangle(width=max(O[0] + UX * 1.5 - wx, 0.01), height=top - bot, fill_color=C.wrong, fill_opacity=0.2 * a, stroke_width=0).move_to([(wx + O[0] + UX * 1.5) / 2, (top + bot) / 2, 0])
        return VGroup(zone, Line([wx, bot, 0], [wx, top, 0], color=C.con, stroke_width=6, stroke_opacity=a), walker(pt(min(c, 0.0))).set_opacity(a))
    live(m, wall, (T.ineq + 0.8, T.cut_outro))
    h = hud(s)
    board(h, [(sc("William Karush, 1939", 32, C.ink), T.karush), (sc("Kuhn \\& Tucker, 1951", 32, C.ink), T.kt)])
    x_c = 5.3
    inset(h, (x_c, 1.75), 2.9, 2.65, T.at_most - 0.85)
    h.play(FadeIn(tex("g", r"\le", "c", size=52, colors={0: C.con, 2: C.con}).move_to([x_c, 2.65, 0])), at=T.at_most - 0.3, dur=0.5)

    def price(t):
        v = abs(max(float(df(min(float(c_t(t)), 0.0))), 0.0))
        L = 2.3 * min(v / 1.4, 1.0)
        return VGroup(Rectangle(width=max(L, 0.001), height=0.3, fill_color=C.lam, fill_opacity=1, stroke_width=0).move_to([x_c - 1.15 + L / 2, 0.9, 0]), tex(r"\lambda", "=", f"{v:.2f}", size=48, colors={0: C.lam}).move_to([x_c, 1.7, 0]))
    live(h, price, (T.at_most + 0.2, T.cut_outro))
    h.play(FadeIn(Rectangle(width=2.3, height=0.3, stroke_color=C.frame, stroke_width=C.thin).move_to([x_c, 0.9, 0])), at=T.at_most + 0.2, dur=0.4)
    h.play(FadeIn(backed(lab("price zero", 30, C.you)).move_to([x_c, -0.1, 0])), at=T.zero_price + 1.3, dur=0.5)
    curtain(s)
