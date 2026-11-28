"""s08 euler (P18): Euler's product. s07's tower comes apart into tiles 1/n^s in rows of ten, laid out like the sieve
grid. Multiplying zeta by (1 - 1/2^s) knocks out every even term; (1 - 1/3^s) the rest of the multiples of 3; then 5,
7 and every other prime, in the sieve colors, until only 1 is left: zeta(s)(1 - 1/2^s)(1 - 1/3^s)... = 1. A small copy
of the s05 sieve replays in sync. Then: a sum over every whole number equals a product over the primes."""
from aion import *

from beats import T
from media_assets import euler_pos, portrait, portrait_frame
from look import (N_END, TB, TW, TX, knob_mob, lab, needle_mob, pin, seen, series_eq, series_results, sieve_color,
                  slider_mobs, spf, tex, tower_grid, tower_mob)

COLS = 10
TL_W, TL_H, GAP = 0.9, 0.82, 0.08            # one tile, and the gap between tiles
GL, GT = -6.2, 1.41                          # the tile grid's left edge and top
MC, ML, MT = 0.2, 4.5, 1.1                   # the mini sieve: cell size, left edge, top
KNOCK, STAGGER = 0.8, 0.02                   # each knockout's length, and the stagger between tiles


def tile_xy(n):
    r, c = divmod(n - 1, COLS)
    return GL + c * (TL_W + GAP) + TL_W / 2, GT - r * (TL_H + GAP) - TL_H / 2


def tile(n):
    box = Rectangle(width=TL_W, height=TL_H, stroke_color=C.muted, stroke_width=1.4, fill_color=C.text,
                    fill_opacity=seen(0.06))
    return box.move_to([*tile_xy(n), 0])


def term(n):
    t = tex("1", size=32) if n == 1 else tex(r"\frac{1}{%d^s}" % n, size=28)
    return t.move_to([*tile_xy(n), 0])


def cell(n):
    r, c = divmod(n - 1, 10)
    sq = Square(side_length=MC, stroke_color=C.faint, stroke_width=1.0, fill_color=C.text, fill_opacity=seen(0.06))
    return sq.move_to([ML + c * MC + MC / 2, MT - r * MC - MC / 2, 0])


def knocked(box, color, strong=0.32):
    return box.set_fill(color, opacity=seen(strong)).set_stroke(color, width=2.0, opacity=1.0)


