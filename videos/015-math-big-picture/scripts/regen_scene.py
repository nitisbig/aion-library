"""Re-voice one scene of video 015 and refresh everything downstream of it.

Steps: build_script.py (scenes.yaml → voiceover.md) → `aion voice 015 --scene ID` (or `--retake ID`) →
timing.py → make_beats.py → lint_script.py → check_plan.py.

Only the named scene is billed: aion pins every other scene's recorded request, so its audio is reused from the
cache (or restored from audio/scenes/ and audio/alignment/). Without --yes this stops after the dry run and prints
the characters that would be billed; spending credits needs the user's OK.

Usage (from the repo root):
    uv run python videos/015-math-big-picture/scripts/regen_scene.py ch3_s05            # dry run: what it costs
    uv run python videos/015-math-big-picture/scripts/regen_scene.py ch3_s05 --yes      # same text, current neighbours
    uv run python videos/015-math-big-picture/scripts/regen_scene.py ch3_s05 --retake --yes   # a new take (new seed)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def run(*cmd: str) -> None:
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode:
        sys.exit(r.returncode)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scene", help="scene id from plan/scenes.yaml, e.g. ch3_s05")
    ap.add_argument("--retake", action="store_true", help="request a new take (seed + take) instead of the same text")
    ap.add_argument("--yes", action="store_true", help="spend the credits the dry run lists")
    a = ap.parse_args()

    py = sys.executable
    run(py, str(HERE / "build_script.py"))
    flag = ["--retake" if a.retake else "--scene", a.scene]
    run("uv", "run", "aion", "voice", "015", *flag, "--dry-run")
    if not a.yes:
        print("dry run only: add --yes (after the user's OK) to spend the credits listed above")
        return
    run("uv", "run", "aion", "voice", "015", *flag, "-y")
    run(py, str(HERE / "timing.py"))
    run(py, str(HERE / "make_beats.py"))
    run(py, str(HERE / "lint_script.py"))
    run(py, str(HERE / "check_plan.py"))


if __name__ == "__main__":
    main()
