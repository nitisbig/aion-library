"""Chapter five's shared stage: the hyperbola y = 1/x on the Classic grid, and regions under it (exact polygons that
follow the curve). c05_s01 and c05_s02 open on the same plane and curve, so the cuts are seamless.

Example:
    g, X, Y = hyper_plane(); hyper = hyperbola(X, Y)
    m.add(region(X, Y, 1, 2))
"""
import numpy as np
from aion import *  # noqa: F403

from kit import P3, plane, polyline, tex

OX, OY, U = -6.0, -2.5, 1.15
XR, YR = (0, 7.2), (0, 4.2)
CX = 4.45
COLW = 3.6


def col(e, y):
    """Fit an equation into the right column (between the plot and the safe margin) at height y."""
    if e.width > COLW:
        e.scale(COLW / e.width)
    return e.move_to(P3(CX, y))


def hyper_plane():
    g, X, Y = plane(OX, OY, U, XR, YR)
    labels = VGroup(*[tex(str(i), 22, C.muted).next_to(P3(X(i), OY), DOWN, buff=0.08) for i in range(1, 8)])  # noqa: F405
    return VGroup(g, labels), X, Y  # noqa: F405


def hyperbola(X, Y, color=None, width=3.5):
    xs = np.geomspace(1 / YR[1], XR[1], 300)
    return polyline([(X(x), Y(1 / x)) for x in xs], color or C.text, width)  # noqa: F405


def region(X, Y, a, b, color=None, opacity=0.32, n=80, sx=1.0):
    """The region under 1/x from a to b; `sx` stretches it sideways (and squashes it by 1/sx) about x = 0."""
    if b - a < 1e-4:
        return VGroup()  # noqa: F405
    xs = np.linspace(a, b, n)
    pts = [P3(X(x * sx), Y(1 / x / sx)) for x in xs] + [P3(X(b * sx), Y(0)), P3(X(a * sx), Y(0))]
    return Polygon(*pts, stroke_width=0, fill_color=color or C.area, fill_opacity=opacity)  # noqa: F405


def edge(X, Y, x, color=None, width=3):
    return Line(P3(X(x), Y(0)), P3(X(x), Y(1 / x)), stroke_color=color or C.natural, stroke_width=width)  # noqa: F405
