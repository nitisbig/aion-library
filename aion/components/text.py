"""Theme-aware text and equation mobjects (Manim) for ManimLayer scores.

    eq = Eqn(r"A \\vec v = \\lambda \\vec v", colors={r"\\lambda": C.vec, r"\\vec v": C.x})
    m.play(Write(eq), at=T.eq)
    m.play(Indicate(eq.part(r"\\lambda")), at=T.lam)

    Label("eigenvector", color=C.x).next_to(v, UR)
    Title("Eigenvectors")            # display font, safe top margin
"""

from __future__ import annotations

__all__ = ["Eqn", "Label", "Title"]


def _theme():
    from aion.theme.tokens import current

    return current()


def Eqn(tex: str, colors: dict[str, str] | None = None, size: float | None = None, **kw):
    """MathTex with named terms isolated and colored by the theme (same color as their visuals).

    Example:
        eq = Eqn(r"f(x) = x^2", colors={"x": C.x, "f(x)": C.fx}); eq.part("f(x)")
    """
    from manim import MathTex

    th = _theme()
    colors = colors or {}
    m = MathTex(tex, substrings_to_isolate=list(colors), tex_to_color_map=dict(colors),
                font_size=size or th.tex_size, color=kw.pop("color", th.text), **kw)
    m.part = lambda key, i=0: m.get_parts_by_tex(key)[i]
    return m


def Label(text: str, size: float | None = None, color=None, weight: str = "NORMAL", **kw):
    """Body-font text at a phone-legible size.

    Example:
        Label("slope = 2", color=C.accent).next_to(line, UP)
    """
    from manim import Text

    th = _theme()
    return Text(text, font=kw.pop("font", th.font), font_size=size or th.label_size, color=color or th.text,
                weight=weight, **kw)


def Title(text: str, size: float | None = None, color=None, **kw):
    """Display-font title placed inside the top safe margin.

    Example:
        m.play(FadeIn(Title("Fourier series")), at=T.title)
    """
    from manim import UP, Text

    th = _theme()
    t = Text(text, font=kw.pop("font", th.display_font), font_size=size or th.title_size, color=color or th.text,
             **kw)
    return t.to_edge(UP, buff=th.margin + 0.2)
