"""aion.fx: GPU effects for layers and whole frames (all parameters animatable)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "Effect": "base",
    "Bloom": "effects", "Glow": "effects", "Blur": "effects", "Grade": "effects", "Lens": "effects",
    "Vignette": "effects", "Grain": "effects", "ChromaticAberration": "effects", "ZoomBlur": "effects", "Tonemap": "effects",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
