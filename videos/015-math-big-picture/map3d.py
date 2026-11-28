"""The upgraded Map of Math and THE circle for video 015, seen through a real perspective camera.

The map lives on a plane in 3D (x, y on the plane, z up). A `View` (pitch, yaw, distance) projects it to the screen:
pitch 0 is the flat top-down 2D map, ~35° a 2.5D tilt, ~60° with yaw a full 3D view. Everything is a pure function of
its arguments, so a scene keys the view per frame (`m.redraw(lambda t: atlas(..., view=View(pitch=track(t))))`).

Pieces (back-to-front by depth):
  base     a faint polar grid disc under the ring (radial spokes and rings, C.map_off) that grounds the 3D view
  track    the ring of the map as a dashed double track with 60 ticks, six major
  chords   lit links as arches that rise off the plane (height ∝ length) in their two pillar hues
  stems    from each node down to its shadow on the plane (3D only)
  nodes    medallions: a hue ring, an inner hexagon, a tinted face, the glyph, the name (billboarded)
  hub      THE circle as a prism ring: 36 arc pieces cycling through the six pillar hues, with a hairline inner ring
           and 60 ticks (six major, at the nodes)

Example:
    v = View(pitch=math.radians(55), yaw=math.radians(20))
    m.add(atlas(turn=0, lit=PILLARS, edges=ALL_EDGES, view=v))
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from aion import C
from manim import Circle, Line, Polygon, VGroup, VMobject

from theme import GLYPHS, NAMES, PILLARS

MAP_R, NODE_R, HUB_R = 2.75, 0.4, 1.375


def _hue(p):
    return getattr(C, p)


def _rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def mix(a: str, b: str, u: float) -> str:
    c = (1 - u) * _rgb(a) + u * _rgb(b)
    return "#" + "".join(f"{int(round(v)):02X}" for v in c)


def tint(color: str, a: float) -> str:
    c = _rgb(color) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4) * a
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in srgb)


def prism(theta: float) -> str:
    """The hue at polar angle theta (radians) of the prism ring: each pillar's hue at its node, blended between."""
    a = (-math.degrees(theta) - 90) % 360 / 60.0           # node k sits at angle −90 − 60k
    k = int(a) % 6
    return mix(_hue(PILLARS[k]), _hue(PILLARS[(k + 1) % 6]), a - int(a))


@dataclass(frozen=True)
class View:
    """Perspective camera looking at the map plane. pitch: tilt from top-down (rad); yaw: spin about the vertical
    (rad); dist: eye distance (world units, larger = flatter); scale: screen scale; c: screen centre."""
    pitch: float = 0.0
    yaw: float = 0.0
    dist: float = 14.0
    scale: float = 1.0
    c: tuple = (0.0, 0.0)

    def project(self, p) -> tuple[np.ndarray, np.ndarray]:
        """World points (N×3) → screen points (N×3, z = 0) and depth (larger = farther)."""
        p = np.atleast_2d(np.asarray(p, float))
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x = cy * p[:, 0] - sy * p[:, 1]
        y = sy * p[:, 0] + cy * p[:, 1]
        z = p[:, 2]
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y2 = cp * y + sp * z                                  # screen up
        d = -sp * y + cp * z                                  # toward the eye
        k = self.dist / (self.dist - d) * self.scale
        out = np.c_[self.c[0] + k * x, self.c[1] + k * y2, np.zeros(len(p))]
        return out, -d

    def k_at(self, p) -> float:
        """The perspective scale at a world point (for sizing billboards)."""
        _, depth = self.project(p)
        return self.dist / (self.dist + depth[0]) * self.scale


FLAT = View()


