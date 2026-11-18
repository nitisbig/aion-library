"""The claim. A move that turns arrows and stretches them is what a matrix does: the hook's step is the matrix
[[1, 1], [-1, 1]] acting on the whole plane. Then the precise statement (the derivative is linear; calculus is linear
algebra plus a limit), four unexplained glimpses (+C collapsing, a quarter turn, a curve that only stretches, a
vibrating string), and the map. The string is left vibrating, then settles flat for chapter 1."""
from aion import *

from beats import T
from shots import (D_EXP, FRAME, HO, HU, I2, Mat, arrow, axis_marks, backdrop, finish, grid_lines, hook_tip, live,
                   log_rings, plane_labels, plot, pt, result_tag, rot2, spiral, tex)

E = "smooth"


def hook_move(u):
    """The hook's one step, grown smoothly: scale 1 -> sqrt2 while turning 0 -> 45 degrees clockwise."""
    return (1 + (np.sqrt(2) - 1) * u) * rot2(-45 * u)


assert np.allclose(hook_move(1.0), D_EXP)


def fade(t0, t1, a=0.0, b=1.0):
    return keys((t0, a), (t1, b), lead=0)


@scene(T.cut_claim, T.cut_ch1)
def s01_claim(s):
    backdrop(s)
    m = s.manim(z=1)
    t0 = T.cut_claim

    # ── the state the hook left, then back to one step ──
    t_back0, t_back1 = T.operation + 0.1, T.operation + 1.3
    t_mv0, t_mv1 = T.matrix_does + 0.4, T.matrix_does + 2.2
    t_clear = T.claim - 0.1
    gop = keys((t_back0, 0.18), (t_back1, 1.0), (t_clear, 1.0), (t_clear + 0.6, 0.0), lead=0)
    mv = keys((t_mv0, 0.0), (t_mv1, 1.0, E), lead=0)
    old = keys((t_back0, 1.0), (t_back1, 0.0), lead=0)          # the spin's leftovers fade out
    new = keys((t_back0 + 0.5, 0.0), (t_back1, 1.0), (t_clear, 1.0), (t_clear + 0.6, 0.0), lead=0)
    m0 = s.manim(z=0)                                             # the grid, then the coloured axes and names

    def plane(t):
        ax = gop(t) if t > t_back1 else 1.0
        lb = new(t) if t > t_back1 else 1.0
        return VGroup(grid_lines(hook_move(mv(t)), HO, HU, FRAME, opacity=0.6 * gop(t)), axis_marks(ax, ax),
                      plane_labels(lb, lb))
    live(m0, plane, (t0, t0 + 0.05), (t_back0, t_back1), (t_mv0, t_mv1), (t_clear, t_clear + 0.6))
    z0 = pt(HO, 1.0, (0, 0))

    def stage(t):
        out = VGroup()
        o = float(old(t))
        if o > 0.01:
            out.add(log_rings(o, 1.0), spiral(100.0, o), arrow(z0, hook_tip(100.0, 1.0), C.fn, width=C.stroke + 1.5,
                                                                 opacity=o))
        nw = float(new(t))
        if nw > 0.01:
            out.add(arrow(z0, pt(HO, HU, hook_move(mv(t)) @ [0.0, 1.0]), C.fn, width=C.stroke + 1.5, opacity=nw))
        return out
    m3 = s.manim(z=0.8)
    live(m3, stage, (t0, t0 + 0.05), (t_back0, t_back1), (t_mv0, t_mv1), (t_clear, t_clear + 0.6))

    # the HUD the hook left: the tag, the counter, the 2^50
    tag = result_tag()
    neq = tex(r"n", r"=", size=40, colors={0: C.fn}).move_to([4.7, 2.75, 0])
    hund = tex("100", size=40).next_to(neq, RIGHT, buff=0.22)
    pw = tex(r"(\sqrt{2})^{100}", r"=", r"2^{50}", size=40, colors={2: C.fn}).move_to([4.6, -2.9, 0])
    m.add(tag, neq, hund, pw, at=t0)
    m.play(FadeOut(VGroup(neq, hund, pw)), at=t_back0, dur=0.8)

    # that's what a matrix does
    Dm = Mat(D_EXP.astype(int), size=56, h_buff=0.9, v_buff=0.72)
    lab = tex(r"D", r"=", size=56, colors={0: C.op})
    g = VGroup(lab, Dm).arrange(RIGHT, buff=0.25)
    g.move_to([7.11 - C.margin - 0.3 - g.width / 2, 2.55, 0])
    from shots import backing
    gb = backing(g, pad=0.22)
    m.play(FadeIn(gb), FadeIn(g, shift=0.1 * DOWN), at=T.matrix_does - 0.1, dur=0.6)
    m.play(FadeOut(VGroup(gb, g, tag)), at=t_clear, dur=0.6)

    # ── the claim ──
    lin = tex(r"D", r"(", r"a", r"f", r"+", r"b", r"g", r")", r"=", r"a", r"\,D", r"f", r"+", r"b", r"\,D", r"g",
              size=60, colors={0: C.op, 3: C.fn, 6: C.fn, 10: C.op, 11: C.fn, 14: C.op, 15: C.fn}).move_to([0, 1.0, 0])
    bigD = tex(r"D", size=110, color=C.op).move_to([0, 0.6, 0])
    m.play(FadeIn(bigD, scale=0.8), at=T.claim + 0.4, dur=0.9)
    rest = lin[1:]
    m.play(ReplacementTransform(bigD, lin[0]), Write(rest), at=T.linear_map + 0.3, dur=1.6)
    m.remove(lin[0], rest, at=T.linear_map + 2.0)            # re-file as one formula
    m.add(lin, at=T.linear_map + 2.0)
    calc = tex(r"\text{calculus}", r"=", r"\text{linear algebra}", r"\;+", size=56).move_to([-0.55, -0.55, 0])
    lim = tex(r"\lim", size=56, color=C.muted).next_to(calc, RIGHT, buff=0.25)
    m.play(FadeIn(calc, shift=0.1 * UP), at=T.surprising + 0.2, dur=0.8)
    m.play(FadeIn(lim, shift=0.35 * DOWN), at=T.limit, dur=0.5, ease="out_back")
    m.play(FadeOut(VGroup(lin, calc, lim)), at=T.pv_plus_c - 0.35, dur=0.5)

    # ── preview 1: +C, a whole family collapsing onto one derivative ──
    PO, PUX, PUY = (0.0, -1.0), 1.0, 0.42
    cs = [-1.5, -0.5, 0.5, 1.5, 2.5]
    parab = VGroup(*[plot(lambda x, c=c: x ** 2 + c, -2.2, 2.2, PO, PUX, PUY, C.fn, opacity=0.85) for c in cs])
    line2x = [plot(lambda x: 2 * x, -2.2, 2.2, PO, PUX, PUY, C.dfn) for _ in cs]
    lp = tex(r"x^2", r"+", r"C", size=48, colors={0: C.fn, 2: C.null}).move_to([3.6, 1.9, 0])
    l2 = tex(r"2x", size=48, color=C.dfn).move_to(lp)
    t_p = T.pv_plus_c
    m.play(LaggedStart(*[Create(p) for p in parab], lag_ratio=0.12), FadeIn(lp), at=t_p - 0.1, dur=1.0)
    m.play(*[Transform(p, q) for p, q in zip(parab, line2x)], ReplacementTransform(lp, l2), at=t_p + 1.5, dur=1.3)
    m.play(FadeOut(VGroup(parab, l2)), at=T.pv_rotation - 0.35, dur=0.4)

    # ── preview 2: cos and sin, a quarter turn at a time ──
    RO, RU = (0.0, -0.3), 1.7
    t_r = T.pv_rotation
    turns = [(t_r + 0.4 + 0.95 * k, t_r + 0.4 + 0.95 * k + 0.6) for k in range(4)]
    ang = keys(*[kf for k, (a, b) in enumerate(turns) for kf in ((a, -90.0 * k), (b, -90.0 * (k + 1), E))], lead=0)
    rop = keys((t_r - 0.2, 0.0), (t_r + 0.2, 1.0), (T.pv_eigen - 0.4, 1.0), (T.pv_eigen - 0.05, 0.0), lead=0)
    zr = pt(RO, 1.0, (0, 0))

    def rot_stage(t):
        R = rot2(float(ang(t)))
        o = float(rop(t))
        out = VGroup(Circle(radius=RU, stroke_color=C.ghost, stroke_width=C.thin, stroke_opacity=o).move_to(zr))
        for j, col, nm in ((0, C.b1, r"\cos"), (1, C.b2, r"\sin")):
            tip = pt(RO, RU, R[:, j])
            out.add(arrow(zr, tip, col, width=C.stroke + 1, opacity=o))
            d = R[:, j]
            out.add(tex(nm, size=36, color=col).set_opacity(o).move_to(tip + 0.42 * np.array([*d, 0])))
        return out
    live(m, rot_stage, (t_r - 0.2, t_r + 0.2), (turns[0][0], turns[-1][1]), (T.pv_eigen - 0.4, T.pv_eigen - 0.05))
    m.add(VGroup(), at=T.pv_eigen)                               # (the last held frame is invisible: opacity 0)

    # ── preview 3: the curve that only stretches ──
    EO, EUX, EUY = (0.0, -2.2), 1.1, 0.55
    t_e = T.pv_eigen
    st = keys((t_e + 0.6, 1.0), (t_e + 1.7, 2.0, E), lead=0)
    eop = keys((t_e - 0.2, 0.0), (t_e + 0.2, 1.0), (T.pv_string - 0.4, 1.0), (T.pv_string - 0.05, 0.0), lead=0)

    def eig_stage(t):
        o = float(eop(t))
        k = float(st(t))
        out = VGroup(Line(pt(EO, 1, (-3.6, 0)), pt(EO, 1, (3.6, 0)), color=C.axis, stroke_width=C.thin,
                          stroke_opacity=0.6 * o))
        out.add(plot(lambda x: np.exp(0.8 * x), -3.2, 1.65, EO, EUX, EUY, C.eigen, opacity=0.3 * o))
        out.add(plot(lambda x: k * np.exp(0.8 * x), -3.2, 1.65, EO, EUX, EUY, C.eigen, opacity=o))
        out.add(tex(r"\times\lambda", size=40, color=C.eigen).set_opacity(o * min(1.0, (k - 1) * 3))
                .move_to(pt(EO, 1, (3.0, 3.2))))
        return out
    live(m, eig_stage, (t_e - 0.2, t_e + 0.2), (t_e + 0.6, t_e + 1.7), (T.pv_string - 0.4, T.pv_string - 0.05))

    # ── preview 4: a string, vibrating in its second mode; then it settles for chapter 1 ──
    SO, SL = (0.0, -0.3), 4.2                                    # centre, half length
    t_s = T.pv_string
    amp = keys((t_s - 0.2, 0.0), (t_s + 0.5, 0.9), (T.listening, 0.9), (T.cut_ch1 - 0.8, 0.0, "easy_ease"), lead=0)
    sop = keys((t_s - 0.3, 0.0), (t_s + 0.1, 1.0), lead=0)
    w = 2 * np.pi * 1.1                                          # a slow, readable vibration (not the real frequency)
    pins = VGroup(*[Dot(pt(SO, 1, (sx * SL, 0)), radius=0.07, color=C.string) for sx in (-1, 1)])
    m.play(FadeIn(pins), at=t_s - 0.3, dur=0.4)

    def string(t):
        a = float(amp(t)) * np.cos(w * (t - t_s))
        xs = np.linspace(-1, 1, 160)
        p = np.stack([SO[0] + SL * xs, SO[1] + a * np.sin(2 * np.pi * (xs + 1) / 2), 0 * xs], -1)
        return VMobject(stroke_color=C.string, stroke_width=C.stroke, stroke_opacity=float(sop(t))).set_points_as_corners(p)
    m.redraw(string, during=(t_s - 0.3, T.cut_ch1 - 0.75))
    finish(s)
