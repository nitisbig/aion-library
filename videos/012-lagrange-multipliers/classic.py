"""The channel's Classic look for Chapter 1 onward (as in 009 and 011): black, a full-frame blue grid, one picture that fills the frame, and small framed equation boxes."""
from functools import lru_cache

import contourpy

from aion import *
from cards import icon  # noqa: F401
from draw3d import Cam, rgb  # noqa: F401
from shots import (BEST, BEST_H, BEST_S, BU, CAST, E, LEVELS, LOW_S, POSE_3D, SHORE, SUMMIT, TRAIL_A, TRAIL_B, area_of, arrow, backdrop, backed, curtain, draw_mountain,  # noqa: F401
                   hill, hill_grad, lab, lerp_cam, live, p3, poly, rect_rope, resample, ring_at, sc, seen, tex, trail, trail_grad, trail_tangent, view, walker)

MAPC = np.array([0.0, -0.05])
U = 1.25
POSE_MAP = (-90.0, 89.9, U, float(MAPC[0]), float(MAPC[1]), 400.0)
CHIPS = ["f,g", "f{=}c", r"\nabla", r"\mathcal{L}", "10", r"\mathbb{R}^3", r"\lambda", "!"]
SPOTS = {"ul": ([-6.85, 3.72, 0], UL), "ur": ([6.85, 3.32, 0], UR), "dl": ([-6.85, -3.72, 0], DL), "dr": ([6.85, -3.72, 0], DR), "l": ([-6.85, 0, 0], LEFT), "r": ([6.85, 0, 0], RIGHT), "d": ([0, -3.72, 0], DOWN)}


def mp(x, y=None):
    """Map coordinates to frame coordinates."""
    q = np.asarray(x, float) if y is None else np.array([x, y], float)
    return p3(MAPC + U * q)


def plane(center=(0.0, 0.0), unit=1.0, op=1.0):
    """The bright integer grid over a dim quarter grid, with white axes, across the whole frame."""
    cx, cy = center
    minor, major = VGroup(), VGroup()
    for k in range(int(-8 / unit) * 4, int(8 / unit) * 4 + 1):
        x, y = cx + k * unit / 4, cy + k * unit / 4
        grp, col, w = (major, C.grid, 1.5) if k % 4 == 0 else (minor, C.grid_minor, 1.0)
        if abs(x) < 7.3:
            grp.add(Line([x, -4.2, 0], [x, 4.2, 0], color=col, stroke_width=w, stroke_opacity=op))
        if abs(y) < 4.2:
            grp.add(Line([-7.3, y, 0], [7.3, y, 0], color=col, stroke_width=w, stroke_opacity=op))
    axes = VGroup(Line([-7.3, cy, 0], [7.3, cy, 0], color=C.axis, stroke_width=2.4, stroke_opacity=op), Line([cx, -4.2, 0], [cx, 4.2, 0], color=C.axis, stroke_width=2.4, stroke_opacity=op))
    return VGroup(minor, major, axes)


@lru_cache(maxsize=None)
def contour_paths(level):
    xs = np.linspace((-7.3 - MAPC[0]) / U, (7.3 - MAPC[0]) / U, 340)
    ys = np.linspace((-4.2 - MAPC[1]) / U, (4.2 - MAPC[1]) / U, 200)
    return tuple(p for p in contourpy.contour_generator(xs, ys, hill(*np.meshgrid(xs, ys))).lines(level) if len(p) > 8)


def loops_at(level):
    xs = np.linspace((-7.3 - MAPC[0]) / U, (7.3 - MAPC[0]) / U, 170)
    ys = np.linspace((-4.2 - MAPC[1]) / U, (4.2 - MAPC[1]) / U, 100)
    return [p for p in contourpy.contour_generator(xs, ys, hill(*np.meshgrid(xs, ys))).lines(float(level)) if len(p) > 6]


def contour_mobs(opacity=0.95):
    out = VGroup()
    for i, lv in enumerate(LEVELS):
        for p in contour_paths(float(lv)):
            out.add(poly([mp(q) for q in p[::2]], C.obj, 2.8 if i % 2 == 0 else 1.6, opacity))
    return out


