"""s24: lambda is a force. A bead settles at the bottom of a hoop, and lambda times the gradient of g is exactly the hoop's push."""
from aion import *

from beats import T
from classic import *

O = np.array([0.0, 0.35])
R = 2.45


@scene(T.cut_force, T.cut_gas)
def s24_force(s):
    plain(s, O, 1.0, 0.55)
    progress(s, 7)
    m = s.manim(z=0)
    m.play(Create(Circle(radius=R, color=C.con, stroke_width=8).move_to(p3(O))), at=T.physics + 0.2, dur=1.1, ease=E)
    t0 = float(T.bead) - 0.2

    def bead(t):
        tau = max(0.0, t - t0)
        a = 0.95 * np.exp(-0.62 * tau) * np.cos(2.5 * tau)
        return walker(O + R * np.array([np.sin(a), -np.cos(a)])).scale(1.3)
    live(m, bead, (t0, T.gravity + 2.5))
    rest = O + [0, -R]
    grav = arrow(rest, rest + [0, -1.15], C.obj, tip=0.3)
    push = arrow(rest, rest + [0, 1.15], C.lam, tip=0.3)
    m.play(GrowArrow(grav), FadeIn(tex("m", "g", size=44, color=C.obj).next_to(grav, RIGHT, buff=0.2)), at=T.gravity + 1.0, dur=0.5)
    m.play(GrowArrow(push), at=T.push_back + 0.7, dur=0.5)
    m.play(FadeIn(tex(r"\lambda", r"\nabla g", size=48, colors={0: C.lam, 1: C.con}).move_to(p3(rest) + [0.85, 1.0, 0]), shift=0.08 * UP), at=T.that_push, dur=0.5)
    h = hud(s)
    board(h, [(tex(r"\min\;", "U=mgy", size=44, colors={1: C.obj}), T.minimize), (tex("x^2+y^2", "=", "R^2", size=44, colors={0: C.con, 2: C.con}), T.minimize)])
    board(h, [(tex(r"\vec F_{\text{hoop}}", "=", r"\lambda", r"\nabla g", size=52, colors={2: C.lam, 3: C.con}), T.that_push), (lab("a constraint pushes back", 26, C.you), T.physically + 0.2)], "ur")
    board(h, [(sc("M\\'ecanique analytique, 1788", 30, C.ink), T.lag_world + 0.4)], "dl")
    curtain(s)
