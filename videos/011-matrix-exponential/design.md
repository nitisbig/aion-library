# What the Matrix Exponential Actually Is: design sheet

The look is the channel's **Classic** style (memory: crisp reference style), the same family as 006, 009 and 010:
pure black, crisp unglowed lines, Computer Modern for every glyph, symbols and numbers only. There's no caption
text, bloom, glow, blur, vignette or grain.

This video adds two things to Classic:
1. **A warm line-art prologue.** The intro opens on everyday things (a coffee cup, coins, a petri dish, a pill), drawn
   in thin white strokes, before any matrix appears. Those drawings come back when their math is paid off.
2. **Motion fields.** Most frames after the intro show a velocity field (orange arrows), with particles (yellow) moving
   through it and leaving short teal trails. Every chapter reuses that picture of a matrix as a velocity, and the
   finale lifts it into 3D as a particle Earth.

## 1. Palette (`theme.py`; scenes use `C.<role>` only)

| role | hex | object | rule |
|---|---|---|---|
| `bg` | `#000000` | background | pure black, no gradient |
| `grid` / `grid_minor` / `axis` | `#1fa2dc` / `#0f3e4d` / `#ffffff` | the plane | bright blue integer grid, dim ¼-unit minor grid, white axes |
| `gen` | `#ff8a6b` | **the generator A**: its symbol, entries, and velocity arrows A v | orange = "how things move right now" |
| `flow` | `#5cd0b3` | **the result e^{tA}**: its symbol, entries, trails, landing ghosts, every exponential curve | teal = "where they end up" |
| `vec` | `#ffe94a` | the state v / x, particles, molecules, the "you" dot on Earth | yellow = "the thing being moved" |
| `ihat` / `jhat` | `#83c167` / `#fc6255` | î, ĵ and the two columns | as in 006/009 |
| `eigen` | `#b78cf2` | eigenvectors, λ, the Earth's axis | the axis is the eigenvector with λ = 1 |
| `area` | `#f0ac5f` | the tracked patch, its area, det, trace | |
| `gen_b` | `#6cb6ff` | the second generator B (ch5 only) | |
| `comm` | `#ff4fa3` | the commutator AB − BA and the loop's leftover gap | pink = something that appears from nothing (010's null) |
| `wrong` | `#8f8f8f` | the element-wise guess and the plane it crushes | gray, never red: a dead end, not an alarm |
| `data` | `#d0d0d0` | plain numbers being read: balances, dates, names, term sizes | |
| `globe` / `land` | `#5f7f94` / `#e8e4d8` | the Earth's particle shell and graticule / its continent dots | back hemisphere dimmed |
| `frame` | `#bdbdbd` | all intro line art, panel borders | |
| `muted` / `faint` | `#a6a6a6` / `#3a3a3a` | ghosts, inactive terms, the progress stack | |

**Color grammar.** Inside an equation, each symbol takes its object's color: `A` orange, `e^{tA}` teal (the whole
exponential, including the `e`), `v` / `x` yellow, `λ` purple, `\operatorname{tr}` amber, `[A,B]` pink. Operators,
`=`, `I` and brackets stay white. The orange/teal pair is the video's spine: whenever A and e^{tA} share a frame
they're orange and teal, so velocity versus trip is readable from color alone. The prologue uses the same rule:
the coffee, coins, bacteria and rock are white line art, but the curve each one draws is teal, because it's
e^{kt}, a result.

## 2. Typography
- **Everything is LaTeX, Computer Modern** (`Eqn`, `MathTex`), including the few words that appear. There's no Inter
  or Space Grotesk on screen.
- Sizes (1080p, legible on a phone, audit `--design`):

  | use | size |
  |---|---|
  | hero equations (s04 `e^{A}`, s13 the series, s25 Rodrigues) | 72–96 px |
  | working equations | `C.tex_size` (48) |
  | matrix entries | 40 |
  | intro dates and names (CM small caps, `data`) | 30 |
  | corner progress stack | 30 (`C.label_size`) |

  Nothing is smaller than 28.
