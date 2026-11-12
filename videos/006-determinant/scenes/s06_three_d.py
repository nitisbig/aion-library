"""Ch6 · Three dimensions: three arrows, a unit cube carried into a slanted box, volume 6; the sign still means a
flip (the R on its base turns into its mirror image); zero still means collapse, onto a plane.

The 3D view is drawn as crisp vector lines through a hand-made orthographic camera (azimuth + elevation), so it
matches the 2D chapters' look exactly.
"""
from aion import *

from beats import T
from shots import (I2, Mat, _clip, backdrop, backing, finish, grid_lines, live, num, panel, pt, rail, strike, tex,
                   words)

E = "easy_ease"
O3, U3 = np.array([0.6, -1.1]), 0.9                  # where the 3D origin sits on screen, units per grid step
C1, C2, C3 = np.array([2.0, 0, 0]), np.array([1.0, 1, 0]), np.array([-1.0, 1, 3])  # det = 2 * 1 * 3 = 6
I3 = np.eye(3)
A3 = np.column_stack([C1, C2, C3])
A3n = np.column_stack([-C1, C2, C3])                 # i-hat reversed: det -6
A30 = np.column_stack([-C1, C2, [-1.0, 1, 0]])        # k-hat pressed into the floor: det 0
CUBE = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
FACES = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]   # z=0 is face 4


def ramp(t, a, b):
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


class Cam:
    """Orthographic view: turn the world by azimuth `az` about z, then tip it so we look down at elevation `el`."""

    def __init__(self, az, el):
        a, e = np.radians(az), np.radians(el)
        self.R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        self.ce, self.se = np.cos(e), np.sin(e)

    def scr(self, p):
        q = self.R @ np.asarray(p, float)
        return np.array([O3[0] + U3 * q[0], O3[1] + U3 * (q[2] * self.ce + q[1] * self.se), 0.0])

    def depth(self, p):
        q = self.R @ np.asarray(p, float)
        return q[1] * self.ce - q[2] * self.se       # larger is farther away


def det3(M):
    return float(np.linalg.det(M))


