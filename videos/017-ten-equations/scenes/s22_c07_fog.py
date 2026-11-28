"""c07_s01 · Foggy hill (hook). Storyboard: plan/scene_plan.md § c07_s01. Layout L2.

Opens on c06_s03's last frame (the hill's contour lines from above, a walker near the top), which gives way to the
chapter card. 'fog': the same hill in 3D (shaders/hill.frag, ray-marched; sims.loss), seen low over the walker's
shoulder, dark beyond a few steps. 'slopes': the slope under its feet, ∇L, points uphill; −∇L points down.
'step': it steps along −∇L, η = 0.25 (sims.descent_path, exact iterates), and feels again. 'gradient descent': the
fog lifts, the camera cranes up to show both valleys, the walker finishes in the deeper one, and the rule writes
in the right column. 'Cauchy' brings the name tag.
"""
import math

import numpy as np
from aion import *

import ch6
import ch7
from beats import T
from kit import P3, RC, X0, Y1, add_rail, chapter_card, glow, mix, glimpse, polyline, shade, smooth01, tag_under, tex



def _carry(s):
    t0 = float(s.start)
    op = fade(t0 - 5, dur=0.1, out=t0 + 0.2, out_dur=0.6)
    cs = ch6.loss_contours()
    lv = np.array([c[0] for c in cs])
    g = VGroup()
    for l, pts in cs:                                       # exactly as c06_s03 drew them
        k = (l - lv.min()) / (lv.max() - lv.min())
        g.add(polyline(pts, mix(C.descent, C.light, 0.25 * (1 - k)), 1.6, 0.85 - 0.45 * k))
    s.manim(z=13, parallax=0.0, opacity=op).add(g)
    glow(s, C.descent, z=14, k=0.7, parallax=0.0, opacity=op).add(
        Dot(P3(*(ch7.PATH[0] * ch6.LS)), radius=0.08, color=C.light))


cam_at = ch7.fog_cam


def _arrow(cam, w, sign, color, op, lab):
    """An arrow along ±∇L on the ground at the walker (direction from the slope, length nominal)."""
    import sims as sm
    g = np.array(sm.loss_grad(*w))
    u = sign * g / max(np.linalg.norm(g), 1e-9)
    a, b = cam.project(ch7.on_hill(np.array([w, w + 0.75 * u]), lift=0.04))
    if np.isnan(a).any() or np.isnan(b).any():
        return VGroup()
    ar = Arrow(P3(*a), P3(*b), buff=0, stroke_width=4, color=color, tip_length=0.18,
               max_tip_length_to_length_ratio=0.35).set_opacity(op)
    d = (b - a) / max(np.linalg.norm(b - a), 1e-9)
    return VGroup(ar, tex(lab, 34, color).move_to(P3(*(b + 0.32 * d + 0.25 * np.array([-d[1], d[0]])))).set_opacity(op))


@scene(T.c07_s01, T.c07_s02)
def s22_c07_fog(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_fg, t_sl, t_st, t_gd, t_ca = (T.c07_s01_fog, T.c07_s01_slopes, T.c07_s01_step, T.c07_s01_gradient_descent,
                                    T.c07_s01_cauchy)
    _carry(s)
    chapter_card(s, 7, at=t0 + 0.45, out=t_fg - 0.5)
    add_rail(s, 7, opacity=fade(t0 + 0.4, dur=0.8), busy=True)

    # the hill in fog
    fog = lambda t: 1.0 - float(smooth01((t - float(t_gd) + 0.1) / 1.6))
    s.shader("hill.frag", z=0, parallax=0.0, animated=True,
             **ch7.hill_uniforms(cam_at, mode=0, opacity=fade(t_fg - 0.5, dur=1.0), fog=fog,
                                 walker=lambda t: ch7.walker_xy(t)[0], fr=0.95))

    # the walker and its path
    w_op = fade(t_fg - 0.2, dur=0.8)

    def walker(t):
        cam = cam_at(t)
        w, _ = ch7.walker_xy(t)
        p = cam.project(ch7.on_hill(w, lift=0.05))[0]
        return Dot(P3(*p), radius=0.09, color=C.light, fill_opacity=float(w_op(t)))

    def path(t):
        tr = ch7.trail(t)
        if len(tr) < 2:
            return VGroup()
        cam = cam_at(t)
        q = cam.project(ch7.on_hill(tr, lift=0.03))
        return polyline([tuple(v) for v in q if not np.isnan(v).any()], C.light, 2.6, 0.85)
    s.manim(z=4, parallax=0.0).redraw(path, during=(t_st, s.end))
    glow(s, C.light, z=6, k=0.9, parallax=0.0).redraw(walker, during=(t_fg - 0.3, s.end))

    # the slope under its feet: ∇L uphill, −∇L downhill (following the walker while it feels its way)
    up_op = fade(t_sl - 0.1, dur=0.5, out=t_st - 0.2, out_dur=0.5)
    dn_op = fade(t_sl + 1.2, dur=0.5, out=t_gd - 0.2, out_dur=0.5)
    s.manim(z=5, parallax=0.0).redraw(
        lambda t: _arrow(cam_at(t), ch7.walker_xy(t)[0], 1, C.muted, float(up_op(t)), r"\nabla L"),
        during=(t_sl - 0.3, t_st + 0.4))
    glow(s, C.descent, z=5, k=0.5, parallax=0.0).redraw(
        lambda t: _arrow(cam_at(t), ch7.walker_xy(t)[0], -1, C.descent, float(dn_op(t)), r"-\nabla L"),
        during=(t_sl + 1.0, t_gd + 0.4))

    # the rule, in the right column
    hud = s.manim(z=50, parallax=0.0)
    e = Eqn(r"\theta\leftarrow\theta-\eta\,\nabla L(\theta)", colors={r"\nabla L": C.descent, r"\eta": C.text})
    e.scale(1.05).move_to(P3(RC, 1.55))
    tags = VGroup(tag_under(e, r"\eta", "position", C.muted).align_to(e, LEFT),     # under the first θ
                  tag_under(e, r"\eta", "step size", C.muted).align_to(e.part(r"\eta"), RIGHT).shift(0.12 * RIGHT),
                  tag_under(e, r"\nabla L", "slope", C.descent))
    hud.play(Write(e), at=t_gd + 1.9, dur=1.1)                       # once the hill has moved left of the column
    hud.play(FadeIn(tags, shift=0.06 * UP, lag_ratio=0.25), at=t_gd + 2.6, dur=0.9)
    glimpse(s, "cauchy", t_ca, C.descent)
