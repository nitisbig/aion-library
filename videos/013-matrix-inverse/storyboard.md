# What Matrix Inverses Actually Mean: storyboard

**Status:** planning complete, waiting for approval before any scene code is written.

Audio: `assets/audio.wav` (10:07, 607.66 s, 1,717 words, 9,197 characters billed, −16.1 LUFS). Captions: `assets/subtitles.srt` (198 cues, up to two lines of 42 characters, broken at sentences and clauses).
Scene ranges below are the real cuts from `beats.py`. The full beat table is in `beats.md`. If `aion voice` is ever re-run, run `finish_audio.py` again afterward.

Alternative titles: *The Inverse Matrix, Visually Explained* · *Undoing a Transformation: The Inverse Matrix* · *How to Reverse Any Linear Transformation*

Files: `voiceover.md` (every spoken word) · `design.md` and `out/design/` (design sheet) · `theme.py` (colors) · `verify.py` (every number on screen; all checks pass) · `beats.py`, `beats.md` (timing) · `finish_audio.py` (cue repairs and subtitles).

## The spine
**An inverse is every thread of a move, walked backward. A way back exists exactly when the move forgot nothing.**

One object carries the whole video: a brass key with four teeth. It is bent and restored in the first thirty seconds. Then a
nearly identical matrix crushes it into a shadow, and sixteen different keys turn out to cast that same shadow. The video
explains why, and the finale does what the opening said could not be done from one shadow: it rebuilds the key from many.

**Not copying.** 3Blue1Brown's inverse-matrix chapter centers on solving systems, column space and null space. Our cast is the key and its
shadow, threads, row reduction as rewind-and-record, two powders, a game camera, a deblurred die and a CT reconstruction.

**Series continuity.** `A` is the hero matrix of 009. The determinant is 006's area factor. 009 said a shadow alone can't rebuild an object, and this video answers what happens with many shadows.

## Chapter structure
| chapter | question it answers | scenes | starts | length |
|---|---|---|---|---|
| Intro | Can a transformation be reversed? | s01–s03 | 0:00 | 1:20 |
| 1 · The way back | What exactly is an inverse? | s04–s07 | 1:20 | 1:39 |
| 2 · Rewind | How do you undo a chain of moves? | s08 | 2:59 | 0:32 |
| 3 · Finding the way back | How do you compute one? | s09–s12 | 3:32 | 1:36 |
| 4 · What can't come back | When does no inverse exist? | s13–s16 | 5:08 | 1:22 |
| 5 · Who landed here? | What does this have to do with equations? | s17–s19 | 6:31 | 1:09 |
| 6 · The way back at work | Where is it used? | s20–s23 | 7:41 | 1:16 |
| 7 · Shadows and outro | Can lost information ever return? | s24–s26 | 8:57 | 1:09 |

## Scene list
| scene | title | starts | length |
|---|---|---|---|
| `s01_cold_open` | Cold open: out and back | 0:00 | 29 s |
| `s02_the_crush` | The one that can't come back | 0:29 | 31 s |
| `s03_promise` | Why it matters, and the promise | 0:59 | 21 s |
| `s04_simple_moves` | Three easy ways back | 1:20 | 22 s |
| `s05_wrong_rule` | The tempting wrong rule | 1:42 | 26 s |
| `s06_threads` | Threads | 2:08 | 18 s |
| `s07_identity` | The identity, and both orders | 2:26 | 33 s |
| `s08_rewind` | Rewind | 2:59 | 33 s |
| `s09_four_moves` | Four moves home | 3:32 | 23 s |
| `s10_recording` | Rewind and record | 3:56 | 27 s |
| `s11_check` | Checking the answer | 4:22 | 15 s |
| `s12_det_emerges` | The determinant appears | 4:37 | 31 s |
| `s13_tilt` | Approaching collapse | 5:08 | 31 s |
| `s14_many_to_one` | Many points, one landing | 5:39 | 19 s |
| `s15_columns` | Reading it in the columns | 5:58 | 18 s |
| `s16_one_fact` | One fact, four sides | 6:15 | 15 s |
| `s17_powders` | Two powders | 6:31 | 28 s |
| `s18_solve` | Following the thread home | 6:59 | 19 s |
| `s19_weak` | No answer, or too many | 7:18 | 22 s |
| `s20_drone` | Two observers | 7:41 | 19 s |
| `s21_camera` | The game camera | 8:00 | 18 s |
| `s22_blur` | The blurred picture | 8:17 | 14 s |
| `s23_noise` | When an inverse is useless | 8:31 | 26 s |
| `s24_second_shadow` | A second shadow | 8:57 | 21 s |
| `s25_ct_reconstruct` | The key comes back | 9:18 | 24 s |
| `s26_outro` | What the move forgot | 9:43 | 25 s |

