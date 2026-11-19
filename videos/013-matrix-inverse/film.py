"""The intro's 3D film (0:00 to 1:21), one pure function of audio time. The maths is the same cast as everywhere else: A, its four moves, S, and the
key whose teeth point along the direction S forgets. Hung upright under parallel light, those teeth can flip without moving its shadow at all."""
from functools import lru_cache

import numpy as np
import skia

from aion import C
from beats import T
from deblur import smear_rgba
from shots import A, DRONE, HOOK, I2, KEY_SCALE, MAPPED, NORMAL, S, SHAFT, TEETH, lab, shadow_profile, tex
from stage import (BOW_C, Cam, H, HOLE_R, Lines, SS, W, card, circle_pts, outline, outline_path, draw_glyphs, draw_key, ease, fill, glyph_paths, grid, key_shadow, key_wire, paint_color, poly_path, polyline, ribbon,
                   ring, rgb, slab, track)
from verify import key_raster
from world import town_rgba

U = S[:, 0] / np.linalg.norm(S[:, 0])                 # the line everything collapses onto
PERP = np.array([-U[1], U[0], 0.0])
HANG = KEY_SCALE * np.sqrt(5.0) * np.linalg.norm(S[:, 1])   # the upright key's size, so its shadow is exactly the streak S leaves
AZ_SIDE = float(np.degrees(np.arctan2(U[1], U[0]))) - 90.0
Z_HANG = 3.3

XR, YR = (-4, 4), (-3, 3)
LAT = np.array([[x, y] for x in range(-3, 4) for y in range(-2, 3) if (x or y)], float)


# ---------------------------------------------------------------- the moves
def bend(t):
    """The sheet's matrix through the cold open and the crush."""
    X = I2
    starts = ((T.lean1, 1.2), (T.pull, 1.0), (T.lean2, 1.0), (T.lean3, 1.2))
    for H_, (at, dur) in zip(HOOK, starts):
        a = ease(t, at, at + dur)
        X = ((1 - a) * I2 + a * H_) @ X
    r = ease(t, T.smooth, T.smooth + 2.6)
    X = (1 - r) * X + r * I2
    c = ease(t, T.flat, T.flat + 1.8)
    return (1 - c) * X + c * S


def lift(t):
    return 1.2 * ease(t, T.lift - 0.2, T.lift + 1.0) * (1 - ease(t, T.smooth, T.smooth + 2.6))


# ---------------------------------------------------------------- the teeth: one flip, then all sixteen patterns
def _gray(n):
    return n ^ (n >> 1)


def _events():
    ev = [(T.flipped - 0.1, 0.55, 2, -1.0)]
    for i, at in enumerate(np.linspace(T.four_teeth + 0.3, T.four_teeth + 2.1, 4)):      # each tooth shows it can go both ways
        ev += [(float(at), 0.22, i, -TEETH[i] if i != 2 else 1.0), (float(at) + 0.3, 0.22, i, TEETH[i] if i != 2 else -1.0)]
    now = list(TEETH)
    now[2] = -1
    t0, step = T.sixteen - 0.1, (T.same_mark - T.sixteen - 0.1) / 16
    for n in range(1, 17):
        want = [1 if _gray(n % 16) >> b & 1 else -1 for b in range(4)]
        for i in range(4):
            if want[i] != now[i]:
                ev.append((t0 + step * (n - 1), step * 0.7, i, float(want[i])))
                now[i] = want[i]
    for i in range(4):
        if now[i] != TEETH[i]:
            ev.append((T.same_mark, 0.4, i, float(TEETH[i])))
    return sorted(ev)


EVENTS = _events()


def teeth_at(t):
    s = [float(v) for v in TEETH]
    for at, dur, i, target in EVENTS:
        if t <= at:
            break
        u = ease(t, at, at + dur)
        s[i] = s[i] + u * (target - s[i])
    return tuple(s)


def pattern_index(t):
    """Which of the sixteen patterns is showing, or None outside the run."""
    t0, step = T.sixteen - 0.1, (T.same_mark - T.sixteen - 0.1) / 16
    return None if not t0 <= t < T.same_mark else _gray((int((t - t0) / step) + 1) % 16)


