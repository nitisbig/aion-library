"""Outro · What we found, one tile per idea; then the opening's bare ad − bc becomes the parallelogram it measures."""
from aion import *

from beats import T
from shots import (A_MAIN, A_SWAP, A_ZERO, FRAME, I2, _clip, backdrop, basis_arrows, finish, grid_lines, lettered,
                   live, panel, pt, rail, span_area, strike, tex, words)

E = "easy_ease"
O7, U7 = np.array([0.4, -3.3]), 0.6                  # Ch7's framing
TL, TR = (-6.85, 0.2, -0.15, 3.55), (0.15, 0.2, 6.85, 3.55)
BL, BR = (-6.85, -3.3, -0.15, 0.05), (0.15, -3.3, 6.85, 0.05)
UT = 0.42                                            # grid unit inside a tile
G, UG = np.array([-2.6, -1.2]), 1.0                  # the closing drawing


def ramp(t, a, b):
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def inner(box, m=0.03):
    return (box[0] + m, box[1] + m, box[2] - m, box[3] - m)


def origin(box):
    return np.array([box[0] + 2.3, box[1] + 0.75])


def label(box, *parts, color=None, size=44):
    t = tex(*parts, size=size, color=color)
    return t.move_to([box[0] + 0.3 + t.width / 2, box[3] - 0.3 - t.height / 2, 0])



