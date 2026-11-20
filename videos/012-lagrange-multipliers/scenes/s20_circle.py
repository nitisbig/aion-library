"""s20: x^2 y on the circle x^2 + y^2 = 3, in 3D. The circle lifted onto the surface rises and falls through six tangencies: 2, 0, 2, -2, 0, -2."""
import contourpy
from functools import lru_cache

from aion import *

from beats import T
from ch1 import *

R = np.sqrt(3)
RD = 2.05                                     # the surface's radius
SZ = 0.24                                      # world height per unit of f
ANG = np.array([np.arctan2(1, np.sqrt(2)), np.pi / 2, np.pi - np.arctan2(1, np.sqrt(2)), np.pi + np.arctan2(1, np.sqrt(2)), 1.5 * np.pi, 2 * np.pi - np.arctan2(1, np.sqrt(2))])
VALS = ["2", "0", "2", "-2", "0", "-2"]
TH = np.linspace(0, TAU, 360)


def F(x, y):
    return x * x * y


def Fz(x, y):
    return SZ * F(x, y)


def on_circle(a):
    a = np.asarray(a, float)
    x, y = R * np.cos(a), R * np.sin(a)
    return np.stack([x, y, Fz(x, y) + 0.04], -1)


@lru_cache(maxsize=1)
def _surf():
    r, th = np.meshgrid(np.linspace(0, RD, 34), np.linspace(0, TAU, 97))
    X, Y = r * np.cos(th), r * np.sin(th)
    Z = Fz(X, Y)
    zmax = SZ * 2 * RD**3 / (3 * np.sqrt(3))
    u = np.clip((Z + zmax) / (2 * zmax), 0, 1)[..., None]
    cols = rgb(C.obj) * (0.18 + 0.82 * u)
    return X, Y, Z, cols


@lru_cache(maxsize=1)
def _levels():
    xs = np.linspace(-RD, RD, 220)
    gen = contourpy.contour_generator(xs, xs, F(*np.meshgrid(xs, xs)))
    out = []
    for lv in (-4.0, -2.0, -0.8, 0.8, 2.0, 4.0):
        for p in gen.lines(lv):
            if len(p) > 6:
                out.append((lv, np.column_stack([p, np.full(len(p), SZ * lv + 0.02)])))
    return out