## Brief coverage
| required concept | where |
|---|---|
| Matrices as transformations of space | s01, s04 |
| What it means to undo a transformation | s04, s06 |
| Applying a matrix and its inverse, geometrically | s01, s06, s07 |
| The identity as the result of reversing | s07 |
| Deriving `A⁻¹A = AA⁻¹ = I` | s07 |
| Inverses through grids, vectors and objects | s01, s06, s09, s18 |
| Why some matrices have no inverse | s02, s13, s14 |
| Singular matrices, collapse, loss of information | s02, s13, s14 |
| Invertibility, determinants, linear independence | s12, s15, s16 |
| A complete numerical example, calculated and verified | s09–s11 |
| Inverses and systems of linear equations | s17–s19 |
| Computer graphics, coordinates, data recovery | s20, s21, s22–s23, s24–s25 |

**One deliberate change of order:** the worked example (Chapter 3) comes before singular matrices (Chapter 4). That way `1/det` emerges from the calculation, and dividing by zero becomes the question that opens the collapse.

## Promises tracked (playbook rule 18)
| promise | made | paid |
|---|---|---|
| Why can one matrix be undone and a near twin can't? | s03 | s13–s16 |
| "Rebuild this key from nothing but its shadows" | s03 | s24–s25 |
| Games, maps, equations and blurred pictures | s03 | s17–s23 |
| "Keep this nearly flat moment in mind" | s13 | s23 |
| The four opening moves were not arbitrary | s01 | s11 |

## Scenes

### Intro

#### `s01_cold_open` · Cold open: out and back · 0:00–0:29 (29 s)
- **Narrative purpose:** State the video's question inside ten seconds, and prove in one motion that a whole plane can be restored exactly.
- **Visual description:** Black. A blue grid draws outward from the origin and a brass key settles on it at a slight angle. The plane is picked up and bent by four moves in four directions until the key is a long warped sliver. Then one teal sweep carries every grid line and every tooth home onto a faint outline of where they began.
- **Rendering technology:** Manim through `s.manim()`: `grid_lines(M(t), ...)` in `m.redraw`, key polygons mapped by the same matrix Track, `Mat` for the entries. Matrix path is `key()` on `HOOK[0..3]` from `verify.py`.
- **Animation direction:** Grid draws in 1.0 s. Each of the four moves takes 1.1 s with `easy_ease`, landing on its spoken word. The return is a single straight matrix path from A to I over 2.0 s (it never passes through a singular matrix). `s.camera.push` to 1.1× during the return, then a 1.5 s hold.
- **On-screen elements:** `A` in coral with its columns in green and red, building one column at a time. `A⁻¹` in teal on "inverse". Faint outline of the original key. No words.
- **Narration:**

> Take a key, and lay it on a flat grid.
>
> Now pick up the whole plane. Lean it to one side. Pull it upward. Lean it again, and once more.
>
> Four moves, and together they make a single matrix.
>
> So here's the question. Can we put it back?
>
> We can. One more matrix, one smooth motion, and every point returns to exactly where it started. That second matrix is called the inverse.

#### `s02_the_crush` · The one that can't come back · 0:29–0:59 (31 s)
- **Narrative purpose:** Create the central tension: a nearly identical matrix destroys something for good.
- **Visual description:** `S` appears beside `A`, with only the second column changing. The plane folds onto one line and the key becomes a slate streak. A teal `S⁻¹` tries to write itself and fails. Two keys with different teeth appear, then all sixteen in a 4 × 4 grid, and threads from every one converge on the same streak.
- **Rendering technology:** Manim: `m.redraw` for the collapsing grid, a `VGroup` of 16 `key_polys` variants, thin `Line` threads drawn with `m.seq`.
- **Animation direction:** Collapse from I to S over 1.6 s with `easy_ease` and a push to 1.15×. Hold in silence on "Put this one back." Keys arrive with a 0.12 s stagger. Threads converge over 0.8 s.
- **On-screen elements:** `S` with its second column highlighted. `S⁻¹ = ?` in gray. Tags: `16 keys`, `1 shadow`.
- **Narration:**

> Now try a matrix that looks almost the same. Only its second column is different.
>
> The plane falls flat. The whole key is now a streak on a single line.
>
> Put this one back.
>
> There's nothing to hold on to. This streak could have come from this key. Or this one, with a tooth flipped. Four teeth, each pointing up or down: that's sixteen different keys, and all sixteen leave exactly the same mark.
>
> It's a shadow, and one shadow can't tell you which key cast it.

