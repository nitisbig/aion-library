"""The clock-arithmetic cousin (s22, s29): solutions of y^2 = x^3 + x + 1 mod p as lilac dots on a p x p grid, and the
Hasse bound |A_p - p| <= 2 sqrt p checked for every prime below 5000."""
from functools import lru_cache

from aion import *

from zmath import primes_upto

P = 101
GX0, GY0, GS = -6.0, -3.3, 5.4               # the grid: left, bottom, side


def affine_count(p):
    sq = np.zeros(p, dtype=np.int64)
    np.add.at(sq, (np.arange(p, dtype=np.int64) ** 2) % p, 1)
    x = np.arange(p, dtype=np.int64)
    return int(sq[(x ** 3 + x + 1) % p].sum())


def solutions(p=P):
    """Every (x, y) with y^2 = x^3 + x + 1 (mod p), sorted by y then x."""
    x = np.arange(p)
    rhs = (x ** 3 + x + 1) % p
    pts = [(int(a), int(b)) for b in range(p) for a in x[rhs == (b * b) % p]]
    return pts


def gxy(x, y, p=P):
    c = GS / p
    return np.array([GX0 + (x + 0.5) * c, GY0 + (y + 0.5) * c, 0.0])


def grid_frame(p=P):
    """The p x p grid of pairs (x, y), its edge labels and the middle row. Parts .lines .labels .mid"""
    c = GS / p
    lines = VGroup(*[Line([GX0 + k * c, GY0, 0], [GX0 + k * c, GY0 + GS, 0]) for k in range(p + 1)],
                   *[Line([GX0, GY0 + k * c, 0], [GX0 + GS, GY0 + k * c, 0]) for k in range(p + 1)])
    lines.set_stroke(C.faint, width=0.35)
    edge = Square(side_length=GS, stroke_color=C.muted, stroke_width=1.4).move_to([GX0 + GS / 2, GY0 + GS / 2, 0])
    labels = VGroup(MathTex("0", font_size=24, color=C.muted).move_to([GX0, GY0 - 0.22, 0]),
                    MathTex(str(p - 1), font_size=24, color=C.muted).move_to([GX0 + GS, GY0 - 0.22, 0]),
                    MathTex("x", font_size=28, color=C.muted).move_to([GX0 + GS / 2, GY0 - 0.28, 0]),
                    MathTex(str(p - 1), font_size=24, color=C.muted).move_to([GX0 - 0.3, GY0 + GS, 0]),
                    MathTex("y", font_size=28, color=C.muted).move_to([GX0 - 0.25, GY0 + GS / 2, 0]))
    mid = DashedLine([GX0, GY0 + GS / 2, 0], [GX0 + GS, GY0 + GS / 2, 0], color=C.muted, stroke_width=1.2,
                     dash_length=0.08)
    g = VGroup(lines, edge, labels, mid)
    g.lines, g.edge, g.labels, g.mid = VGroup(lines, edge), edge, labels, mid
    return g


def dots(p=P):
    return VGroup(*[Dot(gxy(x, y, p), radius=0.045, color=C.ffield) for x, y in solutions(p)])


@lru_cache(maxsize=1)
def hasse_data(limit=5000):
    ps = primes_upto(limit)
    return ps.astype(float), np.array([(affine_count(int(p)) - p) / (2 * np.sqrt(p)) for p in ps])
