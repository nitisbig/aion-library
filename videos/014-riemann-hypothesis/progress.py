"""The proportion bar (s21, s25, s30): the fraction of zeta zeros proven to lie on the critical line, with its dated
records, and s21's "100% is not all" grid of whole numbers with the perfect squares marked."""
from math import isqrt
from types import SimpleNamespace

from aion import *

from look import caps, lab, seen, tex

BX0, BX1, BY, BH = -5.5, 5.5, 1.6, 0.45      # the bar: left, right, centre height, thickness
RECORDS = [                                  # (fraction shown, label, name, row height of the label)
    (0.0, None, r"G. H. Hardy $\cdot$ 1914", -1.15),
    (0.02, r">0", r"A. Selberg $\cdot$ 1942", -0.65),
    (1 / 3, r"1/3", r"N. Levinson $\cdot$ 1974", -0.15),
    (2 / 5, r"2/5", r"J. B. Conrey $\cdot$ 1989", 0.35),
    (5 / 12, r"5/12", r"Pratt, Robles, Zaharescu, Zeindler $\cdot$ 2020", 0.85),
]
GX0, GX1, GY0, GY1 = -5.5, 1.8, -3.3, 0.3    # the grid of whole numbers 1..N


def bx(f):
    return BX0 + (BX1 - BX0) * float(f)


def bar_frame():
    """The empty bar, its title and its ends. Parts .box .title .ends"""
    box = Rectangle(width=BX1 - BX0, height=BH, stroke_color=C.muted, stroke_width=1.6).move_to([0, BY, 0])
    title = lab("zeros proven on the line", 28, C.text)
    title.move_to([BX0 + title.width / 2, BY + BH / 2 + 0.35, 0])
    ends = VGroup(tex("0", size=30, color=C.muted).move_to([BX0 - 0.28, BY, 0]),
                  tex("1", size=30, color=C.muted).move_to([BX1 + 0.28, BY, 0]))
    g = VGroup(box, title, ends)
    g.box, g.title, g.ends = box, title, ends
    return g


def fill_mob(f):
    if f <= 0:
        return VGroup()
    return Rectangle(width=(BX1 - BX0) * f, height=BH - 0.04, stroke_width=0, fill_color=C.crit,
                     fill_opacity=seen(0.75)).move_to([BX0 + (BX1 - BX0) * f / 2, BY, 0])


def record_mob(k):
    """Record k: a leader down from the bar and its label (fraction, then name and year)."""
    f, frac, name, y = RECORDS[k]
    x = bx(f / 2 if k == 1 else f)
    leader = Line([x, BY - BH / 2, 0], [x, y, 0], color=C.faint, stroke_width=1.4)
    parts = ([tex(frac, size=30, color=C.crit)] if frac else [lab("infinitely many", 24, C.crit)])
    parts.append(caps(name, 26, C.ink))
    label = VGroup(*parts).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
    label.move_to([x + 0.12 + label.width / 2, y, 0])
    return VGroup(leader, label)


def pct_mob():
    p = tex(r"\tfrac{5}{12}\approx41.7\%", size=30)
    return p.move_to([bx(5 / 12) + 0.15 + p.width / 2, BY + BH / 2 + 0.35, 0])


def hundred_mob():
    """The rest of the bar, dashed, up to 100%."""
    r = Rectangle(width=(BX1 - BX0) * 7 / 12, height=BH - 0.04, stroke_color=C.muted, stroke_width=1.6)
    r.move_to([bx(5 / 12) + (BX1 - BX0) * 7 / 24, BY, 0])
    d = DashedVMobject(r, num_dashes=60, dashed_ratio=0.55)
    lb = tex(r"100\%", size=30, color=C.muted).move_to([BX1 - 0.4, BY + BH / 2 + 0.35, 0])
    return VGroup(d, lb)


def grid_mob(N):
    """The whole numbers 1..N as cells, row by row; the perfect squares filled pink."""
    N = int(N)
    W, H = GX1 - GX0, GY1 - GY0
    cols = max(1, round(np.sqrt(N * W / H)))
    rows = -(-N // cols)
    c = min(W / cols, H / rows)
    last = N - (rows - 1) * cols                      # cells in the last row
    sw = float(np.clip(1.4 * c / 0.4, 0.25, 1.4))
    lines = VGroup()
    for r in range(rows + 1):                           # horizontal lines
        n = cols if r < rows else last
        lines.add(Line([GX0, GY1 - r * c, 0], [GX0 + n * c, GY1 - r * c, 0]))
    for k in range(cols + 1):                           # vertical lines
        depth = rows if k <= last else rows - 1
        lines.add(Line([GX0 + k * c, GY1, 0], [GX0 + k * c, GY1 - depth * c, 0]))
    lines.set_stroke(C.faint, width=sw)
    sq = VGroup()
    side = max(0.9 * c, 0.06)
    for j in range(1, isqrt(N) + 1):
        r, k = divmod(j * j - 1, cols)
        sq.add(Square(side_length=side, stroke_width=0, fill_color=C.zero, fill_opacity=1.0)
               .move_to([GX0 + (k + 0.5) * c, GY1 - (r + 0.5) * c, 0]))
    return VGroup(lines, sq)


def counter_mob(N):
    """N, the number of squares up to N, and their share."""
    N = int(N)
    s = isqrt(N)
    rows = VGroup(
        VGroup(tex(r"N=", size=34), Integer(N, group_with_commas=True, font_size=34)).arrange(RIGHT, buff=0.15),
        VGroup(lab("squares", 28, C.zero), Integer(s, font_size=34, color=C.zero)).arrange(RIGHT, buff=0.2),
        VGroup(DecimalNumber(100 * s / N, num_decimal_places=1, font_size=34, color=C.zero),
               tex(r"\%", size=34, color=C.zero)).arrange(RIGHT, buff=0.08))
    rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
    return rows.move_to([2.4 + rows.width / 2, -0.45, 0])


def law_mobs():
    """The two conclusions under the counter. Parts .limit .notall"""
    limit = tex(r"\frac{\lfloor\sqrt N\rfloor}{N}\to0", size=34)
    notall = VGroup(tex(r"100\%", size=36), tex(r"\neq", size=36), lab("all", 32)).arrange(RIGHT, buff=0.18)
    limit.move_to([2.4 + limit.width / 2, -2.0, 0])
    notall.move_to([2.4 + notall.width / 2, -2.95, 0])
    return SimpleNamespace(limit=limit, notall=notall)


def end_frame():
    """s21's last frame as (bar-and-grid layer, label layer) lists, each in s21's draw order."""
    bar, hund, law = bar_frame(), hundred_mob(), law_mobs()
    w = [bar.box, bar.ends, fill_mob(5 / 12), hund[0], hund[1], grid_mob(10_000)]
    h = [bar.title, pct_mob(), counter_mob(10_000), law.limit, law.notall]
    return w, h
