"""Shared drawing kit for video 015: type helpers, THE circle, the Map of Math, the chapter card, Buffon's needles.

Scenes import it with `from kit import *` (the video folder is on the path, as for `beats` and `theme`). Sizes follow
design/design_sheet.md: ring radius 2.75 u, node radius 0.4 u, THE circle (the hub) radius 1.375 u = R/2.
Everything here is a pure function of its arguments; nothing keeps state between frames.
"""
from __future__ import annotations

import math

import numpy as np
from aion import *  # noqa: F401,F403  (Manim names, C, tracks)
from aion import C
from aion.components.linalg import panel  # noqa: F401
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arc, Circle, Dot, Line, MathTex, Tex,  # noqa: F401
                   VGroup)

from theme import GLYPHS, NAMES, PILLARS

PX = 135.0                         # px per world unit at 1080p (raster layers are drawn at this density)
XW, YH = 64 / 9, 4.0               # half frame, world units
SAFE = 0.71                        # text-safe inset (96 px)
MAP_R, NODE_R, HUB_R = 2.75, 0.4, 1.375
FILL = 0.06                        # node and card tint
BOARD = 0.6                        # floorboard spacing = needle length (Buffon with l = d)
SEED = 1777                        # the needle stream (Buffon's year); placement uses SEED + 1
N_LOCK = 30_331                    # the stream first reads 2N/H = 3.1416 at this throw (checked in floor())
CIRCLE_W = 5.0                     # THE circle's stroke width


# ------------------------------------------------------------------------------------------------ type
def tex(s: str, size: float = 48, color=None) -> MathTex:
    """Maths in CM roman."""
    return MathTex(s, font_size=size, color=color or C.text)


def sans(s: str, size: float = 32, color=None) -> Tex:
    """Labels and key words in CM sans."""
    return Tex(r"\textsf{" + s + "}", font_size=size, color=color or C.text)


def caps(s: str, size: float = 32, color=None) -> Tex:
    """Names, dates and chapter cards in CM small caps."""
    return Tex(r"\textsc{" + s + "}", font_size=size, color=color or C.text)


def P3(x, y) -> np.ndarray:
    return np.array([float(x), float(y), 0.0])


def hue(p: str) -> str:
    return getattr(C, p)


def rgb255(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tint(color: str, a: float) -> str:
    """`color` at opacity `a` over black, mixed in linear light, as one solid hex (a tint that also hides what's under)."""
    c = np.array(rgb255(color)) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4) * a
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in srgb)


def backed(mob, pad: float = 0.06):
    """A label with a black backing so lines never cut through its glyphs."""
    from manim import Rectangle
    bg = Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_width=0, fill_color=C.bg,
                   fill_opacity=1.0).move_to(mob.get_center())
    return VGroup(bg, mob)


class Digits:
    """Tabular CM-sans numbers built from cached glyphs: one LaTeX run per character, never one per frame.

    Example:
        d = Digits(34)
        m.redraw(lambda t: d.number(f"{2 * n(t) / h(t):.4f}", right=1.0, base=3.0), during=(T.a, T.b))
    """

    CHARS = "0123456789."

    def __init__(self, size: float = 34, color=None):
        self.size, self.color = size, color or C.text
        self.glyphs = {c: Tex(r"\textsf{" + c + "}", font_size=size, color=self.color) for c in self.CHARS}
        self.glyphs["-"] = Tex(r"\textsf{--}", font_size=size, color=self.color)
        self.adv = self.glyphs["0"].width * 1.08          # every digit gets the same cell
        self.gap = self.adv * 0.42                        # thin space between thousands

    def number(self, s: str, right: float, base: float, color=None) -> VGroup:
        """`s` right-aligned so its last cell ends at x = `right`, digits sitting on baseline y = `base`."""
        cells, x = [], right
        for ch in reversed(s):
            if ch == " ":
                x -= self.gap
                continue
            g = self.glyphs[ch].copy()
            w = self.adv if ch.isdigit() or ch == "-" else g.width + 0.04
            g.move_to(P3(x - w / 2, 0)).shift(UP * (base - g.get_bottom()[1]))
            if ch == "-":
                g.shift(UP * 0.12)
            if color:
                g.set_color(color)
            cells.append(g)
            x -= w
        return VGroup(*cells)


def grouped(n: int) -> str:
    return f"{n:,}".replace(",", " ")


# ----------------------------------------------------------------------------------------------- circle
from map3d import FLAT, View, mix as _mix, prism  # noqa: E402  (the perspective camera and the prism hues)


def _proj(mob, view):
    if view is not None and (view.pitch or view.yaw or view.scale != 1.0 or view.c != (0.0, 0.0)):
        mob.apply_function(lambda q: view.project(q[None])[0][0])
    return mob


class PrismCircle(Circle):
    """THE circle as a prism ring: 36 arc pieces cycling through the six pillar hues (each hue at its map node, turned
    with the map by `turn` degrees), a hairline inner ring and, at hub size, 60 ticks (six major in pillar hues).
    It is still a Circle (its own points carry the fill), so move_to / scale / Transform / Create work as before.
    `color` makes it one plain color instead (for a circle that belongs to one branch)."""

    N = 36

    def __init__(self, radius: float = 1.0, turn: float = 0.0, ticks: bool | None = None, color=None,
                 stroke_width: float = 5.0, stroke_opacity: float = 1.0, **kw):
        kw.pop("stroke_color", None)
        super().__init__(radius=radius, stroke_width=stroke_width, stroke_color=C.circle, stroke_opacity=0.0, **kw)
        if ticks is None:
            ticks = radius >= 1.2
        # pieces in angle order (arc, inner hairline, ticks), so Create (lag_ratio 1) sweeps round once
        ir = radius - min(0.11, 0.08 * radius)
        for q in range(self.N):
            a0, a1 = 2 * math.pi * q / self.N, 2 * math.pi * (q + 1) / self.N
            col = color or prism((a0 + a1) / 2 - math.radians(turn))
            self.add(Arc(radius=radius, start_angle=a0, angle=a1 - a0, stroke_color=col, stroke_width=stroke_width,
                         stroke_opacity=stroke_opacity))
            if radius >= 0.8:
                self.add(Arc(radius=ir, start_angle=a0, angle=a1 - a0, stroke_color=color or C.circle,
                             stroke_width=1.2, stroke_opacity=0.5 * stroke_opacity))
            if ticks:
                for j in range(60):
                    a = math.radians(6 * j)
                    if not a0 <= a < a1:
                        continue
                    rel = (math.degrees(a) - (-90 + turn)) % 60                 # majors at the nodes
                    major = min(rel, 60 - rel) < 1e-6
                    l0, l1 = radius + 0.07, radius + (0.24 if major else 0.13)
                    self.add(Line(P3(l0 * math.cos(a), l0 * math.sin(a)), P3(l1 * math.cos(a), l1 * math.sin(a)),
                                  stroke_color=(color or prism(a - math.radians(turn))) if major else C.circle,
                                  stroke_width=2.4 if major else 1.1,
                                  stroke_opacity=(1.0 if major else 0.45) * stroke_opacity))


def the_circle(r: float = HUB_R, turn: float = 0.0, view: View | None = None, **kw) -> PrismCircle:
    """THE circle: a crisp prism ring in the six pillar hues. It is the hub of the map and every chapter's object.
    `turn` keeps its hues lined up with the map's nodes; `view` lays it on the tilted map plane."""
    kw.setdefault("stroke_width", CIRCLE_W)
    return _proj(PrismCircle(radius=r, turn=turn, **kw), view)


