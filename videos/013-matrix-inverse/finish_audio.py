"""Free post-pass on the generated narration: repairs two word cues, then rebuilds subtitles at natural phrase breaks.

Run after `aion voice` (it costs no credits and is safe to run twice):

    uv run python videos/013-matrix-inverse/finish_audio.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
MAX_LINE = 42
MAX_CUE_SECONDS = 6.0
MAX_CPS = 20.0
MIN_CUE_SECONDS = 1.0
HOLD = 0.25          # subtitles linger this long after the last word
GAP = 0.04

# Measured from the waveform: the aligner pushed these words into the pause that follows them.
CUE_FIXES = [(1470, "back.", 511.12, 511.38), (1471, "But", 512.10, 512.24), (1472, "remember", 512.32, 512.72),
             (1558, "true.", 544.86, 545.18), (1559, "But", 545.70, 545.86)]

WEAK_END = {"a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "from", "with", "and", "or", "but", "that", "this",
            "these", "those", "its", "their", "our", "your", "my", "is", "are", "be", "can", "has", "have", "it's", "you",
            "we", "they", "it", "each", "every", "one", "two", "four", "if", "as", "so", "than", "not", "no", "very"}
GOOD_START = {"and", "or", "but", "so", "yet", "that", "which", "who", "how", "where", "when", "while", "if", "because", "since",
              "to", "of", "in", "on", "from", "with", "by", "for", "as", "until", "then"}


def stamp(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def bare(word: str) -> str:
    return re.sub(r"[^a-z']", "", word.lower().replace("’", "'"))


def break_cost(words: list[dict], i: int) -> float:
    """Cost of a break after words[i]: 0 at punctuation, low before a connective, high inside a phrase."""
    text = words[i]["text"]
    if text[-1] in ".?!":
        return 0.0
    if text[-1] in ":;":
        return 0.5
    if text[-1] == ",":
        return 1.0
    next_word = bare(words[i + 1]["text"]) if i + 1 < len(words) else ""
    cost = 5.0 if next_word in GOOD_START else 14.0
    return cost + (30.0 if bare(text) in WEAK_END else 0.0)


def split_lines(words: list[dict]) -> list[str] | None:
    """One or two lines of at most MAX_LINE characters, broken at the best phrase boundary."""
    text = " ".join(w["text"] for w in words)
    if len(text) <= MAX_LINE:
        return [text]
    best, lines = float("inf"), None
    for k in range(len(words) - 1):
        a, b = " ".join(w["text"] for w in words[:k + 1]), " ".join(w["text"] for w in words[k + 1:])
        if len(a) <= MAX_LINE and len(b) <= MAX_LINE:
            cost = break_cost(words, k) + abs(len(a) - len(b)) / 12
            if cost < best:
                best, lines = cost, [a, b]
    return lines


def segment(words: list[dict]) -> list[list[dict]]:
    """Best cue boundaries for one sentence, by dynamic programming."""
    n = len(words)
    best = [0.0] + [float("inf")] * n
    prev = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - 22), j):
            cue = words[i:j]
            lines = split_lines(cue)
            secs = cue[-1]["end"] - cue[0]["start"]
            if lines is None or secs > MAX_CUE_SECONDS or best[i] == float("inf"):
                continue
            chars = sum(len(x) for x in lines)
            shown = max(secs + HOLD, 0.01)
            cost = 1.5 + (break_cost(words, j - 1) if j < n else 0.0)
            cost += max(0.0, chars / shown - MAX_CPS) * 3
            cost += max(0.0, MIN_CUE_SECONDS - shown) * 12
            if len(lines) == 2 and bare(lines[0].split()[-1]) in WEAK_END:
                cost += 20.0                                 # never leave a line hanging on a small word
            if best[i] + cost < best[j]:
                best[j], prev[j] = best[i] + cost, i
    cues, j = [], n
    while j > 0:
        cues.append(words[prev[j]:j])
        j = prev[j]
    return cues[::-1]


def main() -> None:
    path = ASSETS / "words.json"
    words = json.loads(path.read_text())
    for index, text, start, end in CUE_FIXES:
        assert words[index]["text"] == text, (index, text, words[index]["text"])
        words[index]["start"], words[index]["end"] = start, end
    path.write_text(json.dumps(words, ensure_ascii=False, indent=1))
    srt = "\n".join(f"{i + 1}\n{stamp(w['start'])} --> {stamp(w['end'])}\n{w['text']}\n" for i, w in enumerate(words))
    (ASSETS / "cue-per-word.srt").write_text(srt)

    sentences, current = [], []
    for w in words:
        current.append(w)
        if w["text"][-1] in ".?!":
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)

    cues = [cue for sentence in sentences for cue in segment(sentence)]
    out = []
    for i, cue in enumerate(cues):
        begin = cue[0]["start"]
        limit = cues[i + 1][0]["start"] - GAP if i + 1 < len(cues) else cue[-1]["end"] + 1.0
        finish = min(max(cue[-1]["end"] + HOLD, begin + MIN_CUE_SECONDS), limit)
        out.append(f"{i + 1}\n{stamp(begin)} --> {stamp(finish)}\n" + "\n".join(split_lines(cue)) + "\n")
    (ASSETS / "subtitles.srt").write_text("\n".join(out))
    print(f"{len(words)} words, {len(cues)} subtitle cues")


if __name__ == "__main__":
    main()
