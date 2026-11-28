"""c06_s02 · Gamma (equation). Storyboard: plan/scene_plan.md § c06_s02. Layout L2.

Opens on c06_s01's last frame. The clocks and tick lines leave; the triangle rises into the right column, and
Pythagoras on it, (c Δt′)² = (c Δt)² + (v Δt′)², becomes Δt′ = Δt / √(1 − v²/c²). 'everyday': γ against v/c
draws flat at 1 (car, jet and the ISS all sit there: γ − 1 < 10⁻⁹) and 'without limit' it climbs the wall at the
speed of light, past 0.9 c and 0.99 c. 'Muons': the same 90 muons are born near 15 km in two columns; on the left
their clocks run at the normal rate and they decay after about 0.66 km; on the right their clocks are slowed ten
times (γ = 10 at 0.995 c) and about one in nine reaches the ground (each decay distance is −ln u times the mean
distance, with the same u in both columns; ch6.muon_draw).
"""
import math

import numpy as np
from aion import *

import ch6
from beats import T
from kit import chapter_backdrop, COL, P3, RC, add_rail, fit, glow, polyline, sans, smooth01, tag_under, tex, tint

TRI_TO, TRI_K = P3(RC, 2.05), 0.55               # where the triangle settles in the right column, and its scale


def _carry(s, out):
    """c06_s01's last frame, minus the triangle: the clock at rest, the dimmed zig-zag, the tick lines and counts."""
    t0 = float(s.start)
    op = fade(t0 - 5, dur=0.1, out=out, out_dur=0.7)
    m = s.manim(z=5, opacity=op)
    m.add(ch6.ground(), ch6.mirrors(ch6.LX))
    s.manim(z=4, opacity=op).redraw(lambda t: Line(P3(ch6.LX, ch6.YB), P3(ch6.LX, ch6.YT), stroke_color=C.light,
                                                   stroke_width=2.2, stroke_opacity=0.5), during=(s.start, out + 0.8))
    glow(s, C.light, z=9, k=1.0, opacity=op).redraw(
        lambda t: Dot(P3(ch6.LX, ch6.rest_y(t, ch6.T_REST)), radius=0.08, color=C.light), during=(s.start, out + 0.8))
    glow(s, C.dilation, z=6, k=0.35, opacity=op).redraw(
        lambda t: polyline(ch6.zigzag(t), C.dilation, 3.0, 0.35), during=(s.start, out + 0.8))
    s.manim(z=12, opacity=op).redraw(lambda t: VGroup(ch6.tick_rows(t), ch6.row_counts(t)), during=(s.start, out + 0.8))
    m.add(ch6.row_labels())


def _gamma_axes():
    g = VGroup(Line(ch6.g_pt(0, 0), ch6.g_pt(1.04, 0), stroke_color=C.axis, stroke_width=2),
               Line(ch6.g_pt(0, 0), ch6.g_pt(0, ch6.GMAX + 0.3), stroke_color=C.axis, stroke_width=2))
    for gm in (1, 2, 4, 6, 8):
        p = ch6.g_pt(0, gm)
        g.add(Line(p + LEFT * 0.08, p + RIGHT * 0.08, stroke_color=C.axis, stroke_width=1.6),
              tex(f"{gm}", 26, C.muted).next_to(p, LEFT, buff=0.15))
    for b, lab in ((0.5, "0.5"), (1.0, "1")):
        p = ch6.g_pt(b, 0)
        g.add(Line(p + DOWN * 0.08, p + UP * 0.08, stroke_color=C.axis, stroke_width=1.6),
              tex(lab, 26, C.muted).next_to(p, DOWN, buff=0.14))
    g.add(tex(r"v/c", 30, C.muted).next_to(ch6.g_pt(1.04, 0), RIGHT, buff=0.15),
          tex(r"\gamma", 36, C.dilation).next_to(ch6.g_pt(0, ch6.GMAX + 0.3), UP, buff=0.1))
    wall = DashedLine(ch6.g_pt(1, 0), ch6.g_pt(1, ch6.GMAX + 0.3), stroke_color=C.muted, stroke_width=1.8,
                      dash_length=0.1)
    wl = sans("speed of light", 22, C.muted).next_to(ch6.g_pt(1, ch6.GMAX + 0.3), UP, buff=0.12)
    return g, VGroup(wall, wl)


_BETA = 1 - np.geomspace(1, 1 - 0.99215, 400)        # dense toward the wall; γ(0.99215) ≈ 8


def _curve(t, t_a, t_b, op):
    """γ(v/c) drawn by v/c: the flat part over the first 55 % of the time, the climb after."""
    a = float(op(t))
    u = float(np.clip((t - t_a) / (t_b - t_a), 0, 1))
    if u <= 0 or a < 0.01:
        return VGroup()
    bmax = 0.8 * float(smooth01(u / 0.55)) if u < 0.55 else 0.8 + (0.99215 - 0.8) * float(smooth01((u - 0.55) / 0.45))
    b = _BETA[_BETA <= bmax]
    if len(b) < 2:
        return VGroup()
    gm = 1 / np.sqrt(1 - b * b)
    return polyline([ch6.g_pt(x, y)[:2] for x, y in zip(b, gm)], C.dilation, 4, a)


