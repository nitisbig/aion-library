"""Frame grid and time ranges. All aion time is absolute audio time in seconds.

    g = FrameGrid(60)
    g.frame(1.0) -> 60;  g.time(60) -> 1.0;  g.snap(1.004) -> 1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["FrameGrid", "TimeRange", "LEAD", "set_lead"]

LEAD = 0.15
"""Default seconds an animation starts before its beat (theme may override)."""


def set_lead(seconds: float) -> None:
    """Change the global default lead used by `at=` everywhere.

    Example:
        set_lead(0.1)   # usually set by the theme's `lead` token instead
    """
    global LEAD
    LEAD = float(seconds)


@dataclass(frozen=True)
class FrameGrid:
    """Maps between seconds and frame indices at `fps`.

    Example:
        FrameGrid(60).snap(1.2345)  # 1.2333…
    """

    fps: float = 60

    def frame(self, t: float) -> int:
        """Index of the frame that shows time t (floor, with float slack)."""
        return math.floor(t * self.fps + 1e-6)

    def time(self, k: int) -> float:
        return k / self.fps

    def snap(self, t: float) -> float:
        """Nearest frame boundary."""
        return round(t * self.fps) / self.fps

    def count(self, t0: float, t1: float) -> int:
        """Frames in [t0, t1) when both ends are frame-snapped."""
        return round(t1 * self.fps) - round(t0 * self.fps)


@dataclass(frozen=True)
class TimeRange:
    """Half-open [start, end) interval in seconds.

    Example:
        TimeRange(2, 5).local(3.5)  # 0.5
    """

    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start

    def contains(self, t: float) -> bool:
        return self.start <= t < self.end

    def local(self, t: float) -> float:
        """0→1 progress through the range (clamped)."""
        if self.end <= self.start:
            return 1.0 if t >= self.end else 0.0
        return min(1.0, max(0.0, (t - self.start) / (self.end - self.start)))

    def overlaps(self, a: float, b: float) -> bool:
        return self.start < b and a < self.end
