"""co_s01 · Sticks on a floor (the cold open, the video's first scene).

A wooden floor of boards fills the frame. On 'stick' the first needle drops and settles; on 'another' two more. On
'Count' needles that cross a crack turn pink and a readout (throws, crossings, 2N/H) comes up; the throws ramp to
30 331 and the estimate narrows until on 'pi' it locks at 3.1416 and turns gold, ≈ π. On 'no circle' the camera
pulls back and the floor dims. On 'hiding' 360 needles slide to the centre keeping their angles and grow until their
tips sit on one circle; THE circle draws over them and holds alone.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import (glow_layer, FL_BOX, HUB_R, N_LOCK, P3, Canvas, Digits, full_floor, mix_hex, sans, tex, the_circle, window, wood_floor)

N_SLIDE = 360


def ss(x):
    return np.clip(x, 0.0, 1.0) ** 2 * (3 - 2 * np.clip(x, 0.0, 1.0))


@scene(T.start, T.in_s01)
def co_s01(s):
    s.solid(C.bg, z=-200)
    m, hud = s.manim(z=1), s.manim(z=3, parallax=0)
    t0, t1 = float(s.start), float(s.end)
    t_st, t_an, t_ct = float(T.co_s01_stick), float(T.co_s01_another), float(T.co_s01_count)
    t_pi, t_nc, t_hd = float(T.co_s01_pi), float(T.co_s01_no_circle), float(T.co_s01_hiding)
    U = C.uncertainty

    cx, cy, th, hit, lines_y, half = full_floor(N_LOCK)
    t_lock = t_pi + 0.15

    # how many have landed by time t: one, then two more, then an exponential ramp to N_LOCK by 'pi'
    def n_at(t):
        if t < t_st - 0.1:
            return 0
        if t < t_an:
            return 1
        if t < t_an + 1.1:
            return 2
        if t < t_ct:
            return 3
        u = min((t - t_ct) / (t_lock - t_ct), 1.0)
        return int(round(3 * (N_LOCK / 3) ** (u ** 1.6)))

    grid = np.arange(t0, t_lock + 0.5, 0.002)
    ns = np.array([n_at(t) for t in grid])
    land = grid[np.minimum(np.searchsorted(ns, np.arange(1, N_LOCK + 1)), len(grid) - 1)]   # when each one lands
    cum_hit = np.cumsum(hit)

    # the floor: wood, drawn once; dims to 40% on 'no circle'
    rgba, kw = wood_floor(lines_y)
    s.add(ArrayLayer(rgba, z=-5, opacity=keys((t0, 0.0), (t0 + 0.6, 1.0), (t_nc, 1.0), (t_nc + 1.5, 0.4),
                                                (t_hd + 0.4, 0.4), (t_hd + 1.5, 0.0), default_ease="smooth"), **kw))

    # the needles, drawn per frame
    cv = Canvas(FL_BOX)
    sk = cv.skia
    slide = np.arange(N_SLIDE)

    # a stick is drawn like a real one: soft shadow on the boards, a birch body with a lit edge and a shaded edge,
    # darker end grain. In the air it is bigger (closer), spins, and its shadow sits further off and blurrier.
    BODY = mix_hex(C.text, C.change, 0.32)
    W = 7.0                                                   # stick thickness, px
    tone = {}

    def tones(u_hit):
        key = round(float(u_hit), 2)
        if key not in tone:
            b = mix_hex(BODY, U, 0.78 * key)
            tone[key] = (b, mix_hex(b, C.text, 0.55), mix_hex(b, C.bg, 0.38), mix_hex(b, C.bg, 0.55))
        return tone[key]

    def stroke(color, alpha, width, cap=None, blur=0.0):
        p_ = cv.paint(color, alpha, width)
        p_.setStrokeCap(cap if cap is not None else sk.Paint.kButt_Cap)
        if blur > 0:
            p_.setMaskFilter(sk.MaskFilter.MakeBlur(sk.kNormal_BlurStyle, blur))
        return p_

    shadow_rest = stroke(C.bg, 0.5, W + 1.0, sk.Paint.kRound_Cap, 1.6)

    def stick(c, x, y, a, ln, u_hit, alpha, lift=0.0, w=W):
        """One stick centred at world (x, y), angle a, length ln (world units)."""
        if alpha <= 0.01:
            return
        X, Y = cv.T(x, y)
        h = 0.5 * ln * cv.px
        dx, dy = h * math.cos(a), -h * math.sin(a)
        nx, ny = -dy / max(h, 1e-6), dx / max(h, 1e-6)        # unit normal (screen)
        body, lite, dark, grain = tones(u_hit)
        ox, oy = 3.0 + 26.0 * lift, 4.0 + 34.0 * lift          # the shadow drifts off as the stick rises
        sh = shadow_rest if lift <= 0 else stroke(C.bg, 0.5 * (1 - 0.5 * lift), w + 1.0, sk.Paint.kRound_Cap,
                                                  1.6 + 7.0 * lift)
        if lift <= 0:
            sh.setAlphaf(0.5 * alpha)
        else:
            sh.setAlphaf(0.5 * (1 - 0.5 * lift) * alpha)
        c.drawLine(X - dx + ox, Y - dy + oy, X + dx + ox, Y + dy + oy, sh)
        c.drawLine(X - dx, Y - dy, X + dx, Y + dy, stroke(body, alpha, w))
        o = 0.27 * w                                         # lit edge (upper left) and shaded edge
        c.drawLine(X - dx - nx * o, Y - dy - ny * o, X + dx - nx * o, Y + dy - ny * o, stroke(lite, 0.75 * alpha, 0.3 * w))
        c.drawLine(X - dx + nx * o, Y - dy + ny * o, X + dx + nx * o, Y + dy + ny * o, stroke(dark, 0.8 * alpha, 0.3 * w))
        e = min(0.9 * w, 0.2 * h) / max(h, 1e-6)              # end grain at both ends
        for sgn in (-1, 1):
            c.drawLine(X + sgn * dx, Y + sgn * dy, X + sgn * dx * (1 - e), Y + sgn * dy * (1 - e),
                       stroke(grain, alpha, w))

    def lines(c, ids, col, alpha, width):
        dx, dy = half * np.cos(th[ids]), half * np.sin(th[ids])
        pts = []
        for a, b, c2, d in zip(cx[ids] - dx, cy[ids] - dy, cx[ids] + dx, cy[ids] + dy):
            pts += [sk.Point(*cv.T(a, b)), sk.Point(*cv.T(c2, d))]
        c.drawPoints(sk.Canvas.kLines_PointMode, pts, cv.paint(col, alpha, width))

    N_FULL = 420                                              # the first throws keep their full look; the rest, fine lines
    SPIN = np.random.default_rng(7).uniform(-1.6, 1.6, N_LOCK)

    def draw(t):
        c = cv.begin()
        n = n_at(t)
        lit = float(ss((t - t_ct + 0.1) / 0.5))              # crossings blush pink on 'Count'
        rest = float(1.0 - ss((t - t_hd - 0.2) / 0.6))       # the rain gives way to the slide
        if n and rest > 0:
            ids = np.arange(n)
            ids = ids[ids >= N_SLIDE] if t > t_hd - 0.1 else ids
            age = t - land[ids]
            fresh = age < 0.45
            old = ids[~fresh]
            mass = old[old >= N_FULL]                       # the crowd: thin strokes in the stick tones
            if len(mass):
                b_hit, b_miss = tones(lit)[0], tones(0)[0]
                thin = min(1.0, (2500 / len(mass)) ** 0.6)    # the floor keeps showing through the crowd
                lines(c, mass[~hit[mass]], b_miss, 0.22 * thin * rest * (1 - 0.3 * lit), 1.3)
                lines(c, mass[hit[mass]], b_hit, 0.3 * thin * rest, 1.3)
            for i in old[old < N_FULL]:
                stick(c, cx[i], cy[i], th[i], 2 * half, lit if hit[i] else 0.0, rest * (1 - 0.25 * lit * (not hit[i])))
            for i in ids[fresh][-40:]:                      # sticks in the air: closer, spinning, then settling
                u = float(ss((t - land[i]) / 0.45))
                lift = 1 - u
                stick(c, cx[i], cy[i], th[i] + SPIN[i] * lift, 2 * half * (1 + 0.45 * lift),
                      lit if hit[i] else 0.0, rest * min(1.0, 0.2 + 1.6 * u), lift=lift, w=W * (1 + 0.45 * lift))
        if t > t_hd - 0.1:                                   # 'hiding': slide to the centre, tips on one circle
            f = 1.0 - float(ss((t - t_hd - 1.6) / 0.5))
            if f > 0:
                u = ss((t - t_hd + 0.1 - 0.0015 * slide) / 1.1)
                k = (1 - u) + u * (HUB_R / half)
                for j in slide:
                    stick(c, (1 - u[j]) * cx[j], (1 - u[j]) * cy[j], th[j], 2 * half * k[j], 1.0,
                          f * (0.9 - 0.45 * u[j]), w=W * (1 - 0.55 * u[j]))
        return cv.array()

    s.add(FramesLayer(draw, z=0, during=[(t_st - 0.2, min(t_hd + 2.2, t1))], **cv.layer_kw()))

    # the readout (HUD)
    X0, XR, Y = -6.3, -2.55, (3.2, 2.65, 2.1)
    panel = RoundedRectangle(width=5.45, height=1.85, corner_radius=0.08, stroke_width=0, fill_color=C.bg,
                             fill_opacity=0.82).move_to(P3(-3.93, 2.62))
    labels = VGroup(sans("throws", 30, C.muted), sans("crossings", 30, C.muted), sans(r"2N\,/\,H", 30, C.muted))
    for lab, y in zip(labels, Y):
        lab.move_to(P3(X0, y), aligned_edge=LEFT)
    hud.play(FadeIn(panel), FadeIn(labels, shift=0.06 * UP), at=t_ct - 0.1, dur=0.5)
    dg, gold = Digits(32), Digits(32, C.quantity)

    def grouped_(v):
        return f"{v:,}".replace(",", " ")

    def readout(t):
        n = max(n_at(t), 3)
        h = int(cum_hit[n - 1])
        g = VGroup(dg.number(grouped_(n), XR, Y[0] - 0.12), dg.number(grouped_(h), XR, Y[1] - 0.12))
        est = f"{2 * n / max(h, 1):.4f}"
        g.add((gold if t >= t_lock else dg).number(est, XR, Y[2] - 0.12))
        return g.set_opacity(1.0 - float(ss((t - t_hd + 0.3) / 0.5)))

    hud.redraw(window(readout, t_ct - 0.1, t_hd + 0.25), during=(t_ct - 0.1, t_hd + 0.3))
    approx = tex(r"\approx \pi", 40, C.quantity).move_to(P3(XR + 0.62, Y[2]))
    hud.play(FadeIn(approx, shift=0.06 * LEFT), at=t_lock, dur=0.5)
    hud.play(FadeOut(VGroup(panel, labels, approx)), at=t_hd - 0.3, dur=0.5)

    # 'no circle': pull back; 'hiding': THE circle draws over the tips and holds alone
    s.camera.push(t_nc, zoom=0.92, dur=1.5, ease="easy_ease")
    circ = the_circle(fill_opacity=0)
    gl = glow_layer(s, z=1.5, color=C.circle)
    gl.play(Create(circ), at=t_hd + 1.1, dur=0.9, ease="easy_ease")
    gl.play(FadeOut(circ), at=t1 - 0.35, dur=0.35)
