"""s23: lambda is a price. One more meter of rope raises the best area's block by ten square meters, and the best-area curve standing behind the beach has slope exactly lambda."""
from aion import *

from beach3d import AH, M, SH, block, corners, sand_and_sea
from beats import T
from ch1 import *

YC = SH + 2.0                       # the chart stands in the sea, behind the beach
XL = 0.25                           # world x per meter of rope on the chart
X0 = 5.2                            # the chart's x at 40 m, off to the right of the plot


def best_area(L):
    return L * L / 8.0


def chart(L):
    L = np.asarray(L, float)
    return np.stack([X0 + (L - 40) * XL, np.full_like(L, YC), best_area(L) * AH], -1)


@scene(T.cut_ch7, T.cut_force)
def s23_price(s):
    backdrop(s)
    beach = (-78, 30, 1.05, 0.0, -1.0, 30, 0, 0.8, 0.8)
    face = (-90, 10, 1.35, -1.0, -0.6, 60, X0, YC, 2.2)
    cam = camera(
        (T.cut_ch7, beach),
        (T.add_m, (-70, 32, 1.15, 0.0, -1.0, 30, 0, 0.8, 1.0)),
        (T.no_coin, (-60, 30, 1.15, 0.0, -1.0, 30, 0, 0.8, 1.0)),
        (T.loosens + 1.6, face),
        (T.exchange, face),
        (T.cut_force, (-98, 14, 1.35, -1.0, -0.6, 60, X0, YC, 2.2)),
    )
    Lt = lambda t: 40.0 + ramp(t, T.add_m, T.climbs + 1.0)
    ca = lambda t: ramp(t, T.loosens - 0.2, T.loosens + 1.2)

    def frame(t):
        v = view().begin(cam(t))
        sand_and_sea(v)
        L = Lt(t)
        block(v, 10.0, 1.0)
        if L > 40.01:
            block(v, L / 4, 0.35, L=L, color=C.lam)
        v.line(np.column_stack([corners(L / 4, L), np.full(4, 0.02)]), C.con, 6.0)
        a = ca(t)
        if a > 0.01:
            Ls = np.linspace(30, 50, 120)
            n = max(2, int(len(Ls) * ramp(t, T.loosens, T.loosens + 1.6)))
            v.arrow(chart(29.0) * [1, 1, 0], chart(51.5) * [1, 1, 0], C.axis, width=3.0, tip=0.18, alpha=a)
            v.arrow(chart(30.0) * [1, 1, 0] - [0, 0, 0.05], chart(30.0) * [1, 1, 0] + [0, 0, 4.2], C.axis, width=3.0, tip=0.18, alpha=a)
            v.line(chart(Ls[:n]), C.area, 5.0, a)
            for LL in (40.0, 41.0):
                v.line([chart(LL) * [1, 1, 0], chart(LL)], C.muted, 1.6, 0.7 * a)
                v.dot(chart(LL), C.you if LL == 40 else C.lam, 0.08, ring=C.bg)
            ra = ramp(t, T.rate, T.rate + 0.8)
            if ra > 0.01:
                d = 7.0 * ra
                v.line([chart(40.0) + np.array([-d * XL, 0, -10 * d * AH]), chart(40.0) + np.array([d * XL, 0, 10 * d * AH])], C.lam, 4.5)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch7, T.cut_force)]))
    title(s, r"Chapter 7  ·  what $\lambda$ is", T.cut_ch7 + 0.3, hold=3.0)
    m = s.manim(z=5, parallax=0.0)
    top = [0.0, SH - 1.0, 200 * AH]
    pin(m, cam, top, backed(tex("200", r"\text{ m}^2", size=50, colors={0: C.area, 1: C.area}), 0.1, 0.85), T.back_rope, T.climbs, off=(0.0, 0.55))
    pin(m, cam, top, backed(tex("200", r"\to", "210", r"\text{ m}^2", size=50, colors={0: C.area, 2: C.lam, 3: C.lam}), 0.1, 0.85), T.climbs, T.loosens + 0.6, off=(0.0, 0.65))
    pin(m, cam, [0.0, SH - 2.1, 0.0], backed(tex("40", r"\to", "41", r"\text{ m of rope}", size=44, colors={0: C.con, 2: C.lam}), 0.1, 0.85), T.add_m, T.loosens + 0.6, off=(0.0, -0.5))
    pin(m, cam, chart(51.5) * [1, 1, 0], backed(lab("rope", 26, C.con), 0.1, 0.85), T.loosens + 0.8, T.cut_force - 0.05, off=(0.0, -0.35))
    pin(m, cam, chart(30.0) * [1, 1, 0] + [0, 0, 4.2], backed(lab("best area", 26, C.area), 0.1, 0.85), T.loosens + 0.8, T.cut_force - 0.05, off=(0.0, 0.3))
    pin(m, cam, chart(40.0), backed(tex(r"\text{slope}", "=", r"\lambda", "=10", size=44, colors={2: C.lam}), 0.1, 0.85), T.rate + 0.5, T.cut_force - 0.05, off=(-2.0, 0.45))
    h = s.manim(z=20, parallax=0.0)
    lam = backed(tex(r"\lambda", "=", "10", size=64, colors={0: C.lam, 2: C.lam}), 0.12, 0.85).move_to([5.3, 3.2, 0])
    h.play(FadeIn(lam, shift=0.08 * DOWN), at=T.was10, dur=0.5, ease=E)
    h.play(FadeOut(lam), at=T.loosens, dur=0.4, ease=E, lead=0)
    headline(h, backed(tex("+1", r"\text{ m}", r"\;\to\;", r"+10", r"\text{ m}^2", size=56, colors={0: C.con, 1: C.con, 3: C.lam, 4: C.lam}), 0.12, 0.85), T.ten_more, T.loosens - 0.2)
    headline(h, backed(tex(r"\dfrac{d f^{*}}{d c}", "=", r"\lambda", size=56, colors={2: C.lam}), 0.12, 0.85), T.exchange - 1.0, T.shadow - 0.1, y=3.0)
    headline(h, backed(sc("a shadow price", 40, C.lam), 0.12, 0.85), T.shadow, T.cut_force - 0.3)
    stack(h, [(lab("one more unit of budget", 28, C.text), T.units), (lab("of steel", 28, C.text), T.units + 1.0), (lab("of machine time", 28, C.text), T.units + 1.8)], pos=(-6.75, 2.6), out=T.cut_force - 0.3)
    curtain(s, a=True, b=True)
