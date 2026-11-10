"""Deterministic noise: every value is a pure function of (seed, coordinates).

    hash01(7, 3)            -> float in [0, 1)
    noise1(t * 2, seed=4)   -> smooth value noise in [-1, 1]
    shake(t, amp=0.02)      -> (dx, dy) camera shake
    simplex2(x, y)          -> opensimplex (lazy import)
"""

from __future__ import annotations

import math

import numpy as np

__all__ = ["hash01", "noise1", "fbm1", "shake", "simplex2", "simplex3", "rng"]


def hash01(*ints: int) -> float:
    """Stateless integer hash → [0, 1).

    Example:
        jitter = hash01(i, 7)            # stable per index
    """
    h = 0x9E3779B9
    for i in ints:
        h ^= (int(i) & 0xFFFFFFFF) + 0x9E3779B9 + ((h << 6) & 0xFFFFFFFF) + (h >> 2)
        h &= 0xFFFFFFFF
        h = ((h ^ (h >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
        h = ((h ^ (h >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
        h ^= h >> 16
    return (h & 0xFFFFFF) / float(1 << 24)


def noise1(x: float, seed: int = 0) -> float:
    """Smooth 1D value noise in [-1, 1] (quintic interpolation of hashed lattice).

    Example:
        y = noise1(t * 1.5, seed=1)
    """
    i = math.floor(x)
    f = x - i
    u = f * f * f * (f * (f * 6 - 15) + 10)
    a = hash01(seed, i) * 2 - 1
    b = hash01(seed, i + 1) * 2 - 1
    return a + (b - a) * u


def fbm1(x: float, seed: int = 0, octaves: int = 4) -> float:
    """Fractal sum of noise1 (roughly in [-1, 1]).

    Example:
        wobble = track(lambda t: 0.1 * fbm1(t * 2, seed=3))
    """
    v, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        v += amp * noise1(x * freq, seed + 101 * o)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return v / norm


def shake(t: float, amp: float = 0.02, freq: float = 9.0, seed: int = 0) -> tuple[float, float]:
    """Handheld-style 2D offset at time t (pure).

    Example:
        dx, dy = shake(t, amp=0.03)
    """
    return amp * fbm1(t * freq, seed), amp * fbm1(t * freq, seed + 7919)


def rng(*seed: int) -> np.random.Generator:
    """Seeded numpy Generator (use for scene setup; never at render time without a seed).

    Example:
        pts = rng(42).normal(size=(500, 2))
    """
    return np.random.default_rng([int(s) for s in seed] or [0])


_OS = {}


def _os(seed: int):
    if seed not in _OS:
        from opensimplex import OpenSimplex

        _OS[seed] = OpenSimplex(seed)
    return _OS[seed]


def simplex2(x: float, y: float, seed: int = 0) -> float:
    """2-D OpenSimplex noise in [-1, 1] (deterministic per seed).

    Example:
        h = simplex2(x * 0.5, y * 0.5, seed=2)
    """
    return _os(seed).noise2(x, y)


def simplex3(x: float, y: float, z: float, seed: int = 0) -> float:
    """3-D OpenSimplex noise in [-1, 1]; use z = time for evolving 2-D noise.

    Example:
        h = simplex3(x, y, t * 0.3, seed=2)
    """
    return _os(seed).noise3(x, y, z)
