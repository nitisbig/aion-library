"""Chapter 1 kit: a keyed orbit camera over the 3D mountain, the mountain at any rise, surface curves and labels pinned to 3D points."""
from functools import lru_cache

import contourpy

from aion import *
from classic import *  # noqa: F401,F403
from draw3d import Cam, rgb
from shots import LEVELS, hill, hill_grad, live

# pose = (az, el, zoom, cx, cy, dist, tx, ty, tz)
OVER = (-68.0, 33.0, 1.08, 0.1, -1.0, 26.0, 0.0, 0.0, 0.0)


def sm(x):
    """Smooth 0..1 ramp (ease in and out)."""
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * x * (x * (6 * x - 15) + 10)


def ramp(t, a, b):
    """0 before a, 1 after b, eased between."""
    return sm((float(t) - float(a)) / max(1e-6, float(b) - float(a)))


def win(t, a, b, fin=0.5, fout=0.5):
    """Fades in from a, out toward b."""
    return ramp(t, a, a + fin) * (1.0 - ramp(t, b - fout, b))


def camera(*keys, orbit=0.0, follow=None):
    """A camera path through (time, pose) keys, eased between keys, with a slow extra azimuth drift in degrees per second.

    follow(t) -> (weight, point) pulls the camera's target toward a moving point."""
    ks = [(float(t), np.array(p, float)) for t, p in keys]
    t0 = ks[0][0]

    def at(t):
        t = float(t)
        p = ks[0][1]
        for (ta, pa), (tb, pb) in zip(ks, ks[1:]):
            if t >= tb:
                p = pb
            elif t > ta:
                p = pa + (pb - pa) * sm((t - ta) / (tb - ta))
                break
        az, el, zoom, cx, cy, dist, tx, ty, tz = p
        if follow is not None:
            w, q = follow(t)
            tx, ty, tz = np.array([tx, ty, tz]) * (1 - w) + np.asarray(q, float) * w
        return Cam(az=az + orbit * (t - t0), el=el, zoom=zoom, center=(cx, cy), target=(tx, ty, tz), dist=dist)
    return at


def lift(xy, k=1.0, dz=0.03):
    """Map points (n, 2) onto the surface raised by k."""
    xy = np.asarray(xy, float)
    return np.column_stack([xy[:, 0], xy[:, 1], k * hill(xy[:, 0], xy[:, 1]) + dz])


def seen_k(P, cam, k=1.0):
    """Which world points are not hidden behind the mountain of rise k."""
    P = np.asarray(P, float)
    if k < 0.02:
        return np.ones(len(P), bool)
    ss = np.linspace(0.12, 8.0, 22)[None, :, None]
    Q = P[:, None, :] + ss * cam.d[None, None, :]
    return ~np.any(k * hill(Q[..., 0], Q[..., 1]) > Q[..., 2] + 0.02, axis=1)


@lru_cache(maxsize=1)
def _grid():
    xs = np.linspace(-6.6, 6.6, 96)
    X, Y = np.meshgrid(xs, xs)
    Z = hill(X, Y)
    u = np.clip(Z / 3.05, 0, 1)[..., None]
    low, mid, top = rgb(C.bg) * 0.82 + rgb(C.obj) * 0.18, rgb(C.obj) * 0.9, rgb(C.obj) * 0.55 + rgb(C.text) * 0.45
    col = np.where(u < 0.6, low + (mid - low) * np.clip(u / 0.6, 0, 1) ** 0.9, mid + (top - mid) * np.clip((u - 0.6) / 0.4, 0, 1) ** 1.3)
    fall = np.clip((6.3 - np.hypot(X, Y)) / 2.4, 0, 1)[..., None] ** 1.4
    return X, Y, Z, col * fall


def mountain(v, k=1.0, alpha=1.0, tint=None):
    """The shaded mountain at rise k. `tint(X, Y, cols)` may recolour it (the forbidden land)."""
    X, Y, Z, cols = _grid()
    if tint is not None:
        cols = tint(X, Y, cols)
    if alpha > 0.01:
        v.mesh(X, Y, np.maximum(Z * k, 0.0), cols, alpha=alpha, ambient=0.4)


@lru_cache(maxsize=1)
def _wires():
    out = []
    s = np.linspace(-5.4, 5.4, 160)
    for c in np.arange(-4.5, 4.6, 0.75):
        for P in (np.column_stack([np.full_like(s, c), s]), np.column_stack([s, np.full_like(s, c)])):
            keep = np.hypot(P[:, 0], P[:, 1]) < 5.4
            out.append(P[keep])
    return out


