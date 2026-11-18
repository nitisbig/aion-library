"""s17 trace (ch4): one pattern ties them together. Drop a small patch into the flow and watch its area (shoelace,
live). In the spiral it shrinks, as e^{−t/2}; in the shear (after a held pause for the guess) it leans over but its
area never changes. det e^{A} = e^{tr A}: the trace (sum of the diagonal) is the field's divergence, how much it
spreads out at each point. Rotations and shears have zero trace, so they never change area."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, backdrop, backed, field_arrows, finish, lab, live, p3, panel, tex
from verify import CAST, N

SP = CAST["spiral"]
U = 0.85
L_C, R_C = np.array([-3.6, 0.35]), np.array([3.6, 0.35])
L_BOX = (-6.95, -2.25, -0.25, 2.95)
R_BOX = (0.25, -2.25, 6.95, 2.95)


def blob(c, r=0.75, n=72, seed=2):
    """A wobbly closed patch around c (in plane coordinates)."""
    g = rng(seed)
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    k = g.normal(0, 1, 3)
    rr = r * (1 + 0.12 * k[0] * np.cos(2 * a + k[1]) + 0.08 * np.sin(3 * a + k[2]))
    return np.stack([c[0] + rr * np.cos(a), c[1] + rr * np.sin(a)], -1)


def area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


B_SP, B_SH = blob((1.9, 0.6), seed=2), blob((-1.0, 0.9), seed=4)
A_SP, A_SH = area(B_SP), area(B_SH)


@scene(T.cut_trace, T.cut_ch5)
def s17_trace(s):
    backdrop(s)
    mg = s.manim(z=0)
    m = s.manim(z=3)

    # ── two panels: spiral and shear ──
    panels = VGroup()
    for box, ctr, A, name in ((L_BOX, L_C, SP, "spiral"), (R_BOX, R_C, N, "shear")):
        fr = panel(*box, fill=False)
        gl = grid_lines(np.eye(2), tuple(ctr), U, box, n=10, opacity=0.6)
        fa = field_arrows(A, center=ctr, unit=U, box=(box[0] + 0.2, box[1] + 0.2, box[2] - 0.2, box[3] - 0.2),
                          spacing=0.7, opacity=0.45)
        tg = lab(name, 28, C.gen).move_to([(box[0] + box[2]) / 2, box[3] + 0.32, 0])
        panels.add(VGroup(gl, fa, fr, tg))
    mg.play(FadeIn(panels, lag_ratio=0.1), at=T.last_pattern, dur=1.0)

    # flow times: the spiral runs on "shrinks"; the shear holds through the pause, then leans
    ts = keys((T.spiral_area - 0.4, 0.0), (T.spiral_area + 3.4, 2.8, E), lead=0)
    th = keys((T.leans - 0.7, 0.0), (T.leans + 2.4, 2.0, E), lead=0)
    p_op = keys((T.patch - 0.2, 0.0), (T.patch + 0.4, 1.0), (T.cut_ch5 - 0.4, 1.0), (T.cut_ch5 - 0.05, 0.0), lead=0)

    def patch(B, A, ctr, tau, a0):
        def fn(t):
            M = expm(float(tau(t)) * A)
            P = B @ M.T
            op = float(p_op(t))
            poly_ = Polygon(*[p3(ctr + U * q) for q in P], stroke_color=C.area, stroke_width=C.stroke,
                            fill_color=C.area, fill_opacity=0.4 * op).set_stroke(opacity=op)
            rd = VGroup(lab("area", 24, C.area), DecimalNumber(area(P) / a0, num_decimal_places=2, font_size=36,
                                                              color=C.area)).arrange(RIGHT, buff=0.15)
            rd.set_opacity(op).move_to(p3(ctr + [0, -2.0]))
            return VGroup(poly_, rd)
        return fn
    live(m, patch(B_SP, SP, L_C, ts, A_SP), (T.patch - 0.2, T.patch + 0.45), (T.spiral_area - 0.4, T.spiral_area + 3.45),
         (T.cut_ch5 - 0.4, T.cut_ch5 - 0.02))
    live(m, patch(B_SH, N, R_C, th, A_SH), (T.patch - 0.2, T.patch + 0.45), (T.leans - 0.7, T.leans + 2.45),
         (T.cut_ch5 - 0.4, T.cut_ch5 - 0.02))

    e_sp = backed(tex(r"e^{-t/2}", size=40, color=C.area), buff=0.05).move_to(p3(L_C + [2.2, -2.0]))
    m.play(FadeIn(e_sp), at=T.spiral_area + 1.6, dur=0.5)
    q = backed(tex("?", size=72, color=C.area), buff=0.06).move_to(p3(R_C + [1.8, 1.6]))
    m.play(FadeIn(q, scale=0.8), at=T.shear_q + 0.5, dur=0.4)
    m.play(FadeOut(q), at=T.nothing_q - 0.2, dur=0.3)
    same = backed(lab("never changes", 26, C.area), buff=0.05).move_to(p3(R_C + [2.0, -2.0]))
    m.play(FadeIn(same), at=T.leans + 1.4, dur=0.5)

    # ── det e^A = e^{tr A}; trace = divergence; zero-trace flows keep area ──
    law = tex(r"\det e^{A}", "=", r"e^{\operatorname{tr}A}", size=58, colors={0: C.area, 2: C.flow}).move_to([0, -3.2, 0])
    m.play(Write(law), at=T.det_tr + 0.2, dur=1.0)
    trd = tex(r"\operatorname{tr}A", "=", r"a_{11} + a_{22}", size=40, colors={0: C.gen}).move_to([0, 3.6, 0])
    m.play(FadeIn(trd, shift=0.1 * DOWN), at=T.sum_diag + 0.2, dur=0.6)
    dv = tex(r"\operatorname{tr}A", "=", r"\nabla\cdot(A\mathbf v)", size=40, colors={0: C.gen}).move_to(trd)
    dv_l = lab("divergence: how much the field spreads", 24, C.muted)
    m.play(FadeOut(trd, shift=0.1 * UP), FadeIn(dv, shift=0.1 * UP), at=T.divergence - 0.2, dur=0.6)
    chips = [backed(tex(r"\operatorname{tr} = -\tfrac12", size=34, color=C.warm), buff=0.06).move_to(p3(L_C + [-2.2, -2.0])),
             backed(tex(r"\operatorname{tr} = 0", size=34, color=C.flow), buff=0.06).move_to(p3(R_C + [-2.2, -2.0]))]
    m.play(FadeIn(chips[0], shift=0.1 * UP), at=T.zero_trace - 0.2, dur=0.5)
    m.play(FadeIn(chips[1], shift=0.1 * UP), Indicate(same, color=C.flow), at=T.zero_trace + 0.8, dur=0.7)
    m.play(FadeOut(VGroup(law, dv, e_sp, same, *chips)), at=T.cut_ch5 - 0.4, dur=0.5)
    mg.play(FadeOut(panels), at=T.cut_ch5 - 0.4, dur=0.5)
    finish(s)
