"""Chapter 1's painted world: the dusk mountain, an explorer's relief map, and the forbidden ground around the trail."""
from functools import lru_cache

import numpy as np
import skia

from aion import *
from coast import _col, _mix
from draw3d import rgb
from shots import BOX, LEVELS, MAPC, U, _mountain, _mountain_lines, arrow, contour_paths, seen, trail_mob
from voyage import paint, poly_path, sky_image
from world import TRAIL_A, TRAIL_B, hill, hill_grad

W, H = 1920, 1080
DUSK_HZ = 372


def GROUND():
    return _mix(C.indigo, C.bg, 0.25)


def _xy(q):
    q = np.asarray(q, float)
    return np.column_stack([960 + 135 * (MAPC[0] + U * q[:, 0]), 540 - 135 * (MAPC[1] + U * q[:, 1])])


def ramp(u, stops):
    """Colors along a list of theme colors, for u in [0, 1]."""
    c = np.array([rgb(k) for k in stops])
    x = np.clip(u, 0, 1) * (len(c) - 1)
    i = np.minimum(x.astype(int), len(c) - 2)
    f = (x - i)[..., None]
    return c[i] * (1 - f) + c[i + 1] * f


def _rose(cv, x, y, r):
    for k in range(8):
        cv.save()
        cv.translate(x, y)
        cv.rotate(45.0 * k)
        L = r if k % 2 == 0 else r * 0.58
        cv.drawPath(poly_path([(0, -L), (L * 0.14, -L * 0.2), (0, 0)]), paint(_col(C.gold)))
        cv.drawPath(poly_path([(0, -L), (-L * 0.14, -L * 0.2), (0, 0)]), paint(_col(_mix(C.gold, C.indigo, 0.6))))
        cv.restore()
    cv.drawCircle(x, y, r * 0.74, paint(_col(C.gold, 0.8), 1.8))
    cv.drawCircle(x, y, r * 0.09, paint(_col(C.foam)))


