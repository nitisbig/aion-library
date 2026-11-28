"""s02 staircase (P05-P07): the primes below 100 land on a number line and the count climbs as a staircase. A smooth
curve follows the trend; 1, 5, 30, then 100 waves (one per zeta zero, assets/explicit.npz) bend it until it turns a
corner at every prime. Each wave lights its zero on the line at the right: every one sits on the same vertical line."""
from aion import *

from beats import T
from look import (EASE, GAM, PY0, TOP_INF, ZTOP, ZX, X, Y, batch_starts, bump, curve_mob, explicit, lab, live,
                  number_line, pin, prime_ticks, smooth01, stair_mob, stair_points, tex, wave_weights, y_axis, zero_line,
                  zy)

SIZES = (1, 4, 25, 70)                     # waves added on "single", "five", "thirty", "a hundred"
LINE_Y = 0.0                               # the number line, before it drops to become the x-axis

CAM = (-0.6, -0.1)                         # the push on "turns a corner" (keeps the y-axis clear of the labels)


@scene(T.cut_staircase, T.cut_map)
def s02_staircase(s):
    s.solid(C.bg, z=-200)
    w = s.manim(z=2)                       # the plot and the line of zeros (the camera pushes in on these)
    h = s.manim(z=6, parallax=0.0)         # the equations and the wave count stay put
    E = explicit()
    xs, base, waves = E["x"], E["base"], E["waves"]
    n_w = sum(SIZES)
    starts = batch_starts((T.single, T.five, T.thirty, T.hundred), SIZES)
    durs = np.full(n_w, 0.5)
    durs[0] = 0.9                                        # the single wave sweeps in slowly enough to follow
    done = float(np.max(starts + durs))

    # ── the line of zeros: it fades in with the first wave, dim until each wave lights its dot ──
    def zline(t):
        u = (t - starts) / 0.35
        lit = smooth01(u)
        sc = 1 + 0.6 * bump((t - starts) / 0.45)
        k = np.arange(n_w)
        sc = sc + 0.45 * bump((t - (T.right - 0.1) - 0.9 * k / n_w) / 0.35)          # ripple bottom to top
        sc = sc + 0.5 * bump((t - (T.vline - 0.15)) / 0.8)                         # all together
        top = ZTOP + (TOP_INF - ZTOP) * smooth01((t - (T.infinite - 0.15)) / 1.2)
        beyond = np.ones(200)
        g = GAM[:n_w + 200]
        tip = top - 0.05
        beyond_lit = smooth01((tip - zy(g[n_w:])) / 0.3)                           # lit as the tip passes
        lit_all = np.concatenate([lit, beyond_lit * beyond])
        sc_all = np.concatenate([sc, np.ones(200)])
        glow = smooth01((t - (T.vline - 0.15)) / 0.6)
        return zero_line(top=top, lit=lit_all, scale=sc_all, line_opacity=0.75 + 0.25 * glow, width=2.0 + 1.2 * glow)

    zl0 = zero_line()
    w.play(FadeIn(zl0), at=float(starts[0]) - 0.9, dur=0.8, lead=0)     # appears with the first wave, not before
    w.remove(zl0, at=starts[0])
    live(w, zline, (starts[0], done), (T.right - 0.15, T.right + 1.1), (T.vline - 0.2, T.vline + 0.9),
         (T.infinite - 0.2, T.infinite + 1.25))
    zeros_tag = lab("zeros", 30, C.zero)
    zeros_tag.move_to([ZX + 0.16 + zeros_tag.width / 2, float(zy(GAM[0])) - 0.02, 0])
    w.play(FadeIn(zeros_tag, shift=0.1 * LEFT), at=T.zeros, dur=0.6)

    # ── the primes land on a number line (s01 ends with a gold dot dropping onto it) ──
    nl = number_line(LINE_Y)
    seed = Dot([X(2), LINE_Y, 0], radius=0.07, color=C.prime)
    w.add(nl, seed)
    ticks = prime_ticks(LINE_Y)
    w.play(ReplacementTransform(seed, ticks[0]), at=T.primes, dur=0.4)
    w.play(LaggedStart(*[FadeIn(tk, shift=0.3 * DOWN) for tk in ticks[1:]], lag_ratio=0.114), at=T.primes + 0.1,
           dur=1.27)

    # ── the line drops into the x-axis, and the count climbs as a staircase ──
    drop = PY0 - LINE_Y
    w.play(VGroup(nl, ticks).animate.shift(drop * UP), at=T.themselves, dur=1.2, ease=EASE, lead=0)
    ya = y_axis()
    w.play(Create(ya[0]), FadeIn(ya[1]), FadeIn(ya[2]), at=T.count, dur=0.8)
    defn = tex(r"\pi(x)", r"=\#\{", r"p", r"\le x\}", size=44, colors={0: C.prime, 2: C.prime})
    pin(defn, top=3.5, left=-5.9)
    h.play(Write(defn), at=T.count + 0.5, dur=1.0)

    xc = key(T.count + 0.5, 0.0, 100.0, dur=4.4, ease="in_out_sine")
    sweep = (T.count + 0.5 - C.lead, T.count + 0.5 - C.lead + 4.4)
    w.redraw(lambda t: stair_mob(float(xc(t))), during=sweep)

    def cursor(t):
        x = float(xc(t))
        _, n = stair_points(x)
        top = float(Y(n)) + 0.22
        bar = Line([X(x), PY0, 0], [X(x), top, 0], color=C.muted, stroke_width=1.4)
        num = tex(str(n), size=34, color=C.prime)
        num.move_to([X(x) - 0.08 - num.width / 2, top + 0.12 + num.height / 2, 0])
        return VGroup(bar, num)

    cur = w.redraw(cursor, during=sweep)
    w.play(FadeOut(cur), at=sweep[1] + 0.3, dur=0.5, lead=0)
    w.remove(cur, at=sweep[1] + 0.85)
    tally = tex(r"\pi(100)", r"=25", size=40, colors={0: C.prime})
    pin(tally, top=2.78, left=-5.9)
    h.play(FadeIn(tally, shift=0.1 * DOWN), at=sweep[1] + 0.3, dur=0.6, lead=0)

    # ── a smooth curve follows the trend (R(x) plus the small terms; s16 names them) ──
    ghost = curve_mob(base, xs, color=C.smooth, width=2.6)
    w.play(Create(ghost), at=T.smooth_curve, dur=2.0)
    r_tag = tex(r"R(x)", size=34, color=C.smooth)
    r_tag.move_to([X(100) + 0.16 + r_tag.width / 2, float(Y(base[-1])), 0])
    w.play(FadeIn(r_tag), at=T.smooth_curve + 1.7, dur=0.6, lead=0)

    # ── waves: 1, 5, 30, 100; each sweeps in left to right ──
    def pink(t):
        wt = wave_weights(t, starts, durs)
        y = base + (wt * waves).sum(axis=0)
        xmax = None
        if t < starts[0] + durs[0]:
            hit = xs[wt[0] > 0]
            xmax = float(hit.max()) if len(hit) else 0.0
        return curve_mob(y, xs, color=C.zero, width=2.6, xmax=xmax)

    w.redraw(pink, during=(starts[0], done))
    w.play(ghost.animate.set_stroke(opacity=0.12), FadeOut(r_tag), at=starts[0] + durs[0] + 0.3, dur=0.6, lead=0)

    count = tex(r"1", r"\to 5", r"\to 30", r"\to 100", size=40, color=C.zero)
    word = lab("waves", 34, C.zero)
    row = VGroup(word, count).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
    pin(row, top=2.05, left=-5.9)
    h.play(FadeIn(word), FadeIn(count[0]), at=T.single, dur=0.5)
    for part, beat in zip(count[1:], (T.five, T.thirty, T.hundred)):
        h.play(FadeIn(part, shift=0.08 * RIGHT), at=beat, dur=0.4)

    # ── "until it turns a corner at every prime": push in, hold, then back out to the line of zeros ──
    s.camera.frame(T.corner - C.lead, center=CAM, zoom=1.12, dur=2.0)
    s.camera.frame(T.each - C.lead, center=(0.0, 0.0), zoom=1.0, dur=1.5)
