"""Ch3 · curl in 3D. The plane tilts back (orthographic 3D). The wheel's axle is now free: it swings through a few
directions and the wheel's spin (c . n) changes with it, fastest when the axle lines up with the green curl vector c.
A right-hand glyph wraps the axle: fingers with the spin, thumb along c. Our flat curl was only c's z part: c dims to
its vertical piece, and seen from above it points straight out of the page. Then the shorthand: del as a list of
three derivatives; dotted with F it gives the divergence, crossed with F the curl (as a determinant). A memory trick;
the meaning is the dye and the wheel, which sit beside them. The del-cross F badge drops."""
from aion import *

from beats import T
from shots import BADGES, arrow, badge, dim, dye_poly, ease, ortho, paddle, ramp, spin_glyph, stage, tex

E = "easy_ease"
C3 = (0.6, -0.5)                                # 3D view centre (world)
SCL = 1.25
AZ = np.radians(-35)
CV = np.array([0.6, -0.4, 1.0])                 # the curl vector
CH = CV / np.linalg.norm(CV)
D1 = np.array([1.0, 0.25, 0.35]) / np.linalg.norm([1.0, 0.25, 0.35])
D2 = np.array([-0.35, 1.0, 0.3]) / np.linalg.norm([-0.35, 1.0, 0.3])
Z = np.array([0.0, 0.0, 1.0])
WR3 = 0.95


