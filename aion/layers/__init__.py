"""aion.layers: everything that can be stacked in a Comp (all pure functions of t)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "Layer": "base", "Surface": "base",
    "Solid": "solid", "Gradient": "solid",
    "ShaderLayer": "shader", "ManimLayer": "manim",
    "ImageLayer": "media", "ArrayLayer": "media",
    "PointsLayer": "points", "FieldLayer": "points",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
