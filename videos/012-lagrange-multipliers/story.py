"""The ox hide on a workbench, the twisted rope, and the dusk beach it is laid on, painted in crisp skia."""
from functools import lru_cache

import numpy as np
import skia

from aion import *
from coast import _col, _mix
from voyage import paint, poly_path, ship, sky_image, sstep

W, H = 1920, 1080
HZ2 = 420
SHORE_Y = 637


def faded(a):
    p = skia.Paint()
    p.setAlphaf(float(a))
    return p


def px(p):
    p = np.asarray(p, dtype=float)
    return np.column_stack([960 + 135 * p[..., 0], 540 - 135 * p[..., 1]])


def resample(pts, n):
    pts = np.asarray(pts, dtype=float)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    u = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])])


def smooth_closed(ctrl, per=14):
    """A closed Catmull-Rom curve through the control points."""
    c = np.asarray(ctrl, dtype=float)
    out = []
    for i in range(len(c)):
        a, b, d, e = c[i - 1], c[i], c[(i + 1) % len(c)], c[(i + 2) % len(c)]
        for t in np.linspace(0, 1, per, endpoint=False):
            out.append(0.5 * (2 * b + (d - a) * t + (2 * a - 5 * b + 4 * d - e) * t**2 + (3 * b - a - 3 * d + e) * t**3))
    return np.array(out)


def draw_rope(cv, pts, w, alpha=1.0, shadow=True):
    """A laid rope: cast shadow, dark edge, bright core and diagonal twisted strands."""
    if len(pts) < 2 or w <= 0:
        return
    path = poly_path([tuple(q) for q in pts], False)
    if shadow:
        cv.save()
        cv.translate(w * 0.28, w * 0.42)
        cv.drawPath(path, paint(_col(C.walnut, 0.42 * alpha), w * 1.05))
        cv.restore()
    cv.drawPath(path, paint(_col(_mix(C.con, C.indigo, 0.68), alpha), w * 1.16))
    cv.drawPath(path, paint(_col(C.con, alpha), w * 0.84))
    if w < 3.5:
        return
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    marks = np.arange(w * 0.3, s[-1], w * 0.82)
    xs, ys = np.interp(marks, s, pts[:, 0]), np.interp(marks, s, pts[:, 1])
    tx, ty = np.gradient(pts[:, 0]), np.gradient(pts[:, 1])
    tx, ty = np.interp(marks, s, tx), np.interp(marks, s, ty)
    norm = np.hypot(tx, ty) + 1e-6
    tx, ty = tx / norm, ty / norm
    dark, light = paint(_col(_mix(C.con, C.indigo, 0.55), alpha), max(1.2, w * 0.17)), paint(_col(_mix(C.con, C.foam, 0.62), alpha), max(0.9, w * 0.11))
    a, b = w * 0.38, w * 0.3
    for x, y, u, v in zip(xs, ys, tx, ty):
        cv.drawLine(x - v * a - u * b, y + u * a - v * b, x + v * a + u * b, y - u * a + v * b, dark)
        cv.drawLine(x - v * a - u * b + u * w * 0.2, y + u * a - v * b + v * w * 0.2, x + v * a + u * b + u * w * 0.2, y - u * a + v * b + v * w * 0.2, light)


def stake(cv, x, y, k=1.0):
    """A wooden stake driven into the sand."""
    if k <= 0:
        return
    h, w = 74 * k, 15
    cv.drawOval(skia.Rect(x - 24, y - 7, x + 34, y + 11), paint(_col(C.walnut, 0.4)))
    cv.drawRoundRect(skia.Rect(x - w / 2, y - h, x + w / 2, y + 3), 4, 4, paint(_col(C.walnut)))
    cv.drawRect(skia.Rect(x - w / 2, y - h, x - w / 2 + 4, y + 2), paint(_col(C.dusk, 0.8)))
    cv.drawRect(skia.Rect(x - w / 2 - 2, y - h + 14 * k, x + w / 2 + 2, y - h + 22 * k), paint(_col(C.gold)))


PELT_HALF = [(0, -350), (58, -338), (88, -262), (215, -292), (318, -352), (352, -282), (272, -176), (262, -40), (280, 92), (352, 214), (338, 306), (252, 276), (168, 214), (92, 262), (34, 330), (12, 410)]


