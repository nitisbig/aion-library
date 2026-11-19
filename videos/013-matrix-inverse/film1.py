"""Chapter 1's 3D film (1:21 to 3:00), one pure function of audio time. The plane climbs as it moves, so height is progress: every point's thread is a
straight line in space, the moving sheet is a slice through the web, and the inverse is the same web walked back down."""
from functools import lru_cache

import numpy as np
import skia

from aion import C
from beats import T
from film import on_sheet
from shots import A, A_INV, I2, SIMPLE, TEETH, tex
from stage import H, Lines, SS, W, draw_glyphs, draw_key, ease, fill, glyph_paths, grid, key_shadow, paint_color, polyline, ribbon, ring, slab, track

RISE = 3.6                                            # the height of the landed plane above home
XR, YR = (-4, 4), (-3, 3)
HERO = np.array([1.5, -0.5])
STRETCH, SLIDE = SIMPLE["stretch"][0], SIMPLE["slide"][0]
PX = W / (64 / 9 * 2)                                 # pixels per Manim unit

LAT = np.array([[x, y] for x in np.arange(-3, 3.01, 0.5) for y in np.arange(-2, 2.01, 0.5) if x or y], float)
DELAY = np.random.default_rng(13).permutation(len(LAT)) / len(LAT) * 0.72
PHASE = np.random.default_rng(14).random(len(LAT))


def turn(th):
    return np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])


def lerp(a, b, u):
    return tuple(int(x + (y - x) * u) for x, y in zip(a, b))


