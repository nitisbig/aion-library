"""Effect protocol and the GPU pass helper every effect uses.

An Effect takes a full-frame linear premultiplied RenderTarget and returns one
(possibly a new pooled target). Parameters may be Tracks, so effects animate:

    Bloom(strength=0.3 + pulse(T.lam, 0.6))
"""

from __future__ import annotations

from aion.core.track import Track, track
from aion.gpu import pool
from aion.gpu.program import fullscreen, program, set_uniforms

__all__ = ["Effect", "gpu_pass"]


def gpu_pass(frag: str, size, dtype: str = "f2", **uniforms):
    """Run a fullscreen fragment shader into a new pooled target."""
    rt = pool.target(tuple(size), dtype)
    prog = program(frag)
    set_uniforms(prog, **uniforms)
    rt.use(clear=None)
    fullscreen(prog).render(vertices=3)
    return rt


class Effect:
    """Base effect. Subclasses implement apply(); params given as Tracks.

    Example:
        class Desat(Effect):
            def __init__(self, amount=1.0): super().__init__(amount=amount)
            def apply(self, rt, t, rc):
                return gpu_pass("fx/grade.frag", rt.size, u_src=(rt.tex, 0), u_sat=1 - self.p("amount", t))
    """

    animated = False   # True: output depends on t even with constant params (e.g. grain)

    def __init__(self, **params):
        self.params: dict[str, Track] = {k: track(v) for k, v in params.items()}

    def p(self, name: str, t: float):
        return self.params[name](t)

    def changes(self, t0: float, t1: float) -> bool:
        return self.animated or any(tr.changes(t0, t1) for tr in self.params.values())

    def apply(self, rt, t: float, rc):
        raise NotImplementedError

    def cache_key(self):
        return [type(self).__name__, {k: v.label for k, v in self.params.items()}]

    def __repr__(self):
        return f"{type(self).__name__}()"
