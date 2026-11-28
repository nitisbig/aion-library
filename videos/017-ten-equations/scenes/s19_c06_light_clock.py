"""c06_s01 · Light clock (hook). Storyboard: plan/scene_plan.md § c06_s01. Layout L3 (one open stage, frame 08).

Opens on c05_s03's last frame (two identical clocks), which gives way to the chapter card. 'light': a clock made of
light, a photon bouncing between two mirrors, each bounce one tick (a ring opens on the mirror). 'train': the same
clock rides a train at 0.6 c; both photons left their bottom mirrors together, and the two clocks' ticks are laid
on one time line below. 'slanted': the moving photon's zig-zag, seen from the platform. 'Einstein': both photons
carry the same speed c (arrows of equal length; the moving one's is tilted). 'longer path': one zig is pulled out
into a right triangle, and the light's path in the clock at rest slides over to become its upright leg. 'slowly':
the tick lines show the count: eight ticks at rest for every six on the train (γ = 1.25 at 0.6 c, all computed in
ch6).
"""
import math

import numpy as np
from aion import *

import ch6
from beats import T
from kit import P3, X1, Y0, add_rail, chapter_card, glow, glimpse, polyline, sans, smooth01, tex

def _carry(s):
    """c05_s03's last frame: two identical clocks ticking together; they fade as the chapter card comes in."""
    t0, t_sr = float(s.start), float(T.c05_s03_same_rate)
    op = fade(t0 - 5, dur=0.1, out=t0 + 0.15, out_dur=0.6)

    def clocks(t):
        a = float(op(t))
        g = VGroup()
        if a < 0.01:
            return g
        k = math.floor((t - t_sr) / 1.0)
        for x in (-2.6, 2.6):
            face = VGroup(Circle(radius=1.15, stroke_color=C.light, stroke_width=2.4, stroke_opacity=a).move_to(P3(x, 0.2)))
            for j in range(12):
                ang = 2 * math.pi * j / 12
                face.add(Line(P3(x + 1.0 * math.sin(ang), 0.2 + 1.0 * math.cos(ang)),
                              P3(x + 1.12 * math.sin(ang), 0.2 + 1.12 * math.cos(ang)),
                              stroke_color=C.muted, stroke_width=1.6, stroke_opacity=a))
            ang = 2 * math.pi * (k + 8) / 60
            face.add(Line(P3(x, 0.2), P3(x + 0.95 * math.sin(ang), 0.2 + 0.95 * math.cos(ang)),
                          stroke_color=C.fourier, stroke_width=3, stroke_opacity=a),
                     Dot(P3(x, 0.2), radius=0.05, color=C.light, fill_opacity=a))
            g.add(face)
        return g
    s.manim(z=8).redraw(clocks, during=(s.start, t0 + 1.0))


def _speed_arrow(p, v, color, op):
    """An arrow of the photon's velocity (length ∝ speed, so both are equal) with its 'c'."""
    q = np.array(p[:2]) + 0.5 * np.asarray(v)
    a = Arrow(P3(*p[:2]), P3(*q), buff=0, stroke_width=3, color=color, tip_length=0.14,
              max_tip_length_to_length_ratio=0.3).set_opacity(op)
    side = np.array([v[1], -v[0]]) / np.hypot(*v)
    lab = tex("c", 34, color).move_to(P3(*(np.array(p[:2]) + 0.25 * np.asarray(v) + 0.3 * side))).set_opacity(op)
    return VGroup(a, lab)


