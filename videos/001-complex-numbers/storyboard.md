# 001 — Complex Numbers, Explained Visually

**Mode:** experimental production. **Status:** phase 3, timed scene plan (waiting for approval before scene code).

**Inputs** (`assets/`): `audio.mp3` is **56.856 s**. `cue-per-word.srt` has 165 word cues and matches `voiceover.md` word for word. There is also `normal-subtitle.srt`.

## Timing facts from the audio

- Parsed with `aion/sync.py` (`Cue.load(...)`). Every beat below is a `cue.at()` / `cue.phrase()` lookup and none are hard-coded. The **t** column shows what the lookup returns today.
- **Anchor on word starts, not ends.** The aligner leaves no gaps between words: each word's end time absorbs the pause after it. `ffmpeg silencedetect` shows the real breaths are only **0.3–0.6 s**, with no long paragraph breaks (the largest are 4.08–4.69 and 8.93–9.52). In practice, a visual has about **0.4 s of air** at a chapter boundary.
- Matching ignores case and punctuation. The SRT writes "i" as "I" at 27.06 and 53.19, and writes "90" as digits. Repeated words need `after=`, for example `cue.at("minus one", after=34)`.
- Animation start = word start − `LEAD` (0.15 s), unless noted otherwise.

## Scene slices (60 fps, cut on frame boundaries inside real silences)

| Scene | File / class | Range (s) | Frames | Cut lands in silence |
|---|---|---|---|---|
| Intro | `scene_01_intro.py` · `Scene01Intro` | 0.000 – 9.500 | 0 – 570 | 8.93–9.52 |
| Ch1 Puzzle | `scene_02_puzzle.py` · `Scene02Puzzle` | 9.500 – 21.967 | 570 – 1318 | 21.54–21.97 |
| Ch2 Quarter turn ★ | `scene_03_quarter_turn.py` · `Scene03QuarterTurn` | 21.967 – 35.167 | 1318 – 2110 | 34.73–35.09 |
| Ch3 Plane | `scene_04_plane.py` · `Scene04Plane` | 35.167 – 46.317 | 2110 – 2779 | 45.82–46.31 |
| Outro | `scene_05_outro.py` · `Scene05Outro` | 46.317 – **58.856** | 2779 – 3531 | — (+2.0 s tail, see ⚠) |

Each scene sets `TOTAL_DURATION` from these numbers, plays its slice of the audio with `add_sound(..., time_offset=-scene_start)`, and drives every beat with `wait_until(t - scene_start)`. Each scene ends in exactly the state the next scene starts from, so the concat has no visible cuts.

> ⚠ **Decision needed: end tail.** The last word ("rotation") ends at 56.66 s, and the audio ends at 56.856 s. That leaves **0.2 s** for the closing spin and fade, which would feel chopped off. **Recommendation:** add a **2.0 s silent tail** (`apad` at mux time) so the final spin can finish and the frame can rest. The video would then be 58.856 s. The alternative is to keep it at exactly 56.856 s and cut the ending down to a quarter turn plus a fast fade.

## Color semantics (whole video)

These get added to `aion/style.py` as new constants.

| Object | Constant | Color |
|---|---|---|
| Real part, real axis, "steps right", plain numbers on the line | `REAL` (= `ACCENT`) | `#58C4DD` blue |
| Imaginary part, imaginary axis, "steps up" | `IMAG` (= `J_HAT`) | `#FC6255` red |
| The number *i*, quarter-turn arcs, `× i` | `I_UNIT` | `#B48EF0` violet |
| The moving number *z* (the arrow) | `Z` (= `VEC`) | `#F4D35E` yellow |
| −1, half turn, `× (−1)` | `NEG` | `#F2A65A` orange |

Background is `BG #0E1117`. Equations are color-coded to match, e.g. `3` blue, `2i` red, `−2` blue, `3i` red, `i` violet, `−1` orange.

## As built (deviations from the plan below)

