"""ch2_s04 · The second direction (L2, rail: B_cloud, B_varu, B_dial).

PC1 stays gold. A probe line searches again, swinging round until it stands at a right angle to PC1 (a right-angle
mark), and becomes PC2 (C.pc2); its shadows show the spread PC1 missed. On 'Turn the grid' the Classic grid turns
until its lines run along PC1 and PC2 (a pure function of the angle); one person gets their new coordinates (drops
onto both axes). On 'overall size' a small and a large person stand at the two ends of PC1 ('size'); on 'long or
short' a short-armed and a long-armed person (same height) at the ends of PC2 ('proportion'). Everything fades
for the chapter three card.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, KP, PHI1, STAGE_IN, STAGE_L2, P3, backed, board, cen_names, dial_pinned, drops_shadows,
                 glow_layer, grid_lines, mean_ring, people_v, person_icon, probe_line, rail_cloud, rail_obj, sans,
                 udir)


def at(cm):
    return CEN0 + KP * np.asarray(cm, float)


@scene(T.ch2_s04, T.ch3_s01)
def ch2_s04(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_ra, t_pc2, t_grid = float(T.ch2_s04_right_angle), float(T.ch2_s04_second_principal_com), float(T.ch2_s04_turn_the_grid)
    t_size, t_arms = float(T.ch2_s04_overall_size), float(T.ch2_s04_long_or_short)
    t_look = t_ra - 3.7                          # 'Look for the best direction again'
    t_picks = t_pc2 + 1.6                        # 'It picks up the spread'
    t_coords = t_grid + 2.8                      # 'every person gets new coordinates'
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))
    P, V = people_v()
    Xc = P.Xc
    u1, u2 = V[:, 0], V[:, 1]
    PHI2 = PHI1 + 90

    # ---- the rail, the board; the grid turns to the PC axes
    rl = s.manim(z=0, opacity=end)
    rl.add(rail_cloud(), rail_obj(), dial_pinned(), board(STAGE_L2))
    turn = keys((t0, 0.0), (t_grid - 0.1, 0.0), (t_grid + 2.2, 1.0))

    def grid(t):
        a = math.radians(PHI1) * float(turn(t))
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        return grid_lines(R, CEN0, KP * 10, STAGE_IN, n=14, minor=2)

    gm = s.manim(z=0.2, opacity=end)
    gm.redraw(grid, during=(t0, t1))
    names = s.manim(z=0.3, opacity=end * keys((t0, 1.0), (t_grid - 0.4, 1.0), (t_grid + 0.2, 0.0)))
    names.add(cen_names())

    # ---- PC1 (gold, glowing), the search for PC2, PC2
    th = keys((t0, PHI1 + 30), (t_look - 0.1, PHI1 + 30), (t_ra - 0.2, PHI2 + 12), (t_ra + 0.5, PHI2))
    probe_on = keys((t0, 0.0), (t_look - 0.4, 0.0), (t_look + 0.2, 1.0), (t_pc2 + 0.6, 1.0), (t_pc2 + 1.0, 0.0))
    teal = keys((t0, 0.0), (t_pc2 - 0.1, 0.0), (t_pc2 + 0.7, 1.0))
    sh2 = keys((t0, 0.0), (t_picks - 0.1, 0.0), (t_picks + 1.2, 1.0), (t_grid - 0.6, 1.0), (t_grid, 0.0))

    def lines(t):
        g = VGroup()
        s2 = float(sh2(t))
        if s2 > 0.001:
            g.add(drops_shadows(CEN0, PHI2, Xc, 1.0, s2, drop_op=0.45 * s2))
        g.add(*[bead(P3(*at(p))) for p in Xc], mean_ring(P3(*CEN0)))
        pa = float(probe_on(t))
        if pa > 0.001:
            g.add(probe_line(CEN0, float(th(t)), opacity=pa))
        tl = float(teal(t))
        if tl > 0.001:
            g.add(probe_line(CEN0, PHI2, L_cm=26 * tl, color=C.pc2, width=4))
        g.add(probe_line(CEN0, PHI1, color=C.pc1, width=4.5))
        return g

    lm = s.manim(z=2, opacity=end)
    lm.redraw(lines, during=(t0, t1))
    gl = glow_layer(s, z=1.9, color=C.pc1, k=0.45, opacity=end)
    gl.add(probe_line(CEN0, PHI1, color=C.pc1, width=4.5))

    m = s.manim(z=3, opacity=end)
    mark = RightAngle(Line(P3(*CEN0), P3(*at(10 * u1))), Line(P3(*CEN0), P3(*at(10 * u2))), length=0.22,
                      stroke_color=C.text, stroke_width=2)
    m.play(Create(mark), at=t_ra, dur=0.6)
    l1 = sans("PC1", 30, C.pc1).move_to(P3(*(at(30.5 * u1) + np.array([-0.45, 0.1]))))
    l2 = sans("PC2", 30, C.pc2).move_to(P3(*(at(26 * u2) + np.array([0.1, 0.32]))))
    m.add(l1)
    m.play(FadeIn(l2), at=t_pc2 + 0.5, dur=0.6)

    # ---- one person's new coordinates: drops onto both axes
    I = 36
    x = Xc[I]
    z1, z2 = float(x @ u1), float(x @ u2)
    co = VGroup(DashedLine(P3(*at(x)), P3(*at(z1 * u1)), stroke_color=C.pc1, stroke_width=2.2, dash_length=0.08),
                DashedLine(P3(*at(x)), P3(*at(z2 * u2)), stroke_color=C.pc2, stroke_width=2.2, dash_length=0.08),
                bead(P3(*at(x)), r=0.085))
    m.play(Create(co), at=t_coords, dur=0.8)
    m.play(FadeOut(co), at=t_size - 1.6, dur=0.6)

    # ---- what the new axes mean: size (PC1), proportion (PC2)
    off = -1.0 * u2
    big_c, small_c = at(30 * u1) + off - np.array([0.0, 0.45]), at(-22 * u1) - 0.85 * u2 - np.array([0.0, 0.3])
    fig_size = VGroup(person_icon(*big_c, H=0.95), person_icon(*small_c, H=0.6))
    tag1 = backed(sans("size", 28, C.pc1)).move_to(P3(*(at(22 * u1) + 0.55 * u2)))
    m.play(LaggedStart(FadeIn(fig_size[1], shift=UP * 0.1), FadeIn(fig_size[0], shift=UP * 0.1), lag_ratio=0.4),
           at=t_size - 0.3, dur=1.0)
    m.play(FadeIn(tag1), at=t_size + 0.3, dur=0.6)
    long_c, short_c = at(17 * u2) + 0.65 * u1 - np.array([0.0, 0.38]), at(-17 * u2) + 0.65 * u1 - np.array([0.0, 0.38])
    fig_arms = VGroup(person_icon(*short_c, H=0.75, span=0.72), person_icon(*long_c, H=0.75, span=1.3))
    tag2 = backed(sans("proportion", 28, C.pc2)).move_to(P3(*(at(-19 * u2) - 0.75 * u1)))
    m.play(LaggedStart(FadeIn(fig_arms[0], shift=UP * 0.1), FadeIn(fig_arms[1], shift=UP * 0.1), lag_ratio=0.4),
           at=t_arms - 0.3, dur=1.0)
    m.play(FadeIn(tag2), at=t_arms + 0.4, dur=0.6)
