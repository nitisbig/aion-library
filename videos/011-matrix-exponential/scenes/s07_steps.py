"""s07 steps (ch1): the same flow built from small steps, the way Bernoulli's banker did. Split the second into n
pieces; in each, a point moves by velocity × step = x/n, so it is multiplied by 1 + 1/n. After n steps it sits at
(1 + 1/n)^n: n = 4 → 2.441, n = 12 → 2.613, n = 100 → 2.705, closing in on e. Multiplying the limit out gives the
series 1 + x + x²/2! + ⋯. Three faces of e^x (flow, steps, sum), and all three make the jump to matrices."""
from aion import *

from beats import T
from shots import E, backdrop, backed, finish, lab, live, p3, panel, poly, tex

LY, LU, LX0 = -0.7, 1.12, -1.4                        # the same number line as s06
BY = 2.0                                              # the one-second bar
BX0, BX1 = -3.0, 3.0


def X(x):
    return np.array([LX0 + LU * x, LY])


def hop_times(n, t0, t1):
    return np.linspace(t0, t1, n + 1)[:-1]


RUNS = [(4, T.split + 2.6, T.one_plus - 0.2), (12, T.n_times + 0.4, T.n_times + 3.4),
        (100, T.n_times + 3.8, T.n_times + 5.2)]
for n, _, _ in RUNS:
    assert abs((1 + 1 / n) ** n - [2.4414, 2.6130, 2.7048][[4, 12, 100].index(n)]) < 1e-3


def value(t):
    """Where the dot is at time t: the latest run's (1 + 1/n)^k, with each hop eased over its slot."""
    v, n_now = 1.0, None
    for n, t0, t1 in RUNS:
        if t < t0 - 0.35:
            break
        n_now = n
        if t < t0:                                     # slide back to 1 before a new run
            return 1.0 + (v - 1.0) * (1 - smooth(np.clip((t - t0 + 0.35) / 0.35, 0, 1))), n
        slot = (t1 - t0) / n
        k = min((t - t0) / slot, n)
        whole = int(np.floor(k))
        frac = smooth(min(1.0, (k - whole) / 0.7)) if whole < n else 0.0
        v = (1 + 1 / n) ** whole * (1 + frac / n)
    return v, n_now


