"""Shared building blocks for "What Matrices Actually Are" (009).

Copied from video 006 (`tex`, `words`, `grid_lines`, `basis_arrows`, `brackets`, `Mat`, `panel`, `backing`) and from
lab 2026-11-15-det-zero-short (`Cam`, `clip_box`), plus this video's additions: lit flat shading (`shade`), the
lattice, and the lit die rendered off-screen by pyvista (`die_rgba`). All numbers are computed, never typed:
see the "Running numbers" table in storyboard.md.
"""
from functools import lru_cache
from pathlib import Path

from aion import *

# ---------------------------------------------------------------- the cast (verified in scratch check.py)
H3 = np.array([[2, 1, 0], [0, 1, 1], [1, 0, 1]], float)        # the hook box, det 3
A = np.array([[3, 1], [2, 2]], float)                           # hero: det 4, lambda 4 on (1,1), 1 on (1,-2)
QUARTER = np.array([[0, -1], [1, 0]], float)                    # i-hat -> up, j-hat -> left
GENTLE = np.array([[1, -1], [1, 2]], float)                     # ch3's example move: (2,1) -> (1,4)
VEC = np.array([2.0, 1.0])                                      # "our arrow from before" (s04)
O3, U3 = (1.8, -2.6), 0.95                                      # ch3's 2D grid: origin and step
O5, U5 = (-0.2, -2.7), 0.8                                      # ch5's 2D grid (s11, s12)
SHEAR = np.array([[1, 1], [0, 1]], float)
COLLAPSE = np.array([[2, 1], [2, 1]], float)                    # det 0, null space along (1,-2)
I2, I3 = np.eye(2), np.eye(3)
FRAME = (-7.3, -4.2, 7.3, 4.2)                                  # a little past the 14.22 x 8 frame
KEY = np.array([0.45, -0.55, 0.70]) / np.linalg.norm([0.45, -0.55, 0.70])   # the one key light (world space)


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
                    for j, col in ((0, C.ihat), (1, C.jhat))])


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


COLS = lambda: [C.ihat, C.jhat, C.khat]                        # column colours, in order


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
class Cam:
    """Perspective camera looking at the world origin: azimuth `az` about z, elevation `el` above the floor.

    `origin` is the screen point of the world origin, `unit` the screen units per world unit, `dist` the camera
    distance (perspective strength; lab det-zero-short used 11).
    """

    def __init__(self, az, el, origin=(0.0, 0.0), unit=1.0, dist=11.0):
        a, e = np.radians(az), np.radians(el)
        self.R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        self.ce, self.se = np.cos(e), np.sin(e)
        self.o, self.u, self.dist = np.asarray(origin, float), unit, dist

    def _view(self, p):
        q = self.R @ np.asarray(p, float)
        return q[0], q[2] * self.ce + q[1] * self.se, q[1] * self.ce - q[2] * self.se   # right, up, depth

    def scr(self, p):
        x, y, d = self._view(p)
        k = self.dist / (self.dist + d)
        return np.array([self.o[0] + self.u * k * x, self.o[1] + self.u * k * y, 0.0])

    def depth(self, p):
        return self._view(p)[2]

    def eye(self):
        """World-space direction from the origin toward the camera (for back-face tests and shading)."""
        return self.R.T @ np.array([0.0, -self.ce, self.se])


def clip_box(a, b, h):
    """Clip the segment a-b to the cube [-h, h]^3 (Liang-Barsky). Returns the clipped ends or None."""
    d = b - a
    lo, hi = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if abs(a[i]) > h:
                return None
            continue
        s0, s1 = sorted(((-h - a[i]) / d[i], (h - a[i]) / d[i]))
        lo, hi = max(lo, s0), min(hi, s1)
        if lo >= hi:
            return None
    return a + lo * d, a + hi * d


