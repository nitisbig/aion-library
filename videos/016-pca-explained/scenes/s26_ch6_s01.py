"""ch6_s01 · Units matter (L2, rail: B_recipe, B_scree).

Chapter card (carry-over strip: the scree). The people cloud on the centred plane, with its PC1 (gold). The units
change continuously (a pure function of the scale factors, interpolated in log space): on 'millimetres' height is
multiplied by 10, on 'metres' arm span by 1/100. The plot keeps equal aspect and fits the larger spread, so the cloud
flattens onto the height axis and PC1 (recomputed from the scaled data every frame) turns flat along it. The two
variances in their units on 'thousand times bigger'. On 'same footing' each measurement is divided by its own spread
(z = x / σ): the cloud comes back round and PC1 sits at 45°.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, P3, PHI1, STAGE_IN, STAGE_L2, backed, board, chapter_card, glow_layer, grid_lines, rail_recipe,
                 rail_scree, sans, udir)

W = 3.0                                           # 3 sd of the larger measurement spans this many units


@scene(T.ch6_s01, T.ch6_s02)
def ch6_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_mm, t_m, t_k = float(T.ch6_s01_millimetres), float(T.ch6_s01_metres), float(T.ch6_s01_thousand_times_bigge)
    t_h, t_f, t_own = float(T.ch6_s01_straight_along_heigh), float(T.ch6_s01_same_footing), float(T.ch6_s01_own_spread)
    P = pd.people2()
    Xc = P.Xc
    sd = Xc.std(0)
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))

    # ---- card; strip = the scree
    on = chapter_card(s, t0, t0 + 2.6, "chapter six", "Where PCA Breaks")
    strip = s.manim(z=20, opacity=on * 0.5)
    strip.add(rail_scree().move_to(P3(0, -2.35)))
    back = keys((t0, 0.0), (t0 + 2.2, 0.0), (t0 + 3.0, 1.0))
    st = s.manim(z=0, opacity=back)
    st.add(board(STAGE_L2), rail_recipe(), rail_scree())

    # ---- the unit scales, in log10: cm -> (mm, cm) -> (mm, m) -> z
    lz = np.log10(1.0 / sd)
    lx = keys((t0, 0.0), (t_mm - 0.1, 0.0), (t_mm + 1.2, 1.0), (t_f + 0.4, 1.0), (t_own + 0.4, float(lz[0])))
    ly = keys((t0, 0.0), (t_m - 0.1, 0.0), (t_m + 1.2, -2.0), (t_f + 0.4, -2.0), (t_own + 0.4, float(lz[1])))
    pc_on = keys((t0, 1.0), (t_mm - 0.4, 1.0), (t_mm, 0.25), (t_h - 0.3, 0.25), (t_h + 0.4, 1.0))
    cl_on = keys((t0, 0.0), (t0 + 2.4, 0.0), (t0 + 3.2, 1.0))

    def scaled(t):
        sc = np.array([10 ** float(lx(t)), 10 ** float(ly(t))])
        Y = Xc * sc
        k = W / (3 * max(Y.std(0)))
        return Y * k, k * sc

    def pc1_deg(Y):
        w, V = np.linalg.eigh(np.cov(Y.T))
        v = V[:, -1] * (1 if V[0, -1] + V[1, -1] >= 0 else -1)
        return math.degrees(math.atan2(v[1], v[0]))

    def plot(t):
        a = float(cl_on(t))
        if a <= 0.001:
            return VGroup()
        Y, ks = scaled(t)
        g = VGroup(grid_lines(np.eye(2), CEN0, 1.05, STAGE_IN, n=12, minor=2, opacity=0.8 * a))
        g.add(*[bead(P3(*(CEN0 + q)), a=a) for q in Y])
        d = pc1_deg(Y)
        L = 3.6
        g.add(Line(P3(*(CEN0 - L * udir(d))), P3(*(CEN0 + L * udir(d))), stroke_color=C.pc1, stroke_width=4.5,
                   stroke_opacity=a * float(pc_on(t))))
        return g

    pm = s.manim(z=1, opacity=end)
    pm.redraw(plot, during=(t0 + 2.3, t1))
    gl = glow_layer(s, z=0.9, color=C.pc1, k=0.6, opacity=end * keys((t0, 0.0), (t_h - 0.1, 0.0), (t_h + 0.6, 1.0),
                                                                       (t_h + 2.6, 1.0), (t_h + 3.2, 0.0)))
    gl.add(Line(P3(CEN0[0] - 3.6, CEN0[1]), P3(CEN0[0] + 3.6, CEN0[1]), stroke_color=C.pc1, stroke_width=4.5))

    # ---- the axis names carry the units
    m = s.manim(z=3, opacity=end)
    hx, ay = P3(CEN0[0] + 3.4, CEN0[1] - 0.3), P3(CEN0[0] + 0.95, STAGE_IN[3] - 0.3)

    def names(h, a_):
        return VGroup(backed(sans(h, 26, C.muted)).move_to(hx), backed(sans(a_, 26, C.muted)).move_to(ay))

    n0 = names("height (cm)", "arm span (cm)")
    n1 = names("height (mm)", "arm span (cm)")
    n2 = names("height (mm)", "arm span (m)")
    n3 = names(r"height $/\,\sigma$", r"arm span $/\,\sigma$")
    m.play(FadeIn(n0), at=t0 + 3.0, dur=0.6)
    m.play(ReplacementTransform(n0, n1), at=t_mm, dur=0.6)
    m.play(ReplacementTransform(n1, n2), at=t_m, dur=0.6)
    m.play(ReplacementTransform(n2, n3), at=t_own, dur=0.6)

    # ---- the two variances, a factor of about a million apart
    v = Xc.var(0)
    e = VGroup(Eqn(rf"\mathrm{{Var}}(h) \approx {v[0] * 100:,.0f}\ \mathrm{{mm}}^2".replace(",", r"\,"),
                   colors={r"\mathrm{Var}(h)": C.spread}, size=38),
               Eqn(rf"\mathrm{{Var}}(a) \approx {v[1] / 1e4:.4f}\ \mathrm{{m}}^2", colors={r"\mathrm{Var}(a)": C.spread},
                   size=38)).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    eb = backed(e, 0.08).move_to(P3(STAGE_IN[0] + 0.25, 2.55), aligned_edge=LEFT)
    m.play(FadeIn(eb, shift=DOWN * 0.1), at=t_k, dur=0.8)
    m.play(FadeOut(eb), at=t_f - 0.3, dur=0.5)
    z = backed(Eqn(r"z = x \,/\, \sigma", colors={r"\sigma": C.spread}, size=48), 0.08)
    z.move_to(P3(STAGE_IN[0] + 0.25, 2.65), aligned_edge=LEFT)
    m.play(Write(z), at=t_f + 0.6, dur=1.0)
