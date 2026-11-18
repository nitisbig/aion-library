"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern; C.grid, C.grid_minor, C.axis,
C.ghost, C.frame built in). No bloom, glow, blur, grain or vignette. Colors shared with 009/010 keep their values,
so the channel's linear-algebra series reads as one family. Full design sheet: design.md.

    role      object
    gen       the generator A: its symbol, its entries, the velocity arrows A v of its field (= 010's op)
    flow      the result e^{tA}: its symbol, its entries, flow trails, the "where it lands" ghosts (= 010's dfn)
    vec       a state vector v / x, the particles, the moving point, pill molecules, the "you" dot on Earth (= 009's vec)
    ihat      i-hat and the first column (= 009)
    jhat      j-hat and the second column (= 009)
    eigen     eigenvectors, eigenvalues lambda, the 3D rotation axis (= 009)
    area      the tracked patch, its area, det and trace (= 009)
    gen_b     the second generator B (ch5 only)
    comm      the commutator AB - BA and the loop's leftover gap (ch5, = 010's null pink)
    wrong     the element-wise guess and the plane it crushes (intro, ch3, ch4)
    data      plain numbers being read: compounding values, term sizes, dates
    globe     the Earth's particle shell and graticule (ch6);  land = its continent dots
    The intro's line art (rooms, circuit, building, satellite, ...) is drawn in C.frame; any exponential curve
    it shows is `flow` (it is e^{kt}, a result), and anything that moves is `vec`.

    Prologue worlds (intro only; each world's icon, curve, dots and law share its hue, and all four curves turn
    `flow` when they merge into one equation):
    heat / warm / cool   the coffee: hot → warm → room temperature (a 3-stop ramp; `cool` is also the room line)
    money                compound interest (coins, its curve)
    life                 bacteria (cells, its curve)
    decay                radioactive rock (atoms, its curve)
    dose                 the pill's stomach amount s (the blood amount b is `flow`)

Typography (all Computer Modern, so maths and words share one family): maths in CM roman (`tex`), labels and
units in CM sans (`lab`), names and dates in small caps (`sc`), key words in bold (`key`).
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    gen="#ff8a6b",
    flow="#5cd0b3",
    vec="#ffe94a",
    ihat="#83c167",
    jhat="#fc6255",
    eigen="#b78cf2",
    area="#f0ac5f",
    gen_b="#6cb6ff",
    comm="#ff4fa3",
    wrong="#8f8f8f",
    data="#d0d0d0",
    globe="#5f7f94",
    land="#e8e4d8",
    heat="#ff3d3d",
    warm="#ffb347",
    cool="#4da3ff",
    money="#e9c46a",
    life="#9be564",
    decay="#9d8cff",
    dose="#ffb347",
)
