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


# Words a caption line or cue should not end on: ending there strands the phrase ("…is minus the | identity").
_WEAK = frozenset("a an the to of and or but nor in on at by for with from into onto as is are was were be its "
                  "their his her your our my this that these those than so if e".split())


def _chars(ws: list[Word]) -> int:
    return sum(len(w.text) for w in ws) + len(ws) - 1


def _break_cost(w: Word) -> float:
    """How bad it is to end a line or a cue right after `w`: free at a sentence end, cheap at a clause."""
    if w.ends_sentence:
        return 0.0
    if w.ends_clause:
        return 1.0
    bare = w.text.lower().strip("\"'“”‘’()")
    return 3.0 + (6.0 if bare in _WEAK else 0.0)


def _layout(ws: list[Word], max_chars: int, max_lines: int) -> tuple[float, list[list[Word]]] | None:
    """Best line layout for one cue, as (cost, lines), or None if it can't fit.

    A sentence may end inside a two-line cue only at the line break, so each line reads as a whole thought."""
    inner = [i for i, w in enumerate(ws[:-1]) if w.ends_sentence]
    if not inner and _chars(ws) <= max_chars:
        return 0.0, [ws]
    if max_lines < 2 or len(inner) > 1:
        return None
    best = None
    for k in range(1, len(ws)):
        if inner and k - 1 != inner[0]:
            continue
        a, b = ws[:k], ws[k:]
        la, lb = _chars(a), _chars(b)
        if la > max_chars or lb > max_chars:
            continue
        cost = _break_cost(ws[k - 1]) + 2.0 * abs(la - lb) / max_chars
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best


def write_subtitles(words: list[Word], path: Path, max_chars: int = 42, max_lines: int = 2,
                    min_dur: float = 1.2, max_dur: float = 6.5, max_cps: float = 20.0,
                    gap: float = 0.6, linger: float = 0.4) -> None:
    """Viewer captions: cues of up to `max_lines` lines of ≤ `max_chars`, broken where a reader would pause.

    A cost search over the whole word list picks the cues. Breaks are free at sentence ends, cheap at commas, and
    expensive after weak words ("the", "of", "to"…), so phrases stay together. Two sentences share a cue only when
    both are whole, one per line. Flash cues shorter than `min_dur`
    are penalized, so a short sentence like "Swallow a pill." joins its neighbor. So are cues longer than `max_dur`
    or faster than `max_cps` characters per second. A cue never spans a silence of `gap` seconds or more after a
    sentence end, so captions follow the paragraph pauses. Each cue lingers up to `linger` s after its last word, ending before
    the next one starts.

    Example:
        write_subtitles(words, Path("assets/subtitles.srt"))
    """
    n = len(words)
    INF = float("inf")
    best, back, lines = [0.0] + [INF] * n, [0] * (n + 1), [None] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            if i < j - 1 and words[i].ends_sentence and words[i + 1].start - words[i].end >= gap:
                break                                            # this cue would span a paragraph pause
            # (mid-sentence "gaps" are skipped: aligners often stamp a sentence's last word late)
            ws = words[i:j]
            if _chars(ws) > max_chars * max_lines and i < j - 1:
                break
            lay = _layout(ws, max_chars, max_lines)
            if lay is not None and len(lay[1]) > 1 and lay[1][0][-1].ends_sentence and not (
                    ws[-1].ends_sentence and (i == 0 or words[i - 1].ends_sentence)):
                lay = None                                       # two sentences share a cue only if both are whole
            if lay is None:
                if i == j - 1:                                   # a single over-long word still gets a cue
                    lay = (0.0, [ws])
                else:
                    continue
            dur = ws[-1].end - ws[0].start
            cost = best[i] + 1.0 + lay[0] + _break_cost(ws[-1])
            cost += 8.0 * max(0.0, min_dur - dur) + 4.0 * max(0.0, dur - max_dur)
            cost += 0.5 * max(0.0, _chars(ws) / max(dur, 0.3) - max_cps)
            if cost < best[j]:
                best[j], back[j], lines[j] = cost, i, lay[1]
    cues, j = [], n
    while j > 0:
        cues.append(lines[j])
        j = back[j]
    cues.reverse()
    out = []
    for k, cue in enumerate(cues):
        start, last = cue[0][0].start, cue[-1][-1].end
        nxt = cues[k + 1][0][0].start if k + 1 < len(cues) else INF
        end = max(min(last + linger, nxt - 0.05), min(last, nxt))   # aligned words can overlap: never overlap cues
        text = "\n".join(" ".join(w.text for w in line) for line in cue)
        out.append(f"{k + 1}\n{fmt_srt_time(start)} --> {fmt_srt_time(end)}\n{text}\n")
    path.write_text("\n".join(out), encoding="utf-8")
