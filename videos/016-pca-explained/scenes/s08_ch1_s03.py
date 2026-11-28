"""ch1_s03 · Spread (L2, rail: B_cloud).

On the centred plane each person's height gap draws (C.spread), then grows a square. On 'average the squares' the
squares fly into a board in the rail, nested at one corner, and their average draws over them: a square whose side
is the standard deviation (computed: sqrt of the mean of the squared gaps). sigma^2 = (1/n) sum (x_i - mu)^2 writes.
On 'far points' the two largest squares light. Then three spread bars (+-1 sd): along height, along arm span, and
along the diagonal, which glows and outgrows both; copies of the first two swing parallel to it to compare. On
'cares about' the board pins into rail slot 2 (B_var).
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, KP, RAIL, SLOT_GAP, STAGE_IN, STAGE_L2, Y0, P3, Aura, bead, bead_layer, card, cen_grid,
                 cen_names, eq_var, glow_layer, mean_ring, rail_cloud_parts, rail_var_parts, slot, var_square)

B2 = (RAIL[0], Y0, RAIL[2], slot(0)[1] - SLOT_GAP)
CORNER = (B2[0] + 0.32, B2[1] + 0.3)


def cp(x, y):
    return P3(CEN0[0] + KP * x, CEN0[1] + KP * y)


@scene(T.ch1_s03, T.ch1_s04)
def ch1_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_far_, t_sq, t_avg = float(T.ch1_s03_how_far), float(T.ch1_s03_square_that_gap), float(T.ch1_s03_average_the_squares)
    t_var, t_fp = float(T.ch1_s03_variance), float(T.ch1_s03_far_points)
    t_bh, t_ba, t_dg = float(T.ch1_s03_spread_along_height), float(T.ch1_s03_along_arm_span), float(T.ch1_s03_diagonal)
    t_cares = float(T.ch1_s03_cares_about)
    t_num = t_var - 1.35                          # 'That number'
    t_further = t_dg + 1.9                        # 'stretches further'
    P = pd.people2()
    Xc = P.Xc
    n = len(Xc)
    gaps = Xc[:, 0]
    sd_h, sd_a = math.sqrt(P.C[0, 0]), math.sqrt(P.C[1, 1])
    u = np.array([1.0, 1.0]) / math.sqrt(2)
    sd_d = math.sqrt(float(u @ P.C @ u))
    assert abs(math.sqrt(np.mean(gaps ** 2)) - sd_h) < 1e-9

    # ---- static: the centred plane, the cloud, the ring; B_cloud in the rail
    s.manim(z=-1).add(card(STAGE_L2))
    pl = s.manim(z=0)
    pl.add(cen_grid(pr=True), cen_names(pr=True))
    rd, rring, req = rail_cloud_parts(pr=True)
    s.manim(z=0.1).add(card(slot(0)), rring, req)
    bead_layer(s, z=0.2).add(rd)
    dm = bead_layer(s, z=2)
    pts = VGroup(*[bead(cp(*p)) for p in Xc])
    dm.add(pts)
    mg = glow_layer(s, z=2.2, color=C.mean, k=0.2)
    mg.add(mean_ring(cp(0, 0), pr=True))
    au = Aura(STAGE_IN)
    W = np.array([cp(*p)[:2] for p in Xc])
    s.add(FramesLayer(lambda t: au.frame(W, 1.0, 0.35), z=0.5, during=[(t0, t1)], **au.layer_kw()))

    # ---- gaps, then squares on them
    m = s.manim(z=1)
    segs = VGroup(*[Line(cp(0, y), cp(x, y), stroke_color=C.spread, stroke_width=2.2) for x, y in Xc])
    order = np.argsort(np.abs(gaps))
    m.play(LaggedStart(*[Create(segs[i]) for i in order], lag_ratio=0.03), at=t_far_, dur=1.4)
    sqs, targets = [], []
    for x, y in Xc:
        side = abs(x) * KP
        up = -1 if y >= 0 else 1                       # toward the height axis: stays on the board
        q = Square(side_length=max(side, 1e-3), stroke_color=C.spread, stroke_width=1.3, stroke_opacity=0.7,
                   fill_color=C.spread, fill_opacity=0.035).move_to(cp(x / 2, y) + UP * up * side / 2)
        sqs.append(q)
        targets.append(var_square(max(side, 1e-3), CORNER, stroke=1.4, fill=0.04).set_stroke(opacity=0.85))
    m.play(LaggedStart(*[GrowFromEdge(sqs[i], UP if Xc[i, 1] >= 0 else DOWN) for i in order], lag_ratio=0.03),
           at=t_sq, dur=1.4)

    # ---- the board in the rail; the squares fly there, nested at one corner
    bm = m
    b2 = card(B2)
    bm.play(FadeIn(b2), at=t_avg - 0.3, dur=0.5)
    bm.play(LaggedStart(*[ReplacementTransform(sqs[i], targets[i]) for i in order[::-1]], lag_ratio=0.025),
            at=t_avg, dur=1.7)
    big2 = order[-2:]
    for i in range(n):
        q = targets[i]
        bm.play(q.animate.set_stroke(opacity=0.32, width=1.2).set_fill(opacity=0.0), at=t_num, dur=0.6)
    hi = VGroup()
    for i in big2:
        hi.add(var_square(abs(gaps[i]) * KP, CORNER, stroke=3.0, fill=0.12),
               Line(cp(0, Xc[i, 1]), cp(Xc[i, 0], Xc[i, 1]), stroke_color=C.spread, stroke_width=5.5))
    bm.play(FadeIn(hi), at=t_fp, dur=0.4)
    bm.play(FadeOut(hi), at=t_fp + 1.9, dur=0.6)
    msq = var_square(KP * sd_h, CORNER)
    bm.play(GrowFromPoint(msq, P3(*CORNER)), at=t_num + 0.3, dur=0.9)
    eq = eq_var(42)
    eq.scale(min(1.0, (B2[2] - B2[0] - 0.4) / eq.width)).move_to(P3((B2[0] + B2[2]) / 2, B2[3] - 0.65))
    bm.play(Write(eq), at=t_var, dur=1.2)
    m.play(FadeOut(segs), at=t_bh - 1.0, dur=0.7)

    # ---- the spread bars: height, arm span, then the diagonal (glows, outgrows both)
    y_bar, x_bar = -27.0, -31.0
    hb = Line(cp(-sd_h, y_bar), cp(sd_h, y_bar), stroke_color=C.spread, stroke_width=7)
    ab = Line(cp(x_bar, -sd_a), cp(x_bar, sd_a), stroke_color=C.spread, stroke_width=7)
    m.play(GrowFromCenter(hb), at=t_bh, dur=0.8)
    m.play(GrowFromCenter(ab), at=t_ba, dur=0.8)
    dl = DashedLine(cp(*(-30 * u)), cp(*(30 * u)), stroke_color=C.muted, stroke_width=1.8, dash_length=0.1)
    m.play(Create(dl), at=t_dg - 0.1, dur=0.8)
    gl = glow_layer(s, z=2.5, color=C.spread, k=0.8)
    db = Line(cp(*(-sd_d * u)), cp(*(sd_d * u)), stroke_color=C.spread, stroke_width=7)
    gl.play(GrowFromCenter(db), at=t_dg + 0.6, dur=1.0)
    nrm = np.array([-1.0, 1.0]) / math.sqrt(2) * (0.32 / KP)       # 0.32 u off the diagonal, in cm
    cps = []
    for bar, sd, side in ((hb, sd_h, 1), (ab, sd_a, -1)):
        cpy = bar.copy()
        m.add(cpy, at=t_further - 0.05)
        cps.append(cpy)
        m.play(Transform(cpy, Line(cp(*(-sd * u + side * nrm)), cp(*(sd * u + side * nrm)), stroke_color=C.spread,
                                   stroke_width=4, stroke_opacity=0.65)), at=t_further, dur=1.2)

    # ---- 'cares about': the board pins into rail slot 2 (B_var)
    rsq, req = rail_var_parts()
    bm.play(FadeOut(VGroup(*targets)), at=t_cares - 1.4, dur=0.6)
    bm.play(Transform(b2, card(slot(1))), ReplacementTransform(msq, rsq), ReplacementTransform(eq, req),
            at=t_cares, dur=1.0)
    # the bars, the diagonal and its glow leave in the pause (the cloud stays for ch1_s04)
    gl.play(FadeOut(db), at=t1 - 0.75, dur=0.6)
    m.play(FadeOut(VGroup(hb, ab, dl, *cps)), at=t1 - 0.75, dur=0.6)
