"""Word-level narration timing from `cue-per-word.srt` or `words.json`.

    cue = Cue.load("videos/004-x/assets/cue-per-word.srt")
    cue.at("spin")                     # start of first "spin"
    cue.at("minus", after=30)          # first "minus" at/after 30 s
    cue.phrase("quarter turn")         # (start, end)
    cur = cue.cursor(); cur.at("a"); cur.at("b")   # each search after the previous hit
    cue.segments(); cue.text(10, 14)

Matching ignores case and punctuation ("Turn," == "turn"). Lookups raise
KeyError with the nearest candidates, so a changed script fails loudly.
"""

from __future__ import annotations

import bisect
import difflib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

__all__ = ["Word", "Segment", "Cue", "Cursor", "norm", "parse_srt_time", "fmt_srt_time"]

_TS = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


def parse_srt_time(s: str) -> float:
    h, m, sec, ms = _TS.search(s).groups()
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 10 ** len(ms)


def fmt_srt_time(t: float) -> str:
    ms = max(0, round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def norm(word: str) -> str:
    """Matching key: lowercase, letters/digits only ("Don't," → "dont").

    Example:
        norm("Don't,")   # → 'dont'
    """
    return re.sub(r"[^\w]", "", word.lower()).replace("_", "")


@dataclass(frozen=True)
class Word:
    """One narrated word with absolute start/end seconds.

    Example:
        cue.word_at(12.3)   # Word(text='matrix', start=12.21, end=12.6)
    """
    text: str
    start: float
    end: float

    @property
    def key(self) -> str:
        return norm(self.text)

    @property
    def ends_sentence(self) -> bool:
        return self.text.rstrip().rstrip("\"')”’")[-1:] in ".?!"

    @property
    def ends_clause(self) -> bool:
        return self.text.rstrip()[-1:] in ",;:—–"


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
    """Indexed word timeline loaded from a word-level SRT or words.json, with in-order phrase search.

    Example:
        cue = Cue.load("assets/cue-per-word.srt"); cue.at("eigenvector"); cue.phrase("for every vector")
    """

    def __init__(self, words: list[Word]):
        self.words = sorted(words, key=lambda w: w.start)
        self.starts = [w.start for w in self.words]
        self._index: dict[str, list[int]] = defaultdict(list)
        for i, w in enumerate(self.words):
            self._index[w.key].append(i)

    # ── loading ────────────────────────────────────────────────────────────
    @classmethod
    def load(cls, path: str | Path) -> "Cue":
        """Load `.srt` (one word per cue; multi-word cues are split evenly) or `words.json`."""
        path = Path(path)
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data["words"] if isinstance(data, dict) else data
            return cls([Word(d["text"], float(d["start"]), float(d["end"])) for d in items])
        words: list[Word] = []
        for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
            lines = [l for l in block.strip().splitlines() if l.strip()]
            ti = next((i for i, l in enumerate(lines) if "-->" in l), None)
            if ti is None:
                continue
            a, z = (parse_srt_time(x) for x in lines[ti].split("-->"))
            toks = " ".join(lines[ti + 1:]).split()
            for k, tok in enumerate(toks):
                words.append(Word(tok, a + (z - a) * k / len(toks), a + (z - a) * (k + 1) / len(toks)))
        return cls(words)

    # ── lookups ────────────────────────────────────────────────────────────
    def find(self, text: str, after: float = 0.0, nth: int = 1) -> tuple[int, int]:
        """Word index range [i, j) of the nth occurrence of `text` starting at/after `after`."""
        keys = [norm(t) for t in text.split() if norm(t)]
        if not keys:
            raise KeyError(f"empty phrase {text!r}")
        n, seen = len(keys), 0
        lo = bisect.bisect_left(self.starts, after - 1e-6)
        for i in self._index.get(keys[0], []):
            if i < lo:
                continue
            if all(i + k < len(self.words) and self.words[i + k].key == keys[k] for k in range(1, n)):
                seen += 1
                if seen == nth:
                    return i, i + n
        raise KeyError(self._miss(text, after))

    def _miss(self, text: str, after: float) -> str:
        first = norm(text.split()[0])
        near = difflib.get_close_matches(first, list(self._index), n=3)
        hits = [f"{self.words[i].start:.2f}s" for i in self._index.get(first, [])][:6]
        return (f"{text!r} not found after {after:.2f}s"
                + (f"; '{first}' occurs at {', '.join(hits)}" if hits else "")
                + (f"; similar words: {near}" if near and not hits else ""))

    def at(self, text: str, after: float = 0.0, nth: int = 1) -> float:
        """Start time of word/phrase."""
        return self.words[self.find(text, after, nth)[0]].start

    def end_of(self, text: str, after: float = 0.0, nth: int = 1) -> float:
        return self.words[self.find(text, after, nth)[1] - 1].end

    def phrase(self, text: str, after: float = 0.0, nth: int = 1) -> tuple[float, float]:
        i, j = self.find(text, after, nth)
        return self.words[i].start, self.words[j - 1].end

    def word_at(self, t: float) -> Word | None:
        i = bisect.bisect_right(self.starts, t) - 1
        return self.words[i] if i >= 0 and self.words[i].end >= t else None

    def text(self, t0: float, t1: float) -> str:
        """Narration spoken in [t0, t1)."""
        lo, hi = bisect.bisect_left(self.starts, t0), bisect.bisect_left(self.starts, t1)
        return " ".join(w.text for w in self.words[lo:hi])

    def cursor(self, after: float = 0.0) -> "Cursor":
        return Cursor(self, after)

    # ── structure ──────────────────────────────────────────────────────────
    def segments(self, pause: float = 0.35) -> list[Segment]:
        """Split on sentence punctuation and on gaps longer than `pause`."""
        out, cur = [], []
        for k, w in enumerate(self.words):
            cur.append(w)
            nxt = self.words[k + 1] if k + 1 < len(self.words) else None
            if nxt is None or w.ends_sentence or nxt.start - w.end > pause:
                out.append(Segment(tuple(cur)))
                cur = []
        return out

    def gaps(self, min_gap: float = 0.35) -> list[tuple[float, float]]:
        """Gaps between consecutive words longer than `min_gap` (SRTs often have none: use sync.silences)."""
        return [(a.end, b.start) for a, b in zip(self.words, self.words[1:]) if b.start - a.end > min_gap]

    @property
    def duration(self) -> float:
        return self.words[-1].end if self.words else 0.0

    def __len__(self) -> int:
        return len(self.words)


class Cursor:
    """Ordered lookups: each `at()` searches after the previous match's start.

    Example:
        c = cue.cursor(); a = c.at("matrix"); b = c.at("matrix")  # second occurrence
    """

    def __init__(self, cue: Cue, after: float = 0.0):
        self.cue, self.pos = cue, after

    def find(self, text: str) -> tuple[int, int]:
        i, j = self.cue.find(text, self.pos)
        self.pos = self.cue.words[i].start + 1e-4
        return i, j

    def at(self, text: str) -> float:
        return self.cue.words[self.find(text)[0]].start
