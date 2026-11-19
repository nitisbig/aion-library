"""Chapters 5 to 7 on the 3D stage (6:31 to 10:08), one pure function of audio time. Every value drawn comes from the same cast and the same real
computations as before: the recipes, the drone's axes, the blur spectrum, the key's line integrals and the baked CT solves."""
from functools import lru_cache

import numpy as np
import skia

from aion import C, keys
from beats import T
from ct import recon
from deblur import KEEP, band_maps, bars
from film import on_sheet
from film1 import LAT, mix as tint
from film2 import PX, floor, inset, px, rider, sheet, tag
from shots import A, DRONE, I2, MAPPED, POWDER, S, SCOOPS, SHAFT, TARGET, TEETH, lab, shadow_profile, tex, tilt
from stage import Cam, H, Lines, SS, W, card, draw_glyphs, draw_key, ease, fill, glyph_paths, grid, key_shadow, paint_color, polyline, ribbon, ring, slab, track
from verify import key_raster
from world import SPEED, _blocks

EASE = "easy_ease"
C1, C2 = POWDER[:, 0], POWDER[:, 1]
MIX_O = np.array([-8.6, 0.0])


@lru_cache(maxsize=64)
def gl(text, color_name, size=44):
    return glyph_paths(tex(text, size=size, color=getattr(C, color_name)))


@lru_cache(maxsize=32)
def word(text, color_name="text", size=36):
    return glyph_paths(lab(text, size=size, color=getattr(C, color_name)))


def put(can, cam, p, glyphs, alpha=1.0, plate=False, dx=0.0, dy=0.0):
    if alpha <= 0.01:
        return
    q = cam.pj(np.array([p], float))[0][0] + np.array([dx, dy])
    if plate:
        tag(can, q, glyphs, alpha)
    else:
        draw_glyphs(can, glyphs, float(q[0]), float(q[1]), PX, alpha)


def dot(can, cam, p, r, color, alpha=1.0):
    if alpha > 0.01:
        q = cam.pj(np.array([p], float))[0][0]
        can.drawCircle(float(q[0]), float(q[1]), r, skia.Paint(AntiAlias=True, Color=paint_color(color, alpha)))


def dashed(lines, cam, a, b, color, alpha, upto=1.0, n=16):
    a, b = np.asarray(a, float), np.asarray(b, float)
    for k in range(n):
        u0, u1 = k / n, (k + 0.55) / n
        if u0 < upto:
            polyline(lines, cam, np.array([a + (b - a) * u0, a + (b - a) * min(u1, upto)]), color, 2.6, alpha)


def arc3(a, b, h, upto=1.0, n=40):
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = np.linspace(0, upto, n)[:, None]
    return a + s * (b - a) + np.c_[np.zeros((n, 2)), h * 4 * s * (1 - s)]


# ---------------------------------------------------------------- chapter 5: two powders
def nut3(v, z=0.04):
    return np.array([v[0], v[1], z], float)


def mix3(v, z=0.04):
    return np.array([MIX_O[0] + v[0], MIX_O[1] + v[1], z], float)


def board(can, cam, origin, xr, yr, op):
    if op <= 0.01:
        return
    lines = Lines()
    slab(can, cam, I2, origin, xr=xr, yr=yr, op=op)
    grid(lines, cam, I2, origin=origin, z=0.01, xr=xr, yr=yr, op=op, minor=False, far=60)
    lines.flush(can)


def pw_cam(t):
    u = ease(t, T.geo - 0.2, T.geo + 1.2)
    return Cam(4.2 - 4.3 * u, 3.2 - 0.3 * u, 0, -90 + 3 * np.sin(t * 0.2), 56, 15.5 + 7.5 * u), 2.7 * PX * (1 - u)


def nut_labels(can, cam, op):
    put(can, cam, (7.62, 0.6, 0.04), word("protein"), op, plate=True)
    put(can, cam, (-0.1, 7.45, 0), word("fibre"), op)


def mix_labels(can, cam, op):
    put(can, cam, (MIX_O[0] + 3.5, -0.55, 0), word("first"), op)
    put(can, cam, (MIX_O[0] - 0.1, 5.45, 0), word("second"), op)


def marks(can, cam, v, h, d, label, alpha=1.0):
    lines = Lines()
    dashed(lines, cam, nut3((7, 0)), nut3(TARGET), C.vec, alpha, v)
    dashed(lines, cam, nut3((0, 6)), nut3(TARGET), C.vec, alpha, h)
    lines.flush(can)
    put(can, cam, (7, -0.5, 0.04), gl("7", "vec"), v * alpha)
    put(can, cam, (-0.45, 6, 0.04), gl("6", "vec"), h * alpha)
    dot(can, cam, nut3(TARGET), 13, C.vec, d * alpha)
    put(can, cam, nut3(TARGET), gl(r"\mathbf{b}=(7,\,6)", "vec"), label * alpha, dy=-52)