@lru_cache(maxsize=2)
def atlas_rgba(contours=True):
    """The relief map on the left and the equation panel on the right, as one opaque picture."""
    xs = (np.arange(W) + 0.5) / 135 - 64 / 9
    ys = 4 - (np.arange(H) + 0.5) / 135
    X, Y = np.meshgrid(xs, ys)
    mx, my = (X - MAPC[0]) / U, (Y - MAPC[1]) / U
    idx = np.digitize(hill(mx, my), LEVELS)
    col = ramp(idx / len(LEVELS), [C.bg, C.indigo, C.plum, _mix(C.plum, C.dusk, 0.55), _mix(C.dusk, C.obj, 0.6), C.obj, C.gold])
    gx, gy = hill_grad(mx, my)
    n = np.dstack([-gx, -gy, np.full_like(gx, 0.8)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    light = np.array([-0.52, 0.52, 0.68])
    col = col * (0.66 + 0.5 * np.clip(n @ light, 0, 1))[..., None]
    v = (np.arange(H) / H)[:, None, None]
    panel = rgb(C.indigo) * (0.5 - 0.42 * v) + rgb(C.bg) * (0.5 + 0.42 * v)
    col = np.where((X > BOX[2])[..., None], panel, col)
    rgba = np.dstack([np.clip(col, 0, 1) * 255, np.full((H, W), 255.0)]).astype(np.uint8)
    sf = skia.Surface(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    cv = sf.getCanvas()
    x_edge = 960 + 135 * BOX[2]
    cv.save()
    cv.clipRect(skia.Rect(16, 16, x_edge - 16, H - 16))
    for k in np.arange(-6, 7):
        a = _xy([[k, -9], [k, 9]])
        b = _xy([[-9, k], [9, k]])
        cv.drawLine(*a[0], *a[1], paint(_col(C.gold, 0.1), 1.2))
        cv.drawLine(*b[0], *b[1], paint(_col(C.gold, 0.1), 1.2))
    for i, level in enumerate(LEVELS if contours else []):
        for p in contour_paths(float(level)):
            major = i % 2 == 0
            cv.drawPath(poly_path([tuple(q) for q in _xy(p[::2])], False), paint(_col(C.gold if major else C.obj, 0.85 if major else 0.5), 2.5 if major else 1.3))
    cv.restore()
    m = 16
    cv.drawRect(skia.Rect(m, m, x_edge - m, H - m), paint(_col(C.gold), 2.4))
    cv.drawRect(skia.Rect(m + 8, m + 8, x_edge - m - 8, H - m - 8), paint(_col(C.gold, 0.5), 1))
    for x in np.arange(m + 60, x_edge - m, 60):
        cv.drawLine(x, m, x, m + 8, paint(_col(C.gold), 1.6))
        cv.drawLine(x, H - m - 8, x, H - m, paint(_col(C.gold), 1.6))
    for y in np.arange(m + 60, H - m, 60):
        cv.drawLine(m, y, m + 8, y, paint(_col(C.gold), 1.6))
        cv.drawLine(x_edge - m - 8, y, x_edge - m, y, paint(_col(C.gold), 1.6))
    _rose(cv, 118, H - 118, 72)
    cv.drawLine(x_edge, 0, x_edge, H, paint(_col(C.gold), 3))
    sf.flushAndSubmit()
    return rgba


@lru_cache(maxsize=1)
def dusk_rgba():
    """The evening behind the mountain, in the colors of Dido's voyage."""
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    cv.save()
    cv.scale(1, DUSK_HZ / 620)
    cv.drawImage(sky_image(), 0, 0)
    cv.restore()
    r = rng(12)
    for x, y, a in zip(r.uniform(0, W, 150), r.uniform(0, 210, 150), r.uniform(0.3, 1.0, 150)):
        cv.drawCircle(x, y, float(r.uniform(0.9, 2.3)), paint(_col(C.foam, float(a))))
    cv.drawCircle(1560, DUSK_HZ - 26, 170, paint(_col(C.ember, 0.14)))
    cv.drawCircle(1560, DUSK_HZ - 26, 112, paint(_col(C.gold)))
    cv.drawCircle(1560, DUSK_HZ - 26, 86, paint(_col(C.foam, 0.48)))
    for tone, top, seed in ((_mix(C.rose, C.plum, 0.6), 100, 2), (_mix(C.plum, C.indigo, 0.4), 56, 5)):
        xs = np.arange(-20, W + 40, 18.0)
        ys = DUSK_HZ + 4 - top * 0.6 * np.array([0.45 + 0.55 * fbm1(x * 0.0032, seed) for x in xs])
        cv.drawPath(poly_path([(-20, DUSK_HZ + 40)] + list(zip(xs, ys)) + [(W + 40, DUSK_HZ + 40)]), paint(_col(tone)))
    cv.drawRect(skia.Rect(0, DUSK_HZ, W, H), paint(_col(GROUND())))
    return sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()


@lru_cache(maxsize=1)
def _dusk_mesh():
    a, b = np.meshgrid(np.linspace(-1, 1, 100), np.linspace(-1, 1, 100))
    dx, dy = a * np.sqrt(1 - b * b / 2), b * np.sqrt(1 - a * a / 2)
    X, Y, r = 0.5 + 5.0 * dx, 0.2 + 5.0 * dy, 5.0 * np.hypot(dx, dy)
    Z = hill(X, Y) * np.clip((5.0 - r) / 1.1, 0, 1) ** 0.7
    u = np.clip(Z / 3.05, 0, 1) ** 0.8
    cols = ramp(u, [C.indigo, C.plum, _mix(C.plum, C.dusk, 0.6), C.dusk, C.obj, C.gold])
    fall = np.clip((5.0 - r) / 2.0, 0, 1)[..., None] ** 1.3
    return X, Y, Z, cols * fall + rgb(GROUND()) * 1.14 * (1 - fall)


def dusk_mountain(v, contour_alpha=0.35, below=None):
    X, Y, Z, cols = _dusk_mesh()
    v.mesh(X, Y, Z, cols, shade=True, ambient=0.5)
    for p in _mountain_lines():
        if np.hypot(p[:, 0] - 0.5, p[:, 1] - 0.2).max() < 3.9 and (below is None or p[0, 2] <= below):
            v.line(p, C.gold, 1.7, contour_alpha, visible=seen(p, v.cam))


@lru_cache(maxsize=1)
def forbidden_rgba():
    """Hatching over everything except a narrow band along the trail."""
    xs = (np.arange(W) + 0.5) / 135 - 64 / 9
    ys = 4 - (np.arange(H) + 0.5) / 135
    X, Y = np.meshgrid(xs, ys)
    mx, my = (X - MAPC[0]) / U, (Y - MAPC[1]) / U
    off = np.abs(np.sqrt((mx / TRAIL_A) ** 2 + (my / TRAIL_B) ** 2) - 1.0)
    keep = np.clip((off - 0.055) / 0.02, 0, 1) * (X < BOX[2] - 0.13) * (X > BOX[0] + 0.17) * (np.abs(Y) < 3.87)
    stripe = np.mod((X + Y) * 3.4, 1.0) < 0.2
    col = np.where(stripe[..., None], rgb(C.wrong), rgb(C.bg))
    alpha = keep * np.where(stripe, 0.62, 0.56)
    return (np.clip(np.dstack([col, alpha]), 0, 1) * 255).astype(np.uint8)


def garrow(a, b, color, width=6, tip=0.28):
    """An arrow with a dark casing, so it reads on the relief map."""
    return VGroup(arrow(a, b, C.bg, width=width + 4, tip=tip + 0.05), arrow(a, b, color, width=width, tip=tip))


def trail_art(width=7):
    """The hiking trail: a dark casing, the cyan path and a pale center line."""
    core = trail_mob(width)
    return VGroup(trail_mob(width + 5).set_stroke(C.bg), core, DashedVMobject(trail_mob(1.8).set_stroke(C.foam), num_dashes=54, dashed_ratio=0.5))
