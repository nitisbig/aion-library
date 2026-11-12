"""aion.theme: semantic design tokens (C.<role>) shared by every layer."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {"Theme": "tokens", "BASE": "tokens", "MODERN": "tokens", "C": "tokens"}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
