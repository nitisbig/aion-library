"""Print ebook.html to What-Matrices-Actually-Are-Notes.pdf with headless Chromium, plus PNG previews of every page.

    uv run python videos/009-what-matrices-are/ebook/stills.py     # video frames → figs/
    uv run python videos/009-what-matrices-are/ebook/gen_figs.py   # diagrams + SVD strip → figs/
    uv run python videos/009-what-matrices-are/ebook/build.py
"""
import glob
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
PDF = HERE / "What-Matrices-Actually-Are-Notes.pdf"
CHROME = sorted(glob.glob(str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux*/chrome")))[-1]

subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                "--allow-file-access-from-files", "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=20000", f"--print-to-pdf={PDF}", (HERE / "ebook.html").as_uri()],
               check=True, capture_output=True)
prev = HERE / "preview"
prev.mkdir(exist_ok=True)
for f in prev.glob("*.png"):
    f.unlink()
subprocess.run(["pdftoppm", "-r", "50", "-png", str(PDF), str(prev / "p")], check=True)
print(PDF, f"{PDF.stat().st_size / 1e6:.1f} MB")
