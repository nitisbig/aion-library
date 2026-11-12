"""Ch5 · When the determinant is zero: the plane is squashed onto a line, points pile up, the information is gone,
so there is no inverse; and what that means for a system of equations."""
from aion import *

from beats import T
from shots import (A_ZERO, FRAME, I2, _clip, backdrop, backing, basis_arrows, finish, grid_lines, live,
                   matrix_panel, panel, pt, rail, strike, tex)

E = "easy_ease"
R5, R10 = np.sqrt(5.0), np.sqrt(10.0)
OF, UF = np.array([-1.6, -1.0]), 1.0                 # Ch4's swing framing
Z4 = np.column_stack([[3.0, 1.0], np.array([3.0, 1.0]) * R5 / R10])   # Ch4's last matrix: j-hat on i-hat's line
GX, GY0, GS = 6.0, -0.2, 0.5                         # Ch4's gauge
O5, U5 = np.array([0.6, -0.6]), 0.8                  # framing for the squash
NULL = np.array([-2.0, 1.0]) / R5                    # A_ZERO sends this direction to zero
STARTS = np.array([(1, 0), (3, -1), (-1, 1), (-3, 2), (5, -2)], float)   # all on x + 2y = 1, all land on (2, 1)
VLIM = 6.0                                           # colour range of the wash (the lost coordinate)


def ramp(t, a, b):
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def rot(deg, k=1.0):
    a = np.radians(deg)
    return k * np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def wash(p):
    """Colour of a starting point: its coordinate along the direction the matrix destroys."""
    v = float(np.clip((np.dot(p, NULL) + VLIM) / (2 * VLIM), 0, 1))
    return interpolate_color(ManimColor(C.khat), ManimColor(C.area), v)


