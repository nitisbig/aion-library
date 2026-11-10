"""Blend modes (premultiplied, linear light).

Fast modes use GL blending: normal, add, screen. Advanced modes read the
destination in the shader: multiply, overlay, soft_light, difference,
lighten, darken, color_dodge.
"""

from __future__ import annotations

__all__ = ["BLEND_MODES", "FAST", "ADVANCED"]

FAST = {"normal", "add", "screen"}
ADVANCED = {"multiply": 10, "overlay": 11, "soft_light": 12, "difference": 13, "lighten": 14,
            "darken": 15, "color_dodge": 16}
BLEND_MODES = sorted(FAST | set(ADVANCED))


def gl_func(mode: str):
    import moderngl

    if mode == "add":
        return moderngl.ONE, moderngl.ONE
    if mode == "screen":
        return moderngl.ONE, moderngl.ONE_MINUS_SRC_COLOR
    return moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
