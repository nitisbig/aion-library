"""Time remapping from a rate curve (slow-motion, freeze, ease to a stop), still pure in t.

A Clock answers "how far has this motion progressed at audio time t" when its
speed varies. The integral is precomputed on a fine grid once, so evaluating
any frame (in any order, in any worker) is a lookup.

    spin = Clock(rate=keys((T.a, 1.0), (T.slow, 0.1), (T.b, 1.0)), start=T.a)
    angle = lambda t: TAU * 0.5 * spin(t)        # 0.5 rev/s, slowed at T.slow
"""

from __future__ import annotations

import numpy as np

from aion.core.track import Track, track

__all__ = ["Clock"]


class Clock:
    """Integrated time: clock(t) = ∫ rate(τ) dτ from `start` (0 before start).

    Example:
        c = Clock(rate=0.5, start=2.0); c(4.0)  # 1.0
    """

    def __init__(self, rate=1.0, start: float = 0.0, end: float | None = None, step: float = 1 / 480):
        self.rate = track(rate)
        self.start = float(start)
        windows = [w for w in self.rate.active if np.isfinite(w[1])]
        self.end = end if end is not None else max([self.start + 1.0] + [b for _, b in windows])
        n = max(2, int(np.ceil((self.end - self.start) / step)) + 1)
        self._t = np.linspace(self.start, self.end, n)
        r = np.array([float(self.rate(t)) for t in self._t])
        self._v = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) * 0.5 * np.diff(self._t))])
        self._rate_end = r[-1]

    def __call__(self, t: float) -> float:
        if t <= self.start:
            return 0.0
        if t >= self.end:
            return float(self._v[-1] + self._rate_end * (t - self.end))
        return float(np.interp(t, self._t, self._v))

    def track(self) -> Track:
        return Track(self, [(self.start, float("inf"))], "clock")