@lru_cache(maxsize=1)
def pelt():
    half = [(x, y * 0.84) for x, y in PELT_HALF]
    ring = half + [(-12, half[-1][1])] + [(-x, y) for x, y in reversed(half[1:-1])]
    return smooth_closed(ring) + np.array([960.0, 535.0])


@lru_cache(maxsize=1)
def bench_image():
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    r = rng(14)
    plank = H / 7
    for i in range(7):
        tone = _mix(C.walnut, C.dusk, float(r.uniform(0.04, 0.2)))
        cv.drawRect(skia.Rect(0, i * plank, W, (i + 1) * plank), paint(_col(tone)))
        for _ in range(16):
            y = i * plank + r.uniform(8, plank - 8)
            x0 = r.uniform(-200, W)
            xs = np.linspace(x0, x0 + r.uniform(260, 900), 16)
            ph = r.uniform(0, 6)
            cv.drawPath(poly_path(list(zip(xs, y + 3.5 * np.sin(xs / 90 + ph))), False), paint(_col(C.walnut, 0.55), 1.8))
        cv.drawRect(skia.Rect(0, (i + 1) * plank - 3, W, (i + 1) * plank + 2), paint(_col(C.bg, 0.72)))
        for x in r.uniform(40, W - 40, 3):
            cv.drawCircle(x, i * plank + 15, 4, paint(_col(C.gold, 0.5)))
    shade = skia.GradientShader.MakeRadial(skia.Point(960, 520), 1120, [_col(C.bg, 0.0), _col(C.bg, 0.0), _col(C.bg, 0.72)], [0.0, 0.48, 1.0])
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=shade))
    return sf.makeImageSnapshot()


@lru_cache(maxsize=1)
def hide_image():
    info = skia.ImageInfo.MakeN32Premul(W, H)
    sf = skia.Surface.MakeRaster(info)
    cv = sf.getCanvas()
    cv.clear(0)
    P = pelt()
    path = poly_path([tuple(q) for q in P])
    cv.save()
    cv.translate(16, 24)
    cv.drawPath(path, paint(_col(C.bg, 0.55)))
    cv.restore()
    fill = skia.GradientShader.MakeLinear([skia.Point(620, 180), skia.Point(1300, 900)], [_col(_mix(C.sand, C.ember, 0.3)), _col(_mix(C.sand, C.dusk, 0.32)), _col(_mix(C.sand, C.walnut, 0.42))], [0.0, 0.55, 1.0])
    cv.drawPath(path, skia.Paint(AntiAlias=True, Shader=fill))
    cv.save()
    cv.clipPath(path, True)
    r = rng(31)
    for _ in range(7):
        c = np.array([r.uniform(700, 1220), r.uniform(220, 850)])
        th = np.linspace(0, 2 * np.pi, 9, endpoint=False)
        rad = r.uniform(34, 98) * r.uniform(0.6, 1.25, 9)
        blot = smooth_closed(np.column_stack([c[0] + rad * np.cos(th) * 1.3, c[1] + rad * np.sin(th)]), 6)
        cv.drawPath(poly_path([tuple(q) for q in blot]), paint(_col(C.walnut, 0.46)))
    cv.drawRect(skia.Rect(944, 150, 976, 930), paint(_col(C.walnut, 0.16)))
    for _ in range(1500):
        x, y = r.uniform(600, 1320), r.uniform(170, 920)
        a = r.uniform(0, 6.28)
        cv.drawLine(x, y, x + 8 * np.cos(a), y + 8 * np.sin(a), paint(_col(C.walnut if r.uniform() < 0.55 else C.foam, 0.13), 1.3))
    cv.restore()
    n = np.gradient(P, axis=0)
    n = np.column_stack([n[:, 1], -n[:, 0]]) / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-6)
    for q, v, L in zip(P[::2], n[::2], r.uniform(4, 13, len(P[::2]))):
        cv.drawLine(q[0], q[1], q[0] + v[0] * L, q[1] + v[1] * L, paint(_col(C.walnut, 0.85), 2.1))
    cv.drawPath(path, paint(_col(C.walnut), 3.2))
    inset = (P - [960, 535]) * 0.93 + [960, 535]
    st = paint(_col(C.gold, 0.92), 2.6)
    st.setPathEffect(skia.DashPathEffect.Make([13, 11], 0))
    cv.drawPath(poly_path([tuple(q) for q in inset]), st)
    return sf.makeImageSnapshot()


