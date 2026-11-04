# Human cell → DNA: 45 s hobby scene (exploration)

One unbroken "powers of ten" dive: a living human cell floats out of the black, the camera tours its
organelles, slips through a nuclear pore, follows chromatin down to nucleosomes, and lands on a
B-DNA double helix that unzips into its base pairs. Then a fast pull-back to the whole cell and out to black.

Black background. **No text at all.** Motion-graphics grade: depth of field and rack focus, bloom,
light wrap, chromatic aberration at the frame edges, film grain, vignette, motion blur on fast moves.
Every cut is hidden inside a continuous zoom.

**Real anatomy and scale.** The shapes are stylized; the proportions, counts and geometry are not.

| Thing | Real value used | Source of truth |
|---|---|---|
| Cell | ~20 µm, irregular, with microvilli on one side | `anatomy.py` |
| Nucleus | ~7 µm, double envelope, ~2 000 nuclear pores (~120 nm), 1–2 nucleoli | " |
| Rough ER | sheets continuous with the outer nuclear envelope, ribosome-studded (~25 nm) | " |
| Golgi | 5–7 curved cisternae with budding vesicles | " |
| Mitochondria | 0.5 × 1–3 µm, outer membrane + inner membrane folded into cristae | " |
| Others | lysosomes, vesicles, centrosome with radiating microtubules (25 nm), actin cortex | " |
| Chromatin | interphase chromatin territories, not X chromosomes (those exist only in mitosis); the 10-nm "beads on a string" fibre (the 30-nm fibre is mostly absent in vivo) | " |
| Nucleosome | 147 bp in 1.65 **left-handed** superhelical turns around a histone octamer (~10 nm × 6 nm), linker DNA 20–60 bp | `dna.py` |
| B-DNA | right-handed, 2.0 nm diameter, 10.5 bp/turn, 0.34 nm rise, 34.3° twist, antiparallel strands, major (2.2 nm) / minor (1.2 nm) grooves | `dna.py` |
| Base pairs | A–T with 2 hydrogen bonds, G–C with 3. The sequence is the real start of the human **HBB** (β-globin) coding sequence | `dna.py` (asserted) |

Zoom range: 20 µm → 1 nm, about 4.3 decades. The camera lives in log-scale space (as in the supernova lab),
so float precision holds across the dive.

---

## 1. Engine choice

| Need | Tool | Why |
|---|---|---|
| Cell body and organelles: translucent membranes, cristae, ER sheets, cytoplasm haze | **moderngl**: raymarched SDFs + volumetric scattering | Soft translucent biology needs per-pixel light (fresnel rim, subsurface glow, absorption). Runs on the Radeon R4 |
| Chromatin, nucleosomes, DNA atoms, ribosomes, cytoplasm particles | **moderngl**: instanced sphere/capsule impostors (rasterized, depth-correct) | Tens of thousands of molecular primitives per frame cheaply. Exact geometry from numpy |
| Geometry: helix coordinates, nucleosome superhelix, chromatin random walk, organelle placement | **numpy / scipy** | Real math, seeded RNG, deterministic |
| Post: DOF, bloom, light wrap, chromatic aberration, ACES, grade, grain, vignette | **moderngl** post passes | Reuses the black-hole / neural-network lab composite |
| Motion blur on the fast dives | **moderngl** sub-frame accumulation (finals only) | The "AE" look on whip moves |
| Encode | **ffmpeg** + **tqdm** ETA bar | Resumable segments, as in the other labs |

Not used: **Manim** (no text or equations; its CPU renderer would crawl), **skia** (no 2D overlays or typography),
**pyvista** (offline 3D meshes are slower and less stylable than our own shaders here).

Scale hand-offs (cell SDF ↔ molecular instances) happen inside DOF blur + bloom while the camera is moving fast,
so the viewer sees one continuous zoom.

---

## 2. Storyboard (45.0 s @ 60 fps = 2 700 frames)

