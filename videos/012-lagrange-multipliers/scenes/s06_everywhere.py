"""s06: where those numbers live today: wings, budgets, networks, learning machines and heat."""
from aion import *

from beats import T
from cards import panel, tracked
from ch1 import backed, camera, pin, ramp
from intro3d import box, ground
from shots import tex, view, E, arrow, backdrop, bold, curtain, lab, mix, poly


def wing():
    x = np.linspace(0, 1, 60)
    t = 0.16 * (2.97 * np.sqrt(x) - 1.26 * x - 3.52 * x**2 + 2.84 * x**3 - 1.02 * x**4)
    camber = 0.09 * np.sin(np.pi * x)
    up, lo = np.column_stack([x, camber + t]), np.column_stack([x[::-1], (camber - t)[::-1]])
    P = (np.vstack([up, lo]) - [0.5, 0.05]) * 2.0
    g = VGroup(Polygon(*[[a, b, 0] for a, b in P], stroke_color=C.ink, stroke_width=3, fill_color=mix(C.ink, C.bg, 0.8), fill_opacity=1))
    for k, y in enumerate((-0.75, 0.68, 0.98)):
        g.add(poly([[u, y + 0.09 * np.exp(-3 * u**2) * (1 if y > 0 else -1)] for u in np.linspace(-1.15, 1.15, 30)], C.con, 2.4))
    return g


def pie():
    g = VGroup()
    fr = [0.42, 0.26, 0.2, 0.12]
    a = PI / 2
    for i, f in enumerate(fr):
        g.add(Sector(radius=0.95, start_angle=a, angle=-f * TAU, fill_color=mix(C.area, C.bg, 0.12 + i * 0.2), fill_opacity=1, stroke_color=C.bg, stroke_width=3))
        a -= f * TAU
    return g


def net():
    P = np.array([[-0.85, 0.55], [-0.85, -0.55], [0, 0.9], [0, 0], [0, -0.9], [0.85, 0.5], [0.85, -0.5]])
    E_ = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (3, 6), (4, 6)]
    g = VGroup(*[Line([*P[a], 0], [*P[b], 0], color=C.tang, stroke_width=2.6 + 2.4 * ((a + b) % 3 == 0)) for a, b in E_])
    g.add(*[Dot([*p, 0], radius=0.11, color=C.ink) for p in P])
    return g


def split():
    r = rng(4)
    a = r.normal([-0.45, 0.4], 0.24, (14, 2))
    b = r.normal([0.45, -0.4], 0.24, (14, 2))
    g = VGroup(Line([-1.0, -0.9, 0], [1.0, 0.9, 0], color=C.text, stroke_width=4))
    g.add(*[Dot([*p, 0], radius=0.065, color=C.con) for p in a], *[Dot([*p, 0], radius=0.065, color=C.obj) for p in b])
    return g


def gas():
    r = rng(9)
    g = VGroup(Square(2.0, color=C.ink, stroke_width=3))
    for p in r.uniform(-0.86, 0.86, (34, 2)):
        d = r.normal(size=2)
        d = d / np.linalg.norm(d) * r.uniform(0.1, 0.24)
        g.add(arrow(p, p + d, C.energy, width=2.2, tip=0.08))
    return g


GX = [0.0, 7.0, 14.0, 21.0, 28.0]
_r = rng(9)
GAS = (_r.uniform(0, TAU, (40, 3)), _r.uniform(0.7, 1.6, (40, 3)))
_r2 = rng(4)
CLOUD_A = _r2.normal([-0.7, 0.0, 1.6], [0.35, 0.5, 0.35], (26, 3))
CLOUD_B = _r2.normal([0.7, 0.0, 0.8], [0.35, 0.5, 0.3], (26, 3))
NODES = np.array([[-1.2, -0.8, 0.6], [-1.2, 0.8, 0.6], [0.0, -1.1, 1.4], [0.0, 0.0, 1.0], [0.0, 1.1, 1.4], [1.2, -0.6, 0.7], [1.2, 0.6, 2.0]])
EDGES = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (3, 6), (4, 6), (2, 3), (4, 3)]


