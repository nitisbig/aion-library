"""Shared building blocks for the determinant video: the moving grid, basis arrows, the area they span, the matrix.

All geometry is computed from the matrix itself (columns = where i-hat and j-hat land). The look is crisp: thin
unglowed vector lines on black, a bright integer grid over a dim half-step grid, Computer Modern for all text.
"""
from aion import *

A_MAIN = np.array([[3.0, 1.0], [1.0, 2.0]])      # the running example: det = 3*2 - 1*1 = 5
A_SWAP = A_MAIN[:, ::-1].copy()                  # columns swapped: det = -5
A_ZERO = np.array([[2.0, 4.0], [1.0, 2.0]])      # columns on one line: det = 0
A_SCALE = np.array([[2.0, 0.0], [0.0, 3.0]])     # det = 6
A_SHEAR = np.array([[1.0, 1.0], [0.0, 1.0]])     # det = 1
I2 = np.eye(2)

FRAME = (-7.3, -4.2, 7.3, 4.2)                   # a little past the 14.22 x 8 frame, so grid lines run off screen
CHAPTERS = ["A matrix moves space", "One number for the stretch", "Where the formula comes from",
            "When the determinant is negative", "When the determinant is zero", "Three dimensions", "The payoff"]


def det2(A):
    """ad - bc for a 2x2 matrix."""
    A = np.asarray(A, float)
    return float(A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0])


def tex(*parts, size=None, colors=None, color=None):
    """MathTex in the theme's text colour; `colors` maps part index → colour."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def words(text, size=None, color=None):
    """Plain words set in LaTeX (Computer Modern), so text and maths share one typeface."""
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def pt(origin, unit, v):
    """World point of the grid coordinate v (2-vector) for a grid with this origin and unit."""
    o = np.asarray(origin, float)[:2]
    v = np.asarray(v, float)[:2]
    return np.array([o[0] + unit * v[0], o[1] + unit * v[1], 0.0])


def _clip(p, d, box):
    """Clip the infinite line p + s*d to the box (x0, y0, x1, y1). Returns two end points or None."""
    x0, y0, x1, y1 = box
    lo, hi = -np.inf, np.inf
    for pc, dc, a, b in ((p[0], d[0], x0, x1), (p[1], d[1], y0, y1)):
        if abs(dc) < 1e-12:
            if pc < a or pc > b:
                return None
            continue
        s0, s1 = sorted(((a - pc) / dc, (b - pc) / dc))
        lo, hi = max(lo, s0), min(hi, s1)
    if lo >= hi:
        return None
    return p + lo * d, p + hi * d


def grid_lines(A, center, unit, box, n=14, minor=2, color=None, width=None, opacity=1.0, axes=True):
    """The grid after the matrix A, clipped to `box` (x0, y0, x1, y1 in Manim units).

    Integer lines in `C.grid`, `minor - 1` dim lines between them in `C.grid_minor`, the two axes in `C.axis`.
    Pass `color` for a single-colour reference grid (minor lines are then left out).
    """
    A = np.asarray(A, float)
    c = np.asarray(center, float)[:2]
    w = width or C.thin
    sub = 1 if color else max(1, minor)
    dim, major, axis = VGroup(), VGroup(), VGroup()
    for col in (0, 1):
        d = A[:, col] * unit                       # direction of this family of lines
        step = A[:, 1 - col] * unit / sub          # offset between neighbouring lines
        if np.linalg.norm(d) < 1e-9:
            continue
        for k in range(-n * sub, n * sub + 1):
            seg = _clip(c + k * step, d, box)
            if seg is None:
                continue
            a, b = [*seg[0], 0], [*seg[1], 0]
            if axes and k == 0:
                axis.add(Line(a, b, color=C.axis, stroke_width=w * 1.5, stroke_opacity=opacity))
            elif k % sub == 0:
                major.add(Line(a, b, color=color or C.grid, stroke_width=w, stroke_opacity=opacity))
            else:
                dim.add(Line(a, b, color=C.grid_minor, stroke_width=w * 0.7, stroke_opacity=opacity))
    return VGroup(dim, major, axis)


def basis_arrows(A, center, unit, width=None):
    """i-hat and j-hat after the matrix A (the two columns), in their role colours."""
    A = np.asarray(A, float)
    c = np.array([*np.asarray(center, float)[:2], 0.0])
    out = VGroup()
    for col, colr in ((0, C.ihat), (1, C.jhat)):
        tip = c + np.array([*(A[:, col] * unit), 0.0])
        L = max(np.linalg.norm(tip - c), 1e-6)
        out.add(Arrow(c, tip, buff=0, color=colr, stroke_width=width or C.stroke + 1,
                      tip_length=min(0.26, 0.4 * L), max_tip_length_to_length_ratio=0.4,
                      max_stroke_width_to_length_ratio=40))
    return out


def span_area(A, center, unit, color=None, opacity=0.3):
    """The parallelogram spanned by the two columns of A. Colour follows the determinant's sign by default."""
    A = np.asarray(A, float)
    c = np.asarray(center, float)[:2]
    u, v = A[:, 0] * unit, A[:, 1] * unit
    d = det2(A)
    col = color or (C.area if d > 1e-9 else C.flip if d < -1e-9 else C.collapse)
    pts = [[*p, 0] for p in (c, c + u, c + u + v, c + v)]
    return Polygon(*pts, color=col, stroke_width=C.thin + 0.6, fill_color=col, fill_opacity=opacity)


