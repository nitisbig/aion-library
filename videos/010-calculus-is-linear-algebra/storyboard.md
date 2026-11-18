# Calculus Is Secretly Linear Algebra: storyboard

**Status:** phase 3, audio generated and beats resolved (2026-11-17). Waiting for storyboard approval before theme and
scene code.

Audio: `assets/audio.wav` (793.82 s = **13:14**, 2,175 words, voice speed 0.92, the 009 voice). Generated 2026-11-17
with `aion voice` (5 chunks, 11,798 characters). Scene ranges below are the real cuts from `beats.py`
(`uv run aion beats 010-calculus-is-linear-algebra --md`); the full beat table is at the end of this file.

Pacing (`voice.toml [pacing]`): 1.5 s lead-in, +0.5 s after each paragraph, +1.5 s between chapters, 3.0 s tail,
a held 3 s pause after the intro map (`cut_ch1` offset 1.5 keeps most of it with s01), and two 2.5 s pause-and-predict
pauses (the cosine arrow at 6:19, the eigenvector at 8:02). Captions: `assets/subtitles.srt`. Research and sources:
`research.md`.

Structure: intro, seven chapters, outro. Seventeen scene files, none over 70 s.

| # | scene | chapter | range | length | mode |
|---|---|---|---|---|---|
| 0 | `s00_hook` | Intro: the hundredth derivative, the spinning arrow | 0:00–0:57 | 57 s | question → visual answer |
| 1 | `s01_claim` | Intro: "that's what a matrix does", the claim, preview, map | 0:57–1:45 | 48 s | claim + montage |
| 2 | `s02_samples` | Ch1 A curve becomes a column: 8 → 50 → 1000 samples | 1:45–2:10 | 25 s | visual, data |
| 3 | `s03_linear` | Ch1 (cont.) add, scale, slope respects both → linear map | 2:10–2:46 | 36 s | derivation |
| 4 | `s04_band` | Ch2 The difference matrix, the 1000 × 1000 band, sin → cos | 2:46–3:41 | 55 s | build, numerics |
| 5 | `s05_poly` | Ch2 (cont.) the exact 4 × 4 matrix on cubics | 3:41–4:29 | 47 s | derivation, payoff |
| 6 | `s06_null` | Ch3 The zero column, constants collapse, det 0 | 4:29–5:06 | 37 s | visual, callback |
| 7 | `s07_plus_c` | Ch3 (cont.) D F = f, particular + null space, D⁴ = 0 | 5:06–5:55 | 49 s | **reveal** |
| 8 | `s08_rotation` | Ch4 The cos/sin plane, predict #1, quarter turns, the cycle | 5:55–6:59 | 64 s | predict, visual |
| 9 | `s09_inverse` | Ch4 (cont.) back to the hook, the integral by inverse matrix | 6:59–7:42 | 43 s | payoff of the hook |
| 10 | `s10_eigen` | Ch5 Predict #2, e^{λx} only stretches, why e is everywhere | 7:42–8:43 | 62 s | predict, **midpoint re-hook** |
| 11 | `s11_ode` | Ch5 (cont.) the spring's solution plane, Fourier/Laplace = diagonalizing | 8:43–9:35 | 52 s | synthesis |
| 12 | `s12_string` | Ch6 Build the 1, −2, 1 matrix for a pinned string | 9:35–10:02 | 27 s | build |
| 13 | `s13_modes` | Ch6 (cont.) the eigenvectors appear, vibrate, pluck, *sound* | 10:02–10:59 | 58 s | **showpiece**, audio |
| 14 | `s14_shift` | Ch7 e^{hD} is the Taylor series is a shift; the asterisk | 10:59–12:08 | 68 s | reveal, honesty |
| 15 | `s15_infinity` | Outro: where the analogy breaks, functional analysis | 12:08–12:56 | 48 s | honesty |
| 16 | `s16_recap` | Outro (cont.) the five lines, "plus a limit" | 12:56–13:14 | 18 s | callback, end card |

## The story spine
"**Differentiation is a linear map on a space of functions.** Most of calculus is linear algebra, plus a limit."
Each chapter is one linear-algebra idea applied to D: vectors (Ch1), the matrix (Ch2), null space (Ch3), rotation and
inverse (Ch4), eigenvectors (Ch5), eigenvectors of a real system (Ch6), the matrix exponential (Ch7). The hook's
spinning arrow is explained in Ch4. The outro says honestly where the picture stops being exact.

Not repeating ourselves (see `research.md` §8): matrices, determinants, eigenvectors, Taylor, Fourier, Laplace and e are
**used, never re-taught**. Each callback is ≤ 10 s and carries a new visual. 3Blue1Brown's polynomial derivative
matrix (s05) is the standard example. It gets ~40 s, and the video spends its time on what comes after it.

## Running numbers (verified with sympy/numpy, scratchpad `verify.py`, 2026-11-17; computed at build time, never typed)

