"""ch1_s02 · Find the centre (L2).

The raw cloud from ch1_s01. On 'centre' a soft ellipse pulses round it. On 'Average all the heights' each person
drops a tick onto the height axis and the ticks slide together into their average (a C.mean tick and a dashed
line); the same on the arm-span axis. Where the two lines cross: the average person (a C.mean ring), and
mu = (1/n) sum x_i. On 'slide' the cloud moves so the average person sits on the origin of a centred plane; a ghost
of where it was stays behind, then slides across and lands exactly on it ('Nothing about the shape changes').
x~_i = x_i - mu writes; on 'spread out' a copy of the centred cloud and the equation pin into rail slot 1.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, KP, RAW0, STAGE_IN, STAGE_L2, P3, Aura, backed, bead, bead_layer, card, cen_grid, cen_names,
                 ellipse_of, eq_centre, eq_mean, glow_layer, mean_ring, raw_plane, raw_xy, rail_cloud_parts, slot,
                 smoothstep)


@scene(T.ch1_s02, T.ch1_s03)
def ch1_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_cen, t_avh, t_ava = float(T.ch1_s02_centre), float(T.ch1_s02_average_all_the_heig), float(T.ch1_s02_arm_spans)
    t_per, t_sl, t_out = float(T.ch1_s02_average_person), float(T.ch1_s02_slide), float(T.ch1_s02_spread_out)
    t_same = t_sl + 4.85                          # 'Nothing about the shape changes'
    P = pd.people2()
    X, mu = P.X, P.mu
    R = raw_xy(X)
    Cc = CEN0 + KP * P.Xc
    shift = CEN0 - raw_xy(mu)

    # ---- the planes: raw (fades on 'slide'), centred (fades in)
    s.manim(z=-1).add(card(STAGE_L2))
    pl = s.manim(z=0)
    raw = raw_plane(pr=True)
    pl.add(raw)
    pl.play(FadeOut(raw), at=t_sl, dur=1.0)
    cg = cen_grid(pr=True)
    pl.play(FadeIn(cg), at=t_sl + 0.5, dur=1.2)
    pl.play(FadeIn(cen_names(pr=True)), at=t_sl + 1.6, dur=0.6)

    # ---- the cloud and the ring (pure functions of the slide)
    u = keys((t0, 0.0), (t_sl - 0.1, 0.0), (t_sl + 1.6, 1.0))
    ring_on = keys((t0, 0.0), (t_per - 0.1, 0.0), (t_per + 0.5, 1.0))

    def cloud(t):
        k = float(u(t))
        return VGroup(*[bead(P3(*(p + k * shift))) for p in R])

    dm = bead_layer(s, z=2)
    dm.redraw(cloud, during=(t0, t1))

    # the average person: a ring that closes in, lit, with a soft pulse on arrival
    def ring(t):
        a = float(ring_on(t))
        if a <= 0.001:
            return VGroup()
        k = float(u(t))
        c = P3(*(raw_xy(mu) + k * shift))
        g = VGroup(mean_ring(c, r=0.1 + 0.25 * (1 - a), pr=True).set_stroke(opacity=a).set_fill(opacity=0))
        v = (t - (t_per + 0.5)) / 0.9
        if 0 <= v < 1:
            g.add(Circle(radius=0.12 + 0.35 * v, stroke_color=C.mean, stroke_width=2.0,
                         stroke_opacity=0.8 * (1 - v) ** 1.5).move_to(c))
        return g

    rgm = glow_layer(s, z=2.2, color=C.mean, k=0.2)
    rgm.redraw(ring, during=(t_per - 0.2, t1))

    # the density aura travels with the cloud
    au = Aura(STAGE_IN)
    s.add(FramesLayer(lambda t: au.frame(R + float(u(t)) * shift, 1.0, 0.35), z=0.5, during=[(t0, t1)],
                      **au.layer_kw()))

    # the ghost of the old place: stays, then slides across onto the cloud
    g_on = keys((t_sl, 0.0), (t_sl + 0.4, 0.3), (t_same + 1.3, 0.3), (t_same + 1.8, 0.0))
    g_u = keys((t_same - 0.1, 0.0), (t_same + 1.3, 1.0))

    def ghost(t):
        a = float(g_on(t))
        if a <= 0.001:
            return VGroup()
        k = float(g_u(t))
        return VGroup(*[Circle(radius=0.062, stroke_color=C.data, stroke_width=1.6, stroke_opacity=min(1.0, a * 2.2))
                        .move_to(P3(*(p + k * shift))) for p in R])

    gm = s.manim(z=1.5)
    gm.redraw(ghost, during=(t_sl - 0.1, t_same + 1.9))

    # ---- 'centre': a soft ellipse pulses round the cloud
    c, w, h, ang = ellipse_of(R, k=2.2)
    ell = Ellipse(width=w, height=h, stroke_color=C.text, stroke_width=1.6, stroke_opacity=0.55).rotate(ang).move_to(P3(*c))
    m = s.manim(z=1)
    m.play(Create(ell), at=t_cen, dur=0.9)
    m.play(FadeOut(ell), at=t_cen + 1.1, dur=0.6)

    # ---- the averages: ticks drop onto each axis and slide together into the mean
    ax_y, ax_x = RAW0[1], RAW0[0]
    mh, ma = raw_xy(mu)
    hticks = VGroup(*[Line(P3(x, ax_y - 0.09), P3(x, ax_y + 0.09), stroke_color=C.data, stroke_width=2.4) for x in R[:, 0]])
    aticks = VGroup(*[Line(P3(ax_x - 0.09, y), P3(ax_x + 0.09, y), stroke_color=C.data, stroke_width=2.4) for y in R[:, 1]])
    m.play(LaggedStart(*[FadeIn(q, shift=DOWN * 0.25) for q in hticks], lag_ratio=0.03), at=t_avh, dur=1.0)
    m.play(*[q.animate.move_to(P3(mh, ax_y)) for q in hticks], at=t_avh + 1.15, dur=0.9)
    m.play(FadeOut(hticks), at=t_avh + 1.9, dur=0.3)
    hmean = Line(P3(mh, ax_y - 0.14), P3(mh, ax_y + 0.14), stroke_color=C.mean, stroke_width=4)
    hline = DashedLine(P3(mh, ax_y), P3(mh, STAGE_IN[3]), stroke_color=C.mean, stroke_width=1.8, dash_length=0.1)
    m.play(FadeIn(hmean), at=t_avh + 1.85, dur=0.3)
    m.play(Create(hline), at=t_avh + 2.0, dur=0.8)

    m.play(LaggedStart(*[FadeIn(q, shift=LEFT * 0.25) for q in aticks], lag_ratio=0.03), at=t_ava - 0.1, dur=1.0)
    m.play(*[q.animate.move_to(P3(ax_x, ma)) for q in aticks], at=t_ava + 1.0, dur=0.9)
    m.play(FadeOut(aticks), at=t_ava + 1.75, dur=0.3)
    amean = Line(P3(ax_x - 0.14, ma), P3(ax_x + 0.14, ma), stroke_color=C.mean, stroke_width=4)
    aline = DashedLine(P3(ax_x, ma), P3(STAGE_IN[2], ma), stroke_color=C.mean, stroke_width=1.8, dash_length=0.1)
    m.play(FadeIn(amean), at=t_ava + 1.7, dur=0.3)
    m.play(Create(aline), at=t_ava + 1.85, dur=0.8)
    m.play(FadeOut(VGroup(hmean, hline, amean, aline)), at=t_sl - 0.3, dur=0.5)

    # ---- the equations (lower right of the stage)
    e1 = backed(eq_mean(44), 0.08, fill=C.card).move_to(P3(0.75, -1.85))
    e2 = backed(eq_centre(44), 0.08, fill=C.card).move_to(P3(0.75, -2.65))
    m.play(Write(e1), at=t_per + 0.6, dur=1.0)
    m.play(Write(e2), at=t_sl + 1.9, dur=1.0)

    # ---- 'spread out': B_cloud pins into rail slot 1
    rd, rring, req = rail_cloud_parts(pr=True)
    stage_dots = VGroup(*[bead(P3(*p)) for p in Cc])
    rm = bead_layer(s, z=3)
    rm.add(stage_dots, at=t_out - 0.2)
    s.manim(z=2.9).play(FadeIn(card(slot(0))), at=t_out - 0.2, dur=0.6)
    rm.play(ReplacementTransform(stage_dots, rd), at=t_out, dur=1.0)
    rm.play(FadeIn(rring), at=t_out + 0.6, dur=0.4)
    m.play(FadeOut(e1), at=t_out - 0.2, dur=0.5)
    e2c = eq_centre(44).move_to(e2[1].get_center())
    m.remove(e2, at=t_out)
    rq = s.manim(z=3.1)
    rq.add(e2c, at=t_out)
    rq.play(ReplacementTransform(e2c, req), at=t_out, dur=1.0)
