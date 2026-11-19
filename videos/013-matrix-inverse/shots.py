"""Shared building blocks for "What Matrix Inverses Actually Mean" (013).

Everything is a pure function of t, and every number comes from verify.py.
- text:     tex, lab (CM sans key words), caps (CM small caps), mat_label
- plane:    plane, ref_grid, basis, varrow, live
- the key:  to_plane, key_mob, key_samples, streak_ends, streak_mob
- threads:  lines_mob, rays_mob, rays_disc
- shadows:  shadow_profile, strip_mob
- chapter 1: C0, SIMPLE_ROWS, ledger, dots_mob, lattice
- chapter 3: U9, O9, STATES, RECORD, E_TAGS, fr, rows_of, along, four_rows, home_marks, thumb
- chapter 4: readout
- chapter 5: U5, nut, mix, nutrient_plane, recipe_plane, scoop_icon, unit_bar, powder_table, target_marks, heading5, ask_x, thread
- picture:  die_pictures (sharp and blurred versions of 009's die)
"""
from fractions import Fraction
from functools import lru_cache

from PIL import Image

from aion import *
from aion.components.linalg import grid_lines, panel  # noqa: F401
from verify import (A, A_INV, BLUR_LEN, DRONE, E, HOOK, tilt, MAPPED, NULL, POWDER, REPO, S, SCOOPS, SEEN, SHAFT, SIMPLE, TARGET, TEETH,  # noqa: F401
                    WEAK, key_raster)

EASE = "easy_ease"
I2 = np.eye(2)
FRAME = (-7.4, -4.3, 7.4, 4.3)
NORMAL = np.array([-SHAFT[1], SHAFT[0]])
KEY_SCALE = 0.62
A_ROWS = [["3", "1"], ["2", "2"]]
AINV_ROWS = [[r"\frac{1}{2}", r"-\frac{1}{4}"], [r"-\frac{1}{2}", r"\frac{3}{4}"]]
S_ROWS = [["3", r"\frac{3}{2}"], ["2", "1"]]
LABEL_X = -5.25                                       # the matrices sit in a column on the left
SAFE_LEFT, SAFE_TOP = -6.6, 3.5                       # inside the safe margin