# ------------------------------------------------------------------------------------------------- map
def angle_of(k: int, turn: float = 0.0) -> float:
    """Node k's angle in radians: Foundations at 6 o'clock, then clockwise; `turn` in degrees."""
    return math.radians(-90 - 60 * k + turn)


def node_xy(k: int, R: float = MAP_R, turn: float = 0.0, c=(0.0, 0.0)) -> np.ndarray:
    a = angle_of(k, turn)
    return P3(c[0] + R * math.cos(a), c[1] + R * math.sin(a))


BOW, RISE = 0.06, 0.32             # chords bow toward the centre by BOW·length; lit arches rise RISE·length (tilted)


def _floor_path(i: int, j: int, R: float, turn: float, n: int = 28) -> np.ndarray:
    """The link i–j on the map plane (N×3): neighbours follow the ring, other pairs a chord bowed toward the centre."""
    if (j - i) % 6 in (1, 5):
        if (j - i) % 6 == 5:
            i, j = j, i
        a0 = angle_of(i, turn)
        aa = a0 - np.linspace(0, math.pi / 3, n)
        return np.c_[R * np.cos(aa), R * np.sin(aa), np.zeros(n)]
    a, b = node_xy(i, R, turn), node_xy(j, R, turn)
    s = np.linspace(0, 1, n)[:, None]
    pts = a * (1 - s) + b * s
    mid = (a + b) / 2
    nm = np.linalg.norm(mid)
    if nm > 1e-3:
        pts = pts - 4 * s * (1 - s) * (mid / nm) * BOW * np.linalg.norm(b - a)
    return pts


def _link(i: int, j: int, R: float, turn: float, view: View, lift: float, f0=0.0) -> VMobject:
    pts = _floor_path(i, j, R, turn)
    if lift > 0:
        s = np.linspace(0, 1, len(pts))
        pts = pts.copy()
        pts[:, 2] = lift * RISE * np.linalg.norm(pts[-1] - pts[0]) * 4 * s * (1 - s)
    ln = VMobject()
    ln.set_points_smoothly(view.project(pts)[0])
    return ln


def _rise(view: View) -> float:
    """How far the lit arches rise for this view: 0 flat (2D), growing with the tilt."""
    return min(view.pitch / math.radians(40), 1.0) * (1.0 - 0.45 * min(max(view.pitch - 0.7, 0) / 0.3, 1.0))


def map_lines(R: float = MAP_R, color=None, width: float = 1.6, opacity: float = 1.0, pairs=None,
              turn: float = 0.0, view: View = FLAT) -> VGroup:
    """The map's fifteen links as plain lines on the map plane: six ring arcs between neighbours (the track) and nine
    chords, bowed gently toward the hub. Order: arcs k→k+1 for k = 0..5, then chords (i, j)."""
    color = color or C.map_off
    g = VGroup()
    for i, j in link_pairs():
        g.add(_link(i, j, R, turn, view, 0.0).set_stroke(color=color, width=width, opacity=opacity))
    return g


def link_pairs() -> list[tuple[int, int]]:
    """Node index pairs in map_lines() order."""
    out = [(k, (k + 1) % 6) for k in range(6)]
    out += [(i, j) for i in range(6) for j in range(i + 2, 6) if (i, j) != (0, 5)]
    return out


def lit_link(i: int, j: int, turn: float = 0.0, view: View = FLAT, opacity: float = 0.95, width: float = 3.0,
             R: float = MAP_R) -> VMobject:
    """One lit link: shaded from node i's hue to node j's; on a tilted view it rises off the plane as an arch."""
    ln = _link(i, j, R, turn, view, _rise(view))
    ln.set_stroke(color=[hue(PILLARS[i]), hue(PILLARS[j])], width=width, opacity=opacity)
    ln.set_sheen_direction(ln.get_end() - ln.get_start())
    return ln


def lit_links(opacity: float = 0.85, width: float = 2.4, turn: float = 0.0, view: View = FLAT) -> VGroup:
    """All fifteen links in their two pillar hues (a gradient from one node's hue to the other's)."""
    return VGroup(*(lit_link(i, j, turn, view, opacity, width) for i, j in link_pairs()))


def map_deco(turn: float = 0.0, view: View = FLAT, R: float = MAP_R, opacity: float = 1.0) -> VGroup:
    """What grounds the map: a faint polar grid (two rings, twelve spokes) and the track's two outer rails."""
    g = VGroup()
    for rr, w, op in ((0.7 * R, 1.0, 0.3), (1.22 * R, 1.0, 0.3), (R - 0.08, 1.2, 0.45), (R + 0.08, 1.2, 0.45)):
        aa = np.linspace(0, 2 * math.pi, 121)
        c_ = VMobject().set_points_smoothly(view.project(np.c_[rr * np.cos(aa), rr * np.sin(aa), np.zeros(121)])[0])
        g.add(c_.set_stroke(color=C.map_off, width=w, opacity=op * opacity))
    for j in range(12):
        a = math.radians(-90 + 30 * j + turn)
        seg = np.array([[1.2 * HUB_R * math.cos(a), 1.2 * HUB_R * math.sin(a), 0],
                        [1.22 * R * math.cos(a), 1.22 * R * math.sin(a), 0]])
        g.add(VMobject().set_points_as_corners(view.project(seg)[0]).set_stroke(color=C.map_off, width=0.9,
                                                                                    opacity=0.2 * opacity))
    return g


def node(k: int, lit: bool = False, turn: float = 0.0, glyph: bool = True, label: bool = True,
         c=(0.0, 0.0), view: View = FLAT, lift: float | None = None) -> VGroup:
    """Map node k as a medallion: a face ring with a solid fill (hides link ends), an outer halo ring and an inner
    hexagon. Lit: hue strokes, tint fill, glyph, name in small caps. On a tilted view the node rises on a stem over its
    shadow. Parts: [face, halo, hexagon, (glyph), (label), (stem, shadow)]."""
    p = PILLARS[k]
    col = hue(p) if lit else C.map_off
    if lift is None:
        lift = 0.55 * math.sin(view.pitch)
    base = node_xy(k, turn=turn, c=c)
    top = base + np.array([0, 0, lift])
    sc = view.project(top[None])[0][0]
    kk = view.k_at(top)
    rr = NODE_R * kk
    flat = math.cos(view.pitch) * 0.35 + 0.65
    face = Circle(radius=rr, stroke_color=col, stroke_width=3.0 if lit else 2.0,
                  fill_color=tint(col, 0.16) if lit else C.bg, fill_opacity=1.0)
    halo = Circle(radius=rr * 1.22, stroke_color=col, stroke_width=1.2, stroke_opacity=0.7 if lit else 0.35)
    hexa = Polygon(*[P3(rr * 0.78 * math.cos(math.pi / 6 + q * math.pi / 3), rr * 0.78 * math.sin(math.pi / 6 + q * math.pi / 3))
                     for q in range(6)], stroke_color=col, stroke_width=1.2, stroke_opacity=0.55 if lit else 0.3)
    g = VGroup()
    for mob in (face, halo, hexa):
        g.add(mob.stretch(flat, 1).move_to(sc))
    if lit and glyph:
        gl = tex(GLYPHS[p], 44 * kk, col)
        if gl.width > 1.4 * rr:
            gl.scale_to_fit_width(1.4 * rr)
        g.add(gl.move_to(sc))
    if lit and label:
        g.add(node_label(k, turn, c, view=view, at=sc, rr=rr))
    if lift > 0.01:
        sb = view.project(np.array([base, top]))[0]
        stem = Line(sb[0], sb[1], stroke_color=col, stroke_width=1.6, stroke_opacity=0.6)
        shadow = Circle(radius=rr * 0.7, stroke_color=col, stroke_width=1.2, stroke_opacity=0.45)
        shadow.stretch(math.cos(view.pitch), 1).move_to(sb[0])
        g.add(stem, shadow)
        g.submobjects = g.submobjects[-2:] + g.submobjects[:-2]      # stem and shadow under the medallion
    return g