#### `s03_promise` · Why it matters, and the promise · 0:59–1:20 (21 s)
- **Narrative purpose:** Raise the stakes, preview the applications unexplained, and open the loop that the finale pays off.
- **Visual description:** Four quick framed vignettes: a game camera over a low-poly world, a drone over a map, a pair of equations, and a blurred die that snaps sharp. They shrink away and the streak returns. Pink rays begin to circle it, a hint of many shadows. The title resolves in small caps.
- **Rendering technology:** Manim panels with `panel()`; `FramesLayer` thumbnails reused from s21 and s22. Title with `\textsc`.
- **Animation direction:** Each vignette holds about 3 s and fades on with its word. Rays rotate slowly (6°/s) under the final sentence. Title fades in with `smooth` and holds 2 s.
- **On-screen elements:** Title: What Matrix Inverses Actually Mean. Nothing else.
- **Narration:**

> Why can one matrix be undone, when its near twin can't? The answer decides how a video game draws its world, how a drone reads a map, how a computer solves an equation, and whether a blurred picture can be made sharp again.
>
> And by the end, we'll do something that sounds impossible. We'll rebuild this key from nothing but its shadows.


### 1 · The way back

#### `s04_simple_moves` · Three easy ways back · 1:20–1:42 (22 s)
- **Narrative purpose:** Build intuition with moves whose undoing is obvious, and let the viewer predict each return.
- **Visual description:** A clean grid with î and ĵ. The plane turns and turns back, stretches and shrinks, and slides like a deck of cards and slides back. Each finished pair of matrices parks in a neat ledger on the left, coral above teal.
- **Rendering technology:** Manim: rotation interpolates the angle, the others interpolate entries. `Mat` pairs from `SIMPLE` in `verify.py`.
- **Animation direction:** Each move takes 1.4 s out, a 0.5 s pause to predict, then 1.4 s back with mirrored easing. The ledger entry slides in as the plane comes home.
- **On-screen elements:** Three matrix pairs. Tags: `turn`, `stretch`, `slide`.
- **Narration:**

> A matrix is a move. Its columns say where the two basic arrows land, and the rest of the plane follows them.
>
> Some moves are easy to undo. Turn the plane, and the way back turns it the same amount in the other direction. Stretch it, and the way back shrinks it. Slide each row sideways, like pushing a deck of cards, and the way back pushes the deck the other way.

#### `s05_wrong_rule` · The tempting wrong rule · 1:42–2:08 (26 s)
- **Narrative purpose:** Wrong intuition first: entry-by-entry thinking fails, which motivates thinking about the whole transformation.
- **Visual description:** The stretch pair enlarges and its entries flip to reciprocals. The rule is tested on the slide, where its zero becomes a gray `1/0`. Beside it, S shows four nonzero entries but cannot be undone. Results contradict the rule.
- **Rendering technology:** Manim `TransformMatchingTex` style moves on `Mat` cells, colored with `C.wrong`.
- **Animation direction:** Entries flip in place with a 0.08 s stagger. The failing `1/0` dims to gray. Both matrices hold side by side for 1.5 s.
- **On-screen elements:** `a → 1/a` in gray, `1/0`. Tags: `has a zero`, `undone`, `no zeros`, `stuck`.
- **Narration:**

> That stretch suggests a shortcut. Two became a half, and three became a third. So maybe you just flip every number upside down.
>
> But the sliding deck has a zero in it, and zero can't be flipped, yet we undid that move by changing a single sign. And the matrix that crushed our key has no zeros at all. So the numbers, read one at a time, won't tell us. We have to watch what the whole matrix does to space.

#### `s06_threads` · Threads · 2:08–2:26 (18 s)
- **Narrative purpose:** Give the video's core definition as a picture: an inverse is every thread reversed.
- **Visual description:** A single point travels and leaves a coral thread. Then a whole lattice does the same and the plane is woven with about 150 threads. Bright dashes run back along each thread as the web turns from coral to teal.
- **Rendering technology:** Manim `m.redraw` with batched `Line`s (skia `FramesLayer` as fallback if it renders slowly on this machine). Lattice and images computed from `A`.
- **Animation direction:** First thread takes 1.0 s alone. Web draws with a 15 ms stagger over 2 s. Color and dash direction reverse together over 1.5 s on "opposite direction".
- **On-screen elements:** Dots at each end of every thread. `x ⇄ Ax` once. No words.
- **Narration:**

