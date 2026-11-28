"""s23 meaning (P41-P42): chapter 6's card. Solving it means one of two things: a proof covering every zero at once
(a bracket over the whole line while the real zeros stream past, far beyond any computer) or a single zero off the line
(a rogue mirror pair, "what if"), forall vs exists. A shelf of results that begin "assume RH" (Schoenfeld's bound,
Cramer's gap bound, many more): on "unconditional" their tags fade. One more card needs GRH (Miller's primality test),
and faint critical lines fan out, one per L-function. Then encryption: N = 3233 = 53 x 61; an arrow from "how the
primes are spread" to "factor N", struck through. Ends on black (s24 is a different idea)."""
from aion import *

from beats import T
from look import EASE, GAM, caps, chapter_card, lab, live, tex

LX, RX = -3.3, 3.3                       # the two lines: proof (left), counterexample (right)
ZB, ZT = -2.35, 4.2                      # the lines run from ZB up out of frame
K = 0.115                                # screen units per unit of height t
ROGUE = 0.9                              # Re 0.8 is 0.3 right of the line: 0.3 x 3 units


def zero_dots(x, off, color=None):
    ys = ZB + 0.25 + K * (GAM - off)
    keep = (ys > ZB + 0.05) & (ys < ZT)
    return VGroup(*[Dot([x, y, 0], radius=0.052, color=color or C.zero) for y in ys[keep]])


def card(math, who, tag, x, y=1.45, w=3.05, h=1.9):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.08, stroke_color=C.muted, stroke_width=1.6)
    m = math if isinstance(math, Mobject) else tex(math, size=28)
    m.scale_to_fit_width(min(m.width, w - 0.35))
    name = caps(who, 22, C.ink)
    body = VGroup(m, name).arrange(DOWN, buff=0.3).move_to([0, -0.08, 0])
    t = lab(tag, 20, C.conj)
    tg = VGroup(SurroundingRectangle(t, buff=0.07, corner_radius=0.05, stroke_color=C.conj, stroke_width=1.2), t)
    g = VGroup(box, body)
    g.move_to([x, y, 0])
    tg.move_to(box.get_corner(UR) + [-tg.width / 2 - 0.1, -tg.height / 2 - 0.1, 0])
    g.tag = tg
    return g


