"""s14 diagonal (ch4): the easiest case. D = diag(1, −1/2): its flow is two ch1 number lines minding their own
business, growing sideways and shrinking vertically. So e^{tD} = diag(e^t, e^{−t/2}): e to each diagonal entry, the
one time you exponentiate entries, and only on the diagonal. The zeros stay zero; element-wise would make them ones."""
from aion import *

from beats import T
from shots import (BOX4, PAN4, PC4, PX4, E, backdrop, chapter_card, cycles, disc_points, field_arrows, finish,
                   flow_layers, lab, live, p3, stage4, tex)
from verify import CAST

D = CAST["diag"]


@scene(T.cut_ch4, T.cut_saddle)
def s14_diagonal(s):
    backdrop(s)
    mg = s.manim(z=0)
    mf = s.manim(z=1)
    m = s.manim(z=4)
    mp = s.manim(z=5)
    chapter_card(mp, 4, "Directions, spirals, and shears", r"\lambda", T.cut_ch4, color=C.eigen)
    t_in = T.cut_ch4 + 2.8
    stage4(mg, mp, t_in)

    # ── D and its field ──
    Dm = VGroup(tex("D", "=", size=44, colors={0: C.gen}),
                Mat([["1", "0"], ["0", r"-\tfrac12"]], colors=C.gen, size=40, h_buff=1.0, v_buff=0.75)).arrange(
        RIGHT, buff=0.2).move_to([PX4, 2.75, 0])
    mp.play(FadeIn(Dm, shift=0.1 * DOWN), at=T.diagonal + 0.3, dur=0.6)
    field = field_arrows(D, center=PC4, box=BOX4, spacing=0.75)
    mf.play(FadeIn(field, lag_ratio=0.004), at=T.diagonal + 0.8, dur=1.2)

    # ── two number lines minding their own business ──
    tau, al = cycles(T.two_lines + 0.4, T.cut_saddle - 0.3, 4.0, 1.25)
    hx = Line(p3(PC4 + [-4.9, 0]), p3(PC4 + [4.6, 0]), color=C.ihat, stroke_width=C.stroke + 1.5)
    hy = Line(p3(PC4 + [0, -4.1]), p3(PC4 + [0, 4.1]), color=C.jhat, stroke_width=C.stroke + 1.5)
    m.play(Create(hx), Create(hy), at=T.two_lines - 0.2, dur=0.8, ease=E)
    m.play(FadeOut(VGroup(hx, hy)), at=T.diag_exp - 0.6, dur=0.6)

    d_out = keys((T.diag_exp - 0.6, 1.0), (T.diag_exp - 0.1, 0.0), lead=0)

    def axis_dots(t):
        k = float(tau(t))
        a = float(al(t)) * float(d_out(t))
        out = VGroup()
        for x in (-2.0, -1.0, 1.0, 2.0):
            out.add(Dot(p3(PC4 + [x * np.exp(k), 0]), radius=0.1, color=C.ihat).set_opacity(a))
            out.add(Dot(p3(PC4 + [0, 1.6 * x * np.exp(-0.5 * k)]), radius=0.1, color=C.jhat).set_opacity(a))
        return out
    live(m, axis_dots, (T.two_lines + 0.4, T.diag_exp - 0.05))
    flow_layers(s, disc_points(2500, 4.2, seed=7), D, tau, alpha=al * 0.5, trail=8, size=2.2, z=2, center=PC4,
                start=T.diag_exp - 0.6, end=T.cut_saddle)

    # ── e to each diagonal entry ──
    eD = VGroup(tex(r"e^{tD}", "=", size=44, colors={0: C.flow}),
                Mat([[r"e^{t}", "0"], ["0", r"e^{-t/2}"]], colors=C.flow, size=40, h_buff=1.2, v_buff=0.8)).arrange(
        RIGHT, buff=0.2).move_to([PX4, 0.75, 0])
    mp.play(FadeIn(eD, shift=0.1 * DOWN), at=T.diag_exp + 0.3, dur=0.7)
    tag = lab("e to each diagonal entry", 26, C.flow).next_to(eD, DOWN, buff=0.3)
    mp.play(FadeIn(tag), at=T.one_time + 0.3, dur=0.5)

    # ── the zeros stay zero; the element-wise ghost would make them ones ──
    zs = VGroup(eD[1].cell(0, 1), eD[1].cell(1, 0))
    mp.play(zs.animate.set_color(C.text), at=T.zeros + 0.2, dur=0.4)
    mp.play(Indicate(zs, color=C.text, scale_factor=1.4), at=T.zeros + 0.6, dur=0.8)
    gh = VGroup(lab("entry by entry", 24, C.wrong),
                Mat([[r"e^{t}", "1"], ["1", r"e^{-t/2}"]], colors=C.wrong, size=36, h_buff=1.15, v_buff=0.75)).arrange(
        DOWN, buff=0.2).move_to([PX4, -2.45, 0])
    mp.play(FadeIn(gh, shift=0.1 * UP), at=T.made_ones - 1.2, dur=0.6)
    mp.play(Indicate(VGroup(gh[1].cell(0, 1), gh[1].cell(1, 0)), color=C.comm, scale_factor=1.4), at=T.made_ones + 0.2,
            dur=0.8)
    mp.play(FadeOut(VGroup(Dm, eD, tag, gh)), at=T.cut_saddle - 0.4, dur=0.5)
    mf.play(FadeOut(field), at=T.cut_saddle - 0.4, dur=0.5)
    finish(s)
