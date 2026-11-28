"""ch6_s06 · Randomness at work (sightings).

Random samples measure a shape: dots rain into a square and the ones inside THE circle light pink, so the circle
appears out of chance. On 'Monte Carlo' the key words Monte Carlo · 1940s. On 'films' a line-art scene, a ball on a
floor under a lamp, with its lighting computed by random light paths (a toy flatland path tracer, seeded): at one
sample per pixel it is pure noise; on 'random paths' rays trace from the lamp and the samples climb 1 → 512 per pixel
until the shading and the soft shadow are smooth. On 'medical trial' two groups of outcomes (treatment, control); on
'statistics' the differences that chance alone gives (4 000 reshuffles); on 'luck' the real difference lands outside
them, tagged 'not luck'.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_fx, glow_layer, P3, Canvas, Digits, backed, caps, rgb255, sans, the_circle, window

SQ_C, SQ_R = P3(0.0, -0.3), 1.75               # part A: square half side; THE circle inscribed
PB = (-6.2, -2.7, 1.2, 1.5)                    # part B: the render panel (world box)
FLOOR_Y, BALL_C, BALL_R = -2.1, np.array([-1.7, -1.13]), 0.97
LAMP = (np.array([-5.4, 1.05]), np.array([-4.1, 1.05]))
RES = 30                                       # render pixels per world unit
LEVELS = [2 ** k for k in range(10)]           # 1 … 512 samples per pixel


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def blocked(p, q):
    """Does the segment p → q (arrays (..., 2)) pass through the ball?"""
    d = q - p
    f = p - BALL_C
    a = (d * d).sum(-1)
    b = 2 * (f * d).sum(-1)
    c = (f * f).sum(-1) - BALL_R ** 2
    disc = b * b - 4 * a * c
    sq = np.sqrt(np.maximum(disc, 0))
    t1, t2 = (-b - sq) / (2 * a), (-b + sq) / (2 * a)
    return (disc > 0) & (((t1 > 1e-4) & (t1 < 1)) | ((t2 > 1e-4) & (t2 < 1)))


_IMG = {}


def renders():
    """Cumulative Monte Carlo renders at LEVELS samples per pixel, as float images in [0, 1]."""
    if _IMG:
        return _IMG
    x0, y0, x1, y1 = PB
    w, h = int((x1 - x0) * RES), int((y1 - y0) * RES)
    xs = x0 + (np.arange(w) + 0.5) / RES
    ys = y1 - (np.arange(h) + 0.5) / RES
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X, Y], -1)
    floor_px = Y < FLOOR_Y
    rel = (P - BALL_C) / BALL_R
    rr = (rel ** 2).sum(-1)
    ball_px = rr < 1
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    Q = P.copy()
    Q[..., 1] = np.where(floor_px, FLOOR_Y + 1e-3, Y)                    # floor pixels show the floor's surface
    rng = np.random.default_rng(1940)
    acc = np.zeros((h, w))
    out = {}
    for k in range(1, LEVELS[-1] + 1):
        u = rng.random((h, w))
        S = LAMP[0] + u[..., None] * (LAMP[1] - LAMP[0])                 # a random point on the lamp
        d = S - Q
        dist2 = (d * d).sum(-1)
        cos = np.clip(d[..., 1] / np.sqrt(dist2), 0, 1)
        e = 2.2 * cos / (0.6 + dist2)
        vis = ~blocked(Q, S)
        val = np.where(floor_px, e * vis, 0.32 * e * vis)               # the back wall is dimmer
        l3 = np.stack([d[..., 0], d[..., 1], np.full_like(dist2, 1.2)], -1)
        l3 /= np.linalg.norm(l3, axis=-1, keepdims=True)
        lam = np.clip(rel[..., 0] * l3[..., 0] + rel[..., 1] * l3[..., 1] + nz * l3[..., 2], 0, 1)
        val = np.where(ball_px, 0.95 * lam * (u < 0.999), val)
        acc += np.clip(val, 0, 1.5)
        if k in LEVELS:
            out[k] = np.clip(acc / k, 0, 1)
    _IMG.update(out)
    return _IMG


@scene(T.ch6_s06, T.ch6_s07)
def ch6_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_mc, t_fi, t_rp = float(T.ch6_s06_monte_carlo), float(T.ch6_s06_films), float(T.ch6_s06_random_paths)
    t_med, t_lk = float(T.ch6_s06_medical_trial), float(T.ch6_s06_luck)
    t_stat, t_avg = t_med + 2.37, t_rp + 1.44                               # 'statistics' 'averages'
    Uc = C.uncertainty
    out_t = t1 - 0.45

    # part A: random samples find the circle's area
    a_out = t_fi - 0.9
    rg = np.random.default_rng(1946)
    NA = 2600
    pts = rg.uniform(-1, 1, (NA, 2))
    inside = (pts ** 2).sum(1) <= 1
    ca = Canvas((-2.0, -2.3, 2.0, 1.7))
    sk = ca.skia
    sq = Square(side_length=2 * SQ_R, stroke_color=C.map_off, stroke_width=2.4).move_to(SQ_C)
    m.play(Create(sq), at=t0 + 0.2, dur=0.6)
    m.play(FadeOut(sq), at=a_out, dur=0.5)

    def rain(t):
        u = min(max((t - t0 - 0.6) / (t_mc - t0 - 0.2), 0.0), 1.0)
        n = int(NA * u ** 1.6)
        f = 1 - ss((t - a_out) / 0.5)
        c = ca.begin()
        if n:
            for mask, col, al in ((inside[:n], Uc, 0.9), (~inside[:n], C.muted, 0.55)):
                p = pts[:n][mask]
                q = [sk.Point(*ca.T(SQ_C[0] + SQ_R * a, SQ_C[1] + SQ_R * b)) for a, b in p]
                if q:
                    c.drawPoints(sk.Canvas.kPoints_PointMode, q, ca.paint(col, al * f, 6.0))
        return ca.array()

    s.add(FramesLayer(rain, z=1, during=[(t0 + 0.5, a_out + 0.55)], fx=glow_fx(Uc, k=0.25, radius=3), **ca.layer_kw()))
    word = backed(caps(r"Monte\ Carlo\ \textperiodcentered\ 1940s", 44, C.text), pad=0.1).move_to(P3(0, 2.9))
    top.play(FadeIn(word, shift=0.08 * DOWN), at=t_mc - 0.1, dur=0.6)
    top.play(FadeOut(word), at=t_fi - 0.6, dur=0.5)

    # part B: a ball under a lamp, lit by random light paths
    b_out = t_med - 0.7
    imgs = renders()
    col = np.array(rgb255(C.circle), float) / 255.0
    warm = np.array(rgb255(C.quantity), float) / 255.0

    def spp(t):
        if t < t_rp + 0.2:
            return 1
        u = min(max((t - t_rp - 0.2) / (t_avg + 0.6 - t_rp - 0.2), 0.0), 1.0)
        return LEVELS[int(round(u * (len(LEVELS) - 1)))]

    def render(t):
        v = imgs[spp(t)]
        lum = (v ** (1 / 2.2))[..., None]
        g = lum * ((1 - 0.3 * lum) * col + 0.3 * lum * warm)          # bright light runs warm, like the lamp
        a = np.ones(v.shape)[..., None]
        rgba = np.concatenate([g, a], -1)
        rgba = np.repeat(np.repeat(rgba, 3, 0), 3, 1)
        return (rgba * 255).astype(np.uint8)

    x0, y0, x1, y1 = PB
    on = fade(t_fi + 0.2, dur=0.6, out=b_out, out_dur=0.5)
    s.add(FramesLayer(render, z=1, opacity=on, during=[(t_fi + 0.15, b_out + 0.55)], height=y1 - y0,
                      pos=((x0 + x1) / 2, (y0 + y1) / 2)))
    frame = Rectangle(width=x1 - x0, height=y1 - y0, stroke_color=C.map_off, stroke_width=2).move_to(
        P3((x0 + x1) / 2, (y0 + y1) / 2))
    art = VGroup(Line(P3(x0, FLOOR_Y), P3(x1, FLOOR_Y), stroke_color=C.circle, stroke_width=2.4),
                 Circle(radius=BALL_R, stroke_color=C.circle, stroke_width=2.4).move_to(P3(*BALL_C)),
                 Line(P3(*LAMP[0]), P3(*LAMP[1]), stroke_color=C.quantity, stroke_width=7))
    lamp_l = glow_layer(s, z=2.5, color=C.quantity)
    top.play(Create(frame), Create(art[:2]), at=t_fi - 0.4, dur=0.8)
    lamp_l.play(Create(art[2]), at=t_fi - 0.4, dur=0.8)

    # 'random paths': rays from the lamp; they stop at the ball
    rr = np.random.default_rng(7)
    rays = VGroup()
    for _ in range(36):
        a_ = LAMP[0] + rr.random() * (LAMP[1] - LAMP[0])
        b_ = np.array([rr.uniform(x0 + 0.3, x1 - 0.2), rr.uniform(y0 + 0.65, y1 - 0.6)])
        if b_[1] < FLOOR_Y:
            b_[1] = FLOOR_Y
        d = b_ - a_
        f_ = a_ - BALL_C
        A, B, Cq = d @ d, 2 * f_ @ d, f_ @ f_ - BALL_R ** 2
        disc = B * B - 4 * A * Cq
        if disc > 0:
            tt = (-B - math.sqrt(disc)) / (2 * A)
            if 0 < tt < 1:
                b_ = a_ + tt * d
        rays.add(Line(P3(*a_), P3(*b_), stroke_color=Uc, stroke_width=1.8, stroke_opacity=0.85))
    top.play(LaggedStart(*(Create(r_) for r_ in rays), lag_ratio=0.06), at=t_rp - 0.1, dur=1.4)
    top.play(FadeOut(rays), at=t_avg + 0.3, dur=0.6)

    dg = Digits(48)
    lab = sans("samples per pixel", 28, C.muted).move_to(P3(2.1, 0.55), aligned_edge=LEFT)

    def counter(t):
        f = ss((t - t_fi - 0.2) / 0.4) * (1 - ss((t - b_out) / 0.5))
        return dg.number(str(spp(t)), 4.6, -0.35, color=Uc).set_opacity(f) if f > 0 else VGroup()

    top.play(FadeIn(lab), at=t_fi + 0.2, dur=0.4)
    top.redraw(window(counter, t_fi + 0.15, b_out + 0.55), during=(t_fi + 0.15, b_out + 0.6))
    top.play(FadeOut(VGroup(frame, art[:2], lab)), at=b_out, dur=0.5)
    lamp_l.play(FadeOut(art[2]), at=b_out, dur=0.5)

    # part C: a medical trial, and what chance alone would give
    r3 = np.random.default_rng(1946)
    ctl, trt = r3.normal(0, 1, 30), r3.normal(1.0, 1, 30)
    obs = trt.mean() - ctl.mean()
    pool = np.concatenate([ctl, trt])
    perm = []
    for _ in range(4000):
        r3.shuffle(pool)
        perm.append(pool[30:].mean() - pool[:30].mean())
    perm = np.array(perm)
    YB = -2.2

    def oy(v):
        return YB + 0.6 * (v + 2.4)

    jit = np.random.default_rng(3).uniform(-0.32, 0.32, (2, 30))
    groups = VGroup()
    for k_, (vals, cx, cl) in enumerate(((trt, -4.5, Uc), (ctl, -2.6, C.muted))):
        dots = VGroup(*(Dot(P3(cx + jit[k_, i], oy(v)), radius=0.065, color=cl) for i, v in enumerate(vals)))
        mean = Line(P3(cx - 0.5, oy(vals.mean())), P3(cx + 0.5, oy(vals.mean())), stroke_color=cl, stroke_width=4)
        groups.add(VGroup(dots, mean))
    g_lab = VGroup(sans("treatment", 28, Uc).move_to(P3(-4.5, YB - 0.85)),
                   sans("control", 28, C.muted).move_to(P3(-2.6, YB - 0.85)))
    m.play(LaggedStart(*(FadeIn(d_, scale=1.5) for d_ in [*groups[0][0], *groups[1][0]]), lag_ratio=0.01),
           FadeIn(g_lab), at=t_med - 0.1, dur=1.0)
    m.play(Create(groups[0][1]), Create(groups[1][1]), at=t_med + 1.0, dur=0.5)

    def hx(d):
        return 3.1 + 1.9 * d

    counts, edges = np.histogram(perm, bins=np.linspace(-1.2, 1.2, 33))
    hb = -1.6
    bars = VGroup(*(Rectangle(width=1.9 * (edges[1] - edges[0]) * 0.9, height=max(2.6 * c_ / counts.max(), 0.001),
                              stroke_width=0, fill_color=C.muted, fill_opacity=0.75)
                    .move_to(P3(hx((a + b) / 2), hb), aligned_edge=DOWN)
                    for c_, a, b in zip(counts, edges[:-1], edges[1:])))
    base = Line(P3(hx(-1.25), hb), P3(hx(1.25), hb), stroke_color=C.axis, stroke_width=2)
    h_lab = sans("chance alone", 28, C.muted).move_to(P3(hx(0), hb - 0.45))
    m.play(Create(base), FadeIn(h_lab), at=t_stat - 0.4, dur=0.5)
    m.play(LaggedStart(*(GrowFromEdge(b_, DOWN) for b_ in bars), lag_ratio=0.03), at=t_stat - 0.2, dur=1.0)
    mark = Line(P3(hx(obs), hb), P3(hx(obs), hb + 2.9), stroke_color=Uc, stroke_width=5)
    tag = sans("not luck", 32, Uc).move_to(P3(hx(obs), hb + 3.3))
    mark_l = glow_layer(s, z=0.5, color=Uc)
    mark_l.play(Create(mark), at=t_lk - 1.1, dur=0.5)
    mark_l.play(FadeOut(mark), at=out_t, dur=0.4)
    m.play(FadeIn(tag, shift=0.06 * DOWN), at=t_lk - 0.6, dur=0.4)

    # out
    m.play(FadeOut(VGroup(groups, g_lab, bars, base, h_lab, tag)), at=out_t, dur=0.4)
