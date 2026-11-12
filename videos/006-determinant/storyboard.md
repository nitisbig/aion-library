# What the Determinant Actually Means: storyboard

Audio: `assets/audio.wav` (479.22 s = 7:59, 1,298 words, about 163 words a minute, voice speed 0.92)

Pacing (`voice.toml [pacing]`): 1.5 s lead-in, +0.5 s after each paragraph, +1.5 s between chapters, 3.0 s tail.
Captions for YouTube: `assets/subtitles.srt`. Full beat table at the end of this file.

Structure: intro, seven chapters, outro. Ten scene files (chapter 2 is split in two so no scene runs past ~65 s).

| # | scene | chapter | range | length | mode |
|---|---|---|---|---|---|
| 0 | `s00_intro` | Intro: the hook and the preview | 0:00–0:53 | 53 s | cinematic preview |
| 1 | `s01_matrix` | Ch1 A matrix moves space | 0:53–1:51 | 58 s | visual, 2D grid |
| 2 | `s02_area` | Ch2 One number for the stretch | 1:51–2:41 | 50 s | measurement |
| 3 | `s02b_predict` | Ch2 (cont.) test it, then predict | 2:41–3:13 | 33 s | examples, pause-and-predict |
| 4 | `s03_formula` | Ch3 Where the formula comes from | 3:13–4:16 | 63 s | derivation |
| 5 | `s04_sign` | Ch4 When the determinant is negative | 4:16–5:24 | 67 s | surprise, re-hook at the midpoint |
| 6 | `s05_zero` | Ch5 When the determinant is zero | 5:24–6:19 | 56 s | particles, application |
| 7 | `s06_three_d` | Ch6 Three dimensions | 6:19–7:00 | 41 s | 2D → 3D |
| 8 | `s07_product` | Ch7 The payoff: det(AB) | 7:00–7:27 | 27 s | payoff |
| 9 | `s08_outro` | Outro: what we found | 7:27–7:59 | 32 s | recap, final callback |

## The running example

One matrix for the whole video, so every number on screen is one the viewer has already met:

    A = [[3, 1], [1, 2]]     columns (3, 1) and (1, 2)     det = 3·2 − 1·1 = 5

| use | matrix | det | where |
|---|---|---|---|
| running example | `[[3, 1], [1, 2]]` | 5 | Ch1–Ch4, Ch7, outro |
| pure stretch | `[[2, 0], [0, 3]]` | 6 | Ch2 test |
| shear | `[[1, 1], [0, 1]]` | 1 | Ch2 predict |
| columns swapped | `[[1, 3], [2, 1]]` | −5 | Ch4 |
| collapse | `[[2, 4], [1, 2]]` | 0 | Ch5 (both columns on the line through (2, 1)) |
| second matrix | `[[2, 1], [0, 1]]` | 2 | Ch7 (5 × 2 = 10) |
| 3 × 3 | columns (2, 0, 0), (1, 2, 0), (0, 1, 1.5) | 6 | Ch6 (volume 6; verified with numpy at build time) |

These live in `shots.py` (`A_MAIN`, `A_SWAP`, `A_ZERO`, `A_SCALE`, `A_SHEAR`). All areas and readouts are computed
from the matrices, never typed in.

## Visual system

Design: **4 · Classic** (default; sheet `out/design/design_4.png`). Pure black, crisp unglowed lines, a bright blue
integer grid over a dim half-step grid, white axes, Computer Modern for all text (chapter titles set in LaTeX).
Designs 1–3 (`design_sheet.py --all`) define the same roles and stay available with `--design N`.

| object | color token | meaning |
|---|---|---|
| i-hat, first column (a, c) | `C.ihat` | where the first basis arrow lands |
| j-hat, second column (b, d) | `C.jhat` | where the second basis arrow lands |
| k-hat, third column | `C.khat` | Ch6 only |
| unit square, parallelogram, box, a positive determinant | `C.area` | the thing being measured |
| flipped area, the minus sign | `C.flip` | orientation reversed |
| the line or plane space collapses onto, det = 0 | `C.collapse` | information lost |
| pieces removed from the bounding rectangle | `C.cutaway` | Ch3 only |
| moving grid / original grid left behind | `C.grid` / `C.ghost` | the stage, never the subject |

Rules for every scene:
- Pure black background. One focal point per frame, at most three things moving.
- No explanatory captions on screen: only symbols, equations and the occasional key word. The narration explains.
- The matrix (`shots.Mat`, hand-set square brackets) sits top-left in a thin-bordered black panel whenever a grid is
  on screen, columns colored `C.ihat` / `C.jhat` with the hat symbol over each column. A determinant readout sits
  beside it and counts continuously while the grid moves (computed from the live matrix).
