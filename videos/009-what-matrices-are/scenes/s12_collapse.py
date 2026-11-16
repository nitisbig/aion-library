"""Ch5 · det 0 (2/3): the plane squashes onto a line; different points land on one spot, so nothing can undo it. The
null space (pink) crushes into the origin, the column space is what is left. A shadow is the same kind of move:
the light direction is the null space, and a die stretched along the light casts exactly the same shadow."""
from aion import *

from beats import T
from shots import (COLLAPSE, FRAME, I2, I3, O5, U5, Cam, Mat, arrow, backdrop, backing, basis_arrows, die_height,
                   die_rgba, finish, grid_lines, live, pt, tex, unit_square)

E = "smooth"
NULL = np.array([1.0, -2.0])                           # COLLAPSE @ NULL = 0
P0 = np.array([1.0, 1.0])
KS = (-1.0, -0.5, 0.0, 0.5, 1.0)

# 3D: a die hovering over a floor, parallel light
AZ, EL, CO, CU = -35.0, 22.0, np.array([0.6, -0.1]), 1.0
DIE_C = np.array([0.0, 0.0, 0.7])                      # the die's centre
ZF = -1.9                                              # the floor
L = np.array([0.55, 0.4, -1.0])
L = L / np.linalg.norm(L)                              # the light's direction (downwards)
STRETCH = I3 + 0.9 * np.outer(L, L)                    # a die stretched along the light: same shadow


def shadow(p):
    """Where the light carries a world point p onto the floor (a rank-2 move: the light direction is lost)."""
    p = np.asarray(p, float)
    return p - ((p[2] - ZF) / L[2]) * L


