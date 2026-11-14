"""Ch2 · out minus in. A general field; the drop of dye shrinks into a tiny square, which we blow up to look at.
Water crosses all four edges. Left and right: only the sideways part P (teal) crosses them; the right arrows are
longer than the left ones, and sliding a copy of the left arrow over the right one leaves the difference, which over
the width h becomes dP/dx. Top and bottom do the same with Q (purple) -> dQ/dy. The two terms slide together into
del-dot F = dP/dx + dQ/dy, which is then checked on the rail: 1 + 1 = 2, 0 + 0 = 0, 1 - 1 = 0."""
from aion import *

from beats import T
from shots import BADGES, RAIL, RAIL_S, arrow, div_eq, dye_poly, ease, field_arrows, ramp, stage, tex

E = "easy_ease"
SQ = np.array([1.0, -0.5])                       # the square (world)
H = 3.6                                          # its size once blown up
S = 0.9                                          # arrow scale on the edges
L, R, B, U = SQ[0] - H / 2, SQ[0] + H / 2, SQ[1] - H / 2, SQ[1] + H / 2
OFF = (-H / 3, 0.0, H / 3)                       # three crossing points per edge


def gen(x, y):
    """A smooth general field (world coordinates): P grows to the right, Q grows upward."""
    u, v = x - SQ[0], y - SQ[1]
    return 1.0 + 0.35 * u + 0.08 * v, 0.7 + 0.25 * v + 0.06 * u


def Fv(x, y):
    P, Q = gen(x, y)
    return np.array([float(P), float(Q)])