- Progress rail, bottom-left: seven small ticks, one per chapter, the current one lit. Each chapter leaves a
  badge that stays for the rest of the video: the grid → `× 5` → `ad − bc` → `±` → `0` → the box → `det(AB)`.
  The outro gathers these badges, so the recap is things the viewer already saw being made.
- Equations build one term at a time, on the word that names the term. Nothing appears before it is spoken.
- Transform, do not cut: the unit square from Ch2 is the same object that becomes the parallelogram in Ch3,
  flips in Ch4, flattens in Ch5 and lifts into a cube in Ch6.
- Finishing: none. No glow, bloom, blur, vignette or grain; lines stay crisp. Side-by-side views use framed panels
  (`shots.panel`: black inside, thin light border).

## Retention plan

| device | where |
|---|---|
| Promise in the first 15 s | `adbc` (0:11): the formula everyone memorised, then "long before anyone told you what it is" |
| Wrong intuition first | `recipe` (0:22) "just a recipe… But watch." |
| Preview the result, unexplained | 0:27–0:39: stretch, flip and collapse flash past in three short shots |
| Map in one sentence | `square` (0:47) "start with a single square, end by flattening three dimensional space" |
| Open loop 1 | "something has been destroyed" (0:35) → paid off in Ch5 (`info`, 5:52) |
| Open loop 2 | "How much did space just stretch?" (1:48) closes Ch1 and opens Ch2 |
| Pause and predict | the shear (`ask`, 3:02): a full second of silence before "It is one" |
| Midpoint re-hook | `neg5` (4:22) "what would a determinant of negative five mean?" |
| Plant and payoff | Ch4 ends on "zero is the most important value" → Ch5 |
| Mode switches | preview → grid → measurement → examples → derivation → flip → particles → 3D → payoff |
| End on the payoff | the last line turns `ad − bc` back into the parallelogram; no spoken list after it |

## Scenes

### s00_intro · T.start → T.cut_ch1  (0:00–0:53, 53 s)
- **Narration:** "Take a matrix… A times D, minus B times C… long before anyone told you what it is… But watch. This
  one number knows how much a matrix stretches space… flipped over… destroyed… see a picture instead of a
  formula… start with a single square, and end by flattening three dimensional space."
- **Visual idea (why it explains):** the familiar thing first, then the surprise. A bare `[[a, b], [c, d]]` writes on.
  Two diagonal strokes cross it on "multiply them in a cross" and `ad − bc` drops out below, exactly the school
  ritual. On "just a recipe" the formula dims to grey. On "But watch" the four letters lift off and become the
  two arrows of a grid, and three short shots preview the whole video: the grid stretches and a gold square swells
  (`stretches`), the grid turns over and the square goes violet (`flipped`), the grid folds onto a red line and
  the square vanishes (`zero`, `destroyed`). On the promise the formula returns, now in color, sitting on the
  parallelogram it measures. On the map sentence: one gold unit square alone (`square`), which lifts into a cube
  and is pressed flat (`flatten`).
- **Beats:** `matrix`, `four`, `cross`, `adbc`, `named`, `learned`, `recipe`, `watch`, `stretches`, `flipped`, `zero`,
  `destroyed`, `promise`, `picture`, `square`, `flatten`
- **In / out:** fade up from the background; out: the flattened cube dissolves into the flat grid of Ch1.
- **Layers:** shader backdrop (`shaders/lattice.frag`, a slow dot lattice in `C.ghost`) · manim (matrix, strokes,
  grids via `shots.grid_lines`) · pyvista → `ArrayLayer` for the 4 s cube tease · `ZoomBlur` between the three shots

### s01_matrix · T.cut_ch1 → T.cut_ch2  (0:53–1:51, 58 s) — Ch1 A matrix moves space
- **Narration:** flat grid, two arrows, i hat and j hat → a matrix is instructions → first column says where
  i hat lands, second where j hat lands → three, one and one, two → lines stay straight, parallel, evenly spaced →
  "a movement of space" → "How much did space just stretch?"
- **Visual idea:** the grid draws on from the origin outward. i-hat grows, gets its name; j-hat the same. The matrix
  appears top-left with empty columns; the first column lights in `C.ihat` and a thin connector runs from it to the
  arrow. Numbers fill in on "three, one" and i-hat alone glides to (3, 1) with the grid still; then j-hat to (1, 2).
  Only then does the whole grid follow (`follows`), over a faint copy of the original grid. Three quick checks land on
  their words: a ruler laid along a line (`straight`), two lines pulsing together (`parallel`), tick marks (`leans`).
  The scene ends by playing the transformation once more, slowly, with a `?` where the readout will be.
