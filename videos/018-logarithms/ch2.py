"""Chapter two's shared pieces: the 8·32 identity (c02_s01 writes it, c02_s02 opens on it)."""
from aion import *  # noqa: F403

from kit import P3, ctex


def identity():
    """8·32 = 2³·2⁵ = 2³⁺⁵ = 256, coloured by role."""
    return ctex([("8", C.value), (r"\cdot", None), ("32", C.value), ("=", None), ("2", C.base), ("^3", C.steps),  # noqa: F405
                 (r"\cdot", None), ("2", C.base), ("^5", C.steps), ("=", None), ("2", C.base), ("^{3+5}", C.steps),  # noqa: F405
                 ("=", None), ("256", C.value)], 46).move_to(P3(2.75, -2.35))  # noqa: F405
