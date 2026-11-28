"""Lint video 018's narration (plan/scenes.yaml) against the brief's writing rules.

Errors (exit code 1):
    banned words and phrases (voice.toml [lint] banned, plus their other forms)
    more than one sentence starting with "Now" in a chapter
    em or en dashes, or a spaced hyphen
    digits (numbers must be written as spoken)
    malformed [pause N] marks, or a pause before the video's first word
Warnings (listed for a human to judge):
    layout talk ("on the left", "as you can see"), symbol-by-symbol reading ("equals", "squared plus"),
    counting items aloud ("first,", "three reasons"), "Here's" openers, sentences over 32 words,
    more than two *emphasis* marks in a scene, and chapters with no scene marked as a human example.

Usage (from the repo root):
    uv run python videos/018-logarithms/scripts/lint_script.py
"""
from __future__ import annotations

import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

from ruamel.yaml import YAML

VIDEO = Path(__file__).resolve().parents[1]
PAUSE = re.compile(r"\[pause\s+(\d+(?:\.\d*)?|\.\d+)\s*s?\s*\]", re.I)
INFLECT = {  # other forms of banned words
    "strange": r"strange(ly|ness)?", "fascinating": r"fascinat(ing|ed|es|ion)", "magical": r"magical(ly)?",
    "delve": r"delv(e|es|ed|ing)", "journey": r"journey(s|ed|ing)?", "unlock": r"unlock(s|ed|ing)?",
    "remarkable": r"remarkabl[ey]", "profound": r"profound(ly)?", "crucial": r"crucial(ly)?",
    "stunning": r"stunning(ly)?", "realm": r"realms?",
}
LAYOUT = [r"\bon the (left|right)\b", r"\bat the (top|bottom) of\b", r"\bon[- ]screen\b", r"\bin the corner\b",
          r"\bas you can see\b", r"\byou can see (here|that)\b", r"\b(top|bottom)[- ](left|right)\b",
          r"\bthe (left|right) side\b", r"\b(above|below) (it|this|that)\b"]
SYMBOLS = [r"\bequals\b", r"\bsquared plus\b", r"\bplus\b[^.]*\bsquared\b", r"\bto the power\b",
           r"\bdivided by\b", r"\b(open|close) (bracket|paren)", r"\bsubscript\b", r"\bdelta\b", r"\btheta\b",
           r"\bover (p|q|n|x|y)\b", r"\b[a-z] (plus|minus|times) [a-z]\b"]
COUNTING = [r"(^|[.!?]\s+)(first|second|third|fourth|fifth|sixth)(ly)?,", r"\bnumber (one|two|three)\b",
            r"\b(two|three|four|five|six)( more)? (things|reasons|ideas|steps|ways|parts|properties|rules|pieces)\b"]


def spoken(text: str) -> str:
    return " ".join(PAUSE.sub(" ", str(text)).replace("*", "").split())


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", spoken(text)) if s]


def banned_patterns() -> list[tuple[str, re.Pattern]]:
    vt = tomllib.loads((VIDEO / "voice.toml").read_text())
    out = []
    for b in vt.get("lint", {}).get("banned", []):
        core = INFLECT.get(b, re.escape(b).replace("'", "['’]").replace(r"\ ", r"\s+"))
        out.append((b, re.compile(rf"(?<![\w-]){core}(?![\w-])", re.I)))
    return out


def main() -> None:
    data = YAML(typ="safe").load((VIDEO / "plan" / "scenes.yaml").read_text())
    errors, warnings = [], []
    now_count = defaultdict(list)
    banned = banned_patterns()
    for i, s in enumerate(data["scenes"]):
        sid, raw = s["id"], " ".join(str(s["narration"]).split())
        text = spoken(raw)
        for word, pat in banned:
            for m in pat.finditer(text):
                errors.append(f"{sid}: banned {word!r}: …{text[max(0, m.start() - 30):m.end() + 30]}…")
        for sent in sentences(raw):
            if re.match(r"now\b", sent, re.I):
                now_count[s["chapter"]].append(sid)
            n = len(sent.split())
            if n > 32:
                warnings.append(f"{sid}: long sentence ({n} words): {sent[:70]}…")
        if re.search(r"[—–]| - ", raw):
            errors.append(f"{sid}: dash in narration")
        for m in re.finditer(r"\d", PAUSE.sub("", raw)):
            errors.append(f"{sid}: digit in narration near …{raw[max(0, m.start() - 20):m.end() + 20]}…")
        stripped = PAUSE.sub("", raw)
        if "[" in stripped or "]" in stripped:
            errors.append(f"{sid}: malformed pause mark or stray bracket")
        if i == 0 and raw.lstrip().lower().startswith("[pause"):
            errors.append(f"{sid}: pause before the first word does nothing (use [pacing] lead_in)")
        for kind, pats in (("layout talk", LAYOUT), ("symbol reading", SYMBOLS), ("counting aloud", COUNTING)):
            for p in pats:
                for m in re.finditer(p, text, re.I):
                    warnings.append(f"{sid}: {kind}: …{text[max(0, m.start() - 25):m.end() + 25]}…")
        for m in re.finditer(r"\bhere(['’]s| is)\b", text, re.I):
            warnings.append(f"{sid}: 'Here's' opener: …{text[m.start():m.end() + 40]}…")
        emph = len(re.findall(r"\*[^*]+\*", raw))
        if emph > 2:
            warnings.append(f"{sid}: {emph} emphasis marks (keep it to one or two)")
    for ch, sids in now_count.items():
        if len(sids) > 1:
            errors.append(f"chapter {ch}: {len(sids)} sentences start with 'Now' ({', '.join(sids)}); at most one")
    for ch in data["chapters"]:
        if ch["id"] in ("cold", "intro", "outro"):
            continue
        scenes = [s for s in data["scenes"] if s["chapter"] == ch["id"]]
        if not any("human" in (s.get("retention_device", "") + s.get("goal", "")).lower() for s in scenes):
            warnings.append(f"chapter {ch['id']}: no scene is marked as a human example")

    for e in errors:
        print("✘", e)
    for w in warnings:
        print("⚠", w)
    print(f"{len(errors)} errors, {len(warnings)} warnings · 'Now' sentences per chapter: "
          + ", ".join(f"{k} {len(v)}" for k, v in now_count.items()))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