- **Beats:** `what_does`, `grid`, `ihat`, `ihat_name`, `jhat`, `jhat_name`, `instructions`, `col1`, `col2`, `take`,
  `c31`, `i_moves`, `c12`, `j_moves`, `follows`, `straight`, `parallel`, `leans`, `all_it_is`, `movement`, `question`,
  `how_much`
- **In / out:** in from the intro's flat grid; out: the grid snaps back to rest, the unit square starts to glow.
- **Layers:** manim (grid as `m.redraw` of `grid_lines(A(t))`, arrows, HUD matrix) · slow camera push

### s02_area · T.cut_ch2 → T.cut_test  (1:51–2:41, 50 s) — Ch2 One number for the stretch
- **Narration:** the square on i hat and j hat, area exactly one → apply the matrix, a parallelogram, area five →
  "One became five" → every square grew five times → any shape: a circle, a leaf, the outline of a country, filled
  with tiny squares → "That factor… is the determinant. For this matrix, the determinant is five."
- **Visual idea (as built):** concrete before general. The grid relaxes from Ch1, the unit square's outline is traced,
  `1` appears inside it. The matrix is applied and the number counts 1 → 5 live (computed from the moving matrix).
  "Count it up": the original unit grid shows through the parallelogram. `1 → 5` appears under the matrix panel.
  Every other cell of the transformed grid fills in a checkerboard wave from the origin out, under the grid lines.
  The view zooms out and the grid rests; a circle, a leaf and a country outline are drawn, filled with tiny squares,
  and the matrix is applied to all of them: `×5` beside each. The HUD matrix then moves to the centre:
  `det [3 1; 1 2] = 5`.
- **Beats:** `measure`, `unit_sq`, `area1`, `apply`, `para`, `area5`, `one_five`, `not_just`, `every_sq`, `five_times`,
  `any_shape`, `circle`, `leaf`, `country`, `tiny`, `tiny5`, `whole5`, `factor`, `det_word`, `det5`
- **In / out:** in from Ch1's transformed grid; out: the centre equation, which s02b clears.
- **Layers:** manim only (tiny squares are Manim polygons, about 75 of them; light enough).
- **Country:** Nepal, hand-simplified (35 points, `shots.country_outline`); recognisable, not survey-accurate.

### s02b_predict · T.cut_test → T.cut_ch3  (2:41–3:13, 33 s) — Ch2 (cont.)
- **Narration:** stretch by two sideways and three upward, a one by one square becomes two by three, determinant six →
  "Now try to predict this one." A shear → "So what is the determinant?" → "It is one… its base and its height
  never change… not a drop of area is gained or lost."
- **Visual idea:** two small experiments, same layout so the eye knows where to look. First `[[2, 0], [0, 3]]`: the
  square widens (`scale2`), then grows tall (`scale3`), six unit cells counted inside it. Then the shear matrix
  appears with the readout showing `det = ?`. The grid slides, shapes visibly lean, and the frame holds through the
  1.1 s silence after "what is the determinant?". On "It is one" the `?` flips to `1`; a base bracket and a height
  bracket stay fixed while the square leans back and forth between them. A triangle is cut from one side and slid to
  the other to make the square again.
- **Beats:** `test`, `scale2`, `scale3`, `two_by_three`, `det6`, `predict`, `shear`, `slides`, `distorted`, `ask`, `det1`,
  `base_height`, `no_area`
- **In / out:** in from the `det(A) = 5` readout; out: the sheared square relaxes to the unit square.
- **Layers:** manim only

### s03_formula · T.cut_ch3 → T.cut_ch4  (3:13–4:16, 63 s) — Ch3 Where the formula comes from
- **Narration:** "Why A times D, minus B times C?" → letters: i hat lands at A, C; j hat at B, D → the parallelogram
  is the area we want → a rectangle around it, width A plus B, height C plus D → remove two triangles (A times C),
  two more (B times D), two corner rectangles (B times C each) → everything cancels → A times D minus B times C →
  try it: three times two, one times one, six minus one, five.
