"""Ch6 · The directions that don't turn (1/3): one arrow sweeps the circle under the hero A; its output is knocked off
its line except along (1, 1) (×4) and (1, −2) (×1). Av = λv. Predict: a plane rotation keeps no direction; a turn
in space always has an axis: the die's two quarter turns are one 120° turn about (1, 1, 1), eigenvalue 1."""
from aion import *

from beats import T
from shots import (A, FRAME, I2, I3, Cam, Mat, arrow, backdrop, backing, die_height, die_rgba, finish, grid_lines, live,
                   pt, rail, rot2, rot3, tex)

E = "smooth"
O, U = (1.6, -0.5), 0.6
R = 1.5                                                # the input arrow's length
ROT = rot2(60)                                         # the test rotation
E1, E2 = np.array([1.0, 1.0]) / np.sqrt(2), np.array([1.0, -2.0]) / np.sqrt(5)
TH1, TH2 = 45.0, float(np.degrees(np.arctan2(-2, 1)))  # the two eigen-directions (45°, −63.4°)
N = np.ones(3) / np.sqrt(3)                            # the die's turn axis
P = rot3(0, 90) @ rot3(1, 90)                          # y then x (s09): [[0,0,1],[1,0,0],[0,1,0]]


def turn(axis, deg):
    """Rotation by `deg` about the unit vector `axis` (Rodrigues)."""
    a = np.radians(deg)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return I3 + np.sin(a) * K + (1 - np.cos(a)) * K @ K


def full_line(d, color, op, width=None):
    d = np.asarray(d, float) / np.linalg.norm(d)
    return Line(pt(O, U, -24 * d), pt(O, U, 24 * d), color=color, stroke_width=width or C.thin + 0.5, stroke_opacity=op)


