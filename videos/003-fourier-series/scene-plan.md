# 003: Fourier Series. Drawing Anything With Rotating Circles

**Mode:** production · **Status:** ✅ phase 1 approved (revision 2, 2026-11-09). **Superseded by `storyboard.md`** (phase 3, real SRT timings, 30 scenes). Kept as history: scene numbers and times here are the old estimates.

**Pipeline**
1. ⏳ **This file** + `voiceover.md` (plain text with `[pause]` tags, ready for ElevenLabs).
2. ⬜ User generates `assets/audio.mp3`, then exports `assets/normal-subtitle.srt` and `assets/cue-per-word.srt`.
3. ⬜ Chunk every chapter into timed scenes from the SRT (`beats.py` + `storyboard.md`, same method as 002). Every beat below becomes a real timestamp.
4. ⬜ Build the library pieces and run the lab checks, then the scenes. Preview, verify, and render the finals.

Times below are **estimates** (165 words per minute plus 0.6 s per `[pause]`). Phase 3 replaces all of them with SRT times. The **cue key** column names the word that each visual lands on.

## Voice and narrative structure (revision 2)

What we took from the sample transcript (its *style*, never its content):

| Device | Where it's used here |
|---|---|
| Open by pointing at the finished picture: "What you're looking at is…" | Intro, on the clef chain already drawing |
| A first-person guide who talks *with* the viewer: "you and I", "I want you to…", "here's what I find strange" | throughout |
| One everyday analogy, planted early and paid off late | **piano chord** (intro) → singer and violin (Ch6) |
| Show the formula early "just so you'll recognize it later", then dissect it in steps | recipe ghosted in the intro, read in two steps in Ch5 |
| "Start easy", warm-up case first | Ch1 one circle · Ch5 "warm up with speed zero" |
| "You might be wondering why…" / "the short answer is…" | Ch3 opener (heat) |
| Sanity check against a case we already know | Ch5, the rounded square |
| "If you hold on to just one idea…" | Ch5, the spin-and-average rule |
| Name the fancy term after the idea is clear | Gibbs phenomenon, Fourier series, Fourier transform |
| Honest look ahead to the next chapter | Outro, Fourier transform |

## The idea of the video, in one line

**A circle seen from the side is a wave, and enough circles stacked tip to tail can draw anything.** The whole video answers one question from the intro: *how does something that only goes round draw a corner?* The **square** carries that question. It appears as a drawn square in the intro, as a square *wave* in Ch2, as a hot/cold ring in Ch3, as a rounded square (2 circles) in Ch4, is decoded in Ch5, and in Ch6 its circles shrink as 1/n² against the square wave's 1/n. The **treble clef** is the spectacle. It is the first thing on screen, rebuilt from scratch in Ch6, and played one last time to close the video.

## Chapters (estimated)

| Part | Title | Scenes | Est. range | Est. length | Mode (rule 10) |
|---|---|---|---|---|---|
| Intro | Circles that draw | 01–02 | 0:00 – 1:15 | ~75 s | spectacle, question, analogy |
| Ch1 | One circle | 03–05 | 1:15 – 2:25 | ~70 s | 2D geometry, then 3D (spring) |
| Ch2 | Stacking circles | 06–09 | 2:25 – 3:48 | ~83 s | build-up + **pause and predict** |
| Ch3 | Fourier's hot ring | 10–12 | 3:48 – 5:07 | ~79 s | history + 3D physics |
| Ch4 | Waves become drawings | 13–16 | 5:07 – 6:32 | ~85 s | **midpoint re-hook**, astronomy, 2D drawing |
| Ch5 | Spin and average ★ | 17–21 | 6:32 – 9:02 | ~150 s | derivation (the core) |
| Ch6 | Drawing anything | 22–25 | 9:02 – 10:36 | ~94 s | payoff + applications |
| Outro | What we built | 26–28 | 10:36 – 11:40 | ~64 s | recap cards + teaser + final payoff |

Total about **11.1–12.0 min** (1,799 words, 76 pauses) at 174 to 160 words per minute. That's inside the 8–12 min target, but near the top. If the generated audio runs past 12:00, the visual cut is marked ✂ in S25. On the narration side, the first lines to drop are the astronomy paragraph (S14, ~17 s) and the complex-numbers callback sentence (S21, ~5 s).

## Verified math (numpy, 2026-11-09)

| Object | Fact used on screen |
|---|---|
| One circle | tip = r·e^{i(nt+φ)}; height = r·sin(nt + φ). Quarter-turn start → cos |
| Helix | (t, r cos t, r sin t): side shadow = sine, top shadow = cosine |
| **Square wave** | (4/π)·Σ_{odd n} sin(nt)/n. First radius 4/π ≈ 1.273 ("a little taller"). Radii 1, 1/3, 1/5, 1/7 relative |
| **Gibbs** | peak → 1.17898 for a ±1 wave, i.e. **8.95 % of the jump** (checked: 5 terms 1.1823, 25 → 1.1791, 101 → 1.17899, 1001 → 1.17898) |
| **Heat on a ring** | u_t = κ u_θθ. Mode n decays as e^{−κn²t}, so 3× the wiggles → **9×** faster. Square start: u = Σ_{odd} (4/πn) e^{−n²κt} sin nθ |
| Planets | geocentric Mars with circular, coplanar orbits = r_M e^{iω_M t} − r_E e^{iω_E t}: exactly two circles, and it makes the retrograde loops |
| **Square loop** (side 2, constant speed, starting mid-side) | nonzero only for n ≡ 1 (mod 4): c₁ = 1.14632, c₋₃ = −0.12737 (= c₁/9, half-turn start), c₅ = −c₁/25, c₋₇ = c₁/49, c₉ = c₁/81. **Shrinks like 1/n²** |
| **Rounded square** | z = e^{2πit} − (1/9)e^{−2πi·3t}: the first two circles of the square loop, normalized |
| Rotating frame | multiplying by e^{−2πikt} turns speed n into n − k. Average over a loop = c_k |
| Recipe | c_n = ∫₀¹ f(t) e^{−2πint} dt · f(t) = Σ c_n e^{2πint} |
| Piano chord | C major triad (C4 261.63 Hz, E4 329.63, G4 392.00) as three sines → their sum (computed, displayed slowed down) |
| Clef | 1,000 samples, n = −100…100 → 201 circles (FFT), sorted by \|c_n\|, drawing centered so c₀ = 0 |