# ---------------------------------------------------------------- placements
def on_sheet(M, z=0.0, scale=KEY_SCALE, origin=(0, 0)):
    M, origin = np.asarray(M, float), np.asarray(origin, float)

    def place(k):
        k = np.atleast_2d(k) - np.array([0.2, 0.0])
        return np.c_[(M @ (scale * (k[:, [0]] * SHAFT + k[:, [1]] * NORMAL)).T).T + origin, np.full(len(k), z)]
    return place


def hanging(z):
    def place(k):
        k = np.atleast_2d(k) - np.array([0.2, 0.0])
        return np.c_[HANG * k[:, 0] * U[0], HANG * k[:, 0] * U[1], z + HANG * k[:, 1]]
    return place


@lru_cache(maxsize=1)
def column_profile():
    r = key_raster(380).sum(axis=0)
    return r / r.max()


def silhouette_top(rel, teeth):
    """The height of the key's top edge above a point of the streak, or None where light passes the key."""
    x = rel + 0.2
    if abs(x + 1.05) < 0.45:
        return float(np.sqrt(0.45 ** 2 - (x + 1.05) ** 2))
    if -0.65 < x < 1.5:
        top = 0.08
        for i, s in enumerate(teeth):
            if 0.42 + 0.27 * i <= x <= 0.59 + 0.27 * i and s > 0:
                top = max(top, 0.42 * s)
        return top
    return None


# ---------------------------------------------------------------- act one: out, back, and the crush
CAMERA = [(0.0, (0, 0, 0.3, -62, 30, 4.3)), (T.lay + 0.5, (0, 0, 0, -76, 46, 9.5)), (T.lift, (0, 0, 0.3, -82, 54, 12.5)), (T.lean1 + 0.8, (0, 0, 0.6, -90, 58, 19)),
          (T.lean3 + 1.4, (0, 0, 0.8, -104, 62, 31)), (T.question, (0, 0, 0.8, -108, 62, 31)), (T.smooth, (0, 0, 0.8, -110, 62, 31)),
          (T.smooth + 2.6, (0, 0, 0.2, -82, 54, 12.5)), (T.flat, (0, 0, 0.2, -76, 54, 12.5)), (T.flat + 1.8, (0, 0, 0, -68, 46, 13)), (T.no_hold, (0, 0, 0, -64, 44, 13)),
          (T.this_key - 0.4, (1.7 * U[0], 1.7 * U[1], 2.6, AZ_SIDE, 13, 20)), (T.shadow, (1.7 * U[0], 1.7 * U[1], 2.6, AZ_SIDE + 5, 15, 20)),
          (T.why, (1.7 * U[0], 1.7 * U[1], 2.0, AZ_SIDE - 6, 24, 23))]


