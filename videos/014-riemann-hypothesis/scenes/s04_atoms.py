"""s04 atoms (P09-P10): chapter 1 opens. Every whole number above one is a product of primes in only one way: 60 as
6 * 10 and as 4 * 15, both trees ending in the same gold leaves 2 * 2 * 3 * 5. Euclid (c. 300 BC): the primes never
run out. Combs of the multiples of 2, 3, 5, 7 cover a number line; zoomed in, 210 = 2*3*5*7 has all four teeth and
211 has none (each division leaves remainder 1). The product + 1 need not itself be prime: 30031 = 59 * 509, both new."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import EASE, caps, chapter_card, lab, pin, sieve_color, tex

PS = (2, 3, 5, 7)
AX, X0, X1 = -0.4, -5.7, 6.2                 # the number line's y and screen extent
ZOOM = (198.0, 218.0)                        # the window after the push-in


def tree(root, kids, leaves, cx):
    """A factor tree: root over two kids over four leaves (gold). Parts .root .edges1 .kids .edges2 .leaves"""
    ys = (1.75, 0.6, -0.55)
    r = tex(str(root), size=48).move_to([cx, ys[0], 0])
    k = VGroup(*[tex(str(v), size=44).move_to([cx + d, ys[1], 0]) for v, d in zip(kids, (-1.0, 1.0))])
    lx = [cx - 1.5, cx - 0.5, cx + 0.5, cx + 1.5]
    lf = VGroup(*[tex(str(v), size=44, color=C.prime).move_to([x, ys[2], 0]) for v, x in zip(leaves, lx)])

    def edge(a, b):
        return Line(a.get_bottom() + 0.08 * DOWN, b.get_top() + 0.08 * UP, color=C.muted, stroke_width=2.0)

    e1 = VGroup(edge(r, k[0]), edge(r, k[1]))
    e2 = VGroup(edge(k[0], lf[0]), edge(k[0], lf[1]), edge(k[1], lf[2]), edge(k[1], lf[3]))
    g = VGroup(r, e1, k, e2, lf)
    g.root, g.edges1, g.kids, g.edges2, g.leaves = r, e1, k, e2, lf
    return g


@scene(T.cut_atoms, T.cut_sieve)
def s04_atoms(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_sieve - 0.5, T.cut_sieve - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    card = s.manim(z=8, parallax=0.0)
    chapter_card(card, T.cut_atoms, r"2,3,5,7,11,\ldots", "The primes", out=T.a_every - 0.3, color=C.prime)

    # ── every whole number above one is a product of primes, in only one way ──
    gen = tex(r"n", r"=p_1\,p_2\cdots p_k", size=44)
    pin(gen, top=3.55, left=-6.2)
    one = lab("in only one way", 30, C.muted).next_to(gen, RIGHT, buff=0.4)
    h.play(FadeIn(gen, shift=0.06 * DOWN), at=T.a_every + 0.4, dur=0.6)
    h.play(FadeIn(one, shift=0.06 * LEFT), at=T.a_oneway, dur=0.5)

    t1, t2 = tree(60, (6, 10), (2, 3, 2, 5), -3.3), tree(60, (4, 15), (2, 2, 3, 5), 3.3)

    def grow(tr, at):
        w.play(FadeIn(tr.root, scale=0.9), at=at, dur=0.5)
        w.play(Create(tr.edges1), FadeIn(tr.kids, shift=0.1 * DOWN), at=at + 0.6, dur=0.6, lead=0)
        w.play(Create(tr.edges2), FadeIn(tr.leaves, shift=0.1 * DOWN), at=at + 1.2, dur=0.6, lead=0)

    grow(t1, T.a_sixty)
    grow(t2, T.a_order)

    # ── apart from the order, no other way: both sets of leaves land on the same row ──
    row = tex(r"60", r"=", r"2", r"\cdot", r"2", r"\cdot", r"3", r"\cdot", r"5", size=52,
              colors={2: C.prime, 4: C.prime, 6: C.prime, 8: C.prime})
    row.move_to([0, -2.2, 0])
    slots = (row[2], row[4], row[6], row[8])
    moves = [TransformFromCopy(t1.leaves[i], slots[j]) for i, j in enumerate((0, 2, 1, 3))]
    moves += [TransformFromCopy(t2.leaves[i], slots[i].copy()) for i in range(4)]
    w.play(*moves, at=T.a_noother, dur=1.0)
    w.play(FadeIn(VGroup(row[0], row[1], row[3], row[5], row[7])), at=T.a_noother + 0.7, dur=0.5, lead=0)
    atoms = lab("atoms", 32, C.prime).next_to(row, DOWN, buff=0.3)
    w.play(FadeIn(atoms, shift=0.06 * UP), at=T.a_atoms, dur=0.6)
    part_a = VGroup(t1, t2, atoms)
    landed = VGroup(*[m.mobject for m in moves])             # the leaf copies that now sit on the row
    w.play(FadeOut(part_a), FadeOut(VGroup(row[0], row[1], row[3], row[5], row[7], landed)), at=T.a_euclid - 0.9,
           dur=0.6, lead=0)
    h.play(FadeOut(VGroup(gen, one)), at=T.a_euclid - 0.9, dur=0.6, lead=0)

    # ── Euclid: the primes never run out ──
    portrait_card(s, h, "euclid", r"Euclid $\cdot$ c.\ 300 BC", T.a_euclid, T.cut_sieve - 0.05, (5.6, 2.55),
                  height=1.8, name_size=24)
    lst = tex(r"2,3,5,7,11,13,\ldots", size=38, color=C.prime)
    pin(lst, top=3.55, left=-6.2)
    h.play(FadeIn(lst, shift=0.06 * RIGHT), at=T.a_runout, dur=0.6)

    # combs: the multiples of 2, 3, 5, 7 as teeth, one row each; then the view pushes in on 210
    draw = [T.a_runout + 0.2 + 0.25 * k for k in range(4)]
    win = keys((T.a_multiply - L, (0.0, 220.0)), (T.a_multiply + 1.0, ZOOM, EASE), lead=0)

    def combs(t):
        lo, hi = (float(v) for v in win(t))
        X = lambda n: X0 + (X1 - X0) * (n - lo) / (hi - lo)              # noqa: E731
        g = VGroup(Line([X0 - 0.1, AX, 0], [X1 + 0.1, AX, 0], color=C.axis, stroke_width=2.0))
        for k, p in enumerate(PS):
            r = float(np.clip((t - draw[k]) / 0.4, 0.0, 1.0))
            top = lo + r * (hi - lo)
            y0 = AX + 0.1 + 0.34 * k
            for m in range(p * int(np.ceil(max(lo, 1) / p)), int(min(hi, top)) + 1, p):
                g.add(Line([X(m), y0, 0], [X(m), y0 + 0.24, 0], color=sieve_color(p), stroke_width=2.4))
        step = 50 if hi - lo > 60 else 5
        for n in range(int(np.ceil(lo / step)) * step, int(hi) + 1, step):
            g.add(tex(str(n), size=24, color=C.muted).move_to([X(n), AX - 0.3, 0]))
        return g

    w.redraw(combs, during=(draw[0] - L, T.a_multiply + 1.0))
    keys_lab = VGroup(*[tex(r"\times%d" % p, size=26, color=sieve_color(p)).move_to(
        [X0 - 0.45, AX + 0.22 + 0.34 * k, 0]) for k, p in enumerate(PS)])
    h.play(FadeIn(keys_lab), at=draw[0], dur=0.6)

    # ── multiply the list: 210 has a tooth in every comb; add one: 211 has none ──
    Xz = lambda n: X0 + (X1 - X0) * (n - ZOOM[0]) / (ZOOM[1] - ZOOM[0])     # noqa: E731
    prod = tex(r"2\cdot3\cdot5\cdot7", r"=210", r"\quad 210+1", r"=211", size=44)
    prod.move_to([0, 1.75, 0])
    h.play(Write(prod[:2]), at=T.a_multiply + 0.2, dur=1.0)
    cur = Line([Xz(210), AX - 0.12, 0], [Xz(210), AX + 1.45, 0], color=C.text, stroke_width=2.4)
    hits = VGroup(*[Line([Xz(210), AX + 0.1 + 0.34 * k, 0], [Xz(210), AX + 0.34 + 0.34 * k, 0],
                         color=sieve_color(p), stroke_width=7.0) for k, p in enumerate(PS)])
    w.play(Create(cur), at=T.a_multiply + 1.0, dur=0.4, lead=0)
    w.play(FadeIn(hits, scale=1.3), at=T.a_multiply + 1.2, dur=0.3, lead=0)
    w.play(FadeOut(hits), at=T.a_addone - 0.1, dur=0.3, lead=0)
    w.play(cur.animate.move_to([Xz(211), cur.get_y(), 0]), at=T.a_addone, dur=0.5)
    h.play(FadeIn(prod[2:], shift=0.06 * LEFT), at=T.a_addone + 0.3, dur=0.6)

    # ── dividing by any prime on the list leaves remainder one ──
    chips = VGroup(*[carded(tex(r"211", r"=%d\cdot%d" % (211 // p, p), r"+1", size=32,
                                colors={1: sieve_color(p)}), p) for p in PS]).arrange(RIGHT, buff=0.45)
    chips.move_to([0, -1.55, 0])
    for k, c in enumerate(chips):
        h.play(FadeIn(c, shift=0.08 * UP), at=T.a_divide + 0.6 + 0.45 * k, dur=0.4)
    h.play(*[Indicate(c[1][2], color=C.text, scale_factor=1.3) for c in chips], at=T.a_rem + 0.3, dur=0.9)

    # ── the product + 1 need not be prime, but its prime factors are new ──
    big = tex(r"2\cdot3\cdot5\cdot7\cdot11\cdot13+1", r"=30031", r"=59\cdot509", size=40, colors={2: C.prime})
    big.move_to([0, -2.75, 0])
    new = lab("both factors new", 28, C.prime).next_to(big, DOWN, buff=0.22)
    h.play(FadeIn(big[:2], shift=0.06 * UP), at=T.a_new, dur=0.6)
    h.play(FadeIn(big[2], shift=0.06 * LEFT), FadeIn(new), at=T.a_new + 1.2, dur=0.6)


def carded(mob, p):
    """A remainder chip: the division on a black card outlined in the prime's sieve color."""
    box = SurroundingRectangle(mob, color=sieve_color(p), stroke_width=1.6, buff=0.12, corner_radius=0.08)
    return VGroup(box, mob)
