"""Character alignment → words → SRT / VTT / JSON writers, plus a caption-limit checker."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

from aion.sync.cue import Word, fmt_srt_time

__all__ = ["words_from_alignment", "write_word_srt", "write_words_json", "Caption", "subtitle_cues",
           "write_subtitles", "write_vtt", "srt_text", "vtt_text", "read_captions", "check_subtitles", "LIMITS"]

LIMITS = (1.0, 6.0)          # hard seconds on screen per caption (min, max)
_EPS = 0.0015                # margin so the limits still hold once times are rounded to whole milliseconds
INF = float("inf")


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


def _lines(ws: list[Word], max_chars: int, max_lines: int) -> list[list[Word]]:
    """`_layout`'s lines, or a greedy wrap when no tidy layout exists."""
    lay = _layout(ws, max_chars, max_lines)
    if lay is not None:
        return lay[1]
    out: list[list[Word]] = [[]]
    for w in ws:
        if out[-1] and _chars(out[-1] + [w]) > max_chars:
            out.append([])
        out[-1].append(w)
    return out


@dataclass
class Caption:
    """One subtitle cue: its lines of words and the seconds it is on screen.

    Example:
        [(c.start, c.end, c.text) for c in subtitle_cues(words)]
    """

    lines: list[list[Word]]
    start: float
    end: float

    @property
    def words(self) -> list[Word]:
        return [w for line in self.lines for w in line]

    @property
    def text(self) -> str:
        return "\n".join(" ".join(w.text for w in line) for line in self.lines)


def _search(words: list[Word], max_chars: int, max_lines: int, min_dur: float, max_dur: float, max_cps: float,
            gap: float) -> list[list[list[Word]]]:
    """Cost search over the whole word list: the line groups of the cheapest captioning."""
    n = len(words)
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
    groups, j = [], n
    while j > 0:
        groups.append(lines[j])
        j = back[j]
    groups.reverse()
    return groups


def _timed(groups: list[list[list[Word]]], linger: float) -> list[Caption]:
    """Each cue shows from its first word until `linger` s after its last, ending before the next one starts."""
    out = []
    for k, g in enumerate(groups):
        start, last = g[0][0].start, g[-1][-1].end
        nxt = groups[k + 1][0][0].start if k + 1 < len(groups) else INF
        end = max(min(last + linger, nxt - 0.05), min(last, nxt))   # aligned words can overlap: never overlap cues
        out.append(Caption(g, start, end))
    return out


def _split_long(lines: list[list[Word]], max_chars: int, max_lines: int, lo: float, hi: float) -> list:
    """Split a cue whose speech runs longer than `hi` at its best phrase break, recursively."""
    ws = [w for line in lines for w in line]
    if len(ws) < 2 or ws[-1].end - ws[0].start <= hi - _EPS:
        return [lines]
    best = None
    for k in range(1, len(ws)):
        a, b = ws[:k], ws[k:]
        la, lb = _layout(a, max_chars, max_lines), _layout(b, max_chars, max_lines)
        if la is None or lb is None:
            continue
        da, db = a[-1].end - a[0].start, b[-1].end - b[0].start
        cost = _break_cost(a[-1]) + la[0] + lb[0] + 2.0 * abs(da - db) / hi
        cost += 8.0 * (max(0.0, lo - da) + max(0.0, lo - db))
        if best is None or cost < best[0]:
            best = (cost, la[1], lb[1])
    if best is None:
        k = len(ws) // 2
        best = (0.0, _lines(ws[:k], max_chars, max_lines), _lines(ws[k:], max_chars, max_lines))
    return _split_long(best[1], max_chars, max_lines, lo, hi) + _split_long(best[2], max_chars, max_lines, lo, hi)


def _merge(cs: list[Caption], k: int, max_chars: int, max_lines: int, hi: float) -> list[Caption] | None:
    """Join the short cue k with the neighbour it reads with, if the result still fits; None if neither fits."""
    options = []
    for j in (k - 1, k + 1):
        if not 0 <= j < len(cs):
            continue
        a, b = min(j, k), max(j, k)
        ws = cs[a].words + cs[b].words
        if ws[-1].end - ws[0].start > hi:
            continue
        lay = _layout(ws, max_chars, max_lines)
        if lay is None:
            continue
        # prefer the neighbour across a mid-phrase break (it reads as one thought), then the closer one
        options.append((-_break_cost(cs[a].words[-1]), cs[b].start - cs[a].end, lay[0], a, b, lay[1]))
    if not options:
        return None
    *_, a, b, lines = min(options, key=lambda o: o[:3])
    return cs[:a] + [Caption(lines, cs[a].start, cs[b].end)] + cs[b + 1:]


