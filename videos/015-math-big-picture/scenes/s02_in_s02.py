"""in_s02 · Pieces without the map.

Six pieces of school maths appear around THE circle, each a small live diagram in its branch's hue, sitting roughly
where its map node will be:
  foundations: two sets fill with elements, the overlap shaded;  quantity: a sieve strikes out multiples, primes stay;
  structure: a parabola and its two roots under the quadratic formula;  space: a triangle whose top vertex slides
  while its three angles keep summing to 180°;  change: a tangent slides along x², slope 2x;  uncertainty: a histogram
  of coin-flip totals grows into a bell curve.
They drift apart; a thin line reaches from one piece to another and gives up. On 'city' they freeze and shrink into
streets among city blocks seen from above; on 'map' the blocks fade, the camera pulls back and the streets fold into
the dim Map of Math. The derivative comes back and settles on its own corner of the map.
"""
import math

import numpy as np
from aion import *
from scipy.optimize import linear_sum_assignment

from beats import T
from kit import map_deco, HUB_R, P3, PILLARS, hue, map_lines, node_xy, sans, tex, the_circle, tint, window

STREETS = [((-4.8, -2.3), (-2.9, -2.3)), ((-1.2, -2.3), (0.9, -2.3)), ((2.4, -2.3), (4.6, -2.3)),
           ((-4.8, 2.3), (-2.6, 2.3)), ((-0.9, 2.3), (1.3, 2.3)), ((2.8, 2.3), (4.8, 2.3)),
           ((-3.8, -1.6), (-3.8, 0.2)), ((-2.2, 0.6), (-2.2, 2.0)), ((3.8, -1.8), (3.8, -0.1)),
           ((2.2, 0.3), (2.2, 1.9)), ((-5.4, -0.6), (-5.4, 1.2)), ((5.4, -1.0), (5.4, 0.8)),
           ((-2.0, -1.9), (-2.0, -0.6)), ((1.9, -1.9), (1.9, -0.8)), ((-0.6, -3.0), (0.6, -3.0))]
ROT = [0.10, -0.08, 0.07, -0.06, 0.09, -0.10]


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- the six live fragments, drawn at the origin
rg = np.random.default_rng(1502)
VENN_PTS = []                                                 # (point, which region) for the set elements
while len(VENN_PTS) < 16:
    p = rg.uniform([-0.95, -0.5], [0.95, 0.5])
    ina, inb = np.hypot(p[0] + 0.28, p[1]) < 0.47, np.hypot(p[0] - 0.28, p[1]) < 0.47
    if ina or inb:
        VENN_PTS.append(p)
SIEVE = list(range(2, 32))                                   # 2..31 in a 6 × 5 grid
SIEVE_TEX = {n: tex(str(n), 20, C.text) for n in SIEVE}
COIN_TOTALS = rg.binomial(12, 0.5, 400)                      # 400 rounds of 12 coin flips: heads counted


def venn(u):
    c = hue("foundations")
    a = Circle(radius=0.47, stroke_color=c, stroke_width=2.6).shift(LEFT * 0.28)
    b = Circle(radius=0.47, stroke_color=c, stroke_width=2.6).shift(RIGHT * 0.28)
    lens = Intersection(a, b, fill_color=tint(c, 0.28), fill_opacity=1, stroke_width=0)
    g = VGroup(lens, a, b, tex("A", 24, c).move_to(P3(-0.62, 0.55)), tex("B", 24, c).move_to(P3(0.62, 0.55)))
    for j, p in enumerate(VENN_PTS):
        k = ss((u - 0.3 - 0.18 * j) / 0.25)
        if k > 0:
            g.add(Dot(P3(*p), radius=0.035 * k, color=C.text))
    return g


