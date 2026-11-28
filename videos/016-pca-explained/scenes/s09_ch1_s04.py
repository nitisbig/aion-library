"""ch1_s04 · More columns (L3 split).

The rail clears and the stage folds into the left board, keeping the 2D cloud. Right board: the same cloud, face
on; on 'shoulder width' the view tips back so the height/arm-span plane becomes a floor and a third axis grows up
out of it; on 'three dimensions' every dot rises to its shoulder width (a thin drop line to the floor under each).
The view orbits; on 'turn it' it comes round edge-on and the cloud shows its shape: a long, thin pebble.
On 'digits' the right board changes to the digit 3; on 'Sixty-four shades' its tiles unroll into a column vector,
and a 64-spoke star turns beside it ('sixty-four directions'). On "can't turn" the star stops and greys out.
Everything is computed: people3() for the cloud, the digit from the UCI set.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (CEN0, DIGIT_I, KP, LEFT_L3, RIGHT_L3, STAGE_IN, STAGE_L2, P3, Aura, bead, bead_layer, box_c, brackets,
                 card, cen_names, glow_layer, grey, mean_ring, plane_grid, rail_cloud, rail_var, sans, smoothstep, tex)

RC = np.array([3.26, -0.15])                    # the 3D view's centre on the right board
STAR_C = np.array([1.95, 0.35])
COL_X, COL_TOP, BAR_H, BAR_W = 4.75, 2.62, 0.08, 0.42


def rx(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])


def rz(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])


def lerp_box(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(4))


@scene(T.ch1_s04, T.ch2_s01)
def ch1_s04(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_sh, t_3d, t_turn = float(T.ch1_s04_shoulder_width), float(T.ch1_s04_three_dimensions), float(T.ch1_s04_turn_it)
    t_dig, t_64, t_cant = float(T.ch1_s04_digits), float(T.ch1_s04_sixty_four_shades), float(T.ch1_s04_can_t_turn)
    t_dirs = t_64 + 3.9                          # 'sixty-four directions'
    end = keys((t0, 1.0), (t1 - 0.75, 1.0), (t1 - 0.05, 0.0))
    P = pd.people2()
    Q = pd.people3()
    Xc, X3 = P.Xc, Q.Xc

    # ---- the rail clears; the stage folds into the left board
    rail = s.manim(z=0, opacity=keys((t0, 1.0), (t0 + 0.15, 1.0), (t0 + 0.75, 0.0)))
    rail.add(rail_cloud(pr=True), rail_var(pr=True))
    fold = keys((t0, 0.0), (t0 + 0.4, 0.0), (t0 + 1.6, 1.0))
    st_in = (STAGE_L2[0], STAGE_L2[1], STAGE_L2[2], STAGE_L2[3])
    c_left = np.array(box_c(LEFT_L3)[:2]) + np.array([0.15, -0.1])

    def left(t):
        u = float(smoothstep(min(max(fold(t), 0.0), 1.0)))
        bx = lerp_box(st_in, LEFT_L3, u)
        c0 = CEN0 + (c_left - CEN0) * u
        inner = (bx[0] + 0.05, bx[1] + 0.05, bx[2] - 0.05, bx[3] - 0.05)
        return VGroup(card(bx), plane_grid(c0, KP * 10, inner), cen_names(c0, 26.0 - 7.0 * u, pr=True))

    def c_left0(t):
        u = float(smoothstep(min(max(fold(t), 0.0), 1.0)))
        return CEN0 + (c_left - CEN0) * u

    def left_pts(t):
        c0 = c_left0(t)
        return VGroup(*[bead(P3(*(c0 + KP * p))) for p in Xc])

    def left_ring(t):
        return mean_ring(P3(*c_left0(t)), pr=True)

    lm = s.manim(z=0.4, opacity=end)
    lm.redraw(left, during=(t0, t1))
    lb = bead_layer(s, z=1, opacity=end)
    lb.redraw(left_pts, during=(t0, t1))
    lr = glow_layer(s, z=1.1, color=C.mean, k=0.2, opacity=end)
    lr.redraw(left_ring, during=(t0, t1))
    au = Aura((STAGE_IN[0], LEFT_L3[1] + 0.05, STAGE_IN[2], LEFT_L3[3] - 0.05))
    s.add(FramesLayer(lambda t: au.frame(c_left0(t) + KP * Xc, 1.0, 0.35), z=0.5, opacity=end, during=[(t0, t1)],
                      **au.layer_kw()))

    # ---- right board: the 3D view (a pure function of the view angles)
    rb = s.manim(z=1, opacity=end)
    rb.play(FadeIn(card(RIGHT_L3)), at=t0 + 1.0, dur=0.7)
    el = keys((t0, 0.0), (t_sh - 0.2, 0.0), (t_sh + 1.9, -58.0), (t_turn - 0.2, -58.0), (t_turn + 1.9, -86.0))
    az = keys((t0, 0.0), (t_sh + 1.7, 0.0), (t_turn - 0.2, -27.0, "linear"), (t_turn + 1.9, -45.0), (t_dig + 0.6, -50.0))
    rise = keys((t0, 0.0), (t_3d - 0.1, 0.0), (t_3d + 1.5, 1.0))
    s_ax = keys((t0, 0.0), (t_sh - 0.1, 0.0), (t_sh + 1.4, 1.0))
    v_on = keys((t0, 0.0), (t0 + 1.3, 0.0), (t0 + 2.0, 1.0), (t_dig - 0.1, 1.0), (t_dig + 0.6, 0.0))

    def view(t):
        a = float(v_on(t))
        if a <= 0.001:
            return VGroup()
        R = rx(math.radians(float(el(t)))) @ rz(math.radians(float(az(t))))
        k = float(rise(t))
        g = VGroup()

        def scr(p):
            q = R @ (np.asarray(p, float) * KP)
            return P3(RC[0] + q[0], RC[1] + q[1]), q[2]

        for v in range(-20, 21, 10):                      # the floor grid (height x arm span, 10 cm)
            for a_, b_ in (((v, -25, 0), (v, 25, 0)), ((-22, v, 0), (-22 + 44, v, 0))):
                (p0, _), (p1, _) = scr(a_), scr(b_)
                g.add(Line(p0, p1, stroke_color=C.plane, stroke_width=1.2, stroke_opacity=a))
        for d, L in (((1, 0, 0), 24), ((0, 1, 0), 26)):
            (p0, _), (p1, _) = scr(np.multiply(d, -L)), scr(np.multiply(d, L))
            g.add(Line(p0, p1, stroke_color=C.plane_axis, stroke_width=2.0, stroke_opacity=a))
        sl = float(s_ax(t)) * 15
        if sl > 0.05:
            (p0, _), (p1, _) = scr((0, 0, -sl)), scr((0, 0, sl))
            g.add(Line(p0, p1, stroke_color=C.plane_axis, stroke_width=2.0, stroke_opacity=a))
            lab = sans("shoulder", 24, C.muted).set_opacity(a * min(1.0, sl / 15) * min(1.0, max(0.0, (abs(float(el(t))) - 48.0) / 10.0))).move_to(p1 + P3(0, 0.28))
            g.add(lab)
        pts = [(scr((h, ar, sw * k)), scr((h, ar, 0))[0]) for h, ar, sw in X3]
        order = np.argsort([dp for (_, dp), _ in pts])[::-1]           # far first
        zs = np.array([dp for (_, dp), _ in pts])
        zn = (zs - zs.min()) / max(np.ptp(zs), 1e-6)
        for i in order:
            (p, _), f = pts[i]
            if k > 0.02:
                g.add(Line(f, p, stroke_color=C.data, stroke_width=1.2, stroke_opacity=0.35 * a))
            near = 1.0 - zn[i]
            g.add(bead(p, r=0.042 + 0.022 * near, a=a * (0.5 + 0.5 * near)))
        return g

    vm = bead_layer(s, z=2, k=0.22, opacity=end)
    vm.redraw(view, during=(t0 + 1.2, t_dig + 0.7))
    r3 = tex(r"\mathbf{x}\in\mathbb{R}^{3}", 42).move_to(P3(RIGHT_L3[2] - 0.95, RIGHT_L3[1] + 0.45))
    rb.play(FadeIn(r3), at=t_3d + 0.4, dur=0.7)
    rb.play(FadeOut(r3), at=t_dig - 0.1, dur=0.6)

    # ---- the digit: tiles, then a column vector of 64 shades
    Xd, _ = pd.digits()
    vals = Xd[DIGIT_I]
    TILE = 0.33
    cells = VGroup()
    for r in range(8):
        for c in range(8):
            cells.add(Square(side_length=TILE, stroke_width=0, fill_color=grey(vals[8 * r + c]), fill_opacity=1.0)
                      .move_to(P3(STAR_C[0] + (c - 3.5) * TILE, STAR_C[1] + (3.5 - r) * TILE)))
    frame = Square(side_length=8 * TILE + 0.06, stroke_width=0, fill_color=C.card, fill_opacity=0.0).move_to(P3(*STAR_C))
    dg = s.manim(z=2, opacity=end)
    dg.play(FadeIn(cells), FadeIn(frame), at=t_dig + 0.2, dur=0.8)
    bars = [Rectangle(width=BAR_W, height=BAR_H, stroke_color=C.card, stroke_width=0.8,
                      fill_color=grey(vals[j]), fill_opacity=1.0)
            .move_to(P3(COL_X, COL_TOP - (j + 0.5) * BAR_H)) for j in range(64)]
    dg.play(FadeOut(frame), at=t_64 - 0.1, dur=0.5)
    dg.play(LaggedStart(*[ReplacementTransform(cells[j], bars[j]) for j in range(64)], lag_ratio=0.04),
            at=t_64, dur=3.2)
    colH = 64 * BAR_H
    br = brackets(colH + 0.16, BAR_W + 0.14, color=C.text).move_to(P3(COL_X, COL_TOP - colH / 2))
    col_fr = Rectangle(width=BAR_W, height=colH, stroke_width=0, fill_opacity=0.0).move_to(
        P3(COL_X, COL_TOP - colH / 2))
    dg.play(FadeIn(col_fr), at=t_64, dur=0.5)
    dg.play(FadeIn(br), at=t_64 + 2.9, dur=0.6)

    # ---- the 64-spoke star where the tiles were: turns, then (can't turn) stops and greys out
    rng = np.random.default_rng(1604)
    dirs = rng.normal(size=(64, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    lens = rng.uniform(0.8, 1.0, 64) * 1.55
    grow = keys((t0, 0.0), (t_dirs - 0.3, 0.0), (t_dirs + 1.4, 1.0))
    spin = keys((t0, 0.0), (t_dirs - 0.3, 0.0), (t_cant + 0.5, 1.0, "linear"), (t_cant + 1.4, 1.12, "out_cubic"))
    grey_out = keys((t0, 0.0), (t_cant + 0.4, 0.0), (t_cant + 1.6, 1.0))

    def star(t):
        gr = float(grow(t))
        if gr <= 0.001:
            return VGroup()
        ang = float(spin(t)) * 1.6
        R = rx(0.5 * ang + 0.3) @ rz(ang)
        q = (dirs * lens[:, None]) @ R.T
        gy = float(grey_out(t))
        g = VGroup()
        n_show = int(round(64 * gr))
        for j in range(n_show):
            p = P3(STAR_C[0] + q[j, 0], STAR_C[1] + q[j, 1])
            g.add(Line(P3(*STAR_C), p, stroke_color=C.axis if gy < 0.5 else C.muted, stroke_width=1.4,
                       stroke_opacity=(0.8 - 0.55 * gy) * (0.55 + 0.45 * (q[j, 2] / 1.55 + 1) / 2)))
        return g

    sm = s.manim(z=1.5, opacity=end)
    sm.redraw(star, during=(t_dirs - 0.4, t1))
    r64 = tex(r"\mathbf{x}\in\mathbb{R}^{64}", 42).move_to(P3(STAR_C[0], RIGHT_L3[1] + 0.45))
    dg.play(FadeIn(r64), at=t_dirs + 0.3, dur=0.7)
