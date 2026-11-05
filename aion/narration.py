"""Scenes that play a slice of the narration and time everything from the SRT.

    class Scene03QuarterTurn(NarratedScene):
        AUDIO, SRT = ".../audio.mp3", ".../cue-per-word.srt"
        SCENE_START, SCENE_END = 1318 / 60, 2110 / 60   # absolute seconds in the audio
        PREVIOUS = Scene02Puzzle                         # optional, see "Hand-off"

        def timeline(self):
            h = self.handoff                             # objects left by Scene02
            self.play_at(self.t("flips"), Rotate(...), run_time=1.3)
            ...
            self.handoff = {...}                         # for the next scene
            self.finish()                                # hold until SCENE_END

Timing: every time passed to `wait_until` / `play_at` is an ABSOLUTE audio time,
so beats read exactly like the SRT. Run times and waits snap to whole frames so
clip lengths stay frame-exact. A beat that starts late (the previous animation
was still running) prints a warning.

Hand-off: if PREVIOUS is set, `construct` first replays the earlier scenes'
timelines with animations skipped (no frames written, no audio), which leaves
the exact objects and layout of the previous scene's last frame on screen and
in `self.handoff`. Cuts between clips are then invisible by construction.
Timelines must only use `self.*` API from NarratedScene (not helper methods
defined on their own class), because they also run on later scene instances.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from manim import config
from tqdm import tqdm

from . import style as S
from .progress import ProgressScene
from .sync import Cue


def audio_slice(audio: str | Path, start: float, end: float) -> Path:
    """Cut [start, end) of `audio` to a cached WAV under media/audio_slices/."""
    out_dir = Path(config.media_dir) / "audio_slices"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{Path(audio).stem}_{start:.3f}_{end:.3f}.wav"
    if not out.exists():
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
             "-i", str(audio), "-ac", "2", "-ar", "48000", str(out)],
            check=True,
        )
    return out


class NarratedScene(ProgressScene):
    AUDIO: str | Path | None = None
    SRT: str | Path | None = None
    SCENE_START: float = 0.0
    SCENE_END: float | None = None
    PREVIOUS: type | None = None
    BACKGROUND: str = S.BG
    LATE_TOLERANCE = 0.05   # seconds a beat may slip before warning

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if cls.SCENE_END is not None and "TOTAL_DURATION" not in cls.__dict__:
            cls.TOTAL_DURATION = cls.SCENE_END - cls.SCENE_START

    def setup(self):
        super().setup()
        self.camera.background_color = self.BACKGROUND
        self.cue = Cue.load(self.SRT) if self.SRT else None
        self.handoff: dict = {}
        self._seg = (self.SCENE_START, self.SCENE_END)
        self._replaying = False
        if self.AUDIO and self.SCENE_END is not None:
            self.add_sound(str(audio_slice(self.AUDIO, self.SCENE_START, self.SCENE_END)))

    # ── structure ──────────────────────────────────────────────
    def timeline(self) -> None:
        raise NotImplementedError

    def construct(self):
        chain, cls = [], self.PREVIOUS
        while cls is not None:
            chain.append(cls)
            cls = cls.PREVIOUS
        for prev in reversed(chain):
            self._replay(prev)
        self._seg = (self.SCENE_START, self.SCENE_END)
        self.timeline()

    def _replay(self, cls) -> None:
        r = self.renderer
        saved = (r._original_skipping_status, r.skip_animations, r.time)
        r._original_skipping_status = r.skip_animations = True
        self._pg_paused = self._replaying = True
        self._seg = (cls.SCENE_START, cls.SCENE_END)
        r.time = 0.0
        try:
            cls.timeline(self)
        finally:
            r._original_skipping_status, r.skip_animations, r.time = saved
            self._pg_paused = self._replaying = False

    # ── time ───────────────────────────────────────────────────
    @property
    def fps(self) -> float:
        return config.frame_rate

    def snap(self, seconds: float) -> float:
        """Round a duration to a whole number of frames (at least one)."""
        return max(1, round(seconds * self.fps)) / self.fps

    @property
    def now(self) -> float:
        """Current ABSOLUTE audio time."""
        return self._seg[0] + self.renderer.time

    def t(self, text: str, after: float | None = None) -> float:
        """Absolute start time of `text`, searching from the segment start by default."""
        return self.cue.at(text, after=self._seg[0] - 0.05 if after is None else after)

    def t_end(self, text: str, after: float | None = None) -> float:
        return self.cue.end_of(text, after=self._seg[0] - 0.05 if after is None else after)

    def wait_until(self, t_abs: float) -> None:
        dt = t_abs - self.now
        frames = round(dt * self.fps)
        if frames >= 1:
            self.wait(frames / self.fps)
        elif dt < -self.LATE_TOLERANCE and not self._replaying:
            tqdm.write(f"⚠ {type(self).__name__}: beat at {t_abs:.2f}s starts "
                       f"{-dt:.2f}s late (now {self.now:.2f}s)")

    def play_at(self, t_abs: float, *anims, lead: float = S.LEAD, run_time: float = 1.0, **kw):
        """Start `anims` at t_abs - lead (absolute), with a frame-snapped run_time."""
        self.wait_until(t_abs - lead)
        self.play(*anims, run_time=self.snap(run_time), **kw)

    def finish(self) -> None:
        if self._seg[1] is not None:
            self.wait_until(self._seg[1])
