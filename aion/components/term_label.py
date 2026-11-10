"""Equation labels pinned to spinning circles.

    from aion.components.term_label import exp_tex, sin_tex, labels
    g = labels([(center, radius, exp_tex(3), S.FWD)], op=1.0)     # c₃ e^{2πi·3t} beside the circle

Each label is a LaTeX term, built once per (tex, size, color) and copied per frame, so it is
cheap inside a redraw. A dark background stroke keeps it legible over rims and ink.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import MathTex, VGroup

from aion import style as S


def exp_tex(n: int, coef: str | None = None) -> str:
    """The series term for speed n: c_n e^{2πint} with n written in (c₁ e^{2πit}, c₋₃ e^{−2πi·3t})."""
    c = coef if coef is not None else f"c_{{{n}}}"
    if n == 0:
        return c
    return c + r"\," + exp_part(n)


def exp_part(n: int) -> str:
    """e^{2πit}, e^{−2πi·3t}: the turning part of the term (empty for n = 0)."""
    if n == 0:
        return ""
    sgn = "-" if n < 0 else ""
    k = "" if abs(n) == 1 else rf"\cdot {abs(n)}"
    return rf"e^{{{sgn}2\pi i{k}t}}"


def exp_parts(n: int, color, coef: str | None = None, coef_color=S.STILL) -> tuple:
    """((c_n, green), (e^{2πint}, white)): the coefficient keeps the video's c_n color; the rest is
    label white, never the circle's own color (`color` is accepted for old call sites)."""
    c = coef if coef is not None else f"c_{{{n}}}"
    head = ((c, str(coef_color)),) if c else ()
    return head + (((exp_part(n), str(S.LABEL)),) if n else ())


def sin_tex(n: int, amp: str) -> str:
    """A real term, e.g. sin_tex(3, r'\\tfrac{4}{3\\pi}') → 4/(3π) sin 3t."""
    k = "" if n == 1 else str(n)
    return rf"{amp}\,\sin {k}t"


@lru_cache(maxsize=512)
def _tex(tex, size: float, color: str) -> MathTex:
    """tex: one string (one color) or a tuple of (part, color) pairs."""
    if isinstance(tex, tuple):
        m = MathTex(*[p for p, _ in tex], font_size=size)
        for sub_, (_, col) in zip(m, tex):
            sub_.set_color(col)
    else:
        m = MathTex(tex, font_size=size, color=color)
    m.set_stroke(S.STAGE if hasattr(S, "STAGE") else "#000000", width=5, opacity=0.85, background=True)
    return m


def label(tex: str, at, size: float = 28, color=S.TEXT, op: float = 1.0) -> MathTex:
    m = _tex(tex, float(size), str(color)).copy().move_to(np.asarray(at, float))
    return m.set_opacity(op) if op < 1 else m


def labels(items, op: float = 1.0, size: float = 28, pad: float = 0.1, angles=(125.0, 55.0, 20.0, -20.0),
           min_r: float = 0.18) -> VGroup:
    """items: (center complex, radius, tex, color[, angle°]). Each label sits just outside its circle.

    tex is a string, or exp_parts(...) for a two-color term (green c_n, direction-colored e^{…})."""
    g = VGroup()
    if op <= 0:
        return g
    for k, it in enumerate(items):
        c, r, tex, col = it[:4]
        if r < min_r:
            continue
        th = np.radians(it[4] if len(it) > 4 else angles[k % len(angles)])
        d = np.array([np.cos(th), np.sin(th)])
        m = _tex(tex, float(size), str(S.LABEL)).copy()     # text stays white, apart from its circle
        w, h = m.width / 2, m.height / 2
        reach = r + pad + abs(d[0]) * w + abs(d[1]) * h      # the label's near edge touches the anchor
        p = np.array([c.real, c.imag]) + reach * d
        m.move_to([p[0], p[1], 0.0])
        g.add(m.set_opacity(op) if op < 1 else m)
    return g
