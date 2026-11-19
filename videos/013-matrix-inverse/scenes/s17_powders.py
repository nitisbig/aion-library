"""s17 powders: two scoops, each a column of grams. The matrix answers "what do these scoops make?" easily, but the question that matters
runs the other way: seven grams of protein and six of fibre, how many scoops is that?"""
from aion import *

from beats import T
from film3 import frame
from shots import ask_x, caps, heading5, powder_table, tex, unit_bar


@scene(T.cut_powders, T.cut_solve)
def s17_powders(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_powders, T.cut_solve)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # the table and equations

    # ── chapter card: its symbol stays on as the heading ──
    big = heading5(size=104)
    name = caps("Who landed here?", size=52)
    VGroup(big, name).arrange(DOWN, buff=0.42).move_to(ORIGIN)
    m.play(FadeIn(big), FadeIn(name), at=T.cut_powders + 0.05, dur=0.3, lead=0)
    m.play(FadeOut(name), at=T.cut_powders + 1.6, dur=0.4)
    m.play(ReplacementTransform(big, heading5()), at=T.powders - 1.0, dur=0.9)

    # ── each scoop is a column of grams ──
    table = powder_table()
    mat = table.mat
    m.play(FadeIn(table.rows), at=T.p1, dur=0.5)
    m.play(Create(table.icons[0]), at=T.p1 - 0.1, dur=0.8)
    m.play(Create(table.icons[1]), at=T.p2 - 0.1, dur=0.8)
    amounts = ((0, 0, 3, C.ihat, T.p1_pro), (1, 0, 2, C.ihat, T.p1_pro + 1.32), (0, 1, 1, C.jhat, T.p2_pro), (1, 1, 2, C.jhat, T.p2_pro + 1.04))
    bars = []
    for i, j, n, col, at in amounts:
        bar = unit_bar(n, mat.cell(i, j).get_center(), col)
        bars.append(bar)
        m.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in bar], lag_ratio=0.25), at=at, dur=0.5)

    # ── the blocks become numbers, and the columns become arrows ──
    m.play(*[FadeOut(b) for b in bars], *[FadeIn(mat.cell(i, j)) for i in range(2) for j in range(2)], FadeIn(mat.br), at=T.cols_mat - 0.1, dur=0.6)
    # ── forward is easy: one scoop of each ──
    demo = tex("A", r"\begin{pmatrix}1\\1\end{pmatrix}", "=", r"\begin{pmatrix}4\\4\end{pmatrix}", size=50, colors={0: C.fwd, 3: C.fwd}).move_to([-3.2, -2.35, 0])
    m.play(FadeIn(VGroup(demo[0], demo[1])), at=T.scoops_in, dur=0.5)
    m.play(FadeIn(VGroup(demo[2], demo[3])), at=T.get, dur=0.5)
    m.play(FadeOut(demo), at=T.other_way - 0.1, dur=0.5)

    # ── the question runs the other way ──
    m.play(FadeIn(ask_x(), shift=0.06 * UP), at=T.how_many + 0.25, dur=0.5)