def mix(c1, c2, u):
    a, b = [np.array([int(str(c).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], float) for c in (c1, c2)]
    return "#%02x%02x%02x" % tuple(int(v) for v in a + (b - a) * u)


# ---------------------------------------------------------------- the camera: one unbroken shot
CAMERA = [(T.cut_simple, (0, 0, 0, -92, 58, 17)), (T.move + 0.6, (0, 0, 0, -84, 52, 12.5)), (T.rest + 1.1, (0, 0, 0.2, -94, 58, 20)), (T.easy + 0.5, (0, 0, 0, -84, 54, 12.5)),
          (T.turn + 0.6, (0, 0, 0, -90, 68, 13)), (T.stretch, (0, 0, 0, -88, 58, 16)), (T.shrinks + 0.6, (0, 0, 0, -84, 52, 13)), (T.slide + 0.9, (0, 0, 0, -72, 36, 10.5)),
          (T.deck + 0.6, (0, 0, 0, -76, 38, 10.5)), (T.cut_wrong + 0.8, (0, 0, 0, -86, 50, 14)), (T.but_deck, (0, 0, 0, -98, 42, 17)), (T.whole - 0.5, (0, 0, 0, -78, 44, 17)),
          (T.cut_threads, (0, 0, 0, -78, 46, 14)), (T.one_point + 0.3, (0, 0, 0.7, -76, 38, 15)), (T.now_do + 0.9, (0, 0, 1.8, -70, 25, 25)), (T.web + 1.0, (0, 0, 1.8, -94, 23, 27)),
          (T.opposite + 2.6, (0, 0, 1.2, -116, 28, 24)), (T.cut_identity + 0.3, (0, 0, 1.0, -112, 34, 22)), (T.come_back + 1.7, (0, 0, 0.4, -98, 46, 16)),
          (T.its_cols, (0, 0, 0, -90, 56, 10.5)), (T.mult + 2.4, (0, 0, 0, -86, 54, 11)), (T.so_inv + 1.5, (0, 0, 0, -94, 46, 14)), (T.back_first + 0.6, (0, 0, -1.3, -78, 26, 17)),
          (T.gets_home + 0.5, (0, 0, -0.2, -92, 42, 17))]


def shift(t):
    """Keep the plane right of the matrices while they sit in the left column."""
    return PX * 1.8 * (1 - ease(t, T.cut_wrong, T.cut_wrong + 0.8) + ease(t, T.whole - 0.4, T.whole + 0.8))


# ---------------------------------------------------------------- what the sheet is doing
def easy_move(t):
    r = np.pi / 6 * (ease(t, T.turn, T.turn + 1.0) - ease(t, T.turn_back - 0.1, T.turn_back + 1.3))
    st = ease(t, T.stretch, T.stretch + 0.75) - ease(t, T.shrinks - 0.15, T.shrinks + 0.6)
    return (I2 + slide_amount(t) * (SLIDE - I2)) @ (I2 + st * (STRETCH - I2)) @ turn(r)


def slide_amount(t):
    return ease(t, T.slide, T.slide + 1.2) - ease(t, T.deck - 0.5, T.deck + 0.9)


def up(t):
    return ease(t, T.one_point + 0.35, T.one_point + 2.05) * (1 - ease(t, T.opposite - 0.15, T.opposite + 2.45)) + ease(t, T.out_back - 0.05, T.out_back + 1.35) * (1 - ease(t, T.come_back - 0.1, T.come_back + 1.6))


def down(t):
    return ease(t, T.back_first + 0.1, T.back_first + 1.6) * (1 - ease(t, T.gets_home - 1.3, T.gets_home + 0.4))


def state(t):
    """(sheet matrix, arrow matrix, height, opacity)."""
    if t < T.cut_wrong + 1.0:
        g = ease(t, T.rest, T.rest + 1.1) * (1 - ease(t, T.easy - 0.3, T.easy + 0.7))
        a = ease(t, T.two_arrows, T.two_arrows + 1.0) * (1 - ease(t, T.easy - 0.3, T.easy + 0.7))
        E = easy_move(t)
        return E @ ((1 - g) * I2 + g * A), E @ ((1 - a) * I2 + a * A), 0.0, 1 - ease(t, T.cut_wrong + 0.1, T.cut_wrong + 0.8)
    if t < T.whole - 0.3:
        s = ease(t, T.shortcut, T.shortcut + 1.2) * (1 - ease(t, T.flip + 0.2, T.flip + 1.4))
        M = I2 + s * (STRETCH - I2)
        return M, M, 0.0, 0.3 * ease(t, T.shortcut - 0.5, T.shortcut + 0.2) * (1 - ease(t, T.but_deck - 0.6, T.but_deck))
    u, v = up(t), down(t)
    M = ((1 - u) * I2 + u * A) @ ((1 - v) * I2 + v * A_INV)
    return M, M, RISE * (u - v), ease(t, T.whole - 0.1, T.whole + 0.9)


@lru_cache(maxsize=1)
def tags():
    return dict(x=glyph_paths(tex(r"\mathbf{x}", size=54, color=C.vec)), ax=glyph_paths(tex("A", r"\mathbf{x}", size=54, colors={0: C.fwd, 1: C.vec})))


def tag(can, q, glyphs, alpha):
    can.drawRect(skia.Rect(q[0] - 44, q[1] - 34, q[0] + 44, q[1] + 34), skia.Paint(Color=skia.Color(0, 0, 0, int(205 * alpha))))
    draw_glyphs(can, glyphs, float(q[0]), float(q[1]), PX, alpha)


# ---------------------------------------------------------------- pieces
def deck(can, cam, t):
    """The sheet as seven real cards, each pushed sideways by its height."""
    op = ease(t, T.cards - 0.25, T.cards + 0.2) * (1 - ease(t, T.deck + 0.75, T.deck + 1.2))
    if op <= 0:
        return
    amount, lines = slide_amount(t), Lines()
    for y in np.arange(1.75, -1.76, -0.5):
        o = np.array([amount * y, y])
        z = 0.22 + 0.03 * (y + 1.75)
        q = np.array([[-1.6, -0.22], [1.6, -0.22], [1.6, 0.22], [-1.6, 0.22]]) + o
        fill(can, cam.pj(np.c_[q, np.full(4, z)])[0], C.bg, 0.94 * op)
        slab(can, cam, I2, o, z=z, xr=(-1.6, 1.6), yr=(-0.22, 0.22), thick=0.1, op=op, tint=C.key)
        polyline(lines, cam, np.array([[o[0] - 1.42, y, z], [o[0] - 0.7, y, z]]), C.key, 2.4, 0.8 * op)
        lines.flush(can)


def web(can, cam, t):
    """Threads climb from every home point to where it lands."""
    built = ease(t, T.now_do + 0.15, T.now_do + 2.85) if t < T.cut_identity else 1.0
    op = ease(t, T.now_do, T.now_do + 0.3) * (1 - 0.45 * ease(t, T.opposite + 1.8, T.reversed_ + 1.2)) * (1 - ease(t, T.round_trip - 0.3, T.round_trip + 0.8))
    if op <= 0.01:
        return
    back = ease(t, T.opposite - 0.15, T.opposite + 1.15) * (1 - ease(t, T.out_back - 0.05, T.out_back + 0.4)) + ease(t, T.come_back - 0.1, T.come_back + 0.4)
    col, u, lines = mix(C.fwd, C.back, min(back, 1.0)), up(t), Lines()
    home, top = np.c_[LAT, np.zeros(len(LAT))], np.c_[(A @ LAT.T).T, np.full(len(LAT), RISE)]
    dash = ease(t, T.web - 0.5, T.web) * (1 - ease(t, T.reversed_ + 0.8, T.cut_identity - 0.2))
    way = -1.0 if t >= T.opposite - 0.15 else 1.0
    for i in range(len(LAT)):
        prog = float(np.clip((built - DELAY[i]) / 0.28, 0, 1))
        if prog <= 0:
            continue
        polyline(lines, cam, np.array([home[i], home[i] + prog * (top[i] - home[i])]), col, 1.6, 0.62 * op)
        if dash > 0:
            s = (PHASE[i] + way * 0.42 * t) % 1.0
            polyline(lines, cam, np.array([home[i] + s * (top[i] - home[i]), home[i] + min(s + 0.09, 1.0) * (top[i] - home[i])]), mix(col, C.home, 0.35), 3.4, dash)
    lines.flush(can)
    for i in range(len(LAT)):
        prog = float(np.clip((built - DELAY[i]) / 0.28, 0, 1))
        if prog > 0:
            q = cam.pj((home[i] + min(prog, u) * (top[i] - home[i]))[None])[0][0]
            can.drawCircle(float(q[0]), float(q[1]), 4.6, skia.Paint(AntiAlias=True, Color=paint_color(col, op)))


def web_below(can, cam, t):
    """Take the way back first: the same threads, entered from the other end."""
    op = ease(t, T.back_first - 0.1, T.back_first + 0.4) * (1 - ease(t, T.gets_home + 0.6, T.either))
    if op <= 0:
        return
    col, lines = mix(C.back, C.fwd, ease(t, T.gets_home - 1.5, T.gets_home - 1.0)), Lines()
    low = np.c_[(A_INV @ LAT.T).T, np.full(len(LAT), -RISE)]
    for p, q in zip(low, np.c_[LAT, np.zeros(len(LAT))]):
        polyline(lines, cam, np.array([p, q]), col, 1.5, 0.5 * op)
    lines.flush(can)


def hero(can, cam, t):
    show = ease(t, T.one_point - 0.15, T.one_point + 0.25) * (1 - ease(t, T.cut_identity - 0.5, T.cut_identity))
    if show <= 0:
        return
    a, b = np.array([*HERO, 0.0]), np.array([*(A @ HERO), RISE])
    u, d, lines = up(t), ease(t, T.thread, T.thread + 1.2), Lines()
    if d > 0:
        polyline(lines, cam, np.array([a, a + d * (b - a)]), mix(C.fwd, C.back, ease(t, T.opposite - 0.15, T.opposite + 1.15)), 4.0, show)
        lines.flush(can)
    start, now = cam.pj(a[None])[0][0], cam.pj((a + u * (b - a))[None])[0][0]
    can.drawCircle(float(start[0]), float(start[1]), 7, skia.Paint(AntiAlias=True, Color=paint_color(C.home, show)))
    can.drawCircle(float(now[0]), float(now[1]), 12, skia.Paint(AntiAlias=True, Color=paint_color(C.vec, show)))
    label = ease(t, T.thread + 0.1, T.thread + 0.5) * (1 - ease(t, T.now_do + 0.3, T.now_do + 0.8))
    if label > 0:
        tag(can, start + np.array([-52.0, 44.0]), tags()["x"], label)
        tag(can, cam.pj(b[None])[0][0] + np.array([0.0, -62.0]), tags()["ax"], ease(t, T.thread + 1.0, T.thread + 1.4) * label)


def markers(can, cam, t, M, z):
    lines = Lines()
    land = ease(t, T.columns + 0.1, T.columns + 0.6) * (1 - ease(t, T.rest + 0.2, T.rest + 0.6))
    if land > 0:                                      # where the columns say the arrows will land
        ring(lines, cam, A[:, 0], 0.3, 0.03, C.ihat, 3.0, land)
        ring(lines, cam, A[:, 1], 0.3, 0.03, C.jhat, 3.0, land)
    th = np.pi / 6 * (ease(t, T.turn, T.turn + 1.0) - ease(t, T.turn_back - 0.1, T.turn_back + 1.3))
    if th > 0.002:                                    # the angle swept, coral out and teal home
        arc = np.linspace(0, th, 24)
        polyline(lines, cam, np.c_[3.5 * np.cos(arc), 3.5 * np.sin(arc), np.full(24, 0.04)], C.back if t > T.turn_back - 0.1 else C.fwd, 4.0, 1.0)
    home = ease(t, T.its_cols + 0.4, T.its_cols + 1.0) * (1 - ease(t, T.identity - 0.3, T.identity + 0.1))
    if home > 0:                                      # both arrows are already at home
        ring(lines, cam, (1, 0), 0.26, z + 0.05, C.ihat, 3.0, home)
        ring(lines, cam, (0, 1), 0.26, z + 0.05, C.jhat, 3.0, home)
    same = ease(t, T.mult, T.mult + 0.6) * (1 - ease(t, T.so_inv - 0.2, T.so_inv + 0.4))
    if same > 0:                                      # multiply by I and this point stays put
        ring(lines, cam, (-2.5, -1.5), 0.26, z + 0.05, C.vec, 3.0, same)
        q = cam.pj(np.array([[-2.5, -1.5, z + 0.05]]))[0][0]
        can.drawCircle(float(q[0]), float(q[1]), 8, skia.Paint(AntiAlias=True, Color=paint_color(C.vec, same)))
    lines.flush(can)


# ---------------------------------------------------------------- the whole film
def frame(t):
    """One finished frame of Chapter 1 at audio time t, as RGBA uint8."""
    surf = skia.Surface(W * SS, H * SS)
    can = surf.getCanvas()
    can.scale(SS, SS)
    can.clear(skia.ColorBLACK)
    can.translate(float(shift(t)), 0.0)
    cam = track(t, CAMERA)
    lines = Lines()
    grid(lines, cam, I2, z=-5.0, xr=(-26, 26), yr=(-20, 20), op=0.42, minor=False, color=C.grid_minor, axes=False, far=64)
    lines.flush(can)

    M, Ma, z, op = state(t)
    web_below(can, cam, t)
    if abs(z) > 0.01 or (T.now_do < t < T.cut_identity):       # home stays visible while the sheet is away
        grid(lines, cam, I2, xr=XR, yr=YR, op=0.42, minor=False, axes=True)
        lines.flush(can)
    reveal = 0.2 + 9 * ease(t, T.move + 0.5, T.move + 1.7)
    faint = 1 - 0.55 * min(abs(z) / RISE, 1.0)
    if op > 0.01 and t > T.move + 0.4:
        slab(can, cam, M, z=z, xr=XR, yr=YR, op=op * faint)
        grid(lines, cam, M, z=z + 0.01, xr=XR, yr=YR, op=op * faint, reveal=reveal, far=70)
        lines.flush(can)
    web(can, cam, t)
    hero(can, cam, t)
    markers(can, cam, t, M, z)

    b_op = ease(t, T.move + 0.9, T.move + 1.4) * (1 - ease(t, T.cut_wrong + 0.1, T.cut_wrong + 0.7) + ease(t, T.cut_identity, T.cut_identity + 0.4)) * (1 - ease(t, T.either, T.either + 0.6))
    k_op = ease(t, T.cut_identity + 0.05, T.cut_identity + 0.45) * (1 - ease(t, T.either, T.either + 0.6))
    if k_op > 0:
        key_shadow(can, cam, on_sheet(M, z=z + 0.07), TEETH, floor=z, alpha=0.6 * k_op)
        draw_key(can, cam, on_sheet(M, z=z + 0.07), (0, 0, 1), TEETH, thick=0.1, sheen=0.1 * t, op=k_op)
    if b_op > 0:
        ribbon(can, cam, (0, 0), Ma[:, 0], C.ihat, 0.075, 0.34, z + 0.05, b_op)
        ribbon(can, cam, (0, 0), Ma[:, 1], C.jhat, 0.075, 0.34, z + 0.05, b_op)
    deck(can, cam, t)
    return surf.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