@scene(T.cut_collapse, T.cut_solve)
def s12_collapse(s):
    backdrop(s)
    t2 = T.shadow - 1.5                                # 2D out, 3D in
    out2 = keys((t2, 1.0), (t2 + 0.8, 0.0), lead=0)
    in3 = keys((t2 + 0.6, 0.0), (t2 + 1.4, 1.0), (T.cut_solve - 0.7, 1.0), (T.cut_solve - 0.05, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=out2)
    m = s.manim(z=1, opacity=out2)
    sq = s.manim(z=2, opacity=out2)
    g = s.manim(z=3, opacity=out2)
    hb = s.manim(z=4.9, parallax=0.0, opacity=out2)
    hud = s.manim(z=5, parallax=0.0, opacity=out2)

    # ── squash: det 0 ──
    c0, c1 = T.nothing + 0.3, T.nothing + 2.3
    u = keys((c0, 0.0), (c1, 1.0, E), lead=0)

    def M(t):
        return I2 + u(t) * (COLLAPSE - I2)
    base = grid_lines(I2, O5, U5, FRAME)
    m.add(base)
    m.remove(base, at=c0)
    live(m, lambda t: grid_lines(M(t), O5, U5, FRAME), (c0, c1))
    ghost.add(grid_lines(I2, O5, U5, FRAME, color=C.ghost, axes=False))
    a0 = basis_arrows(I2, O5, U5)
    g.add(a0)
    g.remove(a0, at=c0)
    live(g, lambda t: basis_arrows(M(t), O5, U5), (c0, c1))

    sq0 = VGroup(unit_square(I2), DecimalNumber(1.0, num_decimal_places=1, font_size=40)
                 .move_to(unit_square(I2).get_center()))
    sq.add(sq0)
    sq.remove(sq0, at=c0)

    def square_now(t):
        Mt = M(t)
        poly = unit_square(Mt)
        num = DecimalNumber(abs(float(np.linalg.det(Mt))), num_decimal_places=1, font_size=40)
        return VGroup(poly, num.next_to(poly.get_center(), DR, buff=0.12))
    held = sq.redraw(square_now, during=(c0, c1))
    sq.play(FadeOut(held), at=T.lost, dur=0.5)
    sq.remove(held, at=T.lost + 0.6)

    Cm = Mat(COLLAPSE, size=44, h_buff=0.85, v_buff=0.7)
    det = tex(r"\det", "=", "0", size=56, colors={2: C.null})
    stack = VGroup(Cm, det).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
    stack.move_to([-7.11 + C.margin + 0.35 + stack.width / 2, 3.55 - C.margin - stack.height / 2, 0])
    panel = backing(stack, pad=0.28)
    hb.add(panel)
    hud.play(FadeIn(Cm), at=T.cut_collapse + 0.1, dur=0.6)
    hud.play(FadeIn(det, shift=0.1 * UP), at=c1 + 0.1, dur=0.6)

    # ── something is lost: different points, one landing spot ──
    pts_in = [P0 + k * NULL for k in KS]
    land = pt(O5, U5, COLLAPSE @ P0)
    dots = [Dot(pt(O5, U5, p), radius=0.09, color=C.vec) for p in pts_in]
    g.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.12), at=T.lost + 1.6, dur=0.8)
    for i, d in enumerate(dots):
        g.play(d.animate.move_to(land), at=T.same_spot - 0.3 + 0.12 * i, dur=1.3, ease=E)
    g.play(Flash(land, color=C.null, line_length=0.22, flash_radius=0.3), at=T.cant_undo + 0.4, dur=0.7)
    g.play(FadeOut(VGroup(*dots)), at=T.crushed - 0.3, dur=0.5)

    # ── the null space: a whole line crushed into the origin ──
    o = pt(O5, U5, (0, 0))
    a_, b_ = pt(O5, U5, -2.3 * NULL), pt(O5, U5, 1.7 * NULL)
    nline = Line(a_, b_, color=C.null, stroke_width=C.stroke)
    g.play(Create(nline), at=T.crushed + 0.6, dur=0.8)
    nd = [Dot(pt(O5, U5, k * NULL), radius=0.08, color=C.null) for k in (-1.5, -1.0, -0.5, 0.5, 1.0, 1.5)]
    g.play(LaggedStart(*[FadeIn(d, scale=2) for d in nd], lag_ratio=0.08), at=T.crushed + 1.2, dur=0.6)
    for i, d in enumerate(nd):
        g.play(d.animate.move_to(o), at=T.crushed + 2.3 + 0.06 * i, dur=1.0, ease=E)
    lN = tex("N(A)", size=48, color=C.null).move_to(pt(O5, U5, -1.9 * NULL) + np.array([-0.75, 0, 0]))
    g.play(FadeIn(lN, shift=0.1 * UP), at=T.null + 0.3, dur=0.6)

    # ── the column space: everything that survives lands on one line ──
    d1 = COLLAPSE[:, 0] / np.linalg.norm(COLLAPSE[:, 0])
    cline = Line(pt(O5, U5, -3.0 * d1), pt(O5, U5, 9.5 * d1), color=C.grid, stroke_width=C.stroke + 2)
    m.play(Create(cline), at=T.survive + 0.9, dur=1.0)
    lC = tex("C(A)", size=48, color=C.grid).move_to(pt(O5, U5, 5.6 * d1) + np.array([-0.2, 0.55, 0]))
    g.play(FadeIn(lC, shift=0.1 * UP), at=T.colspace + 0.3, dur=0.6)

    # ── a shadow is this kind of move ──
    cam = Cam(AZ, EL, origin=CO, unit=CU)
    w3 = s.manim(z=1, opacity=in3)                     # floor, shadow
    r3 = s.manim(z=3, opacity=in3)                     # dots, labels
    ry = s.manim(z=1.5, opacity=in3)                   # rays (behind the die)
    floor = VGroup()
    for k in range(-4, 5):
        for ax in (0, 1):
            a, b = np.zeros(3), np.zeros(3)
            a[ax], b[ax] = -4, 4
            a[1 - ax] = b[1 - ax] = k
            a[2] = b[2] = ZF
            floor.add(Line(cam.scr(a), cam.scr(b), color=C.grid_minor, stroke_width=C.thin, stroke_opacity=0.8))
    w3.add(floor)
    corners = [DIE_C + 1.0 * np.array([x, y, z]) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    from scipy.spatial import ConvexHull
    sh = np.array([shadow(p) for p in corners])
    hull = ConvexHull(sh[:, :2])
    shade = Polygon(*[cam.scr(sh[i]) for i in hull.vertices], stroke_color=C.faint, stroke_width=1.5,
                    fill_color=C.ghost, fill_opacity=1.0)
    w3.play(FadeIn(shade), at=T.sunlight + 1.4, dur=1.0)

    sl = keys((T.rebuild + 0.4, 0.0), (T.rebuild + 2.2, 1.0, E), lead=0)
    s.add(FramesLayer(lambda t: die_rgba(I3 + sl(t) * (STRETCH - I3), az=AZ, el=EL, size=900, offset=DIE_C),
                      height=die_height(CU), pos=tuple(CO), z=2, opacity=in3, start=t2 + 0.5,
                      during=[(T.rebuild + 0.3, T.rebuild + 2.3)]))

    # rays of light: every point on a ray lands on one shadow point
    starts = [DIE_C + np.array(v) for v in ((-1, -1, 1), (1, -1, 1), (1, 1, 1),
                                            (-1, 1, 1))]
    rays = VGroup(*[Line(cam.scr(p - 2.6 * L), cam.scr(shadow(p)), color=C.null, stroke_width=2, stroke_opacity=0.75)
                    for p in starts])
    ry.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.15), at=T.sunlight + 0.2, dur=1.4)
    pr = starts[0]
    on_ray = [pr - s_ * L for s_ in (2.2, 1.2, 0.0)]
    spot = cam.scr(shadow(pr))
    rd = [Dot(cam.scr(p), radius=0.08, color=C.vec) for p in on_ray]
    r3.play(LaggedStart(*[FadeIn(d, scale=2) for d in rd], lag_ratio=0.15), at=T.ray + 0.6, dur=0.6)
    for i, d in enumerate(rd):
        r3.play(d.animate.move_to(spot), at=T.ray + 1.6 + 0.15 * i, dur=1.4, ease=E)
    r3.play(Flash(spot, color=C.vec, line_length=0.2, flash_radius=0.25), at=T.ray + 3.3, dur=0.6)

    # the light's direction is the null space
    la = np.array([-3.0, -3.2, 2.6])
    lb = la + 1.8 * L
    lArrow = arrow(cam.scr(la), cam.scr(lb), C.null, width=C.stroke)
    lN3 = tex("N(A)", size=48, color=C.null).next_to(lArrow, LEFT, buff=0.15)
    r3.play(GrowArrow(lArrow), FadeIn(lN3), at=T.light_null + 0.9, dur=0.7)
    finish(s)
