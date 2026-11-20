"""Dido's beach in 3D (Chapters 5 and 7): sand, sea, the rope's plot and its area standing up as a block."""
from aion import *

from ch1 import *  # noqa: F401,F403

M = 0.2                     # world units per meter
SH = 2.2                    # the shoreline (world y)
AH = 0.011                  # block height per square meter


def corners(d, L=40.0):
    """The plot d meters deep made from L meters of rope, as map corners."""
    w = (L - 2 * d) * M / 2
    return np.array([[-w, SH], [-w, SH - d * M], [w, SH - d * M], [w, SH]])


def block(v, d, a, L=40.0, color=None):
    """The plot's area as a block standing on it."""
    P = corners(d, L)
    H = d * (L - 2 * d) * AH
    color = color or C.area
    x0, x1, y0, y1 = P[0, 0], P[2, 0], P[1, 1], P[0, 1]
    X, Y = np.meshgrid([x0, x1], [y0, y1])
    v.mesh(X, Y, np.zeros_like(X) + 0.005, color, alpha=0.3 * a, shade=False)
    if H > 0.02:
        faces = [([x0, x1], [y0, y0]), ([x1, x1], [y0, y1]), ([x0, x1], [y1, y1]), ([x0, x0], [y0, y1])]
        for xs, ys in faces:
            FX = np.array([xs, xs])
            FY = np.array([ys, ys])
            FZ = np.array([[0, 0], [H, H]])
            v.mesh(FX, FY, FZ, color, alpha=0.22 * a, shade=False)
        v.mesh(X, Y, np.full_like(X, H), color, alpha=0.4 * a, shade=False)
        top = [[x0, y0, H], [x1, y0, H], [x1, y1, H], [x0, y1, H]]
        v.line(top, color, 2.4, a, close=True)
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            v.line([[x, y, 0], [x, y, H]], color, 1.8, 0.8 * a)
    return H


def sand_and_sea(v):
    """The beach in 3D: sand, a 1 m-per-5 grid, the sea with its swell, and the shoreline."""
    X, Y = np.meshgrid([-7.5, 7.5], [-4.5, SH])
    v.mesh(X, Y, np.zeros_like(X), np.broadcast_to(rgb(C.sand) * 0.22 + rgb(C.bg) * 0.78, (2, 2, 3)), shade=False)
    X, Y = np.meshgrid([-7.5, 7.5], [SH, 6.5])
    v.mesh(X, Y, np.zeros_like(X), np.broadcast_to(rgb(C.sea) * 0.45 + rgb(C.bg) * 0.55, (2, 2, 3)), shade=False)
    for k in range(-7, 8):
        v.line([[k, -4.5, 0], [k, SH, 0]], C.grid, 1.2, 0.5)
    for k in range(-4, 3):
        v.line([[-7.5, k, 0], [7.5, k, 0]], C.grid, 1.2, 0.5)
    for dd in (0.35, 0.9, 1.6, 2.4):
        xs = np.linspace(-7.5, 7.5, 80)
        v.line(np.column_stack([xs, SH + dd + 0.06 * np.sin(1.4 * xs + 7 * dd), np.zeros_like(xs)]), C.con, 1.5, 0.45)
    v.line([[-7.5, SH, 0], [7.5, SH, 0]], C.axis, 3.0)