def node_label(k: int, turn: float = 0.0, c=(0.0, 0.0), view: View = FLAT, at=None, rr: float = NODE_R) -> Tex:
    p = PILLARS[k]
    pos = node_xy(k, turn=turn, c=c) if at is None else at
    lab = caps(NAMES[p], 32, hue(p))
    a = angle_of(k, turn) + view.yaw
    d = np.array([math.cos(a), math.sin(a) * math.cos(view.pitch)])
    if abs(d[1]) > 0.9 * np.linalg.norm(d):           # 12 and 6 o'clock: beside the node, clear of the track
        up = d[1] > 0
        lab.move_to(pos + RIGHT * (rr * 1.22 + 0.08) + (UP if up else DOWN) * 0.55 * rr,
                    aligned_edge=LEFT + (DOWN if up else UP))
    else:
        dd = RIGHT if d[0] > 0 else LEFT
        lab.next_to(pos + dd * rr * 1.22, dd, buff=0.12)
    return lab


def chapter_card(pillar: str, field: str, c=(0.0, 0.0)) -> VGroup:
    """The chapter card: the node's ring grown to radius 0.78 with its glyph (96), the name in small caps (80) and the
    field in CM sans (36, muted). Parts: [ring, glyph, name, field]."""
    ring = Circle(radius=0.78, stroke_color=hue(pillar), stroke_width=3.0, fill_color=tint(hue(pillar), 0.16),
                  fill_opacity=1.0)
    ring.add(Circle(radius=0.95, stroke_color=hue(pillar), stroke_width=1.4, stroke_opacity=0.7),
             RegularPolygon(6, radius=0.62, stroke_color=hue(pillar), stroke_width=1.4, stroke_opacity=0.55))
    ring.move_to(P3(c[0], c[1] + 1.05))
    gl = tex(GLYPHS[pillar], 96, hue(pillar)).move_to(ring.get_center())
    if gl.width > 1.25:
        gl.scale_to_fit_width(1.25)
    name = caps(NAMES[pillar], 80).move_to(P3(c[0], c[1] - 0.55))
    sub = sans(field, 36, C.muted).next_to(name, DOWN, buff=0.34)
    return VGroup(ring, gl, name, sub)


# ---------------------------------------------------------------------------------------------- needles
def buffon(n: int, seed: int = SEED):
    """Buffon trials, needle length = board spacing = 1: centre distance x to the nearest line, angle θ, crossed?
    Row k is throw k for every n (a true stream)."""
    u = np.random.default_rng(seed).random((n, 2))
    x, th = 0.5 * u[:, 0], np.pi * u[:, 1]
    return x, th, x <= 0.5 * np.sin(th)


def floor(n: int = N_LOCK, box=(-8.0, -4.8, 8.0, 4.8), seed: int = SEED + 1):
    """The first n throws placed on a floor of horizontal boards inside `box` (world units).

    The (x, θ) of each throw is the maths, so a needle crosses on screen exactly when x ≤ ½ sin θ. Which board, which
    side of it and how far along come from their own seed. Returns cx, cy, th, hit, board line heights.
    """
    x0, y0, x1, y1 = box
    xs, th, hit = buffon(n)
    est = 2 * n / hit.sum()
    if n == N_LOCK:
        assert f"{est:.4f}" == "3.1416", est
    rg = np.random.default_rng(seed)
    lines_y = np.arange(math.ceil(y0 / BOARD) * BOARD, y1 + 1e-9, BOARD)
    k = rg.integers(0, len(lines_y), n)
    side = rg.choice((-1.0, 1.0), n)
    cx = rg.uniform(x0, x1, n)
    cy = lines_y[k] + side * xs * BOARD
    return cx, cy, th, hit, lines_y


class Canvas:
    """A skia surface covering a world box at PX px/unit; `layer_kw()` places the array in the world."""

    def __init__(self, box, px: float = PX):
        import skia
        self.skia, self.box, self.px = skia, box, px
        x0, y0, x1, y1 = box
        self.w, self.h = int(round((x1 - x0) * px)), int(round((y1 - y0) * px))
        self.surf = skia.Surface(self.w, self.h)

    def T(self, x, y):
        return (x - self.box[0]) * self.px, (self.box[3] - y) * self.px

    def begin(self):
        c = self.surf.getCanvas()
        c.clear(self.skia.ColorTRANSPARENT)
        return c

    def array(self) -> np.ndarray:
        sk = self.skia
        return self.surf.makeImageSnapshot().toarray(colorType=sk.kRGBA_8888_ColorType, alphaType=sk.kPremul_AlphaType)

    def layer_kw(self) -> dict:
        x0, y0, x1, y1 = self.box
        return dict(height=y1 - y0, pos=((x0 + x1) / 2, (y0 + y1) / 2), premultiplied=True)

    def paint(self, color: str, alpha: float = 1.0, width: float = 3.0):
        sk = self.skia
        r, g, b = rgb255(color)
        return sk.Paint(AntiAlias=True, Style=sk.Paint.kStroke_Style, StrokeWidth=width,
                        StrokeCap=sk.Paint.kRound_Cap, Color=sk.Color(r, g, b, int(round(255 * min(max(alpha, 0), 1)))))


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def dim(mob, k: float):
    """Scale every stroke and fill opacity in `mob` by k (keeps each part's own opacity; never turns a fill on)."""
    for sm in mob.family_members_with_points():
        sm.set_stroke(opacity=sm.get_stroke_opacity() * k, family=False)
        sm.set_fill(opacity=sm.get_fill_opacity() * k, family=False)
    return mob


def window(fn, a: float, b: float):
    """A redraw function that draws `fn(t)` only for a <= t < b (empty outside), for `m.redraw(..., during=(a, b+))`.
    A redraw keeps its last mobject after its window, so it must end on an empty frame."""
    def f(t):
        return fn(t) if a <= t < b else VGroup()
    return f


# --------------------------------------------------------------------------------------------- chapter 1
R1 = 2.2                           # the leash circle (Ch1): one leash length
UNIT1 = R1 / 5                     # grid unit, so the leash is five units long in ch1_s04
GRID_C = P3(-2.6, 0.0)             # where the post sits once the grid is in (ch1_s03, ch1_s04)


