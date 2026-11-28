"""Semantic colors for video 014: each math object keeps ONE color for the whole video.

BASE is the Classic look (pure black, crisp unglowed lines, Computer Modern). No bloom, glow, blur, grain or vignette.
The only full-spectrum element is domain coloring, where hue *is* the data (the argument of the output).

    role        object (scenes from storyboard v2)
    prime       a prime: its tick, its sieve cell, a factor-tree leaf, each step of the staircase pi(x)
    smooth      the smooth curves that model the staircase: li(x) and Riemann's R(x)
    approx      Gauss's density 1/ln x and his first guess x / ln x (a dimmer cousin of smooth)
    gap         the error pi(x) - li(x): the band between staircase and curve; prime-free runs (s05)
    bound       the RH envelope sqrt(x) log x / 8 pi (dashed); the e^gamma line in Robin's plot (s27)
    zero        a nontrivial zero AND the wave it contributes (one object, two views); the Z wave (s15, s20)
    trivial     the trivial zeros -2, -4, -6, ... and the sine that makes them (s12)
    crit        the critical line Re(s) = 1/2 (strip fill uses it at low opacity)
    s_in        the input s, the probe point and the arrows n^-s
    zeta        zeta: its symbol, the spiral of partial sums, the output point, the partial-product paths (s19)
    rogue       a hypothetical off-line zero and its runaway wave (s13, s17, s20, s23); always labeled "what if"
    sieve2 / sieve3 / sieve5 / sieve7   each sieving prime's color: combs (s04), grid (s05), Euler product (s08)
    ffield      solutions of y^2 = x^3 + x + 1 in clock arithmetic (s22, s29); never on screen with sieve7
    lean        machine checking: Lean code, kernel ticks, the file wall (s01, s26, s28)
    ai          the AI system as an actor (the 2026 bar segment, attribution chips)
    human       human mathematicians as actors (attribution chips, the understanding rung)
    evidence / claimed / conj   status ladder rungs: numerical evidence, claimed proof (amber outline), conjecture
    ink         history cards: duotone portraits, the 1859 paper, small-caps names and dates

Typography (all Computer Modern): maths in CM roman, labels in CM sans, names and dates in small caps,
Lean code in CM typewriter.
"""
from aion import BASE

theme = BASE.extend(
    tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",
    prime="#ffd166",
    smooth="#4dd0e1",
    approx="#5b8fa3",
    gap="#fc6255",
    bound="#c8c8c8",
    zero="#ff4fa3",
    trivial="#8fa3b8",
    crit="#9be564",
    s_in="#6cb6ff",
    zeta="#b78cf2",
    rogue="#ff9f1c",
    sieve2="#f78c6b",
    sieve3="#83c167",
    sieve5="#58c4dd",
    sieve7="#c792ea",
    ffield="#cdb4db",
    lean="#5cd0b3",
    ai="#e8a87c",
    human="#f4efe0",
    evidence="#8fa3b8",
    claimed="#f2b544",
    conj="#a0a0a0",
    ink="#e8e4d8",
)