@scene(T.cut_outro, T.end)
def s08_outro(s):
    backdrop(s)
    old = s.manim(z=0.5)                              # Ch7's last frame
    tl = s.manim(z=1)                                 # tiles
    mv = s.manim(z=2)                                 # the moving miniature
    fbg = s.manim(z=2.8)                              # the closing parallelogram, under its arrows
    fin = s.manim(z=3)                                # the closing drawing
    hud = s.manim(z=6, parallax=0.0)
    rl = rail(hud, 8)                                 # every chapter done
    t0 = T.cut_outro

    # ── Ch7's last frame: the rested grid, the unit square, the arrows ──
    leftovers = VGroup(grid_lines(I2, O7, U7, FRAME, n=20), span_area(I2, O7, U7), basis_arrows(I2, O7, U7))
    old.add(leftovers)
    old.play(FadeOut(leftovers), at=T.gather - 0.6, dur=0.9, lead=0)

    # ── four tiles, framed; each fills on its sentence ──
    frames = VGroup(*[panel(*b) for b in (TL, TR, BL, BR)])
    tl.play(LaggedStart(*[FadeIn(f_) for f_ in frames], lag_ratio=0.15), at=T.gather + 0.2, dur=1.0)

    # 1 · a matrix moves space, and scales area: ×5
    o1 = origin(TL)
    w1 = (T.r_moves - 0.1, T.r_moves + 1.6)
    M1 = keys((t0, I2), (w1[0], I2), (w1[1], A_MAIN, E), lead=0)
    k1 = (T.r_moves - 0.6, T.r_moves - 0.1)

    def tile1(t):
        k = ramp(t, *k1) * (1 - ramp(t, T.final_adbc - 0.9, T.final_adbc - 0.2))
        out = VGroup(grid_lines(M1(t), o1, UT, inner(TL), n=10, opacity=k))
        out.add(span_area(M1(t), o1, UT, opacity=0.3 * k).set_stroke(opacity=k))
        out.add(basis_arrows(M1(t), o1, UT, width=C.stroke).set_opacity(k))
        return out
    live(mv, tile1, k1, (w1[0], w1[1] + 0.1), (T.final_adbc - 0.9, T.final_adbc - 0.15))
    lab1 = label(TL, r"\times 5", color=C.area, size=56)
    tl.play(FadeIn(lab1), at=T.r_scales, dur=0.6)

    # 2 · or, in three dimensions, volume
    a, e = np.radians(-28), np.radians(58)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    o2, u2 = np.array([TR[0] + 3.2, TR[1] + 1.2]), 0.4

    def S(p):
        q = Rz @ np.asarray(p, float)
        return np.array([o2[0] + u2 * q[0], o2[1] + u2 * (q[2] * np.cos(e) + q[1] * np.sin(e)), 0.0])

    def D(p):
        q = Rz @ np.asarray(p, float)
        return q[1] * np.cos(e) - q[2] * np.sin(e)
    A3 = np.column_stack([[2.0, 0, 0], [1.0, 1, 0], [-1.0, 1, 3]])
    cube = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
    faces = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]
    corners = [A3 @ c for c in cube]
    box3 = VGroup()
    for k in range(-2, 5):                            # a small floor that stays inside the tile
        box3.add(Line(S((k, -1, 0)), S((k, 3, 0)), color=C.grid, stroke_width=C.thin, stroke_opacity=0.5))
    for k in range(-1, 4):
        box3.add(Line(S((-2, k, 0)), S((4, k, 0)), color=C.grid, stroke_width=C.thin, stroke_opacity=0.5))
    for f_ in sorted(faces, key=lambda f_: -np.mean([D(corners[i]) for i in f_])):
        box3.add(Polygon(*[S(corners[i]) for i in f_], stroke_color=C.area, stroke_width=C.thin + 0.4,
                         fill_color=C.area, fill_opacity=0.22))
    for k, col in enumerate((C.ihat, C.jhat, C.khat)):
        box3.add(Arrow(S((0, 0, 0)), S(A3[:, k]), buff=0, color=col, stroke_width=C.stroke, tip_length=0.16,
                       max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40))
    vol = words("volume", size=48, color=C.area)
    vol.move_to([TR[0] + 0.3 + vol.width / 2, TR[3] - 0.3 - vol.height / 2, 0])
    tl.play(FadeIn(box3), at=T.r_volume - 0.5, dur=0.7)
    tl.play(FadeIn(vol), at=T.r_volume, dur=0.5)

    # 3 · the sign: space turned over
    o3 = origin(BL)
    t3 = VGroup(grid_lines(A_SWAP, o3, UT, inner(BL), n=10), span_area(A_SWAP, o3, UT),
                basis_arrows(A_SWAP, o3, UT, width=C.stroke))
    a_i, a_j = np.arctan2(A_SWAP[1, 0], A_SWAP[0, 0]), np.arctan2(A_SWAP[1, 1], A_SWAP[0, 1])
    turn = Arc(radius=0.8 * UT, start_angle=a_i, angle=a_j - a_i, arc_center=[*o3, 0], color=C.flip,
               stroke_width=C.stroke)
    turn.add_tip(tip_length=0.14, tip_width=0.14)
    tl.play(FadeIn(t3), at=T.r_sign - 0.3, dur=0.7)
    lab3 = tex(r"\det", "<", "0", size=44, colors={2: C.flip})
    lab3.move_to([BL[0] + 0.3 + lab3.width / 2, BL[3] - 0.3 - lab3.height / 2, 0])
    tl.play(Create(turn), FadeIn(lab3), at=T.r_sign + 0.6, dur=0.7)

    # 4 · zero: collapse, and no way back
    o4 = origin(BR)
    seg = _clip(o4, np.array([2.0, 1.0]), inner(BR))
    t4 = VGroup(grid_lines(A_ZERO, o4, UT, inner(BR), n=10),
                Line([*seg[0], 0], [*seg[1], 0], color=C.collapse, stroke_width=5),
                basis_arrows(A_ZERO, o4, UT, width=C.stroke))
    tl.play(FadeIn(t4), at=T.r_zero - 0.3, dur=0.7)
    lab4 = tex(r"\det", "=", "0", size=44, colors={2: C.collapse})
    lab4.move_to([BR[0] + 0.3 + lab4.width / 2, BR[3] - 0.3 - lab4.height / 2, 0])
    tl.play(FadeIn(lab4), at=T.r_zero + 0.4, dur=0.6)
    inv = tex("A^{-1}", size=56).move_to([BR[2] - 0.9, BR[1] + 0.6, 0])
    x_inv = strike(inv, color=C.collapse).set_stroke(width=C.stroke)
    tl.play(Write(inv), at=T.r_undone - 0.4, dur=0.6)
    tl.play(Create(x_inv), at=T.r_undone + 0.3, dur=0.4)

    # ── the tiles clear: the opening's bare formula, and what it was all along ──
    tiles_out = T.final_adbc - 0.9
    tl.play(FadeOut(VGroup(frames, lab1, box3, vol, t3, turn, lab3, t4, lab4, inv, x_inv)), at=tiles_out, dur=0.7,
            lead=0)
    big = lettered("ad", "-bc", size=120).move_to([0, 0.4, 0])
    big[1][0].set_color(C.text)
    fin.play(Write(big), at=T.final_adbc - 0.2, dur=1.2)

    o = pt(G, UG, (0, 0))
    ai = Arrow(o, pt(G, UG, (3, 1)), buff=0, color=C.ihat, stroke_width=C.stroke + 1, tip_length=0.26)
    aj = Arrow(o, pt(G, UG, (1, 2)), buff=0, color=C.jhat, stroke_width=C.stroke + 1, tip_length=0.26)
    para = Polygon(o, pt(G, UG, (3, 1)), pt(G, UG, (4, 3)), pt(G, UG, (1, 2)), stroke_color=C.area,
                   stroke_width=C.thin + 0.6, fill_color=C.area, fill_opacity=0.3)
    a_, d_, m_, b_, c_ = big[0][0], big[0][1], big[1][0], big[1][1], big[1][2]
    fin.play(ReplacementTransform(VGroup(a_, c_), ai), ReplacementTransform(VGroup(b_, d_), aj), FadeOut(m_),
             at=T.never_recipe + 0.2, dur=1.4)
    fbg.play(FadeIn(para), at=T.final_area + 0.2, dur=1.0)
    small = lettered("ad", "-bc", size=80).move_to([-0.6, -2.35, 0])
    small[1][0].set_color(C.text)
    fin.play(Write(small), at=T.final_area + 1.0, dur=1.0)
    fbg.play(para.animate.set_fill(opacity=0.45), at=T.see_it - 0.2, dur=0.5)

    # ── fade to the background over the last second ──
    fin.play(FadeOut(VGroup(ai, aj, small)), at=T.end - 1.05, dur=1.0, lead=0)
    fbg.play(FadeOut(para), at=T.end - 1.05, dur=1.0, lead=0)
    hud.play(FadeOut(rl), at=T.end - 1.05, dur=1.0, lead=0)

    finish(s)
