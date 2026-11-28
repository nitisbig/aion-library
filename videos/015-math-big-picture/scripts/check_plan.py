"""Self-review for video 015: the brief's checklist (section 11) plus the plan's own checks, as pass / fail.

Runs at any stage. Before voicing, times are estimates from plan/scenes.yaml (build_script.py's model); once
scripts/timing.py has written plan/timing.json, real scene and cue times are used. Checks whose inputs do not
exist yet (subtitles, style frames, timing) report "pending" and do not fail.

    ✔ pass   ✘ fail (exit code 1)   … pending   ⚠ needs a human look

Usage (from the repo root):
    uv run python videos/015-math-big-picture/scripts/check_plan.py [--wpm 166]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ruamel.yaml import YAML

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_script as bs  # noqa: E402
import lint_script as ls  # noqa: E402

VIDEO = bs.VIDEO
ARC = ["hook", "intuition", "formalization", "worked_example", "sighting", "takeaway"]
PILLAR_CHAPTERS = ["foundations", "quantity", "structure", "space", "change", "uncertainty"]
results: list[tuple[str, str, str]] = []


def report(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))


def estimated_times(data: dict, wpm: float) -> tuple[list[dict], float, str]:
    """Per scene: start, end, and the time of each reveal cue. From timing.json when it exists."""
    tj = VIDEO / "plan" / "timing.json"
    if tj.exists():
        t = json.loads(tj.read_text())
        return t["scenes"], t["total_s"], "timing.json (audio)"
    rows, out = bs.plan(data, wpm), []
    for r in rows:
        s = r["scene"]
        text = r["text"]
        # time of each word: speech so far plus inline pauses that come before it
        tokens, clock, times = re.split(r"(\[pause[^\]]*\])", text), r["start"], []
        for tok in tokens:
            m = bs.PAUSE.fullmatch(tok.strip()) if tok.strip().startswith("[pause") else None
            if m:
                clock += float(m.group(1))
                continue
            for _ in bs.WORD.findall(tok.replace("*", "")):
                times.append(clock)
                clock += 60.0 / wpm
        ws, pos, cues = bs.words(text), -1, []
        for st in s["visual"].get("reveal_sequence") or []:
            ph = bs.words(st["at_word"])
            hit = next((i for i in range(pos + 1, len(ws) - len(ph) + 1) if ws[i:i + len(ph)] == ph), None)
            if hit is not None:
                pos = hit
                cues.append({"at_word": st["at_word"], "t": times[hit]})
        out.append({"id": s["id"], "chapter": s["chapter"], "start": r["start"], "end": r["start"] + r["est"],
                    "cues": cues})
    return out, out[-1]["end"], f"estimate at {wpm:g} wpm"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wpm", type=float, default=166.0)
    a = ap.parse_args()
    data = YAML(typ="safe").load((VIDEO / "plan" / "scenes.yaml").read_text())
    scenes = data["scenes"]
    order = {s["id"]: i for i, s in enumerate(scenes)}
    timed, total, source = estimated_times(data, a.wpm)

    # 1. runtime
    m, sec = divmod(int(round(total)), 60)
    if source.startswith("timing"):
        report("✔" if total >= 22 * 60 else "✘", "Total runtime from timing.json ≥ 22:00", f"{m}:{sec:02d}")
    else:
        report("…", "Total runtime from timing.json ≥ 22:00",
               f"no timing.json yet; estimate {m}:{sec:02d} ({'above' if total >= 1320 else 'BELOW'} 22:00)")

    # 2. every scene complete
    missing = []
    for s in scenes:
        v = s.get("visual") or {}
        need = {"narration": s.get("narration"), "visual.description": v.get("description"),
                "reveal_sequence": v.get("reveal_sequence"), "engines": (s.get("engines") or {}).get("primary"),
                "engine_reason": s.get("engine_reason"), "retention_device": s.get("retention_device"),
                "transition_out": s.get("transition_out"), "sfx_music": s.get("sfx_music")}
        missing += [f"{s['id']}.{k}" for k, val in need.items() if not val]
    report("✘" if missing else "✔", "Every scene has narration, visual, engine + reason, retention device, transition",
           ", ".join(missing) or f"{len(scenes)} scenes")

    # 3. banned words (count)
    hits = sum(len(p.findall(ls.spoken(s["narration"]))) for s in scenes for _, p in ls.banned_patterns())
    report("✔" if hits == 0 else "✘", "No banned words", f"{hits} found")

    # 4. layout talk / symbol reading
    flagged = []
    for s in scenes:
        text = ls.spoken(s["narration"])
        for p in ls.LAYOUT + ls.SYMBOLS:
            flagged += [f"{s['id']}: …{text[max(0, x.start() - 20):x.end() + 20]}…" for x in re.finditer(p, text, re.I)]
    report("✔" if not flagged else "⚠", "No narration describes layout or reads an equation symbol by symbol",
           "; ".join(flagged) or "0 lines flagged by the lint heuristics")

    # 5. loops planted before paid, all paid; map at every chapter boundary
    bad = []
    for lp in data["loops"]:
        plant = max(order[x] for x in lp["planted_in"])
        pay = min(order[x] for x in lp["paid_in"])
        if not lp["paid_in"] or pay <= min(order[x] for x in lp["planted_in"]):
            bad.append(f"{lp['id']} paid before planted")
        if plant > max(order[x] for x in lp["paid_in"]):
            bad.append(f"{lp['id']} last plant after last payoff")
    no_map = []
    for ch in data["chapters"]:
        rs = [s for s in scenes if s["chapter"] == ch["id"]]
        if ch["id"] in ("cold", "outro") or not rs:
            continue
        if not any(s.get("map_update") for s in rs) or (ch["id"] != "connects" and not rs[-1].get("map_update")):
            no_map.append(ch["id"])
    for e in data["map_edges"]:
        mu = next(s for s in scenes if s["id"] == e["lit_in"]).get("map_update") or {}
        if not any({e["a"], e["b"]} == set(pair) for pair in mu.get("edges") or []):
            no_map.append(f"edge {e['a']}-{e['b']} missing from {e['lit_in']}.map_update")
    report("✘" if bad or no_map or len(data["loops"]) < 2 else "✔",
           "Open loops paid off; Map of Math at every chapter boundary",
           "; ".join(bad + no_map) or f"{len(data['loops'])} loops, each planted before paid; map update closes "
           f"every chapter; {len(data['map_edges'])} chords each lit where listed")

    # 6. subtitles
    srt = VIDEO / "subtitles" / "full.srt"
    if srt.exists():
        viol = check_srt(srt)
        report("✘" if viol else "✔", "Subtitle cues: ≤ 42 chars/line, ≤ 2 lines, 1–6 s", "; ".join(viol[:8]) or "0 violations")
    else:
        report("…", "Subtitle cues: ≤ 42 chars/line, ≤ 2 lines, 1–6 s", "subtitles/full.srt not generated yet")

    # 7. style frames
    frames = sorted((VIDEO / "design" / "style_frames").glob("*.png"))
    report("⚠" if len(frames) >= 8 else "…", "Style frames match the design sheet",
           f"{len(frames)} PNGs; compare by eye with design/design_sheet.md" if frames else "no style frames yet")

    # 8. retention: interrupts ≤ 60 s apart, visual change ≤ 20 s, recap per chapter, arc order, 15–45 s scenes
    starts = [t["start"] for t, s in zip(timed, scenes) if s.get("interrupt")]
    gaps = [b - a for a, b in zip(starts, starts[1:] + [total])]
    worst = max(gaps)
    report("✔" if worst <= 60 else "✘", "Pattern interrupt every 40–60 s", f"longest gap {worst:.0f} s ({source})")
    events = sorted({0.0, total} | {t["start"] for t in timed} | {c["t"] for t in timed for c in t["cues"]})
    still = max((b - a, a) for a, b in zip(events, events[1:]))
    report("✔" if still[0] <= 20 else "✘", "No more than 20 s without visual change",
           f"longest still stretch {still[0]:.1f} s at {still[1] / 60:.0f}:{still[1] % 60:04.1f} ({source})")
    arc_bad, recap_bad = [], []
    for ch in PILLAR_CHAPTERS:
        steps = [arcs(s) for s in scenes if s["chapter"] == ch]
        idx = [next((i for i, st in enumerate(steps) if x in st), -1) for x in ARC]
        if -1 in idx or idx != sorted(idx):
            arc_bad.append(f"{ch}: {steps}")
    for ch in data["chapters"]:
        if ch["id"] in PILLAR_CHAPTERS + ["connects"]:
            last = [s for s in scenes if s["chapter"] == ch["id"]][-1]
            if not ch.get("takeaway") or "takeaway" not in arcs(last):
                recap_bad.append(ch["id"])
    report("✘" if arc_bad else "✔", "Each chapter: hook → intuition → formalization → worked example → sighting → takeaway",
           "; ".join(arc_bad) or "all six pillar chapters in order")
    report("✘" if recap_bad else "✔", "A one-sentence recap ends each chapter", ", ".join(recap_bad) or "7 chapters")
    durs = [t["end"] - t["start"] for t in timed]
    off = [f"{t['id']} {d:.0f} s" for t, d in zip(timed, durs) if not 15 <= d <= 45.5]
    report("✘" if off else "✔", "Scenes of 15–45 s", ", ".join(off) or f"{min(durs):.0f}–{max(durs):.0f} s ({source})")

    # 9. cues resolve
    errs = [e for s in scenes for e in bs.check_cues(s)]
    report("✘" if errs else "✔", "Every at_word cue appears in its narration, in order", "; ".join(errs) or
           f"{sum(len(s['visual'].get('reveal_sequence') or []) for s in scenes)} cues")

    width = max(len(n) for _, n, _ in results)
    for st, name, detail in results:
        print(f"{st} {name:<{width}}  {detail}")
    sys.exit(1 if any(st == "✘" for st, _, _ in results) else 0)


def arcs(scene: dict) -> list[str]:
    """A scene's arc steps (arc_step may be one step or a list, for a scene that does two jobs)."""
    a = scene["arc_step"]
    return list(a) if isinstance(a, list) else [a]


def check_srt(path: Path) -> list[str]:
    """Violations of the brief's subtitle limits in an SRT file."""
    out = []
    blocks = [b for b in re.split(r"\n\s*\n", path.read_text().strip()) if b.strip()]
    ts = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")

    def sec(x: str) -> float:
        h, m_, s_, ms = map(int, ts.match(x).groups())
        return h * 3600 + m_ * 60 + s_ + ms / 1000

    for b in blocks:
        lines = b.splitlines()
        t0, t1 = [p.strip() for p in lines[1].split("-->")]
        d, text = sec(t1) - sec(t0), lines[2:]
        if not 1.0 <= d <= 6.0:
            out.append(f"cue {lines[0]}: {d:.2f} s")
        if len(text) > 2:
            out.append(f"cue {lines[0]}: {len(text)} lines")
        out += [f"cue {lines[0]}: {len(t)} chars" for t in text if len(t) > 42]
    return out


if __name__ == "__main__":
    main()
