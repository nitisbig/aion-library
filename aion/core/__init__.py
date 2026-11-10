"""aion.core: time, easing, keyframe tracks, clocks and noise (all pure functions of t)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "FrameGrid": "time", "TimeRange": "time", "set_lead": "time",
    "ease": "ease", "cubic_bezier": "ease", "spring": "ease", "steps": "ease", "EASES": "ease",
    "Track": "track", "track": "track", "const": "track", "key": "track", "keys": "track",
    "fade": "track", "pulse": "track", "ramp": "track", "wave": "track", "lerp": "track",
    "Clock": "clock",
    "hash01": "noise", "noise1": "noise", "fbm1": "noise", "shake": "noise", "rng": "noise",
    "simplex2": "noise", "simplex3": "noise",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
