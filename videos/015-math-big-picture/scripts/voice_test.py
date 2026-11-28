"""Voice a few scenes of video 015 as a test: check pronunciations by ear and measure the voice's real rate.

Each test clip is one scene requested exactly as the full run would request it (same TTS text, aliases applied,
same neighbours for stitching, same seed), optionally with a different `speed`. Clips land in audio/voice_test/
and the TTS cache, so a test at the final settings is a free cache hit for the full run later.

Without --yes nothing is requested: it prints what would be billed. Spending credits needs the user's OK.

Usage (from the repo root):
    uv run python videos/015-math-big-picture/scripts/voice_test.py                       # show the cost
    uv run python videos/015-math-big-picture/scripts/voice_test.py --yes                 # voice ch3_s05, ch6_s05
    uv run python videos/015-math-big-picture/scripts/voice_test.py --scene ch6_s05 --speed 0.86 --speed 1.0 --yes
"""
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from aion.project import find_video
from aion.voice.elevenlabs import VoiceSettings, is_cached, tts_with_timestamps
from aion.voice.master import plan

VIDEO = Path(__file__).resolve().parents[1]
OUT = VIDEO / "audio" / "voice_test"


def speech_span(al: dict) -> float:
    """Seconds from the first spoken character to the last one."""
    chars, s, e = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    idx = [i for i, c in enumerate(chars) if not c.isspace()]
    return e[idx[-1]] - s[idx[0]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", action="append", help="scene id (repeatable); default ch3_s05 and ch6_s05")
    ap.add_argument("--speed", action="append", type=float, help="speed value(s); default: voice.toml's")
    ap.add_argument("--yes", action="store_true", help="spend credits")
    a = ap.parse_args()

    vp = plan(find_video("015"))
    jobs = {j.id: j for j in vp.scenes}
    ids = a.scene or ["ch3_s05", "ch6_s05"]
    base: VoiceSettings = vp.settings
    speeds = a.speed or [base.settings.get("speed")]
    runs = []
    for sid in ids:
        j = jobs[sid]
        for sp in speeds:
            settings = dict(base.settings)
            if sp is not None:
                settings["speed"] = sp
            vs = replace(base, settings=settings, seed=j.seed)
            runs.append((j, sp, vs, is_cached(j.text, j.prev, j.next, vs)))
    bill = sum(j.chars for j, _, _, hit in runs if not hit)
    for j, sp, _, hit in runs:
        print(f"{j.id:<8} speed {sp}  {j.chars:>4} chars  {'cached' if hit else 'BILL'}")
    print(f"total to bill: {bill} characters")
    if not a.yes:
        print("dry run: nothing requested (add --yes after the user's OK)")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for j, sp, vs, _ in runs:
        audio, al = tts_with_timestamps(j.text, j.prev, j.next, vs)
        name = f"{j.id}_speed{sp}.mp3"
        (OUT / name).write_bytes(audio)
        span = speech_span(al)
        wpm = len(j.display) / span * 60
        report.append({"scene": j.id, "speed": sp, "file": f"audio/voice_test/{name}", "words": len(j.display),
                       "speech_s": round(span, 2), "wpm": round(wpm, 1)})
        print(f"{name:<26} {len(j.display):>3} words  {span:6.2f} s of speech  {wpm:5.1f} wpm")
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