def s17(can, t):
    cam, sx = pw_cam(t)
    can.save()
    can.translate(sx, 0)
    floor(can, cam)
    op = ease(t, T.powders - 0.3, T.powders + 0.4)
    board(can, cam, (0, 0), (0, 8.5), (0, 7), op)
    nut_labels(can, cam, op)
    ribbon(can, cam, (0, 0), C1 * ease(t, T.cols_mat + 0.3, T.cols_mat + 1.0), C.ihat, 0.1, 0.36, 0.05, 1.0)
    ribbon(can, cam, (0, 0), C2 * ease(t, T.cols_mat + 0.75, T.cols_mat + 1.45), C.jhat, 0.1, 0.36, 0.05, 1.0)
    walk = ease(t, T.scoops_in + 0.4, T.scoops_in + 1.1) * (1 - ease(t, T.other_way - 0.1, T.other_way + 0.4))
    ribbon(can, cam, C1, C1 + C2 * walk, C.jhat, 0.08, 0.3, 0.05, min(walk * 3, 1.0))
    dot(can, cam, nut3(C1 + C2), 11, C.fwd, ease(t, T.get, T.get + 0.4) * (1 - ease(t, T.other_way - 0.1, T.other_way + 0.4)))
    marks(can, cam, ease(t, T.target, T.target + 0.7), ease(t, T.six, T.six + 0.7), ease(t, T.how_many - 0.1, T.how_many + 0.35), ease(t, T.how_many, T.how_many + 0.5))
    can.restore()


def s18(can, t):
    cam, sx = pw_cam(t)
    can.save()
    can.translate(sx, 0)
    floor(can, cam)
    clr = 1 - ease(t, T.cut_weak - 0.4, T.cut_weak - 0.1)
    rec = ease(t, T.geo + 0.2, T.geo + 0.8)
    board(can, cam, (0, 0), (0, 8.5), (0, 7), 1.0)
    board(can, cam, MIX_O, (0, 4.2), (0, 5), rec)
    nut_labels(can, cam, 1.0)
    mix_labels(can, cam, rec)
    ribbon(can, cam, (0, 0), C1, C.ihat, 0.1, 0.36, 0.05, 1.0)
    ribbon(can, cam, (0, 0), C2, C.jhat, 0.1, 0.36, 0.05, 1.0)
    marks(can, cam, clr, clr, 1.0, 1.0)
    lines = Lines()
    ring(lines, cam, TARGET, 0.34, 0.05, C.vec, 3.2, ease(t, T.landed + 0.3, T.landed + 0.9) * clr)
    lines.flush(can)
    start, end = nut3(TARGET, 0.1), mix3(SCOOPS, 0.1)
    d = ease(t, T.follow, T.follow + 1.5)
    if d > 0 and clr > 0:                             # the thread home leaves the target and lands on the recipe
        P = arc3(start, end, 3.2, d)
        polyline(lines, cam, P, C.back, 4.6, clr)
        lines.flush(can)
        dot(can, cam, P[-1], 9, C.back, clr)
    dot(can, cam, end, 14, C.vec, ease(t, T.follow + 1.45, T.follow + 1.85) * clr)
    g1, g2 = ease(t, T.answer, T.answer + 0.7), ease(t, T.one_of, T.one_of + 0.7)
    dashed(lines, cam, mix3((2, 0)), end, C.vec, clr, g1)
    dashed(lines, cam, mix3((0, 1)), end, C.vec, clr, g2)
    lines.flush(can)
    put(can, cam, mix3((2, -0.5)), gl("2", "ihat", 38), g1 * clr)
    put(can, cam, mix3((-0.45, 1)), gl("1", "jhat", 38), g2 * clr)
    ribbon(can, cam, C1, C1 + C1 * g1, C.ihat, 0.1, 0.36, 0.07, min(g1 * 3, 1) * clr)
    ribbon(can, cam, 2 * C1, 2 * C1 + C2 * g2, C.jhat, 0.1, 0.36, 0.07, min(g2 * 3, 1) * clr)
    put(can, cam, nut3(TARGET), word("ended up", "vec", 36), ease(t, T.ended - 0.1, T.ended + 0.35) * clr, plate=False, dx=135, dy=0)
    put(can, cam, end, word("started", "vec", 36), ease(t, T.want + 0.7, T.want + 1.15) * clr, dx=112, dy=8, plate=True)
    put(can, cam, (-0.45, 6, 0.04), gl("6", "vec"), clr, plate=True)    # the thread passes behind the axis mark
    can.restore()


GOAL = np.array([6.0, 4.0])
RECIPES = ((2, 0), (1, 2), (0, 4))
XMAX, YMAX = 8.5, 7.0


def edge(d):
    return np.asarray(d, float) * min(XMAX / d[0], YMAX / d[1])


