"""@scene: declare one storyboard section as a function that builds a Comp.

    from aion import *
    from beats import T

    @scene(T.cut1, T.cut2)
    def s02(s):
        s.shader("layers/domain_coloring.frag", z=-1, u_theta=key(T.turn, 0, PI / 2))
        m = s.manim()
        m.play(Create(Arrow(ORIGIN, [2, 1, 0])), at=T.vector)
        s.camera.push(T.stretch, zoom=1.15, dur=2)
        s.fx(Bloom(0.5), Vignette(0.3))

`s` is a SceneBuilder: every helper adds a layer spanning the scene's range.
The function must be deterministic: workers call it again to rebuild.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from aion.comp.comp import Comp

__all__ = ["scene", "SceneDef", "SceneBuilder", "REGISTRY"]

REGISTRY: list["SceneDef"] = []


@dataclass
class SceneDef:
    name: str
    start: float
    end: float
    build: Callable
    file: str = ""
    options: dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return self.end - self.start

    def comp(self, size=(1920, 1080), fps: float = 60, background=None) -> Comp:
        """Build a fresh Comp for this scene."""
        from aion.theme.tokens import current

        th = current()
        comp = Comp(size, fps, background=background or self.options.get("background") or th.bg,
                    start=self.start, end=self.end, name=self.name)
        b = SceneBuilder(self, comp)
        self.build(b)
        for layer in comp.layers:
            if not math.isfinite(layer.start):
                layer.start = self.start
            if not math.isfinite(layer.end):
                layer.end = self.end
        b._validate()
        return comp


def scene(start: float, end: float, **options):
    """Register a scene covering absolute audio times [start, end).

    Example:
        @scene(T.start, T.cut1)
        def s01(s): ...
    """

    def deco(fn: Callable) -> SceneDef:
        sd = SceneDef(fn.__name__, float(start), float(end), fn, getattr(fn, "__module__", ""), options)
        code = getattr(fn, "__code__", None)
        if code is not None:
            sd.file = code.co_filename
        if sd.end <= sd.start:
            raise ValueError(f"scene {sd.name}: end {sd.end:.3f} ≤ start {sd.start:.3f}")
        REGISTRY.append(sd)
        return sd

    return deco


class SceneBuilder:
    """Passed to every @scene function. Adds layers clipped to the scene's range.

    Example:
        @scene(T.start, T.cut1)
        def s01(s): s.gradient(C.bg2, C.bg); m = s.manim(); s.fx(Bloom())
    """

    def __init__(self, sd: SceneDef, comp: Comp):
        self.sd, self.comp = sd, comp
        self.start, self.end = sd.start, sd.end
        self._beats_seen: list[float] = []

    # ── layers ───────────────────────────────────────────────────────────────
    def add(self, layer):
        """Add any Layer."""
        return self.comp.add(layer)

    def manim(self, **kw):
        """A transparent Manim layer (score API: add/play/seq/drive/redraw/remove)."""
        from aion.layers.manim import ManimLayer

        return self.add(ManimLayer(**kw))

    def shader(self, frag: str, **kw):
        """A fullscreen GLSL layer; u_* keywords are uniforms (Tracks allowed)."""
        from aion.layers.shader import ShaderLayer

        return self.add(ShaderLayer(frag, **kw))

    def image(self, path: str, **kw):
        from aion.layers.media import ImageLayer

        p = Path(path)
        if not p.is_absolute() and self.sd.file:
            for base in (Path(self.sd.file).parent, Path(self.sd.file).parent.parent):
                if (base / p).exists():
                    p = base / p
                    break
        return self.add(ImageLayer(p, **kw))

    def solid(self, color, **kw):
        from aion.layers.solid import Solid

        return self.add(Solid(color, **kw))

    def gradient(self, *a, **kw):
        from aion.layers.solid import Gradient

        kw.setdefault("z", -100)
        return self.add(Gradient(*a, **kw))

    def precomp(self, build: Callable, **kw):
        """A nested Comp (transparent) built by build(sub_builder); use for grouped fx."""
        sub = Comp(self.comp.size, self.comp.fps, None, camera=self.comp.camera, **kw)
        sb = SceneBuilder(self.sd, sub)
        build(sb)
        return self.add(sub)

    # ── comp-level ───────────────────────────────────────────────────────────
    @property
    def camera(self):
        return self.comp.camera

    def fx(self, *effects):
        """Effects applied to the whole frame, in order (bloom, grade, vignette, grain…)."""
        self.comp.comp_fx.extend(effects)
        return self.comp

    def beat_in_range(self, t: float) -> float:
        self._beats_seen.append(float(t))
        return t

    def _validate(self) -> None:
        tol = 1e-6
        for layer in self.comp.layers:
            for a, b in getattr(layer, "windows", []):
                if math.isfinite(a) and (a < self.start - 1.0 - tol or a > self.end + tol):
                    raise ValueError(f"{self.sd.name}: event at {a:.2f}s is outside the scene "
                                     f"[{self.start:.2f}, {self.end:.2f}) — wrong beat?")
                if math.isfinite(b) and b > self.end + 0.5:
                    raise ValueError(f"{self.sd.name}: an animation runs until {b:.2f}s, past the scene end "
                                     f"{self.end:.2f}s — shorten dur or move the cut")
