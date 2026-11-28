"""ch4_s06 · Maps that forget distance (sighting).

A made-up transit network (three lines, no real names) draws on 'subway' as it lies on the ground: bent lines, uneven
gaps. On 'Harry Beck' a lower third reads H. Beck · 1933. On 'straight lines' the network straightens into horizontal,
vertical and 45° runs with even spacing. On 'Distances' two map gaps that now look the same are tagged with their real
lengths, and the word 'distances' is struck out. On 'connect' a trip from one end of the network to another lights up
and 'connections' comes up; the map slides back to the ground and straightens again, and the trip never breaks.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, caps, sans, window

KM = 1.6                                         # km per world unit on the ground
LINES = {                                        # schematic stations (world units); shared points are interchanges
    "space": [(-5.0, 0.5), (-3.75, 0.5), (-2.5, 0.5), (-1.25, 0.5), (0.0, 0.5), (1.25, 0.5), (2.5, 0.5), (3.75, 0.5),
              (5.0, 0.5)],
    "foundations": [(-2.5, 2.5), (-2.5, 1.5), (-2.5, 0.5), (-1.5, -0.5), (-0.5, -1.5), (-0.5, -2.5)],
    "change": [(-4.5, -1.5), (-3.5, -1.5), (-2.5, -1.5), (-1.5, -1.5), (-0.5, -1.5), (0.5, -1.5), (1.5, -0.5),
               (2.5, 0.5), (2.5, 1.5), (2.5, 2.5)],
}
SEG = 24
TRIP = [("space", 0, 6), ("change", 7, 9)]       # west end of one line → interchange → north end of another


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ground():
    """Where each station really is: the schematic position pushed by a smooth, seeded warp."""
    rg = np.random.default_rng(1933)
    keys = sorted({p for pts in LINES.values() for p in pts})
    jit = {k: rg.normal(0, 0.12, 2) for k in keys}
    out = {}
    for x, y in keys:
        wx = 0.55 * math.sin(0.7 * y + 1.3) + 0.35 * math.sin(1.1 * x + 0.4)
        wy = 0.5 * math.sin(0.8 * x + 2.1) + 0.3 * math.cos(1.3 * y)
        a = math.radians(-6)
        gx, gy = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        sq = 0.28 + 0.17 * math.hypot(gx, gy)                    # the centre is crowded, the suburbs spread out
        g = np.array([gx * sq + 0.8 * wx, gy * sq + 0.8 * wy]) + jit[(x, y)]
        out[(x, y)] = g
    return out


GROUND = ground()


def dense(pts, smooth):
    """SEG samples per gap: straight for the diagram, Catmull–Rom through the stations on the ground."""
    P = np.array(pts, float)
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for s in np.linspace(0, 1, SEG, endpoint=False):
            if smooth:
                s2, s3 = s * s, s * s * s
                q = 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3)
            else:
                q = p1 + s * (p2 - p1)
            out.append(q)
    out.append(P[-1])
    return np.array(out)


SCHEM = {n: dense(pts, False) for n, pts in LINES.items()}
GEO = {n: dense([GROUND[p] for p in pts], True) for n, pts in LINES.items()}
COUNT = {}
for pts in LINES.values():
    for p in pts:
        COUNT[p] = COUNT.get(p, 0) + 1


def poly(q, color, width, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(
        [P3(*r) for r in q])


@scene(T.ch4_s06, T.ch4_s07)
def ch4_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_sub, t_hb, t_sl = float(T.ch4_s06_subway), float(T.ch4_s06_harry_beck), float(T.ch4_s06_straight_lines)
    t_di, t_co = float(T.ch4_s06_distances), float(T.ch4_s06_connect)
    t_wrong, t_right = t_di + 1.28, t_co + 0.88                          # 'everywhere' 'stayed exactly right'
    out_t = t1 - 0.8

    def k_at(t):                                                         # 0 on the ground, 1 the diagram
        k = ss((t - t_sl - 0.1) / 2.5)
        k -= ss((t - t_right + 0.1) / 1.2) * (1 - ss((t - t_right - 1.6) / 1.2))
        return k

    def trip_at(t):
        return ss((t - t_co + 0.1) / 0.6) * (1 - ss((t - out_t + 0.3) / 0.6))

    def net(t):
        k = k_at(t)
        draw = ss((t - t_sub + 0.3) / 1.6)
        pop = ss((t - t_sub - 0.9) / 0.8)
        f = 1 - ss((t - out_t) / 0.6)
        h = trip_at(t)
        g = VGroup()
        for n in LINES:
            q = (1 - k) * GEO[n] + k * SCHEM[n]
            nq = max(2, int(draw * len(q)))
            g.add(poly(q[:nq], getattr(C, n), 7, f * (1 - 0.6 * h)))
        for n, a, b in TRIP:                                             # the trip: full strength, a white core
            q = (1 - k) * GEO[n] + k * SCHEM[n]
            seg = q[a * SEG: b * SEG + 1]
            g.add(poly(seg, getattr(C, n), 7, f * h), poly(seg, C.text, 2.6, f * h))
        if pop > 0:
            for p, c in COUNT.items():
                xy = (1 - k) * GROUND[p] + k * np.array(p)
                big = c > 1
                col = C.text if big else next(getattr(C, n) for n, pts in LINES.items() if p in pts)
                g.add(Circle(radius=(0.17 if big else 0.105) * pop, stroke_color=col, stroke_width=3 if big else 2.6,
                             stroke_opacity=f, fill_color=C.bg, fill_opacity=f).move_to(P3(*xy)))
        ends = [np.array(LINES["space"][0]), np.array(LINES["change"][-1])]
        gends = [GROUND[LINES["space"][0]], GROUND[LINES["change"][-1]]]
        for e, ge in zip(ends, gends):
            if h > 0:
                xy = (1 - k) * ge + k * e
                g.add(Circle(radius=0.3, stroke_color=C.text, stroke_width=3, stroke_opacity=f * h).move_to(P3(*xy)))
        return g

    m.redraw(window(net, t_sub - 0.3, t1 - 0.05), during=(t_sub - 0.3, t1))

    # 'Harry Beck'
    lt = VGroup(caps(r"H.\ Beck\ \textperiodcentered\ 1933", 34, C.text),
                Line(ORIGIN, RIGHT * 3.4, stroke_color=C.muted, stroke_width=1.4))
    lt.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(-6.3, 3.3), aligned_edge=LEFT)
    top.play(FadeIn(lt, shift=0.08 * LEFT), at=t_hb - 0.1, dur=0.6)
    top.play(FadeOut(lt), at=t_di - 1.0, dur=0.5)

    # 'Distances': two gaps that now look equal, tagged with their real lengths
    pts = LINES["space"]
    lens = [np.linalg.norm(GROUND[pts[i + 1]] - GROUND[pts[i]]) for i in range(len(pts) - 1)]
    i_lo, i_hi = int(np.argmin(lens)), int(np.argmax(lens))
    tags, marks = VGroup(), VGroup()
    for i in (i_lo, i_hi):
        a, b = np.array(pts[i]), np.array(pts[i + 1])
        marks.add(Line(P3(*a) + P3(0.2, 0), P3(*b) - P3(0.2, 0), stroke_color=C.text, stroke_width=3))
        tags.add(sans(f"{lens[i] * KM:.1f} km", 28, C.text).move_to(P3(*(a + b) / 2) + P3(0, 0.42)))
    top.play(LaggedStart(*(Create(x_) for x_ in marks), lag_ratio=0.3), at=t_di, dur=0.6)
    top.play(LaggedStart(*(FadeIn(x_, shift=0.06 * UP) for x_ in tags), lag_ratio=0.3), at=t_di + 0.2, dur=0.7)
    top.play(FadeOut(VGroup(marks, tags)), at=t_co - 0.5, dur=0.4)
    w_dist = sans("distances", 34, C.muted).move_to(P3(-2.2, 3.3))
    strike = Line(w_dist.get_left() + P3(-0.08, 0), w_dist.get_right() + P3(0.08, 0), stroke_color=C.muted,
                  stroke_width=3)
    top.play(FadeIn(w_dist, shift=0.08 * DOWN), at=t_di + 0.1, dur=0.45)
    top.play(Create(strike), at=t_wrong, dur=0.5)
    w_conn = sans("connections", 34, C.space).move_to(P3(2.4, 3.3))
    top.play(FadeIn(w_conn, shift=0.08 * DOWN), at=t_co, dur=0.45)
    top.play(FadeOut(VGroup(w_dist, strike, w_conn)), at=out_t, dur=0.6)
