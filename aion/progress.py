"""Whole-scene render progress bar with ETA.

Manim's built-in bars are per-animation, so they can't show an ETA for the whole
render. Inherit from `ProgressScene` instead of `Scene`:

    class MyScene(ProgressScene):
        TOTAL_DURATION = 45.0      # seconds; lets the bar show % and ETA from frame 1

You get one tqdm bar (frames done / total, elapsed, ETA, render fps) on stderr.
Progress is also written to `<media_dir>/progress/<Scene>.json` about once a second,
so a render running in the background can be monitored.

If TOTAL_DURATION isn't set, the duration of the previous render of the same scene
(stored in `<media_dir>/progress/durations.json`) is used. On a first render without
it, the bar counts frames with no ETA.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from manim import Scene, ThreeDScene, config
from tqdm import tqdm


def _progress_dir() -> Path:
    d = Path(config.media_dir) / "progress"
    d.mkdir(parents=True, exist_ok=True)
    return d


class RenderProgressMixin:
    TOTAL_DURATION: float | None = None

    # ── public hook ───────────────────────────────────────────────
    def render(self, preview: bool = False):
        name = type(self).__name__
        fps = config.frame_rate
        key = f"{name}@{config.pixel_height}p{fps:g}"
        durations_file = _progress_dir() / "durations.json"
        durations = self._read_json(durations_file)
        expected = self.TOTAL_DURATION or durations.get(name)
        total_frames = round(expected * fps) if expected else None

        self._pg_status = _progress_dir() / f"{name}.json"
        self._pg_start = time.monotonic()
        self._pg_last_write = 0.0
        self._pg_total = total_frames
        self._pg_bar = tqdm(
            total=total_frames, desc=key, unit="fr", dynamic_ncols=True, smoothing=0.1,
            bar_format=(
                "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]"
                if total_frames else "{desc}: {n_fmt} fr [{elapsed}, {rate_fmt}]"
            ),
        )

        renderer = self.renderer
        orig_add_frame, orig_play = renderer.add_frame, renderer.play

        def add_frame(*args, **kwargs):
            orig_add_frame(*args, **kwargs)
            self._pg_sync()

        def play(*args, **kwargs):  # also covers cached animations that skip add_frame
            orig_play(*args, **kwargs)
            self._pg_sync()

        renderer.add_frame, renderer.play = add_frame, play
        try:
            result = super().render(preview)
        finally:
            renderer.add_frame, renderer.play = orig_add_frame, orig_play
            self._pg_sync(force=True, done=True)
            self._pg_bar.close()

        durations[name] = round(renderer.time, 3)
        durations_file.write_text(json.dumps(durations, indent=2))
        movie = getattr(renderer.file_writer, "movie_file_path", None)
        took = time.monotonic() - self._pg_start
        tqdm.write(f"✔ {key}: {renderer.time:.2f}s of video in {took:.0f}s"
                   + (f" → {movie}" if movie else ""))
        return result

    # ── internals ─────────────────────────────────────────────────
    def _pg_sync(self, force: bool = False, done: bool = False) -> None:
        if getattr(self, "_pg_paused", False) and not done:
            return  # e.g. a NarratedScene silently replaying earlier scenes
        frames = round(self.renderer.time * config.frame_rate)
        bar = self._pg_bar
        if bar.total is not None and frames > bar.total:
            bar.total = frames  # the scene ran longer than expected
        if frames > bar.n:
            bar.update(frames - bar.n)

        now = time.monotonic()
        if not force and now - self._pg_last_write < 1.0:
            return
        self._pg_last_write = now
        elapsed = now - self._pg_start
        total = bar.total
        rate = frames / elapsed if elapsed > 0 else 0.0
        eta = (total - frames) / rate if (total and rate) else None
        status = {
            "scene": type(self).__name__,
            "quality": f"{config.pixel_height}p{config.frame_rate:g}",
            "frames": frames,
            "total_frames": total,
            "percent": round(100 * frames / total, 1) if total else None,
            "elapsed_s": round(elapsed, 1),
            "eta_s": round(eta, 1) if eta is not None else None,
            "done": done,
        }
        self._pg_status.write_text(json.dumps(status))

    @staticmethod
    def _read_json(path: Path) -> dict:
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return {}


class ProgressScene(RenderProgressMixin, Scene):
    """Drop-in replacement for manim.Scene with a whole-render progress bar."""


class ProgressThreeDScene(RenderProgressMixin, ThreeDScene):
    """Drop-in replacement for manim.ThreeDScene with a whole-render progress bar."""
