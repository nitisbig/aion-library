"""Bake assets/images/vitruvian_ink.png from the Commons scan (public domain: Leonardo da Vinci, Vitruvian Man,
c. 1490; photo Luc Viatour, File:Da_Vinci_Vitruve_Luc_Viatour.jpg).

The paper is removed: ink strength (darkness against the local paper level) becomes alpha, and the colour is the
theme's lamp tone, so the drawing sits on black like light. Crop: the circle and square. Run:
    uv run python videos/016-pca-explained/scripts/vitruvian_ink.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter, median_filter

HERE = Path(__file__).resolve().parents[1]
SRC, OUT = HERE / "assets/images/vitruvian_viatour.jpg", HERE / "assets/images/vitruvian_ink.png"
CROP = (110, 205, 1830, 1925)          # x0, y0, x1, y1 in the 1920 x 2610 scan (square, 1720 px)
INK = (255, 226, 176)                  # C.lamp
CIRC = (860, 905, 842)                 # the drawn circle in crop px (cx, cy, r)


def main():
    im = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32) / 255
    L = median_filter(im @ np.array([0.2126, 0.7152, 0.0722], np.float32), 3)
    paper = gaussian_filter(maximum_filter(L, 25), 15)
    ink = np.clip((paper - L) / np.maximum(paper, 1e-3), 0, 1)
    ink = np.clip((ink - 0.21) / 0.36, 0, 1) ** 1.1
    x0, y0, x1, y1 = CROP
    a = ink[y0:y1, x0:x1]
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(xx - CIRC[0], yy - CIRC[1]) / CIRC[2]
    a = a * np.clip((1.035 - r) / 0.03, 0, 1)           # only the drawing: the circle and what is inside it
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = INK
    out[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(OUT)
    print(OUT, out.shape)


if __name__ == "__main__":
    main()
