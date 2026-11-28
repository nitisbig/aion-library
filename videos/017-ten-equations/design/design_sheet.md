# 10 Equations That Run the Modern World: design sheet (video 017)

Rendered reference: `design/style_frames/01_in_heat_bar.png` … `13_out_web.png` (intro, one look frame per chapter,
outro) and `design/components.png` (progress rail, chapter card, type scale, palette). They go through aion itself (theme,
LaTeX, Manim rasteriser, GPU compositor, pyvista, skia), at 1920×1080. Every curve, field and number on them is computed
in `sims.py` / `eqdata.py` (seeded numpy, an LBM bake). Rebuild with
`uv run python videos/017-ten-equations/design/style_frames.py [n …]` (one process per frame; frames 2 and 13 reuse the
chapter PNGs, so render them last). Tokens: `design/tokens.json`, written and checked by `scripts/export_tokens.py`.
`theme.py` is the only source of colour, and `plan/scenes.yaml` is the only source of what each scene shows.

The look is the channel's **Classic** style with **accent glow**: pure black, crisp lines, Computer Modern for every
glyph, key words only, and glow only on the element each shot is about.

**Screen language (revised 2026-11-26).** Each chapter gets its own full-bleed composition built for its simulation.
There are no bordered boards, panels, cards or other web-UI boxes, and nothing is split into framed multi-views.
Equations float in open black space. Where text has to sit over a busy raster, a feathered **shade** darkens the pixels
under it, and you never see it as a shape. There's no `n / 10` counter: a **progress rail** in the bottom-left
corner shows where you are in the video. **Text never glows.**

## Signature ideas
1. **Ten windows, one wall.** Every chapter's look frame is also its tile. The intro wall (in_s02) is ten live tiles
   lit in narration order. Each chapter opens by diving into its tile, and the outro (out_s01) brings the same ten
   tiles back as a carousel. The viewer sees each simulation three times: as a preview, in full, and as a memory.
2. **One hue per chapter, carried everywhere.** The chapter hue marks the tile rule, its segment of the progress rail,
   the name-tag rule, the card rule and the equation's main symbol (u in Fourier, ψ in Schrödinger, G_μν in Einstein …). Inside a chapter
   the in-chapter roles take over (E gold, B cyan, charges red/magenta, noise violet …).