# ---------------------------------------------------------------- text
def tex(*parts, size=None, color=None, colors=None):
    """Maths in CM roman; `colors` maps part index to color."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def lab(text, size=34, color=None):
    """A key word in CM sans."""
    return Tex(r"\textsf{" + text + "}", font_size=size, color=color or C.text)


def pin(mob, top=SAFE_TOP, left=SAFE_LEFT):
    """Place a label by its top-left corner."""
    return mob.move_to([left + mob.width / 2, top - mob.height / 2, 0])


def carded(mob, buff=0.1):
    """A label on a black card, so it stays legible over grids and rays."""
    return VGroup(BackgroundRectangle(mob, color=C.bg, fill_opacity=0.92, buff=buff), mob)


def caps(text, size=56, color=None):
    """A name in CM small caps."""
    return Tex(r"\textsc{" + text + "}", font_size=size, color=color or C.text)


def mat_label(sym, rows, sym_color, colors=None, size=44, h_buff=0.9, v_buff=0.9):
    """`sym = [matrix]` on a black card. Parts: .card, .sym, .eq, .mat"""
    mat = Mat(rows, colors=colors or sym_color, size=size, h_buff=h_buff, v_buff=v_buff)
    sym_m = tex(sym, size=size + 4, color=sym_color)
    eq = tex("=", size=size + 4)
    row = VGroup(sym_m, eq, mat).arrange(RIGHT, buff=0.2)
    card = BackgroundRectangle(row, color=C.bg, fill_opacity=0.92, buff=0.14)
    g = VGroup(card, row)
    g.card, g.sym, g.eq, g.mat = card, sym_m, eq, mat
    return g


# ---------------------------------------------------------------- plane
def live(m, fn, *windows):
    """Rebuild `fn(t)` every frame inside each (start, end) window and hold it still in between."""
    merged = []
    for a, b in sorted(windows):
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    held = []
    for a, b in merged:
        if held:
            m.remove(held[-1], at=a)
        held.append(m.redraw(fn, during=(a, b)))
    return held


def plane(M, center=(0, 0), unit=1.0, box=FRAME, opacity=1.0, n=14):
    """The Classic grid moved by M."""
    return grid_lines(np.asarray(M, float), center=center, unit=unit, box=box, n=n, minor=2, opacity=opacity)


def ref_grid(opacity=1.0, box=FRAME):
    """A dim fixed grid: where the plane used to be."""
    return grid_lines(I2, center=(0, 0), unit=1.0, box=box, n=14, color=C.faint, opacity=opacity, axes=False)


def p3(v):
    return np.array([float(v[0]), float(v[1]), 0.0])


def varrow(a, b, color, width=None, tip=0.24, opacity=1.0):
    """A crisp arrow: a line and a triangular tip."""
    a, b = p3(a), p3(b)
    L = np.linalg.norm(b - a)
    if L < 1e-6:
        return VGroup()
    d = (b - a) / L
    n = np.array([-d[1], d[0], 0.0])
    tl = min(tip, 0.45 * L)
    head = Polygon(b, b - tl * d + 0.42 * tl * n, b - tl * d - 0.42 * tl * n, stroke_width=0, fill_color=color,
                   fill_opacity=opacity)
    return VGroup(Line(a, b - 0.8 * tl * d, color=color, stroke_width=width or C.stroke + 1, stroke_opacity=opacity), head)


def basis(M, center=(0, 0), unit=1.0, opacity=1.0):
    """The two basic arrows, carried by M."""
    c = np.asarray(center, float)
    return VGroup(varrow(c, c + unit * M[:, 0], C.ihat, opacity=opacity), varrow(c, c + unit * M[:, 1], C.jhat, opacity=opacity))


# ---------------------------------------------------------------- the key
def key_outline(teeth=TEETH):
    """The key's outer edge in its own frame (same shape as verify.key_polys, drawn as one line)."""
    a0 = np.arcsin(0.08 / 0.45)
    th = np.linspace(a0, 2 * np.pi - a0, 64)
    pts = [tuple(p) for p in np.c_[-1.05 + 0.45 * np.cos(th), 0.45 * np.sin(th)]]
    for i, sign in enumerate(teeth):
        x0 = 0.42 + 0.27 * i
        if sign < 0:
            pts += [(x0, -0.08), (x0, -0.42), (x0 + 0.17, -0.42), (x0 + 0.17, -0.08)]
    pts += [(1.5, -0.08), (1.5, 0.08)]
    for i, sign in reversed(list(enumerate(teeth))):
        x0 = 0.42 + 0.27 * i
        if sign > 0:
            pts += [(x0 + 0.17, 0.08), (x0 + 0.17, 0.42), (x0, 0.42), (x0, 0.08)]
    return np.array(pts)


def key_hole():
    th = np.linspace(2 * np.pi, 0, 36)
    return np.c_[-1.05 + 0.2 * np.cos(th), 0.2 * np.sin(th)]


def to_plane(p, scale=KEY_SCALE):
    """Key frame to plane: the shaft lies along (2, 1), so the teeth point exactly along the crushed direction."""
    p = np.atleast_2d(p) - np.array([0.2, 0.0])
    return scale * (p[:, [0]] * SHAFT + p[:, [1]] * NORMAL)


def _closed(q):
    q = np.vstack([q, q[:1]])
    return np.c_[q, np.zeros(len(q))]


def key_mob(M=I2, center=(0, 0), teeth=TEETH, color=None, fill=0.3, width=2.8, scale=KEY_SCALE, opacity=1.0):
    """The key after the matrix M, as one shape with a real hole."""
    color = color or C.key
    c = np.asarray(center, float)
    out = (np.asarray(M) @ to_plane(key_outline(teeth), scale).T).T + c
    hole = (np.asarray(M) @ to_plane(key_hole(), scale).T).T + c
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity, fill_color=color, fill_opacity=fill * opacity)
    v.set_points_as_corners(_closed(out))
    v.append_points(VMobject().set_points_as_corners(_closed(hole)).points)
    return v


def key_samples(teeth=TEETH, step=13, scale=KEY_SCALE):
    """A few points around the key's edge, in the plane."""
    return to_plane(key_outline(teeth)[::step], scale)


def streak_ends():
    """Where the key lands under S: the two ends of the streak."""
    s = 2 * to_plane(key_outline())[:, 0] + to_plane(key_outline())[:, 1]
    return float(s.min()) * S[:, 1], float(s.max()) * S[:, 1]