> Follow one point as the plane moves, and draw a thread from where it started to where it landed. Now do the same for every other point.
>
> That web of threads is the move. The way back is the same web, walked in the opposite direction. That's what an inverse is. Every thread, reversed.

#### `s07_identity` · The identity, and both orders · 2:26–2:59 (33 s)
- **Narrative purpose:** Derive `A⁻¹A = AA⁻¹ = I` from the round trip.
- **Visual description:** The key rides out and back along the threads. The two moves merge into a single move that does nothing, and I writes itself with both basic arrows resting at home. The trip then runs in the other order from a bent starting point.
- **Rendering technology:** Manim: the equation assembles from the two matrix symbols that were doing the moving. `m.seq` for term reveals.
- **Animation direction:** Round trip 3 s. `A⁻¹` and `A` slide together and collapse into `I` with `spring`. Second order takes 3 s. A coral-then-teal arc under the product shows reading order.
- **On-screen elements:** `A⁻¹A = I`, then `AA⁻¹ = I`, merged into `A⁻¹A = AA⁻¹ = I`, which parks in the corner stack.
- **Narration:**

> Go out along the threads and come back, and every point ends up where it began. The round trip, taken as one move, does nothing at all.
>
> Doing nothing has a matrix too. Its columns leave both arrows at home. We call it the identity, and it behaves like the number one: multiply by it, and nothing changes.
>
> So the inverse is the matrix that, applied after A, leaves you with the identity. Take the way back first, and the threads haven't changed, so everyone still gets home. Either order gives the identity.


### 2 · Rewind

#### `s08_rewind` · Rewind · 2:59–3:32 (33 s)
- **Narrative purpose:** Show why inverses of a chain reverse order, and set up the method for finding any inverse.
- **Visual description:** The plane leans, then makes a quarter turn. A gray attempt undoes them in the wrong order and the grid ends visibly bent against the outline of home. A teal attempt undoes the last move first and everything snaps into place. Three film frames slide past in reverse.
- **Rendering technology:** Manim, two passes over the same matrices `LEAN` and `TURN`. Wrong result is computed: `[[1, 1], [1, 2]]`.
- **Animation direction:** Each step 1.2 s. The wrong ending holds for 1.0 s. Film frames translate right to left during the last sentence with `s.camera.pan`.
- **On-screen elements:** `(TL)⁻¹ = L⁻¹T⁻¹`, with the swap animated. Tags: `lean`, `turn`.
- **Narration:**

> Most moves come in stages. Say we lean the plane, then give it a quarter turn. How do we get back?
>
> Undo the lean, then undo the turn, and the grid doesn't come home. The turn happened last, so it has to come off first. Undo the turn, then the lean, and everything lines up.
>
> It works like a film played backward. The inverse of a chain is the inverse of each link, in reverse order. So if a complicated move can be broken into simple ones, we can rewind it, one simple move at a time.


### 3 · Finding the way back

#### `s09_four_moves` · Four moves home · 3:32–3:56 (23 s)
- **Narrative purpose:** The worked example, geometrically: restate the goal, then make each step visible and exact.
- **Visual description:** The bent plane from s01 returns exactly, with faint outlines marking home at (1, 0) and (0, 1). Step by step the arrows return. î goes (3, 2) → (1, 2) → (1, 0). ĵ goes (1, 2) → (−1, 2) → (−1, 4) → (−1, 1) → (0, 1). The key unbends with the plane. Four dots count the steps.
- **Rendering technology:** Manim, with `E` from `verify.py` applied cumulatively as a matrix Track.
- **Animation direction:** Each move takes 1.4 s and lands on its phrase, followed by a 0.4 s rest. A home arrow flashes warm white on arrival.
- **On-screen elements:** `A`, then elementary matrices stacking up as they are used. Tags: `slide`, `slide`, `squash`, `slide`. Step dots.
- **Narration:**

> Let's do that for the matrix that bent our key, using only slides and stretches.
>
> The first slide pulls one arrow upright. A second slide drops it onto the axis, exactly where it belongs.
>
> The other arrow is standing four times too tall, so we squash the plane to a quarter of its height.
>
> One last slide straightens it. Four moves, and the key is home.

