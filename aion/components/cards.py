"""Rounded "card" panels rendered with skia (gradient fill, hairline border, soft edge glow).

    card = card_image(width=4.0, height=3.0)      # ImageMobject, Manim units
    card.set_opacity(0.3)                          # placeholder; animate to 1.0 to light it
"""

from __future__ import annotations

import numpy as np
import skia
from manim import ImageMobject, color_to_rgb

from .glow import _unpremultiply


def _rgba(hex_color: str, a: float = 1.0) -> int:
    r, g, b = (int(round(255 * c)) for c in color_to_rgb(hex_color))
    return skia.Color(r, g, b, int(255 * a))


def card_image(
    width: float, height: float, *,
    radius: float = 0.22, top: str = "#16191F", bottom: str = "#0A0B0E",
    border: str = "#3A4150", glow: str = "#3A4150", ppu: float = 160.0,
) -> ImageMobject:
    pad = 0.25
    W, H = int((width + 2 * pad) * ppu), int((height + 2 * pad) * ppu)
    surface = skia.Surface(W, H)
    c = surface.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    rect = skia.RRect.MakeRectXY(
        skia.Rect.MakeXYWH(pad * ppu, pad * ppu, width * ppu, height * ppu),
        radius * ppu, radius * ppu)

    c.drawRRect(rect, skia.Paint(AntiAlias=True, Color=_rgba(glow, 0.55),
                                 MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.07 * ppu)))
    shader = skia.GradientShader.MakeLinear(
        [skia.Point(0, pad * ppu), skia.Point(0, (pad + height) * ppu)],
        [_rgba(top), _rgba(bottom)])
    c.drawRRect(rect, skia.Paint(AntiAlias=True, Shader=shader))
    c.drawRRect(rect, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                 StrokeWidth=0.012 * ppu, Color=_rgba(border)))

    rgba = _unpremultiply(surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType))
    img = ImageMobject(rgba)
    img.stretch_to_fit_width(width + 2 * pad)
    img.stretch_to_fit_height(height + 2 * pad)
    return img
