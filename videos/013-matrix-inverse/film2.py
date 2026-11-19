"""Chapters 2 to 4 on the 3D stage (3:00 to 6:31), one pure function of audio time. Every matrix drawn here is the real one from the cast, driven by the
same beats as the equations laid over it."""
from functools import lru_cache

import numpy as np
import skia

from aion import C, keys
from beats import T
from film import on_sheet
from film1 import mix
from shots import A, I2, NULL, RECORD, S, STATES, TEETH, tex, tilt
from stage import Cam, H, Lines, SS, W, draw_glyphs, draw_key, ease, fill, glyph_paths, grid, key_shadow, key_wire, paint_color, polyline, ribbon, ring, slab, track
from verify import LEAN

PX = 135.0
XR, YR = (-4, 4), (-3, 3)
L_INV = np.linalg.inv(LEAN)
EASE = "easy_ease"


def px(x, y):
    return 960 + PX * x, 540 - PX * y


def rot(th):
    return np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])


def shear(M, a):
    return I2 + a * (M - I2)


def along(states, spans, t):
    M = states[0].copy()
    for i, (a, b) in enumerate(spans):
        M = M + ease(t, a, b) * (states[i + 1] - states[i])
    return M


def floor(can, cam, z=-5.0, op=0.42):
    lines = Lines()
    grid(lines, cam, I2, z=z, xr=(-26, 26), yr=(-20, 20), op=op, minor=False, color=C.grid_minor, axes=False, far=64)
    lines.flush(can)


def sheet(can, cam, M, z=0.0, xr=XR, yr=YR, op=1.0, color=None):
    if op <= 0.01:
        return
    lines = Lines()
    slab(can, cam, M, z=z, xr=xr, yr=yr, op=op, tint=color)
    grid(lines, cam, M, z=z + 0.01, xr=xr, yr=yr, op=op, far=70, color=color)
    lines.flush(can)


def rider(can, cam, M, z=0.0, k_op=1.0, b_op=1.0, color=None, t=0.0):
    if k_op > 0.01:
        key_shadow(can, cam, on_sheet(M, z=z + 0.07), TEETH, floor=z, alpha=0.6 * k_op)
        draw_key(can, cam, on_sheet(M, z=z + 0.07), (0, 0, 1), TEETH, thick=0.1, sheen=0.1 * t, op=k_op, color=color)
    if b_op > 0.01:
        ribbon(can, cam, (0, 0), M[:, 0], C.ihat, 0.075, 0.34, z + 0.05, b_op)
        ribbon(can, cam, (0, 0), M[:, 1], C.jhat, 0.075, 0.34, z + 0.05, b_op)


def home_marks(can, cam, op, z=0.02):
    if op > 0.01:
        key_wire(can, cam, on_sheet(I2, z=z), TEETH, C.home, 2.2, op)
        ribbon(can, cam, (0, 0), (1, 0), C.home, 0.03, 0.24, z, op)
        ribbon(can, cam, (0, 0), (0, 1), C.home, 0.03, 0.24, z, op)


def tile(can, cam, M, z, op, scale=1.0, h=0.14):
    """A violet unit square standing on the sheet: the area, as an object."""
    q = scale * (np.asarray(M) @ np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float).T).T
    low, top = np.c_[q, np.full(4, z + 0.02)], np.c_[q, np.full(4, z + 0.02 + h)]
    for i in range(4):
        fill(can, cam.pj([low[i], low[(i + 1) % 4], top[(i + 1) % 4], top[i]])[0], C.det, 0.5 * op, 0.62)
    fill(can, cam.pj(top)[0], C.det, 0.5 * op)
    lines = Lines()
    polyline(lines, cam, np.r_[top, top[:1]], C.det, 3.0, op)
    lines.flush(can)


def inset(can, box, draw):
    """Draw into a framed window given in Manim coordinates, with the stage centred in it."""
    x0, y1 = px(box[0], box[1])
    x1, y0 = px(box[2], box[3])
    can.save()
    can.clipRect(skia.Rect(x0, y0, x1, y1), True)
    can.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Color=skia.ColorBLACK))
    can.translate((x0 + x1) / 2 - W / 2, (y0 + y1) / 2 - H / 2)
    draw()
    can.restore()