#### `s10_recording` · Rewind and record · 3:56–4:22 (27 s)
- **Narrative purpose:** Reveal what row reduction means: the same moves applied to a fresh grid record the inverse.
- **Visual description:** Two framed grids side by side. The left starts bent and straightens. The right starts straight and bends, move for move. Beneath them is the augmented matrix, with each half directly under its grid, updating through all four states.
- **Rendering technology:** Manim: `panel()`, `grid_lines` clipped per panel, `Mat` with fixed cells. Right-hand values: `[[1, −1], [0, 1]]`, `[[1, −1], [−2, 3]]`, `[[1, −1], [−½, ¾]]`, `[[½, −¼], [−½, ¾]]`.
- **Animation direction:** The four moves run in sync, 1.2 s each, with entries ticking. Final state holds 2 s. `s.camera.pan` centers the divider.
- **On-screen elements:** `[A | I] → [I | A⁻¹]`. Tags: `rewinds`, `records`.
- **Narration:**

> But we never wrote the inverse down as a single matrix. So let's play the same four moves on a second grid, one that starts untouched. As the bent grid straightens out, the straight grid bends, keeping a record of every step.
>
> When the first grid reaches the identity, the second has become the inverse.
>
> If you've learned row reduction, those two blocks of numbers side by side are these two grids. One rewinds, and the other records.

#### `s11_check` · Checking the answer · 4:22–4:37 (15 s)
- **Narrative purpose:** Verify by arithmetic and by geometry, then pay off the four moves from the opening.
- **Visual description:** The product is computed cell by cell, fractions cancelling to ones and zeros. The key goes out through A and back through A⁻¹. Then frames from s01 and s09 line up in two rows, mirror images of each other.
- **Rendering technology:** Manim: `Mat` cells with a highlighted row and column per product. Thumbnails rebuilt as live grids in `panel()`.
- **Animation direction:** Each entry resolves over 0.7 s. Round trip 2.5 s. The two strips slide into alignment over 1.5 s.
- **On-screen elements:** `½·3 − ¼·2 = 1` and its three siblings, shown one at a time. `A⁻¹A = I` in place.
- **Narration:**

> Let's check it. Multiply the inverse by the original, and the fractions cancel, leaving ones on the diagonal and zeros everywhere else.
>
> You may also recognize those four moves. They're the same four that bent the key at the start, played backward.

#### `s12_det_emerges` · The determinant appears · 4:37–5:08 (31 s)
- **Narrative purpose:** Show that 1/det is forced by geometry, then derive the 2 × 2 formula and open the question of zero.
- **Visual description:** A violet unit patch rides through the four moves. Its area reading stays constant through each slide and drops at the squash. `det A = 4` lands. The numbers then morph into letters: two entries swap, two negate, and `1/(ad − bc)` slides in.
- **Rendering technology:** Manim: patch mapped by the cumulative matrix, area computed live. The formula is built with `TransformMatchingTex`.
- **Animation direction:** Patch moves replay at double speed. Push to 1.1× on the squash. Swap and negate each take 0.8 s. The denominator pulses once on the last sentence.
- **On-screen elements:** Area readout. `det A = 4`. `A⁻¹ = 1/(ad − bc) [[d, −b], [−c, a]]`. Then `ad − bc = 0 ?`.
- **Narration:**

> And there's something hiding in that list. A slide never changes area. So all of the shrinking came from that single squash, down to a quarter.
>
> Four is exactly how much the original matrix grew every area. It's the determinant.
>
> Run the same steps with letters in place of numbers, and out comes the recipe for any two by two matrix. Swap these two, negate those two, and divide by the determinant.
>
> Which should make you a little uneasy. What happens when there's nothing to divide by?


### 4 · What can't come back

#### `s13_tilt` · Approaching collapse · 5:08–5:39 (31 s)
- **Narrative purpose:** Mid-video re-hook: watch the inverse blow up in real time as the plane thins, and plant the nearly flat moment that pays off in s23.
- **Visual description:** Two panels. On the left the second column tilts toward the first and the plane thins. On the right the inverse's grid stretches violently out of frame. Readouts climb through ×10, ×100, ×1000, and the tilt pauses there, nearly flat. At the moment of alignment the left is a line and the right has nothing left to show.
- **Rendering technology:** Manim with `tilt(s)` from `verify.py`. `s` is keyed so ×10 (s = 0.8991), ×100 (0.9899), ×1000 (0.9990) land on their spoken words. Stretch is 1/σ_min.
- **Animation direction:** A slow, accelerating approach. Readouts tick live in fixed-width cells. The tilt holds still on "Keep this nearly flat moment in mind." The last step arrives in 0.5 s and is followed by a 1.5 s hold.
- **On-screen elements:** `det` in violet, falling to 0. `×10`, `×100`, `×1000`, then `∞`.
- **Narration:**

> Take our matrix, and slowly tilt its second column toward the first. The plane grows thinner, the determinant falls, and the inverse has to work harder. To reopen a plane this thin, it has to stretch by a factor of ten. Then a hundred. Then a thousand.
>
> Keep this nearly flat moment in mind. It's going to matter.
>
> When the two columns finally line up, the plane is flat, the determinant is zero, and the inverse has run off to infinity.

