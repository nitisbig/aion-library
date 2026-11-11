"""s05c: one equation, three fates. A six-second bridge that puts the shadow back on screen for chapter 5."""
from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_eq, glow_fx, ray_path, starfield

A, B = T.cut_ready, T.cut_ch5
HC, K = np.array([0.3, -0.3, 0.0]), 0.55


@scene(A, B)
def s05c_ready(s):
    starfield(s, opacity=1.0 - fade(B - 1.4, dur=1.2, lead=0))
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim(z=3)
    eq = badge_eq().scale(1.6).move_to([0, 2.85, 0])
    m.play(FadeIn(eq, shift=0.2 * DOWN), at=T.everything + 0.9, dur=0.7)

    # three fates, drawn once more round one hole
    hole = Circle(radius=K, stroke_color=C.horizon, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0).move_to(HC)
    m.play(FadeIn(hole), at=A + 0.2, dur=0.6)
    bc = S.critical_b(1.0)
    for i, (b, role, layer) in enumerate(((3.3, "light", glow), (bc * (1 + 1e-9), "ring", m), (-1.6, "bad", m))):
        pts, _ = ray_path(b, HC, K, r_far=13.5, half=(6.9, 2.4))
        ray = VMobject(stroke_color=getattr(C, role), stroke_width=C.thin + 1).set_points_as_corners(pts)
        layer.play(Create(ray), at=T.everything + 1.9 + 0.35 * i, dur=1.1, ease="easy_ease")
        layer.play(FadeOut(ray), at=B - 1.5, dur=0.7)

    # what chapter 5 starts from: the shadow and the dashed horizon
    edge = Circle(radius=bc * K, color=C.shadow, stroke_width=C.thin + 1).move_to(HC)
    inner = DashedVMobject(Circle(radius=K, color=C.horizon, stroke_width=C.thin + 1), num_dashes=28).move_to(HC)
    m.play(Create(edge), at=B - 1.6, dur=1.0)
    m.play(FadeOut(hole), FadeIn(inner), FadeOut(eq), at=B - 1.2, dur=0.8)
