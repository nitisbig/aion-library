"""BendGauge: the recurring "bending meter" icon of video 002.

A short arc that smiles (blue) when the bending k > 0, frowns (orange) when k < 0
and lies flat (grey) at 0. Its curvature grows with |k|, so one icon carries the
sign and the size of a second derivative.

    k = ValueTracker(2)
    g = BendGauge(k, readout=True).place(RIGHT * 3)
    self.add(g)
    self.play(k.animate.set_value(-1))      # smile → flat → frown, readout follows
"""

from __future__ import annotations

import numpy as np
from manim import (DOWN, ORIGIN, DecimalNumber, ManimColor, ValueTracker, VGroup, VMobject,
                   interpolate_color)

from .. import style as S


def bend_color(k: float, full: float = 0.6):
    """Grey at 0, blending to SMILE (k > 0) or FROWN (k < 0) by |k| = full."""
    t = min(abs(k) / full, 1.0)
    return interpolate_color(ManimColor(S.FLAT), ManimColor(S.SMILE if k > 0 else S.FROWN), t)


class BendGauge(VGroup):
    def __init__(self, k: ValueTracker | float, *, width: float = 1.1, gain: float = 0.22,
                 max_c: float = 0.75, stroke: float = 7, readout: bool = False,
                 decimals: int = 0, font_size: float = 34, center=ORIGIN):
        super().__init__()
        self.k = k if isinstance(k, ValueTracker) else ValueTracker(k)
        self.span, self.gain, self.max_c, self.stroke = width, gain, max_c, stroke
        self.center_pt = np.array(center, float)
        self.glow = VMobject()
        self.arc = VMobject()
        self.add(self.glow, self.arc)
        self.readout = None
        if readout:
            self.readout = DecimalNumber(self.k.get_value(), num_decimal_places=decimals,
                                         font_size=font_size, include_sign=False)
            self.add(self.readout)
        self._redraw()
        self.add_updater(lambda m: m._redraw())

    def _shape(self) -> np.ndarray:
        k = self.k.get_value()
        c = float(np.clip(k * self.gain, -self.max_c, self.max_c))
        xs = np.linspace(-self.span / 2, self.span / 2, 25)
        ys = c * (xs / (self.span / 2)) ** 2 * (self.span / 2)
        ys -= (ys.max() + ys.min()) / 2                 # keep the icon centred as it flips
        return np.stack([xs, ys, np.zeros_like(xs)], 1) + self.center_pt

    def _redraw(self):
        k = self.k.get_value()
        col = bend_color(k)
        pts = self._shape()
        self.arc.set_points_smoothly(pts).set_stroke(col, self.stroke).set_fill(opacity=0)
        self.glow.set_points_smoothly(pts).set_stroke(col, self.stroke * 3.2, opacity=0.18).set_fill(opacity=0)
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