- **Visual idea:** the derivation is a picture that loses pieces. The grid fades back and the parallelogram moves to
  the left two thirds of the frame, with side lengths labelled a, c, b, d on the arrows' shadows. The bounding
  rectangle draws on; braces give `a + b` and `c + d`. Each removed piece lights in `C.cutaway`, is named, and
  slides out to the right where it stacks into the working: `(a + b)(c + d) − ac − bd − 2bc`. On "Expand" the
  product opens into four terms; on "cancels" the matching terms cross out in pairs; `ad − bc` is what is left and
  moves back onto the gold parallelogram. Then the letters become our numbers one product at a time, ending on the
  same gold `5` from Ch2.
- **Math check:** rectangle (a+b)(c+d) = ac + ad + bc + bd; minus ac, bd and 2bc leaves ad − bc. The pieces are exact
  for a, b, c, d > 0 with ad > bc, which holds for the example (3, 1, 1, 2).
- **Beats:** `where`, `why`, `letters`, `ac`, `bd`, `want`, `trick`, `rect`, `width`, `height`, `too_big`, `remove`,
  `tri_ac`, `ac_val`, `tri_bd`, `bd_val`, `corners`, `bc_val`, `expand`, `cancels`, `survives`, `never_arb`, `area_para`,
  `try_it`, `six`, `one`, `minus`, `five`, `same5`
- **In / out:** in from the unit square (it re-grows into the parallelogram); out: `ad − bc` to the progress rail.
- **Layers:** manim (polygons, braces, `TransformMatchingTex`) · glow on the surviving area

### s04_sign · T.cut_ch4 → T.cut_ch5  (4:16–5:24, 67 s) — Ch4 When the determinant is negative
- **Narration:** a subtraction can fall below zero, an area cannot → "what would a determinant of negative five
  mean?" → swap the columns: same shape, same area, the formula gives negative five → j hat was to the left of
  i hat, now it is to the right → a sheet of paper flipped onto its back, writing in mirror image → size is the
  scaling, sign is the flip → swing j hat toward i hat: thinner, zero for an instant, out the other side →
  "zero is the most important value".
- **Visual idea:** the re-hook. `ad − bc` with the minus sign pulsing in `C.flip`, a number line under it with the
  marker sliding past zero to −5. Then the matrix's two columns physically trade places and the grid re-forms: same
  parallelogram, now violet, the two arrows in each other's positions. A small curved arrow from i-hat to j-hat
  shows the turn: counter-clockwise before, clockwise after. The plane is given a letter `R` and a paper texture, and
  the whole sheet turns over in 2.5D to show the mirrored `R`. For the last paragraph: a live demo. j-hat swings
  around the origin toward i-hat; the area thins and its readout falls continuously on a vertical gauge (gold above
  zero, violet below). At `exact0` everything is one red line and the motion holds for half a second; then it
  continues and the area re-opens in violet.
- **Beats:** `below`, `neg_area`, `neg5`, `swap`, `i_j`, `j_i`, `same_shape`, `same_area`, `gives_neg`, `look`, `left`,
  `right`, `turned`, `paper`, `mirror`, `sign`, `size`, `sign_flip`, `watch_sign`, `swing`, `thinner`, `falls`, `line_up`,
  `exact0`, `other_side`, `doorway`, `important`
- **In / out:** in from the `5`; out: the swing reverses and stops exactly on the red line, which is Ch5's first frame.
- **Layers:** manim (`m.redraw` driven by the swing angle, gauge) · skia → `ArrayLayer` for the paper sheet with
  the `R` · 2.5D `s.camera` for the turn-over

### s05_zero · T.cut_ch5 → T.cut_ch6  (5:24–6:19, 56 s) — Ch5 When the determinant is zero
- **Narration:** both arrows on the same line, the whole plane squashed onto it → zero area → "something worse":
  points that started apart now sit on top of each other → "where did it come from? You cannot tell me… The
  information is gone." → no inverse, you cannot unsquash a line → systems of equations: nonzero means exactly one
  answer; zero means none, or infinitely many.
- **Visual idea:** pays off the intro's "destroyed". The plane is shown as about 20,000 soft points colored by where
  they started (a smooth two-color wash), so position is visible as color. Under `[[2, 4], [1, 2]]` they flow onto
  the red line and the colors smear together: the picture of lost information. Then five highlighted points on one
  diagonal (a line parallel to the null direction (−2, 1), computed) travel to the same landing spot. The question is
  staged backwards: one landed point, a `?`, and the whole dashed line of starting points lighting up behind it. On
  "no inverse" `A⁻¹` writes on and is struck through; the reverse animation is attempted and the line simply
  stays a line. Last paragraph: split screen, two small systems as pairs of lines. Left, det ≠ 0: the lines cross
  at one point. Right, det = 0: parallel lines (no answer), then one slides onto the other (infinitely many).
