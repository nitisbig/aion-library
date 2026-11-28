"""Semantic colors for video 015, "Fundamentals of Math: The Big Picture". Each object keeps ONE color all video.

BASE is the Classic look: pure black, crisp unglowed lines, Computer Modern. No bloom, glow, blur, grain or
vignette. BASE neutrals and the Classic grid (C.grid, C.grid_minor, C.axis) are kept as they are.

The six pillar hues come from the hue tokens of the "Aion YouTube Design System First" (DS), so a pillar reads the
same here as in the channel's other videos. The DS hues as given fail the color-blind check (blue/violet and
teal/pink merge under deuteranopia), and no set of six DS hues passes, so each pillar keeps its DS hue family with
the smallest lightness/chroma/hue change that passes (at most 4.1 ΔE2000 from the DS value). The pillars also differ
by ring position and by key glyph, so color is never the only cue. `scripts/export_tokens.py` checks contrast and
color-blind separation and writes `design/tokens.json`; `design/design_sheet.md` holds the rules.

    role         DS token     object
    foundations  hue-blue     sets, logic, the symbol ∈, the inside-set tint (Ch1)
    quantity     hue-gold     numbers: π as a quantity, 22/7, 355/113, √2, the locked π estimate (Ch2)
    structure    hue-violet   symmetry and algebra: rotations e^{iθ}, the group C6, quaternions (Ch3)
    space        hue-teal     shape and topology: χ = V − E + F, the torus, the (θ, x) rectangle (Ch4)
    change       hue-orange   calculus: d/dr, the rings and their unrolled strips, the sine arch (Ch5)
    uncertainty  hue-pink     chance: P, the needles, estimates converging (Ch6)
    circle       (warm white) THE recurring circle: needle-tip trace, x² + y² = 25, the unit circle, the hub
    map_off      (dim slate)  unlit map nodes, the ring track, unlit chords, the floorboard cracks; graphics only
    alert        hue-red      the one contradiction of the video (Ch2, p/q parity clash); used once

Accent glow (approved for 015, 2026-11-23): only lit elements and payoff moments glow, through `kit.glow_layer`
(a layer with a Glow fx in that element's color, strength C.glow). Text, grids, axes, backgrounds and unlit map
parts stay crisp; no frame-wide bloom, grain or vignette.

Typography (all Computer Modern via LaTeX): maths in CM roman, labels and key words in CM sans (\\textsf),
names, dates and chapter cards in CM small caps (\\textsc).
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    foundations="#7EB7E7",   # DS hue-blue   #5FB6FF, ΔE00 4.0
    quantity="#FFDC84",      # DS hue-gold   #FFD17E, ΔE00 4.0
    structure="#A77FFF",     # DS hue-violet #B58CFF, ΔE00 4.1
    space="#1FE0AB",         # DS hue-teal   #36D6B0, ΔE00 4.0
    change="#FF9A3B",        # DS hue-orange #FF9F3D, ΔE00 1.7
    uncertainty="#FF5DA7",   # DS hue-pink   #FF6FA8, ΔE00 3.4
    circle="#F4EFE0",
    map_off="#5A606B",
    alert="#FF5A4E",         # DS hue-red, unchanged
    glow=0.9,                # accent glow: strength of the halo on lit elements only (kit.glow_layer)
    glow_r=5,                # accent glow radius, px at 1080p
)

NAMES = {
    "foundations": "Foundations",
    "quantity": "Quantity",
    "structure": "Structure",
    "space": "Space",
    "change": "Change",
    "uncertainty": "Uncertainty",
}

PILLARS = ("foundations", "quantity", "structure", "space", "change", "uncertainty")
"""Ring order: Foundations at the bottom (6 o'clock), then clockwise. Index k sits at angle -90° - 60°·k."""

GLYPHS = {
    "foundations": r"\in",
    "quantity": r"\pi",
    "structure": r"e^{i\theta}",
    "space": r"\chi",
    "change": r"\tfrac{d}{dr}",
    "uncertainty": r"P",
}
"""Each map node's key glyph (CM roman, drawn in the pillar's color once the node is lit)."""
