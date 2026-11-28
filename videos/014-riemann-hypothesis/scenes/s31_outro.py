"""s31 outro (P53-P54): back to the staircase. The s02 frame returns: the staircase, the curve rebuilt from 100 zero
pairs lying on it, the line of zeros. Each wave from one zero (the dots ripple); if every zero is on the line, every
wave grows like sqrt(x) and the curve never strays far. 1859: Riemann's "very likely" card, small; 1859 -> 2026,
167 years. A proof mathematicians are only beginning to read: the plot fades and only the line of
zeros is left, running out of the frame, as in the first shot. Then black."""
from aion import *

from beats import T
from look import (EASE, GAM, ZX, caps, lab, pin, seen, staircase_frame, tex, zero_line, zero_line_lit, zy, TOP_INF)


@scene(T.cut_outro, T.end)
def s31_outro(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    up = (T.cut_outro + 0.3, T.oo_back + 0.6)
    gone = (T.oo_read - 0.2, T.oo_read + 1.4)
    last = (T.end - 1.4, T.end - 0.1)
    plot_op = keys((up[0], 0.0), (up[1], 1.0), (T.oo_holds - 0.2, 1.0), (T.oo_holds + 0.6, seen(0.45)),
                   (gone[0], seen(0.45)), (gone[1], 0.0), lead=0)
    wp = s.manim(z=2, opacity=plot_op)
    wz = s.manim(z=3, opacity=keys((up[0], 0.0), (up[1], 1.0), (last[0], 1.0), (last[1], 0.0), lead=0))
    h = s.manim(z=6, parallax=0.0, opacity=keys((last[0], 1.0), (last[1], 0.0), lead=0))

    # ── the s02 frame returns ──
    frame = staircase_frame()
    wp.add(frame)
    zl = zero_line_lit()
    wz.add(zl)

    # ── built exactly from waves, one for each zero ──
    formula = tex(r"\pi(x)", r"=", r"R(x)", r"-", r"\sum\nolimits_\rho R(x^\rho)", size=44,
                  colors={0: C.prime, 2: C.smooth, 4: C.zero})
    small = lab("+ small terms", 28, C.muted)
    top = VGroup(formula, small).arrange(RIGHT, buff=0.25)
    pin(top, top=3.55, left=-5.9)
    h.play(Write(formula), at=T.oo_built - 0.3, dur=1.4)
    h.play(FadeIn(small), at=T.oo_built + 1.0, dur=0.5, lead=0)
    dots = zl.dots
    wz.play(LaggedStart(*[Indicate(d, color=C.zero, scale_factor=2.2) for d in dots[:60]], lag_ratio=0.03),
            at=T.oo_each, dur=1.6)

    # ── if every zero is on the line, every wave grows like sqrt(x) ──
    flash = Line([ZX, -3.5, 0], [ZX, TOP_INF, 0]).set_stroke(C.crit, width=8.0)
    wz.play(ShowPassingFlash(flash, time_width=0.5), at=T.oo_if + 0.4, dur=1.2, lead=0)
    half = tex(r"\mathrm{Re}\,\rho=\tfrac12", size=32, color=C.crit)
    half.move_to([ZX - 0.25 - half.width / 2, 2.4, 0])
    h.play(FadeIn(half, shift=0.06 * RIGHT), at=T.oo_if + 0.8, dur=0.5)
    grow = tex(r"|x^\rho|=\sqrt{x}", size=34, color=C.zero)
    pin(grow, top=2.65, left=-5.9)
    h.play(FadeIn(grow, shift=0.06 * DOWN), at=T.oo_slowly, dur=0.6)
    wp.play(Indicate(frame.pink, color=C.zero, scale_factor=1.0), at=T.oo_never, dur=1.0)
    h.play(FadeOut(VGroup(top, grow, half)), at=T.oo_1859 - 0.5, dur=0.5, lead=0)

    # ── 1859: Riemann put the search aside; 167 years later ──
    de = Tex(r"\textit{\dots sehr wahrscheinlich \dots}", font_size=32, color=C.human)
    yr = caps(r"B. Riemann $\cdot$ 1859", 26, C.ink)
    card = VGroup(de, yr).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    pin(card, top=3.5, left=-5.9)
    h.play(FadeIn(card, shift=0.06 * UP), at=T.oo_1859 + 0.3, dur=0.6)
    tl = VGroup(caps("1859", 30, C.ink), Line(ORIGIN, 3.6 * RIGHT, color=C.muted, stroke_width=1.6),
                caps("2026", 30, C.ink)).arrange(RIGHT, buff=0.25)
    tl.move_to([2.4, -1.7, 0])
    yrs = lab("167 years", 26, C.muted).next_to(tl[1], UP, buff=0.12)
    h.play(FadeIn(tl[0]), Create(tl[1]), at=T.oo_holds, dur=1.0)
    h.play(FadeIn(tl[2]), FadeIn(yrs), at=T.oo_167 - 0.4, dur=0.6)

    # ── a proof mathematicians are only beginning to read: the wall, faint; then only the line is left ──
    h.play(FadeOut(VGroup(card, tl, yrs)), at=gone[0], dur=1.2, lead=0)
