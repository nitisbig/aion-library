"""Ch5 · Solving equations (3/3): Ax = b asks which arrow the move sent to b. In 2D the two lines cross at (1, 2), and
that arrow pushed through A lands on b. In 3D three planes meet at (1, 2, 1); at det 0 they share a line, or miss."""
from aion import *

from beats import T
from shots import (A, FRAME, I2, Cam, Mat, arrow, backdrop, backing, basis_arrows, finish, grid_lines, live, lit_poly,
                   pt, rail, tex)

E = "smooth"
B = np.array([5.0, 6.0])                               # A @ (1, 2)
X = np.array([1.0, 2.0])
O2, U2 = (0.2, -2.9), 0.58                             # the 2D grid (right of the panel)
BOX2 = (-2.6, FRAME[1], FRAME[2], FRAME[3])

# 3D: x + y + z = 4, x - y + 2z = 1, 2x + y - z = 3 → (1, 2, 1); singular third row 2x + 3z = 5 (a line) or 6 (none)
P = np.array([1.0, 2.0, 1.0])
N1, N2 = np.array([1.0, 1.0, 1.0]), np.array([1.0, -1.0, 2.0])
N3a, N3b = np.array([2.0, 1.0, -1.0]), np.array([2.0, 0.0, 3.0])
D1, D2, D3a, D3b, D3c = 4.0, 1.0, 3.0, 5.0, 6.0
LINE = np.cross(N1, N2) / np.linalg.norm(np.cross(N1, N2))   # the shared line when det = 0 (through P)
H = 2.1                                                # half size of each drawn plane patch


