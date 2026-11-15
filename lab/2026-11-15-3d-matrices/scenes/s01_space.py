"""A 3x3 matrix moves 3D space: a lattice, three basis arrows and the unit cube, seen through a slowly orbiting
orthographic camera. Identity -> shear/stretch (det 2) -> rotate 90 deg about x (det stays 2) -> flatten z (det 0) ->
back to the identity.

Everything 3D is projected by hand into crisp Manim lines (Classic look: black, blue grid, white axes, no glow).
The whole view is one `redraw` because the camera never stops moving.
"""
from aion import *

from beats import T

E = "easy_ease"
O3, U3 = np.array([1.9, -1.3]), 0.82              # screen position of the 3D origin, units per grid step
N = 2                                             # lattice runs from -N to N on every axis

I3 = np.eye(3)
A = np.array([[1.0, 1.0, 0.0],                    # i stays, j leans over to (1, 1, 1), k stretches to (0, 0, 2)
              [0.0, 1.0, 0.0],
              [0.0, 1.0, 2.0]])                   # det = 1 * (1*2 - 0*1) - 1 * (0*2 - 0*0) = 2
P = np.diag([1.0, 1.0, 0.0])                      # flatten onto the floor z = 0


def Rx(theta):
    """Rotation about the x-axis (tips the box over toward -y, against the fixed floor)."""
    c, s_ = np.cos(theta), np.sin(theta)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s_], [0.0, s_, c]])


R90 = np.round(Rx(PI / 2))
KEYS = [I3, A, R90 @ A, P @ R90 @ A]              # the matrices the HUD shows, in order
CUBE = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
FACES = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]

# windows (start, end) for every move, all from the beat table
W_FLOOR = (T.floor, T.floor + 1.0)
W_TILT = (T.tilt, T.tilt + 2.0)
W_HATS = [(T.hats + 0.3 * k, T.hats + 0.3 * k + 0.7) for k in range(3)]
W_CUBE = (T.cube, T.cube + 0.8)
W_SHEAR = (T.shear, T.shear + 2.2)
W_ROT = (T.rotate, T.rotate + 2.4)
W_SQUASH = (T.squash, T.squash + 2.2)
W_BACK = (T.restore, T.restore + 2.6)


def ramp(t, w, ease=smooth):
    a, b = w
    return ease(float(np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)))


def matrix_at(t):
    """The total matrix at time t, built from the moves (so the rotation stays a true rotation)."""
    back = ramp(t, W_BACK)
    S = I3 + (A - I3) * ramp(t, W_SHEAR) * (1 - back)
    R = Rx(PI / 2 * ramp(t, W_ROT) * (1 - back))
    Q = I3 + (P - I3) * ramp(t, W_SQUASH) * (1 - back)
    return Q @ R @ S


class Cam:
    """Orthographic camera: turn the world by azimuth `az` about z, then tip it to elevation `el`."""

    def __init__(self, az, el):
        a, e = np.radians(az), np.radians(el)
        self.R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        self.ce, self.se = np.cos(e), np.sin(e)

    def scr(self, p):
        q = self.R @ np.asarray(p, float)
        return np.array([O3[0] + U3 * q[0], O3[1] + U3 * (q[2] * self.ce + q[1] * self.se), 0.0])

    def depth(self, p):
        q = self.R @ np.asarray(p, float)
        return q[1] * self.ce - q[2] * self.se    # larger = farther from the viewer


def camera_at(t):
    """Top-down at the start, tipped to an oblique view, then a slow continuous orbit."""
    k = ramp(t, W_TILT, ease=rate_functions.ease_in_out_cubic)
    orbit = 1.6 * max(0.0, t - W_TILT[0])        # degrees per second
    return Cam(-48.0 * k + orbit, 90.0 - 32.0 * k)


def num(d):
    s_ = f"{d:.1f}"
    if s_.endswith(".0"):
        s_ = s_[:-2]
    return "0" if s_ in ("-0", "-0.0") else s_


def tex(*parts, size=None, color=None):
    return MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)


def brackets(height, gap, width=2.4, hook=0.16):
    """Square brackets as crisp polylines, `gap` apart (inner edges), hooks pointing inward."""
    h = height / 2

    def one(sign):
        x = sign * gap / 2
        tip = x - sign * hook
        return VMobject(stroke_color=C.text, stroke_width=width).set_points_as_corners(
            [[tip, h, 0], [x, h, 0], [x, -h, 0], [tip, -h, 0]])
    return VGroup(one(-1), one(1))


def mat(M, size=42, hb=0.82, vb=0.62):
    """A 3x3 matrix with hand-set brackets; column j in its basis colour."""
    cols = (C.ihat, C.jhat, C.khat)
    g = VGroup()
    for i in range(3):
        for j in range(3):
            g.add(tex(num(M[i, j]), size=size, color=cols[j]).move_to([(j - 1) * hb, (1 - i) * vb, 0]))
    br = brackets(2 * vb + 0.62, 2 * hb + 0.72, hook=0.14).move_to(ORIGIN)
    return VGroup(br, g)


