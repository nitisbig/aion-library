"""Dido's coast at dusk: flat, crisp, banded skia layers for the opening and the ending."""
from functools import lru_cache

import skia

from aion import *
from draw3d import rgb

W, H = 1600, 900
UNITS = 9.4                 # frame units covered by the layer's height
HORIZON = 0.2


def _x(x):
    return W / 2 + x * H / UNITS


def _y(y):
    return H / 2 - y * H / UNITS


def _col(c, a=1.0):
    r, g, b = (rgb(c) * 255).astype(int).tolist()
    return skia.Color(r, g, b, int(a * 255))


def _mix(a, b, u):
    r, g, b_ = ((rgb(a) * (1 - u) + rgb(b) * u) * 255).astype(int).tolist()
    return f"#{r:02x}{g:02x}{b_:02x}"


def _surface():
    return skia.Surface(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType))


def _arr(sf):
    return sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()


def _poly(cv, pts, color):
    p = skia.Path()
    p.moveTo(_x(pts[0][0]), _y(pts[0][1]))
    for x, y in pts[1:]:
        p.lineTo(_x(x), _y(y))
    p.close()
    cv.drawPath(p, skia.Paint(AntiAlias=True, Color=color))


@lru_cache(maxsize=1)
def coast_layers():
    out = {}
    # sky: flat bands from night down to the ember horizon, and a half-set sun
    sf = _surface()
    cv = sf.getCanvas()
    cv.clear(_col(C.night))
    n = 11
    for i in range(n):
        u = i / (n - 1)
        c = _mix(C.night, C.dusk, u**1.5) if u < 0.8 else _mix(C.dusk, C.ember, (u - 0.8) / 0.2)
        top = 4.8 - (4.8 - HORIZON) * i / n
        cv.drawRect(skia.Rect(0, _y(top), W, _y(HORIZON) + 2), skia.Paint(Color=_col(c)))
    cv.drawCircle(_x(3.3), _y(HORIZON + 0.28), 0.78 * H / UNITS, skia.Paint(AntiAlias=True, Color=_col(C.ember)))
    out["sky"] = _arr(sf)
    # sea: darker bands toward the viewer, with crisp glitter under the sun
    sf = _surface()
    cv = sf.getCanvas()
    cv.clear(0)
    for i in range(7):
        top = HORIZON - i * 0.42
        cv.drawRect(skia.Rect(0, _y(top), W, H), skia.Paint(Color=_col(_mix(_mix(C.sea, C.dusk, 0.28), C.night, min(1, 0.12 + i * 0.13)))))
    r = rng(5)
    for _ in range(90):
        d = r.uniform(0.04, 1)
        y = HORIZON - d * 2.2
        x = 3.3 + r.normal(0, 0.28 + d * 0.95)
        L = r.uniform(0.1, 0.55) * (0.5 + d)
        cv.drawRect(skia.Rect(_x(x - L), _y(y), _x(x + L), _y(y) + 2.2), skia.Paint(Color=_col(C.ember, 0.75 * (1 - d * 0.55))))
    out["sea"] = _arr(sf)
    # the far headland
    sf = _surface()
    cv = sf.getCanvas()
    cv.clear(0)
    xs = np.linspace(-8.4, -0.7, 120)
    top = [(x, HORIZON + max(0, 1.5 * ((-0.7 - x) / 7.7) ** 0.75 + 0.2 * fbm1(x * 0.8, 3) * ((-0.7 - x) / 7.7))) for x in xs]
    _poly(cv, top + [(-0.7, HORIZON - 0.02), (-8.4, HORIZON - 0.02)], _col(_mix(C.night, C.dusk, 0.16)))
    out["cliffs"] = _arr(sf)
    # the beach: two flat dunes in the last light
    sf = _surface()
    cv = sf.getCanvas()
    cv.clear(0)
    xs = np.linspace(-8.4, 8.4, 160)
    edge = [(x, -0.62 + 0.1 * fbm1(x * 0.35, 8) - 0.05 * x) for x in xs]
    _poly(cv, edge + [(8.4, -5.2), (-8.4, -5.2)], _col(_mix(C.sand, C.dusk, 0.28)))
    p = skia.Path()
    p.moveTo(_x(edge[0][0]), _y(edge[0][1]))
    for x, y in edge[1:]:
        p.lineTo(_x(x), _y(y))
    cv.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=_col(C.ember, 0.9)))
    low = [(x, -2.75 + 0.3 * fbm1(x * 0.3, 11) + 0.08 * x) for x in xs]
    _poly(cv, low + [(8.4, -5.2), (-8.4, -5.2)], _col(_mix(C.sand, C.night, 0.5)))
    out["dunes"] = _arr(sf)
    return out


def coast(s, z=-60):
    """Add the four parallax layers of the coast to a scene."""
    L = coast_layers()
    s.add(ArrayLayer(L["sky"], height=UNITS, z=z, parallax=0.15))
    s.add(ArrayLayer(L["sea"], height=UNITS, z=z + 10, parallax=0.3))
    s.add(ArrayLayer(L["cliffs"], height=UNITS, z=z + 20, parallax=0.45))
    s.add(ArrayLayer(L["dunes"], height=UNITS, z=z + 40, parallax=0.9))