| # | Time | What the viewer sees | Camera | Scale |
|---|---|---|---|---|
| 1 | 0.0–4.0 | Black. Faint drifting particles in shallow focus. A rack focus pulls a soft glowing **cell** out of the dark, membrane rim lighting up first | Locked, slow push-in | 40 µm field |
| 2 | 4.0–13.0 | Orbit around the translucent cell. Organelles become visible through the membrane one by one: **nucleus** (pores glinting), **rough ER** folding around it, **Golgi** stack, **mitochondria** with cristae, lysosomes, vesicles, the **centrosome** with microtubules radiating. Organelles breathe and vesicles drift (subtle secondary motion) | Slow 120° orbit, slight tilt. Hero pass near a mitochondrion at ~10 s (cut-away shows the cristae) | 25 µm → 8 µm |
| 3 | 13.0–18.0 | The camera dives through the membrane and the cytoplasm (ribosomes, microtubules streak past with motion blur) toward the nucleus. The **nuclear envelope** fills the frame; one **nuclear pore** grows into a ring and we pass through it | Accelerating dolly, whip into the pore | 8 µm → 150 nm |
| 4 | 18.0–24.0 | Inside: glowing **chromatin territories**. Bloom softens, then the threads resolve into the **10-nm fibre**: nucleosome beads on a string | Glide along one fibre, slow S-curve | 2 µm → 60 nm |
| 5 | 24.0–30.0 | One **nucleosome** fills the frame: DNA wraps 1.65 turns around the histone octamer, histone tails flicker. The DNA **unwraps** off the core, uncoiling into a straight helix | Orbit the nucleosome, then follow the unwrapping DNA | 30 nm → 12 nm |
| 6 | 30.0–39.0 | Hero **B-DNA double helix**: sugar-phosphate backbones, colored base pairs, major/minor grooves. The camera glides along the axis. Then the helix **unzips**: the two strands part, base pairs separate and their hydrogen bonds (2 for A–T, 3 for G–C) light up as they break | Low glide along the axis, then a slow lateral move across the unzipping fork | 12 nm → 2 nm |
| 7 | 39.0–45.0 | Hold on the fork for a beat, then a fast **reverse powers-of-ten** pull-back: helix → nucleosome → fibre → nucleus → the whole cell, small and glowing in the black. Fade to black | Exponential pull-back with motion blur, ease into a hold | 2 nm → 60 µm |

Colour stays semantic for the whole piece: each organelle type, the DNA backbone, and each base (A, T, G, C) keep one colour.

---

## 3. Look options (built as stills side by side before the full render)

| Look | Feel |
|---|---|
| **A: Bioluminescent** | Cyan/teal membranes, magenta-violet nucleus, warm amber mitochondria, strong bloom, deep-sea feel |
| **B: Cinematic medical** | Warm subsurface skin tones, crimson/peach organelles, soft key light, DNA in gold and ice-blue. "Pharma ad" grade |
| **C: Holographic glass** | Desaturated glass membranes with fresnel edges, monochrome cyan + one accent per scale, crisp, little bloom |

---

## 4. Files (planned)

| File | Role |
|---|---|
| `anatomy.py` | Organelle layout and sizes (seeded), asserted against the real ranges above |
| `dna.py` | B-DNA atom/bead coordinates, nucleosome superhelix, chromatin fibre walk, HBB sequence, unzip state. Asserted (10.5 bp/turn, 0.34 nm rise, left-handed 1.65 turns, 147 bp) |
| `timeline.py` | Camera path in log-scale space, all events as functions of t |
| `shaders/cell.frag` | Raymarched cell + organelles + cytoplasm volume |
| `shaders/impostor.*` | Instanced sphere/capsule impostors for molecules |
| `shaders/composite.frag` | DOF, bloom, light wrap, CA, ACES, grade, grain, vignette |
| `render.py` | `still`, `looks`, `video` subcommands, tqdm ETA, resumable ffmpeg segments |

## 5. Render plan

1. Still frames at the 7 key beats in all 3 looks (480p) → pick a look.
2. 480p30 preview of the whole 45 s.
3. 1080p60 final in the background with 4 sub-frames of motion blur on the fast shots. The budget is ≤1.5 s/frame on
   the R4 (about 70 min); I'll measure on the stills and report the real number before committing.