- **Background is pure black `#000000`** in every scene (user request). It is set once in `scenes/shared.py` (`VideoScene.BACKGROUND`). The channel default `style.BG` is unchanged.
- **2.0 s tail approved.** The outro runs to 58.850 s, and the audio is padded with silence at mux time.
- **The GPU plate renders inside Manim**, not as an ffmpeg overlay. `aion/components/shader_plate.py` runs the moderngl shader every frame at output resolution and hands the pixels to Cairo, so previews already show it and no compositing step is needed. The arrow and the plate share the same `theta` ValueTracker, so they cannot drift apart.
- **Hand-offs are exact by construction.** Each scene sets `PREVIOUS`, and `NarratedScene` silently replays the earlier timelines (no frames written) to reach the previous scene's last frame. Ch1 → Ch2 measured 48 dB PSNR, which is identical up to compression.
- The intro trail is a gradient arc (`shared.trailing_arc`) instead of a TracedPath, because a TracedPath looked polygonal at low fps.
- `./build.sh [l|m|h|k]` renders all five scenes, concatenates them and muxes the audio. `h` writes `out/final.mp4`.

## Engines and layers

- **Manim CE**: every mathematical element in all five scenes. Scenes 01 and 05 render with `-t` (transparent `.mov`) so they can sit over a GPU plate.
- **moderngl**: `plate_domain.py` renders a **domain-coloring plate** for the intro (0–9.5 s) and the outro (55.9 s to the end). The hue is arg(e^{iθ(t)}·z) and the brightness rolls off with |z|. θ(t) is the **same easing function** that drives the Manim arrow's angle, defined once in `scenes/beats.py`, so the background hue turns in lockstep with the arrow. Mathematically, the plate shows the whole plane being multiplied by e^{iθ}. The plate also gets a single-pass bloom.
- **skia-python**: the glow sprite for the *i* glyph (Gaussian halo, additive), loaded as an `ImageMobject`. Also the outro recap cards (rounded rects with soft shadow), and a static vignette and grain overlay.
- **ffmpeg**: overlays the alpha clips on the plates, concatenates five 60 fps clips, pads the audio (if the tail is approved), and muxes `audio.mp3` → `out/final.mp4`.

---

## SCENE 01: INTRO · 0.000–9.500 · Manim (alpha) + moderngl plate

> What if a number could turn, not just grow or shrink but spin? That's a complex number, and in one minute you'll see it isn't complex at all.

**Purpose:** a hook. The viewer watches a number *do* something numbers don't usually do, then gets a 3-shot trailer of the video's payoffs.

| t | cue key | What happens | Anim |
|---|---|---|---|
| 0.00 | (frame 0) | A number line from −3 to 3 fades up with a slight upward drift | `FadeIn(shift=UP*0.2)`, 0.0, rt 0.6 |
| 0.06 | `what` | A yellow arrow grows from 0 to 1 | `GrowArrow`, 0.25, rt 0.7 |
| 1.38 | `turn` | Tease: the arrow tilts about 15° and back | `Rotate`, `there_and_back`, 1.23, rt 0.6 |
| 2.44 | `grow` | The arrow stretches to 2, and the tick under its tip glows | `smooth`, 2.29, rt 0.5 |
| 2.92 | `shrink` | The arrow shrinks to ½ | `smooth`, 2.77, rt 0.5 |
| 3.82 | `spin` | **The arrow lifts off the line and spins a full 360°**, back to length 1, leaving a fading violet trail. The domain-coloring plate blooms in behind it to 25% opacity, its hue locked to the arrow's angle | `rush_from`, 3.67, rt 1.0. Plate fades 3.67 → 4.5 |
| 5.24 | `complex` | **Trailer shot 1:** the line folds up into a plane (the vertical axis rises and the grid flashes in) | 5.10, rt 1.0 |
| 6.64 | `one minute` | **Trailer shot 2:** a violet `i² = −1` with an orange −1, centered with a soft glow | cross-dissolve 6.30, rt 0.6 |
| 7.40 | `see` | **Trailer shot 3:** the grid with the arrow rotates 90° | cross-dissolve 7.25, rt 0.9 |
| 7.70 | `isnt complex` | Everything collapses back to the calm number line and the single arrow at 1. The plate fades to 0 | 8.00, rt 0.7. Plate out by 9.3 |
| 8.93–9.50 | silence | **Hold** the quiet frame | — |