def post(c=ORIGIN) -> VGroup:
    """The post seen from above: a wooden disc (warm, with growth rings) and a cross on it."""
    c = np.asarray(c, dtype=float)
    return VGroup(Circle(radius=0.16, stroke_width=0, fill_color=C.bg, fill_opacity=0.7).move_to(c + P3(0.03, -0.04)),
                  Circle(radius=0.14, stroke_color=tint(C.change, 0.5), stroke_width=2.2, fill_color=tint(C.change, 0.12),
                         fill_opacity=1).move_to(c),
                  Circle(radius=0.09, stroke_color=tint(C.change, 0.3), stroke_width=1.2).move_to(c),
                  Circle(radius=0.045, stroke_color=tint(C.change, 0.3), stroke_width=1.2).move_to(c),
                  Line(c + P3(-0.2, 0), c + P3(0.2, 0), stroke_color=C.text, stroke_width=2.2),
                  Line(c + P3(0, -0.2), c + P3(0, 0.2), stroke_color=C.text, stroke_width=2.2))


def dog(pos, heading: float, k: float = 1.0, phase: float | None = None, size: float = 1.35) -> VGroup:
    """A dog seen from above in C.foundations: a shaded body with a darker back stripe, head with snout and floppy
    ears, a wagging tail, and four legs that step in a trot while `phase` (radians of stride) advances.
    `phase=None` is a dog standing still. Points along `heading` (radians).
    """
    pos = np.asarray(pos, dtype=float)
    u, v = P3(math.cos(heading), math.sin(heading)), P3(-math.sin(heading), math.cos(heading))
    sz = size
    col, fill, dark = C.foundations, tint(C.foundations, 0.32), tint(C.foundations, 0.18)
    ph = 0.0 if phase is None else phase
    amp = 0.0 if phase is None else 0.07 * sz
    legs = VGroup()
    for fx, sy, off in ((0.14, 1, 0.0), (0.14, -1, math.pi), (-0.17, 1, math.pi), (-0.17, -1, 0.0)):
        step = amp * math.sin(ph + off)
        legs.add(Ellipse(width=0.1 * sz, height=0.06 * sz, stroke_width=0, fill_color=dark, fill_opacity=1)
                 .rotate(heading).move_to(pos + (fx * sz + step) * u + sy * 0.13 * sz * v))
    shadow = Ellipse(width=0.62 * sz, height=0.36 * sz, stroke_width=0, fill_color=C.bg, fill_opacity=0.6)
    shadow.rotate(heading).move_to(pos + P3(0.04, -0.05) * sz)
    body = Ellipse(width=0.48 * sz, height=0.26 * sz, stroke_color=col, stroke_width=2.2, fill_color=fill,
                   fill_opacity=1).rotate(heading).move_to(pos - 0.04 * sz * u)
    stripe = Ellipse(width=0.34 * sz, height=0.08 * sz, stroke_width=0, fill_color=dark, fill_opacity=1)
    stripe.rotate(heading).move_to(pos - 0.06 * sz * u)
    sheen = Ellipse(width=0.26 * sz, height=0.05 * sz, stroke_width=0, fill_color=tint(C.foundations, 0.6),
                    fill_opacity=0.7).rotate(heading).move_to(pos - 0.02 * sz * u + 0.07 * sz * v)
    head = Circle(radius=0.11 * sz, stroke_color=col, stroke_width=2.2, fill_color=fill, fill_opacity=1)
    head.move_to(pos + 0.25 * sz * u)
    snout = Ellipse(width=0.1 * sz, height=0.08 * sz, stroke_color=col, stroke_width=1.6, fill_color=fill,
                    fill_opacity=1).rotate(heading).move_to(pos + 0.35 * sz * u)
    nose = Dot(pos + 0.395 * sz * u, radius=0.018 * sz, color=C.bg)
    flap = 0.03 * sz * math.sin(2 * ph)
    ears = VGroup(*(Ellipse(width=0.12 * sz, height=0.06 * sz, stroke_width=0, fill_color=col, fill_opacity=1)
                    .rotate(heading + s_ * 0.5).move_to(pos + (0.2 * sz - abs(flap)) * u + s_ * 0.12 * sz * v)
                    for s_ in (-1, 1)))
    wag = 0.09 * sz * math.sin(3 * ph + 1.0) if phase is not None else 0.04 * sz
    tail = VMobject(stroke_color=col, stroke_width=3.0).set_points_smoothly(
        [pos - 0.26 * sz * u, pos - 0.36 * sz * u + 0.5 * wag * v, pos - 0.45 * sz * u + wag * v])
    return dim(VGroup(shadow, legs, tail, body, stripe, sheen, ears, head, snout, nose), k)


def paw(pos, heading: float, side: float = 1.0, color=None, opacity: float = 1.0) -> VGroup:
    """A paw print: a pad and three toes, pointing along `heading`, nudged left/right by `side`."""
    pos = np.asarray(pos, dtype=float)
    u, v = P3(math.cos(heading), math.sin(heading)), P3(-math.sin(heading), math.cos(heading))
    c = pos + side * 0.06 * v
    col = color or C.foundations
    g = VGroup(Ellipse(width=0.075, height=0.06, stroke_width=0, fill_color=col, fill_opacity=opacity)
               .rotate(heading).move_to(c))
    for a in (-0.7, 0.0, 0.7):
        g.add(Dot(c + 0.06 * (math.cos(a) * u + math.sin(a) * v), radius=0.017, color=col).set_opacity(opacity))
    return g


