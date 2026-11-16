"""Raster media layers: images (and, later, video clips) placed in world space."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from aion.gpu.context import gl
from aion.layers.base import ENC_SRGB, ENC_SRGB_PREMUL, Layer, Surface

__all__ = ["ImageLayer", "ArrayLayer", "FramesLayer"]


class ArrayLayer(Layer):
    """An RGBA uint8 numpy image (sRGB, straight alpha unless premultiplied=True).

    Example:
        ArrayLayer(np_rgba, height=3, pos=(2, 0))
    """

    def __init__(self, rgba: np.ndarray, height: float = 8.0, premultiplied: bool = False, **kw):
        super().__init__(**kw)
        a = np.ascontiguousarray(rgba, dtype=np.uint8)
        if a.ndim == 3 and a.shape[2] == 3:
            a = np.concatenate([a, np.full(a.shape[:2] + (1,), 255, np.uint8)], axis=2)
        self.rgba = a
        self.height = height
        self.enc = ENC_SRGB_PREMUL if premultiplied else ENC_SRGB
        self._tex = None

    def draw(self, t, rc):
        if self._tex is None:
            import moderngl

            h, w = self.rgba.shape[:2]
            self._tex = gl().texture((w, h), 4, np.flipud(self.rgba).tobytes())
            self._tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            self._tex.build_mipmaps()
        h, w = self.rgba.shape[:2]
        return Surface(self._tex, self.enc, (self.height * w / h, self.height))


class ImageLayer(ArrayLayer):
    """An image file (PNG/JPG) placed in world space, `height` in Manim units.

    Example:
        ImageLayer("assets/images/portrait.png", height=5, pos=(-3, 0), opacity=fade(T.who))
    """

    def __init__(self, path: str | Path, height: float = 4.0, **kw):
        from PIL import Image

        img = np.asarray(Image.open(path).convert("RGBA"))
        super().__init__(img, height=height, name=kw.pop("name", Path(path).name), **kw)


class FramesLayer(Layer):
    """Animated RGBA uint8 images: `frame(t)` returns the array for time t (pyvista, skia, numpy renders).

    `frame` must be a pure function of t. It is only called again inside the `during` windows; outside them the
    last image is held for free, so pass the windows in which the picture actually moves.
    Example:
        FramesLayer(lambda t: die_rgba(spin(t)), height=4, pos=(3, 0), during=[(T.turn, T.turn + 2)])
    """

    def __init__(self, frame, height: float = 8.0, during=None, premultiplied: bool = False, **kw):
        super().__init__(**kw)
        self.frame = frame
        self.height = height
        self.during = [(float(a), float(b)) for a, b in (during or [(-math.inf, math.inf)])]
        self.enc = ENC_SRGB_PREMUL if premultiplied else ENC_SRGB
        self._tex = None
        self._shape = None

    def content_changes(self, t0: float, t1: float) -> bool:
        return any(t1 > a and t0 < b for a, b in self.during)

    def draw(self, t, rc):
        import moderngl

        a = np.ascontiguousarray(self.frame(t), dtype=np.uint8)
        if a.ndim == 3 and a.shape[2] == 3:
            a = np.concatenate([a, np.full(a.shape[:2] + (1,), 255, np.uint8)], axis=2)
        h, w = a.shape[:2]
        if self._tex is None or self._shape != a.shape:
            if self._tex is not None:
                self._tex.release()
            self._tex = gl().texture((w, h), 4)
            self._tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            self._shape = a.shape
        self._tex.write(np.flipud(a).tobytes())
        self._tex.build_mipmaps()
        return Surface(self._tex, self.enc, (self.height * w / h, self.height))
