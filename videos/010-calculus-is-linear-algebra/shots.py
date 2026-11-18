"""Shared building blocks for "Calculus Is Secretly Linear Algebra" (010).

Copied from video 009 (`tex`, `words`, `fmt`, `pt`, `grid_lines`, `arrow`, `brackets`, `Mat`, `panel`, `backing`, `live`,
`rot2`), with matrix columns coloured by this video's basis roles (b1 green, b2 red). Additions: `plot` (a function's
graph as a crisp polyline) and the cast below. All numbers are computed, never typed: see storyboard.md "Running numbers".
"""
from aion import *

# ---------------------------------------------------------------- the cast (verified in scratch verify.py)
D_EXP = np.array([[1, 1], [-1, 1]], float)        # D on (e^x cos x, e^x sin x): sqrt2 * (45 deg clockwise turn), det 2
D_TRIG = np.array([[0, 1], [-1, 0]], float)       # D on (cos, sin): a clockwise quarter turn
I2 = np.eye(2)
FRAME = (-7.3, -4.2, 7.3, 4.2)                    # a little past the 14.22 x 8 frame
assert np.allclose(np.linalg.matrix_power(D_EXP, 100), -(2.0 ** 50) * I2)   # the hook: D^100 = -2^50 I


def tex(*parts, size=None, colors=None, color=None):
    """MathTex in the theme's text colour; `colors` maps part index → colour."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def words(text, size=None, color=None):
    """Plain words set in LaTeX (Computer Modern), so text and maths share one typeface."""
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def fmt(x):
    """A number for display: integers bare, otherwise up to two decimals ("-0" never appears)."""
    r = round(float(x))
    if abs(x - r) < 1e-9:
        return "0" if r == 0 else str(int(r))
    return f"{x:.2f}".rstrip("0").rstrip(".")


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


def grid_lines(M, center, unit, box, n=14, minor=2, color=None, width=None, opacity=1.0, axes=True):
    """The grid after the matrix M, clipped to `box` (x0, y0, x1, y1 in Manim units).

    Integer lines in `C.grid`, `minor - 1` dim lines between them in `C.grid_minor`, the two axes in `C.axis`.
    Pass `color` for a single-colour reference grid (e.g. `C.ghost`; minor lines are then left out).
    """
    M = np.asarray(M, float)
    c = np.asarray(center, float)[:2]
    w = width or C.thin
    sub = 1 if color else max(1, minor)
    dim, major, axis = VGroup(), VGroup(), VGroup()
    for col in (0, 1):
        d = M[:, col] * unit
        step = M[:, 1 - col] * unit / sub
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


def arrow(a, b, color, width=None, tip=0.24, opacity=1.0):
    """A crisp straight arrow between two world points (tip scaled down for short arrows)."""
    a, b = np.array([*np.asarray(a, float)[:2], 0.0]), np.array([*np.asarray(b, float)[:2], 0.0])
    L = max(np.linalg.norm(b - a), 1e-6)
    return Arrow(a, b, buff=0, color=color, stroke_width=width or C.stroke, tip_length=min(tip, 0.4 * L),
                 max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40).set_opacity(opacity)


def basis_arrows(M, center, unit, width=None):
    """i-hat and j-hat after the matrix M (the two columns), in their role colours."""
    M = np.asarray(M, float)
    c = np.asarray(center, float)[:2]
    return VGroup(*[arrow(c, c + M[:, j] * unit, col, width=width or C.stroke + 1)
                    for j, col in ((0, C.b1), (1, C.b2))])


def brackets(height, gap, width=None, hook=0.16):
    """A pair of square brackets drawn as crisp polylines: `gap` apart (inner edges), `height` tall."""
    w = width or 2.4
    h = height / 2

    def one(sign):
        x = sign * gap / 2
        tip = x - sign * hook
        return VMobject(stroke_color=C.text, stroke_width=w).set_points_as_corners(
            [[tip, h, 0], [x, h, 0], [x, -h, 0], [tip, -h, 0]])
    return VGroup(one(-1), one(1))


COLS = lambda: [C.b1, C.b2, C.text]                          # column colours, in order (basis roles)


class Mat(VGroup):
    """A matrix with hand-set square brackets: entries in a fixed grid, every part addressable.

    `m.br` brackets, `m.cols[j]` the entries of column j (top to bottom), `m.cell(i, j)`, `m.col_box(j)`.
    By default the columns take the basis colours (green, red, blue); pass `colors=` to override (e.g. all `C.data`).
    Example:
        M = Mat([["3", "1"], ["2", "2"]]).move_to(UP * 2)
    """

    def __init__(self, rows, colors=None, size=None, h_buff=0.95, v_buff=0.78, pad=0.2):
        super().__init__()
        rows = [[r if isinstance(r, str) else fmt(r) for r in row] for row in rows]
        size = size or C.tex_size + 8
        nr, nc = len(rows), len(rows[0])
        colors = colors or (COLS()[:nc] if nc <= 3 else [C.text] * nc)
        if isinstance(colors, str):
            colors = [colors] * nc
        self.cells = [[tex(rows[i][j], size=size, color=colors[j]) for j in range(nc)] for i in range(nr)]
        for i in range(nr):
            for j in range(nc):
                self.cells[i][j].move_to([(j - (nc - 1) / 2) * h_buff, ((nr - 1) / 2 - i) * v_buff, 0])
        self.cols = [VGroup(*[self.cells[i][j] for i in range(nr)]) for j in range(nc)]
        self.h_buff, self.v_buff = h_buff, v_buff
        k = size / 48
        body = VGroup(*self.cols)
        hgt = max(body.height, (nr - 1) * v_buff + 0.5 * k) + 2 * pad * k
        self.br = brackets(hgt, body.width + 2 * pad * k * 0.9, width=2.0 + 0.6 * k, hook=0.13 * k)
        self.br.move_to(body)
        self.add(self.br, *self.cols)

    def cell(self, i, j):
        return self.cells[i][j]

    def col_box(self, j, color, opacity=0.12):
        """A thin rectangle around column j, in the column's colour."""
        col = self.cols[j]
        return Rectangle(width=self.h_buff * 0.78, height=col.height + 0.42, stroke_color=color,
                         stroke_width=C.thin, fill_color=color, fill_opacity=opacity).move_to(col)


