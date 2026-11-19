"""Shared building blocks for "What Lagrange Multipliers Actually Are" (012). Everything is a pure function of t.

- text:      tex, words, sc (small caps), lab (sans), bold
- plane:     p3, arrow, poly, live, backed, curtain, backdrop, mix
- the map:   mp, contour_mobs, trail_mob, walker, map_bg, stage (same layout in every map scene, so cuts are seamless)
- mountain:  view, draw_mountain, surf (3D, skia)
- beach:     beach_bg, rect_rope, resample, area_of (top view of Dido's shore)
Numbers come from cast.json, which verify.py writes after all of its checks pass.
"""
import json
from functools import lru_cache
from pathlib import Path

import contourpy

from aion import *
from draw3d import Cam, View3D, rgb
from world import TRAIL_A, TRAIL_B, hill, hill_grad, trail, trail_grad, trail_tangent

CAST = json.loads((Path(__file__).parent / "cast.json").read_text())
E = "easy_ease"
BEST_S = CAST["trail_best_s"]
BEST = np.array(CAST["trail_best"])
SUMMIT = np.array(CAST["summit"])
BEST_H = float(hill(*BEST))
LEVELS = [BEST_H + k * 0.3 for k in range(-5, 4)]
LOW_S = CAST["trail_stations"][3][1] - 2 * np.pi    # the trail's low point: walking from here up to BEST only climbs
MAPC = np.array([-2.7, -0.15])
U = 1.3
BOX = (-7.11, -4.0, 1.0, 4.0)                       # the map's frame; the right side holds the equations


# ---------------------------------------------------------------- text
def tex(*parts, size=None, colors=None, color=None):
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def words(text, size=None, color=None):
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def sc(text, size=32, color=None):
    return Tex(r"\textsc{" + text + "}", font_size=size, color=color or C.ink)


def lab(text, size=28, color=None):
    return Tex(r"\textsf{" + text + "}", font_size=size, color=color or C.muted)


def bold(text, size=36, color=None):
    return Tex(r"\textbf{" + text + "}", font_size=size, color=color or C.text)


def mix(a, b, u):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(u, 0, 1))).to_hex()


# ---------------------------------------------------------------- plane
def p3(v):
    v = np.asarray(v, float)
    return np.array([v[0], v[1], 0.0])


def arrow(a, b, color, width=None, tip=0.26, opacity=1.0):
    a, b = p3(a), p3(b)
    L = max(np.linalg.norm(b - a), 1e-6)
    return Arrow(a, b, buff=0, color=color, stroke_width=width or C.stroke + 1, tip_length=min(tip, 0.45 * L),
                 max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=40).set_opacity(opacity)


def poly(pts, color, width=None, opacity=1.0, close=False):
    P = np.array([p3(p) for p in pts])
    if close:
        P = np.vstack([P, P[:1]])
    return VMobject(stroke_color=color, stroke_width=width or C.stroke, stroke_opacity=opacity).set_points_as_corners(P)


def live(m, fn, *windows):
    """Rebuild fn(t) every frame inside each (start, end) window and hold it still in between."""
    merged = []
    for a, b in sorted(windows):
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


def backed(mob, buff=0.12, opacity=0.92):
    return VGroup(BackgroundRectangle(mob, color=C.bg, fill_opacity=opacity, buff=buff), mob)


def backdrop(s):
    s.solid(C.bg, z=-200)


def curtain(s, a=True, b=True, dur=0.32):
    """Dip from and to black at the scene's edges."""
    s0, s1 = float(s.start), float(s.end)

    def op(t):
        u = 1 - (t - s0) / dur if a else 0.0
        v = (t - (s1 - dur)) / dur if b else 0.0
        return float(np.clip(max(u, v), 0, 1))
    s.solid(C.bg, z=400, opacity=Track(op, active=[(s0, s0 + dur), (s1 - dur, s1)]))


# ---------------------------------------------------------------- the map
def mp(x, y=None):
    """Map coordinates to frame coordinates."""
    q = np.asarray(x, float) if y is None else np.array([x, y], float)
    return p3(MAPC + U * q)


@lru_cache(maxsize=None)
def contour_paths(level):
    xs = np.linspace((BOX[0] - MAPC[0]) / U, (BOX[2] - MAPC[0]) / U, 260)
    ys = np.linspace((BOX[1] - MAPC[1]) / U, (BOX[3] - MAPC[1]) / U, 260)
    Z = hill(*np.meshgrid(xs, ys))
    return tuple(p for p in contourpy.contour_generator(xs, ys, Z).lines(level) if len(p) > 8)


