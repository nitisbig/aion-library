# What Matrices Actually Are: storyboard

Audio: `assets/audio.wav` (962.88 s = **16:03**, 2,696 words, about 168 words a minute, voice speed 0.92,
-16.2 LUFS). Generated 2026-11-16 with `aion voice` (7 chunks, 14,717 characters). Scene ranges below are the real
cuts from `beats.py` (`uv run aion beats 009 --md`); the full beat table is at the end of this file.

Pacing (`voice.toml [pacing]`): 1.5 s lead-in, +0.5 s after each paragraph, +1.5 s between chapters, 3.0 s tail,
a held 3 s pause after the intro map, and three 2.5 s pause-and-predict pauses (quarter turn, order, plane rotation).
Captions for YouTube: `assets/subtitles.srt` (474 cues, one sentence or balanced half-sentence per cue,
≤ 42 characters; short cues retimed or merged, original kept as `assets/.subtitles.before-retime.srt`).

Structure: intro, seven chapters, outro. Twenty scene files.

| # | scene | chapter | range | length | mode |
|---|---|---|---|---|---|
| 0 | `s00_hook` | Intro: nine numbers come alive, the wrong intuition | 0:00–0:53 | 53 s | cinematic 3D |
| 1 | `s01_preview` | Intro: the claim, preview montage, one-sentence map | 0:53–1:35 | 42 s | hero montage |
| 2 | `s02_box` | Ch1 Nine numbers in a box: size, address, equations | 1:35–2:05 | 30 s | notation |
| 3 | `s03_photo` | Ch1 (cont.) a picture is a matrix, the open question | 2:05–2:42 | 37 s | data, zoom |
| 4 | `s04_machine` | Ch2 A machine that moves space: arrow in, arrow out | 2:42–3:29 | 46 s | visual |
| 5 | `s05_gallery` | Ch2 (cont.) rotate, stretch, shear, flip, flatten; 3D die | 3:29–4:10 | 41 s | gallery |
| 6 | `s06_columns` | Ch3 The columns are the whole story | 4:10–5:14 | 64 s | derivation |
| 7 | `s07_read` | Ch3 (cont.) read a matrix, predict #1, decode the box, games | 5:14–6:06 | 52 s | predict, 2D → 3D |
| 8 | `s08_compose` | Ch4 One move after another → the row-times-column rule | 6:06–6:58 | 52 s | derivation, payoff |
| 9 | `s09_order` | Ch4 (cont.) predict #2: does order matter? the die | 6:58–7:32 | 34 s | predict, **midpoint re-hook** |
| 10 | `s10_layers` | Ch4 (cont.) neural networks: matrices + bends | 7:32–8:14 | 43 s | application |
| 11 | `s11_undo` | Ch5 The moves you can't undo: inverse, determinant | 8:14–8:52 | 38 s | visual |
| 12 | `s12_collapse` | Ch5 (cont.) det 0, null space, column space, shadow | 8:52–9:49 | 56 s | surprise, lit 3D |
| 13 | `s13_solve` | Ch5 (cont.) solving equations: lines, three planes | 9:49–10:39 | 50 s | 2D → 3D, payoff |
| 14 | `s14_eigen` | Ch6 The directions that don't turn, predict #3, rotation axis | 10:39–11:50 | 71 s | predict, 3D |
| 15 | `s15_power` | Ch6 (cont.) apply it again and again | 11:50–12:15 | 26 s | visual |
| 16 | `s16_pagerank` | Ch6 (cont.) PageRank: the settled crowd | 12:15–13:01 | 45 s | application, sim |
| 17 | `s17_ellipse` | Ch7 A rotation, a stretch, and a rotation (SVD) | 13:01–14:12 | 71 s | reveal, lit 3D |
| 18 | `s18_photo_svd` | Ch7 (cont.) the picture comes apart, the big payoff | 14:12–15:08 | 57 s | **payoff** |
| 19 | `s19_outro` | Outro: the box one last time; the numbers change, the move doesn't | 15:08–16:03 | 55 s | callback |

## The story spine
"A matrix looks like a table of numbers, but it is a **move you make to space**, and its columns record where the axes
land." Every chapter is one consequence of that sentence: reading columns (Ch3), multiplying = composing (Ch4),
undoing and collapsing (Ch5), directions it leaves alone (Ch6), and the shape of every move, rotate-stretch-rotate (Ch7).
The two faces from Ch1 (matrix as *table* vs matrix as *move*) are reunited in s18: the picture, read as a move, comes
apart into stretches, and the biggest ones rebuild it. The outro adds the closing thought: the numbers depend on the
arrows we measure with. The move does not.

## Running numbers (computed with numpy/sympy; scratch `check.py`, `die_svd.py`; never typed by hand at build time)

| use | value | where |
|---|---|---|
| hook box H | `[[2,1,0],[0,1,1],[1,0,1]]`, det 3, columns (2,0,1) (1,1,0) (0,1,1) | s00, s07, s19 |
| shape example | a 2 × 3 matrix | s02 |
| three equations | x + y + z = 4, x − y + 2z = 1, 2x + y − z = 3 → det 7, solution (1, 2, 1) | s02 → s13 |
| singular variant | third row = first + second (2x + 3z): right side 5 → a line of solutions; 6 → none | s13 |
| the arrow | (2, 1) = 2 î + 1 ĵ | s04, s06 |
| gallery | rotate 45°, stretch diag(2, 0.5), shear [[1,1],[0,1]], flip diag(−1, 1), flatten [[1,0],[0,0]] | s05 |
| quarter turn | `[[0,−1],[1,0]]`: î → up, ĵ → left, counterclockwise | s07 |
| composition | shear Sh = [[1,1],[0,1]], then R = quarter turn: R·Sh = [[0,−1],[1,1]]; Sh·R = [[1,−1],[1,0]] | s08, s09 |
| die | opposite faces sum to 7; +x 3, +y 2, +z 1 (up). Quarter turns: x-then-y → **4** on top; y-then-x → **2** on top | s09 |
| y-then-x product | `[[0,0,1],[1,0,0],[0,1,0]]`: one 120° turn about (1,1,1), eigenvalue 1 | s09 → s14 |
| neural net | two interleaved spirals (300 + 300, seed 3): one matrix ≤ 67 %; 2-16-16-1 tanh: 100 % | s10 |
| **hero A** | `[[3,1],[2,2]]`, det 4, λ = 4 on (1, 1), λ = 1 on (1, −2); A⁻¹ = ¼[[2,−1],[−2,3]] | s11–s17 |
| 2D solve | A x = (5, 6) → x = (1, 2); rows 3x + y = 5, 2x + 2y = 6 cross at (1, 2) | s13 |
| collapse | `[[2,1],[2,1]]`, det 0, null space along (1, −2) (pink), column space along (1, 1) | s12 |
| power iteration | from (1, −0.3): angle −17° → 27° → 41° → 44° → 44.7° → 44.9°: on (1, 1) after ~4 rounds | s15 |
| PageRank | links A→C; B→C,G; C→A,B; D→C; E→C,D; F→A,E; G→F,C; damping 0.85: **C .368**, A .204, B .178, G .097, F .063, E .048, D .042. B and D each have one incoming link; B's comes from C → ≈ 4.2 × D | s16 |
| hero SVD | A = U Σ Vᵀ: rotate −30.1°, stretch σ₁ = 4.131, σ₂ = 0.968, rotate +41.4° (σ₁σ₂ = 4 = det) | s17 |
| photo SVD | 480 × 480 grey frame of the lit die (`shots.photo()`, cached in assets/photo.png; rank 382): rel. error k = 1 33 %, 10 9.2 %, 30 4.2 %; 30 layers = 30·961/480² = 12.5 % of the numbers | s03 → s18 |

## Visual system

Design: **Classic + lit 3D** (decided 2026-11-16). Pure black, crisp unglowed lines, Computer Modern for all text, no
bloom, glow, blur, vignette, grain or caption text. The one addition to Classic: 3D *objects* (the die, planes, ellipsoid)
are **shaded by one fixed key light** with a weak fill, so they read as solid. "After Effects grade" comes from motion,
continuity and lighting, never from glow. Design sheet: `out/design/design_{1,2}.png` (`python design_sheet.py`).

| object | color token | meaning |
|---|---|---|
| î, first column, its entries | `C.ihat` (green) | where the first axis lands |
| ĵ, second column | `C.jhat` (red) | where the second axis lands |
| k̂, third column (3D) | `C.khat` (blue) | where the third axis lands |
| a vector x and where it lands | `C.vec` (yellow) | the thing being moved |
| the target b in Ax = b | `C.target` (orange) | where we want to land |
| unit square / cube, det value | `C.area` (gold) | how much space grows |
| collapse, null space, shadow ray | `C.null` (pink) | what is lost |
| eigenvectors, λ, PageRank steady state | `C.eigen` (violet) | the directions that don't turn |
| singular axes, σ, the ellipse | `C.sigma` (teal) | the stretches |
| spiral classes | `C.cls_a` / `C.cls_b` (sky / coral) | the two things a network tells apart |
| numbers as data (pixel values, table cells) | `C.data` (light grey) | a matrix being read, not acting |
| the die body / pips | `C.die` / `C.pip` | the hero object |
| grid / ghost / panel borders | `C.grid` `C.grid_minor` `C.axis` `C.ghost` `C.frame` | the stage |

Rules for every scene:
- One focal point per frame, at most three things moving. Symbols, equations and numbers only, no caption text.
- **Matrix entries are colored by column** (green / red / blue): a column on screen has the same color as its arrow.
  Numeric matrices use 006's hand-set square brackets (`shots.Mat`, columns addressable for animation); symbolic
  formulas may use LaTeX `bmatrix`.
- **Palette notes:** `target`, `area` and `cls_b` are three warm oranges. They are never on screen together (b only in
  s13, the unit square in s00/s11/s12, the spiral class only in s10). `vec` (yellow) and `area` (amber) do share s11 and
  stay distinct there.
- **Moves always start from the identity** and are interpolated as moves: rotations by angle, shears and stretches
  linearly, compositions as products of partial moves (lab 3d-matrices finding). The original grid stays behind as
  `C.ghost`.
- **Progress rail** (top-right, from s04): a badge drops (`spring`) at each chapter end: `[ ]` → grid → columns →
  `AB` → `A⁻¹` → `λ` → `UΣVᵀ`. The outro gathers them around the box.
