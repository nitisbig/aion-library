# 003: Fourier Series. Drawing Anything With Rotating Circles

**Mode:** production · **Status:** phase 3 ✅ timed scene plan **approved** (2026-11-09). Phase 4: building. This file is now the source of truth; `scene-plan.md` is the phase-1 history.

**Pipeline**
1. ✅ Scene plan and `voiceover.md` (revision 2, approved).
2. ✅ Audio and subtitles in `assets/`: `audio.mp3`, `cue-per-word.srt`, `normal-subtitle.srt` (+ `words.json`, the same word timings as JSON).
3. ⏳ **This file:** chapters chunked into 30 scenes, every beat timed from the SRT.
4. ⬜ Library pieces and lab checks, then the scenes. Preview, verify, and render the finals.

## Timing facts from the audio

- `audio.mp3` is **621.576 s (10:21.58)**, 48 kHz, 320 kb/s, inside the 8–12 min target. **No cuts are needed**, so the ✂ notes from the phase-1 plan are dropped.
- `cue-per-word.srt` has **1,799 word cues** and matches `voiceover.md` **word for word** (checked with a diff). ElevenLabs spelled everything out ("eighteen oh seven", "C n", "f of t", "one ninth", "Gibbs"), so **the cue keys are simply the script's words**.
- **Every `t` below comes from `beats.py`**, which looks each cue key up with `Cue.at()` and fails if a key is missing, out of order, or outside its scene. Rerun it if the audio is ever regenerated:
  `uv run python videos/003-fourier-series/beats.py`
  Scenes use the same keys through `self.t("…")`, so no time is typed in by hand anywhere.
