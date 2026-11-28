"""Semantic colors for video 016, "PCA Explained Visually". Each object keeps ONE color for the whole video.

BASE is the Classic look: pure black, crisp unglowed lines, Computer Modern. BASE neutrals and the Classic grid
(C.grid, C.grid_minor, C.axis) are kept as they are.

Accent glow (as approved for 015): only payoff moments glow, through a layer with a Glow fx in that element's
color at strength C.glow (the PC1 lock-in, the two eigenvectors, the digit map settling, the best shadow). Text,
grids, axes and backgrounds stay crisp; no frame-wide bloom, grain or vignette.

The seven core roles pass the color-blind check (CIEDE2000 >= 20 normal vision, >= 10 under simulated deutan /
protan / tritan; scripts/export_tokens.py). Eight would not: variance, covariance and eigenvalues therefore share
ONE role, `spread`, which is also the point (they are all spreads).

    role      object
    data      the data points (people, digit dots before they are labelled), shadow dots on a line
    mean      the average point μ, the centring rulers; the hypotenuse |x̃| in Pythagoras
    probe     the search line / the unit arrow u while it is still searching (a neutral off-white)
    pc1       the first principal component: its line, v1, z1, "kept" (gold; it glows at lock-in)
    pc2       the second principal component: its line, v2, z2
    pc3       the third component (3D pebble, the yield-curve bend)
    residual  what is thrown away: perpendicular gaps d, drop lines, reconstruction error, "lost",
              negative covariance products
    spread    variance, covariance, the matrix C and its ellipse, eigenvalues λ, scree bars
    d0..d9    the ten digit classes on the map (OKLCH hues; ALWAYS paired with a numeral label, since no set of
              ten hues survives color blindness)
    lamp      the warm lamp light of the shadow bookends (graphics only)
    wall      the wall the shadow falls on (graphics only; lit by the lamp, so it never shows at full value)
    floor     the floor of the shadow room (graphics only)
    glass1..3 the sculpture's three bunches of glass beads (graphics only; the wire through them is C.pc1 gold)

Typography (all Computer Modern via LaTeX): maths in CM roman, labels and key words in CM sans (\\textsf),
names, dates and chapter cards in CM small caps (\\textsc).
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}",
    data="#7EB7E7",
    mean="#F4EFE0",
    probe="#D9DEE6",
    pc1="#FFC452",
    pc2="#1FE0AB",
    pc3="#A77FFF",
    residual="#FF5DA7",
    spread="#FF4D00",
    d0="#ED737B", d1="#FFA158", d2="#C39900", d3="#A6CF5C", d4="#15BA81",
    d5="#00DAE0", d6="#00ACED", d7="#98B7FF", d8="#B683E8", d9="#FF95D9",
    lamp="#FFE2B0",
    wall="#A89F8E",          # the lit wall of the shadow bookends (graphics only)
    floor="#5E5247",         # the floor under it (graphics only)
    glass1="#3E8EFF", glass2="#FF4F7B", glass3="#27D3A0",   # the sculpture's three glass bead bunches (graphics only)
    card="#0B0E13",          # borderless boards (a lifted black; premium look, ch1 first)
    plane="#34424F",         # premium plane: major grid lines (neutral slate, so C.data points read clearly)
    plane_minor="#19212A",   # premium plane: minor grid lines
    plane_axis="#D5DCE4",    # premium plane: the two axes
    glow=0.9,                # accent glow strength (payoff elements only)
    glow_r=5,                # accent glow radius, px at 1080p
)

CORE = ("data", "mean", "pc1", "pc2", "pc3", "residual", "spread")
"""Roles that can share a frame: checked for color-blind separation by scripts/export_tokens.py."""

DIGITS = tuple(f"d{i}" for i in range(10))
