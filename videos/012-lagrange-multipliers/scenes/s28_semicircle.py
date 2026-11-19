"""s28: the payoff. Dido's rope relaxes into a semicircle, and the multiplier turns out to be its radius: a length you can lay a stick along."""
from aion import *

from beats import T
from classic import *

RAD = 40 / np.pi


@scene(T.cut_outro, T.end)
def s28_semicircle(s):
    backdrop(s)
    world = s.manim(z=-10, opacity=key(T.last1 - 0.2, 1.0, 0.0, dur=1.3))
    shore(world, 0.0)
    m = s.manim(z=0)
    R = RAD * BU
    th = np.linspace(np.pi, 2 * np.pi, 160)
    semi = np.column_stack([R * np.cos(th), SHORE + R * np.sin(th)])
    box = resample(rect_rope(10, 20))
    u = keys((T.any_shape, 0.0), (T.semi + 0.2, 1.0), default_ease=E)
    gone = key(T.last1 + 1.0, 1.0, 0.0, dur=1.2)

    def rope(t):
        a = float(gone(t))
        if a < 0.01:
            return VGroup()
        k = float(u(t))
        P = box * (1 - k) + semi * k
        return VGroup(patch(P, a), tex(f"{area_of(P):.0f}", r"\text{ m}^2", size=60, colors={0: C.area, 1: C.area}).move_to([-1.0, 1.0, 0]).set_opacity(a))
    held = live(m, rope, (T.cut_outro, T.last1 + 1.1))
    m.remove(held[-1], at=T.last1 + 1.15)
    full = DashedVMobject(Circle(radius=R, color=C.con, stroke_width=3).move_to([0, SHORE, 0]), num_dashes=46)
    m.play(Create(full), at=T.a_circle - 0.2, dur=0.9, ease=E)
    m.play(FadeOut(full), at=T.semi + 0.9, dur=0.5)
    same = backed(lab("same bend everywhere", 34, C.text)).move_to([0, -2.6, 0])
    m.play(FadeIn(same), at=T.bend + 0.3, dur=0.5)
    m.play(FadeOut(same), at=T.a255 - 0.5, dur=0.4)
    better = backed(lab("27\\% more than the rectangle", 34, C.area)).move_to([0, -2.6, 0])
    m.play(FadeIn(better), at=T.quarter, dur=0.5)
    m.play(FadeOut(better), at=T.the_mult - 0.2, dur=0.4)
    a = np.radians(-52)
    tip = np.array([R * np.cos(a), SHORE + R * np.sin(a), 0.0])
    stick = Line([0, SHORE, 0], tip, color=C.lam, stroke_width=11)
    lam = backed(tex(r"\lambda", "=", "r", size=74, colors={0: C.lam, 2: C.lam})).move_to([-5.0, -0.3, 0])
    val = backed(tex(r"r", r"\approx", "12.7", r"\text{ m}", size=58, colors={0: C.lam, 2: C.lam})).move_to([5.0, -0.3, 0])
    m.play(Create(stick), at=T.radius, dur=0.8, ease=E)
    m.play(FadeIn(lam, scale=0.8), at=T.radius + 0.3, dur=0.6, ease="out_back")
    m.play(FadeIn(val, shift=0.08 * UP), at=T.d127, dur=0.6)
    m.play(Indicate(stick, color=C.lam, scale_factor=1.04), at=T.hands, dur=0.9)
    m.play(FadeOut(VGroup(stick, lam, val)), at=T.last1 - 0.2, dur=1.3)
    over = s.manim(z=2)
    r2 = 2.4
    arc = poly([[r2 * np.cos(v), 0.9 + r2 * np.sin(v)] for v in np.linspace(np.pi, 2 * np.pi, 90)], C.con, 6)
    edge = Line([-3.4, 0.9, 0], [3.4, 0.9, 0], color=C.axis, stroke_width=3)
    rad = Line([0, 0.9, 0], [r2 * np.cos(a), 0.9 + r2 * np.sin(a), 0], color=C.lam, stroke_width=8)
    over.play(Create(edge), Create(arc), Create(rad), at=T.last1 + 0.9, dur=1.2, ease=E)
    over.play(FadeIn(tex(r"\lambda", "=", "r", size=64, colors={0: C.lam, 2: C.lam}).move_to([2.6, -1.1, 0])), at=T.last1 + 1.6, dur=0.6, ease=E)
    title = Tex(r"\textbf{What Lagrange Multipliers Actually Are}", font_size=56, color=C.text).move_to([0, 2.7, 0])
    over.play(FadeIn(title, shift=0.1 * UP), at=T.last2 + 2.4, dur=0.9)
    curtain(s, a=True, b=True, dur=0.8)
