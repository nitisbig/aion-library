"""Narration sync: parse word-level SRT and look up beat times.

    from aion.sync import Cue
    cue = Cue.load("videos/001-complex-numbers/assets/cue-per-word.srt")
    t = cue.at("spin")                       # start of first "spin"
    t = cue.at("minus", after=30.0)          # first "minus" starting at/after 30 s
    s, e = cue.phrase("quarter turn", after=40)
    for seg in cue.segments(): ...           # sentences / pause-split phrases

Matching is case- and punctuation-insensitive ("I" == "i", "turn," == "turn").
Lookups raise KeyError when nothing matches, so a changed script fails loudly
instead of silently drifting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TS = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


def _ts(s: str) -> float:
    h, m, sec, ms = _TS.search(s).groups()
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 10 ** len(ms)


def norm(word: str) -> str:
    return re.sub(r"[^\w]", "", word.lower())


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float

    @property
    def key(self) -> str:
        return norm(self.text)

    @property
    def ends_sentence(self) -> bool:
        return self.text.rstrip()[-1:] in ".?!"


@dataclass(frozen=True)
class Segment:
    words: tuple[Word, ...]

    @property
    def start(self) -> float:
        return self.words[0].start

    @property
    def end(self) -> float:
        return self.words[-1].end

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


class Cue:
    def __init__(self, words: list[Word]):
        self.words = words

    @classmethod
    def load(cls, path: str | Path) -> "Cue":
        blocks = re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip())
        words = []
        for b in blocks:
            lines = [l for l in b.strip().splitlines() if l.strip()]
            ti = next(i for i, l in enumerate(lines) if "-->" in l)
            a, z = lines[ti].split("-->")
            words.append(Word(" ".join(lines[ti + 1:]).strip(), _ts(a), _ts(z)))
        return cls(words)

    # ── lookups ────────────────────────────────────────────────
    def find(self, text: str, after: float = 0.0) -> tuple[int, int]:
        """Index range [i, j) of the first occurrence of `text` starting >= after."""
        keys = [norm(t) for t in text.split()]
        n = len(keys)
        for i in range(len(self.words) - n + 1):
            if self.words[i].start + 1e-6 < after:
                continue
            if [w.key for w in self.words[i:i + n]] == keys:
                return i, i + n
        raise KeyError(f"{text!r} not found after {after:.2f}s")

    def at(self, text: str, after: float = 0.0) -> float:
        """Start time of word/phrase `text`."""
        return self.words[self.find(text, after)[0]].start

    def end_of(self, text: str, after: float = 0.0) -> float:
        return self.words[self.find(text, after)[1] - 1].end

    def phrase(self, text: str, after: float = 0.0) -> tuple[float, float]:
        i, j = self.find(text, after)
        return self.words[i].start, self.words[j - 1].end

    # ── structure ──────────────────────────────────────────────
    def segments(self, pause: float = 0.35) -> list[Segment]:
        """Split on sentence punctuation and on silences longer than `pause`."""
        out, cur = [], []
        for k, w in enumerate(self.words):
            cur.append(w)
            nxt = self.words[k + 1] if k + 1 < len(self.words) else None
            if nxt is None or w.ends_sentence or nxt.start - w.end > pause:
                out.append(Segment(tuple(cur)))
                cur = []
        return out

    def gaps(self, min_gap: float = 0.35) -> list[tuple[float, float]]:
        """Silences (start, end) between words longer than `min_gap`."""
        return [
            (a.end, b.start)
            for a, b in zip(self.words, self.words[1:])
            if b.start - a.end > min_gap
        ]

    @property
    def duration(self) -> float:
        return self.words[-1].end
