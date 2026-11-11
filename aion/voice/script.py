"""voiceover.md → clean narration text → TTS chunks.

Rules for voiceover.md (checked by `lint`):
- Plain prose, one paragraph per idea; blank lines separate paragraphs.
- Lines starting with `#`, `>` and HTML comments `<!-- -->` are notes (not spoken).
- Write numbers and symbols the way they should be *said* ("two pi", "x squared").
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = ["read_script", "read_sections", "chunk", "lint", "MAX_CHARS"]

MAX_CHARS = 2500


def read_script(path: str | Path) -> list[str]:
    """Spoken paragraphs from a markdown voiceover file."""
    return [p for p, _ in read_sections(path)]


def read_sections(path: str | Path) -> list[tuple[str, bool]]:
    """(paragraph, starts_section) pairs; a paragraph starts a section when a `# heading` precedes it."""
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    paras, heading = [], False
    for block in re.split(r"\n\s*\n", text):
        heading = heading or any(l.lstrip().startswith("#") for l in block.splitlines())
        lines = [l.strip() for l in block.splitlines()
                 if l.strip() and not l.lstrip().startswith(("#", ">", "---"))]
        if not lines:
            continue
        p = " ".join(lines)
        p = re.sub(r"(\*\*|__|\*|`)", "", p)          # emphasis / code marks
        p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)  # links → text
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            paras.append((p, heading))
            heading = False
    return paras


def _sentences(p: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", p) if s]


def chunk(paragraphs: list[str], max_chars: int = MAX_CHARS) -> list[str]:
    """Greedy-pack paragraphs (split at sentences if needed) into ≤ max_chars chunks."""
    pieces: list[str] = []
    for p in paragraphs:
        if len(p) <= max_chars:
            pieces.append(p)
            continue
        cur = ""
        for s in _sentences(p):
            if cur and len(cur) + 1 + len(s) > max_chars:
                pieces.append(cur)
                cur = s
            else:
                cur = f"{cur} {s}".strip()
        if cur:
            pieces.append(cur)
    chunks: list[str] = []
    for piece in pieces:
        if chunks and len(chunks[-1]) + 2 + len(piece) <= max_chars:
            chunks[-1] = chunks[-1] + "\n\n" + piece
        else:
            chunks.append(piece)
    return chunks


def lint(paragraphs: list[str]) -> list[str]:
    """Warnings about text that TTS will read badly."""
    out = []
    for i, p in enumerate(paragraphs, 1):
        if re.search(r"\d", p):
            out.append(f"¶{i}: digits ({re.findall(r'[^ ]*\d[^ ]*', p)[:3]}); spell numbers as spoken")
        if re.search(r"[=^_\\{}$<>|]", p):
            out.append(f"¶{i}: math/markup symbols; write how it is said")
        for s in _sentences(p):
            if len(s.split()) > 40:
                out.append(f"¶{i}: a {len(s.split())}-word sentence; split it for pacing")
    return out