def act_one(can, t):
    cam = track(t, CAMERA)
    lines = Lines()
    M, z, c = bend(t), lift(t), ease(t, T.flat, T.flat + 1.8)

    # the fixed floor underneath, so every move can be read against home
    floor_op = 0.34 * ease(t, T.lift - 0.2, T.lift + 0.8) + 0.3 * c
    grid(lines, cam, I2, xr=(-20, 20), yr=(-16, 16), op=floor_op, minor=False, color=C.grid_minor, axes=False, far=70)
    lines.flush(can)

    # home: the outline waiting on the floor
    home = ease(t, T.can - 0.2, T.can + 0.4) * (1 - ease(t, T.exact + 0.9, T.exact + 1.5))
    if home > 0:
        key_wire(can, cam, on_sheet(I2), TEETH, C.home, 2.2, home)

    settle = ease(t, T.take - 0.1, T.lay + 0.2)
    show = ease(t, T.lay - 0.1, T.lay + 1.1)
    sheet_op = (1 - ease(t, T.flat + 1.0, T.flat + 1.8))
    if sheet_op > 0.01:
        if show > 0:
            slab(can, cam, M, z=z, xr=XR, yr=YR, op=show * sheet_op)
        grid(lines, cam, M, z=z + 0.01, xr=XR, yr=YR, op=sheet_op, reveal=0.2 + 9 * show, far=70)
        lines.flush(can)

    # threads home: each point walks a straight line back
    r = ease(t, T.smooth, T.smooth + 2.6)
    t_op = ease(t, T.smooth - 0.1, T.smooth + 0.4) * (1 - ease(t, T.exact + 0.6, T.exact + 1.4))
    if t_op > 0:
        for p in LAT:
            tail = max(r - 0.34, 0.0)                         # a comet: a short bright tail on each point's straight way home
            a = np.array([*(((1 - tail) * A + tail * I2) @ p), 1.2 * (1 - tail)])
            b = np.array([*(((1 - r) * A + r * I2) @ p), 1.2 * (1 - r)])
            polyline(lines, cam, np.array([a, b]), C.back, 2.6, 0.9 * t_op)
            q, _ = cam.pj(b[None])
            can.drawCircle(float(q[0, 0]), float(q[0, 1]), 4.5, skia.Paint(AntiAlias=True, Color=paint_color(C.back, t_op)))
        lines.flush(can)

    # the ripple where everything lands
    for k in range(2):
        u = float(np.clip((t - T.exact - 0.15 * k) / 1.5, 0, 1))
        if 0 < u < 1:
            ring(lines, cam, (0, 0), 0.6 + 7.5 * u, 0.02, C.back, 3.0, 0.8 * (1 - u))
    lines.flush(can)

    # the two basic arrows ride the sheet
    b_op = ease(t, T.lift, T.lift + 0.6) * (1 - c)
    if b_op > 0:
        ribbon(can, cam, (0, 0), M[:, 0], C.ihat, 0.075, 0.34, z + 0.05, b_op)
        ribbon(can, cam, (0, 0), M[:, 1], C.jhat, 0.075, 0.34, z + 0.05, b_op)

    # the key: dropped in, carried, crushed
    if c < 0.985:
        drop = 1.3 * (1 - settle) ** 2
        place = on_sheet(M, z=z + 0.07 + drop)
        k_op = ease(t, T.take - 0.15, T.take + 0.35)
        if drop > 0.01 or z > 0.01:
            key_shadow(can, cam, on_sheet(M, z=z + 0.07 + drop), TEETH, floor=z, alpha=0.6 * k_op)
        draw_key(can, cam, place, (0, 0, 1), TEETH, thick=0.1, sheen=0.1 * t, op=k_op)

    # the streak: the key's whole mass pressed onto one line
    if c > 0.6:
        s_op = ease(t, T.flat + 1.0, T.flat + 1.8)
        polyline(lines, cam, np.array([[-30 * U[0], -30 * U[1], 0.0], [30 * U[0], 30 * U[1], 0.0]]), C.shadow, 2.2, 0.55 * s_op)
        lines.flush(can)
        prof = column_profile()
        n = prof.size
        for j in range(0, n, 3):
            v = float(prof[j:j + 3].mean())
            if v > 0.01:
                a, b = (j / n - 0.5) * 3.8 * HANG, ((j + 3) / n - 0.5) * 3.8 * HANG
                q = np.array([[a * U[0], a * U[1], 0.0], [b * U[0], b * U[1], 0.0]])
                w = 0.1 * PERP
                fill(can, cam.pj([q[0] + w, q[1] + w, q[1] - w, q[0] - w])[0], C.shadow, s_op * v ** 0.55, 1.2)

    # the upright key, under falling light
    hang = ease(t, T.this_key - 1.0, T.this_key + 0.35)
    if hang > 0:
        leave = ease(t, T.shadow + 1.9, T.shadow + 3.0)
        teeth = teeth_at(t)
        z_k = Z_HANG + 12.0 * (1 - hang)
        light = ease(t, T.this_key - 0.3, T.this_key + 0.8)
        for i, rel in enumerate(np.linspace(-1.95, 1.95, 61)):
            x = rel * HANG
            top = silhouette_top(rel, teeth)
            stop = 0.0 if top is None or leave > 0.6 else z_k + HANG * top
            base = np.array([x * U[0], x * U[1]])
            polyline(lines, cam, np.array([[*base, 15.0], [*base, stop]]), C.null, 1.5, 0.34 * light)
            for k in range(2):
                y = 15.0 - ((t * 3.4 + i * 0.73 + k * 7.5) % 15.0)
                if y > stop + 0.5:
                    polyline(lines, cam, np.array([[*base, y + 0.5], [*base, y]]), C.null, 2.6, 0.95 * light)
        lines.flush(can)
        place = hanging(z_k)
        draw_key(can, cam, place, PERP, teeth, thick=0.3, sheen=0.05 * t, op=1 - leave, width=1.5)
        if leave > 0:
            key_wire(can, cam, place, teeth, C.home, 2.0, 0.55 * leave)
        sixteen(can, cam, t)


