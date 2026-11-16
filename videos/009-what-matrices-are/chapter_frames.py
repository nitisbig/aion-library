"""Render the real frames the chapter-progress transitions use (see `progress` in shots.py).

For every chapter cut: the last frame of the chapter that ends (end_<k>.png, at the shrink start) and the first
live frame of the chapter that begins (start_<k>.png, when the pop has filled the screen; start_8 is the outro).
They are rendered at 1080p with AION_NO_PROGRESS=1, so they never contain the bars or another transition.
Re-run after editing a scene near a chapter cut.

    uv run python videos/009-what-matrices-are/chapter_frames.py            # all 15
    uv run python videos/009-what-matrices-are/chapter_frames.py 1 2 3      # only the cuts into chapters 1-3
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from beats import T  # noqa: E402
from shots import CHAPTER_CUTS, FRAMES, transition  # noqa: E402

VIDEO = HERE.name
# the scene on each side of each cut (same order as CHAPTER_CUTS)
SIDES = [("s01_preview", "s02_box"), ("s03_photo", "s04_machine"), ("s05_gallery", "s06_columns"),
         ("s07_read", "s08_compose"), ("s10_layers", "s11_undo"), ("s13_solve", "s14_eigen"),
         ("s16_pagerank", "s17_ellipse"), ("s18_photo_svd", "s19_outro")]


def still(scene, t, name):
    env = dict(os.environ, AION_NO_PROGRESS="1")
    out = subprocess.run(["uv", "run", "aion", "still", VIDEO, scene, "--at", f"{t:.3f}", "--final"], env=env,
                         cwd=HERE.parent.parent, capture_output=True, text=True, check=True).stdout
    png = [ln.strip() for ln in out.splitlines() if ln.strip().endswith(".png")][-1]
    FRAMES.mkdir(parents=True, exist_ok=True)
    shutil.copy(png, FRAMES / f"{name}.png")
    print(f"{name}.png  ← {scene} @ {t:.2f}s")


def main(which):
    for i in range(len(CHAPTER_CUTS)):
        if which and (i + 1) not in which:
            continue
        d = transition(i)
        before, after = SIDES[i]
        if i > 0:
            still(before, d["ts"], f"end_{i}")
        still(after, d["p1"], f"start_{i + 1}")


if __name__ == "__main__":
    main({int(a) for a in sys.argv[1:]})
