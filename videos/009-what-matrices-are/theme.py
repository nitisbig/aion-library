"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis,
C.ghost, C.frame built in). No bloom, glow, blur, grain or vignette. This video adds one thing to Classic: 3D objects
(the die, the planes, the ellipsoid) are shaded by a single fixed key light so they read as solid.

    role      object
    ihat      i-hat, the first column, its entries (same green as 006, for the channel's linear algebra series)
    jhat      j-hat, the second column
    khat      k-hat, the third column (3D)
    vec       a vector x and where it lands
    target    the target b in Ax = b
    area      the unit square / cube and the determinant's value
    null      collapse: the null space, the shadow's light rays, a zero determinant
    eigen     eigenvectors, lambda, the PageRank steady state
    sigma     the singular axes, sigma, the ellipse / ellipsoid
    cls_a     spiral class one (s10 only)
    cls_b     spiral class two (s10 only)
    data      numbers being read as data: pixel values, table cells, plain matrices
    die       the hero die's body;  pip = its pips
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    ihat="#83c167",
    jhat="#fc6255",
    khat="#58c4dd",
    vec="#ffe94a",
    target="#ff8a6b",
    area="#f0ac5f",
    null="#ff4fa3",
    eigen="#b78cf2",
    sigma="#5cd0b3",
    cls_a="#6cb6ff",
    cls_b="#ffa26b",
    data="#d0d0d0",
    die="#f2efe8",
    pip="#151515",
)
