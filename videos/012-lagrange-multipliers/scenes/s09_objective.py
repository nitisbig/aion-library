"""s09: the map rises into the mountain f(x, y). We ask which way is steepest, name that arrow the gradient, climb it, and stop where it vanishes."""
from aion import *

from beats import T
from ch1 import *

P0 = np.array([0.6, -1.0])          # the point we label (x, y)
S0 = np.array([1.75, -1.7])         # where the climber stands


def ascent(start, steps=2600, h=0.008):
    P = [np.array(start, float)]
    for _ in range(steps):
        g = hill_grad(*P[-1])
        n = np.linalg.norm(g)
        if n < 1e-4:
            break
        P.append(P[-1] + h * g / max(n, 0.35))
    return np.array(P)


PATH = ascent(S0)
PINS = np.array([[x, y] for x in np.arange(-3.6, 3.7, 0.9) for y in np.arange(-3.6, 3.7, 0.9) if 0.3 < hill(x, y) and np.hypot(x - 0.2, y) < 4.0 and np.hypot(x - P0[0], y - P0[1]) > 0.3])
GK = 1.05                            # ground length of the gradient arrow per unit of |grad f|


@scene(T.cut_ch1, T.cut_constraint)
def s09_objective(s):
    backdrop(s)
    follow = PATH[np.linspace(0, len(PATH) - 1, 5).astype(int)]
    cam = camera(
        (T.cut_ch1, (-38, 40, 1.0, 0.0, -0.4, 26, 0, 0, 0)),
        (T.fxy + 1.0, (-58, 34, 1.05, 0.1, -0.8, 26, 0, 0, 0)),
        (T.no_limit, (-70, 31, 1.08, 0.1, -0.9, 26, 0, 0, 0)),
        (T.no_limit + 2.0, (-76, 33, 1.6, 0.0, -0.5, 26, S0[0] - 0.3, S0[1] + 0.5, 0.9)),
        (T.follow, (-84, 30, 1.6, 0.0, -0.5, 26, S0[0] - 0.3, S0[1] + 0.5, 0.9)),
        (T.stop_ + 0.6, (-96, 31, 1.75, 0.0, -0.4, 26, follow[3][0], follow[3][1], 2.0)),
        (T.grad_zero - 0.2, (-104, 28, 1.7, 0.0, -0.3, 26, SUMMIT[0], SUMMIT[1], 2.4)),
        (T.grad_zero + 1.3, (-112, 7, 2.15, 0.0, -0.5, 40, SUMMIT[0], SUMMIT[1], 2.7)),
        (T.flat_again + 0.9, (-116, 8, 2.15, 0.0, -0.5, 40, SUMMIT[0], SUMMIT[1], 2.7)),
        (T.cut_constraint, OVER),
    )
    rise = lambda t: ramp(t, T.give + 0.1, T.fxy + 0.2)
    skin = lambda t: ramp(t, T.fxy - 0.3, T.fxy + 1.1)
    prog = lambda t: ramp(t, T.follow - 0.1, T.grad_zero - 0.4)
    walker_on = lambda t: win(t, T.no_limit + 0.8, T.flat_again + 1.0, 0.6, 0.6)

    def climber(t):
        return PATH[int(prog(t) * (len(PATH) - 1))]

    def frame(t):
        v = view().begin(cam(t))
        k = rise(t)
        a = skin(t)
        mountain(v, 1.0, a)
        floor(v, k * a)
        if a > 0.01:
            wires(v, 1.0, 0.26 * a)
        contours(v, k if a < 0.99 else 1.0, C.obj, 0.95 * (1 - a), 2.4)
        contours(v, 1.0, C.bg, 0.55 * a, 1.8)
        # pins: every point gets its height
        pa = win(t, T.give - 0.1, T.fxy + 2.6, 0.4, 0.8)
        if pa > 0.01:
            for i, (x, y) in enumerate(PINS):
                h = hill(x, y) * ramp(t, T.give + 0.05 * i % 1.4, T.give + 0.05 * i % 1.4 + 1.1)
                top = np.array([x, y, h + 0.02])
                vis = seen_k(np.array([top]), v.cam, a)[0]
                if vis:
                    v.line([[x, y, 0], top], C.text, 1.6, 0.55 * pa)
                    v.dot(top, C.obj, 0.05)
        qa = win(t, T.give + 0.3, T.no_limit + 0.2, 0.5, 0.6)
        if qa > 0.01:
            h = hill(*P0) * ramp(t, T.give + 0.4, T.fxy + 0.3)
            v.line([[*P0, 0], [*P0, h + 0.03]], C.you, 4.0, qa)
            v.dot([*P0, 0], C.you, 0.07)
            v.dot([*P0, h + 0.03], C.you, 0.09, ring=C.bg)
        # the objective: a level ring climbing to the top
        ra = win(t, T.objective - 0.1, T.no_limit + 0.4, 0.3, 0.6)
        if ra > 0.01:
            lv = 0.2 + 2.78 * ramp(t, T.objective, T.objective + 2.3)
            for p in ring(lv):
                curve(v, p, C.you, 4.0, ra, dz=0.03)
            v.dot([*SUMMIT, hill(*SUMMIT) + 0.04], C.you, 0.08 * ramp(t, T.objective + 2.0, T.objective + 2.4) + 1e-3, ring=C.bg)
        # the compass: every direction you could step
        ca = win(t, T.steepest + 0.1, T.grad_name + 0.4, 0.4, 0.5)
        if ca > 0.01:
            g = hill_grad(*S0)
            best = np.arctan2(g[1], g[0])
            grow = ramp(t, T.steepest + 0.1, T.steepest + 1.0)
            pick = ramp(t, T.steepest + 2.0, T.steepest + 2.8)
            for th in best + np.linspace(0, TAU, 16, endpoint=False):
                d = np.array([np.cos(th), np.sin(th)])
                rise_d = (hill(*(S0 + 0.6 * d)) - hill(*S0)) / 0.6
                top = np.cos(th - best) > 0.999
                xy = S0 + np.outer(np.linspace(0.12, 0.62 * grow + 0.12, 10), d)
                col = C.obj if top and pick > 0.5 else (C.you if rise_d > 0 else C.muted)
                al = ca * (1.0 if top else 1.0 - 0.75 * pick)
                curve(v, xy, col, 5.5 if top else 3.0, al, dz=0.05)
        # the gradient arrow, carried up the hill
        ga = win(t, T.grad_name - 0.2, T.grad_zero + 0.2, 0.6, 0.6)
        if ga > 0.01:
            q = climber(t)
            if prog(t) > 0.002:
                curve(v, PATH[: max(2, int(prog(t) * (len(PATH) - 1)))][::6], C.you, 4.5, ga)
            tip = grad_tip(q, GK * ramp(t, T.grad_name - 0.2, T.grad_name + 0.6))
            v.arrow(lift(np.atleast_2d(q), 1.0, 0.04)[0], tip, C.obj, width=6.0, tip=0.24, alpha=ga)
        wa = walker_on(t)
        if wa > 0.01:
            bead(v, climber(t), r=0.1 * wa + 1e-3)
        # flat ground: the tangent plane at the summit
        fa = win(t, T.grad_zero - 0.1, T.cut_constraint - 0.3, 0.7, 0.7)
        if fa > 0.01:
            zt = hill(*SUMMIT) + 0.02
            w = 1.3 * ramp(t, T.grad_zero - 0.1, T.grad_zero + 0.8)
            ss = np.linspace(-w, w, 9)
            X, Y = np.meshgrid(SUMMIT[0] + ss, SUMMIT[1] + ss)
            v.mesh(X, Y, np.full_like(X, zt), C.tang, alpha=0.32 * fa, shade=False)
            for c in ss[::2]:
                v.line([[SUMMIT[0] + c, SUMMIT[1] - w, zt], [SUMMIT[0] + c, SUMMIT[1] + w, zt]], C.tang, 1.4, 0.8 * fa)
                v.line([[SUMMIT[0] - w, SUMMIT[1] + c, zt], [SUMMIT[0] + w, SUMMIT[1] + c, zt]], C.tang, 1.4, 0.8 * fa)
            v.dot([*SUMMIT, zt + 0.02], C.you, 0.1, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch1, T.cut_constraint)]))
    title(s, "Chapter 1  ·  free and constrained", T.cut_ch1 + 0.3, hold=3.2)
    m = s.manim(z=5, parallax=0.0)
    top0 = lambda t: [*P0, hill(*P0) * ramp(t, T.give + 0.4, T.fxy + 0.3) + 0.03]
    pin(m, cam, [*P0, 0.0], tex("(x,y)", size=40, color=C.text), T.give + 0.5, T.fxy + 1.6, off=(0.15, -0.38))
    pin(m, cam, top0, tex("f", "(x,y)", size=56, colors={0: C.obj}), T.fxy - 0.1, T.no_limit + 0.2, off=(-0.95, 0.25))
    pin(m, cam, top0, lab("objective", 30, C.obj), T.objective, T.no_limit + 0.2, off=(-0.95, -0.3))
    pin(m, cam, [*SUMMIT, hill(*SUMMIT)], lab("as large as possible", 26, C.you), T.objective + 2.3, T.no_limit + 0.4, off=(0.0, 0.5))
    pin(m, cam, [*S0, hill(*S0)], lab("which way is steepest?", 26, C.text), T.steepest + 0.6, T.grad_name, off=(0.0, -0.75))
    pin(m, cam, lambda t: grad_tip(climber_xy(t)), tex(r"\nabla f", size=54, color=C.obj), T.grad_name, T.stop_ + 0.8, off=(0.42, 0.3))
    pin(m, cam, [*SUMMIT, hill(*SUMMIT) + 0.02], tex(r"\nabla f", "=", "0", size=56, colors={0: C.obj}), T.grad_zero, T.cut_constraint - 0.5, off=(0.0, 0.7))
    pin(m, cam, [*SUMMIT, hill(*SUMMIT) + 0.02], lab("flat ground", 30, C.tang), T.flat_again, T.cut_constraint - 0.5, off=(0.0, 1.3))
    curtain(s, a=True, b=False)


def climber_xy(t):
    return PATH[int(ramp(t, T.follow - 0.1, T.grad_zero - 0.4) * (len(PATH) - 1))]
