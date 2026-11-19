"""s05: a nineteen-year-old writes to Euler, and thirty-three years later a machine's restrictions each get one unknown number."""
from aion import *

from beats import T
from cards import card, pop
from shots import E, backdrop, bold, curtain, lab, mix, poly, sc


def envelope():
    b = Rectangle(width=1.1, height=0.72, stroke_color=C.gold, stroke_width=2.5, fill_color=C.ink, fill_opacity=1)
    f = Polygon([-0.55, 0.36, 0], [0, -0.1, 0], [0.55, 0.36, 0], fill_color=C.sand, fill_opacity=1, stroke_color=C.gold, stroke_width=2.5)
    seal = Circle(radius=0.12, fill_color=C.tyrian, fill_opacity=1, stroke_color=C.gold, stroke_width=2).move_to([0, -0.08, 0])
    return VGroup(b, f, seal)


def machine():
    beam = RoundedRectangle(width=5.2, height=0.2, corner_radius=0.08, fill_color=C.area, fill_opacity=1, stroke_color=C.gold, stroke_width=2).move_to([0, 0.75, 0])
    pivot = Polygon([0, 0.68, 0], [-0.46, -0.1, 0], [0.46, -0.1, 0], fill_color=C.gold, fill_opacity=1, stroke_color=C.ember, stroke_width=2)
    base = RoundedRectangle(width=2.6, height=0.16, corner_radius=0.05, fill_color=C.muted, fill_opacity=1, stroke_width=0).move_to([0, -0.18, 0])
    left_r = Line([-2.3, 0.75, 0], [-2.3, -0.65, 0], color=C.ink, stroke_width=4)
    right_r = Line([2.3, 0.75, 0], [2.3, -0.3, 0], color=C.ink, stroke_width=4)
    left_m = RoundedRectangle(width=1.05, height=1.05, corner_radius=0.08, fill_color=C.plum, fill_opacity=1, stroke_color=C.gold, stroke_width=3).move_to([-2.3, -1.17, 0])
    right_m = RoundedRectangle(width=0.72, height=0.72, corner_radius=0.07, fill_color=C.tyrian, fill_opacity=1, stroke_color=C.gold, stroke_width=3).move_to([2.3, -0.66, 0])
    return VGroup(beam, pivot, base, left_r, right_r, left_m, right_m)


@scene(T.cut_lagrange, T.cut_everywhere)
def s05_lagrange(s):
    backdrop(s)
    m = s.manim(z=0)
    axis = Line([-6.2, -3.15, 0], [6.2, -3.15, 0], color=C.frame, stroke_width=C.thin + 0.8)
    x55, x88 = -3.4, 3.4
    ticks = VGroup(*[Line([x, -3.28, 0], [x, -3.02, 0], color=C.ink, stroke_width=3) for x in (x55, x88)])
    yrs = VGroup(sc("1755", 34, C.ink).move_to([x55, -3.62, 0]), sc("1788", 34, C.ink).move_to([x88, -3.62, 0]))
    m.play(Create(axis), FadeIn(ticks), FadeIn(yrs), at=T.turin + 0.2, dur=1.0, ease=E)

    a = card("lagrange", "Lagrange", "Turin, age 19", h=2.9, tilt=-1.5, pos=[-4.7, 0.75, 0])
    now = Dot([x55, -3.15, 0], radius=0.13, color=C.you)
    m.play(FadeIn(now, scale=0.4), at=T.y1755, dur=0.5, ease="out_back")
    b = card("euler", "Euler", "Berlin", h=2.9, tilt=1.5, pos=[4.7, 0.75, 0])
    pop(m, a, T.turin + 1.3)
    pop(m, b, T.euler)
    route = ArcBetweenPoints([-2.9, 1.1, 0], [2.9, 1.1, 0], angle=-0.7)
    trail = DashedVMobject(route.copy().set_stroke(C.gold, 3), num_dashes=30)
    env = envelope().scale(0.72).move_to(route.get_start())
    m.play(FadeIn(env, scale=0.7), at=T.euler + 0.5, dur=0.4, ease="out_back")
    m.play(MoveAlongPath(env, route), Create(trail), at=T.euler + 1.0, dur=1.7, ease=E)
    arc = poly([[0.95 * np.cos(u), -1.05 + 0.95 * np.sin(u)] for u in np.linspace(np.pi, 2 * np.pi, 60)], C.con, 5)
    shore = Line([-1.4, -1.05, 0], [1.4, -1.05, 0], color=C.sand, stroke_width=4)
    q = bold("?", 56, C.con).move_to([0, -1.55, 0])
    m.play(Create(arc), FadeIn(shore), FadeIn(q), at=T.dido_like, dur=0.7, ease=E)
    old = Group(a, b, env, trail, arc, shore, q)
    m.play(FadeOut(old), at=T.y1788 - 0.1, dur=0.6)
    m.play(now.animate.move_to([x88, -3.15, 0]), at=T.y1788 + 1.0, dur=1.5, ease=E)
    span = lab("33 years", 32, C.muted).move_to([0, -2.72, 0])
    m.play(FadeIn(span), at=T.y1788 + 0.1, dur=0.5)
    title = sc("M\\'ecanique analytique", 46, C.ink).move_to([0, 3.1, 0])
    m.play(FadeIn(title, shift=0.1 * UP), at=T.y1788 + 0.8, dur=0.6)
    pop(m, card("lagrange", "Lagrange", "aged 52", h=2.3, tilt=-1.5, pos=[-5.3, 0.9, 0]), T.y1788 + 0.5)
    mach = machine().shift(0.55 * UP)
    m.play(Create(mach), at=T.machines - 0.1, dur=1.5, ease=E)
    glow = VGroup(mach[0].copy(), mach[3].copy(), mach[4].copy()).set_color(C.con)
    m.play(FadeIn(glow), at=T.hold_back, dur=0.6)
    marks = VGroup(*[bold("?", 66, C.lam).move_to(p) for p in ([1.2, 1.85, 0], [-3.0, 0.45, 0], [3.0, 0.45, 0])])
    for i, mk in enumerate(marks):
        m.play(FadeIn(mk, scale=0.5), at=T.extra + 0.35 * i, dur=0.45, ease="out_back")
    curtain(s)
