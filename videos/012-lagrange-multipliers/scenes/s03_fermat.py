"""s03: Fermat's rule. The curve is the profile of a ridge in 3D; a tangent plane rides it and goes flat at the top. Every flat place is a candidate."""
from scipy.optimize import brentq

from aion import *

from beats import T
from cards import card, pop
from ch1 import backed, camera, pin, ramp, rgb, seen_by, win
from intro3d import ground
from shots import E, backdrop, curtain, lab, view


def f(x):
    return 1.15 * np.sin(1.1 * x) + 0.2 * x


def df(x):
    return 1.265 * np.cos(1.1 * x) + 0.2


PEAK = brentq(df, 0.5, 2.5)
VALLEY = brentq(df, -2.5, -0.5)
UX, UZ, Z0, HW = 1.55, 1.0, 2.1, 1.5          # world x per unit, world z per unit, lift, ridge half-width
XR = 3.6


def zx(x):
    return UZ * (f(x) + Z0)


def H(X, Y):
    """Ridge height over world points (zero off the ridge)."""
    x = np.asarray(X, float) / UX
    return np.where((np.abs(Y) <= HW) & (np.abs(x) <= XR), zx(x), 0.0)


def pt(x, y=0.0, dz=0.03):
    return np.array([UX * x, y, zx(x) + dz])


@scene(T.cut_fermat, T.cut_trail)
def s03_fermat(s):
    backdrop(s)
    side = (-90, 4, 1.05, 0.0, -0.9, 60, 0, 0, 1.8)
    cam = camera((T.cut_fermat, side), (T.fermat + 2.6, side), (T.no_hold, (-70, 22, 1.08, 0.0, -0.8, 30, 0.4, 0, 1.6)),
                 (T.flat + 0.6, (-62, 26, 1.25, 0.0, -0.6, 30, UX * PEAK * 0.6, 0, 2.2)), (T.flats + 0.4, (-75, 30, 1.1, 0.0, -0.8, 30, 0, 0, 1.6)),
                 (T.cut_trail, (-82, 32, 1.08, 0.0, -0.8, 30, 0, 0, 1.6)))
    xs = np.linspace(-XR, XR, 140)
    ys = np.linspace(-HW, HW, 9)
    X, Y = np.meshgrid(UX * xs, ys)
    u = np.clip((zx(xs) - zx(-XR) * 0.4) / (zx(PEAK) - zx(-XR) * 0.4), 0, 1)
    cols = np.broadcast_to((rgb(C.obj) * (0.22 + 0.7 * u[None, :, None])), (len(ys), len(xs), 3))
    rise = lambda t: ramp(t, T.fermat + 1.2, T.fermat + 2.6)
    draw = lambda t: ramp(t, T.fermat + 0.3, T.fermat + 2.2)
    x_t = keys((T.no_hold - 0.6, -0.5), (T.flat + 0.5, PEAK), default_ease=E)

    def patch(v, x, color, a, half=0.75):
        """The tangent plane at x: a tilted square riding the ridge's crest line."""
        s_ = df(x) * UZ / UX
        q = pt(x, 0.0, 0.05)
        corners = np.array([[-half, -half], [half, -half], [half, half], [-half, half]])
        P = np.column_stack([q[0] + corners[:, 0], q[1] + corners[:, 1] * 1.4, q[2] + s_ * corners[:, 0]])
        Xp = np.array([[P[0, 0], P[1, 0]], [P[3, 0], P[2, 0]]])
        Yp = np.array([[P[0, 1], P[1, 1]], [P[3, 1], P[2, 1]]])
        Zp = np.array([[P[0, 2], P[1, 2]], [P[3, 2], P[2, 2]]])
        v.mesh(Xp, Yp, Zp, color, alpha=0.35 * a, shade=False)
        v.line(P, color, 2.4, a, close=True)
        v.line([q - [1.3, 0, 1.3 * s_], q + [1.3, 0, 1.3 * s_]], color, 5.0, a)

    def frame(t):
        v = view().begin(cam(t))
        k = rise(t)
        ground(v, -8, 8, -6, 6, 0.5, hide=lambda P: (k > 0.3) & (np.abs(P[:, 1]) <= HW) & (np.abs(P[:, 0]) <= UX * XR))
        if k > 0.01:
            v.mesh(X, Y * k + 1e-3, np.vstack([zx(xs)] * len(ys)), cols, alpha=min(1.0, 2 * k), ambient=0.45)
            for yy in ys[1:-1:2]:
                P = np.column_stack([UX * xs, np.full_like(xs, yy * k), zx(xs) + 0.015])
                v.line(P, C.bg, 1.2, 0.35, visible=seen_by(P, v.cam, H, 1.0))
        n = max(2, int(len(xs) * draw(t)))
        P = np.column_stack([UX * xs[:n], np.full(n, -HW * k - 0.01), zx(xs[:n]) + 0.02])
        v.line(P, C.obj, 6.0)
        Pc = np.column_stack([UX * xs[:n], np.zeros(n), zx(xs[:n]) + 0.03])
        v.line(Pc, C.text, 2.2, 0.6 * k, visible=seen_by(Pc, v.cam, H, 1.0))
        wa = win(t, T.no_hold - 0.8, T.cut_trail + 1.0, 0.5, 0.3)
        if wa > 0.01:
            x = float(x_t(t))
            patch(v, x, C.tang, wa)
            v.dot(pt(x, 0, 0.06), C.you, 0.12, ring=C.bg)
        va = ramp(t, T.flats + 0.5, T.flats + 1.2)
        if va > 0.01:
            patch(v, VALLEY, C.tang, va)
            v.dot(pt(VALLEY, 0, 0.06), C.you, 0.12, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_fermat, T.cut_trail)]))
    m = s.manim(z=5, parallax=0.0)
    pop(m, card("fermat", "Fermat", "c. 1636", h=2.4, tilt=-1.5, pos=[-5.4, 1.95, 0]), T.fermat + 0.9, out=T.no_hold + 0.4)
    pin(m, cam, pt(PEAK, 0, 0.1), backed(lab("flat", 36, C.tang), 0.1, 0.85), T.flat + 0.45, T.cut_trail - 0.05, off=(0.0, 0.62))
    pin(m, cam, pt(VALLEY, 0, 0.1), backed(lab("flat", 36, C.tang), 0.1, 0.85), T.flats + 0.9, T.cut_trail - 0.05, off=(0.0, 0.62))
    h = s.manim(z=20, parallax=0.0)
    cand = backed(lab("find the flat places: candidates", 36, C.you), 0.1, 0.85).move_to([0, 3.3, 0])
    h.play(FadeIn(cand, shift=0.08 * DOWN), at=T.candidates + 0.3, dur=0.5, ease=E)
    curtain(s)
