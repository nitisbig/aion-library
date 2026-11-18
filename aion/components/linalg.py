"""Classic-style linear-algebra drawing blocks for ManimLayer scores: matrices, transformed grids, panels.

Promoted from videos 006–010, where each video had its own copy.

    M = Mat([["0", r"-\\pi"], [r"\\pi", "0"]]).to_edge(UP)       # square brackets, addressable cells
    m.add(grid_lines(np.eye(2), center=(0, 0), unit=1.0, box=(-7.3, -4.2, 7.3, 4.2)))
    m.add(panel(-6.8, -3.6, -0.2, 3.6))                          # framed side-by-side view
"""

from __future__ import annotations

import numpy as np

__all__ = ["Mat", "grid_lines", "panel", "brackets", "fmt"]


def _theme():
    from aion.theme.tokens import current

    return current()


def fmt(x: float, places: int = 2) -> str:
    """A number for display: integers bare, otherwise up to `places` decimals, and never "-0".

    Example:
        fmt(2.0) == "2";  fmt(-0.0001) == "0";  fmt(2.718281) == "2.72"
    """
    v = round(float(x), places)
    if v == 0:
        return "0"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.{places}f}".rstrip("0").rstrip(".")


def brackets(height: float, gap: float, width: float | None = None, hook: float = 0.16, color=None):
    """A pair of square matrix brackets drawn as crisp polylines, `gap` apart (inner edges), `height` tall.

    Example:
        br = brackets(1.6, 2.0)
    """
    from manim import VGroup, VMobject

    th = _theme()
    w, h = width or 2.4, height / 2

    def one(sign):
        x = sign * gap / 2
        tip = x - sign * hook
        return VMobject(stroke_color=color or th.text, stroke_width=w).set_points_as_corners(
            [[tip, h, 0], [x, h, 0], [x, -h, 0], [tip, -h, 0]])
    return VGroup(one(-1), one(1))


def _mat_class():
    from manim import MathTex, Rectangle, VGroup

    class Mat(VGroup):
        """A matrix with hand-set square brackets: entries in a fixed grid, every part addressable.

        `m.br` is the brackets, `m.cols[j]` column j's entries (top to bottom), `m.cell(i, j)` one entry,
        `m.col_box(j, color)` a thin box around column j. Numbers are formatted with `fmt`; strings are TeX.
        Columns default to the theme's `ihat` / `jhat` / `khat` roles when the video defines them (else
        text color). Pass `colors=` (one color, or one per column) to override.

        Example:
            M = Mat([["0", r"-\\pi"], [r"\\pi", "0"]], colors=C.gen).move_to(UP * 2)
        """

        def __init__(self, rows, colors=None, size=None, h_buff=0.95, v_buff=0.78, pad=0.2, places=2):
            super().__init__()
            th = _theme()
            rows = [[r if isinstance(r, str) else fmt(r, places) for r in row] for row in rows]
            size = size or th.tex_size + 8
            nr, nc = len(rows), len(rows[0])
            if colors is None:
                basis = [th.roles.get(k) for k in ("ihat", "jhat", "khat")]
                colors = [b or th.text for b in basis[:nc]] if nc <= 3 else [th.text] * nc
            elif isinstance(colors, str):
                colors = [colors] * nc
            self.cells = [[MathTex(rows[i][j], font_size=size, color=colors[j]) for j in range(nc)]
                          for i in range(nr)]
            for i in range(nr):
                for j in range(nc):
                    self.cells[i][j].move_to([(j - (nc - 1) / 2) * h_buff, ((nr - 1) / 2 - i) * v_buff, 0])
            self.cols = [VGroup(*[self.cells[i][j] for i in range(nr)]) for j in range(nc)]
            self.h_buff, self.v_buff = h_buff, v_buff
            k = size / 48
            body = VGroup(*self.cols)
            hgt = max(body.height, (nr - 1) * v_buff + 0.5 * k) + 2 * pad * k
            width = max(body.width, (nc - 1) * h_buff + 0.3 * k)
            self.br = brackets(hgt, width + 2 * pad * k * 0.9, width=2.0 + 0.6 * k, hook=0.13 * k)
            self.br.move_to(body)
            self.add(self.br, *self.cols)

        def cell(self, i, j):
            return self.cells[i][j]

        def col_box(self, j, color, opacity=0.12):
            """A thin rectangle around column j, in `color`."""
            col = self.cols[j]
            return Rectangle(width=self.h_buff * 0.78, height=col.height + 0.42, stroke_color=color,
                             stroke_width=_theme().thin, fill_color=color, fill_opacity=opacity).move_to(col)

    return Mat


def __getattr__(name):            # Mat subclasses a Manim class, so build it lazily (keeps `import aion` light)
    if name == "Mat":
        cls = _mat_class()
        globals()["Mat"] = cls
        return cls
    raise AttributeError(name)


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
    """The Classic grid after the matrix M, clipped to `box` (x0, y0, x1, y1 in Manim units).

    Integer lines in `C.grid`, `minor - 1` dim lines between them in `C.grid_minor`, and the two axes in `C.axis`.
    Returns VGroup(minor, major, axes). Pass `color` for a single-color reference grid (minor lines are then
    left out). A singular M collapses its lines onto the image line, which is how a det-0 map looks.

    Example:
        g = grid_lines([[1, 1], [0, 1]], center=(0, 0), unit=1.0, box=(-7.3, -4.2, 7.3, 4.2))
    """
    from manim import Line, VGroup

    th = _theme()
    M = np.asarray(M, float)
    c = np.asarray(center, float)[:2]
    w = width or th.thin
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
                axis.add(Line(a, b, color=th.roles.get("axis", th.text), stroke_width=w * 1.5,
                              stroke_opacity=opacity))
            elif k % sub == 0:
                major.add(Line(a, b, color=color or th.roles.get("grid", th.accent), stroke_width=w,
                               stroke_opacity=opacity))
            else:
                dim.add(Line(a, b, color=th.roles.get("grid_minor", th.faint), stroke_width=w * 0.7,
                             stroke_opacity=opacity))
    return VGroup(dim, major, axis)


def panel(x0, y0, x1, y1, fill=True):
    """A framed panel: black inside, thin light border (the Classic look for side-by-side views).

    Example:
        left, right = panel(-6.9, -3.7, -0.15, 3.7), panel(0.15, -3.7, 6.9, 3.7)
    """
    from manim import Rectangle

    th = _theme()
    return Rectangle(width=x1 - x0, height=y1 - y0, stroke_color=th.roles.get("frame", th.muted),
                     stroke_width=th.thin, fill_color=th.bg, fill_opacity=1.0 if fill else 0.0
                     ).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
