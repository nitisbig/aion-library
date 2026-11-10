"""Scene 06 · Ch1: two shadows of one motion (114.283–129.267 s).

"There's another view I really like. Slide the circle forward through time, and its
tip traces out a spring. From the side, the spring looks like a sine wave. From above,
it looks like its twin, the cosine. Two shadows of one turning motion."

The flat picture dissolves into a pyvista 3D view (spring_pv: gold tube helix, sine on
the back wall, cosine on the floor, orbiting camera). Labels are pinned to the 3D view
through VTK's camera. On "turning motion" the camera lands on the side view and the
picture dissolves back to the flat one-circle sine that S07 starts from.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import ImageMobject, MathTex, ValueTracker, config
from PIL import Image

from aion import style as S
import shared as V
import ch1 as C
import spring_pv as P

START, END = V.scene_range(6)


class Scene06Spring(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        L = S.LEAD
        T = {k: self.t(k) - L for k in ("another view", "from the side", "from above", "two shadows",
                                        "turning motion")}
        T["slide"] = self.t("slide the circle forward") - L
        T["slide_end"] = T["turning motion"] - 0.1
        tl = P.SpringTimeline(T)
        fps = config.frame_rate
        n = int(round((END - START) * fps)) + 2
        times = START + np.arange(n) / fps
        size = (config.pixel_width, config.pixel_height)
        d = P.render(times, tl, size, Path(config.media_dir) / "cache" / f"s06_{size[0]}x{size[1]}_{fps:g}")
        labels = json.loads((d / "labels.json").read_text())

        # the flat picture S05 ended on
        flat = C.OneCircle(self, C.S05_END)
        f = C.formula()
        self.add(f)

        # the 3D frames, played back by absolute time
        pv_op = ValueTracker(0.0)
        cache = {}

        def frame(i):
            i = int(np.clip(i, 0, n - 1))
            if i not in cache:
                cache.clear()
                cache[i] = np.asarray(Image.open(d / f"{i:05d}.png").convert("RGB"), np.float32)
            return cache[i]

        img = ImageMobject(np.zeros((size[1], size[0], 4), np.uint8)).set(width=config.frame_width)

        def show(m, dt):
            rgb = frame(round((self.now - START) * fps)) * pv_op.get_value()
            a = np.full(rgb.shape[:2] + (1,), 255, np.uint8)
            m.pixel_array = np.concatenate([rgb.astype(np.uint8), a], axis=2)
        img.add_updater(show)
        self.add(pv_op)
        self.add(img)
        self.bring_to_back(img)

        def pinned(tex, key, op):
            m = MathTex(*tex, font_size=44, color=S.INK)

            def upd(mob, dt):
                i = int(np.clip(round((self.now - START) * fps), 0, n - 1))
                fx, fy = labels[i][key]
                mob.move_to([(fx - 0.5) * config.frame_width, (0.5 - fy) * config.frame_height, 0])
                mob.set_opacity(op.get_value())
            m.add_updater(upd)
            upd(m, 0)
            return m

        sin_op, cos_op = ValueTracker(0.0), ValueTracker(0.0)
        sin_l, cos_l = pinned((r"\sin", "t"), "sin", sin_op), pinned((r"\cos", "t"), "cos", cos_op)
        self.add(sin_op, cos_op, sin_l, cos_l)

        # dissolve flat → 3D (the camera starts its ¾ move on "another view" by itself)
        self.play(flat.v["master"].animate.set_value(0.0), f.animate.set_opacity(0.0), pv_op.animate.set_value(1.0),
                  run_time=self.snap(0.6))
        self.remove(flat.group, f)

        # "from the side": the back-wall shadow is a sine
        self.beat("from the side", sin_op.animate(rate_func=V.window(0.6, 1.0)).set_value(1.0), rt=1.4, rate=None)
        # "from above": the floor shadow is a cosine
        self.beat("from above", sin_op.animate(rate_func=V.window(0, 0.4)).set_value(0.0),
                  cos_op.animate(rate_func=V.window(0.6, 1.0)).set_value(1.0), rt=1.4, rate=None)
        # "two shadows": back to ¾, both lit
        self.beat("two shadows", sin_op.animate(rate_func=V.window(0.4, 1.0)).set_value(1.0), rt=1.2, rate=None)

        # "turning motion": labels go, the camera lands on the side view, then the flat sine returns
        self.beat("turning motion", sin_op.animate.set_value(0.0), cos_op.animate.set_value(0.0), rt=0.5)
        end_flat = C.OneCircle(self, {**C.FLAT, "master": 0.0})
        self.wait_until(T["turning motion"] + 0.8)
        self.play(pv_op.animate.set_value(0.0), end_flat.v["master"].animate.set_value(1.0),
                  run_time=self.snap(0.45))
        self.remove(img)
        self.finish()
        self.handoff = {"machine": end_flat}