def trail_mob(width=6.0, s0=0.0, s1=2 * np.pi):
    return poly([mp(*trail(u)) for u in np.linspace(s0, s1, 240)], C.con, width)


def grad_field(step=0.62, scale=0.34, width=2.2):
    out = VGroup()
    for x in np.arange(-5.4, 5.5, step):
        for y in np.arange(-3.0, 3.1, step):
            g = hill_grad(x, y)
            n = float(np.linalg.norm(g))
            if n > 0.03:
                L = min(0.5, scale * n ** 0.6)
                a = mp(x, y)
                out.add(arrow(a, a + p3(g / n * L), C.obj, width=width, tip=0.13, opacity=0.9))
    return out


@lru_cache(maxsize=1)
def tint_rgba():
    W, H = 960, 540
    xs = (np.arange(W) + 0.5) / W * 128 / 9 - 64 / 9
    ys = 4 - (np.arange(H) + 0.5) / H * 8
    X, Y = np.meshgrid(xs, ys)
    idx = np.digitize(hill((X - MAPC[0]) / U, (Y - MAPC[1]) / U), LEVELS)
    col = rgb(C.obj)[None, None] * (0.015 + 0.03 * idx)[..., None]
    return (np.clip(np.dstack([col, np.ones((H, W))]), 0, 1) * 255).astype(np.uint8)


def stage(s, contours=True, with_trail=True, at=None):
    """The map filling the frame: height tint, grid, contours and trail."""
    backdrop(s)
    s.add(ArrayLayer(tint_rgba(), height=8.0, z=-30, opacity=1.0 if at is None else fade(at, dur=0.9)))
    base = s.manim(z=-20)
    g = VGroup(plane(MAPC, U, 0.6))
    if contours:
        g.add(contour_mobs())
    if with_trail:
        g.add(trail_mob())
    if at is None:
        base.add(g)
    else:
        base.play(FadeIn(g), at=at, dur=0.9, ease=E, lead=0)
    return base


def plain(s, center=(0.0, 0.0), unit=1.0, op=0.6):
    """A full-frame grid with nothing else on it."""
    backdrop(s)
    s.manim(z=-20).add(plane(center, unit, op))


def ground(v, alpha=0.6):
    """The grid under the mountain, in map units, so it lands on the flat grid when the camera tilts down."""
    w = np.linspace(-8.0, 8.0, 130)
    for k in range(-8, 9):
        for P in (np.column_stack([np.full_like(w, k), w, np.zeros_like(w)]), np.column_stack([w, np.full_like(w, k), np.zeros_like(w)])):
            v.line(P, C.grid, 1.3, alpha, visible=(hill(P[:, 0], P[:, 1]) < 0.1) & seen(P, v.cam))


def hud(s):
    """A screen-locked layer for the equation boxes."""
    return s.manim(z=20, parallax=0.0)


def board(m, rows, spot="ul", at=None, out=None, gap=0.24, buff=0.24):
    """A framed black equation box. rows = [(mob, time), ...]; each row fades in on its beat."""
    col = VGroup(*[r[0] for r in rows]).arrange(DOWN, buff=gap)
    full = Rectangle(width=col.width + 2 * buff, height=col.height + 2 * buff).move_to(col)
    pos, edge = SPOTS[spot] if isinstance(spot, str) else spot
    VGroup(full, col).move_to(pos, aligned_edge=edge)
    top, cx, w = full.get_top()[1], full.get_center()[0], full.width

    def upto(k):
        h = top - (col[k].get_bottom()[1] - buff)
        return Rectangle(width=w, height=h, fill_color=C.bg, fill_opacity=1, stroke_color=C.frame, stroke_width=C.thin).move_to([cx, top - h / 2, 0])
    last = [k for k in range(len(rows)) if k == len(rows) - 1 or float(rows[k + 1][1]) > float(rows[k][1])]
    frame = upto(last[0])
    box = VGroup(frame, col)
    m.play(FadeIn(frame), at=(rows[0][1] - 0.25) if at is None else at, dur=0.4, ease=E, lead=0)
    for k in last[1:]:
        m.play(Transform(frame, upto(k)), at=float(rows[k][1]) - 0.32, dur=0.3, ease=E, lead=0)
    for mob, t in rows:
        m.play(FadeIn(mob, shift=0.06 * UP), at=t, dur=0.5, ease=E)
    if out is not None:
        m.play(FadeOut(box), at=out, dur=0.4, ease=E, lead=0)
    return box


