"""s25 august (P44): chapter 7's card. The s21 bar returns at 5/12 (2020). August 2026: the fill jumps to 2/3 (at
least two thirds of the zeros are simple and on the line; Alpoge & Furman, arXiv 2608.13637).
A chain of icons names who did what: Claude found it, Alpoge and Furman checked and wrote it up, Conrey and Goldston
examined it, Lean checked it, Lamzouri gave an independent, simpler proof. Then Anthropic's own caveat, in gray.
Ends on black."""
from aion import *

from beats import T
from media_assets import svg_logo
from look import EASE, caps, chapter_card, lab, live, tex
from progress import BH, BY, bar_frame, bx, fill_mob
from status import chip, ring


@scene(T.cut_august, T.cut_lean)
def s25_august(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_lean - 0.5, T.cut_lean - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    cc = s.manim(z=8, parallax=0.0)
    chapter_card(cc, T.cut_august, r"2026", "Back to November", out=T.au_aug - 0.3)

    # ── the bar, where s21 left it: 5/12 (2020) ──
    bar = bar_frame()
    f512 = fill_mob(5 / 12)
    t512 = VGroup(Line([bx(5 / 12), BY - BH / 2, 0], [bx(5 / 12), BY - BH / 2 - 0.25, 0], color=C.muted,
                       stroke_width=1.4),
                  tex(r"\tfrac{5}{12}", size=28, color=C.muted).move_to([bx(5 / 12), BY - BH / 2 - 0.52, 0]),
                  caps("2020", 22, C.muted).move_to([bx(5 / 12) - 0.62, BY - BH / 2 - 0.52, 0]))
    on = T.au_aug - 0.1
    w.play(FadeIn(bar.box), FadeIn(bar.ends), FadeIn(f512), at=on, dur=0.6, lead=0)
    h.play(FadeIn(bar.title), FadeIn(t512), at=on + 0.2, dur=0.6, lead=0)

    # ── who did what, as a chain of icons (one or two words each) ──
    NX = [-5.0, -2.5, 0.0, 2.5, 5.0]
    IY, LY = -0.95, -1.8

    def doc(color, tick=False):
        pg = RoundedRectangle(width=0.56, height=0.74, corner_radius=0.05, stroke_color=color, stroke_width=2.0)
        lines = VGroup(*[Line([-0.17, 0, 0], [0.17 if i % 3 != 2 else 0.04, 0, 0], color=color, stroke_width=1.6)
                         for i in range(4)]).arrange(DOWN, buff=0.1).move_to(pg)
        g = VGroup(pg, lines)
        if tick:
            g.add(ring(True, r=0.13).move_to(pg.get_corner(DR) + [0.02, 0.02, 0]))
        return g

    def lens(color):
        c_ = Circle(radius=0.24, stroke_color=color, stroke_width=2.4)
        hd = Line(c_.point_at_angle(-PI / 4), c_.point_at_angle(-PI / 4) + 0.26 * np.array([1, -1, 0]) / np.sqrt(2),
                  color=color, stroke_width=4)
        return VGroup(c_, hd)

    def pair(a_, b_):
        return VGroup(caps(a_, 24, C.ink), caps(b_, 24, C.ink)).arrange(DOWN, buff=0.08)

    icons = [svg_logo("claude_symbol.svg", 0.72, C.ai), doc(C.human), lens(C.human),
             ring(True, r=0.3), doc(C.human, tick=True)]
    names = [lab("Claude", 26, C.ai), pair(r"Alp\"oge", r"\& Furman"), pair("Conrey", r"\& Goldston"),
             lab("Lean", 26, C.lean), caps(r"Lamzouri", 24, C.ink)]
    nodes = []
    for k, (ic, nm) in enumerate(zip(icons, names)):
        ic.move_to([NX[k], IY, 0])
        nm.move_to([NX[k], LY, 0]).align_to([0, LY + 0.17, 0], UP)
        nodes.append(VGroup(ic, nm))
    links = [Arrow([NX[k] + 0.55, IY, 0], [NX[k + 1] - 0.55, IY, 0], buff=0, stroke_width=2, color=C.muted,
                   max_tip_length_to_length_ratio=0.12) for k in range(4)]
    h.play(FadeIn(nodes[0], shift=0.06 * UP), at=T.au_claude, dur=0.5)

    # ── from five twelfths to two thirds ──
    jump = (T.au_from, T.au_from + 1.2)
    f = keys((jump[0], 5 / 12), (jump[1], 2 / 3, EASE), lead=0)
    w.remove(f512, at=jump[0])
    live(w, lambda t: fill_mob(float(f(t))), jump)
    mk = VGroup(Line([bx(2 / 3), BY + BH / 2, 0], [bx(2 / 3), BY + BH / 2 + 0.22, 0], color=C.ai, stroke_width=2),
                caps("Aug 2026", 24, C.ai))
    mk[1].move_to([bx(2 / 3), BY + BH / 2 + 0.45, 0])
    h.play(FadeIn(mk, shift=0.06 * DOWN), at=T.au_from + 0.2, dur=0.5)
    two = VGroup(tex(r"\ge\tfrac23", size=34, color=C.crit), lab("simple and on the line", 24, C.text))
    two.arrange(RIGHT, buff=0.2, aligned_edge=DOWN)
    two.move_to([bx(2 / 3) + 0.15 + two.width / 2, BY - BH / 2 - 0.5, 0])
    arx = lab("arXiv 2608.13637", 20, C.muted).next_to(two, DOWN, buff=0.12, aligned_edge=LEFT)
    w.play(Create(Line([bx(2 / 3), BY - BH / 2, 0], [bx(2 / 3), BY - BH / 2 - 0.3, 0], color=C.crit,
                       stroke_width=1.6)), at=T.au_two + 0.3, dur=0.3)
    h.play(FadeIn(two, shift=0.06 * RIGHT), at=T.au_two + 0.4, dur=0.5)
    h.play(FadeIn(arx), at=T.au_two + 0.8, dur=0.4)

    # ── who checked what ──
    for k, at_ in ((1, T.au_alpoge), (2, T.au_conrey - 0.2), (3, T.au_lean), (4, T.au_lamzouri)):
        h.play(GrowArrow(links[k - 1]), at=at_ - 0.2, dur=0.4)
        h.play(FadeIn(nodes[k], shift=0.06 * UP), at=at_, dur=0.5)
    sep = caps("Sep 2026", 20, C.muted).next_to(nodes[4], DOWN, buff=0.12)
    h.play(FadeIn(sep), at=T.au_simpler + 0.4, dur=0.4)

    # ── Anthropic's own caveat ──
    cav = chip("Anthropic: not expected to lead to the full hypothesis", C.conj, size=26)
    cav.move_to([0, -3.2, 0])
    h.play(FadeIn(cav, shift=0.06 * UP), at=T.au_expect, dur=0.6)