def spiral_points(n=900):
    P = pelt() - [960, 535]
    ang = np.mod(np.arctan2(P[:, 1], P[:, 0]), 2 * np.pi)
    idx = np.argsort(ang)
    rad = np.linalg.norm(P, axis=1)[idx]
    u = np.linspace(0, 1, n)
    th = u * 2 * np.pi * 8.5
    r = np.interp(np.mod(th, 2 * np.pi), ang[idx], rad, period=2 * np.pi) * 0.86 * (1 - u) ** 0.92 + 3
    return np.column_stack([960 + r * np.cos(th), 535 + r * np.sin(th)])


def knife(cv, x, y, ang):
    cv.save()
    cv.translate(x, y)
    cv.rotate(float(np.degrees(ang)) - 35)
    cv.drawPath(poly_path([(0, 0), (86, -19), (108, -13), (88, 6)]), paint(_col(C.foam)))
    cv.drawLine(4, -1, 96, -13, paint(_col(C.muted), 2))
    cv.drawRoundRect(skia.Rect(104, -21, 122, 7), 3, 3, paint(_col(C.gold)))
    cv.drawRoundRect(skia.Rect(120, -20, 214, 6), 11, 11, paint(_col(C.walnut)))
    cv.drawRoundRect(skia.Rect(126, -16, 208, -11), 3, 3, paint(_col(C.dusk, 0.8)))
    cv.restore()


def palm(cv, x, y, s, flip=1):
    cv.save()
    cv.translate(x, y)
    cv.scale(s * flip, s)
    trunk = skia.Path()
    trunk.moveTo(-18, 0)
    trunk.cubicTo(-6, -170, 40, -300, 104, -392)
    trunk.lineTo(120, -384)
    trunk.cubicTo(70, -280, 34, -160, 24, 0)
    trunk.close()
    cv.drawPath(trunk, paint(_col(C.walnut)))
    for i in range(9):
        y0 = -40 * i - 16
        cv.drawLine(-14 + i * 8, y0, 26 + i * 8, y0 + 7, paint(_col(C.dusk, 0.5), 3))
    for a in (-168, -128, -88, -44, -6, 32, 150):
        cv.save()
        cv.translate(110, -390)
        cv.rotate(a)
        frond = skia.Path()
        frond.moveTo(0, 0)
        frond.cubicTo(70, -50, 170, -40, 248, 44)
        frond.cubicTo(170, 6, 80, 12, 0, 0)
        cv.drawPath(frond, paint(_col(C.indigo)))
        cv.restore()
    cv.restore()