@lru_cache(maxsize=16)
def mini(key_, w, h, dist=12.0):
    """A still 3D miniature of the sheet after the matrix `key_` (a tuple of four numbers)."""
    M = np.array(key_, float).reshape(2, 2)
    surf = skia.Surface(w, h)
    can = surf.getCanvas()
    can.clear(skia.ColorBLACK)
    s = h / H
    can.translate(w / 2, h / 2)
    can.scale(s, s)
    can.translate(-W / 2, -H / 2)
    cam = Cam(0, 0, 0, -84, 54, dist)
    sheet(can, cam, M)
    rider(can, cam, M)
    return surf.makeImageSnapshot()


def film_cell(can, M, cx, cy, w, h, op=1.0, dist=12.0):
    x0, y1 = px(cx - w / 2, cy - h / 2)
    x1, y0 = px(cx + w / 2, cy + h / 2)
    rect = skia.Rect(x0, y0, x1, y1)
    can.drawImageRect(mini(tuple(np.asarray(M, float).ravel().round(6)), int(x1 - x0) * SS, int(y1 - y0) * SS, dist), rect, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(Alphaf=float(op)))
    can.drawRect(rect, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2, Color=paint_color(C.frame, op)))


@lru_cache(maxsize=4)
def glyph(text, color_name, size=52):
    return glyph_paths(tex(text, size=size, color=getattr(C, color_name)))


def tag(can, q, glyphs, alpha):
    can.drawRect(skia.Rect(q[0] - 46, q[1] - 34, q[0] + 46, q[1] + 34), skia.Paint(Color=skia.Color(0, 0, 0, int(205 * alpha))))
    draw_glyphs(can, glyphs, float(q[0]), float(q[1]), PX, alpha)


# ---------------------------------------------------------------- chapter 2: rewind
CAM8 = [(T.cut_rewind, (0, 0, 0, -92, 58, 17)), (T.stages + 0.6, (0, 0, 0, -84, 52, 12)), (T.quarter + 1.2, (0, 0, 0.3, -98, 56, 14)), (T.undo_t + 1.3, (0, 0, 0.2, -78, 54, 15)),
        (T.last + 0.6, (0, 0, 0.2, -86, 58, 13)), (T.then_l + 1.1, (0, 0, 0, -92, 52, 12.5))]
STRIP = (I2, LEAN, np.array([[0.0, -1.0], [1.0, 1.0]]))


def s08(can, t):
    can.save()
    can.translate(1.8 * PX, 0)
    cam = track(t, CAM8)
    floor(can, cam)
    out = rot(np.pi / 2 * ease(t, T.quarter + 0.1, T.quarter + 1.1)) @ shear(LEAN, ease(t, T.lean + 0.15, T.lean + 1.15))
    keep = 1 - ease(t, T.last - 0.2, T.last + 1.0)
    wrong = rot(-np.pi / 2 * ease(t, T.undo_t + 0.25, T.undo_t + 1.25) * keep) @ shear(L_INV, ease(t, T.wrong + 0.1, T.wrong + 1.05) * keep)
    right = shear(L_INV, ease(t, T.then_l + 0.05, T.then_l + 1.0)) @ rot(-np.pi / 2 * ease(t, T.right + 0.05, T.right + 1.0))
    M = right @ wrong @ out
    leave = 1 - ease(t, T.lines_up + 0.85, T.lines_up + 1.45)
    z = 0.55 * ease(t, T.lean, T.lean + 0.7) * (1 - ease(t, T.then_l + 0.2, T.then_l + 1.0))
    gray = ease(t, T.wrong, T.undo_t + 1.2) * (1 - ease(t, T.last - 0.2, T.last + 1.0))
    home_marks(can, cam, ease(t, T.how_back, T.how_back + 0.6) * (1 - ease(t, T.lines_up + 0.6, T.lines_up + 1.1)))
    sheet(can, cam, M, z=z, op=ease(t, T.stages + 0.3, T.stages + 1.2) * leave, color=mix(C.grid, C.wrong, gray))
    show = ease(t, T.stages + 0.6, T.stages + 1.2) * leave
    rider(can, cam, M, z=z, k_op=show, b_op=show, color=mix(C.key, C.wrong, gray), t=t)
    can.restore()

    # the film strip
    u = ease(t, T.film - 0.75, T.film + 0.05)
    if u > 0:
        can.save()
        can.translate(0.5 * PX * (1 - u), 0)
        x0, y1 = px(-6.55, 0.85 - 1.59)
        x1, y0 = px(6.55, 0.85 + 1.59)
        can.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Color=paint_color(C.bg, u)))
        can.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2, Color=paint_color(C.frame, u)))
        for x in np.arange(-6.2, 6.21, 0.62):
            for side in (-1, 1):
                a, b = px(x - 0.1, 0.85 + side * 1.42 - 0.075), px(x + 0.1, 0.85 + side * 1.42 + 0.075)
                can.drawRect(skia.Rect(a[0], b[1], b[0], a[1]), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.8, Color=paint_color(C.frame, u)))
        for M_, x in zip(STRIP, (-4.25, 0.0, 4.25)):
            film_cell(can, M_, x, 0.85, 3.7, 2.5, u)
        can.restore()