def streak_mob(color=None, width=7.0, opacity=1.0):
    a, b = streak_ends()
    return Line(p3(a), p3(b), color=color or C.shadow, stroke_width=width, stroke_opacity=opacity)


# ---------------------------------------------------------------- threads and rays
def lines_mob(P, Q, color, width=1.4, opacity=1.0):
    """Many straight lines as a single shape (cheap to rasterize)."""
    pts = []
    for a, b in zip(P, Q):
        a, b = p3(a), p3(b)
        pts += [a, a + (b - a) / 3, a + 2 * (b - a) / 3, b]
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity, fill_opacity=0)
    v.points = np.array(pts, float)
    return v


def rays_mob(color=None, spacing=0.62, width=1.2, opacity=0.5):
    """Parallel light rays along the crushed direction, across the whole frame."""
    d = NULL / np.linalg.norm(NULL)
    off = np.arange(-9.3, 9.31, spacing)
    return lines_mob([w * SHAFT - 11 * d for w in off], [w * SHAFT + 11 * d for w in off], color or C.null, width, opacity)


def rays_disc(center, radius, theta, count=11, width=1.3, opacity=0.8):
    """Parallel rays travelling in direction `theta`, clipped to a disc."""
    c = np.asarray(center, float)
    d, u = np.array([np.cos(theta), np.sin(theta)]), np.array([-np.sin(theta), np.cos(theta)])
    off = np.linspace(-0.86, 0.86, count) * radius
    half = np.sqrt(radius ** 2 - off ** 2)
    return lines_mob(c + off[:, None] * u - half[:, None] * d, c + off[:, None] * u + half[:, None] * d, C.null, width, opacity)


# ---------------------------------------------------------------- shadows
@lru_cache(maxsize=None)
def _raster():
    return key_raster(180, TEETH, angle=float(np.arctan2(SHAFT[1], SHAFT[0])))


def shadow_profile(theta, bins=30):
    """How much key each ray crosses when the light travels in direction `theta` (the real line integrals), 0 to 1."""
    r = _raster()
    n = r.shape[0]
    xs = (np.arange(n) + 0.5) / n * 3.8 - 1.9
    X, Y = np.meshgrid(xs, xs)
    across = -X * np.sin(theta) + Y * np.cos(theta)
    hist, _ = np.histogram(across, bins=bins, range=(-1.9, 1.9), weights=r)
    return hist / max(hist.max(), 1e-9)


def strip_mob(center, radius, phi, length=1.3, thick=0.17, bins=30):
    """A thin detector strip on a ring, tangent at polar angle `phi`, shaded by the key's real shadow."""
    c = np.asarray(center, float)
    d, u = np.array([np.cos(phi), np.sin(phi)]), np.array([-np.sin(phi), np.cos(phi)])
    mid = c + radius * d
    prof = shadow_profile(phi, bins)
    w = length / bins
    cells = VGroup()
    for i, v in enumerate(prof):
        if v < 0.01:
            continue
        pos = mid + u * ((i + 0.5) / bins - 0.5) * length
        cells.add(Rectangle(width=w * 1.04, height=thick, stroke_width=0, fill_color=C.shadow,
                            fill_opacity=float(v) ** 0.7).rotate(phi + PI / 2).move_to(p3(pos)))
    frame = Rectangle(width=length, height=thick, stroke_color=C.frame, stroke_width=1.0).rotate(phi + PI / 2).move_to(p3(mid))
    return VGroup(cells, frame)


# ---------------------------------------------------------------- chapter 1: the ledger and the web
C0 = np.array([1.8, 0.0])                             # the plane's origin while matrices sit in the left column
SIMPLE_ROWS = {
    "turn": ([[r"\frac{\sqrt{3}}{2}", r"-\frac{1}{2}"], [r"\frac{1}{2}", r"\frac{\sqrt{3}}{2}"]],
             [[r"\frac{\sqrt{3}}{2}", r"\frac{1}{2}"], [r"-\frac{1}{2}", r"\frac{\sqrt{3}}{2}"]]),
    "stretch": ([["2", "0"], ["0", "3"]], [[r"\frac{1}{2}", "0"], ["0", r"\frac{1}{3}"]]),
    "slide": ([["1", "1"], ["0", "1"]], [["1", "-1"], ["0", "1"]]),
}


