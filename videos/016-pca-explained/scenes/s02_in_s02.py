"""in_s02 · Too many columns (L3 split under a strip, then the table).

Left board: one scanned digit (a 3) as an 8x8 grid of grey tiles, its 64 grey levels written in. On 'Write' copies of
the tiles fly, in reading order, into one strip of 64 cells across the top: one digit is 64 numbers. Right board: the
axes grow: two (a page), three (a turning box), then 64 spokes in 3D, turning, unreadable. On 'this table' the
boards clear, the strip settles into its row of the full table (skia), and the table scrolls to its 1,797th row.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import (CELL, DIGIT_I, PITCH, ROW1_Y, TAB_X0, X0, X1, Y0, Canvas, Counter, Glyphs, P3, Table, board,
                 box_c, grey, sans, smoothstep, tex, window)

LBOX, RBOX = (X0, Y0, -0.125, 2.3), (0.125, Y0, X1, 2.3)
LBOX_C = (LBOX[0] - (LBOX[0] + LBOX[2]) / 2, LBOX[1], LBOX[2] - (LBOX[0] + LBOX[2]) / 2, LBOX[3])  # centred first
DX = -(LBOX[0] + LBOX[2]) / 2
TILE = 0.5
STRIP_Y = ROW1_Y
AX = 1.9                                    # axis length on the right board


def strip_xy(j):
    return P3(TAB_X0 + (j + 0.5) * CELL, STRIP_Y)


@scene(T.in_s02, T.in_s03)
def in_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_dig, t_64, t_wr = float(T.in_s02_handwritten_digit), float(T.in_s02_sixty_four_squares), float(T.in_s02_write)
    t_two, t_three, t_nob = float(T.in_s02_two_numbers), float(T.in_s02_three), float(T.in_s02_nobody_can_picture)
    t_tab = float(T.in_s02_this_table)
    lead = 0.15
    X, _ = pd_digits()
    vals = X[DIGIT_I].reshape(8, 8)

    m = s.manim(z=1)
    # ---- left board and the scan
    bl = board(LBOX_C)
    m.play(FadeIn(bl), at=t0 + 0.6, dur=0.8)
    c0 = box_c(LBOX_C) + DOWN * 0.12
    tiles, nums = VGroup(), VGroup()
    G = Glyphs([str(v) for v in range(17)], size=16)
    for r in range(8):
        for c in range(8):
            v = vals[r, c]
            pos = c0 + P3((c - 3.5) * TILE, (3.5 - r) * TILE)
            tiles.add(Square(side_length=TILE, stroke_width=0, fill_color=grey(v), fill_opacity=1.0).move_to(pos))
            nums.add(G(str(int(v)), C.bg if v > 8 else C.muted).move_to(pos))
    frame = Square(side_length=8 * TILE, stroke_color=C.roles["frame"], stroke_width=1.4).move_to(c0)
    m.add(frame, at=t_dig - 0.6)
    m.play(Create(frame), at=t_dig - 0.3, dur=0.6)
    for r in range(8):                                         # scanned in, row by row
        m.play(FadeIn(VGroup(*tiles[8 * r:8 * r + 8])), at=t_dig + 0.09 * r, dur=0.35)
    scan = Line(c0 + P3(-4.3 * TILE, 4 * TILE), c0 + P3(4.3 * TILE, 4 * TILE), stroke_color=C.probe, stroke_width=2.4)
    m.add(scan, at=t_dig - lead)
    m.play(scan.animate.shift(DOWN * 8 * TILE).set_stroke(opacity=0.0), at=t_dig, dur=0.9, ease="linear")
    m.remove(scan, at=t_dig + 1.0)
    grid = VGroup(*[Line(c0 + P3((k - 4) * TILE, -4 * TILE), c0 + P3((k - 4) * TILE, 4 * TILE)) for k in range(1, 8)],
                  *[Line(c0 + P3(-4 * TILE, (k - 4) * TILE), c0 + P3(4 * TILE, (k - 4) * TILE)) for k in range(1, 8)])
    grid.set_stroke(C.roles["frame"], 1.2)
    m.play(Create(grid), at=t_64, dur=0.8)
    for k in range(64):
        m.play(FadeIn(nums[k]), at=t_64 + 0.4 + 0.025 * k, dur=0.3)
    left = VGroup(bl, frame, tiles, nums, grid)
    m.play(left.animate.shift(LEFT * DX), at=t_two - 0.5, dur=1.0)

    # ---- 'Write': copies fly, in reading order, into a 64-cell strip
    fly = VGroup(*[VGroup(tiles[k].copy(), nums[k].copy()) for k in range(64)])
    m.add(fly, at=t_wr - lead)
    m.play(LaggedStart(*[g.animate.scale(CELL / TILE).move_to(strip_xy(k)) for k, g in enumerate(fly)],
                       lag_ratio=0.035), at=t_wr, dur=2.6)
    cells = VGroup(*[Square(side_length=CELL, stroke_color=C.roles["frame"], stroke_width=1.0).move_to(strip_xy(k))
                     for k in range(64)])
    m.play(LaggedStart(*[FadeIn(q) for q in cells], lag_ratio=0.035), at=t_wr, dur=2.6)

    # ---- right board: 2 axes, 3 (turning), then 64
    br = board(RBOX)
    m.play(FadeIn(br), at=t_two - 0.3, dur=0.6)
    oc = box_c(RBOX) + P3(-0.75, -0.75)
    rng = np.random.default_rng(1604)
    dirs = rng.normal(size=(61, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    lens = rng.uniform(0.75, 1.0, 61) * AX
    labs = [tex(f"x_{i}", 32, C.axis) for i in (1, 2, 3)]
    dot3 = np.array([1.25, 0.95, 1.05])
    batches = [4, 8, 16, 32, 64]

    def proj(v, th, ph):
        x, y, z = v[..., 0], v[..., 1], v[..., 2]          # x1 right, x2 up, x3 toward us
        xr = x * np.cos(th) - z * np.sin(th)
        zr = x * np.sin(th) + z * np.cos(th)
        yr = y * np.cos(ph) + zr * np.sin(ph) * 0.55
        xr = xr + zr * 0.0
        return np.stack([xr - 0.42 * zr * np.cos(ph) * (ph > 0), yr], -1)

    def axes(t):
        g1 = smoothstep((t - (t_two - lead)) / 0.6)
        g2 = smoothstep((t - (t_two + 0.25)) / 0.6)
        gd = smoothstep((t - (t_two + 0.9)) / 0.5)
        g3 = smoothstep((t - (t_three - lead)) / 0.8)
        u = max(0.0, t - (t_three - lead))
        th = 0.42 * u * u / (u + 1.2)
        ph = 0.4 * g3
        gs = smoothstep((t - (t_tab - lead)) / 0.6)                # boards clear on 'this table'
        keep = 1 - gs
        g = VGroup()
        E = np.eye(3) * AX
        for i, gi in enumerate((g1, g2, g3)):
            if gi <= 0:
                continue
            q = proj(E[i] * gi, th, ph)
            tip = oc + P3(*q)
            g.add(Arrow(oc, tip, buff=0, stroke_color=C.axis, stroke_width=2.6, tip_length=0.16,
                        max_tip_length_to_length_ratio=0.2).set_opacity(keep))
            g.add(labs[i].copy().move_to(tip + P3(*(q / max(np.linalg.norm(q), 1e-6) * 0.32))).set_opacity(gi * keep))
        # spokes: 64 axes in all (batches on 'nobody can picture'), turning with the box
        n_sp = 0
        for k, b in enumerate(batches):
            if t >= t_nob - lead + 0.32 * k:
                n_sp = b - 3
        if n_sp > 0:
            q = proj(dirs[:n_sp] * lens[:n_sp, None], th, ph)
            for j in range(n_sp):
                a = smoothstep((t - (t_nob - lead + 0.32 * batches.index(next(b for b in batches if b - 3 > j)))) / 0.4)
                g.add(Line(oc, oc + P3(*q[j]), stroke_color=C.axis, stroke_width=1.5, stroke_opacity=0.6 * a * keep))
        if gd > 0:                                                    # one data point, with its drop lines
            dv = np.array([dot3[0], dot3[1], dot3[2] * g3]) * 1.0
            pd_ = oc + P3(*proj(dv, th, ph))
            star = smoothstep((t - (t_nob - lead)) / 0.6)
            o = gd * keep * (1 - star)
            g.add(DashedLine(pd_, oc + P3(*proj(np.array([dv[0], 0, dv[2]]), th, ph)), stroke_color=C.data,
                             stroke_width=1.6, dash_length=0.07, stroke_opacity=0.7 * o))
            g.add(Dot(pd_, radius=0.08, color=C.data, fill_opacity=o))
        return g

    top = s.manim(z=2)
    top.redraw(window(axes, t_two - lead, t_tab + 0.6), during=(t_two - lead, t_tab + 0.65))
    eq = tex(r"\mathbf{x} \in \mathbb{R}^{64}", 44).move_to(box_c(RBOX) + P3(1.6, -2.15))
    m.play(Write(eq), at=t_nob + 1.3, dur=0.9)

    # ---- 'this table': boards clear, the strip settles into its row, the table scrolls to 1,797
    for mob in (bl, br, frame, tiles, nums, grid, eq):
        m.play(FadeOut(mob), at=t_tab, dur=0.6)
    row_y = ROW1_Y - DIGIT_I * PITCH
    drop = DOWN * (STRIP_Y - row_y)                 # .animate targets are fixed at build time: give absolute ones
    m.play(*[g.animate.scale(CELL / TILE).move_to(strip_xy(k) + drop) for k, g in enumerate(fly)],
           cells.animate.shift(drop), at=t_tab + 0.1, dur=0.6)
    m.play(FadeOut(VGroup(fly, cells)), at=t_tab + 0.75, dur=0.3, lead=0)

    cv = Canvas((X0, -4.0, X1, 4.0), px=s.comp.size[1] / 8)
    tab = Table(cv)
    n_vis = (ROW1_Y - (-3.29)) / PITCH
    top_end = tab.n - n_vis
    a_s, d_s = t_tab + 0.9, t1 - (t_tab + 0.9) - 0.6

    def top_of(t):
        return top_end * float(smoothstep((t - a_s) / d_s) ** 1.0) if t > a_s else 0.0

    def rows_alpha(i, t):
        if i == DIGIT_I:
            return 1.0 if t >= t_tab + 0.75 else 0.0
        d = 0.04 * abs(i - DIGIT_I) if i < 40 else 0.0               # the first screenful fans out from our row
        return float(smoothstep((t - (t_tab + 0.15 + d)) / 0.35))

    last = {}

    def draw(t):
        k = (round(top_of(t), 3), round(min(t, t_tab + 2.0), 2))
        if last.get("k") != k:
            c = cv.begin()
            tab.draw(c, top_of(t), fade_rows=lambda i: rows_alpha(i, t))
            last.update(k=k, a=cv.array())
        return last["a"]

    s.add(FramesLayer(draw, z=0, during=[(t_tab, t1)], **cv.layer_kw()))
    cnt = Counter(30)
    rows_word = sans("rows", 26, C.muted)

    def counter(t):
        n = min(tab.n, int(math.floor(top_of(t) + n_vis)) + 1)
        num = cnt.number(n, right=-TAB_X0 - 0.95, base=STRIP_Y + 0.27)
        return VGroup(num, rows_word.copy().next_to(num, RIGHT, buff=0.15, aligned_edge=DOWN))

    top.redraw(counter, during=(t_tab + 0.3, t1))


def pd_digits():
    import pcadata
    return pcadata.digits()