def wires(v, k=1.0, alpha=0.3):
    """Graph-paper lines drawn on the surface."""
    for P in _wires():
        Q = lift(P, k, 0.02)
        v.line(Q, C.bg, 1.3, alpha, visible=seen_k(Q, v.cam, k))


@lru_cache(maxsize=1)
def _levels():
    xs = np.linspace(-6.6, 6.6, 200)
    gen = contourpy.contour_generator(xs, xs, hill(*np.meshgrid(xs, xs)))
    return [(float(lv), [p[::2] for p in gen.lines(float(lv)) if len(p) > 8]) for lv in LEVELS]


def contours(v, k=1.0, color=None, alpha=0.6, width=1.8):
    """The level curves of f, carried up to their heights by k."""
    for lv, paths in _levels():
        for p in paths:
            Q = np.column_stack([p, np.full(len(p), lv * k + 0.015)])
            v.line(Q, color or C.bg, width, alpha, visible=seen_k(Q, v.cam, k))


def ring(level):
    """The mountain's contour at any height, as map polylines."""
    xs = np.linspace(-6.6, 6.6, 150)
    return [p for p in contourpy.contour_generator(xs, xs, hill(*np.meshgrid(xs, xs))).lines(float(level)) if len(p) > 6]


def floor(v, k=1.0, alpha=0.55):
    """The blue map grid on the ground, hidden where the mountain stands."""
    w = np.linspace(-8.0, 8.0, 120)
    for j in range(-8, 9):
        for P in (np.column_stack([np.full_like(w, j), w, np.zeros_like(w)]), np.column_stack([w, np.full_like(w, j), np.zeros_like(w)])):
            on = (k * hill(P[:, 0], P[:, 1]) < 0.08) & seen_k(P, v.cam, k)
            v.line(P, C.grid, 1.2, alpha, visible=on)


def curve(v, xy, color, width=5.0, alpha=1.0, k=1.0, dz=0.04, close=False):
    """A map curve drawn on the surface, hidden where the mountain is in front."""
    Q = lift(xy, k, dz)
    v.line(Q, color, width, alpha, visible=seen_k(Q, v.cam, k), close=close)


def bead(v, xy, k=1.0, color=None, r=0.1):
    """The walker on the surface."""
    p = lift(np.atleast_2d(xy), k, 0.04)[0]
    v.dot(p, color or C.you, r, ring=C.bg)


def pin(m, cam, P, mob, a, b, off=(0.0, 0.0), fin=0.5, fout=0.5):
    """A label that follows a 3D point (P may be a function of t) on screen."""
    def fn(t):
        q = P(t) if callable(P) else P
        xy, _ = cam(t).frame(np.asarray(q, float))
        return mob.copy().move_to([xy[0] + off[0], xy[1] + off[1], 0]).set_opacity(win(t, a, b, fin, fout))
    h = live(m, fn, (a, b))
    m.remove(h[-1], at=b)


def title(s, text, at, hold=3.8):
    """The chapter's name, quietly, in small caps across the top."""
    m = s.manim(z=40, parallax=0.0)
    t = sc(text, 34, C.text).move_to([0, 3.55, 0])
    rule = Line([-1.6, 3.22, 0], [1.6, 3.22, 0], color=C.obj, stroke_width=2)
    m.play(FadeIn(t, shift=0.08 * DOWN), Create(rule), at=at, dur=0.8, ease=E, lead=0)
    m.play(FadeOut(VGroup(t, rule)), at=at + hold, dur=0.6, ease=E, lead=0)


def headline(m, mob, at, out, y=3.45):
    """One equation or phrase across the top of the frame, without a box."""
    mob.move_to([0, y, 0])
    m.play(FadeIn(mob, shift=0.08 * DOWN), at=at, dur=0.6, ease=E)
    m.play(FadeOut(mob), at=out, dur=0.5, ease=E, lead=0)
    return mob


def grad_tip(q, scale=1.05):
    """Tip of the gradient arrow in the surface's tangent plane at q: it points uphill and grows with the slope."""
    g = hill_grad(*q)
    n = float(np.linalg.norm(g)) + 1e-9
    L = scale * n ** 0.6
    return np.array([q[0] + L * g[0] / n, q[1] + L * g[1] / n, hill(*q) + L * n + 0.04])