- **Keys are searched in order.** Each beat is looked up *after the previous beat* of its scene, so repeated words ("circle", "one", "average", "stand still") always resolve to the right occurrence, with no hand-typed `after=` times (an improvement on 002).
- **Cuts are word pairs, not numbers.** Each cut is defined as (last words of a scene, first words of the next). The cut lands on the 60 fps frame nearest the middle of the gap between them, **intersected with the real silence** from `ffmpeg silencedetect -35dB d=0.25` (the aligner's word ends can overrun a pause). Every cut sits in a pause of at least 0.35 s; most are 0.5–1.2 s.
- **Anchor on word starts.** Animation start = word start − `LEAD` (0.15 s) unless the Anim column says otherwise. `end:` keys anchor on a word's end (used for loops that must close on a word).
- **The video ends exactly on the audio:** 37,294 frames = 621.567 s. The voice ends at 621.19; the last fade runs to the final frame.

## Chapters (real timings)

| Part | Title | Scenes | Range | Length |
|---|---|---|---|---|
| Intro | Circles that draw | 01–03 | 0:00.00 – 1:04.28 | 64.3 s |
| Ch1 | One circle | 04–06 | 1:04.28 – 2:09.27 | 65.0 s |
| Ch2 | Stacking circles | 07–10 | 2:09.27 – 3:24.62 | 75.4 s |
| Ch3 | Fourier's hot ring | 11–13 | 3:24.62 – 4:32.28 | 67.7 s |
| Ch4 | Waves become drawings | 14–18 | 4:32.28 – 5:51.30 | 79.0 s |
| Ch5 | Spin and average ★ | 19–23 | 5:51.30 – 8:03.57 | 132.3 s |
| Ch6 | Drawing anything | 24–27 | 8:03.57 – 9:24.50 | 80.9 s |
| Outro | What we built | 28–30 | 9:24.50 – 10:21.57 | 57.1 s |

The mode switches every 60–80 s (rule 10): spectacle → 2D → 3D spring → build-up → physics/3D ring → history/sky → derivation → GPU spectacle → applications → recap → 2.5D finale.

## What changed from the phase-1 plan (the improvements)

1. **30 scenes instead of 28.** Two long scenes split at natural pauses: the intro's S02 (51 s) became **S02 corner + S03 chord** (the break before "Think of a chord"), and the old S16 (40 s) became **S17 rounded square + S18 speed rack** (the break before "In general"). No scene is longer than 45 s, so previews on the 2-core CPU stay quick, and every cut sits in a real pause.
2. **Same chain at both ends.** S01 and S30 use the **identical 201-circle clef chain** that S24–S25 build, so the finale is a true callback. S01's loop period is the whole scene (13.28 s): the clef is ~90 % drawn on the word "clef" and closes in the pause, at the cut. The finale loop starts on "For now" and closes exactly as "round" ends (4.39 s).
3. **A math fix in S21.** Turning the drawing backward once lowers *every* speed by one, so the still speed-0 arm also starts turning (speed −1). The phase-1 plan forgot this; the labels now update 0 → −1, +1 → 0, +2 → +1, −1 → −2, −2 → −3.
4. **The Ch5 bean is fixed and verified.** `BEAN = {0: 0.6+0.35i, 1: 1, −1: 0.35e^{0.5i}, 2: 0.22e^{2.2i}, −2: 0.12e^{−0.8i}}`: a simple loop (no self-crossing), about 12 % concave, so it reads as a squiggly bean. `beats.py` checks that spin-and-average returns all five circles exactly and zero for ±3.
5. **S11 no longer needs an outside asset.** The optional Fourier portrait (and its name text) is replaced by a computed picture of heat spreading along a metal bar, which then bends into the ring. A "hot on one side" beat raises the temperature crown before the unroll.
6. **S27's compression image** is a frame of this video's own clef render (no dependency on 002's media).
7. **More beats land on spoken words** that had no visual before: the three chips on "Size, speed, and starting point" (S05), each fraction as it is said (S08, S26), `+1`/`−1` on "positive"/"negative speed" (S16), a green pulse on "just as it should" (S22), the dashed slot before "a second" appears (S07), "faster it fades" (S12).
8. **Gibbs numbers are checked against the actual counts shown** (10 / 50 / 200 circles), not just the limit.

## The idea of the video, in one line

**A circle seen from the side is a wave, and enough circles stacked tip to tail can draw anything.** The whole video answers one question from the intro: *how does something that only goes round draw a corner?* The **square** carries it: a drawn square (S02), a square *wave* (S09), a hot/cold ring (S11), the rounded square (S17), decoded (S22), and 1/n² against 1/n (S26). The **treble clef** is the spectacle: first on screen (S01), rebuilt from scratch (S24–S25), played one last time (S30).

## Verified math (numpy, regenerated by `beats.py`)

| Object | Fact used on screen |
|---|---|
| One circle | tip = r·e^{i(nt+φ)}; height = r·sin(nt + φ). Quarter-turn start → cos |
| Helix | (t, r cos t, r sin t): side shadow = sine, top shadow = cosine |
| **Square wave** | (4/π)·Σ_{odd n} sin(nt)/n. First radius 4/π ≈ 1.273 ("a little taller"). Radii 1, 1/3, 1/5, 1/7 relative |
| **Gibbs** | peak 1.1798 / 1.1790 / 1.1790 with 10 / 50 / 200 circles for a ±1 wave → **8.95 % of the jump** |
| **Heat on a ring** | u_t = κ u_θθ. Mode n fades as e^{−κn²t}, so 3× the wiggles → **9×** faster. Square start: u = Σ_{odd} (4/πn) e^{−n²κt} sin nθ |
| Planets | geocentric Mars, circular coplanar orbits = r_M e^{iω_M t} − r_E e^{iω_E t}: exactly two circles, with retrograde loops |
| **Square loop** (side 2, constant speed, starting mid-side) | nonzero only for n ≡ 1 (mod 4): c₁ = 1.14632, c₋₃ = −0.12737, c₅ = −0.04585, c₋₇ = 0.02339; \|c_n\| = c₁/n² |
| **Rounded square** | z = e^{2πit} − (1/9)e^{−2πi·3t}. Spin-and-average: k = 1 → 1, k = −3 → −1/9, k = 2 → 0 (exact) |
| **Bean** (Ch5) | 5 known circles (above); spin-and-average returns each exactly |
| Rotating frame | multiplying by e^{−2πikt} turns speed n into n − k. Average over a loop = c_k |
| Recipe | c_n = ∫₀¹ f(t) e^{−2πint} dt · f(t) = Σ c_n e^{2πint} |
| Piano chord | C major triad (C4 261.63 Hz, E4 329.63, G4 392.00) as three sines → their sum (displayed slowed down) |
| Clef | 1,000 samples, n = −100…100 → 201 circles (FFT), sorted by \|c_n\|, centered so c₀ = 0 |

## Color semantics (whole video)

Same black stage and luminous line look as 002. New constants go in `aion/style.py` under `# Fourier series (video 003)`.

| Meaning | Constant | Color | Why |
|---|---|---|---|
| The pen tip, the ink it leaves (every wave and every drawing) | `INK` (= `GRAD`) | `#FFD43B` gold | the output is always gold |
| Positive speed: counterclockwise circles, bars above the axis | `FWD` (= `SMILE`) | `#2E9BFF` blue | the "positive" blue of 001/002 |
| Negative speed: clockwise circles | `BWD` (= `FROWN`) | `#FF8A2A` orange | the "negative" orange of 001/002 |
| Speed zero, the **balance point** (average), a frozen circle, `c_n` | `STILL` (= `HY`) | `#2EE88A` green | "found it" |
| Starting angle (phase) arcs | `PHASE` (= `TWIST`) | `#A77BFF` violet | |
| Circle rims and arms (neutral) | `ARM` (= `TERRAIN_LINE`) | `#C9D4E3` silver, rims at 25–35 % opacity | the machinery stays quiet so the ink pops |
| Target / ghost shapes | `GHOST_LINE` | `#5C6370` dashed | |
| Gibbs spike, "expensive corner" marker | `SPIKE` (= `HX`) | `#FF3D5A` red | used only twice, so it reads as a warning |
| Temperature (Ch3 only) | `HEAT_RAMP` | `#1B2A6B` → `#7A2BB8` → `#FF5A1F` → `#FFE9C7` | ice-indigo to ember to white-hot, kept apart from the blue/orange speed colors |

Equations are color-coded the same way every time: `c_n` green, `f(t)` gold, `e^{−2πint}` orange (backward spin), `∫₀¹ … dt` silver (average), `n` blue, `φ` violet.
**Background:** pure black `#000000` (`STAGE`), with the 002 post stack: two-level bloom, vignette 0.5, grain 0.04.
**Type:** Space Grotesk for title and chapter eyebrows, Inter Light for labels, Libertinus for math (same as 002). **Minimal text on screen**: no sentences, only numbers, short labels, named terms, and equations.

## Engines

| Engine | Role here |
|---|---|
| **Manim CE** | The default. Small chains (≤ 30 circles), shadow waves, the square-wave build, Gibbs zoom, all equations, the spectrum strip, the rotating-frame derivation (Ch5), recap cards, and every label. |
| **moderngl** | **`EpicyclePlate`**, for chains of 50–500 circles with glowing ink, bloom, a camera that zooms 40× onto the pen tip, and a 2.5D tilted finale. Manim's Cairo renderer would crawl at 200+ circles × 60 fps on 2 cores. **`HeatRingPlate`** renders the 3D metal ring in Ch3: temperature as height and color, lit, with a soft reflection. Both reuse the `post_gl` bloom and the `SurfacePlate` camera / `project()` pattern, so Manim labels stay pinned to GL geometry. |
| **Taichi** | **`InkParticles`**: about 20k sparks shed by the pen tip, drifting on curl noise and cooling as they fade (intro, Ch6, finale), plus the flame/frost particles on the ring in Ch3. Taichi steps the simulation; moderngl draws additive points. Seeded, so re-renders match exactly. |
| **pyvista** | **The spring (Ch1, S06)**: a lit, glossy tube helix with sine and cosine shadows on two glass walls, under an orbiting camera. This is the "tube or ribbon curves" case from `advanced-scene-type.md`. It renders off-screen frames that are composited in Manim. **Lab check first** (VTK off-screen on Mesa/R4). Fallback: Manim `ProgressThreeDScene` with a `ParametricFunction` (lines are cheap even on Cairo). |
| **skia-python** | Title plate (`TitlePlate`), chapter eyebrows, glass recap cards (`cards.py`), the starfield in Ch4, line-art piano keys, and the image tiles for the compression demo in Ch6. |
| **numpy / scipy** | All Fourier math (FFT for coefficients), heat solution, chord and voice/violin synthesis, and the real 8×8 DCT compression demo in Ch6 (`scipy.fft.dctn`). |
| **fontTools** (to add) | Pulls the treble clef outline from **Noto Music** (installed, SIL OFL, U+1D11E) via `aion/drawings.py` (lab-checked 2026-11-09). |
| ffmpeg | Concatenation and the audio mux, as in 002's `render.py`. |

### New library pieces (built before scenes)
- **`aion/fourier.py`**: `sample_path(path, n)` (arc-length or uniform-time resampling, contour bridging for multi-contour glyphs), `coefficients(points, N)` (FFT, returns `{n: c_n}`), `partial_sum(coeffs, t, order="size")`, `chain_points(coeffs, t)` (every joint position for drawing arms), `square_wave(n_terms)`, `square_loop_coeffs(N)`, `heat_ring(theta, t)`. Unit tests check them against the closed forms in the math table.
- **`aion/components/epicycles.py` → `EpicycleChain`** (Manim): a `ValueTracker` for t, then rims, arms, and pen, with rims colored by speed sign, an optional phase arc, and an ink `TracedPath` with an age fade. `rotating_frame=k` multiplies the whole picture by e^{−2πikt} (Ch5).
- **`aion/components/shadow_wave.py` → `ShadowWave`**: a dashed projection line from the tip to a moving pen that writes the wave. Horizontal or vertical (Ch4 uses both).
- **`aion/components/spectrum.py` → `SpectrumStrip`**: one bar per speed, blue above / orange for negative speeds, green for 0. It can fill live, **sort by size**, and **morph bars into circles** (Ch6). It is the "list" from Ch2, the rack in Ch4, and the readout in Ch5 and Ch6.
- **`aion/components/epicycle_gl.py` → `EpicyclePlate`** (moderngl): instanced rims and arms, an ink ribbon with constant screen width and age-faded glow, camera `(center, zoom, tilt, yaw)` trackers, and `project()`. The ink is re-evaluated from the coefficients every frame, so it stays sharp at 40× zoom.
- **`aion/components/heat_ring.py` → `HeatRingPlate`** (moderngl): a torus with temperature `u(θ, t)` as height and `HEAT_RAMP` color.
- **`aion/components/ink_particles.py` → `InkParticles`** (Taichi + moderngl).
- **Drawing assets** in `assets/drawings/`: the treble clef (`aion.drawings.treble_clef()`, Noto Music), the square loop (analytic), the "bean" loop for Ch5 (built from 5 known circles, so the answer is exact).

### Lab checks before production (`lab/2026-11-09-epicycles/`): ✅ all four done 2026-11-09, results in its NOTES.md
1. `EpicyclePlate` speed at 480p and 1080p with 200 and 500 circles on the R4, and the ink look in **3 variations** (thin hairline with bloom / tapered brush / dotted comet) for the user to pick.
2. pyvista off-screen helix: does it render on Mesa and how fast? If not, use the Manim fallback.
3. `InkParticles` look and cost at 20k particles.
4. The clef glyph: how many contours, and does bridging them read as one line?

## Recurring motifs (continuity, rule 9)

- **The pen**: a gold glowing dot at the tip of every chain. It is the only gold thing that moves.
- **The chain**: silver arms and faint rims. It never cuts. Chains grow, shrink, re-parameterize, and morph between scenes.
- **The square**: drawn square (intro) → square wave (Ch2) → hot/cold ring (Ch3) → rounded square (Ch4) → decoded (Ch5) → 1/n² vs 1/n (Ch6).
- **The piano chord**: three note waves merging into one (intro), returning as the singer and violin spectra (Ch6).
- **The spectrum strip ("the list")**: born in Ch2 as the list of speeds and sizes, it becomes the empty speed rack in Ch4, fills in Ch5, sorts and turns into circles in Ch6, and melts into a continuous band in the outro teaser.
- **The recipe line**: ghosted and unexplained in the intro, read in two steps in Ch5, shown on the last recap card.
- **The red corner marker**: planted at the Gibbs spike (Ch2), paid off in Ch6.
- **Chapter eyebrow**: a small uppercase label, top-left, for ~2.5 s at each chapter start ("01 · ONE CIRCLE"). It doubles as graphical progress (rule 6).

## Promise tracker (rule 18)

| # | Promise (where it opens) | Paid off |
|---|---|---|
| P1 | "How does something that only goes round draw a corner?" (S02) | S09 square wave, S17 rounded square, S26 1/n² |
| P2 | "I'll put it on screen now, just so you'll recognize it later." (S03, muted formula at `RECIPE_POS`) | S23, read in two steps at the same spot |
| P3 | "while studying, of all things, heat" (S02, ring flash) | S11–S13 |
| P4 | "Sharp corners are expensive." (S10, red marker) | S26 "Remember how I said…" |
| P5 | The clef on screen from frame 0 (S01) | S24–S25 rebuilt from scratch, S30 final play |
| P6 | "Here's a friendly example we'll keep coming back to." / "Its first two circles are exactly these." (S17) | S22 sanity check finds 1/9 · S26 |
| P7 | The piano chord (S03) | S27 "Think back to the piano chord." |
| P8 | "That's the Fourier transform, and it's where we'll go next." (S29) | next video |

---

## Scene slices (60 fps, every cut on a frame inside a real silence)

| # | Part | File · class | Range (s) | Frames | Length | Cut silence |
|---|---|---|---|---|---|---|
| 01 | INTRO | `scene_01_hook.py` · `Scene01Hook` | 0.000 – 13.283 | 0 – 797 | 13.3 s | 12.74–13.84 |
| 02 | INTRO | `scene_02_corner.py` · `Scene02Corner` | 13.283 – 45.900 | 797 – 2754 | 32.6 s | 45.51–46.30 |
| 03 | INTRO | `scene_03_chord.py` · `Scene03Chord` | 45.900 – 64.283 | 2754 – 3857 | 18.4 s | 63.90–64.68 |
| 04 | CH1 | `scene_04_one_circle.py` · `Scene04OneCircle` | 64.283 – 84.433 | 3857 – 5066 | 20.2 s | 84.08–84.78 |
| 05 | CH1 | `scene_05_three_settings.py` · `Scene05ThreeSettings` | 84.433 – 114.283 | 5066 – 6857 | 29.8 s | 113.95–114.61 |
| 06 | CH1 | `scene_06_spring.py` · `Scene06Spring` | 114.283 – 129.267 | 6857 – 7756 | 15.0 s | 128.87–129.65 |
| 07 | CH2 | `scene_07_two_circles.py` · `Scene07TwoCircles` | 129.267 – 146.967 | 7756 – 8818 | 17.7 s | 146.61–147.33 |
| 08 | CH2 | `scene_08_square_build.py` · `Scene08SquareBuild` | 146.967 – 168.800 | 8818 – 10128 | 21.8 s | 168.26–169.33 |
| 09 | CH2 | `scene_09_square_wave.py` · `Scene09SquareWave` | 168.800 – 186.217 | 10128 – 11173 | 17.4 s | 185.94–186.48 |
| 10 | CH2 | `scene_10_gibbs.py` · `Scene10Gibbs` | 186.217 – 204.617 | 11173 – 12277 | 18.4 s | 204.17–205.06 |
| 11 | CH3 | `scene_11_ring.py` · `Scene11Ring` | 204.617 – 228.117 | 12277 – 13687 | 23.5 s | 227.73–228.49 |
| 12 | CH3 | `scene_12_fading.py` · `Scene12Fading` | 228.117 – 256.167 | 13687 – 15370 | 28.1 s | 255.76–256.58 |
| 13 | CH3 | `scene_13_doubt.py` · `Scene13Doubt` | 256.167 – 272.283 | 15370 – 16337 | 16.1 s | 272.00–272.56 |
| 14 | CH4 | `scene_14_two_directions.py` · `Scene14TwoDirections` | 272.283 – 280.783 | 16337 – 16847 | 8.5 s | 280.44–281.14 |
| 15 | CH4 | `scene_15_sky.py` · `Scene15Sky` | 280.783 – 296.467 | 16847 – 17788 | 15.7 s | 296.13–296.79 |
| 16 | CH4 | `scene_16_direction.py` · `Scene16Direction` | 296.467 – 310.767 | 17788 – 18646 | 14.3 s | 310.17–311.37 |
| 17 | CH4 | `scene_17_rounded_square.py` · `Scene17RoundedSquare` | 310.767 – 330.717 | 18646 – 19843 | 19.9 s | 330.20–331.23 |
| 18 | CH4 | `scene_18_rack.py` · `Scene18Rack` | 330.717 – 351.300 | 19843 – 21078 | 20.6 s | 350.76–351.85 |
| 19 | CH5 | `scene_19_balance.py` · `Scene19Balance` | 351.300 – 382.017 | 21078 – 22921 | 30.7 s | 381.45–382.58 |
| 20 | CH5 | `scene_20_rule.py` · `Scene20Rule` | 382.017 – 389.317 | 22921 – 23359 | 7.3 s | 388.87–389.75 |
| 21 | CH5 | `scene_21_freeze.py` · `Scene21Freeze` | 389.317 – 417.983 | 23359 – 25079 | 28.7 s | 417.50–418.47 |
| 22 | CH5 | `scene_22_check.py` · `Scene22Check` | 417.983 – 438.717 | 25079 – 26323 | 20.7 s | 438.26–439.17 |
| 23 | CH5 | `scene_23_recipe.py` · `Scene23Recipe` | 438.717 – 483.567 | 26323 – 29014 | 44.9 s | 483.37–483.76 |
| 24 | CH6 | `scene_24_compute.py` · `Scene24Compute` | 483.567 – 501.733 | 29014 – 30104 | 18.2 s | 501.48–502.00 |
| 25 | CH6 | `scene_25_converge.py` · `Scene25Converge` | 501.733 – 516.983 | 30104 – 31019 | 15.2 s | 516.77–517.20 |
| 26 | CH6 | `scene_26_smooth_sharp.py` · `Scene26SmoothSharp` | 516.983 – 540.800 | 31019 – 32448 | 23.8 s | 540.59–541.00 |
| 27 | CH6 | `scene_27_everywhere.py` · `Scene27Everywhere` | 540.800 – 564.500 | 32448 – 33870 | 23.7 s | 564.33–564.68 |
| 28 | OUTRO | `scene_28_recap.py` · `Scene28Recap` | 564.500 – 596.900 | 33870 – 35814 | 32.4 s | 596.62–597.19 |
| 29 | OUTRO | `scene_29_teaser.py` · `Scene29Teaser` | 596.900 – 615.050 | 35814 – 36903 | 18.1 s | 614.84–615.25 |
| 30 | OUTRO | `scene_30_finale.py` · `Scene30Finale` | 615.050 – 621.567 | 36903 – 37294 | 6.5 s | — (end of audio) |

Total: **37294 frames = 621.567 s** (audio 621.576 s).

### Derived timings (from `derived()`)

| Name | Value |
|---|---|
| `CLEF_LOOP_S01` | 13.283 |
| `CLEF_S01_AT_WORD` | 0.897 |
| `FINALE_LOOP` | 4.390 |
| `FINALE_START` | 615.260 |
| `FINALE_CLOSE` | 619.650 |
| `VOICE_END` | 621.190 |

### Math check (`verify_math()`, run on every regenerate)

- Gibbs peak (±1 wave) with 10 / 50 / 200 circles: 1.1798 / 1.1790 / 1.1790 → overshoot 8.95 % of the jump
- Square loop: c₁ = 1.14632, c₋₃ = -0.12737, c₅ = -0.04585, c₋₇ = 0.02339: only n ≡ 1 mod 4, |c_n| = c₁/n² (shrinks like 1/n²)
- Rounded square spin-and-average: k=1 → 1, k=−3 → −1/9, k=2 → 0, k=0 → 0 (exact)
- Bean: spin-and-average returns all 5 circles exactly; k=±3 → 0
- Heat: mode n fades as e^(−κn²t), so mode 3 fades 9× as fast as mode 1

---

## INTRO

### SCENE 01 · What you're looking at · 0.000–13.283 (0:00.00–0:13.28, 13.3 s)

**Engine:** moderngl `EpicyclePlate` + Taichi `InkParticles` + `post_gl` bloom  
**Why it works:** Opens on the finished picture (rule 1, 3). The strangest fact comes before any explanation.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 0.00 | (frame 0) | Fade up from black on a chain already turning: the **same 201-circle clef chain** used in S25 and S30 (identical coefficients, so the ending is a true callback). Rims faint silver, pen gold. The pen has just started its loop and leaves a thin gold line. The camera drifts in from 1.08× | fade 0.4 s · camera `smooth` over the whole scene · loop period = `CLEF_LOOP_S01` |
| 1.30 | `chain of circles` | A light sweep runs down the chain from the root joint to the pen, joint by joint | 1.2 s |
| 4.10 | `edge of the one before` | Close beat: the camera follows joint 3 for about a second, showing one circle riding the rim of the one before, then eases back out | 1.0 s in, 0.8 s out |
| 6.38 | `own steady speed` | Rims tint `FWD` / `BWD` by spin direction | 0.5 s |
| 9.86 | `very last circle` | The camera settles on the whole drawing. The pen ignites: bloom up, first sparks | 0.4 s |
| 11.92 | `treble clef` | About 90 % of the clef is drawn and it reads. Comet glow on the ink | — |
| 12.74 | end of `treble clef` | The pen keeps going and **closes the loop inside the pause** (at the cut). A soft flash runs once along the whole outline | ease out on the last 0.5 s of the loop |

### SCENE 02 · How can circles draw a corner? · 13.283–45.900 (0:13.28–0:45.90, 32.6 s)

**Engine:** `EpicyclePlate` (clef → square chain) + Manim overlay + skia `TitlePlate` + `HeatRingPlate` stills (from S11)  
**Why it works:** The square is the extreme wrong-intuition case (rule 4). The question is asked aloud and held (rule 15).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 17.26 | `roundest thing` | The clef chain fades to 15 % and its ink to 30 %. One circle at the root brightens alone | 0.8 s |
| 18.74 | `no corners` | A dashed square ghost flickers around that circle and dissolves: what a circle is *not* | 0.5 s in / 0.8 s out |
| 22.58 | `sharp turns` | The chain returns to full. Push in on the clef's sharpest turn (bottom hook), then pull back | camera 1.2 s |
| 24.18 | `square` | **No cut:** the chain re-tunes into the square loop's circles (speeds 1, −3, 5, −7, …; 61 circles) and the ink morphs clef → square | coefficient tween 1.4 s `smooth` |
| 24.84 | `four perfect corners` | The camera dives 8× into one corner. Tiny circles whirl there; the ink corner stays razor sharp | 1.5 s `smooth` |
| 29.16 | `draw a corner` | Freeze. Everything dims to 20 % except the corner and the pen. Hold through the pause | 0.4 s |
| 32.46 | `fourier series` | Pull back to the whole square. **"Fourier Series"** sets in Space Grotesk with a soft glow and a warm light sweep | `TitlePlate` 1.1 s |
| 34.38 | `joseph fourier` | A small name line under the title, Inter Light | 0.6 s |
| 38.95 | `heat` | Teaser flash: the metal ring, half ember and half ice (a still from S11) | in 0.4 s, hold 1.2 s, out 0.4 s |
| 40.66 | `bold claim` | Title lifts and fades | 0.6 s |
| 42.28 | `any loop` | Gallery: three small chains draw at once (clef, square, the Ch5 bean) | `LaggedStart` 0.25 |
| 44.52 | `spinning circles` | Their rims pulse in a stagger, then the gallery fades to black | 0.8 s |

### SCENE 03 · A chord, and a recipe · 45.900–64.283 (0:45.90–1:04.28, 18.4 s)

**Engine:** Manim (waves, formula) + skia line-art piano keys  
**Why it works:** The analogy gives a familiar picture before any math. The formula is planted, unexplained (rule 8).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 46.84 | `chord on a piano` | A line-art octave of piano keys (skia). C, E, G press down in turn | 0.8 s |
| 48.62 | `one sound` | Three thin silver sines (C4, E4, G4, computed, slowed) rise from the keys and **merge into one gold waveform** | 1.2 s |
| 50.20 | `few notes` | The gold waveform splits back into its three waves, then re-merges | 0.6 s + 0.6 s |
| 53.44 | `take a shape` | The keys and wave fade. A gold rounded square draws in their place | 1.0 s |
| 54.40 | `pick out the circles` | It splits into its two circles (blue r = 1, orange r = 1/9), which then re-merge | 1.2 s |
| 58.44 | `recipe` | Everything fades except the big blue circle, which slides to the left third | 0.8 s |
| 61.60 | `on screen now` | The recipe `c_n = ∫₀¹ f(t) e^{−2πint} dt` writes on in muted silver at 60 %, upper right (colors arrive only in S23) | `Write` 1.2 s |
| 62.98 | `recognize it later` | The formula fades to 0 in place; its exact position is saved as `RECIPE_POS` for S23. The single circle remains: the hand-off to Ch1 | 0.8 s |

## CH1

### SCENE 04 · One circle · 64.283–84.433 (1:04.28–1:24.43, 20.2 s)

**Engine:** Manim (`EpicycleChain` with 1 circle, `ShadowWave`)  
**Why it works:** Concrete before general (rule 13). One focal point: the tip's height.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 66.48 | `start easy` | Eyebrow **01 · ONE CIRCLE** (top-left) | 0.6 s |
| 68.72 | `single circle` | The circle settles at the left third (center x = −4) | 1.0 s |
| 70.84 | `arrow` | A silver arm grows from the center to the rim, with the pen at its tip | `GrowArrow` 0.6 s |
| 72.42 | `turning steadily` | It turns counterclockwise, one turn per 4 s, for the rest of the chapter | `linear` |
| 75.58 | `how high its tip is` | The circle dims to 40 %. A dashed line runs from the pen to a vertical track just right of the circle, where a gold marker rides up and down | 0.6 s |
| 77.44 | `up down up down` | A glow pulse at the top and bottom of the track. The motion is phased so the marker actually hits the top on "up" | `there_and_back` |
| 81.04 | `time move to the right` | A time axis draws to the right of the track (hairline, no numbers) | 0.8 s |
| 83.62 | `trail` | The marker leaves a gold trail that scrolls right: the wave is born | continuous |

### SCENE 05 · Size, speed, start · 84.433–114.283 (1:24.43–1:54.28, 29.8 s)

**Engine:** Manim  
**Why it works:** Each setting changes exactly one thing, with a ghost of the old wave to compare (rules 12, 14).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 85.74 | `sine wave` | Label `\sin t` (gold) settles above a crest | `Write` 0.6 s |
| 90.32 | `seen from the side` | 2.5D beat: the circle tilts about its vertical axis to edge-on and becomes a vertical line, the pen bouncing on it; then tilts back | 1.0 s + 0.8 s |
| 93.28 | `three settings` | Three small glass chips under the stage: **size · speed · start** | `LaggedStart` 0.15 |
| 94.62 | `its size` | Chip 1 lights. Radius 1 → 1.5; the wave grows taller. The old wave stays as a dim ghost | 1.0 s |
| 98.46 | `its speed` | Chip 2 lights. Turn rate doubles; the wave has twice the wiggles. Ghost kept | 1.0 s |
| 103.82 | `where it starts` | Chip 3 lights | 0.4 s |
| 106.10 | `quarter turn ahead` | A **violet arc** shows a quarter-turn head start. The arm jumps ahead and the whole wave slides over by a quarter period (a cosine) | arc 0.6 s, slide 0.9 s |
| 109.65 | `size speed and starting point` | The three chips light again in time with the three words | 0.3 s each |
| 112.52 | `everything one circle can do` | The formula `r\,\sin(n t + \varphi)` assembles from the chips: r silver, n blue, φ violet | `TransformMatchingTex` 1.2 s |

### SCENE 06 · Two shadows of one motion · 114.283–129.267 (1:54.28–2:09.27, 15.0 s)

**Engine:** **pyvista** off-screen frames (glossy gold tube helix, glass back wall and floor) composited in Manim; labels pinned by the shared camera matrix. Fallback: Manim `ProgressThreeDScene`  
**Why it works:** 2D → 3D mode switch (rule 10). A sine and a cosine are one motion seen two ways.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 114.84 | `another view` | The flat frame tilts into 3D (¾ view) | camera 1.2 s |
| 116.50 | `slide the circle forward` | The circle slides along the time axis | continuous |
| 120.08 | `spring` | Its tip leaves a glowing gold **tube helix** | continuous |
| 121.03 | `from the side` | Orbit to a pure side view: the back-wall shadow is a sine. Label `\sin t` | orbit 1.4 s |
| 123.59 | `from above` | The camera rises to a top view: the floor shadow is a cosine. Label `\cos t` | 1.4 s |
| 126.73 | `two shadows` | Back to ¾ view, both shadows lit at once | 1.2 s |
| 128.06 | `turning motion` | The camera settles to the side view, so the scene ends on a flat sine: the hand-off to Ch2 | 0.8 s |

## CH2

### SCENE 07 · Two circles · 129.267–146.967 (2:09.27–2:26.97, 17.7 s)

**Engine:** Manim  
**Why it works:** The smallest possible step up: one extra circle, and the heights simply add.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 130.80 | `one smooth wave` | Eyebrow **02 · STACKING CIRCLES**. The sine from S06 dims to a ghost | 0.6 s |
| 132.76 | `add a second` | A dashed empty circle appears on the tip (anticipation) | 0.4 s |
| 134.52 | `smaller circle` | It fills in (r = ⅓), turning three times as fast, blue | grow 0.7 s |
| 140.04 | `two motions` | The pen now rides the small rim. The camera eases in slightly | 0.8 s |
| 142.36 | `first height` | A silver vertical bar next to the track shows the first circle's height | 0.5 s |
| 143.09 | `plus the second` | A blue bar stacks on top; the sum lands exactly on the gold marker | 0.5 s |
| 145.86 | `little ripple` | The new gold trail scrolls out with a ripple over the ghost sine | continuous |

### SCENE 08 · One third, one fifth, one seventh · 146.967–168.800 (2:26.97–2:48.80, 21.8 s)

**Engine:** Manim (≤ 4 circles) + `SpectrumStrip` (first appearance: "the list")  
**Why it works:** The recipe grows one term at a time, then the viewer is asked to guess (rule 15).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 148.52 | `deliberate` | Reset to one circle of radius 4/π against a target height of 1 (two faint hairlines). A small `SpectrumStrip` appears bottom-right with one bar at speed 1 | 0.8 s |
| 150.48 | `a little taller` | The radius visibly overshoots the hairline: a tiny bracket shows the extra (0.273) | 0.6 s |
| 154.34 | `three times as fast` | Circle 2 (×3) attaches. Bar at 3 rises | 0.7 s |
| 155.76 | `one third` | Label `⅓` flashes beside it | 0.3 s |
| 158.21 | `five times as fast` | Circle 3 (×5), bar at 5 | 0.7 s |
| 159.58 | `one fifth` | Label `⅕` | 0.3 s |
| 161.26 | `seven times` | Circle 4 (×7), bar at 7 | 0.7 s |
| 162.26 | `one seventh` | Label `1/7` | 0.3 s |
| 165.25 | `take a moment to guess` | **Pause and predict:** motion slows to a crawl, the wave breathes, nothing new appears | 0.4 s |
| 167.52 | `turning into` | Hold through the 1.2 s pause | — |

### SCENE 09 · A square wave · 168.800–186.217 (2:48.80–3:06.22, 17.4 s)

**Engine:** `EpicyclePlate` (10 → 200 circles) + Manim overlay (counter, ghost, strip)  
**Why it works:** The answer to the guess, with the counter locked to the spoken numbers.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 169.78 | `top flatten` | Circles keep arriving; the trail's crest visibly flattens | 1.0 s |
| 173.42 | `ten circles` | Counter top-right: **10**. The strip fills to 10 bars | 0.6 s |
| 174.74 | `fifty` | **50**. The chain is a dense spiral of tiny rims | 0.6 s |
| 175.97 | `two hundred` | **200**. The strip is a fine comb | 0.6 s |
| 178.08 | `square wave` | The ideal square wave appears as a dashed ghost exactly under the gold trace | 0.6 s |
| 179.18 | `flat on top` | Hairline highlight on the tops | 0.4 s |
| 180.19 | `flat on the bottom` | On the bottoms | 0.4 s |
| 181.52 | `straight walls` | On the walls | 0.4 s |
| 185.00 | `sharp corners` | A light sweep from the chain (left) to a corner (right): circles in, corners out | 0.9 s |

### SCENE 10 · The spike that never shrinks · 186.217–204.617 (3:06.22–3:24.62, 18.4 s)

**Engine:** Manim (partial sums computed at high resolution near the jump)  
**Why it works:** Plants "sharp corners are expensive" with a red marker (promise P4).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 186.94 | `closely` | Zoom 6× onto one jump of the square wave | 1.2 s `smooth` |
| 190.30 | `small spike` | The overshoot crest gets a red dot (`SPIKE`) | 0.4 s |
| 191.76 | `more circles` | N steps 10 → 50: the spike narrows toward the wall. The old version stays as a fading ghost | 0.7 s |
| 193.32 | `thinner` | N → 200: thinner again | 0.7 s |
| 194.16 | `never gets any shorter` | A red hairline at the crest height stays put while every version touches it | 0.6 s |
| 196.66 | `nine percent` | A small bracket from the top of the wave to the hairline: `≈ 9\%` of the jump | 0.6 s |
| 199.44 | `gibbs phenomenon` | The name sets small in Inter Light beside the bracket | 0.6 s |
| 203.48 | `expensive` | Zoom out. A small **red corner marker** docks top-right and stays until S26. The square wave detaches and floats free (hand-off) | 0.8 s |

## CH3

### SCENE 11 · A hot ring · 204.617–228.117 (3:24.62–3:48.12, 23.5 s)

**Engine:** skia type + moderngl `HeatRingPlate` + Taichi flame/frost particles  
**Why it works:** Mode switch to history and physics (rule 10). The ring is the square wave in a new body. Pays off "of all things, heat" (P3).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 205.62 | `wondering` | Eyebrow **03 · FOURIER'S HOT RING**. The floating square wave fades to 30 % | 0.6 s |
| 210.72 | `heat` | The ring from the intro teaser returns, larger, then dims to wait | 0.8 s |
| 212.04 | `eighteen oh seven` | Large faint "1807" in Space Grotesk at 12 % opacity, behind everything | fade 0.8 s |
| 215.12 | `spreads through a solid` | A short metal bar with one hot spot: the glow spreads out along it (1D heat equation, computed) | 1.6 s |
| 216.98 | `metal ring` | The bar bends round into a brushed-metal torus at 30° pitch, slowly rotating | 1.2 s |
| 218.94 | `flame` | Ember particles lick one half, which glows orange-white | 1.0 s |
| 220.58 | `ice` | Frost particles on the other half, which cools to deep indigo | 1.0 s |
| 221.34 | `let it go` | The particles stop | 0.6 s |
| 222.67 | `hot on one side` | A temperature crown rises over the ring: the hot half up, the cold half down | 0.8 s |
| 225.22 | `unroll the ring` | The ring **unrolls** into a straight bar with its profile drawn in gold above it: the square wave, matching the S10 ghost. It rolls back up, keeping the crown | 1.2 s + 1.0 s |

### SCENE 12 · Wigglier waves fade faster · 228.117–256.167 (3:48.12–4:16.17, 28.1 s)

**Engine:** `HeatRingPlate` (main ring + three small mode rings) + Manim inset plot  
**Why it works:** Shows why sines are natural: they keep their shape while they fade.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 230.90 | `simple waves` | Three small rings split out to the right with mode 1, 3, 5 crowns (heights 1, ⅓, ⅕ × 4/π) | `LaggedStart` 1.0 s |
| 233.22 | `once` | Ring 1 pulses | 0.4 s |
| 234.70 | `three times` | Ring 3 pulses | 0.4 s |
| 235.90 | `five` | Ring 5 pulses | 0.4 s |
| 240.54 | `keeps its shape` | Time starts (κ so that mode 1 fades over ~6 s). Each small crown shrinks **without changing shape** | continuous |
| 244.60 | `faster it fades` | Ring 5 is nearly flat already, ring 1 barely changed | — |
| 247.12 | `nine times as fast` | Inset plot: `e^{−t}` and `e^{−9t}` (computed). The steep one is labeled `×9` | 0.8 s |
| 249.52 | `sharp edges melt` | The main crown loses its corners first (exact sum of the decaying modes) | continuous |
| 252.60 | `one gentle wave` | The main crown is now just mode 1. A ghost of ring 1 overlays it: a match | 0.6 s |
| 255.04 | `even warmth` | The crown flattens; the ring settles to one mid-tone | 1.2 s |

### SCENE 13 · Nobody believed it · 256.167–272.283 (4:16.17–4:32.28, 16.1 s)

**Engine:** Manim  
**Why it works:** The doubt is answered by what the viewer has already seen.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 259.74 | `sudden jumps` | Left: a jagged gold temperature profile with jumps | 1.0 s |
| 261.42 | `sum of smooth waves` | Right: `= \sum` and a column of three small sines | 0.8 s |
| 265.41 | `didn't buy it` | The `=` flickers into a dim `\overset{?}{=}` | 0.6 s |
| 268.14 | `watched it happen` | A 2 s replay of S09 (10 → 200 circles). The `?` dissolves | 2.0 s |
| 270.98 | `back to our drawing` | The ring crown unrolls into a line, which winds back into a circle with an arm: the hand-off to Ch4 | 1.4 s |

## CH4

### SCENE 14 · Use both directions · 272.283–280.783 (4:32.28–4:40.78, 8.5 s)

**Engine:** Manim (`EpicycleChain` + two `ShadowWave`s)  
**Why it works:** Midpoint re-hook (rule 11): the half we ignored is the key to drawing.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 274.18 | `height of the tip` | Eyebrow **04 · WAVES BECOME DRAWINGS**. The two-circle chain, with its height wave on the right | 0.8 s |
| 276.24 | `left and right` | A second projection runs down from the pen; the left-right motion writes its own wave going down the screen | 1.0 s |
| 277.64 | `use both` | Both projection lines converge back on the pen. The two waves fade | 0.6 s |
| 279.46 | `right on the page` | The pen draws its 2D path in gold ink. A faint clef ghost flashes behind it for 0.6 s | continuous + flash |

### SCENE 15 · Circles in the sky · 280.783–296.467 (4:40.78–4:56.47, 15.7 s)

**Engine:** skia starfield (seeded) + Manim (two-circle geocentric Mars, computed)  
**Why it works:** A short history aside that proves the drawing idea is old and real. **First cut candidate** if needed.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 282.42 | `very old` | The stage becomes a night sky. A small Earth dot at center | 1.0 s |
| 285.42 | `astronomers` | A faint Mars dot wanders across the stars | 0.8 s |
| 287.12 | `circles riding on circles` | Two circles appear (Mars orbit − Earth orbit). The planet traces **retrograde loops** in gold | 3.0 s |
| 289.52 | `wrong about how the sky works` | Aside: the view re-centers on the Sun; the loops untangle into plain orbits, then re-center back | 1.5 s |
| 291.70 | `right about the circles` | The rims brighten | 0.6 s |
| 295.10 | `almost any path` | The stars fade out; the gold loops remain on black | 0.8 s |

### SCENE 16 · Plus, minus, zero · 296.467–310.767 (4:56.47–5:10.77, 14.3 s)

**Engine:** Manim  
**Why it works:** Introduces the color code for direction before it is needed.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 297.72 | `direction matters` | Stage clears to three empty slots | 0.4 s |
| 300.30 | `counterclockwise` | Left: a circle turning counterclockwise, blue rim | 0.8 s |
| 302.26 | `positive speed` | Label `+1` | 0.4 s |
| 303.34 | `clockwise` | Middle: one turning clockwise, orange rim | 0.8 s |
| 304.32 | `negative speed` | Label `−1` | 0.4 s |
| 306.30 | `speed zero` | Right: a green arm that doesn't turn. Label `0` | 0.6 s |
| 309.02 | `where the drawing sits` | The green arm stretches and swings, and a small gold loop on its tip moves with it: it only places the drawing | 1.2 s |

### SCENE 17 · The friendly example · 310.767–330.717 (5:10.77–5:30.72, 19.9 s)

**Engine:** Manim (`EpicycleChain`) + small `EpicyclePlate` still for the inset  
**Why it works:** Plants the example that the sanity check in S22 pays off (P6), and partly answers P1.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 311.78 | `friendly example` | The stage clears to center | 0.6 s |
| 314.64 | `big circle` | A blue circle, r = 1, speed +1 | 0.8 s |
| 318.05 | `one ninth` | An orange circle, r = 1/9, on its tip. A violet arc marks its **half-turn** start | 0.8 s |
| 319.88 | `backward three times` | The small circle spins clockwise, three times as fast | — |
| 324.32 | `rounded square` | The pen traces the rounded square in gold | 4 s loop |
| 326.28 | `square from the beginning` | The intro square appears as a dashed ghost around it | 0.8 s |
| 327.92 | `first two circles` | An inset of the intro's square chain lights its first two circles: the same two | 0.8 s |

### SCENE 18 · Every whole number speed · 330.717–351.300 (5:30.72–5:51.30, 20.6 s)

**Engine:** Manim (`SpectrumStrip` as an empty "speed rack")  
**Why it works:** States the real question with an empty slot for every answer (open loop).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 333.20 | `every whole number speed` | The rounded square moves up. Below it, a row of **empty dashed slots** for speeds | 0.8 s |
| 334.68 | `zero` | Slots get their labels in time with the words: 0, 1, −1, 2, −2 … | `LaggedStart` across the list |
| 337.90 | `and so on` | More slots fade in toward both edges | 0.6 s |
| 341.30 | `its size` | Each slot shows a faint empty radius knob | 0.5 s |
| 342.50 | `starting angle` | … and a faint violet angle tick | 0.5 s |
| 344.82 | `real question` | Everything dims except the rack | 0.6 s |
| 346.34 | `hand you a drawing` | The treble clef ghost slides in above the rack | 0.8 s |
| 349.98 | `every circle` | All slots pulse once, still empty | 0.6 s |

## CH5

### SCENE 19 · Speed zero is the balance point · 351.300–382.017 (5:51.30–6:22.02, 30.7 s)

**Engine:** Manim  
**Why it works:** Warm-up case first. The averaging picture is built before any formula.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 352.10 | `warm up` | Eyebrow **05 · SPIN AND AVERAGE**. The rack's slot `0` lights green | 0.6 s |
| 355.94 | `never moves` | A still green arm from the origin | 0.6 s |
| 357.94 | `center of the drawing` | The **bean** loop (gold) appears, offset from the origin | 1.0 s |
| 361.20 | `squiggly shape` | The bean wobbles once; a dim `?` ping at its middle | 0.6 s |
| 364.94 | `spread dots` | The pen goes around once and drops 60 gold dots, evenly in time (denser where it moves slowly) | 2.0 s |
| 368.10 | `average all their positions` | Every dot sends a faint line to their mean; the dots slide in and merge into the **green balance point** | `LaggedStart` 1.2 s |
| 371.02 | `balance point` | The green dot pulses. The green arm stretches from the origin to it: an exact match | 0.8 s |
| 376.66 | `every other circle` | The bean's other four arms appear faintly, spinning | 0.6 s |
| 380.18 | `averages out to nothing` | Inset: one spinning arm drops 12 dots around a circle; their average sits exactly at the center, grey | 1.2 s |

### SCENE 20 · Spin averages to zero · 382.017–389.317 (6:22.02–6:29.32, 7.3 s)

**Engine:** Manim  
**Why it works:** States the key idea as two icons and keeps them on screen (rule 6).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 383.36 | `key idea` | Stage clears | 0.4 s |
| 384.56 | `things that spin` | Left icon: a spinning arm whose dots average to the center (grey) | 0.6 s |
| 387.46 | `stand still` | Right icon: a still arm whose dots all sit at its tip, so the average is the tip (green) | 0.6 s |
| 388.40 | `dont` | Both icons shrink into a small **rule card** docked bottom-left for the rest of Ch5 | 0.6 s |

### SCENE 21 · Turn the drawing backward · 389.317–417.983 (6:29.32–6:57.98, 28.7 s)

**Engine:** Manim (`EpicycleChain(rotating_frame=1)`)  
**Why it works:** The one idea of the video, shown rather than stated (rule 14): the camera turns, and the matching circle stops.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 390.42 | `speed one circle` | The bean's 5-arm chain is drawn. The speed-1 arm gets a soft highlight | 0.6 s |
| 392.64 | `cant see it` | Its dots average to nothing: a grey ping at the center | 0.6 s |
| 394.86 | `stand still` | The speed-1 arm glows briefly (the hope) | 0.4 s |
| 396.54 | `heres the trick` | Hold. The pen keeps going round | — |
| 399.15 | `turn the whole drawing backward` | The **whole stage rotates clockwise**, one turn per loop. A thin orange ring with an arrow at the stage edge shows the backward turn | 4 s loop |
| 407.85 | `so it stops` | In the turning view, the speed-1 arm **freezes**. It turns green and its glow steadies | 0.6 s |
| 410.74 | `still spinning` | The other arms keep spinning; their labels update: 0 → −1, +2 → +1, −1 → −2, −2 → −3 | 0.8 s |
| 413.06 | `wash out` | The dots, now wound into a new shape, collapse to their average: a green point exactly at the frozen arm's tip | 1.4 s |
| 416.28 | `frozen in place` | A silver radius bracket and violet angle arc on the frozen arm. Rack slot `1` fills | 0.6 s |

### SCENE 22 · Sanity check · 417.983–438.717 (6:57.98–7:18.72, 20.7 s)

**Engine:** Manim (rounded square, speed dial, `SpectrumStrip`)  
**Why it works:** A case where the viewer already knows the answer (P6).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 418.84 | `sanity check` | The rounded square from S17 returns. A small **speed dial** sits top-center | 0.8 s |
| 422.86 | `backward once` | Dial → 1. The stage turns backward and the dots wind | 1.4 s |
| 426.12 | `tip of the big circle` | The average lands on the big circle's tip (green). Rack bar `1` rises to 1 (blue) | 1.0 s |
| 428.40 | `forward three times` | Dial → −3. The stage turns forward three times per loop | 1.4 s |
| 431.06 | `one ninth` | The average lands **1/9 from center, pointing the opposite way** (violet half-turn arc). Bar `−3` rises to 1/9 (orange) | 1.0 s |
| 432.21 | `just as it should` | Both bars pulse green once | 0.4 s |
| 434.20 | `speed two` | Dial → 2. The stage spins | 1.2 s |
| 435.82 | `falls to zero` | The average lands at the center: a grey ping | 0.8 s |
| 437.30 | `no circle there` | Slot `2` stays empty and dims | 0.4 s |

### SCENE 23 · Spin, then average · 438.717–483.567 (7:18.72–8:03.57, 44.9 s)

**Engine:** Manim (`MathTex` with per-term color)  
**Why it works:** Pays off P2: the muted line from the intro returns to its exact spot and gets its colors in two steps.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 440.02 | `just one idea` | Everything dims except the rule card, which slides to center and grows | 0.8 s |
| 444.79 | `spin the drawing against it` | Card: a turning stage (orange ring) | 0.6 s |
| 446.46 | `take the average` | Card: dots collapsing into a green point. Hold | 0.6 s |
| 448.62 | `line from the beginning` | The card returns to its corner. The muted formula fades in at `RECIPE_POS` (same spot as S03), then glides to center | 0.8 s + 0.8 s |
| 450.13 | `c n` | `c_n` turns green | 0.4 s |
| 451.50 | `integral` | `∫₀¹ … dt` turns silver | 0.4 s |
| 453.36 | `f of t` | `f(t)` turns gold | 0.4 s |
| 454.52 | `e to the minus` | `e^{−2πint}` turns orange | 0.4 s |
| 460.26 | `two steps` | Two brackets under the formula: ① under `f(t) e^{−2πint}`, ② under `∫₀¹ … dt` | 0.6 s |
| 462.50 | `pens position` | `f(t)` lifts; a tiny inset of the pen on the bean appears beside it | 0.8 s |
| 468.00 | `turns the drawing backward` | A small clockwise arrow icon beside `e^{−2πint}` | 0.6 s |
| 469.46 | `n times per loop` | The `n` inside it pulses blue | 0.4 s |
| 472.26 | `complex numbers` | Callback inset: video 001's quarter-turn arrow on the unit circle, spinning | 0.6 s in, 0.6 s out |
| 477.82 | `takes the average` | Bracket ② and `∫₀¹ … dt` brighten. The mini inset shows dots collapsing to their mean | 1.0 s |
| 480.47 | `spin then average` | Insets fade; the formula glows once and a light sweep crosses it | 1.0 s |
| 482.50 | `all it says` | Hold | — |

## CH6

### SCENE 24 · Two hundred and one circles · 483.567–501.733 (8:03.57–8:21.73, 18.2 s)

**Engine:** Manim (dots, dial, strip) → `EpicyclePlate` (chain)  
**Why it works:** Bars become circles: the transform that ties "the list" to "the machine" (rule 9).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 484.50 | `real test` | Eyebrow **06 · DRAWING ANYTHING**. The formula shrinks to top-right and stays | 0.8 s |
| 486.22 | `treble clef` | The clef outline appears as a silver ghost | 0.8 s |
| 487.10 | `one continuous line` | A spark runs along the whole outline once | 1.2 s |
| 489.28 | `thousand dots` | 1,000 gold dots sprinkle along it | 1.0 s |
| 491.98 | `minus one hundred` | The dial counter sweeps −100 → 100. Behind it the dot cloud spins, and the `SpectrumStrip` fills bar by bar | until `spin and average` |
| 496.13 | `two hundred and one` | The strip lands complete: 201 bars, blue and orange | 0.4 s |
| 498.90 | `biggest to smallest` | The bars **re-order** by height, biggest first | 1.2 s |
| 500.64 | `tip to tail` | Each bar lifts off, curls into a circle of that radius, and snaps onto the end of the growing chain | `LaggedStart` 1.6 s |

### SCENE 25 · One, five, twenty, two hundred · 501.733–516.983 (8:21.73–8:36.98, 15.2 s)

**Engine:** `EpicyclePlate` + `InkParticles`  
**Why it works:** The spectacle rebuilt from scratch (P5), with the counter locked to the spoken numbers.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 502.22 | `one circle` | Counter **1**. The chain is just the biggest circle; the pen traces a plain loop | 1.6 s loop |
| 504.42 | `five` | **5**: a rough blob. The previous ink stays as a faint ghost | 1.6 s |
| 506.42 | `twenty` | **20**: the clef starts to read | 1.6 s |
| 508.76 | `two hundred` | **200** (all 201): the chain traces the clef almost perfectly, sparks shedding; the ghost outline sits exactly under it | 3.0 s |
| 512.70 | `up close` | The camera dives **40×** onto the pen and follows it. The last dozen tiny circles whirl visibly; the ink stays crisp | 1.6 s `smooth` |
| 515.76 | `the others cant` | Toggle: the last 50 circles switch off and the ink at this zoom goes visibly wrong (a smoothed corner); they switch back and the detail returns. Pull back | 0.3 + 0.8 + 0.3 s |

### SCENE 26 · Why sharp corners are expensive · 516.983–540.800 (8:36.98–9:00.80, 23.8 s)

**Engine:** Manim  
**Why it works:** Pays off P4 and P1: two squares compared side by side.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 517.20 | `remember` | The red corner marker from S10 (top-right) pulses and flies to center | 0.8 s |
| 521.44 | `first few circles` | The clef drawn with 10 circles: its smooth arcs light up, already right | 1.0 s |
| 523.88 | `all the rest` | Its sharp turns flash red: still rough | 0.6 s |
| 525.38 | `pen jumps` | Left panel: the square wave with its strip | 0.8 s |
| 529.19 | `one third` | `⅓` writes above bar 3 | 0.4 s |
| 530.18 | `one fifth` | `⅕` above bar 5 | 0.4 s |
| 532.14 | `turns a corner` | Right panel: the square loop and its strip; its bars drop off visibly faster | 0.8 s |
| 535.60 | `one ninth` | `1/9` | 0.4 s |
| 536.43 | `one twenty fifth` | `1/25` | 0.4 s |
| 539.22 | `fewer circles` | A third mini panel: a smooth oval loop whose strip has only 3 bars. The red marker dissolves (promise kept) | 1.0 s |

### SCENE 27 · Sound and pictures · 540.800–564.500 (9:00.80–9:24.50, 23.7 s)

**Engine:** Manim (synthetic waveforms and spectra) + skia piano keys + scipy DCT + skia image tiles  
**Why it works:** Pays off the piano chord (P7) and shows the idea in everyday technology.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 542.60 | `everywhere` | The chain shrinks into a small icon at top-left | 0.6 s |
| 544.24 | `piano chord` | The intro's three keys and merging waves return (callback) | 0.6 s in |
| 545.62 | `sound is a wave` | The gold chord waveform slides left and becomes the start of a longer sound wave | 0.8 s |
| 548.76 | `singer and a violin` | Two stacked waveforms (synthetic, seeded: same fundamental, different harmonic recipes), each with its strip on the right | 1.0 s |
| 551.58 | `slowest circle` | The first bar of both strips lights up: same speed, aligned | 0.6 s |
| 554.32 | `faster circles on top` | Their other bars differ and glow | 0.6 s |
| 559.38 | `shrink photos` | An image (a frame of this video's own clef render) splits into an 8×8 block grid | 1.0 s |
| 560.98 | `keeping the big circles` | A threshold line sweeps across one block's coefficient bars; small ones fall away | 1.0 s |
| 563.50 | `wont notice` | The image re-forms from about 10 % of its coefficients (real `scipy.fft.dctn`). A thin wipe compares it to the original: nearly the same | 1.4 s |

## OUTRO

### SCENE 28 · What we built · 564.500–596.900 (9:24.50–9:56.90, 32.4 s)

**Engine:** Manim + skia glass cards (`cards.py`)  
**Why it works:** Each recap sentence is a visual callback, not a spoken list (rule 17).

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 565.10 | `step back` | Pull back; four empty glass cards fade up in a row | `LaggedStart` 0.8 s |
| 568.94 | `simplest wave` | Card 1 plays live: circle → sine, with the three chips | 0.8 s |
| 572.83 | `stack circles` | Card 2: stacked circles | 0.8 s |
| 579.42 | `sharp corners` | … building a square wave with its sharp corners | 0.6 s |
| 580.76 | `fouriers insight` | Card 3 lights | 0.4 s |
| 586.10 | `two directions` | Card 3: a chain drawing the rounded square | 0.8 s |
| 590.84 | `spin the drawing backward` | Card 4: a turning stage and a frozen green arm. The recipe in full color writes under the cards | 0.8 s |
| 594.04 | `stands still` | Card 4's frozen arm glows green | 0.4 s |
| 595.94 | `looking for` | All four cards glow once | 0.6 s |

### SCENE 29 · What comes next · 596.900–615.050 (9:56.90–10:15.05, 18.1 s)

**Engine:** Manim  
**Why it works:** Honest look ahead (P8) without opening anything this video can't keep.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 598.12 | `quietly assumed` | The cards fade | 0.6 s |
| 600.26 | `drawings repeat` | A pen finishes a loop | 0.8 s |
| 603.26 | `where it started` | It lands on its start point, which pings: the loop closes | 0.4 s |
| 605.80 | `never repeats` | A gold sound wave with no repeating pattern (deterministic chirp with a noise envelope) scrolls past | 1.2 s |
| 608.74 | `every possible speed` | The integer speed rack's separate bars **melt together** into one continuous glowing band | 1.4 s |
| 612.22 | `fourier transform` | "Fourier transform" in small Space Grotesk under the band, with a light sweep | 0.8 s |
| 614.10 | `go next` | The band drifts off and fades to black | 0.8 s |

### SCENE 30 · Just circles, going round · 615.050–621.567 (10:15.05–10:21.57, 6.5 s)

**Engine:** `EpicyclePlate` in **2.5D** (plane tilted ~25°, slow yaw orbit, rims in perspective, soft floor reflection) + `InkParticles`  
**Why it works:** Ends on the payoff (rule 19): the opening image, now understood.

| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |
|---|---|---|---|
| 615.05 | (frame 0) | The 201-circle clef chain fades up from black and the plane tilts into perspective | 1.2 s |
| 615.26 | `for now` | The pen starts its loop. Period = `FINALE_LOOP`, so it closes as "round" ends | `linear`, ease out on the last 0.4 s |
| 616.60 | `one more time` | Camera yaw orbit begins | continuous |
| 619.65 | end of `round` | The clef closes. A soft flash runs along the outline | 0.4 s |
| 620.34 | `thanks for watching` | The chain fades; the gold clef holds, glowing, and the sparks settle | 0.8 s |
| 621.19 | end of `watching` | Fade to black, landing on the last frame of the audio | to the end |

---

## Production notes

- **Hand-offs (`PREVIOUS`):** every scene starts from the last frame of the one before. Pairs that must match exactly: S01 → S02 (clef chain mid-pose), S02 → S03 (black), S03 → S04 (single blue circle at the left third), S06 → S07 (flat sine), S10 → S11 (floating square wave), S13 → S14 (circle with an arm), S16 → S17, S17 → S18 (rounded square), S18 → S19 (rack with slot 0), S20 → S21 (rule card bottom-left), S23 → S24 (formula), S25 → S26 (clef + red marker top-right), S28 → S29 (cards).
- **Render cost on this machine:** GL scenes (S01, S02, S09, S11, S12, S24, S25, S30) render on the R4 through moderngl; everything else is Manim/Cairo on 2 CPU cores. Preview with `-ql`, render finals in the background. S06 depends on the pyvista lab check.
- **Shared state between scenes** lives in `scenes/shared.py`: `RECIPE_POS`, the clef coefficients (from `aion.drawings.treble_clef(1000)`), `BEAN`, `ROUNDED_SQUARE`, and the stage/post setup. `beats.py` is the single source for `BEAN` and `ROUNDED_SQUARE`; `shared.py` imports them.
- **Determinism:** seed the starfield (S15), particles (S01, S02, S11, S25, S30), the singer/violin synthesis (S27) and the teaser chirp (S29).
