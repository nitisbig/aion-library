"""s08 field (ch2): add a dimension. A point in the plane is a vector v; let the matrix hand out velocities: at v the
velocity is A v (orange, growing from v's tip), so v̇ = A v. The matrix to play with, A = [[0, −1], [1, 0]], turns
every vector a quarter turn counterclockwise (î → ĵ, ĵ → −î). As a velocity field that means every point moves at
right angles to its radius: the arrows fill the plane from the centre out and six points start to circle."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, FRAME, J, arrow, backdrop, backed, chapter_card, field_arrows, finish, lab, live, p3, rot2, tex

V = np.array([2.0, 1.0])
RADII = [0.9, 1.5, 2.1, 2.7, 3.3, 3.9]
PHASE = [0.3, 2.4, 4.4, 1.2, 3.5, 5.6]


@scene(T.cut_ch2, T.cut_grid)
def s08_field(s):
    backdrop(s)
    mg = s.manim(z=0)                                  # grid + axes
    mf = s.manim(z=1)                                  # the field
    m = s.manim(z=3)
    chapter_card(m, 2, "A matrix as a velocity", r"A\mathbf v", T.cut_ch2, color=C.gen)

    # ── the number line becomes the x-axis; a second axis grows out of zero; the grid fills in ──
    t0 = T.cut_ch2 + 2.85
    xa = Line(p3((-7.3, 0)), p3((7.3, 0)), color=C.axis, stroke_width=C.thin + 0.8)
    ya = Line(p3((0, 0)), p3((0, 4.2)), color=C.axis, stroke_width=C.thin + 0.8)
    yb = Line(p3((0, 0)), p3((0, -4.2)), color=C.axis, stroke_width=C.thin + 0.8)
    mg.play(Create(xa), at=t0, dur=0.9, ease=E)
    mg.play(Create(ya), Create(yb), at=t0 + 0.7, dur=0.8, ease=E)
    grid = grid_lines(np.eye(2), (0.0, 0.0), 1.0, FRAME, n=16, axes=False)
    mg.play(FadeIn(grid, lag_ratio=0.02), at=t0 + 1.4, dur=1.2)

    # ── a vector v, and the velocity A v the matrix hands out at v ──
    AV = J @ V
    v_ar = arrow((0, 0), V, C.vec, width=C.stroke + 1)
    v_lb = backed(tex(r"\mathbf v", size=44, color=C.vec), buff=0.06).next_to(p3(V), DR, buff=0.05)
    m.play(GrowArrow(v_ar), FadeIn(v_lb), at=T.hand_out - 1.7, dur=0.8, ease=E)
    av_ar = arrow(V, V + AV, C.gen, width=C.stroke + 1)
    av_lb = backed(tex(r"A\mathbf v", size=44, colors={}), buff=0.06)
    av_lb[1][0][0].set_color(C.gen)
    av_lb.next_to(p3(V + AV), UP, buff=0.08)
    m.play(GrowArrow(av_ar), at=T.hand_out + 0.6, dur=0.8, ease=E)
    m.play(FadeIn(av_lb, shift=0.1 * UP), at=T.Av + 0.4, dur=0.5)
    law = backed(tex(r"\dot{\mathbf v}", "=", "A", r"\mathbf v", size=60, colors={0: C.gen, 2: C.gen, 3: C.vec}))
    law.move_to([4.6, 3.1, 0])
    m.play(Write(law), at=T.Av + 1.0, dur=1.0)

    # ── a matrix to play with: the quarter turn ──
    A_m = backed(VGroup(tex("A", "=", size=44, colors={0: C.gen}),
                        Mat([["0", "-1"], ["1", "0"]], colors=C.gen, size=40, h_buff=0.85, v_buff=0.7)).arrange(
        RIGHT, buff=0.2)).move_to([4.6, 1.55, 0])
    m.play(FadeIn(A_m, shift=0.1 * DOWN), at=T.play_mat + 0.2, dur=0.6)
    m.play(FadeOut(VGroup(v_ar, v_lb, av_ar, av_lb)), at=T.quarter - 1.3, dur=0.5)
    U = 1.8                                             # basis arrows drawn longer, so the turn reads
    i_ar = arrow((0, 0), (U, 0), C.ihat, width=C.stroke + 1.5)
    j_ar = arrow((0, 0), (0, U), C.jhat, width=C.stroke + 1.5)
    m.play(GrowArrow(i_ar), GrowArrow(j_ar), at=T.quarter - 0.6, dur=0.6)
    turn = [Arc(radius=U + 0.25, start_angle=0.08, angle=PI / 2 - 0.16, color=C.ihat, stroke_width=C.stroke),
            Arc(radius=U + 0.25, start_angle=PI / 2 + 0.08, angle=PI / 2 - 0.16, color=C.jhat, stroke_width=C.stroke)]
    for a in turn:
        a.add_tip(tip_length=0.18, tip_width=0.18)
    i_to = arrow((0, 0), (0, U), C.ihat, width=C.stroke + 1.5, opacity=0.55).shift(0.0 * LEFT)
    j_to = arrow((0, 0), (-U, 0), C.jhat, width=C.stroke + 1.5, opacity=0.55)
    m.play(Create(turn[0]), TransformFromCopy(i_ar, i_to), at=T.quarter + 0.3, dur=0.9, ease=E)
    m.play(Create(turn[1]), TransformFromCopy(j_ar, j_to), at=T.quarter + 1.2, dur=0.9, ease=E)
    m.play(FadeOut(VGroup(i_ar, j_ar, i_to, j_to, *turn)), at=T.right_angles - 0.6, dur=0.5)

    # ── as a velocity: arrows fill the plane from the centre out ──
    field = field_arrows(J, box=FRAME, spacing=0.75)
    order = sorted(field, key=lambda a: np.linalg.norm(a.get_start()[:2]))
    mf.play(LaggedStart(*[GrowArrow(a) for a in order], lag_ratio=0.006), at=T.right_angles - 0.3, dur=1.6)

    # ── six points start to circle, each at right angles to its radius ──
    w = keys((T.right_angles + 1.2, 0.0), (T.right_angles + 2.2, 0.55, E), lead=0)
    ang = Clock(rate=w, start=T.right_angles + 1.2)
    d_op = keys((T.right_angles + 0.9, 0.0), (T.right_angles + 1.4, 1.0), (T.cut_grid - 0.6, 1.0),
                (T.cut_grid - 0.1, 0.0), lead=0)

    def dots(t):
        a, op = float(ang(t)), float(d_op(t))
        out = VGroup()
        for r, ph in zip(RADII, PHASE):
            q0 = r * np.array([np.cos(ph), np.sin(ph)])
            if a > 0.01:                                 # a short teal trail behind each point
                out.add(Arc(radius=r, start_angle=ph + max(a - 0.5, 0.0), angle=min(a, 0.5), color=C.flow,
                            stroke_width=C.stroke, stroke_opacity=0.8 * op))
            out.add(Dot(p3(rot2(a) @ q0), radius=0.09, color=C.vec).set_opacity(op))
        return out
    live(m, dots, (T.right_angles + 0.9, T.cut_grid - 0.05))

    # one of them, with its radius and a right-angle mark
    r_op = keys((T.right_angles + 1.6, 0.0), (T.right_angles + 2.1, 1.0), (T.cut_grid - 1.0, 1.0),
                (T.cut_grid - 0.5, 0.0), lead=0)
    k = 3

    def radius(t):
        op = float(r_op(t))
        q = rot2(float(ang(t))) @ (RADII[k] * np.array([np.cos(PHASE[k]), np.sin(PHASE[k])]))
        u = q / np.linalg.norm(q)
        n = J @ u
        c = 0.22
        sq = VMobject(stroke_color=C.text, stroke_width=C.thin + 0.4, stroke_opacity=op).set_points_as_corners(
            [p3(q - c * u), p3(q - c * u + c * n), p3(q + c * n)])
        return VGroup(DashedLine(p3((0, 0)), p3(q), color=C.text, stroke_width=C.thin + 0.6,
                                 dash_length=0.1).set_stroke(opacity=op),
                      sq, arrow(q, q + 1.1 * n, C.gen, width=C.stroke + 1.5, opacity=op))
    live(m, radius, (T.right_angles + 1.6, T.cut_grid - 0.45))
    m.play(FadeOut(VGroup(law, A_m)), at=T.cut_grid - 0.4, dur=0.5)
    finish(s)