- **Beats:** `det0`, `same_line`, `goes_with`, `squashed`, `zero_area`, `worse`, `points`, `different`, `on_top`,
  `suppose`, `came_from`, `cannot`, `whole_line`, `info`, `no_inv`, `undo`, `unsquash`, `system`, `nonzero`, `one_answer`,
  `missing`, `infinite`
- **In / out:** in on the red line from Ch4; out: the line tilts up out of the page, becoming an edge in 3D.
- **Layers:** `PointsLayer` (numpy positions = A(t) · p, values = starting coordinate, glow) · manim (arrows, line,
  highlighted points, the two systems)

### s06_three_d · T.cut_ch6 → T.cut_ch7  (6:19–7:00, 41 s) — Ch6 Three dimensions
- **Narration:** everything survives the move into three dimensions, only one word changes → three arrows, a three by
  three matrix → a unit cube carried into a slanted box → the determinant is the volume of that box → the sign still
  means a flip, a right hand becomes a left hand → zero still means collapse, onto a plane, no way back.
- **Visual idea:** the 2D grid tips back and gains depth: the same teal and rose arrows, joined by a blue third. A
  slow orbit runs for the whole scene so the depth is always readable. The gold unit cube shears into the box; the
  word `area` in the readout is crossed out and replaced by `volume` (the "one word"). `det = 6` counts up as
  the box fills. For the sign: a right hand (thumb, index, middle finger along the three arrows) beside the box;
  one column is negated, the box passes through itself, turns violet, and the hand is now a left hand. For zero:
  the third column is rotated into the plane of the other two; the box flattens to a red sheet and the readout
  reaches 0.
- **Beats:** `three_d`, `one_word`, `three_arrows`, `three_by`, `cube`, `box`, `volume`, `every_vol`, `sign3`, `mirror3`,
  `hand`, `left_hand`, `collapse3`, `plane`, `vol0`, `no_back`
- **In / out:** in from the 2D plane tilting; out: the red sheet rotates face-on and becomes the flat grid again.
- **Layers:** pyvista off-screen → `ArrayLayer` (cube, box, axes, flat-shaded with soft edges; frames baked once and
  cached) · manim HUD on top (3 × 3 matrix, readout) · skia hand glyphs → `ArrayLayer`
- **Render note:** this is the heaviest scene for the machine (about 2,500 frames at 60 fps). The pyvista frames are
  baked at 30 fps and held, which is invisible on a slow orbit.

### s07_product · T.cut_ch7 → T.cut_outro  (7:00–7:27, 27 s) — Ch7 The payoff
- **Narration:** "the determinant of a product is the product of the determinants. Prove it with algebra, and you
  will fill a page." → as a picture: one matrix, areas grow by five; another, by two; both, by ten. "Of course
  they have. There is nothing left to prove."
- **Visual idea:** the reward for having the picture. `det(AB) = det(A) det(B)` writes on. Behind it a page of
  small grey algebra (the real expansion of the 2 × 2 product, generated with sympy) scrolls and fills the frame on
  "fill a page", then is swept away. One gold unit square: A is applied, `1 → 5`; then B = `[[2, 1], [0, 1]]`,
  `5 → 10`; the counter shows `5 × 2 = 10`. The equation comes back with the numbers under each term.
- **Beats:** `payoff`, `rule`, `product`, `is_product`, `page`, `as_picture`, `by5`, `another`, `by2`, `both`, `by10`,
  `of_course`, `nothing`
- **In / out:** in on the flat grid; out: the square relaxes to area one.
- **Layers:** manim (sympy-generated algebra as `Eqn` rows, grid, counter)

### s08_outro · T.cut_outro → T.end  (7:27–7:59, 32 s) — Outro
- **Narration:** "A matrix moves space. The determinant measures how much that movement scales area. Or in three
  dimensions, volume. Its sign tells you whether space was flipped. And when it is zero, space has collapsed, and
  the matrix cannot be undone. A times D, minus B times C. It was never a recipe. It is the area of a
  parallelogram. And now, you can see it."
- **Visual idea:** the progress-rail badges fly out of the corner and open into four live tiles, each a looping
  miniature of its chapter: the stretch (gold, `× 5`), the box (`volume`), the flip (violet, `−`), the collapse
  (red, `0`). Each lights on its sentence; nothing new is introduced. For the final lines the tiles clear and the
  frame is the opening shot again, the bare `ad − bc`. This time it does what the intro promised: `a` and `c`
  become the teal arrow, `b` and `d` the rose arrow, the parallelogram fills gold between them, and the formula
  settles underneath. Hold on that frame through the 3 s tail, then fade.
