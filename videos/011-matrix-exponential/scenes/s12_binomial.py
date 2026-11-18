"""s12 binomial (ch3): where 1/k! comes from. Expanding (I + (t/n) A)^n, each term picks which of the n steps used
(t/n) A while the rest used I. One step: n choices of weight t/n, total tA. Two steps: C(n, 2) ≈ n²/2 pairs, total
t²A²/2. Three steps: C(n, 3) ≈ n³/3!, because the same three nudges arrive in 3! = 6 orders. In the limit: the
series e^A = I + A + A²/2! + A³/3! + ⋯, the series for e^x with a matrix for the number and I for 1."""
from itertools import permutations

from aion import *

from beats import T
from shots import E, backdrop, backed, finish, lab, live, p3, tex

NSL = 12                                              # slots on screen (n of them, in principle)
SY, SW, SG = 2.0, 0.82, 0.98                          # slot row height, slot width, slot pitch
PAIRS = [(0, 3), (1, 7), (2, 10), (4, 5), (6, 11), (3, 9), (0, 8), (5, 10)]
TRIPLE = (2, 6, 9)
TCOL = [C.gen, C.eigen, C.gen_b]                     # the three nudges of the triple, told apart


def sx(i):
    return (i - (NSL - 1) / 2) * SG


@scene(T.cut_binom, T.cut_terms)
def s12_binomial(s):
    backdrop(s)
    m = s.manim(z=2)

    # ── the power, written out as n factors ──
    pw = tex(r"\left(I+\tfrac{t}{n}A\right)^{n}", size=52, color=C.money).move_to([0, 3.35, 0])
    m.play(FadeIn(pw, shift=0.1 * DOWN), at=T.expand + 0.1, dur=0.6)

    t_one = (T.one_step + 0.4, T.one_step + 3.4)
    t_two = (T.two_steps + 0.3, T.two_steps + 4.0)
    t_three = (T.three_steps + 0.2, T.series - 0.6)
    choose = [(T.choosing + 0.3, (2, 8)), (T.choosing + 1.3, (5,)), (T.choosing + 2.2, (1, 6, 10))]

    def chosen(t):
        """The slots that use (t/n) A at time t, with a color for each."""
        if t_one[0] <= t < t_one[1] + 0.6:
            i = int(np.clip((t - t_one[0]) / (t_one[1] - t_one[0]) * NSL, 0, NSL - 1))
            return {i: C.gen}
        if t_two[0] <= t < t_two[1] + 0.6:
            k = int(np.clip((t - t_two[0]) / (t_two[1] - t_two[0]) * len(PAIRS), 0, len(PAIRS) - 1))
            return {i: C.gen for i in PAIRS[k]}
        if t_three[0] <= t < t_three[1]:
            return dict(zip(TRIPLE, TCOL))
        for at, sel in choose[::-1]:
            if at <= t < choose[-1][0] + 1.0 and t >= at:
                return {i: C.gen for i in sel}
        return {}

    s_op = keys((T.expand + 0.5, 0.0), (T.expand + 1.2, 1.0), (T.series - 0.6, 1.0), (T.series - 0.1, 0.0), lead=0)

    def slots(t):
        op = float(s_op(t))
        ch = chosen(t)
        out = VGroup()
        for i in range(NSL):
            col = ch.get(i)
            box = Rectangle(width=SW, height=0.78, stroke_color=col or C.frame, stroke_width=C.thin + (1.0 if col else 0.2),
                            stroke_opacity=op, fill_color=col or C.bg, fill_opacity=(0.14 if col else 0.0) * op
                            ).move_to(p3((sx(i), SY)))
            txt = tex(r"\tfrac{t}{n}A" if col else "I", size=30 if col else 34, color=col or C.muted)
            out.add(box, txt.move_to(box).set_opacity(op))
        return out
    live(m, slots, (T.expand + 0.5, T.series - 0.05))
    br = Brace(Line(p3((sx(0) - SW / 2, SY - 0.42)), p3((sx(NSL - 1) + SW / 2, SY - 0.42))), DOWN, buff=0.08,
               color=C.muted)
    br_l = lab("n steps", 26, C.muted).next_to(br, DOWN, buff=0.1)
    m.play(FadeIn(br), FadeIn(br_l), at=T.expand + 1.2, dur=0.5)
    m.play(FadeOut(VGroup(br, br_l)), at=T.one_step - 0.3, dur=0.4)

    # ── the counts ──
    RX, RY = -6.2, [0.55, -0.85, -2.25]
    rows = [
        tex(r"n", r"\cdot", r"\tfrac{t}{n}A", "=", r"tA", size=46, colors={0: C.money, 2: C.gen, 4: C.gen}),
        tex(r"\tbinom{n}{2}", r"\approx", r"\tfrac{n^2}{2}", r"\;\Rightarrow\;", r"\tfrac{t^2A^2}{2}", size=46,
            colors={0: C.money, 2: C.money, 4: C.gen}),
        tex(r"\tbinom{n}{3}", r"\approx", r"\tfrac{n^3}{3!}", r"\;\Rightarrow\;", r"\tfrac{t^3A^3}{3!}", size=46,
            colors={0: C.money, 2: C.money, 4: C.gen}),
    ]
    tags = [lab(w, 26, C.muted) for w in ("one step", "two steps", "three steps")]
    for r, tg, y in zip(rows, tags, RY):
        tg.move_to([RX, y, 0], aligned_edge=LEFT)
        r.next_to(tg, RIGHT, buff=0.45)
    m.play(FadeIn(tags[0]), at=T.one_step, dur=0.4)
    m.play(FadeIn(rows[0][:3]), at=t_one[0] + 0.3, dur=0.5)
    m.play(FadeIn(rows[0][3:]), at=t_one[1] - 0.2, dur=0.5)
    m.play(FadeIn(tags[1]), FadeIn(rows[1][:3]), at=T.two_steps + 1.0, dur=0.6)
    m.play(FadeIn(rows[1][3:]), at=T.two_steps + 3.2, dur=0.6)
    m.play(FadeIn(tags[2]), FadeIn(rows[2][:3]), at=T.three_steps + 0.6, dur=0.6)

    # ── six orders of the same three nudges fan out, then merge ──
    PX, PY = 3.1, -0.65
    perms = list(permutations(range(3)))
    fan = VGroup()
    for k, pm in enumerate(perms):
        y = PY - 0.42 * k
        row = VGroup(*[Dot(p3((PX + 0.38 * j, y)), radius=0.11, color=TCOL[pm[j]]) for j in range(3)])
        arr = Arrow(p3((PX - 0.45, y)), p3((PX - 0.1, y)), buff=0, color=C.muted, stroke_width=C.thin + 0.4,
                    tip_length=0.1, max_stroke_width_to_length_ratio=40)
        fan.add(VGroup(arr, row))
    one = VGroup(*[Dot(p3((PX + 0.38 * j + 2.1, PY - 1.05)), radius=0.13, color=TCOL[j]) for j in range(3)])
    fact = tex(r"3!", "=", "6", size=46, colors={0: C.money, 2: C.money}).next_to(fan, RIGHT, buff=1.4).shift(0.75 * UP)
    m.play(LaggedStart(*[FadeIn(f, shift=0.15 * RIGHT) for f in fan], lag_ratio=0.15), at=T.three_steps + 1.6, dur=1.4)
    m.play(FadeIn(fact, scale=0.9), at=T.orders - 0.7, dur=0.5)
    m.play(*[Transform(f[1], one.copy()) for f in fan], FadeOut(VGroup(*[f[0] for f in fan])), at=T.orders - 0.1,
           dur=0.7, ease=E)
    m.play(FadeIn(rows[2][3:]), at=T.orders + 0.4, dur=0.5)

    # ── in the limit: the series, above its scalar twin ──
    old = VGroup(pw, *rows, *tags, *[f[1] for f in fan], fact)
    m.play(FadeOut(old), at=T.series + 0.1, dur=0.5)
    parts = [r"e^{A}", "=", "I", "+", "A", "+", r"\frac{A^2}{2!}", "+", r"\frac{A^3}{3!}", "+", r"\cdots"]
    twin_p = [r"e^{x}", "=", "1", "+", "x", "+", r"\frac{x^2}{2!}", "+", r"\frac{x^3}{3!}", "+", r"\cdots"]
    hero = tex(*parts, size=78, colors={0: C.flow, 2: C.gen, 4: C.gen, 6: C.gen, 8: C.gen}).move_to([0, 1.0, 0])
    twin = tex(*twin_p, size=60, color=C.muted)
    for i in range(len(parts)):                         # align the twin term by term under the hero
        twin[i].move_to([hero[i].get_center()[0], -1.25, 0])
    m.play(Write(hero), at=T.series + 1.0, dur=3.2)
    m.play(FadeIn(twin, shift=0.1 * UP), at=T.series + 7.5, dur=1.0)
    m.play(Indicate(hero[2], color=C.gen, scale_factor=1.35), Indicate(twin[2], color=C.text, scale_factor=1.35),
           at=T.identity_one + 0.3, dur=0.9)
    m.play(FadeOut(VGroup(hero, twin)), at=T.cut_terms - 0.4, dur=0.5)
    finish(s)