Every curve, radius, and readout is computed from these with numpy. Nothing is drawn by eye. `aion/fourier.py` gets unit tests against the closed forms above.

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
| **pyvista** | **The spring (Ch1, scene 05)**: a lit, glossy tube helix with sine and cosine shadows on two glass walls, under an orbiting camera. This is the "tube or ribbon curves" case from `advanced-scene-type.md`. It renders off-screen frames that are composited in Manim. **Lab check first** (VTK off-screen on Mesa/R4). Fallback: Manim `ProgressThreeDScene` with a `ParametricFunction` (lines are cheap even on Cairo). |
| **skia-python** | Title plate (`TitlePlate`), chapter eyebrows, glass recap cards (`cards.py`), the starfield in Ch4, line-art piano keys, and the image tiles for the compression demo in Ch6. |
| **numpy / scipy** | All Fourier math (FFT for coefficients), heat solution, chord and voice/violin synthesis, and the real 8×8 DCT compression demo in Ch6 (`scipy.fft.dctn`). |
| **fontTools** (to add) | Pulls the treble clef outline from the **Bravura** music font (SIL OFL, glyph U+E050 `gClef`) as a path. `uv add fonttools` if it isn't already pulled in. |
| ffmpeg | Concatenation and the audio mux, as in 002's `render.py`. |

### New library pieces (built before scenes)
- **`aion/fourier.py`**: `sample_path(path, n)` (arc-length or uniform-time resampling, contour bridging for multi-contour glyphs), `coefficients(points, N)` (FFT, returns `{n: c_n}`), `partial_sum(coeffs, t, order="size")`, `chain_points(coeffs, t)` (every joint position for drawing arms), `square_wave(n_terms)`, `square_loop_coeffs(N)`, `heat_ring(theta, t)`. Unit tests check them against the closed forms in the math table.
- **`aion/components/epicycles.py` → `EpicycleChain`** (Manim): a `ValueTracker` for t, then rims, arms, and pen, with rims colored by speed sign, an optional phase arc, and an ink `TracedPath` with an age fade. `rotating_frame=k` multiplies the whole picture by e^{−2πikt} (Ch5).
- **`aion/components/shadow_wave.py` → `ShadowWave`**: a dashed projection line from the tip to a moving pen that writes the wave. Horizontal or vertical (Ch4 uses both).
- **`aion/components/spectrum.py` → `SpectrumStrip`**: one bar per speed, blue above / orange for negative speeds, green for 0. It can fill live, **sort by size**, and **morph bars into circles** (Ch6). It is the "list" from Ch2, the rack in Ch4, and the readout in Ch5 and Ch6.
- **`aion/components/epicycle_gl.py` → `EpicyclePlate`** (moderngl): instanced rims and arms, an ink ribbon with constant screen width and age-faded glow, camera `(center, zoom, tilt, yaw)` trackers, and `project()`. The ink is re-evaluated from the coefficients every frame, so it stays sharp at 40× zoom.
- **`aion/components/heat_ring.py` → `HeatRingPlate`** (moderngl): a torus with temperature `u(θ, t)` as height and `HEAT_RAMP` color.
- **`aion/components/ink_particles.py` → `InkParticles`** (Taichi + moderngl).
- **Drawing assets** in `assets/drawings/`: `treble_clef.svg` (from Bravura), the square loop (analytic), the "bean" loop for Ch5 (built from 5 known circles, so the answer is exact).

### Lab checks before production (`lab/2026-11-1x-epicycles/`)
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

| # | Promise (where it's opened) | Paid off |
|---|---|---|
| P1 | "How does something that only goes round draw a corner?" (S02) | S08 square wave, S16 rounded square, S24 1/n² |
| P2 | "I'll put it on screen now, just so you'll recognize it later." (S02, ghosted formula) | S21, read in two steps |
| P3 | "while studying, of all things, heat" (S02, ring flash) | S10–S12 |
| P4 | "Sharp corners are expensive." (S09, red marker) | S24 "Remember how I said…" |
| P5 | The clef on screen from frame 0 (S01) | S22–S23 rebuilt from scratch, S28 final play |
| P6 | "Here's a friendly example we'll keep coming back to." / "Its first two circles are exactly these." (S16) | S20 sanity check finds 1/9 · S24 |
| P7 | The piano chord (S02) | S25 "Think back to the piano chord." |
| P8 | "That's the Fourier transform, and it's where we'll go next." (S27) | next video |

---

# INTRO · Circles that draw (~0:00–1:15)

### SCENE 01 · `scene_01_hook.py` · `Scene01Hook` · ~0:00–0:15
**Narration:** "What you're looking at is a chain of circles … and it draws a treble clef."
**Engine:** moderngl `EpicyclePlate` + Taichi `InkParticles` + bloom.
**Why it works:** like the sample's opening, it starts on the finished picture and promises to build it (rules 1, 3). The strangest fact comes before any explanation.

| Cue key | What happens | Anim |
|---|---|---|
| (frame 0) | Already in motion: a chain of ~60 circles turns slowly at the center of the black stage. Rims are faint silver, the pen is gold. The camera drifts in from 1.08× | `smooth` 3 s drift |
| `chain of circles` | A light sweep runs down the chain from the root joint to the pen, joint by joint | 1.2 s |
| `edge of the one before` | Close beat: the camera tracks one joint for ~1 s, showing one circle riding the rim of the one before | 1.0 s |
| `own steady speed` | Rims tint blue or orange by spin direction | 0.5 s |
| `very last circle` | The pen ignites: bloom up, first sparks | 0.4 s |
| `treble clef` | The chain traces the **treble clef** in one ~6 s loop: gold ink with a comet glow, sparks shedding from the pen. The pace is set so the loop closes in the pause after "clef" | `linear` t, ease out on the last 0.5 s |

