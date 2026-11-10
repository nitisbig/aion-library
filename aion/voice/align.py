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


def write_subtitles(words: list[Word], path: Path, max_chars: int = 42) -> None:
    """Viewer captions: cues of ≤ max_chars, breaking after sentence punctuation."""
    cues, cur = [], []
    for w in words:
        if cur and len(" ".join(x.text for x in cur + [w])) > max_chars:
            cues.append(cur)
            cur = []
        cur.append(w)
        if w.ends_sentence:
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    path.write_text("\n".join(
        f"{i}\n{fmt_srt_time(c[0].start)} --> {fmt_srt_time(c[-1].end)}\n{' '.join(x.text for x in c)}\n"
        for i, c in enumerate(cues, 1)), encoding="utf-8")
