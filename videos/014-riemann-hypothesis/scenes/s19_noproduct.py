"""s19 noproduct (P37): the zeros sit where the sum stops working. s18's line of zeros slides left and becomes
Re s = 1/2 of the colored plane. Right of Re s = 1 (lit) the Euler product converges: its partial products over the
primes up to 10^4 (inset) settle on zeta(2 + 10i), away from 0, so zeta can't be zero there. Slid into the strip
(1/2 + 10i), the same partial products wander, and with more primes leave the frame: the product no longer converges.
Every partial product is computed here from the primes."""
from aion import *

from beats import T
from littlewood import end_frame
from look import EASE, carded, live, probe_mob, tex
from noproduct import BOX, N0, N1, S_IN, S_STRIP, SHADER, TC, XH, parts, path_mob, primes, products, to_ins, to_p


@scene(T.cut_noproduct, T.cut_nearmiss)
def s19_noproduct(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    s.shader("zeta_domain.frag", z=0, animated=False, **SHADER,
             u_opacity=keys((T.n_sit + 0.5, 0.0), (T.n_sit + 1.6, 1.0, EASE), lead=0))
    wp = s.manim(z=2)                      # s18's plot; then the shade over Re s < 1
    wz = s.manim(z=3)                      # the line of zeros, the strip edges, the probe
    h = s.manim(z=6, parallax=0.0)         # formulas, the inset

    P = parts()

    # ── s18's last frame ──
    plot, zeros, hud, lb = end_frame()
    wp.add(*plot)
    wz.add(*zeros)
    h.add(*hud)
    line, sliver = zeros
    out = T.n_sit - 0.1
    wp.play(*[FadeOut(m) for m in plot], at=out, dur=0.5, lead=0)
    h.play(*[FadeOut(m) for m in hud], at=out, dur=0.5, lead=0)
    wz.play(FadeOut(sliver), at=out, dur=0.4, lead=0)

    # ── the line of zeros becomes Re s = 1/2 of the colored plane ──
    wz.play(line.animate.put_start_and_end_on([XH, -4.2, 0], [XH, 4.2, 0]), at=T.n_sit + 0.2, dur=1.2, ease=EASE)
    re0, re1, r1lab = P.re0, P.re1, P.r1lab
    wz.play(Create(re0), Create(re1), at=T.n_stops - 0.6, dur=0.8)
    wz.play(FadeIn(r1lab), at=T.n_stops, dur=0.5)

    # ── where the sum works (Re s > 1) the product over primes converges ──
    shade_l, shade_s = P.shade_l, P.shade_s
    wp.play(FadeIn(shade_l), FadeIn(shade_s), at=T.n_works, dur=0.6)
    sig = keys((T.n_inside - L, S_IN.real), (T.n_inside - L + 1.2, S_STRIP.real, EASE), lead=0)
    s_of = lambda t: complex(float(sig(t)), TC)       # noqa: E731
    pr0 = probe_mob(S_IN, 0.0, 0.0, to_xy=to_p)
    wz.play(FadeIn(pr0, scale=0.8), at=T.n_works + 0.4, dur=0.5)

    eq, so = P.eq, P.so
    h.play(FadeIn(P.eq_bg), Write(eq), at=T.n_product, dur=1.0)

    frame, cap, zero = P.frame, P.cap, P.zero
    h.play(FadeIn(frame), FadeIn(cap), FadeIn(zero), at=T.n_product + 0.3, dur=0.5)
    grow = keys((T.n_product + 0.6, 0.0), (T.n_product + 2.6, np.log10(N0), "in_out_sine"), lead=0)
    live(h, lambda t: path_mob(S_IN, 10 ** float(grow(t))), (T.n_product + 0.6, T.n_product + 2.6))

    # ── so zeta can't be zero there ──
    zv = products(S_IN, N0)[-1]
    zdot = Dot(to_ins(zv), radius=0.07, color=C.zeta)
    ztag = carded(tex(r"\zeta(s)\neq0", size=30, color=C.zeta), buff=0.06, opacity=1.0)
    ztag.move_to(to_ins(zv) + [0.0, 0.5, 0])
    h.play(FadeIn(zdot, scale=0.5), at=T.n_product + 2.4, dur=0.4, lead=0)
    h.play(FadeIn(ztag), at=T.n_cant, dur=0.5)
    h.play(FadeIn(P.so_bg), FadeIn(so, shift=0.06 * DOWN), at=T.n_cant + 0.2, dur=0.6)

    # ── inside the strip the same product wanders, and with more primes leaves the frame ──
    slide = (T.n_inside - L, T.n_inside - L + 1.2)
    wz.remove(pr0, at=slide[0])
    wz.redraw(lambda t: probe_mob(s_of(t), 0.0, 0.0, to_xy=to_p), during=(slide[0], T.cut_nearmiss))
    wp.play(shade_s.animate.set_fill(opacity=0.75), at=T.n_inside, dur=0.6)
    h.play(FadeOut(zdot), FadeOut(ztag), at=slide[0], dur=0.3, lead=0)
    wander = (slide[1] + 0.1, T.cut_nearmiss - 0.3)
    more = keys((wander[0], np.log10(N1)), (wander[1], np.log10(len(primes())), "in_out_sine"), lead=0)
    held = live(h, lambda t: path_mob(s_of(t), N1, tip=True), slide)
    h.remove(held[-1], at=wander[0])
    live(h, lambda t: path_mob(S_STRIP, 10 ** float(more(t)), tip=True), wander)
    nolonger = P.nolonger
    h.play(FadeIn(nolonger), at=T.n_that + 0.72, dur=0.5)