@scene(T.cut_flux, T.cut_map)
def s05_flux_box(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:1])

    # ── the field, on its own layer so it can step back ──
    k_f = keys((s.start, 0.0), (s.start + 0.3, 0.0), (s.start + 1.5, 1.0, E), (T.square + 1.2, 1.0),
               (T.square + 2.6, 0.22, E), (T.lr, 0.22), (T.lr + 1.0, 0.13, E), (T.add_two - 0.6, 0.13), (T.add_two + 0.4, 0.0, E), lead=0)
    mf = s.manim(z=1, opacity=k_f)
    mf.add(field_arrows(gen, (-5.0, -4.2, 7.3, 4.2), step=0.62, scale=0.42, width=2.0), at=s.start)

    # ── the drop shrinks to a tiny square, which we blow up ──
    th = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    drop = dye_poly(np.stack([SQ[0] + 0.35 * np.cos(th), SQ[1] + 0.35 * np.sin(th)], 1), C.div, opacity=0.16)
    drop.set_stroke(width=C.stroke)
    m.play(FadeIn(drop, scale=0.4), at=T.to_formula, dur=0.6, ease="out_back")
    sq = Square(side_length=0.6, color=C.boundary, stroke_width=C.stroke).move_to([*SQ, 0])
    m.play(ReplacementTransform(drop, sq), at=T.square, dur=0.9, ease=E)
    m.play(sq.animate.scale(H / 0.6), at=T.square + 1.3, dur=1.6, ease=E)

    # ── water crossing every edge: the full arrows, centred on the edges ──
    def full_arrows():
        g = VGroup()
        for o in OFF:
            for p in ((L, SQ[1] + o), (R, SQ[1] + o), (SQ[0] + o, B), (SQ[0] + o, U)):
                v = Fv(*p) * S
                g.add(arrow(np.array(p) - v / 2, np.array(p) + v / 2, C.field, width=C.stroke, tip=0.16))
        return g
    crossing = full_arrows()
    lr_idx = [i for i in range(12) if i % 4 in (0, 1)]
    tb_idx = [i for i in range(12) if i % 4 in (2, 3)]
    m.play(LaggedStart(*[GrowArrow(a) for a in crossing], lag_ratio=0.08), at=T.count, dur=1.6)
    oi = tex(r"\text{out}", "-", r"\text{in}", size=56, colors={0: C.div, 2: C.sink}).move_to([SQ[0], 3.12, 0])
    m.play(FadeIn(oi, shift=0.15 * DOWN), at=T.out_in, dur=0.7)

    # ── left and right: only P crosses ──
    edge = lambda a, b: Line([*a, 0], [*b, 0], color=C.boundary, stroke_width=C.stroke + 3)
    e_lr = VGroup(edge((L, B), (L, U)), edge((R, B), (R, U)))
    m.play(Create(e_lr), *[crossing[i].animate.set_opacity(0.2) for i in tb_idx], at=T.lr, dur=0.8)

    def P_arrows():
        g = VGroup()
        for o in OFF:
            y = SQ[1] + o
            pl, pr = Fv(L, y)[0] * S, Fv(R, y)[0] * S
            g.add(arrow((L - pl, y), (L, y), C.xpart, width=C.stroke + 0.5, tip=0.16))     # entering on the left
            g.add(arrow((R, y), (R + pr, y), C.xpart, width=C.stroke + 0.5, tip=0.16))     # leaving on the right
        return g
    pa = P_arrows()
    m.play(*[ReplacementTransform(crossing[i], pa[j]) for j, i in enumerate(lr_idx)], at=T.only_P, dur=1.2, ease=E)
    p_lab = tex("P", size=46, color=C.xpart).move_to([R + 1.95, SQ[1] + H / 3, 0])
    m.play(FadeIn(p_lab, shift=0.1 * LEFT), at=T.only_P + 0.9, dur=0.5)

    # "a little bigger on the right": slide a copy of each left arrow over its right partner; the rest is the gain
    ghosts, gains = VGroup(), VGroup()
    for o in OFF:
        y = SQ[1] + o
        pl, pr = Fv(L, y)[0] * S, Fv(R, y)[0] * S
        ghosts.add(arrow((L - pl, y), (L, y), C.muted, width=C.stroke, tip=0.16))
        gains.add(Line([R + pl, y + 0.17, 0], [R + pr, y + 0.17, 0], color=C.xpart, stroke_width=C.stroke + 5))
    m.add(ghosts, at=T.bigger + 0.2)
    shifts = [R - L + Fv(L, SQ[1] + o)[0] * S for o in OFF]       # left arrow's tail lands on the right edge
    m.play(LaggedStart(*[g.animate.shift(d * RIGHT + 0.17 * UP) for g, d in zip(ghosts, shifts)], lag_ratio=0.15),
           at=T.bigger + 0.4, dur=1.4, ease=E)
    m.play(LaggedStart(*[Create(g) for g in gains], lag_ratio=0.15), at=T.bigger + 2.2, dur=0.9)
    br = Brace(Line([L, B, 0], [R, B, 0]), DOWN, buff=0.45, color=C.muted)
    h_lab = tex("h", size=44, color=C.muted).next_to(br, DOWN, buff=0.1)
    m.play(FadeIn(br), FadeIn(h_lab), at=T.bigger + 3.6, dur=0.7)

    dP = tex(r"\frac{P_{\mathrm{right}}-P_{\mathrm{left}}}{h}", r"\;\longrightarrow\;", r"\frac{\partial P}{\partial x}",
             size=46, colors={0: C.xpart, 2: C.xpart}).move_to([SQ[0], 3.12, 0])
    m.play(FadeOut(oi), at=T.dPdx - 1.0, dur=0.5)
    m.play(FadeIn(dP[0], shift=0.1 * DOWN), at=T.dPdx - 0.6, dur=0.8)
    m.play(FadeIn(dP[1]), FadeIn(dP[2], shift=0.15 * LEFT), at=T.dPdx + 0.6, dur=0.8)
    termP = dP[2]
    m.play(FadeOut(dP[0:2]), termP.animate.move_to([5.75, 1.0, 0]), at=T.tb - 1.2, dur=1.0, ease=E)

    # ── top and bottom: Q, the same way ──
    e_tb = VGroup(edge((L, B), (R, B)), edge((L, U), (R, U)))
    m.play(FadeOut(e_lr), FadeOut(gains), FadeOut(ghosts), FadeOut(p_lab), pa.animate.set_opacity(0.25),
           Create(e_tb), at=T.tb, dur=0.8)

    def Q_arrows():
        g = VGroup()
        for o in OFF:
            x = SQ[0] + o
            qb, qt = Fv(x, B)[1] * S, Fv(x, U)[1] * S
            g.add(arrow((x, B - qb), (x, B), C.ypart, width=C.stroke + 0.5, tip=0.12))
            g.add(arrow((x, U), (x, U + qt), C.ypart, width=C.stroke + 0.5, tip=0.16))
        return g
    qa = Q_arrows()
    m.play(*[ReplacementTransform(crossing[i], qa[j]) for j, i in enumerate(tb_idx)], at=T.tb + 0.8, dur=1.2, ease=E)
    q_lab = tex("Q", size=46, color=C.ypart).move_to([R + 0.45, U + 0.5, 0])
    m.play(FadeIn(q_lab, shift=0.1 * DOWN), at=T.tb + 1.8, dur=0.5)
    gq = VGroup()
    for o in OFF:
        x = SQ[0] + o
        qb, qt = Fv(x, B)[1] * S, Fv(x, U)[1] * S
        gq.add(VGroup(arrow((x + 0.17, U), (x + 0.17, U + qb), C.muted, width=C.stroke, tip=0.1),
                      Line([x + 0.17, U + qb, 0], [x + 0.17, U + qt, 0], color=C.ypart, stroke_width=C.stroke + 5)))
    m.play(LaggedStart(*[FadeIn(g[0]) for g in gq], lag_ratio=0.15), at=T.tb + 2.8, dur=0.8)
    m.play(LaggedStart(*[Create(g[1]) for g in gq], lag_ratio=0.15), at=T.tb + 3.8, dur=0.9)

    dQ = tex(r"\frac{Q_{\mathrm{top}}-Q_{\mathrm{bottom}}}{h}", r"\;\longrightarrow\;", r"\frac{\partial Q}{\partial y}",
             size=46, colors={0: C.ypart, 2: C.ypart}).move_to([SQ[0], 3.12, 0])
    m.play(FadeIn(dQ[0], shift=0.1 * DOWN), at=T.dQdy - 1.0, dur=0.8)
    m.play(FadeIn(dQ[1]), FadeIn(dQ[2], shift=0.15 * LEFT), at=T.dQdy + 0.2, dur=0.8)
    termQ = dQ[2]
    m.play(FadeOut(dQ[0:2]), termQ.animate.move_to([5.75, -1.2, 0]), at=T.add_two - 1.4, dur=1.0, ease=E)

    # ── add the two: del-dot F ──
    square_bits = VGroup(sq, pa, qa, e_tb, gq, q_lab, br, h_lab)
    m.play(FadeOut(square_bits), at=T.add_two - 0.3, dur=0.8)
    eq = div_eq(size=80).move_to([1.0, 0.2, 0])
    m.play(ReplacementTransform(termP, eq[3]), ReplacementTransform(termQ, eq[5]), at=T.add_two + 0.4, dur=1.3,
           ease=E)
    m.play(FadeIn(eq[4], scale=0.5), at=T.add_two + 1.4, dur=0.5)
    m.play(FadeIn(eq[0:3], shift=0.2 * RIGHT), at=T.del_dot, dur=0.9)

    # ── check it on the cast ──
    m.play(eq.animate.scale(0.75).move_to([2.2, 2.7, 0]), at=T.check, dur=1.0, ease=E)
    hl = Rectangle(width=RAIL_S + 0.12, height=RAIL_S + 0.12, stroke_color=C.boundary, stroke_width=C.stroke)
    hl.move_to([*RAIL[0], 0])
    rows = [tex("1", "+", "1", "=", "2", size=56, colors={0: C.xpart, 2: C.ypart, 4: C.div}),
            tex("0", "+", "0", "=", "0", size=56, colors={0: C.xpart, 2: C.ypart, 4: C.div}),
            tex("1", "-", "1", "=", "0", size=56, colors={0: C.xpart, 2: C.ypart, 4: C.div})]
    for r, c in zip(rows, RAIL):
        r.move_to([0, c[1], 0]).align_to([-4.95, 0, 0], LEFT)
    m.play(Create(hl), at=T.chk_source - 0.3, dur=0.5)
    m.play(FadeIn(rows[0][0:3], lag_ratio=0.3), at=T.chk_source + 0.6, dur=1.0)
    m.play(FadeIn(rows[0][3:], shift=0.1 * LEFT), at=T.chk_two, dur=0.5)
    m.play(hl.animate.move_to([*RAIL[1], 0]), at=T.chk_whirl - 0.2, dur=0.5, ease=E)
    m.play(FadeIn(rows[1], lag_ratio=0.2), at=T.chk_whirl + 0.5, dur=1.2)
    m.play(hl.animate.move_to([*RAIL[2], 0]), at=T.chk_saddle - 0.3, dur=0.5, ease=E)
    m.play(FadeIn(rows[2][0:3], lag_ratio=0.3), at=T.chk_saddle + 0.3, dur=1.0)
    m.play(FadeIn(rows[2][3:], shift=0.1 * LEFT), at=T.chk_zero, dur=0.5)
    tick = tex(r"\checkmark", size=56, color=C.boundary).next_to(rows[2], RIGHT, buff=0.35)
    m.play(FadeIn(tick, scale=0.5), at=T.chk_zero + 0.4, dur=0.5, ease="out_back")
    m.play(FadeOut(VGroup(eq, *rows, tick, hl)), at=T.cut_map - 0.9, dur=0.7)
