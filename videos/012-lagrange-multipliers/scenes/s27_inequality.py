"""s27: tangency only makes a candidate (four kisses on the trail), a trail can climb forever, and a limit you aren't pressing against has a price of zero."""
from aion import *

from beats import T
from ch1 import *

ALL = np.linspace(0, TAU, 360)
STATIONS = [(name, float(s_)) for name, s_, _ in CAST["trail_stations"]]
GY = 0.0                                   # the inequality profile stands in the plane y = 0
UX, UZ = 2.2, 1.6


def f(x):
    return 1.6 * np.exp(-(np.asarray(x, float) ** 2) / 1.5)


def df(x):
    return -2 * x / 1.5 * f(x)


def prof(x):
    x = np.asarray(x, float)
    return np.stack([UX * x, np.full_like(x, GY), UZ * f(x)], -1)


@scene(T.cut_ineq, T.cut_outro)
def s27_inequality(s):
    backdrop(s)
    ramp_cam = lambda t: (1.0, [4.0 * ramp(t, T.infinity, T.ineq - 0.3) * 4.0, 0.0, 0.0])
    cam = camera(
        (T.cut_ineq, (-160, 26, 1.6, 0.0, -0.3, 30, 0.4, 0.0, 0.0)),
        (T.tangency + 1.0, (-70, 40, 1.12, 0.1, -0.8, 26, 0, 0, 0)),
        (T.infinity - 0.2, (-60, 40, 1.12, 0.1, -0.8, 26, 0, 0, 0)),
        (T.infinity + 0.8, (-110, 22, 1.2, 0.0, -0.5, 30, 0, 0, 1.0)),
        (T.ineq - 0.3, (-120, 22, 1.2, 0.0, -0.5, 30, 0, 0, 1.0)),
        (T.ineq + 0.6, (-90, 6, 1.25, 0.0, -1.0, 60, 0.0, 0.0, 1.2)),
        (T.lovely, (-78, 12, 1.25, 0.0, -1.0, 60, 0.0, 0.0, 1.2)),
        (T.cut_outro, (-70, 16, 1.25, 0.0, -1.0, 60, 0.0, 0.0, 1.2)),
        follow=lambda t: (win(t, T.infinity + 0.3, T.ineq - 0.2, 0.6, 0.3), [16.0 * ramp(t, T.infinity, T.ineq - 0.3), 0.0, 0.3 * 16.0 * ramp(t, T.infinity, T.ineq - 0.3) + 0.6]),
    )
    phase1 = lambda t: 1 - ramp(t, T.infinity - 0.3, T.infinity + 0.3)
    phase2 = lambda t: win(t, T.infinity - 0.2, T.ineq + 0.2, 0.5, 0.5)
    phase3 = lambda t: ramp(t, T.ineq, T.ineq + 0.8)
    c_t = keys((T.at_most + 1.0, -0.95), (T.lovely, -0.55), (T.zero_price + 1.6, 1.2), default_ease=E)

    def frame(t):
        v = view().begin(cam(t))
        a1 = phase1(t)
        if a1 > 0.01:
            mountain(v, 1.0, a1)
            floor(v, 1.0, 0.55 * a1)
            wires(v, 1.0, 0.2 * a1)
            curve(v, np.column_stack(trail(ALL)), C.con, 6.0, a1)
            for i, (name, s_) in enumerate(STATIONS):
                g = ramp(t, T.tangency + 0.3 + 0.35 * i, T.tangency + 0.7 + 0.35 * i) * a1
                if g > 0.01:
                    q = np.array(trail(s_))
                    level(v, float(hill(*q)), C.text, 3.0, 0.7 * g)
                    bead(v, q, color=C.you if name == "max" else C.wrong, r=0.1)
        a2 = phase2(t)
        if a2 > 0.01:
            xs = np.linspace(-4, 26, 2)
            X, Y = np.meshgrid(xs, [-2.0, 2.0])
            v.mesh(X, Y, 0.3 * X, C.obj, alpha=0.55 * a2, ambient=0.6)
            for x in np.arange(-4, 27, 1.0):
                v.line([[x, -2, 0.3 * x], [x, 2, 0.3 * x]], C.bg, 1.2, 0.5 * a2)
            v.line([[-4, 0, -1.2 + 0.03], [26, 0, 7.8 + 0.03]], C.con, 6.0, a2)
            w = 16.0 * ramp(t, T.infinity, T.ineq - 0.3)
            v.dot([w, 0, 0.3 * w + 0.05], C.you, 0.12, ring=C.bg)
        a3 = phase3(t)
        if a3 > 0.01:
            floor(v, 0.0, 0.45 * a3)
            xs = np.linspace(-1.9, 1.9, 160)
            v.line(prof(xs), C.obj, 6.0, a3)
            c = float(c_t(t)) if t > T.at_most + 0.9 else -0.95
            wa = a3 * ramp(t, T.at_most - 0.2, T.at_most + 0.6)
            if wa > 0.01:
                wx = UX * c
                Y, Z = np.meshgrid([-1.6, 1.6], [0.0, 3.4])
                v.mesh(np.full_like(Y, wx), Y, Z, C.con, alpha=0.3 * wa, shade=False)
                v.line([[wx, -1.6, 0], [wx, 1.6, 0], [wx, 1.6, 3.4], [wx, -1.6, 3.4]], C.con, 3.0, wa, close=True)
                X, Y = np.meshgrid([wx, UX * 2.0], [-1.6, 1.6])
                v.mesh(X, Y, np.full_like(X, 0.01), C.wrong, alpha=0.25 * wa, shade=False)
                x_w = min(c, 0.0)
                v.dot(prof(x_w) + [0, 0, 0.04], C.you, 0.12, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ineq, T.cut_outro)]))
    m = s.manim(z=5, parallax=0.0)
    for i, (name, s_) in enumerate(STATIONS):
        q = np.array(trail(s_))
        pin(m, cam, [*q, hill(*q)], backed(lab(name, 28, C.you if name == "max" else C.wrong), 0.1, 0.85), T.tangency + 0.5 + 0.35 * i, T.infinity - 0.2, off=(0.0, 0.45))
    pin(m, cam, lambda t: [16.0 * ramp(t, T.infinity, T.ineq - 0.3), 0, 0.3 * 16.0 * ramp(t, T.infinity, T.ineq - 0.3)], backed(lab("climbs forever: no best point", 30, C.wrong), 0.1, 0.85), T.infinity + 0.6, T.ineq - 0.2, off=(0.0, 0.6))
    cw = lambda t: [UX * float(c_t(t)) if t > T.at_most + 0.9 else -UX * 0.95, 0.0, 3.4]
    pin(m, cam, cw, backed(tex("g", r"\le", "c", size=48, colors={0: C.con, 2: C.con}), 0.1, 0.85), T.at_most, T.cut_outro - 0.05, off=(0.0, 0.4))

    def price(t):
        c = float(c_t(t)) if t > T.at_most + 0.9 else -0.95
        v = abs(max(float(df(min(c, 0.0))), 0.0))
        xy, _ = cam(t).frame(np.array(prof(min(c, 0.0))) + [0, 0, 0.04])
        lbl = tex(r"\lambda", "=", f"{v:.1f}", size=46, colors={0: C.lam})
        return backed(lbl, 0.08, 0.85).move_to([xy[0] - 1.3, xy[1] + 0.5, 0]).set_opacity(win(t, T.at_most + 0.3, T.cut_outro, 0.5, 0.3))
    live(m, price, (T.at_most + 0.3, T.cut_outro - 0.05))
    h = s.manim(z=20, parallax=0.0)
    headline(h, backed(lab("tangency only makes a candidate", 32, C.text), 0.1, 0.85), T.tangency + 0.2, T.infinity - 0.2)
    headline(h, backed(sc("spend at most this much", 34, C.con), 0.1, 0.85), T.ineq + 0.4, T.karush - 0.2)
    stack(h, [(sc("William Karush, 1939", 32, C.ink), T.karush), (sc("Kuhn \\& Tucker, 1951", 32, C.ink), T.kt)], pos=(-6.75, 3.3), out=T.lovely)
    headline(h, backed(lab("a limit you aren't pressing against has price zero", 32, C.you), 0.1, 0.85), T.zero_price + 1.2, T.cut_outro - 0.2)
    curtain(s, a=False, b=True)