def mini(can, cx, cy, teeth, scale, color, solid):
    """A small flat key in screen space."""
    shift = np.array([0.2, 0.0])
    q = np.c_[cx + scale * (outline(teeth) - shift)[:, 0], cy - scale * outline(teeth)[:, 1]]
    h = np.c_[cx + scale * (circle_pts(BOW_C, HOLE_R) - shift)[:, 0], cy - scale * circle_pts(BOW_C, HOLE_R)[:, 1]]
    style = skia.Paint.kFill_Style if solid else skia.Paint.kStroke_Style
    can.drawPath(outline_path(q, h), skia.Paint(AntiAlias=True, Style=style, StrokeWidth=1.8, Color=color))


def cell_xy(p):
    return 1312.0 + 158.0 * (p % 4), 300.0 + 112.0 * (p // 4)


def sixteen(can, cam, t):
    """All sixteen tooth patterns, each lit the moment the big key shows it, then each threaded down to the one mark."""
    t0, step = T.sixteen - 0.1, (T.same_mark - T.sixteen - 0.1) / 16
    show = ease(t, t0 - 0.3, t0 + 0.1) * (1 - ease(t, T.shadow + 1.4, T.shadow + 2.2))
    if show <= 0:
        return
    now = pattern_index(t)
    seen = {_gray((k + 1) % 16) for k in range(16) if t >= t0 + step * k}
    tie = ease(t, T.same_mark - 0.1, T.same_mark + 1.1)
    target = cam.pj(np.array([[0.0, 0.0, 0.0]]))[0][0]
    for p in range(16 if tie > 0 else 0):                 # threads first, so the cells sit cleanly on top of them
        cx, cy = cell_xy(p)
        mid = np.array([cx, cy]) + tie * (target - np.array([cx, cy]))
        can.drawLine(cx, cy, float(mid[0]), float(mid[1]), skia.Paint(AntiAlias=True, StrokeWidth=1.6, Color=paint_color(C.shadow, 0.6 * show)))
    for p in range(16):
        cx, cy = cell_xy(p)
        pattern = tuple(1 if p >> b & 1 else -1 for b in range(4))
        can.drawRect(skia.Rect(cx - 72, cy - 50, cx + 72, cy + 50), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * show))))
        lit = p in seen or tie > 0
        edge = C.key if p == now else C.frame
        can.drawRect(skia.Rect(cx - 72, cy - 50, cx + 72, cy + 50), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6 if p == now else 1.4, Color=paint_color(edge, show * (1.0 if p == now else 0.6))))
        mini(can, cx, cy, pattern, 37.0, paint_color(C.key, show * (1.0 if lit else 0.24)), p == now or tie > 0)


# ---------------------------------------------------------------- act two: the twins
def act_two(can, t):
    """A bends and comes straight back. Its twin bends once and stays flat."""
    cam = Cam(0, 0, 0.1, -90 + 4 * np.sin((t - T.why) * 0.25), 54, 14.5)
    lines = Lines()
    go = ease(t, T.why + 0.1, T.why + 1.1) * (1 - ease(t, T.why + 1.3, T.why + 2.3))
    crush = ease(t, T.why + 2.4, T.why + 3.5)
    u, xr, yr = 0.6, (-2.5, 2.5), (-2, 2)
    for ox, M in ((-4.2, (1 - go) * I2 + go * A), (4.2, (1 - crush) * I2 + crush * S)):
        flat = crush if ox > 0 else 0.0
        Mu, o = u * np.asarray(M), np.array([ox, 0.0])
        slab(can, cam, Mu, o, z=0.0, xr=xr, yr=yr, op=1 - flat)
        grid(lines, cam, Mu, o, z=0.01, xr=xr, yr=yr, op=1 - flat)
        lines.flush(can)
        draw_key(can, cam, on_sheet(np.asarray(M), z=0.08, scale=KEY_SCALE * u, origin=o), (0, 0, 1), TEETH, thick=0.08, sheen=0.1 * t, op=1 - 0.9 * flat, width=0.7)
    d = 3.6 * u * U[:2] * np.linalg.norm(S[:, 0])
    polyline(lines, cam, np.array([[4.2 - d[0], -d[1], 0.02], [4.2 + d[0], d[1], 0.02]]), C.shadow, 3.4, crush)
    lines.flush(can)