def leash(a, b, slack: float = 0.0, side: float = 1.0) -> VMobject:
    """The leash from post `a` to collar `b`: straight when taut, bowed sideways by `slack` (0..1) when loose."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    d = b - a
    n = P3(-d[1], d[0]) / max(np.linalg.norm(d), 1e-6)
    mid = (a + b) / 2 + side * slack * 0.45 * n
    pts = [(1 - s) ** 2 * a + 2 * (1 - s) * s * mid + s * s * b for s in np.linspace(0, 1, 24)]
    return VMobject(stroke_color=C.circle, stroke_width=2.6).set_points_smoothly(pts)


def set_braces(height: float, gap: float, c=ORIGIN, color=None) -> VGroup:
    """A pair of set braces { } of the given height, `gap` apart, centred on c."""
    c = np.asarray(c, dtype=float)
    l, r = tex(r"\{", 96, color or C.foundations), tex(r"\}", 96, color or C.foundations)
    for b in (l, r):
        b.stretch_to_fit_height(height).stretch_to_fit_width(height * 0.22)
    l.move_to(c + LEFT * gap / 2)
    r.move_to(c + RIGHT * gap / 2)
    return VGroup(l, r)


def reuleaux(n: int, width: float, samples: int = 40) -> np.ndarray:
    """Boundary of the Reuleaux n-gon (n odd) of constant `width`, centred at its centroid: (n·samples, 2).

    The arc between vertices k and k+1 is centred on the opposite vertex k + (n+1)/2, with radius = width.
    """
    Rv = width / (2 * math.cos(math.pi / (2 * n)))
    V = np.array([[Rv * math.cos(math.pi / 2 + 2 * math.pi * k / n), Rv * math.sin(math.pi / 2 + 2 * math.pi * k / n)]
                  for k in range(n)])
    out = []
    for k in range(n):
        c = V[(k + (n + 1) // 2) % n]
        a0 = math.atan2(*(V[k] - c)[::-1])
        a1 = math.atan2(*(V[(k + 1) % n] - c)[::-1])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for s in np.linspace(0, 1, samples, endpoint=False):
            out.append(c + width * np.array([math.cos(a0 + s * da), math.sin(a0 + s * da)]))
    return np.array(out)


A0 = math.atan2(4, 3)                           # the point starts at (3, 4)
COL = {  # Ch1 side colors: x leg, y leg, the leash r
    "x": C.space, "y": C.quantity, "r": C.circle}


def eq_parts(*parts, size=64):
    """MathTex from parts, each part colored by the symbol it is about."""
    m = MathTex(*parts, font_size=size, color=C.text)
    for sub, p in zip(m, parts):
        if p.startswith("x"):
            sub.set_color(COL["x"])
        elif p.startswith("y"):
            sub.set_color(COL["y"])
        elif p.startswith("r"):
            sub.set_color(COL["r"])
        elif p in (r"\{", r"\}"):
            sub.set_color(C.foundations)
    return m


def triangle(a, k=1.0):
    """Ch1: right triangle under the point at angle a on the circle (centre GRID_C): legs x, y and the leash r."""
    o = GRID_C
    p = o + R1 * P3(math.cos(a), math.sin(a))
    f = P3(p[0], o[1])
    g = VGroup(Line(o, f, stroke_color=COL["x"], stroke_width=4),
               Line(f, p, stroke_color=COL["y"], stroke_width=4),
               Line(o, p, stroke_color=COL["r"], stroke_width=4))
    sx, sy = np.sign(p[0] - o[0]) or 1, np.sign(p[1] - o[1]) or 1
    if abs(p[0] - o[0]) > 0.3 and abs(p[1] - o[1]) > 0.3:
        q = 0.2
        g.add(VMobject(stroke_color=C.text, stroke_width=1.6).set_points_as_corners(
            [f + P3(-sx * q, 0), f + P3(-sx * q, sy * q), f + P3(0, sy * q)]))
    g.add(tex("x", 40, COL["x"]).next_to((o + f) / 2, DOWN * sy, buff=0.14),
          tex("y", 40, COL["y"]).next_to((f + p) / 2, RIGHT * sx, buff=0.14),
          tex("r", 40, COL["r"]).move_to((o + p) / 2 + 0.3 * P3(-math.sin(a), math.cos(a)) * sx * sy),
          Dot(p, radius=0.08, color=C.text))
    for sm in g.family_members_with_points():
        sm.set_stroke(opacity=sm.get_stroke_opacity() * k, family=False)
        sm.set_fill(opacity=sm.get_fill_opacity() * k, family=False)
    return g


# --------------------------------------------------------------------------------------------- chapter 2
def pi_digits(n: int) -> str:
    """'3.' followed by the first n decimals of π (mpmath, exact)."""
    from mpmath import mp
    mp.dps = n + 10
    return mp.nstr(mp.pi, n + 1, strip_zeros=False)[: n + 2]


_LINE_DIGITS: dict = {}


def line_digits(size: float = 26) -> "Digits":
    if size not in _LINE_DIGITS:
        _LINE_DIGITS[size] = Digits(size, C.muted)
    return _LINE_DIGITS[size]


def zline(c: float, scale: float, y: float = 0.0, x_lo: float = -7.6, x_hi: float = 7.6, labels: bool = True,
          size: float = 26, color=None, opacity: float = 1.0, spacing: float = 1.6) -> VGroup:
    """A number line seen through a zoom: value v sits at x = (v - c)·scale. Ticks and labels adapt to the zoom.

    Major ticks are 1, 2 or 5 × 10^k apart (about 1.6 units on screen), minor ticks a fifth of that; labels are tabular
    CM sans with just enough decimals. Returns VGroup(axis, minor, major, labels).
    """
    color = color or C.muted
    v_lo, v_hi = c + x_lo / scale, c + x_hi / scale
    raw = spacing / scale
    e = math.floor(math.log10(raw))
    step = next(m * 10 ** e for m in (1, 2, 5, 10) if m * 10 ** e >= raw)
    dec = max(0, -math.floor(math.log10(step) + 1e-9))
    axis = Line(P3(x_lo, y), P3(x_hi, y), stroke_color=color, stroke_width=2, stroke_opacity=opacity)
    minor, major, labs = VGroup(), VGroup(), VGroup()
    ms = step / 5
    if ms * scale > 0.12:
        for i in range(math.ceil(v_lo / ms), math.floor(v_hi / ms) + 1):
            if i % 5:
                x = (i * ms - c) * scale
                minor.add(Line(P3(x, y - 0.06), P3(x, y + 0.06), stroke_color=color, stroke_width=1.2,
                               stroke_opacity=opacity))
    dg = line_digits(size)
    for i in range(math.ceil(v_lo / step), math.floor(v_hi / step) + 1):
        v = i * step
        x = (v - c) * scale
        major.add(Line(P3(x, y - 0.13), P3(x, y + 0.13), stroke_color=color, stroke_width=2, stroke_opacity=opacity))
        if labels:
            s = f"{abs(v):.{dec}f}"
            g = dg.number(s, 0.0, y - 0.48)
            if v < -1e-12:
                g.add(dg.number("-", 0.0, y - 0.48).shift(LEFT * (g.width + 0.04)))
            g.shift(RIGHT * (x - g.get_center()[0]))
            labs.add(g.set_opacity(opacity))
    return VGroup(axis, minor, major, labs)


def map_state(turn: float = 0.0, lit=(), edges=(), link_width: float = 1.8, view: View = FLAT,
              deco: bool = True) -> tuple[VGroup, VGroup]:
    """The Map of Math turned by `turn` degrees and seen through `view` (FLAT = the 2D map; a tilted View = 2.5D/3D):
    (links, nodes). links = VGroup(dim, lit): dim = VGroup(deco, the fifteen plain links); lit = the lit edges, in the
    order given, as arches in their two hues. Lit nodes by pillar name."""
    dim = VGroup(map_deco(turn, view) if deco else VGroup(),
                 map_lines(color=C.map_off, width=link_width * 0.8, opacity=0.6, turn=turn, view=view))
    over = VGroup()
    for e in edges:
        i, j = sorted(PILLARS.index(x) for x in e)
        over.add(lit_link(i, j, turn, view))
    nodes = VGroup(*(node(k, lit=PILLARS[k] in lit, turn=turn, view=view) for k in range(6)))
    return VGroup(dim, over), nodes


def turn_view(u: float, peak: float, yaw: float = 0.0) -> View:
    """The camera during a signature map turn: it tips by up to `peak` degrees at mid-turn and settles back flat
    (u = turn progress 0..1)."""
    w = math.sin(math.pi * min(max(u, 0.0), 1.0)) ** 2
    return View(pitch=math.radians(peak) * w, yaw=math.radians(yaw) * w, dist=12.0, scale=1.0 - 0.08 * w)


def finale_view(t: float, t_ev: float, t_wh: float) -> View:
    """The finale camera (ch7_s04 → out_s01): on 'Every lens' the full map lifts into 3D (56° tilt) and slowly orbits,
    then settles flat again just before 'what is a circle'. A pure function of absolute time, so both scenes agree."""
    def ss_(x):
        x = min(max(x, 0.0), 1.0)
        return x * x * (3 - 2 * x)
    w = ss_((t - t_ev - 0.3) / 2.4) * (1 - ss_((t - t_wh + 2.4) / 2.1))
    return View(pitch=math.radians(56) * w, yaw=math.radians(-12 + 4.5 * (t - t_ev)) * w, dist=11.0,
                scale=1.0 + 0.04 * w)


def hub_at(turn: float = 0.0, view: View = FLAT, k: float = 1.0) -> PrismCircle:
    """The map's hub (THE circle, filled with the background) on the map plane."""
    return the_circle(HUB_R * k, turn=turn, view=view, fill_color=C.bg, fill_opacity=1.0)


