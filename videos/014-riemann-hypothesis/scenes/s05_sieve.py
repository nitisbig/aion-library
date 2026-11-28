"""s05 sieve (P11-P12): the sieve of Eratosthenes on 1-100. Keep 2 and knock out its other multiples (sieve2), then 3,
5 and 7 (each composite takes its smallest prime factor's color, as in s08); the 25 survivors turn gold. Then the
irregularity up close: twin pairs (11, 13 bright; 17-19 ... 71-73 faint) and the run 90-96 with no prime (gap red)."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import caps, lab, seen, sieve_color, spf, tex

CS, PITCH, GL, GT = 0.62, 0.68, -6.4, 3.4     # cell side, pitch, grid left and top
RX = 1.0                                       # left edge of the right-hand column
STAG, KNOCK = 0.03, 0.5
TWINS = [(17, 19), (29, 31), (41, 43), (59, 61), (71, 73)]


def xy(n):
    r, c = divmod(n - 1, 10)
    return np.array([GL + c * PITCH + PITCH / 2, GT - r * PITCH - PITCH / 2, 0.0])


def cell(n):
    sq = Square(side_length=CS, stroke_color=C.faint, stroke_width=1.2, fill_color=C.text, fill_opacity=seen(0.06))
    return sq.move_to(xy(n))


def num(n):
    return tex(str(n), size=26).move_to(xy(n))


def outline(n, color, width=3.0, opacity=1.0):
    return Square(side_length=CS + 0.04, stroke_color=color, stroke_width=width, stroke_opacity=opacity).move_to(xy(n))


@scene(T.cut_sieve, T.cut_pnt)
def s05_sieve(s):
    s.solid(C.bg, z=-200)
    bye = (T.cut_pnt - 0.5, T.cut_pnt - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── write out the numbers up to a hundred ──
    cells = VGroup(*[cell(n) for n in range(1, 101)])
    nums = VGroup(*[num(n) for n in range(1, 101)])
    cells[0].set_fill(opacity=0.0).set_stroke(opacity=0.35)
    nums[0].set_opacity(0.35)
    w.play(LaggedStart(*[FadeIn(VGroup(cells[10 * r:10 * r + 10], nums[10 * r:10 * r + 10])) for r in range(10)],
                       lag_ratio=0.12), at=T.e_write, dur=1.4)

    def survive(ns, at, stagger=0.0):
        anims = [AnimationGroup(cells[n - 1].animate.set_fill(C.prime, opacity=seen(0.15)).set_stroke(C.prime, width=2.2,
                                                                                                    opacity=1.0),
                                nums[n - 1].animate.set_color(C.prime)) for n in ns]
        w.play(LaggedStart(*anims, lag_ratio=stagger / 0.5 if stagger else 0.0), at=at, dur=0.5 + stagger * len(ns))

    def knock(p, at):
        ns = [n for n in range(2 * p, 101) if spf(n) == p]
        col = sieve_color(p)
        anims = [AnimationGroup(cells[n - 1].animate.set_fill(col, opacity=seen(0.32)).set_stroke(col, width=2.0,
                                                                                                opacity=1.0),
                                nums[n - 1].animate.set_opacity(0.3)) for n in ns]
        w.play(LaggedStart(*anims, lag_ratio=STAG / KNOCK), at=at, dur=KNOCK + STAG * (len(ns) - 1))

    chips = VGroup(*[VGroup(Square(side_length=0.28, stroke_color=sieve_color(p), stroke_width=2.0,
                                   fill_color=sieve_color(p), fill_opacity=seen(0.32)),
                            tex(r"\times%d" % p, size=30, color=sieve_color(p))).arrange(RIGHT, buff=0.12)
                     for p in (2, 3, 5, 7)])
    pchip = VGroup(Square(side_length=0.28, stroke_color=C.prime, stroke_width=2.2, fill_color=C.prime,
                          fill_opacity=seen(0.15)), lab("primes", 28, C.prime)).arrange(RIGHT, buff=0.12)
    legend = VGroup(*chips, pchip).arrange(RIGHT, buff=0.32).move_to([0, 2.95, 0])
    legend.align_to([RX, 0, 0], LEFT)

    # ── keep two, cross out its other multiples; the same for three, five and seven ──
    for p, keep, cross in ((2, T.e_keep2 + 0.3, T.e_cross), (3, T.e_same + 0.74, T.e_same + 0.74),
                           (5, T.e_five, T.e_five), (7, T.e_five + 0.61, T.e_five + 0.61)):
        survive([p], keep)
        h.play(FadeIn(chips[(2, 3, 5, 7).index(p)], shift=0.06 * UP), at=keep, dur=0.4)
        knock(p, cross)

    # ── what survives are the primes ──
    rest = [n for n in range(11, 101) if spf(n) == n]
    survive(rest, T.e_survives + 0.16, stagger=0.02)
    h.play(FadeIn(pchip, shift=0.06 * UP), at=T.e_survives + 0.4, dur=0.4)
    primes = VGroup(*[nums[n - 1] for n in [2, 3, 5, 7] + rest])
    w.play(Indicate(primes, color=C.prime, scale_factor=1.18), at=T.e_survives + 1.1, dur=0.9, lead=0)
    count = tex(r"\pi(100)=25", size=38, colors=None).set_color(C.prime)
    count.move_to([RX + count.width / 2, 2.2, 0])
    h.play(FadeIn(count, shift=0.06 * UP), at=T.e_survives + 1.6, dur=0.5, lead=0)

    # ── the sieve of Eratosthenes ──
    name = caps("the sieve of Eratosthenes", 36, C.ink)
    name.move_to([RX + name.width / 2, 1.35, 0])
    h.play(FadeIn(name, shift=0.06 * UP), at=T.e_sieve, dur=0.6)
    portrait_card(s, h, "eratosthenes", None, T.e_sieve + 0.2, T.e_pairs, (RX + 1.25, -0.75), height=2.5)

    # ── predicting them is another matter: close pairs ──
    h.play(FadeOut(VGroup(legend, count)), at=T.e_predict, dur=0.5)
    h.play(name.animate.move_to([RX + name.width / 2, 2.95, 0]), at=T.e_predict, dur=0.6)
    faint = VGroup(*[VGroup(outline(a, C.text, 2.0, 0.4), outline(b, C.text, 2.0, 0.4)) for a, b in TWINS])
    w.play(LaggedStart(*[Create(f) for f in faint], lag_ratio=0.2), at=T.e_pairs, dur=1.0)
    twin = VGroup(outline(11, C.text, 3.2), outline(13, C.text, 3.2))
    w.play(Create(twin), at=T.e_eleven + 0.2, dur=0.5)
    pair = VGroup(tex(r"11,\ 13", size=40, color=C.prime), lab("close pairs", 28, C.muted)).arrange(RIGHT, buff=0.3)
    pair.move_to([RX + pair.width / 2, 1.6, 0])
    h.play(FadeIn(pair, shift=0.06 * UP), at=T.e_eleven + 0.4, dur=0.5)

    # ── after 89, seven numbers go by with no prime at all ──
    w.play(Indicate(nums[88], color=C.prime, scale_factor=1.3), at=T.e_after + 0.32, dur=0.8)
    run = VGroup(*[VGroup(Square(side_length=CS, stroke_width=0, fill_color=C.gap, fill_opacity=seen(0.3)).move_to(xy(n)),
                          outline(n, C.gap, 5.0)) for n in range(90, 97)])
    w.play(LaggedStart(*[FadeIn(r) for r in run], lag_ratio=0.25), at=T.e_gone, dur=1.3)
    gap = VGroup(tex(r"89\to97", size=40, color=C.prime), lab("no prime in between", 28, C.gap))
    gap.arrange(RIGHT, buff=0.3).move_to([0, 0.5, 0]).align_to([RX, 0, 0], LEFT)
    h.play(FadeIn(gap, shift=0.06 * UP), at=T.e_gone + 0.4, dur=0.5)
