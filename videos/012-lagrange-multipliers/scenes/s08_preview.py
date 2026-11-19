"""s08: what the video will show, and the promise: the mysterious number can be measured with a stick."""
from aion import *

from beats import T
from cards import panel, twisted
from coast import coast
from shots import BEST, E, arrow, backdrop, bold, contour_mobs, curtain, lab, mp, p3, poly, rect_rope, tex, trail_mob, walker, hill_grad, trail_grad


@scene(T.cut_preview, T.cut_ch1)
def s08_preview(s):
    backdrop(s)
    coast(s, z=-60)
    s.solid(C.bg, z=-10, opacity=keys((T.concrete + 0.6, 1.0), (T.measure - 0.3, 0.0)))
    m = s.manim(z=0)
    xs = np.linspace(-4.95, 4.95, 4)
    boxes = [panel(x, 0.2, 3.05, 3.8, a) for x, a in zip(xs, (C.obj, C.con, C.lam, C.area))]
    a = VGroup(contour_mobs(width=1.2), trail_mob(3.5), walker(mp(BEST))).scale(0.345).move_to([xs[0], 0.2, 0])
    c = np.array([xs[1], 0.2])
    d = np.array([0.6, 0.8])
    t_ = np.array([d[1], -d[0]])
    b = VGroup(poly([c - 1.3 * t_, c + 1.3 * t_], C.tang, 4), arrow(c, c + 1.15 * d, C.obj), arrow(c, c - 0.8 * d, C.con), walker(c))
    e = tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=52, colors={0: C.obj, 2: C.lam, 3: C.con}).move_to([xs[2], 0.2, 0])
    r = rect_rope(10, 20) * 0.55 + [xs[3], -0.9]
    plot = VGroup(Polygon(*[p3(q) for q in r], fill_color=C.area, fill_opacity=0.4, stroke_width=0), twisted(poly(r, C.con, 5), 5, 30), Line(p3(r[0]) + LEFT * 0.4, p3(r[3]) + RIGHT * 0.4, color=C.sand, stroke_width=4)).scale_to_fit_width(2.6).move_to([xs[3], 0.2, 0])
    tags = ["the touch", "the arrows", "the method", "the examples"]
    ats = [T.pv_top, T.pv_arrow, T.pv_method, T.pv_solve]
    gone = VGroup()
    for x, box, art, tag, at in zip(xs, boxes, [a, b, e, plot], tags, ats):
        name = lab(tag, 32, C.text).move_to([x, -2.25, 0])
        m.play(FadeIn(VGroup(box, art, name), scale=0.84, shift=0.2 * UP), at=at, dur=0.55, ease="out_back")
        gone.add(box, art, name)
    m.play(FadeOut(gone), at=T.concrete - 0.5, dur=0.6)
    lam = tex(r"\lambda", size=170, color=C.lam).move_to([0, 0.6, 0])
    m.play(FadeIn(lam, scale=0.7), at=T.concrete, dur=0.7, ease="out_back")
    stick = Line([-1.9, -2.3, 0], [1.9, -2.05, 0], color=C.lam, stroke_width=11)
    m.play(lam.animate.scale(0.55).move_to([0, -1.25, 0]), at=T.measure - 0.1, dur=0.8, ease=E)
    m.play(Create(stick), at=T.measure + 0.2, dur=0.8, ease=E)
    curtain(s)