**End state:** the number line from −3 to 3 with the yellow arrow at 1, on a plain BG.

## SCENE 02: CH1 THE PUZZLE · 9.500–21.967 · Manim + skia glow

> Here's the puzzle. What number times itself gives minus one? Square two, you get four. Square minus two, still four. Nothing on the number line works. So we give it a name, i.

**Purpose:** *show* why no real number works. The parabola y = x² never reaches y = −1.

| t | cue key | What happens | Anim |
|---|---|---|---|
| 9.50 | `heres the puzzle` | The arrow fades out. The number line drifts down and becomes the x-axis of a graph | 9.40, rt 1.0 |
| 10.60 | `what number times itself` | `x · x` writes at the top | `Write`, 10.45, rt 0.8 |
| 12.72 | `minus one` (after 10) | `= −1` appears in orange | 12.57, rt 0.5 |
| 13.22 | silence | `x · x` → `x²` | `TransformMatchingTex`, 13.15, rt 0.45 |
| 13.64 | `square two` | The y-axis grows from 0 to 4.5. A blue dot lights at x = 2 | 13.50, rt 0.6 |
| 14.53 | `you get four` | The dot rises to (2, 4), leaving a dashed riser. The label `2² = 4` lands on "four" (15.00) | rise 14.38, rt 0.5 |
| 15.60 | `square minus two` | A dot lights at x = −2 | 15.45, rt 0.4 |
| 16.87 | `still four` | The dot rises to (−2, 4). A dashed horizontal links the two mirror dots | 16.75, rt 0.6. Link 17.40 |
| 17.88 | `nothing` | **The parabola y = x²** sweeps through both dots (on [−√4.5, √4.5], so it stays inside the y range) | `Create`, 17.75, rt 1.1 |
| 19.20 | `works` | A dashed orange line at y = −1 slides in below. The band −1 < y < 0 gets a faint red tint, showing the curve never gets there | 19.05, rt 0.6 |
| 19.72 | `so we give it a name` | The graph dims to 20% | 19.60, rt 0.8 |
| 19.72 | (same beat) | `x² = −1` slides down to sit under the center of the screen | with the dim |
| 21.36 | `i` | **A violet *i* rises in the center with its skia glow** (scale 0.92 → 1.0). At the same moment, the x in `x² = −1` morphs into *i*, giving `i² = −1` | 21.21, rt 0.6 |

**End state:** the dimmed graph with the glowing *i* and `i² = −1` in the center. Ch1 has only about 0.6 s on the *i* before Ch2 begins, so Scene 03 starts on this same frame and keeps it for another 0.3 s.

## SCENE 03: CH2 i IS A QUARTER TURN ★ · 21.967–35.167 · Manim

> Watch what multiplying by minus one does. It flips the line, a half turn. So I should be half of that, a quarter turn. Multiply one by i, and it swings straight up again, and it lands on minus one.

**Purpose:** the conceptual turn of the video. ×(−1) is a 180° rotation, and the number whose square is −1 is half of that rotation.

