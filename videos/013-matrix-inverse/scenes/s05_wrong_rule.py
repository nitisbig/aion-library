"""s05 wrong rule: the stretch suggests flipping every entry. The slide has a zero yet comes back, and S has no zeros yet is
stuck, so single entries can't decide it. We have to watch the whole plane."""
from aion import *

from beats import T
from film1 import frame
from shots import EASE, SIMPLE_ROWS, S_ROWS, lab, ledger, tex, varrow


@scene(T.cut_wrong, T.cut_threads)
def s05_wrong_rule(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_wrong, T.cut_threads)], z=0))
    mb = s.manim(z=3, parallax=0.0)                   # the two test panels
    m = s.manim(z=5, parallax=0.0)

    # ── what s04 left on screen ──
    rows = ledger()
    m.add(*rows.values())
    r = rows["stretch"]
    m.play(FadeOut(rows["turn"]), FadeOut(rows["slide"]), FadeOut(r.card), FadeOut(r.tag), at=T.cut_wrong + 0.1, dur=0.6)

    # ── two became a half, three became a third ──
    go, ret = SIMPLE_ROWS["stretch"]
    big_f = Mat(go, colors=C.fwd, size=68, h_buff=1.45, v_buff=1.55, pad=0.32).move_to([-2.9, 0.75, 0])
    big_b = Mat(ret, colors=C.back, size=68, h_buff=1.45, v_buff=1.55, pad=0.32).move_to([2.9, 0.75, 0])
    m.play(ReplacementTransform(r.fwd, big_f), ReplacementTransform(r.back, big_b), at=T.shortcut - 0.5, dur=1.1, ease=EASE)
    link = varrow((-0.75, 0.75), (0.75, 0.75), C.text, width=3.0)
    m.play(FadeIn(link), at=T.shortcut + 0.4, dur=0.4)

    def ring(mob):
        return SurroundingRectangle(mob, color=C.home, buff=0.12, stroke_width=2.4)
    b1 = VGroup(ring(big_f.cell(0, 0)), ring(big_b.cell(0, 0)))
    b2 = VGroup(ring(big_f.cell(1, 1)), ring(big_b.cell(1, 1)))
    m.play(Create(b1), at=T.half - 0.45, dur=0.45)
    m.play(ReplacementTransform(b1, b2), at=T.third - 0.3, dur=0.5, ease=EASE)
    m.play(FadeOut(b2), at=T.flip - 0.35, dur=0.35)

    rule = tex("a", r"\;\longrightarrow\;", r"\frac{1}{a}", size=64, color=C.wrong).move_to([0, -2.15, 0])
    m.play(FadeIn(rule, shift=0.08 * UP), at=T.flip - 0.1, dur=0.6)

    # ── the rule moves aside and is tested twice ──
    m.play(FadeOut(VGroup(big_f, big_b, link)), rule.animate.scale(0.56).move_to([0, 3.27, 0]), at=T.but_deck - 0.4, dur=0.7, ease=EASE)

    panels = VGroup(*[Rectangle(width=6.4, height=6.3, stroke_color=C.frame, stroke_width=1.6, fill_color=C.bg, fill_opacity=0.9).move_to([x, -0.4, 0]) for x in (-3.4, 3.4)])
    mb.play(FadeIn(panels[0]), at=T.but_deck - 0.2, dur=0.6)
    mb.play(FadeIn(panels[1]), at=T.mat_crush - 0.3, dur=0.6)
    mb.play(FadeOut(panels), at=T.whole - 0.55, dur=0.7)

    kw = dict(size=46, h_buff=1.05, v_buff=1.14, pad=0.3)
    sl_f, sl_b = SIMPLE_ROWS["slide"]
    left = Mat(sl_f, colors=C.fwd, **kw).move_to([-5.05, 1.0, 0])
    flipped = Mat([["1", "1"], [r"\frac{1}{0}", "1"]], colors=C.wrong, **kw).move_to([-1.75, 1.0, 0])
    test = varrow((-3.95, 1.0), (-2.95, 1.0), C.wrong, width=2.6)
    undo = Mat(sl_b, colors=C.back, **kw).move_to([-3.4, -1.55, 0])
    t_zero, t_undone = lab("has a zero").move_to([-5.05, 2.45, 0]), lab("undone", color=C.back).move_to([-3.4, -3.2, 0])

    right = Mat(S_ROWS, colors=C.fwd, **kw).move_to([3.4, 1.0, 0])
    stuck_eq = VGroup(tex(r"S^{-1}", size=56, color=C.wrong), tex("=", size=56, color=C.wrong), tex("?", size=60, color=C.wrong))
    stuck_eq.arrange(RIGHT, buff=0.2).move_to([3.4, -1.55, 0])
    t_none, t_stuck = lab("no zeros").move_to([3.4, 2.45, 0]), lab("stuck", color=C.wrong).move_to([3.4, -3.2, 0])

    m.play(FadeIn(left, shift=0.06 * DOWN), at=T.but_deck + 0.1, dur=0.6)
    z_box = SurroundingRectangle(left.cell(1, 0), color=C.null, buff=0.1, stroke_width=2.4)
    m.play(Create(z_box), FadeIn(t_zero), at=T.zero, dur=0.5)
    m.play(FadeIn(test), FadeIn(flipped, shift=0.06 * RIGHT), at=T.cant - 0.5, dur=0.6)
    m.play(FadeIn(undo, shift=0.06 * DOWN), FadeIn(t_undone), at=T.undid, dur=0.6)
    s_box = SurroundingRectangle(undo.cell(0, 1), color=C.back, buff=0.1, stroke_width=2.4)
    m.play(Create(s_box), at=T.sign, dur=0.5)

    m.play(FadeIn(right, shift=0.06 * DOWN), at=T.mat_crush, dur=0.6)
    m.play(FadeIn(t_none), at=T.no_zeros, dur=0.5)
    m.play(FadeIn(stuck_eq), FadeIn(t_stuck), at=T.no_zeros + 0.9, dur=0.6)

    # ── one entry at a time tells us nothing ──
    cells = [left.cell(i, j) for i in range(2) for j in range(2)] + [right.cell(i, j) for i in range(2) for j in range(2)]
    m.play(LaggedStart(*[Indicate(c, color=C.home, scale_factor=1.22) for c in cells], lag_ratio=0.3), at=T.one_at, dur=1.7)

    # ── so we go back to the plane ──
    every = VGroup(rule, left, flipped, test, undo, t_zero, t_undone, right, stuck_eq, t_none, t_stuck, z_box, s_box)
    m.play(FadeOut(every), at=T.whole - 0.55, dur=0.7)
