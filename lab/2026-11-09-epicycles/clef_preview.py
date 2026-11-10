"""Bridge the clef contours into one line and preview 1 / 5 / 20 / 201 circles."""
import numpy as np
from PIL import Image, ImageDraw
from aion import fourier as F

from aion.drawings import treble_clef

HERE = "lab/2026-11-09-epicycles/"
z = treble_clef(1000)
c = F.coefficients(z, 100)
terms = F.order_terms(c, keep_zero_first=False)   # centered: c0 = 0 goes last, "1 circle" = the biggest

t = np.linspace(0, 1, 4000, endpoint=False)
W = H = 420
panels = [("outline", z, None)] + [(f"{k} circles", F.partial_sum(terms[:k], t), k) for k in (1, 5, 20, 201)]
img = Image.new("RGB", (W * len(panels), H + 30), "black")
d = ImageDraw.Draw(img)
for i, (label, w, _) in enumerate(panels):
    p = [(i * W + W / 2 + 190 * q.real, H / 2 - 190 * q.imag) for q in np.append(w, w[0])]
    d.line(p, fill=(255, 212, 59), width=2)
    d.text((i * W + 10, H + 8), label, fill=(200, 200, 200))
img.save(HERE + "clef_convergence.png")
mags = sorted((abs(v) for n, v in c.items() if n), reverse=True)
err = {k: np.abs(F.partial_sum(terms[:k], np.arange(1000) / 1000) - z).max() for k in (1, 5, 20, 50, 100, 201)}
print("biggest radii:", np.round(mags[:6], 4), "smallest:", f"{mags[-1]:.2e}")
print("max error vs outline (radius 1):", {k: round(float(v), 4) for k, v in err.items()})