@lru_cache(maxsize=1)
def beach_image():
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    cv.save()
    cv.scale(1, HZ2 / 620)
    cv.drawImage(sky_image(), 0, 0)
    cv.restore()
    r = rng(17)
    for x, y, a in zip(r.uniform(0, W, 90), r.uniform(0, 200, 90), r.uniform(0.3, 0.9, 90)):
        cv.drawCircle(x, y, 1.6, paint(_col(C.foam, float(a))))
    cv.drawCircle(1370, HZ2 - 18, 150, paint(_col(C.ember, 0.18)))
    cv.drawCircle(1370, HZ2 - 18, 104, paint(_col(C.gold)))
    cv.drawCircle(1370, HZ2 - 18, 80, paint(_col(C.foam, 0.5)))
    xs = np.linspace(-20, 1040, 90)
    ridge = HZ2 + 3 - 128 * (1 - (xs + 20) / 1060) ** 0.8 * np.array([0.75 + 0.25 * fbm1(x * 0.006, 4) for x in xs])
    cv.drawPath(poly_path([(-20, HZ2 + 8)] + list(zip(xs, ridge)) + [(1040, HZ2 + 8)]), paint(_col(_mix(C.plum, C.indigo, 0.35))))
    for i, y in enumerate((HZ2, HZ2 + 34, HZ2 + 78, HZ2 + 132)):
        cv.drawRect(skia.Rect(0, y, W, SHORE_Y + 30), paint(_col(_mix(_mix(C.rose, C.dusk, 0.5), C.sea, 0.3 + i * 0.23))))
    for _ in range(90):
        d = r.uniform(0, 1)
        x, L = 1370 + r.normal(0, 40 + d * 170), r.uniform(10, 56)
        cv.drawRoundRect(skia.Rect(x - L, HZ2 + 8 + d * 190, x + L, HZ2 + 11 + d * 190), 1.5, 1.5, paint(_col(C.gold, 0.8 * (1 - d * 0.5))))
    cv.save()
    cv.translate(1110, HZ2 + 62)
    cv.scale(0.24, 0.24)
    ship(cv, 3.0, 1.0, 0)
    cv.restore()
    sand = skia.GradientShader.MakeLinear([skia.Point(0, SHORE_Y), skia.Point(0, H)], [_col(_mix(C.sand, C.ember, 0.35)), _col(_mix(C.sand, C.dusk, 0.34)), _col(_mix(C.sand, C.plum, 0.5))], [0.0, 0.5, 1.0])
    edge = np.arange(-20, W + 30, 20.0)
    top = SHORE_Y + 7 * np.sin(edge / 170)
    cv.drawPath(poly_path([(-20, H + 10)] + list(zip(edge, top)) + [(W + 30, H + 10)]), skia.Paint(AntiAlias=True, Shader=sand))
    for _ in range(420):
        x, y = r.uniform(0, W), r.uniform(SHORE_Y + 40, H)
        L = r.uniform(12, 60)
        cv.drawRoundRect(skia.Rect(x, y, x + L, y + 2.4), 1.2, 1.2, paint(_col(C.dusk if r.uniform() < 0.6 else C.foam, 0.2)))
    low = 990 + 26 * np.sin(edge / 260 + 1.2)
    cv.drawPath(poly_path([(-20, H + 10)] + list(zip(edge, low)) + [(W + 30, H + 10)]), paint(_col(_mix(C.sand, C.plum, 0.68))))
    palm(cv, 60, 1020, 1.15)
    palm(cv, 1860, 1040, 1.3, -1)
    return sf.makeImageSnapshot()


def story(T):
    """frame(t) from the end of the voyage to the scene's last beat: hide, knife, rope and beach."""
    strips, thread, rope, shore, guard, shape = (float(x) for x in (T.strips, T.thread, T.rope, T.shore, T.guard, T.shape_q))
    S = resample(spiral_points(), 700)
    x_long = np.linspace(-6.5, 6.5, 700)
    L = px(np.column_stack([x_long, 0.3 + 0.32 * np.sin(1.4 * x_long) + 0.14 * np.sin(3.1 * x_long)]))
    xs = np.linspace(-4.2, 2.8, 240)
    mid, half = (xs[0] + xs[-1]) / 2, (xs[-1] - xs[0]) / 2
    A = resample(px(np.column_stack([xs, -0.74 - 2.0 * (1 - np.abs((xs - mid) / half) ** 3.2) ** 0.75 * (1 + 0.16 * (xs - mid) / half)])), 700)
    bench, hide, beach = bench_image(), hide_image(), beach_image()
    sf = skia.Surface(W, H)

    def frame(t):
        cv = sf.getCanvas()
        cv.drawImage(beach, 0, 0)
        foam = np.arange(-20, W + 30, 16.0)
        y = SHORE_Y + 7 * np.sin(foam / 170) + 3 * np.sin(foam / 46 + 1.1 * t)
        cv.drawPath(poly_path(list(zip(foam, y)), False), paint(_col(C.foam, 0.92), 5))
        cv.drawPath(poly_path(list(zip(foam, y - 11 - 3 * np.sin(foam / 80 - 0.8 * t))), False), paint(_col(C.foam, 0.34), 2.6))
        bench_a = 1 - float(sstep((t - shore + 0.9) / 0.9))
        if bench_a > 0:
            cv.drawImage(bench, 0, 0, skia.SamplingOptions(), faded(bench_a))
        hide_a = (1 - float(sstep((t - rope + 0.2) / 0.7))) * float(sstep((t - strips + 0.95) / 0.7))
        if hide_a > 0:
            k = 0.94 + 0.06 * float(sstep((t - strips + 0.95) / 0.9))
            cv.save()
            cv.translate(960, 535)
            cv.scale(k, k)
            cv.translate(-960, -535)
            cv.drawImage(hide, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), faded(hide_a))
            cv.restore()
        a, b = float(sstep((t - rope - 0.9) / 1.3)), float(sstep((t - shore - 0.4) / 1.5))
        P = S * (1 - a) + L * a
        P = P * (1 - b) + A * b
        cut = float(np.clip((t - strips - 0.5) / (rope - strips - 0.7), 0, 1))
        n = max(2, int(cut * len(P)))
        w = 5 + 11 * a
        area = float(sstep((t - shape + 0.2) / 0.8))
        if area > 0:
            cv.drawPath(poly_path([tuple(q) for q in A]), paint(_col(C.gold, 0.2 * area)))
        g = float(sstep((t - guard) / 0.9))
        if g > 0:
            x0, x1 = A[0, 0], A[0, 0] + (A[-1, 0] - A[0, 0]) * g
            cv.drawLine(x0, SHORE_Y - 2, x1, SHORE_Y - 2, paint(_col(C.gold), 7))
        if cut > 0:
            draw_rope(cv, P[:n], w)
        if cut > 0 and t < rope - 0.1:
            q = P[n - 1]
            d = P[min(n, len(P) - 1)] - P[max(n - 6, 0)]
            knife(cv, q[0], q[1], np.arctan2(d[1], d[0]))
        s = float(sstep((t - guard + 0.5) / 0.5))
        stake(cv, A[0, 0], A[0, 1] + 6, s)
        stake(cv, A[-1, 0], A[-1, 1] + 6, s)
        arr = sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()
        arr[..., 3] = 255
        return arr
    return frame