@scene(T.c06_s01, T.c06_s02)
def s19_c06_light_clock(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_li, t_ti, t_tr, t_sl, t_ei, t_lp, t_sw = (T.c06_s01_light, T.c06_s01_tick, T.c06_s01_train, T.c06_s01_slanted,
                                                T.c06_s01_einstein, T.c06_s01_longer_path, T.c06_s01_slowly)
    _carry(s)
    chapter_card(s, 6, at=t0 + 0.45, out=t_li + 0.6)
    add_rail(s, 6, opacity=fade(t0 + 0.4, dur=0.8))
    hud = s.manim(z=50, parallax=0.0)

    # the clock at rest
    m = s.manim(z=5)
    m.play(FadeIn(ch6.ground()), at=t_li + 0.7, dur=0.8)
    m.play(Create(ch6.mirrors(ch6.LX)), at=t_li + 0.8, dur=0.7)
    rest_lab = sans("at rest", 24, C.light).move_to(P3(ch6.LX, ch6.GROUND - 0.35))
    m.play(FadeIn(rest_lab), at=t_li + 1.4, dur=0.5)
    m.play(FadeOut(rest_lab), at=t_tr + 0.3, dur=0.5)                 # the tick lines carry the names from here
    t_rest = ch6.T_REST
    path_op = lambda t: float(smooth01((t - t_rest) / 0.6))
    s.manim(z=4).redraw(lambda t: Line(P3(ch6.LX, ch6.YB), P3(ch6.LX, max(ch6.rest_y(t), ch6.YB + 1e-3)
                                                                         if t < t_rest + ch6.TAU else ch6.YT),
                                       stroke_color=C.light, stroke_width=2.2, stroke_opacity=0.5 * path_op(t)),
                        during=(t_rest - 0.1, s.end))
    ph = glow(s, C.light, z=9, k=1.0)
    ph_op = fade(t_rest - 0.25, dur=0.4)
    ph.redraw(lambda t: Dot(P3(ch6.LX, ch6.rest_y(t)), radius=0.08, color=C.light, fill_opacity=float(ph_op(t))),
              during=(t_rest - 0.4, s.end))

    # tick: a ring opens on each mirror the light hits
    tk_op = fade(t_ti - 0.3, dur=0.4)
    s.manim(z=7).redraw(lambda t: ch6.bounce_flashes(t, t_rest, ch6.TAU, lambda _: ch6.LX, C.light, float(tk_op(t))),
                        during=(t_ti - 0.3, s.end))
    tick_w = sans("one tick", 22, C.muted).move_to(P3(ch6.LX + 0.95, ch6.YB + 0.05), aligned_edge=LEFT)
    m.play(FadeIn(tick_w), at=t_ti, dur=0.4)
    m.play(FadeOut(tick_w), at=t_tr - 0.5, dur=0.4)

    # the same clock on a train
    tr_op = fade(t_tr - 0.35, dur=0.6)
    s.manim(z=5).redraw(lambda t: ch6.train(t, float(tr_op(t))), during=(t_tr - 0.4, s.end))
    mv_ph = lambda t: ch6.moving_photon(t)
    glow(s, C.light, z=9, k=1.0).redraw(lambda t: Dot(P3(*mv_ph(t)), radius=0.08, color=C.light, fill_opacity=float(tr_op(t))),
              during=(t_tr - 0.4, s.end))
    s.manim(z=7).redraw(lambda t: ch6.bounce_flashes(t, ch6.T_REF, ch6.TAU_M, ch6.train_x, C.dilation,
                                                     float(tr_op(t))), during=(t_tr - 0.4, s.end))

    def v_arrow(t):
        a = float(tr_op(t))
        x = ch6.train_x(t)
        y = ch6.YT + 0.55
        return VGroup(Arrow(P3(x - 0.8, y), P3(x + 0.5, y), buff=0, stroke_width=3, color=C.muted, tip_length=0.15,
                            max_tip_length_to_length_ratio=0.2),
                      tex(r"v=0.6\,c", 30, C.muted).move_to(P3(x + 0.65, y), aligned_edge=LEFT)).set_opacity(a)
    v_op = fade(t_tr, dur=0.5, out=t_lp - 0.6, out_dur=0.5)
    s.manim(z=11).redraw(lambda t: v_arrow(t).set_opacity(float(v_op(t))), during=(t_tr - 0.2, t_lp))

    # the two clocks' ticks on one time line
    rows_op = fade(t_tr + 0.4, dur=0.6)
    s.manim(z=12).redraw(lambda t: ch6.tick_rows(t, float(rows_op(t))) if t >= ch6.T_REF else VGroup(),
                         during=(ch6.T_REF, s.end))
    labs = ch6.row_labels()
    m2 = s.manim(z=12)
    m2.play(FadeIn(labs), at=t_tr + 0.4, dur=0.6)

    # slanted: the moving light's path, seen from the platform
    zz_op = fade(t_sl - 0.35, dur=0.6)
    dim = lambda t: 1 - 0.65 * float(smooth01((t - float(t_lp)) / 0.8))
    glow(s, C.dilation, z=6, k=0.35).redraw(
        lambda t: polyline(ch6.zigzag(t), C.dilation, 3.0, float(zz_op(t)) * dim(t)) if t > ch6.T_REF + 0.05
        else VGroup(), during=(t_sl - 0.4, s.end))

    # Einstein: the same speed c for both
    glimpse(s, "einstein_1905", t_ei, C.dilation, dur=4.4, h=1.6)   # small: the clock stands just right of it
    c_op = fade(t_ei + 0.6, dur=0.5, out=t_lp - 0.2, out_dur=0.5)

    def c_arrows(t):
        a = float(c_op(t))
        if a < 0.01:
            return VGroup()
        up_r = (math.floor((t - t_rest) / ch6.TAU) % 2) == 0
        up_m = (math.floor((t - ch6.T_REF) / ch6.TAU_M) % 2) == 0
        vy_m = ch6.H / ch6.TAU_M * (1 if up_m else -1)
        return VGroup(_speed_arrow((ch6.LX, ch6.rest_y(t)), (0, ch6.CS * (1 if up_r else -1)), C.light, a),
                      _speed_arrow(mv_ph(t), (ch6.U, vy_m), C.dilation, a))
    s.manim(z=10).redraw(c_arrows, during=(t_ei + 0.3, t_lp + 0.4))

    # longer path: one zig becomes a right triangle; the rest clock's path slides over as its upright leg
    tri = ch6.triangle()
    x1 = ch6.TRI[1]
    hyp_l = glow(s, C.dilation, z=8, k=0.9)
    hyp_l.play(Create(tri["hyp"]), at=t_lp - 0.1, dur=0.7)
    copy = DashedLine(P3(ch6.LX, ch6.YB), P3(ch6.LX, ch6.YT), stroke_color=C.light, stroke_width=2.4,
                      dash_length=0.09)
    tm = s.manim(z=9)
    tm.play(FadeIn(copy), at=t_lp + 0.3, dur=0.3)
    tm.play(copy.animate.move_to(P3(x1, ch6.CY)), at=t_lp + 0.55, dur=1.3)
    tm.play(FadeIn(tri["base"]), at=t_lp + 0.6, dur=0.6)
    l_h, l_v, l_b = tri["labels"]
    tm.play(FadeIn(l_h, shift=0.05 * UP), at=t_lp + 0.3, dur=0.5)
    tm.play(FadeIn(l_v), at=t_lp + 1.8, dur=0.5)
    tm.play(FadeIn(l_b, shift=0.05 * UP), at=t_lp + 2.3, dur=0.5)

    # slowly: the count
    cnt_op = fade(t_sw - 0.2, dur=0.5)
    s.manim(z=12).redraw(lambda t: ch6.row_counts(t).set_opacity(float(cnt_op(t))), during=(t_sw - 0.4, s.end))