# ---------------------------------------------------------------- act three: four worlds on floating cards
CW, CH = 960, 540
CARD_W, CARD_H = 6.6, 3.71
SPOTS = ((T.game, -11.4), (T.drone_q, -3.8), (T.eqn_q, 3.8), (T.blur_q, 11.4))


@lru_cache(maxsize=1)
def type_assets():
    return dict(game=glyph_paths(lab("game", size=46)), drone=glyph_paths(lab("drone", size=46)), solve=glyph_paths(lab("equations", size=46)), pic=glyph_paths(lab("picture", size=46)),
                sys=glyph_paths(tex("3", "x", "+", "y", "=", "7", size=118, colors={1: C.ihat, 3: C.jhat, 5: C.vec})),
                sys2=glyph_paths(tex("2", "x", "+", "2", "y", "=", "6", size=118, colors={1: C.ihat, 4: C.jhat, 6: C.vec})),
                sol=glyph_paths(tex("x", "=", "2", r",\quad", "y", "=", "1", size=104, colors={0: C.ihat, 2: C.ihat, 4: C.jhat, 6: C.jhat})),
                seen=glyph_paths(tex(r"(2,\,1)", size=84, color=C.cam)), map=glyph_paths(tex(r"(3,\,4)", size=84, color=C.vec)))


def _surface():
    surf = skia.Surface(CW * SS, CH * SS)
    can = surf.getCanvas()
    can.scale(SS, SS)
    can.clear(skia.Color(6, 8, 12, 255))
    return surf, can


def _finish(surf, tag):
    can = surf.getCanvas()
    can.drawRect(skia.Rect(0, CH - 66, 290, CH), skia.Paint(Color=skia.Color(0, 0, 0, 225)))
    draw_glyphs(can, type_assets()[tag], 145, CH - 33, 88)
    can.drawRect(skia.Rect(1.5, 1.5, CW - 1.5, CH - 1.5), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=paint_color(C.frame)))
    return surf.makeImageSnapshot()


def card_game(t):
    frame = town_rgba(max(0.0, t - T.game + 1.0), W=CW * SS, H=CH * SS)
    surf, can = _surface()
    can.drawImageRect(skia.Image.fromarray(frame, colorType=skia.kRGBA_8888_ColorType), skia.Rect(0, 0, CW, CH), skia.SamplingOptions(skia.FilterMode.kLinear))
    return _finish(surf, "game")


def card_drone(t):
    surf, can = _surface()
    u, o = 46.0, np.array([300.0, 430.0])
    g = ease(t, T.drone_q - 0.2, T.drone_q + 1.1)
    px = lambda v: o + u * np.array([v[0], -v[1]])
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.5, Color=paint_color(C.grid, 0.5))
    for v in range(-8, 16):
        can.drawLine(*px((v, -10)), *px((v, 14)), paint)
        can.drawLine(*px((-8, v)), *px((16, v)), paint)
    M = (1 - g) * I2 + g * DRONE
    sky = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2, Color=paint_color(C.cam, 0.9))
    for v in range(-7, 8):
        can.drawLine(*px(M @ np.array([v, -8.0])), *px(M @ np.array([v, 8.0])), sky)
        can.drawLine(*px(M @ np.array([-8.0, v])), *px(M @ np.array([8.0, v])), sky)
    pin = px(MAPPED)
    can.drawCircle(float(pin[0]), float(pin[1]), 13, skia.Paint(AntiAlias=True, Color=paint_color(C.vec)))
    show = ease(t, T.drone_q + 0.8, T.drone_q + 1.3)
    can.drawRect(skia.Rect(630, 60, 930, 250), skia.Paint(Color=skia.Color(0, 0, 0, int(225 * show))))
    draw_glyphs(can, type_assets()["seen"], 780, 110, 88, show)
    draw_glyphs(can, type_assets()["map"], 780, 200, 88, show)
    return _finish(surf, "drone")


