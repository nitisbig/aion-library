"""Ch3 · around the square. The wheel from s07 shrinks into the tiny yellow square, which we blow up. A marker walks
once round it counter-clockwise; the push along the way (F along the walk) adds into a running circulation readout.
Bottom: walking right, P helps (+). Top: walking left, P works against you (-), and P is bigger on top, so you lose
more than you gain -> -dP/dy. Right edge up and left edge down: Q gives dQ/dx. Together: curl F = dQ/dx - dP/dy,
circulation per unit area. Checked: whirl 1 - (-1) = 2, river 0 - 1 = -1 (clockwise), source and saddle 0."""
from aion import *

from beats import T
from shots import (BADGES, CAST, arrow, cast_arrows, curl_eq, dim, ease, field_arrows, panel, panel_arrows, paddle,
                   ramp, spin_glyph, stage, tex)

E = "easy_ease"
SQ = np.array([0.9, -0.3])
H = 3.6
S = 0.9
L, R, B, U = SQ[0] - H / 2, SQ[0] + H / 2, SQ[1] - H / 2, SQ[1] + H / 2
OFF = (-H / 3, 0.0, H / 3)
COL = np.array([5.4, 0.0])
G = 0.28                                         # edge arrows sit just outside the edges                       # right-hand column (readout and terms)


def gen(x, y):
    """P grows upward, Q grows to the right: curl = 0.7 - 0.3 = 0.4 everywhere."""
    u, v = x - SQ[0], y - SQ[1]
    return 0.9 + 0.3 * v + 0.0 * u, 0.3 + 0.7 * u + 0.0 * v


def Fv(x, y):
    P, Q = gen(x, y)
    return np.array([float(P), float(Q)])


def walk(sv):
    """Point and unit tangent at arc parameter sv in [0, 4] (one unit per edge), counter-clockwise from (L, B)."""
    e, f = int(min(sv, 3.999)), sv - int(min(sv, 3.999))
    corners = [(L, B), (R, B), (R, U), (L, U), (L, B)]
    a, b = np.array(corners[e]), np.array(corners[e + 1])
    return a + (b - a) * f, (b - a) / H


# circulation so far, tabulated along the walk
_sv = np.linspace(0, 4, 801)
_dl = np.array([Fv(*walk(v)[0]) @ walk(v)[1] for v in _sv]) * H * (4 / 800)
_circ = np.concatenate([[0], np.cumsum(0.5 * (_dl[1:] + _dl[:-1]))])