def sieve(u):
    c = hue("quantity")
    g = VGroup()
    struck = {n for pr, t0 in ((2, 0.6), (3, 2.2), (5, 3.8)) if u > t0 for n in SIEVE if n > pr and n % pr == 0}
    for i, n in enumerate(SIEVE):
        x, y = -0.75 + 0.3 * (i % 6), 0.6 - 0.3 * (i // 6)
        prime = all(n % d for d in range(2, int(n ** 0.5) + 1))
        lit = prime and u > 5.0
        box = Square(0.27, stroke_color=c if lit else C.map_off, stroke_width=1.6 if lit else 1.0,
                     fill_color=tint(c, 0.25), fill_opacity=1.0 if lit else 0.0).move_to(P3(x, y))
        num = SIEVE_TEX[n].copy().move_to(P3(x, y))
        if n in struck:
            num.set_color(C.map_off)
            g.add(box, num, Line(P3(x - 0.1, y - 0.1), P3(x + 0.1, y + 0.1), stroke_color=C.muted, stroke_width=1.2))
        else:
            if lit:
                num.set_color(c)
            g.add(box, num)
    return g


def parabola(u):
    c = hue("structure")
    ax = VGroup(Line(P3(-0.95, 0), P3(0.95, 0), stroke_color=C.muted, stroke_width=1.2),
                Line(P3(0, -0.55), P3(0, 0.55), stroke_color=C.muted, stroke_width=1.2))
    f = lambda x: 0.55 * (x * x - 0.36) - 0.05                      # roots at ±0.6 shifted down a hair
    k = ss(u / 1.4)
    xs = np.linspace(-0.92, -0.92 + 1.84 * max(k, 0.01), 50)
    curve = VMobject(stroke_color=c, stroke_width=2.8).set_points_smoothly([P3(x, f(x)) for x in xs])
    g = VGroup(ax, curve)
    r0 = math.sqrt(0.36 + 0.05 / 0.55)
    for j, x in enumerate((-r0, r0)):
        kk = ss((u - 1.6 - 0.3 * j) / 0.35)
        if kk > 0:
            g.add(Dot(P3(x, 0), radius=0.06 * kk, color=c))
    g.add(tex(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", 26, c).move_to(P3(0, -0.92)))
    return g


def triangle(u):
    c = hue("space")
    A, B = P3(-0.8, -0.45), P3(0.8, -0.45)
    Cc = P3(0.55 * math.sin(0.9 * u), 0.5 + 0.08 * math.cos(0.6 * u))          # the top vertex wanders
    g = VGroup(Polygon(A, B, Cc, stroke_color=c, stroke_width=2.8))
    for v, w1, w2, r in ((A, B, Cc, 0.24), (B, Cc, A, 0.24), (Cc, A, B, 0.2)):
        g.add(Angle(Line(v, w1), Line(v, w2), radius=r, stroke_color=c, stroke_width=2))
    g.add(tex(r"\alpha + \beta + \gamma = 180^\circ", 26, c).move_to(P3(0, -0.85)))
    return g


def tangent(u):
    c = hue("change")
    f = lambda x: 0.55 * x * x - 0.4
    xs = np.linspace(-1.0, 1.0, 50)
    g = VGroup(VMobject(stroke_color=C.muted, stroke_width=2.2).set_points_smoothly([P3(x, f(x)) for x in xs]))
    x0 = 0.8 * math.sin(0.75 * u)
    sl = 1.1 * x0
    g.add(Line(P3(x0 - 0.5, f(x0) - 0.5 * sl), P3(x0 + 0.5, f(x0) + 0.5 * sl), stroke_color=c, stroke_width=2.8))
    g.add(Dot(P3(x0, f(x0)), radius=0.055, color=c))
    g.add(tex(r"\frac{d}{dx}\,x^2 = 2x", 28, c).move_to(P3(0, -0.92)))
    return g


def histogram(u):
    c = hue("uncertainty")
    n = int(min(len(COIN_TOTALS), max(0, 400 * ss(u / 5.0))))
    counts = np.bincount(COIN_TOTALS[:n], minlength=13)
    g = VGroup(Line(P3(-1.0, -0.5), P3(1.0, -0.5), stroke_color=C.muted, stroke_width=1.2))
    for i, h in enumerate(counts):
        hh = 1.05 * h / (400 * 0.2256)                            # scaled to the expected peak, C(12,6)/2^12
        if hh > 0.004:
            x = -0.9 + 0.15 * i
            g.add(Rectangle(width=0.12, height=hh, stroke_color=c, stroke_width=1.0, fill_color=tint(c, 0.3),
                            fill_opacity=1).move_to(P3(x, -0.5 + hh / 2)))
    k = ss((u - 4.6) / 0.9)
    if k > 0:                                                   # the normal curve with the same mean and spread
        xs = np.linspace(-1.0, 1.0, 60)
        sd = math.sqrt(3.0) * 0.15
        pts = [P3(x, -0.5 + 1.05 * math.exp(-x * x / (2 * sd * sd))) for x in xs]
        g.add(VMobject(stroke_color=c, stroke_width=2.4, stroke_opacity=k).set_points_smoothly(pts))
    return g


DRAW = {"foundations": venn, "quantity": sieve, "structure": parabola, "space": triangle, "change": tangent,
        "uncertainty": histogram}


@scene(T.in_s02, T.in_s03)
def in_s02(s):
    s.solid(C.bg, z=-200)
    city_l = s.manim(z=-2)                                   # blocks and streets
    mp = s.manim(z=-1)                                       # fragments → streets → map
    m = s.manim(z=0)                                         # THE circle (solid black inside)
    top = s.manim(z=1)
    m.add(the_circle(fill_color=C.bg, fill_opacity=1.0))

    t_one, t_sense, t_fit = float(T.in_s02_one_piece), float(T.in_s02_makes_sense), float(T.in_s02_fit_together)
    t_city, t_map, t_stray = float(T.in_s02_city), float(T.in_s02_map), float(T.in_s02_stray_fact)
    base = [P3(node_xy(k)[0] * 1.5, node_xy(k)[1] * 1.05) for k in range(6)]
    born = [t_one + 0.62 * k for k in range(6)]

    def place(k, t):
        d = ss((t - t_sense + 0.15) / 1.6)
        return P3(base[k][0] * (1 + 0.2 * d), base[k][1] * (1 + 0.06 * d)), ROT[k] * d

    def frag(k, t):
        u = t - born[k]
        g = DRAW[PILLARS[k]](max(u, 0.0))
        pos, rot = place(k, t)
        a = ss(u / 0.45)
        g.scale(1.2 * (0.7 + 0.3 * a)).rotate(rot).shift(pos)
        if a < 1:
            for sm in g.family_members_with_points():
                sm.set_stroke(opacity=sm.get_stroke_opacity() * a, family=False)
                sm.set_fill(opacity=sm.get_fill_opacity() * a, family=False)
        return g

    freeze = t_city - 0.1
    for k in range(6):
        mp.redraw(window(lambda t, k=k: frag(k, t), born[k] - 0.05, freeze), during=(born[k] - 0.05, freeze + 0.05))
    frozen = [frag(k, freeze) for k in range(6)]
    for f in frozen:
        mp.add(f, at=freeze)

    # a thin line reaches from one piece toward another, and gives up
    pa, _ = place(2, t_fit)
    pb, _ = place(3, t_fit)
    a, b = pa + 0.95 * (pb - pa) / np.linalg.norm(pb - pa), pb
    reach = DashedLine(a, a + 0.55 * (b - a), stroke_color=C.muted, stroke_width=2, dash_length=0.08)
    mp.play(Create(reach), at=t_fit, dur=0.55, ease="out_cubic")
    mp.play(Uncreate(reach), at=t_fit + 0.8, dur=0.45)

    # the city from above: blocks of building lots between the streets
    rgc = np.random.default_rng(1503)
    segs = [(np.array(u_), np.array(v_)) for u_, v_ in STREETS]

    def seg_d(p, u_, v_):
        w = v_ - u_
        h = np.clip(np.dot(p - u_, w) / np.dot(w, w), 0, 1)
        return np.linalg.norm(p - (u_ + h * w))

    blocks = VGroup()
    for x in np.arange(-5.85, 5.9, 0.78):
        for y in np.arange(-3.3, 3.35, 0.78):
            p = np.array([x, y])
            if np.hypot(x, y) < HUB_R + 0.35 or min(seg_d(p, *sg) for sg in segs) < 0.42:
                continue
            w_, h_ = rgc.uniform(0.38, 0.58, 2)
            lot = VGroup(Rectangle(width=w_, height=h_, stroke_color=C.map_off, stroke_width=1.0,
                                   fill_color=tint(C.map_off, 0.18), fill_opacity=1))
            if rgc.random() < 0.6:                                # a second building on the lot
                lot.add(Rectangle(width=w_ * 0.45, height=h_ * 0.5, stroke_color=C.map_off, stroke_width=0.8,
                                  fill_color=tint(C.map_off, 0.32), fill_opacity=1).shift(
                    P3(rgc.choice([-1, 1]) * w_ * 0.2, rgc.choice([-1, 1]) * h_ * 0.2)))
            blocks.add(lot.move_to(P3(x + rgc.normal(0, 0.03), y + rgc.normal(0, 0.03))))
    order = np.argsort([np.hypot(*b_.get_center()[:2]) for b_ in blocks])
    blocks = VGroup(*(blocks[i] for i in order))

    streets = [Line(P3(*u_), P3(*v_), stroke_color=C.map_off, stroke_width=2.6) for u_, v_ in STREETS]
    mids = np.array([[(u_[0] + v_[0]) / 2, (u_[1] + v_[1]) / 2] for u_, v_ in STREETS])
    cost = np.array([[np.linalg.norm(f.get_center()[:2] - mm) for mm in mids] for f in frozen])
    rows, cols = linear_sum_assignment(cost)
    own = dict(zip(rows, cols))
    s.camera.push(t_city, zoom=1.12, dur=2.0, ease="easy_ease")
    mp.play(*(Transform(frozen[r], streets[own[r]]) for r in range(6)), at=t_city, dur=1.3, ease="easy_ease")
    rest = [streets[j] for j in range(15) if j not in own.values()]
    mp.play(LaggedStart(*(Create(st) for st in rest), lag_ratio=0.12), at=t_city + 0.5, dur=1.4)
    city_l.play(LaggedStart(*(FadeIn(b_, scale=0.6) for b_ in blocks), lag_ratio=0.02), at=t_city + 0.2, dur=1.8)
    city = [frozen[r] for r in range(6)] + rest
    city_mid = np.array([c.get_center()[:2] for c in [streets[own[r]] for r in range(6)] + rest])

    # pull back: the streets were the map all along (ring arcs and chords, dim); the blocks fall away
    links = map_lines(color=C.map_off, width=1.8, opacity=0.75)
    lmid = np.array([ln.point_from_proportion(0.5)[:2] for ln in links])
    _, to = linear_sum_assignment(np.linalg.norm(city_mid[:, None] - lmid[None], axis=2))
    s.camera.push(t_map, zoom=1.0, dur=2.0, ease="easy_ease")
    city_l.play(LaggedStart(*(FadeOut(b_, scale=0.5) for b_ in blocks[::-1]), lag_ratio=0.015), at=t_map - 0.3,
                dur=1.5)
    mp.play(*(Transform(c, links[j]) for c, j in zip(city, to)), at=t_map, dur=2.0, ease="easy_ease")
    mp.play(FadeIn(map_deco()), at=t_map + 0.8, dur=1.6)

    # a new idea stops being a stray fact: the derivative returns and settles on its corner of the map
    d = tangent(1.2).scale(0.8)
    spot = node_xy(PILLARS.index("change"))
    d.move_to(P3(5.0, 2.4))
    top.play(FadeIn(d, shift=0.15 * LEFT), at=t_stray, dur=0.5)
    top.play(d.animate.scale(0.75).move_to(spot + P3(1.05, 0.55)), at=t_stray + 0.8, dur=1.2, ease="easy_ease")
    dot = Dot(spot, radius=0.085, color=C.change)
    top.play(GrowFromCenter(dot), at=t_stray + 1.7, dur=0.35, ease="out_back")
    here = sans("you are here", 24, C.change).next_to(dot, RIGHT, buff=0.2).shift(DOWN * 0.22)
    top.play(FadeIn(here, shift=0.05 * UP), at=t_stray + 2.0, dur=0.4)
    top.play(FadeOut(d), FadeOut(dot), FadeOut(here), at=s.end - 0.6, dur=0.5)
