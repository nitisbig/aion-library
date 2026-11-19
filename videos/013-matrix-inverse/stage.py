"""A small 3D stage drawn with skia: a perspective camera, slabs of grid, a machined brass key, and vector type. Everything stays crisp: depth comes
from perspective, material and hard cast shadows, never from glow or blur."""
import os
from functools import lru_cache

import numpy as np
import skia

from aion import C

W, H = 1920, 1080
SS = max(1, int(os.environ.get("AION_FILM_SS", "1")))   # raster scale of the films: 2 draws every vector at true 4K
FOCAL = 1.62 * H
LIGHT = np.array([-0.42, -0.5, 0.76]) / np.linalg.norm([-0.42, -0.5, 0.76])
BANDS = (0.42, 0.78, 1.32, 1.02, 0.62, 0.9, 1.26, 0.7, 0.42)   # the brushed sheen across the brass


def rgb(c):
    h = str(c).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def paint_color(c, a=1.0, mul=1.0):
    v = np.clip(rgb(c) * mul, 0, 255).astype(int)
    return skia.Color(int(v[0]), int(v[1]), int(v[2]), int(np.clip(a, 0, 1) * 255))


def ease(t, a, b):
    """Quintic ease from 0 at time a to 1 at time b."""
    u = float(np.clip((t - a) / max(b - a, 1e-6), 0, 1))
    return u * u * u * (u * (6 * u - 15) + 10)


class Cam:
    """Orbits a target: az and el in degrees, dist in world units."""

    def __init__(self, tx, ty, tz, az, el, dist):
        a, e = np.radians(az), np.radians(el)
        self.target = np.array([tx, ty, tz], float)
        self.eye = self.target + dist * np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        self.f = (self.target - self.eye) / dist
        r = np.cross(self.f, [0.0, 0.0, 1.0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)

    def pj(self, P):
        v = np.asarray(P, float) - self.eye
        d = np.maximum(v @ self.f, 0.08)
        return np.c_[W / 2 + FOCAL * (v @ self.r) / d, H / 2 - FOCAL * (v @ self.u) / d], d


def track(t, frames):
    """Camera keyframes [(time, (tx, ty, tz, az, el, dist)), ...], eased between neighbours."""
    if t <= frames[0][0]:
        return Cam(*frames[0][1])
    for (a, va), (b, vb) in zip(frames, frames[1:]):
        if t <= b:
            u = ease(t, a, b)
            return Cam(*[(1 - u) * x + u * y for x, y in zip(va, vb)])
    return Cam(*frames[-1][1])


# ---------------------------------------------------------------- lines
class Lines:
    """Thousands of line segments batched by colour, width and opacity."""

    def __init__(self):
        self.paths = {}

    def add(self, p, q, color, width, alpha):
        level = int(np.clip(alpha, 0, 1) * 8 + 0.5)
        if level:
            path = self.paths.setdefault((str(color), round(width, 1), level), skia.Path())
            path.moveTo(float(p[0]), float(p[1]))
            path.lineTo(float(q[0]), float(q[1]))

    def flush(self, can):
        for (color, width, level), path in self.paths.items():
            can.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, StrokeCap=skia.Paint.kRound_Cap, Color=paint_color(color, level / 8)))
        self.paths = {}


def polyline(lines, cam, P, color, width=2.0, alpha=1.0):
    q, _ = cam.pj(P)
    for a, b in zip(q[:-1], q[1:]):
        lines.add(a, b, color, width, alpha)