@scene(T.c06_s02, T.c06_s03)
def s20_c06_gamma(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 6)
    add_rail(s, 6)
    t0 = float(s.start)
    t_tg, t_ev, t_wl, t_mu, t_de, t_mk = (T.c06_s02_triangle, T.c06_s02_everyday, T.c06_s02_without_limit,
                                          T.c06_s02_muons, T.c06_s02_decay, T.c06_s02_make_it)
    _carry(s, t0 + 0.25)

    # the triangle rises into the right column
    tri = ch6.triangle()
    c0 = VGroup(tri["hyp"], tri["vert"], tri["base"], tri["labels"]).get_center()
    tri_out = t_mu - 0.6
    hl = glow(s, C.dilation, z=8, k=0.9)
    hl.add(tri["hyp"])
    tm = s.manim(z=9)
    tm.add(tri["vert"], tri["base"], tri["labels"])
    for layer, mob in ((hl, tri["hyp"]), (tm, tri["vert"]), (tm, tri["base"]), (tm, tri["labels"])):
        layer.play(mob.animate.scale(TRI_K, about_point=c0).shift(TRI_TO - c0), at=t0 + 0.3, dur=1.3)
        layer.play(FadeOut(mob), at=tri_out, dur=0.5)

    # Pythagoras on it, solved for the moving clock's time
    hud = s.manim(z=50, parallax=0.0)
    e1 = Eqn(r"(c\,\Delta t')^2=(c\,\Delta t)^2+(v\,\Delta t')^2",
             colors={r"c\,\Delta t'": C.dilation, r"v\,\Delta t'": C.muted, r"c\,\Delta t": C.light})
    fit(e1.scale(0.8), COL[1] - COL[0] + 0.2).move_to(P3(RC, 0.15))
    e2, tags = ch6.gamma_eqn()
    hud.play(Write(e1), at=t_tg + 0.2, dur=1.2)
    hud.play(TransformMatchingTex(e1, e2), at=t_tg + 1.9, dur=1.2)
    hud.play(FadeIn(tags, shift=0.06 * UP), at=t_tg + 3.0, dur=0.6)

    # γ against v/c: flat for everything we know, a wall at the speed of light
    g_op = fade(t_ev - 0.4, dur=0.6, out=t_mu - 0.35, out_dur=0.5)
    axes, wall = _gamma_axes()
    s.manim(z=4, opacity=g_op).add(axes)
    s.manim(z=4, opacity=fade(t_wl - 1.2, dur=0.6, out=t_mu - 0.35, out_dur=0.5)).add(wall)
    t_a, t_b = float(t_ev) - 0.1, float(t_wl) + 0.4
    glow(s, C.dilation, z=6, k=0.7).redraw(lambda t: _curve(t, t_a, t_b, g_op), during=(t_ev - 0.3, t_mu + 0.3))
    pts = s.manim(z=7)
    d0 = Dot(ch6.g_pt(0.0, 1.0), radius=0.07, color=C.light)
    gm1 = ch6.everyday_gamma_minus_one()
    assert gm1 < 1e-9, gm1
    ev = VGroup(sans("car · jet · ISS", 22, C.light), tex(r"\gamma-1<10^{-9}", 28, C.muted)) \
        .arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(ch6.g_pt(0.02, 1.0), UR, buff=0.25)
    pts.play(FadeIn(d0, scale=0.5), at=t_ev + 0.3, dur=0.4)
    pts.play(FadeIn(ev, shift=0.05 * UP), at=t_ev + 0.6, dur=0.5)
    pts.play(FadeOut(VGroup(d0, ev)), at=t_mu - 0.35, dur=0.5)
    for b, when in ((0.9, t_a + 0.55 * (t_b - t_a) + 0.6), (0.99, t_b - 0.25)):
        gm = 1 / math.sqrt(1 - b * b)
        d = Dot(ch6.g_pt(b, gm), radius=0.07, color=C.light)
        lab = VGroup(tex(rf"{b}\,c", 28, C.light), tex(rf"\gamma={gm:.1f}", 28, C.muted)) \
            .arrange(DOWN, aligned_edge=RIGHT, buff=0.1).next_to(d, LEFT, buff=0.22)
        pts.play(FadeIn(d, scale=0.5), at=when, dur=0.35)
        pts.play(FadeIn(lab, shift=0.05 * LEFT), at=when + 0.15, dur=0.45)
        pts.play(FadeOut(VGroup(d, lab)), at=t_mu - 0.35, dur=0.5)

    # muons: the same shower with clocks at the normal rate and slowed ten times
    t_on = ch6.MU_ON
    mu_op = fade(t_mu - 0.1, dur=0.6)
    s.manim(z=4, opacity=mu_op).add(ch6.muon_axes())
    heads = ch6.muon_heads()
    mm = s.manim(z=10)
    mm.play(FadeIn(heads), at=t_mu + 0.2, dur=0.6)
    s.manim(z=6).redraw(lambda t: ch6.muon_column(t, t_on, False, float(mu_op(t))), during=(t_mu - 0.2, s.end))
    glow(s, C.dilation, z=7, k=0.5).redraw(lambda t: ch6.muon_column(t, t_on, True, float(mu_op(t))),
                                           during=(t_mu - 0.2, s.end))

    (b0, l0), (b1, l1) = ch6.muon_braces()
    mm.play(FadeIn(VGroup(b0, l0)), at=t_de, dur=0.5)
    mm.play(FadeIn(VGroup(b1, l1)), at=t_de + 1.3, dur=0.5)
    n_land = ch6.muon_landed(float(s.end) + 10, t_on, True)

    def ground_count(t):
        return ch6.ground_counts(t, t_on).set_opacity(float(smooth01((t - float(t_mk) + 0.1) / 0.5)))
    s.manim(z=10).redraw(ground_count, during=(t_mk - 0.3, s.end))
    assert 5 <= n_land <= 20, n_land
