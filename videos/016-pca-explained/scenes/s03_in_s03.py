"""in_s03 · The glimpse (L1): 1,797 digits in two numbers each, and they sort themselves.

The table from in_s02 squeezes until all 1,797 rows fit ('best shadow'); on 'Squeeze' every row's 64 cells pull
together into one dot ('to just two'); on 'plot' the dots fly to their real PCA coordinates (numpy eigh, pcadata).
They arrive in one dim colour. On 'zeros', 'sixes', 'fours' those classes light in their own hues with a ringed
numeral, then the rest light together. A glow passes over the map on 'survives'. Title lockup on the name.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import (CELL, PITCH, ROW1_Y, TAB_X0, TAB_Y0, X1, Y0, Y1, Canvas, Table, P3, caps, sans, smoothstep,
                 spans_raster, tex, tint)

MAP_BOX = (-5.6, -1.55, 5.6, Y1)
N_VIS = (ROW1_Y - TAB_Y0) / PITCH


@scene(T.in_s03, T.in_s04)
def in_s03(s):
    import pcadata as pd
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_best, t_sq, t_nob = float(T.in_s03_best_shadow), float(T.in_s03_squeeze), float(T.in_s03_nobody_told)
    t_z, t_6, t_4 = float(T.in_s03_zeros), float(T.in_s03_sixes), float(T.in_s03_fours)
    t_surv, t_pca = float(T.in_s03_survives), float(T.in_s03_principal_component_)
    t_two = t_sq + 3.35                               # 'just two'
    t_plot = t_sq + 4.23                              # 'plot each one as a dot'
    t_num = t_surv - 3.1                              # 'Two numbers out of sixty-four'
    t_name = t_pca + 2.44                             # 'PCA.'
    lead = 0.15

    D = pd.digits_pca()
    X, y = pd.digits()
    n = len(y)
    Z = D.Z[:, :2] * np.array([1, -1])
    k = min((MAP_BOX[2] - MAP_BOX[0]) / np.ptp(Z[:, 0]), (MAP_BOX[3] - MAP_BOX[1]) / np.ptp(Z[:, 1]))
    mc = np.array([(MAP_BOX[0] + MAP_BOX[2]) / 2, (MAP_BOX[1] + MAP_BOX[3]) / 2])
    dest = mc + k * (Z - (Z.max(0) + Z.min(0)) / 2)

    # ---- the table: squeeze to fit all rows, then each row pulls into a dot
    sig_all = N_VIS / (n - 1)
    a_sq, d_sq = t_best - lead, 1.6
    a_c, d_c = t_sq - lead, t_two - t_sq + 0.2
    rng = np.random.default_rng(1605)
    xi = rng.uniform(TAB_X0 + 0.3, -TAB_X0 - 0.3, n)

    def sigma(t):
        u = float(smoothstep((t - a_sq) / d_sq))
        return math.exp((1 - u) * 0.0 + u * math.log(sig_all))

    def top(t, sg):
        return max(0.0, (n - 1) - N_VIS / sg)

    row_y_all = ROW1_Y - np.arange(n) * PITCH * sig_all
    cv = Canvas((-6.4, -4.0, 6.4, 4.0), px=s.comp.size[1] / 8)
    tab = Table(cv)
    xc = TAB_X0 + (np.arange(64) + 0.5) * CELL
    vals = np.maximum(tab.rgb.astype(np.float32), 24)
    flare = pulse(t_best, amp=1.0, dur=1.0)
    last = {}

    def draw(t):
        sg = sigma(t)
        u = float(smoothstep((t - a_c) / d_c))
        key = (round(sg, 6), round(u, 4), round(float(flare(t)), 3))
        if last.get("k") == key:
            return last["a"]
        if u <= 0 and sg > 0.12:
            c = cv.begin()
            tab.draw(c, top(t, sg), squeeze=sg, alpha=1.0)
            a = cv.array()
        else:
            ys = (ROW1_Y - (np.arange(n) - top(t, sg)) * PITCH * sg)
            Y = np.repeat(ys, 64)
            Xc = (xc[None, :] * (1 - u) + xi[:, None] * u).ravel()
            half = CELL / 2 * (1 - u) + 0.004
            V = vals.ravel() * (1 + 0.3 * u)
            a = spans_raster(cv, Y, Xc - half, Xc + half, V, h_px=max(1.0, PITCH * sg * cv.px * 0.8))
        f = float(flare(t))
        if f > 0.01:                                          # the rows flare as the question is asked
            a = np.clip(a.astype(np.float32) * (1 + 0.35 * f), 0, 255).astype(np.uint8)
        last.update(k=key, a=a)
        return a

    tab_on = keys((t0, 1.0), (t_plot - 0.1, 1.0), (t_plot + 0.25, 0.0))
    s.add(FramesLayer(draw, z=0, opacity=tab_on, during=[(t0, t_plot + 0.3)], **cv.layer_kw()))
    m = s.manim(z=1)
    rows = VGroup(Tex(r"\textsf{1\,797}", font_size=30), sans("rows", 26, C.muted)).arrange(RIGHT, buff=0.15,
                                                                                         aligned_edge=DOWN)
    rows.move_to(P3(-TAB_X0, ROW1_Y + 0.36), aligned_edge=RIGHT)
    m.add(rows)
    m.play(FadeOut(rows), at=t_plot, dur=0.6)

    # ---- dots fly to the map, then light class by class
    start = np.c_[xi, row_y_all]
    order = rng.permutation(n)
    lag = np.empty(n)
    lag[order] = np.linspace(0, 1.1, n)
    a_f, d_f = t_plot - lead, 1.6
    bend = rng.normal(0, 0.6, (n, 1)) * np.array([[-1, 1]])

    def pos(t):
        f = smoothstep((t - a_f - lag) / d_f)[:, None]
        p = start + (dest - start) * f
        return p + bend * (np.sin(np.pi * f)) * (dest - start)[:, ::-1] * 0.12

    pos_c = {"t": None}

    def pos_cached(t):
        if pos_c["t"] != t:
            pos_c.update(t=t, p=pos(t))
        return pos_c["p"]

    t_rest = t_4 + 1.2
    light_at = {0: t_z, 6: t_6, 4: t_4}
    for j, d in enumerate([1, 2, 3, 5, 7, 8, 9]):
        light_at[d] = t_rest + 0.14 * j
    dim_col = tint(C.data, 0.6)
    on = keys((t_plot - 0.1, 0.0), (t_plot + 0.25, 1.0), (t1 - 0.7, 1.0), (t1 - 0.1, 0.0))
    numerals = s.manim(z=3)
    for d in range(10):
        idx = np.where(y == d)[0]
        lit = fade(light_at[d], dur=0.7)
        P = (lambda t, idx=idx: pos_cached(t)[idx])
        s.add(PointsLayer(P, color=dim_col, size=5.0, glow=0.0, additive=False, z=1, opacity=on * (1 - lit),
                          start=t_plot - 0.2))
        s.add(PointsLayer(P, color=getattr(C, f"d{d}"), size=5.5, glow=0.25, additive=False, z=1.2, opacity=on * lit,
                          start=light_at[d] - 0.3))
        s.add(PointsLayer(P, color=getattr(C, f"d{d}"), size=6.0, glow=0.9, additive=True, z=1.4,
                          opacity=on * pulse(t_surv + 0.04 * d, amp=0.7, dur=1.8), start=t_surv - 1.2,
                          end=t_surv + 1.2))
        cen = np.median(dest[idx], 0)
        disc = VGroup(Circle(radius=0.27, stroke_color=getattr(C, f"d{d}"), stroke_width=2.2, fill_color=C.bg,
                             fill_opacity=1.0), tex(str(d), 44, getattr(C, f"d{d}"))).move_to(P3(*cen))
        numerals.play(FadeIn(disc, scale=0.8), at=light_at[d], dur=0.6)
        numerals.play(FadeOut(disc), at=t1 - 0.6, dur=0.5)

    # ---- 'Two numbers out of sixty-four', then the name
    title = sans(r"\textbf{PCA}", 64)
    sub = caps("principal component analysis", 34, C.muted)
    VGroup(title, sub).arrange(DOWN, buff=0.18).move_to(P3(0, -2.55))
    m.play(Write(sub), at=t_pca, dur=1.4)
    m.play(FadeIn(title, shift=0.1 * UP), at=t_name, dur=0.6)
    for mob in (title, sub):
        m.play(FadeOut(mob), at=t1 - 0.6, dur=0.5)