| use | value | where |
|---|---|---|
| hook function | f = eˣ sin x; f⁽¹⁰⁰⁾ = −2⁵⁰ eˣ sin x (2⁵⁰ = 1,125,899,906,842,624) | s00, s09 |
| hook plane | basis b₁ = eˣ cos x, b₂ = eˣ sin x. D = [[1, 1], [−1, 1]] = √2 · (45° clockwise turn); det 2; eigenvalues 1 ± i | s00, s09 |
| hook spin | 100 steps: −4500° = 12.5 turns, length (√2)¹⁰⁰ = 2⁵⁰. Shown on a **log length scale** (else off-screen after ~6 steps) | s00 |
| samples | sin x on [0, 2π] at N = 8, 50, 1000 | s02 |
| linearity pair | f = sin x, g = 0.5 cos 2x (any smooth pair); (f + g)′ = f′ + g′; (3f)′ = 3f′ | s03 |
| difference matrix | forward difference: −1 on the diagonal, +1 above it, ÷ h. Shown 8 × 8 with symbols, then 1000 × 1000 heat map. D·sin ≈ cos, max error ≈ h/2 = 0.0031 at N = 1000 on [0, 2π] (recompute and show the real number only if it's on screen) | s04 |
| polynomial D | basis 1, x, x², x³: [[0,1,0,0],[0,0,2,0],[0,0,0,3],[0,0,0,0]], rank 3, det 0 | s05–s07 |
| example cubic | p = 2 + 3x − x² + 4x³ → (2, 3, −1, 4) → p′ = 3 − 2x + 12x² → (3, −2, 12, 0) | s05, s07 |
| collapse pair | x² + 5 and x² − 2 → both 2x | s06 |
| cascade | (2, 3, −1, 4) → (3, −2, 12, 0) → (−2, 24, 0, 0) → (24, 0, 0, 0) → (0, 0, 0, 0) | s07 |
| rotation | basis (cos, sin): D = [[0, 1], [−1, 0]], clockwise quarter turn; D² = −I; D⁴ = I | s08 |
| mixed arrow | 2 cos x + sin x = (2, 1) → derivative (1, −2) = cos x − 2 sin x | s08 |
| integral | D⁻¹ = (1/√2)·(45° counterclockwise turn) = ½[[1, −1], [1, 1]]; D⁻¹(0, 1) = (−½, ½) → ∫eˣ sin x dx = ½eˣ(sin x − cos x) + C | s09 |
| eigen | D e^{λx} = λ e^{λx}; shown λ = 1, 2, −1 | s10 |
| spring | y″ + y = 0 → y = C₁ cos x + C₂ sin x (null space of D² + 1). Example: y(0) = 1, y′(0) = 0.5 → (1, 0.5) | s11 |
| string matrix | N = 200 interior points, L = 1, (1, −2, 1)/Δx², ends pinned. Eigenvalues −9.869, −39.475, −88.810 vs −(kπ)² = −9.870, −39.478, −88.826. Mode k ∝ sin(kπx) | s12, s13 |
| pluck | triangle pluck at x = 0.2 projected onto the first 12 modes (coefficients from numpy); frequency ∝ k | s13 |
| sound | 110 Hz fundamental (A2), harmonics k·110 Hz weighted by the pluck coefficients with an exponential decay. Mixed under the narration, seeded, about −24 dB below the voice | s13 |
| shift | p(x) = 0.3x³ − x + 0.5 (any cubic), h = 1.2: e^{hD} p = p(x + h) exactly (series ends at D³) | s14 |
| asterisk | e^{−1/x²} (0 at x = 0): every derivative at 0 is 0 | s14 |

## Visual system

Design: **Classic** (memory: crisp reference style). Pure black, crisp unglowed lines, Computer Modern for all text,
no bloom, glow, blur, vignette, grain or caption text. Symbols and numbers only.

| object | color token | meaning |
|---|---|---|
| the input function f, its samples, its arrow | `C.fn` (yellow, = 009's `vec`) | the thing being moved |
| the output D f (derivatives) | `C.dfn` (sky blue) | where it lands |
| the operator D: band entries, the 4 × 4 entries, "D" itself | `C.op` (coral) | the move |
| first basis function (1, cos, eˣ cos x) and its axis | `C.b1` (green, = 009's `ihat`) | first building block |
| second basis function (x, sin, eˣ sin x) and its axis | `C.b2` (red, = 009's `jhat`) | second building block |
| null space: constants, the +C, the collapse | `C.null` (pink, = 009) | what is lost |
| eigenfunctions e^{λx}, λ, string modes | `C.eigen` (violet, = 009) | what only stretches |
| the string body | `C.string` (ivory) | the physical object |
| the shift h | `C.shift` (amber) | the slide |
| plain numbers being read (sample values, coefficients) | `C.data` (light grey) | data, not acting |
| grid / ghost / panel borders | `C.grid` `C.grid_minor` `C.axis` `C.ghost` `C.frame` | the stage |

Rules for every scene:
- One focal point per frame, at most three things moving. No caption text.
- **Function ↔ column, always linked.** Whenever a function is treated as a vector, its column of samples or
  coefficients sits beside the graph, and the two move together (heights ↔ entries, same color).
- **Matrix columns colored by the basis they come from** (b1 green, b2 red) in s08–s09 and s11, as in 009. The
  polynomial matrix in s05–s07 uses `C.op` for its entries. Its constant slot turns `C.null` from s06 on.
- Function planes (s00, s08, s09, s11) reuse 009's grid look: `C.grid` over `C.grid_minor`. Each axis carries its basis
  function's tiny graph as a label instead of words.
- Callbacks to older videos (determinant, Euler's identity, e, Taylor, Fourier/Laplace) show a small framed thumbnail of
  that video's key frame for ≤ 3 s, top-right, then fade out. No title text.
- **Progress rail** (top-right, from s02): a badge drops (`spring`) at each chapter end: `f ⟶ [⋮]` → band → `+C` →
  `↻` → `λ` → string → `e^{hD}`. s16 gathers them.
- Transform, don't cut: the hook arrow (s00) → the s09 plane; the sine graph → its column (s02) → the band's input
  (s04); the 4 × 4 (s05) → s06 → s07; the cos/sin plane (s08) → the eˣ plane (s09); e^{λx} curves (s10) → the
  exponentials in the s11 Fourier panel; the 1, −2, 1 band (s12) → its eigenvectors (s13); the string's arch (s13) →
  the s14 graph.
- Motion: `smooth` for matrix moves and rotations (1.2–2.0 s), `easy_ease` for the camera, `out_back` for label
  pops, `spring` for badges, ~0.05 s stagger per entry.

### Engines
| engine | used for |
|---|---|
| Manim (ManimLayer) | graphs, axes, function planes, arrows, matrices (006/009 hand-set brackets), Eqns, the progress rail, string curves driven per frame (`m.drive` of a numpy shape) |
| numpy (exact) | samples, difference matrices, the 1000 × 1000 band, eigen-decompositions, pluck coefficients, the cascade, every number on screen |
| skia-python → ArrayLayer | the 1000 × 1000 band heat map and its zoom (crisp nearest-neighbour cells at the 8 × 8 zoom) |
| numpy → audio | the s13 string sound: a seeded harmonic sum written to `assets/string.wav`, mixed in. **aion has no audio-mix step** (checked: `aion catalog`, `Encoder` takes one audio file). Options: an ffmpeg pre-mix into the narration file the render muxes (word timings unchanged), or a small library addition |
| ModernGL | GPU compositing and the 2.5D camera for the 1000 → 8 zoom in s04 |

## Retention plan

| device | where |
|---|---|
| Visual question inside 15 s | s00: the graph of eˣ sin x on black from `fn` (0:01), and `d¹⁰⁰/dx¹⁰⁰ = ?` on `hundredth` (0:11) |
| Answer inside 30 s, *why* inside 60 s | s00: `−2⁵⁰ eˣ sin x` on `one_line` (0:18); the arrow turns on `turns` (0:38), spins on `spin` (0:46) and lands on `backwards` (0:50) |
| Wrong intuition first | s00: product-rule terms pile up and spill off the frame on "fill pages" |
| Claim + preview + map | s01: the claim, four preview shots (null line, rotation, an e^{λx} curve that only stretches, a vibrating string), then the one-sentence map and a 3 s hold |
| Open loops | hook arrow (s00) → explained s09 · "the derivative should be a matrix" (s03) → s04 · "can't be undone" (s06) → "can be undone" (s09) · "Keep that in mind" infinity → s15 |
| Pause and predict | s08 (where does cosine go?), s10 (which function only stretches?), each 2.5 s silence |
| Midpoint re-hook | the midpoint (6:37) falls in s08: predict #1 (6:18), the quarter-turn reveal (6:23) and "the derivative is a rotation" (6:34). The second jolt is s10's eigenvector reveal (8:12) |
| Mode switches | question → spin → montage → sampling → algebra → heat map → matrix → collapse → reveal → predict → rotation → inverse → predict → plane → build → vibrating string + sound → series → honesty → recap |
| Sound payoff | s13: the plucked note is heard, built from the eigenvectors on screen |
| End on the thesis | s16: "Calculus is linear algebra, plus a limit." The limit is drawn: the 8 samples become 1000 become a curve |

## Scenes

Each entry: **title · range**, then purpose, visual, engine, animation, on-screen, narration, in/out.
Beat names in `code` become `beats.py` entries once the audio exists.

### s00_hook · T.start → T.cut_claim (0:00–0:57, 57 s)
- **Purpose:** a concrete question with a surprising one-line answer, answered and *seen* inside 45 s.
- **Visual:** black. The graph of eˣ sin x (`C.fn`) draws left to right on faint axes (`fn` "function", ~0:02).
  `d/dx` and the product rule result eˣ sin x + eˣ cos x pop above it (`first`); `d²/dx²` (`second`). On
  `hundredth` the question `d¹⁰⁰/dx¹⁰⁰ (eˣ sin x) = ?` takes the center. On `fill pages` product-rule terms
  multiply down the frame in grey and spill off the bottom (the wrong way). On `one line` they clear and
  `= −2⁵⁰ eˣ sin x` lands (`out_back`), `−2⁵⁰` in `C.op`. On `flat plane` the graph shrinks into the upper-left corner
  and a function plane fades in: the x-axis labelled with a tiny green graph of eˣ cos x (`C.b1`), the y-axis with a
  tiny red graph of eˣ sin x (`C.b2`). The yellow arrow f = (0, 1) appears. On `turns` it turns 45° clockwise and
  grows √2: the derivative, (1, 1), traced as a dotted arc. Then it keeps going: steps 2, 3, 4 … speeding up
  (step k at 0.6 s → 0.08 s), counter `n = 1 … 100` beside it. The length axis switches to a log scale at step 4
  (rings at 2¹⁰, 2²⁰, … labelled faintly) so the arrow stays on screen. After 12.5 turns it settles pointing
  straight down on `backwards`, ring label `2⁵⁰`.
- **Engine:** Manim (graph, Eqn, plane, arrow), numpy for the step angles and lengths.
- **Animation:** graph `Create` 1.5 s; product-rule spill linear 2 s; spin as one `m.drive` on a precomputed easing of
  the step index (accelerating, then easing into the last step).
- **On-screen:** the graph, `d¹⁰⁰/dx¹⁰⁰ = ?`, `−2⁵⁰ eˣ sin x`, the plane, the arrow, `n`, log rings.
- **Narration:** "Here is a function … So what is its hundredth derivative? … the answer fits on one line … Picture a
  flat plane … turns by an eighth of a turn, and stretches by the square root of two … twelve and a half full turns
  … That's two to the fiftieth."
- **In / out:** from black. Out: the plane and arrow stay.

### s01_claim · T.cut_claim → T.cut_ch1 (0:57–1:45, 48 s)
- **Purpose:** name it ("that's what a matrix does"), state the precise claim, preview four payoffs, map.
- **Visual:** on `matrix does` the 2 × 2 `[[1, 1], [−1, 1]]` (columns green / red) slides out of the arrow's motion and
  sits beside the plane; the plane's grid turns as a whole with it (009's "move you make", 1 s callback). The plane
  clears. On `linear map` the claim is a single symbol line: `D(af + bg) = a Df + b Dg` (f yellow, D coral).
  On `plus one extra idea: the limit` a small `lim` drops under it in grey. Preview, one shot per sentence (~4 s each):
  `+C`: a stack of parallel cubics x² + C all crushing to a single 2x line (pink); `rotation`: cos and sin arrows turning
  a quarter turn; `eigenvector`: eˣ, e²ˣ curves stretching vertically without changing shape (violet); `guitar
  string`: a string with its second mode vibrating. On `listening to that string` everything clears except the string;
  hold 3 s.
- **Engine:** Manim; numpy for the curves.
- **On-screen:** the 2 × 2, `D(af + bg) = a Df + b Dg`, `lim`, the four preview shots.
- **Narration:** "An operation that turns arrows and stretches them … That's what a matrix does. So here is the claim …
  The plus C … is a null space … e to the x … eigenvector … a guitar string … fall out of a matrix. We'll start by
  turning a curve into a list of numbers …" (3 s hold.)
- **In / out:** from s00's plane. Out: the string flattens into the sine graph of s02.

### s02_samples · T.cut_ch1 → T.cut_linear (1:45–2:10, 25 s) · Ch1 A function is a very long vector
- **Purpose:** a function *is* a vector; make the infinite-dimensional idea concrete.
- **Visual:** sin x on [0, 2π] (`C.fn`). Eight vertical sticks drop to it (`eight`); the curve fades, dots remain.
  The eight heights fly right into a bracketed column (values to two decimals, `C.data`), with an 8-dimensional label
  `ℝ⁸`. On `fifty` the dots multiply to 50, the column is now a tall thin strip of tiny numbers; on `thousand` the
  dots touch and become the curve again, and the column is a solid yellow strip (`ℝ¹⁰⁰⁰`).
- **Engine:** Manim; numpy samples.
- **Animation:** sticks staggered 0.05 s; heights fly with `smooth` 0.8 s, staggered; densify with a cross-fade.
- **On-screen:** curve, dots, the column, `ℝ⁸`, `ℝ⁵⁰`, `ℝ¹⁰⁰⁰`.
- **Narration:** Ch1 paragraphs 1–2.
- **In / out:** from the string. Out: the curve and column stay.

### s03_linear · T.cut_linear → T.cut_ch2 (2:10–2:46, 36 s)
- **Purpose:** linearity, the one property that makes D a matrix.
- **Visual:** two curves f (yellow) and g (`C.fn` at 60 %, dashed) with their columns. `add`: the curves add point by
  point (vertical sticks stack), the columns add entry by entry, in sync. `scale by three`: the curve stretches
  vertically, every entry ×3. Then `slope`: tangent lines (sky blue) on f, g, and f + g at the same x; the tangent of
  the sum is the sum of the tangents (slope numbers add). `(f + g)′ = f′ + g′` and `(3f)′ = 3f′` stack, then morph
  into the claim line from s01, which now gets a box. Badge `f ⟶ [⋮]` drops on `Let's build it`.
- **Engine:** Manim.
- **On-screen:** the two rules, the claim line.
- **Narration:** Ch1 paragraphs 3–5.

### s04_band · T.cut_ch2 → T.cut_poly (2:46–3:41, 55 s) · Ch2 The derivative, as a matrix
- **Purpose:** build D as an actual matrix on samples, then show it working.
- **Visual:** zoom on two neighboring dots of the sine; rise and run drawn (`next height minus this height`):
  `(f_{k+1} − f_k)/h`. Then the 8 × 8 matrix writes on row by row: `−1` on the diagonal, `+1` just right of it (coral),
  zeros as faint dots, the `1/h` outside. Each new row highlights the two dots it reads. On `thousand points` the
  camera pulls back: the 8 × 8 shrinks into the corner of a 1000 × 1000 heat map (skia), black with one thin coral
  line down the diagonal. On `multiply` the yellow sine column slides in from the right, the product runs, a sky-blue
  column comes out and unrolls into a curve: cos x, overlaid with the true cos x as a thin dashed white line (they
  match). `≈` between them.
- **Engine:** Manim for the 8 × 8 and curves; skia → ArrayLayer for the 1000 × 1000 band; 2.5D camera for the pull back.
- **On-screen:** the difference quotient, the 8 × 8, the heat map, `D · sin ≈ cos`.
- **Narration:** Ch2 paragraphs 1–4.

### s05_poly · T.cut_poly → T.cut_ch3 (3:41–4:29, 47 s)
- **Purpose:** the exact matrix, no approximation.
- **Visual:** four small graphs 1, x, x², x³ in a row, each with a coefficient slot. The cubic
  p = 2 + 3x − x² + 4x³ builds from them; its column `(2, 3, −1, 4)` beside its graph. On `sends one to zero`, each
  basis graph is differentiated in turn and its result drops into a column of the 4 × 4 (coral), filling
  `[[0,1,0,0],[0,0,2,0],[0,0,0,3],[0,0,0,0]]`. On `multiply` the matrix acts on (2, 3, −1, 4) → `(3, −2, 12, 0)`
  (sky blue), and p′'s graph draws from it. On `No limits` a struck-through `lim` flicks away.
- **Engine:** Manim.
- **On-screen:** basis graphs, the 4 × 4, the column multiply.
- **Narration:** Ch2 paragraphs 5–6. Badge: band.

### s06_null · T.cut_ch3 → T.cut_plus_c (4:29–5:06, 37 s) · Ch3 Why plus C exists
- **Purpose:** constants are the null space; D can't be undone.
- **Visual:** the 4 × 4 stays; its first column of zeros glows pink. A constant function (horizontal line at 5)
  enters and the matrix returns the zero column. Then the picture: a stack of horizontal lines y = 5, y = −2,
  y = 1,000,000 (an arrow off-frame), all funnelling into one dot labelled `0` (pink). `null space` as a symbol:
  `ker D = {C}`. On `determinant is zero` a 1 s 006 callback thumbnail (a square flattening to a line), and
  `det D = 0` in pink. On `x squared plus five` two parabolas, x² + 5 and x² − 2, differentiate into the *same* 2x line,
  which lands on one curve; a reverse arrow with a `?` tries to go back and splits into two.
- **Engine:** Manim.
- **On-screen:** `ker D`, `det D = 0`, the two parabolas → `2x`.
- **Narration:** Ch3 paragraphs 1–3.

### s07_plus_c · T.cut_plus_c → T.cut_ch4 (5:06–5:55, 49 s)
- **Purpose:** the reveal: +C is the null space of D.
- **Visual:** `D F = f` (F yellow, f sky blue). Under it, the shape of every solution of a singular system:
  `F = F_p + (null space)`. Then specific: `∫2x dx = x² + C`, the `+ C` sliding up out of the pink null space symbol.
  The family x² + C fans out as a stack of parabolas, all with the same slope field (tiny tangent ticks align).
  On `odd habit` the cascade: (2, 3, −1, 4) → (3, −2, 12, 0) → (−2, 24, 0, 0) → (24, 0, 0, 0) → (0, 0, 0, 0), each
  entry sliding up one slot as the top one falls off and fades to pink. `D⁴ = 0`.
- **Engine:** Manim.
- **On-screen:** `D F = f`, `x² + C`, the cascade, `D⁴ = 0`. Badge `+C`.
- **Narration:** Ch3 paragraphs 4–6.

### s08_rotation · T.cut_ch4 → T.cut_inverse (5:55–6:59, 64 s) · Ch4 The derivative is a rotation
- **Purpose:** on span{cos, sin}, D is a quarter turn.
- **Visual:** the function plane again: green axis = cos (tiny graph label), red axis = sin. The mix 2 cos x + sin x
  appears as the yellow arrow (2, 1) with its graph in a small inset. On `pause and predict` the cos arrow pulses;
  2.5 s silence, a faint `?`. Then the cos arrow swings down to −sin, the sin arrow swings right to cos (clockwise),
  then the whole grid turns with them; the (2, 1) arrow goes to (1, −2) and the inset graph becomes its derivative.
  `D = [[0, 1], [−1, 0]]` (columns green / red). Then four quarter turns, each stamped with its function:
  sin → cos → −sin → −cos → sin, the cycle drawn as a square loop. `D² = −I`, `D⁴ = I`. On `i squared` a 2 s callback
  thumbnail of the Euler-identity quarter turn.
- **Engine:** Manim.
- **On-screen:** the plane, D, the cycle, `D² = −I`.
- **Narration:** Ch4 paragraphs 1–4 (with the 2.5 s pause).

### s09_inverse · T.cut_inverse → T.cut_ch5 (6:59–7:42, 43 s)
- **Purpose:** close the hook's loop; integration as a matrix inverse.
- **Visual:** the axis labels morph: cos → eˣ cos x, sin → eˣ sin x (green / red stay). The hook's arrow returns and
  turns one 45° step with its √2 growth; `D = [[1, 1], [−1, 1]]`, `det D = 2` (contrast with the pink `det = 0` from
  s06, recalled small). On `integral` the target `∫eˣ sin x dx` appears; the arrow (0, 1) turns **back** 45° and
  shrinks by √2 → (−½, ½). `D⁻¹ = ½[[1, −1], [1, 1]]`. The coordinates read off: `½eˣ(sin x − cos x)`. Check: a quick
  forward turn returns it to (0, 1) ✓. `+ C` drops in pink.
- **Engine:** Manim.
- **On-screen:** the plane, D, D⁻¹, the integral result. Badge `↻`.
- **Narration:** Ch4 paragraphs 5–6.

### s10_eigen · T.cut_ch5 → T.cut_ode (7:42–8:43, 62 s) · Ch5 The eigenvectors of the derivative
- **Purpose:** e^{λx} is the eigenvector of D. The midpoint re-hook.
- **Visual:** a 1 s 009 callback: a grid move with two violet lines that don't turn. The question: `D f = λ f ?`.
  Predict pause 2.5 s. Candidates in a row, each with its graph and its derivative overlaid: sin (derivative is a
  shifted wave, `✗`), x² (different shape, `✗`), eˣ (derivative lies exactly on top, violet glow-free highlight, `✓`).
  Then e²ˣ: its derivative is the same shape, stretched ×2 vertically; e^{−x}: flipped. The general line
  `D e^{λx} = λ e^{λx}`, λ violet. On `everywhere` a 1 s callback thumbnail of the e video, then three tiny
  growth/decay curves (money, population, decay) labelled only with `y′ = ky`.
- **Engine:** Manim.
- **On-screen:** `D f = λ f`, the candidates, `D e^{λx} = λ e^{λx}`, `y′ = ky`.
- **Narration:** Ch5 paragraphs 1–4.

### s11_ode · T.cut_ode → T.cut_ch6 (8:43–9:35, 52 s)
- **Purpose:** ODEs are null spaces; Fourier/Laplace diagonalize D.
- **Visual:** a spring (simple zig-zag with a mass) oscillates at left; `y″ + y = 0` → `(D² + 1) y = 0`. The cos/sin
  plane returns: the whole plane lights pink (the null space of D² + 1 is all of it). A point (1, 0.5) in the plane,
  and its curve cos x + 0.5 sin x driving the spring; two sliders "start position", "start speed" are just the two
  coordinates (no words: `y(0)`, `y′(0)`). On `Fourier and Laplace` the 4 × 4-style matrix of D in an exponential basis
  appears **diagonal**: `diag(λ₁, λ₂, λ₃, …)` with the eˣ-family curves from s10 as its basis labels; the
  off-diagonal entries visibly zero. Small callback thumbnails of the Fourier and Laplace videos, 2 s each. `D = diag`.
- **Engine:** Manim.
- **On-screen:** the ODE, the plane, `y(0)`, `y′(0)`, the diagonal matrix. Badge `λ`.
- **Narration:** Ch5 paragraphs 5–6.

### s12_string · T.cut_ch6 → T.cut_modes (9:35–10:02, 27 s) · Ch6 A guitar string is an eigenvector problem
- **Purpose:** set up the real system: bending = second derivative = a matrix.
- **Visual:** an ivory string between two pins, displaced into a gentle bump. Arrows along it show the restoring pull,
  longest where it bends most (computed from the discrete second difference). `u″` beside it. Then 200 dots on the
  string; one dot and its two neighbors highlighted: `u_{k−1} − 2u_k + u_{k+1}`. The matrix builds as in s04: the
  tri-band 1, −2, 1 (coral), with the 8 × 8 close-up then a pull back to the full 200 × 200 band. Pins drawn as two
  solid ends on the matrix (first and last row).
- **Engine:** Manim; skia band.
- **On-screen:** the string, pull arrows, `1  −2  1`, the band.
- **Narration:** Ch6 paragraphs 1–4.

### s13_modes · T.cut_modes → T.cut_ch7 (10:02–10:59, 58 s)
- **Purpose:** the showpiece: eigenvectors of the matrix *are* the harmonics; hear them.
- **Visual:** `eig` runs: three violet curves rise out of the band one by one and settle as stacked strings: one arch,
  two, three. Beside each, its eigenvalue vs the exact one: `−9.869 ≈ −π²`, `−39.48 ≈ −4π²`, `−88.81 ≈ −9π²`. Then each
  mode vibrates in place at a speed ∝ k (1 : 2 : 3). On `Pluck` the ivory string is pulled into a triangle at x = 0.2,
  released, and its motion is the sum of 12 modes (each mode's amplitude shown as a small bar, violet). The
  **sound plays**: the plucked note built from those same modes. On the last line the stacked modes brighten to full violet, then the badge (string) drops.
- **Engine:** numpy eigen-decomposition and modal sum, Manim curves via `m.drive`, audio as in Engines.
- **On-screen:** modes, eigenvalues, the pluck, mode bars.
- **Narration:** Ch6 paragraphs 5–7.

### s14_shift · T.cut_ch7 → T.cut_outro (10:59–12:08, 68 s) · Ch7 The exponential of the derivative
- **Purpose:** e^{hD} = shift; Taylor series as a matrix exponential; the honest asterisk.
- **Visual:** `eˣ = 1 + x + x²/2! + …` then `x` is replaced by `hD` (D coral, h amber):
  `e^{hD} = 1 + hD + h²D²/2! + …`. Apply to a cubic p (yellow): the terms p, hp′, h²p″/2, h³p‴/6 are drawn as curves and
  added one at a time; the running sum visibly slides toward p(x + h), landing exactly on it after four terms (it's a
  cubic, so D⁴ = 0, a callback to s07). An amber arrow of length h shows the slide; the graph glides sideways. 1 s
  thumbnail callback to the Taylor video. On `asterisk` the graph of e^{−1/x²} (flat near 0) and its Taylor series at 0:
  the zero line. `T(x) = 0 ≠ f(x)` for x ≠ 0. Badge `e^{hD}`.
- **Engine:** Manim.
- **On-screen:** the two series, the partial sums, `e^{hD} p(x) = p(x + h)`, the counterexample.
- **Narration:** Ch7.

### s15_infinity · T.cut_outro → T.cut_recap (12:08–12:56, 48 s) · Outro: where the analogy breaks
- **Purpose:** honest limits of the picture.
- **Visual:** the 1000-sample column from s02 grows taller, past the frame, `ℝ^∞`. `det D` appears and is struck out.
  A row of e^{λx} curves for many λ (a violet fan) on `every number is an eigenvalue`. Then the limit: dots → curve,
  `lim_{h→0}`. A small 3-symbol frame for quantum: `Ĥψ = Eψ` (the eigenvalue form, a nod to the same idea), held 2 s.
- **Engine:** Manim.
- **On-screen:** `ℝ^∞`, struck `det`, the λ fan, `lim`, `Ĥψ = Eψ`.
- **Narration:** Outro paragraphs 1–3.

### s16_recap · T.cut_recap → T.end (12:56–13:14, 18 s)
- **Purpose:** land the thesis; callback to every chapter.
- **Visual:** the badges gather into a column, each lighting its one-line restatement as it's spoken:
  `+C = ker D`, `D = ↻`, `D eˣ = eˣ`, the string's first mode, and finally
  `calculus = linear algebra + lim`. The 8 dots from s02 densify into a curve one last time on `plus a limit`. Hold
  on black 3 s (end-screen space at the right third).
- **Engine:** Manim.
- **Narration:** Outro paragraph 4.

## Open decisions for the user
1. Ch7 (Taylor = e^{hD}) is in the audio (68 s). Dropping it now means re-generating the outro chunk, so the default is to keep it.
2. The string sound in s13: aion has no audio mixing. Pre-mix it with ffmpeg (simplest), add a mix step to aion, or skip the sound?
3. Callback thumbnails of older videos (≤ 3 s each): OK to reuse their key frames?

## Beat table

`uv run aion beats 010-calculus-is-linear-algebra --md` (2026-11-17)

| beat | time | end | words |
|---|---|---|---|
| fn | 1.50 | 2.57 | Here is a function |
| first | 5.69 | 6.88 | Its first derivative |
| second | 8.86 | 10.25 | The second takes two |
| hundredth | 11.64 | 12.79 | its hundredth derivative |
| pages | 16.18 | 17.29 | would fill pages |
| one_line | 17.86 | 19.46 | the answer fits on one line |
| flipped | 21.24 | 22.39 | flipped upside down |
| see_why | 25.33 | 26.18 | And you can see why |
| plane | 26.75 | 28.52 | Picture a flat plane |
| axis_cos | 28.52 | 29.56 | One direction means |
| axis_sin | 31.36 | 32.20 | The other means |
| arrow | 34.09 | 35.48 | Our function is an arrow |
| turns | 37.88 | 39.24 | the arrow turns by an eighth |
| stretches | 40.28 | 41.48 | stretches by the square root |
| every_derivative | 42.50 | 44.12 | Every derivative does exactly |
| spin | 45.85 | 47.02 | A hundred eighth turns |
| backwards | 50.02 | 51.17 | pointing straight backwards |
| stretched | 52.38 | 53.74 | stretched by root two |
| fiftieth | 55.28 | 56.63 | That's two to the fiftieth |
| cut_claim ✂ | 57.13 | 57.13 | two to the fiftieth. ✂ An operation that turns |
| operation | 57.63 | 59.04 | An operation that turns |
| not_calculus | 61.28 | 62.40 | not what calculus is supposed |
| matrix_does | 63.41 | 64.63 | That's what a matrix does |
| claim | 65.61 | 66.66 | So here is the claim |
| linear_map | 68.42 | 70.53 | Taking a derivative is a linear map |
| surprising | 74.45 | 76.02 | a surprising amount of calculus |
| limit | 79.56 | 79.96 | the limit |
| pv_plus_c | 80.85 | 82.20 | The plus C you were told |
| pv_rotation | 84.53 | 86.52 | Sine and cosine cycle forever |
| pv_eigen | 89.04 | 90.36 | e to the x is special |
| pv_string | 92.36 | 93.48 | the notes a guitar string |
| map | 96.30 | 97.66 | We'll start by turning a curve |
| listening | 100.02 | 100.88 | listening to that string |
| cut_ch1 ✂ | 104.87 | 104.87 | to that string. ✂ Take a curve |
| curve | 105.84 | 106.76 | Take a curve |
| eight | 109.56 | 110.96 | keep only its height at eight |
| stack | 113.76 | 114.67 | Stack them in a column |
| eight_dims | 115.12 | 116.59 | a vector in eight dimensions |
| fifty | 117.49 | 119.02 | Sample it at fifty points |
| thousand | 121.08 | 122.05 | At a thousand |
| blur | 124.02 | 125.23 | blur back into a curve |
| computer_stores | 125.73 | 126.98 | That's how a computer stores |
| cut_linear ✂ | 129.62 | 129.62 | a very long vector. ✂ And functions behave |
| behave | 130.05 | 131.86 | And functions behave like vectors |
| add | 132.19 | 133.19 | Add two curves |
| scale | 137.37 | 138.89 | Scale a curve by three |
| watch | 141.78 | 142.86 | watch what the derivative does |
| slope_sum | 143.73 | 144.86 | The slope of a sum |
| slope_three | 146.70 | 147.82 | the slope of three times |
| two_rules | 150.57 | 151.44 | Those two rules |
| every_matrix | 155.28 | 157.10 | the rules every matrix obeys |
| should_be | 162.17 | 163.88 | the derivative should be a matrix |
| build_it | 164.44 | 164.97 | Let's build it |
| cut_ch2 ✂ | 166.07 | 166.07 | build it. ✂ The slope at a point |
| rise | 167.22 | 168.22 | The slope at a point |
| next_minus | 171.58 | 172.74 | Next height |
| every_point | 176.40 | 177.84 | write that down for every point |
| row | 178.78 | 180.16 | Each row of the matrix |
| minus_one | 181.64 | 182.95 | minus one on the diagonal |
| plus_one | 183.25 | 184.60 | plus one just to its right |
| zeros | 185.36 | 186.00 | zeros everywhere |
| divide | 186.96 | 188.24 | Then divide everything |
| zoom_out | 189.86 | 191.66 | Zoom out to a thousand points |
| almost_zero | 194.37 | 195.67 | Almost all of them are zero |
| band | 197.14 | 198.50 | one thin, bright band |
| multiply | 200.45 | 201.52 | Now multiply |
| feed_sin | 201.76 | 203.32 | Feed it the column for sine |
| plot_back | 205.18 | 206.59 | Plot it back as a curve |
| cosine | 206.92 | 207.88 | it's cosine x |
| took | 208.15 | 210.60 | The computer just took a derivative |
| physics | 213.87 | 214.92 | Physics simulations |
| cut_poly ✂ | 221.40 | 221.40 | mostly empty matrices. ✂ That matrix is an approximation |
| approximation | 221.85 | 223.77 | That matrix is an approximation |
| no_approx | 227.50 | 228.86 | you don't need an approximation |
| polys | 230.00 | 231.93 | Take the polynomials up to x cubed |
| blocks | 233.98 | 234.96 | four building blocks |
| four_numbers | 239.02 | 240.54 | a cubic is really just four |
| sends | 241.55 | 243.29 | The derivative sends one to zero |
| lands | 248.61 | 250.22 | Write where each building block lands |
| four_by_four | 251.58 | 252.94 | an exact four by four |
| above_diag | 255.39 | 256.81 | sitting just above the diagonal |
| mult_cubic | 257.34 | 258.86 | Multiply it by the four numbers |
| no_limits | 262.59 | 263.62 | No limits |
| by_matrix | 265.02 | 266.86 | Calculus, done entirely |
| cut_ch3 ✂ | 268.72 | 268.72 | done entirely by a matrix. ✂ Look at the first column |
| first_col | 269.67 | 270.60 | Look at the first column |
| all_zeros | 271.79 | 272.91 | It's all zeros |
| constant | 273.14 | 274.40 | Feed it a constant |
| crushed | 278.41 | 280.14 | a whole direction gets crushed |
| every_constant | 281.34 | 282.52 | Every constant function |
| same_point | 285.31 | 286.37 | lands on the same point |
| null_space | 287.82 | 289.04 | is called the null space |
| undone | 291.84 | 293.09 | can never be undone |
| det_zero | 293.38 | 294.84 | Its determinant is zero |
| no_way | 297.89 | 298.96 | there is no way to tell |
| parabolas | 300.88 | 301.97 | x squared plus five |
| two_x | 303.43 | 305.22 | both have derivative two x |
| cut_plus_c ✂ | 305.63 | 305.63 | derivative two x. ✂ So think about what integration |
| integration | 306.06 | 307.62 | So think about what integration |
| find | 308.94 | 310.74 | Find a function whose derivative |
| dff | 314.11 | 316.08 | D times F equals f |
| crushed_system | 318.30 | 319.86 | what the answer to a crushed system |
| particular | 320.74 | 322.04 | One particular solution |
| constants | 325.83 | 327.36 | the null space is the constants |
| plus_c | 327.64 | 328.60 | That's the plus C |
| memorize | 328.94 | 330.64 | It isn't a rule to memorize |
| must | 335.48 | 337.77 | exactly where linear algebra says it must |
| odd_habit | 339.90 | 340.91 | one more odd habit |
| slides | 342.72 | 344.95 | every coefficient slides one slot up |
| four_times | 347.17 | 348.54 | Apply it four times |
| nothing_left | 353.10 | 353.96 | nothing is left |
| cut_ch4 ✂ | 354.97 | 354.97 | is left. ✂ Let's change the building |
| change_blocks | 355.95 | 356.92 | Let's change the building |
| cos_sin | 360.82 | 361.93 | cosine and sine |
| mix | 363.61 | 365.67 | like two cosine x plus sine x |
| cos_deriv | 370.88 | 372.85 | Cosine's derivative is minus sine |
| sin_deriv | 373.17 | 374.69 | Sine's derivative is cosine |
| where_go | 374.93 | 376.70 | So where does the cosine arrow go |
| predict1 | 378.07 | 379.11 | Pause and predict |
| cos_swings | 382.60 | 383.97 | Cosine, pointing right |
| sin_swings | 386.65 | 388.22 | Sine, pointing up |
| quarter | 390.22 | 392.12 | Both arrows turn a quarter turn |
| rotation | 394.34 | 395.88 | the derivative is a rotation |
| old_facts | 397.28 | 398.63 | the old facts read differently |
| twice | 399.02 | 400.28 | Differentiate twice |
| minus_sine | 404.36 | 406.72 | the second derivative of sine is minus sine |
| full_turn | 407.00 | 408.84 | Four derivatives make a full turn |
| cycle | 410.52 | 413.64 | sine, cosine, minus sine, minus cosine |
| i_squared | 415.20 | 417.40 | the same quarter turn that makes i squared |
| cut_inverse ✂ | 418.77 | 418.77 | equal minus one. ✂ And this is the secret |
| secret | 419.24 | 421.43 | And this is the secret behind the opening |
| swap_in | 421.70 | 423.58 | Swap in e to the x cosine |
| eighth | 426.38 | 427.98 | each derivative turns by an eighth |
| crushes_nothing | 432.38 | 433.75 | this one crushes nothing |
| det_two | 434.03 | 435.55 | Its determinant is two |
| trick | 437.32 | 438.16 | That gives a trick |
| by_parts | 442.64 | 443.72 | integration by parts |
| inverse | 446.13 | 447.28 | it is just the inverse |
| turn_back | 448.03 | 449.04 | turn back by an eighth |
| out_comes | 451.80 | 453.48 | comes one half e to the x |
| check | 455.74 | 456.69 | Differentiate that |
| plus_c2 | 459.39 | 460.51 | Add the plus C |
| cut_ch5 ✂ | 461.90 | 461.90 | you're done. ✂ In linear algebra, the most revealing |
| revealing | 464.14 | 465.42 | the most revealing question |
| leave_alone | 467.85 | 469.70 | Which directions does it leave alone |
| only_stretch | 471.26 | 473.01 | only stretch, and never turn |
| ask_d | 473.99 | 475.66 | So ask the derivative |
| which_fn | 475.93 | 477.36 | Which function comes back |
| predict2 | 480.83 | 481.97 | Pause and predict |
| not_sine | 485.65 | 486.39 | Not sine |
| not_x2 | 488.99 | 490.07 | Not x squared |
| answer_ex | 491.79 | 493.83 | The answer is e to the x |
| itself | 494.14 | 495.64 | Its derivative is itself |
| doubled | 497.60 | 498.41 | comes back doubled |
| flipped_x | 500.08 | 501.56 | comes back flipped |
| lambda_x | 501.72 | 503.72 | Every function e to the lambda x |
| everywhere | 508.58 | 510.98 | the deepest reason e shows up everywhere |
| proportional | 512.22 | 513.66 | changes at a rate proportional |
| one_family | 520.70 | 522.30 | only one family of functions |
| cut_ode ✂ | 523.43 | 523.43 | functions answers. ✂ Differential equations become |
| diffeq | 523.97 | 525.36 | Differential equations become |
| spring_eq | 527.36 | 529.44 | y double prime plus y equals zero |
| spring | 529.71 | 531.44 | the equation of a spring |
| operator | 531.44 | 532.65 | Read it as an operator |
| solutions | 536.05 | 538.40 | So its solutions are exactly the null space |
| flat | 539.54 | 541.33 | A null space is always flat |
| plane2 | 541.92 | 543.08 | this one is a plane |
| two_numbers | 545.68 | 547.04 | Two numbers pick out one |
| conditions | 550.75 | 552.08 | where it begins and how fast |
| channel | 554.08 | 555.49 | a trick from earlier on this channel |
| fourier | 555.94 | 557.76 | The Fourier and Laplace transforms |
| eigenbasis | 561.73 | 563.64 | the derivative's own eigenbasis |
| multiplied | 567.24 | 568.24 | multiplied by its own |
| algebra | 569.92 | 571.52 | turning calculus into algebra |
| diagonalizing | 572.62 | 574.41 | It's diagonalizing the derivative |
| cut_ch6 ✂ | 575.38 | 575.38 | diagonalizing the derivative. ✂ Let's put the matrix to work |
| hear | 577.74 | 578.66 | something you can hear |
| pinned | 579.54 | 581.04 | A guitar string is pinned |
| bends | 582.27 | 583.55 | Where it bends more sharply |
| second_deriv | 586.96 | 587.81 | its second derivative |
| build | 589.42 | 591.35 | build the second derivative as a matrix |
| two_hundred | 592.10 | 593.39 | hundred points along the string |
| neighbors | 593.63 | 595.89 | Each row takes a point's two neighbors |
| one_m2_one | 598.14 | 599.84 | One, minus two, one |
| pin_ends | 600.21 | 601.89 | Pin both ends at zero |
| cut_modes ✂ | 602.35 | 602.35 | ends at zero. ✂ Now ask the computer |
| ask_computer | 602.87 | 604.04 | Now ask the computer |
| eigvecs | 606.72 | 608.75 | What are this matrix's eigenvectors |
| only_scale | 609.04 | 610.67 | Which shapes does it only scale |
| out_come | 611.77 | 612.80 | Out come these |
| arch1 | 613.20 | 614.08 | A single arch |
| arch2 | 614.40 | 615.11 | Two arches |
| arch3 | 615.37 | 615.71 | Three |
| sine_waves | 616.82 | 618.14 | sine waves, each fitting |
| nobody | 620.69 | 622.70 | Nobody typed in a sine |
| eigvals | 625.98 | 627.02 | their eigenvalues match |
| vibrate | 631.52 | 634.16 | Each eigenvector is a way the string can vibrate |
| how_fast | 637.74 | 640.04 | Its eigenvalue sets how fast |
| octave | 643.60 | 644.32 | one octave up |
| three_fast | 644.56 | 646.00 | The third, three times |
| pluck | 647.63 | 648.53 | Pluck the string |
| note | 653.25 | 654.74 | That mix is the sound |
| overtones | 656.13 | 657.14 | The overtones you hear |
| cut_ch7 ✂ | 659.95 | 659.95 | eigenvectors of a matrix. ✂ One last move |
| last_move | 660.93 | 661.85 | One last move |
| exp_series | 663.39 | 664.76 | e to the x is one |
| for_matrices | 668.72 | 670.53 | That same series works for matrices |
| exponent | 672.24 | 674.27 | put the derivative itself in the exponent |
| ehd | 675.45 | 677.33 | e to the h D is one |
| apply | 683.86 | 684.86 | Apply it to a function |
| taylor | 690.41 | 691.71 | That's the Taylor series |
| x_plus_h | 694.47 | 695.99 | evaluated at x plus h |
| shift | 697.48 | 699.80 | the exponential of the derivative is a shift |
| slides_h | 700.20 | 701.64 | It slides the whole graph |
| tiny | 703.29 | 704.28 | Tiny changes |
| asterisk | 707.46 | 708.80 | One honest asterisk |
| only_works | 709.36 | 710.78 | This only works for functions |
| fails | 716.62 | 718.67 | There are smooth functions where it fails |
| bump | 718.98 | 720.78 | e to the minus one over x squared |
| zero_series | 725.58 | 727.47 | its Taylor series there is just zero |
| cut_outro ✂ | 728.43 | 728.43 | there is just zero. ✂ So, is calculus secretly |
| secretly | 729.41 | 731.24 | So, is calculus secretly |
| mostly | 732.51 | 733.69 | Mostly, yes |
| second_half | 735.24 | 736.79 | has a second half |
| every_point2 | 738.30 | 739.55 | a value at every point |
| infinite | 741.50 | 743.54 | a vector with infinitely many entries |
| no_det | 749.10 | 750.12 | it has no determinant |
| every_eigenvalue | 752.97 | 754.97 | every number is an eigenvalue |
| takes_limit | 760.66 | 761.15 | takes a limit |
| cant_do | 763.34 | 764.04 | can't do for you |
| functional | 767.60 | 769.02 | called functional analysis |
| quantum | 771.04 | 772.16 | quantum mechanics |
| cut_recap ✂ | 776.17 | 776.17 | just like the derivative. ✂ But the picture holds |
| holds | 776.68 | 777.73 | But the picture holds |
| r_plus_c | 778.74 | 779.84 | C is a null space |
| r_rotation | 780.19 | 782.39 | Sine and cosine are a rotation |
| r_eigen | 782.71 | 784.55 | e to the x is an eigenvector |
| r_string | 784.71 | 787.49 | A guitar string is an eigenvector problem |
| r_thesis | 787.90 | 789.59 | Calculus is linear algebra |
| r_limit | 791.30 | 791.30 | plus a limit |
240 beats, 17 scenes, audio 793.82s