def partial(mob, a: float):
    """mob drawn up to share a (0..1) as Create draws it (parts one after another), for redraws."""
    if a >= 1:
        return mob
    fam = mob.family_members_with_points()
    n = len(fam)
    for i, sm in enumerate(fam):
        sm.pointwise_become_partial(sm.copy(), 0, min(max(a * n - i, 0.0), 1.0))
    return mob


def face_of(n):
    """A map node's face circle (its centre is the node's screen position)."""
    return next(x for x in n if isinstance(x, Circle) and x.get_fill_opacity() > 0.5)


# ---------------------------------------------------------------------------------------------- Ch3 plane
PL_O, PL_U = P3(-3.0, -0.3), 1.6            # the complex plane of ch3_s04–s06: origin and unit
PL_BOX = (-6.9, -3.95, 0.9, 3.0)


def plane_line():
    """The real number line of the Ch3 plane, −2 to 2, its labels backed so grid lines never cut them."""
    g = VGroup(Line(PL_O + P3(-3.75, 0), PL_O + P3(3.75, 0), stroke_color=C.axis, stroke_width=2.6))
    for v in range(-2, 3):
        g.add(Line(PL_O + P3(v * PL_U, -0.12), PL_O + P3(v * PL_U, 0.12), stroke_color=C.axis, stroke_width=2.6),
              backed(tex(str(v), 34, C.muted).move_to(PL_O + P3(v * PL_U + (0.2 if v == 0 else 0), -0.48))))
    return g


def plane_grid(opacity: float = 1.0):
    """The Classic grid of the Ch3 plane."""
    import numpy as np
    from aion.components.linalg import grid_lines
    return grid_lines(np.eye(2), center=tuple(PL_O[:2]), unit=PL_U, box=PL_BOX, minor=1, opacity=opacity)


# ---------------------------------------------------------------------------------------------- Ch4 solids
TOR_R, TOR_r = 0.75, 0.32                    # the torus of shaders/solid.frag, in object units


def lin(c: str) -> tuple:
    """A theme color as a linear-light RGB tuple for shader uniforms."""
    from aion.comp.comp import hex_to_linear
    return tuple(float(x) for x in hex_to_linear(c))


def to_view(q, tilt: float, spin: float):
    """Object points (N×3, z up) → view space, exactly as shaders/solid.frag does: spin about z, then tilt about x."""
    import numpy as np
    q = np.atleast_2d(np.asarray(q, dtype=float))
    cs, sn = np.cos(spin), np.sin(spin)
    v = np.c_[cs * q[:, 0] - sn * q[:, 1], sn * q[:, 0] + cs * q[:, 1], q[:, 2]]
    ct, st = np.cos(tilt), np.sin(tilt)
    return np.c_[v[:, 0], ct * v[:, 1] - st * v[:, 2], st * v[:, 1] + ct * v[:, 2]]


def torus_xyz(u, v, R: float = TOR_R, r: float = TOR_r, grow: float = 1.0):
    """Points on the torus about z: u around the hole, v around the tube."""
    import numpy as np
    u, v = np.broadcast_arrays(np.asarray(u, float), np.asarray(v, float))
    return np.stack([(R + grow * r * np.cos(v)) * np.cos(u), (R + grow * r * np.cos(v)) * np.sin(u),
                     grow * r * np.sin(v)], -1)


def surface_curve(q, normals, c, size: float, tilt: float, spin: float, color, width: float = 4.0,
                  back: float = 0.0) -> VGroup:
    """A curve on a solid drawn over its shader render: segments whose surface normal faces away are hidden
    (opacity `back`), so the curve wraps round the solid."""
    import numpy as np
    pv = to_view(q, tilt, spin)
    nv = to_view(normals, tilt, spin)
    g = VGroup()
    for k in range(len(pv) - 1):
        face = 0.5 * (nv[k, 2] + nv[k + 1, 2])
        op = 1.0 if face > 0.02 else back
        if op <= 0:
            continue
        a = np.asarray(c, float) + size * np.array([pv[k, 0], pv[k, 1], 0.0])
        b = np.asarray(c, float) + size * np.array([pv[k + 1, 0], pv[k + 1, 1], 0.0])
        g.add(Line(a, b, stroke_color=color, stroke_width=width, stroke_opacity=op))
    return g


# ---------------------------------------------------------------------------------------------- Ch4 band
BAND_TH = None                               # the angles every loop is sampled at (set lazily)


def band_theta():
    import numpy as np
    global BAND_TH
    if BAND_TH is None:
        BAND_TH = np.linspace(0, 2 * np.pi, 361)
    return BAND_TH


def r_poly(n: int, R: float, phase: float = 0.0):
    """Radial function of a regular n-gon with the same area as a circle of radius R (an edge midpoint at `phase`)."""
    import numpy as np
    th = band_theta()
    apo = R * np.sqrt(np.pi / (n * np.tan(np.pi / n)))           # apothem for equal area
    w = np.mod(th - phase - np.pi / n, 2 * np.pi / n) - np.pi / n
    return apo / np.cos(w)


def r_blob(R: float):
    import numpy as np
    th = band_theta()
    return R * (1 + 0.16 * np.sin(2 * th + 0.5) + 0.11 * np.cos(3 * th - 1.0) + 0.06 * np.sin(5 * th + 2.0))


def r_star(R: float, k: int = 5):
    import numpy as np
    th = band_theta()
    return R * (0.78 + 0.34 * np.cos(k * (th - np.pi / 2)))


def band(r, c, color=None, width: float = 12.0, opacity: float = 1.0) -> VGroup:
    """The rubber band: a closed curve r(θ) about c, drawn as a lit elastic tube.

    Three strokes along the same path: a dark rim (full width), the body (its color), and a thin specular streak
    pushed toward the light (upper left), so the band reads as round rubber rather than a flat line.
    """
    import numpy as np
    th = band_theta()
    col = color or C.space
    c = np.asarray(c, float)
    pts = [c + np.array([ri * np.cos(t), ri * np.sin(t), 0.0]) for ri, t in zip(r, th)]
    off = np.array([-0.32, 0.42, 0.0]) * width / PX                   # toward the light, a third of the half-width
    pts_h = [p_ + off for p_ in pts]

    def path(ps, colr, w, op):
        v = VMobject(stroke_color=colr, stroke_width=w, stroke_opacity=op * opacity)
        v.set_points_as_corners(ps)
        return v

    return VGroup(path(pts, mix_hex(str(ManimColor(col).to_hex()), C.bg, 0.55), width, 1.0),
                  path(pts, col, width * 0.68, 1.0),
                  path(pts_h, mix_hex(str(ManimColor(col).to_hex()), C.text, 0.7), max(width * 0.16, 1.0), 0.85))


