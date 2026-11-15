"""Portrait short, after the user's reference frame: outlined two-line title, det [M] = value with a column box,
and a perspective 3D lattice with fixed white axes. One column at a time changes; the last change makes column 3
equal to column 1 + column 2, so the whole lattice folds into the plane x = z and det reads 0.
"""
from aion import *

from beats import T

O3, U3 = np.array([0.0, -2.9]), 0.86            # screen point of the 3D origin, units per grid step
DIST = 11.0                                     # camera distance (perspective strength)
N = 4                                           # lattice lines at integers in [-N, N], clipped to BOX
AX = 4.4                                        # axis half-length

I3 = np.eye(3)
K1 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2]], float)     # c3 -> (0,0,2)          det 2
K2 = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 2]], float)     # c1 -> (1,0,1)          det 2
K3 = np.array([[1, 0, 1], [0, 1, 1], [1, 0, 1]], float)     # c3 -> c1 + c2 = (1,1,1) det 0 (rows 1 and 3 equal)
STAGES = [(T.s1, 2.2, I3, K1, 2), (T.s2, 2.2, K1, K2, 0), (T.s3, 2.8, K2, K3, 2)]   # (start, dur, from, to, col)

CUBE = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
FACES = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]


def ramp(t, a, b, ease=smooth):
    return ease(float(np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)))


def matrix_at(t):
    M = I3
    for a, dur, F, G, _ in STAGES:
        if t >= a:
            M = F + (G - F) * ramp(t, a, a + dur, ease=rate_functions.ease_in_out_cubic)
    return M


class Cam:
    """Perspective camera looking at the origin: azimuth `az` about z, elevation `el` above the floor."""

    def __init__(self, az, el):
        a, e = np.radians(az), np.radians(el)
        self.R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        self.ce, self.se = np.cos(e), np.sin(e)

    def _view(self, p):
        q = self.R @ np.asarray(p, float)
        return q[0], q[2] * self.ce + q[1] * self.se, q[1] * self.ce - q[2] * self.se   # right, up, depth

    def scr(self, p):
        x, y, d = self._view(p)
        k = DIST / (DIST + d)
        return np.array([O3[0] + U3 * k * x, O3[1] + U3 * k * y, 0.0])

    def depth(self, p):
        return self._view(p)[2]

    def scale(self, p):
        return DIST / (DIST + self.depth(p))


def camera_at(t):
    """Slow orbit at a low angle (like the reference); during the collapse it swings round to face the plane
    x = z (face-on would be az = -90; -80 keeps a little depth) and lifts a little."""
    k = ramp(t, T.s3 + 0.4, T.zero + 1.2, ease=rate_functions.ease_in_out_cubic)
    drift = -38.0 + 1.6 * t
    return Cam(drift + (-80.0 + 0.8 * (t - T.zero) - drift) * k, 22.0 + 10.0 * k)


BOX = 3.2                                       # the lattice is clipped to this world-space cube after M


def clip_box(a, b, h=BOX):
    """Clip the segment a-b to the cube [-h, h]^3 (Liang-Barsky). Returns the clipped ends or None."""
    d = b - a
    lo, hi = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if abs(a[i]) > h:
                return None
            continue
        s0, s1 = sorted(((-h - a[i]) / d[i], (h - a[i]) / d[i]))
        lo, hi = max(lo, s0), min(hi, s1)
        if lo >= hi:
            return None
    return a + lo * d, a + hi * d


def num(d):
    s_ = f"{d:.1f}"
    s_ = s_[:-2] if s_.endswith(".0") else s_
    return "0" if s_ in ("-0", "-0.0") else s_


def tex(*parts, size=None, color=None):
    return MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)


def brackets(height, gap, width=2.2, hook=0.15):
    h = height / 2

    def one(sign):
        x = sign * gap / 2
        tip = x - sign * hook
        return VMobject(stroke_color=C.text, stroke_width=width).set_points_as_corners(
            [[tip, h, 0], [x, h, 0], [x, -h, 0], [tip, -h, 0]])
    return VGroup(one(-1), one(1))


HB, VB, FS = 0.72, 0.56, 38                     # matrix column spacing, row spacing, entry size