def brackets(height, gap, width=None, hook=0.16):
    """A pair of square brackets drawn as crisp polylines: `gap` apart (inner edges), `height` tall."""
    w = width or 2.4
    h = height / 2

    def one(sign):
        x = sign * gap / 2
        tip = x - sign * hook                      # hooks point inward, toward the entries
        pts = [[tip, h, 0], [x, h, 0], [x, -h, 0], [tip, -h, 0]]
        return VMobject(stroke_color=C.text, stroke_width=w).set_points_as_corners(pts)
    return VGroup(one(-1), one(1))


class Mat(VGroup):
    """A matrix with hand-set brackets: entries in a fixed grid, columns coloured, every part addressable.

    `m.br` brackets, `m.cols[j]` the entries of column j (top to bottom), `m.cell(i, j)`, `m.col_box(j)`.
    Example:
        M = Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat]).move_to(UP * 2)
    """

    def __init__(self, rows, colors=None, size=None, h_buff=0.95, v_buff=0.78, pad=0.2):
        super().__init__()
        size = size or C.tex_size + 8
        nr, nc = len(rows), len(rows[0])
        colors = colors or [C.text] * nc
        self.cells = [[tex(rows[i][j], size=size, color=colors[j]) for j in range(nc)] for i in range(nr)]
        for i in range(nr):
            for j in range(nc):
                self.cells[i][j].move_to([(j - (nc - 1) / 2) * h_buff, ((nr - 1) / 2 - i) * v_buff, 0])
        self.cols = [VGroup(*[self.cells[i][j] for i in range(nr)]) for j in range(nc)]
        self.h_buff, self.v_buff = h_buff, v_buff
        k = size / 48                                  # everything scales with the type size
        body = VGroup(*self.cols)
        hgt = max(body.height, (nr - 1) * v_buff + 0.5 * k) + 2 * pad * k
        self.br = brackets(hgt, body.width + 2 * pad * k * 0.9, width=2.0 + 0.6 * k, hook=0.13 * k)
        self.br.move_to(body)
        self.add(self.br, *self.cols)

    def cell(self, i, j):
        return self.cells[i][j]

    def col_box(self, j, color, opacity=0.12):
        """A thin rectangle around column j (a slot), in the column's colour."""
        col = self.cols[j]
        return Rectangle(width=self.h_buff * 0.78, height=col.height + 0.42, stroke_color=color,
                         stroke_width=C.thin, fill_color=color, fill_opacity=opacity).move_to(col)