def lattice(cam, M=I3, n=2, box=2.6, width=None, floor_only=False):
    """The integer lattice of [-n, n]^3 carried by M, clipped to a world cube, painted far to near with depth fade."""
    segs = []
    for ax in range(3):
        o1, o2 = [a_ for a_ in range(3) if a_ != ax]
        for u in range(-n, n + 1):
            for v in range(-n, n + 1):
                if floor_only and (ax == 2 or (o2 == 2 and v != 0) or (o1 == 2 and u != 0)):
                    continue
                p0, p1 = np.zeros(3), np.zeros(3)
                p0[ax], p1[ax] = -n, n
                p0[o1] = p1[o1] = u
                p0[o2] = p1[o2] = v
                seg = clip_box(M @ p0, M @ p1, box)
                if seg is not None:
                    segs.append((cam.depth((seg[0] + seg[1]) / 2), *seg))
    out = VGroup()
    dmax = n * 2.2
    for dep, a_, b_ in sorted(segs, key=lambda r: -r[0]):
        near = float(np.clip(0.55 - 0.45 * dep / dmax, 0.15, 1.0))
        out.add(Line(cam.scr(a_), cam.scr(b_), color=C.grid if not floor_only else C.grid_minor,
                     stroke_width=(width or C.thin) * 0.75, stroke_opacity=0.8 * near))
    return out


def shade(color, normal, ambient=0.28, diffuse=0.72):
    """Lambert shading for a flat face under the key light: the colour scaled by ambient + diffuse * max(0, n·L)."""
    n = np.asarray(normal, float)
    n = n / max(np.linalg.norm(n), 1e-9)
    k = ambient + diffuse * max(0.0, float(n @ KEY))
    rgb = np.array(ManimColor(color).to_rgb()) * min(k, 1.0)
    return ManimColor(rgb)


def lit_poly(cam, pts, color, opacity=1.0, edge=None):
    """A flat 3D polygon, shaded by the key light, with a crisp edge. `pts` are world points (counter-clockwise)."""
    P = np.asarray(pts, float)
    nrm = np.cross(P[1] - P[0], P[2] - P[0])
    if nrm @ cam.eye() < 0:
        nrm = -nrm
    col = shade(color, nrm)
    return Polygon(*[cam.scr(p) for p in P], stroke_color=edge or C.frame, stroke_width=C.thin * 0.8,
                   stroke_opacity=0.9 * opacity, fill_color=col, fill_opacity=opacity)


# ---------------------------------------------------------------- the lit die (pyvista, off-screen)
PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (-1, 1), (1, -1), (1, 1)], 5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
        6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]}
DIE_FACES = {(0, 0, 1): 1, (0, 0, -1): 6, (1, 0, 0): 3, (-1, 0, 0): 4, (0, 1, 0): 2, (0, -1, 0): 5}   # sum 7


@lru_cache(maxsize=1)
def _die_meshes():
    import pyvista as pv
    body = pv.Box(bounds=(-1, 1, -1, 1, -1, 1), level=8, quads=False).triangulate()
    p = body.points
    body.points = p / np.linalg.norm(p, ord=10, axis=1, keepdims=True)        # flat faces, softly rounded edges
    body = body.compute_normals(auto_orient_normals=True)
    pips = []
    for normal, k in DIE_FACES.items():
        nrm = np.array(normal, float)
        a = np.roll(nrm, 1)
        b = np.cross(nrm, a)
        for u, v in PIPS[k]:
            c = nrm * 1.004 + 0.46 * (u * a + v * b)
            pips.append(pv.Disc(center=c, normal=nrm, inner=0, outer=0.15, c_res=40))
    return body, pv.merge(pips)


