"""Chapter one's shared picture: the ten-step staircase with both forms of the definition (c01_s02 builds it,
c01_s03 opens on it)."""
from aion import *  # noqa: F403

from kit import P3, ctex, sans, staircase, tex

N, X0S, Y0S, SW, SH = 10, -5.75, -2.5, 0.7, 0.52
CXC = 4.6
DEPTH = (0.12, 0.08)                 # the ten-step staircase's back-edge offset


def lift(st, d):
    """Raise a staircase's tread values (and move its ×b tags right) clear of its back edge (stair_depth with offset d)."""
    for v in st.vals:
        v.shift(UP * (d[1] + 0.03))  # noqa: F405
    for g in st.tags:
        g.shift(RIGHT * d[0])  # noqa: F405
    return st


def stair10():
    st = staircase(N, X0S, Y0S, SW, SH, label_size=28)
    lift(st, DEPTH)
    steps_lbl = sans("steps", 22, C.steps).move_to(P3(X0S - 0.62, Y0S + N * SH + 0.45))  # noqa: F405
    e1 = ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 64)  # noqa: F405
    e2 = ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("1024", C.value), ("=", None), ("10", C.steps)], 64)  # noqa: F405
    iff = MathTex(r"\Updownarrow", font_size=48, color=C.muted)  # noqa: F405
    VGroup(e1, iff, e2).arrange(DOWN, buff=0.35).move_to(P3(CXC, 0.6))  # noqa: F405
    legend = VGroup(*[VGroup(Dot(radius=0.06, color=c), sans(w, 20, C.muted)).arrange(RIGHT, buff=0.15)  # noqa: F405
                      for c, w in ((C.base, "base"), (C.steps, "steps = log"), (C.value, "value"))])  # noqa: F405
    legend.arrange(RIGHT, buff=0.4).move_to(P3(CXC, -1.35))  # noqa: F405
    return st, steps_lbl, e1, iff, e2, legend


CHAIN_Y = -2.45


def chain_x(k):
    """x of value k (2^k) on the doubling chain along the bottom of c01_s01."""
    return -5.9 + 1.18 * k


def chain():
    """The doubling chain 1, 2, 4 … 1024 with a ×2 over each gap (c01_s01 builds it; c01_s02 lifts it onto the stairs)."""
    vals = VGroup(*[tex(str(2 ** k), 30, C.value).move_to(P3(chain_x(k), CHAIN_Y)) for k in range(N + 1)])  # noqa: F405
    tags = VGroup(*[tex(r"\times2", 20, C.base).move_to(P3(chain_x(k) + 0.59, CHAIN_Y + 0.3))  # noqa: F405
                    for k in range(N)])
    return vals, tags


def stair_depth(n, x0, y0, sw, sh, d=(0.16, 0.12), color=None):
    """A staircase's back edge and side faces, drawn behind the path so the steps read as a solid object."""
    from kit import stair_points, polyline, tint
    color = color or C.text  # noqa: F405
    pts = stair_points(n, x0, y0, sw, sh)
    dx, dy = d
    g = VGroup()  # noqa: F405
    for k in range(n + 1):                           # tread tops as faint faces
        y = y0 + k * sh
        a, b = x0 + k * sw if k else x0, x0 + (k + 1) * sw
        g.add(Polygon(P3(a, y), P3(b, y), P3(b + dx, y + dy), P3(a + dx, y + dy), stroke_width=0,  # noqa: F405
                      fill_color=C.steps, fill_opacity=0.10))  # noqa: F405
    g.add(polyline([(x + dx, y + dy) for x, y in pts], tint(color, 0.3), 1.6))
    for x, y in pts[1:]:
        g.add(Line(P3(x, y), P3(x + dx, y + dy), stroke_color=tint(color, 0.3), stroke_width=1.2))  # noqa: F405
    return g
