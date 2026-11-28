"""c08_s03 · Voyager (payoff). Storyboard: plan/scene_plan.md § c08_s03. Layout L1.

Opens on c08_s02's last frame (the coded constellation, the capacity equation, band and curve); the equation holds
while the rest gives way. 'WiFi': a router and a mobile mast send their signals. 'Voyager': a starfield at three
depths drifting at three speeds; Voyager 1 far off at the upper left, a ground dish at the lower right, 24 billion km
between them. 'twenty watts': pulses leave Voyager and fade with distance on their way to the dish. 'receiver': the
picture dims and the received constellation comes up: four candidates and one faint, noisy point between them.
'most likely': each candidate gets its probability (Gaussian likelihoods, equal priors; ch8.likelihoods), and on
'evidence' the bars take the Bayes hue: the bridge to chapter 9.
"""
import math

import numpy as np
from aion import *

import ch8
from beats import T
from kit import chapter_backdrop, glimpse, P3, add_rail, glow, mix, polyline, sans, smooth01, tex, tint


def _carry(s, out):
    """c08_s02's last frame, minus the equation (which this scene keeps on screen a little longer)."""
    t_end = float(s.start) - 0.01
    op = fade(t_end - 5, dur=0.1, out=out, out_dur=0.6)
    yaw = -0.10 + 0.2 * (t_end - float(T.c08_s02)) / 25.0
    pts, unit, sent = ch8.samples(16)
    P = ch8.constellation(16)
    R = P[sent] + ch8.SIGMA * 0.55 * unit
    s.add(PointsLayer(lambda t: ch8.plane(R, yaw), color=C.noise, size=2.2, glow=0.0, alpha=op * 0.55,
                      additive=False, z=2, parallax=0.0))
    m = s.manim(z=3, parallax=0.0, opacity=op)
    L = 1.4
    for a_ in (ch8.plane(np.array([[-L, 0], [L, 0]]), yaw), ch8.plane(np.array([[0, -L], [0, L]]), yaw)):
        m.add(Line(P3(*a_[0]), P3(*a_[1]), stroke_color=tint(C.muted, 0.45), stroke_width=1.2))
    m.add(*[Dot(P3(*q), radius=0.06, color=C.light) for q in ch8.plane(P, yaw)],
          sans("16 levels", 26, C.text).move_to(P3(ch8.CC[0], 2.35)),
          sans("noise", 24, C.noise).move_to(P3(0.1, 0.55), aligned_edge=LEFT),
          sans("coding", 24, C.text).move_to(P3(0.1, 0.0), aligned_edge=LEFT))
    ax, spec, br = ch8.band()
    dot, guide, lab = ch8.marker()
    m.add(ax, spec, br, ch8.graph_axes(), guide, dot, lab)
    glow(s, C.shannon, z=5, k=0.6, parallax=0.0, opacity=op).add(polyline(ch8.curve_pts(1.0), C.shannon, 3.0))