- **Beats:** `gather`, `r_moves`, `r_scales`, `r_volume`, `r_sign`, `r_zero`, `r_undone`, `final_adbc`, `never_recipe`,
  `final_area`, `see_it`
- **In / out:** in from the unit square; out: fade to the background over the last second.
- **Layers:** manim (tiles, final formula) · baked pyvista loop reused from Ch6 for the volume tile

## Promises made, and where each is kept

| promise (intro) | kept in |
|---|---|
| "how much a matrix stretches space" | Ch2 `det_word` (2:36) |
| "whether space has been flipped over" | Ch4 `sign_flip` (4:59) |
| "something has been destroyed, and can never be recovered" | Ch5 `info`, `no_inv` (5:52–5:59) |
| "see a picture instead of a formula" | Ch3 `survives` (3:56) and the last frame of the outro |
| "start with a single square" | Ch2 `unit_sq` (1:55) |
| "end by flattening three dimensional space" | Ch6 `plane` (6:54) |

## Build order

One chapter at a time, each one: scene code → `aion still` at its key beats → fixes → `aion preview` of that scene →
your review. Suggested order: s01, s02, s02b, s03 (pure Manim, sets the look), then s04, s05, s07, then s06 (3D),
and s00 and s08 last, since the intro previews and the outro recaps shots that must exist first.

## Beat table