### SCENE 02 · `scene_02_corner.py` · `Scene02Corner` · ~0:15–1:15
**Narration:** "Here's what I find strange about this … just so you'll recognize it later."
**Engine:** `EpicyclePlate` (square chain), `HeatRingPlate` (1.5 s teaser), Manim (piano waves, formula), skia `TitlePlate` and piano-key line art.
**Why it works:** the square is the most extreme "wrong intuition" case (rule 4). The question is asked out loud and then held (rule 15). The analogy gives the viewer a familiar picture before any math. The formula is planted, unexplained (rule 8).

| Cue key | What happens | Anim |
|---|---|---|
| `roundest thing` | The clef's chain fades to 15 %. One circle at the root brightens alone | 0.8 s |
| `no corners` | A faint dashed square ghost flickers around that circle and dissolves: what a circle is *not* | 0.5 s in / 0.8 s out |
| `sharp turns` | The chain is back: a push in on the clef's sharpest turn (bottom hook), then pull back | camera 1.2 s |
| `square` | **No cut:** the chain re-tunes its circles into the square loop's (speeds 1, −3, 5, −7, …, 60 circles), and the ink morphs clef → square | coefficient tween 1.4 s |
| `four perfect corners` | The camera dives into one corner (8×). Tiny circles whirl there, and the ink corner stays razor sharp | 1.5 s `smooth` |
| `draw a corner` | Freeze. Everything dims to 20 % except the corner and the pen. Hold through the `[pause]` | 0.4 s |
| `fourier series` | **"Fourier Series"** sets in Space Grotesk with a soft glow and a warm `light` sweep | `TitlePlate` 1.1 s |
| `joseph fourier` | A small name line under the title, Inter Light | 0.6 s |
| `heat` | Teaser flash: a glowing metal ring, half ember and half ice (from S10's renders) | cross-fade in 0.4 s, hold 1.2 s, out 0.4 s |
| `any loop` | Gallery: three small chains draw at once (clef, square, a smooth bean), ~3 s | `LaggedStart` 0.25 |
| `chord on a piano` | The gallery clears. A line-art octave of piano keys (skia), with three keys (C, E, G) pressing down in turn | 0.8 s |
| `one sound` | Three thin sine waves (blue-tinted silver) rise from the three keys and **merge into one gold waveform** | 1.2 s |
| `few notes` | The gold waveform briefly splits back into its three waves, then re-merges | 0.6 + 0.6 s |
| `pick out the circles` | The same move on a shape: a gold rounded square splits into its two circles, which re-merge | 1.2 s |
| `recipe` | Everything fades except one circle on the left | 0.8 s |
| `on screen now` | The recipe `c_n = ∫₀¹ f(t) e^{−2πint} dt` writes on in muted silver at 60 %, upper right (its colors appear only in Ch5) | `Write` 1.2 s |
| `recognize it later` | The formula shrinks into the top-right corner and fades to 0 (its spot is kept for S21). The single circle remains: the hand-off to Ch1 | 0.8 s |

# CH1 · One circle (~1:15–2:25)

### SCENE 03 · `scene_03_one_circle.py` · `Scene03OneCircle` · ~1:15–1:40
**Narration:** "As with anything new, it's best to start easy … let that height leave a trail."
**Engine:** Manim (`EpicycleChain` with 1 circle, `ShadowWave`).
**Why it works:** concrete before general (rule 13). One focal point, the tip's height.

| Cue key | What happens | Anim |
|---|---|---|
| `start easy` | Eyebrow **01 · ONE CIRCLE** (top-left) | 0.6 s |
| `single circle` | The circle slides to the left third (center x = −4) | 1.0 s |
| `arrow` | A silver arm grows from the center to the rim, with the pen at its tip | `GrowArrow` 0.6 s |
| `turning steadily` | It turns counterclockwise, one turn per 4 s, and keeps turning for the whole chapter | `linear` |
| `how high its tip is` | The rest of the circle dims to 40 %. A dashed horizontal line runs from the pen to a vertical track just right of the circle, where a gold marker rides up and down | 0.6 s |
| `up down` | A short glow pulse at the top and the bottom of the track, in time with the words | `there_and_back` |
| `time` | A time axis draws to the right of the track (hairline, no numbers) | 0.8 s |
| `trail` | The marker leaves a gold trail that scrolls right: the wave is born | continuous |

### SCENE 04 · `scene_04_three_settings.py` · `Scene04ThreeSettings` · ~1:40–2:09
**Narration:** "What you get is a sine wave … That's everything one circle can do."
**Engine:** Manim.
**Why it works:** each setting changes exactly one thing, with a ghost of the "before" wave left behind to compare (rules 12, 14).

| Cue key | What happens | Anim |
|---|---|---|
| `sine wave` | Label `\sin t` (gold) settles above the wave's crest | `Write` 0.6 s |
| `seen from the side` | 2.5D beat: the circle tilts about its vertical axis to edge-on and collapses into a vertical line, with the pen bouncing up and down. It then tilts back | 1.0 s + 0.8 s |
| `three settings` | Three small glass chips appear under the stage: **size · speed · start** | `LaggedStart` 0.15 |
| `its size` | Chip 1 lights. The radius grows 1 → 1.5 and the wave grows taller. The old wave stays as a dim ghost | radius tween 1.0 s |
| `its speed` | Chip 2 lights. The turn rate doubles and the wave compresses to twice as many wiggles. Ghost kept | 1.0 s |
| `where it starts` | Chip 3 lights. A **violet arc** shows a quarter-turn head start. The arm jumps ahead and the whole wave slides left by a quarter period (it becomes a cosine) | arc 0.6 s, slide 0.9 s |
| `everything one circle can do` | The formula `r\,\sin(n t + \varphi)` assembles from the three chips: r silver, n blue, φ violet | `TransformMatchingTex` 1.2 s |

### SCENE 05 · `scene_05_spring.py` · `Scene05Spring` · ~2:09–2:25
**Narration:** "There's another view I really like … Two shadows of one turning motion."
**Engine:** **pyvista** off-screen frames (glossy gold tube helix, glass side wall and floor, soft key light), composited into Manim with `sin`/`cos` labels pinned via a shared camera matrix. Fallback: Manim `ProgressThreeDScene`.
**Why it works:** the 2D→3D mode switch (rule 10). One object, two shadows: a sine and a cosine are the same motion.

| Cue key | What happens | Anim |
|---|---|---|
| `slide the circle` | The flat S04 frame tilts into 3D (¾ view). The circle now slides along the time axis | camera 1.2 s |
| `spring` | Its tip leaves a glowing gold **tube helix** | continuous |
| `from the side` | The camera orbits to a pure side view. The helix's shadow on the back wall is a sine. Label `\sin t` | orbit 1.4 s |
| `from above` | The camera rises to a top view. The floor shadow is a cosine. Label `\cos t` | 1.4 s |
| `two shadows` | Back to ¾ view, with both shadows lit at once | 1.2 s |
| (end) | The camera settles to the side view, so the scene ends on a flat sine wave: the hand-off to Ch2 | 0.8 s |

# CH2 · Stacking circles (~2:25–3:48)

### SCENE 06 · `scene_06_two_circles.py` · `Scene06TwoCircles` · ~2:25–2:48
**Narration:** "One circle gives you one smooth wave … The wave picks up a little ripple."
**Engine:** Manim.

| Cue key | What happens | Anim |
|---|---|---|
| `add a second` | Eyebrow **02 · STACKING CIRCLES**. The S05 sine dims to a ghost | 0.6 s |
| `smaller circle` | A circle (r = ⅓) grows on the tip of the first. It turns three times as fast (blue) | grow 0.7 s |
| `two motions` | The pen now rides the small rim. The camera eases in slightly | 0.8 s |
| `first height` | A silver vertical bar next to the track shows the first circle's height | 0.5 s |
| `plus the second` | A blue bar stacks on top of it, and the sum lands on the gold marker | 0.5 s |
| `ripple` | The new trail (gold) scrolls out with a ripple over the ghost sine | continuous |

### SCENE 07 · `scene_07_square_build.py` · `Scene07SquareBuild` · ~2:48–3:11
**Narration:** "Now let's be more deliberate … What do you think this is turning into?"
**Engine:** Manim (≤ 4 circles) + `SpectrumStrip` (first appearance: "the list").
**Why it works:** the viewer watches the recipe grow one term at a time, then is asked to guess (rule 15).

| Cue key | What happens | Anim |
|---|---|---|
| `deliberate` | Reset to one circle of radius 4/π (relative to a target height of 1, marked by two faint hairlines). A small `SpectrumStrip` appears at the bottom right with one bar at speed 1 | 0.8 s |
| `a little taller` | The radius visibly overshoots the hairline: a tiny bracket shows the extra | 0.6 s |
| `three times` | Circle 2 (×3, ⅓) attaches. The bar at 3 rises to ⅓. Labels `×3`, `⅓` flash next to it | 0.7 s |
| `five times` | Circle 3 (×5, ⅕), bar at 5 | 0.7 s |
| `seven times` | Circle 4 (×7, 1/7), bar at 7 | 0.7 s |
| `take a moment to guess` | **Pause and predict:** motion slows to a crawl, the wave breathes softly, and nothing new appears through the `[pause]` | 0.4 s |

### SCENE 08 · `scene_08_square_wave.py` · `Scene08SquareWave` · ~3:11–3:28
**Narration:** "Watch the top flatten out … Smooth circles, adding up to sharp corners."
**Engine:** `EpicyclePlate` (10 → 200 circles) + Manim overlay (counter, target ghost, strip).

| Cue key | What happens | Anim |
|---|---|---|
| `top flatten` | Circles keep arriving. The trail's crest visibly flattens | 1.0 s |
| `ten circles` | A counter at top right shows **10**. The strip fills to 10 bars | 0.6 s |
| `fifty` | **50**. The chain is now a dense spiral of tiny rims | 0.6 s |
| `two hundred` | **200**. The strip is a fine comb | 0.6 s |
| `square wave` | The ideal square wave appears as a dashed ghost exactly under the gold trace: they match | 0.6 s |
| `flat on top` / `flat on the bottom` / `straight walls` | A hairline sweep highlights each part in turn | 0.4 s each |
| `sharp corners` | A light sweep runs from the chain (left) to the corner (right): circles in, corners out | 0.9 s |

### SCENE 09 · `scene_09_gibbs.py` · `Scene09Gibbs` · ~3:28–3:48
**Narration:** "But look closely at a corner … Sharp corners are expensive."
**Engine:** Manim (partial sums computed at high resolution near the jump).

| Cue key | What happens | Anim |
|---|---|---|
| `closely` | Zoom 6× onto one jump of the square wave | 1.2 s `smooth` |
| `small spike` | The overshoot crest is marked with a red dot (`SPIKE`) | 0.4 s |
| `more circles` | N steps 10 → 50 → 200: the spike narrows and slides toward the wall. Earlier versions stay as fading ghosts | 3 × 0.7 s |
| `never gets any shorter` | A horizontal red hairline at the crest's height stays put while every version touches it | 0.6 s |
| `nine percent` | A small bracket from the top of the wave to the hairline, label `≈ 9\%` of the jump | 0.6 s |
| `gibbs phenomenon` | The name sets small in Inter Light beside the bracket | 0.6 s |
| `expensive` | Zoom out. A small **red corner marker** docks into the top-right corner and stays until Ch6 (promise P4) | 0.8 s |
| (end) | The square wave detaches and floats free: the hand-off to Ch3 | 0.8 s |

# CH3 · Fourier's hot ring (~3:48–5:07)

### SCENE 10 · `scene_10_ring.py` · `Scene10Ring` · ~3:48–4:16
**Narration:** "Now you might be wondering … Unroll the ring, and that's our square wave."
**Engine:** skia typography + moderngl `HeatRingPlate` + Taichi flame/frost particles.
**Why it works:** a mode switch to history and physics (rule 10). The ring is the square wave in a new body (rule 9). "The short answer is heat" pays off the intro's "of all things, heat".

| Cue key | What happens | Anim |
|---|---|---|
| `wondering` | Eyebrow **03 · FOURIER'S HOT RING**. The floating square wave fades to 30 % | 0.6 s |
| `heat` | The heat-ring teaser from the intro returns, larger | 0.8 s |
| `eighteen oh seven` | Large faint "1807" in Space Grotesk, at 12 % opacity, behind everything | fade 0.8 s |
| `spreads through a solid` | Optional: a public-domain portrait engraving of Fourier, small, lower third, if the user adds one to `assets/`. Otherwise a name card | 0.8 s |
| `metal ring` | A brushed-metal torus in 3D at 30° pitch, slowly rotating | 1.2 s |
| `flame` | Ember particles lick one half, which glows orange-white | 1.0 s |
| `ice` | Frost particles on the other half, which cools to deep indigo | 1.0 s |
| `let it go` | The particles stop. The ring holds its half-and-half temperature | 0.6 s |
| `unroll the ring` | The ring **unrolls** into a straight bar whose temperature profile is drawn above it in gold: the square wave. Then it rolls back up, and the gold profile stays wrapped around it as a height crown | 1.2 s + 1.0 s |

### SCENE 11 · `scene_11_fading.py` · `Scene11Fading` · ~4:16–4:48
**Narration:** "Fourier's move was to break the temperature into simple waves … and then into an even warmth."
**Engine:** `HeatRingPlate` (main ring + three small mode rings), Manim inset plot.
**Why it works:** the viewer sees why sines are natural. They are the shapes that keep their shape as they fade.

| Cue key | What happens | Anim |
|---|---|---|
| `simple waves` | Three small rings split out to the right, showing mode 1, mode 3, and mode 5 crowns (heights 1, ⅓, ⅕ × 4/π) | `LaggedStart` 1.0 s |
| `once` / `three times` / `five` | Each small ring pulses as it's named | 0.4 s each |
| `keeps its shape` | Time starts (κ chosen so mode 1 fades over ~6 s). Each small crown shrinks **without changing shape** | continuous |
| `nine times as fast` | Inset plot: the curves `e^{−t}` and `e^{−9t}` (computed). The steep one is labeled `×9` | 0.8 s |
| `sharp edges melt` | The main ring's crown loses its corners first (the exact sum of the decaying modes) | continuous |
| `one gentle wave` | The main crown is now just mode 1. A brief ghost of the mode-1 ring overlays it: a match | 0.6 s |
| `even warmth` | The crown flattens. The ring settles to a single mid-tone | 1.2 s |

### SCENE 12 · `scene_12_doubt.py` · `Scene12Doubt` · ~4:48–5:07
**Narration:** "But for this to work … Now let's bring all this back to our drawing."
**Engine:** Manim.

| Cue key | What happens | Anim |
|---|---|---|
| `sudden jumps` | Left: a jagged gold temperature profile with jumps. Right: `= \sum` and a column of three small sines | 1.0 s |
| `didn't buy it` | The `=` flickers and turns into a dim `\overset{?}{=}` | 0.6 s |
| `watched it happen` | A 2 s replay of S08's square wave forming (10 → 200 circles). The `?` dissolves | 2.0 s |
| `back to our drawing` | The ring's crown unrolls into a line, which winds back into a circle with an arm: the hand-off to Ch4 | 1.4 s |

# CH4 · Waves become drawings (~5:07–6:32)

### SCENE 13 · `scene_13_two_directions.py` · `Scene13TwoDirections` · ~5:07–5:19
**Narration:** "So far, we've only watched the height of the tip … let the tip draw right on the page."
**Engine:** Manim (`EpicycleChain` + two `ShadowWave`s).
**Why it works:** the midpoint re-hook (rule 11). The half we've been ignoring is the key to drawing.

| Cue key | What happens | Anim |
|---|---|---|
| `height of the tip` | Eyebrow **04 · WAVES BECOME DRAWINGS**. The two-circle chain is back, with its height wave on the right | 0.8 s |
| `left and right` | A second projection runs downward from the pen: the left-right motion writes its own wave going down the screen | 1.0 s |
| `use both` | Both projection lines converge back onto the pen. The waves fade | 0.6 s |
| `draw right on the page` | The pen draws its 2D path in gold ink, a loop. A faint clef ghost flashes behind it for 0.6 s (where this is going) | continuous + flash |

### SCENE 14 · `scene_14_sky.py` · `Scene14Sky` · ~5:19–5:36
**Narration:** "This picture is actually very old … you can follow almost any path."
**Engine:** skia starfield (seeded, static) + Manim (two-circle geocentric Mars model, computed).

| Cue key | What happens | Anim |
|---|---|---|
| `very old` | The stage becomes a night sky. A small Earth dot sits at center | 1.0 s |
| `circles riding on circles` | Two circles appear (Earth-relative Mars = Mars orbit − Earth orbit). The planet traces a path with **retrograde loops**, in gold | 3.0 s |
| `wrong about how the sky works` | 1.5 s aside: the view re-centers on the Sun, the loops untangle into plain orbits, then it re-centers back | 1.5 s |
| `right about the circles` | The rims brighten | 0.6 s |
| `almost any path` | The stars fade out. The loops' gold ink remains on black | 0.8 s |

### SCENE 15 · `scene_15_direction.py` · `Scene15Direction` · ~5:36–5:50
**Narration:** "On a page, direction matters … It just sets where the drawing sits."
**Engine:** Manim.

| Cue key | What happens | Anim |
|---|---|---|
| `counterclockwise` | Left: a circle turning counterclockwise, blue rim, label `+1` | 0.8 s |
| `clockwise` | Middle: one turning clockwise, orange rim, label `−1` | 0.8 s |
| `speed zero` | Right: a green arm that doesn't turn. Label `0` | 0.6 s |
| `where the drawing sits` | The green arm stretches and swings, and a small gold loop attached to its tip moves with it: it only places the drawing | 1.2 s |

### SCENE 16 · `scene_16_rounded_square.py` · `Scene16RoundedSquare` · ~5:50–6:32
**Narration:** "Here's a friendly example we'll keep coming back to … how do you find the size and starting angle of every circle?"
**Engine:** Manim (`EpicycleChain`, then `SpectrumStrip` as an empty "speed rack").

| Cue key | What happens | Anim |
|---|---|---|
| `friendly example` | The stage clears to center | 0.6 s |
| `big circle` | A blue circle, r = 1, speed +1 | 0.8 s |
| `one ninth` | An orange circle, r = 1/9, speed −3, on its tip. A violet arc marks its **half-turn** start | 0.8 s |
| `rounded square` | The pen traces the rounded square in gold | 4 s loop |
| `square from the beginning` | The intro square appears as a dashed ghost around it, and an inset of the intro chain lights its first two circles (the same two) | 0.8 s |
| `every whole number speed` | The rounded square moves up. Below it, a row of **empty dashed slots** labeled 0, 1, −1, 2, −2, 3, −3, … (the speed rack) | `LaggedStart` 1.2 s |
| `size` / `starting angle` | Each slot shows two faint empty knobs: a radius tick and a violet angle tick | 0.6 s |
| `if i hand you a drawing` | The treble clef ghost slides in above the rack | 0.8 s |
| `every circle` | The rack's slots pulse once, all empty | 0.6 s |

# CH5 · Spin and average ★ (~6:32–9:02)

The core chapter. Mostly Manim, so every object can be exact and labeled. The test drawing is a **"bean" loop** built from 5 known circles (speeds 0, 1, −1, 2, −2, with chosen sizes and angles), so every answer on screen is exactly right.

### SCENE 17 · `scene_17_balance.py` · `Scene17Balance` · ~6:32–7:06
**Narration:** "Let's warm up with the easiest circle, speed zero … a full turn averages out to nothing."

| Cue key | What happens | Anim |
|---|---|---|
| `warm up` | Eyebrow **05 · SPIN AND AVERAGE**. The rack's slot `0` lights green | 0.6 s |
| `center of the drawing` | The bean loop (gold) appears, offset from the origin | 1.0 s |
| `squiggly shape` | The bean wobbles once (a slight tween), with a dim `?` cursor ping at its middle | 0.6 s |
| `spread dots` | The pen goes around once and drops 60 gold dots, evenly in time (denser where the pen moves slowly) | 2.0 s |
| `average` | Every dot sends a faint line to their mean, then the dots slide in and merge into the **green balance point** | `LaggedStart` 1.2 s |
| `balance point` | The green dot pulses. The speed-zero arm (green) grows from the origin to it: an exact match | 0.8 s |
| `full turn` | Inset: a single spinning arm drops 12 dots around a circle. Their average sits exactly at the center, which is grey (nothing) | 1.2 s |

### SCENE 18 · `scene_18_rule.py` · `Scene18Rule` · ~7:06–7:13
**Narration:** "That gives us the key idea. Things that spin average out to zero. Things that stand still don't."

| Cue key | What happens | Anim |
|---|---|---|
| `spin` | Left icon: a spinning arm whose dots average to the center (grey) | 0.6 s |
| `stand still` | Right icon: a still arm whose dots all sit at its tip, so the average is the tip (green) | 0.6 s |
| (end) | Both icons shrink into a small **rule card** docked bottom-left for the rest of the chapter (rule 6) | 0.6 s |

### SCENE 19 · `scene_19_freeze.py` · `Scene19Freeze` · ~7:13–7:44
**Narration:** "Now, the speed one circle spins … frozen in place."
**Why it works:** it is the one idea of the video, shown rather than stated (rule 14). The camera itself turns, and the circle that matches stops.

| Cue key | What happens | Anim |
|---|---|---|
| `speed one circle` | The bean's chain is drawn (5 arms). The speed-1 arm gets a soft highlight | 0.6 s |
| `can't see it` | Its dots average to nothing: a grey ping at the center | 0.6 s |
| `here's the trick` | Hold. The pen keeps going round | — |
| `turn the whole drawing backward` | The **whole stage rotates clockwise**, one turn per loop (`rotating_frame=1`). A thin orange ring with an arrow at the stage edge shows the backward turn | 4 s loop |
| `so it stops` | In the turning view, the speed-1 arm **freezes**. It turns green and its glow steadies | 0.6 s |
| `still spinning` | The other arms keep spinning. Their speed labels update (+2 → +1, −1 → −2, −2 → −3) | 0.8 s |
| `wash out` | The dots, now wound into a new shape, collapse to their average: a green point exactly at the frozen arm's tip | 1.4 s |
| `frozen in place` | A silver radius bracket and a violet angle arc on the frozen arm. Slot `1` in the rack fills | 0.6 s |

### SCENE 20 · `scene_20_check.py` · `Scene20Check` · ~7:44–8:09
**Narration:** "As a sanity check, let's try our rounded square … There's no circle there."
**Engine:** Manim (rounded square, a speed dial UI, `SpectrumStrip`).
**Why it works:** a sanity check on a case where the viewer already knows the answer (P6).

| Cue key | What happens | Anim |
|---|---|---|
| `sanity check` | The two-circle rounded square from S16 returns. A small **speed dial** sits at the top center | 0.8 s |
| `backward once` | Dial → 1. The stage turns backward and the dots wind | 1.4 s |
| `tip of the big circle` | The average lands on the big circle's tip (green). The rack bar at `1` rises to 1 (blue) | 1.0 s |
| `forward three times` | Dial → −3. The stage turns forward ×3 | 1.4 s |
| `one ninth` | The average lands on a point **1/9 from center, pointing the opposite way** (violet half-turn arc). The bar at `−3` rises to 1/9 (orange) | 1.0 s |
| `speed two` | Dial → 2. The stage spins | 1.2 s |
| `falls to zero` | The average lands at the center: a grey ping, and slot `2` stays empty | 0.8 s |

### SCENE 21 · `scene_21_recipe.py` · `Scene21Recipe` · ~8:09–9:02
**Narration:** "If you hold on to just one idea from this video … Spin, then average. That's all it says."
**Engine:** Manim (`MathTex` with per-term color).
**Why it works:** promise P2 is paid off. The muted line from the intro returns to its exact spot and gets its colors in two steps, each with its picture.

| Cue key | What happens | Anim |
|---|---|---|
| `just one idea` | Everything dims except the rule card, which slides to center and grows | 0.8 s |
| `spin the drawing against it` | Card: a turning stage (orange ring) | 0.6 s |
| `take the average` | Card: dots collapsing into a green point. Hold | 0.6 s |
| `line from the beginning` | The card returns to its corner. The intro's muted silver formula fades in at the **same screen position** as in S02, then glides to center | 0.8 s + 0.8 s |
| `c n` | `c_n` turns green | 0.4 s |
| `f of t` (1st) | `f(t)` turns gold | 0.4 s |
| `e to the minus` (1st) | `e^{−2πint}` turns orange | 0.4 s |
| `integral` (1st) | `∫₀¹ … dt` turns silver | 0.4 s |
| `two steps` | Two brackets under the formula: step 1 under `f(t) e^{−2πint}`, step 2 under `∫₀¹ … dt` | 0.6 s |
| `pen's position` | `f(t)` lifts. A tiny inset of the pen on the bean appears beside it | 0.8 s |
| `turns the drawing backward` | A small clockwise-turning arrow icon appears beside `e^{−2πint}`. The `n` inside it pulses blue | 0.8 s |
| `complex numbers` | Callback inset: video 001's quarter-turn arrow on the unit circle, spinning, ~2 s (built with 001's style constants) | 0.6 s in, 0.6 s out |
| `average over one trip` | `∫₀¹ … dt` brightens with its bracket. The mini inset shows dots collapsing to their mean | 1.0 s |
| `spin then average` | The insets fade, the formula glows once, and a light sweep crosses it. Hold | 1.0 s |