def airfoil():
    x = np.linspace(0, 1, 40)
    t = 0.16 * (2.97 * np.sqrt(x) - 1.26 * x - 3.52 * x**2 + 2.84 * x**3 - 1.02 * x**4)
    cam_ = 0.09 * np.sin(np.pi * x)
    P = np.vstack([np.column_stack([x, cam_ + t]), np.column_stack([x[::-1], (cam_ - t)[::-1]])])
    return (P - [0.5, 0.0]) * 2.4


AF = airfoil()


def draw_wing(v, x0, t, a):
    ys = np.array([-1.6, 1.6])
    X = x0 + np.vstack([AF[:, 0], AF[:, 0]])
    Y = np.vstack([np.full(len(AF), ys[0]), np.full(len(AF), ys[1])])
    Z = 1.3 + np.vstack([AF[:, 1], AF[:, 1]])
    v.mesh(X, Y, Z, C.ink, alpha=a, ambient=0.5)
    v.line(np.column_stack([X[0], Y[0], Z[0]]), C.text, 1.6, 0.7 * a, close=True)
    for y in (-1.1, 0.0, 1.1):
        for h, sgn in ((0.42, 1), (0.85, 1), (-0.45, -1)):
            u = np.linspace(-2.2, 2.2, 90)
            z = 1.3 + h + sgn * 0.22 * np.exp(-2.2 * u**2) * (1 if sgn > 0 else 0.4)
            P = np.column_stack([x0 + u, np.full_like(u, y), z])
            v.line(P, C.con, 1.4, 0.35 * a)
            ph = (1.2 * float(t) + 0.37 * y + h) % 1.0
            j = int(ph * 80)
            v.line(P[j:j + 10], C.con, 3.2, a)


def draw_budget(v, x0, t, a):
    w = np.array([1.0, 0.7, 0.55, 0.4]) + 0.25 * np.sin(1.4 * float(t) + np.arange(4) * 1.7)
    h = 4.6 * w / w.sum()
    for i, hh in enumerate(h):
        box(v, [x0 - 1.35 + 0.9 * i, 0, hh / 2 * a], [0.62, 0.62, max(hh * a, 0.02)], C.area if i % 2 == 0 else C.obj, 1.0)


def draw_net(v, x0, t, a):
    N = NODES * [1.5, 1.4, 1.2] + [x0, 0, 0]
    for k, (i, j) in enumerate(EDGES):
        flow = 0.5 + 0.5 * np.sin(1.8 * float(t) + 1.3 * k)
        v.line([N[i], N[j]], C.tang, 2.4 + 5.0 * flow, (0.5 + 0.5 * flow) * a)
        u = (0.7 * float(t) + 0.29 * k) % 1.0
        v.dot(N[i] + u * (N[j] - N[i]), C.text, 0.05, ring=None)
    for p in N:
        v.dot(p, C.ink, 0.17, ring=C.bg)


def draw_learn(v, x0, t, a):
    for p in CLOUD_A:
        v.dot(p + [x0, 0, 0], C.con, 0.07, ring=None)
    for p in CLOUD_B:
        v.dot(p + [x0, 0, 0], C.obj, 0.07, ring=None)
    sa = ramp(t, T.learn + 0.4, T.learn + 1.2)
    if sa > 0.01:
        Yp, S = np.meshgrid([-1.5, 1.5], [-1.3, 1.3])
        n = np.array([0.7, 0.0, -0.4]) / np.linalg.norm([0.7, 0.0, -0.4])
        c = np.array([x0, 0, 1.2])
        tdir = np.array([0.4, 0.0, 0.7]) / np.linalg.norm([0.4, 0.0, 0.7])
        X = c[0] + S * tdir[0]
        Z = c[2] + S * tdir[2]
        v.mesh(X, Yp, Z, C.text, alpha=0.18 * sa, shade=False)
        v.line([[X[0, 0], -1.5, Z[0, 0]], [X[0, 0], 1.5, Z[0, 0]], [X[1, 0], 1.5, Z[1, 0]], [X[1, 0], -1.5, Z[1, 0]]], C.text, 2.0, 0.8 * sa, close=True)


