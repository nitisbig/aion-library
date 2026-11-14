"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis,
C.ghost, C.frame built in). No bloom, glow, blur, grain or vignette.

    role      object
    field     the vector field's arrows and streak texture (light cyan; field scenes dim the grid to grid_minor)
    dust      the dust grains carried by the flow
    div       positive divergence: sources, outflow, the warm end of the divergence map, del-dot
    sink      negative divergence: sinks, inflow, the cool end of the divergence map
    curl      counter-clockwise spin: paddle wheel turning +, curl > 0, del-cross
    cw        clockwise spin: curl < 0 (the river)
    xpart     P, the horizontal part, d/dx terms
    ypart     Q, the vertical part, d/dy terms
    boundary  the tiny square's edge, a region's boundary, the wire loop in Stokes
    efield    the electric field E (Ch5)
    bfield    the magnetic field B (Ch5)
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    field="#9fdcf0",
    dust="#ffffff",
    div="#f0ac5f",
    sink="#5c9dff",
    curl="#83c167",
    cw="#d147bd",
    xpart="#5cd0b3",
    ypart="#b78cf2",
    boundary="#ffe94a",
    efield="#ff8a6b",
    bfield="#8f9bff",
)