@scene(T.cut_ch5, T.cut_ch6)
def s05_zero(s):
    backdrop(s)
    old = s.manim(z=2.5)                              # Ch4's leftovers
    w = s.manim(z=1)                                  # grid
    ln = s.manim(z=2)                                 # the red line
    r = s.manim(z=3)                                  # arrows
    hl = s.manim(z=3.5)                               # the five highlighted points, the question
    sy = s.manim(z=4)                                 # the two systems
    hb = s.manim(z=5.5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 5)
    t0 = T.cut_ch5

    # ── one score: Ch4's line relaxes to the plain grid, the arrows fall onto a line, then the whole plane follows;
    #    later, an attempt to undo it only moves the line around ──
    relax = (t0, T.det0 + 1.7)
    S1, S2 = rot(32, 1.35), np.array([[0.7, 0.0], [0.0, 1.9]])
    Mg = keys((t0, Z4), (relax[0] + 0.4, Z4), (relax[1], I2, E), (T.goes_with, I2), (T.squashed, A_ZERO, E), lead=0)
    Ma = keys((t0, Z4), (relax[0] + 0.4, Z4), (relax[1], I2, E), (T.same_line - 0.1, I2),
              (T.same_line + 1.0, A_ZERO, E), lead=0)
    Sx = keys((t0, I2), (T.undo, I2), (T.undo + 1.3, S1, E), (T.unsquash - 0.1, S1), (T.unsquash + 1.0, S2, E),
              (T.unsquash + 2.2, I2, E), lead=0)
    Og = keys((t0, OF), (relax[0] + 0.4, OF), (relax[1], O5, E), lead=0)
    Ug = keys((t0, UF), (relax[0] + 0.4, UF), (relax[1], U5, E), lead=0)
    out = (T.system - 1.3, T.system - 0.5)

    def kout(t):
        return 1 - ramp(t, *out)
    undo = (T.undo - 0.05, T.unsquash + 2.25)
    moving_g = (relax, (T.goes_with - 0.05, T.squashed + 0.05), undo, out)
    moving_a = (relax, (T.same_line - 0.15, T.same_line + 1.05), undo, out)
    live(w, lambda t: grid_lines(Sx(t) @ Mg(t), Og(t), Ug(t), FRAME, n=16, opacity=kout(t)), *moving_g)
    live(r, lambda t: basis_arrows(Sx(t) @ Ma(t), Og(t), Ug(t)).set_opacity(kout(t)), *moving_a)

    def red(t):
        k = ramp(t, T.same_line + 0.6, T.same_line + 1.2) * kout(t)
        d = Sx(t) @ np.array([2.0, 1.0])
        seg = _clip(np.asarray(Og(t)), d, FRAME)
        if k < 0.003 or seg is None:
            return VGroup()
        return Line([*seg[0], 0], [*seg[1], 0], color=C.collapse, stroke_width=6, stroke_opacity=k)
    live(ln, red, (T.same_line + 0.55, T.same_line + 1.25), undo, out)

    # ── the plane as points, coloured by the coordinate the matrix is about to destroy ──
    gen = np.random.default_rng(5)
    xs, ys = np.meshgrid(np.arange(-11, 11, 0.11), np.arange(-7, 7, 0.11))
    P0 = np.column_stack([xs.ravel(), ys.ravel()]) + gen.uniform(-0.04, 0.04, (xs.size, 2))
    P0 = P0[gen.permutation(len(P0))]                # draw order shuffled, so the squashed line is a true smear
    vals = P0 @ NULL

    def positions(t):
        M = Sx(t) @ Mg(t)
        return Og(t) + Ug(t) * (P0 @ M.T)
    alpha = keys((t0, 0.0), (relax[1] - 0.6, 0.0), (relax[1] + 0.4, 1.0, E), (T.worse, 1.0), (T.worse + 0.7, 0.3, E),
                 (T.no_inv - 0.8, 0.3), (T.no_inv - 0.1, 1.0, E), (out[0], 1.0), (out[1], 0.0, E), lead=0)
    s.add(PointsLayer(positions, values=lambda t: vals, cmap="ramp", vmin=-VLIM, vmax=VLIM,
                      colors=(C.khat, C.text, C.area), size=4.2, glow=0.0, alpha=alpha, additive=False, z=2.5))

    # ── Ch4's last frame: the red line, the swing's orbit, the gauge reading zero ──
    seg = _clip(OF, np.array([3.0, 1.0]), FRAME)
    red4 = Line([*seg[0], 0], [*seg[1], 0], color=C.collapse, stroke_width=6)
    orbit = DashedVMobject(Circle(radius=R5 * UF, color=C.faint, stroke_width=C.thin).move_to([*OF, 0]),
                           num_dashes=60)
    old.add(red4, orbit)
    old.play(FadeOut(VGroup(red4, orbit)), at=relax[0] + 1.0, dur=0.7, lead=0)

    def GY(v):
        return GY0 + v * GS
    gauge = VGroup(Line([GX, GY(-6.2), 0], [GX, GY(6.2), 0], color=C.text, stroke_width=C.thin + 0.4))
    for k in range(-6, 7):
        L = 0.24 if k % 5 == 0 else 0.13
        gauge.add(Line([GX - L / 2, GY(k), 0], [GX + L / 2, GY(k), 0], color=C.text, stroke_width=C.thin + 0.4))
    gauge.add(Line([GX - 0.3, GY(0), 0], [GX + 0.3, GY(0), 0], color=C.text, stroke_width=C.thin + 0.8))
    gauge.add(tex(r"\det", size=44).move_to([GX, GY(6.2) + 0.4, 0]))
    gback = backing(VGroup(gauge, Line([GX - 1.05, 0, 0], [GX - 1.05, 0.01, 0]),
                           Line([GX + 0.6, 0, 0], [GX + 0.6, 0.01, 0])), pad=0.2)
    zero = VGroup(Line([GX - 0.2, GY(0), 0], [GX + 0.2, GY(0), 0], color=C.collapse, stroke_width=C.stroke))
    zl = tex("0", size=40, color=C.collapse)
    zero.add(zl.move_to([GX - 0.3 - zl.width / 2, GY(0), 0]))
    hb.add(gback)
    hud.add(gauge, zero)
    hb.play(FadeOut(gback), at=t0 + 0.05, dur=0.7, lead=0)
    hud.play(FadeOut(VGroup(gauge, zero)), at=t0 + 0.05, dur=0.7, lead=0)

    # ── the HUD: our new matrix, det A = 0 ──
    rd = tex(r"\det A", "=", "0", size=56, colors={2: C.collapse})
    M, hats, back = matrix_panel([["2", "4"], ["1", "2"]], below=rd)
    hb.play(FadeIn(back), at=T.det0 + 0.2, dur=0.6, lead=0)
    hud.play(FadeIn(VGroup(M, hats, rd)), at=T.det0 + 0.3, dur=0.6, lead=0)
    hud.play(Indicate(rd[2], color=C.collapse, scale_factor=1.5), at=T.zero_area, dur=0.9)

    # ── five points on one line of starting points, all landing on the same spot ──
    def W(v):
        return pt(O5, U5, v)
    land = W(A_ZERO @ STARTS[0])
    dots = VGroup(*[Dot(W(p), radius=0.11, color=wash(p)).set_stroke(C.text, width=2.5) for p in STARTS])
    hl.play(LaggedStart(*[FadeIn(d, scale=2.0) for d in dots], lag_ratio=0.2), at=T.points, dur=1.2)
    hl.play(LaggedStart(*[Indicate(d, color=d.get_color(), scale_factor=1.6) for d in dots], lag_ratio=0.15),
            at=T.different - 0.1, dur=1.2)
    hl.play(LaggedStart(*[d.animate.move_to(land) for d in dots], lag_ratio=0.12), at=T.on_top - 0.5, dur=1.8)
    ring = Circle(radius=0.26, color=C.text, stroke_width=C.thin + 0.6).move_to(land)
    q = tex("?", size=80).next_to(ring, UR, buff=0.05)
    hl.play(Create(ring), at=T.suppose + 0.4, dur=0.6)
    hl.play(FadeIn(q, scale=1.3), at=T.came_from, dur=0.5)
    p_a, p_b = STARTS[0] + 9 * NULL * R5 / 2, STARTS[0] - 9 * NULL * R5 / 2
    preimage = DashedLine(W(p_a), W(p_b), color=C.text, stroke_width=C.thin + 0.4, dash_length=0.12)
    ghosts = VGroup(*[Circle(radius=0.11, color=wash(p), stroke_width=C.thin + 1).move_to(W(p)) for p in STARTS])
    hl.play(Create(preimage), at=T.whole_line, dur=1.2)
    hl.play(LaggedStart(*[FadeIn(g_, scale=1.5) for g_ in ghosts], lag_ratio=0.2), at=T.whole_line + 0.6, dur=1.2)
    hl.play(Indicate(preimage, color=C.text, scale_factor=1.0), Indicate(q, scale_factor=1.3), at=T.info, dur=1.0)
    hl.play(FadeOut(VGroup(dots, ring, q, preimage, ghosts)), at=T.no_inv - 0.9, dur=0.6, lead=0)

    # ── no inverse: A⁻¹ is written and struck out; the attempt to undo only moves the line ──
    inv = tex("A^{-1}", size=96).move_to([1.6, 2.75, 0])
    x_inv = strike(inv, color=C.collapse).set_stroke(width=C.stroke)
    hud.play(Write(inv), at=T.no_inv, dur=0.8)
    hud.play(Create(x_inv), at=T.no_inv + 0.9, dur=0.4)
    hb.play(FadeOut(back), at=out[0], dur=0.6, lead=0)
    hud.play(FadeOut(VGroup(M, hats, rd, inv, x_inv)), at=out[0], dur=0.6, lead=0)

    # ── systems of equations, side by side: two lines crossing once; two parallel lines; the same line twice ──
    def system(box, eqs, cols, head):
        x0, y0, x1, y1 = box
        fr = panel(*box)
        rows = VGroup(*[tex(*e, size=40, color=c) for e, c in zip(eqs, cols)]).arrange(DOWN, aligned_edge=LEFT,
                                                                                      buff=0.22)
        rows.move_to([x0 + 0.35 + rows.width / 2, y1 - 0.3 - rows.height / 2, 0])
        hd = tex(*head, size=48).move_to([x1 - 0.4, rows.get_y(), 0], aligned_edge=RIGHT)
        gbox = (x0 + 0.03, y0 + 0.03, x1 - 0.03, rows.get_bottom()[1] - 0.25)
        O, U = np.array([x0 + 1.3, y0 + 1.0]), 0.62
        ref = grid_lines(I2, O, U, gbox, n=12, color=C.grid_minor)
        return fr, rows, hd, gbox, O, U, ref

    def eq_line(a_, b_, c_, O, U, box, col):
        n = np.array([a_, b_], float)
        p0 = n * c_ / n.dot(n)                        # the point of a x + b y = c nearest the origin
        seg = _clip(O + U * p0, U * np.array([-b_, a_], float), box)
        return Line([*seg[0], 0], [*seg[1], 0], color=col, stroke_width=C.stroke)

    boxL, boxR = (-6.85, -3.35, -0.15, 3.35), (0.15, -3.35, 6.85, 3.35)
    c1, c2 = C.khat, C.area
    fL, rL, hL, gL, OL, UL, refL = system(boxL, ((r"x + y = 3",), (r"x - y = 1",)), (c1, c2),
                                          (r"\det", r"\neq", "0"))
    hL[2].set_color(C.text)
    fR, rR, hR, gR, OR, UR_, refR = system(boxR, ((r"x + 2y = 2",), (r"2x + 4y = ", "8")), (c1, c2),
                                           (r"\det", "=", "0"))
    hR[2].set_color(C.collapse)
    L1, L2 = eq_line(1, 1, 3, OL, UL, gL, c1), eq_line(1, -1, 1, OL, UL, gL, c2)
    R1, R2 = eq_line(1, 2, 2, OR, UR_, gR, c1), eq_line(1, 2, 4, OR, UR_, gR, c2)
    R2b = eq_line(1, 2, 2, OR, UR_, gR, c2).set_stroke(width=C.stroke * 0.45)   # thinner: both lines show
    sy.play(FadeIn(VGroup(fL, refL, fR, refR)), at=T.system - 0.3, dur=0.8)
    sy.play(FadeIn(rL), Create(L1), Create(L2), at=T.nonzero - 0.4, dur=0.9)
    sy.play(Write(hL), at=T.nonzero + 0.4, dur=0.7)
    meet = Dot(pt(OL, UL, (2, 1)), radius=0.1, color=C.text)
    sy.play(FadeIn(meet, scale=2.5), at=T.one_answer, dur=0.5)
    sy.play(Indicate(meet, color=C.text, scale_factor=1.8), at=T.one_answer + 0.7, dur=0.8)
    sy.play(FadeIn(rR), Create(R1), Create(R2), Write(hR), at=T.one_answer + 1.8, dur=1.0)
    none = tex(r"\varnothing", size=56, color=C.collapse).move_to([boxR[2] - 0.7, -2.6, 0])
    sy.play(FadeIn(none, scale=1.3), at=T.missing, dur=0.5)
    eight = rR[1][1]
    four = tex("4", size=40, color=c2).move_to(eight, aligned_edge=LEFT)
    inf = tex(r"\infty", size=56, color=C.collapse).move_to(none)
    sy.play(Transform(R2, R2b), FadeOut(eight), FadeIn(four), FadeOut(none), at=T.infinite - 0.4, dur=1.1)
    sy.play(FadeIn(inf, scale=1.3), at=T.infinite + 0.6, dur=0.5)

    finish(s)
