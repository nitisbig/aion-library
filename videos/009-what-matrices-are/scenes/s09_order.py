"""Ch4 · Does the order matter? RS acts S first (like f(g(x))). Predict, then RS and SR side by side land differently,
and a real die agrees: forward-then-side shows 4 on top, side-then-forward shows 2."""
from aion import *

from beats import T
from shots import (I2, QUARTER, SHEAR, Cam, arrow, backdrop, die_height, die_rgba, finish, grid_lines, panel, pt, rail,
                   rot2, rot3, tex, top_face)

E = "smooth"
V = np.array([1.0, 1.0])                               # one yellow arrow per side
PANELS = ((-6.85, -3.75, -0.2, 1.75), (0.2, -3.75, 6.85, 1.75))
OS = [(-3.5, -1.55), (3.55, -1.55)]
U = 0.68


@scene(T.cut_order, T.cut_layers)
def s09_order(s):
    backdrop(s)
    m = s.manim(z=1, opacity=keys((T.real - 0.15, 1.0), (T.real + 0.45, 0.0), lead=0))   # the two framed grids
    g = s.manim(z=3)                                   # arrows, top-face outlines
    hud = s.manim(z=5, parallax=0.0)
    rail(hud, 3)

    # ── RS: written R on the left because R acts second, like f(g(x)) ──
    R_, S_ = tex("R", size=96), tex("S", size=96)
    head = VGroup(R_, S_).arrange(RIGHT, buff=0.12).move_to([0, 1.6, 0])
    flow = Arrow(S_.get_bottom() + DOWN * 0.25 + RIGHT * 0.2, R_.get_bottom() + DOWN * 0.25 + LEFT * 0.2, buff=0,
                 color=C.muted, stroke_width=3, tip_length=0.2)
    fgx = tex("f", "(", "g", "(x))", size=56, color=C.muted).next_to(flow, DOWN, buff=0.4)
    hud.play(FadeIn(head, shift=0.15 * UP), at=T.left_side + 0.1, dur=0.7)
    hud.play(Indicate(R_, color=C.text, scale_factor=1.15), at=T.left_side + 1.2, dur=0.8)
    hud.play(GrowArrow(flow), at=T.left_side + 1.9, dur=0.8)
    hud.play(FadeIn(fgx, shift=0.1 * UP), at=T.fgx, dur=0.7)

    # ── does the order matter? RS on the left, SR on the right ──
    tq = T.order_q + 0.1
    lRS = tex("R", "S", size=64).move_to([-3.5, 2.55, 0])
    lSR = tex("S", "R", size=64).move_to([3.55, 2.55, 0])
    hud.play(FadeOut(VGroup(flow, fgx)), at=tq, dur=0.5)
    hud.play(ReplacementTransform(head, lRS), at=tq + 0.2, dur=0.9, ease=E)
    hud.play(FadeIn(lSR, shift=0.2 * LEFT), at=tq + 0.6, dur=0.7)

    first = [SHEAR, QUARTER]                           # left acts S first, right acts R first
    second = [QUARTER, SHEAR]
    s0, s1 = T.dont, T.dont + 1.3                      # step one (lands on "You don't")
    r0, r1 = T.dont + 1.45, T.dont + 2.75              # step two (lands on "different places")
    u = keys((s0, 0.0), (s1, 1.0, E), lead=0)
    w = keys((r0, 0.0), (r1, 1.0, E), lead=0)

    def move(side, t):
        """Moves as moves: the turn by angle, the shear linearly."""
        def part(Mx, k):
            return rot2(90 * k) if Mx is QUARTER else I2 + k * (SHEAR - I2)
        return part(second[side], w(t)) @ part(first[side], u(t))

    def board(side, t):
        x0, y0, x1, y1 = PANELS[side]
        o = OS[side]
        Mt = move(side, t)
        box = (x0 + 0.02, y0 + 0.02, x1 - 0.02, y1 - 0.02)
        return VGroup(grid_lines(Mt, o, U, box, n=12),
                      arrow(pt(o, U, (0, 0)), pt(o, U, Mt[:, 0]), C.ihat, width=C.stroke),
                      arrow(pt(o, U, (0, 0)), pt(o, U, Mt[:, 1]), C.jhat, width=C.stroke),
                      arrow(pt(o, U, (0, 0)), pt(o, U, Mt @ V), C.vec, width=C.stroke + 1))
    frames = VGroup(*[panel(*p).set_fill(opacity=0) for p in PANELS])
    ghosts = VGroup(*[grid_lines(I2, OS[k], U, PANELS[k], n=12, color=C.ghost, axes=False) for k in (0, 1)])
    m.play(FadeIn(frames), at=tq + 0.4, dur=0.6)
    b0 = [board(0, s0), board(1, s0)]
    m.play(FadeIn(b0[0]), FadeIn(b0[1]), at=tq + 0.7, dur=0.8)
    m.add(ghosts, at=s0)
    m.remove(*b0, at=s0)
    m.redraw(lambda t: VGroup(board(0, t), board(1, t)), during=(s0, r1))
    neq_top = tex(r"\neq", size=72).move_to([0.0, 2.55, 0])
    hud.play(FadeIn(neq_top), at=T.grids_differ + 1.3, dur=0.6)
    hud.play(FadeOut(VGroup(neq_top, lRS, lSR)), at=T.real - 0.15, dur=0.6)

    # ── real objects agree: two dice, same start (1 up, 5 toward us, 3 right) ──
    DU, AZ, EL = 1.3, -35.0, 24.0
    DC = [np.array([-3.5, -0.75]), np.array([3.55, -0.75])]
    f1 = keys((T.forward + 0.1, 0.0), (T.forward + 1.3, 1.0, E), lead=0)        # left: forward (x) ...
    f2 = keys((T.side - 0.05, 0.0), (T.side + 1.1, 1.0, E), lead=0)             # ... then to the side (y)
    g1 = keys((T.other_order - 0.2, 0.0), (T.other_order + 0.95, 1.0, E), lead=0)   # right: side (y) ...
    g2 = keys((T.top_face - 0.1, 0.0), (T.top_face + 1.05, 1.0, E), lead=0)        # ... then forward (x)

    def pose(side, t):
        if side == 0:
            return rot3(1, 90 * f2(t)) @ rot3(0, 90 * f1(t))
        return rot3(0, 90 * g2(t)) @ rot3(1, 90 * g1(t))
    wins = [(T.forward - 0.1, T.side + 1.2), (T.other_order - 0.3, T.top_face + 1.1)]
    t_die = T.real + 0.3
    for side in (0, 1):
        s.add(FramesLayer(lambda t, side=side: die_rgba(pose(side, t), az=AZ, el=EL, size=900),
                          height=die_height(DU), pos=tuple(DC[side]), z=2, start=T.real - 0.1,
                          opacity=fade(t_die, dur=0.7, out=T.cut_layers - 0.05, out_dur=0.6),
                          during=[wins[side]]))

    # top faces outlined once both have landed; their pips read 4 and 2
    def top_outline(side):
        cam = Cam(AZ, EL, origin=DC[side], unit=DU)
        sq = [(-0.78, -0.78), (0.78, -0.78), (0.78, 0.78), (-0.78, 0.78)]
        return Polygon(*[cam.scr((x, y, 1.0)) for x, y in sq], stroke_color=C.area, stroke_width=3.5, fill_opacity=0)
    tops = VGroup(top_outline(0), top_outline(1))
    assert top_face(pose(0, 1e9)) == 4 and top_face(pose(1, 1e9)) == 2
    g.play(Create(tops), at=T.top_face + 1.25, dur=0.7)
    labels = VGroup(tex("R_y", "R_x", size=52).move_to([-3.5, -3.3, 0]), tex("R_x", "R_y", size=52).move_to([3.55, -3.3, 0]))
    neq = tex(r"\neq", size=60).move_to([0.0, -3.3, 0])
    hud.play(FadeIn(labels[0]), at=T.side + 1.3, dur=0.6)
    hud.play(FadeIn(labels[1]), at=T.top_face + 1.25, dur=0.6)
    hud.play(FadeIn(neq, scale=1.4), at=T.part_of + 0.3, dur=0.6, ease="out_back")
    g.play(FadeOut(tops), at=T.cut_layers - 0.05, dur=0.6)
    hud.play(FadeOut(VGroup(labels, neq)), at=T.cut_layers - 0.05, dur=0.6)
    finish(s)