def contour_mobs(levels=None, width=1.7, opacity=0.9, color=None):
    out = VGroup()
    for lv in (LEVELS if levels is None else levels):
        for p in contour_paths(float(lv)):
            out.add(poly([mp(q) for q in p[::2]], color or C.obj, width, opacity))
    return out


def trail_mob(width=None, s0=0.0, s1=2 * np.pi):
    ss = np.linspace(s0, s1, 240)
    return poly([mp(*trail(u)) for u in ss], C.con, width or C.stroke + 1.5)


def walker(p):
    q = p3(p)
    return VGroup(Dot(q, radius=0.15, color=C.bg), Dot(q, radius=0.105, color=C.you))


@lru_cache(maxsize=None)
def _map_rgba():
    W, H = 960, 540
    xs = (np.arange(W) + 0.5) / W * 16 * 8 / 9 - 64 / 9
    ys = 4 - (np.arange(H) + 0.5) / H * 8
    X, Y = np.meshgrid(xs, ys)
    Z = hill((X - MAPC[0]) / U, (Y - MAPC[1]) / U)
    idx = np.digitize(Z, LEVELS)
    tint = 0.03 + 0.042 * idx
    base, warm = rgb(C.bg), rgb(C.obj)
    col = (base[None, None] * (1 - tint[..., None]) + warm[None, None] * tint[..., None])
    inside = (X >= BOX[0]) & (X <= BOX[2])
    a = np.dstack([col, inside.astype(float)])
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)


def map_bg(s, z=-20, opacity=1.0):
    s.add(ArrayLayer(_map_rgba(), height=8.0, z=z, opacity=opacity))


def stage(s, contours=True, with_trail=True):
    """The map layout shared by every map scene: tinted bands, contours, trail, and the equation side panel."""
    backdrop(s)
    map_bg(s)
    base = s.manim(z=0)
    base.add(Line([BOX[2], -4, 0], [BOX[2], 4, 0], color=C.frame, stroke_width=C.thin))
    if contours:
        base.add(contour_mobs())
    if with_trail:
        base.add(trail_mob())
    return base


# ---------------------------------------------------------------- the mountain in 3D
@lru_cache(maxsize=1)
def view():
    return View3D()


@lru_cache(maxsize=1)
def _mountain():
    xs = np.linspace(-6.6, 6.6, 92)
    X, Y = np.meshgrid(xs, xs)
    Z = hill(X, Y)
    u = np.clip(Z / 3.05, 0, 1)[..., None] ** 0.8
    fall = np.clip((6.3 - np.hypot(X, Y)) / 2.4, 0, 1)[..., None] ** 1.4
    cols = (mix_rgb(C.bg, C.obj, 0.16) * (1 - u) + rgb(C.obj) * u) * fall
    return X, Y, Z, cols


def mix_rgb(a, b, u):
    return rgb(a) * (1 - u) + rgb(b) * u


@lru_cache(maxsize=1)
def _mountain_lines():
    xs = np.linspace(-6.6, 6.6, 200)
    Z = hill(*np.meshgrid(xs, xs))
    out = []
    for lv in LEVELS:
        for p in contourpy.contour_generator(xs, xs, Z).lines(float(lv)):
            if len(p) > 8:
                out.append(np.column_stack([p[::2], np.full(len(p[::2]), lv + 0.012)]))
    return out


def seen(P, cam):
    """Which world points are not hidden behind the mountain, by marching toward the camera."""
    P = np.asarray(P, float)
    ss = np.linspace(0.14, 7.0, 18)[None, :, None]
    Q = P[:, None, :] + ss * cam.d[None, None, :]
    return ~np.any(hill(Q[..., 0], Q[..., 1]) > Q[..., 2] + 0.02, axis=1)


def surf(x, y, lift=0.03):
    return np.stack([x, y, hill(x, y) + lift], -1)


def draw_mountain(v, contour_alpha=0.0, below=None):
    """The shaded mountain; `below` shows only the contour rings under that height (the rising slice)."""
    X, Y, Z, cols = _mountain()
    v.mesh(X, Y, Z, cols, shade=True, ambient=0.42)
    if contour_alpha > 0.01:
        for p in _mountain_lines():
            if below is None or p[0, 2] <= below:
                v.line(p, C.bg, 1.8, contour_alpha, visible=seen(p, v.cam))


def ring_at(level):
    """The contour of the mountain at any height, as world polylines."""
    xs = np.linspace(-6.6, 6.6, 150)
    Z = hill(*np.meshgrid(xs, xs))
    return [np.column_stack([p, np.full(len(p), level + 0.02)]) for p in contourpy.contour_generator(xs, xs, Z).lines(float(level)) if len(p) > 6]


