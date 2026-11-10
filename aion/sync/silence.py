"""Real silences in the narration audio (SRT word timings usually touch end-to-start).

    silences("assets/audio.wav")          -> [(start, end), ...] seconds
    audio_duration("assets/audio.wav")    -> exact seconds from decoded samples
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from aion import cache

__all__ = ["load_audio", "audio_duration", "silences", "rms_envelope"]


def load_audio(path: str | Path, rate: int = 16000) -> np.ndarray:
    """Decode any audio file to mono float32 at `rate` Hz (PyAV).

    Example:
        x = load_audio("assets/audio.wav")   # mono float32 @16 kHz
    """
    import av

    out = []
    with av.open(str(path)) as f:
        stream = f.streams.audio[0]
        res = av.AudioResampler(format="flt", layout="mono", rate=rate)
        for frame in f.decode(stream):
            for r in res.resample(frame):
                out.append(r.to_ndarray().reshape(-1))
        for r in res.resample(None):
            out.append(r.to_ndarray().reshape(-1))
    return np.concatenate(out) if out else np.zeros(0, np.float32)


def audio_duration(path: str | Path) -> float:
    """Duration in seconds, from decoded sample count (cached by file hash).

    Example:
        audio_duration("assets/audio.wav")   # exact, from decoded samples
    """
    path = Path(path)

    def make(tmp: Path):
        import av

        n, rate = 0, None
        with av.open(str(path)) as f:
            s = f.streams.audio[0]
            rate = s.rate
            for frame in f.decode(s):
                n += frame.samples
        tmp.write_text(repr(n / rate))

    return float(cache.get_or_make("duration", [cache.file_hash(path)], make, ".txt").read_text())


def rms_envelope(x: np.ndarray, rate: int, win: float = 0.01) -> np.ndarray:
    n = max(1, int(rate * win))
    m = len(x) // n
    frames = x[: m * n].reshape(m, n)
    return np.sqrt((frames.astype(np.float64) ** 2).mean(axis=1) + 1e-12)


def silences(path: str | Path, db: float = -38.0, min_len: float = 0.18, rate: int = 16000,
             win: float = 0.01) -> list[tuple[float, float]]:
    """Spans quieter than `db` dBFS (relative to the 99th-percentile level) lasting ≥ min_len s.

    Example:
        for a, b in silences("assets/audio.wav", db=-40): ...
    """
    path = Path(path)

    def make(tmp: Path):
        x = load_audio(path, rate)
        env = rms_envelope(x, rate, win)
        ref = np.percentile(env, 99) if len(env) else 1.0
        level = 20 * np.log10(env / max(ref, 1e-9))
        quiet = np.concatenate([[False], level < db, [False]])
        edges = np.flatnonzero(np.diff(quiet.astype(np.int8)))
        spans = [(a * win, b * win) for a, b in zip(edges[::2], edges[1::2]) if (b - a) * win >= min_len]
        np.save(tmp, np.array(spans, dtype=np.float64).reshape(-1, 2))

    p = cache.get_or_make("silence", [cache.file_hash(path), db, min_len, rate, win], make, ".npy")
    return [(float(a), float(b)) for a, b in np.load(p)]
