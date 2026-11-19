"""Documentary plates for the cold open: real images, graded, moved by a virtual camera with depth parallax.

A Shot is one image on screen from t0 to t1. Its camera is a list of keys (t, u, v, zoom), where (u, v) is the point of
the image at the center of the frame. Every frame is a pure function of absolute audio time.
"""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

PHOTOS = Path(__file__).parent / "assets" / "photos"
OUT_W, OUT_H = 1920, 1080
ASPECT = OUT_W / OUT_H
FRAME_W, FRAME_H = 64 / 4.5, 8.0
_GX, _GY = np.meshgrid(np.arange(OUT_W, dtype=np.float32) - OUT_W / 2 + 0.5, np.arange(OUT_H, dtype=np.float32) - OUT_H / 2 + 0.5)
_SCRIM = np.clip(0.42 + 0.58 * (1 - (np.linspace(0, 1, OUT_H, dtype=np.float32) - 0.62) / 0.38), 0.42, 1.0)[:, None, None]


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def _luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def _photo(name, sat=0.9, contrast=1.14, warm=0.03, gain=1.0):
    im = Image.open(PHOTOS / f"{name}.jpg").convert("RGB")
    im.thumbnail((2880, 2880), Image.LANCZOS)
    a = np.asarray(im, dtype=np.float32) / 255
    y = _luma(a)[..., None]
    a = y + (a - y) * sat
    a = np.clip(0.5 + (a - 0.5) * contrast, 0, 1) * gain
    return np.clip(a * np.array([1 + warm, 1.0, 1 - warm], dtype=np.float32), 0, 1)


def _print(name, box=None, scale=1):
    """An engraving: enlarged, its lines tightened, printed in warm ink on parchment."""
    im = Image.open(PHOTOS / f"{name}.jpg").convert("L")
    if box:
        w, h = im.size
        im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    if scale > 1:
        im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS).filter(ImageFilter.GaussianBlur(scale * 0.2))
    im.thumbnail((2880, 2880), Image.LANCZOS)
    y = np.asarray(im, dtype=np.float32) / 255
    y = smooth((y - 0.1) / 0.8)[..., None]
    ink, paper = np.array([0.045, 0.032, 0.026], dtype=np.float32), np.array([0.86, 0.77, 0.61], dtype=np.float32)
    return ink + (paper - ink) * y


