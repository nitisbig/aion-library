"""ch2_s01 · Shadows on a line (L2, rail: B_cloud, B_var, then B_dial).

Chapter card (carry-over strip: the centred cloud, dim). The centred cloud returns with its rail boards. A probe
line (C.probe) draws through the centre; every point drops a perpendicular onto it (staggered) and leaves a hollow
shadow dot. The line turns: near the short axis the shadows bunch, near the long axis they spread. On 'record' a
dial board covers the rail and traces the spread of the shadows, u^T C u, against the angle for half a turn (the
other half is the same line). On 'one clear peak' the line turns back to the peak and locks gold (accent glow);
'PC1'. The dial pins into rail slot 3. Every shadow and the whole dial are pure functions of the angle.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, DIAL_BIG, KP, PHI1, STAGE_L2, P3, board, cen_grid, cen_names, chapter_card, dial, dots,
                 drops_shadows, glow_layer, mean_ring, panel, probe_line, rail_cloud, rail_var, sans, slot, smoothstep, udir)


@scene(T.ch2_s01, T.ch2_s02)
def ch2_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_draw, t_drop, t_sh = float(T.ch2_s01_draw_a_line), float(T.ch2_s01_drop_every_point), float(T.ch2_s01_shadows)
    t_turn, t_bunch, t_spread = float(T.ch2_s01_turn_the_line), float(T.ch2_s01_bunch_up), float(T.ch2_s01_spread_far_apart)
    t_rec, t_peak, t_pc1 = float(T.ch2_s01_record), float(T.ch2_s01_one_clear_peak), float(T.ch2_s01_first_principal_comp)
    t_land = t_sh - 1.0                          # 'Those landing spots'
    P = pd.people2()
    Xc = P.Xc

    # ---- card; the carry-over strip is the centred cloud
    on = chapter_card(s, t0, t0 + 2.6, "chapter two", "The Best Direction")
    strip = s.manim(z=20, opacity=on * 0.5)
    strip.add(dots([P3(*(np.array([0.0, -2.35]) + KP * 0.42 * p)) for p in Xc], C.data, r=0.04))

    # ---- the stage and the rail return
    back = keys((t0, 0.0), (t0 + 2.2, 0.0), (t0 + 3.0, 1.0))
    st = s.manim(z=0, opacity=back)
    st.add(board(STAGE_L2), cen_grid(), cen_names(), rail_cloud(), rail_var())
    dm = s.manim(z=2, opacity=back)
    dm.add(dots([P3(*(CEN0 + KP * p)) for p in Xc], C.data), mean_ring(P3(*CEN0)))

    # ---- the line's angle: a pure track
    A0 = PHI1 + 62
    lo, hi = PHI1 + 95, PHI1 + 275
    th = keys((t0, A0), (t_turn - 0.1, A0), (t_bunch + 0.3, PHI1 + 92), (t_spread + 0.5, PHI1 + 172),
              (t_rec - 1.4, PHI1 + 172), (t_rec - 0.05, lo), (t_rec + 5.0, hi, "linear"),
              (t_peak - 0.15, hi), (t_peak + 1.2, PHI1 + 180))
    drawn = keys((t0, 0.0), (t_draw - 0.15, 0.0), (t_draw + 0.8, 1.0))
    drop = keys((t0, 0.0), (t_drop - 0.1, 0.0), (t_drop + 2.3, 1.0, "linear"))
    shadow = keys((t0, 0.0), (t_land, 0.0), (t_land + 0.8, 1.0))
    gold = keys((t0, 0.0), (t_peak + 1.1, 0.0), (t_peak + 1.7, 1.0))

    def line_and_shadows(t):
        d = float(drawn(t))
        if d <= 0.001:
            return VGroup()
        deg = float(th(t))
        g = drops_shadows(CEN0, deg, Xc, drop=float(drop(t)), shadow=float(shadow(t)))
        gl_ = float(gold(t))
        col = interpolate_color(ManimColor(C.probe), ManimColor(C.pc1), gl_)
        ln = probe_line(CEN0, deg, L_cm=32 * d, color=col, width=3.5 + 1.0 * gl_)
        g.add(ln)
        return g

    lm = s.manim(z=1.5)
    lm.redraw(line_and_shadows, during=(t_draw - 0.2, t1))
    gl = glow_layer(s, z=1.6, color=C.pc1, k=0.45, opacity=gold)
    gl.add(probe_line(CEN0, PHI1, color=C.pc1, width=4.5))
    lab = sans("PC1", 30, C.pc1).move_to(P3(*(CEN0 + KP * 30.5 * udir(PHI1) + np.array([-0.45, 0.1]))))
    lm2 = s.manim(z=3)
    lm2.play(FadeIn(lab), at=t_pc1, dur=0.6)

    # ---- the dial: a big board over the rail, tracing; then pinned into slot 3
    pin = keys((t0, 0.0), (t_pc1 + 0.3, 0.0), (t_pc1 + 1.3, 1.0))
    d_on = keys((t0, 0.0), (t_rec - 0.35, 0.0), (t_rec + 0.25, 1.0))
    sb = slot(2)
    small_c = np.array([(sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2])
    big_c = np.array([(DIAL_BIG[0] + DIAL_BIG[2]) / 2, (DIAL_BIG[1] + DIAL_BIG[3]) / 2])

    def dial_board(t):
        a = float(d_on(t))
        if a <= 0.001:
            return VGroup()
        u = float(smoothstep(min(max(pin(t), 0.0), 1.0)))
        box = tuple(DIAL_BIG[i] + (sb[i] - DIAL_BIG[i]) * u for i in range(4))
        c = big_c + (small_c - big_c) * u
        r = 1.75 + (0.85 - 1.75) * u
        deg = float(th(t))
        if t < t_rec:
            tr = None
        elif t < t_rec + 5.0:
            tr = (lo, deg)
        else:
            tr = (lo, hi)
        tip = deg if t >= t_rec else None
        g = VGroup(panel(*box).set_opacity(a) if a < 1 else panel(*box))
        g.add(dial(c, r, tip, tr, a, tip_col=C.pc1 if float(gold(t)) > 0.5 else C.spread))
        return g

    dl = s.manim(z=4)
    dl.redraw(dial_board, during=(t_rec - 0.4, t1))
