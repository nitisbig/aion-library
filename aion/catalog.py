"""API catalog built from exports + signatures + docstrings (what `aion catalog` prints).

Agents query this instead of reading source:

    uv run aion catalog bloom          # one line per match
    uv run aion catalog layer --full   # with docstring examples
"""

from __future__ import annotations

import importlib
import inspect
import re
from dataclasses import asdict, dataclass

__all__ = ["Entry", "entries", "search", "render_lines", "build_llms"]


# Docs for exported plain values (dicts, lists, proxies) that cannot carry a docstring.
VALUE_DOCS = {
    "C": "Active theme tokens: C.bg, C.text, C.accent, C.<your role>, sizes, lead, bloom… (read at call time).\n\n"
         "Example:\n    Dot(color=C.accent); Text(\"hi\", font_size=C.label_size)",
    "EASES": "Named easing curves accepted by every `ease=`: smooth, easy_ease, snap, out_back, spring, …\n\n"
             "Example:\n    sorted(EASES)",
    "BLEND_MODES": "Layer `blend=` names: normal, add, screen (fast GL) + multiply, overlay, soft_light, difference, "
                   "lighten, darken, color_dodge (shader).\n\nExample:\n    s.add(PointsLayer(fn, blend=\"add\"))",
}


@dataclass
class Entry:
    name: str
    module: str
    kind: str
    signature: str
    summary: str
    example: str
    doc: str


def _sig(obj) -> str:
    try:
        target = obj.__init__ if inspect.isclass(obj) and "__init__" in obj.__dict__ else obj
        s = str(inspect.signature(target))
        s = s.replace("(self, ", "(").replace("(self)", "()")
        s = re.sub(r"<function (\w+)[^>]*>", r"\1", s)
        s = re.sub(r"<[^>]+>", "…", s)
        return s if len(s) < 220 else s[:217] + "…)"
    except (TypeError, ValueError):
        return ""


def _example(doc: str) -> str:
    m = re.search(r"Example:\s*\n((?:\s{4,}.*\n?)+)", doc)
    return "\n".join(l.strip() for l in m.group(1).splitlines() if l.strip()) if m else ""


def entries() -> list[Entry]:
    import aion

    out = []
    for name, mod in sorted(aion.registry().items(), key=lambda kv: (kv[1], kv[0])):
        try:
            obj = getattr(importlib.import_module(mod), name)
        except Exception as e:  # pragma: no cover
            out.append(Entry(name, mod, "error", "", f"import failed: {e}", "", ""))
            continue
        doc = inspect.getdoc(obj) or ""
        if inspect.isclass(obj):
            kind, sig = "class", _sig(obj)
        elif inspect.isroutine(obj) or inspect.isfunction(getattr(obj, "__wrapped__", None)):
            kind, sig = "function", _sig(obj)   # incl. lru_cache-wrapped functions
        else:
            kind, sig = "value", ""
            doc = VALUE_DOCS.get(name) or (doc if obj.__class__.__module__.startswith("aion") else "")
        summary = doc.strip().split("\n\n")[0].replace("\n", " ") if doc else ""
        out.append(Entry(name, mod.replace("aion.", ""), kind, sig, summary, _example(doc), doc))
    return out


def search(query: str | None = None) -> list[Entry]:
    es = entries()
    if not query:
        return es
    q = query.lower()
    exact = [e for e in es if e.name.lower() == q]
    rest = [e for e in es if e not in exact and (q in e.name.lower() or q in e.summary.lower() or q in e.module)]
    return exact + rest


def render_lines(es: list[Entry], full: bool = False) -> str:
    lines = []
    for e in es:
        head = f"{e.name}{e.signature}" if e.kind != "value" else e.name
        lines.append(f"{head}  # {e.summary}  [{e.module}]" if e.summary else f"{head}  [{e.module}]")
        if full and e.example:
            lines += ["    " + l for l in e.example.splitlines()]
    return "\n".join(lines)


def build_llms(root) -> tuple[str, str]:
    """(llms.txt API section, llms-full.txt) generated from the live package + docs."""
    from pathlib import Path

    root = Path(root)
    es = entries()
    groups: dict[str, list[Entry]] = {}
    for e in es:
        groups.setdefault(e.module.split(".")[0], []).append(e)
    api = []
    for g, items in groups.items():
        api.append(f"\n### aion.{g}")
        for e in items:
            sig = e.signature if e.kind != "value" else ""
            api.append(f"- `{e.name}{sig}`: {e.summary}" if e.summary else f"- `{e.name}{sig}`")
    api_text = "\n".join(api).strip() + "\n"
    full = []
    for name in ("AGENTS.md", "CHEATSHEET.md"):
        p = root / name
        if p.exists():
            full.append(f"\n\n<!-- ===== {name} ===== -->\n\n" + p.read_text())
    for p in sorted((root / "docs").glob("*.md")):
        full.append(f"\n\n<!-- ===== docs/{p.name} ===== -->\n\n" + p.read_text())
    full.append("\n\n<!-- ===== API reference (generated) ===== -->\n")
    for e in es:
        full.append(f"\n## {e.name}{e.signature}  [{e.module}]\n\n{e.doc or e.summary}\n")
    return api_text, "".join(full)


def as_json(es: list[Entry]) -> list[dict]:
    return [asdict(e) for e in es]
