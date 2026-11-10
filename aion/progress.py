"""One progress bar with an ETA for every long job, plus a JSON status file.

    with Progress("004-demo", total=1800) as bar:     # frames, chunks, sim steps...
        for _ in range(1800):
            bar.update()

Prints `004-demo: 42%|████| 756/1800 fr [00:31 elapsed, ETA 00:43, 24.1fr/s]`
and finishes with `✔ 004-demo: … → <output>`. About once a second it writes
`media/progress/<name>.json` with frames, total_frames, percent, elapsed_s,
eta_s and done, so `aion status` can report on background renders.

`ProgressScene` / `ProgressThreeDScene` give a raw `manim` render the same bar
(only for exploration; production renders go through `aion render`).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from tqdm import tqdm

from aion._env import media_dir

__all__ = ["Progress", "read_status", "ProgressScene", "ProgressThreeDScene"]

_FMT = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} {unit} [{elapsed} elapsed, ETA {remaining}, {rate_fmt}]"
_FMT_NOTOTAL = "{desc}: {n_fmt} {unit} [{elapsed}, {rate_fmt}]"


def status_path(name: str) -> Path:
    return media_dir("progress") / f"{name.replace('/', '_')}.json"


class Progress:
    """tqdm bar + media/progress/<name>.json. `initial` counts cached work (ETA excludes it)."""

    def __init__(self, name: str, total: int | None, unit: str = "fr", initial: int = 0,
                 desc: str | None = None, disable: bool = False):
        self.name, self.total, self.unit = name, total, unit
        self.status = status_path(name)
        self.t0 = time.monotonic()
        self.initial = initial
        self.n = initial
        self._last = 0.0
        self.bar = tqdm(total=total, initial=initial, desc=desc or name, unit=unit,
                        dynamic_ncols=True, smoothing=0.1, disable=disable,
                        bar_format=_FMT if total else _FMT_NOTOTAL)
        self._write(force=True)

    def update(self, n: int = 1) -> None:
        self.n += n
        if self.total is not None and self.n > self.total:
            self.total = self.bar.total = self.n
        self.bar.update(n)
        self._write()

    def set(self, n: int) -> None:
        if n > self.n:
            self.update(n - self.n)

    def note(self, text: str) -> None:
        self.bar.set_postfix_str(text, refresh=False)

    def close(self, output: str | Path | None = None, ok: bool = True) -> None:
        self._write(force=True, done=True)
        self.bar.close()
        took = time.monotonic() - self.t0
        mark = "✔" if ok else "✘"
        tqdm.write(f"{mark} {self.name}: {self.n}/{self.total or self.n} {self.unit} in {took:.0f}s"
                   + (f" → {output}" if output else ""))

    def __enter__(self) -> "Progress":
        return self

    def __exit__(self, exc_type, *_):
        self.close(ok=exc_type is None)

    def _write(self, force: bool = False, done: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last < 1.0:
            return
        self._last = now
        elapsed = now - self.t0
        fresh = self.n - self.initial
        rate = fresh / elapsed if elapsed > 0 else 0.0
        eta = (self.total - self.n) / rate if (self.total and rate) else None
        self.status.write_text(json.dumps({
            "name": self.name, "unit": self.unit, "frames": self.n, "total_frames": self.total,
            "percent": round(100 * self.n / self.total, 1) if self.total else None,
            "elapsed_s": round(elapsed, 1), "eta_s": round(eta, 1) if eta is not None else None,
            "done": done, "updated": time.time(),
        }))


def read_status(name: str | None = None) -> list[dict]:
    """All progress JSONs (newest first), or the one for `name`."""
    files = [status_path(name)] if name else sorted(
        media_dir("progress").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for f in files:
        try:
            out.append(json.loads(f.read_text()))
        except (OSError, ValueError):
            pass
    return out


# ── raw-Manim exploration scenes ─────────────────────────────────────────────

def _progress_scene_classes():
    from manim import Scene, ThreeDScene, config

    class _Mixin:
        TOTAL_DURATION: float | None = None

        def render(self, preview: bool = False):
            fps = config.frame_rate
            total = round(self.TOTAL_DURATION * fps) if self.TOTAL_DURATION else None
            name = type(self).__name__
            bar = Progress(name, total, desc=f"{name}@{config.pixel_height}p{fps:g}")
            renderer = self.renderer
            add_frame, play = renderer.add_frame, renderer.play

            def sync():
                bar.set(round(renderer.time * fps))

            def _add_frame(*a, **k):
                add_frame(*a, **k)
                sync()

            def _play(*a, **k):
                play(*a, **k)
                sync()

            renderer.add_frame, renderer.play = _add_frame, _play
            ok = False
            try:
                result = super().render(preview)
                ok = True
            finally:
                renderer.add_frame, renderer.play = add_frame, play
                bar.close(getattr(renderer.file_writer, "movie_file_path", None), ok=ok)
            return result

    class ProgressScene(_Mixin, Scene):
        """manim.Scene with one whole-render progress bar (set TOTAL_DURATION)."""

    class ProgressThreeDScene(_Mixin, ThreeDScene):
        """manim.ThreeDScene with one whole-render progress bar."""

    return ProgressScene, ProgressThreeDScene


def __getattr__(name: str):
    if name in ("ProgressScene", "ProgressThreeDScene"):
        a, b = _progress_scene_classes()
        globals().update(ProgressScene=a, ProgressThreeDScene=b)
        return globals()[name]
    raise AttributeError(name)
