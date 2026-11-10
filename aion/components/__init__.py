"""aion.components: theme-aware Manim building blocks (equations, labels, titles…)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {"Eqn": "text", "Label": "text", "Title": "text"}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
