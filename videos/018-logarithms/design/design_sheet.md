# What Logarithms Actually Are: design sheet (video 018)

Rendered reference: `design/style_frames/01_in_napier.png` … `10_out_recap.png` (one look frame per chapter, plus the
intro and outro) and `design/components.png` (progress rail, name tag, chapter card, type scale, palette). They are
rendered through aion itself (theme, LaTeX, Manim rasteriser, GPU compositor, skia) at 1920×1080, and every number on
them comes from `logdata.py`. Rebuild with `uv run python videos/018-logarithms/design/style_frames.py [n …]`. Tokens
live in `design/tokens.json`, which is written and checked by `scripts/export_tokens.py`. `theme.py` is the only source
of colour, and `plan/scenes.yaml` is the only source of what each scene shows.

The look is the channel's **Classic** style with **accent glow**: pure black, crisp lines, Computer Modern for every
glyph, key words only, and glow only on the graphic each shot is about. Text never glows. There are no boards, panels
or boxes, and no `n / N` counter.

## Signature ideas
1. **The multiplication staircase is the video.** Every chapter turns the same object: it is counted (c01), stacked
   and descended (c02), tipped flat into a ruler (c03), smoothed into the curve (c04), and rebuilt as the recap (outro).
   Its geometry is fixed (`staircase()` in `style_frames.py`, promoted into `kit.py` for the build): treads carry the
   value bᵏ, a ×b tag sits beside each riser, and a left axis counts the steps, so **height = the logarithm**.
2. **Three colours carry every logarithm.** The base is amber, the steps (the logarithm itself) are periwinkle, and the
   value (bᵏ) is magenta. This holds for `log₂ 1024 = 10`, for `log 2 + log 3 = log 6`, for the slide rule's lengths
   and for the decibel ruler. A viewer learns to read the colours before the symbols.
3. **e and ln are mint, and so is the area under 1/x**, because that area *is* ln x. The colour makes the c05 payoff
   before the narration does.
4. **Every worked example pauses.** The question writes, a thin countdown ring (a graphic, never a box) runs during the
   1.2 to 1.5 s pause, then the answer is built step by step in the open column.

**Signature shots** (hold 1.5 to 2.5 s each):
- π × e collapsing into log + log over Napier's page (in_s01)
- the colony of 1024 cells (c01_s01)
- the full staircase with both forms of the definition (c01_s02)
- the 31-digit number typed out under its underline (c02_s03)
- the slide rule reading 6 (c03_s02)
- the 3D flip of 2ˣ into log₂ x (c04_s01)
- the edge stopping at e with the area reading 1.000 (c05_s03)
- the concert three ×10 steps above conversation (c06_s01)
- Kepler's planets on one line (c06_s03)
- the six-step recap (out_s01)

## 1. Stage
- 16:9. The master is **1920×1080 at 60 fps**, SDR Rec.709 (4K on request). The world frame is 14.22 × 8 u, with
  **1 u = 135 px**.
