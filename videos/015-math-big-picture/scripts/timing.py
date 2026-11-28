"""Real timing for video 015, from the voiced audio: plan/timing.json, real duration_s, and the delivery copies.

Reads what `uv run aion voice 015` wrote (assets/scenes.json, assets/words.json, audio/manifest.json) and:
- writes plan/timing.json: every scene's start / end on the final timeline (boundaries sit halfway through the silence
  between two scenes), its speech span, the time of each reveal cue (`at_word`), and chapter totals;
- sets `duration_s` (end - start) and `duration_source: audio` for every scene in plan/scenes.yaml, editing only those
  lines;
- writes audio/voice_settings.json (the request settings actually used, and the measured speaking rate);
- copies assets/subtitles.srt / .vtt to subtitles/full.srt / full.vtt;
- hard-links audio/full_narration.wav to assets/audio.wav (same bytes, no second copy).

Free: no credits are spent. Run after every `aion voice` (scripts/regen_scene.py does).

Usage (from the repo root):
    uv run python videos/015-math-big-picture/scripts/timing.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

from ruamel.yaml import YAML

VIDEO = Path(__file__).resolve().parents[1]
SCENES = VIDEO / "plan" / "scenes.yaml"
ASSETS = VIDEO / "assets"
AUDIO = VIDEO / "audio"


def letters(s: str) -> str:
    """Lower-case letters and digits only: the key used to match cue phrases against spoken words."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_phrase(words: list[dict], lo: int, hi: int, phrase: str) -> int | None:
    """Index of the first word in words[lo:hi] where `phrase` starts and ends on word boundaries.

    Matching is on letters only, so punctuation, emphasis and hyphenated words split into two tokens all match.
    """
    key = letters(phrase)
    for i in range(lo, hi):
        acc = ""
        for j in range(i, hi):
            acc += letters(words[j]["text"])
            if acc == key:
                return i
            if not key.startswith(acc):
                break
    return None


def cue_times(scene: dict, words: list[dict], row: dict) -> tuple[list[dict], list[str]]:
    """Time of each reveal cue, searched in order inside the scene's own words."""
    out, errs, pos = [], [], row["first_index"]
    for st in scene["visual"].get("reveal_sequence") or []:
        hit = find_phrase(words, pos, row["last_index"] + 1, st["at_word"])
        if hit is None:
            errs.append(f"{scene['id']}: cue {st['at_word']!r} not found after word {pos}")
            continue
        out.append({"at_word": st["at_word"], "t": round(words[hit]["start"], 3), "word_index": hit})
        pos = hit + 1
    return out, errs


def update_durations(timed: list[dict]) -> int:
    """Write real duration_s and duration_source: audio, touching only those two lines per scene."""
    text, changed = SCENES.read_text(), 0
    for t in timed:
        block = re.compile(
            rf"(\n  - id: {re.escape(t['id'])}\n(?:(?!\n  - id: ).)*?\n    duration_s: )([0-9.]+)"
            rf"(\n    duration_source: )(\w+)", re.S)
        m = block.search(text)
        if not m:
            sys.exit(f"duration_s / duration_source lines not found (adjacent) for {t['id']}")
        new = f"{t['end'] - t['start']:.2f}"
        if m.group(2) != new or m.group(4) != "audio":
            text = text[: m.start(2)] + new + m.group(3) + "audio" + text[m.end(4):]
            changed += 1
    SCENES.write_text(text)
    return changed


