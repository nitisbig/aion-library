"""Load a production video: video.py settings, beats, theme, and its @scene list.

    vid = load_video("004")          # configures Manim + theme, imports scenes/*
    vid.scenes, vid.duration, vid.check()

Video folders put their own dir on sys.path, so scenes write
`from beats import T` and `from theme import theme`.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

from aion import cache
from aion._env import PKG
from aion.project import VideoPaths, find_video

__all__ = ["Video", "LoadedVideo", "load_video", "QUALITY", "configure_manim"]

QUALITY = {
    "preview": ((854, 480), 15),
    "low": ((854, 480), 30),
    "draft": ((1280, 720), 30),
    "final": ((1920, 1080), 60),
    "4k": ((3840, 2160), 60),
}


@dataclass
class Video:
    """Declared in videos/<slug>/video.py.

    Example:
        video = Video(theme=theme, fps=60)
    """

    theme: object = None
    fps: float = 60
    size: tuple[int, int] = (1920, 1080)
    title: str = ""
    background: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class LoadedVideo:
    paths: VideoPaths
    video: Video
    scenes: list
    duration: float

    @property
    def slug(self) -> str:
        return self.paths.slug

    def scene(self, name: str):
        for s in self.scenes:
            if s.name == name or s.name.startswith(name):
                return s
        raise KeyError(f"no scene {name!r}; scenes: {[s.name for s in self.scenes]}")

    def check(self) -> None:
        from aion.sync.cuts import check_contiguous

        check_contiguous([(s.name, s.start, s.end) for s in self.scenes], self.duration, self.video.fps)

    def source_hash(self) -> str:
        """Everything a rendered frame depends on besides settings."""
        return cache.key(cache.tree_hash(self.paths.dir, ("*.py", "*.glsl", "*.frag", "*.toml")),
                         cache.tree_hash(PKG), [str(self.paths.srt and cache.file_hash(self.paths.srt))])


def configure_manim(size: tuple[int, int], fps: float, frame_height: float = 8.0) -> None:
    """Set Manim's global frame so mobject layout (to_edge, etc.) matches the comp."""
    from manim import config

    config.pixel_width, config.pixel_height = size
    config.frame_rate = fps
    config.frame_height = frame_height
    config.frame_width = frame_height * size[0] / size[1]
    config.verbosity = "WARNING"
    config.progress_bar = "none"


def _import(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_video(ref, size: tuple[int, int] | None = None, fps: float | None = None,
               only: list[str] | None = None) -> LoadedVideo:
    """Import a video folder. `only` limits which scene files are imported (by prefix).

    Example:
        vid = load_video("004", size=(854, 480), fps=15); vid.check()
    """
    from aion.render import scenes as scene_mod
    from aion.sync.silence import audio_duration
    from aion.theme.tokens import activate

    paths = ref if isinstance(ref, VideoPaths) else find_video(ref)
    d = str(paths.dir)
    if d not in sys.path:
        sys.path.insert(0, d)
    from aion.gpu import program as gprog

    if (paths.dir / "shaders").is_dir() and paths.dir / "shaders" not in gprog.SEARCH_PATH:
        gprog.SEARCH_PATH.insert(0, paths.dir / "shaders")

    vfile = paths.dir / "video.py"
    video = _import(vfile, "video").video if vfile.exists() else Video()
    if video.theme is not None:
        activate(video.theme)
    configure_manim(size or video.size, fps or video.fps)
    from aion.theme.manim import apply
    from aion.theme.tokens import current

    apply(current())

    scene_mod.REGISTRY.clear()
    files = sorted(paths.scenes.glob("s*.py")) if paths.scenes.is_dir() else []
    for f in files:
        if only and not any(f.stem.startswith(o) or o.startswith(f.stem.split("_")[0]) for o in only):
            continue
        _import(f, f"scenes_{f.stem}")
    scenes = sorted(scene_mod.REGISTRY, key=lambda s: s.start)
    duration = audio_duration(paths.audio) if paths.audio else (scenes[-1].end if scenes else 0.0)
    return LoadedVideo(paths, video, scenes, duration)