@lru_cache(maxsize=1)
def top_beach_image(shore_unit):
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    y0 = 540 - 135 * shore_unit
    sand = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, H)], [_col(_mix(C.sand, C.ember, 0.3)), _col(_mix(C.sand, C.dusk, 0.42))], [0.0, 1.0])
    cv.drawRect(skia.Rect(0, y0, W, H), skia.Paint(Shader=sand))
    r = rng(23)
    for _ in range(620):
        x, y = r.uniform(0, W), r.uniform(y0 + 14, H)
        L = r.uniform(10, 54)
        cv.drawRoundRect(skia.Rect(x, y, x + L, y + 2.4), 1.2, 1.2, paint(_col(C.dusk if r.uniform() < 0.6 else C.foam, 0.22)))
    sea = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, y0)], [_col(_mix(C.sea, C.indigo, 0.55)), _col(_mix(C.sea, C.con, 0.28))], [0.0, 1.0])
    cv.drawRect(skia.Rect(0, 0, W, y0), skia.Paint(Shader=sea))
    for i in range(6):
        xs = np.arange(-20, W + 30, 16.0)
        y = 28 + i * (y0 - 40) / 6 + 7 * np.sin(xs / (120 + i * 26) + i * 1.7)
        cv.drawPath(poly_path(list(zip(xs, y)), False), paint(_col(C.foam, 0.13 + i * 0.05), 2.4))
    return sf.makeImageSnapshot()


def top_beach(points, shore_unit):
    """frame(t) for the view from above: sea, sand, the enclosed plot, and the rope staked at the shore."""
    bg = top_beach_image(float(shore_unit))
    y0 = 540 - 135 * float(shore_unit)
    sf = skia.Surface(W, H)

    def frame(t):
        cv = sf.getCanvas()
        cv.drawImage(bg, 0, 0)
        xs = np.arange(-20, W + 30, 16.0)
        y = y0 + 4 * np.sin(xs / 58 + 1.1 * t)
        cv.drawPath(poly_path(list(zip(xs, y)), False), paint(_col(C.foam, 0.95), 7))
        P = px(points(t))
        cv.drawPath(poly_path([tuple(q) for q in P]), paint(_col(C.gold, 0.3)))
        draw_rope(cv, resample(P, 420), 15)
        stake(cv, P[0, 0], P[0, 1] + 6)
        stake(cv, P[-1, 0], P[-1, 1] + 6)
        arr = sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()
        arr[..., 3] = 255
        return arr
    return frame
