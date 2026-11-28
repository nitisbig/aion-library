"""c09_s03 · Updating (payoff). Storyboard: plan/scene_plan.md § c09_s03. Layout L1.

Opens on c09_s02's last frame (the area square and the lit rule), which gives way to a ribbon of belief curves.
'clue': a flat belief, then, one step deeper each time, the Beta posterior after more seeded clues (coin flips,
p = 0.7), each sharper (ch9.belief), ending in a tall narrow peak; the ribbon turns slowly. 'Spam', 'self-driving':
an envelope and a car come in on the right. 'Air France': an ocean search map: a prior around the last known
position; the areas already searched (detection 85 %) lose probability, which flows to the cells nobody searched
(ch9.search_maps, an exact update); on 'week' the wreck turns up in the brightest cell. 'uncertain': the sharp
belief returns and widens; 'price': it turns on its side onto a price chart, a year ahead: the bridge to chapter 10.
"""
import math

import numpy as np
from aion import *

import ch9
from beats import T
from kit import chapter_backdrop, P3, RC, add_rail, glow, mix, polyline, sans, smooth01, tint


def _carry(s, out):
    op = fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.7)
    g, gl = ch9.rule_final()
    s.manim(z=50, parallax=0.0, opacity=op).add(g)
    glow(s, C.positive, z=5, k=0.7, parallax=0.0, opacity=op).add(gl)