@scene(T.c08_s03, T.c09_s01)
def s27_c08_voyager(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 8, last=True)
    t0 = float(s.start)
    t_wf, t_vo, t_tw, t_re, t_ml, t_ev = (T.c08_s03_wifi, T.c08_s03_voyager, T.c08_s03_twenty_watts,
                                          T.c08_s03_receiver, T.c08_s03_most_likely, T.c08_s03_evidence)
    # the spacecraft itself (NASA/JPL, public domain), top right, clear of the far-off Voyager and the dish
    glimpse(s, "photo:voyager.jpg", t_vo + 0.2, C.shannon, dur=min(4.2, float(t_tw) - float(t_vo) - 0.4), h=2.1,
            at_xy=(4.95, 2.2))
    _carry(s, t0 + 0.2)
    add_rail(s, 8)
    hud = s.manim(z=50, parallax=0.0)
    e = ch8.capacity_eqn()
    eo = fade(t0 - 5, dur=0.1, out=t_vo - 0.4, out_dur=0.6)
    s.manim(z=50, parallax=0.0, opacity=eo).add(e, *ch8.eqn_tags(e))

    # every WiFi and mobile network
    w_op = fade(t_wf - 0.2, dur=0.5, out=t_vo - 0.4, out_dur=0.6)
    r, tw = ch8.router().set_stroke(color=C.light).set_fill(C.light), ch8.tower().set_stroke(color=C.light)
    r.move_to(P3(-3.6, -0.9))
    tw.move_to(P3(-0.3, -0.55))
    wm = s.manim(z=4, parallax=0.0, opacity=w_op)
    wm.add(r, tw, sans("WiFi", 24, C.muted).next_to(r, DOWN, buff=0.3),
           sans("mobile", 24, C.muted).next_to(tw, DOWN, buff=0.3))

    def radio(t):
        a = float(w_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        for c, base in ((P3(-3.6, -0.15), 0.0), (P3(-0.3, 0.55), 0.35)):
            for k in range(3):
                ph = ((t - float(t_wf) - base) * 0.9 - k / 3) % 1.0
                rad = 0.25 + 0.9 * ph
                g.add(Arc(radius=rad, start_angle=math.pi / 2 - 0.7, angle=1.4, stroke_color=C.shannon,
                          stroke_width=2.4, stroke_opacity=a * (1 - ph)).move_arc_center_to(c))
        return g
    glow(s, C.shannon, z=5, k=0.6, parallax=0.0).redraw(radio, during=(t_wf - 0.3, t_vo + 0.3))

    # Voyager, 24 billion km away
    xy, layer = ch8.stars()
    st_op = fade(t_vo - 0.4, dur=1.0)
    dim = lambda t: 1.0 - 0.6 * float(smooth01((t - float(t_re) + 0.2) / 0.9))
    for k, (size, al, v) in enumerate(((1.4, 0.45, 0.05), (2.0, 0.7, 0.13), (2.8, 0.95, 0.26))):
        sel = xy[layer == k]

        def stars(t, sel=sel, v=v):
            q = sel.copy()
            q[:, 0] = (q[:, 0] - v * (t - float(t_vo)) + 9.5) % 19.0 - 9.5        # parallax: near layers drift faster
            return q
        s.add(PointsLayer(stars, color=C.light, size=size, glow=0.0,
                          alpha=Track(lambda t, al=al: al * float(st_op(t)) * dim(t)), additive=False,
                          z=-50 + k, parallax=0.0))
    v_op = fade(t_vo - 0.1, dur=0.8, out=t_re + 0.1, out_dur=0.8)
    vg = ch8.voyager(0.7).move_to(P3(*ch8.VOY))
    s.manim(z=6, parallax=0.0, opacity=v_op).add(vg, sans("Voyager 1", 22, C.muted).next_to(vg, DOWN, buff=0.18))
    dsh = ch8.dish(0.9).move_to(P3(*ch8.DISH))
    d_op = fade(t_vo + 0.6, dur=0.8)
    s.manim(z=6, parallax=0.0, opacity=d_op).add(dsh, sans("Earth", 22, C.muted).next_to(dsh, DOWN, buff=0.18))
    A, B = ch8.VOY + np.array([0.75, -0.35]), ch8.DISH + np.array([-0.75, 0.55])
    path = DashedLine(P3(*A), P3(*B), dash_length=0.1, stroke_color=tint(C.muted, 0.6), stroke_width=1.2)
    mid = (A + B) / 2
    dist = sans("24 billion km", 24, C.text).move_to(P3(*(mid + np.array([0.35, 0.45]))))
    pm = s.manim(z=5, parallax=0.0, opacity=fade(t_vo + 1.0, dur=0.6, out=t_re + 0.1, out_dur=0.8))
    pm.play(Create(path), at=t_vo + 1.0, dur=1.0)
    pm.play(FadeIn(dist, shift=0.05 * UP), at=t_vo + 1.6, dur=0.6)
    watts = sans("20 W", 24, C.shannon).next_to(vg, RIGHT, buff=0.35)
    pm.play(FadeIn(watts), at=t_tw + 0.2, dur=0.5)

    # pulses: a short wave packet that weakens with distance (amplitude ∝ 1/distance, from 1 at the first unit)
    u = (B - A) / np.linalg.norm(B - A)
    nrm = np.array([-u[1], u[0]])
    Ltot = float(np.linalg.norm(B - A))
    TRAVEL = 2.4

    def pulses(t):
        g = VGroup()
        a = float(fade(t_tw - 0.1, dur=0.3, out=t_re + 0.4, out_dur=0.6)(t))
        if a < 0.01:
            return g
        for k in range(4):
            te = float(t_tw) + 1.0 * k
            f = (t - te) / TRAVEL
            if not 0 <= f <= 1:
                continue
            c = f * Ltot
            amp = 0.32 / (1 + 4.0 * f)
            ss = np.linspace(-0.55, 0.55, 80)
            env = np.exp(-(ss / 0.3) ** 2)
            pts = [tuple(A + u * (c + x) + nrm * amp * e_ * math.sin(x * 26)) for x, e_ in zip(ss, env)
                   if 0 <= c + x <= Ltot]
            if len(pts) > 2:
                g.add(polyline(pts, C.shannon, 2.6, a * (1 - 0.6 * f)))
        return g
    glow(s, C.shannon, z=7, k=0.6, parallax=0.0).redraw(pulses, during=(t_tw - 0.2, t_re + 1.2))

    # the receiver: four candidates, one faint and noisy point between them
    pts, prob = ch8.likelihoods()
    r_op = fade(t_re + 0.1, dur=0.8)
    cm = s.manim(z=8, parallax=0.0, opacity=r_op)
    L = 1.55
    cm.add(Line(P3(*ch8.rc((-L, 0))), P3(*ch8.rc((L, 0))), stroke_color=tint(C.muted, 0.45), stroke_width=1.2),
           Line(P3(*ch8.rc((0, -L))), P3(*ch8.rc((0, L))), stroke_color=tint(C.muted, 0.45), stroke_width=1.2),
           *[Circle(radius=0.13, stroke_color=C.light, stroke_width=2.4).move_to(P3(*ch8.rc(p))) for p in pts])
    rng = np.random.default_rng(1977)
    cloud = rng.normal(0, 1, (240, 2))

    def fuzz(t):
        k = int(t * 12)                                              # the faint signal shimmers, 12 times a second
        jit = np.random.default_rng(k).normal(0, 0.05, (len(cloud), 2))
        return ch8.rc(ch8.RX) + 0.16 * cloud + jit
    s.add(PointsLayer(fuzz, color=C.noise, size=2.2, glow=0.0, alpha=r_op * 0.7, additive=False, z=8.5,
                      parallax=0.0))
    glow(s, C.light, z=9, k=0.7, parallax=0.0, opacity=r_op).add(Dot(P3(*ch8.rc(ch8.RX)), radius=0.07,
                                                                     color=C.light))
    hud.play(FadeIn(sans("received", 22, C.noise).next_to(P3(*ch8.rc(ch8.RX)), DOWN + RIGHT, buff=0.25)),
             at=t_re + 0.6, dur=0.5)

    # most likely: a probability for each candidate; on 'evidence' they turn the Bayes hue
    HMAX = 1.5
    t_b = float(t_ml) + 0.1

    def bars(t):
        g = VGroup()
        grow = float(smooth01((t - t_b) / 0.9))
        if grow <= 0:
            return g
        hue = float(smooth01((t - float(t_ev) + 0.1) / 0.6))
        col = mix(C.light, C.bayes, hue)
        for (p, pr) in zip(pts, prob):
            base = ch8.rc(p) + np.array([0.36, -0.2])
            h = max(HMAX * pr * grow, 0.012)
            g.add(Rectangle(width=0.2, height=h, stroke_width=0, fill_color=col, fill_opacity=1)
                  .move_to(P3(base[0], base[1] + h / 2)))
            g.add(sans(f"{pr * 100:.0f}%", 22, col).set_opacity(grow)
                  .next_to(P3(base[0], base[1] + h), UP, buff=0.08))
        return g
    s.manim(z=10, parallax=0.0).redraw(bars, during=(t_b - 0.2, s.end))
    win = int(np.argmax(prob))
    ml = sans("most likely", 22, C.muted).next_to(
        P3(*(ch8.rc(pts[win]) + np.array([0.36, -0.2 + 0.5 * HMAX * prob[win]]))), RIGHT, buff=0.3)
    hud.play(FadeIn(ml, shift=0.05 * LEFT), at=t_ml + 0.9, dur=0.5)
    hud.play(ml.animate.set_color(C.bayes), at=t_ev, dur=0.6)
