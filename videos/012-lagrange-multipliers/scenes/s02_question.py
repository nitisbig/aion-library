"""s02: the same question in many worlds. A fixed rope tries several shapes while its area changes, then rope, budget and steel."""
from aion import *

from beats import T
from cards import panel, twisted
from story import top_beach
from intro3d import box, cylinder, ground, prism
from ch1 import backed, camera, pin, ramp
from shots import view, E, SHORE, area_of, backdrop, beach_bg, curtain, lab, live, mix, poly, rect_rope, resample


def shapes():
    a = resample(rect_rope(6, 28))
    b = resample(np.array([[-14, 0], [0, -14.283], [14, 0]]) * 0.24 + [0, SHORE])
    c = resample(rect_rope(14, 12))
    d = resample(rect_rope(10, 20))
    return [a, b, c, d]


def truss():
    xs = np.linspace(-1.5, 1.5, 7)
    top, bot = 0.32, -0.26
    g = VGroup(Line([xs[0], bot, 0], [xs[-1], bot, 0], color=C.ink, stroke_width=3), Line([xs[1], top, 0], [xs[-2], top, 0], color=C.ink, stroke_width=3))
    for i in range(6):
        a = [xs[i], bot if i % 2 == 0 else top, 0]
        b = [xs[i + 1], top if i % 2 == 0 else bot, 0]
        g.add(Line(a, b, color=C.ink, stroke_width=2.4))
    g.add(Polygon([-1.5, bot, 0], [-1.72, bot - 0.32, 0], [-1.28, bot - 0.32, 0], color=C.muted, stroke_width=2), Polygon([1.5, bot, 0], [1.72, bot - 0.32, 0], [1.28, bot - 0.32, 0], color=C.muted, stroke_width=2))
    return g


def coins():
    g = VGroup()
    for i in range(7):
        g.add(Ellipse(width=1.5, height=0.46, fill_color=mix(C.area, C.bg, 0.15 if i % 2 else 0.32), fill_opacity=1, stroke_color=C.bg, stroke_width=2).move_to([0, -0.7 + i * 0.22, 0]))
    return g


