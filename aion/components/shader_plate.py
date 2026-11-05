"""A full-frame GPU (moderngl) layer inside a Manim scene.

    theta = ValueTracker(0)
    plate = ShaderPlate("domain_coloring.frag",
                        lambda: {"u_theta": theta.get_value(), "u_opacity": op.get_value(), ...})
    self.add(plate)          # re-rendered on the GPU every frame, at the output resolution

The fragment shader runs once per output frame on a headless standalone
context (the Radeon R4 here) and the pixels are handed to Cairo as an
ImageMobject. `u_frame` (Manim frame size in units) is set automatically, so a
shader can work directly in Manim coordinates via `v_uv`.

Drive it only through the uniform callback (ValueTrackers). Don't animate the
plate itself (FadeIn, .animate): copies of it would share GPU state. Put a
`u_opacity` uniform in the shader instead.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import moderngl
import numpy as np
from manim import ORIGIN, ImageMobject, config

from . import blit

blit.install()

SHADER_DIR = Path(__file__).resolve().parents[1] / "shaders"

_VERT = """
#version 330
in vec2 in_pos;
out vec2 v_uv;
void main() { v_uv = in_pos * 0.5 + 0.5; gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

_GL: dict[int, dict] = {}   # GPU state kept outside the mobject (mobjects get deep-copied)
_CTX: list = []


def _ctx():
    if not _CTX:
        _CTX.append(moderngl.create_context(standalone=True))
    return _CTX[0]


class ShaderPlate(ImageMobject):
    def __init__(self, frag: str | Path, uniforms: Callable[[], dict], scale: float = 1.0, **kw):
        w = max(2, int(config.pixel_width * scale))
        h = max(2, int(config.pixel_height * scale))
        src = Path(frag)
        if not src.is_absolute():
            src = SHADER_DIR / src
        ctx = _ctx()
        prog = ctx.program(vertex_shader=_VERT, fragment_shader=src.read_text())
        vbo = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes())
        vao = ctx.vertex_array(prog, [(vbo, "2f", "in_pos")])
        fbo = ctx.framebuffer(color_attachments=[ctx.texture((w, h), 4)])

        super().__init__(np.zeros((h, w, 4), dtype=np.uint8), **kw)
        self._gl_key = id(self)
        _GL[self._gl_key] = {"prog": prog, "vao": vao, "fbo": fbo, "size": (w, h),
                             "uniforms": uniforms}
        self.stretch_to_fit_width(config.frame_width)
        self.stretch_to_fit_height(config.frame_height)
        self.move_to(ORIGIN)
        self._fast_blit = True
        self.render_gl()
        self.add_updater(lambda m: m.render_gl())

    def render_gl(self) -> "ShaderPlate":
        gl = _GL[self._gl_key]
        prog = gl["prog"]
        values = {"u_frame": (config.frame_width, config.frame_height), **gl["uniforms"]()}
        for k, v in values.items():
            if k in prog:
                prog[k].value = v
        gl["fbo"].use()
        gl["fbo"].clear(0, 0, 0, 0)
        gl["vao"].render()
        w, h = gl["size"]
        arr = np.frombuffer(gl["fbo"].read(components=4), dtype=np.uint8).reshape(h, w, 4)
        self.pixel_array = np.ascontiguousarray(arr[::-1])
        return self