- Transform, don't cut: box columns → arrows (s00, s07, s19); the die frame → the picture (s03) → layers (s18);
  2D grid → 3D lattice (s05, s07); the s08 product → the s09 split screen; s09's y-then-x die turn → s14's axis;
  flatten (s12) → shadow (s12); s14's circle of arrows → s17's circle → ellipse; the three equations (s02) → planes (s13).
- Motion: `easy_ease` for camera, `smooth` for matrix moves (1.6–2.2 s), `out_back` for label pops, `spring` for badge
  drops, ~0.06 s stagger per item.

### Engines
| engine | used for |
|---|---|
| Manim (ManimLayer) | grids (006 `grid_lines`, clipped), arrows, square-bracket matrices, `Eqn`s, panels, the progress rail, the web graph, 3D lattices and flat-shaded polygons through the hand-made perspective camera (`Cam`, lab 2026-11-15-3d-matrices / det-zero-short) |
| pyvista (off-screen) → ArrayLayer | the lit die (rounded body, inset pips), the ellipsoid, the source frame for the s03/s18 picture. Animated shots need per-frame arrays: either an `ArrayLayer` that accepts f(t) or a baked frame cache (one library addition, decided when Ch2 is built). Fallback: flat-shaded Manim polygons |
| numpy (exact) | every matrix product, eigen/SVD, power iteration cloud, spiral data + a seeded 2-16-16-1 tanh net (trained once, cached), image SVD layers |
| Taichi | `Surfers(Sim)`: 3,000 random surfers hopping along links with damping 0.85, baked and seeded → `PointsLayer(glow=0)` |
| skia-python → ArrayLayer | the pixel-grid photo zoom (nearest-neighbour squares with crisp borders) |
| ModernGL | GPU compositing, the 2.5D camera, an optional `shaders/grid.frag` (analytic anti-aliased transformed grid) for full-frame hero grid moves in s01 |

## Retention plan

| device | where |
|---|---|
| Visual question inside 10 s | s00: the box on black at `box` (0:02) with the camera already creeping in; its columns lift at `columns` (0:14) and space moves at `tilts` (0:16) |
| Wrong intuition first | s00 end: the row-times-column rule as grey bookkeeping; "it just hides what a matrix actually is" |
| Preview the result, unexplained | s01: two moves stacking, flatten to a line, arrows that don't turn, circle → ellipse with the picture reassembling |
| Map in one sentence | s01 "two arrows on a flat grid … taking a photograph apart, one stretch at a time", then a 3 s hold |
| Open loops | s03 "how did nine numbers … turn it?" → s06–s07; s10 "that isn't always possible" → s11–s12 |
| Plant → payoff | rule (s00) → s08 · equations (s02) → s13 · picture (s03) → s18 · box (s00) → s07, s19 · die turn y-then-x (s09) → axis (s14) · surfers (s00 montage) → s16 · ellipse (s01) → s17 |
| Pause and predict | quarter turn (s07), order (s09), plane rotation (s14), each 2.5 s of silence |
| Midpoint re-hook | s09–s10 (6:58–8:14): `dont` "You don't." (7:15), `top_face` a different face on top (7:26), then the spirals fold apart right at the 8:01 midpoint (`fold` 8:02 → `told_apart` 8:06) |
| Mode switches | 3D cinematic → montage → notation → data zoom → grid machine → gallery → derivation → predict → split screen → network → inverse → shadow → planes → sweep → cloud → web sim → ellipse → picture layers → callback |
| Close each chapter visually | badge drops at `forget`→ (s01 end), `do` (s03), `numbers come in` (s05), `fresh for every frame` (s07), `always possible` (s10), `all along` (s13), `far more` (s16), `matter most` (s18) |
| End on the payoff | s19 "The numbers change. The move doesn't.": the die holds still while the measuring arrows (and the nine numbers) change |

## Scenes

Each entry: **title · range**, then purpose, visual, engine, animation, on-screen, narration.

### s00_hook · T.start → T.cut_preview (0:00–0:53, 53 s)
- **Purpose / concept:** the strongest hook. A matrix is an innocent box of numbers that, given space, *moves* it.
  Sets the visual identity: black, Computer Modern, green/red/blue columns, a lit die in a crisp lattice.
- **Visual:** black. The hook box H (3 × 3, square brackets, entries colored by column) fades in dead center, large,
  and holds alone. Then the camera dollies in; each column lifts off the box as a 3D arrow (green, red, blue) into a
  perspective 3D lattice (dim floor grid at `C.grid_minor`, lattice lines fading with depth). A lit ivory die sits at
  the origin. H acts: the lattice and die shear and stretch together (det 1 → 3 readout in `C.area`), then a turn about
  x, then a squash flat onto the floor (preview of collapse), then everything springs back. Match-cut montage, one
  shot per sentence: a frame of the die dissolves into a grid of grey squares with numbers; a 3D wireframe die spins
  in a game-camera frustum; a small web graph with surfers flowing; a 2D spiral dataset folding. Then the wrong
  intuition: a plain grey 2 × 2 times 2 × 2 product with a row sliding over a column, entry by entry, mechanical
  and flat. On `hides` the grey product dims to `C.ghost`.
