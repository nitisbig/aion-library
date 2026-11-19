"""s21: three dimensions. A sphere of constant distance inflates until it touches the plane at (1, 2, 2), and the gradients align again."""
from aion import *

from beats import T
from classic import *

N = np.array([1.0, 2.0, 2.0]) / 3.0
TOUCH = np.array([1.0, 2.0, 2.0])


@scene(T.cut_ch6, T.cut_ellipse)
def s21_sphere(s):
    backdrop(s)
    progress(s, 6, "Higher dimensions")
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
        v = view().begin(Cam(az=-8 + 10 * (t - float(s.start)) / 30.0, el=20, zoom=1.0, center=(0.0, -0.25), dist=34))
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
            v.dot(TOUCH, C.you, 0.13, ring=C.bg)
        g = float(arrows(t))
        if g > 0.01:
            v.arrow(TOUCH, TOUCH + N * 2.1 * g, C.obj, 6, tip=0.3)
            v.arrow(TOUCH, TOUCH + N * 1.05 * g, C.con, 6, tip=0.3)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10))
    h = hud(s)
    board(h, [(tex("x+2y+2z", "=", "9", size=40, colors={0: C.con, 2: C.con}), T.the_plane + 0.6), (tex(r"\min\;", "x^2+y^2+z^2", size=40, colors={1: C.obj}), T.spheres)])
    board(h, [(tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=60, colors={0: C.obj, 2: C.lam, 3: C.con}), T.same_eq - 0.3), (tex("(1,\\,2,\\,2)", size=46, color=C.you), T.pt122), (lab("distance 3", 28, C.text), T.pt122 + 1.3), (tex(r"\lambda", "=2", size=44, colors={0: C.lam}), T.pt122 + 2.0)], "dr")
    curtain(s)
