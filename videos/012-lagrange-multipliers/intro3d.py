"""Intro kit: solid 3D props (boxes, prisms, cylinders) for the skia View3D painter, plus a shared ground grid."""
from aion import *

from ch1 import *  # noqa: F401,F403


def _face(v, P, color, alpha, shade=True, ambient=0.45):
    """One quad (4 corners in order) as a 2x2 mesh."""
    P = np.asarray(P, float)
    X = np.array([[P[0, 0], P[1, 0]], [P[3, 0], P[2, 0]]])
    Y = np.array([[P[0, 1], P[1, 1]], [P[3, 1], P[2, 1]]])
    Z = np.array([[P[0, 2], P[1, 2]], [P[3, 2], P[2, 2]]])
    v.mesh(X, Y, Z, color, alpha=alpha, shade=shade, ambient=ambient)


def roty(P, th, c):
    """Rotate points about the y axis through c."""
    P = np.asarray(P, float) - c
    co, si = np.cos(th), np.sin(th)
    return np.column_stack([co * P[:, 0] + si * P[:, 2], P[:, 1], -si * P[:, 0] + co * P[:, 2]]) + c


def box(v, c, size, color, alpha=1.0, th=0.0, pivot=None, edge=None):
    """A solid box centred at c with size (sx, sy, sz), optionally tilted by th about the y axis through pivot."""
    c = np.asarray(c, float)
    sx, sy, sz = np.asarray(size, float) / 2
    K = np.array([[x, y, z] for z in (-sz, sz) for y in (-sy, sy) for x in (-sx, sx)]) + c
    if th:
        K = roty(K, th, np.asarray(pivot if pivot is not None else c, float))
    faces = [K[list(f)] for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5))]
    for F in sorted(faces, key=lambda F: float(F.mean(0) @ v.cam.d)):
        _face(v, F, color, alpha)
    if edge is not None:
        for a, b in ((4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)):
            v.line([K[a], K[b]], edge, 1.6, 0.8 * alpha)
    return K


def cylinder(v, c, r, h, color, alpha=1.0, n=40):
    """An upright solid cylinder (a coin) standing on c."""
    c = np.asarray(c, float)
    th = np.linspace(0, TAU, n)
    X = c[0] + r * np.vstack([np.cos(th), np.cos(th)])
    Y = c[1] + r * np.vstack([np.sin(th), np.sin(th)])
    Z = c[2] + np.vstack([np.zeros(n), np.full(n, h)])
    v.mesh(X, Y, Z, color, alpha=alpha, ambient=0.5)
    rr, tt = np.meshgrid([0, r], th)
    v.mesh(c[0] + rr * np.cos(tt), c[1] + rr * np.sin(tt), np.full_like(rr, c[2] + h), color, alpha=alpha, ambient=0.6)


def prism(v, c, w, h, d, color, alpha=1.0):
    """A triangular wedge (a pivot) standing on c: base w wide, h tall, d deep."""
    c = np.asarray(c, float)
    a, b, t = c + [-w / 2, 0, 0], c + [w / 2, 0, 0], c + [0, 0, h]
    Y0, Y1 = np.array([0, -d / 2, 0]), np.array([0, d / 2, 0])
    faces = [np.array(F) for F in ([a + Y0, b + Y0, t + Y0, t + Y0], [a + Y1, b + Y1, t + Y1, t + Y1],
                                   [a + Y0, t + Y0, t + Y1, a + Y1], [b + Y0, t + Y0, t + Y1, b + Y1])]
    for F in sorted(faces, key=lambda F: float(F.mean(0) @ v.cam.d)):
        _face(v, F, color, alpha)


def ground(v, x0=-8, x1=8, y0=-8, y1=8, alpha=0.5, hide=None):
    """The blue floor grid; hide(P) -> bool mask of points to skip."""
    for j in range(int(y0), int(y1) + 1):
        P = np.column_stack([np.linspace(x0, x1, 120), np.full(120, j), np.zeros(120)])
        v.line(P, C.grid, 1.2, alpha, visible=None if hide is None else ~hide(P))
    for j in range(int(x0), int(x1) + 1):
        P = np.column_stack([np.full(120, j), np.linspace(y0, y1, 120), np.zeros(120)])
        v.line(P, C.grid, 1.2, alpha, visible=None if hide is None else ~hide(P))
