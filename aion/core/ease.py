"""Easing curves: functions [0, 1] → [0, 1] (some overshoot). Pure numpy-friendly.

Any `ease=` argument in aion accepts a name from `EASES`, a Manim rate function,
or any callable. Defaults: `smooth` for moves, `out_cubic` for entrances,
`in_out_sine` for loops. Avoid `linear` except for constant-speed motion.

    ease("easy_ease")(0.5) -> 0.5
    cubic_bezier(.2, 0, 0, 1)        # After Effects / CSS style curve
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Callable

import numpy as np

__all__ = ["ease", "cubic_bezier", "spring", "steps", "EASES"]

Ease = Callable[[float], float]


def _c(u):
    return np.clip(u, 0.0, 1.0)


def linear(u):
    return _c(u)


def smooth(u):
    """Smoothstep 3u²−2u³ (gentle in/out; the house default)."""
    u = _c(u)
    return u * u * (3 - 2 * u)


def smoother(u):
    """Smootherstep: zero velocity *and* acceleration at both ends."""
    u = _c(u)
    return u * u * u * (u * (6 * u - 15) + 10)


def in_cubic(u):
    return _c(u) ** 3


def out_cubic(u):
    return 1 - (1 - _c(u)) ** 3


def in_out_cubic(u):
    u = _c(u)
    return np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)


def out_quint(u):
    return 1 - (1 - _c(u)) ** 5


def out_expo(u):
    u = _c(u)
    return np.where(u >= 1, 1.0, 1 - 2.0 ** (-10 * u))


def in_out_sine(u):
    return -(np.cos(math.pi * _c(u)) - 1) / 2


def out_back(u, s: float = 1.70158):
    u = _c(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def out_elastic(u):
    u = _c(u)
    c4 = 2 * math.pi / 3
    return np.where((u <= 0) | (u >= 1), u, 2 ** (-10 * u) * np.sin((u * 10 - 0.75) * c4) + 1)


def there_and_back(u):
    """0 → 1 → 0, smooth (for pulses / indications)."""
    u = _c(u)
    return smooth(np.where(u < 0.5, 2 * u, 2 - 2 * u))


def spring(damping: float = 0.55, freq: float = 2.2) -> Ease:
    """Damped spring settling at 1 (natural overshoot). damping in (0, 1).

    Example:
        m.play(FadeIn(dot), at=T.pop, ease=spring(damping=0.4, freq=3))
    """
    w = 2 * math.pi * freq
    zeta = damping

    def f(u):
        u = _c(u)
        wd = w * math.sqrt(max(1e-6, 1 - zeta ** 2))
        v = 1 - np.exp(-zeta * w * u) * (np.cos(wd * u) + zeta * w / wd * np.sin(wd * u))
        return np.where(u >= 1, 1.0, v / (1 - math.exp(-zeta * w) * (math.cos(wd) + zeta * w / wd * math.sin(wd))))

    return f


def steps(n: int) -> Ease:
    """Hold-frame staircase with n steps (stop-motion / counters).

    Example:
        key(T.count, 0, 10, dur=2, ease=steps(10))
    """
    return lambda u: np.floor(_c(u) * n) / n


@lru_cache(maxsize=64)
def cubic_bezier(x1: float, y1: float, x2: float, y2: float) -> Ease:
    """CSS / After Effects cubic-bezier timing curve (solved by lookup table).

    Example:
        key(T.x, 0, 1, ease=cubic_bezier(0.2, 0, 0, 1))
    """
    s = np.linspace(0, 1, 1025)
    bx = 3 * x1 * s * (1 - s) ** 2 + 3 * x2 * s ** 2 * (1 - s) + s ** 3
    by = 3 * y1 * s * (1 - s) ** 2 + 3 * y2 * s ** 2 * (1 - s) + s ** 3
    order = np.argsort(bx)
    bx, by = bx[order], by[order]
    return lambda u: np.interp(_c(u), bx, by)


EASES: dict[str, Ease] = {
    "linear": linear, "smooth": smooth, "smoother": smoother,
    "in_cubic": in_cubic, "out_cubic": out_cubic, "in_out_cubic": in_out_cubic,
    "out_quint": out_quint, "out_expo": out_expo, "in_out_sine": in_out_sine,
    "out_back": out_back, "out_elastic": out_elastic, "there_and_back": there_and_back,
    "easy_ease": cubic_bezier(0.33, 0.0, 0.67, 1.0),        # AE F9
    "easy_ease_out": cubic_bezier(0.0, 0.0, 0.58, 1.0),
    "easy_ease_in": cubic_bezier(0.42, 0.0, 1.0, 1.0),
    "snap": cubic_bezier(0.2, 0.0, 0.0, 1.0),               # fast start, long settle
    "spring": spring(),
}


def ease(e: str | Ease | None) -> Ease:
    """Resolve a name / callable / None (→ smooth) to an easing function.

    Example:
        ease("out_back")(0.8)
    """
    if e is None:
        return smooth
    if callable(e):
        return e
    try:
        return EASES[e]
    except KeyError:
        raise KeyError(f"unknown ease {e!r}; choose from {sorted(EASES)}") from None
