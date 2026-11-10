"""Layer: the unit of compositing. Every layer is a pure function of absolute time.

Subclasses implement `draw(t, rc) -> Surface` and, if their content moves,
`content_changes(t0, t1)`. Shared behaviour handled here:

- visibility window `start`/`end`, `opacity` (Track), `blend` mode
- transform: `pos`, `scale`, `rotation` (Tracks, Manim units/radians)
- `parallax` against the comp camera (1 world, 0 screen-locked)
- `fx`: per-layer effects (glow, blur...), `matte` + `matte_mode`
- reuse: if nothing changed since the last frame, the last surface is reused
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from aion.core.track import Track, track

__all__ = ["Layer", "Surface", "RenderContext", "ENC_LINEAR", "ENC_SRGB_PREMUL", "ENC_SRGB"]

ENC_LINEAR, ENC_SRGB_PREMUL, ENC_SRGB = 0, 1, 2


@dataclass
class Surface:
    """A layer's pixels for one frame.

    tex: moderngl texture. enc: ENC_* colour encoding. extent: (w, h) in Manim
    units for a positioned quad, or None for a full-frame surface already in
    screen space (vector layers drawn through the camera; `screen_rot` is any
    camera roll the layer could not apply itself).

    Example:
        return Surface(rt.tex, ENC_LINEAR)      # from a custom Layer.draw()
    """

    tex: Any
    enc: int = ENC_LINEAR
    extent: tuple[float, float] | None = None
    screen_rot: float = 0.0     # residual camera roll for full-frame surfaces


@dataclass
class RenderContext:
    size: tuple[int, int]
    fps: float
    frame_units: tuple[float, float]       # Manim frame (w, h) in units
    t: float = 0.0
    frame_index: int = 0
    cam: Any = None                         # CamState
    seed: int = 0

    @property
    def aspect(self) -> float:
        return self.size[0] / self.size[1]

    def view(self, parallax: float = 1.0) -> np.ndarray:
        from aion.comp.camera import CamState

        return (self.cam or CamState()).view(parallax)


class Layer:
    """Base layer. See module docstring for shared parameters.

    Example:
        Solid("#0e1116", z=-10)
    """

    vector = False   # True: draws itself through the camera (full-frame screen-space surface)

    def __init__(self, *, z: float = 0.0, start: float = -math.inf, end: float = math.inf,
                 opacity=1.0, blend: str = "normal", fx=(), matte: "Layer | None" = None,
                 matte_mode: str = "alpha", parallax: float = 1.0, pos=(0.0, 0.0), scale=1.0,
                 rotation=0.0, name: str = ""):
        self.z, self.start, self.end = z, start, end
        self.opacity = track(opacity)
        self.blend, self.fx = blend, list(fx)
        self.matte, self.matte_mode = matte, matte_mode
        self.parallax = parallax
        self.pos, self.scale, self.rotation = track(pos), track(scale), track(rotation)
        self.name = name or type(self).__name__
        self._last: tuple[float, Any, Surface] | None = None   # (t, cam key, surface)
        self.order = 0

    # ── subclass API ─────────────────────────────────────────────────────────
    def draw(self, t: float, rc: RenderContext) -> Surface:
        raise NotImplementedError

    def content_changes(self, t0: float, t1: float) -> bool:
        """Does the drawn content (not transform/opacity) change in [t0, t1]?"""
        return False

    def tracks(self) -> list[Track]:
        return [self.opacity, self.pos, self.scale, self.rotation]

    def cache_key(self) -> Any:
        return [type(self).__name__, self.name, self.z, self.blend]

    # ── shared ───────────────────────────────────────────────────────────────
    def visible(self, t: float) -> bool:
        return self.start <= t < self.end and float(self.opacity(t)) > 1e-4

    def changes(self, t0: float, t1: float) -> bool:
        return self.content_changes(t0, t1) or any(tr.changes(t0, t1) for tr in self.tracks()) or \
            any(getattr(f, "changes", lambda a, b: True)(t0, t1) for f in self.fx)

    def surface(self, t: float, rc: RenderContext) -> Surface:
        """draw() with reuse of the previous surface when content is static."""
        cam_key = rc.cam.key() if (self.vector and rc.cam is not None) else None
        if self._last is not None:
            t_prev, cam_prev, surf = self._last
            if cam_prev == cam_key and not self.content_changes(min(t_prev, t), max(t_prev, t)):
                return surf
        surf = self.draw(t, rc)
        self._last = (t, cam_key, surf)
        return surf

    def model(self, t: float) -> np.ndarray:
        """3x3 layer→world transform (applied to quads; vector layers ignore it)."""
        px, py = np.asarray(self.pos(t), dtype=float)[:2]
        s = np.asarray(self.scale(t), dtype=float)
        sx, sy = (float(s), float(s)) if s.ndim == 0 else (float(s[0]), float(s[1]))
        r = float(self.rotation(t))
        c, n = math.cos(r), math.sin(r)
        return np.array([[c * sx, -n * sy, px], [n * sx, c * sy, py], [0, 0, 1]])

    def __repr__(self):
        return f"<{self.name} z={self.z}>"
