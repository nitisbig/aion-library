"""aion.maths: numerics behind the visuals (always computed, never eyeballed)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
