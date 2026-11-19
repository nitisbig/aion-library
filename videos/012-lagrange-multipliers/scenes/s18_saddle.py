"""s18: the flat point of the Lagrangian is a saddle, not a peak, shown on the smallest example: maximize -x^2 with x = 1."""
from aion import *

from beats import T
from classic import *


def height(a, b):
    """L + 1 at x = 1 + a, lambda = -2 + b, drawn at a gentler height scale."""
    return 0.2 * (-(a**2) - a * b)


def display(a, b):
    return np.stack([1.25 * a, 0.62 * b, height(a, b)], -1)


@scene(T.cut_saddle, T.cut_ch5)
def s18_saddle(s):
    backdrop(s)
    progress(s, 4)
    aa, bb = np.meshgrid(np.linspace(-2, 2, 60), np.linspace(-3.4, 3.4, 60))
    Z = height(aa, bb)
    u = np.clip((Z + 2.2) / 4.4, 0, 1)[..., None]
    cols = rgb(C.lag) * (0.28 + 0.72 * u)
    P = display(aa, bb)
    show = fade(T.plot_l, dur=0.8)
    grow_up = key(T.rising + 0.1, 0.0, 1.0, dur=0.9, ease=E)
    grow_dn = key(T.rising + 1.3, 0.0, 1.0, dur=0.9, ease=E)
    uu = np.linspace(-1, 1, 40)

    def frame(t):
        az = -58 + 16 * (t - float(T.plot_l)) / 21.0
        v = view().begin(Cam(az=az, el=27, zoom=1.5, center=(0.0, -0.35), dist=30))
        a = float(show(t))
        v.mesh(P[..., 0], P[..., 1], P[..., 2], cols * a, alpha=a, ambient=0.55)
        for w in np.linspace(-2, 2, 9):
            v.line(display(np.full_like(uu, w), uu * 3.4), C.bg, 1.5, 0.45 * a)
        for w in np.linspace(-3.4, 3.4, 11):
            v.line(display(uu * 2, np.full_like(uu, w)), C.bg, 1.5, 0.45 * a)
        for g, d, col in ((float(grow_up(t)), (1.0, -2.414), C.tang), (float(grow_dn(t)), (1.0, 0.414), C.wrong)):
            if g > 0.01:
                w = uu * 1.3 * g
                n = np.hypot(*d)
                v.line(display(w * d[0] / n * 1.5, w * d[1] / n * 1.5) + [0, 0, 0.03], col, 6)
        if t >= float(T.on_saddle) - 0.2:
            v.dot(display(0.0, 0.0) + [0, 0, 0.04], C.you, 0.14, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10, during=[(T.plot_l - 0.2, T.cut_ch5)]))
    left = s.manim(z=1)
    flat = tex(r"\nabla", r"\mathcal{L}", "=", "0", size=120, colors={1: C.lag})
    left.play(FadeIn(flat, shift=0.1 * UP), at=T.careful, dur=0.6)
    left.play(FadeOut(flat), at=T.smallest - 0.2, dur=0.4)
    c0, ux, uy = np.array([0.0, 2.3]), 1.7, 0.95
    def pt(x, y): return [c0[0] + ux * x, c0[1] + uy * y, 0]
    para = poly([pt(x, -x * x) for x in np.linspace(-2.3, 2.3, 120)], C.obj, 6)
    wall = Line(pt(1, 0.7), pt(1, -5.6), color=C.con, stroke_width=5)
    mark = Dot(pt(1, -1), radius=0.13, color=C.you)
    left.play(Create(para), at=T.smallest + 1.2, dur=1.0, ease=E)
    left.play(Create(wall), FadeIn(mark, scale=0.4), at=T.forced, dur=0.7, ease=E)
    left.play(FadeOut(VGroup(para, wall, mark)), at=T.plot_l - 0.1, dur=0.5)
    h = hud(s)
    board(h, [(lab("not a peak", 32, C.wrong), T.not_peak), (tex(r"\max\;", "-x^2", size=44, colors={1: C.obj}), T.smallest + 1.0), (tex("x", "=", "1", size=44, colors={0: C.con, 2: C.con}), T.forced)])
    board(h, [(tex(r"\mathcal{L}", "=", "-x^2", "-", r"\lambda", "(x-1)", size=42, colors={0: C.lag, 2: C.obj, 4: C.lam}), T.plot_l), (tex("x=1", r",\quad", r"\lambda", "=-2", size=42, colors={2: C.lam}), T.on_saddle),
              (lab("solve, don't climb", 30, C.you), T.solve_it)], "dr")
    m = s.manim(z=5)
    m.play(FadeIn(backed(lab("rises", 30, C.tang)).move_to([-2.4, 2.1, 0])), at=T.rising + 0.6, dur=0.4)
    m.play(FadeIn(backed(lab("falls", 30, C.wrong)).move_to([2.9, 1.2, 0])), at=T.rising + 1.8, dur=0.4)
    curtain(s)
