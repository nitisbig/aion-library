"""Ch1 · What e really is. Not a decimal: a kind of growth. A bank draws on (100% a year), shrinks to the corner
beside a calendar of payment months. A gold coin drops onto the axes: one dollar. Paid once, twice, four times,
monthly, daily: gold staircases, each finer one leaving a ghost, the calendar filling in, a ledger of (1 + 1/n)^n.
Interest on interest is shown as a split bar: the second payment is 0.50 on the dollar plus 0.25 on the first
interest. The camera leans in on the end of the year: the totals pile up under a ceiling, 2.718…, e."""
from aion import *

from beats import T
from shots import (BANK_O, BANK_UX, BANK_UY, backdrop, bank_pt, calendar, chapter_card, coin, glyphs, graph_axes,
                   icon, live, panel, ramp, rail, tex)

E = "easy_ease"
NS = (1, 2, 4, 12, 365)
VAL = {n: (1 + 1 / n) ** n for n in NS}
LED_X, LED_Y0, LED_DY = (3.35, 5.15), 1.0, 0.6       # ledger columns (n, value), first row y, row step
LED_C, LED_W, LED_H = (4.75, -0.7), 3.8, 5.4         # ledger panel centre and size
TOPROW = 2.85                                        # bank, 100%, calendar sit above the ledger
BANK_SMALL, BANK_BIG = (3.55, TOPROW), (-2.35, 0.75)
CAL_AT = (6.0, TOPROW)


def stair(n, tau):
    """Balance for n payments a year, drawn from year-time 0 to tau (0..1): flat, then a jump at each payment."""
    pts = [bank_pt(0, 1.0)]
    level = 1.0
    for k in range(1, n + 1):
        tk = k / n
        if tau < tk - 1e-9:
            pts.append(bank_pt(tau, level))
            break
        pts.append(bank_pt(tk, level))
        level *= 1 + 1 / n
        pts.append(bank_pt(tk, level))
    return pts


def stair_mob(n, tau, k_ghost=0.0, k=1.0):
    """The staircase for n payments. Daily (n = 365) steps are far below a pixel, so it is drawn as the smooth
    compound curve (1 + 1/n)^(n t) through its corners (ends at 2.7146, not e)."""
    width = C.stroke + 0.5 - 2.4 * k_ghost
    op = (1.0 - 0.7 * k_ghost) * k
    mob = VMobject(stroke_color=C.growth, stroke_width=width, stroke_opacity=op)
    if n < 100:
        return mob.set_points_as_corners(stair(n, tau))
    ts = np.linspace(0, max(tau, 1e-3), 90)
    return mob.set_points_smoothly([bank_pt(t, (1 + 1 / n) ** (n * t)) for t in ts])


def bar(t, y0, y1, color, dx=0.16, opacity=0.9):
    """A thin vertical bar beside the staircase at year t, from balance y0 to y1 (an amount of interest)."""
    a, b = bank_pt(t, y0) + [dx, 0, 0], bank_pt(t, y1) + [dx, 0, 0]
    return Rectangle(width=0.13, height=b[1] - a[1], stroke_width=0, fill_color=color,
                     fill_opacity=opacity).move_to((a + b) / 2)