def inset(m, center, w, h, at, out=None):
    """A framed black window for a small graph."""
    r = Rectangle(width=w, height=h, fill_color=C.bg, fill_opacity=1, stroke_color=C.frame, stroke_width=C.thin).move_to([center[0], center[1], 0])
    m.play(FadeIn(r), at=at, dur=0.4, ease=E, lead=0)
    if out is not None:
        m.play(FadeOut(r), at=out, dur=0.4, ease=E, lead=0)
    return r


def progress(s, n, title=None):
    """The chapter strip in the top corner, with the chapter's name at its first scene."""
    m = s.manim(z=40, parallax=0.0)
    row = VGroup()
    for i, name in enumerate(CHIPS):
        lit = i + 1 <= n
        box = Rectangle(width=0.58, height=0.3, fill_color=C.bg, fill_opacity=1, stroke_color=C.you if i + 1 == n else (C.frame if lit else C.faint), stroke_width=1.4)
        chip = VGroup(box)
        if lit:
            t = MathTex(name, font_size=20, color=C.text)
            chip.add(t.scale_to_fit_width(min(t.width, 0.48)).move_to(box))
        row.add(chip.move_to([6.56 - (7 - i) * 0.63, 3.72, 0]))
    m.add(row)
    if title:
        t = sc(title, 34, C.text)
        t = backed(t.scale_to_fit_width(min(t.width, 3.4)), 0.12, 1.0).move_to([-0.1, 3.68, 0])
        m.play(FadeIn(t), at=float(s.start) + 0.3, dur=0.6, ease=E, lead=0)
        m.play(FadeOut(t), at=float(s.start) + 4.4, dur=0.6, ease=E, lead=0)


def shore(m, cx=0.0):
    """Dido's beach from above as a surveyor's plan: the sea, the shoreline, and a 5 meter grid on the sand."""
    sea = Rectangle(width=14.6, height=4.2 - SHORE, stroke_width=0, fill_color=C.sea, fill_opacity=0.34).move_to([0, (4.2 + SHORE) / 2, 0])
    waves = VGroup(*[poly([[x, SHORE + d + 0.05 * np.sin(1.4 * x + 18 * d)] for x in np.linspace(-7.4, 7.4, 70)], C.con, 1.5, 0.5) for d in (0.3, 0.75, 1.25, 1.75)])
    lines = VGroup()
    for k in range(-30, 31):
        x = cx + k * 1.25 * BU
        if abs(x) < 7.3:
            major = k % 4 == 0
            lines.add(Line([x, -4.2, 0], [x, SHORE, 0], color=C.grid if major else C.grid_minor, stroke_width=1.5 if major else 1.0, stroke_opacity=0.7))
    for k in range(1, 30):
        y = SHORE - k * 1.25 * BU
        if y > -4.2:
            major = k % 4 == 0
            lines.add(Line([-7.3, y, 0], [7.3, y, 0], color=C.grid if major else C.grid_minor, stroke_width=1.5 if major else 1.0, stroke_opacity=0.7))
    m.add(lines, sea, waves, Line([-7.3, SHORE, 0], [7.3, SHORE, 0], color=C.axis, stroke_width=3))


def patch(P, a=1.0):
    """Enclosed land: a light amber fill with the rope as its crisp edge."""
    return VGroup(Polygon(*[p3(q) for q in P], fill_color=C.area, fill_opacity=0.28 * a, stroke_width=0), poly(P, C.con, 6, a))
