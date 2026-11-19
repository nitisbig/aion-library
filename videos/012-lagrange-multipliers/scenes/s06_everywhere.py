"""s06: where those numbers live today: wings, budgets, networks, learning machines and heat."""
from aion import *

from beats import T
from cards import panel, tracked
from shots import E, arrow, backdrop, bold, curtain, lab, mix, poly


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


@scene(T.cut_everywhere, T.cut_nofig)
def s06_everywhere(s):
    backdrop(s)
    m = s.manim(z=0)
    title = tracked("Lagrange multipliers", 62, C.lam).move_to([0, 2.95, 0])
    rule = Line([-3.4, 2.42, 0], [3.4, 2.42, 0], color=C.gold, stroke_width=3)
    m.play(FadeIn(title, shift=0.14 * UP), Create(rule), at=T.called + 0.2, dur=0.8, ease=E)
    xs = np.linspace(-5.3, 5.3, 5)
    items = [(wing(), "wings", T.wings, C.con), (pie(), "budgets", T.econ, C.area), (net(), "networks", T.network, C.tang), (split(), "learning", T.learn, C.obj), (gas(), "heat", T.heat, C.energy)]
    for x, (art, name, at, accent) in zip(xs, items):
        box = panel(x, -0.45, 2.45, 3.5, accent)
        art.scale(0.92).move_to([x, -0.05, 0])
        tag = lab(name, 32, C.text).move_to([x, -1.72, 0])
        m.play(FadeIn(VGroup(box, art, tag), scale=0.82, shift=0.2 * UP), at=at, dur=0.55, ease="out_back")
    curtain(s)