#### `s14_many_to_one` · Many points, one landing · 5:39–5:58 (19 s)
- **Narrative purpose:** Explain geometrically why no inverse can exist: one output would need many answers.
- **Visual description:** The camera dollies to one spot on the line. A pink line of source points lights up and threads fan in from it to the spot. Teal arrows then try to fan back out, one input to many outputs, and dim to gray.
- **Rendering technology:** Manim. Source line is `p + t·(1, −2)`. Landing spot is `S p`. Rays never touch the spot directly (see design sheet, section 4).
- **Animation direction:** `s.camera.push` to 2× over 2.5 s. Fan draws over 1.0 s. Failed reverse fan takes 1.0 s and dims.
- **On-screen elements:** A single spot. Tag: `many to one`.
- **Narration:**

> Pick one spot on the line, and ask which points landed there. The threads come in from an entire line of points. These are the rays that cast our shadow.
>
> A way back would have to send this one spot to all of those points at once, and a matrix gives each input just one answer.

#### `s15_columns` · Reading it in the columns · 5:58–6:15 (18 s)
- **Narrative purpose:** Connect collapse to linear dependence, and find the crushed direction in the matrix itself.
- **Visual description:** The two column arrows of S lie along one line. The second doubled equals the first. Tip to tail, one of the first and minus two of the second walk out and return to the origin. That recipe appears as the pink vector (1, −2).
- **Rendering technology:** Manim, using the same arrows as s09, recolored per the column roles.
- **Animation direction:** Tip-to-tail walk takes 2.0 s. The recipe's coefficients lift out of the sum and become the arrow's coordinates.
- **On-screen elements:** `c₁ = 2c₂`, `1·c₁ − 2·c₂ = 0`, `S(1, −2) = 0`. Tag: `linearly dependent`.
- **Narration:**

> You can read this in the columns. Here, the first column is exactly twice the second, so the second adds nothing new. We say the columns are linearly dependent. And that relationship is the crushed arrow itself: one of the first, minus two of the second, makes nothing.

#### `s16_one_fact` · One fact, four sides · 6:15–6:31 (15 s)
- **Narrative purpose:** Unify invertibility, determinant, independence and null direction into one statement.
- **Visual description:** Four small framed diagrams driven by a single tilt control: columns, area, a surviving arrow, and a round trip. As the tilt crosses the critical value, all four fail at the same instant. It rocks back and they all recover together.
- **Rendering technology:** Manim with four `panel()` views sharing one Track for `s`.
- **Animation direction:** The control sweeps 0.8 → 1 → 0.8 over 4 s. Each panel lights on its spoken phrase first. The failure lands on one frame in all panels.
- **On-screen elements:** Tags: `columns`, `area`, `direction`, `way back`. `⇔` between neighbours.
- **Narration:**

> So these are one fact, seen from four sides. The columns depend on each other. The area drops to zero. A whole direction disappears. And there is no way back. If any one of these is true, all of them are.


### 5 · Who landed here?

#### `s17_powders` · Two powders · 6:31–6:59 (28 s)
- **Narrative purpose:** Ground linear systems in a concrete question that runs forward easily and backward with difficulty.
- **Visual description:** Two line-art scoops, each with a small bar pair for protein and fibre. Their bars become the two column arrows on a plane with labelled axes. Scoops combine tip to tail. A yellow target appears at (7, 6).
- **Rendering technology:** Manim: icons of 12 strokes or fewer, drawn with `Create`. Columns reuse î and ĵ colors.
- **Animation direction:** Icons draw over 0.8 s. Each column grows from its bars. The target lands on "How many scoops is that?" with a held silence.
- **On-screen elements:** Tags: `protein`, `fibre`. The matrix of columns. `b = (7, 6)`.
- **Narration:**

> Undoing a matrix is also what it means to solve an equation.
>
> Say you're mixing two powders. A scoop of the first has three grams of protein and two of fibre. A scoop of the second has one of protein and two of fibre. Those are the columns of our matrix. Give it a number of scoops, and it tells you what you get.
>
> Usually, though, the question runs the other way. You need seven grams of protein and six of fibre. How many scoops is that?