def s19(can, t):
    cam, _ = pw_cam(t)
    floor(can, cam)
    board(can, cam, (0, 0), (0, 8.5), (0, 7), 1.0)
    board(can, cam, MIX_O, (0, 4.2), (0, 5), 1.0)
    nut_labels(can, cam, 1.0)
    mix_labels(can, cam, 1.0)
    M = tilt(ease(t, T.weak - 0.1, T.weak + 1.4))
    far1, far2 = edge(M[:, 0]), edge(M[:, 1])
    corner = [(XMAX, YMAX)] if far2[1] >= YMAX - 1e-9 else []
    fill(can, cam.pj(np.array([nut3(v, 0.02) for v in [(0, 0), far1, *corner, far2]]))[0], C.fwd, 0.16 * ease(t, T.cut_weak + 0.1, T.cut_weak + 0.7))
    step2 = tilt(1.0)[:, 1]
    lines = Lines()
    ln = ease(t, T.line1 - 0.3, T.line1 + 0.5)
    if ln > 0:
        ribbon(can, cam, (0, 0), edge(C1) * ln, C.shadow, 0.1, 0.0, 0.03, 1.0)
    ribbon(can, cam, (0, 0), C1, C.ihat, 0.1, 0.36, 0.05, 1.0)
    ribbon(can, cam, (0, 0), M[:, 1], C.jhat, 0.1, 0.36, 0.05, 1.0)
    samples = ((0.5, 0.0), (0.4, 1.0), (1.0, 1.0), (1.5, 0.5), (1.2, 2.0), (2.0, 1.0))
    for k, (a, b) in enumerate(samples):
        op = ease(t, T.every_mix + 0.17 * k, T.every_mix + 0.17 * k + 0.35) * (1 - ease(t, T.off - 0.45, T.off - 0.05))
        dot(can, cam, nut3(a * C1 + b * step2), 9, C.fwd, op)

    bad = 1 - ease(t, T.on_line - 0.55, T.on_line - 0.15)
    foot = (TARGET @ C1) / (C1 @ C1) * C1
    dot(can, cam, nut3(TARGET), 13, C.vec, max(bad, ease(t, T.no_ans - 0.1, T.no_ans + 0.35)))
    put(can, cam, nut3(TARGET), gl(r"\mathbf{b}=(7,\,6)", "vec"), bad, dy=-52)
    ring(lines, cam, TARGET, 0.34, 0.05, C.vec, 3.2, ease(t, T.off - 0.1, T.off + 0.4) * bad)
    lines.flush(can)
    ribbon(can, cam, (0, 0), foot * ease(t, T.off + 0.4, T.off + 1.1), C.wrong, 0.07, 0.28, 0.07, bad)
    dashed(lines, cam, nut3(foot), nut3(TARGET), C.wrong, bad, ease(t, T.off + 1.0, T.off + 1.4))
    lines.flush(can)

    g = ease(t, T.on_line + 0.05, T.on_line + 0.45)
    dot(can, cam, nut3(GOAL), 13, C.vec, g)
    put(can, cam, nut3(GOAL), gl(r"(6,\,4)", "vec", 40), g, dx=86, dy=52, plate=True)
    for k, r in enumerate(RECIPES):                   # three different recipes, one mix: their threads all land on the goal
        at = T.on_line + 0.45 + 0.7 * k
        u = ease(t, at, at + 0.7)
        if u > 0:
            polyline(lines, cam, arc3(mix3(r, 0.08), nut3(GOAL, 0.08), 2.6 + 0.5 * k, u), C.fwd, 3.2, 1.0)
            lines.flush(can)
            dot(can, cam, mix3(r, 0.08), 11, C.vec, min(u * 2.5, 1.0))
            put(can, cam, mix3(r), gl(rf"({r[0]},\,{r[1]})", "vec", 34), min(u * 2.5, 1.0), dx=72, dy=-20, plate=True)
    along = ease(t, T.on_line + 2.2, T.on_line + 2.8)
    if along > 0:
        a, b = mix3(RECIPES[2], 0.06), mix3(RECIPES[0], 0.06)
        polyline(lines, cam, np.array([a, a + along * (b - a)]), C.null, 3.6, 1.0)
        lines.flush(can)
    put(can, cam, (-0.1, 7.45, 0), word("fibre"), 1.0, plate=True)      # the axis names stay readable above the threads
    put(can, cam, (MIX_O[0] - 0.1, 5.45, 0), word("second"), 1.0, plate=True)


# ---------------------------------------------------------------- chapter 6: the way back at work
SKY = 2.3


