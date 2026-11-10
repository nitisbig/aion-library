"""aion.render: scene builder, frame scheduling, encoding, muxing, stills."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {"Encoder": "encode", "scene": "scenes", "SceneBuilder": "scenes", "Video": "project", "load_video": "project"}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
