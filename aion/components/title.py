"""Title lockup in the design system's display face, rendered with skia.

    sweep = ValueTracker(0)
    title = TitlePlate("The Hessian Matrix", sweep=sweep).move_to(DOWN * 2)
    self.play(FadeIn(title, shift=UP * 0.1), sweep.animate.set_value(1), run_time=1.2)

Space Grotesk (from aion/assets/fonts, no system install needed), tracking +0.02em,
a soft glow under the glyphs, and a `light` sweep that crosses the word once as
`sweep` goes 0 → 1 (outside (0, 1) there is no sweep). Sizes are 1080p design px.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import skia
from manim import RESAMPLING_ALGORITHMS, ImageMobject, ValueTracker, color_to_rgb, config

from .. import style as S

FONT_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_WGHT = 0x77676874   # 'wght'


def _typeface(weight: int) -> skia.Typeface:
    base = skia.Typeface.MakeFromFile(str(FONT_DIR / S.FONT_DISPLAY))
    args = skia.FontArguments()
    coords = skia.FontArguments.VariationPosition.Coordinates([
        skia.FontArguments.VariationPosition.Coordinate(_WGHT, float(weight))])
    args.setVariationDesignPosition(skia.FontArguments.VariationPosition(coords))
    return base.makeClone(args)


def _c4(color, a: float = 1.0) -> int:
    r, g, b = (int(round(255 * c)) for c in color_to_rgb(color))
    return skia.ColorSetARGB(int(round(255 * a)), r, g, b)


class TitlePlate(ImageMobject):
    def __init__(self, text: str, *, size_px: float = 72, weight: int = 600,
                 color=S.TEXT, glow: float = 0.6, tracking: float = 0.02,
                 sweep: ValueTracker | None = None, **kw):
        self._args = (text, size_px, weight, color, glow, tracking)
        self._sweep = sweep
        self._k = config.pixel_height / 1080.0               # design px → output px
        img = self._draw(-1.0)
        super().__init__(img, **kw)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        h_units = img.shape[0] / config.pixel_height * config.frame_height
        self.stretch_to_fit_height(h_units)
        self.stretch_to_fit_width(h_units * img.shape[1] / img.shape[0])
        self._last = -1.0
        if sweep is not None:
            self.add_updater(lambda m: m._update())

    def _update(self):
        v = self._sweep.get_value()
        if v != self._last and (0.0 < v < 1.0 or 0.0 < self._last < 1.0):
            self.pixel_array = self._draw(v)
        self._last = v

    def _draw(self, sweep: float) -> np.ndarray:
        text, size_px, weight, color, glow, tracking = self._args
        k = self._k
        font = skia.Font(_typeface(weight), size_px * k)
        glyphs = font.textToGlyphs(text)
        widths = font.getWidths(glyphs)
        track = tracking * size_px * k
        xs = np.concatenate([[0.0], np.cumsum(np.array(widths) + track)[:-1]])
        width = float(xs[-1] + widths[-1])
        pad = 0.6 * size_px * k
        W, H = int(np.ceil(width + 2 * pad)), int(np.ceil(size_px * k * 1.35 + 2 * pad))
        base = pad + size_px * k * 1.0
        blob = skia.TextBlob.MakeFromPosTextH(text, [float(x + pad) for x in xs], 0.0, font) \
            if hasattr(skia.TextBlob, "MakeFromPosTextH") else None
        surf = skia.Surface(W, H)
        cv = surf.getCanvas()
        cv.clear(skia.ColorTRANSPARENT)

        def draw(paint):
            if blob is not None:
                cv.drawTextBlob(blob, 0, base, paint)
            else:
                for g, x in zip(text, xs):
                    cv.drawString(g, float(x + pad), base, font, paint)

        if glow > 0:
            p = skia.Paint(AntiAlias=True, Color=_c4(color, 0.55 * glow),
                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.22 * size_px * k))
            draw(p)
        p = skia.Paint(AntiAlias=True, Color=_c4(color))
        if 0.0 < sweep < 1.0:
            x = -0.3 * W + sweep * 1.6 * W
            band = 0.16 * W
            p.setShader(skia.GradientShader.MakeLinear(
                [skia.Point(x - band, 0), skia.Point(x + band, H * 0.4)],
                [_c4(color), _c4(S.LIGHT), _c4(color)], [0.0, 0.5, 1.0]))
        draw(p)
        arr = np.array(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType,
                                                        alphaType=skia.kUnpremul_AlphaType))
        return arr