def panel(x0, y0, x1, y1):
    """A framed panel: black inside, thin light border (the reference look for side-by-side views)."""
    return Rectangle(width=x1 - x0, height=y1 - y0, stroke_color=C.frame, stroke_width=C.thin,
                     fill_color=C.bg, fill_opacity=1.0).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])


def backing(mob, pad=0.25):
    """An opaque black panel with a thin border behind HUD content, so it reads cleanly over the grid."""
    return Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_color=C.frame,
                     stroke_width=C.thin * 0.8, fill_color=C.bg, fill_opacity=1.0).move_to(mob)


# ---------------------------------------------------------------- 3D: perspective camera, lattice, lit shading

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


def backdrop(s):
    """Flat background in C.bg."""
    s.solid(C.bg, z=-200)

def finish(s):
    """Frame finish from the theme (the Classic design sets every term to zero)."""
    fx = []
    if C.bloom > 0:
        fx.append(Bloom(C.bloom, threshold=0.8))
    if C.vignette > 0 or C.grain > 0:
        fx.append(Lens(vignette=C.vignette, grain=C.grain))
    if fx:
        s.fx(*fx)


def rot2(deg):
    """The 2x2 rotation by `deg` degrees (counter-clockwise)."""
    a = np.radians(deg)
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def plot(f, x0, x1, origin, ux, uy, color, width=None, n=240, opacity=1.0, ylim=None):
    """The graph of y = f(x) for x in [x0, x1] as a crisp polyline; graph point (x, y) sits at origin + (ux x, uy y).

    `ylim` (lo, hi) clips the curve (in graph units) so steep graphs stop at the panel edge.
    Example:
        g = plot(np.sin, 0, TAU, (-3, 0), 0.5, 1.0, C.fn)
    """
    xs = np.linspace(x0, x1, n)
    ys = np.asarray(f(xs), float) * np.ones_like(xs)
    if ylim is not None:
        ys = np.clip(ys, *ylim)
    o = np.asarray(origin, float)
    pts = np.stack([o[0] + ux * xs, o[1] + uy * ys, np.zeros_like(xs)], -1)
    return VMobject(stroke_color=color, stroke_width=width or C.stroke, stroke_opacity=opacity).set_points_as_corners(pts)