def quad(can, cam, t, p, heading, op):
    """A small quadcopter, rotors turning, hovering at p."""
    if op <= 0.01:
        return
    c, s_ = np.cos(heading), np.sin(heading)
    lines = Lines()
    for a in (np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4):
        d = np.array([np.cos(a + heading), np.sin(a + heading), 0.0])
        hub = np.asarray(p) + 0.62 * d
        polyline(lines, cam, np.array([p, hub]), C.cam, 4.2, op)
        ring(lines, cam, hub[:2], 0.3, hub[2], C.cam, 2.6, op, n=28)
        w = t * 22 + a
        b = 0.28 * np.array([np.cos(w), np.sin(w), 0.0])
        polyline(lines, cam, np.array([hub - b, hub + b]), C.home, 2.4, op)
    lines.flush(can)
    dot(can, cam, p, 15, C.cam, op)


def s20(can, t):
    can.save()
    can.translate(-2.0 * PX, 0.0)
    cam = Cam(2.6, 1.9, 1.0, -102 + 10 * ease(t, T.observers, T.cut_camera), 40, 17.5)
    floor(can, cam)
    board(can, cam, (0, 0), (-3, 8), (-3, 7), ease(t, T.observers + 0.25, T.observers + 0.85))
    pin = ease(t, T.observers + 1.4, T.observers + 1.85)
    m3 = nut3(MAPPED, 0.05)
    lines = Lines()
    ring(lines, cam, MAPPED, 0.36, 0.05, C.vec, 3.2, ease(t, T.landmark - 0.1, T.landmark + 0.4))
    g = ease(t, T.axes + 1.75, T.axes + 2.35)
    dashed(lines, cam, nut3((3, 0)), m3, C.vec, 1.0, g)
    dashed(lines, cam, nut3((0, 4)), m3, C.vec, 1.0, g)
    lines.flush(can)
    dot(can, cam, m3, 13, C.vec, pin)
    u = ease(t, T.drone, T.drone + 1.5)
    if u > 0.01:
        grid(lines, cam, DRONE * (0.22 + 0.78 * u), z=SKY, xr=(-2, 3), yr=(-1, 3), op=0.9 * min(1.0, 3 * u), minor=False, color=C.cam, axes=False, far=60)
        lines.flush(can)
    a, b = DRONE[:, 0], 2 * DRONE[:, 0]
    ribbon(can, cam, (0, 0), a * ease(t, T.steps - 0.1, T.steps + 0.25), C.cam, 0.09, 0.32, SKY + 0.03, 1.0)
    ribbon(can, cam, a, a + a * ease(t, T.steps + 0.25, T.steps + 0.6), C.cam, 0.09, 0.32, SKY + 0.03, min(1.0, ease(t, T.steps + 0.25, T.steps + 0.4)))
    w3 = ease(t, T.steps + 1.2, T.steps + 1.65)
    ribbon(can, cam, b, b + w3 * (MAPPED - b), C.cam, 0.09, 0.32, SKY + 0.03, min(1.0, w3 * 3))
    stem = ease(t, T.steps + 1.3, T.steps + 1.9)          # the same place, seen from both levels
    if stem > 0:
        polyline(lines, cam, np.array([m3, m3 + np.array([0, 0, stem * SKY])]), C.vec, 2.6, 1.0)
        lines.flush(can)
        dot(can, cam, m3 + np.array([0, 0, SKY]), 11, C.vec, stem)
    quad(can, cam, t, (0, 0, SKY + 0.25), float(np.arctan2(DRONE[1, 0], DRONE[0, 0])), ease(t, T.drone - 0.25, T.drone + 0.25))
    can.restore()


W21, H21 = 6.3, 6.3 * 468 / 894
CL21 = np.array([-3.3, 0.45])
BOX21 = (CL21[0] - W21 / 2, CL21[1] - H21 / 2, CL21[0] + W21 / 2, CL21[1] + H21 / 2)
Z_START, RATE = 6.0, 0.6