def grid(lines, cam, M, origin=(0, 0), z=0.0, xr=(-5, 5), yr=(-4, 4), op=1.0, reveal=None, far=46.0, minor=True, color=None, axes=True):
    """A grid carried by the 2x2 matrix M. It fades with distance, and `reveal` opens it outward from the origin."""
    M, origin = np.asarray(M, float), np.asarray(origin, float)
    fam = []
    step = 0.5 if minor else 1.0
    for v in np.arange(xr[0], xr[1] + 1e-6, step):
        fam.append((np.c_[np.full(25, v), np.linspace(yr[0], yr[1], 25)], v))
    for v in np.arange(yr[0], yr[1] + 1e-6, step):
        fam.append((np.c_[np.linspace(xr[0], xr[1], 25), np.full(25, v)], v))
    for src, v in fam:
        on = abs(v) < 1e-6 and axes
        whole = abs(v - round(v)) < 1e-6
        col, width = (C.axis, 3.0) if on else ((color or C.grid), 2.3) if whole else (C.grid_minor, 1.2)
        world = np.c_[(M @ src.T).T + origin, np.full(25, z)]
        q, d = cam.pj(world)
        a = op * np.clip(1.15 - d / far, 0.0, 1.0) * (1.0 if whole else 0.8)
        if reveal is not None:
            a = a * np.clip((reveal - np.hypot(src[:, 0], src[:, 1])) / 0.9, 0, 1)
        for i in range(24):
            lines.add(q[i], q[i + 1], col, width, 0.5 * (a[i] + a[i + 1]))


def poly_path(q, close=True):
    path = skia.Path()
    path.moveTo(float(q[0][0]), float(q[0][1]))
    for p in q[1:]:
        path.lineTo(float(p[0]), float(p[1]))
    if close:
        path.close()
    return path


def fill(can, q, color, alpha=1.0, mul=1.0):
    can.drawPath(poly_path(q), skia.Paint(AntiAlias=True, Color=paint_color(color, alpha, mul)))


def slab(can, cam, M, origin=(0, 0), z=0.0, xr=(-5, 5), yr=(-3.5, 3.5), thick=0.16, op=1.0, tint=None):
    """The sheet the grid is printed on: a thin plate with lit edges."""
    M, origin = np.asarray(M, float), np.asarray(origin, float)
    corners = (M @ np.array([[xr[0], yr[0]], [xr[1], yr[0]], [xr[1], yr[1]], [xr[0], yr[1]]], float).T).T + origin
    top, low = np.c_[corners, np.full(4, z)], np.c_[corners, np.full(4, z - thick)]
    for i in range(4):
        j = (i + 1) % 4
        mid = 0.5 * (top[i] + top[j])
        out = mid[:2] - corners.mean(axis=0)
        if out @ (cam.eye[:2] - mid[:2]) > 0:
            fill(can, cam.pj([top[i], top[j], low[j], low[i]])[0], tint or C.grid, 0.62 * op, 0.55 + 0.35 * i / 3)
    q, _ = cam.pj(top)
    fill(can, q, tint or C.grid, 0.06 * op)
    can.drawPath(poly_path(q), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.4, Color=paint_color(tint or C.grid, op, 1.25)))


def ribbon(can, cam, a, b, color, width=0.09, head=0.0, z=0.03, alpha=1.0):
    """A flat arrow lying on a plane, drawn as one crisp shape."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-4:
        return
    d = d / L
    n = np.array([-d[1], d[0]])
    h = min(head, L * 0.6)
    neck = b - h * d
    pts = [a + n * width / 2, neck + n * width / 2, neck + n * h * 0.5, b, neck - n * h * 0.5, neck - n * width / 2, a - n * width / 2] if head else [a + n * width / 2, b + n * width / 2, b - n * width / 2, a - n * width / 2]
    fill(can, cam.pj(np.c_[np.array(pts), np.full(len(pts), z)])[0], color, alpha)


def ring(lines, cam, c, r, z, color, width=2.0, alpha=1.0, n=72):
    th = np.linspace(0, 2 * np.pi, n)
    polyline(lines, cam, np.c_[c[0] + r * np.cos(th), c[1] + r * np.sin(th), np.full(n, z)], color, width, alpha)


# ---------------------------------------------------------------- the key
BOW_C, BOW_R, HOLE_R, HALF = -1.05, 0.45, 0.2, 0.08
TIP = 1.5


def _teeth_edge(teeth, sign):
    """The upper (sign +1) or lower (sign -1) edge of the blade, walking from the bow to the tip."""
    pts = [(-0.66, HALF), (-0.6, 0.14), (-0.5, 0.14), (-0.45, HALF)]
    c = 0.035
    for i, s in enumerate(teeth):
        h = max(HALF, 0.42 * max(s * sign, 0.0))
        x0, x1 = 0.42 + 0.27 * i, 0.59 + 0.27 * i
        if h > HALF + 1e-3:
            pts += [(x0, HALF), (x0, h - c), (x0 + c, h), (x1 - c, h), (x1, h - c), (x1, HALF)]
    pts += [(TIP - 0.12, HALF), (TIP, 0.0)]
    return [(x, sign * y) for x, y in pts]


@lru_cache(maxsize=512)
def outline(teeth):
    """The key's silhouette in its own frame, counter-clockwise, including the collar at the bow."""
    phi = float(np.arcsin(HALF / BOW_R))
    arc = np.linspace(phi, 2 * np.pi - phi, 64)
    bow = [(BOW_C + BOW_R * np.cos(a), BOW_R * np.sin(a)) for a in arc]
    low, up = _teeth_edge(teeth, -1), _teeth_edge(teeth, 1)
    return np.array(bow + low + up[-2::-1], float)