def basis(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(n, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(n, e1)


def poly3(proj, pts, color, width, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(
        [proj(p) for p in pts])


@scene(T.cut_3d, T.cut_ch4)
def s09_curl_3d(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:2], tile=True)

    el = keys((s.start, np.radians(89.5)), (T.three_d - 0.2, np.radians(89.5)), (T.three_d + 1.8, np.radians(24), E),
              (T.out_page - 0.3, np.radians(24)), (T.out_page + 1.0, np.radians(89.5), E), lead=0)
    n_tr = keys((s.start, Z), (T.axle - 0.1, Z), (T.axle + 1.0, D1, E), (T.axle + 2.0, D2, E), (T.rhr - 0.3, CH, E),
                (T.flat + 0.3, CH), (T.flat + 1.6, Z, E), lead=0)
    nrm = lambda t: (lambda v: v / np.linalg.norm(v))(np.asarray(n_tr(t), float))
    # spin angle: integrate omega = 0.9 * (c . n) on a fine grid
    tt = np.linspace(s.start, T.cut_ch4, int((T.cut_ch4 - s.start) * 60) + 1)
    om = np.array([0.9 * CV @ nrm(t) for t in tt])
    ang = np.concatenate([[0], np.cumsum(0.5 * (om[1:] + om[:-1]) * np.diff(tt))])
    spin = lambda t: float(np.interp(t, tt, ang))
    k_in = (s.start + 0.3, s.start + 1.2)
    k_out = (T.shorthand + 0.4, T.shorthand + 1.0)

    def scene3d(t):
        k = ease(t, *k_in) * (1 - ramp(t, *k_out))
        proj = ortho(AZ, float(el(t)), scale=SCL, center=C3)
        g = VGroup()
        # the plane: a 4 x 4 grid at z = 0
        for a in np.linspace(-2, 2, 5):
            edge = abs(a) > 1.99
            col, w = (C.frame, C.thin) if edge else (C.grid_minor, C.thin * 0.8)
            g.add(Line(proj([a, -2, 0]), proj([a, 2, 0]), color=col, stroke_width=w))
            g.add(Line(proj([-2, a, 0]), proj([2, a, 0]), color=col, stroke_width=w))
        # the wheel: hub, vanes, axle (perpendicular to the wheel)
        n = nrm(t)
        e1, e2 = basis(n)
        th = np.linspace(0, 2 * np.pi, 49)
        hub = [0.2 * WR3 * (np.cos(a) * e1 + np.sin(a) * e2) for a in th]
        g.add(poly3(proj, hub, C.dust, 3))
        for j in range(4):
            a = spin(t) + j * np.pi / 2
            d = np.cos(a) * e1 + np.sin(a) * e2
            g.add(Line(proj(0.2 * WR3 * d), proj(WR3 * d), color=C.dust, stroke_width=4))
            g.add(Dot(proj(WR3 * d), radius=0.035, color=C.dust))
        rim = [WR3 * (np.cos(a) * e1 + np.sin(a) * e2) for a in th]
        g.add(poly3(proj, rim, C.muted, C.thin, opacity=0.5))
        g.add(Line(proj(-1.0 * n), proj(1.3 * n), color=C.muted, stroke_width=C.thin + 0.5))
        # the curl vector, once the axle has found it
        kc = ramp(t, T.rhr - 0.6, T.rhr) * (1 - 0.65 * ramp(t, T.flat, T.flat + 0.8)) * (1 - ramp(t, T.out_page - 0.4, T.out_page + 0.2))
        if kc > 0.01:
            g.add(arrow(proj([0, 0, 0])[:2], proj(1.7 * CH)[:2], C.curl, width=C.stroke + 1.5, tip=0.22, opacity=kc))
        # right hand: fingers curl with the spin, the thumb is c
        kf = ramp(t, T.fingers - 0.3, T.fingers + 0.6) * (1 - ramp(t, T.flat - 0.3, T.flat + 0.3))
        if kf > 0.01:
            arc = [1.35 * CH + 0.42 * (np.cos(a) * basis(CH)[0] + np.sin(a) * basis(CH)[1])
                   for a in np.linspace(0, 1.6 * np.pi * min(1.0, kf * 1.2), 40)]
            curve = poly3(proj, arc, C.curl, C.stroke, opacity=kf)
            g.add(curve)
            p1, p0 = proj(arc[-1])[:2], proj(arc[-4])[:2]
            g.add(arrow(p0, p0 + (p1 - p0) * 1.6, C.curl, width=C.stroke, tip=0.16, opacity=kf))
        kt = ramp(t, T.thumb - 0.1, T.thumb + 0.3) * (1 - ramp(t, T.thumb + 0.9, T.thumb + 1.4))
        if kt > 0.01:
            g.add(arrow(proj([0, 0, 0])[:2], proj(1.7 * CH)[:2], C.curl, width=C.stroke + 5, tip=0.26,
                        opacity=0.6 * kt))
        # the z part (our flat curl): straight up, out of the page from above
        kz = ramp(t, T.flat + 0.3, T.flat + 1.1)
        if kz > 0.01:
            tip = np.array([0, 0, 1.7 * CH[2]])
            g.add(DashedLine(proj(1.7 * CH), proj(tip), color=C.muted, stroke_width=C.thin, dash_length=0.06)
                  .set_stroke(opacity=kz * (1 - ramp(t, T.out_page, T.out_page + 0.6))))
            if np.linalg.norm(proj(tip) - proj([0, 0, 0])) > 0.15:
                g.add(arrow(proj([0, 0, 0])[:2], proj(tip)[:2], C.curl, width=C.stroke + 1.5, tip=0.22, opacity=kz))
            ko = ramp(t, T.out_page + 0.6, T.out_page + 1.1)
            if ko > 0.01:                       # seen from above: out of the page
                c0 = proj([0, 0, 0])
                g.add(Circle(radius=0.2, color=C.curl, stroke_width=C.stroke).move_to(c0).set_stroke(opacity=ko))
                g.add(Dot(c0, radius=0.06, color=C.curl).set_opacity(ko))
        return dim(g, k)
    m.redraw(scene3d, during=(k_in[0], k_out[1] + 0.05))

    # spin readout while the axle swings
    def readout(t):
        k = ramp(t, T.axle - 0.3, T.axle + 0.2) * (1 - ramp(t, T.flat - 0.4, T.flat + 0.1))
        v = float(CV @ nrm(t))
        lab = tex(r"\text{spin}", size=40, color=C.muted).move_to([5.3, 1.5, 0])
        num = DecimalNumber(v, num_decimal_places=2, font_size=58, color=C.curl).move_to([5.3, 0.85, 0])
        return VGroup(lab, num).set_opacity(k)
    m.redraw(readout, during=(T.axle - 0.3, T.flat + 0.15))
    c_lab = tex(r"\mathbf{c}", size=50, color=C.curl)
    c_lab.move_to(ortho(AZ, np.radians(24), scale=SCL, center=C3)(1.85 * CH) + np.array([0.3, 0.1, 0]))
    m.play(FadeIn(c_lab, scale=0.6), at=T.rhr - 0.2, dur=0.5)
    m.play(FadeOut(c_lab), at=T.flat, dur=0.5)

    # ── the shorthand ──
    nab = tex(r"\nabla", "=", r"\Big(", r"\frac{\partial}{\partial x}", ",", r"\frac{\partial}{\partial y}", ",",
              r"\frac{\partial}{\partial z}", r"\Big)", size=62).move_to([0.9, 2.55, 0])
    m.play(FadeIn(nab[0:3], shift=0.1 * DOWN), FadeIn(nab[8]), at=T.del_list, dur=0.8)
    m.play(LaggedStart(*[FadeIn(nab[i], shift=0.12 * DOWN) for i in (3, 4, 5, 6, 7)], lag_ratio=0.3),
           at=T.dxdydz - 0.3, dur=1.8)
    dv = tex(r"\nabla\cdot", r"\mathbf{F}", "=", r"\frac{\partial P}{\partial x}", "+", r"\frac{\partial Q}{\partial y}",
             "+", r"\frac{\partial R}{\partial z}", size=54, colors={0: C.div, 3: C.xpart, 5: C.ypart})
    dv.move_to([0.6, 0.55, 0])
    m.play(FadeIn(dv[0:3], shift=0.15 * RIGHT), at=T.dot, dur=0.7)
    m.play(LaggedStart(*[FadeIn(dv[i], shift=0.1 * LEFT) for i in range(3, 8)], lag_ratio=0.2), at=T.dot + 0.7,
           dur=1.4)
    cr = tex(r"\nabla\times", r"\mathbf{F}", "=",
             r"\begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ \partial_x & \partial_y & \partial_z \\"
             r" P & Q & R \end{vmatrix}", size=52, colors={0: C.curl})
    cr.move_to([0.6, -1.85, 0])
    m.play(FadeIn(cr[0:3], shift=0.15 * RIGHT), at=T.cross, dur=0.7)
    m.play(FadeIn(cr[3], shift=0.1 * LEFT), at=T.cross + 0.7, dur=1.0)
    m.play(nab.animate.set_opacity(0.35), dv.animate.set_opacity(0.35), cr.animate.set_opacity(0.35),
           at=T.trick, dur=1.0)

    # "the meaning is the drop of dye, and the paddle wheel"
    th = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    dc = np.array([5.2, 0.55])
    dye = dye_poly(np.stack([dc[0] + 0.5 * np.cos(th), dc[1] + 0.5 * np.sin(th)], 1), C.div, opacity=0.15)
    dye.set_stroke(width=C.stroke)
    wc = np.array([5.2, -1.85])
    wheel = VGroup(paddle(wc, np.pi / 4, radius=0.5, color=C.dust, width=3), spin_glyph(wc, 0.75, +1, C.curl))
    m.play(FadeIn(dye, scale=0.5), at=T.meaning + 0.6, dur=0.7, ease="out_back")
    m.play(FadeIn(wheel, scale=0.5), at=T.meaning + 1.3, dur=0.7, ease="out_back")
    b = badge(2, BADGES[2])
    m.play(FadeIn(b, shift=0.6 * DOWN), at=T.cut_ch4 - 1.5, dur=0.6, ease="out_back")
    m.play(FadeOut(VGroup(nab, dv, cr, dye, wheel)), at=T.cut_ch4 - 0.7, dur=0.6)
