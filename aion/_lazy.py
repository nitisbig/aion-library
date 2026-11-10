"""Lazy exports: subpackages declare `EXPORTS = {name: module}` and stay cheap to import.

    # aion/sync/__init__.py
    EXPORTS = {"Cue": "cue", "beats": "beats"}
    __getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)

Heavy dependencies (manim, moderngl, taichi, pyvista) load only when a name
that needs them is first touched.
"""

from __future__ import annotations

import importlib


def lazy(pkg: str, exports: dict[str, str]):
    def __getattr__(name: str):
        mod = exports.get(name)
        if mod is None:
            raise AttributeError(f"module {pkg!r} has no attribute {name!r}")
        value = getattr(importlib.import_module(f"{pkg}.{mod}"), name)
        globals_ = importlib.import_module(pkg).__dict__
        globals_[name] = value  # cache: next access skips __getattr__
        return value

    def __dir__():
        return sorted(exports)

    return __getattr__, __dir__, sorted(exports)