# CH6 · Drawing anything (~9:02–10:36)

### SCENE 22 · `scene_22_compute.py` · `Scene22Compute` · ~9:02–9:24
**Narration:** "So let's give it a real test … chain them tip to tail."
**Engine:** Manim (dots, dial, strip) → `EpicyclePlate` (chain).
**Why it works:** the bars-become-circles moment is the transform that ties "the list" to "the machine" (rule 9).

| Cue key | What happens | Anim |
|---|---|---|
| `real test` | Eyebrow **06 · DRAWING ANYTHING**. The formula shrinks to the top-right corner and stays | 0.8 s |
| `treble clef` | The clef outline appears as a silver ghost | 0.8 s |
| `one continuous line` | A spark runs along the whole outline once | 1.2 s |
| `thousand dots` | 1,000 gold dots sprinkle along it | 1.0 s |
| `minus one hundred` | The dial counter sweeps −100 → 100 (≈ 3 s). Behind it the dot cloud spins (motion-blurred), and the `SpectrumStrip` fills bar by bar: 201 bars, blue and orange | 3.0 s |
| `two hundred and one` | The strip lands complete | 0.4 s |
| `biggest to smallest` | The bars **re-order** by height, biggest first (an animated sort) | 1.2 s |
| `tip to tail` | Each bar lifts off, curls into a circle of that radius, and snaps onto the end of the growing chain | `LaggedStart` 1.6 s |

