"""Tracks: animatable values as pure functions of absolute time t.

A Track is what you pass to any animatable parameter (shader uniforms, layer
opacity, fx strength, camera zoom...). Plain numbers/arrays are constant tracks.

    opacity = fade(T.field)                       # 0 → 1, landing on the beat
    zoom    = key(T.stretch, 1, 1.15, dur=2)      # 1 → 1.15 over 2 s
    glow    = 0.2 + pulse(T.lam, 0.8)             # tracks support arithmetic
    m       = key(T.stretch, I2, [[2, 0], [0, 1]])  # arrays interpolate elementwise
    color   = keys((T.a, 0.0), (T.b, 1.0, "out_back"), (T.c, 0.3))

Every `at=` lands on the beat: the motion starts `lead` seconds earlier
(default `core.time.LEAD`, set by the theme).

Tracks know *when* they change (`changes(t0, t1)`), which lets the renderer
skip re-rendering static layers.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Iterable, Sequence

import numpy as np

from aion.core import time as _time
from aion.core.ease import ease as _ease

__all__ = ["Track", "track", "const", "key", "keys", "fade", "pulse", "ramp", "wave", "hold", "lerp"]

ALWAYS = [(-math.inf, math.inf)]


def lerp(a, b, u):
    """Linear interpolation that works for scalars, arrays and nested lists.

    Example:
        lerp([0, 0], [2, 1], 0.5)   # → [1.0, 0.5]
    """
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * u
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a + (b - a) * u


def _lead(lead: float | None) -> float:
    return _time.LEAD if lead is None else lead


class Track:
    """Callable value-over-time with known change intervals.

    Example:
        tr = key(2.0, 0, 1, dur=1, lead=0); tr(2.5)  # 0.5
    """

    __slots__ = ("fn", "active", "label")

    def __init__(self, fn: Callable[[float], Any], active: Sequence[tuple[float, float]] | None = None,
                 label: str = ""):
        self.fn = fn
        self.active = list(ALWAYS if active is None else active)
        self.label = label

    def __call__(self, t: float):
        return self.fn(t)

    def changes(self, t0: float, t1: float) -> bool:
        """Does the value possibly change anywhere in [t0, t1]?"""
        return any(a < t1 and t0 < b for a, b in self.active)

    def cache_key(self):
        # Tracks are code: their identity is the label plus active windows. Scene
        # source hashes cover the closure, so this only needs to be descriptive.
        return [self.label, self.active]

    # ── combinators ──────────────────────────────────────────────────────────
    def map(self, f: Callable[[Any], Any]) -> "Track":
        """Apply f to the value (f must be pure)."""
        return Track(lambda t: f(self.fn(t)), self.active, f"{self.label}.map")

    def delay(self, dt: float) -> "Track":
        return Track(lambda t: self.fn(t - dt), [(a + dt, b + dt) for a, b in self.active], self.label)

    def clamp(self, lo: float = 0.0, hi: float = 1.0) -> "Track":
        return self.map(lambda v: np.clip(v, lo, hi))

    def _bin(self, other, op, name):
        o = track(other)
        return Track(lambda t: op(self.fn(t), o.fn(t)), self.active + o.active, f"({self.label}{name}{o.label})")

    def __add__(self, o): return self._bin(o, lambda a, b: a + b, "+")
    def __radd__(self, o): return track(o)._bin(self, lambda a, b: a + b, "+")
    def __sub__(self, o): return self._bin(o, lambda a, b: a - b, "-")
    def __rsub__(self, o): return track(o)._bin(self, lambda a, b: a - b, "-")
    def __mul__(self, o): return self._bin(o, lambda a, b: a * b, "*")
    def __rmul__(self, o): return track(o)._bin(self, lambda a, b: a * b, "*")
    def __truediv__(self, o): return self._bin(o, lambda a, b: a / b, "/")
    def __neg__(self): return self.map(lambda v: -v)

    def __repr__(self):
        return f"Track({self.label or 'fn'})"


def const(v) -> Track:
    """A value that never changes.

    Example:
        s.solid(C.bg, opacity=const(0.5))
    """
    return Track(lambda t: v, [], f"const({v!r})" if np.ndim(v) == 0 else "const")


hold = const


def track(x) -> Track:
    """Coerce a number / array / callable(t) / Track into a Track.

    Example:
        glow = track(lambda t: 0.5 + 0.5 * np.sin(t))
    """
    if isinstance(x, Track):
        return x
    if callable(x):
        return Track(x, None, getattr(x, "__name__", "fn"))
    return const(x)


def key(at: float, a, b, dur: float = 1.0, ease="smooth", lead: float | None = None) -> Track:
    """Hold `a`, move to `b` over `dur` seconds landing on beat `at`, then hold `b`.

    Example:
        key(T.stretch, 1.0, 1.2, dur=1.4, ease="easy_ease")
    """
    t0 = at - _lead(lead)
    f = _ease(ease)

    def fn(t):
        if t <= t0:
            return a
        if t >= t0 + dur:
            return b
        return lerp(a, b, float(f((t - t0) / dur)))

    return Track(fn, [(t0, t0 + dur)], f"key@{at:.2f}")


def keys(*frames: tuple, default_ease="smooth", dur: float | None = None, lead: float | None = None) -> Track:
    """Keyframes `(t, value[, ease])` sorted by time; values interpolate between keys.

    With `dur`, each key is a `key()` move of that length landing on its time
    (holds between moves). Without, values interpolate across whole gaps.

    Example:
        keys((T.a, 0), (T.b, 1, "out_back"), (T.c, 0.3), dur=0.8)
    """
    fr = sorted(frames, key=lambda f: f[0])
    if dur is not None:
        out = const(fr[0][1])
        prev = fr[0][1]
        segs = []
        for f_ in fr[1:]:
            segs.append(key(f_[0], prev, f_[1], dur=dur, ease=f_[2] if len(f_) > 2 else default_ease, lead=lead))
            prev = f_[1]

        def fn(t):
            v = fr[0][1]
            for s in segs:
                if t > s.active[0][0]:
                    v = s(t)
            return v

        return Track(fn, [w for s in segs for w in s.active], "keys")
    times = [f_[0] for f_ in fr]
    eases = [_ease(f_[2] if len(f_) > 2 else default_ease) for f_ in fr]

    def fn(t):
        if t <= times[0]:
            return fr[0][1]
        if t >= times[-1]:
            return fr[-1][1]
        i = int(np.searchsorted(times, t, side="right")) - 1
        u = (t - times[i]) / (times[i + 1] - times[i])
        return lerp(fr[i][1], fr[i + 1][1], float(eases[i + 1](u)))

    return Track(fn, [(times[0], times[-1])], "keys")


def fade(at: float, to: float = 1.0, dur: float = 0.6, out: float | None = None, out_dur: float | None = None,
         ease="smooth", lead: float | None = None) -> Track:
    """0 → `to` landing on `at`; optionally back to 0 landing on `out`.

    Example:
        opacity=fade(T.field, out=T.next_idea)
    """
    up = key(at, 0.0, to, dur=dur, ease=ease, lead=lead)
    if out is None:
        return up
    down = key(out, to, 0.0, dur=out_dur or dur, ease=ease, lead=lead)
    t_out = down.active[0][0]
    return Track(lambda t: up(t) if t < t_out else down(t), up.active + down.active, f"fade@{at:.2f}")


def pulse(at: float, amp: float = 1.0, dur: float = 0.6, base: float = 0.0) -> Track:
    """A bump base → base+amp → base, peaking exactly on the beat.

    Example:
        u_glow = 0.2 + pulse(T.lam, 0.8)
    """
    t0 = at - dur / 2
    f = _ease("there_and_back")
    return Track(lambda t: base + amp * float(f((t - t0) / dur)) if t0 < t < t0 + dur else base,
                 [(t0, t0 + dur)], f"pulse@{at:.2f}")


def ramp(t0: float, t1: float, a: float = 0.0, b: float = 1.0, ease="linear") -> Track:
    """a → b between absolute times t0 and t1 (no lead; for long continuous motion).

    Example:
        u = ramp(T.a, T.b, 0.0, 1.0)
    """
    f = _ease(ease)
    span = max(t1 - t0, 1e-9)
    return Track(lambda t: lerp(a, b, float(f((t - t0) / span))) if t0 < t < t1 else (a if t <= t0 else b),
                 [(t0, t1)], f"ramp@{t0:.2f}")


def wave(freq: float = 1.0, amp: float = 1.0, phase: float = 0.0, base: float = 0.0,
         during: tuple[float, float] | None = None) -> Track:
    """base + amp·sin(2π·freq·t + phase): idle breathing / oscillation (pure in t).

    Example:
        breathe = wave(freq=0.5, amp=0.05, base=1.0)
    """
    lo, hi = during or (-math.inf, math.inf)

    def fn(t):
        tt = min(max(t, lo), hi)
        return base + amp * math.sin(2 * math.pi * freq * tt + phase)

    return Track(fn, [(lo, hi)], "wave")


def every(tracks: Iterable[Track]) -> list[tuple[float, float]]:
    return [w for tr in tracks for w in track(tr).active]
