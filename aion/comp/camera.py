"""2.5D compositor camera: pan, zoom, rotate, shake. Pure in t.

    s.camera.push(T.stretch, zoom=1.15, dur=3)          # dolly in, landing on the beat
    s.camera.pan(T.detail, to=(2, 1), dur=1.5)
    s.camera.rotate(T.twist, 0.05)
    s.camera.shake(T.impact, amp=0.03, dur=0.5)

Layers see the camera through `parallax` (1 = world-locked, 0 = screen-locked
HUD, >1 foreground, <1 background), so depth reads without real 3D.
Vector layers (Manim, shaders) re-render through the camera, so zoom stays crisp.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from aion.core.ease import ease as _ease
from aion.core.noise import fbm1
from aion.core import time as _time

__all__ = ["Camera", "CamState"]


@dataclass(frozen=True)
class CamState:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    rot: float = 0.0

    def view(self, parallax: float = 1.0) -> np.ndarray:
        """3x3 world→screen matrix (Manim units) for a layer with this parallax."""
        z = self.zoom ** parallax
        r = self.rot * parallax
        c, s = math.cos(-r), math.sin(-r)
        tx, ty = self.x * parallax, self.y * parallax
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        S = np.diag([z, z, 1.0])
        T = np.array([[1, 0, -tx], [0, 1, -ty], [0, 0, 1]])
        return S @ R @ T

    def key(self):
        return (round(self.x, 6), round(self.y, 6), round(self.zoom, 6), round(self.rot, 6))


@dataclass
class _Move:
    t0: float
    dur: float
    target: float
    ease: object


@dataclass
class Camera:
    """Keyframed camera. Moves chain: each starts from where the previous ended.

    Example:
        s.camera.push(T.zoom, zoom=1.3, dur=2); s.camera.shake(T.hit, amp=0.03)
    """

    moves: dict[str, list[_Move]] = field(default_factory=lambda: {"x": [], "y": [], "zoom": [], "rot": []})
    base: dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "zoom": 1.0, "rot": 0.0})
    shakes: list[tuple[float, float, float, float, int]] = field(default_factory=list)

    def _add(self, ch: str, at: float, target: float, dur: float, ease, lead):
        t0 = at - (_time.LEAD if lead is None else lead)
        self.moves[ch].append(_Move(t0, dur, float(target), _ease(ease)))
        self.moves[ch].sort(key=lambda m: m.t0)
        return self

    def push(self, at: float, zoom: float, dur: float = 1.5, ease="easy_ease", lead: float | None = None):
        """Zoom to `zoom` (absolute, 1 = full frame)."""
        return self._add("zoom", at, zoom, dur, ease, lead)

    def pan(self, at: float, to: tuple[float, float], dur: float = 1.2, ease="easy_ease", lead: float | None = None):
        """Center the view on world point `to` (Manim units)."""
        self._add("x", at, to[0], dur, ease, lead)
        return self._add("y", at, to[1], dur, ease, lead)

    def rotate(self, at: float, angle: float, dur: float = 1.2, ease="easy_ease", lead: float | None = None):
        return self._add("rot", at, angle, dur, ease, lead)

    def frame(self, at: float, center: tuple[float, float], zoom: float, dur: float = 1.5, ease="easy_ease"):
        """Pan + zoom together (e.g. frame a detail)."""
        self.pan(at, center, dur, ease)
        return self.push(at, zoom, dur, ease)

    def shake(self, at: float, amp: float = 0.03, dur: float = 0.5, freq: float = 12.0, seed: int = 0):
        """Decaying handheld shake starting on the beat."""
        self.shakes.append((at, dur, amp, freq, seed))
        return self

    def _channel(self, ch: str, t: float) -> float:
        v = self.base[ch]
        for m in self.moves[ch]:
            if t <= m.t0:
                break
            u = 1.0 if m.dur <= 0 else min(1.0, (t - m.t0) / m.dur)
            v = v + (m.target - v) * float(m.ease(u))
        return v

    def at(self, t: float) -> CamState:
        x, y = self._channel("x", t), self._channel("y", t)
        for t0, dur, amp, freq, seed in self.shakes:
            if t0 <= t < t0 + dur:
                k = amp * (1 - (t - t0) / dur) ** 2
                x += k * fbm1((t - t0) * freq, seed)
                y += k * fbm1((t - t0) * freq, seed + 7919)
        return CamState(x, y, self._channel("zoom", t), self._channel("rot", t))

    def changes(self, t0: float, t1: float) -> bool:
        for ms in self.moves.values():
            if any(m.t0 < t1 and t0 < m.t0 + m.dur for m in ms):
                return True
        return any(a < t1 and t0 < a + d for a, d, *_ in self.shakes)

    @property
    def is_static(self) -> bool:
        return not any(self.moves.values()) and not self.shakes
