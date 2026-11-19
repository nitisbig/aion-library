"""s20: x^2 y on a circle. Six tangencies, the values 2, 0, 2, -2, 0, -2, and the equations can't say which is which."""
import contourpy

from aion import *

from beats import T
from classic import *

O, UN = np.array([0.0, -0.1]), 1.5
R = np.sqrt(3)
ANG = np.array([np.arctan2(1, np.sqrt(2)), np.pi / 2, np.pi - np.arctan2(1, np.sqrt(2)), np.pi + np.arctan2(1, np.sqrt(2)), 1.5 * np.pi, 2 * np.pi - np.arctan2(1, np.sqrt(2))])
VALS = ["2", "0", "2", "-2", "0", "-2"]


def q(x, y):
    return np.array([O[0] + UN * x, O[1] + UN * y, 0.0])


def fn(x, y):
    return x * x * y


@scene(T.cut_circle, T.cut_ch6)
def s20_circle(s):
    plain(s, O, UN)
    progress(s, 5)
    g = s.manim(z=0)
    xs, ys = np.linspace(-4.9, 4.9, 400), np.linspace(-2.8, 2.8, 240)
    gen = contourpy.contour_generator(xs, ys, fn(*np.meshgrid(xs, ys)))
    lines = VGroup()
    for lv in (-4, -2, -0.8, 0.8, 2, 4):
        for p in gen.lines(lv):
            if len(p) > 8:
                lines.add(poly([q(*u) for u in p[::2]], C.obj, 3.2 if abs(lv) == 2 else 1.7, 0.95 if abs(lv) == 2 else 0.65))
    g.play(FadeIn(lines), at=T.extremes, dur=0.9)
    g.play(Create(poly([q(R * np.cos(a), R * np.sin(a)) for a in np.linspace(0, TAU, 200)], C.con, 5.5)), at=T.the_circle, dur=1.2, ease=E)
    h = hud(s)
    z = 36
    board(h, [(tex("f", "=x^2y", size=z + 6, colors={0: C.obj}), T.extremes + 0.5), (tex("g", "=x^2+y^2=3", size=z + 6, colors={0: C.con}), T.the_circle), (tex("2xy", "=", "2", r"\lambda", "x", size=z, colors={3: C.lam}), T.arrow2 + 0.8),
              (tex("x^2", "=", "2", r"\lambda", "y", size=z, colors={3: C.lam}), T.arrow2 + 0.8), (tex("x=0", r"\ \text{or}\ ", r"\lambda", "=y", size=z, colors={2: C.lam}), T.either),
              (tex(r"y=\pm1,\ x=\pm\sqrt2", size=z, color=C.text), T.y1), (tex(r"x=0,\ y=\pm\sqrt3", size=z, color=C.text), T.y3)], "ul", out=T.six + 1.5)
    dots = VGroup(*[walker(q(R * np.cos(a), R * np.sin(a))) for a in ANG])
    g2 = s.manim(z=2)
    g2.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.15), at=T.six, dur=1.4, ease="out_back")
    x0, x1, y0 = 3.6, 6.6, -1.75
    def gx(a): return x0 + (x1 - x0) * (a - ANG[0] + 0.25) / (TAU + 0.1)
    def gy(v): return y0 + 0.56 * v
    aa = np.linspace(ANG[0] - 0.25, ANG[0] - 0.15 + TAU, 260)
    ff = fn(R * np.cos(aa), R * np.sin(aa))
    inset(h, (5.1, y0), 3.5, 2.9, T.walk_around - 0.95)
    h.play(FadeIn(Line([x0, y0, 0], [x1, y0, 0], color=C.axis, stroke_width=2.5)), at=T.walk_around - 0.4, dur=0.4)
    a_t = keys((T.walk_around, ANG[0]), (T.max2 - 0.2, ANG[5]), default_ease="linear")
    live(h, lambda t: poly(np.column_stack([gx(aa[:max(2, int(np.searchsorted(aa, float(a_t(t)))))]), gy(ff[:max(2, int(np.searchsorted(aa, float(a_t(t)))))])]), C.obj, 4.5), (T.walk_around, T.cut_ch6))
    live(g2, lambda t: walker(q(R * np.cos(float(a_t(t))), R * np.sin(float(a_t(t))))), (T.walk_around, T.cut_ch6))
    for a, v in zip(ANG, VALS):
        at = T.walk_around + (a - ANG[0]) / (ANG[5] - ANG[0]) * float(T.max2 - 0.2 - T.walk_around)
        p = q(R * np.cos(a), R * np.sin(a))
        g2.play(FadeIn(backed(tex(v, size=40, color=C.text), 0.06).move_to(p + np.array([np.cos(a), np.sin(a), 0.0]) * 0.56)), at=at, dur=0.3)
        h.play(FadeIn(Dot([gx(a), gy(float(fn(R * np.cos(a), R * np.sin(a)))), 0], radius=0.09, color=C.you)), at=at, dur=0.3)
    board(h, [(lab("maximum 2", 30, C.tang), T.max2), (lab("minimum $-2$", 30, C.wrong), T.min2), (lab("zeros: turning points", 26, C.muted), T.zeros)], "ur")
    board(h, [(lab("evaluate and compare", 30, C.you), T.compare - 0.3)], "dl")
    curtain(s)