def _depth_painting(a):
    """Near = the dark masses at the sides of the painting; far = the bright sky and water at its center."""
    h, w = a.shape[:2]
    im = Image.fromarray((_luma(a) * 255).astype(np.uint8)).resize((w // 2, h // 2)).filter(ImageFilter.GaussianBlur(w / 110))
    dark = 1 - np.asarray(im, dtype=np.float32) / 255
    u, v = np.meshgrid(np.linspace(0, 1, w // 2), np.linspace(0, 1, h // 2))
    d = 0.6 * dark + 0.28 * np.abs(u - 0.5) * 2 + 0.22 * v
    return ((d - d.min()) / (d.max() - d.min())).astype(np.float32)


def _depth_aerial(a):
    """Near = the bottom of a view taken from a hillside."""
    h, w = a.shape[:2]
    v = np.linspace(0, 1, h // 2, dtype=np.float32)[:, None]
    return np.repeat(v**1.3, w // 2, axis=1)


LOADERS = {
    "med": lambda: (_photo("med", sat=0.95, contrast=1.22, warm=0.0, gain=0.92), None),
    "traders": lambda: (_print("traders", box=(0.02, 0.02, 0.98, 0.97)), None),
    "turner": lambda: ((a := _photo("turner", sat=1.0, contrast=1.16, warm=0.02)), _depth_painting(a)),
    "iss": lambda: (_photo("iss", sat=1.22, contrast=1.38, warm=-0.01, gain=0.98), None),
    "harbor": lambda: ((a := _photo("harbor", sat=0.92, contrast=1.12, warm=0.03)), _depth_aerial(a)),
    "merian": lambda: (_print("merian", box=(0.03, 0.04, 0.97, 0.90), scale=5), None),
}
_CACHE = {}


def plate(name):
    if name not in _CACHE:
        _CACHE[name] = LOADERS[name]()
    return _CACHE[name]


@dataclass
class Shot:
    name: str
    t0: float
    t1: float
    keys: list
    fade: float = 0.4
    parallax: float = 0.0
    size: tuple = field(default=None)

    def window(self, t):
        """(cx, cy, wu, wv): the part of the image in frame at time t, in image coordinates."""
        k = self.keys
        ts = [q[0] for q in k]
        i = int(np.clip(np.searchsorted(ts, t) - 1, 0, len(k) - 2))
        s = float(smooth((t - k[i][0]) / max(k[i + 1][0] - k[i][0], 1e-6)))
        cu, cv = k[i][1] + (k[i + 1][1] - k[i][1]) * s, k[i][2] + (k[i + 1][2] - k[i][2]) * s
        z = float(np.exp(np.log(k[i][3]) + (np.log(k[i + 1][3]) - np.log(k[i][3])) * s))
        h, w = plate(self.name)[0].shape[:2]
        a = w / h
        wu, wv = (ASPECT / a, 1.0) if a >= ASPECT else (1.0, a / ASPECT)
        wu, wv = wu / z, wv / z
        return float(np.clip(cu, wu / 2, 1 - wu / 2)), float(np.clip(cv, wv / 2, 1 - wv / 2)), wu, wv

    def screen(self, u, v, t):
        """Where image point (u, v) falls on screen, in scene units."""
        cx, cy, wu, wv = self.window(t)
        return [(u - cx) / wu * FRAME_W, -(v - cy) / wv * FRAME_H, 0.0]

    def render(self, t):
        src, depth = plate(self.name)
        h, w = src.shape[:2]
        cx, cy, wu, wv = self.window(t)
        sx, sy = wu * w / OUT_W, wv * h / OUT_H
        mx, my = cx * w + _GX * sx, cy * h + _GY * sy
        if depth is not None and self.parallax:
            d = depth[np.clip((my / 2).astype(np.int32), 0, depth.shape[0] - 1), np.clip((mx / 2).astype(np.int32), 0, depth.shape[1] - 1)] - 0.5
            p = (float(smooth((t - self.t0) / (self.t1 - self.t0))) - 0.5) * self.parallax * w
            mx, my = mx + d * p, my + d * p * 0.12
        mx, my = np.clip(mx, 0, w - 1.001), np.clip(my, 0, h - 1.001)
        x0, y0 = mx.astype(np.int32), my.astype(np.int32)
        fx, fy = (mx - x0)[..., None], (my - y0)[..., None]
        top = src[y0, x0] * (1 - fx) + src[y0, x0 + 1] * fx
        low = src[y0 + 1, x0] * (1 - fx) + src[y0 + 1, x0 + 1] * fx
        return top * (1 - fy) + low * fy


def film(shots, bars):
    """frame(t) for a FramesLayer: cross-dissolved shots, a soft lower scrim for captions and cinema bars."""

    def frame(t):
        live = [(q, float(smooth((t - q.t0) / q.fade))) for q in shots if q.t0 <= t < q.t1]
        for i in range(len(live) - 1, -1, -1):
            if live[i][1] >= 1.0:
                live = live[i:]
                break
        out = np.zeros((OUT_H, OUT_W, 3), dtype=np.float32)
        for q, a in live:
            out = q.render(t) if a >= 1.0 else out * (1 - a) + q.render(t) * a
        out = out * _SCRIM
        b = int(round(float(bars(t)) * OUT_H))
        if b > 0:
            out[:b] = 0
            out[-b:] = 0
        rgba = np.empty((OUT_H, OUT_W, 4), dtype=np.uint8)
        rgba[..., :3] = (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)
        rgba[..., 3] = 255
        return rgba
    return frame