def loops_at(level):
    """Contours of f at any height, as map polylines (not cached: for live swelling loops)."""
    xs = np.linspace((BOX[0] - MAPC[0]) / U, (BOX[2] - MAPC[0]) / U, 150)
    ys = np.linspace((BOX[1] - MAPC[1]) / U, (BOX[3] - MAPC[1]) / U, 150)
    Z = hill(*np.meshgrid(xs, ys))
    return [p for p in contourpy.contour_generator(xs, ys, Z).lines(float(level)) if len(p) > 6]


def lerp_cam(u, a, b):
    """A camera between two poses (az, el, zoom, cx, cy, dist)."""
    q = [x + (y - x) * u for x, y in zip(a, b)]
    return Cam(az=q[0], el=q[1], zoom=q[2], center=(q[3], q[4]), dist=q[5])


POSE_3D = (-68.0, 33.0, 1.08, 0.1, -1.0, 26.0)
POSE_MAP = (-90.0, 89.9, U, float(MAPC[0]), float(MAPC[1]), 400.0)
PX = 4.05       # the centre of the equation panel


def chapter(m, text, at):
    """A quiet chapter name in small caps."""
    c = sc(text, 30, C.muted).move_to([PX, 3.5, 0])
    m.play(FadeIn(c), at=at + 0.2, dur=0.6)
    m.play(FadeOut(c), at=at + 4.0, dur=0.6)


def grad_field(step=0.62, scale=0.34, width=2.2):
    """The gradient of f as short arrows over the map, clipped to its frame."""
    out = VGroup()
    for x in np.arange(-3.2, 2.9, step):
        for y in np.arange(-2.8, 3.0, step):
            g = hill_grad(x, y)
            n = float(np.linalg.norm(g))
            if n < 0.03:
                continue
            L = min(0.5, scale * n ** 0.6)
            a = mp(x, y)
            out.add(arrow(a, a + p3(g / n * L), C.obj, width=width, tip=0.13, opacity=0.8))
    return out


# ---------------------------------------------------------------- Dido's beach, from above
SHORE = 1.9
BU = 0.24       # frame units per meter of rope


def beach_bg():
    sand = Rectangle(width=15, height=8, stroke_width=0, fill_color=mix(C.sand, C.bg, 0.72), fill_opacity=1).move_to([0, SHORE - 4, 0])
    sea = Rectangle(width=15, height=4, stroke_width=0, fill_color=mix(C.sea, C.bg, 0.45), fill_opacity=1).move_to([0, SHORE + 2, 0])
    foam = VGroup(*[poly([[x, SHORE + d + 0.05 * np.sin(1.4 * x + 2 * d * 9)] for x in np.linspace(-7.5, 7.5, 60)],
                         mix(C.sea, C.text, 0.35), C.thin, 0.8 - d * 0.3) for d in (0.12, 0.5, 1.0)])
    edge = Line([-7.5, SHORE, 0], [7.5, SHORE, 0], color=mix(C.sand, C.text, 0.35), stroke_width=C.thin + 0.6)
    return VGroup(sand, sea, foam, edge)


def rect_rope(depth, width, cx=0.0):
    """A rope in meters leaving the shore, running parallel to it, and returning: frame points."""
    w, d = width * BU / 2, depth * BU
    return np.array([[cx - w, SHORE], [cx - w, SHORE - d], [cx + w, SHORE - d], [cx + w, SHORE]])


def resample(P, n=160):
    P = np.asarray(P, float)
    ds = np.linalg.norm(np.diff(P, axis=0), axis=1)
    u = np.concatenate([[0], np.cumsum(ds)]) / ds.sum()
    q = np.linspace(0, 1, n)
    return np.column_stack([np.interp(q, u, P[:, 0]), np.interp(q, u, P[:, 1])])


def area_of(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / BU**2


def side_panel(m):
    """Black equation panel with its divider, for scenes whose left side moves with the camera or runs in 3D."""
    r = Rectangle(width=7.2, height=8.4, fill_color=C.bg, fill_opacity=1, stroke_width=0).move_to([BOX[2] + 3.6, 0, 0])
    m.add(r, Line([BOX[2], -4, 0], [BOX[2], 4, 0], color=C.frame, stroke_width=C.thin))


def nabla_f(size=None):
    return tex(r"\nabla f", size=size, color=C.obj)


def nabla_g(size=None):
    return tex(r"\nabla g", size=size, color=C.con)