def patch(n, d, cam, color, op):
    """The plane n·x = d as a square patch centred at the point of the plane nearest P (world shifted so P is 0)."""
    n = np.asarray(n, float)
    k = np.linalg.norm(n)
    c = P + (d - n @ P) / k ** 2 * n - P
    nh = n / k
    e1 = np.cross(nh, [0.0, 0.0, 1.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(nh, e1)
    pts = [c + H * (sx * e1 + sy * e2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return lit_poly(cam, pts, color, opacity=op, edge=color)


@scene(T.cut_solve, T.cut_ch6)
def s13_solve(s):
    backdrop(s)
    t2 = T.planes - 0.9                                # 2D out, 3D in
    out2 = keys((t2, 1.0), (t2 + 0.7, 0.0), lead=0)
    end = keys((T.cut_ch6 - 0.7, 1.0), (T.cut_ch6 - 0.05, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=out2)
    m = s.manim(z=1, opacity=out2)
    g = s.manim(z=3, opacity=out2)
    w3 = s.manim(z=2, opacity=end)
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 4, drop=(5, T.warning + 0.5))

    # ── the panel: the three equations from the start, and Ax = b ──
    rows = [tex("x", "+", "y", "+", "z", "=", "4", size=44), tex("x", "-", "y", "+", "2z", "=", "1", size=44),
            tex("2x", "+", "y", "-", "z", "=", "3", size=44)]
    eqs = VGroup(*rows).arrange(DOWN, buff=0.22, aligned_edge=RIGHT)
    axb = tex("A", r"\mathbf{x}", "=", r"\mathbf{b}", size=56, colors={1: C.vec, 3: C.target})
    stack = VGroup(eqs, axb).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    stack.move_to([-7.11 + C.margin + 0.35 + stack.width / 2, 3.55 - C.margin - stack.height / 2, 0])
    panel = backing(stack, pad=0.28)
    hb.play(FadeIn(panel), at=T.equations - 0.2, dur=0.5)
    hud.play(LaggedStart(*[FadeIn(r, shift=0.1 * DOWN) for r in rows], lag_ratio=0.2), at=T.equations, dur=1.0)
    hud.play(FadeIn(axb, shift=0.1 * UP), at=T.about_move + 1.6, dur=0.7)

    # ── 2D: where did an arrow land? which arrow was it? ──
    m0, m1 = T.on_target + 1.1, T.on_target + 3.1       # "Seen as a move ..." → lands on "exactly on the target"
    u = keys((m0, 0.0), (m1, 1.0, E), lead=0)

    def M(t):
        return I2 + u(t) * (A - I2)
    base = grid_lines(I2, O2, U2, BOX2)
    m.play(FadeIn(base), at=T.about_move + 2.6, dur=0.8)
    m.remove(base, at=m0)
    live(m, lambda t: grid_lines(M(t), O2, U2, BOX2), (m0, m1))
    ghost.add(grid_lines(I2, O2, U2, BOX2, color=C.ghost, axes=False), at=m0)
    a0 = basis_arrows(I2, O2, U2)
    g.play(FadeIn(a0), at=T.about_move + 2.9, dur=0.6)
    g.remove(a0, at=m0)
    live(g, lambda t: basis_arrows(M(t), O2, U2), (m0, m1))

    tb = pt(O2, U2, B)
    bdot = Dot(tb, radius=0.11, color=C.target)
    bl = tex(r"\mathbf{b}", size=48, color=C.target).next_to(bdot, RIGHT, buff=0.15)
    g.play(FadeIn(bdot, scale=2), FadeIn(bl), at=T.which_arrow - 1.6, dur=0.6)
    qm = tex("?", size=56, color=C.vec).move_to(pt(O2, U2, (0.6, 1.4)))
    g.play(FadeIn(qm, scale=1.4), at=T.which_arrow + 0.6, dur=0.5, ease="out_back")
    g.play(FadeOut(qm), at=T.lines2d - 0.3, dur=0.4)

    # each equation is a line; the answer is where they cross
    def eq_line(a, b, c, color):                       # a x + b y = c, drawn over x in [-2.2, 4.4]
        xs = np.array([-2.2, 4.4])
        if abs(b) > 1e-9:
            ends = [(x, (c - a * x) / b) for x in xs]
        else:
            ends = [(c / a, -3), (c / a, 8)]
        return Line(pt(O2, U2, ends[0]), pt(O2, U2, ends[1]), color=color, stroke_width=C.stroke)
    L1, L2 = eq_line(3, 1, 5, C.data), eq_line(2, 2, 6, C.muted)
    e1 = tex("3x", "+", "y", "=", "5", size=40, color=C.data).move_to(pt(O2, U2, (1.0, 4.3)) + np.array([1.1, 0, 0]))
    e2 = tex("2x", "+", "2y", "=", "6", size=40, color=C.muted).move_to(pt(O2, U2, (-1.6, 4.6)) + np.array([0.2, 0.3, 0]))
    g.play(Create(L1), FadeIn(e1), at=T.lines2d + 0.9, dur=1.0)
    g.play(Create(L2), FadeIn(e2), at=T.lines2d + 1.6, dur=1.0)
    xdot = Dot(pt(O2, U2, X), radius=0.1, color=C.vec)
    xl = tex("(1, 2)", size=40, color=C.vec).next_to(xdot, LEFT, buff=0.2)
    g.play(FadeIn(xdot, scale=2), at=T.cross + 0.4, dur=0.5)
    g.play(FadeIn(xl), at=T.cross + 0.7, dur=0.5)

    # seen as a move: the arrow (1, 2) is the one A sends to b
    g.play(FadeOut(VGroup(L1, L2, e1, e2, xl)), FadeOut(xdot), at=m0 - 0.9, dur=0.5)
    xa = arrow(pt(O2, U2, (0, 0)), pt(O2, U2, X), C.vec, width=C.stroke + 1)
    g.play(GrowArrow(xa), at=m0 - 0.5, dur=0.5)
    g.remove(xa, at=m0)
    held = g.redraw(lambda t: arrow(pt(O2, U2, (0, 0)), pt(O2, U2, M(t) @ X), C.vec, width=C.stroke + 1),
                    during=(m0, m1))
    g.play(Flash(tb, color=C.target, line_length=0.22, flash_radius=0.32), at=m1 + 0.4, dur=0.7)

    # ── 3D: each equation is a plane; three planes meet at one point ──
    t3 = T.planes + 0.9
    az = keys((t3, -66.0), (T.cut_ch6, -44.0, "linear"), lead=0)       # a slow drift so the planes read as 3D

    def cam_at(t):
        return Cam(az(t), 20.0, origin=(1.9, -0.4), unit=0.78)
    cols = (C.data, C.muted, C.frame)
    r = [keys((t3 + 0.6 * i, 0.0), (t3 + 1.2 + 0.6 * i, 1.0, "out_back"), lead=0) for i in range(3)]
    rot = keys((T.det_zero + 0.6, 0.0), (T.det_zero + 2.6, 1.0, E), lead=0)
    sh = keys((T.miss - 0.2, 0.0), (T.miss + 1.3, 1.0, E), lead=0)
    op_x = keys((T.meet - 0.8, 0.0), (T.meet - 0.1, 1.0), lead=0)       # where each pair of planes crosses
    op_s = keys((T.meet + 0.3, 0.0), (T.meet + 0.8, 1.0), (T.det_zero + 0.4, 1.0), (T.det_zero + 0.9, 0.0), lead=0)
    op_l = keys((T.solution + 0.3, 0.0), (T.solution + 0.8, 1.0), (T.det_zero + 0.4, 1.0), (T.det_zero + 0.9, 0.0),
                lead=0)
    op_n = keys((T.infinitely - 0.2, 0.0), (T.infinitely + 0.6, 1.0), (T.miss - 0.2, 1.0), (T.miss + 0.4, 0.0), lead=0)
    sl0 = tex("(1, 2, 1)", size=44, color=C.vec)

    def third(t):
        k = rot(t)
        return (1 - k) * N3a + k * N3b, (1 - k) * D3a + k * D3b + sh(t) * (D3c - D3b)

    def pair_line(cam, n1, d1, n2, d2):
        """The segment where two planes cross (centred on the point nearest P), or None if they are parallel."""
        dvec = np.cross(n1, n2)
        if np.linalg.norm(dvec) < 1e-6:
            return None
        q = np.linalg.lstsq(np.array([n1, n2]), np.array([d1, d2]) - np.array([n1 @ P, n2 @ P]), rcond=None)[0]
        q = q - (q @ dvec) / (dvec @ dvec) * dvec
        e = dvec / np.linalg.norm(dvec)
        return Line(cam.scr(q - 1.9 * e), cam.scr(q + 1.9 * e), color=C.text, stroke_width=C.thin + 1)

    def world(t):
        cam = cam_at(t)
        n3, d3 = third(t)
        pl = ((N1, D1), (N2, D2), (n3, d3))
        out = VGroup()
        for i, (n, d) in enumerate(pl):
            ri = r[i](t)
            if ri > 0.001:
                out.add(patch(n, d, cam, cols[i], 0.16 * min(ri, 1.0)).shift(np.array([0, -1.2 * (1 - ri), 0])))
        ox = op_x(t)
        if ox > 0.01:
            for i, j in ((0, 1), (0, 2), (1, 2)):
                ln = pair_line(cam, *pl[i], *pl[j])
                if ln is not None:
                    out.add(ln.set_stroke(opacity=0.7 * ox))
        on = op_n(t)
        if on > 0.01:
            out.add(Line(cam.scr(-2.6 * LINE), cam.scr(2.6 * LINE), color=C.null, stroke_width=C.stroke + 1,
                         stroke_opacity=on))
        os_, ol = op_s(t), op_l(t)
        if os_ > 0.01:
            out.add(Dot(cam.scr(np.zeros(3)), radius=0.11, color=C.vec).set_opacity(os_))
        if ol > 0.01:
            out.add(sl0.copy().next_to(cam.scr(np.zeros(3)), UR, buff=0.2).set_opacity(ol))
        return out
    w3.redraw(world, during=(t3, T.cut_ch6))

    # det = 0: the third plane turns into 2x + 3z = 5; the three share a whole line
    det = tex(r"\det", "=", "0", size=52, colors={2: C.null}).next_to(stack, DOWN, buff=0.5).align_to(stack, LEFT)
    hb.play(Transform(panel, backing(VGroup(stack, det), pad=0.28)), at=T.det_zero + 0.1, dur=0.5)
    hud.play(FadeIn(det, shift=0.1 * UP), at=T.det_zero + 0.3, dur=0.5)
    row3b = tex("2x", "+", "3z", "=", "5", size=44).move_to(rows[2], aligned_edge=RIGHT)
    hud.play(TransformMatchingTex(rows[2], row3b), at=T.det_zero + 0.6, dur=1.6, ease=E)

    # ... or the right side becomes 6 and the planes miss: no answer at all
    row3c = tex("2x", "+", "3z", "=", "6", size=44).move_to(row3b, aligned_edge=RIGHT)
    hud.play(TransformMatchingTex(row3b, row3c), at=T.miss - 0.2, dur=0.8)
    empty = tex(r"\varnothing", size=72, color=C.null).move_to([4.6, -2.4, 0])
    w3.play(FadeIn(empty, scale=1.5), at=T.no_answer + 0.1, dur=0.6, ease="out_back")
    finish(s)
