"""s09 grid flow (ch2): drop in a whole grid and let the flow of A = J carry it. Its lines stay straight, parallel and
evenly spaced, because the velocity rule is linear: if p and q flow, p + q flows to the sum of where they went (the
parallelogram stays a parallelogram). So at every moment the flow has done a linear transformation, a matrix: e^{tA},
where the flow of A has carried every point after time t. A is the velocity; e^{tA} is the trip."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, FRAME, J, arrow, backdrop, backed, disc_points, field_arrows, finish, flow_layers, lab, live, p3, poly, tex

P, Q = np.array([2.0, 0.6]), np.array([0.4, 1.6])


@scene(T.cut_grid, T.cut_cols)
def s09_grid_flow(s):
    backdrop(s)
    mg = s.manim(z=0)                                  # the static grid (from s08)
    mf = s.manim(z=1)                                  # the field (fades)
    mm = s.manim(z=3)                                  # the moving grid
    m = s.manim(z=5)

    grid = grid_lines(np.eye(2), (0.0, 0.0), 1.0, FRAME, n=16)
    mg.add(grid)
    field = field_arrows(J, box=FRAME, spacing=0.75)
    mf.add(field)
    mf.play(FadeOut(field), at=T.grid - 0.2, dur=0.8)
    grid_d = grid_lines(np.eye(2), (0.0, 0.0), 1.0, FRAME, n=16, opacity=0.45)
    mg.play(FadeOut(grid), FadeIn(grid_d), at=T.grid, dur=0.8)

    # flow time: two full turns over the scene, so the grid is home again at the cut
    t_a, t_b = T.grid + 1.4, T.cut_cols - 0.7
    tau = keys((t_a, 0.0), (t_b, 4 * PI, E), lead=0)
    g_op = keys((T.grid + 0.2, 0.0), (T.grid + 1.0, 1.0), (T.cut_cols - 0.6, 1.0), (T.cut_cols - 0.1, 0.0), lead=0)

    def moving(t):
        M = expm(float(tau(t)) * J)
        return grid_lines(M, (0.0, 0.0), 1.0, FRAME, n=12, minor=1, color=C.text, opacity=0.6 * float(g_op(t)),
                          axes=False)
    live(mm, moving, (T.grid + 0.2, T.cut_cols - 0.05))

    # particles underneath, at 40 %
    p_op = keys((T.grid + 0.6, 0.0), (T.grid + 1.4, 0.4), (T.cut_cols - 0.9, 0.4), (T.cut_cols - 0.2, 0.0), lead=0)
    flow_layers(s, disc_points(2500, 3.9, seed=5), J, tau, alpha=p_op, trail=6, size=2.2, z=2,
                start=T.grid + 0.5, end=T.cut_cols)

    # ── straight, parallel, evenly spaced ──
    def lines_of(t, ys, op):
        M = expm(float(tau(t)) * J)
        out = VGroup()
        for y in ys:
            a, b = M @ np.array([-9.0, y]), M @ np.array([9.0, y])
            out.add(Line(p3(a), p3(b), color=C.vec, stroke_width=C.stroke + 0.5, stroke_opacity=op))
        return out
    h1 = keys((T.straight - 0.2, 0.0), (T.straight + 0.3, 1.0), (T.no_coincidence - 0.3, 1.0),
              (T.no_coincidence + 0.2, 0.0), lead=0)
    h2 = keys((T.straight + 0.9, 0.0), (T.straight + 1.4, 1.0), (T.no_coincidence - 0.3, 1.0),
              (T.no_coincidence + 0.2, 0.0), lead=0)
    h3 = keys((T.straight + 2.0, 0.0), (T.straight + 2.5, 1.0), (T.no_coincidence - 0.3, 1.0),
              (T.no_coincidence + 0.2, 0.0), lead=0)

    def highlights(t):
        M = expm(float(tau(t)) * J)
        out = VGroup(lines_of(t, [1.0], float(h1(t))), lines_of(t, [2.0], float(h2(t))))
        a3 = float(h3(t))
        for k in range(-3, 4):                          # evenly spaced: the integer points of the first line
            out.add(Dot(p3(M @ np.array([k, 1.0])), radius=0.07, color=C.text).set_opacity(a3))
        return out
    live(m, highlights, (T.straight - 0.2, T.no_coincidence + 0.25))
    tags = [lab(w, 30, C.vec) for w in ("straight", "parallel", "evenly spaced")]
    tg = VGroup(*tags).arrange(RIGHT, buff=0.5).move_to([0, 3.45, 0])
    tg = backed(tg)
    m.add(tg[0], at=T.straight - 0.5)
    for i, at in enumerate((T.straight, T.straight + 1.1, T.straight + 2.2)):
        m.play(FadeIn(tags[i], shift=0.08 * DOWN), at=at, dur=0.4)
    m.play(FadeOut(tg), at=T.no_coincidence + 0.2, dur=0.5)

    # ── linear: p, q and p + q all flow, and the parallelogram stays a parallelogram ──
    pq_op = keys((T.sum_flows - 1.6, 0.0), (T.sum_flows - 1.0, 1.0), (T.definition - 0.4, 1.0),
                 (T.definition + 0.2, 0.0), lead=0)

    def pq(t):
        M = expm(float(tau(t)) * J)
        op = float(pq_op(t))
        p, q = M @ P, M @ Q
        out = VGroup(poly([(0, 0), p, p + q, q], C.vec, C.thin + 0.6, opacity=0.6 * op, close=True))
        for v, nm in ((p, "p"), (q, "q"), (p + q, "p+q")):
            out.add(Dot(p3(v), radius=0.1, color=C.vec).set_opacity(op))
            out.add(backed(tex(nm, size=36, color=C.vec), buff=0.04).move_to(p3(v + 0.42 * v / np.linalg.norm(v)))
                    .set_opacity(op))
        return out
    live(m, pq, (T.sum_flows - 1.6, T.definition + 0.25))
    lin = backed(VGroup(tex(r"e^{tA}", "(", "p", "+", "q", ")", "=", r"e^{tA}", "p", "+", r"e^{tA}", "q", size=42,
                            colors={0: C.flow, 2: C.vec, 4: C.vec, 7: C.flow, 8: C.vec, 10: C.flow, 11: C.vec})))
    lin.move_to([0, 3.3, 0])

    # ── the flow is a linear map: a matrix, e^{tA} ──
    lt = backed(lab("a linear transformation", 32, C.text)).move_to([0, 3.3, 0])
    m.play(FadeIn(lt, shift=0.08 * DOWN), at=T.linear + 0.6, dur=0.5)
    m.play(FadeOut(lt), at=T.etA - 0.4, dur=0.4)
    m.play(FadeIn(lin, shift=0.08 * DOWN), at=T.etA + 0.2, dur=0.7)

    # teal arrows from each starting ghost to where the flow has carried it
    def trip(t):
        M = expm(float(tau(t)) * J)
        op = float(pq_op(t)) * float(trip_op(t))
        out = VGroup()
        for v in (P, Q, P + Q):
            out.add(Dot(p3(v), radius=0.08, color=C.vec).set_opacity(0.35 * op))
            out.add(arrow(v, M @ v, C.flow, width=C.stroke, opacity=op))
        return out
    trip_op = keys((T.etA + 0.6, 0.0), (T.etA + 1.1, 1.0), lead=0)
    live(m, trip, (T.etA + 0.6, T.definition + 0.25))

    # ── the definition to keep ──
    m.play(FadeOut(lin), at=T.definition - 0.3, dur=0.4)
    dfn = backed(VGroup(tex(r"e^{tA}", size=60, color=C.flow),
                        lab("where the flow of A has carried every point after time t", 30, C.text)).arrange(
        RIGHT, buff=0.35)).move_to([0, 3.25, 0])
    m.play(FadeIn(dfn, shift=0.08 * DOWN), at=T.definition + 0.4, dur=0.8)

    # ── A is the velocity; e^{tA} is the trip ──
    vel = VGroup(arrow((-0.45, 0), (0.45, 0), C.gen, width=C.stroke + 1.5), tex("A", size=54, color=C.gen),
                 lab("velocity", 28, C.gen)).arrange(DOWN, buff=0.2)
    path = ArcBetweenPoints(p3((-0.5, -0.15)), p3((0.5, 0.15)), angle=-1.6, color=C.flow, stroke_width=C.stroke + 1)
    path.add_tip(tip_length=0.18, tip_width=0.18)
    trp = VGroup(path, tex(r"e^{tA}", size=54, color=C.flow), lab("trip", 28, C.flow)).arrange(DOWN, buff=0.2)
    pair = VGroup(vel, trp).arrange(RIGHT, buff=1.4)
    pair = backed(pair, buff=0.25).move_to([4.1, -2.55, 0])
    m.play(FadeIn(pair[0]), FadeIn(vel, shift=0.1 * UP), at=T.velocity_trip, dur=0.6)
    m.play(FadeIn(trp, shift=0.1 * UP), at=T.velocity_trip + 1.6, dur=0.6)
    m.play(FadeOut(VGroup(dfn, pair)), at=T.cut_cols - 0.4, dur=0.5)
    mg.play(FadeOut(grid_d), FadeIn(grid), at=T.cut_cols - 0.5, dur=0.4)
    finish(s)