@scene(T.cut_meaning, T.cut_spacing)
def s23_meaning(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_spacing - 0.5, T.cut_spacing - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    cc = s.manim(z=8, parallax=0.0)
    chapter_card(cc, T.cut_meaning, r"\forall\rho\ \ \text{or}\ \ \exists\rho", "What solving it would mean",
                 out=T.q_solving - 0.2)

    # ── a proof covers every zero at once, even the ones no computer will reach ──
    lline = Line([LX, ZB, 0], [LX, ZT, 0], color=C.crit, stroke_width=3)
    rline = Line([RX, ZB, 0], [RX, ZT, 0], color=C.crit, stroke_width=3)
    w.play(Create(lline), at=T.q_solving + 0.2, dur=0.8)
    d0 = zero_dots(LX, 0.0)
    w.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in d0], lag_ratio=0.08), at=T.q_solving + 0.6, dur=0.9)
    run = (T.q_every - 0.2, T.q_single - 0.6)
    off = keys((run[0], 0.0), (run[1], float(GAM[-1]) - 60, "in_cubic"), lead=0)
    w.remove(*d0, at=run[0])
    held = live(w, lambda t: zero_dots(LX, float(off(t))), run)
    br = VMobject(color=C.text, stroke_width=2.6)
    br.set_points_as_corners([[LX - 0.2, ZB, 0], [LX - 0.35, ZB, 0], [LX - 0.35, ZT, 0], [LX - 0.2, ZT, 0]])
    w.play(Create(br), at=T.q_proof + 0.3, dur=1.5)
    fa = tex(r"\forall\rho:\ \ \mathrm{Re}\,\rho=\tfrac12", size=36, colors={0: C.zero})
    fa.move_to([LX, -2.95, 0])
    proof = lab("proof", 30, C.text).move_to([LX, -3.55, 0])
    h.play(Write(fa), at=T.q_every, dur=1.0)
    h.play(FadeIn(proof), at=T.q_every + 0.6, dur=0.5)
    past = lab("beyond any computer", 24, C.muted).move_to([LX + 1.75, 2.6, 0])
    h.play(FadeIn(past, shift=0.06 * UP), at=T.q_ones + 0.6, dur=0.5)

    # ── or a single zero off the line, which would disprove it ──
    rdots = zero_dots(RX, 0.0)
    w.play(Create(rline), FadeIn(rdots), at=T.q_single - 0.5, dur=0.6, lead=0)
    yr = ZB + 0.25 + K * (0.5 * (GAM[3] + GAM[4]))          # between two real zeros
    rog = VGroup(Dot([RX + ROGUE, yr, 0], radius=0.08, color=C.rogue),
                 Dot([RX - ROGUE, yr, 0], radius=0.08, color=C.rogue))
    w.play(FadeIn(rog, scale=0.4), at=T.q_single + 0.3, dur=0.5)
    wif = lab("what if", 24, C.rogue).move_to([RX + ROGUE + 0.75, yr, 0])
    h.play(FadeIn(wif), at=T.q_single + 0.6, dur=0.4)
    ex = tex(r"\exists\rho:\ \ \mathrm{Re}\,\rho\ne\tfrac12", size=36, colors={0: C.rogue})
    ex.move_to([RX, -2.95, 0])
    dis = lab("disproof", 30, C.text).move_to([RX, -3.55, 0])
    h.play(Write(ex), at=T.q_single + 0.7, dur=1.0)
    h.play(FadeIn(dis), at=T.q_disprove, dur=0.5)
    clear = T.q_gap - 1.1
    w.play(FadeOut(VGroup(lline, rline, br, rog, held[-1], rdots)),
           at=clear, dur=0.5, lead=0)
    h.play(FadeOut(VGroup(fa, proof, past, wif, ex, dis)), at=clear, dur=0.5, lead=0)

    # ── a shelf of results that begin "assume the Riemann hypothesis" ──
    xs = (-4.85, -1.62, 1.62, 4.85)
    c1 = card(r"|\pi(x)-\mathrm{li}(x)|<\frac{\sqrt x\,\ln x}{8\pi}", r"L. Schoenfeld $\cdot$ 1976", "if RH", xs[0])
    c2 = card(r"p_{n+1}-p_n\le C\sqrt{p_n}\,\ln p_n", r"H. Cram\'er $\cdot$ 1920", "if RH", xs[1])
    c3 = card(tex(r"\cdots", size=48), "many more", "if RH", xs[2])
    c4 = card(lab("fast primality test", 28, C.text), r"G. Miller $\cdot$ 1976", "if GRH", xs[3])
    shelf = Line([-6.5, 0.4, 0], [6.5, 0.4, 0], color=C.muted, stroke_width=2)
    w.play(Create(shelf), at=T.q_gap - 0.5, dur=0.6, lead=0)
    for c, at in ((c1, T.q_gap), (c2, T.q_turn), (c3, T.q_turn + 0.4)):
        w.play(FadeIn(VGroup(c, c.tag), shift=0.3 * DOWN), at=at, dur=0.6)
    w.play(*[Indicate(c.tag, color=C.text, scale_factor=1.15) for c in (c1, c2, c3)], at=T.q_assume, dur=1.0)
    head = lab("if the hypothesis is proved", 30, C.text).move_to([0, 3.2, 0])
    h.play(FadeIn(head, shift=0.06 * DOWN), at=T.q_uncond - 0.4, dur=0.5)
    w.play(*[FadeOut(c.tag) for c in (c1, c2, c3)], at=T.q_uncond, dur=1.0)
    w.play(Indicate(c2[0], color=C.prime, scale_factor=1.04), at=T.q_gaps, dur=1.0)

    # ── some need a stronger version: GRH, the same claim for a family of functions ──
    w.play(FadeIn(VGroup(c4, c4.tag), shift=0.3 * DOWN), at=T.q_some, dur=0.6)
    fx, fy0, fy1, n = 2.9, -3.45, -0.35, 9
    xs_fan = np.linspace(0.4, 5.4, n)
    fan = keys((T.q_family - L, 0.0), (T.q_family + 1.0, 1.0, EASE), lead=0)

    def lines(t):
        u = float(fan(t))
        g = VGroup()
        for k, x in enumerate(xs_fan):
            if abs(x - fx) < 1e-6:
                continue
            g.add(Line([fx + u * (x - fx), fy0, 0], [fx + u * (x - fx), fy1, 0], color=C.crit, stroke_width=2,
                       stroke_opacity=0.35))
        return g

    zline = Line([fx, fy0, 0], [fx, fy1, 0], color=C.crit, stroke_width=3)
    zlab = tex(r"\zeta", size=30, color=C.zeta).move_to([fx + 0.28, fy1 - 0.2, 0])
    w.play(Create(zline), FadeIn(zlab), at=T.q_grh - 0.4, dur=0.6, lead=0)
    grh = VGroup(caps("GRH", 40, C.text), tex(r"L(s,\chi)=\sum_{n\ge1}\frac{\chi(n)}{n^s}", size=36))
    grh.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([-3.4, -1.9, 0])
    h.play(FadeIn(grh[0]), at=T.q_grh, dur=0.5)
    h.play(Write(grh[1]), at=T.q_grh + 1.0, dur=1.0)
    fl = live(w, lines, (T.q_family - L, T.q_family + 1.0))
    each = lab("one line for each", 24, C.muted).move_to([fx, fy0 - 0.25, 0])
    h.play(FadeIn(each), at=T.q_family + 0.9, dur=0.5)

    # ── a proof wouldn't break encryption ──
    go = T.q_break - 1.1
    w.play(FadeOut(VGroup(shelf, c1, c2, c3, c4, c4.tag, zline, zlab, fl[-1])), at=go, dur=0.5, lead=0)
    h.play(FadeOut(VGroup(head, grh, each)), at=go, dur=0.5, lead=0)
    N = tex(r"N", r"=", r"3233", r"=", r"53", r"\times", r"61", size=56, colors={4: C.prime, 6: C.prime})
    N.move_to([0, 1.9, 0])
    assert 53 * 61 == 3233
    left = VGroup(tex(r"\text{RH}", size=52), lab("how the primes are spread", 26, C.muted)).arrange(DOWN, buff=0.3)
    right = VGroup(lab("factor N", 40, C.text), lab("find 53 and 61", 26, C.muted)).arrange(DOWN, buff=0.3)
    left.move_to([-3.7, -0.9, 0])
    right.move_to([3.7, -0.9, 0])
    right[0].align_to(left[0], DOWN)
    arr = Arrow([-1.6, -0.75, 0], [1.6, -0.75, 0], color=C.text, stroke_width=3, buff=0)
    x = Cross(Square(0.6).move_to(arr.get_center()), stroke_color=C.gap, stroke_width=6)
    h.play(Write(N[:3]), at=go + 0.5, dur=0.8, lead=0)
    h.play(FadeIn(left[0]), FadeIn(right[0]), GrowArrow(arr), at=T.q_break - 0.2, dur=0.6)
    h.play(Create(x), at=T.q_break + 0.6, dur=0.5)
    h.play(FadeIn(left[1]), at=T.q_knowing + 0.3, dur=0.5)
    h.play(FadeIn(N[3:], shift=0.06 * LEFT), FadeIn(right[1]), at=T.q_knowing + 2.4, dur=0.6)
