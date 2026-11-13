"""Character alignment → words → SRT / JSON writers."""

from __future__ import annotations

import json
from pathlib import Path

from aion.sync.cue import Word, fmt_srt_time

__all__ = ["words_from_alignment", "write_word_srt", "write_words_json", "write_subtitles"]


def words_from_alignment(align: dict, offset: float = 0.0) -> list[Word]:
    """Group characters into whitespace-separated words (punctuation stays attached)."""
    chars = align["characters"]
    starts = align["character_start_times_seconds"]
    ends = align["character_end_times_seconds"]
    out: list[Word] = []
    buf, s0, e0 = "", None, None
    for ch, a, b in zip(chars, starts, ends):
        if ch.isspace():
            if buf:
                out.append(Word(buf, offset + s0, offset + e0))
            buf, s0, e0 = "", None, None
            continue
        if not buf:
            s0 = a
        buf += ch
        e0 = b
    if buf:
        out.append(Word(buf, offset + s0, offset + e0))
    return out


def write_word_srt(words: list[Word], path: Path) -> None:
    """cue-per-word.srt: exactly one word per cue."""
    path.write_text("\n".join(
        f"{i}\n{fmt_srt_time(w.start)} --> {fmt_srt_time(max(w.end, w.start + 0.001))}\n{w.text}\n"
        for i, w in enumerate(words, 1)), encoding="utf-8")


def write_words_json(words: list[Word], path: Path) -> None:
    path.write_text(json.dumps([{"id": f"w{i}", "text": w.text, "start": round(w.start, 3),
                                 "end": round(w.end, 3)} for i, w in enumerate(words)], indent=0),
                    encoding="utf-8")


def _balanced_split(ws: list[Word], max_chars: int) -> list[list[Word]]:
    """Split one sentence into the fewest cues of ≤ max_chars, evening out their lengths (no orphan tail word)."""
    n = len(ws)
    size = lambda i, j: sum(len(w.text) for w in ws[i:j]) + (j - i - 1)  # noqa: E731  chars of ws[i:j]
    if n <= 1 or size(0, n) <= max_chars:
        return [ws]
    INF = float("inf")
    for k in range(2, n + 1):
        # best[j][i] = smallest possible longest cue when the first i words make j cues; cut[j][i] = last cue start
        best = [[INF] * (n + 1) for _ in range(k + 1)]
        cut = [[0] * (n + 1) for _ in range(k + 1)]
        best[0][0] = 0
        for j in range(1, k + 1):
            for i in range(1, n + 1):
                for s in range(j - 1, i):
                    piece = size(s, i)
                    if piece > max_chars and i - s > 1:
                        continue
                    v = max(best[j - 1][s], piece)
                    if v < best[j][i]:
                        best[j][i], cut[j][i] = v, s
        if best[k][n] < INF:
            out, i = [], n
            for j in range(k, 0, -1):
                s = cut[j][i]
                out.append(ws[s:i])
                i = s
            return out[::-1]
    return [[w] for w in ws]


def write_subtitles(words: list[Word], path: Path, max_chars: int = 42) -> None:
    """Viewer captions: one cue per sentence, long sentences split evenly into cues of ≤ max_chars.

    Splitting is balanced (fewest cues, lengths evened out), so a sentence never ends in a flash cue holding
    one stray word.

    Example:
        write_subtitles(words, Path("assets/subtitles.srt"))
    """
    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if w.ends_sentence:
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    cues = [c for s in sentences for c in _balanced_split(s, max_chars)]
    path.write_text("\n".join(
        f"{i}\n{fmt_srt_time(c[0].start)} --> {fmt_srt_time(c[-1].end)}\n{' '.join(x.text for x in c)}\n"
        for i, c in enumerate(cues, 1)), encoding="utf-8")
