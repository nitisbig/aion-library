"""ch4_s03 · Loops that snag.

The row of equal loops from ch4_s02 clears; the circle slides to the middle as the rubber band. On 'Holes' the key word
comes up. On 'disk' a filled disk appears on the left and a loop drawn on it shrinks to a point. On 'Wrap' the band
widens into a flat ring; a loop wrapped once round it tightens, stops against the hole, and keeps snagging however it
is stretched. On 'donut' a shaded torus (raymarched, shaders/solid.frag) turns slowly on the right; on 'two different'
a loop round the tube and a loop round the hole each try to shrink and catch. On 'tell shapes apart' the counts of
loops that snag (0, 1, 2) land under the three shapes.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import (P3, TOR_R, TOR_r, band, band_theta, caps, lin, r_blob, r_poly, r_star, surface_curve, tex, torus_xyz,
                 window)

ROW_Y, ROW_R = -2.75, 0.48
ROW_X = (-5.0, -2.5, 0.0, 2.5, 5.0)
BR = 1.8
DC, DR = P3(-4.6, 0.2), 1.5                    # the disk
AC, A_IN, A_OUT = P3(0.0, 0.2), 1.0, 1.6        # the flat band (an annulus)
TC, TS = P3(4.5, 0.2), 1.6                      # the torus: centre and world units per object unit
TILT = -0.85


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def loop_pts(c, r):
    th = band_theta()
    return [np.asarray(c, float) + np.array([ri * math.cos(t), ri * math.sin(t), 0.0]) for ri, t in zip(r, th)]


def loop(c, r, color, width=5.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    v.set_points_as_corners(loop_pts(c, r))
    return v


@scene(T.ch4_s03, T.ch4_s04)
def ch4_s03(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_ho, t_di, t_wr = float(T.ch4_s03_holes), float(T.ch4_s03_disk), float(T.ch4_s03_wrap)
    t_do, t_two, t_tell = float(T.ch4_s03_donut), float(T.ch4_s03_two_different), float(T.ch4_s03_tell_shapes_apart)
    S, L = C.space, C.circle                     # the surfaces, and the loops drawn on them
    th = band_theta()
    out_t = t1 - 0.75

    # where ch4_s02 left off: the row of equal loops
    shapes = [np.full_like(th, BR), r_poly(4, BR), r_poly(3, BR, -math.pi / 2), r_blob(BR), r_star(BR)]
    row = VGroup(*(band(r * (ROW_R / BR), P3(x, ROW_Y), width=6) for x, r in zip(ROW_X, shapes)))
    eqs = VGroup(*(tex("=", 48, C.text).move_to(P3(0.5 * (a + b), ROW_Y)) for a, b in zip(ROW_X, ROW_X[1:])))
    same = caps("same circle", 48, S).move_to(P3(0, -1.45))
    m.add(row, eqs, same)
    m.play(FadeOut(eqs), FadeOut(same), at=t0 + 0.1, dur=0.5)
    m.play(*(FadeOut(x_, scale=0.5) for x_ in row[1:]), at=t0 + 0.2, dur=0.6)
    mid = (A_IN + A_OUT) / 2
    ring = band(np.full_like(th, mid), AC)
    m.play(Transform(row[0], ring), at=t0 + 0.5, dur=1.3, ease="easy_ease")

    # 'Holes'
    holes = caps("holes", 60, S).move_to(P3(0, 3.1))
    m.play(FadeIn(holes, shift=0.1 * DOWN), at=t_ho, dur=0.6)

    # 'disk': a loop on a disk shrinks to a point
    disk = Circle(radius=DR, stroke_color=S, stroke_width=4, fill_color=S, fill_opacity=0.15).move_to(DC)
    m.play(GrowFromCenter(disk), at=t_di - 0.1, dur=0.6, ease="out_back")
    lp0 = Circle(radius=1.05, stroke_color=L, stroke_width=5).move_to(DC + P3(0.1, 0.05))
    a_c, a_s, a_e = t_di + 0.45, t_di + 1.1, t_di + 2.6
    top.play(Create(lp0), at=a_c, dur=0.6, ease="easy_ease")
    top.remove(lp0, at=a_s)
    pdot = Dot(DC + P3(0.3, -0.1), radius=0.08, color=L)

    def shrink(t):
        u = ss((t - a_s) / (a_e - a_s))
        c = DC + P3(0.1, 0.05) + u * P3(0.2, -0.15)
        r = 1.05 * (1 - u) * (1 + 0.1 * u * (1 - u) * 4 * np.sin(3 * th + 2.5 * (t - a_s)))
        return loop(c, np.maximum(r, 0.0), L)

    top.redraw(window(shrink, a_s, a_e), during=(a_s, a_e + 0.05))
    top.add(pdot, at=a_e)
    top.play(Flash(pdot, color=L, line_length=0.16, flash_radius=0.22, num_lines=8), at=a_e, dur=0.5)

    # 'Wrap': the band widens into a flat ring; a loop round it tightens and snags on the hole
    ann = Annulus(inner_radius=A_IN, outer_radius=A_OUT, fill_color=S, fill_opacity=0.15, stroke_color=S,
                  stroke_width=4).move_to(AC)
    m.play(FadeOut(row[0]), FadeIn(ann, scale=0.96), at=t_wr - 0.1, dur=0.6)
    hole_c = AC + P3(0, 0)
    b_c, b_s, b_t, b_e = t_wr + 0.55, t_wr + 1.15, t_wr + 2.4, out_t + 0.6
    lp1 = Circle(radius=1.42, stroke_color=L, stroke_width=5).move_to(AC).rotate(math.pi / 2)
    top.play(Create(lp1), at=b_c, dur=0.6, ease="easy_ease")
    top.remove(lp1, at=b_s)

    def snag(t):
        u = ss((t - b_s) / (b_t - b_s))
        r0 = 1.42 + (A_IN + 0.06 - 1.42) * u                        # tightens to just outside the hole
        if t > b_t:                                                  # a small recoil on catching
            r0 += 0.05 * math.exp(-5 * (t - b_t)) * math.sin(16 * (t - b_t))
        k = ss((t - b_t - 0.6) / 0.8)                                # then stretched about, never past the hole
        r = r0 + k * 0.32 * (0.5 + 0.5 * np.sin(2 * th + 1.3 * (t - b_t)))
        f = 1 - ss((t - out_t) / 0.6)
        return loop(hole_c, r, L, opacity=f)

    top.redraw(window(snag, b_s, b_e), during=(b_s, b_e + 0.05))
    hl = Circle(radius=A_IN, stroke_color=L, stroke_width=3, stroke_opacity=0.0).move_to(AC)
    top.add(hl, at=b_t - 0.05)
    top.play(hl.animate.set_stroke(opacity=0.9), at=b_t - 0.05, dur=0.15)
    top.play(hl.animate.set_stroke(opacity=0.0), at=b_t + 0.3, dur=0.6)
    top.remove(hl, at=b_t + 1.0)

    # 'donut': a shaded torus
    s.shader("solid.frag", z=1, u_c=(float(TC[0]), float(TC[1])), u_size=TS, u_tilt=TILT, u_spin=0.0, u_morph=1.0,
             u_amt=fade(t_do + 0.1, dur=0.7, out=t1 - 0.6, out_dur=0.6), u_R=TOR_R, u_r=TOR_r, u_col=lin(S))

    def spin_at(t):                                 # spinning a torus about its axis looks the same: hold it
        return 0.0

    # 'two different': a loop round the tube, then one round the hole
    n = 97
    w = np.linspace(0, 2 * math.pi, n)
    c_m, c_m1, c_p, c_p1 = t_two + 0.1, t_two + 1.3, t_two + 1.6, t_two + 3.0

    def tube(t):                                    # a meridian loop: starts loose, pulls tight onto the tube
        u = ss((t - c_m) / (c_m1 - c_m))
        g = 1.55 - 0.56 * u
        if t > c_m1:
            g += 0.05 * math.exp(-5 * (t - c_m1)) * math.sin(16 * (t - c_m1))
        uu = -math.pi / 2 + 0.55                     # front right
        q = torus_xyz(uu, w, grow=g)
        nrm = np.stack([np.cos(w) * math.cos(uu), np.cos(w) * math.sin(uu), np.sin(w)], -1)
        f = ss((t - c_m) / 0.3) * (1 - ss((t - out_t) / 0.6))
        return surface_curve(q, nrm, TC, TS, TILT, spin_at(t), L, width=5, back=0.0).set_stroke(opacity=f)

    def hole(t):                                    # a loop round the hole: slides in over the top and catches
        u = ss((t - c_p) / (c_p1 - c_p))
        v = 0.22 * math.pi + 0.5 * math.pi * u
        if t > c_p1:
            v += 0.05 * math.exp(-5 * (t - c_p1)) * math.sin(16 * (t - c_p1))
        q = torus_xyz(w, v, grow=1.04)
        nrm = np.stack([math.cos(v) * np.cos(w), math.cos(v) * np.sin(w), np.full_like(w, math.sin(v))], -1)
        f = ss((t - c_p) / 0.3) * (1 - ss((t - out_t) / 0.6))
        return surface_curve(q, nrm, TC, TS, TILT, spin_at(t), L, width=5, back=0.0).set_stroke(opacity=f)

    top.redraw(window(lambda t: VGroup(tube(t), hole(t) if t >= c_p else VGroup()), c_m, out_t + 0.6),
               during=(c_m, out_t + 0.65))

    # 'tell shapes apart': how many loops snag
    counts = VGroup(*(tex(str(k), 64, L).move_to(P3(x, -2.45)) for k, x in zip((0, 1, 2), (DC[0], AC[0], TC[0]))))
    m.play(LaggedStart(*(FadeIn(c_, shift=0.1 * UP) for c_ in counts), lag_ratio=0.35), at=t_tell - 1.6, dur=1.2)

    # out
    m.play(FadeOut(VGroup(disk, ann, holes, counts)), at=out_t, dur=0.6)
    top.play(FadeOut(pdot), at=out_t, dur=0.6)
