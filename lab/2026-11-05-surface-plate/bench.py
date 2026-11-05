"""Time SurfacePlate.render_gl() alone (GPU draw + readback + numpy) at 480p and 1080p.

    uv run python lab/2026-11-05-surface-plate/bench.py
"""

import time

from manim import config

from aion.components.surface_gl import SurfacePlate, slice_line, tangent_disc
from aion import style as S

for w, h in ((854, 480), (1920, 1080)):
    config.pixel_width, config.pixel_height = w, h
    k = {"t": 0.0}
    st = lambda: {"H": (2.0, 3.0, 2.0), "yaw": -58 + k["t"], "R": 3.0, "fog": 0.05,
                  "fog_height": 0.6, "contour": 0.6, "tint": 0.8, "zclip": 1.6,
                  "slices": [slice_line(0, color=S.HX, plane=0.16), slice_line(90, color=S.HY, plane=0.16)],
                  "disc": tangent_disc(0, 0)}
    for opaque in (True, False):
        p = SurfacePlate(st, opaque=opaque)
        n = 30
        t0 = time.perf_counter()
        for i in range(n):
            k["t"] = i
            p.render_gl()
        dt = (time.perf_counter() - t0) / n
        print(f"{w}x{h} opaque={opaque}: {dt * 1000:.1f} ms / frame")