def entries(M, col):
    """Column `col` of M as three white entries, placed in the matrix grid (centred at the origin)."""
    return VGroup(*[tex(num(M[i, col]), size=FS).move_to([(col - 1) * HB, (1 - i) * VB, 0]) for i in range(3)])


def outlined(text, size, colors):
    """Hollow title type: Computer Modern letters drawn as outlines, with a colour gradient across them."""
    t = Tex(text, font_size=size)
    t.set_color_by_gradient(*colors)
    t.set_fill(opacity=0.0)
    t.set_stroke(width=1.8, opacity=1.0)
    return t


@scene(T.start, T.end)
def s01_det_zero(s):
    s.solid(C.bg, z=-200)
    w = s.manim(z=1)
    hud = s.manim(z=6, parallax=0.0)
    top = config.frame_height / 2

    # ── title ──
    t1 = outlined(r"Matrix 3D", 104, [C.title1, C.title1])
    t2 = outlined(r"Determinant $=0$", 104, [C.title2, C.title3])
    for t_ in (t1, t2):
        if t_.width > config.frame_width - 2 * C.margin:
            t_.scale_to_fit_width(config.frame_width - 2 * C.margin)
    t1.move_to([0, top - 1.15, 0]).align_to([-config.frame_width / 2 + C.margin + 0.15, 0, 0], LEFT)
    t2.next_to(t1, DOWN, buff=0.4).align_to(t1, LEFT)
    hud.play(DrawBorderThenFill(t1, run_time=1.2), at=T.title, dur=1.2, lead=0)
    hud.play(DrawBorderThenFill(t2, run_time=1.4), at=T.title2, dur=1.4, lead=0)
    hud.play(t2.animate(rate_func=there_and_back).scale(1.07), at=T.zero + 0.3, dur=1.0)

    # ── det [ M ] = value ──
    eq_c = np.array([-0.35, t2.get_bottom()[1] - 1.45, 0])
    cols = [entries(I3, j) for j in range(3)]
    body = VGroup(*cols)
    br = brackets(2 * VB + 0.6, 2 * HB + 0.68)
    mat = VGroup(br, body).move_to(eq_c)
    det_w = tex(r"\det", size=44).next_to(mat, LEFT, buff=0.25)
    eq_sign = tex("=", size=44).next_to(mat, RIGHT, buff=0.25)
    hud.play(FadeIn(VGroup(det_w, mat, eq_sign), shift=0.1 * UP), at=T.eq, dur=0.7)

    shift = mat.get_center() - ORIGIN                 # entries were built around the origin
    box = Rectangle(width=HB * 0.78, height=2 * VB + 0.62, stroke_color=C.box, stroke_width=3.0,
                    fill_opacity=0.0)
    box.move_to(cols[2].get_center())
    hud.play(Create(box), at=STAGES[0][0] - 0.6, dur=0.5)
    cur = list(cols)
    for k, (a, dur, F, G, col) in enumerate(STAGES):
        if k > 0:
            hud.play(box.animate.move_to(cur[col].get_center()), at=a - 0.5, dur=0.5)
        new = entries(G, col).shift(shift)
        mid = a + dur / 2
        hud.play(FadeOut(cur[col], shift=0.15 * UP), FadeIn(new, shift=0.15 * UP), at=mid, dur=0.6)
        hud.remove(cur[col], at=mid + 0.1)
        cur[col] = new
    hud.play(FadeOut(box), at=T.zero, dur=0.6)

    val_on = (T.eq - 0.15, T.eq + 0.55)

    def value(t):
        d = float(np.linalg.det(matrix_at(t)))
        r_ = tex(num(d), size=44, color=C.collapse if abs(d) < 0.05 else C.text)
        r_.next_to(eq_sign, RIGHT, buff=0.25)
        return r_.set_opacity(ramp(t, *val_on))
    hud.redraw(value, during=(val_on[0], T.end))

    # ── the 3D view ──
    grow = (T.grid, T.grid + 1.8)
    ax_on = (T.grid, T.grid + 1.2)
    cube_on = (T.cube, T.cube + 0.7)
    plane_on = (T.zero, T.zero + 0.8)

    def view(t):
        cam, M = camera_at(t), matrix_at(t)
        d = float(np.linalg.det(M))
        out = VGroup()

        # lattice: every integer line of [-N, N]^3 carried by M, growing out from its midpoint at the start
        g = ramp(t, *grow, ease=rate_functions.ease_out_cubic)
        if g > 0:
            segs = []
            for ax in range(3):
                o1, o2 = [a_ for a_ in range(3) if a_ != ax]
                for u in range(-N, N + 1):
                    for v in range(-N, N + 1):
                        p0, p1 = np.zeros(3), np.zeros(3)
                        p0[ax], p1[ax] = -N * g, N * g
                        p0[o1] = p1[o1] = u
                        p0[o2] = p1[o2] = v
                        seg = clip_box(M @ p0, M @ p1)
                        if seg is not None:
                            a_, b_ = seg
                            segs.append((cam.depth((a_ + b_) / 2), a_, b_))
            dmax = N * 2.2
            for dep, a_, b_ in sorted(segs, key=lambda r: -r[0]):
                near = float(np.clip(0.55 - 0.45 * dep / dmax, 0.2, 1.0))
                out.add(Line(cam.scr(a_), cam.scr(b_), color=C.grid, stroke_width=C.thin * 0.75,
                             stroke_opacity=0.75 * near))

        # the plane everything collapsed onto (x = z), once det is 0
        kp = ramp(t, *plane_on)
        if kp > 0:
            span = [np.array(c, float) * BOX for c in ((-1, -1, -1), (1, -1, 1), (1, 1, 1), (-1, 1, -1))]  # x = z
            out.add(Polygon(*[cam.scr(p) for p in span], stroke_color=C.collapse, stroke_width=C.thin,
                            stroke_opacity=0.8 * kp, fill_color=C.collapse, fill_opacity=0.16 * kp))

        # yellow unit cube carried by M (its volume is |det|), pink as det -> 0
        kc = ramp(t, *cube_on)
        if kc > 0:
            col = interpolate_color(ManimColor(C.collapse), ManimColor(C.vol), float(np.clip(abs(d) / 1.0, 0, 1)))
            cs = [M @ c for c in CUBE]
            for f in sorted(FACES, key=lambda f: -np.mean([cam.depth(cs[i]) for i in f])):
                out.add(Polygon(*[cam.scr(cs[i]) for i in f], stroke_color=col, stroke_width=C.thin + 0.4,
                                stroke_opacity=kc, fill_color=col, fill_opacity=0.22 * kc))

        # fixed white axes with arrowheads and integer ticks, drawn on top like the reference
        ka = ramp(t, *ax_on)
        if ka > 0:
            for i in range(3):
                e = np.zeros(3)
                e[i] = 1.0
                lo = -AX * ka * (0.7 if i == 2 else 1.0)
                a_, b_ = cam.scr(e * lo), cam.scr(e * AX * ka)
                out.add(Arrow(a_, b_, buff=0, color=C.axis, stroke_width=C.thin * 1.8, tip_length=0.2,
                              max_tip_length_to_length_ratio=0.1, max_stroke_width_to_length_ratio=40))
                for n in range(-4, 5):
                    if n == 0 or not (lo < n < AX * ka - 0.3):
                        continue
                    out.add(Dot(cam.scr(e * n), radius=0.035 * cam.scale(e * n), color=C.axis))

        # the column being changed, as a yellow arrow from the origin
        for a, dur, F, G, colj in STAGES:
            kv = ramp(t, a - 0.5, a) * (1 - ramp(t, a + dur + 0.6, a + dur + 1.1))
            if kv > 0:
                p0, p1 = cam.scr((0, 0, 0)), cam.scr(M[:, colj])
                L = np.linalg.norm(p1 - p0)
                if L > 1e-3:
                    out.add(Arrow(p0, p1, buff=0, color=C.vol, stroke_width=C.stroke + 1, stroke_opacity=kv,
                                  tip_length=min(0.22, 0.4 * L), max_tip_length_to_length_ratio=0.4,
                                  max_stroke_width_to_length_ratio=40).set_opacity(kv))
        return out

    w.redraw(view, during=(T.start, T.end))