def live(m, fn, *windows):
    """Rebuild `fn(t)` every frame inside each (start, end) window and hold it still in between.

    Only the moving windows are re-rasterized, so long holds stay free. Returns the handles.
    """
    merged = []
    for a, b in sorted(windows):                      # overlapping or touching windows become one
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    hs = []
    for a, b in merged:
        if hs:
            m.remove(hs[-1], at=a)
        hs.append(m.redraw(fn, during=(a, b)))
    return hs


def chapter_card(m, k, t_in, t_out):
    """A quiet chapter card in Computer Modern: a small 'Chapter k' over the title."""
    num = words(f"Chapter {k}", size=30, color=C.muted)
    name = words(CHAPTERS[k - 1], size=72)
    g = VGroup(num, name).arrange(DOWN, buff=0.32)
    m.play(FadeIn(num, shift=0.12 * UP), at=t_in, dur=0.6, lead=0)
    m.play(FadeIn(name, shift=0.12 * UP), at=t_in + 0.25, dur=0.8, lead=0)
    m.play(FadeOut(g), at=t_out, dur=0.6)
    m.remove(g, at=t_out + 0.1)
    return g


def rail(m, k):
    """Progress rail, bottom-left: seven small chapter ticks, chapters before k done, k lit."""
    g = VGroup()
    for i in range(7):
        col = C.text if i + 1 == k else (C.muted if i + 1 < k else C.faint)
        g.add(Line(ORIGIN, RIGHT * 0.22, color=col, stroke_width=3))
    g.arrange(RIGHT, buff=0.08)
    g.move_to([-7.11 + C.margin, -4 + C.margin, 0], aligned_edge=LEFT)
    m.add(g)
    return g


def backing(mob, pad=0.25):
    """An opaque black panel with a thin border behind HUD content, so it reads cleanly over the grid."""
    return Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_color=C.frame,
                     stroke_width=C.thin * 0.8, fill_color=C.bg, fill_opacity=1.0).move_to(mob)


def panel(x0, y0, x1, y1):
    """A framed panel: black inside, thin light border (the reference look for side-by-side views)."""
    return Rectangle(width=x1 - x0, height=y1 - y0, stroke_color=C.frame, stroke_width=C.thin,
                     fill_color=C.bg, fill_opacity=1.0).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])


def backdrop(s):
    """Flat background in C.bg."""
    s.solid(C.bg, z=-200)


def finish(s):
    """Frame finish from the theme. The Classic design sets every term to zero, so lines stay crisp."""
    fx = []
    if C.bloom > 0:
        fx.append(Bloom(C.bloom, threshold=0.8))
    if C.vignette > 0 or C.grain > 0:
        fx.append(Lens(vignette=C.vignette, grain=C.grain))
    if fx:
        s.fx(*fx)


def glow_fx(color=None, k=1.0):
    """The design's glow, or an empty list when the design has none (Classic). Use as `fx=glow_fx()`."""
    return [Glow(color, strength=C.glow * k, radius=C.glow_radius)] if C.glow > 0 else []


def matrix_panel(rows, pos=(-5.05, 1.95), size=64, below=None, buff=0.4):
    """The top-left HUD: the matrix with its hat symbols over the columns, in a bordered black panel.

    `below` (optional) is placed under the matrix and included in the panel. Returns (M, hats, back).
    """
    M = Mat(rows, colors=[C.ihat, C.jhat], size=size).move_to([*pos, 0])
    hat_i = tex(r"\hat{\imath}", size=44, color=C.ihat).next_to(M.cols[0], UP, buff=0.42)
    hat_j = tex(r"\hat{\jmath}", size=44, color=C.jhat).next_to(M.cols[1], UP, buff=0.42)
    hat_j.align_to(hat_i, DOWN)
    parts = [M, hat_i, hat_j, M.col_box(0, C.ihat), M.col_box(1, C.jhat)]
    if below is not None:
        below.next_to(M, DOWN, buff=buff)
        parts.append(below)
    return M, VGroup(hat_i, hat_j), backing(VGroup(*parts), pad=0.3)


