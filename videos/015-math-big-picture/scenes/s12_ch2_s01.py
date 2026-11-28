"""ch2_s01 · One turn of a wheel (Chapter 2 hook).

The map (turned once, Foundations lit) gives way: the Quantity node at the bottom opens into Chapter 2's card, then
the card shrinks away. A wheel one unit across stands on a number line (0 to 4) with its diameter marked 1. A gold
dot is painted on the rim at 0. On the question it rolls one full turn without slipping (centre moves θ·r): the dot
traces a cycloid and the rim is laid down on the line behind it as a gold segment, the distance around. The dot
touches down just past 3, on 'Just past'; on 'pi' a gold tick, π and 3.14159… land there, with C = πd. On 'coin' a
coin and a Ferris wheel peel their rims into straight segments, each π × width.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, P3, chapter_card, map_state, node_xy, sans, tex, the_circle, window, hub_at

X0, SC, YL = -5.0, 2.0, -1.0           # number line: value v at x = X0 + v·SC, on y = YL
RW = SC / 2                            # wheel radius: one unit across


def xv(v):
    return X0 + v * SC


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def wheel(c, th=0.0, op=1.0):
    """A spoked wheel at centre c turned by -th: dark tyre, the circle's rim, an inner rim, twelve spokes, a hub."""
    g = VGroup(Circle(radius=RW, stroke_color=C.map_off, stroke_width=13, stroke_opacity=op).move_to(c),
               the_circle(RW).move_to(c).set_stroke(opacity=op),
               Circle(radius=0.8 * RW, stroke_color=C.muted, stroke_width=1.4, stroke_opacity=0.7 * op).move_to(c))
    for k in range(12):
        a = -th + math.pi / 2 + 2 * math.pi * k / 12
        u = P3(math.cos(a), math.sin(a))
        g.add(Line(c + 0.12 * u, c + 0.8 * RW * u, stroke_color=C.muted, stroke_width=1.3, stroke_opacity=0.8 * op))
    g.add(Circle(radius=0.12, stroke_color=C.circle, stroke_width=2, fill_color=C.bg, fill_opacity=op,
                 stroke_opacity=op).move_to(c), Dot(c, radius=0.04, color=C.text).set_opacity(op))
    return g


def peel(c, r, u, rim_col, seg_col, width=4):
    """A circle's rim peeling off from its lowest point onto a straight segment to the right: fraction u laid flat."""
    c = np.asarray(c, dtype=float)
    g = VGroup()
    L = 2 * math.pi * r * u
    b = c + P3(0, -r)
    if u < 0.999:
        a0 = -math.pi / 2 + 2 * math.pi * u
        g.add(Arc(radius=r, start_angle=a0, angle=2 * math.pi * (1 - u), arc_center=c, stroke_color=rim_col,
                  stroke_width=width))
    if L > 0.01:
        g.add(Line(b, b + P3(L, 0), stroke_color=seg_col, stroke_width=width + 1))
    return g


