# What Matrix Inverses Actually Mean: design sheet

Rendered reference: `out/design/design_1.png` (palette, type, equations, motion) and `out/design/design_2.png` (look
frames built from the real cast). Rebuild with `uv run python videos/013-matrix-inverse/design_sheet.py`.

The look is the channel's **Classic** style, the same family as 006, 009 and 011: pure black, crisp unglowed lines,
Computer Modern for every glyph, and only symbols, numbers and key words on screen. There is no bloom, glow, blur,
vignette or grain. The "After Effects" quality comes from precise motion, continuity between shots, depth through
parallax and careful holds, not from effects.

This video adds three signature ideas to Classic:
1. **The key.** One brass key is the hero object from the first frame to the last. Its four teeth are the information
   that a collapse destroys and that the finale recovers.
2. **Threads.** A move is drawn as a web of thin lines joining each point to where it lands. Coral means walking out,
   teal means walking home. An inverse is literally the same web with the color and direction reversed.
3. **Rays and shadows.** Pink rays mark the crushed direction. They return in the finale as the beams of a scanner.

## 1. Palette (`theme.py`; scenes use `C.<role>` only)

| role | hex | object | rule |
|---|---|---|---|
| `bg` | `#000000` | background | pure black, no gradient |
| `grid` / `grid_minor` / `axis` | BASE | the plane | bright blue integer grid, dim half-step grid, white axes |
| `fwd` | `#ff8a6b` | **the move A**: symbol, threads walking out | coral always means "going" |
| `back` | `#5cd0b3` | **the way back A⁻¹**: symbol, entries, threads walking home | teal always means "returning" |
| `home` | `#f4efe0` | the identity I, anything that has returned | warm white, a resting state |
| `key` | `#f2b544` | the key | 30% fill, 100% outline |
| `vec` | `#ffe94a` | a probe point x, the target b | as in 009 and 011 |
| `ihat` / `jhat` | `#83c167` / `#fc6255` | î, ĵ, and the first and second columns | as in 006, 009 and 011 |
| `det` | `#b78cf2` | the determinant, the area patch, 1/det | |
| `null` | `#ff4fa3` | the crushed direction, light rays, amplified noise | pink means "forgotten" (as in 010) |
| `shadow` | `#8fa3b8` | the collapsed line, every shadow | cool slate |
| `cam` | `#6cb6ff` | a second observer's grid: drone, game camera | |
| `wrong` | `#8f8f8f` | the flip-every-number rule, the wrong-order rewind | gray, never red: a dead end, not an alarm |
| `data` | `#d0d0d0` | plain numbers being read: grams, angle counts | |

**Color grammar.** Inside an equation each symbol takes its object's color: `A` coral, `A⁻¹` teal, `I` warm white,
`det` violet, `x` and `b` yellow. Operators, `=` and brackets stay white. When a column is the point, its entries
take î green and ĵ red. The coral and teal pair is the spine of the video, so out versus back can be read from color alone.

## 2. Typography
Everything is LaTeX in the Computer Modern family, with three voices so each kind of element reads differently:

| voice | face | size at 1080p | used for |
|---|---|---|---|
| maths | CM roman | hero 72–96, working 48, matrix entries 44 | equations, matrices, numbers |
| key words | CM sans (`\textsf`) | 34 (never under 28) | `slide`, `squash`, `shadow`, `protein`, `fibre` |
| names | CM small caps (`\textsc`) | 32–64 | title card and chapter cards |

- Never a sentence on screen. A tag is at most two words.
- Everything sits inside `C.margin` and is legible on a phone.

## 3. Equation styling
- **Matrices** use `Mat`: square brackets with short serifs, centered entries, a fixed cell grid, so brackets never
  breathe when values tick.
- **Fractions** in `A⁻¹` are always exact (`½, −¼, −½, ¾`), never decimals.
- **Gradual reveals**: each equation grows from what motivated it. `A⁻¹A = I` assembles from the round trip (s07), the
  `1/det` slides out of the squash step (s12), and `x = A⁻¹b` is drawn along the thread it describes (s18).
- **Order of symbols** matches order of events. Products read right to left, so a small coral-then-teal arc sits under
  `A⁻¹A` the first time it appears.
- **The augmented matrix** `[A | I]` has a thin white divider. Its halves sit directly under the two grids they
  describe (s10), so the notation is visibly the picture.

## 4. Geometric diagrams
- **Plane**: 1 unit = 1 Manim unit in full-frame shots (the frame is about 14.2 × 8). At this scale the key stays inside the
  frame at every stage of the cold open (largest half-extent 3.54 × 2.87 units).
- **The key**: built in `verify.key_polys`, drawn at scale 0.62. Bow with a hole, a thin shaft, and four teeth, each up or
  down. Its shaft lies along (2, 1) so that its teeth point exactly along the crushed direction (1, −2).
- **Threads**: 1.5 px lines between a lattice of points and their images, with a warm-white dot at the start and a
  teal dot at the end. Lines outside the frame are clipped. Up to about 150 threads at once.
