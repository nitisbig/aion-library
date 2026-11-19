"""s23: lambda is a price. One more meter of rope buys ten more square meters, and the slope of the best area is exactly lambda."""
from aion import *

from beats import T
from classic import *

CX = -2.5


def best_area(L):
    return L * L / 8.0


@scene(T.cut_ch7, T.cut_force)
def s23_price(s):
    backdrop(s)
    g = s.manim(z=0)
    shore(g, CX)
    progress(s, 7, r"What $\lambda$ is")
    old = rect_rope(10, 20, CX)
    Lt = keys((T.add_m, 40.0), (T.climbs + 1.0, 41.0), default_ease=E)

    def plot(t):
        L = float(Lt(t))
        P = rect_rope(L / 4, L / 2, CX)
        return VGroup(Polygon(*[p3(q) for q in P], fill_color=C.lam, fill_opacity=0.75, stroke_width=0), Polygon(*[p3(q) for q in old], fill_color=C.bg, fill_opacity=1, stroke_width=0), Polygon(*[p3(q) for q in old], fill_color=C.area, fill_opacity=0.32, stroke_width=0), poly(P, C.con, 6))
    live(g, plot, (T.cut_ch7, T.climbs + 1.1))
    h = hud(s)

    def reading(t):
        L = float(Lt(t))
        return VGroup(backed(tex(f"{L:.1f}", r"\text{ m}", size=44, colors={0: C.con}), 0.09).move_to([CX - 1.5, -1.35, 0]), backed(tex(f"{best_area(L):.1f}", r"\text{ m}^2", size=44, colors={0: C.area}), 0.09).move_to([CX + 1.5, -1.35, 0]))
    live(g, reading, (T.was10, T.climbs + 1.1))
    g2 = s.manim(z=2)
    g2.play(FadeIn(backed(tex("+1", r"\text{ m}", r"\;\to\;", r"+10", r"\text{ m}^2", size=50, colors={0: C.con, 1: C.con, 3: C.area, 4: C.area})).move_to([CX, -2.5, 0]), shift=0.08 * UP), at=T.ten_more, dur=0.6)
    pin = tex(r"\lambda", "=", "10", size=60, colors={0: C.lam, 2: C.lam})
    eq = tex(r"\dfrac{d f^{*}}{d c}", "=", r"\lambda", size=50, colors={2: C.lam})
    board(h, [(pin, T.was10), (eq, T.exchange - 1.0)], "ur")
    name = lab("shadow price", 32, C.lam).move_to(eq)
    h.play(FadeOut(eq), FadeIn(name, shift=0.08 * UP), at=T.shadow, dur=0.6, ease=E)
    x0, x1, y0, y1 = 3.0, 6.55, -3.0, -0.1
    L0, L1, A0, A1 = 30.0, 50.0, 100.0, 320.0
    def gx(L): return x0 + (x1 - x0) * (L - L0) / (L1 - L0)
    def gy(A): return y0 + (y1 - y0) * (A - A0) / (A1 - A0)
    inset(h, (4.77, -1.5), 4.15, 3.95, T.loosens - 0.3)
    axes = VGroup(Line([x0, y0, 0], [x1, y0, 0], color=C.axis, stroke_width=2.5), Line([x0, y0, 0], [x0, y1, 0], color=C.axis, stroke_width=2.5))
    Ls = np.linspace(L0, L1, 90)
    h.play(FadeIn(axes), Create(poly(np.column_stack([gx(Ls), gy(best_area(Ls))]), C.area, 4.5)), at=T.loosens, dur=1.0, ease=E)
    h.play(FadeIn(lab("rope", 24, C.con).move_to([5.9, y0 + 0.25, 0])), FadeIn(lab("best area", 24, C.area).move_to([x0 + 0.95, y1 + 0.2, 0])), at=T.loosens + 0.5, dur=0.5)
    dL = 6.5
    h.play(Create(poly([[gx(40 - dL), gy(200 - 10 * dL)], [gx(40 + dL), gy(200 + 10 * dL)]], C.lam, 4.5)), FadeIn(Dot([gx(40), gy(200), 0], radius=0.1, color=C.you)), at=T.rate, dur=0.7, ease=E)
    h.play(FadeIn(tex(r"\text{slope}", "=", r"\lambda", size=38, colors={2: C.lam}).move_to([gx(37), gy(280), 0])), at=T.rate + 0.5, dur=0.5)
    curtain(s)
