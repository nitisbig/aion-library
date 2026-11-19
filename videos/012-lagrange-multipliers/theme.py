"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern). No bloom, glow, blur, grain or vignette.

    role      object
    obj       the objective f: its symbol, its contours, its gradient arrow, the hill's height ramp
    con       the constraint g: its symbol, the trail, the rope, its gradient arrow
    con2      the second constraint h and its gradient (ch6 only)
    lam       the multiplier lambda, wherever it appears, including the stick on the beach
    mu        the second multiplier mu (ch6 only)
    you       the walker: the moving point and the candidate points
    tang      the shared tangent line and the along-the-trail part of the gradient
    lag       the Lagrangian L and its saddle surface
    wrong     what fails: the unreachable summit marker, the cusp
    area      enclosed land and its area values
    energy    Boltzmann's energy levels, the gas molecules, beta's curve

    Prologue worlds (intro only):
    sea / sand / dusk / night / ember   Dido's coast
    ink                 the parchment line art for the history beats

Typography (all Computer Modern): maths in CM roman, labels and units in CM sans, names and dates in small caps.
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    obj="#ffb347",
    con="#4dd0e1",
    con2="#83c167",
    lam="#ff4fa3",
    mu="#b78cf2",
    you="#ffe94a",
    tang="#9be564",
    lag="#6cb6ff",
    wrong="#fc6255",
    area="#e9c46a",
    energy="#ff7a59",
    sea="#1f6f8b",
    sand="#d9b779",
    dusk="#e8743b",
    ink="#e8e4d8",
    night="#121a30",
    ember="#ffc27a",
    gold="#f2c14e",
    rose="#d9486e",
    plum="#4a1f5c",
    indigo="#141a46",
    tyrian="#8c1d5e",
    walnut="#2b1620",
    foam="#ffe9c9",
)