@scene(T.ch2_s01, T.ch2_s02)
def ch2_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    mp_, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    lit = glow_layer(s, z=1.5, color=C.quantity, k=0.8)          # the laid rim, the cycloid and the painted dot
    card_l = s.manim(z=3, parallax=0)
    t0 = float(s.start)
    t_wh, t_dot, t_td = float(T.ch2_s01_wheel), float(T.ch2_s01_dot), float(T.ch2_s01_touch_down)
    t_jp, t_pi, t_coin = float(T.ch2_s01_just_past), float(T.ch2_s01_pi), float(T.ch2_s01_coin)

    # where Chapter 1 left the map; Quantity (now at the bottom) opens into the card
    links, nodes = map_state(60, lit=("foundations",))
    hub = hub_at(60)
    mp_.add(links)
    nd.add(nodes)
    m.add(hub)
    s.camera.push(t0 + 0.2, zoom=1.12, dur=1.4)
    mp_.play(FadeOut(links), at=t0 + 0.2, dur=0.7)
    nd.play(FadeOut(VGroup(*(nodes[k] for k in (0, 2, 3, 4, 5)))), at=t0 + 0.2, dur=0.7)
    nd.play(FadeOut(nodes[1], scale=1.6), at=t0 + 0.3, dur=0.6)
    m.play(FadeOut(hub), at=t0 + 0.2, dur=0.6)
    card = chapter_card("quantity", "numbers and measure")
    origin = node_xy(1, turn=60)
    card_l.play(GrowFromPoint(card, origin), at=t0 + 0.3, dur=0.9, ease="easy_ease")
    card_l.play(card.animate.scale(0.05).move_to(origin).set_opacity(0), at=t_wh - 1.1, dur=0.7, ease="easy_ease")
    card_l.remove(card, at=t_wh - 0.35)
    s.camera.push(t_wh - 0.9, zoom=1.0, dur=1.0)

    # the number line and the wheel
    nl = VGroup(Line(P3(xv(-0.35), YL), P3(xv(4.3), YL), stroke_color=C.muted, stroke_width=2.4))
    for k in range(5):
        nl.add(Line(P3(xv(k), YL - 0.14), P3(xv(k), YL + 0.14), stroke_color=C.muted, stroke_width=2.4),
               tex(str(k), 36, C.muted).move_to(P3(xv(k), YL - 0.5)))
    for k in range(1, 41):
        if k % 10:
            x = xv(k / 10)
            nl.add(Line(P3(x, YL - 0.06), P3(x, YL + 0.06), stroke_color=C.map_off, stroke_width=1.4))
    track = VGroup(Rectangle(width=xv(4.3) - xv(-0.35), height=0.32, stroke_width=0, fill_color=C.map_off,
                             fill_opacity=0.22).move_to(P3((xv(-0.35) + xv(4.3)) / 2, YL - 0.16)),
                   Line(P3(xv(-0.35), YL - 0.32), P3(xv(4.3), YL - 0.32), stroke_color=C.map_off, stroke_width=1))
    m.play(FadeIn(track), at=t_wh - 0.6, dur=0.8)
    m.play(Create(nl[0]), at=t_wh - 0.6, dur=0.8)
    m.play(LaggedStart(*(FadeIn(x_) for x_ in nl[1:]), lag_ratio=0.01), at=t_wh - 0.2, dur=0.8)
    c0 = P3(xv(0), YL + RW)
    wheel0 = wheel(c0)
    m.play(GrowFromCenter(wheel0), at=t_wh, dur=0.6, ease="out_back")
    diam = VGroup(Line(c0 + P3(0, -RW), c0 + P3(0, RW), stroke_color=C.text, stroke_width=2),
                  tex("1", 34, C.text).move_to(c0 + P3(0.24, 0.35)))
    m.play(Create(diam[0]), FadeIn(diam[1]), at=t_wh + 1.0, dur=0.6)
    m.play(FadeOut(diam), at=t_td - 1.0, dur=0.5)
    dot0 = Dot(c0 + P3(0, -RW), radius=0.085, color=C.quantity)
    m.play(GrowFromCenter(dot0), at=t_dot, dur=0.35, ease="out_back")

    # the roll: θ from 0 to 2π, centre at θ·r; the rim is laid flat behind it
    t_r0, t_r1 = t_td + 0.55, t_jp
    s.camera.frame(t_r0, center=(1.2, 0.0), zoom=1.0, dur=t_r1 - t_r0 + 0.6, ease="smooth")

    def theta(t):
        return 2 * math.pi * ss((t - t_r0) / (t_r1 - t_r0))

    def rolling(t):
        th = theta(t)
        return wheel(P3(xv(0) + th * RW, YL + RW), th)

    def trail(t):
        th = theta(t)
        c = P3(xv(0) + th * RW, YL + RW)
        g = VGroup()
        if th > 0.01:
            g.add(Line(P3(xv(0), YL), P3(c[0], YL), stroke_color=C.quantity, stroke_width=6))
            ts = np.linspace(0, th, 90)
            cyc = [P3(xv(0) + a * RW - RW * math.sin(a), YL + RW - RW * math.cos(a)) for a in ts]
            g.add(VMobject(stroke_color=C.quantity, stroke_width=2.2, stroke_opacity=0.8).set_points_smoothly(cyc))
        g.add(Dot(c + RW * P3(-math.sin(th), -math.cos(th)), radius=0.085, color=C.quantity))
        return g

    m.remove(wheel0, dot0, at=t_r0 - 0.05)
    top.redraw(window(rolling, t_r0 - 0.05, float(s.end)), during=(t_r0 - 0.05, float(s.end)))
    lit.redraw(window(trail, t_r0 - 0.05, float(s.end)), during=(t_r0 - 0.05, float(s.end)))
    xp = xv(math.pi)
    ping = Circle(radius=0.1, stroke_color=C.quantity, stroke_width=3).move_to(P3(xp, YL))
    top.play(ping.animate.scale(4).set_stroke(opacity=0), at=t_jp + 0.05, dur=0.8)
    top.remove(ping, at=t_jp + 0.9)

    # 'pi': the tick, the glyph, the decimals, and C = πd
    tick = Line(P3(xp, YL - 0.26), P3(xp, YL + 0.26), stroke_color=C.quantity, stroke_width=4)
    pi_l = tex(r"\pi = 3.14159\ldots", 44, C.quantity).move_to(P3(xp, YL - 1.25))
    cpd = MathTex("C", "=", r"\pi", "d", font_size=48, color=C.text)
    cpd[0].set_color(C.circle)
    cpd[2].set_color(C.quantity)
    cpd.move_to(P3(xp, YL - 2.15))
    m.play(GrowFromCenter(tick), at=t_pi - 0.3, dur=0.4)
    m.play(Write(pi_l), at=t_pi, dur=0.8)
    m.play(FadeIn(cpd, shift=0.1 * UP), at=t_pi + 1.0, dur=0.6)

    # 'coin' and 'Ferris wheel': rims peel into straight segments, π × width each
    coin_c, coin_r = P3(-4.3, 2.55), 0.32
    fw_c, fw_r = P3(1.3, 2.35), 0.85
    t_c0, t_f0 = t_coin - 0.1, t_coin + 0.9
    ferris = VGroup()
    for k in range(10):
        a = 2 * math.pi * k / 10
        ferris.add(Line(fw_c, fw_c + fw_r * P3(math.cos(a), math.sin(a)), stroke_color=C.map_off, stroke_width=1.4),
                   Square(0.13, stroke_color=C.muted, stroke_width=1.4).move_to(fw_c + (fw_r + 0.1) * P3(math.cos(a),
                                                                                                         math.sin(a))))
    ferris.add(Line(fw_c, fw_c + P3(-0.55, -fw_r - 0.25), stroke_color=C.muted, stroke_width=2),
               Line(fw_c, fw_c + P3(0.55, -fw_r - 0.25), stroke_color=C.muted, stroke_width=2))
    coin_face = tex("1", 26, C.muted).move_to(coin_c)
    m.play(FadeIn(coin_face), at=t_c0, dur=0.4)
    m.play(FadeIn(ferris), at=t_f0, dur=0.5)

    def rims(t):
        g = VGroup()
        for c_, r_, ta in ((coin_c, coin_r, t_c0), (fw_c, fw_r, t_f0)):
            a = ss((t - ta) / 0.4) * (1 - ss((t - t_end + 0.95) / 0.7))
            if a <= 0:
                continue
            u = ss((t - ta - 0.6) / 1.8)
            g.add(Circle(radius=r_, stroke_color=C.map_off, stroke_width=1.6, stroke_opacity=a).move_to(c_))
            p = peel(c_, r_, u, C.circle, C.quantity, width=3.5)
            if a < 1:
                p.set_stroke(opacity=a)
            g.add(p)
        return g

    t_end = float(s.end)
    m.redraw(window(rims, t_c0 - 0.05, float(s.end)), during=(t_c0 - 0.05, float(s.end)))
    for c_, r_, ta in ((coin_c, coin_r, t_c0), (fw_c, fw_r, t_f0)):
        L = 2 * math.pi * r_
        tag = tex(r"\pi \times \text{width}", 30, C.quantity).move_to(c_ + P3(L / 2, -r_ - 0.42))
        m.play(FadeIn(tag, shift=0.06 * UP), at=ta + 2.3, dur=0.5)
        m.play(FadeOut(tag), at=t_end - 0.95, dur=0.7)
    m.play(FadeOut(VGroup(cpd, coin_face, ferris)), at=t_end - 0.95, dur=0.7)
