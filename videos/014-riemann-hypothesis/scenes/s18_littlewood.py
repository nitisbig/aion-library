"""s18 littlewood (P36): chapter 5 opens. Ten trillion zeros checked is a sliver: the bracket on the line of zeros
squeezes to its base while the line runs on. Then pi(x) - li(x), scaled by ln x / sqrt x so its sign stays readable,
on a log axis: real data to 10^6 (computed here; always below zero). Littlewood, 1914: it changes sign infinitely
often. The axis zooms out across 300 orders of magnitude; past 10^6 the curve is schematic (dashed, labeled). No flip
below 10^19 (Buthe 2015); a flip near 1.4 x 10^316 (Saouter-Demichel 2010), so the first one lies in between.
Builders live in littlewood.py, so s19 can open on this scene's last frame."""
from aion import *

from beats import T
from littlewood import K_END, SQUEEZE, labels, marks, plot_mob, zline
from look import EASE, chapter_card, live


@scene(T.cut_littlewood, T.cut_noproduct)
def s18_littlewood(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    wz = s.manim(z=3)                      # the line of zeros
    wp = s.manim(z=2)                      # the plot
    h = s.manim(z=6, parallax=0.0)         # formulas, names, labels
    card = s.manim(z=8, parallax=0.0)
    chapter_card(card, T.cut_littlewood, r"10^{13}<\infty", "Why it is so hard", out=T.l_ten - 0.15)
    lb = labels()

    # ── ten trillion zeros checked: a bracket on the line ──
    line = zline()
    sq = keys((T.l_inf - L, 1.0), (T.l_inf - L + 2.0, SQUEEZE, "in_out_sine"), lead=0)
    m0 = marks(1.0)
    wz.play(Create(line), FadeIn(m0[0]), at=T.l_ten + 0.1, dur=0.7, lead=0)
    wz.play(Create(m0[1]), at=T.l_ten + 0.5, dur=0.6, lead=0)
    h.play(FadeIn(lb.chk, shift=0.06 * LEFT), at=T.l_ten + 0.8, dur=0.5, lead=0)
    wz.remove(m0[0], m0[1], at=T.l_inf - L)        # added as parts, so removed as parts
    live(wz, lambda t: marks(float(sq(t))), (T.l_inf - L, T.l_inf - L + 2.0))
    h.play(lb.chk.animate.move_to(lb.chk_end), at=T.l_inf, dur=2.0, ease="in_out_sine")
    h.play(FadeIn(lb.inf, shift=0.1 * UP), at=T.l_inf + 1.4, dur=0.6, lead=0)

    # ── the prime count stays below li for every number checked ──
    zoom = (T.l_first - 0.2, T.l_digits + 0.7)
    u = keys((zoom[0], 0.0), (zoom[1], 1.0, EASE), lead=0)
    draw = keys((T.l_stays - L, 1.0), (T.l_stays + 1.6, 6.0, "in_out_sine"), lead=0)
    a19 = keys((T.l_quint - L, 0.0), (T.l_quint + 0.4, 1.0), lead=0)

    def plot(t):
        return plot_mob(6.0 * (K_END / 6.0) ** float(u(t)), float(draw(t)), float(a19(t)))

    p0 = plot(T.l_fail)
    wp.play(FadeIn(p0), at=T.l_fail - 1.6, dur=0.6, lead=0)
    wp.remove(p0, at=T.l_stays - L)
    live(wp, plot, (T.l_stays - L, T.l_stays + 1.6), (zoom[0], zoom[1] + 0.5))
    h.play(FadeIn(lb.ylab), at=T.l_fail - 1.3, dur=0.6, lead=0)
    h.play(FadeIn(lb.below[0], shift=0.06 * DOWN), at=T.l_stays, dur=0.6)
    h.play(FadeIn(lb.below[1]), at=T.l_checked, dur=0.5)

    # ── Littlewood, 1914: the order flips infinitely often ──
    h.play(FadeIn(lb.who, shift=0.06 * DOWN), at=T.l_little, dur=0.6)
    h.play(lb.below.animate.set_opacity(0.45), at=T.l_flips, dur=0.5)
    h.play(FadeIn(lb.flips[0], shift=0.06 * DOWN), at=T.l_flips + 0.2, dur=0.6)
    h.play(FadeIn(lb.flips[1]), at=T.l_often, dur=0.5)

    # ── past 10^6, schematic; no flip below 10^19; a known flip near 1.4 x 10^316 ──
    h.play(FadeIn(lb.sch), at=zoom[0] + 1.6, dur=0.5, lead=0)
    wp.play(Create(lb.mark), at=zoom[1] + 0.1, dur=0.5, lead=0)
    h.play(FadeIn(lb.flip_lab), at=zoom[1] + 0.3, dur=0.5, lead=0)
    wp.play(FadeIn(lb.band), at=zoom[1] + 0.9, dur=0.6, lead=0)
    h.play(FadeIn(lb.first), at=zoom[1] + 1.1, dur=0.5, lead=0)
