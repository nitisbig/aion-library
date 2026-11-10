"""Raster media layers: images (and, later, video clips) placed in world space."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from aion.gpu.context import gl
from aion.layers.base import ENC_SRGB, ENC_SRGB_PREMUL, Layer, Surface

__all__ = ["ImageLayer", "ArrayLayer"]


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
