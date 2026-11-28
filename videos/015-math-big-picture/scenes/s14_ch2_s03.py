"""ch2_s03 · Kinds of number.

The deep zoom on π pulls back out to the whole line, −4 to 4. On 'Counting' gold dots land on 1, 2, 3 and a box ℕ
opens in a nested diagram; on 'Owing' each dot is mirrored across 0 to −1, −2, −3 and ℤ wraps ℕ; on 'pizza' a pizza
is cut into eighths, one slice pulled out, and fraction ticks p/q (q up to 8) fill the line while ℚ wraps ℤ. On
'packed' the camera dives onto the stretch from 3 to 3.25; on 'halfway' midpoints drop in, depth after depth (seven
levels, 255 ticks) until the stretch looks solid, beside the midpoint rule. On 'no room' a dashed box 'ℝ ?' waits
outside ℚ.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, sans, tex, tint, window, zline

YL = -0.9


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp_log(t, keys):
    """Zoom between keyframes (t, centre, scale, anchor): the scale moves geometrically and the anchor value glides
    in a straight line on screen, so the zoom happens about a point the viewer can follow."""
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2]
    for (ta, ca, sa, a), (tb, cb, sb, _) in zip(keys, keys[1:]):
        if t <= tb:
            u = ss((t - ta) / (tb - ta))
            sc = math.exp(math.log(sa) + u * (math.log(sb) - math.log(sa)))
            xs = (a - ca) * sa + u * ((a - cb) * sb - (a - ca) * sa)
            return a - xs / sc, sc
    return keys[-1][1], keys[-1][2]


@scene(T.ch2_s03, T.ch2_s04)
def ch2_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_cnt, t_owe, t_piz = float(T.ch2_s03_counting), float(T.ch2_s03_owing), float(T.ch2_s03_pizza)
    t_pack, t_half, t_room = float(T.ch2_s03_packed), float(T.ch2_s03_halfway), float(T.ch2_s03_no_room)

    # where ch2_s02 left off (the deepest zoom), then back out to the whole line
    dec = VGroup(tex(r"\tfrac{355}{113} = 3.141592\mathbf{9}\ldots", 40, C.text),
                 tex(r"\pi = 3.141592\mathbf{6}\ldots", 40, C.quantity)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    dec.move_to(P3(0, 2.55))
    yb, xg = -0.3 - 0.95, (355 / 113 - math.pi) * 1.0e7
    gap = VGroup(Line(P3(0, yb), P3(xg, yb), stroke_color=C.quantity, stroke_width=3),
                 Line(P3(0, yb - 0.12), P3(0, yb + 0.12), stroke_color=C.quantity, stroke_width=3),
                 Line(P3(xg, yb - 0.12), P3(xg, yb + 0.12), stroke_color=C.quantity, stroke_width=3))
    gtag = tex(r"\text{gap} \approx 0.00000027", 36, C.quantity).next_to(gap, DOWN, buff=0.2)
    ztag = tex(r"\times\,10^{6}", 34, C.muted).move_to(P3(5.9, -3.45))
    m.add(dec, gap, gtag, ztag)
    m.play(FadeOut(VGroup(dec, gap, gtag, ztag)), at=t0 + 0.1, dur=0.6)

    keys = [(t0 + 0.4, math.pi, 1.0e7, math.pi), (t0 + 3.0, 0.0, 1.45, 0.0), (t_pack, 0.0, 1.45, 3.125),
            (t_pack + 2.0, 3.125, 40.0, 3.125)]

    def y_at(t):
        return -0.3 + (YL + 0.3) * ss((t - t0 - 0.4) / 2.6)

    pi_t, f355 = tex(r"\pi", 44, C.quantity), tex(r"\tfrac{355}{113}", 40, C.text)
    t_dots = [t_cnt + 0.25 * k for k in range(3)]
    t_mir = [t_owe + 0.2 * k for k in range(3)]
    t_q = {q: t_piz + 1.0 + 0.3 * (q - 2) for q in range(2, 9)}
    t_d = [t_half - 0.05 + 0.55 * d for d in range(7)]
    fracs = sorted({(p, q) for q in range(2, 9) for p in range(-4 * q, 4 * q + 1) if math.gcd(p, q) == 1})

    def line(t):
        c, sc = lerp_log(t, keys)
        y = y_at(t)
        k_sp = min(max(math.log(sc / 1.45) / math.log(40 / 1.45), 0.0), 1.0)
        g = zline(c, sc, y, size=24, spacing=1.45 + 1.15 * k_sp)  # matches ch2_s02's 2.6 when zoomed in
        # 355/113 merges into π and fades first; π rides the zoom out, then fades among the whole numbers
        for v, lab, col, fade_old in ((math.pi, pi_t, C.quantity, 1 - ss((t - t0 - 1.9) / 1.0)),
                                      (355 / 113, f355, C.text, 1 - ss((t - t0 - 0.3) / 0.8))):
            x = (v - c) * sc
            if fade_old > 0 and abs(x) < 7.4:
                g.add(Line(P3(x, y - 0.25), P3(x, y + 0.5), stroke_color=col, stroke_width=3,
                           stroke_opacity=fade_old), lab.copy().move_to(P3(x, y + 0.95)).set_opacity(fade_old))
        for (p, q) in fracs:                                     # fraction ticks, by denominator
            a = ss((t - t_q[q]) / 0.4)
            x = (p / q - c) * sc
            if a > 0 and abs(x) < 7.5:
                h = 0.32 / (1 + 0.25 * (q - 2))
                g.add(Line(P3(x, y - h), P3(x, y + h), stroke_color=C.quantity, stroke_width=1.8, stroke_opacity=0.75 * a))
        if t >= t_d[0]:                                          # midpoints between 3 and 3.25, depth by depth
            for d in range(1, 8):
                td = t_d[d - 1]
                if t < td:
                    break
                n = 2 ** (d - 1)
                h = 0.3 * 0.82 ** d
                for j in range(n):
                    a = ss((t - td - 0.04 * j * 8 / n) / 0.25)
                    if a <= 0:
                        continue
                    v = 3 + (2 * j + 1) * 0.25 / 2 ** d
                    x = (v - c) * sc
                    g.add(Line(P3(x, y - h), P3(x, y + h + 0.4 * (1 - a)), stroke_color=C.quantity, stroke_width=2,
                               stroke_opacity=a))
        for k in range(3):                                       # counting dots, then their mirrors
            a = ss((t - t_dots[k]) / 0.35)
            if a <= 0:
                continue
            x = (k + 1 - c) * sc
            g.add(Dot(P3(x, y + 0.35 * (1 - a)), radius=0.1, color=C.quantity, fill_opacity=a))
            u = ss((t - t_mir[k]) / 0.9)
            if u > 0:
                xm = ((k + 1) * (1 - 2 * u) - c) * sc
                g.add(Dot(P3(xm, y + 0.9 * math.sin(math.pi * u)), radius=0.1, color=C.quantity))
        f = 1 - ss((t - float(s.end) + 0.8) / 0.7)              # the whole line fades before the cut
        if f < 1:
            for mob in g.family_members_with_points():
                mob.set_stroke(opacity=mob.get_stroke_opacity() * f)
                mob.set_fill(opacity=mob.get_fill_opacity() * f)
        return g

    m.redraw(window(line, t0, float(s.end)), during=(t0, float(s.end)))

    # the nested diagram: ℕ inside ℤ inside ℚ (and a dashed ℝ ? at the end)
    def box(cx, cy, w, h, dashed=False):
        r = RoundedRectangle(width=w, height=h, corner_radius=0.2, stroke_color=C.quantity, stroke_width=2.4,
                             fill_color=C.quantity, fill_opacity=0.07).move_to(P3(cx, cy))
        if dashed:
            r = DashedVMobject(RoundedRectangle(width=w, height=h, corner_radius=0.2, stroke_color=C.muted,
                                                stroke_width=2).move_to(P3(cx, cy)), num_dashes=60)
        return r

    Qb, Zb, Nb = box(4.1, 2.15, 4.6, 2.7), box(4.55, 1.9, 3.3, 1.9), box(5.05, 1.775, 1.9, 1.35)
    Nl = VGroup(tex(r"\mathbb{N}", 40, C.quantity).move_to(Nb.get_corner(UL) + P3(0.3, -0.3)),
                tex("1,\\,2,\\,3", 30, C.text).move_to(Nb.get_center() + P3(0.1, -0.15)))
    Zl = VGroup(tex(r"\mathbb{Z}", 40, C.quantity).move_to(Zb.get_corner(UL) + P3(0.3, -0.3)),
                tex("-2", 30, C.text).move_to(Zb.get_corner(DL) + P3(0.42, 0.4)))
    Ql = VGroup(tex(r"\mathbb{Q}", 40, C.quantity).move_to(Qb.get_corner(UL) + P3(0.3, -0.3)),
                tex(r"\tfrac12", 34, C.text).move_to(Qb.get_corner(DL) + P3(0.45, 0.45)))
    keyw = [sans("counting", 26, C.muted), sans("owing", 26, C.muted), sans("sharing", 26, C.muted)]
    for b_, lab, kw, t_ in ((Nb, Nl, keyw[0], t_cnt), (Zb, Zl, keyw[1], t_owe), (Qb, Ql, keyw[2], t_piz)):
        kw.next_to(lab[0], RIGHT, buff=0.18)
        m.play(GrowFromCenter(b_), at=t_ + 0.3, dur=0.6, ease="out_back")
        m.play(FadeIn(lab), FadeIn(kw), at=t_ + 0.6, dur=0.5)
    m.play(Wiggle(Ql[0]), at=t_piz + 2.8, dur=0.8)
    rat = sans("rational", 30, C.quantity).next_to(Qb, DOWN, buff=0.15).align_to(Qb, RIGHT)
    m.play(FadeIn(rat, shift=0.06 * UP), at=t_piz + 2.8, dur=0.5)
    Rb = box(4.1, 2.05, 5.5, 3.6, dashed=True)
    Rl = tex(r"\mathbb{R}\,?", 40, C.muted).move_to(P3(1.9, 0.5))
    m.play(Create(Rb), FadeIn(Rl), at=t_room, dur=1.0)

    # the pizza: eight slices, one pulled out
    pc, pr = P3(-4.7, 2.15), 0.95
    crust = Circle(radius=pr, stroke_color=C.quantity, stroke_width=3, fill_color=tint(C.quantity, 0.16),
                   fill_opacity=1).move_to(pc)
    cuts = VGroup(*(Line(pc, pc + pr * P3(math.cos(a), math.sin(a)), stroke_color=C.quantity, stroke_width=1.6)
                    for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)))
    sl = AnnularSector(inner_radius=0, outer_radius=pr, angle=math.pi / 4, start_angle=0, stroke_color=C.quantity,
                       stroke_width=3, fill_color=tint(C.quantity, 0.3), fill_opacity=1).move_arc_center_to(pc)
    eighth = tex(r"\tfrac18", 34, C.quantity).move_to(pc + P3(1.75, 0.75))
    m.play(GrowFromCenter(crust), at=t_piz - 0.2, dur=0.5, ease="out_back")
    m.play(Create(cuts), at=t_piz + 0.2, dur=0.5)
    top.add(sl, at=t_piz + 0.7)
    top.play(sl.animate.shift(0.4 * P3(math.cos(math.pi / 8), math.sin(math.pi / 8))), at=t_piz + 0.7, dur=0.5)
    top.play(FadeIn(eighth), at=t_piz + 1.0, dur=0.4)
    top.play(FadeOut(VGroup(sl, eighth)), at=t_pack - 0.6, dur=0.5)
    m.play(FadeOut(VGroup(crust, cuts)), at=t_pack - 0.6, dur=0.5)

    # the midpoint rule
    mid = tex(r"\tfrac{p}{q},\ \tfrac{r}{s}\ \Rightarrow\ \tfrac12\!\left(\tfrac{p}{q}+\tfrac{r}{s}\right)", 40,
              C.text).move_to(P3(-3.6, 2.3))
    m.play(Write(mid), at=t_half - 0.2, dur=1.0)
    end_lab = sans("halfway, again and again", 28, C.muted).next_to(mid, DOWN, buff=0.3)
    m.play(FadeIn(end_lab, shift=0.06 * UP), at=t_half + 1.4, dur=0.5)
    out_t = float(s.end) - 0.8
    m.play(FadeOut(VGroup(mid, end_lab, Qb, Zb, Nb, Nl, Zl, Ql, *keyw, rat, Rb, Rl)), at=out_t, dur=0.7)
