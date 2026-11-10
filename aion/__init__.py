"""aion: agent-native animation engine for math / CS / physics explainer videos.

Scenes start with `from aion import *`. That gives every aion export
(see `uv run aion catalog`) plus Manim's public names. aion names win on clashes.

Importing `aion` itself is cheap: subpackages are loaded on first use, so the CLI
and the voice pipeline never pay for Manim, moderngl, taichi or pyvista.
"""

from __future__ import annotations

import importlib

from aion import _env

_env.setup()

__version__ = "2.0.0.dev0"

SUBPACKAGES = (
    "core", "sync", "voice", "theme", "gpu", "layers", "comp", "fx",
    "sim", "maths", "components", "render", "audit",
)

_REGISTRY: dict[str, str] | None = None


def registry() -> dict[str, str]:
    """{export name: 'aion.sub.module'} for every public aion symbol."""
    global _REGISTRY
    if _REGISTRY is None:
        reg: dict[str, str] = {}
        for sub in SUBPACKAGES:
            try:
                pkg = importlib.import_module(f"aion.{sub}")
            except ImportError:
                continue
            for name, mod in getattr(pkg, "EXPORTS", {}).items():
                reg.setdefault(name, f"aion.{sub}.{mod}")
        _REGISTRY = reg
    return _REGISTRY


def _manim_names() -> list[str]:
    import manim

    return [n for n in dir(manim) if not n.startswith("_")]


def __getattr__(name: str):
    if name == "__all__":
        return sorted(set(_manim_names()) | set(registry()))
    mod = registry().get(name)
    if mod is not None:
        value = getattr(importlib.import_module(mod), name)
    elif name.startswith("_"):
        raise AttributeError(name)
    else:
        import manim

        if not hasattr(manim, name):
            raise AttributeError(f"aion has no attribute {name!r} (try `aion catalog {name}`)")
        value = getattr(manim, name)
    globals()[name] = value
    return value
