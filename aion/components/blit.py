"""Fast compositing for GPU plates (ShaderPlate, SurfacePlate).

Manim's Cairo camera draws every ImageMobject through PIL's affine `transform`,
which costs ~600 ms per full 1080p frame on this machine. GPU plates are already
rendered at exactly the on-screen pixel size, so when a plate is axis-aligned and
its pixel size matches its on-screen rectangle, it is copied (or alpha-composited)
straight into the frame buffer with numpy instead: about 5 ms.

Anything else (rotated, zoomed by a MovingCamera, resized) falls back to Manim's
own path, so the result is always correct, only the speed differs.

Mark a mobject with `mob._fast_blit = True` to opt in; `mob._blit_add = True` adds
its (premultiplied) pixels onto the frame instead of replacing them. `install()` is idempotent.
"""

from __future__ import annotations

import numpy as np
from manim import Camera

_ORIG = Camera.display_image_mobject
UNDERLAY = False      # True while a backdrop is on: opaque plates are added onto it, not copied over it


def _blit(camera: Camera, mob, pixel_array: np.ndarray) -> bool:
    img = mob.pixel_array
    ih, iw = img.shape[:2]
    corners = camera.points_to_pixel_coords(mob, mob.points)
    ul, ur, dl = corners[0], corners[1], corners[2]
    w, h = ur[0] - ul[0], dl[1] - ul[1]
    if ur[1] != ul[1] or dl[0] != ul[0] or abs(w - iw) > 1 or abs(h - ih) > 1:
        return False
    x0, y0 = int(ul[0]), int(ul[1])
    H, W = pixel_array.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + iw), min(H, y0 + ih)
    if dx1 <= dx0 or dy1 <= dy0:
        return True
    src = img[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
    dst = pixel_array[dy0:dy1, dx0:dx1]
    a = src[..., 3]
    if getattr(mob, "_blit_add", False):           # premultiplied-on-black plate, fading
        dst[..., :3] = np.minimum(dst[..., :3].astype(np.uint16) + src[..., :3], 255)
        dst[..., 3] = 255
    elif a.min() == 255 and UNDERLAY:              # opaque plate on black over a live backdrop:
        cover = getattr(mob, "_cover", None)       # the surface hides it, the black stage shows it
        if cover is not None and cover.shape == img.shape[:2]:
            c = cover[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0), None].astype(np.uint16)
            under = dst[..., :3].astype(np.uint16) * (255 - c) // 255
            dst[..., :3] = np.minimum(under + src[..., :3], 255)
        else:
            dst[..., :3] = np.minimum(dst[..., :3].astype(np.uint16) + src[..., :3], 255)
        dst[..., 3] = 255
    elif a.min() == 255:
        dst[...] = src
    else:
        af = a[..., None].astype(np.uint16)
        dst[..., :3] = ((src[..., :3] * af + dst[..., :3] * (255 - af)) // 255).astype(np.uint8)
        dst[..., 3] = np.maximum(dst[..., 3], a)
    return True


def _display_image_mobject(self, image_mobject, pixel_array):
    if getattr(image_mobject, "_fast_blit", False) and _blit(self, image_mobject, pixel_array):
        return
    _ORIG(self, image_mobject, pixel_array)


def install() -> None:
    Camera.display_image_mobject = _display_image_mobject