def circle_pts(cx, r, n=40):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[cx + r * np.cos(th), r * np.sin(th)]


def outline_path(q, hole_q=None):
    path = poly_path(q)
    if hole_q is not None:
        path.addPath(poly_path(hole_q))
    path.setFillType(skia.PathFillType.kEvenOdd)
    return path


def draw_key(can, cam, place, normal, teeth, thick=0.1, sheen=0.0, op=1.0, width=1.0, color=None):
    """A solid key: lit side walls, a brushed face with a moving sheen, a bright milled rim and engraved detail."""
    color = color or C.key
    if op <= 0.005:
        return
    teeth = tuple(round(float(s), 2) for s in teeth)
    normal = np.asarray(normal, float)
    O, hole = outline(teeth), circle_pts(BOW_C, HOLE_R)
    centre = place(np.array([[0.0, 0.0]]))[0]
    side = 1.0 if normal @ (cam.eye - centre) >= 0 else -1.0
    front, back = 0.5 * thick * side * normal, -0.5 * thick * side * normal
    if op < 0.995:
        can.saveLayerAlpha(None, int(op * 255))

    # the walls, far ones first
    quads = []
    for loop, flip in ((O, 1.0), (hole, -1.0)):
        a, b = loop, np.roll(loop, -1, axis=0)
        tan = b - a
        out = flip * np.c_[tan[:, 1], -tan[:, 0]] / np.maximum(np.hypot(tan[:, 0], tan[:, 1]), 1e-6)[:, None]
        mid = 0.5 * (a + b)
        wm, wo = place(mid), place(mid + 0.02 * out)
        wn = wo - wm
        wn = wn / np.maximum(np.linalg.norm(wn, axis=1, keepdims=True), 1e-6)
        pa, pb = place(a), place(b)
        for i in range(len(a)):
            if wn[i] @ (cam.eye - wm[i]) > 0:
                lit = 0.3 + 0.95 * max(0.0, float(wn[i] @ LIGHT))
                quads.append((float(np.linalg.norm(wm[i] - cam.eye)), [pa[i] + front, pb[i] + front, pb[i] + back, pa[i] + back], lit))
    quads.sort(key=lambda x: -x[0])
    for _, quad, lit in quads:
        q, _ = cam.pj(quad)
        can.drawPath(poly_path(q), skia.Paint(AntiAlias=True, Style=skia.Paint.kStrokeAndFill_Style, StrokeWidth=0.8, Color=paint_color(color, 1.0, lit)))

    # the brushed face
    fq, _ = cam.pj(place(O) + front)
    hq, _ = cam.pj(place(hole) + front)
    path = outline_path(fq, hq)
    ends, _ = cam.pj(place(np.array([[-1.7, -0.7], [1.7, 0.7]])) + front)
    stops = np.linspace(0.0, 1.0, 13)
    colors = [paint_color(color, 1.0, float(np.interp((u * 1.7 + sheen) % 1.0, np.linspace(0, 1, len(BANDS)), BANDS))) for u in stops]
    shader = skia.GradientShader.MakeLinear([skia.Point(*ends[0]), skia.Point(*ends[1])], colors, [float(u) for u in stops])
    can.drawPath(path, skia.Paint(AntiAlias=True, Shader=shader))

    # engraving: a dark cut with a lit lip
    groove = np.c_[np.linspace(-0.42, 1.28, 14), np.zeros(14)]
    inner = circle_pts(BOW_C, 0.33, 48)
    for pts, closed in ((inner, True), (groove, False)):
        q, _ = cam.pj(place(pts) + front)
        can.drawPath(poly_path(q, closed), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6 * width, Color=paint_color(color, 0.9, 0.34)))
        can.drawPath(poly_path(q + np.array([0.0, 1.3 * width]), closed), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.0 * width, Color=paint_color(color, 0.8, 1.38)))
    can.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.9 * width, Color=paint_color(color, 1.0, 1.42)))
    if op < 0.995:
        can.restore()