@scene(T.cut_circle, T.cut_ch6)
def s20_circle(s):
    backdrop(s)
    left = (-60, 34, 1.35, 2.0, -0.6, 30, 0, 0, 0)
    cam = camera(
        (T.cut_circle, (-40, 38, 1.2, 0.0, -0.5, 30, 0, 0, 0)),
        (T.arrow2, left),
        (T.y3, (-80, 40, 1.35, 2.0, -0.6, 30, 0, 0, 0)),
        (T.six + 0.2, (-90, 89.5, 1.45, 2.0, -0.1, 400, 0, 0, 0)),
        (T.walk_around, (-90, 89.5, 1.45, 0.0, -0.1, 400, 0, 0, 0)),
        (T.walk_around + 2.0, (-70, 36, 1.35, 0.0, -0.6, 30, 0, 0, 0)),
        (T.cut_ch6, (-50, 38, 1.35, 0.0, -0.6, 30, 0, 0, 0)),
    )
    rise = lambda t: ramp(t, T.extremes - 0.3, T.extremes + 1.4)
    draw = lambda t: ramp(t, T.the_circle, T.the_circle + 1.4)
    a_t = lambda t: ANG[0] + (ANG[5] - ANG[0]) * ramp(t, T.walk_around, T.max2 - 0.2)
    kiss = lambda t: win(t, T.six - 0.2, T.walk_around + 1.0, 0.6, 0.8)

    def frame(t):
        v = view().begin(cam(t))
        k = rise(t)
        X, Y, Z, cols = _surf()
        for j in range(-6, 7):
            w = np.linspace(-6.5, 6.5, 100)
            for P in (np.column_stack([np.full_like(w, j), w, np.zeros_like(w)]), np.column_stack([w, np.full_like(w, j), np.zeros_like(w)])):
                v.line(P, C.grid, 1.2, 0.5, visible=(np.hypot(P[:, 0], P[:, 1]) > RD + 0.05) & seen_by(P, v.cam, Fz, k))
        if k > 0.01:
            v.mesh(X, Y, Z * k, cols, alpha=min(1.0, 2 * k), ambient=0.45)
            for rr in np.linspace(0.45, RD, 5):
                P = np.column_stack([rr * np.cos(TH), rr * np.sin(TH), k * Fz(rr * np.cos(TH), rr * np.sin(TH)) + 0.015])
                v.line(P, C.bg, 1.2, 0.35, visible=seen_by(P, v.cam, Fz, k))
            ka = kiss(t)
            for lv, P in _levels():
                Q = P * np.array([1, 1, k])
                strong = abs(lv) == 2.0
                v.line(Q, C.text if strong and ka > 0.05 else C.obj, 3.6 if strong else 1.8, (0.55 + 0.45 * ka) if strong else 0.45, visible=seen_by(Q, v.cam, Fz, k) & (np.hypot(Q[:, 0], Q[:, 1]) <= RD))
        dr = draw(t)
        if dr > 0.01:
            n = max(2, int(len(TH) * dr))
            G = np.column_stack([R * np.cos(TH[:n]), R * np.sin(TH[:n]), np.zeros(n) + 0.01])
            v.line(G, C.con, 2.4, 0.7, visible=seen_by(G, v.cam, Fz, k))
            up_ = ramp(t, T.the_circle + 1.0, T.the_circle + 2.4)
            if up_ > 0.01:
                P = on_circle(TH[:n]) * np.array([1, 1, up_ * k])
                v.line(P, C.con, 6.0, visible=seen_by(P, v.cam, Fz, k))
                ss = TH[:n:4]
                FXm = np.vstack([R * np.cos(ss), R * np.cos(ss)])
                FYm = np.vstack([R * np.sin(ss), R * np.sin(ss)])
                FZm = np.vstack([np.zeros_like(ss), up_ * k * Fz(R * np.cos(ss), R * np.sin(ss))])
                if len(ss) > 2:
                    v.mesh(FXm, FYm, FZm, C.con, alpha=0.16, shade=False)
        da = ramp(t, T.six, T.six + 1.2)
        for i, a in enumerate(ANG):
            g = ramp(t, T.six + 0.2 * i, T.six + 0.2 * i + 0.4)
            if g > 0.01:
                v.dot(on_circle(a), C.you, 0.09 * g + 1e-3, ring=C.bg)
        wa = win(t, T.walk_around - 0.2, T.cut_ch6 + 1.0, 0.4, 0.3)
        if wa > 0.01:
            v.dot(on_circle(a_t(t)), C.text, 0.12, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_circle, T.cut_ch6)]))
    h = s.manim(z=20, parallax=0.0)
    z = 40
    stack(h, [(tex("f", "=x^2y", size=z + 6, colors={0: C.obj}), T.extremes + 0.5), (tex("g", "=x^2+y^2=3", size=z + 6, colors={0: C.con}), T.the_circle),
              (tex("2xy", "=", "2", r"\lambda", "x", size=z, colors={3: C.lam}), T.arrow2 + 0.8), (tex("x^2", "=", "2", r"\lambda", "y", size=z, colors={3: C.lam}), T.arrow2 + 1.4),
              (tex("x=0", r"\ \text{or}\ ", r"\lambda", "=y", size=z, colors={2: C.lam}), T.either), (tex(r"y=\pm1,\ x=\pm\sqrt2", size=z, color=C.text), T.y1),
              (tex(r"x=0,\ y=\pm\sqrt3", size=z, color=C.text), T.y3)], pos=(-6.75, 3.3), out=T.six + 1.5, gap=0.2)
    m = s.manim(z=5, parallax=0.0)
    span = float(T.max2 - 0.2 - T.walk_around)
    for a, val in zip(ANG, VALS):
        at = float(T.walk_around) + (a - ANG[0]) / (ANG[5] - ANG[0]) * span
        p = on_circle(a)
        pin(m, cam, p, backed(tex(val, size=44, color=C.text), 0.06, 0.85), at, T.cut_ch6 - 0.05, off=(0.0, 0.45), fin=0.3)
    pin(m, cam, [0.0, 0.0, 0.0], backed(lab("six tangencies", 32, C.you), 0.1, 0.85), T.six + 0.6, T.walk_around + 0.8, off=(0.0, 0.0))
    pin(m, cam, on_circle(ANG[0]), backed(lab("maximum", 30, C.tang), 0.1, 0.85), T.max2, T.cut_ch6 - 0.05, off=(1.3, 0.55))
    pin(m, cam, on_circle(ANG[3]), backed(lab("minimum", 30, C.wrong), 0.1, 0.85), T.min2, T.cut_ch6 - 0.05, off=(-1.2, -0.45))
    pin(m, cam, on_circle(ANG[1]), backed(lab("only a turning point", 26, C.muted), 0.1, 0.85), T.zeros, T.cut_ch6 - 0.05, off=(1.2, 0.8))
    h2 = s.manim(z=21, parallax=0.0)
    headline(h2, backed(lab("the equations give every tangency; you compare", 32, C.you), 0.1, 0.85), T.never + 0.4, T.cut_ch6 - 0.2, y=-3.4)
    curtain(s, a=True, b=True)
