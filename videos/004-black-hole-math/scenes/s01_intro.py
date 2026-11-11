"""s01 intro: the promise (one equation), the wrong intuition (the arc), the map (one ray → one pixel at a time)."""
from aion import *

from beats import T
from shots import disk_edge, glow_fx, hero, scan_tint


def path(pts, **kw):
    m = VMobject(**kw)
    m.set_points_smoothly([[x, y, 0.0] for x, y in pts])
    return m


@scene(T.cut_intro, T.cut_ch1)
def s01_intro(s):
    # the image un-builds itself on "one pixel at a time"
    hero(s, u_reveal=key(T.pixel - 0.5, 1.0, 0.0, dur=2.3, ease="easy_ease", lead=0), u_scanTint=scan_tint(1.5))

    # ── the promise: one equation, shown unexplained ──
    eq_layer = s.manim(fx=[glow_fx(C.text, 0.45)])            # crisp from the start: a tight halo, no blur
    eq = Eqn(r"u'' + u = \frac{3GM}{c^2}\,u^2", colors={"u": C.light, r"\frac{3GM}{c^2}": C.mass}, size=58)
    eq.move_to([3.9, 2.55, 0])
    eq_layer.play(FadeIn(eq, shift=0.25 * UP), at=T.one_equation, dur=1.2)
    eq_layer.play(Indicate(eq, color=C.text, scale_factor=1.08), at=T.read, dur=1.2)
    eq_layer.play(FadeOut(eq), at=T.stranger - 1.6, dur=0.9)

    # ── the wrong intuition: "a second ring, standing upright behind the hole" ──
    m = s.manim(fx=[glow_fx(C.text, 0.8)])
    edge = disk_edge(T.arc)                               # camera is at rest: the curve holds still
    top, bottom = edge[4:177], edge[184:357]
    arc = path(top, stroke_color=C.text, stroke_width=C.thin + 1)
    m.play(Create(arc), at=T.arc, dur=1.5, ease="easy_ease")

    apex = top[np.argmax(top[:, 1])]
    ghost = DashedVMobject(Circle(radius=apex[1] * 0.985, color=C.newton, stroke_width=C.thin), num_dashes=64)
    ghost.move_to([apex[0], 0.0, 0.0])
    m.play(FadeIn(ghost, scale=0.96), at=T.second_ring, dur=0.9)
    m.play(FadeOut(ghost, scale=1.06), at=T.is_not, dur=0.45)

    # "only one flat disk": the same outline closes into a single ring
    rest = path(bottom, stroke_color=C.text, stroke_width=C.thin + 1)
    m.play(Create(rest), at=T.one_disk, dur=1.8, ease="easy_ease")
    m.play(FadeOut(arc), FadeOut(rest), at=T.single_ray - 1.6, dur=0.9)

    # ── the map: a single ray of light ──
    ray_layer = s.manim(fx=[glow_fx()])
    ray = Line([-7.4, -3.2, 0], [7.4, -3.2, 0], color=C.light, stroke_width=C.stroke)
    ray_layer.play(Create(ray), at=T.single_ray, dur=2.2, ease="easy_ease", lead=0)