@scene(T.cut_circ, T.cut_3d)
def s08_circulation(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:2], tile=True)

    k_f = keys((s.start, 0.0), (s.start + 0.8, 0.0), (s.start + 2.0, 0.2, E), (T.together - 0.6, 0.2),
               (T.together + 0.4, 0.0, E), lead=0)
    mf = s.manim(z=1, opacity=k_f)
    mf.add(field_arrows(gen, (-5.0, -4.2, 7.3, 4.2), step=0.62, scale=0.42, width=2.0), at=s.start)

    # ── the wheel from s07 shrinks into the tiny square ──
    hc = np.array([0.9, 0.1])
    shrink = (s.start, s.start + 1.0)

    def wheel(t):
        u = ease(t, *shrink)
        c = hc + (SQ - hc) * u
        r = 1.2 * (1 - u) + 0.25 * u
        ang = np.pi / 4 + 0.5 * (t - T.tiny_wheel) + 1.1 * max(0.0, t - T.how_fast) * 0.6
        g = VGroup(paddle(c, ang, radius=r, color=C.dust, width=3.5), dim(spin_glyph(c, r + 0.35, +1, C.curl), 1 - u))
        return dim(g, 1 - ramp(t, shrink[1] - 0.3, shrink[1]))
    m.redraw(wheel, during=(shrink[0], shrink[1] + 0.05))
    sq = Square(side_length=0.6, color=C.boundary, stroke_width=C.stroke).move_to([*SQ, 0])
    m.play(FadeIn(sq, scale=0.5), at=shrink[1] - 0.45, dur=0.5)
    m.play(sq.animate.scale(H / 0.6), at=shrink[1] + 0.2, dur=1.4, ease=E)

    # ── the walk: a marker goes once round; the push along the way adds up ──
    w0, w1 = T.walk + 0.8, T.circulation - 0.4
    sv = lambda t: 4.0 * ramp(t, w0, w1)

    def walker(t):
        k = ramp(t, w0 - 0.4, w0) * (1 - ramp(t, T.bottom - 0.6, T.bottom - 0.1))
        p, d = walk(sv(t))
        push = Fv(*p) @ d
        g = VGroup(Dot([*p, 0], radius=0.09, color=C.boundary))
        if abs(push) > 0.02:
            g.add(arrow(p, p + d * push * S, C.curl if push > 0 else C.cw, width=C.stroke + 1, tip=0.18))
        return dim(g, k)
    m.redraw(walker, during=(w0 - 0.4, T.bottom - 0.05))
    lab = tex(r"\text{circulation}", size=38, color=C.muted).move_to([COL[0], 2.2, 0])

    def readout(t):
        k = ramp(t, w0 - 0.4, w0) * (1 - ramp(t, T.together - 0.5, T.together))
        v = float(np.interp(sv(t), _sv, _circ))
        num = DecimalNumber(v, num_decimal_places=2, font_size=60, color=C.curl if v >= 0 else C.cw)
        num.move_to([COL[0], 1.55, 0])
        if T.circulation - 0.1 < t < T.circulation + 0.9:
            num.scale(1 + 0.15 * np.sin(np.pi * (t - T.circulation + 0.1)))
        return VGroup(lab.copy(), num).set_opacity(k)
    m.redraw(readout, during=(w0 - 0.4, T.together + 0.05))

    edge = lambda a, b: Line([*a, 0], [*b, 0], color=C.boundary, stroke_width=C.stroke + 3)
    chevron = lambda a, b: arrow(a, b, C.muted, width=C.thin + 0.5, tip=0.14)

    # ── bottom: walking right, P helps ──
    e_b = edge((L, B), (R, B))
    pb = VGroup(*[arrow((SQ[0] + o - Fv(SQ[0] + o, B)[0] * S / 2, B - G), (SQ[0] + o + Fv(SQ[0] + o, B)[0] * S / 2, B - G),
                        C.xpart, width=C.stroke + 0.5, tip=0.14) for o in OFF])
    ch_b = chevron((SQ[0] - 0.6, B - 0.75), (SQ[0] + 0.6, B - 0.75))
    m.play(Create(e_b), FadeIn(ch_b), at=T.bottom, dur=0.7)
    m.play(LaggedStart(*[GrowArrow(a) for a in pb], lag_ratio=0.15), at=T.bottom + 1.2, dur=1.0)
    plus_b = tex("+", size=52, color=C.xpart).move_to([SQ[0] + 1.0, B - 0.78, 0])
    m.play(FadeIn(plus_b, scale=0.5), at=T.P_helps, dur=0.5, ease="out_back")

    # ── top: walking left, P works against you ──
    e_t = edge((R, U), (L, U))
    pt = VGroup(*[arrow((SQ[0] + o - Fv(SQ[0] + o, U)[0] * S / 2, U + G), (SQ[0] + o + Fv(SQ[0] + o, U)[0] * S / 2, U + G),
                        C.xpart, width=C.stroke + 0.5, tip=0.16) for o in OFF])
    ch_t = chevron((SQ[0] + 0.6, U + 1.05), (SQ[0] - 0.6, U + 1.05))
    m.play(Create(e_t), FadeIn(ch_t), at=T.top, dur=0.7)
    m.play(LaggedStart(*[GrowArrow(a) for a in pt], lag_ratio=0.15), at=T.top + 1.0, dur=1.0)
    minus_t = tex("-", size=52, color=C.xpart).move_to([SQ[0] - 1.0, U + 1.05, 0])
    m.play(FadeIn(minus_t, scale=0.5), at=T.against, dur=0.5, ease="out_back")
    # "if P is bigger on top": slide copies of the bottom arrows up; the excess is what you lose
    ghosts = VGroup(*[a.copy().set_color(C.muted) for a in pb])
    m.add(ghosts, at=T.lose - 0.2)
    m.play(ghosts.animate.shift((U - B + 2 * G + 0.3) * UP), at=T.lose, dur=1.2, ease=E)
    excess = VGroup()
    for o in OFF:
        x = SQ[0] + o
        hb, ht = Fv(x, B)[0] * S / 2, Fv(x, U)[0] * S / 2
        excess.add(Line([x + hb, U + G + 0.3, 0], [x + ht, U + G + 0.3, 0], color=C.cw, stroke_width=C.stroke + 5))
    m.play(LaggedStart(*[Create(e) for e in excess], lag_ratio=0.15), at=T.lose + 1.4, dur=0.8)
    termP = tex("-", r"\frac{\partial P}{\partial y}", size=56, colors={1: C.xpart}).move_to([*COL, 0])
    m.play(FadeIn(termP, shift=0.15 * LEFT), at=T.minus_dPdy, dur=0.8)
    m.play(FadeOut(VGroup(ghosts, excess, plus_b, minus_t, ch_b, ch_t)), pb.animate.set_opacity(0.3),
           pt.animate.set_opacity(0.3), FadeOut(VGroup(e_b, e_t)), at=T.right_edge - 0.5, dur=0.6)

    # ── right edge up, left edge down: Q ──
    e_r, e_l = edge((R, B), (R, U)), edge((L, U), (L, B))
    qr = VGroup(*[arrow((R + G, SQ[1] + o - Fv(R, SQ[1] + o)[1] * S / 2), (R + G, SQ[1] + o + Fv(R, SQ[1] + o)[1] * S / 2),
                        C.ypart, width=C.stroke + 0.5, tip=0.16) for o in OFF])
    ql = VGroup(*[arrow((L - G, SQ[1] + o - Fv(L, SQ[1] + o)[1] * S / 2), (L - G, SQ[1] + o + Fv(L, SQ[1] + o)[1] * S / 2),
                        C.ypart, width=C.stroke + 0.5, tip=0.16) for o in OFF])
    ch_r = chevron((R + 0.75, SQ[1] - 0.6), (R + 0.75, SQ[1] + 0.6))
    ch_l = chevron((L - 0.75, SQ[1] + 0.6), (L - 0.75, SQ[1] - 0.6))
    m.play(Create(e_r), FadeIn(ch_r), at=T.right_edge, dur=0.7)
    m.play(LaggedStart(*[GrowArrow(a) for a in qr], lag_ratio=0.15), at=T.right_edge + 0.6, dur=1.0)
    m.play(Create(e_l), FadeIn(ch_l), at=T.left_down, dur=0.7)
    m.play(LaggedStart(*[GrowArrow(a) for a in ql], lag_ratio=0.15), at=T.left_down + 0.6, dur=1.0)
    termQ = tex(r"\frac{\partial Q}{\partial x}", size=56, color=C.ypart).move_to([COL[0], -1.6, 0])
    m.play(FadeIn(termQ, shift=0.15 * LEFT), at=T.dQdx, dur=0.8)

    # ── together: curl F = dQ/dx - dP/dy; circulation per unit area ──
    m.play(FadeOut(VGroup(sq, pb, pt, qr, ql, e_r, e_l, ch_r, ch_l)), at=T.together - 0.3, dur=0.7)
    eq = curl_eq(size=80).move_to([0.9, 0.5, 0])
    m.play(ReplacementTransform(termQ, eq[3]), ReplacementTransform(termP[0], eq[4]),
           ReplacementTransform(termP[1], eq[5]), at=T.together + 0.5, dur=1.3, ease=E)
    m.play(FadeIn(eq[0:3], shift=0.2 * RIGHT), at=T.curl_is, dur=0.9)
    pa = tex("=", r"\frac{\text{circulation}}{\text{area}}", size=60).next_to(eq[2], DOWN, buff=1.0, aligned_edge=LEFT)
    m.play(FadeIn(pa, shift=0.15 * UP), at=T.per_area, dur=0.8)

    # ── check it ──
    m.play(FadeOut(pa), eq.animate.scale(0.68).move_to([1.4, 2.95, 0]), at=T.check2 - 0.3, dur=0.9, ease=E)
    ys = (1.45, 0.25, -0.95, -2.15)
    ic = dict(step=1.1, scale=0.7, width=1.6)
    icons = [cast_arrows("whirl", (-3.6, ys[0]), 1.0, **ic),
             panel_arrows(lambda x, y: (y + 2.4, 0.0 * x), (-3.6, ys[1]), 1.0, step=1.1, scale=0.4, width=1.6),
             cast_arrows("source", (-3.6, ys[2]), 1.0, **ic), cast_arrows("saddle", (-3.6, ys[3]), 1.0, **ic)]
    rows = [tex("1", "-", "(-1)", "=", "2", size=54, colors={0: C.ypart, 2: C.xpart, 4: C.curl}),
            tex("0", "-", "1", "=", "-1", size=54, colors={0: C.ypart, 2: C.xpart, 4: C.cw}),
            tex("0", "-", "0", "=", "0", size=54, colors={0: C.ypart, 2: C.xpart}),
            tex("0", "-", "0", "=", "0", size=54, colors={0: C.ypart, 2: C.xpart})]
    tiles = VGroup()
    for y, ic, r in zip(ys, icons, rows):
        tiles.add(VGroup(panel(-3.6, y, 1.0, 1.0), ic))
        r.move_to([0, y, 0]).align_to([-2.7, 0, 0], LEFT)
    beats_ = [(T.c_whirl, T.c_two), (T.c_river, T.c_neg), (T.c_zero, T.c_zero + 0.6), (T.c_zero + 0.3, T.c_zero + 0.9)]
    for tl, r, (a, b) in zip(tiles, rows, beats_):
        m.play(FadeIn(tl, shift=0.15 * RIGHT), FadeIn(r[0:3], lag_ratio=0.3), at=a, dur=0.9)
        m.play(FadeIn(r[3:], shift=0.1 * LEFT), at=b, dur=0.5)
    cw = spin_glyph(np.array([rows[1].get_right()[0] + 0.55, ys[1]]), 0.3, -1, C.cw)
    m.play(Create(cw), at=T.c_cw, dur=0.7)
    m.play(FadeOut(VGroup(eq, tiles, *rows, cw)), at=T.cut_3d - 0.9, dur=0.7)
