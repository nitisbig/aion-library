"""s26: the fine print. At a cusp the gradient of g vanishes, no multiple of it can match the gradient of f, and the equations miss the answer."""
from aion import *

from beats import T
from classic import *

O, UN = np.array([-1.9, -0.1]), 2.6


def q(x, y):
    return O + UN * np.array([x, y])


@scene(T.cut_ch8, T.cut_ineq)
def s26_cusp(s):
    plain(s, O, UN / 2, 0.55)
    progress(s, 8, "The fine print")
    m = s.manim(z=0)
    ys = np.linspace(-1.33, 1.33, 241)
    m.play(Create(poly([q(a, b) for a, b in zip(np.cbrt(ys**2), ys)], C.con, 6)), at=T.the_cusp, dur=1.4, ease=E)
    for x_ in (0.45, 0.9, 1.35):
        m.play(FadeIn(DashedLine(p3(q(x_, -1.4)), p3(q(x_, 1.4)), color=C.obj, stroke_width=2, dash_length=0.1)), at=T.smallest_x, dur=0.5)
    y_t = keys((T.smallest_x + 0.6, 0.95), (T.no_mult - 0.6, 0.0), default_ease=E)

    def now(t):
        y = float(y_t(t))
        x = np.cbrt(y**2)
        c = q(x, y)
        gg = np.array([-3 * x * x, 2 * y]) * 0.4
        out = VGroup(arrow(c, c + [1.25, 0], C.obj, tip=0.28))
        if np.linalg.norm(gg) > 0.03:
            out.add(arrow(c, c + gg, C.con, tip=0.26))
        return out.add(walker(c))
    live(m, now, (T.smallest_x + 0.6, T.cut_ineq))
    h = hud(s)
    board(h, [(tex(r"\nabla g", r"\neq 0", size=52, colors={0: C.con}), T.assumed)], "ul", out=T.the_cusp - 0.1)
    z = 44
    board(h, [(tex("y^2", "=", "x^3", size=z, colors={0: C.con, 2: C.con}), T.the_cusp + 0.2), (tex(r"\min\;", "x", size=z, colors={1: C.obj}), T.smallest_x), (tex(r"\nabla g", "=(0,0)", size=z, colors={0: C.con}), T.vanish),
              (tex(r"\nabla f", "=(1,0)", size=z, colors={0: C.obj}), T.no_mult - 0.6), (tex("(1,0)", r"\neq", r"\lambda", "(0,0)", size=z, colors={1: C.wrong, 2: C.lam}), T.no_mult + 0.8), (lab("no solution", 32, C.wrong), T.no_sol + 0.4), (lab("check sharp points", 28, C.you), T.check)], "ur")
    curtain(s)
