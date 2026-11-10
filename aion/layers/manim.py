"""ManimLayer: Manim mobjects and animations as a pure-time compositor layer.

Manim does not run the clock here. You register a *score* of events at absolute
audio times; the layer evaluates the scene state at any frame time t and
rasterises it with Cairo onto a transparent surface.

    m = s.manim()                                    # inside a @scene
    m.add(grid)                                      # present from the start
    m.play(Create(v), at=T.vector)                   # lands on the beat (starts `lead` early)
    m.play(ApplyMatrix(A, VGroup(grid, v)), at=T.stretch, dur=1.4, ease="easy_ease")
    m.seq(at=T.eq).play(Write(eq)).wait(0.3).play(Indicate(eq[0]))
    m.drive(dot, lambda d, t: d.move_to(curve(t)), during=(T.a, T.b))   # pure f(t)
    m.redraw(lambda t: Brace(bar(t)), during=(T.a, T.b))               # rebuilt each frame
    m.remove(old, at=T.next)

Anything that works in Scene.play works here (Transform, TransformMatchingTex,
LaggedStart, Succession, .animate, removers/introducers), because the layer
drives each Animation through begin → interpolate(alpha) → finish → cleanup.

Rules: no `add_updater` (stateful, dt-based): use `drive`/`redraw`. Never call
`Scene.play/wait`. Holds cost nothing: if no event is active, the previous
raster is reused.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np

from aion.core import time as _time
from aion.core.ease import ease as _ease
from aion.layers.base import ENC_SRGB_PREMUL, Layer, RenderContext, Surface

__all__ = ["ManimLayer", "BackwardSeek"]


class BackwardSeek(RuntimeError):
    """Raised when asked for an earlier time than already evaluated; the scene rebuilds."""


@dataclass(order=True)
class _Action:
    t: float
    rank: int            # finish < remove < add < begin at equal times
    seq: int
    kind: str = field(compare=False)
    payload: Any = field(compare=False)


@dataclass
class _Anim:
    anim: Any
    t0: float
    t1: float
    state: str = "pending"   # pending | active | done


@dataclass
class _Driver:
    mob: Any
    fn: Callable
    a: float
    b: float
    done_at_end: bool = False


def _shim(camera):
    """A Manim Scene instance without the renderer/file-writer machinery."""
    from manim import Scene

    class _ScoreScene(Scene):
        def __init__(self):  # noqa: D401 - deliberately skip Scene.__init__
            self.renderer = SimpleNamespace(camera=camera, skip_animations=True, time=0.0, static_image=None)
            self.mobjects, self.foreground_mobjects = [], []
            self.moving_mobjects, self.static_mobjects = [], []
            self.animations = None
            self.meshes = []

    return _ScoreScene()


class _Seq:
    """Chained plays: each starts when the previous ends (or later, at its own beat)."""

    def __init__(self, layer: "ManimLayer", t: float):
        self.layer, self.t = layer, t

    def play(self, *anims, at: float | None = None, dur: float | None = None, ease=None,
             lead: float | None = None) -> "_Seq":
        start = self.t if at is None else max(self.t, at - (_time.LEAD if lead is None else lead))
        self.t = self.layer.play(*anims, at=start, dur=dur, ease=ease, lead=0.0)
        return self

    def wait(self, seconds: float) -> "_Seq":
        self.t += seconds
        return self

    @property
    def end(self) -> float:
        return self.t


class ManimLayer(Layer):
    """Transparent Manim layer driven by a score of timed events. See module docstring.

    Example:
        m = ManimLayer(); m.add(Circle()); m.play(Create(sq), at=2.0)
    """

    vector = True

    def __init__(self, **kw):
        super().__init__(**kw)
        self._actions: list[_Action] = []
        self._anims: list[_Anim] = []
        self._drivers: list[_Driver] = []
        self._seq = 0
        self._ptr = 0                  # next action index
        self._t: float | None = None   # logic time already evaluated
        self._sorted = True
        self._scene = None
        self._camera = None
        self._tex = None
        self.windows: list[tuple[float, float]] = []   # when content may change
        self.instants: list[float] = []                # instantaneous changes

    # ── score API ────────────────────────────────────────────────────────────
    def _push(self, t: float, rank: int, kind: str, payload) -> None:
        if self._t is not None:
            raise RuntimeError("cannot add events after rendering started")
        self._seq += 1
        self._actions.append(_Action(t, rank, self._seq, kind, payload))
        self._sorted = False

    def add(self, *mobs, at: float = -math.inf):
        """Show mobjects from `at` (exact, no lead). Default: from the beginning."""
        self._push(at, 2, "add", mobs)
        if math.isfinite(at):
            self.instants.append(at)
        return mobs[0] if len(mobs) == 1 else mobs

    def remove(self, *mobs, at: float):
        """Hide mobjects at `at` (exact)."""
        self._push(at, 1, "remove", mobs)
        self.instants.append(at)

    def play(self, *anims, at: float, dur: float | None = None, ease=None, lead: float | None = None) -> float:
        """Run animations so they land on beat `at` (start = at − lead). Returns end time."""
        from manim import AnimationGroup

        anim = anims[0] if len(anims) == 1 else AnimationGroup(*anims)
        anim = getattr(anim, "build", lambda: anim)() if type(anim).__name__ == "_AnimationBuilder" else anim
        if dur is not None:
            anim.run_time = dur
        if ease is not None:
            anim.rate_func = _ease(ease)
        t0 = at - (_time.LEAD if lead is None else lead)
        t1 = t0 + max(anim.run_time, 1e-6)
        rec = _Anim(anim, t0, t1)
        self._anims.append(rec)
        self._push(t0, 3, "begin", rec)
        self._push(t1, 0, "finish", rec)
        self.windows.append((t0, t1))
        return t1

    def seq(self, at: float, lead: float | None = None) -> _Seq:
        """Start a chain of plays landing on `at`."""
        return _Seq(self, at - (_time.LEAD if lead is None else lead))

    def drive(self, mob, fn: Callable[[Any, float], Any], during: tuple[float, float] = (-math.inf, math.inf)):
        """Each frame in `during`, call fn(mob, t) to set mob's state as a pure function of t.
        Outside the window the state is held at the window's ends."""
        a, b = during
        self._drivers.append(_Driver(mob, fn, a, b))
        self.windows.append((a, b))
        return mob

    def redraw(self, fn: Callable[[float], Any], during: tuple[float, float] = (-math.inf, math.inf)):
        """A mobject rebuilt every frame from fn(t) (replacement for always_redraw)."""
        from manim import VGroup

        holder = VGroup()

        def apply(h, t):
            h.submobjects = [fn(t)]

        self.add(holder, at=during[0] if math.isfinite(during[0]) else -math.inf)
        self._drivers.append(_Driver(holder, apply, *during))
        self.windows.append(during)
        return holder

    # ── change detection ────────────────────────────────────────────────────
    def content_changes(self, t0: float, t1: float) -> bool:
        if any(a <= t1 and t0 < b for a, b in self.windows):
            return True
        return any(t0 < x <= t1 for x in self.instants)

    def cache_key(self):
        return super().cache_key() + [len(self._actions), self.windows, self.instants]

    # ── evaluation ──────────────────────────────────────────────────────────
    def _ensure(self, rc: RenderContext):
        if self._camera is None or (self._camera.pixel_width, self._camera.pixel_height) != rc.size:
            from manim import Camera

            fw, fh = rc.frame_units
            self._camera = Camera(pixel_width=rc.size[0], pixel_height=rc.size[1], frame_width=fw,
                                  frame_height=fh, background_opacity=0.0, background_color="#000000")
            if self._scene is None:
                self._scene = _shim(self._camera)
            else:
                self._scene.renderer.camera = self._camera
        if not self._sorted:
            self._actions.sort()
            self._sorted = True

    def advance(self, t: float) -> None:
        """Bring the scene state to time t (forward only)."""
        if self._t is not None and t < self._t - 1e-9:
            raise BackwardSeek(f"{self.name}: asked for {t:.3f}s after {self._t:.3f}s")
        sc = self._scene
        acts = self._actions
        while self._ptr < len(acts) and acts[self._ptr].t <= t:
            a = acts[self._ptr]
            self._ptr += 1
            if a.kind == "add":
                sc.add(*a.payload)
            elif a.kind == "remove":
                sc.remove(*a.payload)
            elif a.kind == "begin":
                rec = a.payload
                rec.anim._setup_scene(sc)
                rec.anim.begin()
                sc.add_mobjects_from_animations([rec.anim])
                rec.state = "active"
            elif a.kind == "finish":
                rec = a.payload
                rec.anim.finish()
                rec.anim.clean_up_from_scene(sc)
                rec.state = "done"
        for rec in self._anims:
            if rec.state == "active":
                rec.anim.update_mobjects(0)
                rec.anim.interpolate((t - rec.t0) / (rec.t1 - rec.t0))
        for d in self._drivers:
            if t < d.a:
                continue
            if t >= d.b:
                if d.done_at_end:
                    continue
                d.done_at_end = True
            d.fn(d.mob, min(t, d.b))
        self._t = t

    def mobjects(self) -> list:
        return list(self._scene.mobjects) if self._scene else []

    def draw(self, t: float, rc: RenderContext) -> Surface:
        self._ensure(rc)
        self.advance(t)
        cam = self._camera
        st = rc.cam
        if st is not None and self.parallax:
            z = st.zoom ** self.parallax
            cam.frame_center = np.array([st.x * self.parallax, st.y * self.parallax, 0.0])
            cam.frame_width, cam.frame_height = rc.frame_units[0] / z, rc.frame_units[1] / z
        cam.reset()
        cam.capture_mobjects(self._scene.mobjects)
        img = cam.pixel_array
        if self._tex is None or self._tex.size != rc.size:
            from aion.gpu.context import gl

            self._tex = gl().texture(rc.size, 4)
        self._tex.write(np.ascontiguousarray(img[::-1]).tobytes())
        rot = (st.rot * self.parallax) if st is not None else 0.0
        return Surface(self._tex, ENC_SRGB_PREMUL, None, screen_rot=rot)
