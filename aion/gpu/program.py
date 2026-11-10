"""Shader programs: source loading with #include, caching, uniform auto-binding.

    prog = program("layers/my.frag")              # fullscreen vert + this frag
    set_uniforms(prog, u_glow=0.4, u_matrix=np.eye(2))
    fullscreen(prog).render(vertices=3)

Shader search path: the video's `shaders/` dir (if registered), then aion/shaders.
`#include "common/color.glsl"` is resolved recursively.
"""

from __future__ import annotations

import hashlib
import re
import warnings
from pathlib import Path

import numpy as np

from aion._env import SHADERS
from aion.gpu.context import gl

__all__ = ["program", "fullscreen", "set_uniforms", "load_source", "SEARCH_PATH"]

SEARCH_PATH: list[Path] = [SHADERS]
_INC = re.compile(r'^\s*#include\s+"([^"]+)"', re.M)
_PROGRAMS: dict[str, object] = {}
_VAOS: dict[int, object] = {}
_WARNED: set[tuple[str, str]] = set()


def _find(name: str) -> Path:
    p = Path(name)
    if p.is_absolute() and p.exists():
        return p
    for root in SEARCH_PATH:
        if (root / name).exists():
            return root / name
    raise FileNotFoundError(f"shader {name!r} not in {[str(r) for r in SEARCH_PATH]}")


def load_source(src: str, _depth: int = 0) -> str:
    """File name or inline GLSL → source with includes expanded."""
    if "\n" not in src and src.endswith((".frag", ".vert", ".glsl", ".comp")):
        src = _find(src).read_text()
    if _depth > 8:
        raise RecursionError("#include nesting too deep")
    return _INC.sub(lambda m: load_source(_find(m.group(1)).read_text(), _depth + 1), src)


def program(frag: str, vert: str = "common/fullscreen.vert"):
    """Compiled (cached) program for a fragment shader file or inline source."""
    vs, fs = load_source(vert), load_source(frag)
    if not fs.lstrip().startswith("#version"):
        fs = "#version 330\n" + fs
    k = hashlib.sha1((vs + "\0" + fs).encode()).hexdigest()
    prog = _PROGRAMS.get(k)
    if prog is None:
        try:
            prog = _PROGRAMS[k] = gl().program(vertex_shader=vs, fragment_shader=fs)
        except Exception as e:
            raise RuntimeError(f"shader compile failed ({frag if len(frag) < 80 else 'inline'}):\n{e}") from None
    return prog


def fullscreen(prog):
    """Vertex array that draws a fullscreen triangle (render with vertices=3)."""
    vao = _VAOS.get(id(prog))
    if vao is None:
        vao = _VAOS[id(prog)] = gl().vertex_array(prog, [])
    return vao


def _glsl_value(v):
    a = np.asarray(v, dtype="f4")
    if a.ndim == 2:  # numpy row-major matrix -> GLSL column-major
        return tuple(a.T.reshape(-1).tolist())
    if a.ndim == 0:
        return float(a)
    return tuple(a.reshape(-1).tolist())


def set_uniforms(prog, strict: bool = False, **uniforms) -> None:
    """Assign uniforms by name. Textures: pass (texture, unit). Unknown names warn once."""
    for name, value in uniforms.items():
        if name not in prog:
            if strict:
                raise KeyError(f"uniform {name!r} not used by shader")
            tag = (str(id(prog)), name)
            if tag not in _WARNED and name not in _AUTO:
                warnings.warn(f"uniform {name!r} is not used by the shader (typo?)", stacklevel=3)
            _WARNED.add(tag)
            continue
        if isinstance(value, tuple) and len(value) == 2 and hasattr(value[0], "use"):
            tex, unit = value
            tex.use(unit)
            prog[name].value = unit
        elif isinstance(value, (int, np.integer)) and not isinstance(value, bool) and \
                getattr(prog[name], "fmt", "") in ("1i", "1u"):
            prog[name].value = int(value)
        else:
            prog[name].value = _glsl_value(value)


_AUTO = {"u_time", "u_local", "u_res", "u_frame", "u_seed", "u_view", "u_view_inv", "u_frame_index",
         "u_opacity", "u_progress"}