#### `s18_solve` · Following the thread home · 6:59–7:18 (19 s)
- **Narrative purpose:** Connect `Ax = b` to the inverse: solving means asking who landed here.
- **Visual description:** Two panels: scoops on the left, nutrients on the right. A teal thread runs from the target back to the point (2, 1). The two scoop arrows confirm the answer tip to tail on the right.
- **Rendering technology:** Manim with `POWDER`, `TARGET`, `SCOOPS` from `verify.py`.
- **Animation direction:** Equations write 1.5 s. Thread draws back over 1.5 s on "follow its thread home". Answer holds 1.5 s.
- **On-screen elements:** `3x + y = 7`, `2x + 2y = 6`, `x = A⁻¹b`, `x = (2, 1)`.
- **Narration:**

> Geometrically, that asks which point landed on this target. And we know the way back. Apply the inverse, follow the thread home, and there's the answer: two scoops of the first, one of the second.
>
> Every linear system asks the same thing. You know where something ended up, and you want to know where it started.

#### `s19_weak` · No answer, or too many · 7:18–7:41 (22 s)
- **Narrative purpose:** Show the two failure modes of a singular system as direct results of collapse.
- **Visual description:** The second powder's arrow shrinks onto the first, and the reachable plane becomes one line, the same S as the opening. A target off the line has no path to it. A target at (6, 4) lights up three different recipes: (2, 0), (1, 2), and (0, 4).
- **Rendering technology:** Manim, using the collapse animation from s13.
- **Animation direction:** Collapse 1.5 s. Failed path fades after 1.0 s. Recipes draw one after another, 0.8 s each.
- **On-screen elements:** Tags: `no recipe`, `endless recipes`.
- **Narration:**

> Now swap in a second powder that's exactly half as strong as the first. Every mix you can make falls on a single line. Ask for something off that line, and no recipe exists. Ask for something on it, and there are endless recipes.
>
> No answer, or too many. Those are the two ways a system fails, and both are the collapse we just saw.


### 6 · The way back at work

#### `s20_drone` · Two observers · 7:41–8:00 (19 s)
- **Narrative purpose:** Coordinate systems: the same point has different names, and an inverse translates between them.
- **Visual description:** A map grid in blue. A drone hovers above with its own sky-blue grid, turned and scaled. A yellow landmark carries two readouts: (2, 1) in the drone's steps and (3, 4) on the map. Coral and teal arrows translate between them.
- **Rendering technology:** Manim with `DRONE`, `SEEN`, `MAPPED` from `verify.py`. Drone is simple line art.
- **Animation direction:** Drone grid unfolds from the drone over 1.5 s. Readouts write in turn. Each translation arrow travels 1.0 s.
- **On-screen elements:** `D`, `D⁻¹`, `(2, 1)`, `(3, 4)`.
- **Narration:**

> Two observers can describe the same place in different ways. To a drone with its own tilted grid, this landmark is two steps ahead and one to the side. The matrix built from the drone's axes translates that onto the map, and its inverse translates the map back into the drone's point of view.

#### `s21_camera` · The game camera · 8:00–8:17 (18 s)
- **Narrative purpose:** Computer graphics: rendering the world through a camera is applying an inverse.
- **Visual description:** A low-poly town of about 20 flat-shaded blocks in two panels: an outside view with a camera glyph, and the camera's own view. The camera walks forward. Then the outside view locks to the camera, and the whole town visibly slides backward past a motionless camera.
- **Rendering technology:** skia-python → `FramesLayer`, numpy 4 × 4 matrices, painter's-order flat shading with 1 px edges.
- **Animation direction:** Walk forward 3 s at constant speed. Frame-lock switch eases over 1.0 s, then the same walk replays.
- **On-screen elements:** `C` on the camera, `C⁻¹` on the world.
- **Narration:**

> A video game does this for every frame. The camera is placed in the world by a matrix, and to find out what it sees, the game applies the inverse of that matrix to everything else. As far as the computer is concerned, you never walk forward. The world gets carried backward, past you.

#### `s22_blur` · The blurred picture · 8:17–8:31 (14 s)
- **Narrative purpose:** Data recovery: blur is a matrix and, here, an invertible one.
- **Visual description:** A sharp die smears sideways. A zoom onto one row of pixels shows each output pixel averaging its neighbours, and a heatmap of the banded matrix appears. The inverse is applied and every edge returns.
- **Rendering technology:** numpy FFT of the 49-pixel box blur on `009/assets/photo.png` → `FramesLayer`. Matrix heatmap via `FieldLayer`.
- **Animation direction:** Smear builds over 1.5 s by growing the blur length. Inverse snap takes 1.2 s, with a 1.5 s hold on the sharp frame.
- **On-screen elements:** Heatmaps labelled `A` and `A⁻¹`. No other text.
- **Narration:**

