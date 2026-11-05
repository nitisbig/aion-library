"""Stills of TerrainPlate in the intro's key states (no Manim scene, just the plate).

    uv run python lab/2026-11-05-luminous-terrain/stills.py [480|1080]
"""

import sys
import time
from pathlib import Path

from manim import config
from PIL import Image

res = int(sys.argv[1]) if len(sys.argv) > 1 else 480
config.pixel_height = res
config.pixel_width = round(res * 16 / 9)

from aion import style as S  # noqa: E402
from aion.components.terrain_gl import TERRAIN_DEFAULTS, TerrainPlate  # noqa: E402

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
SAD, DOME, BOWL = (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0), (2.0, 0.0, 2.0)

STATES = {
    "a_open": dict(H=(0, 0, 0), fog=0.10, mist=0.8, disc=(0, 0, 0.45, 0.0)),
    "b_thick": dict(H=(0, 0, 0), fog=0.30, fognear=1.5, mist=1.0, haze=1.0, disc=(0, 0, 0.45, 0.9)),
    "c_dome": dict(H=DOME, fog=0.12, disc=(0, 0, 0.45, 0.9), ping=(2.0, 0.6)),
    "d_bowl": dict(H=BOWL, fog=0.12, disc=(0, 0, 0.45, 0.9)),
    "e_pass": dict(H=SAD, fog=0.10, disc=(0, 0, 0.45, 0.9),
                   slices=[(0, 1.0, S.SMILE, 2.4), (90, 1.0, S.FROWN, 2.4)]),
    "f_bends": dict(H=SAD, fog=0.06, tint=1.0, disc=(0, 0, 0.45, 0.6), yaw=215, pitch=24, dist=7.0),
    "g_puzzle": dict(H=(2, 3, 2), wm=0.0, win=0.0, zs=0.3, zclip=1.6, edge=2.7, yaw=-58, pitch=30,
                     dist=8.5, target=(0, 0, 0), fog=0.0, mist=0.25, haze=0.0, cstep=0.15, gstep=0.3,
                     grid=0.35, slices=[(0, 1.0, S.HX, 2.6), (90, 1.0, S.HY, 2.6)]),
}

for name, st in STATES.items():
    s = {**TERRAIN_DEFAULTS, "time": 4.0, **st}
    t0 = time.time()
    p = TerrainPlate(lambda s=s: s)
    dt = time.time() - t0
    Image.fromarray(p.pixel_array[..., :3]).save(OUT / f"{name}_{res}.png")
    print(f"{name}: {dt * 1000:.0f} ms (incl. compile)")

t0 = time.time()
for _ in range(10):
    p.render_gl()
print(f"steady render: {(time.time() - t0) * 100:.1f} ms/frame at {res}p")