# ---------------------------------------------------------------- the hook's function plane (s00 → s01)
HO, HU = (1.0, -0.3), 1.3                         # plane origin and unit (linear scale)
LOG_R0, LOG_K = 1.0, 0.022                        # log scale: radius = LOG_R0 + LOG_K * n, since |D^n f| = 2^(n/2)


def hook_dir(n):
    """Unit direction of D^n f for f = e^x sin x = (0, 1): each step turns 45 degrees clockwise."""
    a = np.radians(90.0 - 45.0 * n)
    return np.array([np.cos(a), np.sin(a)])


def hook_tip(n, w=1.0):
    """World point of the tip of D^n f: linear scale (w = 0, length (sqrt2)^n) blended into the log scale (w = 1)."""
    r = (1 - w) * HU * 2 ** (n / 2) + w * (LOG_R0 + LOG_K * n)
    return pt(HO, 1.0, r * hook_dir(n))


def log_rings(op=1.0, hi=0.0):
    """The log-scale rings at |D^n f| = 2^10 ... 2^50 (n = 20 ... 100); only the outer one is labelled, 2^50.
    `hi` brightens the 2^50 ring and its label."""
    g = VGroup()
    for k in range(1, 6):
        r = LOG_R0 + LOG_K * 20 * k
        last = k == 5
        col = C.fn if (last and hi > 0) else C.muted
        o = op * (0.3 + (0.7 * hi if last else 0.0))
        g.add(Circle(radius=r, stroke_color=col, stroke_width=C.thin, stroke_opacity=o).move_to(pt(HO, 1.0, (0, 0))))
        if last:
            lab = tex(r"2^{50}", size=30, color=col).set_opacity(op * (0.6 + 0.4 * hi))
            g.add(lab.move_to(pt(HO, 1.0, (r * 0.78 + 0.35, r * 0.62 + 0.25))))
    return g


def spiral(n1, op=1.0):
    """The faint trail of the arrow's tip on the log scale, from n = 3 to n1."""
    ns = np.linspace(3.0, max(n1, 3.0001), max(8, int(24 * (n1 - 3)) + 2))
    pts = [hook_tip(n) for n in ns]
    return VMobject(stroke_color=C.fn, stroke_width=C.thin, stroke_opacity=0.22 * op).set_points_as_corners(pts)


def plane_labels(op_cos=1.0, op_sin=1.0, size=34):
    """The two axis names of the hook plane: e^x cos x (green, right end) and e^x sin x (red, top)."""
    lc = tex(r"e^x\cos x", size=size, color=C.b1).set_opacity(op_cos)
    lc.next_to(pt(HO, HU, (3.6, 0)), UP, buff=0.18)
    ls = tex(r"e^x\sin x", size=size, color=C.b2).set_opacity(op_sin)
    ls.next_to(pt(HO, HU, (0, 2.75)), RIGHT, buff=0.2)
    return VGroup(lc, ls)


def axis_marks(op_cos=1.0, op_sin=1.0):
    """The two axes of the hook plane drawn in their basis colours (over the white axes)."""
    w = C.thin * 2.2
    return VGroup(
        Line(pt(HO, HU, (-6.2, 0)), pt(HO, HU, (4.9, 0)), color=C.b1, stroke_width=w, stroke_opacity=op_cos),
        Line(pt(HO, HU, (0, -3.6)), pt(HO, HU, (0, 3.6)), color=C.b2, stroke_width=w, stroke_opacity=op_sin))


def result_tag():
    """The hook's answer, parked small at the top left: f^(100) = -2^50 e^x sin x."""
    g = tex(r"f^{(100)}", r"=", r"-2^{50}", r"\,e^x\sin x", size=36, colors={0: C.fn, 2: C.op, 3: C.fn})
    g.move_to([-7.11 + C.margin + 0.3 + g.width / 2, 4.0 - C.margin - 0.25 - g.height / 2, 0])
    return VGroup(backing(g, pad=0.2), g)


# ---------------------------------------------------------------- chapter 1: a function as a column (s02, s03)
SO, SL = (0.0, -0.3), 4.2                         # s01's string: centre, half length (s02 starts from it flat)
GO1, GUX1, GUY1 = (-6.4, -0.2), 1.05, 1.3         # s02's sine graph: origin, units (x in [0, 2 pi])
COL_X = 3.4                                       # s02's column, centre x
COL_H = 4.0                                       # the column's body height (brackets a little taller)