@scene(T.cut_question, T.cut_fermat)
def s02_question(s):
    backdrop(s)
    m = s.manim(z=0)
    S = shapes()
    k = keys((T.human + 0.4, 0.0), (T.human + 2.0, 1.0), (T.best_we - 0.1, 1.0), (T.best_we + 1.3, 2.0), (T.fixed_rope - 1.5, 2.0), (T.fixed_rope - 0.5, 3.0))
    vmax = 254.65
    frame_bar = Rectangle(width=0.5, height=3.6, fill_color=C.walnut, fill_opacity=0.82, stroke_color=C.gold, stroke_width=2.5).move_to([5.9, -0.45, 0])
    tag = lab("area", 30, C.walnut).next_to(frame_bar, DOWN, buff=0.16)
    m.add(frame_bar, tag)

    def scene_now(t):
        u = float(k(t))
        i = min(int(u), 2)
        P = S[i] * (1 - (u - i)) + S[i + 1] * (u - i)
        h = 3.6 * area_of(P) / vmax
        bar = Rectangle(width=0.5, height=max(h, 0.01), fill_color=C.gold, fill_opacity=1, stroke_width=0).move_to([5.9, -2.25 + h / 2, 0])
        return VGroup(bar)

    hb = live(m, scene_now, (T.cut_question, T.fixed_rope - 0.3))
    m.remove(hb[-1], at=T.fixed_rope - 0.3)

    def outline(t):
        u = float(k(t))
        i = min(int(u), 2)
        return S[i] * (1 - (u - i)) + S[i + 1] * (u - i)
    s.add(FramesLayer(top_beach(outline, SHORE), height=8.0, z=-10, during=[(T.cut_question, T.fixed_rope + 0.5)]))
    # three worlds, one question: one 3D gallery the camera glides along
    s.solid(C.bg, z=-8, opacity=keys((T.fixed_rope - 0.15, 0.0), (T.fixed_rope + 0.3, 1.0)))
    m.play(FadeOut(VGroup(frame_bar, tag)), at=T.fixed_rope - 0.6, dur=0.3, lead=0)
    XS = (-4.6, 0.0, 4.6)
    cam = camera((T.fixed_rope, (-72, 26, 1.7, 0.0, -1.3, 30, XS[0], 0, 0.5)), (T.budget + 0.2, (-80, 24, 1.55, 0.0, -1.3, 30, XS[1] - 1.6, 0, 0.5)),
                 (T.bridge + 0.3, (-86, 22, 1.45, 0.0, -1.3, 30, XS[2] - 2.2, 0, 0.6)), (T.cut_fermat, (-92, 24, 1.1, 0.0, -1.2, 30, 0.0, 0, 0.6)))
    grow = [lambda t, a=a: ramp(t, a - 0.1, a + 0.7) for a in (T.fixed_rope, T.budget, T.bridge)]

    def gallery(t):
        v = view().begin(cam(t))
        ground(v, -9, 9, -4, 4, 0.5)
        g = grow[0](t)
        if g > 0.01:
            r = np.array([[-1.2, 0.6], [-1.2, -1.4], [1.2, -1.4], [1.2, 0.6]]) * [g, 1] + [XS[0], 0]
            X, Y = np.meshgrid([r[0, 0], r[2, 0]], [r[1, 1], r[0, 1]])
            v.mesh(X, Y, np.full_like(X, 0.004), C.area, alpha=0.3 * g, shade=False)
            box(v, [XS[0], -0.4, 0.45 * g], [2.4 * g, 2.0, 0.9 * g], C.area, 0.35 * g)
            v.line([[XS[0] - 2.2, 0.6, 0.01], [XS[0] + 2.2, 0.6, 0.01]], C.axis, 3.0, g)
            v.line(np.column_stack([r, np.full(4, 0.03)]), C.con, 6.0, g)
        g = grow[1](t)
        if g > 0.01:
            for i in range(9):
                z = 0.17 * i
                if z < 1.6 * g:
                    cylinder(v, [XS[1] + 0.03 * np.sin(2.1 * i), 0.03 * np.cos(1.7 * i), z], 0.75, 0.15, C.area if i % 2 else C.obj, 1.0)
        g = grow[2](t)
        if g > 0.01:
            xs = np.linspace(XS[2] - 1.8, XS[2] + 1.8, 7)
            for y in (-0.55, 0.55):
                bot = [[x, y, 0.35] for x in xs]
                top = [[x, y, 0.35 + 0.9 * g] for x in xs[1:-1]]
                v.line(bot, C.ink, 4.0)
                v.line(top, C.ink, 4.0)
                for i in range(6):
                    a = [xs[i], y, 0.35] if i % 2 == 0 else [xs[i], y, 0.35 + 0.9 * g]
                    b = [xs[i + 1], y, 0.35 + 0.9 * g] if i % 2 == 0 else [xs[i + 1], y, 0.35]
                    if 0 < i + 1 < 6 or i % 2:
                        v.line([a, b], C.ink, 2.8)
            for x in xs:
                v.line([[x, -0.55, 0.35], [x, 0.55, 0.35]], C.ink, 1.6, 0.7)
            for x in (xs[0], xs[-1]):
                prism(v, [x, 0, 0], 0.6, 0.35, 1.4, C.muted)
            la = ramp(t, T.steel - 0.4, T.steel + 0.2)
            if la > 0.01:
                v.arrow([XS[2], 0, 2.6], [XS[2], 0, 2.6 - 1.2 * la], C.wrong, width=6.0, tip=0.26)
        return v.rgba()
    s.add(FramesLayer(gallery, height=8.0, z=-5, during=[(T.fixed_rope - 0.2, T.cut_fermat)]))
    tags = s.manim(z=5, parallax=0.0)
    for x, name, col, at in zip(XS, ("rope", "budget", "steel"), (C.con, C.area, C.ink), (T.fixed_rope, T.budget, T.bridge)):
        pin(tags, cam, [x, -1.6, 0.0], backed(lab(name, 34, col), 0.1, 0.85), at + 0.3, T.cut_fermat - 0.05, off=(0.0, -0.35))
    curtain(s)
