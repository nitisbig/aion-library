"""Render the video frames the ebook uses into ebook/figs/ (1080p, no progress strip).

    uv run python videos/009-what-matrices-are/ebook/stills.py
"""
import os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from beats import T  # noqa: E402

SHOTS = {   # fig name: (scene, beat, offset)
    "cover": ("s00_hook", "columns", 2.0), "anatomy": ("s02_box", "address", 1.5),
    "pixels": ("s03_photo", "squares", 2.6), "rules": ("s04_machine", "even", 0.8),
    "shear": ("s05_gallery", "shear", 2.2), "die3d": ("s05_gallery", "die", 2.6),
    "columns": ("s06_columns", "are_matrix", 1.0), "quarter": ("s07_read", "quarter", 1.5),
    "box3d": ("s07_read", "nine_three", 1.0), "compose": ("s08_compose", "row_col", 1.0),
    "order": ("s09_order", "top_face", 1.0), "spirals": ("s10_layers", "told_apart", 0.5),
    "det": ("s11_undo", "four", 0.8), "collapse": ("s12_collapse", "colspace", 1.0),
    "shadow": ("s12_collapse", "light_null", 0.5), "planes": ("s13_solve", "solution", 0.5),
    "eigen": ("s14_eigen", "four_x", 0.5), "power": ("s15_power", "lined_up", 0.3),
    "pagerank": ("s16_pagerank", "two_pages", 1.0), "svd": ("s17_ellipse", "rsr", 0.5),
    "ellipsoid": ("s17_ellipse", "sphere", 1.2), "layers": ("s18_photo_svd", "thirty", 1.0),
    "outro": ("s19_outro", "axes_land", 1.0),
}

def main(only):
    env = dict(os.environ, AION_NO_PROGRESS="1")
    by_scene = {}
    for name, (sc, beat, off) in SHOTS.items():
        if only and name not in only:
            continue
        by_scene.setdefault(sc, []).append((name, float(getattr(T, beat)) + off))
    for sc, items in by_scene.items():
        args = ["uv", "run", "aion", "still", HERE.parent.name, sc, "--final"]
        for _, t in items:
            args += ["--at", f"{t:.3f}"]
        out = subprocess.run(args, env=env, cwd=ROOT, capture_output=True, text=True)
        pngs = [l.strip() for l in out.stdout.splitlines() if l.strip().endswith(".png")]
        if out.returncode or len(pngs) < len(items):
            print("FAILED", sc, out.stderr[-800:]); continue
        for (name, t), png in zip(items, pngs[-len(items):]):
            shutil.copy(png, HERE / "figs" / f"{name}.png")
            print(f"{name}.png  <- {sc} @ {t:.2f}", flush=True)

if __name__ == "__main__":
    main(set(sys.argv[1:]))