def ledger():
    """The three easy moves and their ways back, stacked on the left. Each row has .card .tag .fwd .back"""
    rows = {}
    for name, top in zip(SIMPLE_ROWS, (3.5, 1.15, -1.2)):
        go, ret = SIMPLE_ROWS[name]
        fwd = Mat(go, colors=C.fwd, size=30, h_buff=0.86, v_buff=0.86)
        back = Mat(ret, colors=C.back, size=30, h_buff=0.86, v_buff=0.86)
        pair = VGroup(fwd, back).arrange(RIGHT, buff=0.3)
        tag = lab(name, size=30)
        row = VGroup(tag, pair).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        pin(row, top=top - 0.08, left=SAFE_LEFT + 0.08)
        card = BackgroundRectangle(row, color=C.bg, fill_opacity=0.92, buff=0.08)
        g = VGroup(card, row)
        g.card, g.tag, g.fwd, g.back = card, tag, fwd, back
        rows[name] = g
    return rows


def dots_mob(P, radius=0.05, color=None, opacity=1.0):
    """Many dots as a single shape (cheap to rasterize)."""
    v = VMobject(stroke_width=0, fill_color=color or C.home, fill_opacity=opacity)
    if len(P) == 0:
        return v
    k = 33 if radius >= 0.07 else 9                   # large dots must read as round
    th = np.linspace(0, 2 * np.pi, k)
    ring = radius * np.c_[np.cos(th), np.sin(th), np.zeros(k)]
    pts = []
    for p in P:
        r = ring + p3(p)
        for a, b in zip(r[:-1], r[1:]):
            pts += [a, a + (b - a) / 3, a + 2 * (b - a) / 3, b]
    v.points = np.array(pts, float)
    return v


def lattice(M=A, step=0.5, center=C0):
    """Half-step lattice points x (plane coordinates) where x and Mx both stay in the frame."""
    g = np.arange(-8, 8.01, step)
    x = np.array([[a, b] for a in g for b in g if a or b])
    y = (np.asarray(M) @ x.T).T
    inside = lambda q: (np.abs(q[:, 0] + center[0]) < 6.9) & (np.abs(q[:, 1] + center[1]) < 3.85)
    return x[inside(x) & inside(y)]


# ---------------------------------------------------------------- chapter 3: the four moves home
U9, O9 = 0.8, np.array([2.0, -1.0])                   # scale and origin of the plane while the arrows stand tall
STATES = [A.copy()]                                   # the bent plane after 0, 1, 2, 3, 4 moves
RECORD = [I2.copy()]                                  # the same moves played on a straight plane
for _m in E:
    STATES.append(_m @ STATES[-1])
    RECORD.append(_m @ RECORD[-1])
E_TAGS = ("slide", "slide", "squash", "slide")


def fr(x):
    """An exact entry as TeX: 3, -1, \frac{1}{2}, -\frac{1}{4}."""
    q = Fraction(float(x)).limit_denominator(16)
    if q.denominator == 1:
        return str(q.numerator)
    sign = "-" if q < 0 else ""
    return sign + r"\frac{%d}{%d}" % (abs(q.numerator), q.denominator)


def rows_of(M):
    return [[fr(v) for v in row] for row in np.asarray(M)]


def along(states, tracks, t):
    """The matrix part-way along a list of states, one track per step."""
    M = states[0].copy()
    for i, tr in enumerate(tracks):
        M += float(tr(t)) * (states[i + 1] - states[i])
    return M


def four_rows():
    """The four moves listed on the left: a key word and its matrix. Each row has .card .tag .mat"""
    rows = []
    for i, (tag, M) in enumerate(zip(E_TAGS, E)):
        mat = Mat(rows_of(M), colors=C.back, size=30, h_buff=0.86, v_buff=0.66)
        word = lab(tag, size=32, color=C.back)
        y = 2.72 - 1.5 * i
        word.move_to([SAFE_LEFT + 0.1 + word.width / 2, y, 0])
        mat.move_to([-3.75, y, 0])
        card = BackgroundRectangle(VGroup(word, mat), color=C.bg, fill_opacity=0.92, buff=0.1)
        g = VGroup(card, word, mat)
        g.card, g.tag, g.mat = card, word, mat
        rows.append(g)
    return rows


