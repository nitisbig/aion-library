"""voiceover.md → clean narration text → TTS chunks.

Rules for voiceover.md (checked by `lint`):
- Plain prose, one paragraph per idea; blank lines separate paragraphs.
- Lines starting with `#`, `>` and HTML comments `<!-- -->` are notes (not spoken).
- Write numbers and symbols the way they should be *said* ("two pi", "x squared").
- Text added after the narration was generated goes between `> [insert]` and `> [/insert]` note lines:
  it is synthesised on its own and spliced into the existing audio, so nothing already paid for is re-billed.
- `<!-- scene: <id> -->` puts the paragraphs after it in scene <id>. With `chunking = "scene"` in voice.toml,
  each scene is one TTS request (see master.py).
- `[pause 0.8s]` (or `[pause 2]`) inside a paragraph asks for that much extra silence at that point. It is cut
  out of the TTS text and inserted by the free pacing pass. Put it after punctuation, where the voice stops anyway.

voice.toml options read here (`ScriptOptions`). None of them is part of the TTS cache key:

    chunking = "scene"               # one request per scene ("pack", the default, packs 2500-char chunks)
    [aliases]                        # TTS spelling of single words; cues and captions keep the script's spelling
    Buffon = "Boo-fon"
    [lint]
    banned = ["crucial", "in fact"]  # every hit is reported (case-insensitive, whole words)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

__all__ = ["Para", "ScriptOptions", "read_paras", "read_scenes", "group_scenes", "read_breaks", "global_breaks",
           "read_script", "read_sections", "read_marked", "read_pauses", "scene_markers", "apply_aliases", "unalias",
           "chunk", "lint", "MAX_CHARS"]

MAX_CHARS = 2500

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_MARKER = re.compile(r"<!--\s*scene\s*:(.*?)-->", re.I | re.S)
_SCENE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
_SENTINEL = "\x00scene:"
_INLINE_PAUSE = re.compile(r"\[pause\s+(\d+(?:\.\d*)?|\.\d+)\s*s?\s*\]", re.I)
_NOTE_PAUSE = re.compile(r"\s*>\s*\[pause\s+([0-9.]+)\s*s?\]")
_PUNCT = tuple(".,;:!?…—–-")
_TOKEN = re.compile(r"(\W*)(.*?)(\W*)", re.S)


@dataclass(frozen=True)
class Para:
    """One spoken paragraph of voiceover.md, as `read_paras` returns it.

    `text` is what the captions show: notes, emphasis marks and inline `[pause N]` are gone.

    Example:
        p = read_paras("videos/015-x/voiceover.md")[0]; p.scene, p.text, p.breaks
    """

    text: str
    section: bool = False                         # a `# heading` precedes it
    inserted: bool = False                        # between `> [insert]` and `> [/insert]`
    scene: str | None = None                      # id of the latest `<!-- scene: id -->` marker
    pause: float = 0.0                            # extra seconds before it, from `> [pause N]` lines
    breaks: tuple[tuple[int, float], ...] = ()    # inline `[pause N]`: (index of the word after it, seconds)

    @property
    def words(self) -> list[str]:
        return self.text.split()


@dataclass(frozen=True)
class ScriptOptions:
    """Script options from voice.toml: `chunking`, `[aliases]` and `[lint] banned` (never part of the TTS cache key).

    Example:
        ScriptOptions.load(Path("videos/015-x/voice.toml")).chunking   # "pack" or "scene"
    """

    chunking: str = "pack"
    aliases: dict = field(default_factory=dict)
    banned: tuple[str, ...] = ()

    @classmethod
    def load(cls, path: str | Path | None) -> "ScriptOptions":
        if path is None or not Path(path).exists():
            return cls()
        import tomllib

        data = tomllib.loads(Path(path).read_text())
        chunking = str(data.get("chunking", "pack"))
        if chunking not in ("pack", "scene"):
            raise ValueError(f'voice.toml: chunking = "{chunking}" (use "pack" or "scene")')
        aliases = {str(k): str(v) for k, v in (data.get("aliases") or {}).items()}
        for k, v in aliases.items():
            if not k.strip() or not v.strip() or any(c.isspace() for c in k + v):
                raise ValueError(f"voice.toml [aliases]: {k!r} = {v!r}: both sides must be one word with no spaces, "
                                 "so every spoken word maps back to one script word (use a hyphen: 'Chong-jir')")
        banned = tuple(str(b) for b in (data.get("lint") or {}).get("banned", []) if str(b).strip())
        return cls(chunking, aliases, banned)


def _marker(m: re.Match) -> str:
    sid = m.group(1).strip()
    if not _SCENE_ID.fullmatch(sid):
        raise ValueError(f"bad scene marker <!-- scene:{m.group(1)}-->: the id must be one word of letters, "
                         "digits, '_', '.' or '-'")
    return f"\n\n{_SENTINEL}{sid}\n\n"


def _clean(p: str) -> str:
    p = re.sub(r"(\*\*|__|\*|`)", "", p)            # emphasis / code marks
    p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)  # links → text
    return re.sub(r"\s+", " ", p).strip()


def _split_pauses(p: str) -> tuple[str, list[tuple[int, float]]]:
    """Cut inline `[pause N]` marks out of a paragraph: (text, [(index of the word after the mark, seconds)])."""
    if "[" not in p:
        return p, []
    words: list[str] = []
    breaks: list[tuple[int, float]] = []
    pos = 0
    for m in _INLINE_PAUSE.finditer(p):
        words += p[pos:m.start()].split()
        breaks.append((len(words), float(m.group(1))))
        pos = m.end()
    if not breaks:
        return p, []
    words += p[pos:].split()
    return " ".join(words), breaks


def read_paras(path: str | Path) -> list[Para]:
    """Every spoken paragraph of a voiceover file with its scene, section, insert flag and requested pauses.

    `<!-- scene: id -->` markers are read before HTML comments are dropped, and each one also ends a paragraph.
    Inline `[pause N]` marks become `Para.breaks`. A paragraph made only of them adds to the next one's `pause`.

    Example:
        [(p.scene, p.text) for p in read_paras("videos/015-x/voiceover.md")]
    """
    text = _MARKER.sub(_marker, Path(path).read_text(encoding="utf-8"))
    text = _COMMENT.sub("", text)
    out: list[Para] = []
    heading = inserted = False
    scene: str | None = None
    pending = 0.0
    for block in re.split(r"\n\s*\n", text):
        if block.strip().startswith(_SENTINEL):
            scene = block.strip()[len(_SENTINEL):]
            continue
        heading = heading or any(l.lstrip().startswith("#") for l in block.splitlines())
        for l in block.splitlines():
            if l.lstrip().startswith(">"):
                inserted = True if "[insert]" in l else (False if "[/insert]" in l else inserted)
            m = _NOTE_PAUSE.match(l)
            if m:
                pending += float(m.group(1))
        lines = [l.strip() for l in block.splitlines()
                 if l.strip() and not l.lstrip().startswith(("#", ">", "---"))]
        if not lines:
            continue
        p = _clean(" ".join(lines))
        if not p:
            continue
        p, breaks = _split_pauses(p)
        if not p:                                   # only `[pause N]` marks: silence before the next paragraph
            pending += sum(s for _, s in breaks)
            continue
        out.append(Para(p, heading, inserted, scene, pending, tuple(breaks)))
        heading, pending = False, 0.0
    return out


def read_script(path: str | Path) -> list[str]:
    """Spoken paragraphs from a markdown voiceover file."""
    return [p.text for p in read_paras(path)]


def read_sections(path: str | Path) -> list[tuple[str, bool]]:
    """(paragraph, starts_section) pairs; a paragraph starts a section when a `# heading` precedes it."""
    return [(p.text, p.section) for p in read_paras(path)]


def read_marked(path: str | Path) -> list[tuple[str, bool, bool]]:
    """(paragraph, starts_section, inserted) triples; `inserted` is True between `> [insert]` … `> [/insert]`."""
    return [(p.text, p.section, p.inserted) for p in read_paras(path)]


def read_pauses(path: str | Path) -> list[float]:
    """Extra silence (seconds) requested before each paragraph with a `> [pause N]` line, one entry per paragraph.

    `>` lines never reach the TTS, so adding or changing a pause never re-bills; the pacing pass applies it.
    Example:
        > [pause 4]          (in voiceover.md, between two paragraphs: 4 s more silence before the next one)
    """
    return [p.pause for p in read_paras(path)]


def global_breaks(paras: list[Para]) -> list[tuple[int, float]]:
    """Inline pauses of all paragraphs as (index into the whole narration's words, seconds)."""
    out, k = [], 0
    for p in paras:
        out += [(k + i, s) for i, s in p.breaks]
        k += len(p.words)
    return out


def read_breaks(path: str | Path) -> list[tuple[int, float]]:
    """Inline `[pause N]` marks as (global word index, seconds): the silence goes right before that word.

    Example:
        read_breaks("voiceover.md")   # [(57, 0.8), (130, 2.0)]
    """
    return global_breaks(read_paras(path))


def read_scenes(path: str | Path) -> list[tuple[str, list[Para]]]:
    """Paragraphs grouped by their `<!-- scene: id -->` marker, in script order: [(scene id, [Para, …])].

    Every paragraph must follow a marker, and each id may be used once.

    Example:
        for sid, paras in read_scenes("videos/015-x/voiceover.md"): print(sid, sum(len(p.words) for p in paras))
    """
    return group_scenes(read_paras(path), Path(path).name)


def group_scenes(paras: list[Para], name: str = "the script") -> list[tuple[str, list[Para]]]:
    """`read_scenes` for paragraphs you already have (raises ValueError on an unmarked or repeated scene)."""
    out: list[tuple[str, list[Para]]] = []
    for p in paras:
        if p.scene is None:
            raise ValueError(f"{name}: a paragraph comes before the first <!-- scene: id --> marker: "
                             f"{p.text[:50]!r}")
        if out and out[-1][0] == p.scene:
            out[-1][1].append(p)
        elif any(sid == p.scene for sid, _ in out):
            raise ValueError(f"{name}: scene {p.scene!r} is used by two separate runs of paragraphs")
        else:
            out.append((p.scene, [p]))
    return out


def scene_markers(path: str | Path) -> list[str]:
    """Every scene id named by a `<!-- scene: id -->` marker, in order (scenes with no narration included)."""
    return [m.group(1).strip() for m in _MARKER.finditer(Path(path).read_text(encoding="utf-8"))]


def _swap(tok: str, table: dict[str, str]) -> str:
    lead, core, trail = _TOKEN.fullmatch(tok).groups()
    if core in table:
        return lead + table[core] + trail
    for poss in ("'s", "’s"):
        if core.endswith(poss) and core[:-2] in table:
            return lead + table[core[:-2]] + poss + trail
    return tok


def apply_aliases(text: str, aliases: dict[str, str]) -> str:
    """The TTS spelling of `text`: each word found in `aliases` is swapped, keeping its punctuation and 's.

    Matching is exact (case-sensitive) on the word without its surrounding punctuation.

    Example:
        apply_aliases("Buffon's needles.", {"Buffon": "Boo-fon"})   # "Boo-fon's needles."
    """
    if not aliases:
        return text
    return re.sub(r"\S+", lambda m: _swap(m.group(0), aliases), text)


def unalias(word: str, aliases: dict[str, str]) -> str:
    """Script spelling of one spoken word (the inverse of `apply_aliases`)."""
    return _swap(word, {v: k for k, v in aliases.items()}) if aliases else word


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


def _term(t: str) -> re.Pattern:
    """Case-insensitive pattern for a banned term, with word boundaries on its word-character ends."""
    pre = r"(?<!\w)" if re.match(r"\w", t) else ""
    post = r"(?!\w)" if re.search(r"\w$", t) else ""
    return re.compile(pre + re.escape(t) + post, re.I)


def lint(paragraphs: list[str], banned: Iterable[str] = (),
         breaks: list[Iterable[tuple[int, float]]] | None = None) -> list[str]:
    """Warnings about text that TTS will read badly, inline pauses that may not land, and banned words.

    `banned` terms are matched case-insensitively as whole words, and every hit is reported. `breaks` holds each
    paragraph's inline pauses (`Para.breaks`): a pause should follow punctuation, where the voice really stops.

    Example:
        lint([p.text for p in paras], banned=["crucial", "in fact"], breaks=[p.breaks for p in paras])
    """
    out = []
    terms = [(t, _term(t)) for t in banned if t.strip()]
    for i, p in enumerate(paragraphs, 1):
        if re.search(r"\d", p):
            out.append(f"¶{i}: digits ({re.findall(r'[^ ]*\d[^ ]*', p)[:3]}); spell numbers as spoken")
        if re.search(r"[=^_\\{}$<>|]", p):
            out.append(f"¶{i}: math/markup symbols; write how it is said")
        for s in _sentences(p):
            if len(s.split()) > 40:
                out.append(f"¶{i}: a {len(s.split())}-word sentence; split it for pacing")
        for tag in re.findall(r"\[[^\]]*\]", p):
            out.append(f"¶{i}: {tag} goes to the TTS as an audio tag (an inline pause needs seconds: [pause 0.8s])")
        words = p.split()
        for k, sec in (breaks[i - 1] if breaks and i <= len(breaks) else ()):
            mark = f"[pause {sec:g}s]"
            if k == 0 and i == 1:
                out.append(f"¶1: {mark} before the first word does nothing; use [pacing] lead_in")
            elif k >= len(words) and i == len(paragraphs):
                out.append(f"¶{i}: {mark} after the last word does nothing; use [pacing] tail")
            elif k > 0 and not words[k - 1].rstrip("\"')”’").endswith(_PUNCT):
                out.append(f"¶{i}: {mark} after {words[k - 1]!r} doesn't follow punctuation; the voice won't stop "
                           "there, so the silence may not be inserted")
        for t, rx in terms:
            for m in rx.finditer(p):
                a, b = max(0, m.start() - 25), min(len(p), m.end() + 25)
                out.append(f"¶{i}: banned {t!r}: …{p[a:b]}…")
    return out
