"""s10 recording: the same four moves run on two grids at once. The bent grid straightens while the straight grid bends, and the
augmented matrix beneath them is those two grids written in numbers."""
from aion import *

from beats import T
from film2 import frame
from shots import RECORD, STATES, brackets, carded, four_rows, fr, lab, panel, tex, varrow

BL, BR = (-6.6, -0.85, -0.2, 3.5), (0.2, -0.85, 6.6, 3.5)
OL, OR = np.array([-3.4, 0.9]), np.array([3.4, 0.9])
UNIT = 0.46
ROW_Y, COL_DX = (-1.86, -2.92), 1.0


@scene(T.cut_record, T.cut_check)
def s10_recording(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_record, T.cut_check)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # frames and numbers

    # ── what the last scene left on screen ──
    old_rows = VGroup(*four_rows())
    m.add(old_rows)
    m.play(FadeOut(old_rows), at=T.cut_record + 0.05, dur=0.45)

    # ── the same four moves, on both grids at once ──
    t0, gap = T.as_bent + 0.1, 1.33
    fl, fr_ = panel(*BL, fill=False), panel(*BR, fill=False)
    m.play(FadeIn(fl), at=T.never - 0.2, dur=0.6)
    m.play(FadeIn(fr_), at=T.second_grid - 0.1, dur=0.6)

    def corner(sym, color, box):
        return carded(tex(sym, size=58, color=color).move_to([box[0] + 0.5, box[3] - 0.46, 0]), buff=0.08)
    s_a, s_i = corner("A", C.fwd, BL), corner("I", C.home, BR)
    s_il, s_inv = corner("I", C.home, BL), corner(r"A^{-1}", C.back, BR)
    m.play(FadeIn(s_a), at=T.never, dur=0.5)
    m.play(FadeIn(s_i), at=T.second_grid, dur=0.5)

    # ── the augmented matrix, each half under its own grid ──
    br = brackets(height=2.3, gap=10.7).move_to([0, -2.39, 0])
    divider = Line([0, -1.36, 0], [0, -3.42, 0], color=C.text, stroke_width=2.0)
    m.play(FadeIn(br), FadeIn(divider), at=T.play_same, dur=0.6)

    def entry(v, side, i, j, color):
        x = (OL if side == 0 else OR)[0] + (j - 0.5) * 2 * COL_DX
        return tex(fr(v), size=40, color=color).move_to([x, ROW_Y[i], 0])

    now = {}
    for side, st, col in ((0, STATES, C.fwd), (1, RECORD, C.back)):
        for i in range(2):
            for j in range(2):
                now[side, i, j] = entry(st[0][i, j], side, i, j, col)
    m.play(FadeIn(VGroup(*[v for k, v in now.items() if k[0] == 0])), at=T.play_same + 0.2, dur=0.5)
    m.play(FadeIn(VGroup(*[v for k, v in now.items() if k[0] == 1])), at=T.second_grid + 0.2, dur=0.5)

    for step in range(4):
        out, back = [], []
        for side, st, col in ((0, STATES, C.fwd), (1, RECORD, C.back)):
            for i in range(2):
                for j in range(2):
                    if abs(st[step + 1][i, j] - st[step][i, j]) > 1e-9:
                        fresh = entry(st[step + 1][i, j], side, i, j, col)
                        out.append(now[side, i, j])
                        back.append(fresh)
                        now[side, i, j] = fresh
        m.play(*[FadeOut(v) for v in out], *[FadeIn(v) for v in back], at=t0 + step * gap + 0.35, dur=0.4)

    # ── identity on the left, the inverse on the right ──
    m.play(FadeOut(s_a), FadeIn(s_il), *[now[0, i, j].animate.set_color(C.home) for i in range(2) for j in range(2)], at=T.reaches, dur=0.6)
    answer = SurroundingRectangle(VGroup(*[now[1, i, j] for i in range(2) for j in range(2)]), color=C.back, buff=0.16, stroke_width=2.6)
    m.play(FadeOut(s_i), FadeIn(s_inv), Create(answer), at=T.became, dur=0.7)

    # ── row reduction is these two grids ──
    links = VGroup(varrow((OL[0], -1.32), (OL[0], -0.92), C.home, width=2.6, tip=0.16), varrow((OR[0], -1.32), (OR[0], -0.92), C.back, width=2.6, tip=0.16))
    m.play(FadeIn(links), at=T.blocks, dur=0.6)
    t_l = carded(lab("rewinds", size=36, color=C.home).move_to([OL[0] + 1.1, BL[3] - 0.42, 0]), buff=0.08)
    t_r = carded(lab("records", size=36, color=C.back).move_to([OR[0] + 1.1, BR[3] - 0.42, 0]), buff=0.08)
    m.play(FadeIn(t_l), at=T.rewinds, dur=0.5)
    m.play(FadeIn(t_r), at=T.records, dur=0.5)
    s.solid(C.bg, z=50, opacity=key(T.cut_check - 0.42, 0.0, 1.0, dur=0.4, lead=0))