@scene(T.c09_s03, T.c10_s01)
def s30_c09_updating(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 9, last=True)
    t0 = float(s.start)
    t_cl, t_sp, t_sd, t_af, t_wk, t_un, t_pr = (T.c09_s03_clue, T.c09_s03_spam, T.c09_s03_self_driving,
                                                T.c09_s03_air_france, T.c09_s03_week, T.c09_s03_uncertain,
                                                T.c09_s03_price)
    _carry(s, t0 + 0.2)
    add_rail(s, 9)
    hud = s.manim(z=50, parallax=0.0)

    # the ribbon of beliefs, sharpening clue by clue, one step deeper each time
    t_rb = float(t_cl) - 1.1
    r_op = fade(t0 + 0.4, dur=0.6, out=t_af - 2.6, out_dur=0.7)
    yaw = lambda t: -0.18 + 0.3 * float(smooth01((t - t0) / 12.0))
    N = ch9.N_CURVES

    def ribbon(t):
        a = float(r_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        shown = [k for k in range(N) if t > t_rb + 0.42 * k]
        for k in sorted(shown, reverse=True):                   # deepest first, so nearer curves hide them
            u = float(smooth01((t - t_rb - 0.42 * k) / 0.5))
            pts, base = ch9.ribbon_curve(k, yaw(t))
            pts = pts.copy()
            pts[:, 1] = base[1] + (pts[:, 1] - base[1]) * u
            col = mix(C.prior, C.bayes, k / (N - 1))
            poly = [tuple(p) for p in pts]
            g.add(Polygon(*[P3(*p) for p in poly + [(pts[-1, 0], base[1]), (pts[0, 0], base[1])]],
                          stroke_width=0, fill_color=C.bg, fill_opacity=0.92 * a),
                  Line(P3(pts[0, 0], base[1]), P3(pts[-1, 0], base[1]), stroke_color=tint(C.muted, 0.5),
                       stroke_width=1.2, stroke_opacity=a),
                  polyline(poly, col, 3.2 if k == N - 1 else 2.2, a * u))
        return g
    s.manim(z=4, parallax=0.0).redraw(ribbon, during=(t0, t_af - 1.8))

    def peak_glow(t):                                           # only the newest, sharpest belief glows
        a = float(r_op(t)) * float(smooth01((t - t_rb - 0.42 * (N - 1)) / 0.5))
        if a < 0.01:
            return VGroup()
        pts, _ = ch9.ribbon_curve(N - 1, yaw(t))
        return polyline([tuple(p) for p in pts], C.bayes, 3.2, a)
    glow(s, C.bayes, z=4.5, k=0.8, parallax=0.0).redraw(peak_glow, during=(t0, t_af - 1.8))

    def labels(t):
        a = float(r_op(t))
        if a < 0.01:
            return VGroup()
        _, b0 = ch9.ribbon_curve(0, yaw(t))
        _, b7 = ch9.ribbon_curve(N - 1, yaw(t))
        d = np.array(b7) - np.array(b0)
        tip = np.array(b7) + ch9.RB_W * np.array([1, 0]) + 0.15 * d / np.linalg.norm(d)
        last = float(smooth01((t - t_rb - 0.42 * (N - 1)) / 0.5))
        return VGroup(sans("more clues", 22, C.muted).move_to(P3(*(tip + np.array([0.75, 0.2])))).set_opacity(a),
                      sans("before", 22, C.prior).move_to(P3(b0[0] + ch9.RB_W / 2, b0[1] - 0.35)).set_opacity(a),
                      sans("after", 22, C.bayes).move_to(P3(*(np.array(b7) + np.array([ch9.RB_W * 0.7, 2.25]))))
                      .set_opacity(a * last))
    s.manim(z=50, parallax=0.0).redraw(labels, during=(t_cl - 0.2, t_af - 1.8))

    # spam filters and self-driving cars
    ic_op = fade(t0, dur=0.1, out=t_af - 2.6, out_dur=0.7)
    im = s.manim(z=50, parallax=0.0, opacity=ic_op)
    env, cr = ch9.envelope().move_to(P3(RC + 0.55, 1.9)), ch9.car().move_to(P3(RC + 0.55, -0.55))
    im.play(FadeIn(VGroup(env, sans("spam filters", 22, C.muted).next_to(env, DOWN, buff=0.25)), shift=0.2 * LEFT),
            at=t_sp, dur=0.6)
    im.play(FadeIn(VGroup(cr, sans("self-driving cars", 22, C.muted).next_to(cr, DOWN, buff=0.3)), shift=0.2 * LEFT),
            at=t_sd, dur=0.6)

    # Air France 447: the search map
    prior, searched, post, wreck = ch9.search_maps()
    nx, ny = ch9.MAP_N
    m_op = fade(t_af - 1.8, dur=0.9, out=t_un - 0.4, out_dur=0.6)
    t_fl = float(t_af) + 0.7
    flow = lambda t: float(smooth01((t - t_fl) / 1.8))
    pmax = max(prior.max(), post.max())

    def heat(t):
        a = float(m_op(t))
        if a < 0.01:
            return VGroup()
        P = prior + (post - prior) * flow(t)
        g = VGroup()
        for i in range(ny):
            for j in range(nx):
                x, y, w, h = ch9.cell_rect(i, j)
                v = (P[i, j] / pmax) ** 0.75
                g.add(Rectangle(width=w * 0.92, height=h * 0.92, stroke_width=0, fill_color=C.bayes,
                                fill_opacity=a * (0.05 + 0.9 * v)).move_to(P3(x + w / 2, y + h / 2)))
        return g
    s.manim(z=3, parallax=0.0).redraw(heat, during=(t_af - 2.0, t_un + 0.4))
    x0, x1, y0, y1 = ch9.MAP_BOX
    mp = lambda u, v: P3(x0 + u * (x1 - x0), y1 - v * (y1 - y0))
    mm = s.manim(z=6, parallax=0.0, opacity=m_op)
    lkp = mp(*ch9.LKP)
    mm.play(FadeIn(VGroup(Dot(lkp, radius=0.06, color=C.light),
                          sans("last position", 20, C.text).next_to(lkp, DOWN, buff=0.14))), at=t_af - 1.0, dur=0.5)
    boxes = VGroup()
    for (j0, j1, i0, i1) in ch9.SEARCHED:                      # exactly the searched cells' outer edges
        xa, ya, _, _ = ch9.cell_rect(i1, j0)
        xb, yb, w, h = ch9.cell_rect(i0, j1)
        c = [P3(xa, ya), P3(xb + w, ya), P3(xb + w, yb + h), P3(xa, yb + h)]
        boxes.add(*[DashedLine(c[k], c[(k + 1) % 4], dash_length=0.08, stroke_color=C.text, stroke_width=1.4)
                    for k in range(4)])
    mm.play(Create(boxes), at=t_af + 0.1, dur=0.8)
    mm.play(FadeIn(sans("searched", 22, C.text).next_to(boxes[4:8], UP, buff=0.12)), at=t_af + 0.3, dur=0.5)
    mm.play(FadeIn(VGroup(sans("Air France 447", 26, C.text), sans("2011", 22, C.muted))
                    .arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(P3(2.75, 1.5), aligned_edge=LEFT)),
             at=t_af, dur=0.6)
    wi, wj = wreck
    wx, wy, w, h = ch9.cell_rect(wi, wj)
    wc = P3(wx + w / 2, wy + h / 2)
    mm.play(Create(Circle(radius=0.2, stroke_color=C.light, stroke_width=2.6).move_to(wc)), at=t_wk, dur=0.5)
    mm.play(FadeIn(sans("wreck", 22, C.text).next_to(wc, UP + LEFT, buff=0.2)), at=t_wk + 0.2, dur=0.4)

    def ping(t):
        g = VGroup()
        a = float(m_op(t))
        for k in range(2):
            u = (t - float(t_wk) - 0.1 - 0.7 * k) / 1.4
            if 0 < u < 1:
                g.add(Circle(radius=0.2 + 0.9 * u, stroke_color=C.light, stroke_width=2,
                             stroke_opacity=a * (1 - u)).move_to(wc))
        return g
    glow(s, C.light, z=7, k=0.6, parallax=0.0).redraw(ping, during=(t_wk, t_un))

    # uncertain: the belief widens; price: it turns onto a price chart
    t_w, t_p = float(t_un) - 0.2, float(t_pr)
    b_op = fade(t_un - 0.4, dur=0.5)
    a7, b7 = ch9.belief(N - 1)
    mu, sd0 = a7 / (a7 + b7), math.sqrt(a7 * b7 / ((a7 + b7) ** 2 * (a7 + b7 + 1)))
    OX, TX, PY0, PY1 = -4.6, 2.2, -2.3, 2.2                    # chart: price axis at OX, a year ahead at TX
    xs = np.linspace(0, 1, 160)

    def bell(t):
        a = float(b_op(t))
        if a < 0.01:
            return VGroup()
        sd = sd0 + (0.2 - sd0) * float(smooth01((t - t_w) / 1.2))
        y = np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
        flat = np.stack([-3.0 + 6.0 * xs, -1.6 + 0.38 * y], 1)
        side = np.stack([TX + 0.38 * y, PY0 + (PY1 - PY0) * xs], 1)       # on its side: price up, density right
        u = float(smooth01((t - t_p - 0.1) / 1.0))
        q = flat + (side - flat) * u
        return polyline([tuple(p) for p in q], C.bayes, 3.0, a)
    glow(s, C.bayes, z=6, k=0.8, parallax=0.0).redraw(bell, during=(t_un - 0.5, s.end))
    ch = s.manim(z=5, parallax=0.0, opacity=fade(t_pr, dur=0.6))
    today = P3(OX, PY0 + (PY1 - PY0) * mu)
    ch.add(Line(P3(OX, PY0), P3(OX, PY1 + 0.1), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
           Line(P3(OX, PY0), P3(TX + 1.4, PY0), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
           sans("price", 22, C.muted).next_to(P3(OX, PY1 + 0.1), UP, buff=0.1),
           sans("time", 22, C.muted).next_to(P3(TX + 1.4, PY0), RIGHT, buff=0.12),
           DashedLine(P3(TX, PY0), P3(TX, PY1), dash_length=0.08, stroke_color=tint(C.muted, 0.5), stroke_width=1.2),
           sans("a year from now", 20, C.muted).next_to(P3(TX, PY0), DOWN, buff=0.15),
           Dot(today, radius=0.07, color=C.light), sans("today", 20, C.text).next_to(today, LEFT, buff=0.15),
           DashedLine(today, P3(TX, PY0 + (PY1 - PY0) * mu), dash_length=0.08, stroke_color=tint(C.muted, 0.6),
                      stroke_width=1.2))