- **Matrices**: square brackets with short serifs, centre-aligned entries, a generous column gap (1.1 em), using the
  006/009 `Mat` helper. When an entry depends on t, it's typeset to 2 decimals and ticks live (`m.redraw`) in a
  fixed-width cell, so the brackets never breathe. Column colors (î green, ĵ red) appear only when the columns are
  the point (s10, s18).
- **Symbols**: `e^{tA}` always has t in the exponent when time matters; `\mathbf{v}` is bold upright; `I` is the
  identity; `N` is the shear; `K` is the cross-product matrix; `[A,B]` is the commutator.

## 3. Diagram language
- **Intro line art** (s00–s04): single-weight `C.frame` strokes with square caps and no fills, except `vec` dots.
  The set is a cup with steam, a coin stack, a petri dish, a rock, a pill and two compartments (stomach, blood),
  two rooms, a circuit, a building, a satellite, a robot arm and a quantum-circuit wire. Each is ≤ 12 strokes, built
  from Manim primitives, so it draws itself (`Create`) rather than appearing as clip art.
- **Plane**: `C.grid` integer lines over `C.grid_minor`, white axes, 1 Manim unit per unit (the frame is about
  14.2 × 8 units).
- **Velocity field**: orange arrows on a 0.75-unit lattice. Lengths are **log-compressed**
  (ℓ = 0.55·log(1 + |Av|)/log 2, capped at 0.6), so the far field doesn't swamp the centre. Thin stroke (`C.thin`),
  small triangular tip. The field is redrawn from A(t), so morphing one matrix into another morphs the field
  continuously (`key()` on the matrix itself).
- **Particles**: `PointsLayer`, glow 0, 2.5 px, yellow. Positions are **closed-form**,
  `X(t) = X₀ · expm(τ(t)·A)ᵀ`, where τ is a `Clock`, so flow time can slow, freeze or rewind and stay deterministic.
  Taichi isn't needed: linear flows are exact.
- **Trails**: 8 ghost copies at τ − kΔ (Δ = 0.04), alpha 0.5·(1 − k/8), teal. They read as crisp streaks, not blur.
- **Molecules** (s02, s22): 400 yellow dots. Each has a seeded absorption time ~ Exp(k_a) and a clearance time
  ~ Exp(k_e). A dot sits in the stomach, hops to the blood at its absorption time, and fades at its clearance time.
  It's a pure function of t. In `verify.py`, 2,000 such molecules track e^{tA} within 2%.
- **Panels**: side-by-side comparisons sit in thin `C.frame` panels with square corners (s00, s17, s18, s27).
- **The patch** (area): an amber polygon filled at 25% alpha with a crisp 100% outline. Its 64 boundary points flow
  exactly.
- **Particle Earth** (s05 map frame, s23–s25, s28 tile):
  - ~9,000 points on a unit sphere (Fibonacci lattice) in steel-blue `globe`, plus a graticule of 24 meridians and
    11 parallels.
  - Continent points are bone `land`, from the Natural Earth 110 m land mask. That's public domain, but it's a
    one-time ~150 KB download, so I'll ask first. The fallback is the graticule alone.
  - Rotation is `expm(θK)` from `verify`, projected by a small numpy perspective camera. Back-hemisphere points are
    dimmed to 25% and drawn smaller, so depth reads without lighting or glow.
  - The axis is a purple line through the poles, tilted 23.4° from screen-vertical. The equator ring is teal. A
    yellow "you" dot sits at 45° N.
  - Orange velocity arrows (Ω n × r) sit on a 12 × 6 surface lattice, longest at the equator and zero at the poles.
  - It's the 3D sequel to the 2D fields: same dots, same arrows, one dimension up.
- **Optional backdrop** (decide in the ch2 exploration): a faint LIC streamline texture of the same field
  (`shaders/lic.frag`, GLSL, per-pixel RK4 along A·p, 24 taps, `C.faint` on black, opacity ≤ 0.25). Drop it if it reads
  as blur.

## 4. Animation language
- **When the motion is the math, it's physics.** Flow time runs linearly (`ramp` / `Clock`), never eased, so a viewer
  feels constant velocity as constant. Slow motion and freezes use `Clock(rate=keys(...))`.
- **Everything else is eased**: `easy_ease` for transforms and camera, `smooth` for fades (0.6 s), `spring` only when
  a matrix settles onto its final value. No `out_back` pops.