@scene(T.cut_ch6, T.cut_power)
def s14_eigen(s):
    backdrop(s)
    t3 = T.in_3d + 0.1
    out2 = keys((t3, 1.0), (t3 + 0.7, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=out2)
    m = s.manim(z=1, opacity=out2)
    g = s.manim(z=3, opacity=out2)
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    rail(hud, 5)

    ghost.play(FadeIn(grid_lines(I2, O, U, FRAME, color=C.ghost)), at=T.cut_ch6 + 0.2, dur=0.8)
    circle = Circle(radius=R * U, color=C.faint, stroke_width=C.thin).move_to(pt(O, U, (0, 0)))
    ghost.play(Create(circle), at=T.single - 0.4, dur=0.8)

    # ── the panel ──
    Am = Mat(A, size=44, h_buff=0.85, v_buff=0.7)
    rowA = VGroup(tex("A", "=", size=48), Am).arrange(RIGHT, buff=0.2)
    eq = tex("A", r"\mathbf{v}", "=", r"\lambda", r"\mathbf{v}", size=56, colors={1: C.eigen, 3: C.eigen, 4: C.eigen})
    stack = VGroup(rowA, eq).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    stack.move_to([-7.11 + C.margin + 0.35 + stack.width / 2, 3.55 - C.margin - stack.height / 2, 0])
    panel = backing(stack, pad=0.28)
    p_op = keys((T.cut_ch6 + 0.2, 0.0), (T.cut_ch6 + 0.8, 1.0), (T.test - 0.2, 1.0), (T.test + 0.3, 0.0), lead=0)
    hb.play(FadeIn(panel), at=T.cut_ch6 + 0.3, dur=0.5)
    hud.play(FadeIn(rowA), at=T.cut_ch6 + 0.4, dur=0.6)
    hud.play(FadeIn(eq[:3]), at=T.eigenvectors + 0.2, dur=0.5)
    hud.play(FadeIn(eq[3:], shift=0.1 * LEFT), at=T.eigenvalue + 0.1, dur=0.6)

    # ── one arrow and where it lands, swept around the circle ──
    th = keys((T.single, 110.0), (T.knocked + 0.6, 110.0), (T.knocked + 2.6, 160.0, E), (T.sweep + 0.1, 160.0),
              (T.lines_up + 0.2, TH1, E), (T.another - 0.5, TH1), (T.not_stretched - 0.1, TH2, E), (T.eigenvectors + 2.1, TH2),
              (T.rotation_q, 20.0), (T.none + 0.1, 20.0), (T.none + 2.5, 380.0, E), lead=0)
    a_op = keys((T.single + 0.1, 0.0), (T.single + 0.6, 1.0), (T.eigenvectors + 1.4, 1.0), (T.eigenvectors + 2.0, 0.0),
                (T.rotation_q - 0.3, 0.0), (T.rotation_q + 0.3, 1.0), lead=0)

    def mover(t):
        return A if t < T.test else ROT

    def pair(t):
        o = a_op(t)
        if o < 0.01:
            return VGroup()
        a = np.radians(th(t))
        v = R * np.array([np.cos(a), np.sin(a)])
        w = mover(t) @ v
        z = pt(O, U, (0, 0))
        return VGroup(full_line(v, C.text, 0.28 * o), full_line(w, C.vec, 0.4 * o),
                      arrow(z, pt(O, U, v), C.text, width=C.stroke, opacity=o),
                      arrow(z, pt(O, U, w), C.vec, width=C.stroke + 1, opacity=o))
    wins = [(T.single, T.knocked + 2.7), (T.sweep, T.lines_up + 0.3), (T.another - 0.6, T.not_stretched),
            (T.eigenvectors + 1.3, T.eigenvectors + 2.1), (T.rotation_q - 0.4, T.rotation_q + 0.4),
            (T.none, T.none + 2.6)]
    live(g, pair, *wins)

    # the two directions that stay on their line: violet, tagged with their stretch
    l1, l2 = full_line(E1, C.eigen, 0.9, C.stroke), full_line(E2, C.eigen, 0.9, C.stroke)
    m.play(Create(l1), at=T.lines_up + 0.5, dur=0.8)
    m.play(Create(l2), at=T.not_stretched + 0.2, dur=0.8)
    lam4 = tex(r"\lambda", "=", "4", size=44, color=C.eigen).move_to(pt(O, U, 3.0 * E1) + np.array([0.95, -0.15, 0]))
    lam1 = tex(r"\lambda", "=", "1", size=44, color=C.eigen).move_to(pt(O, U, 2.6 * E2) + np.array([0.95, 0.0, 0]))
    m.play(FadeIn(lam4, scale=1.3), at=T.four_x + 0.6, dur=0.5, ease="out_back")
    m.play(FadeIn(lam1, scale=1.3), at=T.not_stretched + 0.9, dur=0.5, ease="out_back")
    g.play(Flash(pt(O, U, R * E2), color=C.eigen, line_length=0.18, flash_radius=0.28), at=T.not_stretched + 0.6,
           dur=0.6)

    # ── the skeleton: the whole grid moves, the violet lines stay put ──
    k0, k1 = T.skeleton + 1.4, T.skeleton + 3.4
    r0, r1 = T.test - 1.6, T.test - 0.3
    u = keys((k0, 0.0), (k1, 1.0, E), (r0, 1.0), (r1, 0.0, E), lead=0)

    def M(t):
        return I2 + u(t) * (A - I2)
    grid_op = keys((k0 - 0.6, 0.0), (k0, 1.0), (r1, 1.0), (r1 + 0.4, 0.0), lead=0)

    def skel(t):
        o = grid_op(t)
        if o < 0.01:
            return VGroup()
        Mt = M(t)
        z = pt(O, U, (0, 0))
        return VGroup(grid_lines(Mt, O, U, FRAME, opacity=0.55 * o),
                      arrow(z, pt(O, U, Mt @ (R * E1)), C.eigen, width=C.stroke + 1, opacity=o),
                      arrow(z, pt(O, U, Mt @ (R * E2)), C.eigen, width=C.stroke + 1, opacity=o))
    skw = m.redraw(skel, during=(k0 - 0.6, r1 + 0.4))

    # ── a quick test: a rotation of the plane. Which arrows stay on their line? None. ──
    m.play(FadeOut(VGroup(l1, l2, lam4, lam1)), at=T.test - 0.3, dur=0.5)
    Rm = Mat([[r"\cos\theta", r"-\sin\theta"], [r"\sin\theta", r"\cos\theta"]], size=40, h_buff=1.3, v_buff=0.7)
    rot_rot = VGroup(tex("R", "=", size=48), Rm).arrange(RIGHT, buff=0.2)
    rot_rot.move_to(rowA, aligned_edge=LEFT)
    hud.play(FadeOut(VGroup(rowA, eq)), at=T.test - 0.2, dur=0.4)
    hb.play(Transform(panel, backing(rot_rot, pad=0.28)), at=T.test, dur=0.5)
    hud.play(FadeIn(rot_rot), at=T.test + 0.3, dur=0.6)
    turn_u = keys((T.test + 0.8, 0.0), (T.test + 2.6, 1.0, E), lead=0)
    rg_op = keys((T.test + 0.6, 0.0), (T.test + 0.9, 1.0), (T.rotation_q - 0.4, 1.0), (T.rotation_q + 0.2, 0.0), lead=0)
    m.redraw(lambda t: grid_lines(rot2(60 * turn_u(t)), O, U, FRAME, opacity=0.55 * rg_op(t))
             if rg_op(t) > 0.01 else VGroup(), during=(T.test + 0.6, T.rotation_q + 0.2))
    qm = tex("?", size=72, color=C.vec).move_to(pt(O, U, (2.6, 2.4)))
    g.play(FadeIn(qm, scale=1.4), at=T.rotation_q + 1.6, dur=0.5, ease="out_back")
    g.play(FadeOut(qm), at=T.none - 0.2, dur=0.3)

    # ── in 3D it's different: the die's two quarter turns are one turn about a tilted axis ──
    hud.play(FadeOut(rot_rot), at=t3, dur=0.5)
    hb.play(FadeOut(panel), at=t3, dur=0.5)
    cam = Cam(-35.0, 22.0, origin=(1.4, -0.4), unit=1.15)
    g1 = keys((T.remember_die + 0.7, 0.0), (T.remember_die + 1.6, 1.0, E), lead=0)
    g2 = keys((T.remember_die + 1.8, 0.0), (T.remember_die + 2.7, 1.0, E), lead=0)
    reset = T.combine - 0.2
    h = keys((T.combine + 0.9, 0.0), (T.axis - 0.1, 1.0, E), (T.axis + 0.6, 1.0), (T.every_rotation - 0.1, 2.0, E),
             lead=0)

    def pose(t):
        if t < reset:
            return rot3(0, 90 * g2(t)) @ rot3(1, 90 * g1(t))
        return turn(N, 120 * h(t))
    d_op = keys((t3 + 0.4, 0.0), (t3 + 1.2, 1.0), (reset - 0.35, 1.0), (reset, 0.0), (reset + 0.05, 0.0),
                (reset + 0.45, 1.0), (T.cut_power - 0.7, 1.0), (T.cut_power - 0.05, 0.0), lead=0)
    s.add(FramesLayer(lambda t: die_rgba(pose(t), az=-35.0, el=22.0, size=900), height=die_height(1.15),
                      pos=(1.4, -0.4), z=2, opacity=d_op, start=t3,
                      during=[(T.remember_die + 0.6, T.remember_die + 2.8), (reset - 0.01, reset + 0.01),
                              (T.combine + 0.8, T.every_rotation)]))
    assert np.allclose(turn(N, 120), P)

    # the axis through two opposite corners: the near half over the die, the far half behind it
    end3 = keys((T.cut_power - 0.7, 1.0), (T.cut_power - 0.05, 0.0), lead=0)
    back = s.manim(z=1.5, opacity=end3)
    front = s.manim(z=3, opacity=end3)
    c3 = np.sqrt(3)
    near = 1 if cam.depth(N) < cam.depth(-N) else -1
    seg_f = Line(cam.scr(near * c3 * N), cam.scr(near * 3.4 * N), color=C.eigen, stroke_width=C.stroke + 1)
    seg_b = Line(cam.scr(-near * c3 * N), cam.scr(-near * 3.4 * N), color=C.eigen, stroke_width=C.stroke + 1)
    front.play(Create(seg_f), at=T.combine + 1.6, dur=0.8)
    back.play(Create(seg_b), at=T.combine + 1.6, dur=0.8)
    cdot = Dot(cam.scr(near * c3 * N), radius=0.09, color=C.eigen)
    front.play(FadeIn(cdot, scale=2), at=T.axis + 0.6, dur=0.4)
    tip = Dot(cam.scr(near * 3.0 * N), radius=0.09, color=C.eigen)
    front.play(FadeIn(tip, scale=2), at=T.axis + 0.8, dur=0.4)

    Pm = Mat(P.astype(int), size=40, h_buff=0.7, v_buff=0.55)
    rowP = VGroup(tex("R_x", "R_y", "=", size=44), Pm).arrange(RIGHT, buff=0.2)
    rowP.move_to([-7.11 + C.margin + 0.35 + rowP.width / 2, 3.55 - C.margin - rowP.height / 2, 0])
    lam = tex(r"\lambda", "=", "1", size=48, color=C.eigen).next_to(cam.scr(near * 3.4 * N), RIGHT, buff=0.2)
    hb3 = s.manim(z=4.9, parallax=0.0, opacity=end3)
    hud3 = s.manim(z=5, parallax=0.0, opacity=end3)
    hb3.play(FadeIn(backing(rowP, pad=0.28)), at=T.combine - 0.1, dur=0.5)
    hud3.play(FadeIn(rowP), at=T.combine, dur=0.6)
    front.play(FadeIn(lam, scale=1.3), at=T.axis_eigen + 1.4, dur=0.5, ease="out_back")
    finish(s)