def num(d):
    """A determinant value for display: an integer at rest, one decimal while it moves."""
    r = round(d)
    return str(int(r)) if abs(d - r) < 0.02 else f"{d:.1f}"


def inside(poly, pts):
    """Even-odd point-in-polygon test (numpy). poly: (n, 2), pts: (m, 2) → bool (m,)."""
    poly, pts = np.asarray(poly, float), np.asarray(pts, float)
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x0, y0 = poly[:, 0][None], poly[:, 1][None]
    x1, y1 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    cross = ((y0 > y) != (y1 > y)) & (x < (x1 - x0) * (y - y0) / (y1 - y0 + 1e-12) + x0)
    return cross.sum(axis=1) % 2 == 1


def shoelace(poly):
    """Area of a simple polygon (n, 2)."""
    p = np.asarray(poly, float)
    return 0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], -1)) - np.dot(p[:, 1], np.roll(p[:, 0], -1)))


# The contiguous United States, hand-simplified (lon, lat), clockwise from the Olympic Peninsula:
# recognisable at a glance (the lakes edge smoothed for small sizes, Florida, the Gulf, Texas, Cape Cod), not survey-accurate.
_USA = [(-124.7, 48.4), (-123.2, 48.2), (-122.8, 49.0), (-95.15, 49.0), (-95.15, 49.38), (-94.8, 48.75),
        (-93.4, 48.6), (-91.5, 48.1), (-89.6, 48.0), (-92.1, 46.75), (-90.4, 46.6), (-87.6, 46.45), (-84.6, 46.5),
        (-84.0, 45.9), (-83.4, 45.0), (-83.3, 44.0), (-82.5, 43.0),
        (-83.1, 42.1), (-83.4, 41.7), (-82.0, 41.5), (-79.8, 42.2), (-79.0, 42.8), (-79.1, 43.3), (-77.0, 43.3),
        (-76.3, 44.2), (-74.7, 45.0), (-71.5, 45.0), (-70.7, 45.4), (-70.0, 46.7), (-69.2, 47.45), (-67.8, 47.1),
        (-67.8, 45.7), (-67.0, 44.8), (-68.8, 44.3), (-70.2, 43.6), (-70.7, 42.9), (-70.6, 42.3), (-70.0, 41.9),
        (-70.1, 42.05), (-69.95, 41.7), (-70.6, 41.55), (-71.9, 41.3), (-73.6, 41.0), (-74.0, 40.6),
        (-74.0, 39.7), (-74.9, 38.95), (-75.5, 39.5), (-75.1, 38.5), (-75.9, 37.2), (-76.3, 37.0),
        (-75.6, 35.9), (-75.5, 35.2), (-76.5, 34.7), (-77.9, 33.9), (-79.2, 33.2), (-80.8, 32.1), (-81.4, 30.7),
        (-81.0, 29.3), (-80.1, 26.8), (-80.4, 25.2), (-81.1, 25.1), (-81.8, 26.1), (-82.7, 27.6), (-82.8, 28.8),
        (-83.6, 29.9), (-84.9, 29.7), (-86.4, 30.4), (-88.0, 30.6), (-89.4, 30.2), (-89.2, 29.2), (-90.5, 29.1),
        (-92.3, 29.5), (-93.8, 29.7), (-95.0, 29.2), (-96.6, 28.3), (-97.4, 27.3), (-97.2, 25.9), (-99.1, 26.4),
        (-100.3, 28.0), (-101.4, 29.8), (-102.4, 29.8), (-103.1, 29.0), (-104.5, 29.6), (-106.5, 31.8),
        (-108.2, 31.8), (-108.2, 31.3), (-111.1, 31.3), (-114.8, 32.5), (-117.1, 32.5), (-118.5, 34.0),
        (-120.6, 34.6), (-121.9, 36.6), (-122.5, 37.8), (-123.8, 39.4), (-124.4, 40.4), (-124.2, 42.0),
        (-124.5, 43.4), (-124.0, 46.3)]