def _borrow(cs: list[Caption], k: int, lo: float) -> None:
    """Last resort for a short cue: take the previous cue's linger, then start the next cue up to 0.5 s late."""
    c = cs[k]
    need = lo - (c.end - c.start)
    if need > 0 and k > 0 and abs(cs[k - 1].end - c.start) < 1e-6:
        p = cs[k - 1]
        give = max(0.0, min(need, p.end - max(p.start + lo, p.words[-1].end)))
        p.end -= give
        c.start -= give
        need -= give
    if need > 0 and k + 1 < len(cs) and abs(cs[k + 1].start - c.end) < 1e-6:
        n = cs[k + 1]
        give = max(0.0, min(need, n.end - n.start - lo, n.words[0].start + 0.5 - n.start))
        n.start += give
        c.end += give


def _enforce(cues: list[Caption], max_chars: int, max_lines: int, lo: float, hi: float) -> list[Caption]:
    """Hard limits: every cue is on screen between `lo` and `hi` seconds.

    A short cue first grows into free time after it, then before it. Otherwise it merges with a neighbour, or as a
    last resort borrows time from one. A cue on screen too long loses linger first and never hides a spoken word.
    """
    lo_t, hi_t = lo + _EPS, hi - _EPS
    ok = lambda c: c.end - c.start >= lo_t - 1e-9   # noqa: E731  (float slack: start = end - lo_t round-trips)
    cs = [Caption(c.lines, c.start, c.end) for c in cues]
    k, guard = 0, 0
    while k < len(cs) and guard < 10 * len(cues) + 10:
        guard += 1
        c = cs[k]
        if ok(c):
            k += 1
            continue
        prev_end = cs[k - 1].end if k else 0.0
        next_start = cs[k + 1].start if k + 1 < len(cs) else INF
        c.end = max(c.end, min(c.start + lo_t, next_start))
        if not ok(c):
            c.start = min(c.start, max(c.end - lo_t, prev_end))
        if ok(c):
            k += 1
            continue
        merged = _merge(cs, k, max_chars, max_lines, hi_t)
        if merged is not None:
            cs = merged
            k = max(0, k - 1)                                   # re-check the merged cue
            continue
        _borrow(cs, k, lo_t)
        k += 1
    for c in cs:
        if c.end - c.start > hi_t + 1e-9:
            c.end = max(c.start + hi_t, min(c.end, c.words[-1].end))
            if c.end - c.start > hi_t + 1e-9:
                c.start = c.end - hi_t
    return cs


def subtitle_cues(words: list[Word], max_chars: int = 42, max_lines: int = 2, min_dur: float = 1.2,
                  max_dur: float = 6.5, max_cps: float = 20.0, gap: float = 0.6, linger: float = 0.4,
                  limits: tuple[float, float] | None = LIMITS) -> list[Caption]:
    """The captions `write_subtitles` and `write_vtt` write: a phrase-aware cue search, then the hard limits.

    `min_dur` / `max_dur` / `max_cps` are soft targets of the search. `limits` = (min, max) seconds on screen are
    hard: longer cues are split at their best phrase break, and short ones are extended or merged (None = off).

    Example:
        [c.text for c in subtitle_cues(words)]
    """
    groups = _search(words, max_chars, max_lines, min_dur, max_dur, max_cps, gap)
    if limits:
        groups = [part for g in groups for part in _split_long(g, max_chars, max_lines, *limits)]
    cues = _timed(groups, linger)
    return _enforce(cues, max_chars, max_lines, *limits) if limits else cues


