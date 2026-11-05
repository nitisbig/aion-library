"""BendGauge: the recurring "bending meter" icon of video 002.

A curvature glyph: an arc that smiles (blue) when the bending k > 0, frowns (orange)
when k < 0 and lies flat (grey) at 0, drawn against its flat tangent and filled like
a bowl (holds) or a dome (sheds). One icon carries the sign and the size of a
second derivative.

    k = ValueTracker(2)
    g = BendGauge(k, readout=True).place(RIGHT * 3)
    self.add(g)
    self.play(k.animate.set_value(-1))      # smile → flat → frown, readout follows
"""

from __future__ import annotations

import numpy as np
from manim import (DOWN, ORIGIN, UP, DecimalNumber, ManimColor, ValueTracker, VGroup, VMobject,
                   interpolate_color)

from .. import style as S


def bend_color(k: float, full: float = 0.6):
    """Grey at 0, blending to SMILE (k > 0) or FROWN (k < 0) by |k| = full."""
    t = min(abs(k) / full, 1.0)
    return interpolate_color(ManimColor(S.FLAT), ManimColor(S.SMILE if k > 0 else S.FROWN), t)


class BendGauge(VGroup):
    """A curvature glyph: the bend itself with a gradient stroke, the flat tangent it bends
    away from, a dot at the vertex, and the bend filled like a liquid: a blue bowl for
    k > 0 (it holds: a valley), an orange dome for k < 0 (it sheds: a peak), nothing at 0."""

    def __init__(self, k: ValueTracker | float, *, width: float = 1.1, gain: float = 0.22,
                 max_c: float = 0.75, stroke: float = 7, readout: bool = False,
                 decimals: int = 0, font_size: float = 34, center=ORIGIN):
        super().__init__()
        self.k = k if isinstance(k, ValueTracker) else ValueTracker(k)
        self.span, self.gain, self.max_c, self.stroke = width, gain, max_c, stroke
        self.center_pt = np.array(center, float)
        self.ref = VMobject()          # the flat tangent at the vertex (dashed look via short pieces)
        self.circle = VMobject()       # the liquid fill (bowl / dome)
        self.arc = VMobject()          # the bend
        self.dot = VMobject()          # the vertex
        self.glow = VMobject()         # kept for API compatibility (unused)
        self.add(self.ref, self.circle, self.arc, self.dot)
        self.readout = None
        if readout:
            self.readout = DecimalNumber(self.k.get_value(), num_decimal_places=decimals,
                                         font_size=font_size, include_sign=False)
            self.add(self.readout)
        self._redraw()
        self.add_updater(lambda m: m._redraw())

    def _c(self) -> float:
        return float(np.clip(self.k.get_value() * self.gain, -self.max_c, self.max_c))

    def _shape(self) -> np.ndarray:
        c = self._c()
        xs = np.linspace(-self.span / 2, self.span / 2, 33)
        ys = c * (xs / (self.span / 2)) ** 2 * (self.span / 2)
        ys -= (ys.max() + ys.min()) / 2                 # keep the icon centred as it flips
        return np.stack([xs, ys, np.zeros_like(xs)], 1) + self.center_pt

    def _redraw(self):
        k, c, s = self.k.get_value(), self._c(), self.span
        col = bend_color(k)
        dim = interpolate_color(ManimColor("#000000"), col, 0.45)
        pts = self._shape()
        w = max(self.stroke * 0.5, 2.0)
        self.arc.set_points_smoothly(pts).set_stroke([dim, col, dim], w).set_fill(opacity=0)
        vertex = self.center_pt + np.array([0.0, -c * s / 4, 0.0])
        # flat tangent through the vertex: a row of short dashes
        segs = []
        n = 7
        for i in range(n):
            a = -0.62 * s + (i + 0.2) * (1.24 * s / n)
            b = a + 0.6 * (1.24 * s / n)
            segs += [vertex + np.array([a, 0, 0]), vertex + np.array([b, 0, 0])]
        self.ref.clear_points()
        for i in range(0, len(segs), 2):
            self.ref.start_new_path(segs[i])
            self.ref.add_line_to(segs[i + 1])
        self.ref.set_stroke(S.FLAT, 1.3, opacity=0.55).set_fill(opacity=0)
        # the bend filled like a liquid: a smile is a bowl that holds (blue), a frown a dome
        # that sheds (orange); the fill is bounded by the arc and its chord, so it never
        # leaves the icon's box, and it grows with |k|
        if abs(c) > 1e-3:
            shape = np.vstack([pts, pts[:1]])
            deep = interpolate_color(ManimColor("#000000"), col, 0.25)
            self.circle.set_points_as_corners(shape).set_stroke(width=0)
            self.circle.set_fill([col, deep] if c > 0 else [deep, col], opacity=0.42)
            self.circle.set_sheen_direction(DOWN if c > 0 else UP)
        else:
            self.circle.set_points_as_corners([vertex, vertex]).set_stroke(width=0).set_fill(opacity=0)
        r = 0.045 if s >= 0.8 else 0.035
        t = np.linspace(0, 2 * np.pi, 17)
        self.dot.set_points_smoothly(np.stack([vertex[0] + r * np.cos(t), vertex[1] + r * np.sin(t), 0 * t], 1))
        self.dot.set_fill(col, 1.0).set_stroke(width=0)
        if self.readout is not None:
            self.readout.set_value(k)
            self.readout.set_color(col)
            self.readout.next_to(self.center_pt + DOWN * 0.18, DOWN, buff=0.12)
        return self

    def place(self, point) -> "BendGauge":
        """Move the gauge (use this, not move_to/shift: the updater redraws from its centre)."""
        self.center_pt = np.array(point, float)
        self._redraw()
        return self

    def get_center(self):
        return self.center_pt.copy()


class TwistGauge(VGroup):
    """The twist icon: a strip that turns about its own axis along its length.

    k = 1 is a half twist: face-on (bright front) at the left end, edge-on in the middle,
    back face (darker) at the right end. The turn scales with k; k = 0 is a flat grey strip.
    Static: rebuild it to change k. Moves like any VGroup.
    """

    def __init__(self, k: float, *, width: float = 1.1, height: float = 0.42, gain: float = np.pi,
                 max_turn: float = np.pi, n: int = 36, center=ORIGIN):
        super().__init__()
        from manim import Polygon
        turn = float(np.clip(k * gain, -max_turn, max_turn))
        col = interpolate_color(ManimColor(S.FLAT), ManimColor(S.TWIST), min(abs(k) / 0.6, 1.0))
        back = interpolate_color(ManimColor("#000000"), col, 0.55)
        s = np.linspace(0, 1, n + 1)
        phi = s * turn
        xs = (s - 0.5) * width
        h = height / 2
        top = np.stack([xs + 0.45 * h * np.sin(phi), h * np.cos(phi), 0 * s], 1)
        bot = np.stack([xs - 0.45 * h * np.sin(phi), -h * np.cos(phi), 0 * s], 1)
        faces = VGroup()
        for i in range(n):
            c = np.cos((phi[i] + phi[i + 1]) / 2)
            fc, fa = (col if c >= 0 else back), 0.25 + 0.6 * abs(c)
            faces.add(Polygon(top[i], top[i + 1], bot[i + 1], bot[i])
                      .set_fill(fc, fa).set_stroke(fc, 1.2, opacity=fa))   # stroke closes AA seams
        edges = VGroup(VMobject().set_points_smoothly(top), VMobject().set_points_smoothly(bot))
        edges.set_stroke(col, 3).set_fill(opacity=0)
        self.add(faces, edges)
        self.move_to(center)