class _DieStage:
    """One persistent off-screen pyvista plotter per image size: the die's actors are re-posed, never rebuilt."""

    def __init__(self, size, die_col, pip_col):
        import pyvista as pv
        body, pips = _die_meshes()
        self.pl = pv.Plotter(off_screen=True, window_size=(size, size), lighting="none")
        self.pl.set_background("black")
        self.body = self.pl.add_mesh(body, color=die_col, smooth_shading=True, ambient=0.16, diffuse=0.8,
                                     specular=0.22, specular_power=24)
        self.pips = self.pl.add_mesh(pips, color=pip_col, ambient=0.25, diffuse=0.5)
        self.pl.add_light(pv.Light(position=tuple(KEY * 20), focal_point=(0, 0, 0), intensity=1.0))
        self.pl.add_light(pv.Light(position=(-12, 6, 4), focal_point=(0, 0, 0), intensity=0.22))

    def shot(self, M, az, el, zoom, offset):
        T4 = np.eye(4)
        T4[:3, :3] = np.asarray(M, float)
        T4[:3, 3] = np.asarray(offset, float)
        self.body.user_matrix = T4
        self.pips.user_matrix = T4
        a, e = np.radians(az), np.radians(el)
        R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        eye = R.T @ np.array([0.0, -np.cos(e), np.sin(e)])                   # same convention as Cam.eye()
        cam = self.pl.camera
        cam.position, cam.focal_point, cam.up = tuple(eye * 11.0), (0, 0, 0), (0, 0, 1)
        cam.view_angle = 30.0 / zoom
        self.pl.reset_camera_clipping_range()
        self.pl.render()
        return np.ascontiguousarray(self.pl.screenshot(None, transparent_background=True, return_img=True))


def _die_serve(fd, die_col, pip_col):
    """Child process loop: it owns the only VTK/GL context, so pyvista never disturbs the compositor's GL state."""
    from multiprocessing.connection import Connection
    conn = Connection(fd)
    stages = {}
    while True:
        try:
            msg = conn.recv()
        except EOFError:
            break
        M, az, el, size, zoom, offset = msg
        if size not in stages:
            stages[size] = _DieStage(size, die_col, pip_col)
        img = stages[size].shot(M, az, el, zoom, offset)
        conn.send((img.shape, img.tobytes()))


_WORKER = {}


def _die_conn():
    if "conn" not in _WORKER:
        import socket
        import subprocess
        import sys
        from multiprocessing.connection import Connection
        a, b = socket.socketpair()
        proc = subprocess.Popen([sys.executable, __file__, "--die-worker", str(b.fileno()), str(C.die), str(C.pip)],
                                pass_fds=(b.fileno(),), stdout=subprocess.DEVNULL)
        b.close()
        _WORKER.update(conn=Connection(a.detach()), proc=proc)
    return _WORKER["conn"]


@lru_cache(maxsize=8)
def _die_cached(key):
    conn = _die_conn()
    conn.send(key)
    shape, buf = conn.recv()
    return np.frombuffer(buf, np.uint8).reshape(shape)


def die_rgba(M=I3, az=-35.0, el=24.0, size=720, zoom=1.0, gray=False, offset=(0, 0, 0)):
    """The die after the 3x3 matrix M (then moved by `offset`), lit by the key light, as RGBA uint8 (transparent).

    The camera matches `Cam(az, el, dist=11)`: azimuth about z, elevation above the floor, looking at the origin.
    The image spans `die_height(unit, zoom)` screen units when the Cam has that `unit`. Rendered by pyvista in a
    child process (its own GL context); the last few poses are cached.
    Example:
        s.add(FramesLayer(lambda t: die_rgba(spin(t)), height=die_height(cam.u, 1.0), pos=tuple(cam.o)))
    """
    M = tuple(map(tuple, np.round(np.asarray(M, float), 9)))
    img = _die_cached((M, float(az), float(el), int(size), float(zoom), tuple(map(float, offset))))
    if gray:
        g = (img[..., :3] @ [0.299, 0.587, 0.114]).astype(np.uint8)
        img = np.dstack([g, g, g, img[..., 3]])
    return img


def die_height(unit, zoom=1.0):
    """Screen height of a die_rgba image so it lines up with a Cam of this `unit` (pyvista frustum at the origin)."""
    return 2 * 11.0 * np.tan(np.radians(15.0 / zoom)) * unit


# ---------------------------------------------------------------- scene plumbing (from 006)
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
    """Frame finish from the theme. The Classic design sets every term to zero, so lines stay crisp."""
    fx = []
    if C.bloom > 0:
        fx.append(Bloom(C.bloom, threshold=0.8))
    if C.vignette > 0 or C.grain > 0:
        fx.append(Lens(vignette=C.vignette, grain=C.grain))
    if fx:
        s.fx(*fx)


