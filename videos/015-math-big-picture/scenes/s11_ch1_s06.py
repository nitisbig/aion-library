"""ch1_s06 · Sets every day (sighting and takeaway).

A shop's catalogue: thirty shoe tiles in a frame, two overlapping disks 'red' and 'your size' sorting them. On
'overlap' the lens fills and its four tiles fly to a results panel (A ∩ B · 4 results); on 'or' the whole union fills
and seventeen tiles fly over (A ∪ B · 17 results). Counts come from the tiles themselves. On 'Underneath' the shop
clears and the chapter's hero comes back: the circle inside its set braces with its rule. On 'built on top' the map
grows round it, the hero shrinks into the Foundations node, which lights, and in the silence the ring makes the
signature 60° turn while the camera settles on the whole map.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import (HUB_R, P3, PILLARS, R1, eq_parts, map_lines, node, node_xy, sans, set_braces, tex, the_circle,
                 tint, window)
from kit import hub_at, map_state, turn_view

U_C, U_W, U_H = P3(-2.4, -0.25), 8.4, 5.5
A_C, B_C, RD = P3(-3.45, -0.35), P3(-1.35, -0.35), 1.75
COUNTS = {"both": 4, "a": 7, "b": 6, "none": 13}


def region(p):
    ina = np.linalg.norm(p - A_C[:2]) < RD - 0.18
    inb = np.linalg.norm(p - B_C[:2]) < RD - 0.18
    outa = np.linalg.norm(p - A_C[:2]) > RD + 0.18
    outb = np.linalg.norm(p - B_C[:2]) > RD + 0.18
    if ina and inb:
        return "both"
    if ina and outb:
        return "a"
    if inb and outa:
        return "b"
    if outa and outb:
        return "none"
    return None


def place_tiles(seed=1516):
    rg = np.random.default_rng(seed)
    out = []
    x0, x1 = U_C[0] - U_W / 2 + 0.3, U_C[0] + U_W / 2 - 0.3
    y0, y1 = U_C[1] - U_H / 2 + 0.3, U_C[1] + U_H / 2 - 1.25
    for reg_, n in COUNTS.items():
        got = 0
        while got < n:
            p = rg.uniform([x0, y0], [x1, y1])
            if region(p) == reg_ and all(np.linalg.norm(p - q) > 0.42 for q, _ in out):
                out.append((p, reg_))
                got += 1
    return out


def tile(p, k=1.0):
    """A shoe, side view: sole, toe and heel collar."""
    pts = [(-0.17, -0.07), (0.17, -0.07), (0.18, -0.02), (0.06, 0.02), (-0.03, 0.09), (-0.15, 0.09), (-0.17, -0.07)]
    shoe = VMobject(stroke_color=C.text, stroke_width=1.6, fill_color=tint(C.muted, 0.35), fill_opacity=1)
    shoe.set_points_as_corners([P3(*q) for q in pts])
    sole = Line(P3(-0.17, -0.07), P3(0.17, -0.07), stroke_color=C.text, stroke_width=2.6)
    return VGroup(shoe, sole).move_to(P3(*p)).set_opacity(k)


@scene(T.ch1_s06, T.ch2_s01)
def ch1_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    fills, m, top = s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t_red, t_ov, t_or = float(T.ch1_s06_red), float(T.ch1_s06_overlap), float(T.ch1_s06_or)
    t_und, t_top = float(T.ch1_s06_underneath), float(T.ch1_s06_built_on_top)
    t0 = float(s.start)

    # the catalogue
    frame = RoundedRectangle(width=U_W, height=U_H, corner_radius=0.18, stroke_color=C.map_off, stroke_width=2)
    frame.move_to(U_C)
    head = sans("all shoes", 28, C.muted).move_to(frame.get_corner(UL) + P3(0.95, -0.32))
    tiles_data = place_tiles()
    tiles = [tile(p) for p, _ in tiles_data]
    m.play(Create(frame), FadeIn(head), at=t0 + 0.6, dur=0.8)
    m.play(LaggedStart(*(FadeIn(t_, scale=0.6) for t_ in tiles), lag_ratio=0.03), at=t0 + 1.0, dur=1.6)

    A = Circle(radius=RD, stroke_color=C.foundations, stroke_width=3).move_to(A_C)
    B = Circle(radius=RD, stroke_color=C.foundations, stroke_width=3).move_to(B_C)
    la = sans("red", 32, C.foundations).next_to(A, UP, buff=0.12).shift(LEFT * 0.5)
    lb = sans("your size", 32, C.foundations).next_to(B, UP, buff=0.12).shift(RIGHT * 0.5)
    m.play(Create(A), FadeIn(la), at=t_red - 0.1, dur=0.6)
    m.play(Create(B), FadeIn(lb), at=t_red + 0.8, dur=0.6)

    # results panel
    panel = RoundedRectangle(width=3.4, height=5.5, corner_radius=0.18, stroke_color=C.map_off, stroke_width=2)
    panel.move_to(P3(4.65, -0.25))
    p_head = sans("results", 28, C.muted).move_to(panel.get_top() + P3(-0.8, -0.32))
    m.play(Create(panel), FadeIn(p_head), at=t_red + 1.6, dur=0.6)

    def slots(n):
        return [panel.get_top() + P3(-1.12 + 0.56 * (j % 5), -0.95 - 0.48 * (j // 5)) for j in range(n)]

    def results(kind, t_at, eq_tex):
        sel = [j for j, (_, r) in enumerate(tiles_data) if (r == "both" if kind == "and" else r in ("both", "a", "b"))]
        copies = [tiles[j].copy() for j in sel]
        targets = [tile(sp[:2]) for sp in slots(len(sel))]
        for c_ in copies:
            top.add(c_, at=t_at + 0.6)
        top.play(LaggedStart(*(Transform(c_, tg, path_arc=-0.5) for c_, tg in zip(copies, targets)), lag_ratio=0.06),
                 at=t_at + 0.6, dur=1.4, ease="easy_ease")
        eq = eq_parts(*eq_tex, size=44)
        for part in eq:
            part.set_color(C.foundations)
        cnt = sans(f"{len(sel)} results", 30, C.text)
        lab = VGroup(eq, cnt).arrange(RIGHT, buff=0.3).move_to(panel.get_bottom() + P3(0, 0.55))
        m.play(FadeIn(lab, shift=0.08 * UP), at=t_at + 1.4, dur=0.5)
        hi = [tiles[j] for j in sel]
        return copies, lab, hi

    lens = Intersection(A, B, stroke_width=0, fill_color=C.foundations, fill_opacity=0.3)
    union = Union(A, B, stroke_width=0, fill_color=C.foundations, fill_opacity=0.2)
    fills.play(FadeIn(lens), at=t_ov, dur=0.5)
    c_and, lab_and, _ = results("and", t_ov, ("A", r"\cap", "B"))
    fills.play(FadeOut(lens), FadeIn(union), at=t_or, dur=0.6)
    top.play(*(FadeOut(c_) for c_ in c_and), at=t_or - 0.1, dur=0.4)
    m.play(FadeOut(lab_and), at=t_or - 0.1, dur=0.4)
    c_or, lab_or, _ = results("or", t_or, ("A", r"\cup", "B"))

    # 'Underneath': the shop clears; the hero returns
    shop = VGroup(frame, head, A, B, la, lb, panel, p_head, lab_or, *tiles)
    m.play(FadeOut(shop), at=t_und - 0.3, dur=0.7)
    fills.play(FadeOut(union), at=t_und - 0.3, dur=0.7)
    top.play(*(FadeOut(c_) for c_ in c_or), at=t_und - 0.3, dur=0.7)
    hero_c = the_circle(R1)
    braces = set_braces(2 * R1 + 0.9, 2 * R1 + 1.0)
    rule = eq_parts(r"\{", "(x,y)", ":", "x^2", "+", "y^2", "=", "r^2", r"\}", size=40)
    rule[1].set_color(C.text)
    rule.move_to(P3(0, -R1 - 0.85))
    m.play(Create(hero_c), at=t_und + 0.2, dur=1.0, ease="easy_ease")
    m.play(FadeIn(braces, scale=1.2), at=t_und + 0.6, dur=0.7)
    m.play(Write(rule), at=t_und + 1.1, dur=1.0)

    # 'what is in and what is out': a point inside, one outside, one on, each answered
    t_io = t_und + 5.1
    probes = [(0.55, 0.0, C.foundations), (1.0, 0.6, C.circle), (1.35, 2.2, C.muted)]
    pr = VGroup(*(Dot(R1 * f * P3(math.cos(a), math.sin(a)), radius=0.08, color=col) for f, a, col in probes))
    m.play(LaggedStart(*(GrowFromCenter(d) for d in pr), lag_ratio=0.3), at=t_io, dur=0.9, ease="out_back")
    m.play(FadeOut(pr), at=t_top - 1.4, dur=0.5)

    # 'built on top': the map grows round it; the hero shrinks into Foundations, which lights; the 60° turn
    s.camera.base["zoom"] = 1.0
    s.camera.push(t_top - 1.4, zoom=0.94, dur=1.2, ease="easy_ease")
    s.camera.push(t_top + 1.0, zoom=1.0, dur=1.3, ease="easy_ease")
    links = map_state(0)[0]
    unlit = VGroup(*(node(k, lit=False) for k in range(6)))
    hub = the_circle(fill_color=C.bg, fill_opacity=1.0)
    m.play(Transform(hero_c, hub), at=t_top - 1.2, dur=1.0, ease="easy_ease")
    fills.play(FadeIn(links), at=t_top - 1.0, dur=0.8)
    top.play(LaggedStart(*(GrowFromCenter(n_) for n_ in unlit), lag_ratio=0.08), at=t_top - 0.9, dur=0.9)
    target = node_xy(0)
    m.play(VGroup(braces, rule).animate.scale(0.06).move_to(target).set_opacity(0), at=t_top, dur=0.7,
           ease="in_cubic")
    lit0 = node(0, lit=True)
    top.play(Transform(unlit[0], lit0), at=t_top + 0.55, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=C.foundations, stroke_width=3).move_to(target)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_top + 0.6, dur=0.8)
    top.remove(ping, at=t_top + 1.45)

    # the signature turn: the whole ring rotates by a sixth of a turn (Quantity comes round to the bottom)
    t_turn = t_top + 1.0
    turn_d = float(s.end) - 0.05 - t_turn

    def deg(t):
        u = min(max((t - t_turn + 0.15) / turn_d, 0.0), 1.0)
        return 60 * (u * u * (3 - 2 * u))

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 30)

    def ring_at(t):
        return VGroup(*(node(k, lit=(k == 0), turn=deg(t), view=TV(t)) for k in range(6)))

    def links_at(t):
        return map_state(deg(t), view=TV(t))[0]

    fills.remove(links, at=t_turn - 0.15)
    top.remove(*unlit, at=t_turn - 0.15)
    top.redraw(window(ring_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    m.remove(hero_c, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    fills.redraw(window(links_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