> Now here's a picture, smeared by a shaking camera. Each blurred pixel is an average of its neighbours, and averages are exactly what a matrix computes. This blur has an inverse. Apply it, and every edge comes back.

#### `s23_noise` · When an inverse is useless · 8:31–8:57 (26 s)
- **Narrative purpose:** Pay off the near-flat plant: conditioning matters, and existence alone isn't enough.
- **Visual description:** The blurred frame gains noise too faint to see. The inverse buries the die in pink static. A bar chart of how much each direction was squeezed shows the tiny bars responsible. A cutoff line rises, the worst directions are dropped, and a clean die emerges.
- **Rendering technology:** Baked numpy frames, noise σ = 1 of 255 grey levels, seed 13. Chart from the real blur spectrum. Cutoff `BLUR_KEEP` = 0.06.
- **Animation direction:** Noise is added with no visible change. Result reveals over 1.2 s. Cutoff rises over 2 s while the picture updates live.
- **On-screen elements:** Chart with a `cutoff` tag. Static in `C.null`.
- **Narration:**

> But remember that nearly flat plane. Blur squeezes the finest detail almost to nothing, so the inverse has to stretch it by an enormous amount. Add a trace of noise, too faint to see, and it gets stretched too, until the picture is buried.
>
> So a matrix can have an inverse, and that inverse can still be useless. Real deblurring stops short, and undoes only the directions that survived.


### 7 · Shadows and outro

#### `s24_second_shadow` · A second shadow · 8:57–9:18 (21 s)
- **Narrative purpose:** Reopen the question from s02 and show how a new measurement separates what one shadow merged.
- **Visual description:** The key returns at center with a thin detector strip. Pink beams pass through it, recording a shaded shadow. A flipped tooth leaves that shadow unchanged. The light turns, a second strip records, and now the two teeth cast visibly different shadows.
- **Rendering technology:** `shaders/beam.frag` for the beams; profiles from `ct_matrix` in `verify.py`. Manim for strips and labels.
- **Animation direction:** Beam sweeps across over 1.5 s. Tooth flips back and forth twice. The light rotates 40° over 2 s with `easy_ease`.
- **On-screen elements:** Tag: `1 shadow`, then `2 shadows`.
- **Narration:**

> Which brings us back to the key, and the shadow we couldn't undo.
>
> From one shadow, that's still true. But nothing stops us from taking another. Turn the light, and a tooth that could have pointed either way now falls in a different place. Each new shadow adds new equations, and fewer and fewer keys can fit them all.

#### `s25_ct_reconstruct` · The key comes back · 9:18–9:43 (24 s)
- **Narrative purpose:** The big payoff: enough shadows make the combined matrix invertible, and the key is rebuilt.
- **Visual description:** A ring of shadow strips multiplies around a dark center. At the center a real reconstruction sharpens through 2, 4, 8, 16, 32, 64 and 128 angles: streaks, then a blur, then an outline, then the key with every tooth in place. A line-art CT scanner ring closes around it.
- **Rendering technology:** Baked `lsqr` reconstructions on a 96 × 96 grid → `FramesLayer` (error falls from 85% to 0.3%). Ring of strips in Manim.
- **Animation direction:** The angle count ticks up on the beat. Crossfades of 0.6 s between solved frames. Push to 1.2× and hold 2 s on the finished key.
- **On-screen elements:** Counter in `C.data`: 2, 4, 16, 128. Nothing else.
- **Narration:**

> Two shadows. Four. Sixteen. A blur at first, then an outline. With enough angles, the combined matrix no longer forgets anything, and here's the key, teeth and all, rebuilt from shadows alone.
>
> This is how a CT scanner sees inside your body. It records shadows from hundreds of angles, then solves for what must have cast them.

#### `s26_outro` · What the move forgot · 9:43–10:07 (25 s)
- **Narrative purpose:** End on the idea rather than a recap, and close the visual loop.
- **Visual description:** A bent plane returns home along teal threads. A crushed plane stays flat, with pink rays. Light circles once more. Everything clears until the key rests on the grid exactly as in the first frame of the video.
- **Rendering technology:** Manim, rebuilding the s01 opening frame exactly. End screen panels for the 006 and 009 videos are added in the 3 s tail.
- **Animation direction:** Slow, unhurried moves of 2.5 s each. The final frame matches frame one and holds through the tail.
- **On-screen elements:** No equations. The last image is the key.
- **Narration:**

> Every matrix moves space. The inverse asks what that move forgot.
>
> If it forgot nothing, every point still has a thread leading back to where it began, and the way home exists. If it forgot something, that part is gone, and no amount of algebra will bring it back. All you can do is go and look again, from somewhere new.
