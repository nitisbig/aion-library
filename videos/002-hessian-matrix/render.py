"""Preview renderer for video 002: render a chapter (or the whole video) at a chosen
quality and frame rate, then stitch the clips and mux in the matching narration.

    uv run python videos/002-hessian-matrix/render.py --chapter 3 --quality 720p --fps 30
    uv run python videos/002-hessian-matrix/render.py --chapter full --quality 480p --fps 15

Chapters: 0 intro (scenes 01–02), 1 (03–05), 2 (06–08), 3 (09–12), 4 (13–16),
5 (17–20), 6 (21–24), 7 outro (25–26), or `full`. A single scene: --scene 14.

Each scene shows its own progress bar with an ETA; Manim's cache makes unchanged
scenes nearly free on a re-run. Output: videos/002-hessian-matrix/out/
preview_<chapter>_<quality>_<fps>fps.mp4 (clips are joined with ffmpeg's concat
demuxer, one file at a time, so even `full` is light on memory).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from beats import CUT_FRAMES, FPS as CUT_FPS  # noqa: E402

CHAPTERS = {"0": (1, 2), "1": (3, 5), "2": (6, 8), "3": (9, 12), "4": (13, 16), "5": (17, 20),
            "6": (21, 24), "7": (25, 26), "full": (1, 26)}
QUALITY = {"480p": (854, 480), "720p": (1280, 720), "1080p": (1920, 1080), "4k": (3840, 2160)}


def scene_files() -> dict[int, tuple[Path, str]]:
    out = {}
    for f in sorted((HERE / "scenes").glob("scene_*.py")):
        n = int(f.name.split("_")[1])
        m = re.search(r"^class (Scene\w+)\(", f.read_text(), re.M)
        out[n] = (f, m.group(1))
    return out


def render_scene(f: Path, cls: str, w: int, h: int, fps: int) -> Path:
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")   # TinyTeX via .venv/bin
    cmd = [sys.executable, "-m", "manim", "render", "-r", f"{w},{h}", "--fps", str(fps),
           str(f.relative_to(ROOT)), cls]
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    path, tail = None, []
    for line in proc.stdout:
        sys.stdout.write(line)
        tail = (tail + [line])[-40:]
        m = re.search(r"→\s*(\S+\.mp4)", line)
        if m:
            path = Path(m.group(1))
    proc.wait()
    if proc.returncode != 0 or path is None:
        sys.stdout.write("".join(tail))
        sys.exit(f"✘ {cls} failed (exit {proc.returncode})")
    return path


def duration(p: Path, stream: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries",
                        "stream=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip() or "nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chapter", default="full", choices=list(CHAPTERS), help="0–7 or full")
    ap.add_argument("--scene", type=int, help="render one scene (1–26) instead of a chapter")
    ap.add_argument("--quality", default="480p", choices=list(QUALITY))
    ap.add_argument("--fps", type=int, default=15, choices=(15, 30, 60))
    ap.add_argument("--open", action="store_true", help="open the result when done (xdg-open)")
    a = ap.parse_args()

    first, last = (a.scene, a.scene) if a.scene else CHAPTERS[a.chapter]
    tag = f"scene{a.scene:02d}" if a.scene else ("full" if a.chapter == "full" else f"ch{a.chapter}")
    w, h = QUALITY[a.quality]
    files = scene_files()
    t0 = time.time()
    clips = []
    for n in range(first, last + 1):
        f, cls = files[n]
        print(f"\n── scene {n:02d} / {first:02d}–{last:02d} · {cls} · {a.quality} {a.fps} fps ──", flush=True)
        clips.append(render_scene(f, cls, w, h, a.fps))

    start, end = CUT_FRAMES[first - 1] / CUT_FPS, CUT_FRAMES[last] / CUT_FPS
    out = HERE / "out" / f"preview_{tag}_{a.quality}_{a.fps}fps.mp4"
    out.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lst:
        for c in clips:
            lst.write(f"file '{c.resolve()}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst.name,
                    "-ss", f"{start:.4f}", "-to", f"{end:.4f}", "-i", str(HERE / "assets" / "audio.mp3"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-movflags", "+faststart", str(out)], check=True)
    os.unlink(lst.name)
    v, au = duration(out, "v:0"), duration(out, "a:0")
    mins = (time.time() - t0) / 60
    print(f"\n✔ {out.relative_to(ROOT)}  ({end - start:.2f} s of narration; video {v:.2f} s, audio {au:.2f} s;"
          f" {mins:.1f} min)")
    if abs(v - au) > 1.5 / a.fps:
        print(f"⚠ video and audio differ by {abs(v - au):.3f} s")
    if a.open:
        subprocess.Popen(["xdg-open", str(out)])


if __name__ == "__main__":
    main()
