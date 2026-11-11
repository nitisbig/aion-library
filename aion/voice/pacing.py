"""Pacing pass for generated narration: tighten word cues to the waveform, then add breathing room.

Two things TTS output gets wrong for a calm explainer, both fixed here without spending credits:

1. **Cue drift at pauses.** Forced-alignment timestamps are often 0.2–0.4 s late right after a
   pause (the pause gets attributed to the wrong word). `snap_words` detects the real silences
   in the audio and moves the word after each pause onto the actual speech onset.
2. **No room to breathe.** `stretch` lengthens the real silence at paragraph and section
   boundaries (and adds a silent lead-in), shifting every later cue by the same amount.

Enable per video in `voice.toml` (ignored by the TTS cache, so changing it never re-bills):

    [pacing]
    snap = true            # move cues onto real speech onsets
    lead_in = 4.0          # seconds of silence before the first word
    paragraph_gap = 0.5    # extra silence after every paragraph
    section_gap = 1.5      # extra silence before a paragraph that follows a `# heading`
    tail = 2.0             # silence after the last word (room for a fade-out)
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

__all__ = ["Pacing", "silences", "snap_words", "stretch"]


@dataclass(frozen=True)
class Pacing:
    """Pacing options from the `[pacing]` table of voice.toml.

    Example:
        Pacing(snap=True, lead_in=4.0, paragraph_gap=0.5, section_gap=1.5)
    """

    snap: bool = False
    lead_in: float = 0.0
    paragraph_gap: float = 0.0
    section_gap: float = 0.0
    tail: float = 0.0

    @classmethod
    def load(cls, path: Path | None) -> "Pacing":
        if path is None or not path.exists():
            return cls()
        import tomllib

        data = tomllib.loads(path.read_text()).get("pacing", {})
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @property
    def active(self) -> bool:
        return self.snap or max(self.lead_in, self.paragraph_gap, self.section_gap, self.tail) > 0


def silences(x: np.ndarray, rate: int, min_len: float = 0.2, drop_db: float = 34.0) -> list[tuple[float, float]]:
    """(start, end) of every stretch quieter than `drop_db` below the speech level, at least `min_len` long.

    Example:
        gaps = silences(pcm, 44100)
    """
    hop = max(1, int(rate * 0.01))
    n = len(x) // hop
    if n == 0:
        return []
    e = 20 * np.log10(np.sqrt((x[:n * hop].astype(np.float64).reshape(n, hop) ** 2).mean(1)) + 1e-9)
    quiet = e < np.percentile(e, 95) - drop_db
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * hop / rate >= min_len:
                out.append((i * hop / rate, j * hop / rate))
            i = j
        else:
            i += 1
    return out


def snap_words(words: list, sil: list[tuple[float, float]], reach: float = 0.45) -> tuple[list, int]:
    """Move the word that follows each silence onto the real speech onset; keep the word before it out of the silence.

    Returns (new words, number of cues moved by more than 40 ms).

    Example:
        words, moved = snap_words(words, silences(pcm, 44100))
    """
    w = list(words)
    if not w:
        return w, 0
    starts = np.array([x.start for x in w])
    moved = 0
    last = max(x.end for x in w)
    for a, b in sil:
        if b - a < 0.2 or b >= last - 0.02 and not np.any(starts >= b - 0.02):
            continue                                        # too short, or the trailing silence (no word follows)
        cand = np.where(starts >= a + 0.5 * (b - a) - reach)[0]
        cand = cand[np.abs(starts[cand] - b) <= reach]
        if len(cand) == 0:
            continue
        n = int(cand[np.argmin(np.abs(starts[cand] - b))])
        d = b - w[n].start
        if abs(d) > 0.04:
            moved += 1
        nxt = w[n + 1].start if n + 1 < len(w) else np.inf
        end = min(max(w[n].end + d, b + 0.05), nxt) if nxt > b + 0.05 else w[n].end
        w[n] = replace(w[n], start=b, end=max(end, b + 0.01))
        starts[n] = b
        if n > 0 and w[n - 1].end > a:                       # previous word really ended when the silence began
            p = w[n - 1]
            lo = w[n - 2].end if n > 1 else 0.0
            dur = min(max(p.end - p.start, 0.12), 0.45)
            s = p.start if p.start < a - 0.08 else max(lo, a - dur)
            w[n - 1] = replace(p, start=min(s, a - 0.01), end=a)
            starts[n - 1] = w[n - 1].start
    for i in range(1, len(w)):                               # never let cues run backwards
        if w[i].start < w[i - 1].start:
            w[i] = replace(w[i], start=w[i - 1].start)
            w[i] = replace(w[i], end=max(w[i].end, w[i].start))
    return w, moved


def stretch(x: np.ndarray, words: list, rate: int, breaks: list[tuple[int, float]], lead_in: float = 0.0,
            sil: list[tuple[float, float]] | None = None, tail: float = 0.0) -> tuple[np.ndarray, list, float]:
    """Insert extra silence before the words listed in `breaks` [(word index, seconds)], inside the real pause there.

    Each cut lands in the middle of the detected silence that ends at that word, so no speech is split.
    Breaks with no real silence are skipped. `tail` appends silence. Returns (audio, shifted words, seconds
    added before the last word).

    Example:
        audio, words, added = stretch(pcm, words, 44100, [(12, 0.5), (40, 1.5)], lead_in=4.0)
    """
    sil = silences(x, rate, min_len=0.08) if sil is None else sil
    ends = np.array([b for _, b in sil]) if sil else np.zeros(0)
    cuts: list[tuple[float, float, int]] = []                # (time, seconds, first shifted word)
    for idx, sec in sorted(breaks):
        if sec <= 0 or not 0 < idx < len(words) or len(ends) == 0:
            continue
        k = int(np.argmin(np.abs(ends - words[idx].start)))
        a, b = sil[k]
        if abs(b - words[idx].start) > 0.2:
            continue
        cuts.append((0.5 * (a + b), sec, idx))
    fade = int(rate * 0.008)
    parts, pos, shift, out = [], 0, lead_in, list(words)
    shifts = np.full(len(words), lead_in)
    if lead_in > 0:
        parts.append(np.zeros(int(round(lead_in * rate)), x.dtype))
    for t, sec, idx in cuts:
        cut = int(round(t * rate))
        seg = x[pos:cut].copy()
        if len(seg) > fade:
            seg[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=x.dtype)
        parts += [seg, np.zeros(int(round(sec * rate)), x.dtype)]
        pos = cut
        shift += round(sec * rate) / rate
        shifts[idx:] = shift
    tail_sec, tail = tail, x[pos:].copy()
    if cuts and len(tail) > fade:
        tail[:fade] *= np.linspace(0.0, 1.0, fade, dtype=x.dtype)
    parts.append(tail)
    if tail_s := max(tail_sec, 0.0):
        parts.append(np.zeros(int(round(tail_s * rate)), x.dtype))
    out = [replace(w, start=w.start + s, end=w.end + s) for w, s in zip(words, shifts)]
    return np.concatenate(parts), out, float(shift)