def card_solve(t):
    surf, can = _surface()
    a = type_assets()
    w1, w2, w3 = ease(t, T.eqn_q - 0.1, T.eqn_q + 0.5), ease(t, T.eqn_q + 0.3, T.eqn_q + 0.9), ease(t, T.eqn_q + 1.0, T.eqn_q + 1.6)
    draw_glyphs(can, a["sys"], CW / 2, 130, 88, w1)
    draw_glyphs(can, a["sys2"], CW / 2, 245, 88, w2)
    can.drawRect(skia.Rect(250, 318, 710, 321), skia.Paint(Color=paint_color(C.frame, w3)))
    draw_glyphs(can, a["sol"], CW / 2, 395, 88, w3)
    return _finish(surf, "solve")


def card_blur(t):
    surf, can = _surface()
    L = 49.0 + (1.0 - 49.0) * ease(t, T.sharp - 0.1, T.sharp + 0.7)
    img = skia.Image.fromarray(smear_rgba(L), colorType=skia.kRGBA_8888_ColorType)
    can.drawImageRect(img, skia.Rect(0, 0, 480, 480), skia.Rect((CW - CH) / 2, 0, (CW + CH) / 2, CH), skia.SamplingOptions(skia.FilterMode.kLinear))
    return _finish(surf, "pic")


MAKERS = (card_game, card_drone, card_solve, card_blur)


def act_three(can, t):
    x = np.interp(t, [SPOTS[0][0] - 0.6, SPOTS[0][0] + 0.4, SPOTS[1][0] - 0.1, SPOTS[1][0] + 0.7, SPOTS[2][0] - 0.1, SPOTS[2][0] + 0.7, SPOTS[3][0] - 0.1, SPOTS[3][0] + 0.7],
                  [-15.5, SPOTS[0][1], SPOTS[0][1] + 0.5, SPOTS[1][1], SPOTS[1][1] + 0.5, SPOTS[2][1], SPOTS[2][1] + 0.5, SPOTS[3][1]])
    x = x + 0.06 * np.sin(t * 0.7)
    cam = Cam(float(x), 0, 0.12, -90 + 2.2 * np.sin(t * 0.45), 4.0, 8.2)
    lines = Lines()
    grid(lines, cam, I2, origin=(float(np.round(x)), 0), z=-2.3, xr=(-14, 14), yr=(-5, 12), op=0.55, minor=False, axes=False, far=26)
    lines.flush(can)
    for i, ((at, cx), make) in enumerate(zip(SPOTS, MAKERS)):
        if abs(cx - x) > 11.5:
            continue
        yaw = np.radians(np.clip((cx - x) * 5.0, -32, 32))
        dx, dy = 0.5 * CARD_W * np.cos(yaw), 0.5 * CARD_W * np.sin(yaw)
        hh = 0.5 * CARD_H
        face = np.array([[cx - dx, -dy, hh], [cx + dx, dy, hh], [cx + dx, dy, -hh], [cx - dx, -dy, -hh]])
        image = make(t)
        mirror = face * np.array([1, 1, -1]) + np.array([0, 0, -4.6])
        card(can, cam, image, mirror, 0.16)
        card(can, cam, image, face, ease(t, at - 1.4, at - 0.3) if i else 1.0)


# ---------------------------------------------------------------- act four: a ring of shadows, and the key to be rebuilt
RING_N = 12
RING_R = 5.3
RING_KEY = 1.3
TILT = float(np.arctan2(SHAFT[1], SHAFT[0]))