@scene(T.start, T.end)
def s01_space(s):
    s.solid(C.bg, z=-200)
    w = s.manim(z=1)
    hud = s.manim(z=6, parallax=0.0)

    hats_tex = [tex(r"\hat{\imath}", size=38, color=C.ihat), tex(r"\hat{\jmath}", size=38, color=C.jhat),
                tex(r"\hat{k}", size=38, color=C.khat)]

    def view(t):
        cam, M = camera_at(t), matrix_at(t)
        d = float(np.linalg.det(M))
        out = VGroup()
        kf = ramp(t, W_FLOOR)

        # fixed reference floor (z = 0), dim, so the motion of the lattice reads against it
        for k in range(-9, 10):
            for a_, b_ in (((k, -9, 0), (k, 9, 0)), ((-9, k, 0), (9, k, 0))):
                out.add(Line(cam.scr(a_), cam.scr(b_), color=C.grid_minor, stroke_width=C.thin * 0.8,
                             stroke_opacity=kf))

        # the transformed lattice: every integer line of the cube [-N, N]^3, carried by M
        kl = ramp(t, W_CUBE)
        span = (-N, N)
        dmax = U3 * N * 2.5
        if kl > 0:
            lines = []
            for ax in range(3):
                o1, o2 = [a for a in range(3) if a != ax]
                for u in range(-N, N + 1):
                    for v in range(-N, N + 1):
                        p0, p1 = np.zeros(3), np.zeros(3)
                        p0[ax], p1[ax] = span
                        p0[o1] = p1[o1] = u
                        p0[o2] = p1[o2] = v
                        is_axis = u == 0 and v == 0
                        a_, b_ = M @ p0, M @ p1
                        lines.append((cam.depth((a_ + b_) / 2), a_, b_, is_axis))
            for dep, a_, b_, is_axis in sorted(lines, key=lambda r: -r[0]):
                near = float(np.clip(0.5 - dep / dmax, 0.15, 1.0))       # far lines fade
                out.add(Line(cam.scr(a_), cam.scr(b_), color=C.axis if is_axis else C.grid,
                             stroke_width=C.thin * (1.4 if is_axis else 0.9),
                             stroke_opacity=kl * (0.9 if is_axis else 0.55 * near)))

        # the unit cube carried by M, faces painted far to near; colour turns to `collapse` as det -> 0
        kc = ramp(t, W_CUBE)
        if kc > 0:
            col = interpolate_color(ManimColor(C.collapse), ManimColor(C.vol), float(np.clip(abs(d), 0, 1)))
            corners = [M @ c for c in CUBE]
            for f in sorted(FACES, key=lambda f: -np.mean([cam.depth(corners[i]) for i in f])):
                out.add(Polygon(*[cam.scr(corners[i]) for i in f], stroke_color=col, stroke_width=C.thin + 0.4,
                                stroke_opacity=kc, fill_color=col, fill_opacity=0.16 * kc))

        # the three basis arrows (the columns of M), always on top, with their hats at the tips
        for k, colr in enumerate((C.ihat, C.jhat, C.khat)):
            ka = ramp(t, W_HATS[k], ease=rate_functions.ease_out_cubic)
            if ka <= 0:
                continue
            a_, b_ = cam.scr((0, 0, 0)), cam.scr(M[:, k] * ka)
            L = np.linalg.norm(b_ - a_)
            if L > 1e-3:
                out.add(Arrow(a_, b_, buff=0, color=colr, stroke_width=C.stroke + 1, tip_length=min(0.24, 0.4 * L),
                              max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40))
            if L > 0.3:
                dirn = (b_ - a_) / L
                out.add(hats_tex[k].copy().move_to(b_ + dirn * 0.32 + np.array([0.0, 0.08, 0])).set_opacity(ka))
        return out

    w.redraw(view, during=(T.start, T.end))

    # ── HUD: the current matrix (crossfades between key matrices) and a live determinant ──
    pos = np.array([-4.55, 1.7, 0])
    mats = [mat(K).move_to(pos) for K in KEYS] + [mat(I3).move_to(pos)]
    swaps = [W_SHEAR, W_ROT, W_SQUASH, W_BACK]
    hud.play(FadeIn(mats[0], shift=0.1 * UP), at=T.cube + 0.2, dur=0.7)
    for k, (a_, b_) in enumerate(swaps):
        mid = (a_ + b_) / 2
        hud.play(FadeOut(mats[k]), FadeIn(mats[k + 1]), at=mid, dur=0.7)
        hud.remove(mats[k], at=mid + 0.1)
    hud.play(FadeOut(mats[-1]), at=T.out, dur=0.7)

    det_pos = pos + np.array([-0.9, -1.75, 0])
    det_on = (T.cube + 0.3, T.cube + 1.0)
    det_off = (T.out - 0.15, T.out + 0.55)

    def readout(t):
        d = float(np.linalg.det(matrix_at(t)))
        col = C.vol if abs(d) > 0.05 else C.collapse
        r_ = tex(r"\det", "=", num(d), size=46)
        r_[2].set_color(col)
        r_.move_to(det_pos, aligned_edge=LEFT)
        return r_.set_opacity(ramp(t, det_on) * (1 - ramp(t, det_off)))
    hud.redraw(readout, during=(det_on[0], det_off[1] + 0.05))