- **Basis arrows**: î green and ĵ red, 4 px, with crisp triangular tips. Same geometry in every shot.
- **Panels**: thin `C.frame` borders with square corners for all side-by-side views (s09–s12, s20, s21, s22–s23).
- **The area patch**: violet at 25% fill with a crisp outline.
- **Shadow accuracy note**: S equals 4 times a true projection. Each pink ray is the set of points that land on one spot,
  but the spot is not where that ray meets the line. So rays are never drawn touching their landing spot. Landing is
  shown with a fan of threads converging on the spot (s14).

## 5. Animation language
- **Matrix moves** interpolate the matrix elementwise with `easy_ease`, 1.4–2.0 s. Rotations interpolate the angle, so
  a turn stays rigid.
- **Way-back moves mirror their forward move exactly**, same duration and same easing, so a return feels like a
  rewind of the outward motion.
- **Fades** use `smooth`, 0.6 s. `spring` is reserved for a matrix settling on its final value. No `out_back` pops.
- **Threads draw from start to end** over 0.8 s with a 15 ms stagger, then reverse direction by sliding a bright dash along
  themselves when walked home.
- **Equations write left to right** in term groups with a 0.08 s stagger, landing on the narration beat.
- **At most three things move at once.** While the plane moves, equations hold still.
- **Holds**: 1.5–2.5 s of stillness after each payoff (the first return, `A⁻¹A = I`, four moves home, the collapse, the key rebuilt).
- **Continuity over cuts**:
  - the bent plane from s01 is the starting frame of s09;
  - the four moves of s01 are replayed backward in s09;
  - the tilt in s13 starts from the A of s12 and ends on the S of s02;
  - the weak powder in s19 is that same S;
  - the rays of s14 become the scanner beams of s24.

## 6. Camera movement (2.5D, `s.camera`)
- The default framing is static, so the mathematics provides the motion.
- **Dolly in** (`push`, up to 1.2×, 2–3 s, `easy_ease`) on payoffs only: the first return (s01), the flat line (s02), the
  squash (s12), the single landing spot (s14, up to 2×), the rebuilt key (s25).
- **Pan** between panels in s10–s11 and along the chain in s08.
- **Parallax**: the grid sits at parallax 1, equations at 0 (a HUD), so a push feels like depth without any blur.
- **3D** (s21): a virtual camera 20° above the horizon with a slow 3°/s orbit, so depth stays readable.
- No shake, no rotate, no zoom blur.

## 7. Lighting
- 2D scenes have **no lighting at all**. Light is expressed through color and line weight.
- **s21** uses one fixed key light from the upper left with flat Lambert shading per face (ambient 0.25), crisp
  1 px edges, no shadows or specular highlights.
- **s24–s25** are the one place light is the subject. Beams are thin parallel pink lines. Shadows are recorded as slate brightness
  on a thin detector strip. Nothing glows.

## 8. Transitions
- **Within a chapter**: continuity transforms only.
- **Between chapters**: a 1.5 s silence (`section_gap`). The last frame holds, fades to black over 0.4 s, and then a **symbol card**
  appears: the chapter's one key symbol, centered at 96 px, held 1.2 s, with the chapter name in small caps beneath it.

| chapter | card symbol |
|---|---|
| 1 The way back | `A^{-1}` |
| 2 Rewind | `(BA)^{-1}` |
| 3 Finding the way back | `[A \mid I]` |
| 4 What can't come back | `\det A = 0` |
| 5 Who landed here? | `A\mathbf{x} = \mathbf{b}` |
| 6 The way back at work | `C^{-1}` |
| 7 Shadows | the key's shadow, drawn |

- **Progress** (playbook rule 6): a small corner stack (top right, 30 px, `C.muted`) collects results as symbols:
  `A^{-1}A = I`, `(BA)^{-1} = A^{-1}B^{-1}`, `\tfrac{1}{\det A}`, `\det A = 0`. It shows only in chapter-opening frames.

## 9. Audio
- Narration: ElevenLabs with the voice and settings shared with 004–012 (`voice.toml`), normalized to −16 LUFS.
- No music under derivations. An optional soft pad, 28 dB below the voice, under the cold open and the final minute.

## 10. Render plan per tool
| tool | used for | scenes |
|---|---|---|
| Manim via `s.manim()` | grids, key, arrows, threads, equations, matrices, panels | all |
| GPU compositor (moderngl) | all layer compositing, 2.5D camera, parallax | all |
| moderngl GLSL (`shaders/beam.frag`) | scanner beams sweeping across the key, computed per pixel | s24, s25 |
| numpy + scipy → `FramesLayer` | blur, inverse and noise frames; CT reconstructions baked once to `.npz` | s22, s23, s25 |
| skia-python → `FramesLayer` | flat-shaded low-poly game world with crisp edges | s21 |
| Taichi | not needed: nothing here is a simulation, and every frame has a closed-form or pre-solved answer | none |
| PyVista | not needed: skia gives crisper edges for the few flat-shaded blocks and uses less memory on this machine | none |
