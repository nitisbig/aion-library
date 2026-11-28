"""Find where scene content enters the progress tracker's corner (renders with the tracker off).

    AION_NO_HUD=1 uv run python videos/015-math-big-picture/scripts/hud_scan.py [step]
Prints, per scene, the times where pixels in the tracker box (plus a margin) are lit, and the lit share.
"""
import os
import sys

import numpy as np

os.environ["AION_NO_HUD"] = "1"
from aion.render.project import load_video  # noqa: E402

W, H, FPS = 854, 480, 15
step = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
vid = load_video("015", (W, H), FPS)

from hud import BOX, CH, T_IN, T_OUT  # noqa: E402

def px(x, y):
    return int((x + 64 / 9) / (128 / 9) * W), int((4 - y) / 8 * H)

x0, y0 = px(BOX[0] + 0.15, BOX[3] - 0.1)
x1, y1 = px(BOX[2] - 0.15, BOX[1] + 0.1)
for sd in vid.scenes:
    a, b = float(sd.start), float(sd.end)
    if b <= T_IN or a >= T_OUT:
        continue
    comp = sd.comp((W, H), FPS)
    hits = []
    for t in np.arange(max(a, T_IN) + 0.2, min(b, T_OUT) - 0.05, step):
        f = comp.frame(float(t), int(round(t * FPS)))[y0:y1, x0:x1, :3].astype(float)
        lit = (f.max(axis=2) > 60).mean()
        if lit > 0.004:
            hits.append((round(float(t), 1), round(100 * lit, 1)))
    print(sd.name, f"[{a:.1f}, {b:.1f}]", hits if hits else "clear", flush=True)