def key_shadow(can, cam, place, teeth, floor=0.0, alpha=0.55):
    """The key's hard shadow on the plane below it."""
    teeth = tuple(round(float(s), 2) for s in teeth)
    def drop(P):
        return P - np.outer((P[:, 2] - floor) / LIGHT[2], LIGHT)
    q, _ = cam.pj(drop(place(outline(teeth))))
    h, _ = cam.pj(drop(place(circle_pts(BOW_C, HOLE_R))))
    can.drawPath(outline_path(q, h), skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(alpha * 255))))


def key_wire(can, cam, place, teeth, color, width=2.0, alpha=1.0):
    """The key as a single drawn outline."""
    teeth = tuple(round(float(s), 2) for s in teeth)
    q, _ = cam.pj(place(outline(teeth)))
    h, _ = cam.pj(place(circle_pts(BOW_C, HOLE_R)))
    can.drawPath(outline_path(q, h), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=paint_color(color, alpha)))


# ---------------------------------------------------------------- vector type and picture cards
def glyph_paths(mob):
    """A Manim text or maths mobject as skia paths in Manim coordinates: [(path, colour), ...]."""
    out = []
    for sm in mob.family_members_with_points():
        pts = sm.points
        if len(pts) < 4:
            continue
        path, last = skia.Path(), None
        for i in range(0, len(pts) - 3, 4):
            a, b, c, d = pts[i:i + 4]
            if last is None or np.linalg.norm(a - last) > 1e-5:
                path.moveTo(float(a[0]), float(a[1]))
            path.cubicTo(float(b[0]), float(b[1]), float(c[0]), float(c[1]), float(d[0]), float(d[1]))
            last = d
        path.setFillType(skia.PathFillType.kEvenOdd)
        out.append((path, sm.get_fill_color().to_hex()))
    return out


def draw_glyphs(can, glyphs, cx, cy, scale, alpha=1.0):
    """Draw glyph paths centred on pixel (cx, cy); `scale` is pixels per Manim unit."""
    can.save()
    can.translate(cx, cy)
    can.scale(scale, -scale)
    for path, color in glyphs:
        can.drawPath(path, skia.Paint(AntiAlias=True, Color=paint_color(color, alpha)))
    can.restore()


def card(can, cam, image, corners, alpha=1.0):
    """Lay a picture onto a quad in space with true perspective."""
    q, _ = cam.pj(corners)
    w, h = image.width(), image.height()
    src = [skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)]
    m = skia.Matrix()
    m.setPolyToPoly(src, [skia.Point(float(x), float(y)) for x, y in q])
    can.save()
    can.concat(m)
    can.drawImage(image, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(AntiAlias=True, Alphaf=float(alpha)))
    can.restore()
