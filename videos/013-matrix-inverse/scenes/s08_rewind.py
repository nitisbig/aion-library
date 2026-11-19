"""s08 rewind: lean, then a quarter turn. Undoing them in the same order leaves the plane bent; undoing the last move first brings
it home. A film strip played backward then gives the rule (TL)^-1 = L^-1 T^-1."""
from aion import *

from beats import T
from film2 import frame
from shots import EASE, chapter_card, lab, tex, varrow

W, H, CY = 3.7, 2.5, 0.85                             # film frames
XS = (-4.25, 0.0, 4.25)


def step(sym, tag, color, y):
    """One line of the move list: a symbol and a key word on a black card."""
    s_ = tex(sym, size=54, color=color).move_to([-5.95, y, 0])
    parts = [s_]
    if tag:
        t_ = lab(tag, size=32, color=color)
        parts.append(t_.move_to([-5.15 + t_.width / 2, y, 0]))
    body = VGroup(*parts)
    g = VGroup(BackgroundRectangle(body, color=C.bg, fill_opacity=0.92, buff=0.12), *parts)
    g.body = body
    return g


@scene(T.cut_rewind, T.cut_four)
def s08_rewind(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_rewind, T.cut_four)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # the move list, then the film
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    # ── chapter card ──
    chapter_card(mh, tex(r"(TL)^{-1}", size=104, color=C.back), "Rewind", T.cut_rewind, T.stages + 0.05)

    # ── the list of moves, in the order they happen ──
    s_lean, s_turn = step("L", "lean", C.fwd, 3.0), step("T", "turn", C.fwd, 2.2)
    m.play(FadeIn(s_lean, shift=0.06 * RIGHT), at=T.lean, dur=0.5)
    m.play(FadeIn(s_turn, shift=0.06 * RIGHT), at=T.quarter, dur=0.5)

    w1, w2 = step(r"L^{-1}", "undo lean", C.wrong, 1.05), step(r"T^{-1}", "undo turn", C.wrong, 0.25)
    w3 = step(r"\neq I", "", C.wrong, -0.6)
    m.play(FadeIn(w1, shift=0.06 * RIGHT), at=T.wrong, dur=0.5)
    m.play(FadeIn(w2, shift=0.06 * RIGHT), at=T.undo_t + 0.15, dur=0.5)
    m.play(FadeIn(w3), at=T.no_home, dur=0.5)
    m.play(FadeOut(VGroup(w1, w2, w3)), at=T.last - 0.2, dur=0.5)

    ring = SurroundingRectangle(s_turn.body, color=C.fwd, buff=0.1, stroke_width=2.4)
    drop = varrow((-5.95, 1.72), (-5.95, 1.32), C.back, width=3.0, tip=0.2)
    m.play(Create(ring), at=T.last + 0.3, dur=0.5)
    m.play(FadeIn(drop), at=T.off_first - 0.15, dur=0.4)
    m.play(FadeOut(ring), FadeOut(drop), at=T.right - 0.15, dur=0.3)

    r1, r2 = step(r"T^{-1}", "undo turn", C.back, 1.05), step(r"L^{-1}", "undo lean", C.back, 0.25)
    r3 = step("= I", "", C.home, -0.6)
    m.play(FadeIn(r1, shift=0.06 * RIGHT), at=T.right, dur=0.45)
    m.play(FadeIn(r2, shift=0.06 * RIGHT), at=T.then_l, dur=0.45)
    m.play(FadeIn(r3), at=T.lines_up, dur=0.5)
    m.play(FadeOut(VGroup(s_lean, s_turn, r1, r2, r3)), at=T.lines_up + 0.85, dur=0.6)

    # ── a film, played backward ──
    fwd = VGroup(varrow((XS[0] + 0.7, 2.92), (XS[1] - 0.7, 2.92), C.fwd, width=3.0), tex("L", size=44, color=C.fwd).move_to([(XS[0] + XS[1]) / 2, 3.26, 0]),
                 varrow((XS[1] + 0.7, 2.92), (XS[2] - 0.7, 2.92), C.fwd, width=3.0), tex("T", size=44, color=C.fwd).move_to([(XS[1] + XS[2]) / 2, 3.26, 0]))
    m.play(FadeIn(fwd), at=T.film - 0.3, dur=0.5)

    head = Rectangle(width=W + 0.14, height=H + 0.14, stroke_color=C.back, stroke_width=4.0).move_to([XS[2], CY, 0])
    m.play(Create(head), at=T.film + 0.1, dur=0.4)
    b1 = VGroup(varrow((XS[2] - 0.7, -1.18), (XS[1] + 0.7, -1.18), C.back, width=3.0),
                tex(r"T^{-1}", size=44, color=C.back).move_to([(XS[1] + XS[2]) / 2, -1.58, 0]))
    b2 = VGroup(varrow((XS[1] - 0.7, -1.18), (XS[0] + 0.7, -1.18), C.back, width=3.0),
                tex(r"L^{-1}", size=44, color=C.back).move_to([(XS[0] + XS[1]) / 2, -1.58, 0]))
    m.play(head.animate.move_to([XS[1], CY, 0]), FadeIn(b1), at=T.film + 0.6, dur=0.7, ease=EASE)
    m.play(head.animate.move_to([XS[0], CY, 0]), FadeIn(b2), at=T.chain - 0.05, dur=0.7, ease=EASE)

    # ── the rule: each link inverted, and their order swapped ──
    eq = tex(r"(TL)^{-1}", "=", r"L^{-1}", r"T^{-1}", size=72, color=C.back).move_to([0, -2.85, 0])
    eq[1].set_color(C.text)
    tok_t, tok_l = eq[3].copy().move_to(eq[2]).set_color(C.wrong), eq[2].copy().move_to(eq[3]).set_color(C.wrong)
    m.play(FadeIn(eq[0]), FadeIn(eq[1]), at=T.chain + 0.5, dur=0.6)
    m.play(FadeIn(tok_t), FadeIn(tok_l), at=T.reverse_o - 1.2, dur=0.6)
    m.play(Transform(tok_t, eq[3].copy(), path_arc=PI), Transform(tok_l, eq[2].copy(), path_arc=PI), at=T.reverse_o + 0.1, dur=0.9, ease=EASE)

    # ── one simple move at a time ──
    m.play(head.animate.move_to([XS[2], CY, 0]), at=T.broken, dur=0.8, ease=EASE)
    m.play(head.animate.move_to([XS[1], CY, 0]), at=T.rewind_it + 0.2, dur=0.6, ease=EASE)
    m.play(head.animate.move_to([XS[0], CY, 0]), at=T.simple + 0.5, dur=0.6, ease=EASE)
    s.solid(C.bg, z=50, opacity=key(T.cut_four - 0.42, 0.0, 1.0, dur=0.4, lead=0))
