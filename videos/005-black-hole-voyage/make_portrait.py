"""Build assets/images/einstein_card.png from the public-domain source photo: a square head-and-shoulders
crop, slightly deepened, with a soft inner vignette. The scene draws a thin frame round it.

    uv run python videos/005-black-hole-voyage/make_portrait.py

Source: Albert Einstein during a lecture in Vienna, 1921, by Ferdinand Schmutzer (1870–1928). Public domain.
https://commons.wikimedia.org/wiki/File:Einstein_1921_by_F_Schmutzer_-_restoration.jpg
"""
from pathlib import Path

import numpy as np
from PIL import Image

here = Path(__file__).parent / "assets" / "images"
im = Image.open(here / "einstein_1921_schmutzer.jpg").convert("RGB").crop((500, 130, 1700, 1330))
rgb = np.asarray(im, float) / 255.0
rgb = rgb ** 1.15 * 0.92                                        # a little deeper, never brighter than the text
h, w = rgb.shape[:2]
y, x = np.mgrid[0:h, 0:w]
r = np.hypot(x / (w - 1) - 0.5, y / (h - 1) - 0.5) / 0.7071
rgb *= (1.0 - 0.45 * np.clip((r - 0.45) / 0.55, 0, 1) ** 2)[..., None]
out = np.dstack([rgb, np.ones((h, w))])
Image.fromarray((np.clip(out, 0, 1) * 255).astype("uint8"), "RGBA").save(here / "einstein_card.png")
print(here / "einstein_card.png", (w, h))