### SCENE 23 · `scene_23_converge.py` · `Scene23Converge` · ~9:24–9:41
**Narration:** "With one circle, we get a loop … even the tiniest circles are adding detail the others can't."
**Engine:** `EpicyclePlate` + `InkParticles`.

| Cue key | What happens | Anim |
|---|---|---|
| `one circle` | Counter **1**. The chain is cut to the biggest circle, and the pen traces a plain loop | 1.6 s loop |
| `five` | **5**: a rough blob. The previous ink stays as a faint ghost | 1.6 s |
| `twenty` | **20**: the clef starts to read | 1.6 s |
| `two hundred` | **200**: the full chain traces the clef almost perfectly, with sparks shedding. The ghost outline sits exactly under it | 3.0 s |
| `up close` | The camera dives **40×** onto the pen, following it. The last dozen tiny circles whirl visibly, and the ink is still crisp | 1.6 s `smooth` |
| `the others can't` | Toggle: the last 50 circles switch off for 0.8 s, and the ink at that zoom goes visibly wrong (a smoothed corner). They switch back on and the detail returns. Pull back | 0.3 + 0.8 + 0.3 s |

### SCENE 24 · `scene_24_smooth_sharp.py` · `Scene24SmoothSharp` · ~9:41–10:07
**Narration:** "Remember how I said sharp corners are expensive? … The smoother the shape, the fewer circles it takes."
**Engine:** Manim.
**Why it works:** promise P4 pays off, with the two squares compared side by side.

