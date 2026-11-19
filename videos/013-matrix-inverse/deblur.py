"""The blurred die of Chapter 6, computed: the camera-shake matrix, its exact inverse, and what noise does to that inverse.

The kernel is the 49-pixel box from verify.py, centred so the picture does not drift sideways as it smears.
"""
from functools import lru_cache

import numpy as np
from PIL import Image

from aion import C
from verify import BLUR_KEEP, BLUR_LEN, REPO

KEEP = BLUR_KEEP


def _rgb(color):
    h = str(color).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


@lru_cache(maxsize=None)
def photo():
    return np.asarray(Image.open(REPO / "videos/009-what-matrices-are/assets/photo.png").convert("L"), float) / 255


def _kernel(length, n):
    k = np.zeros(n)
    k[:length] = 1 / length
    return np.roll(k, -(length - 1) // 2)


@lru_cache(maxsize=None)
def spectrum_full():
    return np.fft.fft(_kernel(BLUR_LEN, photo().shape[1]))


def _apply(img, F):
    return np.real(np.fft.ifft(np.fft.fft(img, axis=1) * F, axis=1))


def rgba(gray):
    g = (np.clip(gray, 0, 1) * 255).astype(np.uint8)
    return np.dstack([g, g, g, np.full_like(g, 255)])


@lru_cache(maxsize=32)
def smear_rgba(length):
    """The die smeared by an odd box of `length` pixels (1 = sharp)."""
    length = max(1, 2 * int(round((length - 1) / 2)) + 1)
    return rgba(_apply(photo(), np.fft.fft(_kernel(length, photo().shape[1]))) if length > 1 else photo())


@lru_cache(maxsize=None)
def noisy():
    """The blurred die plus noise of about one grey level in 255 (seed 13, as in verify.py)."""
    return _apply(photo(), spectrum_full()) + np.random.default_rng(13).normal(0, 0.004, photo().shape)


def undone(cut=0.0):
    """Undo the blur on the noisy picture, skipping every direction squeezed below `cut`."""
    K = spectrum_full()
    keep = np.abs(K) > cut
    return _apply(noisy(), np.where(keep, 1 / np.where(keep, K, 1), 0))


def _static(gray, amount):
    """Paint the damage in the colour of whatever gets forgotten."""
    err = np.abs(gray - photo())
    w = (np.clip((err - 0.12) / 0.3, 0, 1) * amount)[..., None]
    base = np.clip(gray, 0, 1)[..., None]
    rgb = np.clip((1 - w) * base + w * _rgb(C.null) * (0.35 + 0.65 * base), 0, 1)
    return np.dstack([(rgb * 255).astype(np.uint8), np.full(gray.shape, 255, np.uint8)])


@lru_cache(maxsize=48)
def buried_rgba(step, steps=30):
    """From the faintly noisy blur (step 0) to the picture buried by the exact inverse (step = steps)."""
    u = step / steps
    return _static((1 - u) * noisy() + u * undone(0.0), u)


@lru_cache(maxsize=64)
def rescue_rgba(step, steps=40):
    """The cutoff rises from nothing (step 0) to KEEP (step = steps), and the static clears."""
    u = step / steps
    return _static(undone(KEEP * u), 1 - u)


def bars(count=72):
    """How much each direction survives the blur, largest first, sampled evenly and always including the worst."""
    v = np.sort(np.abs(np.fft.rfft(_kernel(BLUR_LEN, photo().shape[1]))))[::-1]
    return v[np.linspace(0, v.size - 1, count).round().astype(int)]


def worst_stretch():
    return float(1 / np.abs(spectrum_full()).min())


def row_cells(count=13, block=8, row=94):
    """One row of the die, in wide blocks so single pixels can be seen."""
    r = photo()[row]
    start = r.size // 2 - count * block // 2
    return np.array([r[start + i * block:start + (i + 1) * block].mean() for i in range(count)])


def band_maps(size=120, scale=4):
    """A window onto the true blur matrix and onto its true inverse, as RGBA images."""
    n = photo().shape[1]
    k = _kernel(BLUR_LEN, n)
    inv = np.real(np.fft.ifft(1 / spectrum_full()))
    idx = (np.arange(size)[:, None] - np.arange(size)[None, :]) % n

    def paint(v, color):
        img = (np.clip(v[..., None] * _rgb(color), 0, 1) * 255).astype(np.uint8)
        return np.dstack([img, np.full((size, size), 255, np.uint8)]).repeat(scale, 0).repeat(scale, 1)

    M, N = k[idx], inv[idx]
    lo, hi = np.percentile(N, 1), np.percentile(N, 99)
    return paint(M / M.max(), C.fwd), paint(np.clip((N - lo) / (hi - lo), 0, 1), C.back)
