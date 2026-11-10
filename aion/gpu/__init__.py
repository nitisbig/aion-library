"""aion.gpu: the shared headless OpenGL context, resource pool and programs."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {"gl": "context"}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
