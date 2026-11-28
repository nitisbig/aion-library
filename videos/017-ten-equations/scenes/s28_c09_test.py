"""c09_s01 · The test (hook). Storyboard: plan/scene_plan.md § c09_s01. Layout L1.

Opens on c08_s03's last frame (Voyager's candidates and their probability bars), which gives way to the chapter
card and a grid of 1,000 people (sims.bayes_people, seeded). 'one person in a hundred': ten turn ill. 'nine in ten':
nine of them get a positive ring; 'flags': so do 89 of the healthy. 'positive': you, with a positive ring: ill?
'thousand': the grid resets. 'Ten of them': the ill gather on the left, and nine get their rings; 'eighty nine':
the healthy re-form on the right and 89 get theirs. 'among': the 98 positives gather in one block, 9 of them ill:
9 / (9 + 89) ≈ 9 %, about one in eleven.
"""
import numpy as np
from aion import *

import ch8
import ch9
from beats import T
from kit import P3, RC, add_rail, chapter_card, glow, sans, smooth01, tag_under, tex, tint


def _carry(s, out):
    """c08_s03's last frame: dimmed stars, the dish, the four candidates with their (Bayes-hued) bars."""
    t_end = float(s.start) - 0.01
    op = fade(t_end - 5, dur=0.1, out=out, out_dur=0.7)
    xy, layer = ch8.stars()
    for k, (size, al, v) in enumerate(((1.4, 0.45, 0.05), (2.0, 0.7, 0.13), (2.8, 0.95, 0.26))):
        q = xy[layer == k].copy()
        q[:, 0] = (q[:, 0] - v * (t_end - float(T.c08_s03_voyager)) + 9.5) % 19.0 - 9.5
        s.add(PointsLayer(lambda t, q=q: q, color=C.light, size=size, glow=0.0, alpha=op * (al * 0.4),
                          additive=False, z=-50 + k, parallax=0.0))
    pts, prob = ch8.likelihoods()
    m = s.manim(z=8, parallax=0.0, opacity=op)
    L = 1.55
    dsh = ch8.dish(0.9).move_to(P3(*ch8.DISH))
    m.add(dsh, sans("Earth", 22, C.muted).next_to(dsh, DOWN, buff=0.18),
          Line(P3(*ch8.rc((-L, 0))), P3(*ch8.rc((L, 0))), stroke_color=tint(C.muted, 0.45), stroke_width=1.2),
          Line(P3(*ch8.rc((0, -L))), P3(*ch8.rc((0, L))), stroke_color=tint(C.muted, 0.45), stroke_width=1.2),
          *[Circle(radius=0.13, stroke_color=C.light, stroke_width=2.4).move_to(P3(*ch8.rc(p))) for p in pts],
          sans("received", 22, C.noise).next_to(P3(*ch8.rc(ch8.RX)), DOWN + RIGHT, buff=0.25))
    for p, pr in zip(pts, prob):
        base = ch8.rc(p) + np.array([0.36, -0.2])
        h = max(1.5 * pr, 0.012)
        m.add(Rectangle(width=0.2, height=h, stroke_width=0, fill_color=C.bayes, fill_opacity=1)
              .move_to(P3(base[0], base[1] + h / 2)),
              sans(f"{pr * 100:.0f}%", 22, C.bayes).next_to(P3(base[0], base[1] + h), UP, buff=0.08))
    win = int(np.argmax(prob))
    m.add(sans("most likely", 22, C.bayes).next_to(
        P3(*(ch8.rc(pts[win]) + np.array([0.36, -0.2 + 0.75 * prob[win]]))), RIGHT, buff=0.3))
    rng = np.random.default_rng(1977)
    cloud = ch8.rc(ch8.RX) + 0.16 * rng.normal(0, 1, (240, 2))
    s.add(PointsLayer(lambda t: cloud, color=C.noise, size=2.2, glow=0.0, alpha=op * 0.7, additive=False, z=8.5,
                      parallax=0.0))
    glow(s, C.light, z=9, k=0.7, parallax=0.0, opacity=op).add(Dot(P3(*ch8.rc(ch8.RX)), radius=0.07, color=C.light))


