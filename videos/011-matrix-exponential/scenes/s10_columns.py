"""s10 columns (ch2): read e^{tA}'s numbers off the picture. Wherever î lands is the first column, wherever ĵ lands
the second; both turn through the angle t, so e^{tA} = [[cos t, −sin t], [sin t, cos t]]. The question (where is
the grid at t = π?), a held pause, then the flow resumes: î points left, ĵ points down, e^{πJ} = −I, the answer from
the start; e^{iπ} = −1 is nothing more mysterious than a half turn."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, FRAME, J, arrow, backdrop, backed, dim, finish, lab, live, p3, tex

PX0, PX1 = 2.15, 7.05                                 # the matrix panel on the right
MX = (PX0 + PX1) / 2


@scene(T.cut_cols, T.cut_ch3)
def s10_columns(s):
    backdrop(s)
    mg = s.manim(z=0)                                  # static grid
    mm = s.manim(z=2)                                  # moving grid, î, ĵ, arcs
    m = s.manim(z=5)                                   # panel + matrices

    # ── move the plane left and zoom in, to make room for the numbers ──
    mv = keys((T.numbers - 0.3, 0.0), (T.numbers + 0.9, 1.0, E), lead=0)

    def cu(t):
        a = float(mv(t))
        return np.array([-3.0 * a, 0.0]), 1.0 + 0.7 * a

    out = keys((T.cut_ch3 - 0.4, 1.0), (T.cut_ch3 - 0.05, 0.0), lead=0)

    def static(t):
        c, u = cu(t)
        return dim(grid_lines(np.eye(2), tuple(c), u, FRAME, n=16), float(out(t)))
    live(mg, static, (T.cut_cols, T.numbers + 0.95), (T.cut_ch3 - 0.45, T.cut_ch3))

    # ── flow time: to t = 1, freeze for the question, then on to π ──
    r1 = (T.ihat + 0.6, T.angle_t + 1.8)
    r2 = (T.halfway - 0.6, T.halfway + 2.4)
    tau = keys((r1[0], 0.0), (r1[1], 1.0, E), (r2[0], 1.0), (r2[1], PI, E), lead=0)
    g_op = keys((T.cut_cols, 0.0), (T.cut_cols + 0.5, 1.0), (T.cut_ch3 - 0.4, 1.0), (T.cut_ch3 - 0.05, 0.0), lead=0)

    def moving(t):
        c, u = cu(t)
        th = float(tau(t))
        M = expm(th * J)
        op = float(g_op(t))
        g = VGroup(grid_lines(M, tuple(c), u, FRAME, n=12, minor=1, color=C.text, opacity=0.55 * op, axes=False))
        if th > 0.01:                                   # the arcs î and ĵ have swept
            g.add(Arc(radius=u, start_angle=0, angle=th, color=C.ihat, stroke_width=C.stroke + 0.5,
                      stroke_opacity=op, arc_center=p3(c)),
                  Arc(radius=u, start_angle=PI / 2, angle=th, color=C.jhat, stroke_width=C.stroke + 0.5,
                      stroke_opacity=op, arc_center=p3(c)))
        for j, col, nm in ((0, C.ihat, r"\hat\imath"), (1, C.jhat, r"\hat\jmath")):
            tip = c + u * M[:, j]
            g.add(arrow(c, tip, col, width=C.stroke + 2, opacity=op))
            g.add(backed(tex(nm, size=40, color=col), buff=0.04).move_to(p3(c + 1.32 * u * M[:, j])).set_opacity(op))
        return g
    live(mm, moving, (T.cut_cols, T.numbers + 0.95), r1, r2, (T.cut_ch3 - 0.4, T.cut_ch3 - 0.02))

    # ── the panel: t, and e^{tA} with live numbers ──
    pan = panel(PX0, -3.75, PX1, 3.75)
    m.play(FadeIn(pan), at=T.numbers + 0.3, dur=0.6)
    clock = VGroup(tex("t", "=", size=44, colors={0: C.flow}),
                   DecimalNumber(0, num_decimal_places=2, font_size=44, color=C.flow)).arrange(RIGHT, buff=0.15)
    clock.move_to([MX, 3.0, 0])
    m.play(FadeIn(clock), at=T.numbers + 0.6, dur=0.5)
    m.drive(clock, lambda c, t: c[1].set_value(float(tau(t))), during=(r1[0], r2[1] + 0.05))

    lhs = tex(r"e^{tA}", "=", size=46)
    lhs[0][1].set_color(C.flow)
    lhs[0][2].set_color(C.gen)
    lhs.move_to([PX0 + 0.85, 1.55, 0])
    HB, VB = 1.15, 0.72                                  # numeric matrix cell spacing
    NC = np.array([MX + 0.75, 1.55])

    def cell_xy(i, j):
        return NC + [(j - 0.5) * HB, (0.5 - i) * VB]
    nums = VGroup()
    for i in range(2):
        for j in range(2):
            d = DecimalNumber(float(i == j), num_decimal_places=2, include_sign=False, font_size=38,
                              color=(C.ihat, C.jhat)[j])
            nums.add(d.move_to(p3(cell_xy(i, j))))
    br = brackets(2 * VB + 0.2, 2 * HB + 0.25).move_to(p3(NC))
    numat = VGroup(lhs, br, nums)
    m.play(FadeIn(numat), at=T.numbers + 1.0, dur=0.6)

    def upd(g, t):
        M = expm(float(tau(t)) * J)
        for k, d in enumerate(g[2]):
            v = float(M[k // 2, k % 2])
            d.set_value(0.0 if abs(v) < 0.005 else v)
            d.move_to(p3(cell_xy(k // 2, k % 2)))
    m.drive(numat, upd, during=(r1[0], r2[1] + 0.05))

    # columns: wherever î lands, wherever ĵ lands
    boxes = [Rectangle(width=HB * 0.9, height=2 * VB + 0.15, stroke_color=col, stroke_width=C.thin + 0.4,
                       fill_color=col, fill_opacity=0.12).move_to(p3(NC + [(j - 0.5) * HB, 0]))
             for j, col in ((0, C.ihat), (1, C.jhat))]
    m.play(FadeIn(boxes[0]), at=T.ihat + 0.2, dur=0.4)
    m.play(FadeIn(boxes[1]), at=T.jhat + 0.2, dur=0.4)

    # the cosines and sines
    sym = Mat([[r"\cos t", r"-\sin t"], [r"\sin t", r"\cos t"]], size=38, h_buff=1.45, v_buff=0.72)
    for i in range(2):
        for j in range(2):
            sym.cell(i, j).set_color((C.ihat, C.jhat)[j])
    sym_l = VGroup(tex("=", size=46), sym).arrange(RIGHT, buff=0.25).move_to([MX + 0.35, -0.3, 0])
    m.play(FadeIn(sym_l, shift=0.1 * DOWN), at=T.angle_t + 1.2, dur=0.8)
    m.play(FadeOut(VGroup(*boxes)), at=T.question - 0.6, dur=0.5)

    # ── the question: where is the grid at t = π? ──
    def ghost(t):
        c, u = cu(t)
        return VGroup(DashedVMobject(Circle(radius=u, color=C.muted, stroke_width=C.thin + 0.6).move_to(p3(c)),
                                     num_dashes=48),
                      Dot(p3(c + [-u, 0]), radius=0.08, color=C.muted))
    gh = ghost(T.question)
    q_tag = backed(tex(r"t = \pi\,?", size=44, color=C.flow), buff=0.06).move_to(p3(cu(T.question)[0] + [-1.7 * 1.7, 0.75]))
    m.play(Create(gh), at=T.question + 1.3, dur=1.0)
    m.play(FadeIn(q_tag, scale=0.9), at=T.predict - 1.4, dur=0.5)
    m.play(FadeOut(VGroup(gh, q_tag)), at=T.halfway - 0.4, dur=0.5)

    # ── halfway around: −I, the answer from the start ──
    mi = VGroup(tex("=", size=46), tex("-I", size=52)).arrange(RIGHT, buff=0.25).move_to([MX + 0.35, -2.0, 0])
    m.play(FadeIn(mi, shift=0.1 * DOWN), at=T.minus_identity + 0.3, dur=0.6)
    fin = VGroup(tex(r"e^{\pi J}", "=", "-I", size=46), tex(r"e^{i\pi}", "=", "-1", size=40, color=C.muted)).arrange(
        DOWN, buff=0.3)
    fin[0][0][2].set_color(C.gen)
    fin.move_to([MX, -2.65, 0])
    m.play(FadeOut(mi), FadeIn(fin[0], shift=0.1 * UP), at=T.minus_identity + 2.4, dur=0.7)
    m.play(FadeIn(fin[1], shift=0.1 * UP), at=T.half_turn - 1.0, dur=0.6)
    s.camera.push(at=T.halfway + 0.4, zoom=1.04, dur=5.0)
    m.play(FadeOut(VGroup(pan, clock, numat, sym_l, fin)), at=T.cut_ch3 - 0.4, dur=0.5)
    finish(s)