| t | cue key | What happens | Anim |
|---|---|---|---|
| 21.96 | `watch` | The graph cross-fades into a clean centered number line (−3 to 3) with the yellow arrow at 1 and two blue "passenger" dots at 2 and 3. The *i* badge (with `i² = −1`) shrinks to the top-right corner as a reference | 22.20, rt 0.9 |
| 23.71 | `minus` (after 23) | `× (−1)` appears top-left in orange | 23.55, rt 0.5 |
| 24.62 | `flips` | **The whole line (arrow, dots, ticks) rotates 180° around 0** through the upper half-plane. It is a rotation, not a mirror. An orange semicircle traces the arrow tip in sync | `Rotate(PI)`, `smooth`, 24.47, rt 1.3 |
| 26.27 | `half turn` | A `180°` label lands beside the semicircle | 26.10, rt 0.4 |
| 26.92 | silence | The line cross-fades back to its original orientation. The semicircle stays as a 30% ghost (no reverse rotation, so it can't read as a second turn) | 26.95, rt 0.5 |
| 27.69 | `half of that` | A violet tick cuts the ghost semicircle at its top (90°) | 27.55, rt 0.4 |
| 28.84 | `quarter turn` | The violet quarter arc (0° → 90°) lights up. `× i` appears under `× (−1)` | arc 28.70, rt 0.6. Label 29.20 |
| 30.41 | `one` (after 30) | The arrow at 1 pulses | `Indicate`, 30.30, rt 0.6 |
| 31.68 | `swings` | **The arrow swings 90° to point straight up.** As it moves, a vertical axis draws out from the origin, so the imaginary axis is born here | `Rotate(PI/2)`, 31.55, rt 1.0. Axis `Create` 31.85, rt 0.8 |
| 32.60 | `up` | The tip is labeled with a violet `i` | 32.55, rt 0.4 |
| 32.75 | `again` | The arrow turns another 90°, and a second violet quarter arc follows it | 32.65, rt 1.0 |
| 33.64 | `lands` | The tip lands on −1, with an orange flash at the dot | 33.60, rt 0.4 |
| 34.45 | `minus one` (after 34) | A bottom row builds: `1 → i → i·i = −1`, then `i·i` → `i²`. **The two violet quarter arcs merge into the orange half arc**, which is the visual proof | row 34.0, rt 0.6. Merge 34.45, rt 0.6 |

**End state:** both axes, the arrow at −1, the orange half arc, and the bottom equation row.

## SCENE 04: CH3 THE COMPLEX PLANE · 35.167–46.317 · Manim (grid can become a moderngl plate if the 1080p60 render is too slow)

> Now the line opens into a plane. Three plus two i is three steps right, two steps up. Multiply by i, and the arrow turns 90 degrees to minus two plus three i.

**Purpose:** a number is now a point in 2D, and multiplying by *i* rotates the whole plane.

| t | cue key | What happens | Anim |
|---|---|---|---|
| 35.16 | `now the line` | The arcs, equation row, labels and arrow fade out, leaving only the two axes | 35.10, rt 0.6 |
| 36.00 | `opens` | **The grid unfolds outward from the axes** (x from −4 to 4, y from −3 to 4; vertical lines tinted blue, horizontal lines red). `Re` / `Im` labels fade in at "plane" (37.08) | `LaggedStart`, 35.85, rt 1.5 |
| 37.52 | `three plus two i` | A top-left panel writes `3 + 2i`, color-coded | `Write`, 37.40, rt 0.8 |
| 38.72 | `three steps right` | **Three blue unit hops** along the real axis (0.35 s each, small arcing bounce), leaving a dashed blue leg | 38.60 → 39.65 |
| 40.08 | `two steps up` | **Two red hops** up, leaving a dashed red leg. The dot lands at (3, 2), then the yellow arrow grows from 0 to the dot | 40.00 → 40.80. `GrowArrow` 40.75, rt 0.5 |
| 41.16 | `multiply by i` | The label becomes `i · (3 + 2i)`. A 30% ghost copy of the arrow stays in place | `TransformMatchingTex` 41.05, rt 0.6 |
| 42.99 | `arrow` | **The whole grid, arrow and both legs rotate 90° CCW** (`ApplyComplexFunction(lambda z: 1j*z)`), with a violet 90° arc at the origin drawn in sync. The blue leg is now vertical and the red leg horizontal, so the viewer sees the parts swap | 42.85, rt 1.4, `smooth` |
| 43.38 | `turns 90 degrees` | A `90°` label lands by the arc | 43.70, rt 0.4 |
| 44.62 | `minus two plus three i` | The tip dot pulses. The label completes: `i · (3 + 2i) = −2 + 3i`, with −2 in blue and 3i in red | 44.50, rt 0.7 |
| 45.82–46.31 | silence | **Hold.** The ghost (3, 2) and the new (−2, 3) sit side by side for comparison | — |

**Math check (asserted in code):** i(3+2i) = 3i + 2i² = −2 + 3i. Both arrows have length √13, and the angle between them is exactly 90°.
**Change from v1:** the middle step `3i + 2i²` is **dropped from the screen**. The narration gives only 1.7 s from "to minus two" to the scene end, and a three-part expansion there would be too much to read. The rotation itself is the proof here, which is the point of the video.

## SCENE 05: OUTRO · 46.317–58.856 (incl. 2.0 s tail) · Manim (alpha) + skia cards + moderngl plate

> A complex number is a point with a direction. i is a quarter turn, and two quarter turns face backward. That's why I squared is minus one, not imaginary, just rotation.

**Purpose:** sum the video up in three pictures, then echo the intro's spin to close.

| t | cue key | What happens | Anim |
|---|---|---|---|
| 46.32 | `a complex number` | The Ch3 plane (grid, arrow to −2+3i, label) shrinks into the **left card**. Three skia card frames fade in, with the middle and right ones at 30% as placeholders | 46.20, rt 1.0 |
| 47.41 | `point` | The tip dot pulses | 47.30, rt 0.5 |
| 48.24 | `direction` | The arrow body glows briefly | 48.10, rt 0.5 |
| 48.84 | `i is a quarter turn` | **Middle card** lights: an arrow from 1 swings to i along a violet quarter arc. `× i` appears beneath | 48.70, rt 0.9. Label 49.30 |
| 50.51 | `two quarter turns` | **Right card** lights: an arrow goes 1 → i → −1 along two violet arcs | 50.40, rt 0.45 ×2 |
| 51.68 | `backward` | The arrow at −1 flashes orange, and the arcs merge into the orange half arc | 51.55, rt 0.6 |
| 53.26 | `squared` | `i² = −1` writes under the right card. The left and middle cards dim to 50% | 52.95, rt 0.9 |
| 54.80 | `imaginary` | The cards fade out. The word *imaginary* fades in center screen in muted grey, then a thin strike-through draws across it | 54.50, rt 0.5. Strike 55.30, rt 0.35 |
| 56.02 | `just rotation` | *imaginary* fades away. The unit circle and a single yellow arrow appear, and **the arrow makes one slow full turn**. The domain-coloring plate blooms back in behind it, its hue locked to the arrow (bookending the intro) | spin 55.90, rt 2.0. Plate 56.0 → 57.0 |
| 57.90–58.86 | tail | Hold, then fade everything to BG | fade 58.20, rt 0.65 |

---

## Build and render plan

1. Add the color constants to `style.py`, and `wait_until` and audio-slice helpers to `aion/progress.py` (or a new `aion/scene_base.py`).
2. `scenes/beats.py`: every beat time as a named `cue.at(...)` lookup, plus the shared `theta(t)` easing for the arrow and plate.
3. Build scenes in order. Preview each with `uv run manim -pql` and check frames at each beat (`ffmpeg -ss <t>`).
4. `plate_domain.py` (moderngl + tqdm): intro and outro plates at 1080p60.
5. Final renders `-qh` in the background → composite → concat → mux → `ffprobe` duration check.

**Reusable pieces to promote afterward:** `QuarterTurnArc`, `GlowGlyph` (skia), the styled complex-plane builder, and `domain_coloring.glsl`.