@scene(T.cut_ch1, T.cut_growth)
def s01_bank(s):
    backdrop(s)
    t0 = s.start
    w = s.manim(z=1)                                  # the graph (moves with the camera)
    hud = s.manim(z=4, parallax=0.0)                  # card, icons, ledger, rail (fixed to the screen)
    rail(hud, 1)

    # ── "First, we need to see e for what it really is. Not a decimal. A kind of growth." ──
    chapter_card(hud, 1, T.cut_ch1 + 0.1, T.decimal - 0.55)
    dec = tex(r"2.71828\ldots", size=110, color=C.muted)
    hud.play(FadeIn(dec), at=T.decimal, dur=0.4)
    sk = Line(dec.get_corner(DL) + [-0.1, 0.1, 0], dec.get_corner(UR) + [0.1, -0.1, 0], color=C.text,
              stroke_width=C.thin + 1)
    hud.play(Create(sk), at=T.decimal + 0.55, dur=0.4)
    hud.play(FadeOut(VGroup(dec, sk), shift=0.2 * DOWN), at=T.kind, dur=0.6)

    # ── axes on "A kind of growth" ──
    ax = graph_axes(BANK_O, BANK_UX, BANK_UY, 0, 1.08, 3.05, xticks=(0.5, 1), yticks=(1, 2, 3))
    w.play(Create(ax[:2]), at=T.kind + 0.3, dur=1.0, ease=E)
    w.play(FadeIn(ax[2:]), at=T.kind + 0.9, dur=0.6)
    half_ticks = VGroup(*[Line(bank_pt(x, 0) + [0, -0.06, 0], bank_pt(x, 0) + [0, 0.06, 0], color=C.muted,
                               stroke_width=C.thin) for x in (0.25, 0.75)])
    w.play(FadeIn(half_ticks), at=T.kind + 1.2, dur=0.5)

    # ── "Imagine a bank that pays one hundred percent interest per year." ──
    bank = icon("bank", 2.3, C.text, width=C.thin + 1.4).move_to([*BANK_BIG, 0])
    hud.play(Create(bank, lag_ratio=0.15), at=T.bank, dur=1.3, ease=E)
    pct = glyphs(r"100\%", {}, size=72).next_to(bank, DOWN, buff=0.3)
    pct.set_color(C.growth)
    hud.play(FadeIn(pct, shift=0.15 * UP), at=T.bank + 1.3, dur=0.5)           # "one hundred percent"
    to_corner = T.put_in - 0.5
    bank_s = bank.copy().set(height=0.95).move_to([*BANK_SMALL, 0])
    pct_s = pct.copy().set(height=0.32).move_to([BANK_SMALL[0] + 1.1, TOPROW - 0.05, 0])
    hud.play(Transform(bank, bank_s), Transform(pct, pct_s), at=to_corner, dur=1.0, ease=E)

    # the payment calendar beside it: which months pay interest (redrawn when the schedule changes)
    start_of = {1: T.put_in + 0.6, 2: T.six_months, 4: T.four, 12: T.month, 365: T.day}
    clear = (T.is_e + 0.5, T.cut_growth - 0.25)        # ghosts, icons and ledger leave before Ch1 part 2
    cal_in = (to_corner + 0.4, to_corner + 1.0)

    def cal(t):
        n = 1
        for nn in NS:
            if t >= start_of[nn] - 0.1:
                n = nn
        k = ramp(t, *cal_in) * (1 - ramp(t, *clear))
        pop = 1.0 + 0.12 * max(0.0, 1 - abs(t - (start_of[n] + 0.05)) / 0.25) if n > 1 else 1.0
        return calendar(n, 0.85, k).scale(pop).move_to([*CAL_AT, 0])
    live(hud, cal, cal_in, *[(start_of[n] - 0.25, start_of[n] + 0.35) for n in NS[1:]], clear)

    # ── the ledger ──
    led_box = panel(*LED_C, LED_W, LED_H)
    head = VGroup(tex("n", size=40, color=C.muted).move_to([LED_X[0], LED_Y0 + 0.72, 0]),
                  tex(r"\left(1+\tfrac{1}{n}\right)^{n}", size=40, color=C.muted)
                  .move_to([LED_X[1] + 0.35, LED_Y0 + 0.74, 0]))
    rule = Line([LED_X[0] - 0.5, LED_Y0 + 0.36, 0], [LED_X[1] + 1.3, LED_Y0 + 0.36, 0], color=C.faint,
                stroke_width=C.thin)
    hud.play(FadeIn(led_box), at=to_corner + 0.3, dur=0.6)
    hud.play(FadeIn(head), Create(rule), at=to_corner + 0.5, dur=0.8)

    def row(i, n):
        y = LED_Y0 - LED_DY * i
        a = tex(str(n), size=42).move_to([LED_X[0], y, 0])
        b = tex(f"{VAL[n]:.4f}", size=42, color=C.growth).move_to([LED_X[1] + 0.35, y, 0])
        return VGroup(a, b)

    # ── "Put in one dollar": a coin drops onto the axes ──
    c1 = coin(0.24).move_to(bank_pt(0, 1))
    w.play(FadeIn(c1, shift=1.2 * DOWN, rate_func=rate_functions.ease_out_bounce), at=T.put_in + 0.3, dur=0.8)
    two = VGroup(coin(0.2), coin(0.2)).arrange(RIGHT, buff=0.08).next_to(bank_pt(1.0, 2.0), RIGHT, buff=0.25)
    w.play(LaggedStart(*[FadeIn(c, scale=1.6) for c in two], lag_ratio=0.35), at=T.have_two, dur=0.6)  # "two."
    w.play(FadeOut(two), at=T.half - 0.3, dur=0.5)

    taus = {
        1: keys((t0, 0.0), (T.put_in + 0.6, 0.0), (T.have_two - 0.15, 1.0, "in_out_sine"), lead=0),
        2: keys((t0, 0.0), (T.six_months, 0.0), (T.six_months + 1.3, 0.5, "in_out_sine"),
                (T.interest_on + 0.2, 0.5), (T.v225 + 0.05, 1.0, "in_out_sine"), lead=0),
        4: keys((t0, 0.0), (T.four, 0.0), (T.v244 - 0.05, 1.0, "in_out_sine"), lead=0),
        12: keys((t0, 0.0), (T.month, 0.0), (T.month + 0.95, 1.0, "in_out_sine"), lead=0),
        365: keys((t0, 0.0), (T.day, 0.0), (T.day + 1.3, 1.0, "in_out_sine"), lead=0),
    }
    end_of = {1: T.have_two, 2: T.v225 + 0.1, 4: T.v244, 12: T.month + 1.0, 365: T.day + 1.35}
    row_at = {1: T.have_two + 0.2, 2: T.v225 + 0.5, 4: T.v244 + 0.3, 12: T.month + 1.0, 365: T.day + 1.45}

    rows = []
    for i, n in enumerate(NS):
        nxt = start_of[NS[i + 1]] if i + 1 < len(NS) else None

        def draw(t, n=n, nxt=nxt):
            kg = ramp(t, nxt, nxt + 0.6) if nxt is not None else 0.0
            k = 1.0 - (ramp(t, *clear) if n != 365 else 0.0)
            return stair_mob(n, taus[n](t), kg, k)
        wins = [(start_of[n] - 0.05, end_of[n] + 0.05)]
        if nxt is not None:
            wins.append((nxt, nxt + 0.65))
            wins.append(clear)
        live(w, draw, *wins)
        rows.append(row(i, n))
        hud.play(FadeIn(rows[-1], shift=0.15 * LEFT), at=row_at[n], dur=0.5)

    # ── n = 2, interest on interest: the second payment is 0.50 on the dollar + 0.25 on the first 0.50 ──
    b1 = bar(0.5, 1.0, 1.5, C.growth)
    l1 = tex("+0.50", size=30, color=C.growth).next_to(b1, RIGHT, buff=0.1)
    w.play(GrowFromEdge(b1, DOWN), FadeIn(l1), at=T.six_months + 1.45, dur=0.5)        # "one dollar fifty"
    w.play(Indicate(VGroup(b1, l1), color=C.growth, scale_factor=1.15), at=T.interest_on + 0.1, dur=0.8)
    bA = bar(1.0, 1.5, 2.0, C.growth)
    bB = bar(1.0, 2.0, 2.25, C.text)
    lA = tex("+0.50", size=30, color=C.growth).next_to(bA, RIGHT, buff=0.1)
    lB = tex("+0.25", size=30, color=C.text).next_to(bB, RIGHT, buff=0.1).shift(0.08 * UP)
    w.play(GrowFromEdge(bA, DOWN), FadeIn(lA), at=T.v225 + 0.15, dur=0.5)                  # "two twenty five"
    w.play(TransformFromCopy(b1, bB), FadeIn(lB), at=T.v225 + 0.7, dur=0.8, ease=E)       # interest on interest
    w.play(FadeOut(VGroup(b1, l1, bA, lA, bB, lB)), at=T.four - 0.25, dur=0.5)

    # ── "Keep splitting finer and finer… does not run off to infinity. It settles on one number." ──
    s.camera.frame(T.finer, center=(0.12, 1.78), zoom=2.1, dur=2.2)
    shoot = Arrow(bank_pt(1.0, 2.75), bank_pt(1.0, 3.6), buff=0, color=C.muted, stroke_width=C.thin + 1,
                  tip_length=0.12)
    w.play(GrowArrow(shoot), at=T.infinity + 0.2, dur=0.5)
    w.play(FadeOut(shoot, shift=0.15 * DOWN), at=T.infinity + 0.75, dur=0.4)
    ceil = DashedLine(bank_pt(0, np.e), bank_pt(1.06, np.e), color=C.text, stroke_width=C.thin + 0.4,
                      dash_length=0.06)
    w.play(Create(ceil), at=T.settles + 0.2, dur=0.9)
    lab = tex(r"2.718\ldots", size=22).next_to(bank_pt(0.62, np.e), UP, buff=0.06)
    w.play(FadeIn(lab), at=T.v2718 + 0.1, dur=0.4)
    s.camera.frame(T.is_e - 0.4, center=(0.0, 0.0), zoom=1.0, dur=1.4)
    e_lab = tex("e", size=60, color=C.growth).next_to(bank_pt(1.06, np.e), RIGHT, buff=0.1)
    w.play(ReplacementTransform(lab, e_lab), at=T.is_e + 0.3, dur=0.7)

    # the ledger's last row and the definition
    inf_row = VGroup(tex(r"\infty", size=42).move_to([LED_X[0], LED_Y0 - LED_DY * 5, 0]),
                     tex("e", size=48, color=C.growth).move_to([LED_X[1] + 0.35, LED_Y0 - LED_DY * 5, 0]))
    hud.play(FadeIn(inf_row, shift=0.15 * LEFT), at=T.is_e + 0.3, dur=0.5)
    lim = glyphs(r"e=\lim_{n\to\infty}\left(1+\tfrac{1}{n}\right)^{n}", {0: C.growth}, size=44, n=16)
    lim.move_to([LED_C[0], -2.85, 0])
    hud.play(Write(lim), at=T.is_e + 0.5, dur=0.9, lead=0)

    hud.play(FadeOut(VGroup(led_box, head, rule, *rows, inf_row, lim, bank, pct)), at=clear[0],
             dur=clear[1] - clear[0], lead=0)
    w.play(FadeOut(VGroup(ceil, c1, half_ticks)), at=clear[0], dur=clear[1] - clear[0], lead=0)
