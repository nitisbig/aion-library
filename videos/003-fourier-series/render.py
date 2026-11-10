"""Render video 003 (whole or in parts), concatenate, and mux the narration.

Run from the repo root (so manim.cfg applies):

    uv run python videos/003-fourier-series/render.py --fps 15 --quality lq --chapters 0
    uv run python videos/003-fourier-series/render.py --fps 30 --quality hq --chapters 0,4
    uv run python videos/003-fourier-series/render.py --fps 60 --quality hq --chapters full
    uv run python videos/003-fourier-series/render.py --quality hq --scenes 1,2 --skip-existing

Chapters: 0 = intro (S00 cold open + S01–S03), 1…6 = Ch1…Ch6, 7 = outro (S28–S30), or "full".
Quality: lq = 854×480, hq = 1920×1080, 4k = 3840×2160.
Output: videos/003-fourier-series/out/<name>_<H>p<fps>.mp4 (full → final_<H>p<fps>.mp4), with the
matching slices of assets/audio.mp3, then an ffprobe check that video and audio lengths agree.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCENES = HERE / "scenes"
OUT = HERE / "out"
AUDIO = HERE / "assets" / "audio.mp3"
sys.path.insert(0, str(SCENES))

QUALITY = {"lq": (854, 480), "hq": (1920, 1080), "4k": (3840, 2160)}
CHAPTERS = {0: range(0, 4), 1: range(4, 7), 2: range(7, 11), 3: range(11, 14), 4: range(14, 19),
            5: range(19, 24), 6: range(24, 28), 7: range(28, 31)}
NAMES = {0: "intro", 7: "outro"}


def scene_file(n: int) -> tuple[Path, str]:
    files = sorted(SCENES.glob(f"scene_{n:02d}_*.py"))
    if len(files) != 1:
        sys.exit(f"scene {n:02d}: expected one scenes/scene_{n:02d}_*.py, found {len(files)}")
    m = re.search(r"^class (Scene\d\d\w*)\(", files[0].read_text(), re.M)
    if not m:
        sys.exit(f"{files[0].name}: no Scene class")
    return files[0], m.group(1)


def parse_list(text: str) -> list[int]:
    out = []
    for part in text.split(","):
        part = part.strip().lower()
        if not part:
            continue
        if part in ("intro", "outro"):
            out.append(0 if part == "intro" else 7)
        elif "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part.removeprefix("ch")))
    return out


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"failed ({r.returncode}): {' '.join(cmd)}")


def probe(path: Path, stream: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", "stream=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fps", type=int, default=15, help="frame rate, e.g. 15, 30, 60 (default 15)")
    ap.add_argument("--quality", choices=QUALITY, default="lq", help="lq 480p · hq 1080p · 4k 2160p (default lq)")
    sel = ap.add_mutually_exclusive_group()
    sel.add_argument("--chapters", default=None, help='"full", or a list like 0,4 or 1-3 or intro,outro')
    sel.add_argument("--scenes", default=None, help="scene numbers instead, e.g. 1,2 or 24-27")
    ap.add_argument("--skip-existing", action="store_true", help="reuse clips already rendered at this size/fps")
    ap.add_argument("--no-mux", action="store_true", help="render the clips only")
    a = ap.parse_args()

    import shared as V                                   # scene ranges come from the SRT (beats)

    if a.scenes:
        nums = parse_list(a.scenes)
        name = "scenes_" + "-".join(f"{n:02d}" for n in nums)
    else:
        chs = list(CHAPTERS) if a.chapters in (None, "full") else parse_list(a.chapters)
        if a.chapters in (None, "full"):
            name = "final"
        else:
            name = "_".join(NAMES.get(c, f"ch{c}") for c in chs)
        nums = [n for c in chs for n in CHAPTERS[c]]
    nums = sorted(set(nums))
    W, H = QUALITY[a.quality]
    tag = f"{H}p{a.fps}"
    print(f"▶ {len(nums)} scene(s) at {W}×{H}, {a.fps} fps: {', '.join(f'S{n:02d}' for n in nums)}")

    clips, t_all = [], time.time()
    for i, n in enumerate(nums, 1):
        f, cls = scene_file(n)
        clip = ROOT / "media" / "videos" / f.stem / tag / f"{cls}.mp4"
        if a.skip_existing and clip.exists() and clip.stat().st_mtime > f.stat().st_mtime:
            print(f"[{i}/{len(nums)}] S{n:02d} {cls}: reusing {clip.relative_to(ROOT)}")
        else:
            print(f"[{i}/{len(nums)}] S{n:02d} {cls}")
            run(["uv", "run", "manim", "-r", f"{W},{H}", "--fps", str(a.fps), str(f.relative_to(ROOT)), cls])
        if not clip.exists():
            sys.exit(f"missing output {clip}")
        clips.append((n, clip))
    print(f"✔ rendered in {time.time() - t_all:.0f} s")
    if a.no_mux:
        return

    OUT.mkdir(exist_ok=True)
    lst = OUT / f".{name}_{tag}.txt"
    lst.write_text("".join(f"file '{c}'\n" for _, c in clips))
    video = OUT / f".{name}_{tag}_v.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)])

    # the narration: the same slices, joined in order (handles non-adjacent chapters).
    # S00 (the cold open) has no voice: PREVIEW_S of silence before audio time 0.
    from scene_00_preview import PREVIEW_S
    runs = []
    for n, _ in clips:
        s, e = (None, PREVIEW_S) if n == 0 else V.scene_range(n)
        if runs and s is not None and runs[-1][0] is not None and abs(runs[-1][1] - s) < 1e-6:
            runs[-1][1] = e
        else:
            runs.append([s, e])
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    fc = "".join((f"anullsrc=r=48000:cl=stereo,atrim=duration={e:.4f},{fmt}[a{k}];" if s is None else
                  f"[1:a]atrim={s:.4f}:{e:.4f},asetpts=PTS-STARTPTS,{fmt}[a{k}];") for k, (s, e) in enumerate(runs))
    fc += "".join(f"[a{k}]" for k in range(len(runs))) + f"concat=n={len(runs)}:v=0:a=1[a]"
    out = OUT / f"{name}_{tag}.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-i", str(AUDIO), "-filter_complex", fc,
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", str(out)])
    lst.unlink()
    video.unlink()

    dv, da = probe(out, "v:0"), probe(out, "a:0")
    ok = abs(dv - da) <= 1.0 / a.fps + 1e-3
    print(f"{'✔' if ok else '⚠'} {out.relative_to(ROOT)}  video {dv:.3f} s · audio {da:.3f} s"
          f"{'' if ok else '  (differ by more than one frame)'}")


if __name__ == "__main__":
    main()
