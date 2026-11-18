"""s28 bookend (outro): Bernoulli wanted to know what happens to money that grows a little every instant. Asked about a
matrix, the same question describes the medicine in your blood, a turning planet and a quantum computer (three tiles
light in a row). Then the last two sentences: A, how things move, and e^A, where they go, with the flow between them.
Hold through the tail; the bottom-right stays clear for the end card."""
from aion import *

from beats import T
from ch6 import b_level
from shots import (E, J, backdrop, disc_points, field_arrows, finish, flow_layers, globe_wire, lab, live, p3, panel, plot,
                   portrait, qwire_icon, tex)

TX, TY, TW, TH = [-1.75, 1.6, 4.95], 0.75, 3.0, 2.4


@scene(T.cut_bookend, T.end)
def s28_bookend(s):
    backdrop(s)
    mf = s.manim(z=0)
    m = s.manim(z=4)
    t_out = T.how_move - 0.5

    # ── Bernoulli, small at the left ──
    p_op = keys((T.bern2 - 0.1, 0.0), (T.bern2 + 0.5, 1.0), (t_out, 1.0), (t_out + 0.5, 0.0), lead=0)
    fb = portrait(s, "bernoulli", (-5.4, 1.15), 2.1, opacity=p_op, start=T.cut_bookend, end=t_out + 0.6, z=3)
    bl = VGroup(Tex(r"\textsc{Bernoulli}", font_size=30, color=C.text),
                tex(r"\left(1+\tfrac1n\right)^{n}", size=36, color=C.money)).arrange(DOWN, buff=0.15).next_to(
        fb, DOWN, buff=0.2)
    m.play(Create(fb), FadeIn(bl), at=T.bern2, dur=0.6)

    # ── the same question: blood, planet, quantum computer ──
    tiles = VGroup()
    for i, (at, word, col) in enumerate(((T.blood2, "medicine", C.flow), (T.planet2, "planet", C.globe),
                                         (T.qc, "quantum computer", C.comm))):
        x = TX[i]
        fr = panel(x - TW / 2, TY - TH / 2, x + TW / 2, TY + TH / 2, fill=False).set_stroke(color=col)
        tg = lab(word, 26, col).move_to([x, TY - TH / 2 - 0.35, 0])
        tiles.add(VGroup(fr, tg))
        m.play(Create(fr), FadeIn(tg), at=at - 0.1, dur=0.5)
    q_lab = tex(r"e^{tA}", size=56, color=C.flow).move_to([TX[1], TY + TH / 2 + 0.55, 0])
    q_lab[0][2].set_color(C.gen)
    m.play(FadeIn(q_lab, shift=0.1 * DOWN), at=T.asked + 0.3, dur=0.6)
    o = np.array([TX[0] - 1.2, TY - 0.85])
    curve = plot(b_level, 0, 12, o, 2.4 / 12, 2.3, C.flow, width=C.stroke)
    m.play(Create(curve), at=T.blood2 + 0.1, dur=0.9)
    spin = Clock(start=T.planet2)
    g_op = keys((T.planet2 - 0.1, 0.0), (T.planet2 + 0.4, 1.0), (t_out, 1.0), (t_out + 0.5, 0.0), lead=0)
    live(m, lambda t: globe_wire((TX[1], TY), 0.85, 0.6 * float(spin(t)), op=float(g_op(t))),
         (T.planet2 - 0.1, t_out + 0.55))
    qc = qwire_icon((TX[2], TY), s=0.75)
    m.play(Create(qc), at=T.qc + 0.1, dur=0.7)
    m.play(FadeOut(VGroup(bl, tiles, q_lab, curve, qc, fb)), at=t_out, dur=0.5)

    # ── a matrix tells you how things move; e to the matrix tells you where they go ──
    t_end = T.end - 1.6
    field = field_arrows(J, spacing=0.9, opacity=0.35)
    mf.play(FadeIn(field), at=T.how_move, dur=0.8)
    mf.play(FadeOut(field), at=t_end, dur=1.3)
    tau = Clock(rate=0.3, start=T.how_move)
    al = keys((T.how_move, 0.0), (T.how_move + 0.8, 0.45), (t_end, 0.45), (t_end + 1.3, 0.0), lead=0)
    flow_layers(s, disc_points(900, 4.6, seed=29), J, tau, alpha=al, trail=8, size=2.2, z=1, start=T.how_move - 0.1)
    A = tex("A", size=130, color=C.gen).move_to([-3.2, 0.4, 0])
    eA = tex(r"e^{A}", size=130, color=C.flow).move_to([3.2, 0.5, 0])
    eA[0][1].set_color(C.gen)
    la = lab("how things move", 30, C.gen).next_to(A, DOWN, buff=0.45)
    le = lab("where they go", 30, C.flow).next_to(eA, DOWN, buff=0.45).align_to(la, UP)
    cards = [BackgroundRectangle(VGroup(A, la), color=C.bg, fill_opacity=0.85, buff=0.25),
             BackgroundRectangle(VGroup(eA, le), color=C.bg, fill_opacity=0.85, buff=0.25)]
    m.play(FadeIn(cards[0]), FadeIn(A, scale=0.9), at=T.how_move + 0.2, dur=0.7)
    m.play(FadeIn(la, shift=0.1 * UP), at=T.how_move + 1.0, dur=0.5)
    m.play(FadeIn(cards[1]), FadeIn(eA, scale=0.9), at=T.where_go + 0.2, dur=0.7)
    m.play(FadeIn(le, shift=0.1 * UP), at=T.where_go + 1.0, dur=0.5)
    m.play(FadeOut(VGroup(*cards, A, eA, la, le)), at=t_end, dur=1.3)
    finish(s)