def hat_at(M, j, origin, unit, off=0.42):
    """Label spot beside the tip of column j of the 2x2 M (a grid at origin/unit), off to the side away from the other arrow."""
    d = np.asarray(M, float)[:, j]
    d = d / max(np.linalg.norm(d), 1e-9)
    side = np.array([d[1], -d[0]]) if j == 0 else np.array([-d[1], d[0]])
    return pt(origin, unit, np.asarray(M, float)[:, j]) + np.array([*(off * side + 0.12 * d), 0])


def rot3(axis, deg):
    """The 3x3 rotation by `deg` degrees about world axis 0 (x), 1 (y) or 2 (z), right-handed."""
    a = np.radians(deg)
    c, s_ = np.cos(a), np.sin(a)
    i, j = [(1, 2), (2, 0), (0, 1)][axis]
    R = np.eye(3)
    R[i, i], R[i, j], R[j, i], R[j, j] = c, -s_, s_, c
    return R


def top_face(M):
    """Pips on the face that points up (+z) after the die is moved by M."""
    for n, k in DIE_FACES.items():
        if (np.asarray(M, float) @ np.array(n, float))[2] > 0.5:
            return k


def unit_square(M, origin=None, unit=None, opacity=0.35):
    """The unit square after M (gold, crisp edge) on the grid at origin/unit (default: chapter 5's grid)."""
    origin = O5 if origin is None else origin
    unit = U5 if unit is None else unit
    c = [pt(origin, unit, np.asarray(M, float) @ np.array(v, float)) for v in ((0, 0), (1, 0), (1, 1), (0, 1))]
    return Polygon(*c, stroke_color=C.area, stroke_width=C.stroke - 1, fill_color=C.area, fill_opacity=opacity)


def rot2(deg):
    """The 2x2 rotation by `deg` degrees (counter-clockwise)."""
    a = np.radians(deg)
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def rot3z(deg):
    """The 3x3 rotation by `deg` degrees about the vertical (z) axis."""
    R = np.eye(3)
    R[:2, :2] = rot2(deg)
    return R


# ---------------------------------------------------------------- progress rail (top-right, one badge per chapter)
def _badges():
    return [tex(r"[\;\,]", size=26), tex(r"\#", size=24, color=C.grid),
            tex(r"\hat{\imath}", r"\hat{\jmath}", r"\hat{k}", size=22, colors={0: C.ihat, 1: C.jhat, 2: C.khat}),
            tex("AB", size=24), tex(r"A^{-1}", size=24), tex(r"\lambda", size=26, color=C.eigen),
            tex(r"U\Sigma V^{\top}", size=20, color=C.sigma)]


def badge(k):
    """Badge k (1-7) of the progress rail, in its rail slot: a thin frame with the chapter's symbol."""
    b = _badges()[k - 1]
    fr = Rectangle(width=0.62, height=0.4, stroke_color=C.frame, stroke_width=1.0)
    b.scale_to_fit_width(min(b.width, 0.52))
    if b.height > 0.3:
        b.scale_to_fit_height(0.3)
    g = VGroup(fr, b.move_to(fr))
    x1, y1 = 7.11 - C.margin, 4.0 - C.margin
    g.move_to([x1 - 0.31 - (7 - k) * 0.68, y1 - 0.2, 0])      # fixed slots, read left to right
    return g


def rail(m, have, drop=None):
    """Badges 1..`have` sit in the rail (top-right, seven fixed slots); `drop=(k, t)` springs badge k in at t."""
    slots = VGroup(*[badge(k)[0].set_stroke(C.faint) for k in range(have + 1, 8)])   # empty slots, faint
    out = VGroup(*[badge(k) for k in range(1, have + 1)])
    m.add(slots, out)
    if drop:
        k, t = drop
        b = badge(k)
        m.play(FadeIn(b, shift=0.35 * DOWN), at=t, dur=0.7, ease="out_back")
    return out


# ---------------------------------------------------------------- the picture (s03, s18)
PHOTO = Path(__file__).parent / "assets" / "photo.png"