# ---------------------------------------------------------------- chapter 3: finding the way back
SPANS9 = ((T.upright - 0.35, T.upright + 0.85), (T.move2 + 0.65, T.move2 + 1.85), (T.move3 + 0.35, T.move3 + 1.55), (T.move4 + 0.55, T.move4 + 1.65))
CAM9 = [(T.cut_four, (0, 0.8, 0, -92, 58, 20)), (T.bent, (0, 0.8, 0.3, -88, 58, 19)), (T.move1, (0, 1.2, 0.5, -94, 60, 18)), (T.other, (0, 1.3, 0.5, -84, 58, 18)), (T.move4 + 1.6, (0, 0.6, 0, -88, 56, 12))]


def s09(can, t, fade_=1.0):
    can.save()
    can.translate(2.0 * PX, 0.4 * PX)
    cam = track(t, CAM9)
    floor(can, cam)
    M, op = along(STATES, SPANS9, t), ease(t, T.bent - 0.45, T.bent + 0.25) * fade_
    home_marks(can, cam, ease(t, T.slides, T.slides + 0.7) * fade_, z=0.02)
    sheet(can, cam, M, op=op)
    rider(can, cam, M, k_op=op, b_op=op, t=t)
    lines = Lines()
    r1 = ease(t, T.belongs, T.belongs + 0.4) * (1 - ease(t, T.belongs + 0.9, T.belongs + 1.3))
    r2 = ease(t, T.home4 - 0.1, T.home4 + 0.3) * (1 - ease(t, T.home4 + 0.55, T.home4 + 0.85))
    ring(lines, cam, (1, 0), 0.26, 0.06, C.ihat, 3.2, max(r1, r2))
    ring(lines, cam, (0, 1), 0.26, 0.06, C.jhat, 3.2, r2)
    rule = ease(t, T.other, T.other + 0.6) * (1 - ease(t, T.move3 + 0.3, T.move3 + 0.8))
    if rule > 0:                                      # four times too tall
        polyline(lines, cam, np.array([[-1.5, 0, 0.06], [-1.5, 4, 0.06]]), C.jhat, 3.2, rule)
        for k in range(5):
            polyline(lines, cam, np.array([[-1.62, k, 0.06], [-1.38, k, 0.06]]), C.jhat, 3.2, rule)
    lines.flush(can)
    if rule > 0:
        tag(can, cam.pj(np.array([[-2.05, 4.0, 0.06]]))[0][0], glyph("4", "jhat"), rule)
        tag(can, cam.pj(np.array([[-2.05, 1.0, 0.06]]))[0][0], glyph("1", "home"), rule)
    can.restore()


BL10, BR10 = (-6.6, -0.85, -0.2, 3.5), (0.2, -0.85, 6.6, 3.5)


