"""Crop public-domain portraits to 4:5 and map them to one warm duotone (ink → paper), so they read as a set."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
BOX = {"bernoulli": (0.11, 0.0, 0.89), "euler": (0.12, 0.04, 0.95), "laguerre": (0.04, 0.0, 0.96),
       "peano": (0.03, 0.0, 0.97), "lie": (0.1, 0.0, 0.98)}          # left, top, right (height from 4:5)
INK, PAPER = np.array([12, 11, 10]), np.array([242, 230, 206])
for name, (l, t, r) in BOX.items():
    im = Image.open(src / f"{name}.jpg").convert("L")
    W, H = im.size
    w = (r - l) * W
    h = min(w * 1.25, H - t * H)
    w = h / 1.25
    cx = (l + r) / 2 * W
    im = im.crop((int(cx - w / 2), int(t * H), int(cx + w / 2), int(t * H + h)))
    im = ImageOps.autocontrast(im, cutoff=1).resize((640, 800), Image.LANCZOS)
    g = (np.asarray(im, float) / 255.0)[..., None] ** 1.1
    rgb = (INK + (PAPER - INK) * g).clip(0, 255).astype(np.uint8)
    Image.fromarray(rgb).save(dst / f"{name}.png", optimize=True)
    print(name, rgb.shape)