- **Engine:** Manim (box, arrows, lattice via `Cam` perspective, Eqn), pyvista lit die → ArrayLayer frames, Taichi
  surfers (from s16's bake), numpy spirals (from s10), skia pixel plate (from s03). 2.5D camera.
- **Animation:** box `FadeIn` + 0.06 s stagger per entry; camera `easy_ease` dolly 1.0 → 1.6; columns lift with
  `smooth` 1.2 s, staggered; moves 2.0 s each, built as products of partial moves; montage shots are 3–4 s match cuts
  (shape-matched: box ↔ pixel grid ↔ node grid); the grey product crawls at a steady linear rate.
- **On-screen:** H; det readout `3`; montage visuals only; the grey product `[[1,2],[3,4]][[5,6],[7,8]]` with one
  highlighted row/column pair. No words.
- **Narration:** "Nine numbers, arranged in a box. … It might be the most useful object in all of mathematics. It
  also looks like the most boring. … Each column becomes an arrow. … Every photo on your phone is, underneath, a grid
  of numbers … Every frame of a video game … helped Google rank the entire web … a very long stack of them. … And
  yet, most of us first meet matrices as bookkeeping … The rule works. It just hides what a matrix actually is."
- **In / out:** from black. Out: the grey product fades; one flat 2D grid remains for s01.
- **As built:** the box H (size 110) staggers in, then parks top-left. The lattice (n = 1) and the lit die fade in on "alive"; each column lifts off into its arrow (î ĵ k̂). The move plays I → H on "tilts", then folds flat (diag(1, 1, 0.04)·H), and springs home (`out_back`) on "ride"; `det = 3` sits under the box. Montage: the photo turns into 10 × 10 averaged squares with their 0–255 values; a wireframe cube spins in front of a camera (eye, screen, four frustum edges); 500 readers hop around a 7-page web; the spirals fold through all four tanh layers (first two coordinates of each) until they separate. The grey product [[1,2],[3,4]][[5,6],[7,8]] = [[19,22],[43,50]] fills entry by entry with row/column boxes on "rule", ghosts on "hides", and the flat grid of s01 (O (0, −0.3), U 0.8) fades in under it.

### s01_preview · T.cut_preview → T.cut_ch1 (0:53–1:35, 42 s)
- **Purpose / concept:** the central claim ("not a table you read, a move you make") and an unexplained preview of
  every chapter's payoff, plus the one-sentence map.
- **Visual:** on `move you make` the flat grid picks itself up: a full-frame hero move of hero A (bright `C.grid`
  over ghost). Four shots on their words: `one move, and then another`: two moves stack, the composite drawn as one;
  `crush space flat`: the grid flattens onto a pink line; `special directions`: two violet lines stay put while the
  grid turns around them; `three simple motions`: a teal circle → ellipse in three stages (turn, stretch, turn).
  On `photograph apart` the die picture appears beside it and reassembles from blur in fast layers. Hold 3 s on the
  composed final frame (ellipse + picture), then dim.
- **Engine:** Manim grids/arrows; optional `shaders/grid.frag` for the full-frame hero grid; numpy SVD layers.
- **Animation:** each preview shot ~4 s, `smooth`, linked by match cuts on the grid; the photo layers tick in at
  0.15 s per layer.
- **On-screen:** grids, arrows, the ellipse, the picture. No equations yet.
- **Narration:** "So here is the claim this video is going to earn. A matrix is not a table you read. It is a move
  you make … Multiplying two matrices means doing one move, and then another. Some moves crush space flat … Some
  leave a few special directions untouched … built from three simple motions. We'll start with two arrows on a flat
  grid, and end by taking a photograph apart, one stretch at a time." (3 s hold.)
- **In / out:** continuous grid from s00. Out: everything fades except an empty rectangle outline, which becomes s02's
  matrix brackets.
- **As built:** a grey A (top-left) takes its column colours on "move you make". The grid (O (0, −0.3), U 0.8) previews, each from home: A and back; shear then a true 90° turn on top; collapse with the pink null line, springing back; A with the two violet eigen lines (their arrows stay on them); rotate–stretch–rotate (proper SVD: R(−30.1°), diag(4.13, 0.97), R(41.4°)) pulling a teal circle into the ellipse, ending on A. î and ĵ thicken on "two arrows". The stage fades; the framed photo rebuilds k = 1…40 (0.07 s per layer), holds, fades.

### s02_box · T.cut_ch1 → T.cut_photo (1:35–2:05, 30 s) · Ch1 Nine numbers in a box
- **Purpose / concept:** the plain definition: rows × columns, entry addresses; a matrix can store *anything*,
  e.g., the coefficients of a linear system (plant for s13).
- **Visual:** the rectangle from s01 becomes square brackets around a 2 × 3 matrix of plain numbers (`C.data`). A thin
  row band sweeps (`2` appears at left), a column band sweeps (`3` at the bottom) → `2 × 3`. One entry pulses; its row
  and column bands cross on it and the subscript address `a₂₃` pops beside it. Then the three equations write on
  (unknowns x, y, z in `C.vec`, coefficients in `C.data`); the letters and the `=` lift away and fade, and the
  coefficients slide together into a 3 × 3 matrix, with the right-hand sides sliding into a separate column (`C.target`).
  The system shrinks into a small panel parked at the lower left ("remember these").
- **Engine:** Manim (Tex, brackets, `TransformMatchingTex`-style slides done with explicit `m.play` moves).
- **Animation:** bands `smooth` 0.6 s; address pop `out_back`; the letters lift 0.3 units and fade; coefficients slide
  with 0.05 s stagger.
- **On-screen:** the 2 × 3 matrix, `2 × 3`, `a₂₃`, the three equations → the coefficient matrix and the column (4, 1, 3).
- **Narration:** "First, the plain facts. A matrix is a rectangle of numbers … two by three … which row it sits in,
  and which column. … Take three equations … Strip away the letters … what's left is a matrix. Remember these three
  equations. We'll come back and solve them."
- **In / out:** from the s01 rectangle. Out: the system panel parks at the corner; the screen clears for the picture.
- **As built:** the empty rail fades in. [[4, −1, 7], [0, 2, 5]] in `C.data`: row bands with `2` at the left, column bands with `3` below, `2 × 3` above. The entry 5 pulses, its row and column bands light, `a₂₃ = 5` pops. The three equations (letters `C.vec`, right-hand sides `C.target`) are set in columns; the letters lift away, + and = fade, the coefficients slide into the 3 × 3 (each minus becomes −1, the implicit 1s fade in), the right-hand sides into a column. The pair parks lower-left on a backing (`parked_system()` in shots.py, reused by s03).

### s03_photo · T.cut_photo → T.cut_ch2 (2:05–2:42, 37 s)
- **Purpose / concept:** a matrix as *data*: a grayscale picture is a matrix of brightness values (plant for s18).
  Then the open loop: tables can't rotate things, so how did the box move space?
- **Visual:** the 480 × 480 die frame (rendered by us, from s00) appears in a thin `C.frame` panel. The camera pushes
  in (`easy_ease`, ×20) until individual pixels are crisp squares; at the deepest zoom each square shows its value
  (0–255, `C.data`, numbers scale with the squares). Pull back out: the full picture, with a faint `480 × 480`
  under the panel. On `can't rotate anything` a small table of grades (plain numbers) sits beside it, inert; on
  `pick up a whole space and turn it` a tiny replay of the s00 move flickers in a corner panel. On `watching what they
  do` the numbers in the table grey out, and badge 1 `[ ]` drops into the rail.
- **Engine:** skia → ArrayLayer (nearest-neighbour pixel plate with crisp 1 px borders at deep zoom), Manim numbers
  (only for the ~12 × 7 visible squares, values read from the array), 2.5D camera.
- **Animation:** zoom 4 s `easy_ease`; numbers fade in only once squares exceed ~0.5 units; pull-back 2.5 s.
- **On-screen:** the picture, pixel values, `480 × 480`, the inert table, the replay thumbnail. No words.
- **Narration:** "Or take a picture. This one is a single frame from a moment ago … each square is just a number for
  how bright it is … hundreds of rows and hundreds of columns. Keep this one in mind, too. So a matrix can be a table.
  But that leaves a strange question … So how did nine numbers … pick up a whole space and turn it? To answer that, we
  have to stop reading the numbers, and start watching what they do."
- **In / out:** cut on chapter. Out: the picture shrinks to a thumbnail, parked under the system panel.
- **As built:** the parked system stays. The framed die frame (480², 5.6 tall) zooms (`easy_ease`, nearest neighbour) about a point chosen so the deepest crop is exactly 12 × 12 px: rows 98–109, cols 220–231, the top pip's edge (values 12…185). Pixel borders, then every value (dark digits on bright pixels). Pull back, `480 × 480`; the picture steps aside (×0.55) to the left. A 3 × 3 of grades and a column of prices sit inert at right. On "nine numbers" a lower-right panel replays the opening (small H, its lattice, the die turning I → H on "pick up a whole space"). On "watching" the tables grey to ghost, H pulses, and badge 1 drops.

### s04_machine · T.cut_ch2 → T.cut_gallery (2:42–3:29, 46 s) · Ch2 A machine that moves space
- **Purpose / concept:** vectors as arrows; a function from arrows to arrows; watch all of them at once = watch the
  grid; the three rules of a linear move.
- **Visual:** the Classic grid draws on from the center (blue integer lines over the dim half-step grid, white axes).
  A yellow arrow grows to (2, 1); dashed guides show "two over, one up". A small "machine" (a square-bracket outline
  with nothing inside) sits at right: the arrow flies into it and a different arrow comes out (a turned, longer
  yellow arrow). Three more arrows go through quickly. On `every arrow at once` the arrow multiplies into a field of
  dots at every grid point, then the dots move together under a shear-like move with the grid lines following.
  The three rules then light up one by one on the moving grid: one grid line highlights and stays straight; a row of
  evenly spaced lines shows equal tick gaps before and after; the origin dot pulses and doesn't move. On `linear` the
  ghost grid remains under the moved one.
- **Engine:** Manim (006 `grid_lines` clipped to the frame, dots, arrows, dashed guides).
- **Animation:** grid draw-on staggered from the center outward (`out_back` at the end); machine pass-through 0.8 s
  per arrow; the dot field moves `smooth` 2 s; rule highlights pulse `out_back`.
- **On-screen:** grid, the arrow, its tip coordinates `(2, 1)`, the empty-bracket machine. No caption text.
- **Narration:** "Picture a flat grid, and an arrow starting from its center … Two steps over, one step up. Now imagine
  a machine … Arrow in, arrow out. … feed the machine every arrow at once … Straight lines stay straight. Evenly spaced
  lines stay evenly spaced. And the center stays where it is. Moves like these are called linear."
- **In / out:** fresh chapter. Out: the grid relaxes back to identity.
- **As built:** O (−0.5, −0.6), U 0.95. The grid draws on from the centre outward; the (2, 1) arrow, dashed "two over, one up" guides, `(2, 1)`. The machine is an empty bracket box at (4.9, 1.9): a copy of each arrow goes in and GENTLE·v comes out ((2, 1) → (1, 4), then (−1, 2), (1, −1), (3, 0) faster); the inputs dim. Every arrow at once = yellow dots on every grid point, moving with the grid I → GENTLE (ghost grid left behind). On "tangle" a smooth sine warp bends lines and dots, then relaxes. The rules: the grid goes home and replays the move with the line x = 1 drawn white (stays straight), big yellow dots on it (equal gaps), and a pulse at the fixed origin. Back to rest on "linear".

### s05_gallery · T.cut_gallery → T.cut_ch3 (3:29–4:10, 41 s)
- **Purpose / concept:** the freedom inside linearity, and two non-examples. Then the same moves in 3D.
- **Visual:** the grid performs the gallery full-frame, each on its word: rotate 45°, stretch diag(2, 0.5), shear (a
  deck-of-cards sketch beside it slides the same way), flip diag(−1, 1) (a small asymmetric "F" shape rides on the grid
  so the flip reads), flatten onto the x-axis. Non-examples on `curves`: the grid bends into curves and a red ✕ (thin,
  `C.null`) stamps it; on `away from its center` the grid slides off the origin and is stamped too. Then 2D → 3D: the
  grid tips back into the floor of the 3D lattice; the lit die rides through turn, stretch, shear and flatten.
  On `where do the numbers come in?` the die holds, and badge 2 (a tiny grid) drops into the rail.
- **Engine:** Manim (grids, F shape), `Cam` perspective lattice, pyvista lit die frames.
- **Animation:** each move 1.6 s `smooth` from identity, 0.4 s hold, return; 3D moves 2 s; the tip-into-floor transition is a
  1.5 s camera `easy_ease` from top-down to oblique (lab 3d-matrices).
- **On-screen:** grids, the F, ✕ marks, the die. No labels or names of moves.
- **Narration:** "Inside those rules, there's a surprising amount of freedom. You can rotate … stretch … shear …
  like a deck of cards … flip it, as if in a mirror … squash it flat … What you can't do is bend the grid lines into
  curves, or drag the whole plane away from its center. And all of this carries over to three dimensions … So that's
  the machine. But where do the numbers come in?"
- **In / out:** continuous grid. Out: camera returns to top-down; the 3D lattice collapses back into the flat grid.
- **As built:** same grid. Rotate 45°, stretch diag(2, ½), shear (a deck of seven cards in a lower-right panel slides the same way), flip diag(−1, 1) with a yellow F riding the grid, squash diag(1, 0); each returns home. Non-examples: the sine tangle and a drag by (1.6, 0.9), each stamped with a pink ✕. 3D: the floor tips from top-down (az 0, el 90) to az −30°, el 22° and shrinks into the lattice; the lit die with î ĵ k̂ rides turn (Rz 60°) → stretch diag(1.5, 1, 0.7) → shear (x += 0.7z) → flatten (z × 0.06), chained on the words, holds, then springs home on "cell for cell". Badge 2 drops on "where do the numbers come in?"; the ch3 grid (O3/U3) fades in under the fade-out, ready for s06.

### s06_columns · T.cut_ch3 → T.cut_read (4:10–5:14, 64 s) · Ch3 The columns are the whole story
- **Purpose / concept:** *the* idea. Any arrow is a recipe in î and ĵ; linear moves preserve recipes; so the two
  landing spots (the columns) determine everything, and matrix × vector is that recipe.
- **Visual:** î (green) and ĵ (red) grow from the origin. The (2, 1) arrow decomposes: two green copies tip to tail,
  then one red copy, landing on its tip. Recipe `2î + 1ĵ` writes beside it. Apply a move (a gentle example, columns
  (1, 1) and (−1, 2)): the grid, î, ĵ and the yellow arrow move together; the tip-to-tail chain re-forms with the *new*
  green and red arrows and lands on the new yellow tip. On `follow two arrows` everything else dims and only î and ĵ
  stay lit. On `write down where they land` each landed arrow's coordinates fly into a column of a 2 × 2 matrix
  (green column, red column) in the top-left. Then the product writes on: matrix × (x, y) = x·(green column) +
  y·(red column), with the arrow's numbers in yellow scaling each column and the sum resolving to the landed point.
- **Engine:** Manim (arrows, grid, `Eqn` with column colors, `shots.mat()` brackets).
- **Animation:** tip-to-tail chain builds with 0.3 s per copy; the move 2.0 s `smooth`; columns fly in on a curved path
  `smooth` 0.8 s; equation terms land one by one on their words.
- **On-screen:** î, ĵ, `2î + 1ĵ`, the 2 × 2 matrix in column colors, `[a b; c d][x; y] = x[a; c] + y[b; d]`.
- **Narration:** "This is the idea that everything else in this video grows out of. Look at two special arrows … i
  hat … j hat … two copies of i hat, plus one copy of j hat. Now apply a move … that recipe survives … you only need to
  follow two arrows. So write down where they land … Those two columns are the matrix … Scale the first column by the
  vector's first number … Add the two. That's where the arrow lands."
- **In / out:** continuous grid. Out: the product fades on `arrow lands`; the moved grid with î, ĵ carries into s07.
- **As built:** the move is GENTLE = [[1, −1], [1, 2]] ((2, 1) → (1, 4)); dimming is a black veil between the
  grid and î/ĵ, and each chain arrow relights over it as its term lands; the product reads
  `[[1,−1],[1,2]][2;1] = 2[1;1] + 1[−1;2] = [1;4]`.

### s07_read · T.cut_read → T.cut_ch4 (5:14–6:06, 52 s)
- **Purpose / concept:** reading a matrix as a map (predict #1); 3D needs three columns (decode the hook box); the games
  application.
- **Visual:** `[[0,−1],[1,0]]` appears with its columns colored. A small green ghost arrow sketches "up" beside column 1
  and a red one "left" beside column 2. Freeze for the 2.5 s of silence; the grid waits, untouched.
  Reveal: the grid turns a quarter turn counterclockwise, î landing up, ĵ left. Then 2D → 3D: camera tips to oblique,
  k̂ (blue) rises from the floor; the hook box H returns and each column flies out as its arrow, and the lattice
  makes the s00 move again, now readable. On `video game` a wireframe+lit die in a simple game-camera frustum turns
  by a rotation matrix: a dozen of its corner points tagged with tiny dots, each tracing to its new spot; a small
  rotation matrix (cos/sin entries) updates per "frame" tick.
- **Engine:** Manim (2D grid, matrices), `Cam` perspective lattice, pyvista lit die, crisp frustum lines.
- **Animation:** predict pause = held frame; turn 1.8 s; camera tip 1.5 s `easy_ease`; columns fly 0.8 s each
  staggered 0.25 s; frame ticks every 0.5 s with the matrix crossfading (no live LaTeX recompiles).
- **On-screen:** `[[0,−1],[1,0]]`, the hook box H, k̂, a rotation matrix with `cos θ`, `sin θ`.
- **Narration:** "Which means you can now read a matrix the way you'd read a map. Try this one … Before the grid moves,
  what do you think it does?" [pause] "It turns the whole plane a quarter turn, counterclockwise. Three dimensions work
  exactly the same way … decode the box from the very beginning … Nine numbers. Three arrows. This is how a video game
  turns a character … fresh for every frame."
- **In / out:** continuous. Out: badge 3 (three colored ticks) drops; the scene resets to a flat grid.
- **As built:** opens by easing s06's grid back to rest. The 2D → 3D tip is one camera move: the turned plane is
  the floor seen from above at azimuth 90°, so the camera orbits to (−30°, 22°) while the plane contracts into a
  [−1, 1]³ lattice (n = 1 for legibility). The game moment has no frustum: the lit die turns about z with its
  visible corners dotted (yellow, `vec`), and a numeric rotation matrix plus a θ readout re-typeset every 0.5 s.
  The die renders in a pyvista child process (its own GL context) through `FramesLayer`.

### s08_compose · T.cut_ch4 → T.cut_order (6:06–6:58, 52 s) · Ch4 One move after another
- **Purpose / concept:** composition is one move with its own matrix; tracking î and ĵ through both moves *derives*
  the row-times-column rule (payoff of s00).
- **Visual:** shear Sh, then quarter turn R, played in sequence on the grid with their matrices queued right-to-left
  at the top (`R` then `Sh` written as `R Sh`). Freeze. Follow î: shear (it stays), then rotate (up): the landed green
  arrow's coordinates drop into column 1 of a new matrix. Follow ĵ: shear (onto the diagonal (1, 1)), rotate (to (−1, 1)):
  column 2. The composite `[[0,−1],[1,1]]` completes; one single move plays from identity straight to the final grid,
  matching. Then the derivation in numbers: each column of `Sh` is pushed through `R` (`R·[1;0]`, `R·[1;1]`), and the
  entries expand into the row-times-column pattern; the grey product from s00 slides in beside it and lights up
  in color: same thing.
- **Engine:** Manim (grids, `Eqn`, brackets).
- **Animation:** each move 1.6 s `smooth`; î/ĵ tracking with a ghost trail of intermediate positions; the s00 grey
  product transforms into the colored derivation (`TransformMatchingTex`-style by entries).
- **On-screen:** `Sh`, `R`, `R Sh`, the composite matrix, `R[1;0] = [0;1]`, `R[1;1] = [−1;1]`, the expanded rule.
- **Narration:** "What happens if you make one move, and then another? Shear the plane, and then rotate it … it has its
  own matrix … The shear leaves i hat where it is, and then the rotation sends it straight up … the rotation carries
  that diagonal up and to the left … Write that out with numbers, and out comes the row times column rule … It's simply
  what two moves in a row look like, written down."
- **In / out:** continuous. Out: the composite moves to the left half for the split screen.
- **As built:** the shear is written `S` (so the product reads `RS`). The grid plays shear-then-turn, rests, then
  replays once per arrow; j-hat's stop on the diagonal stays as a dashed ghost. The derivation shows `R[1;0] = [0;1]`,
  `R[1;1] = [−1;1]`, then the numeric row-times-column expansion of `RS`, grey first and coloured by column on `row times
  column rule`. The scene fades to black at the end (cut at the paragraph break) instead of moving the composite.

### s09_order · T.cut_order → T.cut_layers (6:58–7:32, 34 s) · midpoint re-hook
- **Purpose / concept:** order matters (predict #2), in 2D and on a real object.
- **Visual:** `R Sh` with an arrow under it pointing right-to-left (`f(g(x))` writes faintly). Split screen: left
  `R Sh`, right `Sh R`, both grids at identity. Freeze, 2.5 s. Both play: the grids land differently; a single yellow
  arrow on each side ends in different places. Then two lit dice side by side at the same start pose (1 on top, 5
  facing the viewer, 3 right; `shots.DIE_FACES`). Left: quarter turn about x, then about y. Right: y, then x. They end with **4** and **2** on top.
  Each die's top face gets a thin `C.area` outline.
- **Engine:** Manim (split grids), pyvista lit dice (two instances).
- **Animation:** both sides play simultaneously (≤ 3 moving things: two grids + arrows count as one per side); die turns
  1.4 s each, `smooth`, with 0.3 s hold between turns.
- **On-screen:** `R Sh`, `Sh R`, `≠`, `f(g(x))`, the dice.
- **Narration:** "We write the rotation on the left, because it acts second, the same way you'd write f of g of x …
  Does the order matter? …" [pause] "You don't. The two grids land in different places. And real objects agree …
  A different face ends up on top. With matrices, the order is part of the move."
- **In / out:** continuous. Out: the right die's final orientation is remembered (it returns in s14); the dice fade.
- **As built:** `RS` with a right-to-left arrow and `f(g(x))`; framed side-by-side grids each carry the yellow (1, 1)
  arrow (RS → (−1, 2), SR → (0, 1)). Dice: left forward (about x) then side (about y) ends with 4 up, right the other
  order ends with 2 up (asserted in code), labelled `R_y R_x ≠ R_x R_y`.

### s10_layers · T.cut_layers → T.cut_ch5 (7:32–8:14, 43 s)
- **Purpose / concept:** neural networks are stacked matrices with bends; without bends the stack collapses into one
  matrix, which can't separate spirals.
- **Visual:** a schematic layer: a column of input numbers → matrix (brackets) → `+ b` → a small tanh bend glyph →
  output column. Then the spiral dataset (sky and coral points). "Without the bend": three matrices stack and
  multiply into one (`W₃W₂W₁ = W`); its move leaves the spirals tangled, and the best straight line still cuts both
  colors (score `67%` in `C.muted`). "With the bends": the points (and a coarse grid riding with them) pass through a
  trained *narrow* tanh net, layer by layer: matrix move, then the bend squashing the grid into a curved box. Every hidden
  layer is drawn exactly, never projected: width 2 → the plane, width 3 → 3D through `Cam`. Fold by fold the classes pull
  apart until a straight line splits them. Back in the input plane, the decision regions fill in softly behind the points,
  curling around the spirals (`100%`). The net's width and depth are fixed by a lab test at build time. The reference
  check (2-16-16-1) reaches 100 %.
- **Engine:** numpy (trained once, cached, seeded), PointsLayer(glow 0) for 600 points, FieldLayer for the decision
  regions, Manim schematic.
- **Animation:** each fold 1.2 s `smooth`; the region fill wipes in 1.5 s.
- **On-screen:** the layer schematic, `W₃W₂W₁ = W`, `67%`, `100%`.
- **Narration:** "This idea, stacking moves, is the heart of a neural network … bends the result … Without it, ten
  layers of matrices would multiply together into just one matrix … no single straight move can untangle these two
  spirals. With the bends, each layer folds space a little … Every move we've made so far could be played backwards.
  But that isn't always possible."
- **In / out:** continuous. Out: badge 4 `AB` drops; the screen clears to the grid for s11.
- **As built:** net 2-3-3-3-3-1 tanh (`nets.py`, cached in assets/spiral_net.npz, 100 %); best straight cut 67 %
  (logistic). The schematic uses the real first-layer weights on one data point. Each fold is the straight path
  from one layer's points to the next (1 s each), seen through `Cam` with a slow orbit inside a faint unit cube; the
  readout plane splits the two strands. On `played backwards` the folds unwind to the input plane and the decision
  regions (FieldLayer, 10 %) fade in behind the spirals.

### s11_undo · T.cut_ch5 → T.cut_collapse (8:14–8:52, 38 s) · Ch5 The moves you can't undo
- **Purpose / concept:** the inverse plays a move backwards; A⁻¹A = I; the determinant as the area factor (link to
  video 006). Introduces the hero A.
- **Visual:** hero A `[[3,1],[2,2]]` appears (column colors) and plays. Then the same move runs backwards in a
  continuous reverse; `A⁻¹ = ¼[[2,−1],[−2,3]]` writes on. A few yellow points ride out and back home. `A⁻¹A = I`
  completes. On `unit square` the gold unit square appears at identity, A plays again, the square becomes a
  parallelogram, and its area readout ticks `1 → 4`; `det A = 4` writes. A tiny thumbnail of video 006's title card
  sits in the corner for 3 s on `whole video of its own`.
- **Engine:** Manim.
- **Animation:** move 2.0 s forward, 2.0 s back; readout counts with the move (cached numbers, no live LaTeX
  recompiles: a pre-built `DecimalNumber`).
- **On-screen:** `A`, `A⁻¹`, `A⁻¹A = I`, `det A = 4`, the 006 thumbnail.
- **Narration:** "Here's the matrix we'll carry through the rest of the video … called the inverse … Together they make
  the move that does nothing at all, the identity. Now watch the little unit square … grows by a factor of four … the
  determinant. It has a whole video of its own. For now, one question matters. What happens when that number is zero?"
- **In / out:** continuous. Out: the grid stays at identity.

- **As built:** the grid plays the hero move forward, backward, then forward and back (A⁻¹A = I, with yellow riders
  and home circles). The unit square shows its area live (1 → 4) during a third pass, then the grid returns to rest
  for s12. Panel: A, A⁻¹ = ¼[[2,−1],[−2,3]], A⁻¹A = I, det A = 4 → `det = 0?`. A small parallelogram + `det` card
  points to video 006.

### s12_collapse · T.cut_collapse → T.cut_solve (8:52–9:49, 56 s)
- **Purpose / concept:** det 0 → collapse; many inputs share one output → no inverse; null space and column space;
  the shadow as a real-world rank-deficient matrix.
- **Visual:** `[[2,1],[2,1]]` plays: the grid squashes onto the line through (1, 1); the gold square flattens to a
  segment, det → 0. Five yellow points along a line parallel to (1, −2) slide and all land on one dot. A reverse
  arrow tries and fails (the points can't separate: a single dot pulses). The pink line through the origin along
  (1, −2) lights: all of it collapses into the origin, labeled with the symbol `N(A)` (no words); the output line is
  traced in bright `C.grid`, labeled `C(A)`. 3D: the camera tips to oblique; a lit die hovers above a floor,
  parallel sunlight (thin pink rays, `C.null`) falls diagonally; its shadow (dark grey polygon) appears on the floor.
  A handful of pink rays thread through the die: every point on a ray lands on the same shadow point. Then two
  different shapes (the die and a stretched die) cast the *same* shadow.
- **Engine:** Manim; `Cam` perspective; pyvista lit die (+ a shadow polygon computed by projecting the die's hull with
  the rank-2 projection matrix, drawn as a flat Manim polygon).
- **Animation:** squash 2.0 s `smooth`; points slide 1.5 s, staggered 0.1 s; light rays draw on 0.8 s.
- **On-screen:** the singular matrix, `det = 0`, `N(A)`, `C(A)`, rays, shadow.
- **Narration:** "Then the area becomes nothing. The whole plane gets squashed onto a single line. And something is
  lost … no move can undo it. One entire line of points gets crushed into the center itself … the null space … the
  column space … A shadow is exactly this kind of move … The direction of the light is the null space … you can't
  rebuild the die from its shadow alone. A photograph does something similar …"
- **In / out:** continuous. Out: back to top-down 2D; the parked equations panel from s02 lifts out of the corner.

- **As built:** COLLAPSE squashes the plane in 2 s (area readout 1 → 0, `det = 0`). Five points (1,1) + k(1,−2)
  slide onto (3,3), and a flash marks the spot. The null line's pink dots fall into the origin (`N(A)`), and C(A) is
  traced along (1,1). The 3D view: a die over a floor, with parallel light rays drawn behind it. Three dots on one ray
  share one shadow point, and a pink light arrow is labelled `N(A)`. On "rebuild" the die stretches along the light
  (I + 0.9 LLᵀ) and casts the same shadow.

### s13_solve · T.cut_solve → T.cut_ch6 (9:49–10:39, 50 s)
- **Purpose / concept:** Ax = b as "which input lands on b"; the row picture (lines, planes) and the move picture
  agree; det 0 → infinitely many or none (payoff of s02).
- **Visual:** hero A and the orange target b = (5, 6) (`C.target` dot). The two lines 3x + y = 5 and 2x + 2y = 6 draw;
  they cross at (1, 2). Then the move view: the yellow arrow (1, 2) is pushed through A and lands exactly on b. The s02
  three-equation panel expands; 3D: three translucent lit planes (flat-shaded, thin crisp edges, one shade per plane from
  `C.frame`/`C.muted`/`C.data` greys with distinct tints) rise into place and intersect at a gold-yellow point (1, 2, 1).
  Singular case: the third plane rotates into `2x + 3z = 5`; the three now share a pink line. Then it slides to `= 6`
  and the planes pass each other, with no common point (a small `∅` pops).
- **Engine:** Manim (2D lines), `Cam` perspective with flat-shaded polygons (Lambert, one fixed key light).
- **Animation:** lines draw on 1.0 s; the arrow push 1.5 s; planes rise 1.2 s each, staggered; the singular rotation
  2.0 s `smooth`.
- **On-screen:** `Ax = b`, the 2D line equations, `(1, 2)`, the three equations, `(1, 2, 1)`, `det = 0`, `∅`.
- **Narration:** "Now, about those three equations from the start. Solving them is really a question about a move …
  Which arrow was sent there? In two dimensions, each equation is a line … With three unknowns, each equation becomes a
  flat plane … That point is the solution. But if the determinant is zero … infinitely many points, or they miss each
  other entirely … That's what a zero determinant has been warning you about all along."
- **In / out:** continuous. Out: badge 5 `A⁻¹` drops; planes fade, back to the 2D grid.

- **As built:** the panel holds the three equations, then `Ax = b`. 2D: the target b = (5, 6), a `?`, then the lines
  3x + y = 5 and 2x + 2y = 6 cross at (1, 2); that arrow is pushed through A onto b. 3D (slow drift, az −66° → −44°):
  three translucent planes rise in, and their pairwise crossing lines meet at (1, 2, 1). At det 0 the third plane
  pivots about that point into 2x + 3z = 5, so the three lines merge into one pink line. At "= 6" they run parallel
  and `∅` pops. Badge 5 drops on "warning".

### s14_eigen · T.cut_ch6 → T.cut_power (10:39–11:50, 71 s) · Ch6 The directions that don't turn
- **Purpose / concept:** eigenvectors are directions a move leaves on their own line; eigenvalues are their stretch;
  predict #3: plane rotations have none, 3D rotations always have an axis (payoff of s09).
- **Visual:** hero A. A single input arrow (thin white) sweeps around a unit circle; its output arrow (yellow) is drawn
  live, with a faint line through each to show "its own line". Most of the sweep: the two lines differ (the output
  visibly knocked off). At (1, 1) they align: the violet line lights and stays, output ×4; at (1, −2) they align
  again: the second violet line, output ×1 (the arrow doesn't change at all, a small `= ` flash). `Av = λv` writes,
  with `λ` in violet; `λ = 4`, `λ = 1` tag the lines. Predict: a pure rotation of the plane, freeze 2.5 s, reveal:
  sweeping shows every output off its line. 3D: the s09 die (y-then-x) returns; its combined move `[[0,0,1],[1,0,0],[0,1,0]]`
  plays as one smooth 120° turn about the violet diagonal axis through (1, 1, 1), and points on the axis stay put.
- **Engine:** Manim (sweep via `m.redraw` pure f(t)), `Cam` perspective, pyvista lit die.
- **Animation:** sweep at constant angular speed with slow-down near the eigen-directions (`Clock` with a rate
  track); the 3D turn 2.4 s `smooth`.
- **On-screen:** `Av = λv`, `λ = 4`, `λ = 1`, the 3D permutation matrix.
- **Narration:** "Back to our running example … Most arrows get knocked off their own line … This arrow only gets
  stretched, by a factor of four … This one isn't stretched at all. These special directions are called eigenvectors
  … They're the skeleton of the move … A quick test …" [pause] "None of them … Those two quarter turns combine into a
  single turn, about a tilted axis … The axis is an eigenvector, with an eigenvalue of one."
- **In / out:** continuous. Out: the camera returns to 2D; the violet lines remain faintly.

- **As built:** one arrow (white) and its image under A (yellow), each with a faint line through it. It sweeps from
  110° to 160° ("knocked off"), then to 45°, where the violet line lights with `λ = 4`, then to −63.4° (`λ = 1`, a
  flash). The panel holds A, then `Av = λv`. For the skeleton, the grid plays A while two violet arrows stay on their
  lines. The test uses R = [[cos θ, −sin θ], [sin θ, cos θ]] (60° on screen). The grid turns, a `?` holds through the
  pause, then a full sweep shows every output off its line. In 3D the die plays its two quarter turns (y then x),
  dips out, and replays them as one 120° turn about (1,1,1) (`turn(N, 120)` == `R_x R_y`, asserted), then turns
  again. The violet axis is split into a far half behind the die and a near half in front, with a dot on the corner
  that stays put, `R_x R_y = [[0,0,1],[1,0,0],[0,1,0]]` in the panel, and `λ = 1` at the tip.

### s15_power · T.cut_power → T.cut_rank (11:50–12:15, 26 s)
- **Purpose / concept:** repeated multiplication drifts everything toward the dominant eigenvector.
- **Visual:** a round cloud of 1,500 white points around the origin. Each "round" applies A (positions rescaled by
  ¼ per round so the cloud stays on screen; the scale is shown as a tiny `×¼` tick). Round by round the cloud thins into the
  violet (1, 1) line: after four rounds it's a needle.
- **Engine:** numpy → PointsLayer (glow 0); Manim round counter and violet line.
- **Animation:** each round 0.9 s `smooth`, 0.3 s hold; counter `A, A², A³, A⁴` ticks.
- **On-screen:** `A`, `A²`, `A³`, `A⁴`, the violet line.
- **Narration:** "Eigenvectors also tell you where things are heading … After just a few rounds, the whole cloud has
  lined up along it. Apply a matrix over and over, and everything drifts toward its strongest eigenvector. That simple
  fact once organized the entire web."
- **In / out:** match cut: the needle's points become surfers dropping onto the s16 graph.

- **As built:** the same stage as s14 with both violet lines faint. 1,500 points in a disc (seed 9) take six rounds
  of A/4, each 0.9 s along a straight path. The counter reads `A^k ×4^{-k}`. The cloud becomes a needle on the (1,1)
  line, which brightens while the other line fades. `λ = 4` appears on "drifts".

### s16_pagerank · T.cut_rank → T.cut_ch7 (12:15–13:01, 45 s)
- **Purpose / concept:** PageRank is the eigenvector with eigenvalue 1 of the click (Markov) matrix; links from
  important pages count for more.
- **Visual:** seven page nodes (rounded-square outlines, letters A–G in CM) with thin arrows for links. 3,000 surfers
  (small white dots) start piled on one page, then hop along links each round; occasional random jumps draw as faint
  arcs. Each node's fill rises with its share (`C.eigen` fill level). Restart from a different pile: the same levels
  return. The matrix `G` (7 × 7, tiny, column-colored by source page in greys) sits at left; the final level column
  writes beside it as a violet vector with `G p = p`. On `these two pages`, B and D outline in `C.area`; B's single
  incoming arrow (from C) thickens.
- **Engine:** Taichi `Surfers(Sim)` (baked, seeded) → PointsLayer; Manim graph and fills.
- **Animation:** one hop per 0.25 s, positions eased along link arcs; fills smooth toward counts; restart crossfade 0.6 s.
- **On-screen:** nodes A–G, `G`, `p`, `G p = p`, the shares (`.37`, `.20`, `.18`, `.10`, `.06`, `.05`, `.04`) beside
  nodes at the end.
- **Narration:** "Here's a tiny web of seven pages, and thousands of imaginary readers clicking links at random … Run
  it, and the crowd settles … That settled crowd is an eigenvector of the click matrix, with an eigenvalue of one …
  This was the idea behind Google's PageRank … one of those links comes from the most popular page, and that makes it
  count for far more."
- **In / out:** cut on chapter. Out: badge 6 `λ` drops.

- **As built:** seven rounded-square pages with curved links (A→C and C→A separate). 3,000 readers (numpy,
  seeded) hop one round every 0.5 s along the link arcs, with 15 % random jumps. The first run starts piled on D. On
  "doesn't matter where everyone started" a second run starts piled on F (0.45 s rounds) and settles to the same
  shares. G is a 7 × 7 grey heat map, then **p** is a violet column and `Gp = p` is written. The shares (.37 .20
  .18 .10 .06 .05 .04, the exact eigenvector) sit beside the pages. On "these two pages" B and D outline in gold,
  their single incoming links (C→B, E→D) thicken, C pulses, and B's .18 flashes. Badge 6 (λ) drops on "far more".

### s17_ellipse · T.cut_ch7 → T.cut_photo_svd (13:01–14:12, 71 s) · Ch7 A rotation, a stretch, and a rotation
- **Purpose / concept:** every matrix turns circles into ellipses; perpendicular inputs land on the perpendicular
  axes; A = UΣVᵀ (the deepest idea; a mirror flip allowed when det < 0).
- **Visual:** hero A and a teal circle of 24 arrows. A plays: circle → ellipse. The longest and shortest axes draw
  (teal, labelled `σ₁`, `σ₂`). Trace back: two perpendicular input arrows on the original circle light up and land
  on the axes. Then the three-step replay from identity on the grid: (1) rotate −30.1° so those inputs align with
  î/ĵ (`Vᵀ`), (2) stretch along the grid by 4.13 and 0.97 (`Σ`), (3) rotate +41.4° into place (`U`). The final grid
  matches the direct A move exactly (overlay check: ghost of A's grid). `A = UΣVᵀ` builds from the three labels.
  3D: a lit sphere (teal tint) becomes an ellipsoid with three perpendicular axes, in three stages.
- **Engine:** Manim; pyvista lit sphere/ellipsoid (or flat-shaded Manim mesh fallback).
- **Animation:** each stage 1.6 s `smooth`, 0.4 s hold; labels `out_back`; the 3D stage turns slowly (camera orbit 2°/s).
- **On-screen:** circle, ellipse, `σ₁`, `σ₂`, `Vᵀ`, `Σ`, `U`, `A = UΣVᵀ`.
- **Narration:** "There's one more thing to see … The circle becomes an ellipse … An ellipse has a longest direction
  and a shortest one … two input arrows, also at right angles … First, rotate … Then stretch … Then rotate again …
  Rotate, stretch, rotate … the singular value decomposition … It works for every matrix, of any shape or size … a
  sphere becomes an ellipsoid … the move underneath is always this simple."
- **In / out:** continuous. Out: the ellipse shrinks into the top-left corner as an icon.

- **As built:** a teal circle of 24 arrows plays A into an ellipse. The axes σ₁ and σ₂ are drawn, then dimmed. The two
  perpendicular inputs V₁ and V₂ are followed back to the circle (right-angle mark) and forward again, landing on the
  axes. The three steps replay from identity: rotate −30.13° (Vᵀ), stretch diag(4.131, 0.968) (Σ), rotate +41.44°
  (U). The proper rotations come from `proper_svd2`, the final frame is asserted equal to A, and `A = UΣVᵀ` builds
  right to left as the steps play, with σ₁ ≈ 4.13 and σ₂ ≈ 0.97 below. In 3D, the hook box H = [[2,1,0],[0,1,1],
  [1,0,1]]: a flat-shaded teal sphere (12 × 24 facets, painter-sorted, key light) and its three V axes go through
  the same three steps into an ellipsoid (σ = 2.53, 1.35, 0.88) while the camera drifts.

### s18_photo_svd · T.cut_photo_svd → T.cut_outro (14:12–15:08, 57 s) · the big payoff
- **Purpose / concept:** the picture (s03) is a matrix, so it is a move with stretches; its rank-1 layers ordered by
  σ rebuild it; keeping the biggest compresses it. Data and move are one object.
- **Visual:** the parked thumbnail from s03 grows back to center. Beside it, the singular values plot as a descending
  teal bar strip (log-ish height, 414 bars, the first few towering). One layer as an outer product: a teal column
  strip × a teal row strip = a soft-banded image (layer 1). Layers accumulate on a canvas at right with a counter:
  1 (a blur), 2, 3, 5, 10 (the die appears), 30 (close to the original); the bar strip lights up to the k-th bar. The
  numbers ratio writes: `30 × 961 / 480² ≈ 12.5%`. The rest of the bars (small stretches) light in muted grey and the
  difference image (noise and fine detail) flashes faintly. On `never two different things` the picture and the
  s17 ellipse icon slide together.
- **Engine:** numpy SVD → ArrayLayer (each partial sum precomputed and cached), Manim bars, counter and equation.
- **Animation:** layer ticks on words ("second", "third", "ten", "thirty") and fast-forward between; each tick 0.4 s
  crossfade.
- **On-screen:** the picture, `σ` bars, `k = 1 … 30`, `u₁ v₁ᵀ`, `≈ 12.5%`.
- **Narration:** "Now, remember the picture from the beginning … Two rotations, and a list of stretches … a single
  column of numbers, times a single row … Just a soft blur … By ten, you can make out the die. By thirty, it's close to
  the original. Thirty layers out of hundreds, using about an eighth of the numbers … a classic way to compress images
  … So the table and the machine were never two different things. A grid of numbers is a move. And its biggest
  stretches are what matter most."
- **In / out:** continuous. Out: badge 7 `UΣVᵀ` drops; the rail is complete.

- **As built:** the photo (`shots.photo()`) sits in tall brackets with `UΣVᵀ` beside it, Σ in teal. All 480
  singular values form a log-height bar strip along the bottom. On "a single column times a single row" the u₁ strip
  and the v₁ᵀ strip frame the empty canvas with σ₁u₁v₁ᵀ, then layer 1 fills the canvas. The layers tick with a 0.35 s
  crossfade: 1, 2, 3, a quick run to 10, a quick run to 30. The bar strip lights in teal up to k, with `k = …`
  under the canvas. Then 30·961/480² ≈ 12.5 % appears, and the 30-layer leftover (×5) flashes on the canvas on
  "noise". On "never two different things" the photo `=` a teal ellipse icon. Badge 7 (UΣVᵀ) drops on "matter
  most", completing the rail.

### s19_outro · T.cut_outro → T.end (15:08–16:03, 55 s)
- **Purpose / concept:** callback and closing thought: a matrix is a move seen from a chosen basis (change-of-basis
  tease); point to video 006.
- **Visual:** black; the hook box H returns to center exactly as in s00. The badges from the rail glide in around
  it one per sentence: columns (arrows lift out), `AB`, `det`, `λ` (violet axis lines), `UΣVᵀ` (sphere → ellipsoid
  icon). On `one last thought` the lattice and the lit die return with H applied. Then a *different* set of three
  measuring arrows (thin white) replaces î ĵ k̂, and H's nine numbers crossfade to the new (computed) matrix
  P⁻¹HP while the die and the lattice **do not move at all**. On `the move doesn't`, everything holds.
  End card: the 006 title thumbnail slides in on `right here`.
- **Engine:** Manim, `Cam` perspective, pyvista lit die.
- **Animation:** badges `spring`; the number crossfade 1.2 s; final hold 3 s.
- **On-screen:** H, badges, P⁻¹HP (numbers only), the 006 card.
- **Narration:** "Let's look at that box of nine numbers one last time. Its columns are where the axes land …
  a rotation, a stretch, and another rotation. One last thought … Pick three different arrows, and the very same move
  gets nine different numbers. The numbers change. The move doesn't. If you'd like to see one of those numbers up
  close, the determinant, that video is right here. Thanks for watching."
- **In / out:** end on black after the tail.
- **As built:** H (size 96) staggers in; the five chapter badges fly out of their rail slots into a ring around it (on "axes land", "one after another", "undone", "don't turn", "underneath"), and H's columns pulse. On "one last thought" the ring fades, H parks top-left on a backing, and the lattice with H applied, the lit die and H's column arrows return (az −30°, el 22°). The three arrows pulse on "i hat / j hat / k hat". Three other measuring arrows (P's columns, det 1) replace them in white, and the numbers cross-fade to P⁻¹HP = [[3, 1, 0], [−2, 1, 1], [3, 0, 0]] (labelled) while nothing in the scene moves. The video-006 determinant card slides in; everything fades over the last 1.3 s.

## Build order (chapter by chapter, after this plan is approved)
1. Library prep: decide the animated lit-3D path (an `ArrayLayer` that takes f(t), or a frame cache) with a quick lab test;
   promote 006's `brackets` / `matrix_panel` / `grid_lines` if they're needed again (now copied in `shots.py`).
2. Ch3 first (s06, s07): it defines the column-color language every other scene uses. Then Ch2, Ch4, Ch5, Ch6, Ch7, Ch1.
3. Intro and outro last (they reuse shots from every chapter).
4. Each scene: `aion still … --at <beat>` → look → `aion preview 009 sNN` → `aion audit 009 --design`.
5. Final: Kaggle bundle (as 007/008) or local `aion render 009 --bg` (16:03 at 1080p60 is long on this machine).

## Beat table
`uv run aion beats 009 --md` (times in seconds of `assets/audio.wav`).

| beat | time | end | words |
|---|---|---|---|
| box | 1.50 | 3.88 | Nine numbers, arranged in a box |
| useful | 5.40 | 6.72 | the most useful object |
| boring | 9.32 | 10.07 | the most boring |
| alive | 12.82 | 13.80 | it comes alive |
| columns | 14.29 | 15.84 | Each column becomes an arrow |
| tilts | 16.19 | 17.98 | Space itself tilts |
| ride | 21.38 | 22.18 | along for the ride |
| photo | 23.32 | 24.60 | Every photo on your phone |
| game | 27.96 | 29.32 | Every frame of a video game |
| google | 31.24 | 32.04 | helped Google rank |
| network | 33.64 | 34.76 | a modern neural network |
| bookkeeping | 40.94 | 41.74 | as bookkeeping |
| rule | 43.66 | 45.02 | a strange rule for multiplying |
| forget | 47.82 | 48.42 | quietly forget |
| works | 49.80 | 50.40 | rule works |
| hides | 50.66 | 51.36 | It just hides |
| cut_preview ✂ | 53.35 | 53.35 | actually is. ✂ So here is the claim |
| claim | 53.85 | 54.90 | So here is the claim |
| not_table | 57.82 | 58.94 | not a table you read |
| move_you_make | 59.34 | 60.54 | It is a move you make |
| picking_up | 61.46 | 62.86 | picking up all of space |
| strange | 66.76 | 68.71 | the strange rules stop being strange |
| two_moves | 68.98 | 70.52 | Multiplying two matrices |
| flat | 72.91 | 74.80 | Some moves crush space flat |
| untouched | 77.48 | 78.88 | special directions untouched |
| three_motions | 83.20 | 84.31 | three simple motions |
| two_arrows | 85.98 | 87.38 | two arrows on a flat grid |
| photograph | 88.38 | 89.56 | taking a photograph apart |
| cut_ch1 ✂ | 95.15 | 95.15 | one stretch at a time. ✂ First, the plain facts |
| plain | 96.72 | 97.53 | the plain facts |
| rectangle | 98.80 | 100.02 | a rectangle of numbers |
| two_by_three | 103.84 | 105.20 | two by three |
| address | 105.36 | 106.79 | every entry has an address |
| which_row | 107.07 | 108.21 | which row it sits in |
| which_col | 108.27 | 108.95 | and which column |
| anything | 111.94 | 113.05 | hold almost anything |
| three_eq | 113.38 | 114.58 | Take three equations |
| strip | 116.65 | 117.94 | Strip away the letters |
| whats_left | 119.86 | 121.23 | what's left is a matrix |
| remember_eq | 121.69 | 123.13 | Remember these three equations |
| solve_later | 123.54 | 124.40 | come back and solve them |
| cut_photo ✂ | 124.85 | 124.85 | solve them. ✂ Or take a picture |
| picture | 125.30 | 126.26 | Or take a picture |
| frame_ago | 127.48 | 128.92 | a single frame from a moment ago |
| zoom | 129.22 | 130.44 | Zoom in far enough |
| squares | 131.32 | 132.41 | tiny squares |
| bright | 134.32 | 135.03 | how bright it is |
| hundreds | 137.56 | 138.44 | hundreds of rows |
| keep_mind | 140.01 | 141.08 | Keep this one in mind |
| table | 142.04 | 143.90 | So a matrix can be a table |
| question | 144.90 | 145.84 | a strange question |
| grades | 146.13 | 147.58 | A table of exam grades |
| prices | 149.00 | 150.06 | A list of prices |
| turn_space | 154.49 | 156.27 | pick up a whole space and turn it |
| watching | 160.08 | 161.32 | start watching what they do |
| cut_ch2 ✂ | 162.22 | 162.22 | what they do. ✂ Picture a flat grid |
| grid | 163.13 | 164.62 | Picture a flat grid |
| vector | 166.95 | 168.42 | That arrow is a vector |
| two_over | 171.04 | 172.21 | Two steps over |
| machine | 174.41 | 175.74 | Now imagine a machine |
| arrow_in | 179.59 | 181.26 | Arrow in, arrow out |
| all_at_once | 186.02 | 187.28 | every arrow at once |
| slides | 188.98 | 190.53 | slides to its new home |
| tangle | 194.12 | 194.76 | tangle the grid |
| straight | 199.33 | 200.96 | Straight lines stay straight |
| even | 201.49 | 204.15 | Evenly spaced lines stay evenly spaced |
| center | 204.28 | 205.74 | the center stays where it is |
| linear | 207.08 | 208.10 | are called linear |
| cut_gallery ✂ | 208.62 | 208.62 | called linear. ✂ Inside those rules |
| freedom | 210.46 | 211.82 | a surprising amount of freedom |
| rotate | 212.23 | 212.94 | You can rotate |
| stretch | 214.31 | 215.07 | You can stretch it |
| shear | 217.36 | 218.12 | You can shear it |
| cards | 221.27 | 222.25 | like a deck of cards |
| flip | 222.67 | 223.35 | You can flip it |
| squash | 225.58 | 226.70 | squash it flat |
| curves | 229.96 | 231.72 | bend the grid lines into curves |
| drag | 232.08 | 233.04 | drag the whole plane |
| three_d | 235.94 | 237.55 | carries over to three dimensions |
| die | 237.96 | 239.50 | A die can be turned |
| cell | 244.10 | 244.95 | cell for cell |
| numbers_q | 247.84 | 248.86 | where do the numbers come in |
| cut_ch3 ✂ | 249.82 | 249.82 | come in? ✂ This is the idea |
| key_idea | 250.77 | 251.70 | This is the idea |
| special | 255.36 | 256.43 | two special arrows |
| one_right | 256.83 | 257.76 | One step to the right |
| ihat | 257.96 | 258.74 | called i hat |
| one_up | 259.14 | 260.32 | And one step up |
| jhat | 260.36 | 261.02 | called j hat |
| built | 261.51 | 263.08 | Every other arrow can be built |
| our_arrow | 264.41 | 265.56 | Our arrow from before |
| recipe | 266.00 | 267.35 | two copies of i hat |
| plus_one | 267.45 | 268.73 | plus one copy of j hat |
| apply | 269.68 | 270.84 | Now apply a move |
| grid_stays | 271.25 | 272.86 | Because the grid lines stay parallel |
| survives | 274.22 | 275.47 | that recipe survives |
| still | 275.86 | 277.18 | The new arrow is still |
| new_i | 277.26 | 279.46 | two copies of wherever i hat landed |
| new_j | 279.50 | 281.69 | plus one copy of wherever j hat landed |
| every_point | 284.59 | 286.00 | To know where every single point |
| follow_two | 288.24 | 289.30 | follow two arrows |
| write_down | 290.16 | 291.57 | So write down where they land |
| where_i | 291.96 | 292.90 | Where i hat lands |
| first_col | 292.98 | 294.27 | becomes the first column |
| where_j | 294.48 | 295.38 | Where j hat lands |
| second_col | 295.46 | 296.29 | becomes the second |
| are_matrix | 296.69 | 298.60 | Those two columns are the matrix |
| mult | 301.56 | 303.24 | multiplying a matrix by a vector |
| scale1 | 305.81 | 306.92 | Scale the first column |
| scale2 | 308.62 | 309.72 | Scale the second column |
| add | 311.02 | 311.61 | Add the two |
| lands | 311.96 | 313.38 | That's where the arrow lands |
| cut_read ✂ | 313.77 | 313.77 | arrow lands. ✂ Which means you can now read |
| read_map | 315.26 | 317.25 | read a matrix the way you'd read a map |
| try_this | 317.78 | 318.41 | Try this one |
| col1_says | 318.67 | 320.22 | Its first column says |
| up | 320.86 | 322.41 | lands pointing straight up |
| col2_says | 322.74 | 323.82 | Its second says |
| left | 323.90 | 326.09 | j hat lands pointing left |
| predict | 327.33 | 328.23 | what do you think it does |
| quarter | 331.89 | 334.30 | It turns the whole plane a quarter turn |
| three_dims | 336.21 | 337.88 | Three dimensions work exactly |
| three_cols | 338.87 | 340.82 | with three arrows and three columns |
| decode | 342.20 | 343.00 | decode the box |
| col1_3d | 344.33 | 346.60 | The first column is where i hat goes |
| col2_3d | 346.95 | 348.43 | The second, j hat |
| khat | 349.48 | 350.47 | where k hat goes |
| k_up | 350.71 | 351.90 | the arrow pointing up |
| nine_three | 352.32 | 353.56 | Nine numbers |
| three_arrows | 353.64 | 354.64 | Three arrows |
| game_turn | 355.18 | 356.66 | This is how a video game turns |
| corners | 359.02 | 360.46 | thousands of corner points |
| same_matrix | 361.78 | 363.94 | multiplied by the same small matrix |
| fresh | 363.98 | 365.18 | fresh for every frame |
| cut_ch4 ✂ | 366.15 | 366.15 | every frame. ✂ What happens if you make |
| then_another | 368.20 | 369.64 | one move, and then another |
| shear_rot | 370.13 | 371.02 | Shear the plane |
| still_straight | 373.18 | 374.61 | The grid still ends up straight |
| own_matrix | 380.22 | 381.59 | it has its own matrix |
| follow | 382.81 | 384.56 | we just follow i hat and j hat |
| ihat_stays | 385.53 | 387.55 | The shear leaves i hat where it is |
| sends_up | 388.52 | 389.47 | sends it straight up |
| col1 | 389.69 | 391.94 | That's the first column of the combined move |
| diag | 393.04 | 394.99 | tips j hat onto the diagonal |
| up_left | 397.12 | 398.06 | up and to the left |
| col2 | 398.27 | 399.59 | That's the second column |
| look | 400.47 | 402.15 | Look at what we just did |
| pushed | 403.97 | 404.82 | we pushed a column |
| row_col | 409.54 | 410.58 | row times column rule |
| torture | 412.12 | 413.38 | Nobody invented that rule |
| written | 415.74 | 417.22 | two moves in a row look like |
| cut_order ✂ | 418.20 | 418.20 | written down. ✂ We write the rotation |
| left_side | 418.65 | 420.28 | We write the rotation on the left |
| fgx | 422.76 | 423.75 | f of g of x |
| order_q | 425.98 | 426.90 | Does the order matter |
| same_place | 429.96 | 431.03 | end up in the same place |
| dont | 434.55 | 434.99 | You don't |
| grids_differ | 435.25 | 437.58 | The two grids land in different places |
| real | 438.28 | 439.79 | real objects agree |
| forward | 440.32 | 441.63 | a quarter turn forward |
| side | 441.92 | 443.06 | a quarter turn to the side |
| other_order | 444.60 | 445.63 | do it in the other order |
| top_face | 445.89 | 447.82 | A different face ends up on top |
| part_of | 449.72 | 451.44 | the order is part of the move |
| cut_layers ✂ | 451.88 | 451.88 | of the move. ✂ This idea, stacking moves |
| stacking | 452.31 | 454.14 | This idea, stacking moves |
| layer | 456.36 | 458.32 | Each layer takes a list of numbers |
| bends | 461.48 | 462.44 | bends the result |
| bend_matters | 464.70 | 465.90 | That bend matters |
| ten_layers | 468.19 | 469.50 | ten layers of matrices |
| spirals | 476.38 | 477.82 | untangle these two spirals |
| with_bends | 478.90 | 479.96 | With the bends |
| fold | 482.37 | 483.47 | Fold by fold |
| told_apart | 486.48 | 487.51 | cleanly told apart |
| backwards | 490.10 | 491.20 | could be played backwards |
| not_always | 492.10 | 493.86 | isn't always possible |
| cut_ch5 ✂ | 494.50 | 494.50 | always possible. ✂ Here's the matrix |
| hero | 495.36 | 496.40 | Here's the matrix we'll carry |
| tilts_grid | 497.99 | 500.59 | It tilts and stretches the grid |
| reverse | 501.64 | 502.86 | play the move in reverse |
| inverse | 505.81 | 506.67 | called the inverse |
| home | 509.60 | 511.47 | every point comes home |
| identity | 514.06 | 514.74 | the identity |
| square | 516.30 | 517.46 | watch the little unit square |
| four | 519.62 | 520.80 | by a factor of four |
| determinant | 523.85 | 525.04 | is called the determinant |
| own_video | 525.86 | 527.49 | a whole video of its own |
| zero_q | 530.02 | 531.89 | What happens when that number is zero |
| cut_collapse ✂ | 532.38 | 532.38 | is zero? ✂ Then the area becomes nothing |
| nothing | 532.88 | 534.90 | Then the area becomes nothing |
| squashed | 536.46 | 538.81 | squashed onto a single line |
| lost | 539.18 | 540.00 | something is lost |
| same_spot | 542.54 | 544.24 | land on exactly the same spot |
| cant_undo | 547.74 | 548.83 | no move can undo it |
| crushed | 549.75 | 551.68 | One entire line of points |
| null | 555.04 | 556.20 | called the null space |
| survive | 556.96 | 558.08 | everything that survives |
| colspace | 559.53 | 560.69 | called the column space |
| shadow | 565.01 | 566.93 | A shadow is exactly this kind of move |
| sunlight | 567.28 | 568.58 | Sunlight flattens |
| ray | 571.70 | 572.98 | along a single ray of light |
| light_null | 575.75 | 576.82 | The direction of the light |
| rebuild | 579.06 | 580.42 | rebuild the die from its shadow |
| photograph2 | 581.57 | 583.33 | A photograph does something similar |
| cut_solve ✂ | 588.70 | 588.70 | read off directly. ✂ Now, about those three equations |
| equations | 589.64 | 590.76 | about those three equations |
| about_move | 593.08 | 594.44 | a question about a move |
| which_arrow | 598.73 | 600.68 | Which arrow was sent there |
| lines2d | 602.41 | 603.61 | each equation is a line |
| cross | 604.78 | 605.77 | where the lines cross |
| on_target | 608.46 | 610.01 | lands exactly on the target |
| planes | 613.04 | 614.24 | becomes a flat plane |
| meet | 616.72 | 617.91 | meet at a single point |
| solution | 618.15 | 619.66 | That point is the solution |
| det_zero | 620.50 | 622.07 | if the determinant is zero |
| infinitely | 625.46 | 626.90 | share infinitely many points |
| miss | 627.78 | 629.25 | miss each other entirely |
| no_answer | 629.70 | 630.46 | no answer at all |
| warning | 636.10 | 637.51 | warning you about all along |
| cut_ch6 ✂ | 638.58 | 638.58 | all along. ✂ Back to our running example |
| running | 639.64 | 640.89 | Back to our running example |
| single | 642.21 | 643.12 | watch single arrows |
| knocked | 645.72 | 647.09 | get knocked off their own line |
| sweep | 650.26 | 651.51 | sweep around the circle |
| lines_up | 653.67 | 655.59 | the output lines up with the input |
| four_x | 658.06 | 659.46 | by a factor of four |
| another | 659.86 | 660.52 | here's another one |
| not_stretched | 661.46 | 662.46 | isn't stretched at all |
| eigenvectors | 665.08 | 666.57 | called eigenvectors |
| eigenvalue | 668.28 | 669.37 | its eigenvalue |
| skeleton | 670.12 | 671.32 | the skeleton of the move |
| plain_mult | 674.60 | 676.65 | plain multiplication by a single number |
| test | 677.79 | 678.79 | A quick test |
| rotation_q | 681.29 | 683.11 | Which arrows stay on their own line |
| none | 686.74 | 687.29 | None of them |
| in_3d | 689.54 | 691.91 | in three dimensions, it's different |
| remember_die | 691.91 | 692.85 | Remember the die |
| combine | 696.26 | 697.80 | combine into a single turn |
| axis | 699.50 | 701.22 | Arrows along that axis |
| every_rotation | 702.41 | 704.10 | Every rotation in space |
| axis_eigen | 705.62 | 707.48 | The axis is an eigenvector |
| cut_power ✂ | 709.80 | 709.80 | eigenvalue of one. ✂ Eigenvectors also tell you |
| heading | 711.88 | 713.06 | where things are heading |
| cloud | 713.35 | 714.63 | Take a cloud of points |
| again | 716.04 | 717.92 | again, and again |
| wins | 720.52 | 722.12 | wins a little more |
| lined_up | 724.72 | 726.28 | lined up along it |
| drifts | 729.12 | 731.02 | drifts toward its strongest eigenvector |
| web | 733.16 | 734.76 | organized the entire web |
| cut_rank ✂ | 735.30 | 735.30 | entire web. ✂ Here's a tiny web |
| seven | 736.22 | 738.22 | a tiny web of seven pages |
| readers | 738.46 | 739.98 | thousands of imaginary readers |
| bored | 743.30 | 743.82 | gets bored |
| clicks | 746.73 | 747.80 | Each round of clicks |
| settles | 752.96 | 753.87 | the crowd settles |
| far_more | 755.84 | 756.64 | far more readers |
| any_start | 757.72 | 759.18 | doesn't matter where everyone started |
| settled | 760.19 | 761.38 | That settled crowd |
| no_change | 765.49 | 767.20 | The shuffle no longer changes it |
| pagerank | 769.14 | 770.14 | Google's PageRank |
| two_pages | 770.82 | 771.91 | look at these two pages |
| one_link | 772.98 | 774.82 | just one incoming link |
| popular | 776.18 | 777.46 | the most popular page |
| counts | 778.62 | 779.57 | count for far more |
| cut_ch7 ✂ | 780.53 | 780.53 | far more. ✂ There's one more thing |
| deepest | 783.40 | 784.40 | the deepest idea |
| circle | 786.21 | 787.73 | Draw a circle of arrows |
| ellipse | 789.51 | 791.14 | The circle becomes an ellipse |
| no_accident | 791.64 | 792.85 | That's no accident |
| every_matrix | 793.06 | 794.42 | Every matrix like this one |
| longest | 798.04 | 799.00 | a longest direction |
| follow_back | 801.59 | 802.95 | Follow them back |
| right_angles | 804.80 | 806.09 | also at right angles |
| three_steps | 811.26 | 812.09 | in three steps |
| rot1 | 812.65 | 814.25 | First, rotate |
| stretch2 | 817.26 | 818.88 | Then stretch along the grid |
| rot2 | 821.24 | 822.70 | Then rotate again |
| rsr | 824.46 | 826.49 | Rotate, stretch, rotate |
| mirror | 828.94 | 829.58 | a mirror flip |
| svd | 832.96 | 835.15 | the singular value decomposition |
| singular_values | 836.64 | 838.40 | called singular values |
| any_shape | 840.24 | 841.34 | any shape or size |
| sphere | 843.04 | 844.56 | a sphere becomes an ellipsoid |
| simple | 849.76 | 851.35 | always this simple |
| cut_photo_svd ✂ | 851.72 | 851.72 | this simple. ✂ Now, remember the picture |
| remember_pic | 852.50 | 853.22 | remember the picture |
| matrix_too | 855.88 | 857.14 | It's a matrix too |
| two_rot | 858.87 | 861.45 | Two rotations, and a list of stretches |
| layer1 | 863.78 | 865.96 | Each stretch contributes one layer |
| col_row | 869.92 | 871.72 | a single column of numbers |
| biggest | 873.14 | 874.36 | Here's the biggest layer |
| blur | 875.19 | 876.40 | Just a soft blur |
| second | 877.08 | 877.81 | Add the second |
| third | 878.19 | 879.11 | and the third |
| ten | 879.42 | 880.15 | By ten |
| thirty | 881.41 | 882.40 | By thirty |
| eighth | 886.36 | 888.39 | about an eighth of the numbers |
| noise | 889.84 | 891.13 | fine detail, and noise |
| compress | 892.86 | 894.89 | a classic way to compress images |
| tables | 897.46 | 899.31 | huge tables of measurements |
| never_two | 901.02 | 902.19 | never two different things |
| is_move | 902.44 | 905.15 | A grid of numbers is a move |
| matter | 906.42 | 907.36 | are what matter most |
| cut_outro ✂ | 908.28 | 908.28 | matter most. ✂ Let's look at that box |
| last_time | 909.31 | 910.52 | Let's look at that box |
| axes_land | 913.45 | 915.74 | Its columns are where the axes land |
| mult2 | 915.74 | 917.34 | Multiplying it by another matrix |
| det2 | 919.35 | 920.78 | Its determinant tells you |
| eig2 | 924.05 | 926.06 | Its eigenvectors are the directions |
| underneath | 928.14 | 928.86 | underneath it all |
| thought | 933.21 | 933.92 | One last thought |
| not_move | 935.60 | 937.15 | aren't really the move itself |
| standing | 938.96 | 940.44 | from where we're standing |
| choice | 941.24 | 942.71 | our own choice of i hat |
| pick | 945.04 | 946.43 | Pick three different arrows |
| change | 950.14 | 951.13 | The numbers change |
| doesnt | 951.49 | 952.52 | The move doesn't |
| det_video | 956.01 | 958.32 | the determinant, that video is right here |
| thanks | 958.90 | 959.96 | Thanks for watching |
319 beats, 20 scenes, audio 962.88s
