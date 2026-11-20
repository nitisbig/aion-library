"""s18: the flat point of the Lagrangian is a saddle, not a peak. The smallest example, max -x^2 with x = 1, grows from its parabola into the surface L(x, lambda)."""
from aion import *

from beats import T
from ch1 import *

SX, SY, SZ = 1.6, 0.7, 0.3          # world units per unit of x, lambda and L
XS = np.linspace(-0.4, 2.4, 57)


def Lf(x, lam):
    return -x**2 - lam * (x - 1)


def world(x, lam):
    """(x, lambda) to world points, with the saddle (1, -2, L=-1) at the origin."""
    x, lam = np.broadcast_arrays(np.asarray(x, float), np.asarray(lam, float))
    return np.stack([(x - 1) * SX, (lam + 2) * SY, (Lf(x, lam) + 1) * SZ], -1)


def climb(a0=0.06, b0=-0.1, steps=500, h=0.02):
    """Gradient ascent on L from just beside the saddle: it runs away."""
    P = [np.array([1 + a0, -2 + b0])]
    for _ in range(steps):
        x, lam = P[-1]
        g = np.array([-2 * x - lam, -(x - 1)])
        n = np.linalg.norm(g) + 1e-9
        q = P[-1] + h * g / max(n, 0.4)
        if not (-0.4 < q[0] < 2.4 and -5.0 < q[1] < 1.0):
            break
        P.append(q)
    return np.array(P)


RUN = climb()
UPV = np.array([1.0, -2.414]) / np.hypot(1.0, 2.414)
DNV = np.array([1.0, 0.414]) / np.hypot(1.0, 0.414)