def s10(can, t):
    if t < T.cut_record + 0.6:
        s09(can, t, 1 - ease(t, T.cut_record + 0.05, T.cut_record + 0.5))
    else:
        floor(can, Cam(0, 0, 0, -86, 46, 16))
    t0, gap = T.as_bent + 0.1, 1.33
    spans = [(t0 + i * gap, t0 + i * gap + 1.05) for i in range(4)]
    sway = 4 * np.sin(t * 0.3)

    def left():
        cam = Cam(0, 0.7, 0, -86 + sway, 56, 25)
        M, op = along(STATES, spans, t), ease(t, T.never - 0.2, T.never + 0.5)
        sheet(can, cam, M, op=op)
        rider(can, cam, M, k_op=op, b_op=op, t=t)

    def right():
        cam = Cam(0, 0, 0, -94 - sway, 52, 11.5)
        M, op = along(RECORD, spans, t), ease(t, T.second_grid - 0.1, T.second_grid + 0.6)
        sheet(can, cam, M, op=op)
        rider(can, cam, M, k_op=op, b_op=op, t=t)
    if t > T.never - 0.25:
        inset(can, BL10, left)
    if t > T.second_grid - 0.15:
        inset(can, BR10, right)


def s11(can, t):
    floor(can, Cam(0, 0, 0, -90 + 6 * np.sin(t * 0.2), 44, 16))
    xs = np.linspace(-5.25, 5.25, 5)
    for k in range(5):
        at = T.recognize - 0.2 + 0.2 * k
        u = ease(t, at, at + 0.5)
        if u > 0:
            film_cell(can, STATES[4 - k], xs[k], 0.0, 2.42, 1.9, u, dist=16.0)


CAM12 = [(T.cut_det, (0, 0.6, 0, -92, 58, 15)), (T.area, (0, 0.8, 0.2, -84, 58, 14)), (T.squash_again + 1.0, (0, 0.6, 0.2, -94, 62, 12.5)), (T.four + 2.4, (0, 0.8, 0, -86, 56, 15))]


def s12(can, t):
    can.save()
    can.translate(2.0 * PX, 0.4 * PX)
    cam = track(t, CAM12)
    floor(can, cam)
    spans = ((T.slide_a + 0.1, T.slide_a + 0.9), (T.area, T.area + 0.8), (T.squash_again, T.squash_again + 1.0), (T.quarter_a + 0.5, T.quarter_a + 1.3))
    M = along(STATES, spans, t) + ease(t, T.four + 0.6, T.four + 2.3) * (A - I2)
    op = ease(t, T.cut_det + 0.05, T.cut_det + 0.65) * (1 - ease(t, T.det + 1.0, T.det + 1.6))
    sheet(can, cam, M, op=op)
    if op > 0.01:
        tile(can, cam, M, 0.0, op)
    rider(can, cam, M, k_op=0.0, b_op=op, t=t)
    can.restore()


# ---------------------------------------------------------------- chapter 4: what can't come back
def stretch(s):
    return 1 / np.linalg.svd(tilt(s), compute_uv=False)[-1]


def s_for(goal):
    """The tilt at which the inverse must stretch by exactly `goal`."""
    lo, hi = 0.0, 1.0 - 1e-9
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if stretch(mid) < goal else (lo, mid)
    return lo


TILT = keys((T.tilt, 0.0), (T.x10 + 0.44, s_for(10), EASE), (T.x100 + 0.58, s_for(100)), (T.x1000 + 0.73, s_for(1000)), (T.line_up + 0.1, s_for(1000)), (T.line_up + 0.6, 1.0, EASE), lead=0)
BL13, BR13 = (-6.6, -2.5, -0.2, 3.3), (0.2, -2.5, 6.6, 3.3)