def samples(n):
    """n evenly spaced sample points on [0, 2 pi] (cell centres, so no sample sits on a zero of sin)."""
    return 2 * np.pi * (np.arange(n) + 0.5) / n


def comb(xs, ys, origin, ux, uy, color, width=None, opacity=1.0):
    """Vertical sticks from the axis up to each sample (x, y) as ONE polyline (cheap even for 1000 sticks)."""
    o = np.asarray(origin, float)
    pts = []
    for x, y in zip(xs, ys):
        a = [o[0] + ux * x, o[1], 0]
        b = [o[0] + ux * x, o[1] + uy * y, 0]
        pts += [a, b, a]
    return VMobject(stroke_color=color, stroke_width=width or C.thin, stroke_opacity=opacity).set_points_as_corners(pts)


def bar_column(ys, cx, cy, height=COL_H, half=0.55, color=None, width=None, opacity=1.0):
    """A column vector drawn as one horizontal bar per entry (length ∝ value, from the centre line), top to bottom.

    With many entries the bars merge into the function's own shape, turned on its side.
    """
    n = len(ys)
    yy = cy + height / 2 - height * (np.arange(n) + 0.5) / n
    ymax = max(1e-9, np.max(np.abs(ys)))
    pts = []
    for y, v in zip(yy, ys):
        a = [cx, y, 0]
        pts += [a, [cx + half * v / ymax, y, 0], a]
    return VMobject(stroke_color=color or C.fn, stroke_width=width or C.thin, stroke_opacity=opacity
                    ).set_points_as_corners(pts)


def col_brackets(cx, cy, height=COL_H, width=0.95):
    """Square brackets around a column of the given body height, centred at (cx, cy)."""
    return brackets(height + 0.35, width).move_to([cx, cy, 0])


# ---------------------------------------------------------------- chapter 2-3: the exact matrix on cubics (s05 → s07)
D_POLY = np.array([[0, 1, 0, 0], [0, 0, 2, 0], [0, 0, 0, 3], [0, 0, 0, 0]], float)   # basis 1, x, x^2, x^3
P_COEF = np.array([2.0, 3.0, -1.0, 4.0])          # p = 2 + 3x - x^2 + 4x^3
assert np.allclose(D_POLY @ P_COEF, [3, -2, 12, 0])
POLY_C = np.array([-0.4, -1.45, 0.0])             # where the 4 x 4 sits
PCOL_X, PEQ_X, PDCOL_X = 2.05, 3.05, 4.15         # p's column, the "=", p''s column


def poly_mat():
    """The 4 x 4 matrix of d/dx on (1, x, x^2, x^3): non-zero entries in C.op, zeros faint."""
    M = Mat(D_POLY.astype(int), colors=C.faint, size=44, h_buff=0.78, v_buff=0.64).move_to(POLY_C)
    for i in range(4):
        for j in range(4):
            if D_POLY[i, j] != 0:
                M.cell(i, j).set_color(C.op)
    return M


def coef_col(v, x, color, size=44):
    """A 4-entry coefficient column (1, x, x^2, x^3 from top) at x, level with the 4 x 4."""
    return Mat(np.asarray(v).reshape(4, 1).astype(int), colors=color, size=size, v_buff=0.64).move_to(
        [x, POLY_C[1], 0])


# ---------------------------------------------------------------- chapter header: seven badges and a title (A)
TITLES = ["a function is a vector", "the derivative is a matrix", r"why $+\,C$ exists", "the derivative is a rotation",
          "eigenvectors of the derivative", "a guitar string", "the exponential of the derivative"]
OUTRO_TITLE = "where the analogy breaks"
HDR_Y, HDR_DX, HDR_T = 3.0, 1.3, 3.56                    # badge row height, spacing; title height