def slab(v, h, alpha, half=3.8, center=(0.0, 0.0), color=None):
    """A horizontal square at height h: a slicing plane."""
    q0, q1 = center[0] - half, center[0] + half
    r0, r1 = center[1] - half, center[1] + half
    X, Y = np.meshgrid([q0, q1], [r0, r1])
    v.mesh(X, Y, np.full_like(X, h), color or C.text, alpha=0.14 * alpha, shade=False)
    v.line([[q0, r0, h], [q1, r0, h], [q1, r1, h], [q0, r1, h]], color or C.text, 1.6, 0.6 * alpha, close=True)


def level(v, lv, color, width=4.5, alpha=1.0, z=None):
    """The contour of f at height lv, on the surface (or laid at height z)."""
    for p in ring(lv):
        if z is None:
            Q = np.column_stack([p, np.full(len(p), lv + 0.03)])
            v.line(Q, color, width, alpha, visible=seen_k(Q, v.cam, 1.0))
        else:
            v.line(np.column_stack([p, np.full(len(p), z)]), color, width, alpha)


def walk_loop(lv):
    """The longest contour loop at height lv, resampled evenly."""
    p = max(ring(lv), key=len)
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    u = np.linspace(0, d[-1], 600)
    return np.column_stack([np.interp(u, d, p[:, 0]), np.interp(u, d, p[:, 1])])


def glass(h, a, cam, half=3.8, center=(0.0, 0.0)):
    """A tint for mountain(): land seen through a square slicing plane at height h (from this camera) looks behind glass."""
    def tint(X, Y, cols):
        Z = hill(X, Y)
        k = (h - Z) / max(cam.d[2], 1e-3)
        QX, QY = X + k * cam.d[0], Y + k * cam.d[1]
        inside = (np.abs(QX - center[0]) < half) & (np.abs(QY - center[1]) < half)
        under = ((Z < h) & inside)[..., None] * (0.2 * a)
        return cols * (1 - under) + rgb(C.text) * under
    return tint


def slab_under(v, h, alpha, half=3.8, center=(0.0, 0.0)):
    """The slicing plane's glass, drawn before the mountain so the land above it stays clear."""
    q0, q1 = center[0] - half, center[0] + half
    r0, r1 = center[1] - half, center[1] + half
    X, Y = np.meshgrid([q0, q1], [r0, r1])
    v.mesh(X, Y, np.full_like(X, h), C.text, alpha=0.14 * alpha, shade=False)


def slab_edge(v, h, alpha, half=3.8, center=(0.0, 0.0)):
    q0, q1 = center[0] - half, center[0] + half
    r0, r1 = center[1] - half, center[1] + half
    P = np.array([[q0, r0, h], [q1, r0, h], [q1, r1, h], [q0, r1, h], [q0, r0, h]])
    P = np.vstack([np.linspace(P[i], P[i + 1], 40) for i in range(4)])
    v.line(P, C.text, 1.6, 0.6 * alpha, visible=seen_k(P, v.cam, 1.0))


def up(q, w, dz=0.05):
    """A map vector w at map point q, laid into the mountain's tangent plane: returns (start, tip) in 3D."""
    q, w = np.asarray(q, float), np.asarray(w, float)
    z = hill(*q) + dz
    return np.array([q[0], q[1], z]), np.array([q[0] + w[0], q[1] + w[1], z + float(hill_grad(*q) @ w)])


def seen_by(P, cam, fn, k=1.0):
    """Which world points are not hidden behind the surface z = k fn(x, y)."""
    P = np.asarray(P, float)
    ss = np.linspace(0.12, 9.0, 24)[None, :, None]
    Q = P[:, None, :] + ss * cam.d[None, None, :]
    return ~np.any(k * fn(Q[..., 0], Q[..., 1]) > Q[..., 2] + 0.02, axis=1)


def stack(m, rows, pos=(-6.75, 3.3), edge=UL, out=None, gap=0.22):
    """Equations down a corner, each on its own dark plate (no frame), each fading in on its beat."""
    col = VGroup(*[r[0] for r in rows]).arrange(DOWN, buff=gap, aligned_edge=LEFT if edge[0] < 0 else RIGHT)
    col.move_to([pos[0], pos[1], 0], aligned_edge=edge)
    plates = []
    for mob, t in rows:
        b = backed(mob.copy(), 0.1, 0.85)
        m.play(FadeIn(b, shift=0.06 * UP), at=t, dur=0.5, ease=E)
        plates.append(b)
    if out is not None:
        m.play(*[FadeOut(b) for b in plates], at=out, dur=0.5, ease=E, lead=0)
    return plates