@scene(T.cut_steps, T.cut_ch2)
def s07_steps(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=2)

    # the line, numbers and e tick carry over from s06
    line = NumberLine(x_range=[-4, 6, 1], length=10 * LU, color=C.text, stroke_width=C.thin + 0.6,
                      include_tip=False, tick_size=0.07).move_to(p3(X(1.0)))
    nums = VGroup(*[tex(str(k), size=30, color=C.muted).move_to(p3(X(k) + [0, -0.42])) for k in range(-4, 7)])
    e_t = VGroup(Line(p3(X(np.e) + [0, -0.12]), p3(X(np.e) + [0, 0.12]), color=C.flow, stroke_width=C.stroke),
                 tex("e", size=40, color=C.flow).move_to(p3(X(np.e) + [0, -0.85])))
    m.add(line, nums, e_t)

    # ── one point, at 1 ──
    d_op = keys((T.steps + 0.3, 0.0), (T.steps + 0.8, 1.0), (T.faces - 0.6, 1.0), (T.faces - 0.1, 0.0), lead=0)
    first, last = RUNS[0][1], RUNS[-1][2]

    def dot(t):
        v, n = value(t) if t >= first - 0.35 else (1.0, None)
        a = float(d_op(t))
        out = VGroup(Dot(p3(X(v)), radius=0.11, color=C.vec).set_opacity(a))
        if n is not None and a > 0.01 and v < 2.72:   # velocity × step: the hop about to happen
            out.add(Arrow(p3(X(v) + [0, 0.42]), p3(X(v + v / n) + [0, 0.42]), buff=0, color=C.gen,
                          stroke_width=C.stroke - 0.5, tip_length=0.12, max_tip_length_to_length_ratio=0.5,
                          max_stroke_width_to_length_ratio=60).set_opacity(a * (1.0 if n < 50 else 0.0)))
        return out
    live(m0, dot, (T.steps + 0.3, T.steps + 0.85), (first - 0.4, last + 0.05), (T.faces - 0.6, T.faces - 0.05))

    # hop arcs (money: Bernoulli's banker), drawn as each hop lands
    def hops(t):
        out = VGroup()
        for n, t0, t1 in RUNS:
            if t < t0 or t > (RUNS[RUNS.index((n, t0, t1)) + 1][1] - 0.35 if n != 100 else T.faces - 0.1):
                continue
            slot = (t1 - t0) / n
            k = int(min(np.floor((t - t0) / slot + 1e-9), n))
            if n == 100:
                continue
            for j in range(k):
                a, b = (1 + 1 / n) ** j, (1 + 1 / n) ** (j + 1)
                out.add(ArcBetweenPoints(p3(X(a) + [0, 0.13]), p3(X(b) + [0, 0.13]), angle=-1.2, color=C.money,
                                         stroke_width=C.thin + 0.6))
        return out
    live(m, hops, (first, last + 0.05))

    # ── split the second into n pieces ──
    bar = Line(p3((BX0, BY)), p3((BX1, BY)), color=C.text, stroke_width=C.stroke)
    bar_lab = lab("one second", 26).next_to(bar, UP, buff=0.18)

    def pieces(t):
        n = 4 if t < RUNS[1][1] - 0.35 else (12 if t < RUNS[2][1] - 0.35 else 100)
        idx = [r[0] for r in RUNS].index(n)
        _, t0, t1 = RUNS[idx]
        done = int(np.clip(np.floor((t - t0) / ((t1 - t0) / n)) + 1, 0, n)) if t >= t0 else 0
        out = VGroup()
        for j in range(n + 1):
            x = BX0 + (BX1 - BX0) * j / n
            out.add(Line(p3((x, BY - 0.12)), p3((x, BY + 0.12)), color=C.money, stroke_width=C.thin + (0.6 if n < 50 else 0)))
        if done:
            out.add(Line(p3((BX0, BY)), p3((BX0 + (BX1 - BX0) * done / n, BY)), color=C.money, stroke_width=C.stroke + 1.5))
        return out
    m.play(Create(bar), FadeIn(bar_lab), at=T.split, dur=0.7)
    hp = live(m, pieces, (T.split + 0.6, last + 0.05))
    frac = tex(r"\tfrac{1}{n}", size=34, color=C.money).move_to(p3(((BX0 * 3 + BX1) / 4 + 0.0, BY - 0.5)))
    frac.move_to(p3((BX0 + (BX1 - BX0) / 8, BY - 0.48)))
    m.play(FadeIn(frac), at=T.split + 1.2, dur=0.5)

    # n and the landing value
    def readout(t):
        v, n = value(t) if t >= first - 0.35 else (1.0, 4)
        nn = VGroup(tex("n", "=", size=40, colors={0: C.money}),
                    Integer(n if n else 4, font_size=40, color=C.money)).arrange(RIGHT, buff=0.15)
        xv = VGroup(tex("x", "=", size=40, colors={0: C.vec}),
                    DecimalNumber(v, num_decimal_places=3, font_size=40, color=C.vec)).arrange(RIGHT, buff=0.15)
        g = VGroup(nn, xv).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([5.3, 2.3, 0])
        return g
    r_op = keys((T.split + 0.4, 0.0), (T.split + 0.9, 1.0), (T.series1 - 0.6, 1.0), (T.series1 - 0.1, 0.0), lead=0)
    live(m, lambda t: readout(t).set_opacity(float(r_op(t))), (T.split + 0.4, T.split + 0.95), (first - 0.4, last + 0.05),
         (T.series1 - 0.6, T.series1 - 0.05))

    # ── each step: multiplied by 1 + 1/n ──
    step = tex(r"x", r"\;\to\;", r"x + \tfrac{x}{n}", "=", r"\left(1+\tfrac{1}{n}\right)", r"x", size=46,
               colors={0: C.vec, 2: C.gen, 4: C.money, 5: C.vec}).move_to([-1.2, 3.25, 0])
    m.play(FadeIn(step[:3], shift=0.1 * DOWN), at=T.split + 4.4, dur=0.6)
    m.play(FadeIn(step[3:], shift=0.1 * DOWN), at=T.one_plus, dur=0.6)

    # ── as n grows: the limit, then the series ──
    lim = tex(r"\lim_{n\to\infty}\left(1+\tfrac{x}{n}\right)^{n}", size=50, color=C.money)
    lim.move_to([-1.2, 3.2, 0])
    m.play(FadeOut(step, shift=0.1 * UP), FadeIn(lim, shift=0.1 * UP), at=T.n_times + 3.4, dur=0.7)
    m.play(FadeOut(VGroup(bar, bar_lab, frac)), at=T.series1 - 0.6, dur=0.5)
    m.remove(hp[-1], at=T.series1 - 0.05)
    ser = tex("=", "1", "+", "x", "+", r"\frac{x^2}{2!}", "+", r"\frac{x^3}{3!}", "+", r"\cdots", size=50,
              colors={1: C.gen, 3: C.gen, 5: C.gen, 7: C.gen})
    grp = VGroup(lim.copy(), ser).arrange(RIGHT, buff=0.25).move_to([0, 2.6, 0])
    m.play(lim.animate.move_to(grp[0]), at=T.series1, dur=0.6, ease=E)
    m.play(Write(ser), at=T.series1 + 0.5, dur=1.4)

    # ── three faces ──
    m.play(FadeOut(VGroup(line, nums, e_t)), lim.animate.set_opacity(0.0), ser.animate.set_opacity(0.0),
           at=T.faces - 0.2, dur=0.5)
    CY, CWd, CHt = -0.45, 4.1, 4.3
    cards = []
    specs = [("flow", C.flow, -4.35, T.faces + 0.9, r"e^{\,t\,x}", r"e^{\,t A}"),
             ("steps", C.money, 0.0, T.faces + 2.0, r"\left(1+\tfrac{x}{n}\right)^{n}", r"\left(I+\tfrac{A}{n}\right)^{n}"),
             ("sum", C.gen, 4.35, T.faces + 3.3, r"\sum_k \frac{x^k}{k!}", r"\sum_k \frac{A^k}{k!}")]
    for name, col, cx, at, f1, f2 in specs:
        fr = panel(cx - CWd / 2, CY - CHt / 2, cx + CWd / 2, CY + CHt / 2, fill=False).set_stroke(color=col)
        word = lab(name, 30, col).move_to([cx, CY + CHt / 2 - 0.38, 0])
        o = np.array([cx - 1.5, CY - 0.35])
        if name == "flow":                              # a line whose points stretch by e
            art = VGroup(Line(p3(o), p3(o + [3.0, 0]), color=C.text, stroke_width=C.thin + 0.4))
            for x0 in (0.35, 0.7):
                a, b = o + [x0 * 1.25, 0], o + [x0 * np.e * 1.25, 0]
                art.add(Dot(p3(a), radius=0.06, color=C.vec).set_opacity(0.4), Dot(p3(b), radius=0.07, color=C.vec),
                        ArcBetweenPoints(p3(a + [0, 0.08]), p3(b + [0, 0.08]), angle=-1.0, color=C.flow,
                                         stroke_width=C.thin + 0.6))
        elif name == "steps":                           # a compounding staircase
            n, pts, b = 6, [o.copy()], 0.0
            for k in range(n):
                b_new = (1 + 1 / n) ** (k + 1) - 1
                pts += [o + [3.0 * (k + 1) / n, 1.05 * b], o + [3.0 * (k + 1) / n, 1.05 * b_new]]
                b = b_new
            art = VGroup(poly(pts, C.money, C.stroke - 0.5),
                         Line(p3(o), p3(o + [3.0, 0]), color=C.muted, stroke_width=C.thin))
        else:                                           # the terms 1, 1, 1/2, 1/6, 1/24 laid end to end
            art, x = VGroup(), 0.0
            for k, tk in enumerate([1, 1, 1 / 2, 1 / 6, 1 / 24]):
                w = 1.1 * tk
                art.add(Rectangle(width=max(w - 0.03, 0.02), height=0.42, stroke_width=0, fill_color=C.gen,
                                  fill_opacity=0.95 - 0.15 * k).move_to(p3(o + [x + w / 2, 0.35])))
                x += w
            art.add(Line(p3(o + [1.1 * np.e, 0.0]), p3(o + [1.1 * np.e, 0.75]), color=C.flow, stroke_width=C.stroke))
            art.add(tex("e", size=30, color=C.flow).move_to(p3(o + [1.1 * np.e, 1.0])))
        f_x = tex(f1, size=46, color=C.text).move_to([cx, CY - CHt / 2 + 0.8, 0])
        f_a = tex(f2, size=46, color=C.gen).move_to(f_x)
        cards.append((fr, word, art, f_x, f_a))
        m.play(Create(fr), FadeIn(word), FadeIn(art, lag_ratio=0.1), FadeIn(f_x, shift=0.1 * UP), at=at, dur=0.8,
               ease=E)

    # ── all three make the jump to matrices ──
    mat = lab("now with matrices", 36, C.gen).move_to([0, 2.65, 0])
    m.play(FadeIn(mat, shift=0.1 * DOWN), at=T.jump + 0.3, dur=0.5)
    m.play(*[ReplacementTransform(c[3], c[4]) for c in cards], at=T.jump + 0.6, dur=1.0, ease=E)
    m.play(FadeOut(VGroup(mat, *[VGroup(c[0], c[1], c[2], c[4]) for c in cards])), at=T.cut_ch2 - 0.4, dur=0.5)
    finish(s)
