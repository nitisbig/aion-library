"""Soft glow halos for Manim vector mobjects, rendered with skia.

    glyph = MathTex("i", font_size=200, color=S.I_UNIT)
    halo = glow_halo(glyph, S.I_UNIT)      # ImageMobject aligned to the glyph
    self.add(halo, glyph)                  # halo behind, crisp glyph on top

The halo is the mobject's own outline (its Bezier paths) rasterized and blurred
with two Gaussian layers: a tight bright core and a wide soft bloom. Moving or
scaling the halo together with the glyph keeps them aligned (group them).
"""

from __future__ import annotations

import numpy as np
import skia
from manim import ImageMobject, VMobject, color_to_rgb


def _skia_path(mob: VMobject, origin: np.ndarray, ppu: float, h_px: int) -> skia.Path:
    path = skia.Path()
    path.setFillType(skia.PathFillType.kWinding)

    def px(p):
        return ((p[0] - origin[0]) * ppu, h_px - (p[1] - origin[1]) * ppu)

    for sub in mob.family_members_with_points():
        for sp in sub.get_subpaths():
            if len(sp) < 4:
                continue
            path.moveTo(*px(sp[0]))
            for k in range(0, len(sp) - 3, 4):
                _, h1, h2, a1 = sp[k:k + 4]
                path.cubicTo(*px(h1), *px(h2), *px(a1))
            path.close()
    return path


def glow_halo(
    mob: VMobject,
    color,
    *,
    core_sigma: float = 0.06,
    bloom_sigma: float = 0.28,
    core_alpha: float = 0.85,
    bloom_alpha: float = 0.55,
    ppu: float = 160.0,
) -> ImageMobject:
    """Blurred halo matching `mob`'s shape. Sigmas are in Manim units."""
    pad = 3.2 * max(core_sigma, bloom_sigma)
    lo = mob.get_corner(np.array([-1, -1, 0])) - pad
    hi = mob.get_corner(np.array([1, 1, 0])) + pad
    w_px = int(np.ceil((hi[0] - lo[0]) * ppu))
    h_px = int(np.ceil((hi[1] - lo[1]) * ppu))

    surface = skia.Surface(w_px, h_px)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorTRANSPARENT)
    path = _skia_path(mob, lo, ppu, h_px)
    r, g, b = (int(round(255 * c)) for c in color_to_rgb(color))

    for sigma, alpha in ((bloom_sigma, bloom_alpha), (core_sigma, core_alpha)):
        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(r, g, b, int(255 * alpha)),
            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma * ppu),
            BlendMode=skia.BlendMode.kPlus,
        )
        canvas.drawPath(path, paint)

    rgba = surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    rgba = _unpremultiply(rgba)
    img = ImageMobject(rgba)
    img.stretch_to_fit_width(w_px / ppu)
    img.stretch_to_fit_height(h_px / ppu)
    img.move_to((lo + hi) / 2)
    return img


def _unpremultiply(rgba: np.ndarray) -> np.ndarray:
    out = rgba.astype(np.float32)
    a = out[..., 3:4] / 255.0
    out[..., :3] = np.where(a > 0, out[..., :3] / np.maximum(a, 1e-6), 0)
    return np.clip(out, 0, 255).astype(np.uint8)
