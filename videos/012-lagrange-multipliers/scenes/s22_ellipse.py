"""s22: two constraints. A cylinder and a plane cut an ellipse, and at its top the gradient of f lies in the plane of the two constraint gradients."""
from aion import *

from beats import T
from ch1 import *

TOP = np.array([-0.6, -0.8, 3.0])
GG = np.array([-1.2, -1.6, 0.0])
GH = np.array([3.0, 4.0, 5.0])
GF = np.array([0.0, 0.0, 1.0])
LAM, MU = 0.5, 0.2
KV = 1.15


@scene(T.cut_ellipse, T.cut_ch7)
def s22_ellipse(s):
    backdrop(s)
    cam = camera(
        (T.cut_ellipse, (-40, 22, 1.3, 0.0, -0.1, 30, 0, 0, 2.05)),
        (T.top_e + 1.0, (-25, 20, 1.45, 0.0, -0.1, 30, 0, 0, 2.05)),
        (T.plane_dirs, (-10, 24, 1.9, 0.0, -0.4, 30, TOP[0], TOP[1], TOP[2])),
        (T.spanned, (15, 26, 1.9, 0.0, -0.4, 30, TOP[0], TOP[1], TOP[2])),
        (T.cut_ch7, (35, 26, 1.7, 0.0, -0.4, 30, TOP[0], TOP[1], TOP[2])),
    )
    assert np.allclose(LAM * GG + MU * GH, GF)
    th = np.linspace(0, TAU, 200)
    ell = np.column_stack([np.cos(th), np.sin(th), (10 - 3 * np.cos(th) - 4 * np.sin(th)) / 5])
    pu, pv = np.meshgrid(np.linspace(-2.0, 2.0, 6), np.linspace(-2.0, 2.0, 6))
    pz = (10 - 3 * pu - 4 * pv) / 5
    cyl_a, plane_a = fade(T.cylinder, dur=0.8), fade(T.cylinder + 1.3, dur=0.8)
    e_draw = key(T.top_e, 0.0, 1.0, dur=1.2, ease=E)
    disc = fade(T.plane_dirs, dur=0.7)
    arrows = fade(T.no_single - 0.2, dur=0.5)
    combo = key(T.mu_t + 0.2, 0.0, 1.0, dur=1.1, ease=E)
    n1, n2 = GG / np.linalg.norm(GG), GH - (GH @ GG) / (GG @ GG) * GG
    n2 = n2 / np.linalg.norm(n2)
    dr, da = np.meshgrid(np.linspace(0, 1.3, 3), np.linspace(0, TAU, 40))
    D = TOP[None, None] + (dr * np.cos(da))[..., None] * n1 + (dr * np.sin(da))[..., None] * n2

    def frame(t):
        c = cam(t)
        v = view().begin(c)
        az = float(np.degrees(np.arctan2(c.d[1], c.d[0])))
        for d in (np.array([3.2, 0, 0]), np.array([0, 3.2, 0])):
            v.line(np.array([-d, d]), C.axis, 2.2, 0.8)
        v.line(np.array([[0, 0, -0.6], [0, 0, 4.9]]), C.axis, 2.2, 0.8)
        a0 = np.radians(az)
        A = float(cyl_a(t))
        def side(lo, hi):
            aa, zz = np.meshgrid(np.linspace(a0 + lo, a0 + hi, 40), np.linspace(0.0, 4.2, 2))
            v.mesh(np.cos(aa), np.sin(aa), zz, C.con, alpha=0.3 * A, ambient=0.75)
        if A > 0.01:
            side(PI / 2, 3 * PI / 2)
        p = float(plane_a(t))
        if p > 0.01:
            v.mesh(pu, pv, pz, C.con2, alpha=0.36 * p, shade=False)
        if A > 0.01:
            side(-PI / 2, PI / 2)
        n = int(float(e_draw(t)) * len(ell))
        if n > 1:
            v.line(ell[:n], C.text, 5.5)
        q = float(disc(t))
        if q > 0.01:
            v.mesh(D[..., 0], D[..., 1], D[..., 2], C.text, alpha=0.13 * q, shade=False)
        if t >= float(T.top_e) + 1.0:
            v.dot(TOP, C.you, 0.12, ring=C.bg)
        g = float(arrows(t))
        if g > 0.01:
            v.arrow(TOP, TOP + KV * g * GG / 1.0 * 0.5, C.con, 5, tip=0.22)
            v.arrow(TOP, TOP + KV * g * GH / np.linalg.norm(GH) * 1.2, C.con2, 5, tip=0.22)
            c = float(combo(t))
            if c > 0.01:
                a = TOP + KV * LAM * GG * c
                b = a + KV * MU * GH * c
                v.line(np.array([TOP, a]), C.lam, 4, 0.9)
                v.line(np.array([a, b]), C.mu, 4, 0.9)
            v.arrow(TOP, TOP + KV * g * GF, C.obj, 6.5, tip=0.26)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10))
    h = s.manim(z=20, parallax=0.0)
    stack(h, [(tex("x^2+y^2", "=", "1", size=42, colors={0: C.con, 2: C.con}), T.cylinder), (tex("3x+4y+5z", "=", "10", size=42, colors={0: C.con2, 2: C.con2}), T.cylinder + 1.3), (tex(r"\max\;", "z", size=46, colors={1: C.obj}), T.top_e)], pos=(-6.75, 3.3))
    eq = tex(r"\nabla f", "=", r"\lambda", r"\nabla g", "+", r"\mu", r"\nabla h", size=66, colors={0: C.obj, 2: C.lam, 3: C.con, 5: C.mu, 6: C.con2})
    headline(h, backed(eq, 0.14, 0.85), T.eq_two, T.cut_ch7 - 0.3, y=-2.6)
    vals = backed(tex(r"\lambda", r"=\tfrac12,\quad", r"\mu", r"=\tfrac15", size=46, colors={0: C.lam, 2: C.mu}), 0.1, 0.85).move_to([0, -3.55, 0])
    h.play(FadeIn(vals, shift=0.06 * UP), at=T.mu_t + 1.3, dur=0.5, ease=E)
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, [0, 0, 0.0], backed(lab("an ellipse floating in space", 28, C.text), 0.1, 0.85), T.back_on, T.plane_dirs, off=(0.0, -1.6))
    pin(m, cam, TOP + 1.3 * n2, backed(lab("a whole plane of normals", 28, C.text), 0.1, 0.85), T.plane_dirs + 0.4, T.eq_two - 0.3, off=(0.0, 0.4))
    pin(m, cam, TOP + KV * GG * 0.5, tex(r"\nabla g", size=48, color=C.con), T.no_single + 0.2, T.cut_ch7 - 0.05, off=(-0.35, -0.2))
    pin(m, cam, TOP + KV * GH / np.linalg.norm(GH) * 1.2, tex(r"\nabla h", size=48, color=C.con2), T.no_single + 0.4, T.cut_ch7 - 0.05, off=(0.4, 0.2))
    pin(m, cam, TOP + KV * GF, tex(r"\nabla f", size=50, color=C.obj), T.no_single + 0.2, T.cut_ch7 - 0.05, off=(0.0, 0.35))
    pin(m, cam, [0, 0, 0.0], backed(lab("one multiplier per constraint", 30, C.you), 0.1, 0.85), T.own, T.cut_ch7 - 0.05, off=(0.0, -1.9))
    curtain(s)
