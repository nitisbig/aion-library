# Human cell → DNA: 45 s hobby piece (exploration)

One continuous "powers of ten" dive. A glowing human cell, a tour of its organelles, through a nuclear pore,
chromatin fibres, a nucleosome that unwraps, a B-DNA helix that unzips, then a rewind back out to the cell.
Black background, no text, look A (bioluminescent). The plan is in `storyboard.md`.

```bash
uv run python lab/2026-11-04-human-cell-dna/dna.py        # asserts + numbers
uv run python lab/2026-11-04-human-cell-dna/anatomy.py
uv run python lab/2026-11-04-human-cell-dna/render.py still --t 3 8.5 15.5 24.8 28.5 37.5     # → out/contact.png
uv run python lab/2026-11-04-human-cell-dna/render.py video --height 480 --fps 30             # preview (≈30 min)
uv run python lab/2026-11-04-human-cell-dna/render.py video --height 1080 --fps 60            # final (not run yet)
```
Output: `out/cell_dna_480p30.mp4`. Renders are resumable (150-frame segments keyed by a hash of the code).

## Pipeline
| File | Role |
|---|---|
| `dna.py` | B-DNA (10.5 bp/turn, 0.338 nm rise, P radius 0.89 nm, 144° strand offset → minor/major grooves), nucleosome superhelix (147 bp, 1.65 **left-handed** turns, R 4.18 nm, pitch 2.39 nm), histone octamer, 34 seeded 10-nm fibres with 104 nucleosomes each, and the hero DNA's **unwrap**: the turning between consecutive base-pair frames is re-integrated with reduced curvature, so the DNA peels off and the remaining wrap (and its histones) moves rigidly. HBB coding sequence asserted by translating it to β-globin |
| `anatomy.py` | Cell 20 µm, nucleus 7 µm, ~2000 nuclear pores on an integer-hash lattice (mirrored exactly in GLSL so the camera can fly through a known pore), 14 mitochondria, 26 vesicles/lysosomes, Golgi, centrosome + 22 microtubules. Rejection-sampled with no overlaps, sizes asserted |
| `timeline.py` | Two worlds with PCHIP camera keys: cell (µm) and molecular (nm, directions keyed in the straightened DNA's basis; the nucleosome shots are keyed to its superhelix axis). Camera targets are blended sources (fibre, histone, peel point, glide, fork) |
| `shaders/cell.frag` | Raymarched cell: every membrane is a thin emissive gaussian shell in its SDF, so grazing rays glow (fresnel/x-ray look). Pore complexes with 8-fold rings and transport channels, ER sheets with ribosomes, Golgi cisternae, mitochondria with inner membrane + cristae, chromatin as two-noise-zero-crossing threads, absorbing nucleoplasm. **Tiled into 128 px draws**: one full-screen draw trips the R4's GPU watchdog ("context lost") |
| `shaders/sphere.*` | ~350k static sphere impostors (fibres, histones, crowding proteins) + ~10k per-frame hero spheres (phosphates, sugar ribbon, 8-sphere bases, H-bonds), true sphere depth, log depth buffer, near-lens dither dissolve |
| `shaders/dof.frag`, `composite.frag` | Scatter-as-gather DOF per world, world cross-mix, Kawase bloom, zoom blur, chromatic aberration, flash, ACES, split-tone grade, vignette, grain |

## The numbers
| | |
|---|---|
| Hero DNA | 296 bp of HBB (from the ATG), wrap at bp 88–234, contour 92.5 nm |
| Grooves (axial) | minor 1.42 nm / major 2.13 nm |
| Wrap rise | 0.298 nm/bp: 147 bp on 1.65 turns of radius 4.18 nm is shorter than 147 × 0.338 nm. The real particle resolves this with DNA bending and stretching; here the wrap is just evenly compressed (≈12%) |
| Hydrogen bonds | A–T 2, G–C 3, flashing as they break when the fork passes |
| Render cost (480p) | cell world 0.7–3.3 s/frame (close shots are the slowest), molecular world ~0.2 s/frame |

## What worked
- **Emissive SDF shells** give translucent biology for free: rims glow, organelles read through the membrane, no lighting model needed.
- **Mirroring the pore lattice in Python and GLSL** (integer hashes only) lets the camera aim at and pass through one specific pore.
- **Re-integrating the frame rotations for the unwrap.** It's continuous, keeps the base-pair twist, and moves the histone core rigidly with the remaining wrap. A plain lerp between curved and straight would have collapsed the helix.
- **The molecular world is cheap** (0.2 s/frame) even with 350k spheres, and it looks the most "finished".

## What didn't (and the fixes)
- First stills were blown out white: the emission budget was about 10× too high. Rebalanced per component.
- A purple wash and a dense dot lattice covered the pore dive. That was the **far side** of the nuclear envelope showing through a transparent nucleus. Fixed with nucleoplasm absorption (real chromatin is dense).
- The teal fill in close cell shots came from the **cell membrane seen face-on**. A thinner, dimmer shell keeps the rim and darkens the face.
- The unwrap at front = 0 straightened the incoming linker: the hero nucleosome sat 36 nm from where the camera aimed. Now asserted: `unwrap(0)` reproduces the wrap exactly.
- Histone spheres poked through the DNA. They're now clamped inside the 3.18 nm DNA inner surface.
- Inside the nucleus (17–18.5 s) the chromatin reads as mottled pink noise rather than distinct threads. That's acceptable because the zoom blur and hand-off cover it, but it's the weakest moment.

## Not done yet
- Looks B/C from the storyboard (only A was built).
- Motion blur (sub-frame accumulation) and 2× SSAA for the final.
- Microvilli on the membrane (dropped).