@scene(T.cut_ch6, T.cut_ch7)
def s06_three_d(s):
    backdrop(s)
    old = s.manim(z=0.5)                              # Ch5's two systems, cleared at the start
    w = s.manim(z=1)                                  # the whole 3D view, redrawn while anything moves
    hb = s.manim(z=5.5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 6)
    t0 = T.cut_ch6

    # ── one score for the camera and the matrix ──
    tilt = (T.three_d - 0.3, T.three_d + 1.9)
    end = (T.no_back - 0.6, T.cut_ch7 - 0.15)        # back to looking straight down, for Ch7
    az = keys((t0, 0.0), (tilt[0], 0.0), (tilt[1], -28.0, E), (end[0], 34.0, "linear"), (end[1], 0.0, E), lead=0)
    el = keys((t0, 90.0), (tilt[0], 90.0), (tilt[1], 58.0, E), (end[0], 58.0), (end[1], 90.0, E), lead=0)
    grow = (T.box - 0.2, T.box + 1.6)
    flip = (T.sign3 + 0.4, T.sign3 + 2.6)
    press = (T.collapse3 + 0.3, T.collapse3 + 2.8)
    M = keys((t0, I3), (grow[0], I3), (grow[1], A3, E), (flip[0], A3), (flip[1], A3n, E), (press[0], A3n),
             (press[1], A30, E), lead=0)

    floor_on = (t0 + 0.6, t0 + 1.4)
    arrows_on = [(T.three_arrows - 0.2 + 0.35 * k, T.three_arrows + 0.4 + 0.35 * k) for k in range(3)]
    cube_on = (T.cube, T.cube + 0.8)
    pulse_v = (T.volume + 0.2, T.volume + 1.2)
    pulse_p = (T.plane, T.plane + 1.6)

    R_glyph = tex("R", size=200)
    rx0, ry0 = R_glyph.get_corner(DL)[:2]
    rw, rh = R_glyph.width, R_glyph.height

    def view(t):
        cam, A = Cam(az(t), el(t)), M(t)
        d = det3(A)
        out = VGroup()
        # the floor: a fixed reference grid in the plane z = 0, axes in white
        kf = ramp(t, *floor_on)
        for k in range(-9, 10):
            for a_, b_ in (((k, -9, 0), (k, 9, 0)), ((-9, k, 0), (9, k, 0))):
                axis = k == 0
                out.add(Line(cam.scr(a_), cam.scr(b_), color=C.axis if axis else C.grid,
                             stroke_width=C.thin * (1.5 if axis else 1.0), stroke_opacity=kf * (1.0 if axis else 0.55)))
        kz = ramp(t, *tilt)
        if kz > 0:
            out.add(Line(cam.scr((0, 0, 0)), cam.scr((0, 0, 4.2)), color=C.axis, stroke_width=C.thin * 1.5,
                         stroke_opacity=kz))
        # the collapsed plane, lit red while it is named
        kp = ramp(t, pulse_p[0], pulse_p[0] + 0.4) * (1 - ramp(t, pulse_p[1] - 0.5, pulse_p[1]))
        if kp > 0:
            out.add(Polygon(*[cam.scr(c) for c in ((-9, -9, 0), (9, -9, 0), (9, 9, 0), (-9, 9, 0))], stroke_width=0,
                            fill_color=C.collapse, fill_opacity=0.18 * kp))
        # the box: faces drawn far to near
        kc = ramp(t, *cube_on)
        if kc > 0:
            col = C.area if d > 0.05 else C.flip if d < -0.05 else C.collapse
            fill = 0.22 + 0.2 * ramp(t, pulse_v[0], pulse_v[0] + 0.3) * (1 - ramp(t, pulse_v[1] - 0.5, pulse_v[1]))
            corners = [A @ c for c in CUBE]
            faces = sorted(FACES, key=lambda f: -np.mean([cam.depth(corners[i]) for i in f]))
            for f in faces:
                out.add(Polygon(*[cam.scr(corners[i]) for i in f], stroke_color=col, stroke_width=C.thin + 0.6,
                                stroke_opacity=kc, fill_color=col, fill_opacity=fill * kc))
            # the R on the base: drawn in the base's own coordinates, so it is carried (and mirrored) with it
            c1, c2 = A[:, 0], A[:, 1]

            def onto(p):
                u = 0.2 + 0.6 * (p[0] - rx0) / rw
                v = 0.15 + 0.7 * (p[1] - ry0) / rh
                return cam.scr(u * c1 + v * c2)
            out.add(R_glyph.copy().apply_function(onto).set_fill(C.text, opacity=kc).set_stroke(width=0))
        # the three arrows, always on top
        for k, colr in enumerate((C.ihat, C.jhat, C.khat)):
            ka = ramp(t, *arrows_on[k])
            if ka <= 0:
                continue
            a_, b_ = cam.scr((0, 0, 0)), cam.scr(A[:, k] * ka)
            L = np.linalg.norm(b_ - a_)
            if L < 1e-3:
                continue
            out.add(Arrow(a_, b_, buff=0, color=colr, stroke_width=C.stroke + 1, tip_length=min(0.24, 0.4 * L),
                          max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40))
        return out
    moving = (floor_on, tilt, *arrows_on, cube_on, grow, pulse_v, flip, press, pulse_p, (tilt[1], end[1]))
    live(w, view, *moving)

    # ── Ch5's last frame: the two systems, cleared ──
    def system(box, eqs, cols, head):
        x0, y0, x1, y1 = box
        rows = VGroup(*[tex(*e, size=40, color=c) for e, c in zip(eqs, cols)]).arrange(DOWN, aligned_edge=LEFT,
                                                                                      buff=0.22)
        rows.move_to([x0 + 0.35 + rows.width / 2, y1 - 0.3 - rows.height / 2, 0])
        hd = tex(*head, size=48).move_to([x1 - 0.4, rows.get_y(), 0], aligned_edge=RIGHT)
        gbox = (x0 + 0.03, y0 + 0.03, x1 - 0.03, rows.get_bottom()[1] - 0.25)
        O, U = np.array([x0 + 1.3, y0 + 1.0]), 0.62
        return VGroup(panel(*box), grid_lines(I2, O, U, gbox, n=12, color=C.grid_minor), rows, hd), gbox, O, U, hd

    def eq_line(a_, b_, c_, O, U, box, col, wd=None):
        n = np.array([a_, b_], float)
        sg = _clip(O + U * (n * c_ / n.dot(n)), U * np.array([-b_, a_], float), box)
        return Line([*sg[0], 0], [*sg[1], 0], color=col, stroke_width=wd or C.stroke)
    boxL, boxR = (-6.85, -3.35, -0.15, 3.35), (0.15, -3.35, 6.85, 3.35)
    gL_, gl_, OL, UL, hL = system(boxL, ((r"x + y = 3",), (r"x - y = 1",)), (C.khat, C.area), (r"\det", r"\neq", "0"))
    gR_, gr_, OR, UR_, hR = system(boxR, ((r"x + 2y = 2",), (r"2x + 4y = ", "4")), (C.khat, C.area), (r"\det", "=", "0"))
    hR[2].set_color(C.collapse)
    leftovers = VGroup(gL_, gR_, eq_line(1, 1, 3, OL, UL, gl_, C.khat), eq_line(1, -1, 1, OL, UL, gl_, C.area),
                       Dot(pt(OL, UL, (2, 1)), radius=0.1, color=C.text), eq_line(1, 2, 2, OR, UR_, gr_, C.khat),
                       eq_line(1, 2, 2, OR, UR_, gr_, C.area, C.stroke * 0.45),
                       tex(r"\infty", size=56, color=C.collapse).move_to([boxR[2] - 0.7, -2.6, 0]))
    old.add(leftovers)
    old.play(FadeOut(leftovers), at=t0 + 0.1, dur=0.8, lead=0)

    # ── "only one word changes": area → volume ──
    w_area = words("area", size=60, color=C.muted).move_to([4.3, 2.9, 0])
    w_vol = words("volume", size=60, color=C.area).move_to([4.3, 2.9, 0])
    x_area = strike(w_area, color=C.collapse).set_stroke(width=C.stroke)
    hud.play(FadeIn(w_area, shift=0.1 * DOWN), at=T.one_word, dur=0.5)
    hud.play(Create(x_area), at=T.one_word + 0.6, dur=0.4)
    hud.play(FadeOut(VGroup(w_area, x_area), shift=0.3 * UP), FadeIn(w_vol, shift=0.3 * UP), at=T.one_word + 1.3,
             dur=0.7)
    hud.play(FadeOut(w_vol), at=T.sign3 - 0.6, dur=0.6, lead=0)

    # ── the HUD: the three-by-three matrix, its hats, and a live readout ──
    Mt = Mat([["-2", "1", "-1"], ["0", "1", "1"], ["0", "0", "3"]], colors=[C.ihat, C.jhat, C.khat], size=44,
             h_buff=0.98, v_buff=0.62).move_to([-4.95, 1.72, 0])   # inside the safe margin
    hats = VGroup(*[tex(h, size=40, color=c).next_to(Mt.cols[j], UP, buff=0.35)
                    for j, (h, c) in enumerate(((r"\hat{\imath}", C.ihat), (r"\hat{\jmath}", C.jhat),
                                                (r"\hat{k}", C.khat)))])
    for h_ in hats[1:]:
        h_.align_to(hats[0], DOWN)
    probe = tex(r"\det", "=", "-6", size=52).next_to(Mt, DOWN, buff=0.35)
    back = backing(VGroup(Mt, hats, probe), pad=0.3)
    hb.play(FadeIn(back), at=T.three_by - 0.2, dur=0.6, lead=0)
    neg2 = Mt.cell(0, 0)                              # sized for -2; shows 2 until the flip
    pos2 = tex("2", size=44, color=C.ihat).move_to(neg2, aligned_edge=RIGHT)
    Mt.cols[0].remove(neg2)
    Mt.cols[0].add(pos2)
    hud.play(FadeIn(VGroup(Mt, hats)), at=T.three_by - 0.1, dur=0.7, lead=0)
    for j in range(3):
        hud.play(Indicate(Mt.cols[j], color=[C.ihat, C.jhat, C.khat][j], scale_factor=1.25),
                 at=T.three_by + 0.9 + 0.6 * j, dur=0.6)
    zero3 = tex("0", size=44, color=C.khat).move_to(Mt.cell(2, 2))
    hud.play(FadeOut(pos2), FadeIn(neg2, scale=1.3), at=flip[0] + 0.2, dur=0.6, lead=0)
    hud.play(FadeOut(Mt.cell(2, 2)), FadeIn(zero3, scale=1.3), at=press[0] + 0.2, dur=0.6, lead=0)

    r_on = (T.cube - 0.1, T.cube + 0.6)

    def readout(t):
        d = det3(M(t))
        col = C.area if d > 0.05 else C.flip if d < -0.05 else C.collapse
        r_ = tex(r"\det", "=", num(d), size=52, colors={2: col})
        r_.move_to(probe, aligned_edge=LEFT)
        return r_.set_opacity(ramp(t, *r_on) * (1 - ramp(t, end[1] - 0.8, end[1])))
    live(hud, readout, r_on, grow, flip, press, (end[1] - 0.8, end[1]))

    # ── no way back ──
    inv = tex("A^{-1}", size=80).move_to([4.6, 2.9, 0])
    x_inv = strike(inv, color=C.collapse).set_stroke(width=C.stroke)
    hud.play(Write(inv), at=T.no_back - 0.2, dur=0.7)
    hud.play(Create(x_inv), at=T.no_back + 0.5, dur=0.4)
    hb.play(FadeOut(back), at=end[1] - 0.8, dur=0.7, lead=0)
    hud.play(FadeOut(VGroup(Mt, hats, neg2, zero3, inv, x_inv)), at=end[1] - 0.8, dur=0.7, lead=0)

    finish(s)