| beat | time | end | words |
|---|---|---|---|
| matrix | 1.50 | 2.42 | Take a matrix |
| four | 4.71 | 5.53 | Four numbers |
| cross | 8.64 | 9.92 | multiply them in a cross |
| adbc | 11.25 | 12.36 | A times D |
| named | 15.28 | 16.12 | the determinant |
| learned | 17.86 | 18.58 | learned to compute |
| recipe | 23.00 | 23.78 | just a recipe |
| watch | 25.63 | 26.17 | But watch |
| stretches | 29.74 | 30.83 | stretches space |
| flipped | 32.58 | 33.20 | flipped over |
| zero | 34.02 | 34.75 | reaches zero |
| destroyed | 36.98 | 37.58 | destroyed |
| promise | 40.13 | 40.48 | By the end |
| picture | 44.44 | 45.20 | see a picture |
| square | 48.10 | 48.92 | a single square |
| flatten | 50.10 | 50.58 | flattening |
| cut_ch1 ✂ | 52.97 | 52.97 | space. ✂ First, |
| what_does | 55.40 | 56.51 | what a matrix does |
| grid | 58.02 | 58.78 | a flat grid |
| ihat | 60.10 | 61.35 | One points to the right |
| ihat_name | 62.37 | 63.23 | Call it i hat |
| jhat | 64.02 | 65.22 | other points straight up |
| jhat_name | 65.49 | 66.28 | Call it j hat |
| instructions | 68.28 | 69.24 | a set of instructions |
| col1 | 73.72 | 74.44 | The first column |
| col2 | 76.06 | 76.92 | The second column |
| take | 79.17 | 80.17 | Take this matrix |
| c31 | 80.78 | 82.18 | first column is three |
| i_moves | 83.26 | 83.82 | i hat moves |
| c12 | 86.14 | 87.38 | second column is one |
| j_moves | 88.22 | 89.16 | j hat goes there |
| follows | 90.40 | 91.40 | everything else follows |
| straight | 92.80 | 93.39 | stay straight |
| parallel | 94.44 | 94.80 | parallel |
| leans | 97.48 | 98.76 | leans and stretches |
| all_it_is | 101.13 | 102.97 | That is all a matrix is |
| movement | 103.27 | 104.59 | A movement of space |
| question | 106.61 | 107.38 | a natural question |
| how_much | 108.26 | 109.30 | How much did space |
| cut_ch2 ✂ | 111.03 | 111.03 | stretch? ✂ To |
| measure | 112.04 | 112.84 | To measure it |
| unit_sq | 114.74 | 115.68 | The square that sits |
| area1 | 120.00 | 120.74 | exactly one |
| apply | 122.18 | 123.29 | apply the matrix again |
| para | 125.14 | 126.14 | into a parallelogram |
| area5 | 127.38 | 128.61 | its area is five |
| one_five | 129.47 | 130.99 | One became five |
| not_just | 133.72 | 134.93 | not just that square |
| every_sq | 135.34 | 136.44 | Every square on the grid |
| five_times | 139.40 | 140.42 | five times larger |
| any_shape | 141.74 | 142.82 | any shape you like |
| circle | 142.86 | 143.63 | a circle |
| leaf | 143.69 | 144.26 | a leaf |
| country | 144.30 | 145.63 | the outline of a country |
| tiny | 146.54 | 147.41 | tiny squares |
| tiny5 | 148.94 | 149.79 | grows by five |
| whole5 | 150.30 | 151.18 | the whole shape grows |
| factor | 152.65 | 153.46 | That factor |
| det_word | 156.49 | 157.43 | is the determinant |
| det5 | 158.88 | 160.20 | the determinant is five |
| cut_test ✂ | 160.68 | 160.68 | five. ✂ Let |
| test | 161.17 | 161.70 | Let us test |
| scale2 | 164.54 | 165.33 | two sideways |
| scale3 | 165.86 | 166.46 | three upward |
| two_by_three | 168.50 | 169.18 | two by three |
| det6 | 169.52 | 170.90 | The determinant is six |
| predict | 172.12 | 172.76 | try to predict |
| shear | 174.44 | 175.05 | a shear |
| slides | 176.44 | 177.56 | slides to the right |
| distorted | 179.92 | 180.69 | looks distorted |
| ask | 181.64 | 182.53 | what is the determinant |
| det1 | 183.61 | 184.24 | It is one |
| base_height | 185.98 | 187.18 | its base and its height |
| no_area | 189.98 | 190.62 | not a drop |
| cut_ch3 ✂ | 193.35 | 193.35 | lost. ✂ So |
| where | 194.76 | 195.56 | where does the formula |
| why | 196.46 | 197.80 | Why A times D |
| letters | 199.90 | 201.31 | Write the matrix with letters |
| ac | 201.66 | 203.06 | i hat lands at A |
| bd | 203.89 | 205.34 | j hat lands at B |
| want | 207.82 | 208.73 | the area we want |
| trick | 210.08 | 210.93 | a lovely trick |
| rect | 211.28 | 212.16 | Draw a rectangle |
| width | 213.57 | 214.08 | Its width |
| height | 215.46 | 216.00 | Its height |
| too_big | 219.10 | 219.55 | too big |
| remove | 220.42 | 221.51 | remove what does not belong |
| tri_ac | 221.88 | 222.98 | Two triangles here |
| ac_val | 224.10 | 224.90 | A times C |
| tri_bd | 225.35 | 226.30 | Two more triangles |
| bd_val | 226.82 | 227.65 | B times D |
| corners | 228.26 | 229.30 | two small rectangles |
| bc_val | 230.98 | 231.79 | B times C |
| expand | 232.62 | 233.34 | Expand |
| cancels | 235.08 | 235.60 | cancels |
| survives | 236.00 | 236.76 | What survives |
| never_arb | 241.02 | 241.95 | never arbitrary |
| area_para | 242.46 | 244.14 | the area of a parallelogram |
| try_it | 246.57 | 247.79 | Try it on our matrix |
| six | 248.16 | 249.04 | Three times two |
| one | 250.04 | 250.88 | One times one |
| minus | 251.77 | 252.84 | Six minus one |
| five | 253.25 | 253.67 | Five |
| same5 | 254.05 | 254.80 | The same five |
| cut_ch4 ✂ | 256.32 | 256.32 | counted. ✂ But |
| below | 258.30 | 259.41 | fall below zero |
| neg_area | 260.38 | 261.26 | cannot be negative |
| neg5 | 263.26 | 263.98 | negative five |
| swap | 266.24 | 267.47 | swap its two columns |
| i_j | 268.32 | 269.12 | i hat lands where |
| j_i | 270.56 | 271.44 | j hat lands where |
| same_shape | 273.60 | 274.64 | the same shape |
| same_area | 274.72 | 275.55 | The same area |
| gives_neg | 276.72 | 277.86 | gives negative five |
| look | 278.70 | 279.56 | Look at the arrows |
| left | 281.94 | 282.50 | to the left |
| right | 285.10 | 285.56 | to the right |
| turned | 286.90 | 287.73 | turned over |
| paper | 287.86 | 288.58 | a sheet of paper |
| mirror | 291.98 | 292.60 | mirror image |
| sign | 293.96 | 294.44 | what the sign |
| size | 295.32 | 296.60 | The size of the determinant |
| sign_flip | 298.96 | 299.48 | sign tells you |
| watch_sign | 301.94 | 303.05 | watch the sign change |
| swing | 303.36 | 304.30 | Swing j hat |
| thinner | 306.86 | 307.61 | gets thinner |
| falls | 307.70 | 308.85 | the determinant falls |
| line_up | 310.30 | 310.83 | line up |
| exact0 | 312.30 | 313.19 | exactly zero |
| other_side | 314.94 | 315.65 | the other side |
| doorway | 317.96 | 318.48 | the doorway |
| important | 320.32 | 321.52 | the most important value |
| cut_ch5 ✂ | 323.60 | 323.60 | take. ✂ When |
| det0 | 324.49 | 325.95 | When the determinant is zero |
| same_line | 327.18 | 328.22 | the same line |
| goes_with | 328.46 | 329.26 | everything else goes |
| squashed | 331.26 | 332.50 | squashed onto that line |
| zero_area | 334.56 | 335.28 | zero area |
| worse | 335.96 | 336.48 | something worse |
| points | 337.68 | 338.30 | these points |
| different | 339.60 | 339.76 | different |
| on_top | 341.44 | 342.35 | on top of each other |
| suppose | 343.38 | 344.26 | suppose I show you |
| came_from | 346.18 | 347.01 | where it came from |
| cannot | 347.57 | 348.64 | You cannot tell me |
| whole_line | 348.99 | 350.90 | A whole line of starting points |
| info | 352.44 | 354.04 | The information is gone |
| no_inv | 358.20 | 359.04 | no inverse |
| undo | 359.88 | 360.76 | no way to undo |
| unsquash | 362.04 | 362.60 | unsquash |
| system | 368.02 | 369.19 | a system of equations |
| nonzero | 370.06 | 371.10 | nonzero determinant |
| one_answer | 371.42 | 372.83 | exactly one answer |
| missing | 375.78 | 376.36 | either missing |
| infinite | 377.50 | 378.29 | infinitely many |
| cut_ch6 ✂ | 379.30 | 379.30 | many. ✂ Everything |
| three_d | 382.28 | 383.35 | into three dimensions |
| one_word | 383.71 | 384.76 | Only one word |
| three_arrows | 386.84 | 387.75 | three arrows |
| three_by | 388.16 | 389.16 | three by three matrix |
| cube | 393.32 | 394.23 | a unit cube |
| box | 395.80 | 397.29 | a slanted box |
| volume | 398.20 | 399.44 | the volume of that box |
| every_vol | 400.76 | 401.40 | every volume |
| sign3 | 403.03 | 404.22 | The sign still means |
| mirror3 | 406.50 | 407.86 | its own mirror image |
| hand | 408.06 | 408.70 | a right hand |
| left_hand | 409.02 | 409.62 | a left hand |
| collapse3 | 411.12 | 412.67 | zero still means collapse |
| plane | 414.92 | 415.83 | onto a plane |
| vol0 | 416.14 | 417.16 | Volume zero |
| no_back | 418.67 | 419.51 | no way back |
| cut_ch7 ✂ | 420.47 | 420.47 | back. ✂ Now |
| payoff | 421.43 | 422.55 | Now for the payoff |
| rule | 423.42 | 423.66 | a rule |
| product | 424.82 | 426.51 | The determinant of a product |
| is_product | 426.70 | 428.20 | the product of the determinants |
| page | 430.30 | 430.99 | fill a page |
| as_picture | 432.16 | 434.10 | look at it as a picture |
| by5 | 435.80 | 436.57 | grow by five |
| another | 436.97 | 437.95 | Apply another |
| by2 | 438.24 | 439.44 | grow by two |
| both | 439.44 | 440.12 | Do both |
| by10 | 442.00 | 442.93 | grown by ten |
| of_course | 443.45 | 444.29 | Of course they have |
| nothing | 445.04 | 446.01 | nothing left to prove |
| cut_outro ✂ | 447.00 | 447.00 | prove. ✂ So |
| gather | 448.54 | 449.57 | gather what we found |
| r_moves | 450.66 | 452.30 | A matrix moves space |
| r_scales | 455.20 | 455.95 | scales area |
| r_volume | 458.37 | 458.80 | volume |
| r_sign | 459.38 | 460.26 | Its sign tells you |
| r_zero | 462.60 | 463.35 | when it is zero |
| r_undone | 465.80 | 466.87 | cannot be undone |
| final_adbc | 467.80 | 468.97 | A times D |
| never_recipe | 470.98 | 471.76 | never a recipe |
| final_area | 472.46 | 474.10 | the area of a parallelogram |
| see_it | 476.70 | 476.70 | you can see it |
198 beats, 10 scenes, audio 479.22s