3. **The heat equation is the spine.** It opens the video (Fourier's hot bar, 1822), is the visual seed of chapter 5,
   and returns in chapter 10 as the hidden form of Black–Scholes, drawn in the Fourier hue (frame 12, bottom right).
4. **Every equation is read in words.** Each term gets one key word in CM sans (carried · pressure · sticky; shape =
   matter; step size · slope). When tags would collide under a long equation, a small term → word legend sits below it
   (frames 7, 9, 10). It's a plain two-column list with no box around it.

**Signature shots** (hold 1.5–2.5 s each): the bar's glow splitting into cosine modes (in_s01) · the full wall with the
timeline (in_s02) · E and B chasing off at c (c01_s03) · the ray-traced black hole (c02_s03) · the packet's glowing
remnant beyond the wall, "15%" (c03_s02) · the vortex street (c04_s02) · epicycles finishing π (c05_s02) · the light
clock's triangle (c06_s01) · the ball settling in the valley (c07_s01) · the constellation blurring (c08_s02) ·
"9 of 98" (c09_s01) · the price fan becoming the bell, with the heat equation beside it (c10_s02) · the carousel (out_s01).

## 1. Stage
- 16:9. Master **3840×2160, 30 fps**, SDR Rec.709; stills, sheets and previews at 1080p. World frame 14.22 × 8 u;
  **1 u = 135 px at 1080p (270 px at 4K)**. Every size here is in world units or Manim font sizes, so it holds at 4K.
- Background `C.bg` #000000, flat. No frame-wide Bloom, Blur, Lens, grain or vignette.
- Margin: nothing drawn beyond 0.45 u (BASE). **Text, tags and the rail stay inside the safe box** x ∈ [−6.40, 6.40],
  y ∈ [−3.29, 3.29] (0.71 u inset). Full-bleed simulations (black hole, vortex street) may run to the frame edge, but text
  over them doesn't.

## 2. Screen language (`components.png`)
No boards, panels, frames, backing rectangles or rounded UI boxes, and no `n / 10` counter. Each chapter composes its own
full-bleed frame around its simulation. The recurring parts are these:

| part | geometry (world units) | rule |
|---|---|---|
| **Sim field** | full frame, or the left ~9 u | the simulation owns the frame; rasters fade into black at their edges (`feather()`), never a hard rectangle |
| **Equation column** | x 2.75 … 6.40 (3.65 wide), centred at x 4.58 | the default place for the equation, its term tags or legend and one small plot (frames 3, 5, 7, 9, 10, 11). Equations are `fit()` to the column |
| **Floating equation** | over the sim, centred | used when the sim fills the frame (ch 2 under the black hole, ch 4 above the vortex street, ch 10 above the paths) |
| **Shade** | the text's bounding box + 0.4–1.2 u | a feathered black superellipse (power 4, alpha 0.7–0.88, 0.6 u soft falloff) under text that sits over a busy raster. You never see its edge. Only where needed (frames 3, 4, 9) |
| **Name tag** | top-left, from (−6.40, 3.29) | a 0.7 u rule in the chapter hue over small caps 30 "James Clerk Maxwell · 1865". Moves to the bottom-right when the equation holds the top (ch 4). First appearance only, then fades |
| **Progress rail** | bottom-left: x −6.40 … −1.40 (5 u), y −3.30 | see below. On screen for the whole of chapters 1–10, hidden in the intro and outro |
| **Wall** | 5 × 2 tiles 2.38 × 1.34, 0.22 gutter, rows at y 1.75 / −0.85, timeline at y −3.05 | intro (in_s02): borderless tiles, a hue rule under each, small-caps name on a shared baseline, year below |
| **Carousel** | orbit (4.75 cos u, −0.15 − 1.75 sin u), tiles scaled 0.48–1.08 by depth | outro (out_s01): the same tiles in depth, linked in story order by glowing arcs; "Ten equations · 1763 – 1973" in the still centre |

**Progress rail.** One rail for the whole video, made of ten segments whose lengths are proportional to each chapter's
real audio duration (from `beats.py`), with a 0.05 u gap between segments.
- Past chapters: a 2.5 px line in their hue at 50 % tint, so the finished part of the video reads as a colour strip.
- Chapters still to come: a 1.5 px line in `C.muted` at 45 %.
- The current chapter:
  - A comet fill that brightens towards the head (24 pieces, tint 0.35 → 1, 4 px).
  - Small ticks at its scene boundaries (s02, s03), which turn from muted to the hue as they're passed.
  - The head itself: a 0.085 u ring in the hue around a 0.04 u `C.light` dot.
- The chapter's title sits in small caps 20 `C.text` 0.17 u above the rail's left end.

The rail is a pure function of audio time, so the head glides continuously. At a chapter boundary the old title fades
out and the new one fades in over 0.4 s. Nothing on the rail glows. `rail(k, t)` in `style_frames.py` is the reference
implementation, to be promoted into the video's `kit` for the build.

**Chapter card** (2 s, inside the chapter's pause), all on black with no frame:
- On the left, the portrait (public domain, duotoned in the chapter hue, 2.2 u tall), feathered so that it fades into
  the black.
- Beside it, the title in small caps 48 `C.text`, a 3.2 u rule in the hue, and the name and year in small caps 24 `C.muted`.
- The rail stays visible below. The card enters with a slow push-in (1.03 → 1.0) and leaves by dissolving into the
  chapter's first frame.

## 3. Palette (`theme.py`; scenes use `C.<role>` only)
Chapter hues: ten OKLCH hues at L ≈ 0.77, 36° apart, ordered so that neighbouring chapters sit far apart on the wheel.
All pass WCAG text contrast on black (≥ 7.9:1). Min pairwise ΔE2000 between them is 16.8 in normal vision. They can't
all separate under colour blindness, so **every tile, card and the rail also carry the chapter's name in words**.

| # | role | hex | contrast | | role | hex | contrast | object |
|---|---|---|---|---|---|---|---|---|
| 1 | `maxwell` | `#02C5FF` | 10.4 | | `e_field` | `#FFC452` | 13.3 | E, its wave, E stems |
| 2 | `einstein` | `#E3AA00` | 10.0 | | `b_field` | `#02C5FF` | 10.4 | B, its wave, the radiation field (= maxwell) |
| 3 | `schrod` | `#B28AFF` | 8.0 | | `charge_p` | `#FF5A4E` | 6.8 | + charge, high pressure, −∇p |
| 4 | `navier` | `#14CEC9` | 10.7 | | `charge_n` | `#B751B5` | 4.9 | − charge, negative vorticity |
| 5 | `fourier` | `#FE955C` | 9.7 | | `light` | `#F2F6FF` | 19.4 | photons, light pulses, stars, error points, the descent ball (glows) |
| 6 | `dilation` | `#8FB3FD` | 10.0 | | `mass` | `#8C9098` | 6.6 | the heavy sphere, matter |
| 7 | `descent` | `#37D385` | 10.8 | | `data` | `#D9DEE6` | 15.5 | data points to fit |
| 8 | `shannon` | `#A7C32B` | 10.5 | | `noise` | `#B77DF8` | 7.3 | noise clouds |
| 9 | `bayes` | `#FF8D9D` | 9.6 | | `ill` / `positive` / `prior` | `#FF5A4E` / `#FFD84A` / `#7EB7E7` | 6.8 / 15.2 / 9.8 | ill dots, positive rings, belief before |
| 10 | `bs` | `#FE7FDD` | 9.3 | | `payoff` / `bad` | `#FFC452` / `#F94047` | 13.3 / 5.9 | option payoff, the market jump |

- In-chapter groups (the colours that share a frame) pass ΔE2000 ≥ 20 in normal vision and ≥ 10 under deutan, protan
  and tritan simulation. The tightest is c04 (`navier`, `charge_p`, `charge_n`, `light`) at 11.8 protan.
  `design/tokens.json` has every number.
- `card` `#0B0E13` is a lifted black for solid bodies on a sim (the ch 4 cylinder), never a backing behind text.
  `C.muted` is for tags and secondary labels only.
- **Domain colouring** (ψ phase, ch 3) uses an even-lightness OKLCH wheel (L 0.80, C 0.13), shown with its key wheel.
  It's the only place a rainbow is allowed.
- **Fields** are dim: they stay ≤ 10 % linear of their hue (`tint(C.b_field, 0.09)` in frame 3), so curves drawn on
  top keep full contrast. Diverging fields (vorticity) run `charge_n` ↔ black ↔ `navier`, with the free stream held at
  black by a 6 % dead zone.

## 4. Type (`components.png`)
| level | face | size (Manim font_size at 1080p) | colour |
|---|---|---|---|
| equations | CM roman (MathTex / `Eqn`) | 40–56 in the column, ≥ 34 after `fit()` | `C.text`, terms in their role colour |
| key words, tags, axis names | CM sans (`\textsf`) | 20–30 (axis 20, tags 22–24, payoff numbers 26–28) | `C.muted`, or the role colour for a coloured term |
| names, dates, titles | CM small caps (`\textsc`) | name tag 30, wall label 24, rail title 20, card title 48 | `C.text` |
- One equation per frame, at most 4 key words under it. No sentences on screen. Numbers on screen are computed
  (`eqdata.py`, `sims.py`): c ≈ 2.998 × 10⁸ m/s, 15 % tunnelled, 199 Mbit/s at 20 MHz and 30 dB, 9 / (9 + 89) ≈ 9 %, ticks 10 vs 8 at 0.6c.
- `%` and `&` are escaped in `sans()`/`caps()`. **Never isolate a single letter that also occurs inside a macro** (B in
  `\Big`, u in `\tau`). Isolate the whole term (`\partial u`) or use `\left`/`\right`.

## 5. Glow (accent only)
- `Glow(color, strength=C.glow·k, radius=C.glow_r)` on a layer that holds **only** the lit element. `C.glow` 0.9,
  `C.glow_r` 5 px at 1080p, k 0.4–1.0.
- Lit elements, one per shot: the hot end of the bar · "speed of light" · the transmitted packet · the drawn π trace ·
  the light-clock photon · the 16 constellation points · the payoff line · the carousel links. **Text, equations, tags,
  the rail, grids and axes never glow.** Names, titles and labels are always plain, crisp glyphs.
- Glow follows the layer's **alpha**, not its colour. Black-filled shapes in a glow layer still bloom, so fade alpha in
  with the quantity instead (the heat bar: alpha = ((v − 0.35)/0.5)²).

## 6. Camera
- **2D** (flat Manim): equations, derivations (ch 6 triangle, ch 9 dots).
- **2.5D**: `s.camera` push-ins and pans with parallax layers; oblique projections drawn in Manim for depth without a
  3D renderer. The mode stack (in_s01, x − 0.30·z, y + 0.66·z), the E ⊥ B wave (x − 0.55·z, y − 0.42·z), the ψ helix,
  the tilted constellation plane, the wall-to-carousel move.
- **3D**: pyvista off-screen rasters (loss surface, later the spacetime sheet, orbitals, the price surface, Earth and
  GPS orbits) and the ray-traced `BlackHoleLayer`. Camera moves in 3D are baked per frame. Keep orbits slow (≤ 15°/s)
  and ease them in and out.
- **Transitions**: dive into a tile (scale about the tile centre, 0.9 s, `easy_ease`) at each chapter start; the bridge
  object morphs (wave → ray → atom → ripple → signal → clock → terrain → bit stream → probability bars → price bell →
  web). Use continuity rather than cuts; cut only on the chapter card.

## 7. Motion
- Every reveal is eased (`smooth`, `easy_ease`, `out_back` for small pops). Stagger lists
  by 0.08–0.12 s. Nothing pops.
- At most 3 things change at once. Hold the signature shots 1.5–2.5 s during pauses.
- Sims run on audio time: the frame shown at time t is a pure function of t (`bake()` caches, `m.drive` for Manim).

## 8. Engine per layer (as used in the frames)
| chapter | layer | engine |
|---|---|---|
| intro | heat bar, cosine modes, wall, timeline | Manim (+ Glow); tiles = `ArrayLayer` of each chapter's precomp |
| 1 Maxwell | dipole radiation field | `FieldLayer` (numpy, analytic) → shader in the build |
| | E ⊥ B wave, the four laws | Manim, oblique 2.5D |
| 2 Einstein | black hole | `BlackHoleLayer` (ray traced, GPU) |
| 3 Schrödinger | ψ(x, t) | split-step FFT (numpy), drawn as a phase-coloured Manim helix |
| 4 Navier–Stokes | vortex street | D2Q9 lattice Boltzmann (420 × 150, 16k steps, cached) → numpy RGBA → `ArrayLayer` |
| 5 Fourier | epicycles, spectrum | Manim (`sims.fourier_path`, 90 terms of the π outline) |
| 6 Dilation | light clocks | Manim |
| 7 Descent | loss surface + path | pyvista off-screen raster → `ArrayLayer` |
| 8 Shannon | 16-QAM + noise | `PointsLayer` (seeded), Manim grid and glowing points |
| 9 Bayes | 1,000 people, 98 positives | `PointsLayer` + Manim rings |
| 10 Black–Scholes | 2,000 GBM paths | skia-python raster → `ArrayLayer`; histogram and payoff in Manim |
| outro | carousel | `ArrayLayer` cards scaled by depth, glowing orbit links |

**4K notes.** Manim text and lines render natively at 4K. Rasters (pyvista, skia, LBM) are made at the output size of
their box: 1080p for previews, the 4K box size for finals (pass `px_per_u=270`). The LBM field is upsampled with cubic
interpolation, so bake the final at 840 × 300 (Taichi) for a sharper street with more shed vortices. VTK must render
before aion's GL context exists (`PRE` hook in style_frames.py).

## 9. Style frames: what each one fixes
| frame | scene @ beat | composition | what it decides |
|---|---|---|---|
| 01 heat bar | in_s01 @ "smooth waves" | full-bleed | the Fourier hue as hot metal; modes stacked in depth; glow on the hot end only; no rail in the intro |
| 02 wall | in_s02 @ "wire" | wall | borderless tiles, hue rule, small-caps name on a shared baseline, year; timeline 1763 → 1973 |
| 03 light | c01_s03 @ "speed of light" | sim left, column right | dim radiation rings behind a bright E ⊥ B wave; four laws and c under soft shades |
| 04 black hole | c02_s03 @ "black hole" | full-bleed, floating equation | ray trace to the edges; equation read as shape = matter over a shade; rail over a corner shade |
| 05 tunnel | c03_s02 @ "tunnelling" | full-width helix, column right | ψ as a phase helix; \|ψ\|² below; glow only on what got through (15%) |
| 06 vortex | c04_s02 @ "pressure" | full-bleed, equation on top | vorticity in two hues over black; terms tagged in their colours; name tag bottom-right |
| 07 epicycles | c05_s02 @ "circles" | sim left, column right | glowing trace, ghost of the rest; bare spectrum stems; term legend |
| 08 light clock | c06_s01 @ "slowly" | one open stage | rest vs moving side by side (no split boxes); the triangle labelled cΔt, vΔt′, cΔt′; ticks 10 vs 8 |
| 09 descent | c07_s01 @ "gradient descent" | 3D surface left, column right | lit pyvista surface fading into black; legend and error curve in the column |
| 10 constellation | c08_s02 @ "strong" | sim left, column right | tilted plane; noise clouds; white error points; capacity curve |
| 11 test | c09_s01 @ "one in eleven" | sim left, column right | 990 + 10 dots, yellow positive rings, the 98 gathered, 9 % |
| 12 paths | c10_s02 @ "heat equation" | full-bleed, equation on top | 2,000 paths fan into a bell; payoff glows; the heat-equation callback |
| 13 web | out_s01 @ "markets" | carousel | the ten tiles in depth, linked in story order, the closing line in the centre |

## 10. Open items for the build
- Portraits: done. 8 public-domain portraits are duotoned and feathered by `scripts/portraits.py` (see
  `assets/images/portraits/CREDITS.md`). Names-only cards: ch 4 (Navier · Stokes), ch 9 (Bayes), ch 10 (Black · Scholes ·
  Merton). Cauchy's lithograph keeps a faint tint around the shoulders; the card's feather hides most of it.
- Ch 4: re-bake the vortex street at 840 × 300 (Taichi) for the final; the 420 × 150 bake is enough for the style frame.
- The heat bar shows faint vertical banding (320 rectangles). In the scene, draw it as a `FieldLayer` row instead.
- Pronunciation of the names in the narration hasn't been checked by ear yet.