def _poly(pts, color, width, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(pts)


def node_pos(k: int, turn: float = 0.0, R: float = MAP_R) -> np.ndarray:
    a = math.radians(-90 - 60 * k + turn)
    return np.array([R * math.cos(a), R * math.sin(a), 0.0])


def hero_ring(r: float = HUB_R, view: View = FLAT, c=(0.0, 0.0, 0.0), width: float = 6.0, turn: float = 0.0,
              ticks: bool = True, opacity: float = 1.0, n: int = 72) -> VGroup:
    """THE circle as a prism ring: n arc pieces in the six pillar hues (each hue at its node), a hairline inner ring
    and 60 ticks, six major. Drawn on the map plane through `view`."""
    c = np.asarray(c, float)
    g = VGroup()
    th = np.linspace(0, 2 * math.pi, n + 1)
    for a0, a1 in zip(th[:-1], th[1:]):
        aa = np.linspace(a0, a1, 4)
        pts = c + np.c_[r * np.cos(aa), r * np.sin(aa), np.zeros(4)]
        sp, _ = view.project(pts)
        g.add(_poly(sp, prism((a0 + a1) / 2 - math.radians(turn)), width, opacity))
    if ticks:
        aa = np.linspace(0, 2 * math.pi, 241)
        inner = c + np.c_[(r - 0.11) * np.cos(aa), (r - 0.11) * np.sin(aa), np.zeros(241)]
        g.add(_poly(view.project(inner)[0], C.circle, 1.2, 0.55 * opacity))
        for j in range(60):
            a = math.radians(-90 + 6 * j + turn)
            major = j % 10 == 0
            l0, l1 = r + 0.07, r + (0.24 if major else 0.13)
            seg = c + np.array([[l0 * math.cos(a), l0 * math.sin(a), 0], [l1 * math.cos(a), l1 * math.sin(a), 0]])
            col = prism(a - math.radians(turn)) if major else C.circle
            g.add(_poly(view.project(seg)[0], col, 2.4 if major else 1.1, (1.0 if major else 0.45) * opacity))
    return g


def _base(view: View, R: float = MAP_R, turn: float = 0.0, opacity: float = 1.0) -> VGroup:
    g = VGroup()
    for rr in (0.7 * R, 1.22 * R):
        aa = np.linspace(0, 2 * math.pi, 161)
        g.add(_poly(view.project(np.c_[rr * np.cos(aa), rr * np.sin(aa), np.zeros(161)])[0], C.map_off, 1.0,
                    0.35 * opacity))
    for j in range(12):
        a = math.radians(-90 + 30 * j + turn)
        seg = np.array([[HUB_R * 1.15 * math.cos(a), HUB_R * 1.15 * math.sin(a), 0],
                        [1.22 * R * math.cos(a), 1.22 * R * math.sin(a), 0]])
        g.add(_poly(view.project(seg)[0], C.map_off, 0.9, 0.22 * opacity))
    return g


def _track(view: View, R: float, turn: float, opacity: float) -> VGroup:
    g = VGroup()
    for rr, w, op in ((R - 0.07, 1.4, 0.55), (R + 0.07, 1.4, 0.55)):
        aa = np.linspace(0, 2 * math.pi, 241)
        g.add(_poly(view.project(np.c_[rr * np.cos(aa), rr * np.sin(aa), np.zeros(241)])[0], C.map_off, w,
                    op * opacity))
    for j in range(72):                                    # dashes between the rails
        a0 = math.radians(-90 + 5 * j + turn + 1.0)
        a1 = a0 + math.radians(2.6)
        aa = np.linspace(a0, a1, 3)
        g.add(_poly(view.project(np.c_[R * np.cos(aa), R * np.sin(aa), np.zeros(3)])[0], C.map_off, 2.2,
                    0.5 * opacity))
    return g


def arch(i: int, j: int, view: View, turn: float = 0.0, R: float = MAP_R, rise: float = 0.32, n: int = 40,
         width: float = 3.0, opacity: float = 1.0, u: float = 1.0, bow: float = 0.06):
    """The lit link between nodes i and j: an arch over the plane (height ∝ its length), shaded from one pillar hue
    to the other in pieces. u ∈ [0, 1] draws it partly (for Create-like reveals). Returns (VGroup, mean depth)."""
    a, b = node_pos(i, turn, R), node_pos(j, turn, R)
    L = np.linalg.norm(b - a)
    s = np.linspace(0, max(u, 1e-3), n)
    pts = a[None] * (1 - s[:, None]) + b[None] * s[:, None]
    mid = (a + b) / 2
    bv = -mid / (np.linalg.norm(mid) + 1e-9) * bow * L if np.linalg.norm(mid) > 1e-3 else np.zeros(3)
    pts = pts + np.outer(4 * s * (1 - s), bv)            # a slight bow toward the centre in the plane
    pts[:, 2] = rise * L * 4 * s * (1 - s)
    sp, depth = view.project(pts)
    ci, cj = _hue(PILLARS[i]), _hue(PILLARS[j])
    g = VGroup()
    m = 8
    idx = np.linspace(0, n - 1, m + 1).astype(int)
    for q in range(m):
        seg = sp[idx[q]:idx[q + 1] + 1]
        g.add(_poly(seg, mix(ci, cj, (q + 0.5) / m), width, opacity))
    return g, float(depth.mean())


def medallion(k: int, view: View, turn: float = 0.0, lit: bool = True, glyph: bool = True, label: bool = True,
              lift: float = 0.0, opacity: float = 1.0, R: float = MAP_R):
    """Node k as a medallion: a hue ring, an inner hexagon, a tinted face, the glyph and the name. `lift` raises it
    off the plane on a stem (3D). Returns (VGroup, depth)."""
    from manim import MathTex, Tex
    p = PILLARS[k]
    col = _hue(p) if lit else C.map_off
    base = node_pos(k, turn, R)
    top = base + np.array([0, 0, lift])
    (sc,), (dp,) = view.project(top[None])
    kk = view.k_at(top)
    rr = NODE_R * kk
    flat = math.cos(view.pitch) * 0.35 + 0.65              # medallions tip slightly with the view
    g = VGroup()
    if lift > 0.01:
        sb, _ = view.project(np.array([base, top]))
        g.add(_poly(sb, col, 1.6, 0.6 * opacity))
        shadow = Circle(radius=rr * 0.7, stroke_width=1.2, stroke_color=col, stroke_opacity=0.45 * opacity)
        shadow.stretch(math.cos(view.pitch), 1).move_to(sb[0])
        g.add(shadow)
    face = Circle(radius=rr, fill_color=tint(col, 0.16 if lit else 0.0) if lit else C.bg, fill_opacity=opacity,
                  stroke_color=col, stroke_width=3.2 if lit else 2.0, stroke_opacity=opacity)
    outer = Circle(radius=rr * 1.22, stroke_color=col, stroke_width=1.2, stroke_opacity=(0.7 if lit else 0.4) * opacity)
    hexa = Polygon(*[np.array([rr * 0.78 * math.cos(math.pi / 6 + q * math.pi / 3),
                               rr * 0.78 * math.sin(math.pi / 6 + q * math.pi / 3), 0]) for q in range(6)],
                   stroke_color=col, stroke_width=1.2, stroke_opacity=(0.55 if lit else 0.3) * opacity, fill_opacity=0)
    for mob in (face, outer, hexa):
        mob.stretch(flat, 1).move_to(sc)
        g.add(mob)
    if lit and glyph:
        gl = MathTex(GLYPHS[p], font_size=44 * kk, color=col)
        if gl.width > 1.4 * rr:
            gl.scale_to_fit_width(1.4 * rr)
        g.add(gl.move_to(sc).set_opacity(opacity))
    if lit and label:
        lab = Tex(r"\textsc{" + NAMES[p] + "}", font_size=32, color=col).set_opacity(opacity)
        a = math.radians(-90 - 60 * k + turn) + view.yaw
        d = np.array([math.cos(a), math.sin(a) * math.cos(view.pitch) + 0.0, 0])
        d = d / (np.linalg.norm(d) + 1e-9)
        if abs(d[1]) > 0.9:
            lab.next_to(sc, np.array([1, 0, 0]), buff=rr * 1.3)
            lab.shift(np.array([0, 0.55 * rr * np.sign(d[1]), 0]))
        else:
            lab.next_to(sc + np.array([np.sign(d[0]) * rr * 1.25, 0, 0]), np.array([np.sign(d[0]), 0, 0]), buff=0.12)
        g.add(lab)
    return g, dp


def atlas(turn: float = 0.0, lit=(), edges=(), view: View = FLAT, hub: bool = True, base: bool = True,
          lift: float | None = None, opacity: float = 1.0, edge_u: dict | None = None, R: float = MAP_R,
          rise: float | None = None) -> VGroup:
    """The whole map through `view`: base disc, track, lit chords as arches, nodes as medallions, the prism hub.

    lit: pillar names lit. edges: (p, q) name pairs drawn as arches (others are not drawn: the track carries the
    unlit structure). lift: node height (default rises with pitch). edge_u: {pair: u} to draw some arches partly.
    """
    if lift is None:
        lift = 0.55 * math.sin(view.pitch)
    if rise is None:
        rise = 0.32 - 0.14 * min(view.pitch / math.radians(55), 1.0)   # flatter arches as the camera tips
    items = []                                              # (depth, mobject)
    if base:
        items.append((1e6, _base(view, R, turn, opacity)))
    items.append((1e5, _track(view, R, turn, opacity)))
    for e in edges:
        i, j = sorted(PILLARS.index(x) for x in e)
        u = 1.0 if edge_u is None else edge_u.get(tuple(e), edge_u.get(tuple(reversed(e)), 1.0))
        if u <= 0:
            continue
        g, d = arch(i, j, view, turn, R, rise=rise, u=u, opacity=opacity, width=3.0)
        items.append((d, g))
    if hub:
        aa = np.linspace(0, 2 * math.pi, 97)[:-1]
        disc = view.project(np.c_[HUB_R * np.cos(aa), HUB_R * np.sin(aa), np.zeros(96)])[0]
        hub_d = view.project(np.zeros((1, 3)))[1][0] - 0.01 if view.pitch > 0.35 else -1e5   # flat: over the chords
        items.append((hub_d,
                      VGroup(Polygon(*disc, stroke_width=0, fill_color=C.bg, fill_opacity=opacity),
                             hero_ring(HUB_R, view, turn=turn, opacity=opacity))))
    for k in range(6):
        g, d = medallion(k, view, turn, lit=PILLARS[k] in lit, lift=lift, opacity=opacity, R=R)
        items.append((d - 0.5, g))
    items.sort(key=lambda x: -x[0])
    return VGroup(*(m for _, m in items))
