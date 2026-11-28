"""s09 complex (P19-P20): Riemann, 1859: the nine real pages of the paper (Monatsberichte scan) fan out beside his portrait.
Then s = sigma + it as a point in a plane, with dashed projections. Each term 1/n^s = n^-sigma e^(-i theta),
theta = t ln n, is an arrow: sigma sets the lengths, t turns them (arrow n by t ln n). Laid end to end, the arrows
curl into a spiral that closes in on zeta(1.4 + 6i). Every arrow is computed from n^-s; the push is drawn, not scaled."""
from aion import *

from beats import T
from media_assets import paper_page_thumb, portrait_card
from look import (EASE, S_SPIRAL, caps, lab, oplane_mob, pin, probe_mob, re_gt1_mobs, s_formula, spiral_mob,
                  splane_mob, term_formula, tex, zeta_label, zeta_mark)

S0 = 1.4 + 3.0j                            # where the probe first lands


@scene(T.cut_complex, T.cut_coloring)
def s09_complex(s):
    s.solid(C.bg, z=-200)
    hist = s.manim(z=2, parallax=0.0)      # the 1859 card
    op = s.manim(z=3)                      # the output plane: arrows and spiral
    sp = s.manim(z=4, parallax=0.0)        # the s-plane panel and the probe
    h = s.manim(z=6, parallax=0.0)         # formulas and tags

    # ── 1859: the real nine pages (Monatsberichte scan) fan out; Riemann beside them ──
    PH_ = 4.4
    gone = T.complex_s - 0.35
    centre = np.array([-3.6, 0.0])
    fan = keys((T.nine_page - 0.1, 0.0), (T.nine_page + 1.1, 1.0, EASE), lead=0)
    for k in range(9, 0, -1):                                           # page 1 on top
        def pos_k(t, k=k):
            f = float(fan(t))
            return tuple(centre + f * np.array([0.34 * (k - 1) - 1.36, -0.04 * (k - 1)]))
        op_k = keys((T.y1859 - 0.1, 0.0), (T.y1859 + 0.6, 1.0), (gone, 1.0), (gone + 0.5, 0.0), lead=0)
        s.add(ArrayLayer(paper_page_thumb(k), height=PH_, pos=pos_k, z=2.0 - 0.01 * k, parallax=0.0, opacity=op_k))
    portrait_card(s, hist, "riemann", r"B. Riemann $\cdot$ 1859", T.y1859 + 1.2, gone + 0.5, (3.3, 0.35), height=3.4,
                  name_size=40)
    nine = tex(r"9", size=44, color=C.human)
    nine_l = lab("pages", 28, C.human)
    nine_g = VGroup(nine, nine_l).arrange(RIGHT, buff=0.15, aligned_edge=DOWN).move_to([centre[0], -2.75, 0])
    hist.play(FadeIn(nine_g, shift=0.06 * UP), at=T.nine_page + 0.6, dur=0.5)
    hist.play(FadeOut(nine_g), at=gone, dur=0.5, lead=0)

    # ── s = sigma + it: a point in a plane ──
    s_eq = s_formula()
    h.play(Write(s_eq), at=T.complex_s + 0.7, dur=1.0)
    plane = splane_mob()
    sp.play(Create(plane.grid), Create(plane.axes), FadeIn(plane.ticks), at=T.point_plane, dur=1.0)

    sig = keys((T.length - C.lead, 1.4), (T.length + 0.55, 2.0, EASE), (T.length + 1.25, 1.4, EASE), lead=0)
    tau = keys((T.arrow - C.lead, S0.imag), (T.arrow + 0.85, 0.0, EASE), (T.turns + 0.75, 0.0),
               (T.turns + 3.35, S_SPIRAL.imag, "in_out_sine"), lead=0)
    s_of = lambda t: complex(float(sig(t)), float(tau(t)))      # noqa: E731
    show_sig = key(T.how_right - 0.7, 0.0, 1.0, dur=0.6, lead=0)    # on "real part"
    show_t = key(T.how_high - 0.8, 0.0, 1.0, dur=0.6, lead=0)       # on "imaginary part"
    p0 = probe_mob(s_of(T.point_plane), 0.0, 0.0)
    sp.play(FadeIn(p0, scale=0.8), at=T.point_plane + 0.7, dur=0.5)
    sp.remove(p0, at=T.how_right - 0.7)
    sp.redraw(lambda t: probe_mob(s_of(t), float(show_sig(t)), float(show_t(t))), during=(T.how_right - 0.7, T.cut_coloring))

    # ── each term is an arrow: 1/n^s = n^-sigma e^(-i theta), theta = t ln n ──
    tf = term_formula()
    term, ang, length, angle = tf.term, tf.ang, tf.length, tf.angle
    h.play(Write(term), at=T.arrow, dur=1.0)
    rest = oplane_mob(0.0)
    op.play(Create(rest), at=T.arrow, dur=0.8)
    h.play(FadeIn(length, shift=0.06 * UP), at=T.length, dur=0.5)
    h.play(Indicate(term[2], color=C.s_in, scale_factor=1.15), at=T.length + 0.1, dur=1.0)
    h.play(FadeIn(ang), FadeIn(angle, shift=0.06 * UP), at=T.turns + 0.75, dur=0.6)
    h.play(Indicate(ang[3], color=C.s_in, scale_factor=1.2), at=T.log_n + 0.2, dur=1.0)

    # ── five arrows from 0 (a fan); then end to end, and on into a spiral that closes in on zeta(s) ──
    n_fan = key(T.arrow + 0.5, 0.0, 5.0, dur=1.0, ease="linear", lead=0)
    n_log = key(T.spiral - 0.6, np.log10(5.0), np.log10(4000.0), dur=T.closes_in + 2.0 - (T.spiral - 0.6),
                ease="in_out_sine", lead=0)
    chain = key(T.end_to_end + 0.3, 0.0, 1.0, dur=1.3, ease=EASE, lead=0)
    push = key(T.closes_in - 0.15, 0.0, 1.0, dur=2.2, ease=EASE, lead=0)

    def n_of(t):
        return float(n_fan(t)) if t < T.spiral - 0.6 else 10.0 ** float(n_log(t))

    op.redraw(lambda t: spiral_mob(s_of(t), n_of(t), float(push(t)), float(chain(t))),
              during=(T.arrow + 0.5, T.cut_coloring))
    grid = (T.closes_in - 0.15, T.closes_in + 2.05)
    op.remove(rest, at=grid[0])
    op.redraw(lambda t: oplane_mob(float(push(t))), during=grid)    # the grid follows the push (drawn, not scaled)

    # ── when the real part is more than one, the spiral closes ──
    gt = re_gt1_mobs()
    sp.play(FadeIn(gt.half), Create(gt.line), at=T.more_than_one, dur=0.8)
    sp.play(FadeIn(gt.label), at=T.more_than_one + 0.5, dur=0.6, lead=0)

    mark = zeta_mark(1.0)
    op.play(FadeIn(mark[1], scale=0.5), Create(mark[0]), at=T.closes_in + 2.05, dur=0.6)
    zl = zeta_label(1.0)
    op.play(Create(zl.leader), FadeIn(zl.card, shift=0.06 * LEFT), at=T.closes_in + 2.35, dur=0.6)
