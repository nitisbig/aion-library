"""Semantic colors for video 017, "10 Equations That Run the Modern World". Each object keeps ONE color all video.

BASE is the Classic look: pure black, crisp unglowed lines, Computer Modern; the Classic grid (C.grid, C.grid_minor,
C.axis) is kept. Accent glow only on lit payoff elements (as approved for 015/016): a layer holding just that element
with Glow(color, strength=C.glow * k, radius=C.glow_r). Text, grids and axes never glow; no frame-wide bloom.

Chapter hues (`maxwell` … `bs`) are ten OKLCH hues at L 0.77, 36° apart, assigned so that chapters next to each other
in the story sit far apart on the wheel. A chapter hue marks that chapter's tile rule, card rule, its segment of the
progress rail and the equation's main symbol. Ten hues cannot all survive colour blindness, so every tile, card and the
rail also carry the chapter's name in words.

In-chapter roles are checked as GROUPS (the colours that share a frame) by scripts/export_tokens.py: CIEDE2000 >= 20
in normal vision and >= 10 under simulated deutan / protan / tritan.

    role       object
    e_field    electric field, E, its arrows and LIC texture, the E wave (gold, by convention)
    b_field    magnetic field, B, loops, the B wave (= the Maxwell hue)
    charge_p   positive charge (+), high pressure (ch 4)
    charge_n   negative charge (−) and low pressure (magenta: a blue would clash with b_field)
    light      a photon / light ray, star points, error crosses (cool white; glows)
    mass       the heavy sphere, the Sun's body, matter T_μν in ch 2 (neutral lead grey)
    data       data points to fit (ch 7), neutral samples (stars in ch 2 use light)
    noise      noise added to a signal, noise clouds (ch 8; violet static)
    ill        the ill group in the Bayes test (ch 9), = BASE bad hue family
    positive   a positive test result ring (ch 9)
    prior      belief before evidence (ch 9)
    payoff     option payoff / the value surface (ch 10)
    bad        errors, wrong bits, the market jump (BASE)

Typography (all Computer Modern via LaTeX): maths in CM roman, key words and tags in CM sans (\\textsf), names, dates,
chapter titles in CM small caps (\\textsc).
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}",
    # ---- chapter hues (tile, card, rail segment, hero symbol)
    maxwell="#02C5FF",
    einstein="#E3AA00",
    schrod="#B28AFF",
    navier="#14CEC9",
    fourier="#FE955C",
    dilation="#8FB3FD",
    descent="#37D385",
    shannon="#A7C32B",
    bayes="#FF8D9D",
    bs="#FE7FDD",
    # ---- in-chapter roles
    e_field="#FFC452",
    b_field="#02C5FF",
    charge_p="#FF5A4E",
    charge_n="#B751B5",
    light="#F2F6FF",
    mass="#8C9098",
    data="#D9DEE6",
    bad="#F94047",          # errors, the market jump (BASE bad, retuned to pass the ch 10 group)
    noise="#B77DF8",
    ill="#FF5A4E",
    positive="#FFD84A",
    prior="#7EB7E7",
    payoff="#FFC452",
    # ---- surfaces
    card="#0B0E13",          # lifted black for solid bodies on sims (the ch 4 cylinder)
    glow=0.9,                # accent glow strength (payoff elements only)
    glow_r=5,                # accent glow radius, px at 1080p
)

CHAPTERS = ("maxwell", "einstein", "schrod", "navier", "fourier", "dilation", "descent", "shannon", "bayes", "bs")
"""Chapter hues in story order (tile T1 … T10)."""

GROUPS = {
    "c01 maxwell": ("e_field", "b_field", "charge_p", "charge_n", "light"),
    "c02 einstein": ("einstein", "mass", "light"),
    "c03 schrodinger": ("schrod", "light", "e_field"),
    "c04 navier": ("navier", "charge_p", "charge_n", "light"),
    "c05 fourier": ("fourier", "data"),
    "c06 dilation": ("dilation", "light", "einstein"),
    "c07 hill": ("descent", "light"),
    "c07 fit": ("descent", "data"),           # the path on the error map is a descent/light mix, not light
    "c07 bridge": ("descent", "shannon", "noise", "light"),
    "c06 bridge": ("dilation", "descent", "light"),
    "c08 errors": ("shannon", "noise", "bad", "light"),
    "c08 receiver": ("shannon", "noise", "bayes", "light"),
    "c09 dots": ("ill", "positive", "muted"),
    "c09 belief": ("prior", "bayes", "light"),
    "c09 rule": ("positive", "prior", "bayes"),   # bayes never shares a frame with ill, nor with muted dots
    "c10 black-scholes": ("bs", "payoff", "bad", "light"),
}
"""Colours that share a frame: each group is checked for colour-blind separation by scripts/export_tokens.py."""