# --------------------------------------------------------------------------------------------- chapter 6
FL_SC = 1.5                                  # the full-frame floor of Ch6: boards 0.9 apart, sticks 0.9 long
FL_BOX = (-7.4, -4.2, 7.4, 4.2)
RO, RSX, RSY = P3(0.9, -1.9), 1.5, 3.0       # the (θ, x) rectangle: θ ∈ [0, π] across, x ∈ [0, 1] up (half boards)
HERO = (1.1, 0.75)                           # the stick measured in ch6_s03: angle θ, distance x (half boards)


def full_floor(n: int):
    """The first n throws on Ch6's full-frame floor (screen units): cx, cy, th, hit, crack heights, half length."""
    box = tuple(v / FL_SC for v in FL_BOX)
    cx, cy, th, hit, ly = floor(n=n, box=box)
    return cx * FL_SC, cy * FL_SC, th, hit, ly * FL_SC, 0.5 * BOARD * FL_SC


def mix_hex(a: str, b: str, u: float) -> str:
    """sRGB blend of two hex colors (u = 0 → a, 1 → b)."""
    u = min(max(u, 0.0), 1.0)
    ca, cb = np.array(rgb255(a), float), np.array(rgb255(b), float)
    return "#" + "".join(f"{int(round(v)):02X}" for v in (1 - u) * ca + u * cb)


def rpt(th, x, o=None, sx: float = RSX, sy: float = RSY):
    """A point (θ, x) of the rectangle in screen units."""
    o = RO if o is None else o
    return o + P3(sx * th, sy * x)


def rect_axes(o=None, sx: float = RSX, sy: float = RSY, size: float = 34) -> VGroup:
    """The rectangle of possibilities (C.space) and its labels: VGroup(frame, VGroup(0, π, 0, 1, θ, x))."""
    from manim import Polygon
    o = RO if o is None else o
    a, b = rpt(0, 0, o, sx, sy), rpt(math.pi, 1, o, sx, sy)
    frame = Polygon(a, P3(b[0], a[1]), b, P3(a[0], b[1]), stroke_color=C.space, stroke_width=2.6, fill_opacity=0)
    lab = VGroup(tex("0", size, C.muted).move_to(a + P3(0, -0.32)),
                 tex(r"\pi", size, C.muted).move_to(P3(b[0], a[1] - 0.32)),
                 tex("0", size, C.muted).move_to(a + P3(-0.3, 0)),
                 tex("1", size, C.muted).move_to(P3(a[0] - 0.3, b[1])),
                 tex(r"\theta", size + 4, C.structure).move_to(P3((a[0] + b[0]) / 2, a[1] - 0.36)),
                 tex("x", size + 4, C.space).move_to(P3(a[0] - 0.34, (a[1] + b[1]) / 2)))
    return VGroup(frame, lab)


def sine_arch(o=None, sx: float = RSX, sy: float = RSY, width: float = 4.5):
    """x = sin θ over the rectangle (C.change)."""
    from manim import VMobject
    th = np.linspace(0, math.pi, 160)
    return VMobject(stroke_color=C.change, stroke_width=width).set_points_smoothly(
        [rpt(t, math.sin(t), o, sx, sy) for t in th])


def arch_region(o=None, sx: float = RSX, sy: float = RSY, opacity: float = 0.3):
    from manim import Polygon
    th = np.linspace(0, math.pi, 120)
    return Polygon(*[rpt(t, math.sin(t), o, sx, sy) for t in th], stroke_width=0, fill_color=C.change,
                   fill_opacity=opacity)


_STREAM = {}


def dot_stream():
    """The throws of the needle stream as rectangle dots: θ, x (half boards), crossed? (x ≤ sin θ), cumulative hits."""
    if not _STREAM:
        xs, th, hit = buffon(N_LOCK)
        _STREAM.update(th=th, x=2 * xs, hit=hit, H=np.concatenate([[0], np.cumsum(hit)]))
    return _STREAM


def dots_n(t: float) -> int:
    """How many throws have landed in the rectangle at time t (ch6_s03 → ch6_s04; one stream, so the cut matches)."""
    from beats import T
    ts = [float(T.ch6_s03_rectangle) + 1.0, float(T.ch6_s03_crosses), float(T.ch6_s04),
          float(T.ch6_s04_two_over_pi) + 1.5]
    g = np.interp(t, ts, [0.0, math.log10(250), math.log10(1500), math.log10(N_LOCK)])
    return 0 if t < ts[0] else int(round(10 ** g))


def draw_dots(c, cv, n: int, lit: float, o=None, sx: float = RSX, sy: float = RSY, alpha: float = 1.0):
    """The first n stream dots on skia canvas c (of Canvas cv). lit ∈ [0, 1] colors crossings pink, the rest dim."""
    sk = cv.skia
    st = dot_stream()
    n = min(n, N_LOCK)
    if n <= 0 or alpha <= 0:
        return
    o = RO if o is None else o
    r = float(np.clip(0.06 * (300 / max(n, 300)) ** 0.3, 0.022, 0.06))
    a = float(np.clip((700 / max(n, 700)) ** 0.33, 0.32, 1.0)) * alpha
    th, x, hit = st["th"][:n], st["x"][:n], st["hit"][:n]
    for mask, col, al in ((hit, mix_hex(C.text, C.uncertainty, lit), a),
                          (~hit, mix_hex(C.text, C.muted, lit), a * (1 - 0.5 * lit))):
        px = (o[0] + sx * th[mask] - cv.box[0]) * cv.px
        py = (cv.box[3] - o[1] - sy * x[mask]) * cv.px
        pts = [sk.Point(float(u), float(v)) for u, v in zip(px, py)]
        if pts:
            c.drawPoints(sk.Canvas.kPoints_PointMode, pts, cv.paint(col, al, 2 * r * cv.px))


def coin(c, phi: float, r: float = 0.42) -> VGroup:
    """A coin seen flipping about its horizontal axis by angle phi (edge-on at phi = π/2)."""
    from manim import Ellipse
    k = math.cos(phi)
    h = max(abs(k), 0.07)
    g = VGroup(Ellipse(width=2 * r, height=2 * r * h, fill_color=tint(C.circle, 0.16), fill_opacity=1.0,
                       stroke_color=C.circle, stroke_width=3).move_to(c))
    if h > 0.2:
        g.add(sans("H" if k > 0 else "T", 34, C.circle).stretch(h, 1).move_to(c))
    return g


def lower_third(s: str, c, width: float = 4.2, size: float = 32) -> VGroup:
    from manim import Line as _L
    lt = VGroup(caps(s, size, C.text), _L(ORIGIN, RIGHT * width, stroke_color=C.muted, stroke_width=1.4))
    return lt.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(c, aligned_edge=LEFT)


