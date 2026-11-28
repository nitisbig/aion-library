"""s26 lean (P45-P46): what a Lean check guarantees. A proof as a chain of steps, each pointing back to earlier ones,
down to Lean's three axioms; the kernel (a small teal box) walks the chain and ticks every step. What it can't say: does
the statement mean what we think? Mathlib's RiemannHypothesis, verbatim, each part mapped to its maths; K. Buzzard's
first question docks top right (it stays through s28); + 4 theorems for Dirichlet L-functions; riemannZeta comes from
Mathlib, so the definitions need checking too. Everything fades except the Buzzard card."""
from aion import *

from beats import T
from media_assets import portrait_card
from leanproof import ORDER, chain, code, four_chip, maths, mathlib_box
from look import EASE, caps, lab, live
from status import buzzard_card, ring


@scene(T.cut_lean, T.cut_robin)
def s26_lean(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_robin - 0.5, T.cut_robin - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    bz = s.manim(z=7, parallax=0.0)        # the Buzzard card stays into s27

    # ── November: what Lean checks ──
    date = caps(r"20 $\cdot$ XI $\cdot$ 2026", 34, C.ink).move_to([0, 3.2, 0])
    h.play(FadeIn(date), at=T.ln_nov, dur=0.5)
    h.play(FadeOut(date), at=T.ln_defs - 0.3, dur=0.4)
    head = lab("definitions, statements, proofs: all code", 30, C.text).move_to([-3.0, 3.2, 0])
    h.play(FadeIn(head, shift=0.06 * DOWN), at=T.ln_defs, dur=0.5)

    boxes, arrows = chain()
    order = sorted(boxes)                                 # bottom-up, left to right
    w.play(LaggedStart(*[FadeIn(boxes[k], shift=0.1 * UP) for k in order], lag_ratio=0.18), at=T.ln_defs + 0.4,
           dur=1.6)
    w.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.06), at=T.ln_code, dur=1.0)
    ax_lab = lab("axioms", 24, C.lean).next_to(boxes[(0, 2)], RIGHT, buff=0.35)

    # ── the kernel walks the chain and ticks each step ──
    walk = (T.ln_each - 0.3, T.ln_each + 2.7)
    pts = [boxes[k][0].get_right() + [0.3, 0, 0] for k in ORDER]
    start = boxes[(1, 0)][0].get_left() + [-0.35, -0.0, 0]
    step = (walk[1] - walk[0]) / len(pts)
    kk = [(walk[0], tuple(start))]
    for i, p in enumerate(pts):
        kk.append((walk[0] + (i + 0.6) * step, tuple(p), EASE))
        kk.append((walk[0] + (i + 1) * step, tuple(p)))
    kpos = keys(*kk, lead=0)

    def kernel(t):
        return Square(side_length=0.24, stroke_width=0, fill_color=C.lean, fill_opacity=1.0).move_to(
            [*np.asarray(kpos(t))[:2], 0])

    k0 = kernel(walk[0])
    klab = lab("kernel", 24, C.lean).next_to(k0, LEFT, buff=0.15)
    w.play(FadeIn(k0, scale=0.6), FadeIn(klab), at=T.ln_kernel + 0.4, dur=0.5)
    w.remove(k0, at=walk[0])
    w.play(FadeOut(klab), at=walk[0], dur=0.3, lead=0)
    held = live(w, kernel, walk)
    ticks = VGroup()
    for i, k in enumerate(ORDER):
        tk = ring(True, r=0.1).move_to(boxes[k][0].get_corner(UR) + [0.0, 0.0, 0])
        ticks.add(tk)
        w.play(FadeIn(tk, scale=0.5), at=walk[0] + (i + 0.6) * step, dur=0.25, lead=0)
    h.play(FadeIn(ax_lab), at=T.ln_axioms, dur=0.5)
    w.play(Indicate(VGroup(*[boxes[(0, i)] for i in range(3)]), color=C.lean, scale_factor=1.06), at=T.ln_axioms,
           dur=0.9)

    # ── if the kernel accepts, a broken step is very unlikely ──
    acc = VGroup(lab("kernel accepts", 32, C.lean), ring(True, r=0.16)).arrange(RIGHT, buff=0.25)
    acc.move_to([2.9, 1.0, 0])
    h.play(FadeIn(acc, shift=0.06 * LEFT), at=T.ln_accepts + 0.3, dur=0.5)
    brk = lab("a broken step: very unlikely", 28, C.muted).next_to(acc, DOWN, buff=0.3, aligned_edge=LEFT)
    h.play(FadeIn(brk), at=T.ln_broken, dur=0.5)

    # ── what it can't tell you: does the statement mean what you think? ──
    clear = T.ln_cant - 0.2
    w.play(FadeOut(VGroup(*boxes.values(), arrows, ticks, held[-1])), at=clear, dur=0.6, lead=0)
    h.play(FadeOut(VGroup(head, ax_lab, acc, brk)), at=clear, dur=0.6, lead=0)
    q = lab("does the statement mean what you think?", 30, C.text).move_to([-2.4, 3.2, 0])
    h.play(FadeIn(q, shift=0.06 * DOWN), at=T.ln_cant + 0.6, dur=0.5)
    c = code()
    h.play(LaggedStart(*[Write(l) for l in c.lines], lag_ratio=0.5), at=T.ln_means, dur=2.0)

    card = buzzard_card()
    h.play(FadeOut(q), at=T.ln_buzzard - 0.4, dur=0.4, lead=0)
    bz.play(FadeIn(card, shift=0.2 * LEFT), at=T.ln_first, dur=0.6)
    portrait_card(s, h, "buzzard", r"K. Buzzard $\cdot$ Imperial", T.ln_buzzard, T.ln_first + 0.4, (3.6, -0.6),
                  height=2.6)

    # ── here is the main statement: each part says something ──
    mp = maths(c)
    for i, (part, col, ln, m) in enumerate(mp):
        at = T.ln_main + 0.2 + 0.3 * i
        h.play(part.animate.set_color(col), Create(ln), FadeIn(m, shift=0.06 * RIGHT), at=at, dur=0.5, lead=0)

    # ── four more theorems: Dirichlet L-functions ──
    fc = four_chip()
    h.play(FadeIn(fc, shift=0.06 * UP), at=T.ln_four, dur=0.5)

    # ── zeta is Mathlib's: part of the job is confirming the definitions ──
    mb, arr = mathlib_box(c)
    h.play(GrowArrow(arr), FadeIn(mb[0]), FadeIn(mb[1][0]), at=T.ln_mathlib - 0.3, dur=0.6)
    h.play(FadeIn(mb[1][1]), at=T.ln_library, dur=0.5)
    h.play(Indicate(mb, color=C.lean, scale_factor=1.06), at=T.ln_job + 0.6, dur=1.0)
