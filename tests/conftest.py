"""Shared fixtures: a synthetic narrated video (tone bursts per word + real silences)."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
import pytest

from aion.sync.cue import fmt_srt_time

# (word, start, end): sentence gaps of 0.6 s; words inside a sentence touch, like ElevenLabs output
WORDS = [
    ("Imagine", 0.20, 0.60), ("a", 0.60, 0.70), ("grid", 0.70, 1.10), ("of", 1.10, 1.25), ("lines.", 1.25, 1.80),
    ("This", 2.40, 2.70), ("arrow", 2.70, 3.10), ("stretches.", 3.10, 3.90),
    ("Now", 4.50, 4.80), ("watch", 4.80, 5.20), ("the", 5.20, 5.35), ("arrow", 5.35, 5.80), ("again.", 5.80, 6.40),
]
DURATION = 7.0
RATE = 16000


def write_fixture_video(root: Path) -> Path:
    vdir = root / "999-fixture"
    (vdir / "assets").mkdir(parents=True)
    (vdir / "scenes").mkdir()
    srt = "\n".join(f"{i}\n{fmt_srt_time(a)} --> {fmt_srt_time(b)}\n{w}\n" for i, (w, a, b) in enumerate(WORDS, 1))
    (vdir / "assets" / "cue-per-word.srt").write_text(srt)
    t = np.arange(int(DURATION * RATE)) / RATE
    x = np.zeros_like(t)
    for _, a, b in WORDS:
        m = (t >= a) & (t < b)
        x[m] = 0.4 * np.sin(2 * np.pi * 220 * t[m])
    with wave.open(str(vdir / "assets" / "audio.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((x * 32767).astype("<i2").tobytes())
    return vdir


@pytest.fixture
def fixture_video(tmp_path, monkeypatch):
    from aion import cache

    monkeypatch.setattr(cache, "CACHE", tmp_path / "cache")
    return write_fixture_video(tmp_path)
