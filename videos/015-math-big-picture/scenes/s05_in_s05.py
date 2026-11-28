"""in_s05 · A promise, and the first turn. On 'sticks' the map slides left and a floor of boards opens beside it:
needles rain and the estimate 2N/H settles on 3.1416, pi (Buffon's needles, paid off in Chapter 6); every link of the
map flashes in its two hues and fades (every part at once); the map makes its signature move, a 60° turn and back,
and a violet arc marks the angle. On 'definition' the camera pushes in, the map and the circle give way, and the
Foundations node opens into Chapter 1's card. On 'circle' the card shrinks back into its node and THE circle is
drawn again, alone.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import (map_deco, BOARD, MAP_R, N_LOCK, P3, PILLARS, Canvas, Digits, chapter_card, dim, floor, grouped, lit_links,
                 map_lines, node, node_xy, sans, tex, the_circle, window)

TURN = math.pi / 3


@scene(T.in_s05, T.ch1_s01)
def in_s05(s):
    s.solid(C.bg, z=-200)
    mp, nd, m, fx = s.manim(z=-2), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    card_l = s.manim(z=3, parallax=0)
    hud = s.manim(z=2, parallax=0)
    links = VGroup(map_deco(), map_lines(color=C.map_off, width=1.8, opacity=0.75))
    nodes = VGroup(*(node(k, lit=False) for k in range(6)))
    mp.add(links)
    nd.add(nodes)
    circle = the_circle(fill_color=C.bg, fill_opacity=1.0)
    m.add(circle)

    # the sticks: the map slides left and a floor of boards opens beside it. Needles rain, faster and faster; the
    # running estimate 2N/H (throws over crossings, needle length = board spacing) settles on 3.1416 by 'pi'.
    ku = PILLARS.index("uncertainty")
    t_in, t_st, t_pi, t_ev = float(T.in_s05) + 3.6, float(T.in_s05_sticks), float(
        T.in_s05_sticks) + 1.45, float(T.in_s05_every_part)
    s.camera.frame(t_in, center=(3.1, 0.0), zoom=0.86, dur=1.2)
    s.camera.frame(t_ev - 0.1, center=(0.0, 0.0), zoom=1.0, dur=1.3)
    nd.play(nodes[ku][0].animate.set_stroke(color=C.uncertainty, width=3.0), at=t_in + 0.4, dur=0.4)
    nd.play(nodes[ku][0].animate.set_stroke(color=C.map_off, width=2.0), at=t_ev + 0.6, dur=0.5)

    box = (0.75, -2.55, 6.45, 2.55)                                # the floor panel, screen units
    sc = 0.5                                                       # boards 0.3 apart, needles 0.3 long
    cx, cy, th, hit, lines_y = floor(box=tuple(v / sc for v in box))
    cx, cy, lines_y = cx * sc, cy * sc, lines_y * sc
    half = 0.5 * BOARD * sc
    hits_cum = np.cumsum(hit)
    cv = Canvas(box)
    sk = cv.skia
    acc = sk.Surface(cv.w, cv.h)
    state = {"L": 0}

    def n_landed(t):
        u = min(max((t - t_st + 0.1) / (t_pi - t_st + 0.1), 0.0), 1.0)
        return int(round(N_LOCK * u ** 3))

    def seg_pts(idx):
        pts = []
        for n_ in idx:
            dx, dy = half * math.cos(th[n_]), half * math.sin(th[n_])
            pts += [sk.Point(*cv.T(cx[n_] - dx, cy[n_] - dy)), sk.Point(*cv.T(cx[n_] + dx, cy[n_] + dy))]
        return pts

    def accumulate(L):
        """Needles already landed, drawn once into a persistent surface at low alpha (redrawn from 0 if t steps back)."""
        if L < state["L"]:
            acc.getCanvas().clear(sk.ColorTRANSPARENT)
            state["L"] = 0
        lo = state["L"]
        if L > lo:
            c = acc.getCanvas()
            idx = np.arange(lo, L)
            for mask, col, al in ((hit[idx], C.uncertainty, 0.045), (~hit[idx], C.muted, 0.03)):
                c.drawPoints(sk.Canvas.kLines_PointMode, seg_pts(idx[mask]), cv.paint(col, al, 1.2))
            state["L"] = L

    def draw(t):
        L = n_landed(t)
        accumulate(L)
        c = cv.begin()
        board = cv.paint(C.map_off, 0.8, 1.4)
        for y in lines_y:
            c.drawLine(*cv.T(box[0], y), *cv.T(box[2], y), board)
        c.drawImage(acc.makeImageSnapshot(), 0, 0)
        idx = np.arange(max(0, L - 60), L)                          # the newest few, bright
        if len(idx):
            for mask, col in ((hit[idx], C.uncertainty), (~hit[idx], C.muted)):
                c.drawPoints(sk.Canvas.kLines_PointMode, seg_pts(idx[mask]), cv.paint(col, 0.95, 2.4))
        frame = cv.paint(C.map_off, 1.0, 2.0)
        c.drawRect(sk.Rect(*cv.T(box[0], box[3]), *cv.T(box[2], box[1])), frame)
        return cv.array()

    on = fade(t_in + 0.2, dur=0.6, out=t_ev + 0.1, out_dur=0.6)
    s.add(FramesLayer(draw, z=1, parallax=0, opacity=on, during=[(t_in, t_ev + 0.8)], **cv.layer_kw()))

    digits = Digits(32)
    right, base = box[2] - 0.75, box[1] - 0.45
    lab = VGroup(sans("throws", 28, C.muted), sans(r"2N\,/\,H", 28, C.muted))
    lab[0].move_to(P3(box[0], base), aligned_edge=LEFT + DOWN)
    lab[1].move_to(P3(box[0] + 2.75, base), aligned_edge=LEFT + DOWN)

    def numbers(t):
        L = n_landed(t)
        H = int(hits_cum[L - 1]) if L else 0
        est = f"{2 * L / H:.4f}" if H else "-"
        g = VGroup(digits.number(grouped(L), box[0] + 2.35, base),
                   digits.number(est, right, base, color=C.quantity if L == N_LOCK else None))
        return dim(g, float(on(t)))

    hud.play(FadeIn(lab), at=t_st, dur=0.4)
    hud.redraw(window(numbers, t_st - 0.15, t_ev + 0.75), during=(t_st - 0.15, t_ev + 0.8))
    pi_mark = tex(r"\approx \pi", 36, C.quantity).next_to(P3(right, base + 0.12), RIGHT, buff=0.15)
    hud.play(FadeIn(pi_mark, shift=0.08 * RIGHT), at=t_pi, dur=0.4)
    hud.play(FadeOut(lab), FadeOut(pi_mark), at=t_ev + 0.1, dur=0.6)

    # every part at once: all fifteen links flash in their hues
    flash = lit_links(opacity=0.7)
    mp.play(FadeIn(flash), at=T.in_s05_every_part, dur=0.45)
    mp.play(FadeOut(flash), at=T.in_s05_every_part + 1.1, dur=1.0)
    mp.remove(flash, at=T.in_s05_every_part + 2.2)

    # the signature move: the ring turns a sixth of a turn, and back
    tt = T.in_s05_turn
    mp.play(Rotate(links, TURN, about_point=ORIGIN), at=tt, dur=1.2, ease="easy_ease")
    nd.play(Rotate(nodes, TURN, about_point=ORIGIN), at=tt, dur=1.2, ease="easy_ease")
    m.play(Rotate(circle, TURN, about_point=ORIGIN), at=tt, dur=1.2, ease="easy_ease")
    mp.play(Rotate(links, -TURN, about_point=ORIGIN), at=tt + 1.75, dur=1.2, ease="easy_ease")
    nd.play(Rotate(nodes, -TURN, about_point=ORIGIN), at=tt + 1.75, dur=1.2, ease="easy_ease")
    m.play(Rotate(circle, -TURN, about_point=ORIGIN), at=tt + 1.75, dur=1.2, ease="easy_ease")
    mark = VGroup(Arc(radius=MAP_R + 0.62, start_angle=-TURN / 2, angle=TURN, stroke_color=C.structure,
                      stroke_width=3).add_tip(tip_length=0.18, tip_width=0.16),
                  tex(r"60^\circ", 36, C.structure).move_to(P3(MAP_R + 1.18, 0)))
    fx.play(Create(mark[0]), FadeIn(mark[1]), at=T.in_s05_come_back, dur=0.6)
    fx.play(FadeOut(mark), at=T.in_s05_come_back + 2.2, dur=0.5)

    # 'definition': push in; the map and the circle give way; the Foundations node opens into the card
    td = T.in_s05_definition
    s.camera.push(td, zoom=1.12, dur=1.5)
    mp.play(FadeOut(links), at=td, dur=0.7)
    nd.play(FadeOut(VGroup(*nodes[1:])), at=td, dur=0.7)
    nd.play(FadeOut(nodes[0], scale=1.6), at=td + 0.1, dur=0.6)
    m.play(FadeOut(circle), at=td, dur=0.6)
    card = chapter_card("foundations", "logic and sets")
    origin = node_xy(0)
    card_l.play(GrowFromPoint(card, origin), at=td + 0.1, dur=0.9, ease="easy_ease")
    tc = T.in_s05_circle
    card_l.play(card.animate.scale(0.05).move_to(origin).set_opacity(0), at=tc - 0.85, dur=0.7, ease="easy_ease")
    card_l.remove(card, at=tc - 0.1)
    s.camera.push(tc - 0.4, zoom=1.0, dur=1.0)
    fresh = the_circle(fill_color=C.bg, fill_opacity=1.0).rotate(-math.pi / 2)
    m.play(Create(fresh), at=tc, dur=1.0, ease="easy_ease")
