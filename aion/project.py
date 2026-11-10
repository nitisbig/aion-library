"""Locate a production video folder and its inputs (cheap, no heavy imports).

    v = find_video("004")            # or "004-eigen", or a path
    v.dir, v.audio, v.srt, v.slug
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path

from aion._env import VIDEOS

__all__ = ["VideoPaths", "find_video", "video_of_caller"]

SRT_NAME = "cue-per-word.srt"


@dataclass(frozen=True)
class VideoPaths:
    dir: Path

    @property
    def slug(self) -> str:
        return self.dir.name

    @property
    def assets(self) -> Path:
        return self.dir / "assets"

    @property
    def out(self) -> Path:
        d = self.dir / "out"
        d.mkdir(exist_ok=True)
        return d

    @property
    def audio(self) -> Path | None:
        """Master audio: audio.wav preferred (sample-exact), else audio.mp3."""
        for name in ("audio.wav", "audio.mp3", "audio.m4a", "audio.flac"):
            p = self.assets / name
            if p.exists():
                return p
        return None

    @property
    def srt(self) -> Path | None:
        for name in (SRT_NAME, "words.json", "cue-per-words.srt"):
            p = self.assets / name
            if p.exists():
                return p
        return None

    @property
    def scenes(self) -> Path:
        return self.dir / "scenes"


def find_video(ref: str | Path) -> VideoPaths:
    """Resolve '004', '004-eigen', 'videos/004-eigen' or an absolute path."""
    p = Path(ref)
    if p.is_dir():
        return VideoPaths(p.resolve())
    if (VIDEOS / str(ref)).is_dir():
        return VideoPaths((VIDEOS / str(ref)).resolve())
    hits = sorted(d for d in VIDEOS.glob(f"{ref}*") if d.is_dir()) if VIDEOS.exists() else []
    if len(hits) == 1:
        return VideoPaths(hits[0].resolve())
    raise FileNotFoundError(f"no unique video matching {ref!r} in {VIDEOS} (found {[h.name for h in hits]})")


def video_dir_of(path: str | Path) -> VideoPaths:
    """The video folder containing `path` (walks up to the folder that has assets/)."""
    p = Path(path).resolve()
    for d in [p] + list(p.parents):
        if (d / "assets").is_dir() and d != Path(d.anchor):
            return VideoPaths(d)
    raise FileNotFoundError(f"{path} is not inside a video folder (no assets/ above it)")


def video_of_caller(depth: int = 2) -> VideoPaths:
    frame = inspect.stack()[depth]
    return video_dir_of(frame.filename)
