"""aion.sim: bake simulations once (Taichi / numpy), replay them as pure functions of t."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "Sim": "bake", "SimCache": "bake", "bake": "bake",
    "NBody": "builtin", "Particles": "builtin", "Wave2D": "builtin", "Heat2D": "builtin", "Springs": "builtin",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
