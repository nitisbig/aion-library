# 002: The Hessian Matrix, Explained Visually

**Mode:** production · **Status:** phase 3 ✅ timed scene plan **approved** (2026-11-05: end exactly on the audio, pure black background). Phase 4: building.

**Pipeline**
1. ✅ Scene plan and `voiceover.md`.
2. ✅ Audio and subtitles in `assets/`: `audio.mp3`, `cue-per-word.srt`, `normal-subtitle.srt`.
3. ✅ **This file:** chapters chunked into 26 scenes, every beat timed from the SRT.
4. ⏳ Build the library pieces and a lab test of `SurfacePlate`, then the scenes; preview, verify, render the finals.

## Timing facts from the audio

- `audio.mp3` is **604.560 s (10:04.56)**, 48 kHz, 320 kb/s. `cue-per-word.srt` has **1,752 word cues** and follows `voiceover.md` word for word, apart from the spellings below. The last cue ("watching.") is stretched to 605.32 by the aligner; the voice actually ends at **604.16**.
- **Every `t` below comes from `beats.py`**, which looks each cue key up with `Cue.at()` and fails if a key is missing, out of order, or outside its scene. If the audio is ever regenerated, rerun it: `uv run python videos/002-hessian-matrix/beats.py`. Scenes will use the same keys through `self.t("...")`, so no time is typed in by hand anywhere.
- **The SRT has no gaps between words**: each word's end absorbs the pause after it, so pauses come from `ffmpeg silencedetect` on the audio. Breaths are short: mostly 0.3–0.5 s, the longest 0.65 s (55.14, before Ch1). Every scene cut sits on a frame boundary at the middle of one of these real pauses.
- **Anchor on word starts.** Animation start = word start − `LEAD` (0.15 s) unless the Anim column says otherwise.
- **SRT spellings the cue keys must use** (matching ignores case and punctuation): "**Why** equals x squared" (for "Y"), "Otto **Hess**", "**Zooming** close", "helps **computer** search", "**It's** bending", "x-axis" (key `xaxis`), and digits for **45**, **20**, **10**. Repeated words are disambiguated with `after=`.
- **Ch4 sweep keyframes.** Bending is `2 + 3 sin 2θ`, so the readout hits each spoken number when θ passes 9.74° ("three"), 20.91° ("four"), 45° ("five"), 90° ("two"), 110.91° ("zero") and 135° ("minus one"). θ(t) is a monotone PCHIP through those keyframes, so the number on screen is always the true bending at the plane's real angle.
- **The video ends exactly on the audio** (user decision): 36,273 frames = 604.550 s. "Thanks for watching" ends at 604.16, so the final fade runs 603.95 → 604.55.

## Chapters (real timings)

| Part | Title | Scenes | Range | Length |
|---|---|---|---|---|
| Intro | The foggy hill | 01–02 | 0:00.00 – 0:55.47 | 55.5 s |
| Ch1 | Bending on a line | 03–05 | 0:55.47 – 2:12.37 | 76.9 s |
| Ch2 | Slopes on a surface | 06–08 | 2:12.37 – 3:20.02 | 67.7 s |
| Ch3 | Four numbers in a grid | 09–12 | 3:20.02 – 5:03.70 | 103.7 s |
| Ch4 | Bending in every direction ★ | 13–16 | 5:03.70 – 6:32.97 | 89.3 s |
| Ch5 | Peak, valley, or saddle | 17–20 | 6:32.97 – 8:00.42 | 87.5 s |
| Ch6 | Why it matters | 21–24 | 8:00.42 – 9:19.57 | 79.2 s |
| Outro | Recap and return to the fog | 25–26 | 9:19.57 – 10:04.55 | 45.0 s |

## The idea of the video, in one line

