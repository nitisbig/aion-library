"""Dido's voyage: one unbroken dusk shot of a Phoenician galley reaching the African coast, painted in crisp flat skia.

Every frame is a pure function of absolute audio time. `voyage(arrive)` returns frame(t) for a FramesLayer; the ship
sails until `arrive`, then lowers its sail and rides at anchor off the shore.
"""
from functools import lru_cache

import numpy as np
import skia

from aion import *
from coast import _col, _mix

W, H = 1920, 1080
HZ = 620
ROWS = [0, 24, 56, 100, 162, 238, 336, 452]
SUN_X = 1170


def ease_out(u):
    u = np.clip(u, 0.0, 1.0)
    return 1 - (1 - u) ** 2.4


def sstep(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def paint(color, stroke=None, cap=True):
    p = skia.Paint(AntiAlias=True, Color=color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def poly_path(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


@lru_cache(maxsize=1)
def sky_image():
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    stops = [(0.0, C.indigo), (0.34, C.plum), (0.6, C.tyrian), (0.76, C.rose), (0.88, C.dusk), (0.96, C.ember), (1.0, C.gold)]
    shader = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, HZ)], [_col(c) for _, c in stops], [u for u, _ in stops])
    cv.drawRect(skia.Rect(0, 0, W, HZ + 2), skia.Paint(Shader=shader))
    r = rng(21)
    for _ in range(9):
        y, x, L = r.uniform(250, 560), r.uniform(-100, W), r.uniform(240, 760)
        h = r.uniform(5, 15)
        tone = _mix(C.rose, C.ember, float(np.clip((y - 250) / 310, 0, 1)))
        cv.drawRoundRect(skia.Rect(x, y, x + L, y + h), h / 2, h / 2, paint(_col(tone, 0.55)))
        cv.drawRoundRect(skia.Rect(x + L * 0.2, y + h + 5, x + L * 0.82, y + h + 5 + h * 0.6), h / 3, h / 3, paint(_col(tone, 0.34)))
    return sf.makeImageSnapshot()


@lru_cache(maxsize=1)
def stars():
    r = rng(8)
    return np.column_stack([r.uniform(0, W, 130), r.uniform(0, 330, 130), r.uniform(0.9, 2.4, 130), r.uniform(0, 6.28, 130)])


@lru_cache(maxsize=1)
def land_paths():
    def ridge(x0, x1, base, top, seed, n=90):
        xs = np.linspace(x0, x1, n)
        u = (xs - x0) / (x1 - x0)
        ys = base - top * (1 - u**3) * (0.72 + 0.28 * np.array([fbm1(x * 0.004, seed) for x in xs]))
        return poly_path([(x0, base + 90)] + list(zip(xs, ys)) + [(x1, base + 90)])
    far = ridge(-1500, 0, HZ, 150, 3)
    mid = ridge(-1500, 0, HZ, 96, 7)
    near = ridge(-1500, 0, HZ + 6, 58, 12)
    # a small hilltop settlement and its tents, cut into the nearest ridge
    city = skia.Path()
    for x, w, h in [(-470, 46, 54), (-418, 30, 74), (-382, 56, 42), (-322, 26, 62), (-290, 44, 36), (-240, 34, 28)]:
        city.addRect(skia.Rect(x, HZ - 34 - h, x + w, HZ))
    for x in (-180, -130, -84):
        city.addPath(poly_path([(x - 24, HZ - 14), (x, HZ - 44), (x + 24, HZ - 14)]))
    return far, mid, near, city


def wave(cv, y0, amp, lam, phase, color):
    xs = np.arange(-20, W + 34, 14.0)
    ys = y0 + amp * np.sin(xs / lam + phase) + amp * 0.4 * np.sin(xs / (lam * 0.43) - phase * 1.4)
    cv.drawPath(poly_path([(-20, H + 20)] + list(zip(xs, ys)) + [(W + 34, H + 20)]), paint(color))
    return xs, ys


