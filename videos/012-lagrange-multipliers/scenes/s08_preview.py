"""s08: what the video will show, as one flight through the mountain (the touch, the arrows, the method), then Dido's beach: the mysterious number is a stick lying on the sand."""
from aion import *

from beach3d import SH, sand_and_sea
from beats import T
from ch1 import *
from world import trail_grad

ALL = np.linspace(0, TAU, 360)
R = 40.0 * 0.2 / np.pi                        # a 40 m rope as a semicircle, in world units


def semi(n=200):
    th = np.linspace(0, np.pi, n)
    return np.column_stack([R * np.cos(th), SH - R * np.sin(th)])


@scene(T.cut_preview, T.cut_ch1)
def s08_preview(s):
    backdrop(s)
    q = BEST
    zq = float(hill(*q))
    beach = (-80, 42, 1.15, 0.0, -0.9, 30, 0.0, SH - 1.2, 0.0)
    cam = camera((T.cut_preview, (-64, 33, 1.08, 0.1, -1.0, 26, 0, 0, 0)), (T.pv_top + 0.3, (-35, 42, 1.5, 0.0, -0.6, 26, q[0] * 0.6, q[1] * 0.6, zq * 0.6)),
                 (T.pv_arrow + 0.3, (-20, 48, 2.3, 0.0, -0.4, 26, q[0], q[1], zq)), (T.pv_solve - 0.35, (-10, 46, 1.9, 0.0, -0.9, 26, q[0], q[1], zq)),
                 (T.pv_solve - 0.05, beach), (T.concrete, (-86, 46, 1.2, 0.0, -0.9, 30, 0.0, SH - 1.2, 0.0)),
                 (T.measure + 0.6, (-94, 56, 1.75, 0.0, -0.6, 30, 0.0, SH - R / 2, 0.0)), (T.cut_ch1, (-98, 58, 1.8, 0.0, -0.6, 30, 0.0, SH - R / 2, 0.0)))
    hill_a = lambda t: 1 - ramp(t, T.pv_solve - 0.45, T.pv_solve - 0.1)
    beach_a = lambda t: ramp(t, T.pv_solve, T.pv_solve + 0.45)
    gf = hill_grad(*q)
    gg = trail_grad(*q)
    lam = np.linalg.norm(gf) / np.linalg.norm(gg)

    def frame(t):
        v = view().begin(cam(t))
        a = hill_a(t)
        if a > 0.01:
            floor(v, 1.0, 0.5 * a)
            mountain(v, 1.0, a)
            contours(v, 1.0, None, 0.55 * a)
            curve(v, np.column_stack(trail(ALL)), C.con, 6.0, a)
            ka = win(t, T.pv_top - 0.2, T.pv_solve, 0.6, 0.3) * a
            if ka > 0.01:
                level(v, float(BEST_H), C.text, 4.0, ka)
            aa = ramp(t, T.pv_arrow - 0.1, T.pv_arrow + 0.6) * a
            if aa > 0.01:
                s0, s1 = up(q, 0.9 * gf / np.linalg.norm(gf) * aa)
                v.arrow(s0, s1, C.obj, width=6.0, tip=0.24)
                s0, s1 = up(q, 0.9 * gf / np.linalg.norm(gf) / lam * aa * 0.55 / 0.9 * 1.2)
                v.arrow(s0, s1, C.con, width=6.0, tip=0.22)
            bead(v, q, color=C.you, r=0.12 * a + 1e-3)
        b = beach_a(t)
        if b > 0.01:
            X, Y = np.meshgrid([-16, 16], [SH, 16])
            v.mesh(X, Y, np.full_like(X, -0.01), np.broadcast_to(rgb(C.sea) * 0.45 + rgb(C.bg) * 0.55, (2, 2, 3)), alpha=b, shade=False)
            sand_and_sea(v)
            ra = ramp(t, T.pv_solve + 0.2, T.pv_solve + 1.6)
            P = semi()
            n = max(2, int(len(P) * ra))
            fa = ramp(t, T.pv_solve + 1.4, T.pv_solve + 2.2)
            if fa > 0.01:
                X = np.vstack([P[:, 0], P[:, 0]])
                Y = np.vstack([P[:, 1], np.full(len(P), SH)])
                v.mesh(X, Y, np.full_like(X, 0.004), C.area, alpha=0.3 * fa, shade=False)
            v.line(np.column_stack([P[:n], np.full(n, 0.03)]), C.con, 6.0)
            sa = ramp(t, T.measure - 0.1, T.measure + 0.7)
            if sa > 0.01:
                y1 = SH - R * sa
                v.line([[0.0, SH, 0.06], [0.0, y1, 0.06]], C.bg, 14.0)
                v.line([[0.0, SH, 0.06], [0.0, y1, 0.06]], C.lam, 9.0)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_preview, T.cut_ch1)]))
    m = s.manim(z=5, parallax=0.0)
    zt = np.array([q[0], q[1], zq + 0.05])
    pin(m, cam, zt, backed(lab("the touch", 32, C.text), 0.1, 0.85), T.pv_top + 0.2, T.pv_arrow - 0.1, off=(0.0, -0.6))
    pin(m, cam, zt, backed(lab("the arrows", 32, C.obj), 0.1, 0.85), T.pv_arrow + 0.3, T.pv_method - 0.1, off=(0.0, -0.6))
    pin(m, cam, [0.0, SH - R - 0.2, 0.0], backed(lab("the examples", 32, C.area), 0.1, 0.85), T.pv_solve + 0.6, T.concrete - 0.2, off=(0.0, -0.45))
    pin(m, cam, [0.0, SH - R / 2, 0.06], tex(r"\lambda", size=80, color=C.lam), T.measure + 0.5, T.cut_ch1 - 0.05, off=(0.55, 0.0))
    h = s.manim(z=20, parallax=0.0)
    headline(h, backed(tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=64, colors={0: C.obj, 2: C.lam, 3: C.con}), 0.12, 0.85), T.pv_method, T.pv_solve - 0.4)
    headline(h, backed(sc("surprisingly concrete", 38, C.lam), 0.1, 0.85), T.concrete, T.cut_ch1 - 0.3)
    curtain(s, a=False, b=True)
