"""s21 progress (P39): the proportion of zeros proven to lie on the line. A bar from 0 to 1; Hardy (1914: infinitely
many), then the fill creeps through Selberg (1942: > 0), Levinson (1974: 1/3), Conrey (1989: 2/5) and Pratt, Robles,
Zaharescu, Zeindler (2020: 5/12, just under 42%). Even 100% wouldn't be enough: the whole numbers 1..N as cells with the
perfect squares in pink; as N grows from 100 to 10,000 the squares fall from 10% to 1% of all numbers, but they keep
coming. Builders live in progress.py (the bar returns in s25 and s30)."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import EASE, live
from nearmiss import end_frame
from progress import (RECORDS, bar_frame, counter_mob, fill_mob, grid_mob, hundred_mob, law_mobs, pct_mob,
                      record_mob)


@scene(T.cut_progress, T.cut_cousin)
def s21_progress(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    o1, o2 = s.manim(z=2, parallax=0.0), s.manim(z=6, parallax=0.0)
    plot, hud = end_frame()                # s20's last frame
    o1.add(*plot)
    o2.add(*hud)
    out = (T.cut_progress + 0.35, T.cut_progress + 0.85)
    o1.play(*[FadeOut(m) for m in plot], at=out[0], dur=out[1] - out[0], lead=0)
    o2.play(*[FadeOut(m) for m in hud], at=out[0], dur=out[1] - out[0], lead=0)
    w = s.manim(z=2, parallax=0.0)         # the bar, the grid
    h = s.manim(z=6, parallax=0.0)         # labels, counter

    # ── the fraction of zeros proven to lie on the line ──
    bar = bar_frame()
    w.play(Create(bar.box), FadeIn(bar.ends), at=T.p_measure, dur=0.7)
    h.play(FadeIn(bar.title, shift=0.06 * DOWN), at=T.p_measure + 0.4, dur=0.6)

    # ── Hardy, 1914: infinitely many; then the fill creeps: > 0, 1/3, 2/5, 5/12 ──
    recs = [record_mob(k) for k in range(len(RECORDS))]
    at = [T.p_hardy, T.p_from + 0.3, T.p_from + 1.6, T.p_crept - 0.3, T.p_512]
    fill_keys = [(at[1] - L, 0.0)]
    for k in range(1, len(RECORDS)):
        fill_keys += [(at[k] - L, fill_keys[-1][1]), (at[k] - L + 0.6, RECORDS[k][0], EASE)]
    f = keys(*fill_keys, lead=0)
    for k, r in enumerate(recs):
        h.play(Create(r[0]), FadeIn(r[1], shift=0.06 * RIGHT), at=at[k], dur=0.5)
    live(w, lambda t: fill_mob(float(f(t))), (at[1] - L, at[-1] - L + 0.6))
    portrait_card(s, h, "hardy", None, T.p_hardy, T.p_from + 1.2, (4.9, -1.75), height=2.2)
    pct = pct_mob()
    h.play(FadeIn(pct, shift=0.06 * DOWN), at=T.p_42, dur=0.6)

    # ── even 100% wouldn't be enough ──
    hund = hundred_mob()
    w.play(Create(hund[0]), FadeIn(hund[1]), at=T.p_even, dur=0.8)
    h.play(*[FadeOut(r) for r in recs], at=T.p_even + 0.2, dur=0.5)
    grow = keys((T.p_even + 1.3, 2.0), (T.p_set + 2.1, 4.0, "in_out_sine"), lead=0)
    N_of = lambda t: int(round(10 ** float(grow(t))))       # noqa: E731
    g0, c0 = grid_mob(100), counter_mob(100)
    w.play(FadeIn(g0), at=T.p_even + 0.7, dur=0.5, lead=0)
    h.play(FadeIn(c0), at=T.p_even + 0.9, dur=0.5, lead=0)
    w.remove(g0, at=T.p_even + 1.3)
    h.remove(c0, at=T.p_even + 1.3)
    live(w, lambda t: grid_mob(N_of(t)), (T.p_even + 1.3, T.p_set + 2.1))
    live(h, lambda t: counter_mob(N_of(t)), (T.p_even + 1.3, T.p_set + 2.1))

    # ── in an infinite set, 100% can still leave out infinitely many ──
    law = law_mobs()
    h.play(FadeIn(law.limit, shift=0.06 * DOWN), at=T.p_set + 0.6, dur=0.6)
    h.play(FadeIn(law.notall, shift=0.06 * DOWN), at=T.p_still + 0.3, dur=0.6)
