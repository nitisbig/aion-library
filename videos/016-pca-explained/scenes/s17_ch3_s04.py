"""ch3_s04 · A bigger C (L3: the digit | its covariance; at the end B_heat pins into rail slot 2).

The rail steps back. Left board: the video's digit as 8x8 grey tiles. Right board: the digits' real 64x64
covariance builds row by row as a diverging heatmap (C.spread together, C.data opposite), symmetric about the
diagonal. On 'two pixels' two neighbouring pixels (27, 28) light on the tile, and crosshairs find their entry (and
its mirror). On 'Neighbouring pixels' row 27 is outlined and its 64 values tint the tile: the pen stroke around the
pixel lights up. On 'blank in every scan' pixels 0, 32, 39 are marked on the tile and their empty rows and columns
outlined (C.muted). On 'best view' the heatmap shrinks into rail slot 2 while B_C and B_varu come back.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (DIGIT_I, P3, X0, X1, Y0, Y1, Canvas, backed, board, cov_heat, grey_tiles, rail_c, rail_obj, slot,
                 smoothstep)

LB = (X0, Y0, -0.05, Y1)                         # left board: the digit
RB = (0.2, Y0, X1, Y1)                           # right board: the covariance
TC = np.array([-3.22, -0.25])                    # tile centre
TS = 4.0                                         # tile size
HC = np.array([3.30, -0.25])                     # heatmap centre
HS = 5.0                                         # heatmap size
PAIR = (27, 28)
BLANK = (0, 32, 39)


def hbox(c, s):
    return (c[0] - s / 2, c[1] - s / 2, c[0] + s / 2, c[1] + s / 2)


def tile_xy(i):
    r, c = divmod(i, 8)
    return TC + TS / 8 * np.array([c - 3.5, 3.5 - r])


def heat_xy(i, j, box=None):
    b = box or hbox(HC, HS)
    h = (b[2] - b[0]) / 64
    return np.array([b[0] + (j + 0.5) * h, b[3] - (i + 0.5) * h])


@scene(T.ch3_s04, T.ch4_s01)
def ch3_s04(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t64, t_two = float(T.ch3_s04_sixty_four_rows), float(T.ch3_s04_two_pixels)
    t_nb, t_blank, t_best = float(T.ch3_s04_neighbouring_pixels), float(T.ch3_s04_blank_in_every_scan), float(T.ch3_s04_best_view)
    X, _ = pd.digits()
    Cm = pd.digits_pca().C
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))

    # ---- the rail steps back; the two boards come in (and the rail returns on 'best view')
    rail = keys((t0, 1.0), (t0 + 0.2, 1.0), (t0 + 0.9, 0.0), (t_best + 0.4, 0.0), (t_best + 1.2, 1.0))
    rl = s.manim(z=0, opacity=rail * end)
    rl.add(rail_c(), rail_obj())
    on = keys((t0, 0.0), (t0 + 0.5, 0.0), (t0 + 1.3, 1.0), (t_best - 0.1, 1.0), (t_best + 0.9, 0.0))
    bd = s.manim(z=0, opacity=on)
    bd.add(board(LB), board(RB))
    eq = backed(Eqn(r"C\in\mathbb{R}^{64\times 64}", colors={r"C": C.spread}, size=40), 0.06).move_to(P3(HC[0], 2.85))
    bd.play(Write(eq), at=t64 - 0.4, dur=1.0)

    # ---- the digit
    cells, fr = grey_tiles(X[DIGIT_I], TS)
    tile = VGroup(cells, fr).move_to(P3(*TC))
    bd.play(FadeIn(tile), at=t0 + 0.9, dur=0.8)

    # ---- the heatmap: builds row by row, then shrinks into rail slot 2
    rows = keys((t0, 0.0), (t64 - 0.3, 0.0), (t64 + 2.2, 64.0, "linear"))
    pin = keys((t0, 0.0), (t_best + 0.2, 0.0), (t_best + 1.4, 1.0))
    sb = slot(2)
    sbc, sbs = np.array([(sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2]), (sb[3] - sb[1]) - 0.3
    cv = Canvas((0.2, Y0, X1, Y1), px=s.comp.size[1] / 8)

    def heat_box(t):
        u = float(smoothstep(min(max(pin(t), 0.0), 1.0)))
        return hbox(HC + (sbc - HC) * u, HS + (sbs - HS) * u)

    def heat(t):
        return cov_heat(heat_box(t), int(round(float(rows(t)))), cv)

    s.add(FramesLayer(heat, z=1, during=[(t64 - 0.4, t1)], opacity=end, **cv.layer_kw()))
    m = s.manim(z=2, opacity=end)
    hf = Square(side_length=HS, stroke_color=C.roles["frame"], stroke_width=1.4, fill_opacity=0).move_to(P3(*HC))
    m.play(FadeIn(hf), at=t64 - 0.4, dur=0.6)
    diag = DashedLine(P3(*hbox(HC, HS)[0:1], hbox(HC, HS)[3]), P3(hbox(HC, HS)[2], hbox(HC, HS)[1]),
                      stroke_color=C.muted, stroke_width=1.4, dash_length=0.08, stroke_opacity=0.8)
    m.play(Create(diag), at=t64 + 2.4, dur=0.8)
    m.play(FadeOut(diag), at=t_two - 0.6, dur=0.5)

    # ---- two pixels: their entry and its mirror
    h = HS / 64
    a, b = PAIR
    px = VGroup(*[Square(side_length=TS / 8, stroke_color=C.probe, stroke_width=3.2).move_to(P3(*tile_xy(i)))
                  for i in PAIR])
    box_ = hbox(HC, HS)
    cross = VGroup(
        Line(P3(box_[0], heat_xy(a, b)[1]), P3(box_[2], heat_xy(a, b)[1]), stroke_color=C.probe, stroke_width=1.2,
             stroke_opacity=0.55),
        Line(P3(heat_xy(a, b)[0], box_[3]), P3(heat_xy(a, b)[0], box_[1]), stroke_color=C.probe, stroke_width=1.2,
             stroke_opacity=0.55),
        Square(side_length=h * 3, stroke_color=C.probe, stroke_width=2.4).move_to(P3(*heat_xy(a, b))),
        Square(side_length=h * 3, stroke_color=C.probe, stroke_width=2.4).move_to(P3(*heat_xy(b, a))))
    m.play(LaggedStart(*[Create(q) for q in px], lag_ratio=0.4), at=t_two - 0.1, dur=0.7)
    m.play(Create(cross), at=t_two + 0.5, dur=0.9)
    m.play(FadeOut(cross), at=t_nb - 0.3, dur=0.5)

    # ---- neighbouring pixels: row 27 tints the tile
    row = Rectangle(width=HS, height=h, stroke_color=C.spread, stroke_width=2.2).move_to(P3(HC[0], heat_xy(a, 0)[1]))
    vmax = float(np.abs(Cm[a]).max())
    tint = VGroup(*[Square(side_length=TS / 8, stroke_width=0, fill_color=C.spread if Cm[a, j] > 0 else C.data,
                           fill_opacity=0.8 * min(abs(Cm[a, j]) / vmax, 1.0) ** 0.8).move_to(P3(*tile_xy(j)))
                    for j in range(64)])
    m.play(Create(row), at=t_nb, dur=0.6)
    m.play(FadeIn(tint), FadeOut(px[1]), at=t_nb + 0.6, dur=1.0)
    m.play(FadeOut(VGroup(row, tint, px[0])), at=t_blank - 0.5, dur=0.5)

    # ---- blank in every scan: three pixels, their empty rows and columns
    marks = VGroup()
    lines_ = VGroup()
    for i in BLANK:
        p = tile_xy(i)
        q = TS / 8 * 0.32
        marks.add(Square(side_length=TS / 8, stroke_color=C.muted, stroke_width=2.4).move_to(P3(*p)),
                  Line(P3(p[0] - q, p[1] - q), P3(p[0] + q, p[1] + q), stroke_color=C.muted, stroke_width=2),
                  Line(P3(p[0] - q, p[1] + q), P3(p[0] + q, p[1] - q), stroke_color=C.muted, stroke_width=2))
        y = heat_xy(i, 0)[1]
        x = heat_xy(0, i)[0]
        lines_.add(Rectangle(width=HS, height=h, stroke_color=C.muted, stroke_width=1.6).move_to(P3(HC[0], y)),
                   Rectangle(width=h, height=HS, stroke_color=C.muted, stroke_width=1.6).move_to(P3(x, HC[1])))
    m.play(LaggedStart(*[Create(q) for q in marks], lag_ratio=0.15), at=t_blank - 0.1, dur=1.0)
    m.play(Create(lines_), at=t_blank + 0.6, dur=1.0)
    m.play(FadeOut(VGroup(marks, lines_, hf)), at=t_best - 0.3, dur=0.5)
    s.manim(z=0.5, opacity=end).play(FadeIn(board(slot(2))), at=t_best + 0.6, dur=0.6)