@scene(T.cut_euler, T.cut_complex)
def s08_euler(s):
    s.solid(C.bg, z=-200)
    bye = (T.cut_complex - 0.5, T.cut_complex - 0.05)            # a breath before 1859
    w = s.manim(z=2)                       # s07's tower and grid; then the tiles and the mini sieve
    h = s.manim(z=6, parallax=0.0, opacity=keys((bye[0], 1.0), (bye[1], 0.0), lead=0))   # s07's slider; Euler's identity
    top = s.manim(z=6, parallax=0.0, opacity=keys((T.product_primes + 1.4, 1.0), (T.product_primes + 2.0, 0.45),
                                                  (bye[0], 0.45), (bye[1], 0.0), lead=0))   # the factor line

    # ── s07's last frame ──
    grid, tower, needle = tower_grid(), tower_mob(N_END, 2.0), needle_mob(N_END, 2.0)
    res = series_results()
    w.add(grid, tower, needle, res.lim, res.pi6)
    eq07 = series_eq()
    slider, knob = slider_mobs(), knob_mob(2.0)
    top.add(eq07)
    h.add(slider, knob, res.r1, res.r2, res.euler)

    # ── the tower comes apart into tiles 1/n^s, in rows of ten ──
    N = 30
    boxes = VGroup(*[tile(n) for n in range(1, N + 1)])
    terms = VGroup(*[term(n) for n in range(1, N + 1)])
    more = tex(r"+\cdots", size=36, color=C.muted)
    more.move_to([GL + COLS * (TL_W + GAP) + 0.12 + more.width / 2, tile_xy(N)[1], 0])
    w.play(*[FadeOut(m) for m in (grid, needle, res.lim, res.pi6, tower.tail, *tower.blocks[N:])], at=T.link, dur=0.6)
    h.play(*[FadeOut(m) for m in (slider, knob, res.r1, res.r2, res.euler)], at=T.link, dur=0.6)
    eframe = portrait_frame(euler_pos(res), 2.0)                      # the portrait carried over from s07
    h.add(eframe)
    h.play(FadeOut(eframe), at=T.link, dur=0.6)
    s.add(ArrayLayer(portrait("euler"), height=2.0, pos=euler_pos(res), z=5, parallax=0.0,
                     opacity=keys((T.link, 1.0), (T.link + 0.6, 0.0), lead=0)))
    top.play(FadeOut(eq07[2:]), at=T.link, dur=0.6)
    w.play(LaggedStart(*[ReplacementTransform(tower.blocks[i], boxes[i]) for i in range(N)], lag_ratio=0.03),
           at=T.link + 0.3, dur=1.6)
    w.play(LaggedStart(*[FadeIn(t) for t in terms], lag_ratio=0.04), at=T.link + 1.1, dur=1.0, lead=0)
    w.play(FadeIn(more), at=T.link + 1.8, dur=0.5, lead=0)

    # ── the equation: zeta(s), then one factor per prime; the '=' moves along ahead of them ──
    L = tex(r"\zeta(s)", r"\left(1-\frac{1}{2^s}\right)", r"\left(1-\frac{1}{3^s}\right)",
            r"\left(1-\frac{1}{5^s}\right)", r"\left(1-\frac{1}{7^s}\right)", r"\cdots", r"=", r"1", size=42,
            colors={0: C.zeta, 1: C.sieve2, 2: C.sieve3, 3: C.sieve5, 4: C.sieve7, 5: C.prime})
    pin(L, top=3.5, left=-6.2)
    gap = L[6].get_left()[0] - L[5].get_right()[0]

    def eq_after(k):
        return np.array([L[k].get_right()[0] + gap + L[6].width / 2, L[6].get_y(), 0])

    eqs = L[6].copy().move_to(eq_after(0))
    top.play(ReplacementTransform(eq07[0], L[0]), ReplacementTransform(eq07[1], eqs), at=T.link + 0.2, dur=0.9)

    def factor(k, at):
        top.play(FadeIn(L[k], shift=0.1 * DOWN), eqs.animate.move_to(eq_after(k)), at=at, dur=0.6)

    def knock(ns, color, at):
        ns = list(ns)
        anims = [AnimationGroup(knocked(boxes[n - 1].animate, color), terms[n - 1].animate.set_opacity(0.3)) for n in ns]
        w.play(LaggedStart(*anims, lag_ratio=STAGGER / KNOCK), at=at, dur=KNOCK + STAGGER * (len(ns) - 1))

    by_p = {p: [n for n in range(2, N + 1) if spf(n) == p] for p in (2, 3, 5, 7)}
    rest = [n for n in range(11, N + 1) if spf(n) == n]
    factor(1, T.f2)
    knock(by_p[2], C.sieve2, T.cancel2 - 0.45)                        # starts on "even", done on "cancels"
    factor(2, T.f3)
    knock(by_p[3], C.sieve3, T.cancel3 - 0.7)

    # ── it's the sieve again: s05's grid, small, with the same colors so far ──
    cells = VGroup(*[cell(n) for n in range(1, 101)])
    for n in range(2, 101):
        if spf(n) in (2, 3) and spf(n) != n:
            knocked(cells[n - 1], sieve_color(spf(n)), 0.6)
    cells[0].set_fill(opacity=0).set_stroke(opacity=0.35)
    cap = lab("sieve", 26, C.muted).next_to(cells, DOWN, buff=0.16)
    w.play(FadeIn(cells, scale=0.96), FadeIn(cap), at=T.sieve_again, dur=0.6)

    def mini(ns, color, at, strong=0.6):
        w.play(LaggedStart(*[knocked(cells[n - 1].animate, color, strong) for n in ns], lag_ratio=0.1),
               at=at, dur=0.8)

    # ── every prime: 5, 7, then the rest, in step with the sieve; only 1 is left ──
    factor(3, T.every_prime)
    knock(by_p[5], C.sieve5, T.every_prime)
    mini([n for n in range(2, 101) if spf(n) == 5 and n != 5], C.sieve5, T.every_prime)
    factor(4, T.every_prime + 0.35)
    knock(by_p[7], C.sieve7, T.every_prime + 0.35)
    mini([n for n in range(2, 101) if spf(n) == 7 and n != 7], C.sieve7, T.every_prime + 0.35)
    factor(5, T.every_prime + 0.7)
    knock(rest, C.prime, T.every_prime + 0.7)
    mini([n for n in range(2, 101) if spf(n) == n], C.prime, T.every_prime + 0.7, strong=0.85)
    w.play(Indicate(VGroup(boxes[0], terms[0]), color=C.text, scale_factor=1.12), at=T.only_one + 0.3, dur=0.9)
    top.play(TransformFromCopy(terms[0], L[7]), at=T.only_one + 0.4, dur=0.8)
    top.play(L[1:6].animate.set_color(C.text), at=T.only_one + 1.1, dur=0.6, lead=0)   # complete: the factors turn white

    # ── a sum over every whole number equals a product over the primes ──
    w.play(FadeOut(VGroup(boxes, terms, more, cells, cap)), at=T.sum_product, dur=0.6)
    euler = tex(r"\sum_{n\ge1}\frac{1}{n^s}", r"=", r"\prod_{p}", r"\frac{1}{1-p^{-s}}", size=60,
                colors={0: C.zeta, 2: C.prime})
    euler.move_to([-0.6, -0.15, 0])
    ns = tex(r"n=1,2,3,4,\ldots", size=30, color=C.muted).next_to(euler[0], DOWN, buff=0.35)
    ps = tex(r"p=2,3,5,7,11,\ldots", size=30, color=C.prime).next_to(euler[2:], DOWN, buff=0.35)
    h.play(Write(euler[0]), at=T.sum_product + 0.9, dur=1.0)
    h.play(FadeIn(ns, shift=0.08 * UP), at=T.sum_product + 1.9, dur=0.6)
    h.play(FadeIn(euler[1]), TransformFromCopy(L[1:6], euler[2:]), at=T.product_primes, dur=1.2)
    h.play(FadeIn(ps, shift=0.08 * UP), at=T.product_primes + 1.2, dur=0.6)
    h.play(Indicate(euler[2], color=C.prime, scale_factor=1.15), at=T.carries + 0.4, dur=1.0)
    gt1 = tex(r"s>1", size=34, color=C.muted).next_to(euler, RIGHT, buff=0.5)
    h.play(FadeIn(gt1), at=T.carries + 1.6, dur=0.6)