- The background `C.bg` is #000000 and flat. There is no frame-wide Bloom, Blur, Lens, grain or vignette.
- **Text, tags and the rail stay inside the safe box** x ∈ [−6.40, 6.40], y ∈ [−3.29, 3.29]. Full-bleed rasters
  (Napier's page, cells, sound rings, terrain) may run to the frame edge and fade into black (`feather()`), but text
  over them does not.

## 2. Palette (`theme.py`, checked by `scripts/export_tokens.py`)

| role | hex | object |
|---|---|---|
| `base` | #FFB23E | the multiplier b, ×b on risers, stretch and scale arrows, ×10 brackets |
| `steps` | #8FB4FF | the logarithm: step counts, exponents, log readouts, lengths on a ruler, fitted lines |
| `value` | #FF5FB8 | the result bᵏ: tread values, products, the exponential curve, markers |
| `natural` | #6EF7B3 | e, ln, the natural-log curve, continuous growth |
| `area` | #6EF7B3 | the region under 1/x (natural at 32 % fill, a glowing edge) |
| `ruler` | #F1E4C4 | engraved scales, the slide-rule cursor, piano keys, line drawings |
| `paper` | #D9C9A3 | Napier's page (raster only) |
| `cell` | #8CF425 | the dividing cells |
| `sound` | #E8453C | sound rings |
| `star` | #F2F6FF | the star field |
| `quake` | #FF7A3D | the earthquake ripple and its ×31.6 tags |
| `acid` | #C9E83A | pH markers and glasses |
| `planet` | #F4AF25 | Kepler's planets and orbits (never shares a frame with `base`) |
| chapter hues | #8FB4FF · #FF5FB8 · #F1E4C4 · #FFB23E · #6EF7B3 · #B48CFF | rail segments, card rule, name tags |

All text roles reach ≥ 4.5:1 contrast on black. Every group of colours that shares a frame passes CIEDE2000 ≥ 20 in
normal vision and ≥ 10 under simulated deuteranopia, protanopia and tritanopia:
- the log roles
- the c04 curves
- the c05 area
- the c01 cells
- the c03 ruler
- the c06 senses, earth and Kepler frames

The six chapter hues are only ≥ 17 apart in normal vision, so the rail and the card always carry the chapter's name
in words.

## 3. Typography (all Computer Modern via LaTeX)
- **Maths:** CM roman, with every term coloured by its role (`ctex()`). Hero equations are 56–64, column equations 44–52,
  and labels on a graph 20–34.
- **Key words:** CM sans (`\textsf`), 20–26, in `C.muted` or the role colour ("steps", "divisions", "concert",
  "swap x and y"). Never sentences.
- **Names, dates, chapter titles:** CM small caps (`\textsc`), 30 for name tags and 48 for chapter cards.

## 4. Screen language (`components.png`)

| part | geometry (world units) | rule |
|---|---|---|
| **Layout L1: full-bleed stage** | whole frame | the raster owns it; text sits on a feathered **shade** (black superellipse, α 0.8 to 0.9, a 0.6 u soft edge) only where the raster is busy |
| **Layout L2: staircase + open column** | staircase in x −6.1 … 2.0; column x 2.75 … 6.40 | the equation floats in the column, coloured by role; at most one key-word legend under it |
| **Layout L3: graph plane** | the Classic grid (minor 0.5, blue integer lines, white axes) | the curve owns the frame; equations float top-right |
| **Layout L4: ruler band** | one or two horizontal rulers across the middle in slight 2.5D | numbers on the ticks, one result below in CM |
| **Name tag** | top-left from (−6.40, 3.29) | a 0.7 u hue rule over small caps 30, "John Napier · 1614"; first mention only, fades after about 4 s; in this tutorial cut only Napier gets a full tag, while Gunter, the 1640s geometers and Kepler get small tags |
| **Progress rail** | bottom-left, x −6.40 … −1.40, y −3.30 | six segments sized by real chapter audio; past chapters are their hue at 50 %; the current one is a comet fill with scene ticks and a ringed head; its title sits in small caps 20 above; hidden in the intro and outro |
| **Countdown ring** | 0.3 u ring beside a question | a thin stroke that empties during a try-it pause; a graphic, not a box |
| **Chapter card** | 2 s inside the chapter's pause | small caps 48 title, a 3.2 u rule in the chapter hue, and "chapter n" in small caps 24 muted, with a 3-step staircase vignette; slow push-in 1.03 → 1.0 |

## 5. Motion
- Every layer is a pure function of audio time. Each cue lands on its beat in `beats.py` (`at=T.<scene>_<word>`), with
  motion starting 0.15 s early.
- Eases: `smooth` for writes, `easy_ease` for camera, `spring` for the stopping edge at e and the slide rule cursor,
  `out_back` only for the small chips of a solved answer.
- At most three things move at once. Worked examples build one line at a time, and earlier lines dim to 60 %.
- Transitions use continuity: the staircase becomes the table, the table becomes the ruler, the ruler becomes the
  curve, and the curve becomes the hyperbola. Cuts are reserved for the chapter cards.

## 6. Engines by chapter

| chapter | engine choices |
|---|---|
| intro | skia (Napier's page, paper fibre, printed columns) → ArrayLayer; Manim for numerals; s.camera 2.5D push; a GL Glow on the + |
| c01 | Taichi soft-body division bake (seed 1801) → PointsLayer; Manim staircase and equations |
| c02 | Manim (table, rules, digits of 2¹⁰⁰); the in_s01 skia page reused as a ghost |
| c03 | skia boxwood rulers; Manim ticks and numbers (crisp at any zoom); pyvista for the 3D slide rule pull-back; a GL glow on the cursor |
| c04 | Manim graph, plus a ThreeD flip of the curve about y = x; GL glow on the point trails |
| c05 | Manim curves and solving steps; a GLSL area fill with a glowing edge driven by a Track |
| c06 | GLSL sound rings; star field as PointsLayer; pyvista terrain ripple (180 baked frames); Manim rulers and log-log plot |
| outro | Manim staircase; chapter precomps as thumbnails |

## 7. Style frames (what each proves)

| # | scene · beat | proves |
|---|---|---|
| 01 | in_s01 · "into an addition" | a skia raster under crisp CM; the role colours on a real computation (π × e) |
| 02 | c01_s01 · "ten divisions" | a full-bleed cell colony with big counters in open space |
| 03 | c01_s02 · "logarithm" | the motif's final geometry and L2 |
| 04 | c02_s03 · "thirty one digits" | a worked example as a vertical build with a decade ruler |
| 05 | c03_s02 · "six" | L4: wooden rulers, the glowing cursor, lengths as periwinkle bars |
| 06 | c04_s01 · "swaps" | L3 on the Classic grid; the mirror pair (value / steps) |
| 07 | c05_s03 · "the number e" | the mint area and edge glow; the ln definitions in the column |
| 08 | c06_s01 · "thousand times" | a shader-like raster with a shade under the column; ×10 brackets in base |
| 09 | c06_s03 · "three for two" | the log-log plot with real planets and the fitted line |
| 10 | out_s01 · "galaxies" | the recap staircase, one hue per chapter |
