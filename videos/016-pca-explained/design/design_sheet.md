# PCA Explained Visually: design sheet (video 016)

Rendered reference: `design/style_frames/01_in_shadow.png` … `08_ch6_curved.png` (one look frame per chapter) and
`design/components.png` (layouts, chapter card, type scale, palette). They are rendered through aion itself (theme,
LaTeX, Manim rasteriser, GPU compositor, pyvista), 1920×1080, and every value on them is computed in `pcadata.py`.
Rebuild with `uv run python videos/016-pca-explained/design/style_frames.py [n …]`. Tokens: `design/tokens.json`
(written and checked by `scripts/export_tokens.py`). `theme.py` is the only source of colour; `plan/scenes.yaml` is the
only source of what each scene shows.

The look is the channel's **Classic** style with **accent glow**: pure black, crisp lines, Computer Modern for every
glyph, key words only, and a glow only on payoff elements.

## Signature ideas
1. **The shadow bookends the video.** A point sculpture under a warm lamp (pyvista, real cast shadow). Most views are
   blobs; the top principal plane shows three clusters and a spiral. It opens the video (in_s01), returns small in
   ch6_s03, and closes it (out_s02). PCA is the calculation that finds the best shadow.
2. **The whiteboard rule (multi-board layout).** Finished results are pinned, not erased: they shrink into the rail and
   return when they're needed (the dial returns in ch3_s03, B_C in ch4, the recipe through ch5, all of them in out_s01).
   Full wipes only at chapter cards.
3. **Two datasets, all video.** Forty people (height and arm span, then shoulder width) carry the intuition; 1,797
   scanned digits carry the payoff. No new example per chapter.
4. **Colour = role.** Gold is always "the best direction" (PC1), pink is always "what you throw away", red-orange is
   always "spread" (variance, covariance, λ). The equations use the same colours as the shapes they describe.

**Signature shots** (hold 1.5–2.5 s each): the shadow resolving (in_s01) · the digits lighting class by class (in_s03)
· the probe line locking gold at the dial's peak (ch2_s01) · Pearson and Hotelling locking together (ch2_s02) · the dial
landing exactly on uᵀCu (ch3_s03) · two arrows that stay on their lines (ch4_s01) · the 3 sharpening (ch5_s03) · the
map with eigen-digits on its axes (ch5_s04) · the best shadow once more (out_s02).

## 1. Stage
- 16:9. Master **3840×2160, 30 fps**, SDR Rec.709; drafts, stills and previews at 1080p. World frame 14.22 × 8 u;
  **1 u = 135 px at 1080p (270 px at 4K)**. Every size below is in world units or Manim font sizes, so it holds at 4K.
- Background `C.bg` #000000, flat. No frame-wide Bloom, Blur, Lens, grain or vignette.
- Margin: nothing drawn beyond 0.45 u (BASE). **Text, tags and boards stay inside the safe box** x ∈ [−6.40, 6.40],
  y ∈ [−3.29, 3.29] (0.71 u inset, 96 px). `aion audit --design` checks only the 0.45 margin, so check the inset by eye.

## 2. Layouts (style frames 3–8, `components.png`)
| id | geometry (world units) | use |
|---|---|---|
| **L1 Stage** | the safe box | intro shots, big reveals, chapter cards, recipe |
| **L2 Stage + Rail** | stage x −6.40…2.30 (8.70 wide); rail x 2.55…6.40 (3.85 wide), three slots 2.06 tall, 0.20 apart, top slot y 1.23…3.29 | the default teaching layout |
| **L3 Split** | two boards x −6.40…−0.125 and 0.125…6.40, y −3.0…3.0 | comparisons (most spread vs closest fit, 2D vs 3D, roll vs shadow) |
| **L4 Grid** | 2×2 boards, 0.25 gutters | applications montage (in_s04), recap wall (out_s01, 2×3 variant) |

- **Boards** are `panel()` frames (black fill, thin `C.roles.frame` border). A board's **tag** is one key word in CM sans
  24, `C.muted`, 0.16 u inside its top-left corner. No sentences on screen.
- **Rail rules.** A board enters the rail by scaling into its slot (0.8 s, `smooth`) and never scales up past 1.0 there.
  Slots fill top-down; when a fourth board arrives, the oldest leaves to the right. Unused slots are not drawn. A
  recalled board slides back to the stage on the same path, then returns.
- **Chapter cards (L1).** CM sans 26 "chapter two" in `C.muted`, the title in small caps 50–64, a 2.8 u gold rule
  (`C.pc1`). A **carry-over strip** at the bottom holds the previous chapter's key board at 50 % opacity, so a full wipe
  still shows where we came from. Card on screen 2.5 s, during the chapter's pause.

