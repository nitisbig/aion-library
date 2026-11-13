"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis,
C.ghost, C.frame built in). No bloom, glow, blur, grain or vignette.

    role    object
    growth  e, money, the e^t curve, ordinary (real) growth
    turn    i, rotation arcs, quarter-turn marks
    arc     pi, theta, the distance walked along the circle
    point   the moving point e^{i theta}, its position arrow, and -1 where it lands
    vel     the velocity arrow
    cos     horizontal parts: real-axis series steps, cos projection, cosine wave
    sin     vertical parts: imaginary-axis series steps, sin projection, sine wave
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    growth="#f0ac5f",
    turn="#fc6255",
    arc="#83c167",
    point="#ffe94a",
    vel="#d147bd",
    cos="#5cd0b3",
    sin="#b78cf2",
)
