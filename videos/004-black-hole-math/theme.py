"""Three design systems for this video. Pick one with `--design N` (or AION_DESIGN=N); default 1.

    uv run aion render 004 --design 2 --quality 4k --fps 30

Every design defines the same roles, so scenes never change: each math object keeps ONE colour
for the whole video, whichever design is active.

    role      object
    light     rays of light, u = 1/r
    mass      the mass M, the bending term 3GM/c² u²
    horizon   Schwarzschild radius r_s, the event horizon
    ring      photon sphere, 1.5 r_s
    shadow    edge of the shadow, 2.6 r_s
    newton    the thrown-ball (Newtonian) prediction
    disk      the accretion disk in diagrams
    grid      the space grid / funnel wireframe
    time_*    how fast clocks run on the spacetime map: fast (far) → mid → slow (near the horizon)
"""
import os

from aion import BASE

# shared by all designs: pure black, no grain or vignette (they lift the black), tight bloom
_COMMON = dict(bg="#000000", bg2="#000000", grain=0.0, vignette=0.0, bloom=0.05, margin=0.4)

DESIGNS = {
    # 1 · EMBER — warm and cinematic. Gold light on black, ember mass, soft violet horizon.
    1: BASE.extend(
        **_COMMON, name="Ember", tagline="warm · cinematic · film-like",
        font="Inter Variable", display_font="Inter Variable",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}",                 # Computer Modern
        stroke=3.0, thin=1.6, glow=0.55, glow_radius=2.0,
        text="#f4f1ea", muted="#9a958a", faint="#2e2b27",
        light="#ffc94a", mass="#ff5a1f", horizon="#a78bfa", ring="#22d3ee", shadow="#ffffff",
        newton="#8f98a3", disk="#f0a050", grid="#3d4a63", bad="#ff4d4d",
        time_fast="#22d3ee", time_mid="#8b5cf6", time_slow="#ff3d81",
        bh_T=4900.0, bh_beam=2.6, bh_shift=0.7, bh_gain=0.55),
    # 2 · NEON — crisp RGB primaries with a tight glow. Technical, high energy.
    2: BASE.extend(
        **_COMMON, name="Neon", tagline="crisp · saturated · technical",
        font="Ubuntu Sans", display_font="Ubuntu Sans",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{eulervm}",   # upright Euler math
        stroke=2.6, thin=1.4, glow=0.75, glow_radius=1.6,
        text="#ffffff", muted="#8a94a6", faint="#1f2937",
        light="#ffe600", mass="#ff2d55", horizon="#8b5cf6", ring="#00f5d4", shadow="#ffffff",
        newton="#94a3b8", disk="#ff8a00", grid="#2f3fa3", bad="#ff3b30",
        time_fast="#00f5d4", time_mid="#7c3aed", time_slow="#ff2d55",
        bh_T=6800.0, bh_beam=3.2, bh_shift=0.9, bh_gain=0.34),
    # 3 · OBSERVATORY — cool and editorial. Serif type, pale light, amber mass, deep blue horizon.
    3: BASE.extend(
        **_COMMON, name="Observatory", tagline="calm · editorial · scientific",
        font="Noto Serif", display_font="Noto Serif Display",
        tex_preamble=r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{newtxtext,newtxmath}",   # Times-like
        stroke=2.8, thin=1.5, glow=0.4, glow_radius=1.8,
        text="#eef2f7", muted="#8d99ab", faint="#263041",
        light="#fff3c4", mass="#ffa62b", horizon="#4d9fff", ring="#5eead4", shadow="#ffffff",
        newton="#7f8ea3", disk="#e8b46a", grid="#33415c", bad="#fb7185",
        time_fast="#5eead4", time_mid="#4d9fff", time_slow="#ff8a5c",
        bh_T=4200.0, bh_beam=2.2, bh_shift=0.6, bh_gain=0.7),
}

DESIGN = int(os.environ.get("AION_DESIGN", "1") or 1)
if DESIGN not in DESIGNS:
    raise SystemExit(f"--design {DESIGN}: this video defines designs {sorted(DESIGNS)}")
theme = DESIGNS[DESIGN]