def home_marks(origin=O9, unit=U9):
    """A warm outline of where the key and the two arrows belong."""
    o = np.asarray(origin, float)
    return VGroup(key_mob(I2 * unit, center=o, color=C.home, fill=0.0, width=1.6), varrow(o, o + unit * np.array([1.0, 0.0]), C.home, width=2.2),
                  varrow(o, o + unit * np.array([0.0, 1.0]), C.home, width=2.2))


def thumb(M, cx, cy, w, h, unit, drop=0.0, n=10):
    """A framed miniature of the plane, the key and the arrows after M."""
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    c = (cx, cy - drop)
    return VGroup(plane(M, center=c, unit=unit, box=box, n=n), key_mob(np.asarray(M) * unit, center=c, width=1.8),
                  basis(M, center=c, unit=unit), panel(*box, fill=False))


# ---------------------------------------------------------------- chapter 4: live numbers
_GLYPHS = {}


def _glyph(ch, size, color):
    k = (ch, size, color)
    if k not in _GLYPHS:
        _GLYPHS[k] = tex(ch, size=size, color=color)
    return _GLYPHS[k].copy()


def readout(text, left, y, size=56, color=None):
    """A number set in fixed cells from cached glyphs, so it can change every frame without recompiling LaTeX."""
    color = color or C.text
    adv = _glyph("0", size, color).width * 1.2
    g, x = VGroup(), 0.0
    for ch in text:
        w = adv * 0.55 if ch == "." else adv
        gl = _glyph(ch, size, color)
        g.add(gl.move_to([x + w / 2, gl.height / 2, 0]))
        x += w
    g.shift(np.array([left, y - _glyph("0", size, color).height / 2, 0]))
    return g


# ---------------------------------------------------------------- chapter 5: two powders
U5 = 0.8
O_NUT, O_MIX = np.array([-0.7, -2.6]), np.array([-5.9, -2.6])
BOX_NUT, BOX_MIX = (-0.7, -2.6, 6.1, 3.0), (-5.9, -2.6, -2.54, 1.56)


def nut(v):
    """A point on the nutrient plane (grams of protein, grams of fibre)."""
    return O_NUT + U5 * np.asarray(v, float)


def mix(v):
    """A point on the recipe plane (scoops of the first, scoops of the second)."""
    return O_MIX + U5 * np.asarray(v, float)


def nutrient_plane():
    return VGroup(grid_lines(I2, center=O_NUT, unit=U5, box=BOX_NUT, n=10, minor=1, opacity=0.62),
                  lab("protein", size=32).move_to([5.75, -3.02, 0]), lab("fibre", size=32).move_to([-0.7, 3.3, 0]))


def recipe_plane():
    return VGroup(grid_lines(I2, center=O_MIX, unit=U5, box=BOX_MIX, n=10, minor=1, opacity=0.62),
                  lab("first", size=32).move_to([-3.1, -3.02, 0]), lab("second", size=32).move_to([-5.9, 1.86, 0]))


def scoop_icon(color):
    """A scoop of powder in a few strokes."""
    kw = dict(color=color, stroke_width=3.5)
    bowl = Arc(radius=0.36, start_angle=PI, angle=PI, **kw)
    rim = Line(0.36 * LEFT, 0.36 * RIGHT, **kw)
    heap = Arc(radius=0.3, start_angle=0.3, angle=PI - 0.6, **kw).stretch(0.62, 1).move_to(0.1 * UP)
    handle = Line(0.36 * RIGHT, 0.36 * RIGHT + 0.6 * np.array([np.cos(0.45), np.sin(0.45), 0.0]), **kw)
    return VGroup(bowl, rim, heap, handle)


def unit_bar(n, center, color):
    """`n` grams as a row of equal blocks, centred on `center`."""
    w, gap = 0.3, 0.07
    return VGroup(*[Square(w, stroke_width=0, fill_color=color, fill_opacity=1.0).move_to(np.asarray(center) + (k - (n - 1) / 2) * (w + gap) * RIGHT) for k in range(n)])


def powder_table():
    """Scoops across the top, nutrients down the side. Parts: .mat .rows .icons"""
    mat = Mat(A_ROWS, colors=[C.ihat, C.jhat], size=58, h_buff=1.85, v_buff=1.05, pad=0.26).move_to([-3.2, -0.25, 0])
    rows = VGroup(*[lab(w, size=34).move_to([-5.72, mat.cell(i, 0).get_y(), 0]) for i, w in enumerate(("protein", "fibre"))])
    icons = VGroup(*[scoop_icon(c).move_to([mat.cell(0, j).get_x(), 1.75, 0]) for j, c in enumerate((C.ihat, C.jhat))])
    g = VGroup(rows, icons, mat)
    g.mat, g.rows, g.icons = mat, rows, icons
    return g


