"""s18 three shapes (ch5): for numbers e^{a+b} = e^a e^b; matrices refuse. Two shears, A (sideways) and B (up and
down). Run A for one unit then B: the unit square becomes [[1,1],[1,2]] = e^B e^A (maps apply right to left). B then
A: [[2,1],[1,1]] = e^A e^B. Both at once, adding velocities: e^{A+B} = [[cosh 1, sinh 1],[sinh 1, cosh 1]], a third
shape. All three keep the area at one, but they are genuinely different."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, backdrop, backed, chapter_card, finish, lab, live, p3, panel, poly, tex
from verify import B, N

A = N
EA, EB, EAB = expm(A), expm(B), expm(A + B)
assert np.allclose(EB @ EA, [[1, 1], [1, 2]]) and np.allclose(EA @ EB, [[2, 1], [1, 1]])
U = 0.72
CX, CY, HW, HH = [-4.6, 0.0, 4.6], -0.75, 2.15, 2.15
SQ = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)


def origin(i):
    return np.array([CX[i] - 1.0, CY - 1.45])


def shape(M, o, col, op=1.0, fill=0.35):
    P = [p3(o + U * (M @ q)) for q in SQ]
    body = Polygon(*P, stroke_width=0, fill_color=col, fill_opacity=fill * op)
    edges = VGroup(Line(P[0], P[1], color=C.ihat, stroke_width=C.stroke + 1, stroke_opacity=op),
                   Line(P[1], P[2], color=col, stroke_width=C.stroke, stroke_opacity=op),
                   Line(P[2], P[3], color=col, stroke_width=C.stroke, stroke_opacity=op),
                   Line(P[3], P[0], color=C.jhat, stroke_width=C.stroke + 1, stroke_opacity=op))
    return VGroup(body, edges)


@scene(T.cut_ch5, T.cut_gap)
def s18_three_shapes(s):
    backdrop(s)
    m = s.manim(z=2)
    chapter_card(m, 5, "The rule that breaks", r"[A,B]", T.cut_ch5, color=C.comm)

    # ── the rule for numbers, and the question for matrices ──
    r1 = tex(r"e^{a+b}", "=", r"e^{a}\,e^{b}", size=64).move_to([0, 0.9, 0])
    r2 = tex(r"e^{A+B}", r"\overset{?}{=}", r"e^{A}\,e^{B}", size=64, colors={1: C.comm}).move_to([0, -0.7, 0])
    m.play(FadeIn(r1, shift=0.1 * UP), at=T.rule_ab + 0.2, dur=0.7)
    m.play(FadeIn(r2, shift=0.1 * UP), at=T.refuse + 0.1, dur=0.7)
    m.play(FadeOut(r1), r2.animate.scale(0.62).move_to([0, 3.4, 0]), at=T.two_shears - 0.5, dur=0.7, ease=E)

    # ── two shears ──
    Am = VGroup(tex("A", "=", size=36, colors={0: C.gen}),
                Mat([["0", "1"], ["0", "0"]], colors=C.gen, size=32, h_buff=0.75, v_buff=0.62)).arrange(RIGHT, buff=0.15)
    Bm = VGroup(tex("B", "=", size=36, colors={0: C.gen_b}),
                Mat([["0", "0"], ["1", "0"]], colors=C.gen_b, size=32, h_buff=0.75, v_buff=0.62)).arrange(RIGHT, buff=0.15)
    Am.move_to([-5.1, 3.25, 0])
    Bm.move_to([5.1, 3.25, 0])
    m.play(FadeIn(Am, shift=0.1 * DOWN), at=T.two_shears + 0.3, dur=0.5)
    m.play(FadeIn(Bm, shift=0.1 * DOWN), at=T.two_shears + 1.6, dur=0.5)

    # ── three panels from the unit square ──
    cols = [C.warm, C.cool, C.flow]
    titles = ["A then B", "B then A", "both at once"]
    frames = VGroup()
    for i in range(3):
        box = (CX[i] - HW, CY - HH, CX[i] + HW, CY + HH)
        g = grid_lines(np.eye(2), tuple(origin(i)), U, box, n=8, opacity=0.5)
        frames.add(VGroup(g, panel(*box, fill=False), lab(titles[i], 28, cols[i]).move_to([CX[i], CY + HH + 0.32, 0])))
    m.play(LaggedStart(*[FadeIn(f) for f in frames], lag_ratio=0.2), at=T.two_shears + 2.6, dur=1.0)

    run = [(T.A_then_B + 0.5, 1.2), (T.B_then_A + 0.2, 1.2), (T.both + 0.6, 2.4)]

    def M_of(i, t):
        t0, leg = run[i]
        u = float(np.clip((t - t0) / leg, 0, 2 if i < 2 else 1)) if i < 2 else float(np.clip((t - t0) / leg, 0, 1))
        if i == 0:
            return expm(min(u, 1) * A) if u <= 1 else expm((u - 1) * B) @ EA
        if i == 1:
            return expm(min(u, 1) * B) if u <= 1 else expm((u - 1) * A) @ EB
        return expm(u * (A + B))

    sq_op = keys((T.two_shears + 3.0, 0.0), (T.two_shears + 3.6, 1.0), (T.cut_gap - 0.4, 1.0), (T.cut_gap - 0.05, 0.0),
                 lead=0)

    def shapes(t):
        op = float(sq_op(t))
        return VGroup(*[shape(M_of(i, t), origin(i), cols[i], op) for i in range(3)])
    live(m, shapes, (T.two_shears + 3.0, T.two_shears + 3.65), (run[0][0], run[0][0] + 2.45),
         (run[1][0], run[1][0] + 2.45), (run[2][0], run[2][0] + 2.45), (T.cut_gap - 0.4, T.cut_gap - 0.02))

    # which shear is running, as each leg plays
    def leg_tag(i, k, txt, col):
        t0, leg = run[i]
        tg = backed(tex(txt, size=34, color=col), buff=0.05).move_to([CX[i] + 1.3, CY + HH - 0.4, 0])
        m.play(FadeIn(tg), at=t0 + k * leg, dur=0.25)
        m.play(FadeOut(tg), at=t0 + (k + 1) * leg - 0.1, dur=0.25)
    leg_tag(0, 0, "A", C.gen)
    leg_tag(0, 1, "B", C.gen_b)
    leg_tag(1, 0, "B", C.gen_b)
    leg_tag(1, 1, "A", C.gen)
    tg3 = backed(tex("A+B", size=34, colors={}), buff=0.05).move_to([CX[2] + 1.2, CY + HH - 0.4, 0])
    m.play(FadeIn(tg3), at=run[2][0], dur=0.25)
    m.play(FadeOut(tg3), at=run[2][0] + run[2][1], dur=0.25)

    # labels: products apply right to left
    labs = [tex(r"e^{B}e^{A}", size=40, color=cols[0]), tex(r"e^{A}e^{B}", size=40, color=cols[1]),
            tex(r"e^{A+B}", size=40, color=cols[2])]
    for i, lb in enumerate(labs):
        lb.move_to([CX[i] - 1.15, CY + HH - 0.45, 0])
        lb = backed(lb, buff=0.05)
        labs[i] = lb
    m.play(FadeIn(labs[0]), at=run[0][0] + 2.5, dur=0.4)
    m.play(FadeIn(labs[1]), at=run[1][0] + 2.5, dur=0.4)
    m.play(FadeIn(labs[2]), at=run[2][0] + 2.5, dur=0.4)
    rl = lab("maps apply right to left", 22, C.muted).move_to([CX[0], CY - HH - 0.3, 0])
    m.play(FadeIn(rl), at=run[0][0] + 2.9, dur=0.4)

    # a third shape: the other two outlines laid over it
    ghosts = VGroup(*[poly([origin(2) + U * (M @ q) for q in SQ], cols[j], C.thin + 0.6, opacity=0.9, close=True)
                      for j, M in ((0, EB @ EA), (1, EA @ EB))])
    m.play(Create(ghosts), at=T.third + 0.3, dur=0.8)

    # all three keep the area at one
    chips = VGroup(*[backed(tex(r"\det = 1", size=32, color=C.area), buff=0.05).move_to([CX[i] + 1.2, CY - HH + 0.38, 0])
                     for i in range(3)])
    m.play(FadeOut(rl), LaggedStart(*[FadeIn(c, shift=0.08 * UP) for c in chips], lag_ratio=0.2), at=T.area_one + 0.2,
           dur=0.8)
    m.play(FadeOut(VGroup(r2, Am, Bm, frames, *labs, ghosts, chips)), at=T.cut_gap - 0.4, dur=0.5)
    finish(s)
