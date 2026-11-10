"""Apply a Theme to Manim's global defaults (fonts, TeX preamble, stroke, colors)."""

from __future__ import annotations

from aion.theme.tokens import Theme

__all__ = ["apply", "register_fonts"]

_FONTS_DONE = False


def register_fonts() -> None:
    """Make bundled fonts (aion/assets/fonts) visible to Manim's Text."""
    global _FONTS_DONE
    if _FONTS_DONE:
        return
    import manimpango

    from aion._env import ASSETS

    for f in sorted((ASSETS / "fonts").glob("*.[ot]tf")):
        manimpango.register_font(str(f))
    _FONTS_DONE = True


def apply(theme: Theme) -> None:
    from manim import MathTex, Tex, TexTemplate, Text, VMobject, config

    register_fonts()
    tpl = TexTemplate()
    tpl.add_to_preamble(theme.tex_preamble)
    config.tex_template = tpl
    config.background_color = theme.bg
    Text.set_default(font=theme.font, color=theme.text, font_size=theme.body_size)
    MathTex.set_default(color=theme.text, font_size=theme.tex_size)
    Tex.set_default(color=theme.text, font_size=theme.tex_size)
    VMobject.set_default(stroke_width=theme.stroke)