def write_subtitles(words: list[Word], path: Path, max_chars: int = 42, max_lines: int = 2,
                    min_dur: float = 1.2, max_dur: float = 6.5, max_cps: float = 20.0,
                    gap: float = 0.6, linger: float = 0.4, limits: tuple[float, float] | None = LIMITS) -> None:
    """Viewer captions (SRT): cues of up to `max_lines` lines of ≤ `max_chars`, broken where a reader would pause.

    A cost search over the whole word list picks the cues. Breaks are free at sentence ends, cheap at commas, and
    expensive after weak words ("the", "of", "to"…), so phrases stay together. Two sentences share a cue only when
    both are whole, one per line. Flash cues shorter than `min_dur`
    are penalized, so a short sentence like "Swallow a pill." joins its neighbor. So are cues longer than `max_dur`
    or faster than `max_cps` characters per second. A cue never spans a silence of `gap` seconds or more after a
    sentence end, so captions follow the paragraph pauses. Each cue lingers up to `linger` s after its last word, ending before
    the next one starts. Finally every cue is held on screen between `limits` seconds (default 1–6 s): long ones
    are split at their best phrase break, short ones extended or merged. `check_subtitles` verifies the file.

    Example:
        write_subtitles(words, Path("assets/subtitles.srt"))
    """
    path.write_text(srt_text(subtitle_cues(words, max_chars, max_lines, min_dur, max_dur, max_cps, gap, linger,
                                           limits)), encoding="utf-8")


def srt_text(cues: list[Caption]) -> str:
    """SRT file content for `cues`."""
    return "\n".join(f"{k}\n{fmt_srt_time(c.start)} --> {fmt_srt_time(c.end)}\n{c.text}\n"
                     for k, c in enumerate(cues, 1))


def vtt_text(cues: list[Caption]) -> str:
    """WebVTT file content for `cues` (`&`, `<` and `>` escaped)."""
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    stamp = lambda t: fmt_srt_time(t).replace(",", ".")  # noqa: E731
    body = "\n".join(f"{k}\n{stamp(c.start)} --> {stamp(c.end)}\n{esc(c.text)}\n" for k, c in enumerate(cues, 1))
    return "WEBVTT\n\n" + body if body else "WEBVTT\n"


def write_vtt(words: list[Word], path: Path, max_chars: int = 42, max_lines: int = 2,
              min_dur: float = 1.2, max_dur: float = 6.5, max_cps: float = 20.0,
              gap: float = 0.6, linger: float = 0.4, limits: tuple[float, float] | None = LIMITS) -> None:
    """WebVTT captions with exactly the cues of `write_subtitles` (same search, same 1–6 s hard limits).

    Example:
        write_vtt(words, Path("assets/subtitles.vtt"))
    """
    path.write_text(vtt_text(subtitle_cues(words, max_chars, max_lines, min_dur, max_dur, max_cps, gap, linger,
                                           limits)), encoding="utf-8")


_TIME = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{1,3})")


def _secs(s: str) -> float:
    m = _TIME.search(s)
    if m is None:
        raise ValueError(f"no timestamp in {s!r}")
    h, mi, se, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")) / 1000


def read_captions(path: str | Path) -> list[tuple[float, float, list[str]]]:
    """(start, end, lines) of every cue in an SRT or WebVTT file (VTT entities like &amp; decoded)."""
    text = Path(path).read_text(encoding="utf-8-sig")
    vtt = text.lstrip().startswith("WEBVTT")
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l.rstrip() for l in block.splitlines() if l.strip()]
        ti = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if ti is None:                                            # WEBVTT header, NOTE / STYLE blocks
            continue
        a, b = lines[ti].split("-->")[:2]
        body = [html.unescape(l) for l in lines[ti + 1:]] if vtt else lines[ti + 1:]
        out.append((_secs(a), _secs(b), body))
    return out


def check_subtitles(path: str | Path, max_chars: int = 42, max_lines: int = 2, min_dur: float = LIMITS[0],
                    max_dur: float = LIMITS[1]) -> list[str]:
    """Every caption-limit violation in an SRT or VTT file: line length, line count, seconds on screen, overlaps.

    Returns [] when the file passes.

    Example:
        assert not check_subtitles("videos/015-x/assets/subtitles.srt")
    """
    out, prev_end = [], None
    for n, (a, b, lines) in enumerate(read_captions(path), 1):
        at = f"cue {n} at {fmt_srt_time(a)}"
        d = b - a
        if not lines:
            out.append(f"{at}: no text")
        if d < min_dur - 1e-6:
            out.append(f"{at}: on screen {d:.3f} s, under {min_dur:g} s")
        if d > max_dur + 1e-6:
            out.append(f"{at}: on screen {d:.3f} s, over {max_dur:g} s")
        if len(lines) > max_lines:
            out.append(f"{at}: {len(lines)} lines, over {max_lines}")
        for line in lines:
            if len(line) > max_chars:
                out.append(f"{at}: {len(line)} characters, over {max_chars}: {line!r}")
        if prev_end is not None and a < prev_end - 1e-6:
            out.append(f"{at}: starts before the previous cue ends")
        prev_end = b
    return out