| Cue key | What happens | Anim |
|---|---|---|
| `remember` | The red corner marker from S09 (top right) pulses and flies to center | 0.8 s |
| `first few circles` | The clef drawn with 10 circles: its smooth arcs light up, already right | 1.0 s |
| `all the rest` | Its sharp turns flash red: still rough | 0.6 s |
| `pen jumps` | Left panel: the square wave, with its strip bars `1, ⅓, ⅕, …` | 0.8 s |
| `one third, one fifth` | The fractions write above the bars on the beat | 0.4 s each |
| `turns a corner` | Right panel: the square loop and its strip `1, 1/9, 1/25, …`. Its bars drop off visibly faster | 0.8 s |
| `one ninth, one twenty fifth` | Fractions on the beat | 0.4 s each |
| `fewer circles it takes` | A third mini panel: a smooth oval loop whose strip has only 3 bars. The red marker dissolves (promise kept) | 1.0 s |

### SCENE 25 · `scene_25_everywhere.py` · `Scene25Everywhere` · ~10:07–10:36
**Narration:** "That's why this idea shows up everywhere … dropping the tiny ones you won't notice."
**Engine:** Manim (synthetic waveforms and spectra) + skia piano keys + scipy DCT + skia image tiles.

| Cue key | What happens | Anim |
|---|---|---|
| `piano chord` | The intro's three-key chord and merging waves return for 1.5 s (callback, P7) | 0.6 s in |
| `sound is a wave` | The merged gold waveform slides left and becomes the start of a longer sound wave | 0.8 s |
| `singer and a violin` | Two stacked waveforms (synthetic, deterministic: the same fundamental, different harmonic recipes). Their strips sit to the right | 1.0 s |
| `slowest circle` | The first bar of both strips lights up, at the same speed and aligned | 0.6 s |
| `faster circles on top` | Their other bars differ and glow | 0.6 s |
| `shrink photos` | An image (a still from video 002's luminous terrain, our own asset) splits into an 8×8 block grid | 1.0 s |
| `keeping the big circles` | A threshold line sweeps across one block's coefficient bars. The small ones fall away | 1.0 s |
| `won't notice` | The image re-forms from about 10 % of its coefficients (real `scipy.fft` DCT). A thin wipe compares it with the original: nearly the same | 1.4 s |

✂ If the audio runs long: drop the 1.5 s chord callback visual (keep the narration) and shorten the compression wipe.

# OUTRO · What we built (~10:36–11:40)

### SCENE 26 · `scene_26_recap.py` · `Scene26Recap` · ~10:36–11:15
**Narration:** "So let's step back and look at what we've built … Whatever stands still is the circle you were looking for."
**Engine:** Manim + skia glass cards (`cards.py`).
**Why it works:** each recap sentence is a 5–8 s visual callback, not a spoken list (rule 17).

| Cue key | What happens | Anim |
|---|---|---|
| `step back` | The camera pulls back. Four empty glass cards fade up in a row | `LaggedStart` 0.8 s |
| `simplest wave` | Card 1 plays a live loop: circle → sine, with the three chips | 0.8 s |
| `stack circles` | Card 2: stacked circles → square wave | 0.8 s |
| `two directions` | Card 3: a chain drawing the rounded square | 0.8 s |
| `spin the drawing backward` | Card 4: a turning stage, a frozen green arm, and the recipe line in full color under the cards | 0.8 s |
| `circle you were looking for` | All four cards glow once | 0.6 s |

### SCENE 27 · `scene_27_teaser.py` · `Scene27Teaser` · ~11:15–11:33
**Narration:** "There's one thing we quietly assumed … it's where we'll go next."

| Cue key | What happens | Anim |
|---|---|---|
| `drawings repeat` | The cards fade. A pen finishes a loop and lands on its starting point, which pings (the loop closes) | 1.0 s |
| `never repeats` | A gold sound wave with no repeating pattern (a deterministic chirp with a noise envelope) scrolls past | 1.2 s |
| `every possible speed` | The integer speed rack's separate bars **melt together** into one continuous glowing band | 1.4 s |
| `fourier transform` | "Fourier transform" in small Space Grotesk under the band, with a light sweep | 0.8 s |

### SCENE 28 · `scene_28_finale.py` · `Scene28Finale` · ~11:33–11:40 (to the end of the audio)
**Narration:** "For now, let's watch it one more time. Just circles, going round. Thanks for watching."
**Engine:** `EpicyclePlate` in **2.5D** (the drawing plane tilted ~25°, slow yaw orbit, rims in perspective, a soft floor reflection) + `InkParticles`.
**Why it works:** it ends on the payoff (rule 19). The opening image comes back, now fully understood.

| Cue key | What happens | Anim |
|---|---|---|
| `one more time` | The 200-circle clef chain, from black. The plane tilts into perspective | 1.2 s |
| `going round` | The pen completes the clef exactly as "round" ends (the loop rate is set from the SRT; if the line is short, the loop starts during S27's last beat) | timed loop |
| `thanks` | The chain fades. The gold clef holds, glowing, and the sparks settle | 0.8 s |
| (audio end) | Fade to black, ending exactly on the audio | 0.6 s |

---

## Phase 3 checklist (when the audio and SRTs arrive)
- `ffprobe` the true duration. The video must match it to within one frame. If it runs over 12:00, apply the ✂ cuts or tighten the voiceover and regenerate.
- `beats.py`: every cue key above is looked up with `Cue.at()` / `after=`, and it fails loudly if a key is missing or out of order.
- **Watch for SRT spellings**: "eighteen oh seven" may come out as "1807", "c n" as "CN", "e to the minus two pi i n t" as fragments, "f of t" as "F of T", "one ninth" as "1/9", "Gibbs" as "Gibs". Cue keys follow the SRT, not this file.
- Cut points: `ffmpeg silencedetect`, with every scene cut on a frame boundary inside a real pause (002's method).
- Lock **S28's loop** so the clef closes on "round", **S01's loop** so it closes after "clef", and **S08's counter steps** on "ten / fifty / two hundred".
- Rewrite this file's Est. ranges into `storyboard.md` with real timestamps, then get approval before building.