# ------------------------------------------------------------------------------------------- archival images
def plate(s, layer, name: str, pos, height: float, at: float, until: float, color=None, caption: str | None = None,
          z: float = 0.5):
    """An archival image (assets/ext/<name>.png, public domain, credits in assets/ext/SOURCES.md) in a thin frame of
    `color`: the frame draws and the picture fades in landing on `at`; both fade out landing on `until`. An optional
    CM sans caption sits under the frame. Returns the frame group.

    Example:
        plate(s, m, "euler", (2.9, -0.6), 2.6, t_eu + 0.2, t_sw - 1.0, C.structure)
    """
    from pathlib import Path

    from PIL import Image
    from manim import Create, FadeIn, FadeOut, Rectangle

    path = Path(__file__).resolve().parent / "assets" / "ext" / f"{name}.png"
    w0, h0 = Image.open(path).size
    w = height * w0 / h0
    s.image(str(path), height=height, pos=tuple(pos), z=z, opacity=fade(at, dur=0.6, out=until, out_dur=0.5))
    fr = VGroup(Rectangle(width=w + 0.1, height=height + 0.1, stroke_color=color or C.muted, stroke_width=2.2)
                .move_to(P3(*pos)))
    layer.play(Create(fr[0]), at=at - 0.5, dur=0.6)
    if caption:
        cap = sans(caption, 24, C.muted).next_to(fr[0], DOWN, buff=0.14)
        fr.add(cap)
        layer.play(FadeIn(cap), at=at - 0.2, dur=0.4)
    layer.play(FadeOut(fr), at=until - 0.5, dur=0.5)
    return fr


# --------------------------------------------------------------------------------------------- wood floor
def wood_floor(lines_y, box=FL_BOX, seed: int = 1777, px: float = PX) -> tuple[np.ndarray, dict]:
    """The wooden floor of Buffon's needles, drawn once with skia: boards between the cracks at `lines_y` (dark warm
    brown, two alternating tones, faint grain and staggered end joints) and each crack a dark gap. Returns the RGBA
    array and the layer placement (`ArrayLayer(rgba, **kw)`).

    Example:
        rgba, kw = wood_floor(full_floor(10)[4])
        s.add(ArrayLayer(rgba, z=-5, opacity=fade(T.start), **kw))
    """
    cv = Canvas(box, px)
    sk = cv.skia
    c = cv.begin()
    rg = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    ys = [y0] + [float(y) for y in lines_y if y0 < y < y1] + [y1]
    tones = (tint(C.change, 0.026), tint(C.change, 0.033))
    for k, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        r, g, b = rgb255(tones[k % 2])
        fill = sk.Paint(AntiAlias=True, Color=sk.Color(r, g, b, 255))
        (ax, ay), (bx, by) = cv.T(x0, yb), cv.T(x1, ya)
        c.drawRect(sk.Rect.MakeLTRB(ax, ay, bx, by), fill)
        grain = cv.paint(tint(C.change, 0.06), 0.55, 1.1)
        for _ in range(5):                                  # grain: long, gently wavy lines along the board
            yy = rg.uniform(ya + 0.08, yb - 0.08)
            amp, ph, fr = rg.uniform(0.01, 0.035), rg.uniform(0, 6.3), rg.uniform(0.25, 0.6)
            xs = np.linspace(x0, x1, 120)
            pts = [sk.Point(*cv.T(x, yy + amp * math.sin(fr * x + ph))) for x in xs]
            path = sk.Path()
            path.addPoly(pts, False)
            c.drawPath(path, grain)
        joint = cv.paint(C.bg, 0.9, 2.0)                    # end joints, staggered board to board
        xj = rg.uniform(x0, x0 + 4.0)
        while xj < x1:
            c.drawLine(*cv.T(xj, ya), *cv.T(xj, yb), joint)
            xj += rg.uniform(3.5, 6.0)
    gap = cv.paint(C.bg, 1.0, 3.2)
    for y in ys[1:-1]:
        c.drawLine(*cv.T(x0, y), *cv.T(x1, y), gap)
    return cv.array(), cv.layer_kw()


def glow_layer(s, z: float, color=None, k: float = 1.0, radius=None, **kw):
    """A Manim layer whose shapes carry the accent glow (C.glow) in `color`: use it for lit elements only.

    Example:
        lit = glow_layer(s, z=1, color=C.change)
        lit.play(Create(curve), at=T.x)
    """
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=radius or C.glow_r)], **kw)


def glow_fx(color=None, k: float = 1.0, radius=None):
    """The accent glow as an fx list for raster layers: `ArrayLayer(..., fx=glow_fx(C.change))`."""
    return [Glow(color, strength=C.glow * k, radius=radius or C.glow_r)]


class StickPainter:
    """Draws Buffon's sticks as real wooden sticks on a skia `Canvas`: soft shadow, birch body with a lit and a
    shaded edge, darker end grain. `hit` (0..1) blushes the body toward C.uncertainty; `lift` (0..1) raises it off the
    floor (shadow drifts off and blurs).

    Example:
        sp = StickPainter(cv)
        c = cv.begin(); sp.stick(c, x, y, angle, length, hit=1.0, alpha=1.0); cv.array()
    """

    def __init__(self, cv: "Canvas", width: float = 7.0):
        self.cv, self.sk, self.W = cv, cv.skia, width
        self.body = mix_hex(C.text, C.change, 0.32)
        self._tones = {}
        self._shadow = self._stroke(C.bg, 0.5, width + 1.0, self.sk.Paint.kRound_Cap, 1.6)

    def tones(self, hit: float):
        key = round(float(hit), 2)
        if key not in self._tones:
            b = mix_hex(self.body, C.uncertainty, 0.78 * key)
            self._tones[key] = (b, mix_hex(b, C.text, 0.55), mix_hex(b, C.bg, 0.38), mix_hex(b, C.bg, 0.55))
        return self._tones[key]

    def _stroke(self, color, a, w, cap=None, blur=0.0):
        sk = self.sk
        p = self.cv.paint(color, a, w)
        p.setStrokeCap(cap if cap is not None else sk.Paint.kButt_Cap)
        if blur > 0:
            p.setMaskFilter(sk.MaskFilter.MakeBlur(sk.kNormal_BlurStyle, blur))
        return p

    def stick(self, c, x, y, a, ln, hit=0.0, alpha=1.0, lift=0.0, w=None):
        if alpha <= 0.01:
            return
        sk, cv = self.sk, self.cv
        w = self.W if w is None else w
        X, Y = cv.T(x, y)
        h = 0.5 * ln * cv.px
        dx, dy = h * math.cos(a), -h * math.sin(a)
        nx, ny = -dy / max(h, 1e-6), dx / max(h, 1e-6)
        body, lite, dark, grain = self.tones(hit)
        ox, oy = 3.0 + 26.0 * lift, 4.0 + 34.0 * lift
        sh = self._shadow if lift <= 0 else self._stroke(C.bg, 0.5, w + 1.0, sk.Paint.kRound_Cap, 1.6 + 7.0 * lift)
        sh.setAlphaf(0.5 * (1 - 0.5 * lift) * alpha)
        c.drawLine(X - dx + ox, Y - dy + oy, X + dx + ox, Y + dy + oy, sh)
        c.drawLine(X - dx, Y - dy, X + dx, Y + dy, self._stroke(body, alpha, w))
        o = 0.27 * w
        c.drawLine(X - dx - nx * o, Y - dy - ny * o, X + dx - nx * o, Y + dy - ny * o,
                   self._stroke(lite, 0.75 * alpha, 0.3 * w))
        c.drawLine(X - dx + nx * o, Y - dy + ny * o, X + dx + nx * o, Y + dy + ny * o,
                   self._stroke(dark, 0.8 * alpha, 0.3 * w))
        e = min(0.9 * w, 0.2 * h) / max(h, 1e-6)
        for sgn in (-1, 1):
            c.drawLine(X + sgn * dx, Y + sgn * dy, X + sgn * dx * (1 - e), Y + sgn * dy * (1 - e),
                       self._stroke(grain, alpha, w))
