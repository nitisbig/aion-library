"""Three design systems for this video. Pick one with `--design N` (or AION_DESIGN=N); default 4 (Classic).

Every design defines the same roles, so scenes never change: each math object keeps ONE colour
for the whole video, whichever design is active.

    role      object
    ihat      first basis vector, the first column (a, c)
    jhat      second basis vector, the second column (b, d)
    khat      third basis vector (chapter 6 only)
    area      the unit square / parallelogram / box, and the determinant's value when positive
    flip      a flipped (negative-determinant) area, and the minus sign
    collapse  a zero determinant: the line or plane that space is squashed onto
    cutaway   the pieces removed from the bounding rectangle in chapter 3
    grid      the moving grid's integer lines;  grid_minor = its half-step lines;  axis = the two axes
    ghost     the original grid left behind for reference;  frame = thin panel borders
"""
import os

from aion import BASE

_COMMON = dict(stroke=4.0, thin=2.0, margin=0.45, lead=0.15)

DESIGNS = {
    # 1 · BLUEPRINT: deep navy, teal and rose arrows, gold area. Calm and technical.
    1: BASE.extend(
        **_COMMON, name="Blueprint", tagline="calm · technical · high contrast",
        font="Inter Variable", display_font="Inter Variable",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",                       # Computer Modern
        bg="#070b14", bg2="#111a2e", text="#eef2f8", muted="#8c97ab", faint="#253049",
        ihat="#2dd4bf", jhat="#ff6fae", khat="#5aa9ff",
        area="#ffd166", flip="#a78bfa", collapse="#ff5a4d", cutaway="#64748b",
        grid="#3b6fb3", grid_minor="#16233a", axis="#eef2f8", ghost="#1f2a40", frame="#3a4660",
        bloom=0.18, grain=0.012, vignette=0.22, glow=0.5, glow_radius=2.0),
    # 2 · CHALK: warm near-black, softer pastel arrows, upright Euler math. Friendly, hand-made.
    2: BASE.extend(
        **_COMMON, name="Chalk", tagline="warm · friendly · classroom",
        font="Inter Variable", display_font="Inter Variable",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{eulervm}",   # upright Euler math
        bg="#0f0e0c", bg2="#1b1916", text="#f5f0e6", muted="#a39c8d", faint="#33302a",
        ihat="#8fd694", jhat="#ff8a70", khat="#7cb8ff",
        area="#f7c948", flip="#c4a1ff", collapse="#ff4d6d", cutaway="#7a7468",
        grid="#5b7a8c", grid_minor="#25303a", axis="#f5f0e6", ghost="#2a2824", frame="#4a463f",
        bloom=0.12, grain=0.02, vignette=0.28, glow=0.35, glow_radius=1.8),
    # 3 · EDITORIAL: cool slate, serif type, Times-like math. Quiet and scientific.
    3: BASE.extend(
        **_COMMON, name="Editorial", tagline="quiet · scientific · serif",
        font="Noto Serif", display_font="Noto Serif Display",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{newtxtext,newtxmath}",
        bg="#0a0d12", bg2="#141a22", text="#eef2f7", muted="#8d99ab", faint="#263041",
        ihat="#5eead4", jhat="#fda4af", khat="#93c5fd",
        area="#fcd34d", flip="#c4b5fd", collapse="#fb7185", cutaway="#6b7686",
        grid="#48607f", grid_minor="#1a2230", axis="#eef2f7", ghost="#1c2431", frame="#3a4658",
        bloom=0.1, grain=0.01, vignette=0.2, glow=0.3, glow_radius=1.8),
    # 4 · CLASSIC: the reference look. Pure black, crisp unglowed lines, bright blue integer grid over a dim
    #     half-step grid, white axes, Computer Modern everywhere (text is set in LaTeX too).
    4: BASE.extend(
        name="Classic", tagline="crisp · black · Computer Modern",
        font="Inter Variable", display_font="Inter Variable",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
        stroke=4.0, thin=1.6, margin=0.45, lead=0.15, tex_size=48,
        bg="#000000", bg2="#161616", text="#ffffff", muted="#a6a6a6", faint="#3a3a3a",
        ihat="#83c167", jhat="#fc6255", khat="#58c4dd",
        area="#ffe94a", flip="#b78cf2", collapse="#ff4fa3", cutaway="#8a8a8a",
        grid="#1fa2dc", grid_minor="#0f3e4d", axis="#ffffff", ghost="#2b2b2b", frame="#bdbdbd",
        bloom=0.0, grain=0.0, vignette=0.0, glow=0.0, glow_radius=0.0),
}

DESIGN = int(os.environ.get("AION_DESIGN", "4") or 4)
if DESIGN not in DESIGNS:
    raise SystemExit(f"--design {DESIGN}: this video defines designs {sorted(DESIGNS)}")
theme = DESIGNS[DESIGN]