- **Line art draws itself** (`Create`, 0.8–1.2 s, linear), then holds still. It never wiggles.
- **Reveals**: equations write left to right in term groups (`m.seq`), with a 0.08 s stagger. New symbols land on the
  narration beat (`at=T.x`, lead 0.15 s).
- **At most three things move at once.** When particles flow, equations hold still.
- **Holds**: after every payoff (−I, the series, the pill curve, Rodrigues returning to I), hold 1.5–2.5 s with
  nothing moving except the flow.
- **Continuity over cuts** (playbook rule 9):
  - the four prologue curves merge into one e^{kt} (s00);
  - the pill drawing returns as the ch6 compartments (s02 → s22);
  - the number line *becomes* the x-axis (s07 → s08);
  - the rotation circle carries into Euler's polygons (s10 → s11);
  - the shear field from ch4 carries into ch5;
  - the intro's last frame (line → globe) is answered by the Earth in s23.

  Each scene boundary rebuilds the exact end state of the previous scene.

## 5. Camera (2.5D, `s.camera`)
- The default framing is static. Moves are rare and motivated:
  - **Intro timeline** (s03): a slow lateral truck along the timeline with parallax (dates at parallax 1, a faint grid
    behind at 0.4). It's the only long camera move in the video.
  - **Dolly in** (`push`, ≤ 1.15×, 2–3 s, easy_ease) on payoffs: e^{πJ} = −I (s10), the series (s13), the loop gap
    (s20, up to 2.5× to show the s² leftover), and Rodrigues returning to I (s25).
  - **Pan** between panels (s18) and from the plane to an equation column (s12).
  - **3D**: the Earth's virtual camera sits 20° above the equator and drifts 4°/s in longitude, independent of the
    planet's own spin, so the tilted axis always reads as 3D.
- No shake, no rotate, no zoom blur.

## 6. Transitions
- **Within a chapter**: continuity transforms only (morph, carry over).
- **Between chapters**: a 1.5 s silence (`section_gap` in voice.toml). The last frame holds, then fades to black over
  0.4 s. A **symbol card** follows: the chapter's one key symbol, centred, 96 px, held 1.2 s, with no title text.
  The cards are `e^{rt}`, `A\mathbf{v}`, `\sum \tfrac{A^k}{k!}`, `\lambda`, `[A,B]` and `e^{tA}\mathbf x_0`.
  YouTube chapter names live in the description, not on screen.
- **Progress** (playbook rule 6): a corner stack (top-right, 30 px, `C.muted`) collects the facts so far as symbols:
  `e^{\pi J}=-I`, `e^{A}=\sum A^k/k!`, `\det e^{A}=e^{\operatorname{tr}A}`, `e^{A+B}\ne e^Ae^B`. It shows only in
  chapter-opening frames, for about 3 s.

## 7. Audio
- Narration: ElevenLabs, with the voice and settings shared with 004–010 (`voice.toml`), at −16 LUFS.
- An optional soft pad sits under the prologue and the outro, −28 dB below the voice. It drops out when the first
  matrix appears (s04).
- No music under dense derivations (ch3, ch5). No sound effects, except an optional low tick when the n-step polygon
  gains steps (s11).

## 8. Render plan per tool
| tool | used for | scenes |
|---|---|---|
| Manim (via `s.manim()`) | line art, planes, grids, fields, equations, matrices, polygons, plots, the timeline | all |
| aion `PointsLayer` + numpy `expm` | particles and trails, exact closed-form flows | s05, s08–s10, s14–s21 |
| seeded per-molecule hop times (numpy) → `PointsLayer` | pill molecules | s02, s22 |
| seeded split/decay times (numpy) → `PointsLayer` | bacteria doubling and atoms decaying in the prologue | s00 |
| numpy perspective projection → `PointsLayer` + Manim | the particle Earth, its axis, arrows and graticule | s05, s23–s25, s28 |
| moderngl GLSL | optional LIC streamline backdrop | s08–s10, s16 (if approved) |
| skia-python, PyVista, Taichi | not needed: every system here is linear with an exact solution, and the Earth is points, not a lit mesh | none |
