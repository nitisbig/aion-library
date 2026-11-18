"""aion.components: theme-aware Manim building blocks (equations, labels, titles, matrices, grids, panels…)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {"Eqn": "text", "Label": "text", "Title": "text",
                           "Mat": "linalg", "grid_lines": "linalg", "panel": "linalg", "brackets": "linalg",
                           "fmt": "linalg"}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