## 3. Palette (`theme.py`; scenes use `C.<role>` only)
| role | hex | contrast | object |
|---|---|---|---|
| `data` | `#7EB7E7` | 9.81 | data points, shadow dots on a line; also the negative side of diverging maps |
| `mean` | `#F4EFE0` | 18.27 | μ, centring rulers, the hypotenuse ‖x̃‖ and its square |
| `probe` | `#D9DEE6` | 15.54 | the searching line / unit arrow u before it locks (graphics) |
| `pc1` | `#FFC452` | 13.27 | PC1, v1, z1, "kept", the cumulative curve. **Glows at lock-in.** |
| `pc2` | `#1FE0AB` | 12.31 | PC2, v2, z2 |
| `pc3` | `#A77FFF` | 7.12 | PC3 (3D pebble), the yield-curve bend |
| `residual` | `#FF5DA7` | 7.38 | gaps d, drop lines, reconstruction error, "lost", negative covariance products |
| `spread` | `#FF4D00` | 6.31 | variance squares and bars, C and its entries and ellipse, λ, scree bars; the positive side of diverging maps |
| `d0`…`d9` | OKLCH ring (see tokens) | 7.3–12.1 | digit classes on the map, **always with a numeral label** |
| `lamp` | `#FFE2B0` | — | the lamp light of the bookends (pyvista) |
| BASE `text` / `muted` / `grid` / `grid_minor` / `axis` / `frame` | | | text; tags and tick labels; the Classic plane |

- **Colour-blind check** (`export_tokens.py`): the seven core roles (data, mean, pc1, pc2, pc3, residual, spread) are
  ≥ 21.1 CIEDE2000 apart in normal vision and ≥ 10.5 under simulated deutan, protan and tritan. Eight hues did not pass,
  so **variance, covariance and eigenvalues share `spread`** (they're all spreads, so that's also the right story).
- **Digit hues** are 16.4 apart in normal vision but cannot survive colour blindness (no ten hues can). So: each class
  carries a numeral at its centroid in a ringed black disc, and in_s03 lights classes **one at a time** on the narration.
- **Diverging maps** (covariance heatmap, eigen-digits): `C.data` (negative) – black – `C.spread` (positive), mixed in
  linear light (`tint()`), the classic colour-blind-safe blue/orange pair.

## 4. Type (all Computer Modern via LaTeX)
| use | style | size (Manim font_size at 1080p) |
|---|---|---|
| equations | CM roman (`MathTex`/`Eqn`) | 44–56 on the stage, ≥ 34 in the rail |
| key words, board tags, axis names | CM sans `\textsf` | 24–30 |
| names, dates, chapter titles | CM small caps `\textsc` | 34 (lower thirds), 50–64 (cards) |
| numerals on the digit map | CM roman | 44, in a 0.27 u ringed disc |
| title lockup | `\textsf{\textbf{PCA}}` 64 over small caps 34 | in_s03 only |

Labels that sit on the grid get a black backing (`backed()`), so grid lines never cut through glyphs. Equations are
coloured term by term to match their shapes (`Eqn(colors=…)`) and revealed term by term on the narration.

## 5. Motion
- Easing: `smooth` for moves, `easy_ease` for camera, `out_back` (small overshoot) only for pins into the rail,
  `spring` never on text. Default move 1.0 s, fade 0.6 s, `lead` 0.15 s before the beat.
- At most three things change at once. Point swarms stagger (0.02–0.05 s per item, seeded order).
- Holds: every signature shot holds ≥ 1.5 s, inside the narration's planned pause.
- Projections and rotations are **pure functions of the angle** (`m.redraw`): the shadows, gaps and the dial are
  recomputed from the data each frame, never tweened.

## 6. Accent glow (approved for 015, reused here)
`Glow(color, strength=C.glow (0.9) × k, radius=C.glow_r (5 px))` on a separate layer holding **only** the lit element:
PC1 at lock-in (k 0.45 for long lines), the eigenvectors (k 1), the digit-map settle (PointsLayer glow 0.25), the
best shadow (k 0.25 on dense point sets). Text, grids, axes, boards and backgrounds never glow.

## 7. Engines (per layer)
| need | engine | notes |
|---|---|---|
| equations, axes, 2D scatter, transforms, matrices (`Mat`, `brackets`), boards | Manim via `s.manim()` | `m.play(at=T.x)`, `m.redraw` for anything computed from an angle |
| 1,797-point digit map, swiss roll, 3D people cloud | `PointsLayer` (moderngl) | one layer per digit class; `additive=False`; 3D via our own orthographic projection or `s.camera` |
| lit 3D: the sculpture and its cast shadow, the pebble and its plane | pyvista off-screen → `FramesLayer` | baked per frame (VTK before aion's GL context), cached; `enable_shadows()` works on this Mesa GPU |
| tables, pixel tiles, eigen-digits, face sketches | skia-python → `ArrayLayer` | premultiplied, crisp squares, no smoothing |
| covariance heatmap | `FieldLayer` | diverging data/spread map, nearest-neighbour cells |
| light cone, glow | GLSL shader layer, `Glow` fx | the cone is additive and only in the bookends |
| every number | `pcadata.py` (numpy `eigh`, checked against sklearn and the SVD in `verify()`) | seeds 16, 17, 1601–1603 |

## 8. Notes from the style-frame pass
- Frame 1: the lamp moved off-axis so the shadow falls beside the sculpture; in the scene the camera will pull back
  ~10 % so the shadow's left edge clears the sculpture.
- Frame 4: glow on long lines is k 0.45, or it swamps the shadow dots.
- Frame 6: with the real C (λ1/λ2 ≈ 8) the v2 image is short (0.37 u); it stays visible because the unit arrow is
  drawn as a ghost behind it. The people data was widened (arm-span spread 6 cm) for exactly this reason.
- Frame 8: the roll must be wider than it is across, or PCA's best view shows the spiral cleanly and the "layers on top
  of each other" claim would be false. `pcadata.swiss_roll()` is built that way.
