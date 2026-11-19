"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis, C.frame
built in). No bloom, glow, blur, grain or vignette. Colors shared with 009/011 keep their values, so the linear-algebra
series reads as one family. Full design sheet: design.md.

    role     object
    fwd      the move A: its symbol, entries, the threads walked outward (= 011's generator)
    back     the way back A^-1: its symbol, entries, the threads walked home (= 011's result)
    home     the identity I and everything that has returned to where it began
    key      the hero key
    vec      a probe point x, a target b
    ihat     i-hat and the first column (= 009)
    jhat     j-hat and the second column (= 009)
    det      the determinant, the area patch, 1/det
    null     the crushed direction, the light rays, whatever gets forgotten (= 009/010's null)
    shadow   the collapsed line and the shadows the key casts
    cam      a second observer's grid: the drone, the game camera
    wrong    a dead end: the flip-every-number rule, the wrong-order rewind (gray, never red)
    data     plain numbers being read: grams, angle counts
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    fwd="#ff8a6b",
    back="#5cd0b3",
    home="#f4efe0",
    key="#f2b544",
    vec="#ffe94a",
    ihat="#83c167",
    jhat="#fc6255",
    det="#b78cf2",
    null="#ff4fa3",
    shadow="#8fa3b8",
    cam="#6cb6ff",
    wrong="#8f8f8f",
    data="#d0d0d0",
)
