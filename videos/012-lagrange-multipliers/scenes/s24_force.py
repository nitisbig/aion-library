"""s24: lambda is a force. A bead settles at the bottom of a hoop standing in 3D, and lambda times the gradient of g is exactly the hoop's push."""
from aion import *

from beats import T
from ch1 import *

R = 2.0
ZC = 3.1                                  # the hoop's center height
TH = np.linspace(0, TAU, 240)
REST = np.array([0.0, 0.0, ZC - R])


@scene(T.cut_force, T.cut_gas)
def s24_force(s):
    backdrop(s)
    cam = camera(
        (T.cut_force, (-60, 18, 1.0, 0.0, -0.4, 30, 0, 0, ZC - 0.3)),
        (T.gravity, (-78, 12, 1.15, 0.0, -0.4, 30, 0, 0, ZC - 0.6)),
        (T.that_push, (-88, 8, 1.0, 0.0, -0.45, 40, 0, 0, ZC - 0.4)),
        (T.cut_gas, (-110, 14, 0.98, 0.0, -0.45, 40, 0, 0, ZC - 0.4)),
    )
    t0 = float(T.bead) - 0.2

    def angle(t):
        tau = max(0.0, float(t) - t0)
        return 0.95 * np.exp(-0.62 * tau) * np.cos(2.5 * tau)

    def frame(t):
        v = view().begin(cam(t))
        floor(v, 0.0, 0.5)
        hp = ramp(t, T.physics + 0.2, T.physics + 1.4)
        n = max(2, int(len(TH) * hp))
        P = np.column_stack([R * np.sin(TH[:n]), np.zeros(n), ZC - R * np.cos(TH[:n])])
        v.line(P * [1, 1, 1] + [0, 0.06, 0], C.bg, 11.0)
        v.line(P, C.con, 8.0)
        if hp > 0.99:
            v.line([[0, 0, ZC + R], [0, 0, ZC + R + 0.6]], C.muted, 3.0)
        if t > t0:
            a = angle(t)
            b = np.array([R * np.sin(a), -0.05, ZC - R * np.cos(a)])
            v.line([b * [1, 1, 0], b], C.muted, 1.2, 0.5)
            v.dot(b, C.you, 0.16, ring=C.bg)
        ga = ramp(t, T.gravity + 1.0, T.gravity + 1.5)
        if ga > 0.01:
            v.arrow(REST + [0, -0.2, 0], REST + [0, -0.2, -1.25 * ga], C.obj, width=6.0, tip=0.26)
        pa = ramp(t, T.push_back + 0.7, T.push_back + 1.2)
        if pa > 0.01:
            v.arrow(REST + [0, -0.2, 0], REST + [0, -0.2, 1.25 * pa], C.lam, width=6.0, tip=0.26)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_force, T.cut_gas)]))
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, REST + [0, -0.2, -1.25], tex("m", "g", size=48, color=C.obj), T.gravity + 1.2, T.cut_gas - 0.05, off=(0.45, 0.1))
    pin(m, cam, REST + [0, -0.2, 1.25], tex(r"\lambda", r"\nabla g", size=50, colors={0: C.lam, 1: C.con}), T.that_push, T.cut_gas - 0.05, off=(0.55, 0.0))
    pin(m, cam, [R, 0, ZC], backed(lab("the hoop", 28, C.con), 0.1, 0.85), T.physics + 1.0, T.minimize, off=(0.9, 0.0))
    h = s.manim(z=20, parallax=0.0)
    stack(h, [(tex(r"\min\;", "U=mgz", size=46, colors={1: C.obj}), T.minimize), (tex("x^2+(z-z_0)^2", "=", "R^2", size=46, colors={0: C.con, 2: C.con}), T.minimize + 0.4)], pos=(-6.75, 3.3))
    headline(h, backed(tex(r"\vec F_{\text{hoop}}", "=", r"\lambda", r"\nabla g", size=60, colors={2: C.lam, 3: C.con}), 0.12, 0.85), T.that_push, T.cut_gas - 0.3, y=3.4)
    headline(h, backed(lab("a constraint is something pushing back", 30, C.you), 0.1, 0.85), T.physically + 0.2, T.cut_gas - 0.3, y=2.55)
    stack(h, [(sc("Lagrange, M\\'ecanique analytique, 1788", 30, C.ink), T.lag_world + 0.4)], pos=(6.75, -3.3), edge=DR)
    curtain(s, a=True, b=True)