def draw_heat(v, x0, t, a):
    c = np.array([x0, 0, 1.3])
    hw = 1.2
    K = np.array([[x, y, z] for z in (-hw, hw) for y in (-hw, hw) for x in (-hw, hw)]) + c
    for i, j in ((0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)):
        v.line([K[i], K[j]], C.ink, 2.2, 0.8 * a)
    ph, w = GAS
    for k in range(len(ph)):
        P = c + 1.05 * np.sin(w[k] * float(t) + ph[k])
        Q = c + 1.05 * np.sin(w[k] * (float(t) - 0.12) + ph[k])
        v.line([Q, P], C.energy, 2.0, 0.5 * a)
        v.dot(P, C.energy, 0.06, ring=None)


@scene(T.cut_everywhere, T.cut_nofig)
def s06_everywhere(s):
    backdrop(s)
    wide = (-72, 20, 0.42, 0.0, -1.4, 40, 14.0, 0, 1.2)
    near = lambda x, az=-62: (az, 20, 1.45, 0.0, -0.7, 30, x, 0, 1.3)
    cam = camera((T.cut_everywhere, wide), (T.every + 0.4, wide), (T.wings + 0.2, near(GX[0])), (T.econ + 0.2, near(GX[1], -66)),
                 (T.network + 0.2, near(GX[2], -60)), (T.learn + 0.2, near(GX[3], -70)), (T.heat + 0.2, near(GX[4], -64)), (T.cut_nofig, near(GX[4], -74)))
    draws = [draw_wing, draw_budget, draw_net, draw_learn, draw_heat]
    ats = [T.wings, T.econ, T.network, T.learn, T.heat]

    def frame(t):
        v = view().begin(cam(t))
        ground(v, -6, 34, -5, 5, 0.45)
        for x0, fn, at in zip(GX, draws, ats):
            a = 0.35 + 0.65 * ramp(t, at - 0.6, at)
            fn(v, x0, t, a * ramp(t, T.cut_everywhere + 0.3, T.called + 1.2))
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_everywhere, T.cut_nofig)]))
    m = s.manim(z=10, parallax=0.0)
    title = tracked("Lagrange multipliers", 62, C.lam).move_to([0, 2.95, 0])
    rule = Line([-3.4, 2.42, 0], [3.4, 2.42, 0], color=C.lam, stroke_width=2.5)
    m.play(FadeIn(title, shift=0.14 * UP), Create(rule), at=T.called + 0.2, dur=0.8, ease=E)
    m.play(VGroup(title, rule).animate.scale(0.6).move_to([0, 3.45, 0]), at=T.every + 0.4, dur=0.8, ease=E)
    p = s.manim(z=5, parallax=0.0)
    for x0, name, at, nxt in zip(GX, ("wings", "budgets", "networks", "learning", "heat"), ats, ats[1:] + [T.cut_nofig + 0.6]):
        pin(p, cam, [x0, -1.7, 0.0], backed(lab(name, 36, C.text), 0.1, 0.85), at + 0.1, min(float(nxt) + 0.1, float(T.cut_nofig) - 0.05), off=(0.0, -0.1))
        pin(p, cam, [x0, 0.0, 3.2], tex(r"\lambda", size=64, color=C.lam), at + 0.3, min(float(nxt) + 0.1, float(T.cut_nofig) - 0.05), off=(0.0, 0.1))
    curtain(s)
