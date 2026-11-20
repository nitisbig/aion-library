"""s26: the fine print. The cusp y^2 = x^3 is the zero level of the surface g = y^2 - x^3, which goes flat at the sharp point: grad g = 0, and no multiple of it can match grad f."""
from aion import *

from beats import T
from ch1 import *

UN = 2.0                                  # world units per unit of x, y
SG = 0.45                                 # world height per unit of g
YS = np.linspace(-1.33, 1.33, 241)


def gz(X, Y):
    """The surface height over world points."""
    x, y = X / UN, Y / UN
    return SG * (y * y - x**3)


def cusp(y):
    y = np.asarray(y, float)
    return np.column_stack([UN * np.cbrt(y * y), UN * y])


@scene(T.cut_ch8, T.cut_ineq)
def s26_cusp(s):
    backdrop(s)
    top = (-90, 89.5, 1.35, 0.6, -0.2, 400, 1.4, 0, 0)
    cam = camera(
        (T.cut_ch8, (-50, 30, 1.1, 0.0, -0.4, 30, 1.0, 0, 0)),
        (T.the_cusp + 2.0, (-35, 34, 1.1, 0.0, -0.4, 30, 1.0, 0, 0)),
        (T.smallest_x, top),
        (T.vanish - 0.4, top),
        (T.vanish + 1.2, (-125, 16, 2.3, 0.0, -0.3, 30, 0.0, 0.0, 0.0)),
        (T.no_sol, (-145, 20, 2.1, 0.0, -0.3, 30, 0.0, 0.0, 0.0)),
        (T.cut_ineq, (-160, 26, 1.6, 0.0, -0.3, 30, 0.4, 0.0, 0.0)),
    )
    rise = lambda t: ramp(t, T.the_cusp - 0.4, T.the_cusp + 1.0)
    dim = lambda t: 1 - 0.75 * win(t, T.smallest_x - 0.5, T.vanish + 0.4, 0.8, 0.8)
    y_t = lambda t: 0.95 * (1 - ramp(t, T.smallest_x + 0.6, T.no_mult - 0.6))
    xs, ys = np.meshgrid(np.linspace(-1.2, 3.2, 60), np.linspace(-3.0, 3.0, 70))

    def frame(t):
        v = view().begin(cam(t))
        k = rise(t)
        a = dim(t)
        w = np.linspace(-7, 7, 90)
        for j in range(-7, 8):
            for P in (np.column_stack([np.full_like(w, j), w, np.zeros_like(w)]), np.column_stack([w, np.full_like(w, j), np.zeros_like(w)])):
                inside = (P[:, 0] > -1.2) & (P[:, 0] < 3.2) & (np.abs(P[:, 1]) < 3.0)
                v.line(P, C.grid, 1.2, 0.5, visible=(~inside | (k * a < 0.3)) & seen_by(P, v.cam, gz, k))
        if k > 0.01:
            Z = gz(xs, ys) * k
            u = np.clip((gz(xs, ys) + 1.5) / 2.5, 0, 1)[..., None]
            v.mesh(xs, ys, Z, rgb(C.con) * (0.2 + 0.6 * u), alpha=min(1.0, 2 * k) * a, ambient=0.45)
            for c in np.linspace(-1.0, 3.0, 9):
                P = np.column_stack([np.full(80, c), np.linspace(-3, 3, 80)])
                Q = np.column_stack([P, gz(*P.T) * k + 0.015])
                v.line(Q, C.bg, 1.2, 0.35 * a, visible=seen_by(Q, v.cam, gz, k))
        ca = ramp(t, T.the_cusp + 0.6, T.the_cusp + 2.0)
        if ca > 0.01:
            n = max(2, int(len(YS) * ca))
            P = np.column_stack([cusp(YS[:n]), np.full(n, 0.03)])
            v.line(P, C.con, 6.5, visible=seen_by(P, v.cam, gz, k * a))
        la = win(t, T.smallest_x, T.vanish + 0.6, 0.6, 0.6)
        for x_ in (0.45, 0.9, 1.35):
            if la > 0.01:
                for j in range(-14, 14, 2):
                    v.line([[UN * x_, 0.2 * j, 0.02], [UN * x_, 0.2 * (j + 1), 0.02]], C.obj, 2.2, 0.8 * la)
        wa = win(t, T.smallest_x + 0.3, T.cut_ineq + 1.0, 0.5, 0.3)
        if wa > 0.01:
            y = y_t(t)
            q = cusp([y])[0]
            p = np.array([q[0], q[1], 0.05])
            v.arrow(p, p + [1.3, 0, 0], C.obj, width=6.0, tip=0.24, alpha=wa)
            x = np.cbrt(y * y)
            gg = np.array([-3 * x * x, 2 * y]) * 0.9
            if np.linalg.norm(gg) > 0.04:
                v.arrow(p, p + [gg[0], gg[1], 0], C.con, width=5.5, tip=0.22, alpha=wa)
            v.dot(p, C.you, 0.1, ring=C.bg)
        fa = win(t, T.vanish + 0.2, T.cut_ineq + 1.0, 0.8, 0.3)
        if fa > 0.01:
            ss = np.linspace(-0.9, 0.9, 7)
            X, Y = np.meshgrid(ss, ss)
            v.mesh(X, Y, np.full_like(X, 0.02), C.tang, alpha=0.35 * fa, shade=False)
            for c in ss[::2]:
                v.line([[c, -0.9, 0.025], [c, 0.9, 0.025]], C.tang, 1.4, 0.8 * fa)
                v.line([[-0.9, c, 0.025], [0.9, c, 0.025]], C.tang, 1.4, 0.8 * fa)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch8, T.cut_ineq)]))
    title(s, "Chapter 8  ·  the fine print", T.cut_ch8 + 0.3, hold=2.4)
    h = s.manim(z=20, parallax=0.0)
    headline(h, backed(tex(r"\text{we assumed }", r"\nabla g", r"\neq 0", size=52, colors={1: C.con}), 0.12, 0.85), T.assumed, T.the_cusp + 1.0, y=2.6)
    stack(h, [(tex("g", "=y^2-x^3", "=", "0", size=46, colors={0: C.con}), T.the_cusp + 0.4), (tex(r"\min\;", "x", size=46, colors={1: C.obj}), T.smallest_x),
              (tex(r"\nabla g", "=(0,0)", size=46, colors={0: C.con}), T.vanish), (tex(r"\nabla f", "=(1,0)", size=46, colors={0: C.obj}), T.no_mult - 0.6)], pos=(-6.75, 3.3))
    headline(h, backed(tex("(1,0)", r"\neq", r"\lambda", "(0,0)", size=60, colors={0: C.obj, 2: C.lam}), 0.12, 0.85), T.no_mult + 0.8, T.cut_ineq - 0.2, y=-2.6)
    headline(h, backed(lab("no solution: the equations miss the answer", 30, C.wrong), 0.1, 0.85), T.no_sol + 0.4, T.check - 0.1, y=-3.5)
    headline(h, backed(lab("always check the sharp points by hand", 32, C.you), 0.1, 0.85), T.check, T.cut_ineq - 0.2, y=-3.5)
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, [0.0, 0.0, 0.05], backed(lab("flat: the gradient of g vanishes", 28, C.tang), 0.1, 0.85), T.vanish + 0.8, T.no_mult + 0.6, off=(0.0, 0.75))
    pin(m, cam, [UN * 0.9, 0.0, 0.0], backed(lab("contours of x", 26, C.obj), 0.1, 0.85), T.smallest_x + 0.4, T.vanish - 0.4, off=(0.0, -2.6))
    curtain(s, a=True, b=False)
