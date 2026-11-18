"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis,
C.ghost, C.frame built in). No bloom, glow, blur, grain or vignette. Colors shared with 009 keep 009's values, so the
channel's linear-algebra series reads as one family.

    role      object
    fn        the input function f: its graph, samples, arrow (= 009's vec)
    dfn       the output D f: derivatives
    op        the operator D: its matrix entries, "D" itself, the band
    b1        first basis function (1, cos, e^x cos x) and its axis (= 009's ihat)
    b2        second basis function (x, sin, e^x sin x) and its axis (= 009's jhat)
    null      the null space: constants, +C, collapse (= 009)
    eigen     eigenfunctions e^(lambda x), lambda, string modes (= 009)
    string    the guitar string's body
    shift     the shift h (ch7)
    data      plain numbers being read: sample values, coefficients
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    fn="#ffe94a",
    dfn="#5cd0b3",
    op="#ff8a6b",
    b1="#83c167",
    b2="#fc6255",
    null="#ff4fa3",
    eigen="#b78cf2",
    string="#f2efe8",
    shift="#f0ac5f",
    data="#d0d0d0",
)
