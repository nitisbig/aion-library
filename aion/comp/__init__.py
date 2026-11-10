"""aion.comp: the GPU layer compositor (linear light, blend modes, mattes, 2.5D camera)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "Comp": "comp", "hex_to_linear": "comp", "Camera": "camera", "BLEND_MODES": "blend",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
