"""One headless OpenGL context per process (standalone, then EGL fallback).

    from aion.gpu import gl
    ctx = gl()                     # moderngl.Context on the Radeon R4
    info()                         # {'renderer': ..., 'version': ..., 'backend': ..., 'float16': True}

Never create contexts elsewhere; every layer, effect and the compositor share
this one. Render workers are spawned (not forked) so each gets its own.
"""

from __future__ import annotations

import os

_CTX = None
_BACKEND = None


def gl():
    """The process-wide moderngl context (created on first call).

    Example:
        ctx = gl(); tex = ctx.texture((64, 64), 4)
    """
    global _CTX, _BACKEND
    if _CTX is not None:
        return _CTX
    import moderngl

    errors = []
    for backend in (None, "egl"):
        try:
            if backend == "egl":
                os.environ.setdefault("EGL_PLATFORM", "surfaceless")
                _CTX = moderngl.create_context(standalone=True, backend="egl", require=330)
            else:
                _CTX = moderngl.create_context(standalone=True, require=330)
            _BACKEND = backend or "standalone"
            break
        except Exception as e:  # pragma: no cover - depends on the machine
            errors.append(f"{backend or 'standalone'}: {e}")
    if _CTX is None:
        raise RuntimeError("no OpenGL context: " + " | ".join(errors))
    return _CTX


def float16_renderable() -> bool:
    """Can we render into RGBA16F textures (needed for linear-light compositing)?"""
    ctx = gl()
    try:
        tex = ctx.texture((4, 4), 4, dtype="f2")
        fbo = ctx.framebuffer([tex])
        fbo.use()
        ctx.clear(0.5, 0.25, 1.0, 1.0)
        ok = abs(float(memoryview(fbo.read(components=4, dtype="f2")).cast("e")[0]) - 0.5) < 1e-3
        fbo.release()
        tex.release()
        return ok
    except Exception:
        return False


def info() -> dict:
    ctx = gl()
    return {
        "backend": _BACKEND,
        "renderer": ctx.info.get("GL_RENDERER"),
        "version": ctx.info.get("GL_VERSION"),
        "max_texture": ctx.info.get("GL_MAX_TEXTURE_SIZE"),
        "float16": float16_renderable(),
    }
