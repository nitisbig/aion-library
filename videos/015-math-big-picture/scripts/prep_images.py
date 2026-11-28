"""Prepare the archival images (assets/ext/raw → assets/ext): portraits cropped to 4:5 around the face, documents kept
whole; all scaled to 600 px tall, gently toned down so they sit on the black stage. Sources: assets/ext/SOURCES.md.

Run: uv run python videos/015-math-big-picture/scripts/prep_images.py
"""
from pathlib import Path

from PIL import Image, ImageEnhance

D = Path(__file__).resolve().parent.parent / "assets" / "ext"
H = 600
# portraits: face centre (fraction of width, height) and crop width (fraction of width)
FACE = {"archimedes": (0.68, 0.3, 0.5), "bernoulli": (0.5, 0.34, 0.78), "buffon": (0.5, 0.26, 0.72),
        "cantor": (0.5, 0.33, 0.92), "euler": (0.43, 0.42, 0.95), "fermat": (0.5, 0.45, 0.98),
        "hamilton": (0.5, 0.45, 0.9), "lambert": (0.47, 0.47, 0.9), "leibniz": (0.55, 0.5, 0.86),
        "newton": (0.5, 0.42, 0.92)}
DOCS = ("ars_conjectandi", "euler_introductio", "fermat_diophantus", "principia", "leibniz_nova")

for f in sorted((D / "raw").iterdir()):
    k = f.stem
    im = Image.open(f).convert("RGB")
    W, Hh = im.size
    if k in FACE:
        cx, cy, wf = FACE[k]
        w = min(wf * W, Hh * 0.8)
        h = 1.25 * w
        x0 = min(max(cx * W - w / 2, 0), W - w)
        y0 = min(max(cy * Hh - h / 2, 0), Hh - h)
        im = im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))
        im = ImageEnhance.Brightness(im).enhance(0.92)
    elif k in DOCS:
        im = ImageEnhance.Brightness(im).enhance(0.8)
    else:
        continue
    im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
    im.save(D / f"{k}.png")
    print(k, im.size)
