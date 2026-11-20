"""s21: three dimensions. A sphere of constant distance inflates until it touches the plane at (1, 2, 2), and the gradients align again."""
from aion import *

from beats import T
from ch1 import *

N = np.array([1.0, 2.0, 2.0]) / 3.0
TOUCH = np.array([1.0, 2.0, 2.0])


@scene(T.cut_ch6, T.cut_ellipse)
def s21_sphere(s):
    backdrop(s)
    cam = camera(
        (T.cut_ch6, (-35, 26, 0.95, 0.0, -0.3, 34, 0, 0, 0.3)),
        (T.spheres, (-15, 22, 1.0, 0.0, -0.25, 34, 0, 0, 0.3)),
        (T.tangent_p - 0.4, (-2, 20, 1.0, 0.0, -0.25, 34, 0, 0, 0.3)),
        (T.tangent_p + 1.4, (8, 16, 1.75, 0.0, -0.4, 34, TOUCH[0], TOUCH[1], TOUCH[2])),
        (T.pt122 + 0.4, (14, 18, 1.75, 0.0, -0.4, 34, TOUCH[0], TOUCH[1], TOUCH[2])),
        (T.cut_ellipse, (24, 26, 1.1, 0.0, -0.3, 34, 0.5, 1.0, 1.0)),
    )
    e1 = np.cross(N, [0.0, 0.0, 1.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(N, e1)
    uu, vv = np.meshgrid(np.linspace(-4.4, 4.4, 8), np.linspace(-3.4, 3.4, 8))
    PL = TOUCH[None, None] + uu[..., None] * e1 + vv[..., None] * e2
    th, ph = np.meshgrid(np.linspace(PI, 3 * PI, 56), np.linspace(0.02, PI - 0.02, 30))
    sph = np.stack([np.sin(ph) * np.cos(th), np.sin(ph) * np.sin(th), np.cos(ph)], -1)
    r = keys((T.inflate - 0.3, 0.7), (T.tangent_p - 0.2, 3.0), default_ease=E)
    plane_a = fade(T.the_plane, dur=0.8)
    arrows = fade(T.tangent_p + 1.3, dur=0.5)

    def frame(t):
        v = view().begin(cam(t))
        for a in (np.array([4.2, 0, 0]), np.array([0, 4.2, 0]), np.array([0, 0, 3.6])):
            v.line(np.array([-a, a]), C.axis, 2.2, 0.8)
        R = float(r(t))
        if t >= float(T.spheres) - 0.3:
            v.mesh(R * sph[..., 0], R * sph[..., 1], R * sph[..., 2], C.obj, ambient=0.3)
            for lat in np.linspace(0.45, PI - 0.45, 6):
                a = np.linspace(0, TAU, 70)
                ring = R * np.column_stack([np.sin(lat) * np.cos(a), np.sin(lat) * np.sin(a), np.full_like(a, np.cos(lat))])
                v.line(ring, C.bg, 1.3, 0.3, visible=ring @ v.cam.d > 0)
        p = float(plane_a(t))
        if p > 0.01:
            v.mesh(PL[..., 0], PL[..., 1], PL[..., 2], C.con, alpha=0.42 * p, shade=False)
            edge = TOUCH + np.array([[-4.4], [4.4], [4.4], [-4.4]]) * e1 + np.array([[-3.4], [-3.4], [3.4], [3.4]]) * e2
            v.line(edge, C.con, 3, p, close=True)
        if t >= float(T.tangent_p) - 0.2:
            da = ramp(t, T.pt122, T.pt122 + 0.8)
            if da > 0.01:
                for j in range(16):
                    if j % 2 == 0:
                        v.line([TOUCH * j / 16 * da, TOUCH * (j + 1) / 16 * da], C.text, 2.4)
            v.dot(TOUCH, C.you, 0.13, ring=C.bg)
        g = float(arrows(t))
        if g > 0.01:
            v.arrow(TOUCH, TOUCH + N * 2.1 * g, C.obj, 6, tip=0.3)
            v.arrow(TOUCH, TOUCH + N * 1.05 * g, C.con, 6, tip=0.3)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10))
    title(s, "Chapter 6  ·  higher dimensions", T.cut_ch6 + 0.3, hold=3.0)
    h = s.manim(z=20, parallax=0.0)
    stack(h, [(tex("x+2y+2z", "=", "9", size=44, colors={0: C.con, 2: C.con}), T.the_plane + 0.6), (tex(r"\min\;", "x^2+y^2+z^2", size=44, colors={1: C.obj}), T.spheres)], pos=(-6.75, 3.3))
    headline(h, backed(tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=72, colors={0: C.obj, 2: C.lam, 3: C.con}), 0.14, 0.85), T.same_eq - 0.3, T.cut_ellipse - 0.3, y=-3.2)
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, TOUCH + N * 2.1, tex(r"\nabla f", size=50, color=C.obj), T.tangent_p + 1.6, T.cut_ellipse - 0.05, off=(0.4, 0.2))
    pin(m, cam, TOUCH + N * 1.05, tex(r"\nabla g", size=50, color=C.con), T.tangent_p + 1.9, T.cut_ellipse - 0.05, off=(-0.45, 0.1))
    pin(m, cam, TOUCH, backed(tex("(1,\\,2,\\,2)", size=46, color=C.you), 0.08, 0.85), T.pt122, T.cut_ellipse - 0.05, off=(1.1, -0.35))
    pin(m, cam, TOUCH * 0.5, backed(lab("distance 3", 28, C.text), 0.1, 0.85), T.pt122 + 1.0, T.cut_ellipse - 0.05, off=(0.0, -0.35))
    pin(m, cam, [0, 0, 0.0], backed(lab("level surfaces: spheres", 28, C.obj), 0.1, 0.85), T.spheres + 0.4, T.tangent_p, off=(0.0, -2.0))
    curtain(s)