def act_four(can, t):
    t0 = T.impossible - 0.05
    span = T.cut_simple - t0 - 0.5
    cam = Cam(0, 0, 1.3, -90 + 34 * (t - t0) / span, 36, 16)
    lines = Lines()
    grid(lines, cam, I2, xr=(-12, 12), yr=(-12, 12), op=0.5, minor=False, color=C.grid_minor, axes=False, far=34)
    lines.flush(can)

    th0 = float(np.arctan2(-2.0, 1.0))
    beam = th0 + 2 * np.pi * (t - t0) / span
    b_op = ease(t, t0, t0 + 0.4) * (1 - ease(t, t0 + span - 0.4, t0 + span))
    d, n = np.array([np.cos(beam), np.sin(beam)]), np.array([-np.sin(beam), np.cos(beam)])
    if b_op > 0:
        for w in np.linspace(-1.5, 1.5, 15):
            a = np.array([*(-RING_R * 0.9 * d + w * n), 0.05])
            b = np.array([*(RING_R * 0.9 * d + w * n), 0.05])
            polyline(lines, cam, np.array([a, b]), C.null, 1.8, 0.6 * b_op)
        lines.flush(can)

    # detector panels stand around the key, each shaded by the key's true shadow from that side
    panels = []
    for k in range(RING_N):
        phi = th0 + 2 * np.pi * k / RING_N
        rise = ease(t, t0 + span * k / RING_N, t0 + span * k / RING_N + 0.4)
        if rise > 0:
            c = RING_R * np.array([np.cos(phi), np.sin(phi)])
            panels.append((float(np.linalg.norm(np.array([*c, 0.0]) - cam.eye)), phi, c, rise))
    for _, phi, c, rise in sorted(panels, key=lambda p: -p[0]):
        v = np.array([-np.sin(phi), np.cos(phi)])
        prof = shadow_profile(phi, 38)[3:35]               # the true shadow, cropped to the part the key can reach
        L, tall = 3.2 * RING_KEY * KEY_SCALE, 1.05 * rise
        base = lambda s, z: np.array([*(c + v * s), z])
        fill(can, cam.pj([base(-L / 2, 0), base(L / 2, 0), base(L / 2, tall), base(-L / 2, tall)])[0], C.bg, 0.9)
        for i, val in enumerate(prof):
            if val > 0.01:
                s0, s1 = -L / 2 + L * i / 32, -L / 2 + L * (i + 1) / 32
                fill(can, cam.pj([base(s0, 0.05), base(s1, 0.05), base(s1, tall - 0.05), base(s0, tall - 0.05)])[0], C.shadow, float(val) ** 0.7)
        polyline(lines, cam, np.array([base(-L / 2, 0), base(L / 2, 0), base(L / 2, tall), base(-L / 2, tall), base(-L / 2, 0)]), C.frame, 1.8, 1.0)
        lines.flush(can)

    place = on_sheet(I2 * RING_KEY, z=1.0)
    wire = ease(t, T.impossible + 0.1, T.impossible + 0.7)
    solid = ease(t, T.rebuild, T.rebuild + 1.2)
    key_shadow(can, cam, place, TEETH, floor=0.0, alpha=0.5 * solid)
    if wire > 0:
        key_wire(can, cam, place, TEETH, C.home, 2.2, wire * (1 - solid))
    draw_key(can, cam, place, (0, 0, 1), TEETH, thick=0.16, sheen=0.14 * t, op=solid, width=1.3)


# ---------------------------------------------------------------- the whole film
ACTS = ((T.why - 0.1, act_one), (T.game - 0.65, act_two), (T.impossible - 0.45, act_three), (float("inf"), act_four))
CUTS = (T.why - 0.1, T.game - 0.65, T.impossible - 0.45)


def frame(t):
    """One finished frame of the intro at audio time t, as RGBA uint8."""
    surf = skia.Surface(W * SS, H * SS)
    can = surf.getCanvas()
    can.scale(SS, SS)
    can.clear(skia.ColorBLACK)
    for end, act in ACTS:
        if t < end:
            act(can, t)
            break
    dip = max([0.0] + [1 - min(abs(t - c) / 0.3, 1.0) for c in CUTS])
    if dip > 0:
        can.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * dip))))
    return surf.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
