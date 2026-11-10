"""Complex Fourier series for closed drawings, waves and the heat equation.

Conventions (the ones the video says out loud):
    f(t) = Σ c_n e^{2πint},   c_n = ∫₀¹ f(t) e^{−2πint} dt,   t ∈ [0, 1)
A drawing is a complex array z (x + iy) sampled at t = k/M. Speed n > 0 turns
counterclockwise, n < 0 clockwise, n = 0 is the still offset.

    z = resample(outline, 1000)              # even spacing along the path
    c = coefficients(z, 100)                 # {n: c_n}, n = −100…100 (201 circles)
    terms = order_terms(c)                   # biggest first (c₀ always first)
    joints = chain_points(terms, t)          # every arm joint at time t; joints[-1] = pen
    pen = partial_sum(terms[:20], t)         # the drawing with only 20 circles

Everything is plain numpy, so scenes, GL plates and tests share one source of truth.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import numpy as np

Terms = Sequence[tuple[int, complex]]
TAU = 2 * np.pi


# ── paths ──────────────────────────────────────────────────────────────────
def as_complex(points) -> np.ndarray:
    p = np.asarray(points)
    if np.iscomplexobj(p) or p.ndim == 1:                           # complex, or a real 1-D signal
        return p.astype(complex).ravel()
    return p[..., 0] + 1j * p[..., 1]


def resample(points, n: int) -> np.ndarray:
    """n points evenly spaced by arc length along the closed polyline `points`."""
    z = as_complex(points)
    if abs(z[0] - z[-1]) < 1e-12:
        z = z[:-1]
    closed = np.append(z, z[0])
    seg = np.abs(np.diff(closed))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    u = np.arange(n) / n * s[-1]
    return np.interp(u, s, closed.real) + 1j * np.interp(u, s, closed.imag)


def bridge(contours: Iterable) -> np.ndarray:
    """Join several closed contours into one closed path.

    Contours are attached one at a time to the growing path at their closest pair
    of points: the pen walks over, goes round the new contour, and walks back the
    same way. Every contour is drawn once and the result is a single loop.
    """
    cs = [as_complex(c) for c in contours]
    cs = [c[:-1] if abs(c[0] - c[-1]) < 1e-12 else c for c in cs]
    cs.sort(key=lambda c: -np.ptp(c.real) * np.ptp(c.imag))      # biggest first
    path = cs.pop(0)
    while cs:
        best = None
        for k, c in enumerate(cs):
            d = np.abs(path[:, None] - c[None, :])
            i, j = np.unravel_index(np.argmin(d), d.shape)
            if best is None or d[i, j] < best[0]:
                best = (d[i, j], k, i, j)
        _, k, i, j = best
        c = np.roll(cs.pop(k), -j)
        path = np.concatenate([path[:i + 1], c, [c[0]], path[i:]])
    return path


def centered(z: np.ndarray) -> np.ndarray:
    """Shift so that the balance point (c₀, the time average) is at the origin."""
    return z - z.mean()


# ── coefficients ───────────────────────────────────────────────────────────
def coefficients(z, N: int) -> dict[int, complex]:
    """c_n for n = −N…N from samples z(k/M), k = 0…M−1 (needs M > 2N)."""
    z = as_complex(z)
    M = len(z)
    if M <= 2 * N:
        raise ValueError(f"{M} samples cannot resolve speeds up to {N}")
    c = np.fft.fft(z) / M
    return {n: complex(c[n % M]) for n in range(-N, N + 1)}


def spin_average(z, k: int) -> complex:
    """The video's recipe done literally: turn the drawing backward k times, average."""
    z = as_complex(z)
    t = np.arange(len(z)) / len(z)
    return complex((z * np.exp(-TAU * 1j * k * t)).mean())


def order_terms(coeffs: Mapping[int, complex], order: str = "size",
                keep_zero_first: bool = True) -> list[tuple[int, complex]]:
    """Terms as (n, c_n), sorted biggest first ("size") or 0, 1, −1, 2, −2… ("speed")."""
    items = list(coeffs.items())
    if order == "size":
        items.sort(key=lambda nc: (-abs(nc[1]), abs(nc[0]), -nc[0]))
    elif order == "speed":
        items.sort(key=lambda nc: (abs(nc[0]), -nc[0]))
    else:
        raise ValueError(order)
    if keep_zero_first:
        items.sort(key=lambda nc: nc[0] != 0)                       # stable: 0 moves to the front
    return items


# ── evaluation ─────────────────────────────────────────────────────────────
def _terms(c) -> list[tuple[int, complex]]:
    return list(c.items()) if isinstance(c, Mapping) else list(c)


def partial_sum(c, t, frame: int = 0) -> np.ndarray | complex:
    """Σ c_n e^{2πi(n − frame)t}. `frame = k` is the drawing turned backward k times."""
    t = np.asarray(t, float)
    out = np.zeros(t.shape, complex)
    for n, cn in _terms(c):
        out = out + cn * np.exp(TAU * 1j * (n - frame) * t)
    return out if out.shape else complex(out)


def chain_points(c, t: float, frame: int = 0) -> np.ndarray:
    """Joint positions of the chain at time t: [0, c₀…, …, pen] (len = terms + 1)."""
    terms = _terms(c)
    arms = np.array([cn * np.exp(TAU * 1j * (n - frame) * t) for n, cn in terms], complex)
    return np.concatenate([[0j], np.cumsum(arms)])


# ── the video's closed-form examples ───────────────────────────────────────
def square_wave(t, n_terms: int) -> np.ndarray:
    """(4/π) Σ_{k<n_terms} sin((2k+1)t)/(2k+1): the ±1 square wave with n_terms circles."""
    t = np.asarray(t, float)
    out = np.zeros(t.shape)
    for n in range(1, 2 * n_terms, 2):                              # loop: memory stays O(len(t))
        out += np.sin(n * t) / n
    return 4 / np.pi * out


def square_wave_radii(n_terms: int) -> list[tuple[int, float]]:
    """(speed, radius) of each circle of the square wave: (1, 4/π), (3, 4/3π), …"""
    return [(n, 4 / (np.pi * n)) for n in range(1, 2 * n_terms, 2)]


def square_loop(M: int, half: float = 1.0) -> np.ndarray:
    """A square of side 2·half traced at constant speed, starting mid-way up the right side."""
    u = (np.arange(M) / M * 8 + 1) % 8                               # perimeter position, 0 = (1, −1)
    corners = np.array([1 - 1j, 1 + 1j, -1 + 1j, -1 - 1j]) * half
    k = (u // 2).astype(int)
    r = (u % 2) / 2
    return corners[k] + (corners[(k + 1) % 4] - corners[k]) * r


def heat_ring(theta, t, kappa: float = 1.0, n_terms: int = 200) -> np.ndarray:
    """Temperature on a ring that starts as the ±1 square wave: Σ (4/πn) e^{−κn²t} sin nθ."""
    theta = np.asarray(theta, float)
    out = np.zeros(theta.shape)
    for n in range(1, 2 * n_terms, 2):
        out += 4 / (np.pi * n) * np.exp(-kappa * n * n * t) * np.sin(n * theta)
    return out


def gibbs_peak(n_terms: int, samples: int = 4001) -> float:
    """Height of the first overshoot of square_wave(·, n_terms) (limit 1.17898)."""
    t = np.linspace(0, min(np.pi / 2, 2 * np.pi / (2 * n_terms)), samples)   # first lobe only
    return float(square_wave(t, n_terms).max())