**A Hessian is a bending meter.** Feed it a direction and it returns how much the ground smiles or frowns that way. Everything in the video (the four entries, symmetry, eigenvectors, the classification, Newton's method) is shown as a consequence of that one picture. The **puzzle surface** `f = x² + 3xy + y²` (Hessian `[[2,3],[3,2]]`, eigenvalues 5 and −1) is planted in the intro, built in Ch3, solved in Ch4, confirmed in Ch5, and is the payoff that keeps viewers watching.

## Verified math (sympy, 2026-11-05)

| Object | Fact used on screen |
|---|---|
| `x²`, `−x²`, `cos x` at 0, `x³` at 0 | f'' = 2, −2, −1, 0 · cos x ≈ 1 − x²/2 |
| bowl `x²+y²` / dome `−x²−y²` / saddle `x²−y²` | H = diag(2,2) / diag(−2,−2) / diag(2,−2) |
| twist `xy` | H = [[0,1],[1,0]], eigenvalues ±1 |
| **puzzle** `x²+3xy+y²` | H = [[2,3],[3,2]] · bending(θ) = uᵀHu = **2 + 3 sin 2θ** · max 5 at 45° along (1,1), min −1 at 135° along (1,−1), zero at θ ≈ 110.9° · det = 4 − 9 = −5 |
| rotated 45° | f = (5/2)u² − (1/2)v², so H → diag(5, −1) |
| landscape `x³ − 3x + y²` | critical points (1,0): H = diag(6,2), det 12, f = −2 (valley) · (−1,0): H = diag(−6,2), det −12, f = 2 (saddle) |
| `x⁴+y⁴`, monkey `x³−3xy²` | H = 0 at the origin for both (the test can't decide) |
| valley `x²+10y²` | H = diag(2,20), condition number 10 · Newton from (3,1) lands on (0,0) in one step |

All curves, arrows, paths and numbers on screen get computed from these (numpy), never drawn by eye.

## Color semantics (whole video)

New constants go in `aion/style.py`. Each object keeps its color for the whole video.

| Meaning | Constant | Color | Why |
|---|---|---|---|
| x direction, x slice, `∂f/∂x`, `f_xx` | `HX` (= `J_HAT`) | `#FC6255` red | x is red, y is green, matching 3D-tool convention |
| y direction, y slice, `∂f/∂y`, `f_yy` | `HY` (= `I_HAT`) | `#83C167` green | |
| Twist, `f_xy`, `f_yx` | `TWIST` (= `I_UNIT`) | `#B48EF0` violet | the "new" kind of number |
| Slope, gradient arrow, the walker dot | `GRAD` (= `VEC`) | `#F4D35E` yellow | |
| **Bending up**: smile, positive eigenvalue, valley | `SMILE` (= `ACCENT`) | `#58C4DD` blue | the same "positive" blue as video 001 |
| **Bending down**: frown, negative eigenvalue, peak | `FROWN` (= `NEG`) | `#F2A65A` orange | the same "negative" orange as video 001 |
| Direction arrow **u** | `TEXT` | `#ECEFF4` | neutral, so its result carries the color |
| Surface body | `SURF_LO` → `SURF_HI` | `#1B2433` → `#4C5D75` slate | stays neutral so the semantic colors pop |
| Fog | `FOG` | `#2B3442` | |

Equations are always color-coded the same way, e.g. `x²` red, `3xy` violet, `y²` green; `5` blue and `−1` orange.
**Background: pure black `#000000`** (user decision, as in 001), set once in `scenes/shared.py`. The fog colour fades to black with distance, so the horizon melts into the frame edge.

## Engines

| Engine | Role here |
|---|---|
| **moderngl** | **All 3D surfaces.** Manim's Cairo `ThreeDScene` would take hours per minute of 3D on 2 CPU cores, while a mesh on the Radeon R4 renders in milliseconds. A new `SurfacePlate` component (see below) renders `z = f(x,y)` inside Manim every frame, the way `ShaderPlate` did in 001. It also does fog, contour lines, curvature tint, slice planes, the tangent disc, and the procedural "trillion-cell" matrix zoom. |
| **Manim CE** | Every 2D graph, equation, matrix, the direction dial, the sign chart, the contour-map paths, and every label. Labels pinned to 3D points use `SurfacePlate.project(x,y,z)`, which shares the GL camera, so the 2D overlay stays locked to the 3D render. That's the 2.5D layer. |
| **skia-python** | Glow halos (`components/glow.py`), recap cards (`components/cards.py`), the chapter-title typography plate, and a static vignette and film-grain overlay applied to every scene. |
| **ffmpeg** | Concatenating the scenes and muxing the audio, as in 001's `build.sh`. |
| pyvista | Considered and **not used**. Its value is meshing and VTK pipelines, but we need per-frame uniform-driven morphs and pixel-locked Manim overlays, which `SurfacePlate` gives directly. |

### New library pieces (built before scenes, in `aion/components/`)
- **`surface_gl.py` → `SurfacePlate`**: a moderngl mesh of `z = f(x,y)`. Heights come from **`H` uniforms**: `f = ½·[x y]·H·[x y]ᵀ` with `H = (a, b, c)` driven by ValueTrackers, so **morphing bowl → dome → saddle is just tweening the matrix the viewer sees.** Custom GLSL height functions cover the non-quadratic landscapes. The camera (yaw, pitch, distance, fov) is driven by ValueTrackers. It has toggles for contours, curvature tint (blue/orange by local sign), exponential height fog with drifting noise, up to 3 slice planes with their intersection curves drawn as depth-tested GL ribbons, and a tangent disc. `project()` maps 3D points to Manim coordinates.
- **`bend_gauge.py` → `BendGauge(k)`**: the recurring "bending meter", a short arc that smiles (blue) or frowns (orange) with curvature proportional to `k`, flattening to a grey line at 0, with a number readout. It appears in every chapter, so the viewer learns one icon.
- **`matrix_grid.py` → `HessianGrid`**: a 2×2 grid built from four rounded cells (not just a LaTeX `bmatrix`), so cells can light up, swap, and be filled one at a time. It can morph into a proper `MathTex` matrix.
- Lab prerequisite: `lab/2026-11-xx-surface-plate/` to check `SurfacePlate` speed at 480p and 1080p on the R4 and the look of the fog and ribbons, **before** production scenes. This is the biggest technical risk.

## Recurring motifs (continuity)

- **The walker**: a small yellow glowing dot standing on the surface. It's "you" from the first line.
- **The tangent disc**: a flat translucent disc under the walker at a critical point. It looks identical on a bowl, dome and saddle, which is the whole problem.
- **The bend gauge**: blue smile or orange frown, always the same icon.
- **The rolling ball**: dropped on the puzzle surface in the intro, it rolls away along the northwest diagonal (unexplained). In Ch4 the same shot comes back with the eigen-axes drawn, and now the viewer sees *why*.
- **The 2×2 grid**: born in Ch3 as a "slopes × directions" table, it becomes the matrix, then diag(5, −1), then the cells in the Ch6 trillion zoom.

---

## Scene slices (60 fps, each cut on a frame inside a real silence)

| # | Part | File · class | Range (s) | Frames | Length | Cut silence |
|---|---|---|---|---|---|---|
| 01 | INTRO | `scene_01_fog.py` · `Scene01Fog` | 0.000 – 28.167 | 0 – 1690 | 28.2 s | 27.98–28.36 |
| 02 | INTRO | `scene_02_puzzle.py` · `Scene02Puzzle` | 28.167 – 55.467 | 1690 – 3328 | 27.3 s | 55.14–55.79 |
| 03 | CH1 | `scene_03_slope.py` · `Scene03Slope` | 55.467 – 80.017 | 3328 – 4801 | 24.5 s | 79.88–80.16 |
| 04 | CH1 | `scene_04_smile.py` · `Scene04Smile` | 80.017 – 107.450 | 4801 – 6447 | 27.4 s | 107.30–107.60 |
| 05 | CH1 | `scene_05_test.py` · `Scene05Test` | 107.450 – 132.367 | 6447 – 7942 | 24.9 s | 132.07–132.67 |
| 06 | CH2 | `scene_06_slices.py` · `Scene06Slices` | 132.367 – 158.750 | 7942 – 9525 | 26.4 s | 158.60–158.89 |
| 07 | CH2 | `scene_07_gradient.py` · `Scene07Gradient` | 158.750 – 178.783 | 9525 – 10727 | 20.0 s | 178.60–178.96 |
| 08 | CH2 | `scene_08_three.py` · `Scene08Three` | 178.783 – 200.017 | 10727 – 12001 | 21.2 s | 199.89–200.14 |
| 09 | CH3 | `scene_09_four.py` · `Scene09Four` | 200.017 – 226.717 | 12001 – 13603 | 26.7 s | 226.55–226.89 |
| 10 | CH3 | `scene_10_twist.py` · `Scene10Twist` | 226.717 – 257.833 | 13603 – 15470 | 31.1 s | 257.62–258.06 |
| 11 | CH3 | `scene_11_matrix.py` · `Scene11Matrix` | 257.833 – 286.867 | 15470 – 17212 | 29.0 s | 286.69–287.03 |
| 12 | CH3 | `scene_12_build.py` · `Scene12Build` | 286.867 – 303.700 | 17212 – 18222 | 16.8 s | 303.53–303.88 |
| 13 | CH4 | `scene_13_direction.py` · `Scene13Direction` | 303.700 – 325.717 | 18222 – 19543 | 22.0 s | 325.48–325.96 |
| 14 | CH4 | `scene_14_sweep.py` · `Scene14Sweep` | 325.717 – 354.267 | 19543 – 21256 | 28.6 s | 354.06–354.49 |
| 15 | CH4 | `scene_15_eigen.py` · `Scene15Eigen` | 354.267 – 374.900 | 21256 – 22494 | 20.6 s | 374.66–375.14 |
| 16 | CH4 | `scene_16_diagonal.py` · `Scene16Diagonal` | 374.900 – 392.967 | 22494 – 23578 | 18.1 s | 392.78–393.16 |
| 17 | CH5 | `scene_17_signs.py` · `Scene17Signs` | 392.967 – 413.117 | 23578 – 24787 | 20.2 s | 412.90–413.34 |
| 18 | CH5 | `scene_18_det.py` · `Scene18Det` | 413.117 – 439.267 | 24787 – 26356 | 26.1 s | 438.99–439.55 |
| 19 | CH5 | `scene_19_landscape.py` · `Scene19Landscape` | 439.267 – 463.133 | 26356 – 27788 | 23.9 s | 462.93–463.33 |
| 20 | CH5 | `scene_20_flat.py` · `Scene20Flat` | 463.133 – 480.417 | 27788 – 28825 | 17.3 s | 480.15–480.68 |
| 21 | CH6 | `scene_21_error.py` · `Scene21Error` | 480.417 – 496.817 | 28825 – 29809 | 16.4 s | 496.73–496.90 |
| 22 | CH6 | `scene_22_descent.py` · `Scene22Descent` | 496.817 – 520.917 | 29809 – 31255 | 24.1 s | 520.71–521.11 |
| 23 | CH6 | `scene_23_newton.py` · `Scene23Newton` | 520.917 – 542.250 | 31255 – 32535 | 21.3 s | 542.02–542.48 |
| 24 | CH6 | `scene_24_saddles.py` · `Scene24Saddles` | 542.250 – 559.567 | 32535 – 33574 | 17.3 s | 559.27–559.85 |
| 25 | OUTRO | `scene_25_recap.py` · `Scene25Recap` | 559.567 – 594.933 | 33574 – 35696 | 35.4 s | 594.75–595.13 |
| 26 | OUTRO | `scene_26_fog.py` · `Scene26Fog` | 594.933 – 604.550 | 35696 – 36273 | 9.6 s | — (end of audio) |

Total: **36273 frames = 604.550 s** (audio 604.560 s; the last 10 ms of silence are trimmed so the video is never longer than the audio).

---

### Chapter 0 redesign (2026-11-05) · the luminous mountain

**Look (Aion YouTube design system, FacelessChamp convolution video as reference):** pure black stage; light comes only from thin geometry. The walker's ground is crisp silver line work (contours every 0.12, every 4th brighter, a wire grid that belongs to the walker's ground), and the range around it is moonlit point-cloud dust (the moon-lake look). Two-level bloom, vignette 0.5, grain 0.04. **No on-screen text except the title.** The old "?" and "slope = 0" labels are gone; a sonar ping and a gold disc carry those beats instead.

**Engine:** new `aion/components/terrain_gl.py` → `TerrainPlate` (moderngl; ~22 ms/frame at 480p on the R4) + Manim overlays (walker, probes, gauges, grid) + `aion/components/title.py` → `TitlePlate` (skia, Space Grotesk from `aion/assets/fonts`, `light` sweep). Height = windowed ½·pᵀHp patch + ridged-fBm range that is exactly 0 within r < 3, so `project()` stays exact for every overlay. The camera stands in an open valley on the −x side looking east: **ahead = +x, sideways = ±y**.

### SCENE 01 · INTRO: The foggy mountain · 0.000–28.167 (0:00.00–0:28.17)

| t | Shot | Cue key | What happens | Anim |
|---|---|---|---|---|
| 0.00 | I-1 | (frame 0) | From black, the range **draws itself on outward from the walker** (reveal front) while the camera **descends from the sky** (dist 15, pitch 26°) to stand beside the walker (dist 6.2, pitch 10°). The gold walker fades in on "hill". | one 4.3 s move to `perfectly flat`, parts on their own windows; slow 0.3°/s orbit under the whole intro |
| 1.82 | I-1 | `thick` | **The fog rolls in** (height fog: valleys vanish first, ghost peaks last). The world shrinks to the walker's small circle: the viewer is now as blind as the walker | window inside the move, ≈1.7–4.0 |
| 4.45 | I-2 | `perfectly flat` | The tangent disc opens under the walker: a thin silver ring | rt 0.7 |
| 5.64 | I-2 | `no slope` | Four gold probe arrows (E, N, W, S) grow and retract: nowhere to go | `LaggedStart`, rt 1.4 |
| 8.03 | I-2 | `where are you` | A **sonar ping** leaves the walker and dies in the fog (replaces the "?") | rt 1.8 |
| 10.34 | I-3 | `top of the hill` | Fog thins; the ground under the still disc becomes a **summit** | H tween rt 0.9 |
| 12.02 | I-3 | `bottom of a valley` | → a **basin** | rt 0.9 |
| 15.44 | I-3 | `mountain pass` | → a **pass**; fog lifts further and the range reappears behind it | rt 0.9 |
| 17.35 | I-3 | `rises ahead` | The forward (east) slice glows **blue** | rt 0.6 |
| 18.61 | I-3 | `falls away` | The sideways (north) slice glows **orange** | rt 0.6 |
| 21.16 | I-4 | `cant tell you` | Push in, fog closes, contours off: only the flat grid around the disc is left. Dome and bowl flash underneath and look the same | push rt 1.4, then 0.6 + 0.6 |
| 23.98 | I-4 | `zero` | The disc ring turns **gold** (gold = slope): the slope is zero (replaces the "slope = 0" label) | rt 0.6 |
| 26.95 | I-5 | `how the ground bends` | Pull back; fog lifts; the contours return and the **bend tint** washes in: blue where the pass rises, orange where it falls | rt 1.2 (ends 28.0) |

### SCENE 02 · INTRO: The puzzle and the promise · 28.167–55.467 (0:28.17–0:55.47)

| t | Shot | Cue key | What happens | Anim |
|---|---|---|---|---|
| 28.61 | I-6 | `heres a puzzle` | **No cut:** a fog bank swells, the range sinks away, the ground under the walker morphs into the puzzle surface `x² + 3xy + y²` and the camera swings to its view. A luminous plate alone on black, tint off so it looks innocent | rt 1.8 |
| 32.07 | I-6 | `east` | The red x-slice lights up on the surface, with a blue smile gauge | rt 0.8 |
| 34.50 | I-6 | `north` | The green y-slice + a second blue smile | rt 0.8 |
| 36.20 | I-7 | `middle` | Slices dim to 30% | rt 0.4 |
| 36.70 | I-7 | `not a valley` | The walker **rolls off along the north-west diagonal**, leaving a gold trail, and fades at the rim. Unexplained on purpose | rt 2.2 `rush_into` |
| 39.60 | I-8 | `small grid` | The surface recedes to 16%; four **glass cells** assemble | rt 0.6 |
| 40.16 | I-8 | `four numbers` | The cells pulse once in reading order | lag 0.12, rt 0.8 |
| 42.19 | I-8 | `hessian matrix` | Cells fill with `f_xx` (red), `f_xy`/`f_yx` (violet), `f_yy` (green). **"The Hessian Matrix"** sets beneath in Space Grotesk with a soft glow, then a warm `light` sweep crosses it | fill rt 0.8, sweep rt 1.1 |
| 44.85 | I-9a | `build it from nothing` | The grid empties and refills cell by cell | rt 0.4 + 0.8 |
| 46.12 | I-9b | `what each number means` | Direction dial (hairline ring) sweeps; its bending curve `2 + 3 sin 2θ` traces blue above zero, orange below | rt 3.9 |
| 51.13 | I-9c | `millions of dimensions` | Hairline contour ellipses, the gold gradient-descent zigzag, then one blue Newton arc to the centre | rt 1.3 + 0.7 |
| 54.28 | I-10 | `idea of a slope` | Everything collapses to **one gold tangent line** on a short arc: the hand-off to Ch1 (unchanged) | rt 1.0 |

### Chapter 1 restyle (2026-11-05) · luminous line work

Same beats and timings as below; only the look changed, to match chapter 0. Axes are muted **hairlines** (`V.hairline`, no numbers). Curves are **silver** (`TERRAIN_LINE`) with a soft halo (`V.lit`, a wide low-opacity background stroke), so the colour stays reserved for meaning: gold = slope (tangent, `f'(x₀)` readout, "slope" axis tag), blue/orange = bending. Labels use Inter via `V.label` (the "bending" tag is muted). The old "?" in scene 04 is replaced by two expanding gold pings. Scene 05's test card is a design-system **glass card** (`GLASS_TOP`→`GLASS_BOTTOM`, `LINE` rim) under an uppercase eyebrow, "SECOND DERIVATIVE TEST". The 02→03 cut is seamless: scene 03 starts on the `handoff_tangent` frame (mean pixel difference 0.04).

### SCENE 03 · CH1: Slope, and the slope of the slope · 55.467–80.017 (0:55.47–1:20.02)

**Engine:** Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 56.75 | 1-1 | `single curve` | Axes (−3..3) fade up under the tangent line from the intro | rt 0.8 |
| 57.72 | 1-1 | `why equals x squared` | The parabola draws through the tangent point; `y = x²` lands top-left. (The SRT writes “Why” for “Y”.) | `Create` rt 1.2, label `Write` rt 0.8 |
| 59.64 | 1-2 | `every point` | The tangent line starts to **ride the curve** (ValueTracker `x₀`) | rt 1.2 |
| 62.02 | 1-2 | `first derivative` | Live readout `slope = f′(x₀) = 2x₀` in yellow | rt 0.6 |
| 63.53 | 1-3 | `left` | Tangent slides to x₀ = −1.5; readout −3 | rt 0.9 `smooth` |
| 64.56 | 1-3 | `negative` | The readout's minus sign glows | `Indicate` rt 0.5 |
| 65.53 | 1-3 | `right` | Tangent slides to x₀ = +1.5; readout +3 | rt 1.0 |
| 67.65 | 1-3 | `bottom` | Tangent settles at the vertex | rt 0.8 |
| 68.55 | 1-3 | `zero` | Readout lands on **0**, the line lies flat | flash rt 0.4 |
| 69.45 | 1-4 | `watch the slope itself` | The frame splits: the parabola rises to the top half, new axes labeled “slope” draw in the bottom half | rt 1.0 |
| 71.20 | 1-4 | `move to the right` | The tangent sweeps x₀ = −2 → 2 again and a yellow dot **traces the slope graph `2x`**, a straight rising line | rt 3.0 `linear` sweep |
| 74.50 | 1-5 | `rate` | A rise/run triangle on the slope line: run 1, rise 2 | rt 0.8 |
| 76.41 | 1-5 | `second derivative` | `f″(x) =` writes under the slope graph | `Write` rt 0.8 |
| 79.04 | 1-5 | `two everywhere` | `= 2` lands; the triangle slides along the line and stays the same size | rt 0.5, then slide rt 0.6 (ends 80.0) |

### SCENE 04 · CH1: Smile, frown, and a flat spot · 80.017–107.450 (1:20.02–1:47.45)

**Engine:** Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 80.46 | 1-6 | `positive second derivative` | `f″ = 2` tints blue | rt 0.5 |
| 82.36 | 1-6 | `slope is rising` | The slope line glows yellow along its length | rt 0.8 |
| 85.55 | 1-6 | `smile` | The **BendGauge** is born: a blue smile beside `f″ = 2`; the parabola glows blue for a beat | `GrowFromCenter` rt 0.6 |
| 86.24 | 1-7 | `flip it over` | A sign tracker 1 → −1 flips the parabola to `−x²` (no cut). The slope line tilts to `−2x` | rt 1.2 `smooth` |
| 89.94 | 1-7 | `minus two` | `f″ = −2` in orange | rt 0.5 |
| 92.41 | 1-7 | `frown` | The gauge bends through flat into an **orange frown** | rt 0.7 |
| 94.52 | 1-8 | `measures bending` | The gauge pulses; a small `f″ = bending` tag | rt 0.6 |
| 97.53 | 1-8 | `flat spot` | The bottom panel slides away. A walker dot sits at the vertex on a flat yellow tangent | rt 0.8 |
| 98.69 | 1-8 | `cosine of x` | The curve morphs into `cos x` on [−2π, 2π]; the walker rides to x = 0 | `Transform` rt 1.0 |
| 100.53 | 1-8 | `its flat` | The flat tangent at x = 0 re-draws | rt 0.5 |
| 101.56 | 1-8 | `top or bottom` | A “?” at 40% over the dot | rt 0.5 |
| 104.60 | 1-9 | `minus one` | The gauge shows a −1 frown | rt 0.6 |
| 105.66 | 1-9 | `bends down` | The curve near 0 tints orange | rt 0.5 |
| 106.93 | 1-9 | `peak` | The “?” becomes an orange ring around the dot | rt 0.5 |

### SCENE 05 · CH1: Every curve is a parabola up close · 107.450–132.367 (1:47.45–2:12.37)

**Engine:** Manim (MovingCamera) + skia card

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 107.84 | 1-10 | `zooming close` | MovingCamera zooms to x = 0 (frame width 14 → 3). (SRT says “Zooming close”) | rt 1.8 `smooth` |
| 110.81 | 1-10 | `parabola` | A dashed orange parabola `1 − x²/2` draws and **hugs the cosine** | `Create` rt 1.0 |
| 114.46 | 1-10 | `one` | `cos x ≈ 1` writes top-left | rt 0.25 |
| 114.72 | 1-10 | `minus x squared over two` | `− x²/2` appends in orange | rt 0.8 |
| 118.12 | 1-10 | `which way that parabola opens` | The camera eases back out. The dashed parabola's opening edges glow; a ghost blue `+x²/2` flickers once to show the other way | rt 1.2 |
| 120.77 | 1-11 | `second derivative test` | A two-row skia card slides up from the bottom | rt 0.8 |
| 122.91 | 1-11 | `bending up` | Row 1: mini smile icon | rt 0.4 |
| 124.08 | 1-11 | `valley` | Row 1 label **valley** (blue) | rt 0.4 |
| 125.40 | 1-11 | `bending down` | Row 2: mini frown icon | rt 0.4 |
| 126.62 | 1-11 | `peak` | Row 2 label **peak** (orange) | rt 0.4 |
| 127.99 | 1-12 | `bending is zero` | Row 3 appears; the main curve becomes `x³` | rt 0.8 |
| 129.32 | 1-12 | `x cubed` | Walker at 0 on the flat tangent; the gauge goes to a **flat grey line** | rt 0.6 |
| 131.76 | 1-12 | `cant tell` | Grey “?” in row 3 | rt 0.5 |

### Chapter 2 restyle (2026-11-05) · luminous surfaces

Same beats and timings as below. Every Ch2 surface uses SurfacePlate's new **luminous look** (`ch2.LUMINOUS`: `lum=1` plus the shared `aion/components/post_gl.py` finish). The body is near-black (`TERRAIN_BODY`), the wire grid and contours are silver (`TERRAIN_LINE`), and the silhouettes have a faint rim. The image gets two-level bloom, vignette 0.5 and grain 0.04. The small triptych viewports get glow only, with no vignette or grain. Slice cut curves glow in their own colour, and their translucent planes are softer, because bloom carries the light. The top-down map becomes pure luminous contours on black. Tangent discs are thin rings, as in the intro.

Overlay changes:
- **Pins:** silver hairlines.
- **Tangents and critical-point rings:** `V.lit` glow.
- **Gradient field arrows:** thinner.
- **Scene 08, "gradient is zero":** a single gold `∇f = 0` at the top (it replaces three copies), and the three discs **turn gold**, the same motif as the intro's "zero" beat.
- **Scene 08, "more than one":** the "how many?" text is gone. Four faint hairline cells in a 2×2 foreshadow the Hessian grid.
- **Hand-off from scene 05:** scene 06 opens on scene 05's glass test card, built by the same helpers (`ch1.test_card`, `ch1.test_row`).

### SCENE 06 · CH2: From a curve to a landscape · 132.367–158.750 (2:12.37–2:38.75)

**Engine:** Manim → moderngl (shared camera) + projected labels

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 133.26 | 1-13 | `step off the line` | The card fades. The 2D axes **tilt back in perspective** and become the red x-axis of a 3D floor. The last Manim frame is pixel-matched to the first SurfacePlate frame | tilt rt 1.6 `smooth` |
| 136.75 | 2-1 | `two inputs` | A green y-axis grows across the floor; labels x, y | rt 0.8 |
| 138.59 | 2-1 | `height` | A field of thin vertical pins rises from the floor grid (the two-hill landscape's heights) | `LaggedStart` rt 1.6 |
| 142.83 | 2-1 | `landscape` | The pins **skin into a surface** | crossfade rt 1.0 |
| 145.58 | 2-2 | `slice it` | A translucent red plane (y = const) slides in | rt 0.8 |
| 146.62 | 2-2 | `hold y fixed` | `y = const` tag pinned to the plane via `project()` | rt 0.5 |
| 148.52 | 2-2 | `x direction` | The cut curve glows red | rt 0.7 |
| 150.38 | 2-2 | `ordinary curve` | The camera swings side-on so the cut reads as a plain 2D curve | orbit rt 1.4 |
| 153.70 | 2-2 | `with respect to x` | A yellow tangent sits on the red curve; label `∂f/∂x` (red) | rt 0.7 |
| 154.92 | 2-3 | `cut along y` | Camera swings back; a green plane, its cut curve, tangent and `∂f/∂y` (green) | rt 1.2 |

### SCENE 07 · CH2: The gradient arrow · 158.750–178.783 (2:38.75–2:58.78)

**Engine:** moderngl + Manim (projected arrows)

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 159.40 | 2-4 | `two slopes together` | The two tangent slopes drop to the floor as red and green component arrows | rt 1.0 |
| 161.17 | 2-4 | `arrow on the floor` | They add tip-to-tail into the **yellow gradient arrow** | rt 0.8 |
| 162.92 | 2-4 | `gradient` | Label `∇f` (yellow) | rt 0.5 |
| 164.24 | 2-4 | `straight uphill` | A faint dashed line from the arrow runs up the surface | rt 0.7 |
| 166.32 | 2-4 | `how steep` | A bracket along the arrow's length | rt 0.5 |
| 167.36 | 2-5 | `walk around` | Camera rises to top-down while the surface shades into a **contour map**. The walker moves on a path; its arrow updates live | camera rt 2.0, walk to scene end |
| 169.85 | 2-5 | `steep side` | Walker crosses the steep flank: the arrow is long | — |
| 171.48 | 2-5 | `near the top` | Walker climbs: the arrow shrinks | — |
| 175.36 | 2-5 | `vanishes` | A grid of true-∇f arrows fades in staggered; near the peaks they vanish | `LaggedStart` rt 1.2 |
| 177.79 | 2-6 | `critical points` | White pulse rings at the three critical points (two peaks and the saddle between, found numerically) | rt 0.8 |

### SCENE 08 · CH2: Bowl, dome, saddle · 178.783–200.017 (2:58.78–3:20.02)

**Engine:** moderngl triptych + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 179.66 | 2-7 | `three surfaces` | The map dissolves into a **triptych**: three viewports, one GL pass, slowly co-rotating | rt 1.0 |
| 180.88 | 2-7 | `bowl` | Left lands: bowl | rise rt 0.6 |
| 181.75 | 2-7 | `dome` | Middle lands: dome | rt 0.6 |
| 182.88 | 2-7 | `saddle` | Right lands: saddle | rt 0.6 |
| 185.36 | 2-8 | `center of each one` | Tangent discs and walkers appear at all three centers | `LaggedStart` rt 0.8 |
| 186.82 | 2-8 | `gradient is zero` | One gold `∇f = 0` above the triptych; all three discs turn gold | rt 0.6 |
| 188.99 | 2-8 | `valley` | **valley** (blue) under the bowl | rt 0.4 |
| 190.59 | 2-8 | `peak` | **peak** (orange) under the dome | rt 0.4 |
| 191.97 | 2-8 | `neither` | **neither** (blue/orange) under the saddle | rt 0.4 |
| 193.01 | 2-9 | `low one way` | The saddle grows to fill the frame. Blue smile gauge on its x-slice | zoom rt 1.2, gauge rt 0.5 |
| 194.08 | 2-9 | `high the other` | Orange frown gauge on its y-slice | rt 0.5 |
| 196.68 | 2-10 | `second derivatives again` | The two gauges lift off the surface and hover | rt 0.8 |
| 199.48 | 2-10 | `more than one` | Four faint hairline cells in a 2×2 (foreshadowing the grid); no text | rt 0.5 |

### Chapter 3 restyle (2026-11-05) · glass cells, luminous surfaces

Same beats and timings as below.
- **Cells:** the table and the matrix are design-system **glass cells** (`ch3.glass`): a `STAGE_RAISED` body with a silver hairline rim. The "lit" empty cells are `GLASS_TOP` with a brighter rim. Entry colours are carried by the rim; the fill is only a quiet wash at 40% of the old strength (`HessianGrid(tint_scale=…)`).
- **Surfaces:** the saddle inset (09), the twist surface `z = xy` (10) and the puzzle flashback (12) use the luminous SurfacePlate look. The puzzle flashback also gets faint contours, to echo the intro. The rulings on `z = xy` are silver until highlighted.
- **Hesse caption (11):** a glass card.

### SCENE 09 · CH3: Four second derivatives · 200.017–226.717 (3:20.02–3:46.72)

**Engine:** Manim + moderngl inset

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 200.79 | 3-1 | `two slopes` | Clean 2D frame. Row labels appear: `∂f/∂x` | rt 0.6 |
| 202.06 | 3-1 | `slope in x` | `∂f/∂x` (red) pulses | rt 0.4 |
| 203.48 | 3-1 | `slope in y` | `∂f/∂y` (green) appears | rt 0.5 |
| 206.18 | 3-1 | `two ways` | Column headers slide in | rt 0.6 |
| 207.35 | 3-1 | `move in x` | Header “move in x” | rt 0.4 |
| 208.92 | 3-1 | `move in y` | Header “move in y” | rt 0.4 |
| 211.96 | 3-1 | `four second derivatives` | The four empty cells light up in a stagger | lag 0.12, rt 0.8 |
| 215.19 | 3-2 | `as you move in x` | Top-left cell highlights | rt 0.4 |
| 217.11 | 3-2 | `bending of the x slice` | Inset (moderngl): the surface with a red slice and a blue smile gauge, the same picture as Ch1 | inset rt 0.8 |
| 220.04 | 3-2 | `f x x` | Top-left fills with red `f_xx` | rt 0.6 |
| 221.28 | 3-3 | `y slope changes` | Bottom-right cell highlights | rt 0.4 |
| 224.72 | 3-3 | `y slice` | Inset swaps to a green slice | rt 0.6 |
| 225.40 | 3-3 | `f y y` | Bottom-right fills with green `f_yy` | rt 0.6 |

### SCENE 10 · CH3: The twist · 226.717–257.833 (3:46.72–4:17.83)

**Engine:** moderngl (`xy` surface, GL line rulings) + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 227.03 | 3-4 | `other two` | The two empty off-diagonal cells glow faint violet | rt 0.6 |
| 228.96 | 3-4 | `picture yourself` | Full-frame moderngl: the `xy` surface; the grid shrinks to the top-right corner | rt 1.0 |
| 230.78 | 3-4 | `facing east` | Walker at the origin with a red “facing east” tangent arrow | rt 0.6 |
| 232.22 | 3-4 | `step to the side` | The walker steps north (y: 0 → 0.6) | rt 1.0 `smooth` |
| 236.14 | 3-4 | `steeper or flatter` | The east arrow **tilts upward**; a ghost of the old flat arrow stays | rt 0.8 |
| 238.13 | 3-5 | `f x y` | Top-right cell fills violet `f_xy` | rt 0.6 |
| 239.90 | 3-5 | `twist` | A small violet **twist ribbon** icon (the gauge for twist) | rt 0.6 |
| 241.57 | 3-6 | `z equals x times y` | `z = xy` writes | rt 0.8 |
| 243.66 | 3-6 | `perfectly` | The surface fades to its **straight-line rulings**: every east-facing line is exactly straight with slope y | rt 1.0 |
| 245.10 | 3-6 | `xaxis` | The ruling on y = 0 highlights: flat | rt 0.5 |
| 246.78 | 3-6 | `step north` | Rulings with y > 0 highlight, tilted up | rt 0.6 |
| 250.08 | 3-6 | `step south` | Rulings with y < 0 highlight, tilted down | rt 0.6 |
| 252.57 | 3-7 | `bending in x is zero` | Readout 1: flat grey gauge, `f_xx = 0` | rt 0.5 |
| 254.53 | 3-7 | `bending in y is zero` | Readout 2: flat grey gauge, `f_yy = 0` | rt 0.5 |
| 256.73 | 3-7 | `twist is one` | Readout 3: violet ribbon, `f_xy = 1` | rt 0.5 |

### SCENE 11 · CH3: The Hessian, and its mirror · 257.833–286.867 (4:17.83–4:46.87)

**Engine:** Manim + skia caption

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 258.06 | 3-8 | `the last one` | Back to the centered grid; bottom-left highlights | rt 0.8 |
| 259.03 | 3-8 | `f y x` | Bottom-left fills violet `f_yx` | rt 0.6 |
| 261.35 | 3-8 | `other way around` | Two tiny arrows show the order swap (move in y, then in x) | rt 0.8 |
| 264.19 | 3-8 | `always matches` | The two violet cells pulse together; `∂²f/∂y∂x = ∂²f/∂x∂y` holds below | rt 0.8 |
| 267.60 | 3-8 | `both sides` | Hold (equation stays) | — |
| 268.76 | 3-9 | `arrange all four` | Row/column labels fade; the cells tighten | rt 1.0 |
| 272.28 | 3-9 | `top left` | `f_xx` pulses | rt 0.4 |
| 274.01 | 3-9 | `bottom right` | `f_yy` pulses | rt 0.4 |
| 275.86 | 3-9 | `other two corners` | Both violet cells pulse | rt 0.4 |
| 277.71 | 3-9 | `hessian matrix` | Brackets grow; `H =` writes to the left | rt 0.8 |
| 280.76 | 3-10 | `otto hess` | Caption “Ludwig Otto Hesse · 1811–1874” (skia). (SRT says “Hess”) | fade rt 0.6, out at 283 |
| 283.98 | 3-10 | `symmetric` | A thin diagonal line sweeps corner to corner | rt 0.8 |
| 284.90 | 3-10 | `mirror image` | The two violet cells reflect onto each other across it | rt 1.0 |

### SCENE 12 · CH3: Building the puzzle Hessian · 286.867–303.700 (4:46.87–5:03.70)

**Engine:** Manim (+ moderngl flashback)

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 287.09 | 3-11 | `lets build one` | The symbols shrink to small corner tags; the cells are empty again | rt 0.6 |
| 288.84 | 3-11 | `x squared` | `f = x²` (red) | `Write` rt 0.6 |
| 290.02 | 3-11 | `three x y` | `+ 3xy` (violet) | rt 0.6 |
| 291.17 | 3-11 | `y squared` | `+ y²` (green) | rt 0.6 |
| 292.45 | 3-12 | `bending in x is two` | Worked line `f_x = 2x + 3y → f_xx = 2`; the **2** flies into the top-left | `TransformMatchingTex` rt 1.0 |
| 294.21 | 3-12 | `bending in y is two` | `f_y = 3x + 2y → f_yy = 2`; **2** into bottom-right | rt 1.0 |
| 296.05 | 3-12 | `twist is three` | `f_xy = 3`; **3** splits into both violet cells | rt 1.0 |
| 297.36 | 3-13 | `so the hessian is` | The worked lines clear; the matrix centers | rt 0.6 |
| 298.76 | 3-13 | `two three three two` | Each entry pulses on its word: 2 · 3 · 3 · 2 | per word, rt 0.3 |
| 300.80 | 3-13 | `hold on to that one` | Soft skia glow on `[[2,3],[3,2]]` | rt 0.8 |
| 302.23 | 3-14 | `puzzle surface` | Flashback: the intro's puzzle surface fades in beside it, the ball rolling away (desaturated) | rt 1.0 |

### Chapter 4 build (2026-11-05) · luminous from the start

Built straight in the design-system look; the builders are in `scenes/ch4.py`, and the math asserts there cover the bending at every keyframe angle and both eigenpairs. Changes from the plan below:
- **Scene 13:** the worked example writes out the multiplication in full: `[2 3; 3 2][1; 0] = [2; 3]`, then `[1 0][2; 3] = 2`. On the map, the shadow of Hu on u is exactly 2u.
- **Scene 14:** θ(t) is a monotone cubic through the narration keyframes, so it holds still at 45°. The readout has one decimal. The compass gets NE and NW tags.
- **Scene 15:** the frown line is where the sweep stopped. The eigen-pairs appear in a small legend with uppercase eyebrows, not as labels on the map.
- **Scene 16:** the grid and the view turn together, so v₁ points up. The diagonal glows warm (`LIGHT`).
- **Chapter end:** holds on the Taylor patch and the parabola inset, with no fade-out, for chapter 5.

### SCENE 13 · CH4: Bending in any direction · 303.700–325.717 (5:03.70–5:25.72)

**Engine:** moderngl (top-down contours) + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 305.28 | 4-1 | `any direction` | Top-down puzzle surface as hyperbolic contours. A white unit arrow **u** appears at the center and turns slowly | rt 0.8, slow spin |
| 306.79 | 4-1 | `east or north` | u touches east, then north | rt 1.2 |
| 309.10 | 4-1 | `in between` | u settles at 30° | rt 0.8 |
| 310.48 | 4-2 | `beautiful part` | Left panel opens; `H` (colored) sits in it | rt 0.8 |
| 312.70 | 4-2 | `new derivatives` | H pulses: nothing new needed | rt 0.5 |
| 314.10 | 4-2 | `pick a direction` | u swings back to east (θ = 0) for the worked example | rt 0.8 |
| 316.18 | 4-2 | `length one` | Unit circle draws; `|u| = 1` | rt 0.6 |
| 317.08 | 4-2 | `multiply the hessian` | `H u = [2, 3]` (first column) and a faint arrow Hu on the map | rt 0.8 |
| 320.19 | 4-2 | `dot product` | Hu's shadow drops onto u; `uᵀ(Hu) = 2` | rt 0.8 |
| 322.83 | 4-2 | `number that comes out` | The **2** pops with a blue smile gauge | rt 0.5 |
| 324.56 | 4-2 | `in that direction` | `bending(u) = uᵀHu` boxed | rt 0.6 |

### SCENE 14 · CH4: The sweep ★ · 325.717–354.267 (5:25.72–5:54.27)

**Engine:** moderngl (slice plane at θ) + Manim live graph

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 326.29 | 4-3 | `watch it on the puzzle surface` | **Main layout**: left, the 3D puzzle surface with a vertical slice plane at θ through the center (cut curve tinted by sign); right, axes for bending vs θ (0°–180°); gauge + readout under the 3D view | rt 1.2 |
| 328.00 | 4-3 | `facing east` | θ = 0: plane faces east; graph dot at (0°, 2) | rt 0.5 |
| 329.96 | 4-3 | `two` | Readout **2** | rt 0.3 |
| 330.60 | 4-3 | `smile` | Gauge: blue smile | rt 0.4 |
| 331.96 | 4-4 | `slowly turn` | θ starts to move; the graph traces live | θ keyframes ↓ |
| 334.00 | 4-4 | `northeast` | Compass tag “NE” at 45° on the dial | rt 0.4 |
| 335.92 | 4-4 | `three` | θ = 9.74° → readout **3** | keyframe |
| 336.87 | 4-4 | `four` | θ = 20.91° → readout **4** | keyframe |
| 339.80 | 4-4 | `five` | θ = 45° → readout **5**; plane along (1,1), curve brightest blue, graph peak marked | keyframe, ease-out |
| 340.61 | 4-4 | `strongest smile` | Peak marker pulses | rt 0.5 |
| 342.78 | 4-5 | `keep turning` | θ moves on | keyframe |
| 345.44 | 4-5 | `two` | θ = 90° (north) → readout **2** | keyframe |
| 349.08 | 4-5 | `zero` | θ = 110.91° → readout **0**, gauge flat grey | keyframe |
| 349.97 | 4-5 | `past it` | Graph dips below zero; formula `2 + 3 sin 2θ` writes onto the graph | rt 0.8 |
| 351.01 | 4-5 | `northwest` | θ = 135° → plane along (1,−1) | keyframe, ease-out |
| 352.90 | 4-5 | `minus one` | Readout **−1** | rt 0.3 |
| 353.80 | 4-5 | `frown` | Gauge: orange frown | rt 0.4 |

### SCENE 15 · CH4: The frown was hiding in between · 354.267–374.900 (5:54.27–6:14.90)

**Engine:** moderngl + Manim (projected axes)

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 355.37 | 4-6 | `smiles along one diagonal` | Blue line drawn on the surface along (1,1) | rt 0.8 |
| 357.16 | 4-6 | `frowns along the other` | Orange line along (1,−1) | rt 0.8 |
| 358.64 | 4-6 | `its a saddle` | Camera lifts to an oblique view: it is plainly a saddle | rt 1.2 |
| 359.93 | 4-6 | `east and north slices` | Red and green slices flash in with their two blue smiles | rt 0.6 |
| 363.44 | 4-6 | `hiding in between` | They fade; **the intro's ball replays** and rolls straight down the orange line. Puzzle solved | roll rt 2.0 |
| 367.10 | 4-7 | `right angles` | A right-angle mark at the center | rt 0.5 |
| 369.05 | 4-7 | `eigenvectors` | Labels `v₁` (blue) and `v₂` (orange) on the two axes | rt 0.6 |
| 372.38 | 4-7 | `five and minus one` | `λ = 5` (blue) and `λ = −1` (orange) | rt 0.6 |
| 373.86 | 4-7 | `eigenvalues` | The word “eigenvalues” underlines both λ | rt 0.5 |

### SCENE 16 · CH4: Line up the grid · 374.900–392.967 (6:14.90–6:32.97)

**Engine:** moderngl + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 375.12 | 4-8 | `turn the grid` | The floor grid rotates 45° onto the eigen-axes; contours become axis-aligned | rt 1.6 `smooth` |
| 377.64 | 4-8 | `twist disappears` | The matrix morphs: violet 3s drain to 0 | rt 0.8 |
| 380.67 | 4-8 | `two eigenvalues` | Diagonal becomes **5** (blue) and **−1** (orange) | rt 0.8 |
| 382.42 | 4-8 | `diagonal` | Diagonal glow | rt 0.5 |
| 383.99 | 4-9 | `any smooth surface` | Cut to the two-hill landscape from Ch2; zoom onto a point | rt 1.4 |
| 385.39 | 4-9 | `up close` | A translucent **quadratic patch** hugs it | rt 0.8 |
| 386.31 | 4-9 | `height` | Term 1: `f(p)` | rt 0.4 |
| 387.00 | 4-9 | `tilt from the gradient` | Term 2: `+ ∇f·h` (yellow); the patch tilts | rt 0.6 |
| 388.60 | 4-9 | `bend from the hessian` | Term 3: `+ ½ hᵀHh` (colored); the patch bends | rt 0.6 |
| 390.57 | 4-10 | `parabola from before` | Inset of the Ch1 cosine-and-parabola frame slides in | rt 0.8 |
| 391.78 | 4-10 | `one dimension up` | Both glow, then fade | rt 0.8 |

### Chapter 5 build (2026-11-05) · luminous from the start

Built straight in the design-system look; the builders are in `scenes/ch5.py`. The asserts there cover det(H) = −5 = λ₁λ₂ for the puzzle surface, the gradient, Hessian and critical points of x³ − 3x + y², the all-zero Hessians of x⁴ + y⁴ and the monkey saddle, and its three low lobes. Changes from the plan below:
- **Scene 17:** the fog returns for one beat, then clears into the sign chart, and the walker turns into the point (λ₁, λ₂). A mini surface with H = diag(λ₁, λ₂) sits beside the chart, ringed by live bend gauges (λ₁cos²φ + λ₂sin²φ).
- **Scene 18:** det H = f_xx f_yy − f_xy² = λ₁λ₂ builds term by term; the 2D test is a glass card, and each row pulses its quadrants. The puzzle surface's calculation ends with the walker at (5, −1).
- **Scene 19:** the Hessians above x = ±1 fill in per spoken word (rt 0.15, since the words are 0.15 s apart). A ball spirals into the valley; a gold path climbs out over the pass.
- **Scene 20:** an echo of the Ch1 card's "can't tell" row, then x⁴ + y⁴ and the turning monkey saddle side by side, each with a zero matrix and a flat gauge. A slow push-in, then a fade to black.

### SCENE 17 · CH5: Read the signs · 392.967–413.117 (6:32.97–6:53.12)

**Engine:** moderngl (fog reuse, mini-surface) + Manim sign chart

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 393.68 | 5-1 | `answer the question` | A 2 s return to the fog, walker and disc (I-1 reused) | dissolve rt 0.8 |
| 397.49 | 5-2 | `two eigenvalues` | The fog dissolves into a **sign chart**: λ₁–λ₂ plane, with a live mini-surface (H = diag(λ₁, λ₂)) in the corner tied to a dot | rt 1.0 |
| 398.78 | 5-3 | `both positive` | Dot → Q1 (2, 2); quadrant tints blue; mini-surface becomes a bowl | rt 1.0 |
| 400.84 | 5-3 | `every direction` | Small gauges around the bowl, all blue smiles | rt 0.5 |
| 402.77 | 5-3 | `local minimum` | Label **valley · local minimum** in Q1 | rt 0.5 |
| 404.12 | 5-4 | `both negative` | Dot → Q3 (−2, −2) through the origin; tints orange; mini-surface becomes a dome | rt 1.2 |
| 407.63 | 5-4 | `local maximum` | Label **peak · local maximum** in Q3 | rt 0.5 |
| 409.08 | 5-5 | `one of each` | Dot → Q4 (2, −2), then Q2; both tint with a blue/orange split; mini-surface becomes a saddle | rt 1.6 |
| 412.49 | 5-5 | `saddle` | Label **saddle** in Q2 and Q4 | rt 0.4 |

### SCENE 18 · CH5: The determinant shortcut · 413.117–439.267 (6:53.12–7:19.27)

**Engine:** Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 414.15 | 5-6 | `shortcut` | The chart shifts right; equation space opens left | rt 0.6 |
| 414.92 | 5-6 | `multiply the two bending numbers` | `f_xx · f_yy` (red · green) | rt 0.8 |
| 416.81 | 5-6 | `subtract the twist squared` | `− f_xy²` (violet) | rt 0.6 |
| 419.13 | 5-6 | `determinant` | `det H =` prefixes it | rt 0.6 |
| 421.62 | 5-6 | `multiplied together` | `= λ₁ · λ₂` | rt 0.6 |
| 423.40 | 5-6 | `negative` | Q2 and Q4 shade: det < 0 | rt 0.6 |
| 425.57 | 5-6 | `saddle` | Tag **saddle** on the shaded quadrants | rt 0.4 |
| 426.79 | 5-6 | `positive` | Q1 and Q3 shade: det > 0 | rt 0.6 |
| 429.84 | 5-6 | `tells you which` | `f_xx > 0` → Q1 arrow, `f_xx < 0` → Q3 arrow | rt 0.6 |
| 431.14 | 5-7 | `puzzle surface` | `[[2,3],[3,2]]` slides in | rt 0.6 |
| 432.20 | 5-7 | `two times two` | `2 · 2 = 4` | rt 0.6 |
| 433.76 | 5-7 | `three squared` | `3² = 9` | rt 0.6 |
| 435.32 | 5-7 | `four minus nine` | `4 − 9` | rt 0.5 |
| 436.72 | 5-7 | `minus five` | `= −5` in orange | rt 0.5 |
| 438.47 | 5-7 | `confirmed` | The dot lands at (5, −1) in Q4; stamp **saddle** | rt 0.6 |

### SCENE 19 · CH5: A real landscape · 439.267–463.133 (7:19.27–7:43.13)

**Engine:** moderngl (GLSL height `x³ − 3x + y²`, z clamped) + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 439.93 | 5-8 | `real landscape` | The landscape rises; slow camera orbit begins | rt 1.2, orbit to scene end |
| 442.08 | 5-8 | `x cubed` | `f = x³ − 3x + y²` writes (color-coded) | rt 1.2 |
| 445.48 | 5-8 | `two flat points` | Two white rings pulse | rt 0.6 |
| 446.80 | 5-8 | `x equals one` | Ring at (1, 0) brightens | rt 0.4 |
| 447.92 | 5-8 | `x equals minus one` | Ring at (−1, 0) brightens | rt 0.4 |
| 451.25 | 5-9 | `six` | Floating label above (1, 0) builds `[[6,0],[0,2]]` entry by entry | per word rt 0.3 |
| 454.68 | 5-9 | `valley` | A ball dropped nearby settles into (1, 0) | rt 1.0 |
| 457.14 | 5-10 | `minus six` | Label above (−1, 0): `[[−6,0],[0,2]]` | per word rt 0.3 |
| 460.31 | 5-10 | `saddle` | Tag **saddle** | rt 0.4 |
| 461.37 | 5-10 | `pass that leads out` | A dashed yellow path climbs out of the valley and over the pass | rt 1.6 |

### SCENE 20 · CH5: When the test can't tell · 463.133–480.417 (7:43.13–8:00.42)

**Engine:** moderngl (two viewports) + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 463.50 | 5-11 | `just like on the line` | The landscape fades; a tiny echo of the Ch1 `x³` row with its grey “?” drifts in | rt 0.8 |
| 466.08 | 5-11 | `cant tell` | The echo fades; a split frame opens | rt 0.8 |
| 467.04 | 5-11 | `x to the fourth` | Left: the flat-bottomed bowl `x⁴ + y⁴` | rt 1.0 |
| 469.40 | 5-11 | `valley` | Tag **valley** | rt 0.4 |
| 472.30 | 5-11 | `all zeros` | A grey zero matrix and a flat grey gauge | rt 0.6 |
| 474.31 | 5-12 | `monkey saddle` | Right: the monkey saddle `x³ − 3xy²`, slowly rotating, also with a zero matrix | rt 1.0 |
| 475.90 | 5-12 | `two legs and a tail` | Its three downward lobes outline one after another | lag 0.3, rt 1.2 |
| 477.75 | 5-13 | `eigenvalue is zero` | Both zero matrices pulse; a slow push-in on both centers starts and runs to the scene end | pulse rt 0.5, push `linear` to 480.4 |
| 479.65 | 5-13 | `look closer` | Fade to background under the push-in | rt 0.6 (ends ≈ 480.1) |

### Chapter 6 build (2026-11-05) · luminous from the start

Built straight in the design-system look; the builders are in `scenes/ch6.py`. The asserts there cover the landscape's global minimum (the glowing pit), both gradient-descent paths (12 steps on the round bowl, 21 on x² + 10y², each of them overshooting), κ = 20/2 = 10, Newton's single step p − H⁻¹∇f = 0, (10⁶)² = 10¹², and the seeded sign rows (3 valleys of 12 with 2 eigenvalues, none with 10 or 100). Changes from the plan below:
- **Scene 21:** a 16-Gaussian seeded landscape (luminous, yaw 145°, slow orbit and dolly). The fan of axes is screen-space, anchored on the pit.
- **Scene 22:** gradient descent first glides into a round bowl (H = 2I). The map then stretches into the narrow valley, so "long narrow valley" is a real change of function. λ₁ = 2 and λ₂ = 20 are bend gauges with curvature ∝ λ, and the floor and steep axes are drawn in red and green.
- **Scene 23:** the bowl is a luminous inset above the map. The mosaic is a numpy-rendered cell field, with the 2×2 grid at its centre, and its zoom-out is exponential. The trillion counter fades through a tracker, because its digit count changes.
- **Scene 24:** twelve flat points are drawn as rows of eigenvalue signs (coin flips, captioned "intuition, not a proof"). Row 5 is a valley with 2 eigenvalues and a saddle with 10. It ends on the luminous saddle, with the ball rolling off along y.

### SCENE 21 · CH6: Landscapes of error · 480.417–496.817 (8:00.42–8:16.82)

**Engine:** moderngl (procedural terrain) + skia

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 480.84 | 6-1 | `why does this matter` | Wide, slow fly-over of a rugged seeded terrain | fly-over `linear` to scene end |
| 486.96 | 6-1 | `bottom of a valley` | The deepest pit glows faintly | rt 0.8 |
| 488.59 | 6-1 | `neural network` | A soft caption “training” | rt 0.6 |
| 490.94 | 6-1 | `lowest point` | A marker settles at the pit | rt 0.6 |
| 492.18 | 6-1 | `height is the error` | Caption `height = error` | rt 0.6 |
| 494.74 | 6-2 | `not two dimensions` | The two floor axes brighten | rt 0.5 |
| 496.00 | 6-2 | `but millions` | Axes **multiply** into hundreds of faint radial axis lines (seeded, skia glow). The fan is handed to Scene 22, which fades it under its first beat | burst rt 0.6 `rush_from` |

### SCENE 22 · CH6: Gradient descent zigzags · 496.817–520.917 (8:16.82–8:40.92)

**Engine:** Manim (contour map of `x² + 10y²`)

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 497.46 | 6-3 | `simplest way down` | Top-down exact ellipses of `x² + 10y²`; ball at (3, 1) | rt 1.0 |
| 498.68 | 6-3 | `follow the gradient` | A `−∇f` arrow from the ball | rt 0.6 |
| 499.88 | 6-3 | `one small step` | First step taken | rt 0.6 |
| 502.20 | 6-3 | `gradient descent` | Label “gradient descent” | rt 0.5 |
| 504.54 | 6-4 | `long narrow valley` | The map stretches to show the long, narrow trough | rt 1.0 |
| 506.75 | 6-4 | `eigenvalues are two` | `H = diag(2, 20)`; short blue axis tick (2) along x | rt 0.6 |
| 508.33 | 6-4 | `20` | Long blue axis tick (20) along y | rt 0.4 |
| 509.75 | 6-4 | `10 times steeper` | The steep walls tint | rt 0.6 |
| 512.46 | 6-5 | `overshoots` | The steps resume: each crosses the trough floor | steps ↓ |
| 514.00 | 6-5 | `zigzags` | The full computed path plays (21 steps, step 0.09, y × −0.8 per step) with a fading trail; a step counter ticks | to ~516.8 |
| 515.64 | 6-5 | `crawling` | The path crawls along x toward the center | — |
| 518.19 | 6-6 | `20 over two` | `κ = 20 / 2 = 10` beside the map | rt 0.8 |
| 520.41 | 6-6 | `condition number` | Label “condition number” | rt 0.5 |

### SCENE 23 · CH6: One Newton jump, and a trillion numbers · 520.917–542.250 (8:40.92–9:02.25)

**Engine:** Manim + moderngl inset + moderngl procedural mosaic

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 521.33 | 6-7 | `bring in the hessian` | The GD path dims; H glows | rt 0.6 |
| 522.80 | 6-7 | `newtons method` | Label “Newton's method” | rt 0.5 |
| 524.76 | 6-7 | `as a bowl` | 3D inset: the local quadratic model as a translucent bowl | rt 0.8 |
| 527.51 | 6-7 | `jumps straight` | **One arc** from (3, 1) to (0, 0) | rt 1.0 `smooth` |
| 530.84 | 6-7 | `one jump` | Landing flash; counter “1 step” vs “21 steps” | rt 0.6 |
| 533.56 | 6-8 | `the catch` | Everything fades except the 2×2 grid | rt 0.6 |
| 536.56 | 6-8 | `million by a million` | The grid **zooms out** into an endless mosaic of tiny cells (procedural shader) | zoom rt 2.0 `rush_into` |
| 538.16 | 6-8 | `trillion numbers` | Counter rolls up to `1,000,000,000,000` | rt 1.0 |
| 541.08 | 6-8 | `estimate pieces` | Only a thin band of cells along the diagonal stays lit | rt 0.8 |

### SCENE 24 · CH6: Most flat points are saddles · 542.250–559.567 (9:02.25–9:19.57)

**Engine:** Manim (seeded) + moderngl

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 543.88 | 6-9 | `something surprising` | Mosaic fades; a grid of critical points, each a row of 2 eigenvalue dots | rt 0.8 |
| 545.43 | 6-9 | `huge landscapes` | Rows grow to 10 dots | rt 0.8 |
| 547.48 | 6-9 | `arent valleys` | All-blue rows (valleys) get a ring; few remain | rt 0.6 |
| 549.34 | 6-9 | `saddles` | The mixed rows tag **saddle** | rt 0.4 |
| 550.97 | 6-9 | `every single eigenvalue` | One all-blue row is highlighted | rt 0.6 |
| 554.12 | 6-9 | `millions of them` | Rows grow to 100 dots; all-blue rows become tiny isolated sparks. Caption “intuition, not a proof” | rt 1.0 |
| 555.83 | 6-9 | `almost always negative` | Orange dots pulse | rt 0.5 |
| 557.44 | 6-10 | `theres almost always` | One saddle row enlarges into a 3D saddle | rt 1.0 |
| 559.01 | 6-10 | `way down` | A ball rolls off it along the orange direction | rt 0.6 `rush_from` (ends 559.5) |

### Outro build (2026-11-05) · luminous from the start

The builders are in `scenes/ch7.py`; the asserts there cover the dial's bending uᵀHu = 2 + 3 sin 2θ and the eigenpairs (5 at 45°, −1 at 135°). Changes from the plan below:
- **Scene 25:** the four glass cards appear straight in their 2×2 slots, one per idea. On "signs decide everything" large brackets close around them, so the recap reads as a matrix. Card 3 is the puzzle surface's direction dial, with a live bend gauge.
- **Scene 26:** the cards dissolve into the scene-17 fog state. The probes reuse scene 01's `probe_arrow`. "How the ground bends" lifts the fog onto the saddle with its smile and frown slices, then a 0.6 s fade lands on black at 604.55.

### SCENE 25 · OUTRO: Recap · 559.567–594.933 (9:19.57–9:54.93)

**Engine:** skia cards + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 560.17 | O-1 | `walk back through it` | Card 1 (skia) slides in | rt 0.8 |
| 561.32 | O-1 | `on a line` | Parabola on card 1 | rt 0.6 |
| 564.99 | O-1 | `smile` | Blue smile gauge | rt 0.4 |
| 566.64 | O-1 | `frown` | Orange frown gauge | rt 0.4 |
| 567.46 | O-2 | `on a surface` | Card 2 slides in: the colored 2×2 grid | rt 0.8 |
| 568.80 | O-2 | `four second derivatives` | Cells light up in a stagger | lag 0.1, rt 0.6 |
| 573.04 | O-2 | `shows up twice` | Violet pair pulses | rt 0.5 |
| 575.76 | O-2 | `you have the hessian` | Brackets close | rt 0.5 |
| 577.36 | O-3 | `any direction` | Card 3: the direction dial sweeping | rt 0.8 |
| 580.49 | O-3 | `eigenvectors` | Blue and orange eigen-axes | rt 0.5 |
| 584.53 | O-3 | `eigenvalues` | λ labels | rt 0.4 |
| 587.06 | O-4 | `flat point` | Card 4: the sign chart | rt 0.8 |
| 588.25 | O-4 | `signs decide everything` | The four cards tile into a 2×2, echoing the matrix | rt 1.0 |
| 590.08 | O-4 | `all positive` | Q1 tints blue | rt 0.3 |
| 591.90 | O-4 | `all negative` | Q3 tints orange | rt 0.3 |
| 593.52 | O-4 | `mixed` | Q2/Q4 tint split | rt 0.3 |

### SCENE 26 · OUTRO: Back to the fog · 594.933–604.550 (9:54.93–10:04.55)

**Engine:** moderngl + Manim

| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|---|
| 595.45 | O-5 | `next time` | The cards dissolve into the **opening shot**: fog, walker, tangent disc | rt 1.2 |
| 597.44 | O-5 | `in the fog` | Fog drifts | — |
| 600.24 | O-6 | `which way is down` | The four probe arrows flash and vanish (as in I-2) | rt 0.8 |
| 601.64 | O-6 | `how the ground bends` | A blue smile arc and an orange frown arc glow under the walker at right angles. **The fog lifts**: the walker stands on a saddle | rt 1.6 |
| 603.28 | O-7 | `thanks for watching` | Hold on the revealed saddle, then fade to black, landing on the last frame | fade starts 603.95, rt 0.6 (ends 604.55) |

---

## Production notes

- **Render budget:** 36,273 frames at 1080p60. About 55% of the runtime is moderngl (fast on the R4); the Manim-only scenes (03–05, 09, 11, 12, 18, 22) dominate CPU time. Keep them light (few `VMobject`s, no big `always_redraw` groups) and render finals in the background, scene by scene.
- **Scene files:** 26 `NarratedScene`s, `scene_NN_slug.py`, each with `SCENE_START`/`SCENE_END` from the slice table (frames ÷ 60) and `PREVIOUS` set to the scene before, so every hand-off is exact by construction (as in 001). Hand-offs that cross engines (06: Manim → GL, 17: fog → chart, 26: cards → fog) are matched through the shared `SurfacePlate` camera.
- **Build order:** `SurfacePlate` lab test (480p and 1080p speed, fog, ribbons) → `BendGauge`, `HessianGrid` → scenes 03–05 (pure Manim, proves the pipeline) → the GL scenes → `build.sh`.
- **Listen check:** at 280.76 the aligner heard "Otto **Hess**". If ElevenLabs said "Hess" rather than "HESS-uh", it's a small inaccuracy; the on-screen caption spells it correctly either way.
- **Honesty flags:** the saddle-dominance shot (6-9) is intuition, captioned as such. "Bending" means the second directional derivative `uᵀHu`; the word "curvature" is kept off screen.

## Chapter 0 splat pass (2026-11-05)
- Scene 01 opens on a spiral galaxy of 120k 3D Gaussian splats (`aion/components/splat_gl.py`, promoted from
  `lab/2026-11-04-gaussian-splat-city`). It rains down in a wave from the walker outward; each splat lands as a
  sliver of the mountain range (altitude ramp `S.SPLAT_RAMP`). The fog now rolls in on "fog." and drowns the
  colour (splat visibility = fog³). Walker lines take the `aurora` cyan→lavender sheen.
- Scene 02: as the range sinks, the splats tear off and rise as sparks (`lift`), under the fog-bank dip.
- Scene 26 reuses the splat range so the outro matches the opening.
- After editing only a shader/GPU component, render with `--fresh` (Manim's cache can't see shader changes).

## Whole-video look pass (2026-11-05)
- Stage is pure black for the whole video (backdrops tried and dropped: galaxy, world, red smoke, red
  gradient). `blit.UNDERLAY` / plate coverage code is kept but dormant.
- Typography: maths in Libertinus (`S.TEX_PREAMBLE`, global tex template in shared.py); labels in Inter
  Light (`S.LABEL_WEIGHT`); headings and eyebrows pass their own weight. Curves use a brighter
  cyan → lavender sheen (`S.CURVE_A/B`) over a deep-blue grid (`S.GRID_MAJOR`).
- Graph motion layer (`VideoScene.play` in shared.py, applies everywhere): `Create`/`FadeIn` of an `Axes`
  becomes a stretch-in from the origin (x, then y, fading up); `Create` of a curve gets a glowing comet head
  riding its drawing tip. `V.punch(mob, point, k)` is a there-and-back zoom on a key word: scene 03 "zero",
  scene 04 "peak", scene 05 "can't tell".
- Labels kept off the plots: "slope" sits left of the slope panel; "2 + 3 sin 2θ" sits above the sweep graph.
- Every SurfacePlate wears the intro's parametric look through `Rig.plate()` (`SURF_LOOK`: gradient fill
  `S.GROUND_GRADIENT`, aurora-tinted grid and contours, crisp boundary with a rim line).
- Scene 17's foggy-hill flashback uses the intro's splat range and gradient ground.
