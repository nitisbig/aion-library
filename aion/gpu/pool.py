"""Render targets (texture + framebuffer) recycled by (size, dtype).

    rt = target((1920, 1080), "f2")     # RGBA16F
    rt.fbo.use(); ...; release(rt)      # back to the pool

Persistent targets (layer caches) are allocated with `target(..., pooled=False)`
and freed when their owner is garbage-collected.
"""

from __future__ import annotations

import weakref
from collections import defaultdict
from dataclasses import dataclass

from aion.gpu.context import gl

__all__ = ["RenderTarget", "target", "release", "clear_pool"]

_FREE: dict[tuple, list["RenderTarget"]] = defaultdict(list)


@dataclass(eq=False)
class RenderTarget:
    tex: object
    fbo: object
    size: tuple[int, int]
    dtype: str

    def use(self, clear: tuple | None = (0.0, 0.0, 0.0, 0.0)):
        self.fbo.use()
        if clear is not None:
            self.fbo.clear(*clear)
        return self

    def free(self):
        self.fbo.release()
        self.tex.release()


def _free(tex, fbo) -> None:
    fbo.release()
    tex.release()


def _make(size, dtype, filt) -> RenderTarget:
    ctx = gl()
    tex = ctx.texture(size, 4, dtype=dtype)
    tex.filter = filt
    tex.repeat_x = tex.repeat_y = False
    return RenderTarget(tex, ctx.framebuffer([tex]), tuple(size), dtype)


def target(size: tuple[int, int], dtype: str = "f2", pooled: bool = True, linear: bool = True) -> RenderTarget:
    import moderngl

    filt = (moderngl.LINEAR, moderngl.LINEAR) if linear else (moderngl.NEAREST, moderngl.NEAREST)
    k = (tuple(size), dtype, filt)
    if pooled and _FREE[k]:
        return _FREE[k].pop()
    rt = _make(size, dtype, filt)
    if not pooled:
        weakref.finalize(rt, _free, rt.tex, rt.fbo)
    rt._key = k
    return rt


def release(rt: RenderTarget) -> None:
    _FREE[rt._key].append(rt)


def clear_pool() -> None:
    for lst in _FREE.values():
        for rt in lst:
            rt.free()
    _FREE.clear()