def s13(can, t):
    floor(can, Cam(0, 0, 0, -86, 46, 16))
    c, op = float(TILT(t)), ease(t, T.tilt - 0.75, T.tilt - 0.05)
    M = tilt(c)
    sway = 5 * np.sin(t * 0.22)

    def left():
        cam = Cam(0, 0, 0, -84 + sway, 56, 23)
        sheet(can, cam, M, xr=(-3, 3), yr=(-2.5, 2.5), op=op)
        tile(can, cam, M, 0.0, op)
        col = mix(C.key, C.shadow, float(np.clip((c - 0.99) / 0.01, 0, 1)))
        rider(can, cam, M, k_op=op, b_op=op, color=col, t=t)

    def right():
        if c > 0.9997:
            return
        cam = Cam(0, 0, 0, -96 - sway, 54, 12)
        Mi = np.linalg.inv(M)
        lines = Lines()
        grid(lines, cam, Mi, z=0.0, xr=(-9, 9), yr=(-9, 9), op=op, minor=False, far=70)
        lines.flush(can)
        U, sv, _ = np.linalg.svd(Mi)
        d = U[:, 0] if U[1, 0] <= 0 else -U[:, 0]         # toward the free corner, away from the panel's name
        ribbon(can, cam, (0, 0), min(sv[0], 7.0) * d, C.back, 0.13, 0.5, 0.05, op)
    if op > 0:
        inset(can, BL13, left)
        inset(can, BR13, right)


X0 = np.array([1.0, 1.0])
RISE = 3.4
TS = np.linspace(-2.3, 0.55, 9)
COL = S[:, 0] / np.linalg.norm(S[:, 0])
ACROSS = np.array([2.0, 1.0]) / np.sqrt(5.0)
CAM14 = [(T.cut_many, (3.0, 2.0, 1.2, -72, 32, 17)), (T.pick + 2.5, (3.6, 2.4, 1.0, -64, 30, 13)), (T.who + 1.6, (2.6, 1.0, 1.7, -50, 24, 16)), (T.rays + 1.0, (2.6, 1.0, 1.7, -36, 24, 16)),
         (T.way_back + 1.2, (3.0, 1.5, 1.6, -58, 24, 15))]


def s14(can, t):
    cam = track(t, CAM14)
    floor(can, cam)
    lines = Lines()
    grid(lines, cam, I2, origin=(3, 2), xr=(-7, 7), yr=(-6, 6), op=0.5, minor=False, color=C.grid_minor, axes=False, far=50)
    lines.flush(can)
    a, b = -3 * COL, 11 * COL
    w = 0.07 * np.array([-COL[1], COL[0]])
    fill(can, cam.pj(np.c_[np.array([a + w, b + w, b - w, a - w]), np.zeros(4)])[0], C.shadow)

    spot = np.array([*(S @ X0), 0.02])
    top = ease(t, T.who - 0.3, T.who + 0.5)
    pts = np.array([[*(X0 + s_ * NULL), RISE] for s_ in TS])
    if top > 0:
        grid(lines, cam, I2, origin=(1, 0), z=RISE, xr=(-5, 5), yr=(-6, 6), op=0.55 * top, minor=False, axes=False, far=50)
        lines.flush(can)
        d = ease(t, T.who, T.who + 0.9)
        p0, p1 = np.array([*(X0 - 3.6 * NULL), RISE]), np.array([*(X0 + 2.0 * NULL), RISE])
        polyline(lines, cam, np.array([p0, p0 + d * (p1 - p0)]), C.null, 3.4, 1.0)
    rays = ease(t, T.rays - 0.2, T.rays + 0.7)
    if rays > 0:                                      # the shadow's rays run along the crushed direction, up on the sheet they came from
        u = NULL / np.linalg.norm(NULL)
        for k in (-2.4, -1.6, -0.8, 0.8, 1.6, 2.4):
            f = X0 + k * ACROSS
            polyline(lines, cam, np.array([[*(f - 5 * u), RISE], [*(f + 5 * u), RISE]]), C.null, 1.8, 0.5 * rays)
    fan = ease(t, T.fan, T.fan + 1.2) * (1 - ease(t, T.way_back - 0.25, T.way_back + 0.15))
    for p in pts:
        if fan > 0:
            polyline(lines, cam, np.array([p, p + fan * (spot - p)]), C.fwd, 2.6, 0.95)
    lines.flush(can)
    back = T.way_back + 0.5
    gray = ease(t, T.matrix_gives, T.matrix_gives + 0.9)
    for i, p in enumerate(pts):
        u = ease(t, back + 0.14 * i, back + 0.14 * i + 0.5)
        if u > 0:
            tip = spot + u * 0.94 * (p - spot)
            polyline(lines, cam, np.array([spot, tip]), mix(C.back, C.wrong, gray), 3.0, 1 - 0.45 * gray)
            lines.flush(can)
            q = cam.pj(tip[None])[0][0]
            can.drawCircle(float(q[0]), float(q[1]), 7, skia.Paint(AntiAlias=True, Color=paint_color(mix(C.back, C.wrong, gray), 1 - 0.45 * gray)))
    for i, p in enumerate(pts):
        u = ease(t, T.who + 0.3 + 0.12 * i, T.who + 0.7 + 0.12 * i)
        if u > 0:
            q = cam.pj(p[None])[0][0]
            can.drawCircle(float(q[0]), float(q[1]), 10, skia.Paint(AntiAlias=True, Color=paint_color(C.null, u)))
    m = ease(t, T.pick, T.pick + 0.6)
    if m > 0:
        ring(lines, cam, spot[:2], 0.36, 0.03, C.vec, 3.4, m)
        lines.flush(can)
        q = cam.pj(spot[None])[0][0]
        can.drawCircle(float(q[0]), float(q[1]), 12, skia.Paint(AntiAlias=True, Color=paint_color(C.vec, m)))


