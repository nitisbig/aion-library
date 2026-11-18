"""s02 tangled: real things change together. A pill's molecules seep from the stomach into the blood and are cleared
from the blood (seeded random times, the same law as the curves beside them). Two amounts, tangled: the stomach drives
the blood. Rooms, circuits and buildings tangle the same way, and writing any of them down gives x' = A x. Next to
x' = kx ⇒ e^{kt} x0, the guess e^{tA} x0 is irresistible, but e raised to a grid of numbers means nothing yet."""
from aion import *

from beats import T
from shots import (BLOOD_C, CAST, E, STOMACH_C, Molecules, backdrop, building_icon, circuit_icon, compartments, dim,
                   finish, lab, live, mini_axes, p3, pill_shape, plot, rooms_icon, tex, words)

KA, KE = -CAST["pill"][0, 0], -CAST["pill"][1, 1]
HMAX = 9.0                                            # hours shown on the plot
PO, PW, PH = np.array([0.9, -3.3]), 5.6, 3.9          # amounts plot (stomach s, blood b)


def s_amt(h):
    return np.exp(-KA * np.asarray(h, float))


def b_amt(h):
    h = np.asarray(h, float)
    return KA / (KA - KE) * (np.exp(-KE * h) - np.exp(-KA * h))


@scene(T.cut_tangled, T.cut_history)
def s02_tangled(s):
    backdrop(s)
    m0 = s.manim(z=0)                                 # compartments, plot (rebuilt while the pill acts)
    m = s.manim(z=1)

    t_land = T.pill + 0.75
    mol = Molecules(n=400, seed=11, t0=T.seeps - 0.2, sec_per_hour=1.15)
    t_away = T.rooms - 0.2                            # the pill picture leaves

    # ── the body: stomach above, bloodstream below ──
    body = compartments()
    m.play(Create(body), at=T.alone + 0.4, dur=1.4, ease=E)

    # ── swallow a pill: it drops in, then dissolves into molecules ──
    pill = pill_shape((STOMACH_C[0], 4.6), L=0.7, r=0.17, angle=0.5)
    m.add(pill, at=T.pill - 0.2)
    m.drive(pill, lambda p, t: p.move_to(p3((STOMACH_C[0], 4.6 + (STOMACH_C[1] - 4.6) * smooth(np.clip(
        (t - T.pill + 0.2) / 0.95, 0, 1))))), during=(T.pill - 0.2, t_land))
    m.play(FadeOut(pill, scale=0.6), at=t_land + 0.35, dur=0.45)
    op_mol = keys((t_land, 0.0), (t_land + 0.5, 1.0), (t_away - 0.3, 1.0), (t_away + 0.4, 0.0), lead=0)
    s.add(PointsLayer(mol.pos, color=C.vec, size=3.2, glow=0.0, alpha=op_mol, additive=False, z=0.5,
                      start=t_land, end=t_away + 0.5))

    # ── seeps (k_a) and clears (k_e) ──
    duct_mid = (STOMACH_C + BLOOD_C) / 2 + [0, 0.35]
    ka = tex(r"k_a", size=40, color=C.gen).move_to(p3(duct_mid + [0.6, 0]))
    out_a = Arrow(p3(BLOOD_C + [1.9, -0.2]), p3(BLOOD_C + [2.9, -0.75]), buff=0, color=C.gen, stroke_width=C.stroke,
                  tip_length=0.2, max_tip_length_to_length_ratio=0.3)
    ke = tex(r"k_e", size=40, color=C.gen).next_to(out_a.get_end(), DOWN, buff=0.12)
    m.play(FadeIn(ka, shift=0.1 * DOWN), at=T.seeps + 0.6, dur=0.5)
    m.play(GrowArrow(out_a), FadeIn(ke), at=T.clears + 0.4, dur=0.6)

    # ── the two amounts over time ──
    op_plot = keys((T.seeps - 0.6, 0.0), (T.seeps, 1.0), (t_away - 0.3, 1.0), (t_away + 0.4, 0.0), lead=0)

    def amounts(t):
        a = float(op_plot(t))
        h = min(mol.hours(t), HMAX)
        g = VGroup(mini_axes(PO, PW, PH))
        xs, ys = PW / HMAX, PH * 0.95
        if h > 0.02:
            g.add(plot(s_amt, 0, h, PO, xs, ys, C.dose, width=C.stroke))
            g.add(plot(b_amt, 0, h, PO, xs, ys, C.flow, width=C.stroke))
        for f, col, nm in ((s_amt, C.dose, "s"), (b_amt, C.flow, "b")):
            p = PO + [xs * h, ys * float(f(h))]
            g.add(Dot(p3(p), radius=0.07, color=col))
            g.add(tex(nm, size=36, color=col).next_to(p3(p), UR, buff=0.06))
        return dim(g, a)
    live(m0, amounts, (T.seeps - 0.6, t_away + 0.4))
    hl = lab("hours", 26).next_to(p3(PO + [PW / 2, 0]), DOWN, buff=0.15)
    m.play(FadeIn(hl), at=T.seeps, dur=0.5)
    m.play(FadeOut(hl), at=t_away, dur=0.4)

    # ── two amounts, tangled together ──
    e1 = tex(r"\dot s", "=", r"-k_a", r"\,s", size=44, colors={0: C.dose, 2: C.gen, 3: C.dose})
    e2 = tex(r"\dot b", "=", r"k_a", r"\,s", "-", r"k_e", r"\,b", size=44,
             colors={0: C.flow, 2: C.gen, 3: C.dose, 5: C.gen, 6: C.flow})
    pair = VGroup(e1, e2).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([3.6, 2.55, 0])
    e2.shift((e1[1].get_center()[0] - e2[1].get_center()[0]) * RIGHT)
    m.play(FadeIn(e1, shift=0.1 * UP), at=T.tangled - 0.4, dur=0.6)
    m.play(FadeIn(e2, shift=0.1 * UP), at=T.tangled + 0.3, dur=0.6)
    m.play(Indicate(e2[3], color=C.dose, scale_factor=1.4), at=T.tangled + 1.2, dur=0.8)

    # ── rooms, circuits, buildings: the same tangle ──
    m.play(FadeOut(VGroup(body, ka, ke, out_a)), at=t_away, dur=0.5)
    m.play(pair.animate.move_to([0, 2.55, 0]), at=t_away + 0.2, dur=0.8, ease=E)
    icons = [rooms_icon((-4.4, -0.5), s=0.95, color=C.warm), circuit_icon((0, -0.5), s=0.95, color=C.gen_b)]
    tags = [lab(w_, 28, col).move_to([x, -2.35, 0]) for w_, col, x in
            (("heat", C.warm, -4.4), ("current", C.gen_b, 0.0), ("sway", C.eigen, 4.4))]
    for k, ic in enumerate(icons):
        m.play(Create(ic), FadeIn(tags[k], shift=0.1 * UP), at=T.rooms + 0.4 + 1.6 * k, dur=0.9, ease=E)
    m.play(FadeIn(tags[2], shift=0.1 * UP), at=T.rooms + 3.6, dur=0.6)
    bw = wave(freq=0.55, amp=0.4, during=(T.rooms + 3.6, T.one_shape))
    op_b = keys((T.rooms + 3.3, 0.0), (T.rooms + 4.0, 1.0), (T.one_shape - 0.1, 1.0), (T.one_shape + 0.4, 0.0), lead=0)
    m.redraw(lambda t: dim(building_icon((4.4, -0.5), s=0.95, sway=float(bw(t)), color=C.eigen), float(op_b(t))),
             during=(T.rooms + 3.3, T.one_shape + 0.4))

    # ── one shape of equation: d/dt [s b] = A [s b] ──
    def xv():
        v = Mat([["s"], ["b"]], size=44, v_buff=0.72)
        v.cell(0, 0).set_color(C.dose)
        v.cell(1, 0).set_color(C.flow)
        return v
    A = Mat([["-k_a", "0"], ["k_a", "-k_e"]], colors=C.gen, size=44, h_buff=1.25, v_buff=0.72)
    big = VGroup(tex(r"\frac{d}{dt}", size=44), xv(), tex("=", size=44), A, xv()).arrange(RIGHT, buff=0.22)
    big.move_to([0, 0.2, 0])
    m.play(FadeOut(VGroup(*icons, *tags)), at=T.one_shape - 0.1, dur=0.5)
    m.play(TransformFromCopy(pair, big), at=T.one_shape + 0.3, dur=1.2, ease=E)

    # ── a matrix, times that list ──
    small = tex(r"\dot{\mathbf x}", "=", "A", r"\,\mathbf x", size=64, colors={0: C.vec, 2: C.gen, 3: C.vec})
    small.move_to([0, -2.1, 0])
    m.play(FadeIn(small, shift=0.15 * DOWN), at=T.mat_times + 0.4, dur=0.8)

    # ── next to the one-number version ──
    ARR_X, ROW1, ROW2 = -0.75, 2.3, 0.9
    l1 = tex(r"\dot x", "=", "k", r"\,x", size=60, colors={2: C.gen})
    l2 = tex(r"\dot{\mathbf x}", "=", "A", r"\,\mathbf x", size=60, colors={0: C.vec, 2: C.gen, 3: C.vec})
    a1, a2 = (tex(r"\Longrightarrow", size=52, color=C.muted) for _ in range(2))
    r1 = tex(r"x(t)", "=", r"e^{kt}", r"\,x_0", size=60, colors={2: C.flow})
    r1[2][1].set_color(C.gen)
    r2 = tex(r"\mathbf x", "(t)", "=", r"e^{tA}", r"\,\mathbf x_0", size=60, colors={0: C.vec, 3: C.flow, 4: C.vec})
    r2[3][2].set_color(C.gen)
    R2E = r2[3]
    for row, (l, a, r) in ((ROW1, (l1, a1, r1)), (ROW2, (l2, a2, r2))):
        a.move_to([ARR_X, row, 0])
        l.next_to(a, LEFT, buff=0.45)
        r.next_to(a, RIGHT, buff=0.45)
    l2.align_to(l1, RIGHT)
    m.play(FadeOut(VGroup(pair, big)), at=T.next_to - 0.3, dur=0.5)
    m.play(ReplacementTransform(small, l2), at=T.next_to, dur=0.9, ease=E)
    m.play(FadeIn(l1, shift=0.1 * DOWN), at=T.next_to + 0.6, dur=0.6)
    m.play(FadeIn(a1), FadeIn(r1, shift=0.1 * LEFT), at=T.next_to + 3.3, dur=0.6)
    m.play(FadeIn(a2), at=T.tempting + 0.6, dur=0.5)
    m.play(FadeIn(r2, shift=0.1 * LEFT), at=T.tempting + 1.5, dur=0.6)

    # ── e, raised to the power of a matrix ──
    E0 = np.array([-2.6, -2.1])
    e_big = tex("e", size=120, color=C.flow).move_to(p3(E0))
    grid = Mat([["a", "b"], ["c", "d"]], colors=C.gen, size=40, h_buff=0.75, v_buff=0.62)
    grid.next_to(e_big, UR, buff=0.02).shift(0.35 * DOWN)
    m.play(Indicate(R2E, color=C.flow, scale_factor=1.15), at=T.e_matrix - 0.4, dur=0.7)
    m.play(TransformFromCopy(R2E[0], e_big), TransformFromCopy(R2E[2], grid), at=T.e_matrix + 0.3, dur=1.1,
           ease=E)
    q = tex("?", size=96, color=C.muted).next_to(VGroup(e_big, grid), RIGHT, buff=0.5)
    m.play(FadeIn(q, scale=0.8), at=T.meaningless + 0.8, dur=0.5)
    times = tex(r"=\;", r"\underbrace{e\cdot e\cdots e}", size=56, color=C.muted)
    times.next_to(VGroup(e_big, grid), RIGHT, buff=0.4).shift(0.15 * DOWN)
    qt = tex("?", r"\ \text{times}", size=36, colors={0: C.gen}, color=C.muted).next_to(times[1], DOWN, buff=0.12)
    m.play(FadeOut(q), FadeIn(times), FadeIn(qt), at=T.grid_times + 0.3, dur=0.6)

    m.play(FadeOut(VGroup(l1, l2, a1, a2, r1, r2, e_big, grid, times, qt)), at=T.cut_history - 0.4, dur=0.5)
    finish(s)