def badge(k, h=0.5):
    """The small symbol for chapter k (1..7), about h tall, centred on the origin."""
    if k == 1:                                            # a function as a column of numbers
        g = VGroup(col_brackets(0, 0, 1.0, width=0.55), bar_column(np.sin(samples(14)), 0, 0, height=1.0, half=0.2,
                                                                   width=2.2))
    elif k == 2:                                          # the band
        g = VGroup(Square(1.0, stroke_color=C.frame, stroke_width=1.6, fill_opacity=0),
                   Line([-0.5, 0.5, 0], [0.5, -0.5, 0], color=C.op, stroke_width=5))
    elif k == 3:
        g = tex(r"+C", size=60, color=C.null)
    elif k == 4:                                          # a quarter turn
        g = VGroup(Arc(radius=0.45, start_angle=PI / 2, angle=-PI / 2, color=C.b1, stroke_width=4).add_tip(
            tip_length=0.22, tip_width=0.22), Dot(ORIGIN, radius=0.05, color=C.text))
    elif k == 5:
        g = tex(r"\lambda", size=72, color=C.eigen)
    elif k == 6:                                          # a string's first mode, pinned
        xs = np.linspace(0, 1, 60)
        g = VGroup(VMobject(stroke_color=C.eigen, stroke_width=4, fill_opacity=0).set_points_smoothly(
            [[x - 0.5, 0.45 * np.sin(np.pi * x), 0] for x in xs]),
            *[Dot([sx, 0, 0], radius=0.05, color=C.string) for sx in (-0.5, 0.5)])
    else:
        g = tex(r"e^{hD}", size=56, color=C.op)
    return g.scale_to_fit_height(h) if g.height > g.width else g.scale_to_fit_width(h * 1.25)


def dim(mob, o):
    """Fade a badge to opacity o without turning on fills that were off (squares, open curves stay hollow)."""
    for sm in mob.family_members_with_points():
        sm.set_stroke(opacity=o * sm.get_stroke_opacity())
        if sm.get_fill_opacity() > 0:
            sm.set_fill(opacity=o * sm.get_fill_opacity())
    return mob


def header_row(lit):
    """The seven badges in a row: chapters before `lit` dim, `lit` full (and larger), later ones faint.
    lit = 0 lights all seven (outro)."""
    row = VGroup()
    for k in range(1, 8):
        b = badge(k).move_to([(k - 4) * HDR_DX, HDR_Y, 0])
        if lit == 0:
            dim(b, 0.9)
        elif k < lit:
            dim(b, 0.4)
        elif k == lit:
            b.scale(1.3)
        else:
            dim(b, 0.15)
        row.add(b)
    return row


def chapter_header(m, k, t0, hold=3.0):
    """At a chapter cut: the badge row and the chapter's title fade in, the current badge lights, then all fade.

    Fills the beat of black between chapters; gone before the chapter's first content reaches the top of the frame.
    """
    row = header_row(k)
    title = words(TITLES[k - 1] if k else OUTRO_TITLE, size=38, color=C.text)
    num = tex(str(k) if k else r"\infty", size=38, color=C.muted)
    head = VGroup(num, tex(r"\cdot", size=38, color=C.muted), title).arrange(RIGHT, buff=0.2).move_to([0, HDR_T, 0])
    m.play(LaggedStart(*[FadeIn(b, shift=0.1 * DOWN) for b in row], lag_ratio=0.07), at=t0 + 0.05, dur=0.9)
    m.play(FadeIn(head, shift=0.1 * DOWN), at=t0 + 0.4, dur=0.6)
    if k:
        m.play(Indicate(row[k - 1], color=row[k - 1].get_color(), scale_factor=1.25), at=t0 + 1.1, dur=0.8)
    m.play(FadeOut(VGroup(row, head), shift=0.1 * UP), at=t0 + hold, dur=0.5)
    return row


def cos_tracer(t, t_start, op=1.0, period=9.0):
    """s04/s05: a dot gliding along the computed derivative of sin (≈ cos) on the s04 plot, with its sample stick."""
    PO, PUX, PUY = (-3.1, -0.5), 1.0, 1.35
    x = 2 * np.pi * (((t - t_start) / period) % 1.0)
    y = np.cos(x)
    p = pt(PO, 1, (PUX * x, PUY * y))
    return VGroup(Line(pt(PO, 1, (PUX * x, 0)), p, color=C.dfn, stroke_width=C.thin, stroke_opacity=0.7 * op),
                  Dot(p, radius=0.08, color=C.dfn).set_opacity(op))