C1, C2 = S[:, 0], S[:, 1]
SIDE = np.array([-2.0, 3.0]) / np.sqrt(13.0) * 0.26


def arc(a, b, h, upto, n=30):
    s_ = np.linspace(0, upto, n)
    return np.c_[np.outer(1 - s_, a) + np.outer(s_, b), 0.08 + h * 4 * s_ * (1 - s_)]


def s15(can, t):
    can.save()
    can.translate(-1.5 * PX, 0.2 * PX)
    cam = Cam(0.6, 0, 0.2, -92 + 8 * ease(t, T.cut_columns, T.cut_fact), 54, 11.5)
    floor(can, cam)
    sheet(can, cam, I2, xr=(-4, 5), yr=(-3.5, 3.5), op=0.6 * ease(t, T.cut_columns + 0.05, T.cut_columns + 0.5))
    ribbon(can, cam, (0, 0), C1, C.ihat, 0.1, 0.38, 0.06, ease(t, T.read_cols, T.read_cols + 0.5))
    ribbon(can, cam, SIDE, C2 + SIDE, C.jhat, 0.1, 0.38, 0.06, ease(t, T.read_cols + 0.45, T.read_cols + 0.95))
    second = ease(t, T.twice - 0.1, T.twice + 0.5) * (1 - ease(t, T.dependent - 0.5, T.dependent))
    ribbon(can, cam, C2 + SIDE, 2 * C2 + SIDE, C.jhat, 0.1, 0.38, 0.06, second)
    cr = ease(t, T.crushed, T.crushed + 0.6)
    ribbon(can, cam, (0, 0), NULL, C.null, 0.11, 0.42, 0.06, cr)
    if cr > 0:
        tag(can, cam.pj(np.array([[NULL[0] + 1.25, NULL[1], 0.06]]))[0][0], glyph(r"(1,\,-2)", "null", 46), ease(t, T.crushed + 0.3, T.crushed + 0.8))
    go, ret = ease(t, T.recipe_cols, T.recipe_cols + 0.8), ease(t, T.minus + 0.05, T.minus + 1.05)
    lines = Lines()
    if go > 0.005:
        P = arc(np.zeros(2), C1, 0.55, go)
        polyline(lines, cam, P, C.ihat, 4.2, 1.0)
        here = P[-1]
        if ret > 0.005:
            Q = arc(C1, np.zeros(2), 1.25, ret)
            polyline(lines, cam, Q, C.jhat, 4.2, 1.0)
            here = Q[-1]
        lines.flush(can)
        q = cam.pj(here[None])[0][0]
        can.drawCircle(float(q[0]), float(q[1]), 13, skia.Paint(AntiAlias=True, Color=paint_color(C.vec)))
    can.restore()


