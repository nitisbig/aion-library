"""Frame time of the prototype EpicycleRenderer, plus stills of the three ink looks."""
import sys, time
sys.path.insert(0, "lab/2026-11-09-epicycles")
import numpy as np
from PIL import Image
from aion import fourier as F
from aion.drawings import treble_clef
from epicycle_gl import EpicycleRenderer

HERE = "lab/2026-11-09-epicycles/"
z = treble_clef(1000)
coef = {k: v * 3.4 for k, v in F.coefficients(z, 250).items()}      # clef ~6.8 units tall
results = []
for size in ((854, 480), (1920, 1080)):
    r = EpicycleRenderer(size)
    for ncirc in (200, 500):
        terms = F.order_terms(coef, keep_zero_first=False)[:ncirc]
        for ink in ("hairline", "brush", "comet"):
            r.render(terms, 0.1, ink)                                 # warm-up
            ts = []
            for k in range(8):
                a = time.perf_counter()
                img = r.render(terms, 0.83 + k * 0.001, ink)
                ts.append(time.perf_counter() - a)
            results.append((size, ncirc, ink, 1000 * np.median(ts)))
            print(f"{size[0]}x{size[1]}  {ncirc} circles  {ink:8s}  {1000*np.median(ts):6.1f} ms/frame", flush=True)
            if size == (1920, 1080) and ncirc == 200:
                Image.fromarray(img).save(HERE + f"ink_{ink}.png")
    if size == (1920, 1080):
        terms = F.order_terms(coef, keep_zero_first=False)[:200]
        pen = F.partial_sum(terms, 0.83)
        Image.fromarray(r.render(terms, 0.83, "brush", camera=(pen, 40.0), ink_span=0.02)).save(HERE + "zoom40x.png")
# split geometry vs GPU time for the worst case
r = EpicycleRenderer((1920, 1080)); terms = F.order_terms(coef, keep_zero_first=False)[:500]
a = time.perf_counter(); [r.geometry(terms, 0.5 + i * 1e-3, "brush") for i in range(5)]; g = (time.perf_counter() - a) / 5
print(f"geometry only (numpy, 500 circles, brush): {1000*g:.1f} ms")