def bez(t, a, b, c, d):
    return (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t**2 * c + t**3 * d


def sheer(u):
    """A point on the top edge of the hull, u from bow (0) to stern (1)."""
    return (float(bez(u, -345, -200, 120, 300)), float(bez(u, -62, -30, -30, -95)))


def ship(cv, t, furl, row):
    """The galley, bow to the left, origin on the waterline."""
    # rigging and mast sit behind the sail
    line = paint(_col(_mix(C.walnut, C.dusk, 0.25)), 2.4)
    cv.drawLine(-10, -476, -352, -78, line)
    cv.drawLine(-10, -476, 322, -112, line)
    cv.drawLine(-10, -30, -10, -486, paint(_col(C.walnut), 13))
    cv.drawLine(-9, -30, -9, -486, paint(_col(C.ember, 0.55), 2.2))
    flap = [(-10 + 13 * i, -486 + 7 * np.sin(2.4 * t - i * 0.9) * (i / 6)) for i in range(7)]
    cv.drawPath(poly_path(flap + [(q[0], q[1] + 24 - 2 * i) for i, q in reversed(list(enumerate(flap)))]), paint(_col(C.gold)))

    # the square sail in Tyrian stripes, full of wind, brailed up to the yard as the ship arrives
    b = (46 + 9 * np.sin(0.85 * t)) * (1 - furl)
    y_top, y_low = -432, -128 + furl * (-432 + 48 + 128)
    sail = skia.Path()
    sail.moveTo(-232, y_top)
    sail.lineTo(222, y_top)
    sail.quadTo(222 - b * 1.2, (y_top + y_low) / 2, 196, y_low)
    sail.quadTo(-10 - b, y_low + 34 * (1 - furl), -214, y_low)
    sail.quadTo(-232 - b * 1.2, (y_top + y_low) / 2, -232, y_top)
    sail.close()
    cv.save()
    cv.clipPath(sail, True)
    for i in range(9):
        x = -250 + i * 56
        cv.drawRect(skia.Rect(x, -450, x + 57, -40), paint(_col(C.tyrian if i % 2 else C.foam)))
    for i in range(5):
        cv.drawRect(skia.Rect(-260 + i * 104, -450, -212 + i * 104, -40), paint(_col(C.walnut, 0.07)))
    cv.drawRect(skia.Rect(90, -450, 260, -40), paint(_col(C.walnut, 0.2)))
    cv.drawRect(skia.Rect(-260, y_low - 26, 260, y_low + 50), paint(_col(C.walnut, 0.16)))
    if furl < 0.55:
        k = 1 - furl / 0.55
        gold = paint(_col(C.gold, k))
        cv.drawCircle(-14 - b * 0.5, -296, 40, gold)
        crescent = skia.Path()
        crescent.addCircle(-14 - b * 0.5, -296, 62)
        crescent.addCircle(-14 - b * 0.5, -318, 62)
        crescent.setFillType(skia.PathFillType.kEvenOdd)
        cv.save()
        cv.clipRect(skia.Rect(-120 - b, -296, 100, -220))
        cv.drawPath(crescent, gold)
        cv.restore()
    cv.restore()
    cv.drawPath(sail, paint(_col(C.walnut, 0.8), 3))
    cv.drawLine(-246, -434, 236, -434, paint(_col(C.walnut), 11))
    cv.drawLine(-246, -437, 236, -437, paint(_col(C.ember, 0.7), 2))
    for x in (-232, 222):
        cv.drawLine(x, -432, x * 0.62, -40, line)

    # far-side oars, the crew and Dido at the bow
    for x, h in [(-120, 40), (-70, 44), (-20, 40), (40, 44), (90, 41), (150, 44)]:
        cv.drawCircle(x, -48 - h + 8, 10, paint(_col(C.walnut)))
        cv.drawRoundRect(skia.Rect(x - 11, -48 - h + 15, x + 11, -30), 7, 7, paint(_col(C.walnut)))
    d = skia.Path()
    d.moveTo(-262, -44)
    d.cubicTo(-268, -86, -256, -112, -250, -122)
    d.cubicTo(-238, -112, -226, -84, -222, -44)
    d.close()
    cv.drawPath(d, paint(_col(C.tyrian)))
    cv.drawCircle(-250, -131, 10.5, paint(_col(C.walnut)))
    cv.drawLine(-250, -143, -250, -140, paint(_col(C.gold), 5))
    cloak = poly_path([(-246, -118), (-214 + 5 * np.sin(1.7 * t), -82), (-206 + 7 * np.sin(1.7 * t + 0.7), -46), (-224, -46)])
    cv.drawPath(cloak, paint(_col(C.rose)))

    # stern post, curled like a scorpion's tail, and the horse-head prow
    stern = skia.Path()
    stern.moveTo(286, -88)
    stern.cubicTo(352, -122, 376, -196, 330, -226)
    stern.cubicTo(300, -240, 282, -204, 310, -194)
    cv.drawPath(stern, paint(_col(C.walnut), 20))
    cv.drawPath(stern, paint(_col(C.gold, 0.85), 2.6))
    bow = skia.Path()
    bow.moveTo(-340, -60)
    bow.cubicTo(-378, -88, -392, -138, -372, -176)
    cv.drawPath(bow, paint(_col(C.walnut), 17))
    head = poly_path([(-362, -170), (-368, -206), (-356, -196), (-378, -212), (-414, -196), (-418, -182), (-392, -182), (-382, -162)])
    cv.drawPath(head, paint(_col(C.walnut)))
    cv.drawPath(head, paint(_col(C.gold, 0.9), 2.2))
    cv.drawCircle(-390, -194, 3.4, paint(_col(C.gold)))
    cv.drawPath(poly_path([(-340, -34), (-432, -6), (-330, 8)]), paint(_col(C.walnut)))

    # hull
    hull = skia.Path()
    hull.moveTo(-345, -62)
    hull.cubicTo(-200, -30, 120, -30, 300, -95)
    hull.cubicTo(270, 50, -230, 60, -345, -62)
    hull.close()
    cv.drawPath(hull, paint(_col(C.walnut)))
    cv.save()
    cv.clipPath(hull, True)
    for k, dy in enumerate((20, 40, 62, 84)):
        pl = skia.Path()
        pl.moveTo(-345, -62 + dy)
        pl.cubicTo(-200, -30 + dy, 120, -30 + dy, 300, -95 + dy)
        cv.drawPath(pl, paint(_col(_mix(C.dusk, C.walnut, 0.45 + k * 0.1), 0.55), 2.2))
    cv.restore()
    top = skia.Path()
    top.moveTo(-345, -62)
    top.cubicTo(-200, -30, 120, -30, 300, -95)
    cv.drawPath(top, paint(_col(C.gold), 4.5))

    # near-side oars rowing together, shipped once the voyage ends
    rowing = 1 - furl
    for i in range(10):
        u = 0.14 + i * 0.078
        x, y = sheer(u)
        ph = 2 * np.pi * 0.42 * t + i * 0.16
        sweep = 46 * np.sin(ph)
        dip = max(0.0, np.cos(ph))
        tx = x - 62 + sweep * rowing
        ty = y + (86 + 16 * dip) * rowing + (1 - rowing) * 18
        tx = tx if rowing > 0 else x - 96
        cv.drawLine(x, y + 8, tx, ty, paint(_col(C.foam, 0.92), 3.6))
        cv.drawLine(tx, ty, tx - 15, ty + 7, paint(_col(C.foam), 9))
    for i in range(14):
        x, y = sheer(0.05 + i * 0.069)
        cv.drawCircle(x, y + 7, 15, paint(_col(C.tyrian if i % 2 else C.gold)))
        cv.drawCircle(x, y + 7, 15, paint(_col(C.walnut), 3))
        cv.drawCircle(x, y + 7, 4, paint(_col(C.foam)))


def voyage(arrive, dusk_start, end):
    """frame(t) for the opening shot: sailing until `arrive`, then at anchor while the evening deepens."""
    arrive, dusk_start, end = float(arrive), float(dusk_start), float(end)
    sky = sky_image()
    far, mid, near, city = land_paths()
    star = stars()
    gl = rng(5)
    glitter = np.column_stack([gl.uniform(0, 1, 110), gl.normal(0, 1, 110), gl.uniform(0.5, 1, 110), gl.uniform(0, 6.28, 110), gl.uniform(0.45, 0.95, 110)])
    gulls = np.array([[-140, 330, 60, 0.0], [-40, 292, 74, 1.4], [70, 352, 52, 2.3], [190, 306, 66, 0.8]])
    sf = skia.Surface(W, H)

    def frame(t):
        u = float(ease_out(t / arrive))
        S = 900 * u
        night = float(sstep((t - dusk_start) / (end - dusk_start)))
        furl = float(sstep((t - arrive + 0.5) / 1.7))
        cv = sf.getCanvas()
        cv.clear(_col(C.indigo))
        zoom = 1 + 0.07 * float(sstep(t / end))
        cv.save()
        cv.translate(1000, 760)
        cv.scale(zoom, zoom)
        cv.translate(-1000, -760)

        cv.drawImage(sky, 0, 0)
        for x, y, r, ph in star:
            cv.drawCircle(x, y, r, paint(_col(C.foam, float(np.clip(0.28 + night * 0.7 + 0.1 * np.sin(0.8 * t + ph), 0, 1)))))
        sy = HZ - 44 + 62 * float(sstep(t / end))
        for r, a in ((236, 0.12), (190, 0.18)):
            cv.drawCircle(SUN_X, sy, r, paint(_col(C.ember, a)))
        cv.drawCircle(SUN_X, sy, 142, paint(_col(C.gold)))
        cv.drawCircle(SUN_X, sy, 112, paint(_col(C.foam, 0.5)))
        for gx, gy, gs, gp in gulls:
            x = (gx + 80 * t + S * 0.2) % (W + 300) - 150
            f = 18 * np.sin(3.2 * t + gp) * gs / 70
            pts = [(x - gs / 2, gy - f), (x - gs / 6, gy - 3), (x, gy + 3), (x + gs / 6, gy - 3), (x + gs / 2, gy - f)]
            cv.drawPath(poly_path(pts, False), paint(_col(C.walnut), 3.4))

        # Africa rises over the horizon as the ship closes on it
        rise = 1 - float(sstep((t - arrive * 0.2) / (arrive * 0.8)))
        for path, par, tip, tone in ((far, 0.45, 960, _mix(C.rose, C.plum, 0.55)), (mid, 0.7, 860, _mix(C.plum, C.indigo, 0.25)), (near, 1.0, 770, C.indigo)):
            cv.save()
            cv.translate(tip - 900 * par + S * par, 170 * rise)
            cv.drawPath(path, paint(_col(tone)))
            if path is near:
                cv.drawPath(city, paint(_col(C.indigo)))
                for x, y in [(-452, -92), (-404, -112), (-306, -98), (-172, -30), (-122, -30), (-76, -30)]:
                    lit = float(sstep((t - arrive - 0.4 - abs(x) * 0.0012) / 0.9))
                    cv.drawCircle(x, HZ + y + 34, 4.2, paint(_col(C.gold, lit)))
            cv.restore()

        # the sea, row by row toward the viewer
        sx = float(1500 - 440 * u)
        wy = 846 + 7 * np.sin(1.05 * t)
        pitch = 1.5 * np.sin(0.78 * t + 0.6)
        for i, dy in enumerate(ROWS):
            k = i / (len(ROWS) - 1)
            tone = _mix(_mix(C.rose, C.dusk, 0.5), C.indigo, k**0.55)
            xs, ys = wave(cv, HZ + dy, 1.5 + 21 * k**1.3, 42 + 190 * k, 0.75 * t * (1 + k) - S / (70 + 330 * k), _col(tone))
            if i >= 5:
                r = rng(40 + i)
                for x0 in r.uniform(0, W, 7):
                    x = (x0 + 0.75 * t * 40 * (1 + k) - S * 0.5 * k) % (W + 200) - 100
                    j = int(np.clip((x + 20) / 14, 0, len(xs) - 16))
                    cv.drawPath(poly_path(list(zip(xs[j:j + 15], ys[j:j + 15])), False), paint(_col(C.foam, 0.22), 2.6))
            if i in (2, 3, 4):
                near_sun = np.exp(-(((xs - SUN_X) / (170 + 220 * k)) ** 2))
                for x, y, a in zip(xs[::3], ys[::3], near_sun[::3]):
                    if a > 0.16:
                        cv.drawLine(x, y, x + 26, y, paint(_col(C.gold, 0.8 * float(a)), 2.6))
            if i == 4:
                for dd, gs, wd, ph, al in glitter:
                    y = HZ + 12 + dd * 228
                    x = SUN_X + gs * (34 + dd * 165)
                    L = 12 + 56 * wd * (0.72 + 0.28 * np.sin(0.9 * t + ph))
                    cv.drawRoundRect(skia.Rect(x - L, y, x + L, y + 3.4), 1.7, 1.7, paint(_col(C.gold, float(al) * (1 - dd * 0.55))))
                cv.save()
                cv.translate(sx, wy)
                cv.rotate(float(pitch))
                ship(cv, t, furl, i)
                cv.restore()
                move = 1 - furl
                for j in range(4):
                    fx = sx + 300 + j * 150
                    L = 170 + j * 80
                    cv.drawRoundRect(skia.Rect(fx, wy + 28 + j * 9, fx + L, wy + 32 + j * 9), 2, 2, paint(_col(C.foam, (0.5 - j * 0.1) * move)))
                cv.drawRoundRect(skia.Rect(sx - 400, wy + 38, sx + 310, wy + 44), 3, 3, paint(_col(C.foam, 0.58)))
        cv.restore()
        if night > 0:
            cv.drawRect(skia.Rect(0, 0, W, H), paint(_col(C.indigo, 0.3 * night)))
        arr = sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()
        arr[..., 3] = 255
        return arr
    return frame