def _albers(lon, lat, lon0=-96.0, lat0=23.0, p1=29.5, p2=45.5):
    """Albers equal-area conic (the usual USA map projection), on the unit sphere."""
    f1, f2, f0, f = (np.radians(v) for v in (p1, p2, lat0, lat))
    n = (np.sin(f1) + np.sin(f2)) / 2
    c = np.cos(f1) ** 2 + 2 * n * np.sin(f1)
    r, r0 = np.sqrt(c - 2 * n * np.sin(f)) / n, np.sqrt(c - 2 * n * np.sin(f0)) / n
    th = n * np.radians(lon - lon0)
    return np.column_stack([r * np.sin(th), r0 - r * np.cos(th)])


def country_outline(width=2.0):
    """The contiguous USA as an (n, 2) polygon in grid units (Albers projection), centred, `width` wide.
    Long edges are densified so the 49th-parallel border bends like it does on a real map."""
    ll = np.array(_USA)
    dense = []
    for a_, b_ in zip(ll, np.roll(ll, -1, axis=0)):
        k = max(1, int(np.ceil(np.hypot(*(b_ - a_)) / 1.5)))
        dense += [a_ + (b_ - a_) * i / k for i in range(k)]
    dense = np.array(dense)
    p = _albers(dense[:, 0], dense[:, 1])
    p -= (p.max(axis=0) + p.min(axis=0)) / 2
    return p * width / (p[:, 0].max() - p[:, 0].min())


def leaf_outline(length=1.7, width=0.8, angle=30, n=48):
    """A leaf: pointed at both ends, fuller near the stem. (n, 2) polygon in grid units, centred."""
    s = np.linspace(0, 1, n)
    x = (s - 0.5) * length
    w = width / 2 * np.sin(np.pi * s) ** 0.85 * (1.15 - 0.3 * s)
    p = np.concatenate([np.column_stack([x, w]), np.column_stack([x[::-1], -w[::-1]])[1:-1]])
    a = np.radians(angle)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return p @ R.T


def circle_outline(r=0.8, n=72):
    """A circle as an (n, 2) polygon in grid units."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([r * np.cos(a), r * np.sin(a)])


def tiny_cells(poly, h=0.2):
    """Centres of the h×h grid cells whose centre lies inside `poly` (grid units)."""
    lo, hi = poly.min(axis=0), poly.max(axis=0)
    xs = np.arange(np.floor(lo[0] / h), np.ceil(hi[0] / h)) * h + h / 2
    ys = np.arange(np.floor(lo[1] / h), np.ceil(hi[1] / h)) * h + h / 2
    c = np.array([(x, y) for x in xs for y in ys])
    return c[inside(poly, c)]


LETTER_ROLE = {"a": "ihat", "c": "ihat", "b": "jhat", "d": "jhat"}


def lettered(*terms, size=None):
    """MathTex from plain terms ("(a+b)(c+d)", "-2bc"…) with a, c in i-hat's colour and b, d in j-hat's.

    Each term is its own part (t[k]), so terms can be struck out or moved one at a time. Plain characters only.
    """
    t = MathTex(*terms, font_size=size or C.tex_size, color=C.text)
    for part, s in zip(t, terms):
        chars = [ch for ch in s if not ch.isspace()]
        if len(chars) == len(part):
            for glyph, ch in zip(part, chars):
                if ch in LETTER_ROLE:
                    glyph.set_color(getattr(C, LETTER_ROLE[ch]))
    return t


def strike(mob, color=None):
    """A thin diagonal strike-through across `mob`."""
    return Line(mob.get_corner(DL) + [-0.04, 0.02, 0], mob.get_corner(UR) + [0.04, -0.02, 0],
                color=color or C.text, stroke_width=C.thin + 0.6)
