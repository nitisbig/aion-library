"""Ch2 · A machine that moves space (1/2): an arrow is a vector, read off by its tip (two over, one up). A machine
takes an arrow and hands back a different one; feed it every arrow at once and the whole grid moves. Most machines
would tangle the grid; the linear ones keep lines straight, evenly spaced, and the center fixed."""
from aion import *

from beats import T
from shots import (FRAME, GENTLE, I2, VEC, arrow, backdrop, backing, brackets, finish, grid_lines, live, pt, rail,
                   tangle, tex, warped_grid)

E = "smooth"
O, U = (-0.5, -0.6), 0.95
MC = np.array([4.9, 1.9, 0.0])                         # the machine
PTS = np.array([(x, y) for x in range(-8, 9) for y in range(-6, 7)], float)   # every grid point in view (and some)
INPUTS = [np.array([-1.0, 2.0]), np.array([1.0, -1.0]), np.array([3.0, 0.0])]


@scene(T.cut_ch2, T.cut_gallery)
def s04_machine(s):
    backdrop(s)
    ghost = s.manim(z=0)
    m = s.manim(z=1)
    g = s.manim(z=3)
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 1)
    z = pt(O, U, (0, 0))

    # ── a flat grid, drawn from the center outward ──
    t_g = T.grid + 0.1
    dim, major, axis = grid_lines(I2, O, U, FRAME)
    by_d = lambda grp: sorted(grp, key=lambda l: np.linalg.norm(l.get_center()[:2] - np.array(O)))  # noqa: E731
    m.play(Create(axis), at=t_g, dur=0.8)
    m.play(LaggedStart(*[FadeIn(l) for l in by_d(major)], lag_ratio=0.03), at=t_g + 0.3, dur=1.5)
    m.play(LaggedStart(*[FadeIn(l) for l in by_d(dim)], lag_ratio=0.02), at=t_g + 0.6, dur=1.5)
    base = VGroup(dim, major, axis)

    # ── an arrow from its center: two steps over, one step up ──
    v0 = arrow(z, pt(O, U, VEC), C.vec, width=C.stroke + 1)
    g.play(GrowArrow(v0), at=T.vector - 1.6, dur=0.8)
    gx = DashedLine(z, pt(O, U, (2, 0)), color=C.vec, stroke_width=C.thin + 0.5, dash_length=0.12)
    gy = DashedLine(pt(O, U, (2, 0)), pt(O, U, VEC), color=C.vec, stroke_width=C.thin + 0.5, dash_length=0.12)
    g.play(Create(gx), at=T.two_over + 0.1, dur=0.7)
    g.play(Create(gy), at=T.two_over + 1.5, dur=0.5)
    lab = tex("(2,", "1)", size=40, color=C.vec).next_to(pt(O, U, VEC), UR, buff=0.12)
    hud.play(FadeIn(lab, shift=0.1 * UP), at=T.two_over + 1.9, dur=0.5)
    g.play(FadeOut(gx), FadeOut(gy), at=T.machine - 0.2, dur=0.5)

    # ── the machine: arrow in, arrow out ──
    br = brackets(1.5, 1.3, width=C.stroke)
    mach = VGroup(backing(VGroup(br), pad=0.2), br).move_to(MC)
    hud.play(FadeIn(mach, scale=0.9), at=T.machine + 0.3, dur=0.7, ease="out_back")
    hud.play(FadeOut(lab), at=T.machine + 0.3, dur=0.4)
    small = lambda: arrow(MC + np.array([-0.35, -0.2, 0]), MC + np.array([0.35, 0.2, 0]), C.vec)  # noqa: E731

    def through(v_in, t, slow=1.0, mob_in=None):
        """Send the input arrow through the machine; return (input mob, output mob)."""
        a_in = mob_in or arrow(z, pt(O, U, v_in), C.vec, width=C.stroke + 1)
        a_out = arrow(z, pt(O, U, GENTLE @ v_in), C.vec, width=C.stroke + 1)
        mid = small()
        if mob_in is None:
            g.play(GrowArrow(a_in), at=t - 0.45 * slow, dur=0.4 * slow)
        g.play(TransformFromCopy(a_in, mid), at=t, dur=0.6 * slow, ease=E)
        g.play(a_in.animate.set_opacity(0.3), at=t + 0.2 * slow, dur=0.4 * slow)
        g.play(ReplacementTransform(mid, a_out), at=t + 0.75 * slow, dur=0.7 * slow, ease=E)
        return a_in, a_out
    pairs = [through(VEC, T.machine + 2.4, slow=1.2, mob_in=v0)]
    for k, v in enumerate(INPUTS):
        pairs.append(through(v, T.arrow_in + 0.3 + 0.75 * k, slow=0.75))
    g.play(*[FadeOut(VGroup(*p)) for p in pairs], at=T.all_at_once - 1.0, dur=0.6)
    hud.play(FadeOut(mach), at=T.all_at_once - 1.0, dur=0.6)

    # ── every arrow at once: the whole grid moves ──
    M = keys((T.slides + 0.1, I2), (T.slides + 2.4, GENTLE, E), (T.straight - 1.0, GENTLE), (T.straight - 0.1, I2, E),
             (T.straight + 0.2, I2), (T.straight + 1.8, GENTLE, E), (T.linear + 0.4, GENTLE),
             (T.linear + 1.3, I2, E), lead=0)
    w = keys((T.tangle - 0.2, 0.0), (T.tangle + 0.9, 1.0, E), (T.tangle + 1.5, 1.0), (T.tangle + 2.5, 0.0, E), lead=0)
    d_op = keys((T.all_at_once + 0.2, 0.0), (T.all_at_once + 1.0, 1.0), (T.cut_gallery - 0.8, 1.0),
                (T.cut_gallery - 0.1, 0.0), lead=0)
    s.add(PointsLayer(lambda t: np.array(O) + U * tangle(M(t), w(t), PTS), color=C.vec, size=6.0, glow=0.0,
                      additive=False, z=2, opacity=d_op))

    def stage(t):
        Mt, wt = M(t), w(t)
        return warped_grid(Mt, wt, O, U) if wt > 1e-3 else grid_lines(Mt, O, U, FRAME)
    m.remove(base, at=T.slides + 0.1)
    m.add(grid_lines(I2, O, U, FRAME), at=T.slides + 0.1)   # (live() replaces it during each window)
    wins = [(T.slides + 0.1, T.slides + 2.4), (T.tangle - 0.2, T.tangle + 2.5), (T.straight - 1.0, T.straight + 1.8),
            (T.linear + 0.4, T.linear + 1.3)]
    live(m, stage, *wins)
    ghost.add(grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False), at=T.slides + 0.1)

    # ── three rules: straight lines stay straight, evenly spaced stays even, the center stays put ──
    hl_op = keys((T.straight - 0.2, 0.0), (T.straight + 0.2, 1.0), (T.center - 0.3, 1.0), (T.center + 0.2, 0.35),
                 (T.linear - 0.2, 0.35), (T.linear + 0.3, 0.0), lead=0)
    s_l = np.linspace(-10, 10, 2)

    def rule_line(t):
        o_ = hl_op(t)
        if o_ < 0.01:
            return VGroup()
        q = [pt(O, U, M(t) @ np.array([1.0, y])) for y in s_l]
        return Line(q[0], q[1], color=C.text, stroke_width=C.stroke + 1.5, stroke_opacity=o_)
    hl = s.manim(z=2.5)
    hl.redraw(rule_line, during=(T.straight - 0.2, T.linear + 0.3))
    ev = np.array([(1.0, y) for y in range(-6, 7)])
    ev_op = keys((T.even - 0.1, 0.0), (T.even + 0.4, 1.0), (T.center - 0.3, 1.0), (T.center + 0.2, 0.0), lead=0)
    s.add(PointsLayer(lambda t: np.array(O) + U * (ev @ M(t).T), color=C.vec, size=13.0, glow=0.0, additive=False,
                      z=2.6, opacity=ev_op))
    od = Dot(z, radius=0.11, color=C.text)
    ring = Circle(radius=0.14, color=C.text, stroke_width=C.stroke).move_to(z)
    g.play(FadeIn(od, scale=0.5), at=T.center + 0.1, dur=0.4, ease="out_back")
    g.play(ring.animate.scale(4.0).set_stroke(opacity=0), at=T.center + 0.3, dur=0.9)
    g.play(FadeOut(od), at=T.linear + 0.2, dur=0.5)
    finish(s)