def photo():
    """The video's picture: a 480 x 480 grayscale frame of the lit die, as floats in [0, 1] (cached in assets/).

    It is rendered once by the die worker (pose: a little turned, seen from above) over black, then saved, so s03 and
    s18 read the same matrix. Delete assets/photo.png to re-render.
    """
    from PIL import Image
    if not PHOTO.exists():
        img = die_rgba(rot3z(-10), az=-35.0, el=30.0, size=480, zoom=1.7, gray=True)
        a = img[..., 3:4].astype(float) / 255
        g = (img[..., 0:1].astype(float) * a)[..., 0]
        Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).save(PHOTO)
    return np.asarray(Image.open(PHOTO), float) / 255


@lru_cache(maxsize=1)
def photo_svd():
    """(U, s, Vt) of the picture."""
    return np.linalg.svd(photo(), full_matrices=False)


def rank_k(k):
    """The picture rebuilt from its k biggest layers sigma_i u_i v_i^T, as an RGBA uint8 image (clipped to [0, 1])."""
    U, s_, Vt = photo_svd()
    g = np.clip((U[:, :k] * s_[:k]) @ Vt[:k], 0, 1) if k > 0 else np.zeros((480, 480))
    v = (g * 255).astype(np.uint8)
    return np.dstack([v, v, v, np.full_like(v, 255)])


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "--die-worker":
    import sys
    _die_serve(int(sys.argv[2]), sys.argv[3], sys.argv[4])


# ---------------------------------------------------------------- ch1's three equations, parked for later (s02 → s03)
SYS = np.array([[1, 1, 1], [1, -1, 2], [2, 1, -1]], float)    # x + y + z = 4, x - y + 2z = 1, 2x + y - z = 3
RHS = np.array([4.0, 1.0, 3.0])                                # det -7 ≠ 0, solution (1, 2, 1) (s13)
assert np.allclose(SYS @ [1, 2, 1], RHS)


def system_mats(size=60):
    """The coefficient matrix (C.data) and the right-hand side column (C.target), side by side, centred at 0."""
    cm = Mat(SYS.astype(int), colors=C.data, size=size, h_buff=1.0 * size / 60, v_buff=0.8 * size / 60)
    rm = Mat(RHS.reshape(3, 1).astype(int), colors=C.target, size=size, v_buff=0.8 * size / 60)
    return VGroup(cm, rm).arrange(RIGHT, buff=0.45 * size / 60)


def parked_system():
    """(backing, matrices) of the system parked at the lower left, as s02 leaves it and s03 keeps it."""
    g = system_mats(60).scale(0.5)
    g.move_to([-7.11 + C.margin + 0.35 + g.width / 2, -4.0 + C.margin + 0.35 + g.height / 2, 0])
    return backing(g, pad=0.22), g


# ---------------------------------------------------------------- what linear moves can't do (s04, s05)
def wobble(p, w):
    """A non-linear tangle of grid coordinates p (..., 2), faded in by w (what most machines would do)."""
    x, y = p[..., 0], p[..., 1]
    return w * np.stack([0.55 * np.sin(1.3 * y + 0.5 * x), 0.5 * np.sin(1.1 * x - 0.7 * y + 1.0)], -1)


def tangle(M, w, p):
    """Grid coordinates p after the linear M plus the tangle at strength w."""
    p = np.asarray(p, float)
    return p @ np.asarray(M, float).T + wobble(p, w)


def warped_grid(M, w, origin, unit, n=9):
    """The grid's integer lines after `tangle` (sampled smooth curves), the axes in C.axis."""
    s = np.linspace(-12, 12, 140)
    major, axis = VGroup(), VGroup()
    for k in range(-n, n + 1):
        for line in (np.c_[np.full_like(s, k), s], np.c_[s, np.full_like(s, k)]):
            q = tangle(M, w, line)
            mob = VMobject().set_points_smoothly([pt(origin, unit, v) for v in q])
            (axis if k == 0 else major).add(mob.set_stroke(C.axis if k == 0 else C.grid,
                                                           C.thin * (1.5 if k == 0 else 1.0)))
    return VGroup(major, axis)