def target_marks():
    """The target (7, 6) and its guides. Parts: .v .h .t7 .t6 .dot .label"""
    kw = dict(color=C.vec, stroke_width=2.2, dash_length=0.12)
    v, h = DashedLine(p3(nut((7, 0))), p3(nut(TARGET)), **kw), DashedLine(p3(nut((0, 6))), p3(nut(TARGET)), **kw)
    t7 = tex("7", size=36, color=C.vec).move_to(p3(nut((7, 0)) + np.array([0.0, -0.36])))
    t6 = tex("6", size=36, color=C.vec).move_to(p3(nut((0, 6)) + np.array([-0.32, 0.0])))
    dot = dots_mob([nut(TARGET)], radius=0.13, color=C.vec)
    label = carded(tex(r"\mathbf{b}", "=", r"(7,\,6)", size=44, colors={0: C.vec}).move_to(p3(nut(TARGET) + np.array([0.1, 0.52]))), buff=0.06)
    g = VGroup(v, h, t7, t6, dot, label)
    g.v, g.h, g.t7, g.t6, g.dot, g.label = v, h, t7, t6, dot, label
    return g


def heading5(size=52):
    return tex("A", r"\mathbf{x}", "=", r"\mathbf{b}", size=size, colors={0: C.fwd, 1: C.vec, 3: C.vec}).move_to([-3.2, 3.05, 0])


def ask_x():
    return tex(r"\mathbf{x}", "=", r"\;{?}", size=72, colors={0: C.vec, 2: C.home}).move_to([-3.2, -2.35, 0])


def thread(a, ctrl, b, color, width=4.0, tip=0.28):
    """A curved thread from a to b. Parts: .path .head (Create the path, then bring in the head)."""
    a, ctrl, b = np.asarray(a, float), np.asarray(ctrl, float), np.asarray(b, float)
    pts = [p3((1 - u) ** 2 * a + 2 * (1 - u) * u * ctrl + u ** 2 * b) for u in np.linspace(0, 1, 48)]
    d = pts[-1] - pts[-3]
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0.0])
    path = VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(pts)
    head = Polygon(pts[-1], pts[-1] - tip * d + 0.42 * tip * n, pts[-1] - tip * d - 0.42 * tip * n, stroke_width=0, fill_color=color, fill_opacity=1.0)
    g = VGroup(path, head)
    g.path, g.head = path, head
    return g


# ---------------------------------------------------------------- the picture
@lru_cache(maxsize=None)
def die_pictures():
    """(sharp, blurred) RGBA arrays of the die from 009, blurred by the steady 49-pixel camera shake."""
    photo = np.asarray(Image.open(REPO / "videos/009-what-matrices-are/assets/photo.png").convert("L"), float) / 255
    K = np.fft.fft(np.ones(BLUR_LEN) / BLUR_LEN, photo.shape[1])
    blur = np.real(np.fft.ifft(np.fft.fft(photo, axis=1) * K, axis=1))

    def rgba(img):
        g = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        return np.dstack([g, g, g, np.full_like(g, 255)])
    return rgba(photo), rgba(blur)


def plated(label):
    """A `mat_label` on a thin framed plate, for labels that sit over the 3D stage."""
    border = Rectangle(width=label.card.width, height=label.card.height, stroke_color=C.frame, stroke_width=1.6).move_to(label.card)
    label.add(border)
    label.border = border
    return label


def chapter_card(m, sym, name, start, out):
    """A chapter opener: the chapter's symbol, a brass rule drawn across, and its name in small caps."""
    title, rule = caps(name, size=56), Line([-2.3, 0, 0], [2.3, 0, 0], color=C.key, stroke_width=2.4)
    card = VGroup(sym, rule, title).arrange(DOWN, buff=0.34)
    m.play(FadeIn(sym), FadeIn(title), at=start + 0.05, dur=0.3, lead=0)
    m.play(Create(rule), at=start + 0.1, dur=0.6, ease="easy_ease", lead=0)
    m.play(FadeOut(card), at=out, dur=0.4)
