"""ch5_s01 · A ripple (Chapter 5 hook).

The map as Chapter 4 left it gives way to Change's card, which shrinks into a stone above the water. On 'stone' it
drops: a ripple spreads (outgoing ring packets, computed per frame, drawn as a contoured field like the intro's pond).
On 'circle' the leading crest is traced by the circle, a ruler of evenly spaced ticks along its radius; on 'steady' a
readout r = 1, 2, 3 … ticks at an even pace. On 'expect' A = πr² comes up beside a dashed line for 'steady growth'. On
'doesn't' the new water of each step lights as a ring on the pond and as a bar (1, 3, 5, … × π) that climbs past the
dashed line. On 'calculus' the word comes up.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, caps, glow_layer, rgb255, chapter_card, map_state, node_xy, sans, tex, the_circle, tint, window, hub_at

LIT = ("foundations", "quantity", "structure", "space")
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"))
PC = P3(-3.5, -0.3)                  # the drop
UNIT = 0.5                           # world units per unit of radius
STEP = 2.2                           # seconds per unit of radius (the ripple's steady pace)
NMAX = 6
BAR_X0, BAR_DX, BAR_W, BAR_Y, BAR_K = 1.35, 0.86, 0.56, -2.55, 0.37


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch5_s01, T.ch5_s02)
def ch5_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    card_l = s.manim(z=3, parallax=0)
    lit = glow_layer(s, z=1.5, color=C.circle)
    t0, t1 = float(s.start), float(s.end)
    t_st, t_ci, t_sd = float(T.ch5_s01_stone), float(T.ch5_s01_circle), float(T.ch5_s01_steady)
    t_ex, t_dn, t_ca = float(T.ch5_s01_expect), float(T.ch5_s01_doesn_t), float(T.ch5_s01_calculus)
    t_every, t_inst = t_dn + 1.35, t_dn + 9.55                              # 'Every second' 'single instant'
    Ch = C.change
    out_t = t1 - 0.75

    # the map as Chapter 4 left it; Change's card; it shrinks into the stone
    links, nodes = map_state(240, lit=LIT, edges=EDGES)
    hub = hub_at(240)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)
    lnk.play(FadeOut(links), at=t0 + 0.1, dur=0.45)
    nd.play(FadeOut(VGroup(*(nodes[k] for k in (0, 1, 2, 3, 5)))), at=t0 + 0.1, dur=0.45)
    nd.play(FadeOut(nodes[4], scale=1.6), at=t0 + 0.15, dur=0.45)
    m.play(FadeOut(hub), at=t0 + 0.1, dur=0.45)
    card = chapter_card("change", "rates of change")
    card_l.play(GrowFromPoint(card, node_xy(4, turn=240)), at=t0 + 0.2, dur=0.7, ease="easy_ease")
    sky = PC + P3(0, 2.6)
    card_l.play(card.animate.scale(0.03).move_to(sky).set_opacity(0), at=t_st - 1.0, dur=0.55, ease="easy_ease")
    card_l.remove(card, at=t_st - 0.4)

    # the stone falls
    stone = Dot(sky, radius=0.1, color=C.text)
    top.add(stone, at=t_st - 0.5)
    top.play(stone.animate.move_to(PC).scale(0.6), at=t_st - 0.45, dur=0.45, ease="in_cubic")
    top.remove(stone, at=t_st)
    t_d = t_st                                                    # the drop

    # the ripple: outgoing ring packets behind a front moving at a steady pace, rendered as lit water
    side, n_g = 7.6, 420
    yy, xx = np.mgrid[0:n_g, 0:n_g]
    gx_, gy_ = (xx - (n_g - 1) / 2) / (n_g / 2) * (side / 2), ((n_g - 1) / 2 - yy) / (n_g / 2) * (side / 2)
    rr = np.hypot(gx_, gy_)
    mask = 1 - np.clip((rr - 3.22) / 0.06, 0, 1)
    c_f, c_p, lam = UNIT / STEP, 0.42, 0.42
    dx = side / n_g

    def front(t):
        return min(c_f * max(t - t_d, 0.0), NMAX * UNIT)

    def height(t):
        age = t - t_d
        h = 0.004 * (np.sin(2.1 * gx_ + 1.3 * gy_ + 0.9 * t) + np.sin(-1.7 * gx_ + 2.3 * gy_ + 0.7 * t))  # calm swell
        if age > 0:
            fr = c_f * age
            behind = np.clip((fr - rr) / 0.55, 0, None)
            env = np.exp(-behind) * (rr < fr) * np.clip((fr - rr) / 0.12, 0, 1)
            h = h + 0.05 * env * np.cos(2 * np.pi * (rr - c_p * age) / lam) / np.sqrt(0.6 + rr) * np.exp(-0.05 * age)
        return h

    def rgbf(c):
        return np.array(rgb255(c), np.float32) / 255.0

    deep, sky, spec_c = rgbf(tint(C.foundations, 0.018)), rgbf(tint(C.foundations, 0.3)), rgbf(C.circle)
    L = np.array([-0.45, 0.55, 0.70])
    L = L / np.linalg.norm(L)
    Hv = (L + np.array([0, 0, 1.0]))
    Hv = Hv / np.linalg.norm(Hv)
    rim = np.exp(-((rr - 3.2) / 0.12) ** 2)                       # a faint lit bank at the pond's edge
    f_on = fade(t_st - 1.4, dur=1.0, out=t1 - 0.8, out_dur=0.7)

    def water(t):
        h = height(t)
        hy, hx = np.gradient(h, dx)
        nx, ny = -hx * 5.0, hy * 5.0
        nz = np.ones_like(nx)
        inv = 1 / np.sqrt(nx * nx + ny * ny + nz * nz)
        nx, ny, nz = nx * inv, ny * inv, nz * inv
        dif = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        spec = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** 90
        fres = (1 - nz) * 2.2
        col = (deep[None, None, :] * (0.55 + 0.6 * dif[..., None])
               + sky[None, None, :] * np.clip(fres, 0, 0.35)[..., None]
               + spec_c[None, None, :] * (1.3 * spec)[..., None]
               + sky[None, None, :] * (0.35 * rim)[..., None])
        a = mask * float(f_on(t))
        rgba = np.empty((n_g, n_g, 4), np.uint8)
        rgba[..., :3] = (np.clip(col, 0, 1) * a[..., None] * 255).astype(np.uint8)
        rgba[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        return rgba

    t_calm = t_d + NMAX * STEP
    s.add(FramesLayer(water, height=side, pos=tuple(PC[:2]), during=[(t_st - 1.45, t1)], premultiplied=True, z=-3))

    # the circle on the leading crest, and a ruler along its radius
    def crest(t):
        R = front(t)
        f = ss((t - t_ci + 0.3) / 0.5) * (1 - ss((t - out_t) / 0.6))
        if R < 0.02:
            return VGroup()
        pulse = 1 + 1.2 * math.exp(-((t - t_inst - 0.3) / 0.35) ** 2)
        g = VGroup(Circle(radius=R, stroke_color=C.circle, stroke_width=5 * pulse, stroke_opacity=f).move_to(PC))
        k = ss((t - t_sd + 0.4) / 0.5) * f
        if k > 0:
            g.add(Line(PC, PC + P3(R, 0), stroke_color=C.circle, stroke_width=2.4, stroke_opacity=k))
            for n in range(1, NMAX + 1):
                if n * UNIT <= R + 1e-6:
                    x = PC + P3(n * UNIT, 0)
                    g.add(Line(x + P3(0, -0.1), x + P3(0, 0.1), stroke_color=C.circle, stroke_width=2.4,
                               stroke_opacity=k))
        return g

    lit.redraw(window(crest, t_ci - 0.3, t1 - 0.05), during=(t_ci - 0.3, t1))

    # 'steady': r = 1, 2, 3 … at an even pace
    def readout(t):
        n = int(front(t) / UNIT + 1e-6)
        f = ss((t - t_sd + 0.3) / 0.4) * (1 - ss((t - out_t) / 0.6))
        if n < 1:
            return VGroup()
        r = tex(rf"r = {n}", 46, C.circle).move_to(PC + P3(0, 3.55)).set_opacity(f)
        return r

    m.redraw(window(readout, t_sd - 0.3, t1 - 0.05), during=(t_sd - 0.3, t1))

    # 'expect': A = πr², and the guess that it grows steadily
    eq = MathTex("A", "=", r"\pi", "r^2", font_size=56, color=C.text)
    eq[0].set_color(Ch)
    eq[3].set_color(C.circle)
    eq.move_to(P3(3.75, 2.85))
    m.play(Write(eq), at=t_ex + 0.5, dur=0.8)
    base = Line(P3(BAR_X0 - 0.5, BAR_Y), P3(BAR_X0 + BAR_DX * (NMAX - 1) + 0.5, BAR_Y), stroke_color=C.axis,
                stroke_width=2.4)
    cap = sans("new water, each step", 28, C.muted).next_to(base, DOWN, buff=0.22)
    guess_y = BAR_Y + BAR_K * 1
    guess = DashedLine(P3(BAR_X0 - 0.5, guess_y), P3(BAR_X0 + BAR_DX * (NMAX - 1) + 0.5, guess_y),
                       dash_length=0.12, stroke_color=C.muted, stroke_width=2.4)
    g_lab = sans("steady?", 28, C.muted).next_to(guess, LEFT, buff=0.12)
    m.play(Create(base), FadeIn(cap), at=t_ex - 0.1, dur=0.6)
    m.play(Create(guess), FadeIn(g_lab), at=t_ex + 0.9, dur=0.7)

    # 'doesn't': each step's new water, as a ring on the pond and a bar
    bars, tags, rings = VGroup(), VGroup(), VGroup()
    for n in range(1, NMAX + 1):
        h = BAR_K * (2 * n - 1)
        x = BAR_X0 + BAR_DX * (n - 1)
        bars.add(Rectangle(width=BAR_W, height=h, stroke_color=Ch, stroke_width=2.4, fill_color=Ch, fill_opacity=0.35)
                 .move_to(P3(x, BAR_Y + h / 2)))
        tags.add(tex(rf"{2 * n - 1}\pi" if n > 1 else r"\pi", 30, Ch).move_to(P3(x, BAR_Y + h + 0.3)))
        a_ = Annulus(inner_radius=max((n - 1) * UNIT, 0.001), outer_radius=n * UNIT, stroke_width=0, fill_color=Ch,
                     fill_opacity=0.4).move_to(PC)
        rings.add(a_)
    t_b = t_dn + 0.2
    for n in range(NMAX):
        tb = t_b + 0.62 * n
        m.play(GrowFromEdge(bars[n], DOWN), FadeIn(tags[n]), at=tb, dur=0.45, ease="out_cubic")

    def ring_fx(t):                                           # each ring flashes as its bar grows, then stays faint
        g = VGroup()
        f = 1 - ss((t - out_t) / 0.6)
        for n in range(NMAX):
            u = t - (t_b + 0.62 * n)
            if u < -0.05:
                break
            op = 0.045 + 0.3 * math.exp(-max(u, 0) / 0.35)       # compositing is linear: low alphas read strong
            g.add(rings[n].copy().set_fill(opacity=op * f))
        return g

    m.redraw(window(ring_fx, t_b - 0.05, t1 - 0.05), during=(t_b - 0.05, t1))
    m.play(guess.animate.set_stroke(opacity=0.5), g_lab.animate.set_opacity(0.5), at=t_every, dur=0.5)

    # 'calculus'
    word = caps("calculus", 60, Ch).move_to(P3(0, 3.3))
    m.play(FadeOut(VGroup(eq)), at=t_ca - 0.9, dur=0.4)
    m.play(FadeIn(word, shift=0.1 * DOWN), at=t_ca - 0.15, dur=0.5)

    # out (the word stays for ch5_s02 to take)
    m.play(FadeOut(VGroup(base, cap, guess, g_lab, bars, tags)), at=out_t, dur=0.6)