CX16, CY16, W16, H16 = (-5.0, -1.667, 1.667, 5.0), 0.35, 2.75, 3.8
HEALTHY = 0.35
MOMENTS = (T.f_cols, T.f_area, T.f_dir, T.f_back)
LIGHT = [keys((T.cut_fact + 0.1, 0.0), (T.cut_fact + 0.6, 0.38), (b - 0.1, 0.38), (b + 0.3, 1.0), lead=0) for b in MOMENTS]
ROCK = keys((T.if_any, 1.0), (T.if_any + 0.9, 0.0, EASE), (T.all_true - 0.25, 0.0), (T.all_true + 0.45, 1.0, EASE), lead=0)


def s16(can, t):
    floor(can, Cam(0, 0, 0, -88, 44, 16))
    for i, cx in enumerate(CX16):
        c = HEALTHY + (1 - HEALTHY) * ease(t, MOMENTS[i] + 0.2, MOMENTS[i] + 1.2) * float(ROCK(t))
        op, bad = float(LIGHT[i](t)), float(np.clip((c - 0.96) / 0.04, 0, 1))
        M = tilt(c)
        box = (cx - W16 / 2, CY16 - H16 / 2, cx + W16 / 2, CY16 + H16 / 2)

        def draw():
            cam = Cam(0.9 if i < 2 else 0.0, 0.5 if i < 2 else -0.3 if i == 2 else 0.0, 0, -82, 50, 15 if i != 3 else 12)
            lines = Lines()
            grid(lines, cam, I2, xr=(-3, 4), yr=(-3, 4), op=0.5 * max(op, 0.5), minor=False, far=40)
            lines.flush(can)
            if i == 0:
                ribbon(can, cam, (0, 0), 0.62 * M[:, 0], C.ihat, 0.13, 0.5, 0.05, op)
                ribbon(can, cam, (0, 0), 0.62 * M[:, 1], C.jhat, 0.13, 0.5, 0.05, op)
            elif i == 1:
                tile(can, cam, M, 0.0, op, scale=0.62, h=0.22)
            elif i == 2:
                polyline(lines, cam, np.array([[0, 0, 0.05], [NULL[0], NULL[1], 0.05]]), C.null, 2.4, 0.4 * op)
                lines.flush(can)
                ribbon(can, cam, (0, 0), M @ NULL, C.null, 0.13, 0.5, 0.05, op)
            else:
                a, b = np.array([-1.05, 0.0]), np.array([1.05, 0.0])
                polyline(lines, cam, arc(a, b, 1.2, 1.0), C.fwd, 4.0, op)
                if bad < 1:
                    polyline(lines, cam, arc(b, a, 0.5, 1.0), C.back, 4.0, op * (1 - bad))
                lines.flush(can)
                for p in (a, b):
                    q = cam.pj(np.array([[*p, 0.08]]))[0][0]
                    can.drawCircle(float(q[0]), float(q[1]), 11, skia.Paint(AntiAlias=True, Color=paint_color(C.vec, op)))
        inset(can, box, draw)
        x0, y1, x1, y0 = *px(box[0], box[1]), *px(box[2], box[3])
        can.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2 + 3 * bad, Color=paint_color(mix(C.frame, C.null, bad), max(op, 0.5))))


# ---------------------------------------------------------------- the whole film
SCENES = ((T.cut_four, s08), (T.cut_record, s09), (T.cut_check, s10), (T.cut_det, s11), (T.cut_tilt, s12), (T.cut_many, s13), (T.cut_columns, s14), (T.cut_fact, s15), (float("inf"), s16))


def frame(t):
    """One finished frame of Chapters 2 to 4 at audio time t, as RGBA uint8."""
    surf = skia.Surface(W * SS, H * SS)
    can = surf.getCanvas()
    can.scale(SS, SS)
    can.clear(skia.ColorBLACK)
    for end, fn in SCENES:
        if t < end:
            fn(can, t)
            break
    return surf.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