def voice_settings(words: list[dict], total: float, rows: list[dict]) -> dict:
    """The settings actually requested (from the manifest) plus measured rates."""
    cfg = tomllib.loads((VIDEO / "voice.toml").read_text())
    man = json.loads((AUDIO / "manifest.json").read_text())
    reqs = {rec["id"]: {k: rec[k] for k in ("seed", "take") if k in rec} for rec in man.get("scenes") or []}
    speech = sum(r["speech_end"] - r["speech_start"] for r in rows)   # first to last word of each scene
    return {
        "voice_id": cfg["voice_id"], "model_id": cfg["model_id"], "output_format": cfg["output_format"],
        "chunking": cfg.get("chunking"), "stitch": cfg.get("stitch"), "base_seed": cfg.get("seed"),
        "settings": cfg.get("settings", {}), "pacing": cfg.get("pacing", {}), "aliases": cfg.get("aliases", {}),
        "notes": [
            "eleven_v4 ignores voice_settings.speed; it is kept only because it is part of the cache key.",
            "Each scene is one request with the neighbouring scenes sent as previous_text / next_text.",
            "Pauses are not sent to the TTS; they are inserted afterwards by the free pacing pass.",
        ],
        "measured": {
            "words": len(words), "runtime_s": round(total, 2),
            "wpm_overall": round(len(words) / total * 60, 1),
            "wpm_within_scenes": round(len(words) / speech * 60, 1),
        },
        "per_scene_requests": reqs,
    }


def main() -> None:
    data = YAML(typ="safe").load(SCENES.read_text())
    scenes = data["scenes"]
    rows = json.loads((ASSETS / "scenes.json").read_text())
    words = json.loads((ASSETS / "words.json").read_text())
    by_id = {r["id"]: r for r in rows}
    missing = [s["id"] for s in scenes if s["id"] not in by_id]
    if missing:
        sys.exit(f"scenes with no audio in assets/scenes.json: {missing}")

    timed, errs = [], []
    for s in scenes:
        r = by_id[s["id"]]
        cues, e = cue_times(s, words, r)
        errs += e
        timed.append({"id": s["id"], "chapter": s["chapter"], "start": round(r["start"], 3), "end": round(r["end"], 3),
                      "speech_start": round(r["speech_start"], 3), "speech_end": round(r["speech_end"], 3),
                      "words": r["last_index"] - r["first_index"] + 1, "cues": cues})
    total = timed[-1]["end"]
    chapters = []
    for ch in data["chapters"]:
        rs = [t for t in timed if t["chapter"] == ch["id"]]
        if rs:
            chapters.append({"id": ch["id"], "title": ch["title"], "start": rs[0]["start"], "end": rs[-1]["end"],
                             "duration_s": round(rs[-1]["end"] - rs[0]["start"], 2), "target_s": ch.get("target_s"),
                             "words": sum(t["words"] for t in rs)})
    out = {"source": "audio", "total_s": round(total, 3), "words": len(words),
           "wpm_overall": round(len(words) / total * 60, 1), "chapters": chapters, "scenes": timed}
    (VIDEO / "plan" / "timing.json").write_text(json.dumps(out, indent=1) + "\n")

    changed = update_durations(timed)
    AUDIO.mkdir(exist_ok=True)
    (AUDIO / "voice_settings.json").write_text(json.dumps(voice_settings(words, total, rows), indent=2) + "\n")
    sub = VIDEO / "subtitles"
    sub.mkdir(exist_ok=True)
    shutil.copyfile(ASSETS / "subtitles.srt", sub / "full.srt")
    shutil.copyfile(ASSETS / "subtitles.vtt", sub / "full.vtt")
    wav = AUDIO / "full_narration.wav"
    if wav.exists() or wav.is_symlink():
        wav.unlink()
    try:
        os.link(ASSETS / "audio.wav", wav)
    except OSError:
        shutil.copyfile(ASSETS / "audio.wav", wav)

    m, sec = divmod(total, 60)
    print(f"runtime {int(m)}:{sec:05.2f}  ·  {len(words)} words  ·  {out['wpm_overall']} wpm overall")
    for c in chapters:
        cm, cs = divmod(c["duration_s"], 60)
        tgt = f"(target {c['target_s']} s)" if c.get("target_s") else ""
        print(f"  {c['id']:<12} {int(cm)}:{cs:04.1f}  {c['words']:>4} words  {tgt}")
    print(f"scenes.yaml: {changed} duration_s updated · timing.json, voice_settings.json, subtitles/, "
          f"full_narration.wav written")
    if errs:
        print("\n".join(errs))
        sys.exit(1)


if __name__ == "__main__":
    main()
