"""c10_s02 · Cancel the randomness (equation). Storyboard: plan/scene_plan.md § c10_s02. Layout L2.

Opens on c10_s01's last frame (the price chart, the first paths setting out, max(S − K, 0)). 'Black': name tag.
'random walk': 2,000 risk-neutral GBM paths (σ 20 %, r 3 %, seeded) fan out from 100, drawn as a density, and at a
year from now their prices pile into a histogram, with the log-normal curve over it. 'mix': in the right column,
the option's value along one path and a mix of shares and cash rebalanced daily (Δ hedging, computed) move together,
and their difference stays flat: the randomness cancels. 'equation': the Black–Scholes equation writes, its terms
tagged. 'heat equation': it becomes ∂u/∂τ = ∂²u/∂x², the heat term in Fourier's hue, and on 'bar of hot metal'
Fourier's bar from the opening returns, cooling (sims.heat_bar, exact).
"""
import numpy as np
from aion import *

import ch10
import sims as sm
from beats import T
from kit import chapter_backdrop, P3, RC, add_rail, fit, glow, glimpse, polyline, sans, smooth01, tag_under, tint


@scene(T.c10_s02, T.c10_s03)
def s32_c10_cancel(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 10)
    t0 = float(s.start)
    t_bl, t_rw, t_mx, t_eq, t_he, t_bar = (T.c10_s02_black, T.c10_s02_random_walk, T.c10_s02_mix,
                                           T.c10_s02_equation, T.c10_s02_heat_equation, T.c10_s02_bar_of_hot_metal)
    add_rail(s, 10)
    hud = s.manim(z=50, parallax=0.0)

    # carried from c10_s01: the chart, the first paths, the payoff formula
    c_op = fade(t0 - 5, dur=0.1, out=t_eq - 0.5, out_dur=0.6)
    s.manim(z=4, parallax=0.0, opacity=c_op).add(ch10.chart_axes())
    few_op = fade(t0 - 5, dur=0.1, out=t_rw + 1.6, out_dur=0.8)
    s.manim(z=3, parallax=0.0).redraw(lambda t: ch10.few_paths(t, float(T.c10_s01_today) + 0.3, float(few_op(t))),
                                      during=(t0, t_rw + 2.6))
    e0 = Eqn(r"\max(S-K,\,0)", colors={"S": C.text, "K": C.text})
    e0.scale(1.1).move_to(P3(RC, 1.6))
    s.manim(z=50, parallax=0.0, opacity=fade(t0 - 5, dur=0.1, out=t_mx - 0.5, out_dur=0.5)).add(
        e0, tag_under(e0, "S", "price", C.muted), tag_under(e0, "K", "100", C.muted))
    glimpse(s, "photo:nyse_1963.jpg", t_bl + 0.2, C.bs, h=2.1)   # the trading floor the equation changed

    # a random walk: 2,000 paths, revealed as time runs to a year from now
    img = ch10.fan_rgba()
    W = img.shape[1]
    t_f = float(t_rw) - 0.1

    def fan(t):
        u = float(smooth01((t - t_f) / 2.4))
        out = img.copy()
        out[:, int(u * W):, 3] = 0
        return out
    cen = ((ch10.OX + ch10.TX) / 2, (ch10.CY0 + ch10.CY1) / 2)
    s.add(FramesLayer(fan, height=ch10.CY1 - ch10.CY0, pos=cen, z=2, parallax=0.0, opacity=c_op,
                      during=[(t_rw - 0.3, t_he + 0.4)]))
    counts, edges = ch10.expiry_hist()
    LMAX = 0.85
    t_h = t_f + 2.3

    def hist(t):
        a = float(c_op(t))
        u = float(smooth01((t - t_h) / 1.0))
        g = VGroup()
        if a < 0.01 or u <= 0:
            return g
        for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
            L = LMAX * c / counts.max() * u
            if L > 0.005:
                y0, y1 = float(ch10.cy(lo)), float(ch10.cy(hi))
                g.add(Rectangle(width=L, height=(y1 - y0) * 0.86, stroke_width=0, fill_color=C.bs, fill_opacity=0.55 * a)
                      .move_to(P3(ch10.TX + 0.04 + L / 2, (y0 + y1) / 2)))
        return g
    s.manim(z=5, parallax=0.0).redraw(hist, during=(t_h - 0.1, t_he + 0.4))
    Sg = np.linspace(ch10.P_LO, ch10.P_HI, 200)
    pdf = ch10.lognormal_pdf(Sg)
    per = 2000 * (edges[1] - edges[0]) / counts.max()                     # expected count per bin, over the tallest
    curve = polyline([(ch10.TX + 0.04 + LMAX * p * per, float(ch10.cy(S_))) for S_, p in zip(Sg, pdf)], C.light, 1.8,
                     0.85)
    s.manim(z=6, parallax=0.0, opacity=c_op).play(Create(curve), at=t_h + 0.9, dur=0.8)

    # the mix: shares and cash that move exactly like the option
    th, Sh, Vh, Ph = ch10.hedge()
    IX0, IX1, IY0, IY1 = 2.95, 6.3, 0.75, 2.25
    vmax = max(Vh.max(), Ph.max()) * 1.05
    ip = lambda tt, v: (IX0 + (IX1 - IX0) * tt, IY0 + (IY1 - IY0) * v / vmax)
    i_op = fade(t_mx - 0.2, dur=0.5, out=t_eq - 0.6, out_dur=0.5)
    t_i = float(t_mx) + 0.3

    def inset(t):
        a = float(i_op(t))
        u = float(smooth01((t - t_i) / 3.2))
        g = VGroup()
        if a < 0.01:
            return g
        k = max(int(u * (len(th) - 1)), 1)
        g.add(Line(P3(IX0, IY0), P3(IX1, IY0), stroke_color=tint(C.muted, 0.6), stroke_width=1.2, stroke_opacity=a))
        g.add(polyline([ip(a_, b_) for a_, b_ in zip(th[:k + 1], Vh[:k + 1])], C.payoff, 3.0, a))
        g.add(polyline([ip(a_, b_) for a_, b_ in zip(th[:k + 1], Ph[:k + 1])], C.bs, 2.0, a))
        dy = -0.55
        g.add(Line(P3(IX0, IY0 + dy), P3(IX1, IY0 + dy), stroke_color=tint(C.muted, 0.35), stroke_width=1.0,
                   stroke_opacity=a))
        dv = (Ph - Vh)[:k + 1]
        g.add(polyline([(ip(a_, 0)[0], IY0 + dy + (IY1 - IY0) * d / vmax) for a_, d in zip(th[:k + 1], dv)], C.text,
                       2.2, a * float(smooth01((t - t_i - 1.4) / 0.6))))
        return g
    s.manim(z=6, parallax=0.0).redraw(inset, during=(t_mx - 0.3, t_eq))
    il = s.manim(z=50, parallax=0.0, opacity=i_op)
    il.add(VGroup(sans("option", 22, C.payoff), sans("shares + cash", 22, C.bs)).arrange(RIGHT, buff=0.45)
           .move_to(P3(IX0, IY1 + 0.35), aligned_edge=LEFT))
    il.play(FadeIn(sans("difference: no randomness left", 20, C.text).move_to(P3(IX0, IY0 - 0.85), aligned_edge=LEFT)),
            at=t_i + 1.9, dur=0.5)

    # the equation that remains
    pde = Eqn(r"\frac{\partial V}{\partial t}+\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}"
              r"+rS\frac{\partial V}{\partial S}-rV=0",
              colors={r"\frac{\partial V}{\partial t}": C.text,
                      r"\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}": C.text,
                      r"rS\frac{\partial V}{\partial S}": C.text, "rV": C.text})
    pde.scale(1.25).move_to(P3(0, 0.9))
    hud.play(Write(pde), at=t_eq - 0.1, dur=1.4)
    below = VGroup(tag_under(pde, r"\frac{\partial V}{\partial t}", "time", C.muted, size=24),
                   tag_under(pde, r"rS\frac{\partial V}{\partial S}", "drift", C.muted, size=24))
    above = VGroup(sans("wobble", 24, C.muted).next_to(pde.part(r"\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}"),
                                                        UP, buff=0.18),
                   sans("interest", 24, C.muted).next_to(pde.part("rV"), UP, buff=0.18))
    for m_ in above:
        m_.set_y(pde.get_top()[1] + 0.3)
    tags = VGroup(below, above)
    hud.play(FadeIn(tags, lag_ratio=0.2), at=t_eq + 1.2, dur=0.8)

    # the heat equation, and Fourier's bar
    heat = Eqn(r"\frac{\partial u}{\partial \tau}=\frac{\partial^2 u}{\partial x^2}",
               colors={r"\frac{\partial^2 u}{\partial x^2}": C.fourier})
    heat.scale(1.3).move_to(P3(0, 1.2))
    hud.play(FadeOut(tags), at=t_he - 0.2, dur=0.4)
    hud.play(FadeTransform(pde, heat), at=t_he + 0.1, dur=1.0)
    hud.play(FadeIn(tag_under(heat, r"\frac{\partial^2 u}{\partial x^2}", "heat equation", C.fourier)), at=t_he + 0.9,
             dur=0.5)
    b_op = fade(t_he + 0.3, dur=0.7)
    s.manim(z=3, parallax=0.0).redraw(lambda t: ch10.hot_bar(t, float(t_bar) - 0.3, b_op), during=(t_he + 0.1, s.end))
