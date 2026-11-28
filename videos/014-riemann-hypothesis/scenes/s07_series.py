"""s07 series (P16-P17): chapter 2 opens. zeta(s) as a sum: blocks of height 1/n^s stack into a tower whose top is the
running total. A slider sets s: at s = 2 the tower settles; at s = 1 it climbs out of the frame; back at s = 2 it settles
on pi^2/6 (Euler, 1734). The tower's builders live in look.py, so s08 can open on this scene's last frame."""
from aion import *

from beats import T
from media_assets import euler_pos, portrait, portrait_frame
from look import (EASE, chapter_card, knob_mob, needle_mob, series_eq, series_results, slider_mobs, tower_grid,
                  tower_mob)


@scene(T.cut_series, T.cut_euler)
def s07_series(s):
    s.solid(C.bg, z=-200)
    w = s.manim(z=2)
    h = s.manim(z=6, parallax=0.0)
    card = s.manim(z=8, parallax=0.0)
    chapter_card(card, T.cut_series, r"\zeta(s)", "The zeta function", out=T.here_fn - 0.1, color=C.zeta)

    # ── the running-total axis: faint gridlines at 1, 2, 3, ... ──
    grid = tower_grid()
    w.play(FadeIn(grid.lines), FadeIn(grid.nums), Create(grid.floor), at=T.here_fn, dur=0.8)

    # ── the sum, term by term ──
    eq = series_eq()
    h.play(FadeIn(eq[0:2]), at=T.here_fn + 0.3, dur=0.6)
    for part, beat in ((eq[2], T.add_one), (eq[3], T.two_s), (eq[4], T.three_s), (eq[5], T.forever)):
        h.play(FadeIn(part, shift=0.08 * LEFT), at=beat, dur=0.5)
    h.play(FadeIn(eq[6], shift=0.08 * LEFT), at=T.total_is + 0.3, dur=0.7)

    # ── the slider for s ──
    s_of = keys((T.s_one - C.lead, 2.0), (T.s_one + 1.05, 1.0, EASE), (T.s_two - C.lead, 1.0),
                (T.s_two + 1.35, 2.0, EASE), lead=0)
    slider = slider_mobs()
    k0 = knob_mob(2.0)
    h.play(Create(slider.track), FadeIn(slider.ends), FadeIn(k0), at=T.pick_s, dur=0.6)
    h.remove(k0, at=T.s_one - C.lead)
    h.redraw(lambda t: knob_mob(s_of(t)), during=(T.s_one - C.lead, T.s_two + 1.35))

    # ── the tower: terms one by one, then faster and faster; s = 1 climbs out, s = 2 settles ──
    n_first = keys((T.add_one - C.lead, 0.0), (T.add_one + 0.45, 1.0), (T.two_s - C.lead, 1.0), (T.two_s + 0.45, 2.0),
                   (T.three_s - C.lead, 2.0), (T.three_s + 0.45, 3.0), lead=0)
    n_log = keys((T.forever - C.lead, np.log10(3.0)), (T.forever + 2.6, 6.0, "in_out_sine"), (T.s_one + 0.2, 6.0),
                 (T.s_two - 0.3, 12.0, "in_cubic"), lead=0)            # ends on N_END = 10^12 terms

    def n_of(t):
        return float(n_first(t)) if t < T.forever - C.lead else 10.0 ** float(n_log(t))

    windows = [(T.add_one - C.lead, T.add_one + 0.45), (T.two_s - C.lead, T.two_s + 0.45),
               (T.three_s - C.lead, T.three_s + 0.45), (T.forever - C.lead, T.forever + 2.6),
               (T.s_one - C.lead, T.s_two + 1.35)]
    held = []
    for a, b in windows:
        if held:
            w.remove(held[-1], at=a)
        held.append(w.redraw(lambda t: tower_mob(n_of(t), float(s_of(t))), during=(a, b)))

    # ── the needle: the running total ──
    nd0 = needle_mob(n_of(T.total_is), 2.0)
    w.play(FadeIn(nd0), at=T.total_is, dur=0.5)
    w.play(Indicate(nd0[1], color=C.zeta), at=T.settles_down + 0.3, dur=0.9)
    w.remove(nd0, at=T.s_one - C.lead)
    w.redraw(lambda t: needle_mob(n_of(t), float(s_of(t))), during=(T.s_one - C.lead, T.s_two + 1.35))

    # ── results: s = 1 grows without limit; s = 2 settles on pi^2/6 (Euler, 1734) ──
    res = series_results()
    h.play(FadeIn(res.r1, shift=0.08 * UP), at=T.without_limit, dur=0.6)
    h.play(FadeIn(res.euler), at=T.euler1734, dur=0.6)
    s.add(ArrayLayer(portrait("euler"), height=2.0, pos=euler_pos(res), z=5, parallax=0.0,
                     opacity=keys((T.euler1734 - 0.15, 0.0), (T.euler1734 + 0.45, 1.0), lead=0)))   # stays into s08
    h.play(FadeIn(portrait_frame(euler_pos(res), 2.0)), at=T.euler1734 + 0.1, dur=0.5, lead=0)
    w.play(Create(res.lim), at=T.pi_sq, dur=0.8)
    h.play(FadeIn(res.r2, shift=0.08 * UP), at=T.pi_sq + 0.6, dur=0.6, lead=0)
    w.play(FadeIn(res.pi6), at=T.pi_sq + 0.6, dur=0.6, lead=0)
