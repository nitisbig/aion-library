"""s02: the same question in many worlds. A fixed rope tries several shapes while its area changes, then rope, budget and steel."""
from aion import *

from beats import T
from cards import panel, twisted
from story import top_beach
from shots import E, SHORE, area_of, backdrop, beach_bg, curtain, lab, live, mix, poly, rect_rope, resample


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

    live(m, scene_now, (T.cut_question, T.fixed_rope - 0.3))

    def outline(t):
        u = float(k(t))
        i = min(int(u), 2)
        return S[i] * (1 - (u - i)) + S[i + 1] * (u - i)
    s.add(FramesLayer(top_beach(outline, SHORE), height=8.0, z=-10, during=[(T.cut_question, T.fixed_rope + 0.5)]))
    # three worlds, one question
    cover = Rectangle(width=15, height=9, fill_color=C.bg, fill_opacity=1, stroke_width=0)
    top = s.manim(z=5)
    top.play(FadeIn(cover), at=T.fixed_rope - 0.1, dur=0.45)
    cx = [-4.6, 0.0, 4.6]
    boxes = [panel(x, 0.1, 4.1, 4.6, a) for x, a in zip(cx, (C.con, C.area, C.ink))]
    rope = twisted(poly(rect_rope(10, 20), C.con, 6).scale_to_fit_width(3.0).move_to([cx[0], 0.45, 0]), 7, 40)
    coin = coins().move_to([cx[1], 0.25, 0])
    br = truss().move_to([cx[2], 0.25, 0])
    tags = [lab("rope", 34, C.con), lab("budget", 34, C.area), lab("steel", 34, C.ink)]
    for t_, x in zip(tags, cx):
        t_.move_to([x, -1.65, 0])
    beats_ = [T.fixed_rope, T.budget, T.bridge]
    for b, item, t_, at in zip(boxes, [rope, coin, br], tags, beats_):
        top.play(FadeIn(VGroup(b, item, t_), scale=0.84, shift=0.2 * UP), at=at, dur=0.55, ease="out_back")
    load = Arrow([cx[2], 1.75, 0], [cx[2], 0.72, 0], buff=0, color=C.wrong, stroke_width=6, tip_length=0.24)
    top.play(GrowArrow(load), at=T.steel - 0.5, dur=0.5)
    curtain(s)
