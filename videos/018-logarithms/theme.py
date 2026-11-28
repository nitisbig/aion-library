"""Semantic colors for video 018, "What Logarithms Actually Are". Each object keeps ONE color all video.

BASE is the Classic look: pure black, crisp unglowed lines, Computer Modern, the bright blue grid (C.grid over
C.grid_minor, white C.axis). Accent glow only on lit payoff graphics (the + in the intro, the ring behind 256, the
slide-rule cursor, light trails in the mirror, the edge of the area under 1/x, the point e). Text, grids and axes
never glow; no frame-wide bloom, grain or vignette.

The three roles of every logarithm keep their colours from the first staircase to the last scale:

    role      object
    base      the multiplier b, ×b on each riser, stretch / scale arrows (amber)
    steps     the count = the logarithm itself: step heights, exponents, log readouts, lengths on a ruler (periwinkle)
    value     the result y = bˣ: tread numbers, products, the exponential curve, markers on x (magenta)
    natural   e and ln, the natural-log curve, growth at rate r (mint)
    area      the region under 1/x and its strips: the natural hue as a translucent fill, because that area is ln x
    ruler     engraved scales, the slide rule, the piano keys, line drawings of objects (ivory)
    paper     Napier's printed page (warm parchment, raster only)
    cell      the dividing cells of c01 (lime membrane)
    sound     sound rings, the decibel marker (coral)
    star      the star field (cool white)
    quake     earthquake ripple and its ×31.6 tags (orange)
    acid      pH markers and glasses (lime)
    planet    Kepler's planets, orbit ellipses (gold; the slope triangle uses steps/value, never base)

Chapter hues (`ch_count` … `ch_world`) mark the progress rail, the chapter card rule and name tags only.

Typography (all Computer Modern via LaTeX): maths in CM roman, key words and tags in CM sans (\\textsf), names,
dates, chapter titles in CM small caps (\\textsc).
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}",
    # ---- the three roles of a logarithm (+ e and the area)
    base="#FFB23E",
    steps="#8FB4FF",
    value="#FF5FB8",
    natural="#6EF7B3",
    area="#6EF7B3",         # = natural: the area under 1/x IS ln x (drawn as a translucent fill)
    # ---- objects
    ruler="#F1E4C4",
    paper="#D9C9A3",
    cell="#8CF425",
    sound="#E8453C",
    star="#F2F6FF",
    quake="#FF7A3D",
    acid="#C9E83A",
    planet="#F4AF25",
    # ---- chapter hues (rail, card rule, name tags)
    ch_count="#8FB4FF",
    ch_add="#FF5FB8",
    ch_slide="#F1E4C4",
    ch_curve="#FFB23E",
    ch_e="#6EF7B3",
    ch_world="#B48CFF",
    # ---- accent glow (graphics only)
    glow=0.9,
    glow_r=5,
)

CHAPTERS = ("ch_count", "ch_add", "ch_slide", "ch_curve", "ch_e", "ch_world")
"""Chapter hues in story order (rail segments 1 … 6)."""

TEXT_ROLES = ("text", "muted", "base", "steps", "value", "natural", "quake", "acid", "planet") + CHAPTERS
GRAPHIC_ROLES = ("ruler", "cell", "sound", "star", "grid", "axis")

GROUPS = {
    "log roles": ("base", "steps", "value"),
    "c04 curves": ("steps", "natural", "value", "base"),
    "c05 area": ("natural", "steps", "base", "value"),
    "c01 cells": ("cell", "steps", "value"),
    "c03 ruler": ("ruler", "steps", "value", "base"),
    "c06 senses": ("sound", "star", "steps", "value"),
    "c06 earth": ("quake", "acid", "steps"),
    "c06 kepler": ("planet", "steps", "value"),
}
"""Colours that share a frame: each group is checked for colour-blind separation by scripts/export_tokens.py."""
