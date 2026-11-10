"""Scene-boundary helpers: contiguity checks and cut suggestions for storyboards."""

from __future__ import annotations

from aion.core.time import FrameGrid
from aion.sync.cue import Cue

__all__ = ["check_contiguous", "suggest_cuts"]


def check_contiguous(ranges: list[tuple[str, float, float]], duration: float, fps: float = 60) -> None:
    """Raise if scene ranges `(name, start, end)` leave gaps/overlaps or miss the audio ends.

    Example:
        check_contiguous([("s01", 0, 4.2), ("s02", 4.2, 9.0)], duration=9.0)
    """
    g = FrameGrid(fps)
    tol = 0.5 / fps
    errors = []
    rs = sorted(ranges, key=lambda r: r[1])
    if not rs:
        raise ValueError("no scenes")
    if abs(rs[0][1]) > tol:
        errors.append(f"first scene {rs[0][0]} starts at {rs[0][1]:.3f}s, not 0")
    for (n1, _, e1), (n2, s2, _) in zip(rs, rs[1:]):
        if abs(g.frame(e1) - g.frame(s2)) > 0:
            errors.append(f"{n1} ends {e1:.3f}s but {n2} starts {s2:.3f}s")
    if abs(rs[-1][2] - duration) > 1 / fps + 1e-6:
        errors.append(f"last scene {rs[-1][0]} ends {rs[-1][2]:.3f}s, audio is {duration:.3f}s")
    for n, s, e in rs:
        if e <= s:
            errors.append(f"{n} has non-positive length ({s:.3f}→{e:.3f})")
    if errors:
        raise ValueError("scene ranges are not contiguous:\n  " + "\n  ".join(errors))


def suggest_cuts(cue: Cue, sil: list[tuple[float, float]], min_silence: float = 0.3) -> list[dict]:
    """Sentence ends followed by a real silence ≥ min_silence: natural scene boundaries.

    Example:
        suggest_cuts(cue, silences(audio), min_silence=0.4)
    """
    out = []
    for a, b in zip(cue.words, cue.words[1:]):
        if not a.ends_sentence:
            continue
        span = max((min(e, b.start + 0.25) - max(s, a.end - 0.25) for s, e in sil
                    if s < b.start + 0.25 and a.end - 0.25 < e), default=0.0)
        if span >= min_silence:
            out.append({"after": a.text, "before": b.text, "t": (a.end + b.start) / 2, "silence": span})
    return out