def ring(xy, a, r=0.08):
    return Circle(radius=r, stroke_color=C.positive, stroke_width=2.2, stroke_opacity=a).move_to(P3(*xy))


@scene(T.c09_s01, T.c09_s02)
def s28_c09_test(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_oh, t_nt, t_po, t_th, t_te, t_en, t_oe = (T.c09_s01_one_person_in_a_hund, T.c09_s01_nine_in_ten,
                                                T.c09_s01_positive, T.c09_s01_thousand, T.c09_s01_ten_of_them,
                                                T.c09_s01_eighty_nine, T.c09_s01_one_in_eleven)
    t_fl, t_nine, t_among = float(T.c09_s01_flags), float(T.c09_s01_nine_of_those), float(T.c09_s01_among)
    _carry(s, t0 + 0.25)
    chapter_card(s, 9, at=t0 + 0.55, out=t_oh - 0.5)
    add_rail(s, 9, opacity=fade(t0 + 0.4, dur=0.8))

    ill, pos = ch9.people()
    G, S = ch9.grid_xy(), ch9.split_xy()
    F = ch9.positives_xy(S)

    def where(t):
        p = ch9.ease_between(G, S, t, float(t_te) + 0.1, 1.2, stagger=0.6, seed=1)
        return ch9.ease_between(p, F, t, t_among, 1.3, stagger=0.5, seed=2)

    g_op = fade(t_oh - 0.35, dur=0.7)                                   # after the chapter card has gone
    you_on = fade(t_po - 0.3, dur=0.5, out=t_th - 0.3, out_dur=0.5)
    dim = lambda t: 1.0 - 0.7 * float(you_on(t))
    rest = lambda t: 1.0 - float(smooth01((t - t_among - 0.2) / 1.0))   # non-positives fade at the end
    hide = lambda q, keep: np.where(keep[:, None], q, 99.0)
    s.add(PointsLayer(lambda t: hide(where(t), ~pos), color=C.muted, size=ch9.DOT, glow=0.0,
                      alpha=Track(lambda t: float(g_op(t)) * dim(t) * rest(t)), additive=False, z=2, parallax=0.0))
    s.add(PointsLayer(lambda t: hide(where(t), pos), color=C.muted, size=ch9.DOT, glow=0.0,
                      alpha=Track(lambda t: float(g_op(t)) * dim(t)), additive=False, z=2.1, parallax=0.0))
    ill_a = lambda t: float(fade(t_oh - 0.1, dur=0.5, out=t_th - 0.3, out_dur=0.5)(t)) \
        + float(fade(t_te + 0.1, dur=0.5)(t))
    s.add(PointsLayer(lambda t: hide(where(t), ill & pos), color=C.ill, size=ch9.DOT, glow=0.0,
                      alpha=Track(lambda t: min(ill_a(t), 1.0) * dim(t)), additive=False, z=2.2, parallax=0.0))
    s.add(PointsLayer(lambda t: hide(where(t), ill & ~pos), color=C.ill, size=ch9.DOT, glow=0.0,
                      alpha=Track(lambda t: min(ill_a(t), 1.0) * dim(t) * rest(t)), additive=False, z=2.2,
                      parallax=0.0))

    # positive rings, popping in one by one (seeded order)
    ip, hp = np.where(ill & pos)[0], np.where(~ill & pos)[0]
    order = np.random.default_rng(9).permutation(len(hp))

    def rings(t):
        q = where(t)
        g = VGroup()
        d = dim(t)
        for k, i in enumerate(ip):
            a = (float(fade(t_nt + 0.3 + 0.08 * k, dur=0.25, out=t_th - 0.3, out_dur=0.5)(t))
                 + float(fade(t_nine + 0.08 * k, dur=0.25)(t)))
            if a > 0.01:
                g.add(ring(q[i], min(a, 1.0) * d))
        for k, i in enumerate(hp[order]):
            a = (float(fade(t_fl + 0.4 + 0.012 * k, dur=0.2, out=t_th - 0.3, out_dur=0.5)(t))
                 + float(fade(t_en - 0.1 + 0.012 * k, dur=0.2)(t)))
            if a > 0.01:
                g.add(ring(q[i], min(a, 1.0) * d))
        return g
    s.manim(z=3, parallax=0.0).redraw(rings, during=(t_nt, s.end))

    # the legend, on the right
    LX = 4.35
    lg = s.manim(z=50, parallax=0.0, opacity=fade(t0, dur=0.1, out=t_te - 0.2, out_dur=0.5))
    r1 = VGroup(Dot(radius=0.07, color=C.ill), sans("ill", 26, C.ill), sans("1 in 100", 22, C.muted)) \
        .arrange(RIGHT, buff=0.2).move_to(P3(LX, 1.75), aligned_edge=LEFT)
    r2 = VGroup(Circle(radius=0.09, stroke_color=C.positive, stroke_width=2.4), sans("positive", 26, C.positive)) \
        .arrange(RIGHT, buff=0.2).move_to(P3(LX, 1.1), aligned_edge=LEFT)
    r3 = sans("9 in 10 ill", 22, C.muted).move_to(P3(LX + 0.38, 0.62), aligned_edge=LEFT)
    r4 = sans("9 in 100 healthy", 22, C.muted).move_to(P3(LX + 0.38, 0.22), aligned_edge=LEFT)
    lg.play(FadeIn(r1, shift=0.05 * LEFT), at=t_oh, dur=0.5)
    lg.play(FadeIn(r2, shift=0.05 * LEFT), at=t_nt, dur=0.5)
    lg.play(FadeIn(r3), at=t_nt + 0.4, dur=0.5)
    lg.play(FadeIn(r4), at=t_fl + 0.3, dur=0.5)

    # you
    yo = s.manim(z=50, parallax=0.0, opacity=you_on)
    yc = P3(4.95, -1.15)
    yo.add(Dot(yc, radius=0.12, color=C.muted), Circle(radius=0.22, stroke_color=C.positive, stroke_width=3).move_to(yc),
           sans("you", 26, C.text).next_to(yc, DOWN, buff=0.32), sans("ill?", 26, C.muted).next_to(yc, RIGHT, buff=0.4))

    # the split: ill on the left, healthy on the right
    sp = s.manim(z=50, parallax=0.0, opacity=fade(t0, dur=0.1, out=t_among - 0.1, out_dur=0.5))
    ilab = VGroup(sans("ill", 26, C.ill), sans("10", 24, C.muted)).arrange(DOWN, buff=0.08) \
        .move_to(P3(ch9.ILL_C[0], ch9.ILL_C[1] + 1.25))
    hlab = VGroup(sans("healthy", 26, C.text), sans("990", 24, C.muted)).arrange(RIGHT, buff=0.2) \
        .move_to(P3(ch9.HEALTHY_C[0], 2.55))
    sp.play(FadeIn(ilab, shift=0.05 * DOWN), at=t_te + 0.6, dur=0.5)
    sp.play(FadeIn(hlab, shift=0.05 * DOWN), at=t_te + 1.0, dur=0.5)
    sp.play(FadeIn(sans("9 positive", 22, C.positive).move_to(P3(ch9.ILL_C[0], ch9.ILL_C[1] - 1.05))),
            at=t_nine + 0.4, dur=0.5)
    sp.play(FadeIn(sans("89 positive", 22, C.positive).move_to(P3(ch9.HEALTHY_C[0], -1.85))), at=t_en + 0.6, dur=0.5)

    # all the positives: 9 of 98 are ill
    hud = s.manim(z=50, parallax=0.0)
    blab = VGroup(sans("98", 26, C.text), sans("positive", 26, C.positive)).arrange(RIGHT, buff=0.18) \
        .move_to(P3(ch9.POS_C[0], ch9.POS_C[1] + 1.55))
    hud.play(FadeIn(blab, shift=0.05 * DOWN), at=t_among + 1.0, dur=0.5)
    e = Eqn(r"\frac{9}{9+89}\approx 9\%")
    e.scale(1.1).move_to(P3(RC, 0.6))
    hud.play(Write(e), at=t_oe - 0.5, dur=1.0)
    hud.play(FadeIn(sans("about 1 in 11", 28, C.text).next_to(e, DOWN, buff=0.45)), at=t_oe + 0.3, dur=0.5)
