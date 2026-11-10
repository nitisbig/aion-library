"""6 s side-by-side clip of the three ink looks (hairline | brush | comet), 1920x720 @30."""
import subprocess, sys
sys.path.insert(0, "lab/2026-11-09-epicycles")
import numpy as np
from tqdm import tqdm
from aion import fourier as F
from aion.drawings import treble_clef
from epicycle_gl import EpicycleRenderer

coef = {k: v * 3.4 for k, v in F.coefficients(treble_clef(1000), 100).items()}
terms = F.order_terms(coef, keep_zero_first=False)          # 201 circles
looks = ("hairline", "brush", "comet")
rs = [EpicycleRenderer((640, 720)) for _ in looks]
FPS, SEC = 30, 6
out = "lab/2026-11-09-epicycles/ink_compare.mp4"
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                       "-s", "1920x720", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt",
                       "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
for f in tqdm(range(FPS * SEC), desc="ink_compare", unit="fr"):
    t = f / (FPS * SEC) * 0.999 + 1e-4                     # one full loop
    span = min(t, 1.0)
    frame = np.hstack([r.render(terms, t, k, ink_span=span) for r, k in zip(rs, looks)])
    ff.stdin.write(np.ascontiguousarray(frame).tobytes())
ff.stdin.close(); ff.wait()
print("→", out)