def s21(can, t):
    floor(can, Cam(0, 0, 0, -88, 44, 16))
    walked = RATE * max(0.0, t - T.cut_camera)
    cam_z = lambda w: Z_START - SPEED * w
    t_lock = T.never_walk - 0.3
    lock = ease(t, t_lock, t_lock + 1.0)
    zc = (Z_START - 13.0) + lock * (cam_z(walked) - cam_z(RATE * max(0.0, t_lock - T.cut_camera)))
    op = ease(t, T.cut_camera + 0.05, T.cut_camera + 0.55)

    def outside():
        cam = Cam(1.5, 0, 4.5, -112, 42, 62)
        lines = Lines()
        grid(lines, cam, I2, xr=(-24, 24), yr=(-12, 12), op=0.42 * op, minor=False, color=C.grid_minor, axes=False, far=120)
        lines.flush(can)
        faces = []
        for x0, x1, z0, z1, h, role in _blocks():
            ax, bx = zc - z1, zc - z0
            if bx < -24 or ax > 24:
                continue
            c = np.array([[ax, x0], [bx, x0], [bx, x1], [ax, x1]], float)
            faces.append((-float(np.linalg.norm(np.array([*c.mean(axis=0), h / 2]) - cam.eye)), c, h, role))
        for _, c, h, role in sorted(faces, key=lambda f: f[0]):
            top = np.c_[c, np.full(4, h)]
            low = np.c_[c, np.zeros(4)]
            for i in range(4):
                j = (i + 1) % 4
                mid = 0.5 * (top[i] + top[j])
                out = mid[:2] - c.mean(axis=0)
                if out @ (cam.eye[:2] - mid[:2]) > 0:
                    fill(can, cam.pj([top[i], top[j], low[j], low[i]])[0], C.shadow, op, 0.42 + 0.22 * (i % 2))
            fill(can, cam.pj(top)[0], getattr(C, role), op)
        x = zc - cam_z(walked)
        eye = np.array([x, 0.0, 8.0])
        for sy, sz in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
            polyline(lines, cam, np.array([eye, eye + np.array([9.0, 4.2 * sy, -3.2 + 2.4 * sz])]), C.cam, 2.0, 0.9 * op)
        lines.flush(can)
        cone = [eye + np.array([9.0, 4.2 * a, -3.2 + 2.4 * b]) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        fill(can, cam.pj(cone)[0], C.cam, 0.2 * op)
        dot(can, cam, eye, 13, C.cam, op)
        put(can, cam, eye + np.array([-2.2, 0, 1.2]), gl("C", "cam", 44), op * ease(t, T.placed, T.placed + 0.4))
    inset(can, BOX21, outside)


@lru_cache(maxsize=2)
def heat(i, size=405 * SS):
    """The true blur matrix (0) or its true inverse (1), every entry shown, on a plate lying in the scene."""
    surf = skia.Surface(size, size)
    can = surf.getCanvas()
    can.clear(skia.ColorBLACK)
    can.translate(size / 2, size / 2)
    can.scale(size / H, size / H)
    can.translate(-W / 2, -H / 2)
    cam = Cam(0, 0, 0, -104, 56, 8.4)
    e = 1.75
    q = np.array([[-e, e, 0], [e, e, 0], [e, -e, 0], [-e, -e, 0]], float)
    low = q - np.array([0, 0, 0.16])
    for a, b in ((3, 2), (0, 3)):                     # the two edges that face the camera
        fill(can, cam.pj([q[a], q[b], low[b], low[a]])[0], C.fwd if i == 0 else C.back, 1.0, 0.45)
    card(can, cam, skia.Image.fromarray(band_maps()[i], colorType=skia.kRGBA_8888_ColorType), q)
    lines = Lines()
    polyline(lines, cam, np.r_[q, q[:1]], C.fwd if i == 0 else C.back, 3.0, 1.0)
    lines.flush(can)
    return surf.makeImageSnapshot()


def s22(can, t):
    floor(can, Cam(0, 0, 0, -88 + 4 * np.sin(t * 0.2), 44, 16))
    h, c = 3.0, (3.75, -1.42)
    t_a, t_b = T.averages + 1.45, T.has_inv + 0.45
    x0, y1, x1, y0 = *px(c[0] - h / 2, c[1] - h / 2), *px(c[0] + h / 2, c[1] + h / 2)
    r = skia.Rect(x0, y0, x1, y1)
    for i, a in ((0, ease(t, t_a, t_a + 0.6) * (1 - ease(t, t_b, t_b + 0.6))), (1, ease(t, t_b, t_b + 0.6) * (1 - ease(t, T.cut_noise - 0.45, T.cut_noise - 0.05)))):
        if a > 0.01:
            can.drawImageRect(heat(i), r, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(Alphaf=float(a)))


VALUES = bars(72)
BOX23 = (0.55, -2.95, 6.65, 2.1)


def box3(can, cam, x0, x1, y0, y1, h, color):
    if h <= 0.004:
        return
    fill(can, cam.pj([[x0, y0, 0], [x1, y0, 0], [x1, y0, h], [x0, y0, h]])[0], color, 1.0, 0.8)
    fill(can, cam.pj([[x1, y0, 0], [x1, y1, 0], [x1, y1, h], [x1, y0, h]])[0], color, 1.0, 0.5)
    fill(can, cam.pj([[x0, y0, h], [x1, y0, h], [x1, y1, h], [x0, y1, h]])[0], color, 1.0, 1.15)


def s23(can, t):
    floor(can, Cam(0, 0, 0, -92, 44, 16))
    r, g2, c = ease(t, T.squeezes - 0.1, T.squeezes + 1.1), ease(t, T.enormous - 0.45, T.enormous + 0.55), ease(t, T.stops + 0.35, T.stops + 2.35) * KEEP

    def chart():
        cam = Cam(4.0, 0.3, 1.9, -100, 20, 19.5)
        lines = Lines()
        grid(lines, cam, I2, origin=(4, 0), xr=(-5, 5), yr=(-1, 3), op=0.5 * min(r * 2, 1), minor=False, color=C.grid_minor, axes=False, far=40)
        lines.flush(can)
        step, tall = 8.0 / VALUES.size, 4.2
        for i, v in enumerate(VALUES):
            x = i * step
            if g2 > 0 and v > c:
                box3(can, cam, x, x + step * 0.72, 0.5, 0.5 + step * 0.72, min(tall, 0.16 * tall / v) * g2, C.back)
        for i, v in enumerate(VALUES):
            x = i * step
            box3(can, cam, x, x + step * 0.72, 0.0, step * 0.72, max(0.012, v * tall * r), C.wrong if v <= c else C.fwd)
        if c > 0:                                     # the cutoff is a pane of glass rising through the bars
            z = c * tall
            q = np.array([[-0.2, -0.5, z], [8.2, -0.5, z], [8.2, 1.2, z], [-0.2, 1.2, z]])
            fill(can, cam.pj(q)[0], C.home, 0.16)
            polyline(lines, cam, np.r_[q, q[:1]], C.home, 3.0, 1.0)
            lines.flush(can)
    if r > 0:
        inset(can, BOX23, chart)


# ---------------------------------------------------------------- chapter 7: shadows and outro
TILT, BINS = float(np.arctan2(SHAFT[1], SHAFT[0])), 48
A0, A1 = float(np.arctan2(-2.0, 1.0)), float(np.arctan2(-2.0, 1.0)) + np.radians(40.0)
R0, R1, HALF = 2.35, 3.4, 1.9
FLIPPED = (1, -1, -1, 1)


@lru_cache(maxsize=None)
def _raster24(teeth):
    return key_raster(300, teeth)


@lru_cache(maxsize=2048)
def _profile(a, teeth):
    r = _raster24(teeth)
    n = r.shape[0]
    xs = (np.arange(n) + 0.5) / n * 3.8 - 1.9
    X, Y = np.meshgrid(xs, xs)
    across = X if abs(a + np.pi / 2) < 1e-4 else -X * np.sin(a) + Y * np.cos(a)
    hist, _ = np.histogram(across, bins=BINS, range=(-1.9, 1.9), weights=r)
    return hist / (n / 3.8) ** 2


def profile(alpha, teeth):
    """How much key each ray crosses when light travels at plane angle `alpha`."""
    return _profile(round(alpha - TILT, 4), teeth)


def keys_that_fit(alphas):
    patterns = [tuple(1 if n >> b & 1 else -1 for b in range(4)) for n in range(16)]
    return [p for p in patterns if all(np.abs(profile(a, p) - profile(a, TEETH)).max() < 1e-6 for a in alphas)]


def wag(b):
    return [(b, 0.0), (b + 0.3, 1.0), (b + 0.65, 1.0), (b + 0.95, 0.0), (b + 1.3, 0.0), (b + 1.6, 1.0), (b + 1.95, 1.0), (b + 2.25, 0.0)]


FLIP = keys(*wag(T.one_sh), *wag(T.falls - 0.4), lead=0)


def wall(can, cam, mid, alpha, values, upto=1.0, mark=None, tall=0.95, length=3.8):
    """A detector standing tangent to the light, each cell shaded by how much key its ray crossed."""
    u = np.array([-np.sin(alpha), np.cos(alpha)])
    top = max(float(profile(A0, TEETH).max()), 1e-9)
    base = lambda s, z: np.array([*(mid + u * s), z])
    fill(can, cam.pj([base(-length / 2, 0), base(length / 2, 0), base(length / 2, tall), base(-length / 2, tall)])[0], C.bg, 0.92)
    for i, v in enumerate(values):
        f = (i + 0.5) / len(values)
        if f > upto or v < 0.01 * top:
            continue
        s0, s1 = -length / 2 + length * i / len(values), -length / 2 + length * (i + 1) / len(values)
        col = C.null if mark is not None and mark[i] else C.shadow
        fill(can, cam.pj([base(s0, 0.04), base(s1, 0.04), base(s1, tall - 0.04), base(s0, tall - 0.04)])[0], col, float(min(v / top, 1.0)) ** 0.7)
    lines = Lines()
    polyline(lines, cam, np.array([base(-length / 2, 0), base(length / 2, 0), base(length / 2, tall), base(-length / 2, tall), base(-length / 2, 0)]), C.frame, 1.8, 1.0)
    lines.flush(can)


def s24(can, t):
    can.save()
    can.translate(-2.7 * PX, -0.55 * PX)
    cam = Cam(0.2, -0.3, 0.3, -82 + 10 * ease(t, T.turn_light, T.turn_light + 2.0), 46, 12.5)
    floor(can, cam)
    op = ease(t, T.brings + 0.3, T.brings + 0.9)
    sheet(can, cam, I2, xr=(-5, 5), yr=(-4.5, 4.5), op=0.45 * op)
    r, c, f = ease(t, T.brings + 1.8, T.brings + 3.3), ease(t, T.turn_light, T.turn_light + 2.0), float(FLIP(t))
    a, R = A0 + c * (A1 - A0), R0 + c * (R1 - R0)
    d, u = np.array([np.cos(a), np.sin(a)]), np.array([-np.sin(a), np.cos(a)])
    now = (1 - f) * profile(a, TEETH) + f * profile(a, FLIPPED)
    if c > 0:                                         # the first detector keeps its place
        wall(can, cam, R0 * np.array([np.cos(A0), np.sin(A0)]), A0, (1 - f) * profile(A0, TEETH) + f * profile(A0, FLIPPED))
    lines = Lines()
    for w in np.linspace(-1.7, 1.7, 13):
        if (w + 1.7) / 3.4 <= r and r > 0:
            polyline(lines, cam, np.array([[*(-3.3 * d + w * u), 0.5], [*((R - 0.14) * d + w * u), 0.5]]), C.null, 1.8, 0.5)
    lines.flush(can)
    teeth = (1.0, -1.0, 1.0 - 2.0 * f, 1.0)
    place = on_sheet(I2, z=0.5, scale=1.0)
    if op > 0:
        key_shadow(can, cam, place, teeth, floor=0.0, alpha=0.55 * op)
        draw_key(can, cam, place, (0, 0, 1), teeth, thick=0.14, sheen=0.1 * t, op=op, width=1.3)
    if r > 0:
        mark = np.abs(profile(A1, TEETH) - profile(A1, FLIPPED)) > 0.01 if c >= 0.999 else None
        wall(can, cam, R * d, a, now, upto=r, mark=mark)
    can.restore()


STAGES = [(T.two, 2), (T.four_s, 4), (T.sixteen_s, 16), (T.outline, 32), (T.enough + 0.5, 64), (T.teeth - 1.1, 128)]
START = float(np.arctan2(-2.0, 1.0))
R25 = 2.75


def solved(t):
    prev, cur, u = None, None, 0.0
    for at, n in STAGES:
        if t >= at:
            prev, cur, u = cur, n, min(1.0, (t - at) / 0.6)
    v = np.zeros((480, 480)) if cur is None else u * recon(cur) + (1 - u) * (recon(prev) if prev else 0.0)
    col = np.array([int(str(C.key).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], float)
    return np.dstack([(v[..., None] * col).astype(np.uint8), np.full((480, 480), 255, np.uint8)])


def s25(can, t):
    can.save()
    can.translate(-1.2 * PX, 0.0)
    push = ease(t, T.teeth - 0.9, T.teeth + 1.1) * (1 - ease(t, T.ct - 0.3, T.ct + 0.9))
    cam = Cam(0, 0, 0.2, -90 + 40 * (t - T.cut_ct) / (T.cut_outro - T.cut_ct), 46 + 12 * push, 13.5 - 4.0 * push)
    floor(can, cam)
    ring_op = 1.0
    shown = [(at, n) for at, n in STAGES[:3] if t >= at - 0.05]
    if shown:
        at, n = shown[-1]
        k = min(n, 16)
        length = min(1.25, np.pi * R25 / k * 0.46 + 0.28)
        walls = []
        for j in range(k):
            for side in (0.0, np.pi):
                phi = START + np.pi * j / k + side
                walls.append((-float(np.linalg.norm(np.array([*(R25 * np.array([np.cos(phi), np.sin(phi)])), 0.3]) - cam.eye)), phi))
        op = ease(t, at - 0.05, at + 0.4)
        for _, phi in sorted(walls):
            mid = R25 * np.array([np.cos(phi), np.sin(phi)])
            u = np.array([-np.sin(phi), np.cos(phi)])
            base = lambda s, z: np.array([*(mid + u * s), z])
            prof = shadow_profile(phi, 18)
            fill(can, cam.pj([base(-length / 2, 0), base(length / 2, 0), base(length / 2, 0.6), base(-length / 2, 0.6)])[0], C.bg, 0.9 * op)
            for i, v in enumerate(prof):
                if v > 0.01:
                    s0, s1 = -length / 2 + length * i / 18, -length / 2 + length * (i + 1) / 18
                    fill(can, cam.pj([base(s0, 0.03), base(s1, 0.03), base(s1, 0.57), base(s0, 0.57)])[0], C.shadow, float(v) ** 0.7 * op)
    half = 1.8
    img = skia.Image.fromarray(solved(t), colorType=skia.kRGBA_8888_ColorType)
    card(can, cam, img, np.array([[-half, half, 0.02], [half, half, 0.02], [half, -half, 0.02], [-half, -half, 0.02]]))
    lines = Lines()
    polyline(lines, cam, np.array([[-half, half, 0.02], [half, half, 0.02], [half, -half, 0.02], [-half, -half, 0.02], [-half, half, 0.02]]), C.frame, 2.0, 1.0)
    gantry = ease(t, T.ct, T.ct + 1.1)
    if gantry > 0:                                    # the scanner closes around it
        for z in (0.0, 0.85):
            for r_ in (3.08, 3.4):
                th = np.linspace(0, 2 * np.pi * gantry, 96)
                polyline(lines, cam, np.c_[r_ * np.cos(th), r_ * np.sin(th), np.full(96, z)], C.frame, 2.4, 1.0)
    show = ease(t, T.ct + 0.6, T.ct + 1.1)
    if show > 0:
        a = START + np.pi + 4 * np.pi * (t - T.ct - 0.6) / (T.cut_outro - T.ct - 0.6)
        p = np.array([3.24 * np.cos(a), 3.24 * np.sin(a), 0.42])
        for w in np.linspace(-0.42, 0.42, 9):
            polyline(lines, cam, np.array([p, [2.95 * np.cos(a + np.pi + w), 2.95 * np.sin(a + np.pi + w), 0.42]]), C.null, 1.8, 0.45 * show)
        lines.flush(can)
        dot(can, cam, p, 11, C.null, show)
    lines.flush(can)
    can.restore()


T_CLEAR = T.look - 1.2
CAM26 = [(T.cut_outro, (0, 0, 0.2, -86, 52, 13)), (T.every + 2.6, (0, 0, 0.8, -100, 50, 20)), (T.nothing_f + 3.6, (0, 0, 0.4, -84, 54, 13)), (T.something + 2.7, (0, 0, 0, -70, 44, 14)), (T_CLEAR + 3.6, (0, 0, 0.1, -76, 46, 9.5))]


def s26(can, t):
    cam = track(t, CAM26)
    floor(can, cam)
    b, r, c = ease(t, T.every + 0.1, T.every + 2.6), ease(t, T.nothing_f + 1.1, T.nothing_f + 3.6), ease(t, T.something + 0.2, T.something + 2.7)
    X = (1 - r) * ((1 - b) * I2 + b * A) + r * I2
    M = (1 - c) * X + c * S
    z = 1.3 * b * (1 - r)
    arrive = ease(t, T.cut_outro + 0.05, T.cut_outro + 0.55) * (1 - ease(t, T.something + 1.6, T.something + 2.7))
    lines = Lines()
    if b > 0 and r < 1:                               # home stays marked underneath
        grid(lines, cam, I2, xr=(-4, 4), yr=(-3, 3), op=0.4, minor=False, far=50)
        lines.flush(can)
    sheet(can, cam, M, z=z, op=arrive)
    t_op = 0.9 * ease(t, T.nothing_f + 0.9, T.nothing_f + 1.4) * (1 - ease(t, T.home_ex + 0.3, T.home_ex + 1.1))
    if t_op > 0:
        for p in LAT[::2]:
            a, q = np.array([*(A @ p), 1.3]), np.array([*(X @ p), z])
            polyline(lines, cam, np.array([a, q]), C.back, 2.2, t_op)
            dot(can, cam, q, 4.5, C.back, t_op)
        lines.flush(can)
    flat = ease(t, T.something + 1.6, T.something + 2.7) * (1 - ease(t, T_CLEAR, T_CLEAR + 0.5))
    if flat > 0:
        U = S[:, 0] / np.linalg.norm(S[:, 0])
        ribbon(can, cam, -7 * U, 7 * U, C.shadow, 0.09, 0.0, 0.03, flat)
    if c < 0.98:
        rider(can, cam, M, z=z, k_op=arrive, b_op=0.0, color=tint(C.key, C.shadow, min(1.0, max(0.0, (c - 0.55) / 0.45))), t=t)
    light = 0.55 * ease(t, T.gone - 0.4, T.gone + 0.3) * (1 - ease(t, T_CLEAR + 2.9, T_CLEAR + 3.7))
    if light > 0:
        th = float(np.arctan2(-2.0, 1.0)) + 2 * np.pi * ease(t, T_CLEAR, T_CLEAR + 3.8)
        d, n = np.array([np.cos(th), np.sin(th)]), np.array([-np.sin(th), np.cos(th)])
        for w in np.linspace(-4, 4, 17):
            polyline(lines, cam, np.array([[*(-9 * d + w * n), 0.6], [*(9 * d + w * n), 0.6]]), C.null, 1.8, light)
        lines.flush(can)


# ---------------------------------------------------------------- the whole film
SCENES = ((T.cut_solve, s17), (T.cut_weak, s18), (T.cut_drone, s19), (T.cut_camera, s20), (T.cut_blur, s21), (T.cut_noise, s22), (T.cut_second, s23), (T.cut_ct, s24), (T.cut_outro, s25),
          (float("inf"), s26))


def frame(t):
    """One finished frame of Chapters 5 to 7 at audio time t, as RGBA uint8."""
    surf = skia.Surface(W * SS, H * SS)
    can = surf.getCanvas()
    can.scale(SS, SS)
    can.clear(skia.ColorBLACK)
    for end, fn in SCENES:
        if t < end:
            fn(can, t)
            break
    return surf.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