@scene(T.cut_saddle, T.cut_ch5)
def s18_saddle(s):
    backdrop(s)
    side = (-90, 4, 1.2, 0.0, 0.4, 80, 0.0, 1.4, -0.4)
    cam = camera(
        (T.cut_saddle, side),
        (T.plot_l, side),
        (T.on_saddle, (-125, 36, 1.15, 0.0, 0.2, 30, 0, 0, -0.3)),
        (T.cant_climb, (-150, 40, 1.15, 0.0, 0.2, 30, 0, 0, -0.3)),
        (T.cut_ch5, (-170, 42, 1.15, 0.0, 0.2, 30, 0, 0, -0.3)),
    )
    grow = lambda t: ramp(t, T.plot_l, T.plot_l + 2.2)
    para = lambda t: win(t, T.smallest + 1.0, T.cut_ch5, 1.0, 0.4)

    def frame(t):
        v = view().begin(cam(t))
        g = grow(t)
        pa = para(t)
        if g > 0.01:
            lo, hi = 0.0 - 5.0 * g, 0.0 + 1.0 * g
            lams = np.linspace(lo, hi, 50)
            X, LM = np.meshgrid(XS, lams)
            P = world(X, LM)
            u = np.clip((Lf(X, LM) + 7) / 8, 0, 1)[..., None]
            cols = rgb(C.lag) * (0.25 + 0.75 * u)
            v.mesh(P[..., 0], P[..., 1], P[..., 2], cols, alpha=1.0, ambient=0.5)
            for x in np.linspace(-0.4, 2.4, 8):
                v.line(world(np.full_like(lams, x), lams), C.bg, 1.4, 0.5)
            for lm in np.arange(np.ceil(lo), hi + 1e-6, 1.0):
                v.line(world(XS, np.full_like(XS, lm)), C.bg, 1.4, 0.5)
        if pa > 0.01:
            v.line(world(XS, np.zeros_like(XS)) + [0, 0, 0.02], C.obj, 6.0, pa)
            wa = pa * ramp(t, T.forced, T.forced + 0.6) * (1 - ramp(t, T.plot_l, T.plot_l + 0.8))
            if wa > 0.01:
                v.line([[0, 1.4, -1.6], [0, 1.4, 0.7]], C.con, 5.0, wa)
                v.dot(world(1.0, 0.0) + [0, 0, 0.03], C.you, 0.1, ring=C.bg)
        for gg, d, col in ((ramp(t, T.rising + 0.1, T.rising + 1.0), UPV, C.tang), (ramp(t, T.rising + 1.3, T.rising + 2.2), DNV, C.wrong)):
            if gg > 0.01:
                w = np.linspace(-1.0, 1.0, 40) * 1.4 * gg
                v.line(world(1 + w * d[0], -2 + w * d[1]) + [0, 0, 0.03], col, 6.0)
        ca = win(t, T.cant_climb, T.cut_ch5, 0.3, 0.3)
        if ca > 0.01:
            k = max(2, int(len(RUN) * ramp(t, T.cant_climb + 0.2, T.solve_it + 0.4)))
            v.line(world(RUN[:k, 0], RUN[:k, 1]) + [0, 0, 0.05], C.text, 4.5, ca)
            v.dot(world(*RUN[k - 1]) + [0, 0, 0.05], C.wrong, 0.09, ring=C.bg)
        if t > T.on_saddle - 0.2:
            v.dot([0, 0, 0.05], C.you, 0.13 * ramp(t, T.on_saddle - 0.2, T.on_saddle + 0.3) + 1e-3, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_saddle, T.cut_ch5)]))
    h = s.manim(z=20, parallax=0.0)
    flat = backed(tex(r"\nabla", r"\mathcal{L}", "=", "0", size=110, colors={1: C.lag}), 0.14, 0.85).move_to([0, 0.6, 0])
    h.play(FadeIn(flat, shift=0.1 * UP), at=T.careful, dur=0.6)
    no = backed(lab("is not a peak", 40, C.wrong), 0.1, 0.85).move_to([0, -0.7, 0])
    h.play(FadeIn(no, shift=0.08 * UP), at=T.not_peak, dur=0.5)
    h.play(FadeOut(VGroup(flat, no)), at=T.smallest - 0.1, dur=0.5, lead=0)
    headline(h, backed(tex(r"\max\;", "-x^2", r"\quad\text{with}\quad", "x", "=", "1", size=56, colors={1: C.obj, 3: C.con, 5: C.con}), 0.12, 0.85), T.smallest + 0.8, T.plot_l - 0.2)
    headline(h, backed(tex(r"\mathcal{L}", "=", "-x^2", "-", r"\lambda", "(x-1)", size=56, colors={0: C.lag, 2: C.obj, 4: C.lam}), 0.12, 0.85), T.plot_l, T.cut_ch5 - 0.3)
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, [0, 0, 0.05], backed(tex("x=1", r",\ ", r"\lambda", "=-2", size=44, colors={2: C.lam}), 0.1, 0.85), T.on_saddle + 0.2, T.cut_ch5 - 0.05, off=(1.9, -0.15))
    pin(m, cam, world(1 + 1.4 * UPV[0], -2 + 1.4 * UPV[1]), backed(lab("rises", 32, C.tang), 0.1, 0.85), T.rising + 0.8, T.cut_ch5 - 0.05, off=(0.0, 0.4))
    pin(m, cam, world(1 + 1.4 * DNV[0], -2 + 1.4 * DNV[1]), backed(lab("falls", 32, C.wrong), 0.1, 0.85), T.rising + 2.0, T.cut_ch5 - 0.05, off=(0.0, -0.4))
    pin(m, cam, world(*RUN[-1]), backed(lab("climbing runs away", 30, C.wrong), 0.1, 0.85), T.cant_climb + 1.6, T.cut_ch5 - 0.05, off=(0.0, 0.45))
    h2 = s.manim(z=21, parallax=0.0)
    headline(h2, backed(lab("solve for it, don't climb to it", 34, C.you), 0.1, 0.85), T.solve_it + 0.2, T.cut_ch5 - 0.2, y=-3.4)
    curtain(s, a=True, b=True)
