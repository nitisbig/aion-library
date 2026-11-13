# Why e^(iπ) = −1, Explained Visually: storyboard

Audio: `assets/audio.wav` (605.14 s = 10:05, 1,632 words, about 162 words a minute, voice speed 0.92)

Pacing (`voice.toml [pacing]`): 1.5 s lead-in, +0.5 s after each paragraph, +1.5 s between chapters, 3.0 s tail,
3 s held pause after the intro map, 2 s pause-and-predict pause in Ch3.
Captions for YouTube: `assets/subtitles.srt` (296 cues, ≤ 42 chars, balanced splits). Full beat table at the end.

Structure: intro, six chapters, outro. Fourteen scene files.

| # | scene | chapter | range | length | mode |
|---|---|---|---|---|---|
| 0 | `s00_hook` | Intro: the equation, the wrong intuition | 0:00–0:41 | 41 s | cinematic hook |
| 1 | `s00b_preview` | Intro: preview montage + map | 0:41–1:09 | 28 s | hero preview (domain coloring) |
| 2 | `s01_bank` | Ch1 What e really is | 1:09–1:51 | 42 s | concrete example → limit |
| 3 | `s02_growth` | Ch1 (cont.) velocity = position | 1:51–2:27 | 36 s | graph → motion |
| 4 | `s03_actions` | Ch2 What i really does | 2:27–3:01 | 35 s | number line, plant "−1 = half turn" |
| 5 | `s04_quarter` | Ch2 (cont.) the quarter turn | 3:01–3:44 | 43 s | line → plane, plane rotation |
| 6 | `s05_sideways` | Ch3 Growth turned sideways | 3:44–4:59 | 75 s | the core; flow field |
| 7 | `s06_walk_pi` | Ch3 (cont.) predict → payoff → re-hook | 4:59–5:39 | 40 s | pause-and-predict, midpoint payoff |
| 8 | `s07_compound_turn` | Ch4 Compounding a turn | 5:39–6:44 | 65 s | check 1: (1 + iπ/n)ⁿ |
| 9 | `s08_series` | Ch5 The infinite sum | 6:44–7:55 | 71 s | check 2: arrow spiral |
| 10 | `s09_formula` | Ch6 Euler's formula | 7:55–8:14 | 19 s | projections |
| 11 | `s10_helix` | Ch6 (cont.) the helix | 8:14–8:41 | 27 s | 2D → 3D |
| 12 | `s11_identity` | Ch6 (cont.) special values, the plane turns | 8:41–9:17 | 36 s | hero callback, e^{iπ} + 1 = 0 |
| 13 | `s12_outro` | Outro: lesson recap → payoff → next | 9:17–10:05 | 48 s | recap via badges |

## The story spine
"e is growth, i is turning, π is a distance." Each chapter adds one word of that sentence, and the main payoff
lands at the midpoint (4:59–5:39). Ch4 and Ch5 are two arithmetic checks that reach the same −1. Ch6
generalises to every angle.

## Running numbers (all computed with numpy at build time, never typed)

| use | value | where |
|---|---|---|
| compounding (1 + 1/n)ⁿ | n = 1, 2, 4, 12, 365 → 2, 2.25, 2.4414, 2.6130, 2.7146 → e = 2.71828… | Ch1 |
| compounding a turn (1 + iπ/n)ⁿ | n = 1 → 1 + 3.14i; n = 2 → −1.47 + 3.14i; n = 4, 8, 16, 100 → −1 | Ch4 |
| total turn n·atan(π/n) | n = 2 → 2.008 rad … → π | Ch4 |
| series terms (iπ)ⁿ/n! | magnitudes 1, 3.14, 4.93, 5.17, 4.06, 2.55, 1.34, 0.60, 0.24 … | Ch5 |
| special values | e^{iπ/2} = i, e^{iπ} = −1, e^{2πi} = 1 | Ch6 |

## Visual system

Design: **Classic** (the BASE default). Pure black, crisp unglowed lines, a bright blue integer grid over a dim minor
grid, white axes, Computer Modern for all text. No bloom, glow, blur, vignette or grain.

| object | color token | meaning |
|---|---|---|
| e, money, e^t, ordinary growth | `C.growth` (gold) | growth whose rate equals its size |
| i, rotation arcs, quarter-turn marks | `C.turn` (red) | a quarter turn |
| π, θ, distance walked | `C.arc` (green) | a distance along the circle |
| the moving point e^{iθ}, its position arrow, −1 | `C.point` (yellow) | where you are |
| the velocity arrow | `C.vel` (pink) | where you're going |
| horizontal parts (series steps, cos, cosine wave) | `C.cos` (teal) | real part |
| vertical parts (series steps, sin, sine wave) | `C.sin` (purple) | imaginary part |
| grid / original grid left behind / panel borders | `C.grid` `C.grid_minor` `C.axis` `C.ghost` `C.frame` | the stage |

Rules for every scene:
- One focal point per frame, at most three things moving. Symbols, equations and numbers only, with no caption text.
- Equations through `Eqn(tex, colors=...)`: e gold, i red, π/θ green, −1 yellow. Each term builds on the word that names it.
- Progress rail, bottom-left: six ticks, one per chapter. Badges stay for the rest of the video:
  `v = x` → `×i = ↺90°` → `v = ix` → `(1+iπ/n)ⁿ` → `Σ` → `cos + i sin`. Ch3 adds two empty "check" slots that Ch4
  and Ch5 tick. The outro gathers the badges.
- Transform, don't cut: the Ch1 number-line point returns in Ch3, the Ch1 staircase morphs into the Ch4 chain, the
  Ch2 half-turn glyph pays off in Ch3, and the intro's "half turn of the whole plane" pays off in s11.
- Motion: `easy_ease` for camera, `smooth` for motion, `out_back` for label pops, `spring` for badge drops.
  Fading ghost copies stand in for motion blur.
- Shared helpers (rail, badges, `panel`, readouts, arrow chains) go in `shots.py`, using 006's `shots.py` as the pattern.

### Engines
| engine | used for |
|---|---|
| Manim (ManimLayer) | equations, graphs, number line, complex plane, arrow chains, circle walk, the 3D helix as crisp vector lines through an orthographic az/el projection (pattern: `006/scenes/s06_three_d.py`) |
| ModernGL | GPU compositing, the 2.5D camera, `aion/shaders/layers/domain_coloring.frag` (its `u_theta` = multiplying by e^{iθ}) in s00b, s04 and s11 |
| GPU `PointsLayer` | s05 flow field, ~6k points under dz/dt = a·z, exact positions z₀·e^{∫a dt} (numpy) |
| skia-python → `ArrayLayer` | one static long-exposure image of the circular streamlines (s05, reused as the outro badge) |
| Taichi / pyvista | not used. Every motion has a closed form, and the only 3D object is one curve. (A pyvista lit-tube helix would need an animated-array layer added to aion first.) |

## Retention plan

| device | where |
|---|---|
| Promise in 10 s | `eq` (0:01) the equation is the first line |
| Wrong intuition first | `times` (0:30) "multiply e by itself i pi times?" |
| Preview the result, unexplained | `growth` → `lands` (0:41–0:51), hero shot over the turning colored plane |
| Map in one sentence | `dollar` → `half_plane` (0:59–1:02) |
| Plant → payoff | `plant` (2:58) "Negative one is a half turn" → `half_pay` (5:27) and the outro |
| Change one word | `one_word` (2:24) → `picks` (3:54) "the rule picks up a single i" |
| Pause and predict | `how_far` (5:09), 2.9 s of silence before `halfway` (5:14) |
| Midpoint re-hook | `fool` (5:34) "a picture can fool you… check it twice" |
| Mode switches | preview → graph → number line → plane → flow field → circle walk → chains → series → projections → 3D → domain coloring |
| Close each chapter visually | badge drops at each chapter end |
| End on the payoff | `o_half_turn` (9:53) "A half turn." then one line to the next video |

## Scenes

### s00_hook · T.start → T.cut_preview (0:00–0:41, 41 s)
- **Narration:** "e to the i pi equals negative one… plus one, equals zero… Five of the most important numbers… most
  beautiful equation… read it slowly… two point seven… multiply e by itself i pi times? An imaginary number of
  times?… a clever trick… It is not. It is a picture."
- **Visual idea:** black. e^{iπ} = −1 writes on symbol by symbol in large CM type, each symbol colored as it's spoken.
  On `plus_one` the −1 slides across the "=" (TransformMatchingTex) to become "+1 = 0". On `five` the five constants
  pulse in turn. On `slowly` the formula greys out. On `two_seven` the e unrolls into `2.71828…`. On `power` a chain
  `e · e · e` assembles. On `times` a counter under it reads `iπ ?`. On `imaginary` the chain stalls and its links
  drift apart, eased and staggered. On `trick` the frame clears. On `picture` the white unit circle draws on with one
  yellow point at 1.
- **Why it explains:** it names the confusion everyone has (exponent = repeated multiplication) before replacing it.
- **Beats:** `eq` `neg1` `another` `plus_one` `five` `beautiful` `slowly` `two_seven` `power` `times` `imaginary` `trick` `not_` `picture`
- **In / out:** fade up from black. Out: the circle and point stay and become the hero shot in s00b.
- **Layers:** manim (Eqn, TransformMatchingTex, redraw counter) · camera push on the equation.

### s00b_preview · T.cut_preview → T.cut_ch1 (0:41–1:09, 28 s)
- **Narration:** "e is a story about growth. i is a story about turning. And pi is a distance. Put them together…
  walking around a circle… lands exactly on negative one. By the end… You will see it. We will start with one
  dollar in a bank, and end with a half turn of the whole plane." (then a 3 s held pause)
- **Visual idea:** three match-cut shots, each landing on its word. `growth`: a gold e^t curve rises with a tangent
  riding it. `turning`: the grid turns a quarter turn about 0 and a red arc carries 1 → i. `distance`: a green arc
  measures along the circle. `together` brings the **hero shot**: the domain-colored plane fades in under a ghost
  grid, the yellow point walks the circle leaving a green arc, and the camera pushes in. On `lands` the point
  reaches −1 just as the color wheel finishes its half turn, and the equation snaps in beneath. On `by_end` the hero
  shrinks into the last tile of a **3 × 2 chapter-preview grid** (`tiles.py`) while the other five tiles arrive,
  each playing its chapter's key picture live: compounding staircases settling on e^t under a ceiling e; the 3D
  plane (`plane3d.frag`, clipped) with an arrow turning by quarter turns; x and v = ix at a right angle in a
  circling field; the chain (1 + iπ/n)^n closing on −1; the series (iπ)^n/n! spiralling onto −1. Each tile has a
  small number and title. e^{iπ} = −1 rises to a header and pulses on `see_it`. On `dollar` tile 1 lights and $1
  drops in; a light sweeps 1 → 6 and on `half_plane` tile 6's plane turns another half turn. In the held pause
  every tile flies into its progress-rail tick.
- **Beats:** `growth` `turning` `distance` `together` `walking` `lands` `by_end` `see_it` `dollar` `half_plane`
- **In / out:** in from s00's circle. Out: the grid collapses into the six rail ticks; the header fades to black.
- **Layers:** shader `domain_coloring.frag` (`u_theta=key(...)`, low saturation) · manim · 2.5D camera.

### s01_bank · T.cut_ch1 → T.cut_growth (1:09–1:51, 42 s) — Ch1 What e really is
- **Narration:** "Not a decimal. A kind of growth. Imagine a bank… one hundred percent… after a year, you have two…
  half that interest every six months… two twenty five… four times a year, two forty four… every month, two
  sixty one… every single day, two seventy one… does not run off to infinity… Two point seven one eight. That
  number is e."
- **Visual idea:** axes (t in years, money). On `put_in`/`have_two` a gold staircase for n = 1 makes one step from 1
  to 2. On `half`/`six_months`/`interest_on`/`v225` the n = 2 staircase appears, its second step visibly taller.
  On `four`, `month` and `day` the staircase gets finer and morphs toward a smooth curve, while the readout
  `(1 + 1/n)ⁿ` counts. On `finer`/`infinity` a framed magnifier panel shows a number line where the values pile up
  against 2.71828…. On `is_e` a gold **e** lands, and `e = lim (1 + 1/n)ⁿ` builds term by term.
- **Beats:** `real_e` `decimal` `kind` `bank` `put_in` `have_two` `half` `six_months` `interest_on` `v225` `four` `v244` `month` `day` `finer` `infinity` `settles` `v2718` `is_e`
- **Layers:** manim (Axes, staircase redraw with n stepped on beats) · camera pan to the magnifier.

### s02_growth · T.cut_growth → T.cut_ch2 (1:51–2:27, 36 s)
- **Narration:** "paid continuously… a rate equal to the money you have. Hold one dollar… Hold two… Draw it as a graph,
  e to the t… the slope of the curve equals its height. Or picture it as motion… a point on a line, whose
  velocity is always equal to its position… the faster it runs. Velocity equals position… we are about to
  change just one word of it."
- **Visual idea:** the staircase relaxes into the e^t curve. On `hold1`/`hold2` small gold rate arrows sit at heights
  1 and 2. On `slope`/`height` a tangent line rides the curve with a slope triangle while two readouts tick in
  lockstep. On `motion` the height bar rotates down onto a horizontal number line. On `pt_line`/`vel_pos` a gold
  point carries a pink velocity arrow with length equal to its position, accelerating and leaving fading ghost
  copies. On `v_eq_x` the equation `v = x` writes on. On `one_word` a red **i** hovers above the "=", and the badge
  `v = x` drops onto the rail.
- **Beats:** `special` `continuously` `rate_eq` `hold1` `hold2` `graph` `et` `slope` `height` `motion` `pt_line` `vel_pos` `faster` `sentence` `v_eq_x` `heart` `one_word`
- **Layers:** manim (drive/redraw, ghost trail).

### s03_actions · T.cut_ch2 → T.cut_quarter (2:27–3:01, 35 s) — Ch2 What i really does
- **Narration:** "Now for i… cannot exist… think of numbers as actions. Lay every number out on a line. Multiplying by two
  is an action. It stretches… by one half squeezes… by negative one? Three goes to negative three. Negative two goes
  to two… swings to the other side of zero. It is a half turn. Remember that. Negative one is a half turn. It is
  going to matter."
- **Visual idea:** a red **i** sits alone, then dissolves. On `line` a number line appears with dots at −3…3. On
  `stretches` the ×2 stretch plays (ApplyFunction) and on `half_sq` the ×½ squeeze. On `neg`, `three` and `neg2` the
  ×(−1) step **rotates through the plane**: the line swings 180° about 0 while each dot traces a dashed red
  semicircle, and the 3 and the −2 are highlighted on their words. On `plant` a half-turn glyph settles top-right
  and stays.
- **Beats:** `now_i` `cannot` `actions` `line` `times2` `stretches` `half_sq` `neg` `three` `neg2` `swings` `half_turn` `remember` `plant` `matter`
- **Layers:** manim.

### s04_quarter · T.cut_quarter → T.cut_ch3 (3:01–3:44, 43 s)
- **Narration:** "What action, done twice, gives a half turn? Not a stretch… only stretch further. But a quarter turn,
  done twice… let the line become a plane… i is the quarter turn. One goes to i… i goes to negative one…
  negative i, and then back to one. i times i is negative one… two quarter turns make a half turn… multiplying
  by i turns the whole plane… rotated ninety degrees."
- **Visual idea:** `? · ? = −1`. On `not_stretch`/`further` two stretches are tried and the line only gets longer.
  On `quarter` a 90° turn, done twice, raises the line vertical and then lays it flat, reversed. On `plane` the
  flat number line tilts away into a **3D perspective plane** that unrolls outward from 0 (grid first, then the
  color wheel), fading toward the horizon; the camera keeps drifting slowly round it. Arrows float just above the
  plane with crisp shadows; labels stand up as billboards. On `one_i`, `i_neg1`, `neg_i` and `back_one` the cycle
  1 → i → −1 → −i runs with red quarter arcs. On `ii` the equation `i · i = −1` builds. On `whole`/`ninety` the whole
  plane turns 90° (z ↦ iz) with a fan of yellow arrows riding along, over the domain coloring turning by π/2:
  the camera cranes to a low hero angle and a thin vertical axis marks what it turns about, then it rises as the
  plane fades. Badge `×i = ↺90°`.
- **Beats:** `question` `twice` `not_stretch` `further` `quarter` `plane` `any_dir` `i_quarter` `one_i` `i_neg1` `neg_i` `back_one` `ii` `not_rule` `two_quarters` `whole` `ninety`
- **Layers:** shader `plane3d.frag` (ray-cast perspective plane: grid, colors, depth fade, reveal disc;
  `u_theta` 0 → π/2) · manim overlays warped through the same camera (`shots3d.Cam3`) · HUD.

### s05_sideways · T.cut_ch3 → T.cut_walk (3:44–4:59, 75 s) — Ch3 Growth turned sideways
- **Narration:** "Now we can read e to the i t… Velocity equals position… picks up a single i. Velocity equals i times
  position… It turns an arrow by a quarter turn… turned ninety degrees. Let us watch. Start at one… the velocity
  points straight up… position arrow tilts… Always at a right angle. Always pushing sideways… stays exactly one
  unit from the center. It traces a circle… same length… one unit of distance, per unit of time. Let the whole
  plane follow the same rule… flying outward… the points spiral… every point circles forever."
- **Visual idea:** two framed panels. The left replays s02's number line with `v = x`. On `picks` the hovering red i
  drops into the right panel's `v = i·x`. The panels merge into the full frame. On `pos_right` the yellow position
  arrow runs from 0 to 1. On `turns_arrow`/`vel_up` a copy **visibly rotates 90° about its tip** and turns pink. On
  `moves_up`/`tilts` the point moves and a right-angle mark stays locked between the two arrows. On `circle` the trail
  closes the unit circle. On `unit_time` a small odometer `t` ticks at speed 1. Then the **flow field**: the camera
  pulls back to ~6k points on rings under dz/dt = a·z while a corner dial sweeps a from 1 (`outward`, radial
  explosion, gold) through e^{iπ/4} (`spiral`) to i (`circles`, red). As the points settle, a skia long-exposure
  of the circular streamlines fades in.
- **Beats:** `read_eit` `rule_et` `v_x` `picks` `v_ix` `know_i` `turns_arrow` `always_pos` `turned90` `watch` `start1` `pos_right` `vel_up` `moves_up` `tilts` `right_angle` `sideways` `never_closer` `stays` `circle` `how_fast` `same_len` `unit_time` `whole_plane` `outward` `spiral` `all_way` `circles`
- **Layers:** manim · `PointsLayer` (numpy exact positions, glow 0) · skia → `ArrayLayer` · camera pull-back.

### s06_walk_pi · T.cut_walk → T.cut_ch4 (4:59–5:39, 40 s)
- **Narration:** "So e to the i t has a simple meaning. Walk along the unit circle, a distance t. Now, pause and predict…
  How far do we have to walk to reach negative one? [2.9 s] Halfway around… two pi. So halfway, is pi. After
  walking a distance pi, the point lands on negative one. e to the i pi equals negative one. A half turn… exactly
  what we said negative one is. That is the picture. But a picture can fool you… check it, twice."
- **Visual idea:** on `walk`/`dist_t` the point walks while a green tape measure unrolls along the arc with readout
  `t`. On `predict` the point stops and a `?` blinks at −1, held through the silence. On `two_pi` a full lap
  traces 2π. On `halfway_pi` it halves to the upper semicircle in green, labelled **π**. On `after_pi`/`lands_neg1`
  the walk resumes and lands on −1. On `eq_pay` the equation assembles from parts flying in: e from the Ch1 badge,
  i from the Ch2 badge, π off the arc, −1 from the point. On `half_pay`/`exactly` the Ch2 half-turn glyph pulses.
  On `fool` the circle redraws dashed, and on `check` two empty check slots appear on the rail. Badge `v = ix`.
- **Beats:** `meaning` `walk` `dist_t` `predict` `start_one` `how_far` `reach` `halfway` `two_pi` `halfway_pi` `after_pi` `lands_neg1` `eq_pay` `half_pay` `exactly` `the_picture` `fool` `check` `arithmetic`
- **Layers:** manim · camera push on the landing.

### s07_compound_turn · T.cut_ch4 → T.cut_ch5 (5:39–6:44, 65 s) — Ch4 Compounding a turn
- **Narration:** "Go back to the bank. e came from compounding. One plus one over n, raised to the n… One plus i pi over
  n… Start crude. Let n be one… far up and to the right. Nowhere near… Let n be two… turns the plane a little, and
  stretches it a little… we land up here. Four steps… The path begins to bend. Eight steps. Sixteen. A hundred…
  closer and closer to a half turn… the path hugs the unit circle… Negative one. Compounding a rate of growth
  gives e. Compounding a rate of turning gives a walk around the circle."
- **Visual idea:** on `back_bank` the Ch1 staircase returns as a miniature. On `lim_e` its formula appears, and on
  `lim_ipi` the `1` becomes `iπ` (TransformMatchingTex). On `n1` one arrow runs to 1 + iπ. On `n2`/`mult2` the chain
  of **similar right triangles** appears (legs 1 and π/n, scaled by the running length), and on `land_here` it ends
  at −1.47 + 3.14i. `n4`, `n8`, `n16` and `n100` snap in on their words. The chain spirals onto the unit circle, the
  camera frames in, the endpoint readout heads to −1 + 0i, and the side ledger `n | (1+iπ/n)ⁿ` adds a row each
  time. On `landed` it's −1. On `growth_e`/`turning_circle` the staircase and the spiral sit side by side, and the
  first check slot ticks.
- **Beats:** `back_bank` `compounding` `lim_e` `should` `lim_ipi` `crude` `n1` `one_ipi` `far` `nowhere` `n2` `mult2` `little` `land_here` `n4` `smaller` `bend` `n8` `n16` `n100` `shrink` `add_up` `hugs` `final` `landed` `growth_e` `turning_circle`
- **Layers:** manim redraw (n as a stepped Track) · camera frame.

### s08_series · T.cut_ch5 → T.cut_ch6 (6:44–7:55, 71 s) — Ch5 The infinite sum
- **Narration:** "a second way… An infinite sum. One, plus x, plus x squared over two… x cubed over six… n factorial.
  Plug in i pi… each term as an arrow, laid tip to tail. The first term is one… The second is i pi… straight up…
  The third has i squared… points left. Pi squared over two. About four point nine. The next turns again… down.
  Then right. Then up… the steps grow… the factorials grow faster… spirals inward… Negative one, again… the
  horizontal steps… cosine of pi. The vertical steps… sine of pi. Which is zero."
- **Visual idea:** the series builds term by term on `inf_sum` → `nfact`. On `plug` x becomes iπ. On `first`,
  `second` and `third` the arrows lay tip to tail (teal horizontal, purple vertical) with small red right-angle turn
  marks. On `pi2`/`v49` the camera pulls back as the steps grow (π²/2 ≈ 4.93, π³/6 ≈ 5.17). On `down`, `right` and
  `up` the next steps snap in. On `factorials` a corner bar chart of πⁿ/n! rises and then collapses. On
  `spirals`/`one_point` the camera pushes about 8× through a framed magnifier as the spiral closes on −1. On
  `horizontal`/`cos_pi` the teal steps slide onto the real axis and sum to −1, and on `vertical`/`sin_pi` the purple
  steps stack and cancel to 0. The second check slot ticks and the `Σ` badge drops.
- **Beats:** `second_way` `inf_sum` `plus_x` `x2` `x3` `so_on` `nfact` `plug` `arrows` `tip` `first` `step_right` `second` `i_turns` `up_pi` `third` `left` `pi2` `v49` `next_turn` `down` `right` `up` `each` `grow` `factorials` `shrink2` `spirals` `one_point` `again` `horizontal` `cos_pi` `vertical` `sin_pi` `zero`
- **Layers:** manim · camera frame moves · numpy partial sums.

### s09_formula · T.cut_ch6 → T.cut_helix (7:55–8:14, 19 s) — Ch6 The whole circle
- **Narration:** "Pi was never special. Walk any distance theta… How far right are you? That is the cosine of theta. How
  far up? The sine of theta. So e to the i theta equals cosine theta, plus i times sine theta. This is Euler's
  formula."
- **Visual idea:** on `any_theta` the point sweeps through θ with a green angle arc and a live θ readout. On
  `how_right`/`cos_t` a teal drop lands on the real axis. On `how_up`/`sin_t` a purple drop lands on the imaginary
  axis. On `euler`/`plus_isin` the formula builds in matching colors, each part linked to its segment. On `formula`
  the badge `cos + i sin` drops.
- **Beats:** `never` `any_theta` `how_right` `cos_t` `how_up` `sin_t` `euler` `plus_isin` `formula`
- **Layers:** manim.

### s10_helix · T.cut_helix → T.cut_identity (8:14–8:41, 27 s)
- **Narration:** "let time run, and spread the walk out along a third direction… a helix. Look from the side… a sine
  wave. Look from below, a cosine wave. Look head on… collapses back into the circle. This is why circles hide…
  Springs, alternating current, sound… a turning arrow underneath."
- **Visual idea:** on `time_runs`/`third_dir` the circle tilts into 3D and the walk stretches along a time axis.
  On `helix` the yellow helix draws, with its shadows on two walls (a purple sine and a teal cosine). On `side`,
  `below` and `head_on` the camera orbits through those three views and the helix flattens into each. On `springs`,
  `ac` and `sound` three small framed panels pop in, each a turning arrow driving its wave (spring, AC sine, sound),
  symbols only.
- **Beats:** `time_runs` `third_dir` `helix` `side` `sine_wave` `below` `cos_wave` `head_on` `collapses` `why` `springs` `ac` `sound` `oscillates` `arrow_under`
- **Layers:** manim crisp vector lines through an orthographic az/el projection (the 006 s06 pattern).

### s11_identity · T.cut_identity → T.cut_outro (8:41–9:17, 36 s)
- **Narration:** "a few special values. Theta equals pi over two… you land on i. Theta equals pi… negative one. Theta
  equals two pi… back at one… multiplying by e to the i theta does not just move one point. It turns the entire
  plane… e to the i pi turns everything by half a turn. Move the one across… e to the i pi, plus one, equals zero."
- **Visual idea:** the 3D plane from s04 returns: it opens flat on the intro's hero frame and tilts away on
  `special_vals`. On `land_i`, `land_neg1` and `back_at_one` the point lands at each value and its label stamps in
  (`out_back`). Then the **hero callback**: on `mult_theta`/`entire` the camera cranes low and the domain-colored plane
  fills the screen under the grid, and on `half_all` the grid and color wheel turn together through π, the half turn of the whole plane
  promised in the intro, about a thin vertical axis. On `move_one` the camera rises back to the flat hero frame and/`final_eq` the −1 moves across (TransformMatchingTex) to give
  e^{iπ} + 1 = 0, and the five constants light.
- **Beats:** `special_vals` `th_half` `land_i` `th_pi` `land_neg1` `th_2pi` `back_at_one` `mult_theta` `not_just` `entire` `half_all` `move_one` `famous` `final_eq`
- **Layers:** shader `plane3d.frag` (`u_theta` = the same θ Track that turns the fan) · manim overlays through
  `shots3d.Cam3` · HUD.

### s12_outro · T.cut_outro → T.end (9:17–10:05, 48 s)
- **Narration:** "So let us read the equation one last time. e is growth… i is a quarter turn… the growth turns sideways…
  walks around a circle, at speed one. Pi is the distance… halfway around… exactly what negative one means. The bank,
  the infinite sum, and the picture all agree. e to the i pi equals negative one. Not a coincidence of symbols. A
  half turn. If you want to see… the Fourier series…"
- **Visual idea:** on `one_last` the rail's badges lift into a row at the centre, and each lights on its word
  (`o_growth`, `o_quarter`, `o_sideways`, `o_dist`). On `agree` the two check marks and the picture badge align.
  On `o_eq` they dissolve into one unit circle and the point makes its last slow half walk with the green arc,
  landing on −1 on `o_half_turn`. The equation holds beneath. On `fourier` a small framed panel of epicycles
  (`aion.maths.fourier`) draws a shape. Fade to black in the 3 s tail.
- **Beats:** `one_last` `o_growth` `o_quarter` `o_sideways` `o_circle` `o_speed` `o_dist` `o_half` `o_neg1` `agree` `o_eq` `coincidence` `o_half_turn` `next_video` `fourier` `going_next`
- **Layers:** manim · `aion.maths.fourier`.

## Ear check (listen once before building)
"e to the i pi" (0:01), "e to the i t" (3:46, 3:54), "one plus i pi over n" (5:50), "x squared over two" (6:50),
"Euler's formula" (8:12).

## Beat table
| beat | time | end | words |
|---|---|---|---|
| eq | 1.50 | 3.18 | e to the i pi equals |
| neg1 | 3.26 | 3.96 | negative one |
| another | 6.00 | 6.94 | written another way |
| plus_one | 8.72 | 10.30 | plus one equals zero |
| five | 10.71 | 11.76 | Five of the most |
| beautiful | 16.32 | 17.52 | most beautiful equation |
| slowly | 19.63 | 20.77 | read it slowly |
| two_seven | 23.38 | 24.39 | about two point seven |
| power | 24.82 | 25.46 | Raising a number |
| times | 30.50 | 32.31 | by itself i pi times |
| imaginary | 32.76 | 33.70 | An imaginary number |
| trick | 36.48 | 37.16 | a clever trick |
| not_ | 38.27 | 38.87 | It is not |
| picture | 39.29 | 40.26 | It is a picture |
| cut_preview ✂ | 40.73 | 40.73 | picture. ✂ e |
| growth | 41.82 | 43.00 | a story about growth |
| turning | 44.14 | 45.21 | a story about turning |
| distance | 45.94 | 47.02 | pi is a distance |
| together | 47.44 | 48.33 | Put them together |
| walking | 49.26 | 50.62 | walking around a circle |
| lands | 50.94 | 52.77 | lands exactly on negative one |
| by_end | 53.70 | 54.08 | By the end |
| see_it | 57.18 | 58.01 | You will see it |
| dollar | 59.78 | 60.98 | one dollar in a bank |
| half_plane | 61.94 | 62.98 | half turn of the whole |
| cut_ch1 ✂ | 68.55 | 68.55 | plane. ✂ First, |
| real_e | 69.32 | 70.12 | see e for what |
| decimal | 71.28 | 72.05 | Not a decimal |
| kind | 72.45 | 73.43 | A kind of growth |
| bank | 74.32 | 75.10 | Imagine a bank |
| put_in | 77.75 | 78.86 | Put in one dollar |
| have_two | 80.45 | 80.45 | you have two |
| half | 82.48 | 83.60 | pays half that interest |
| six_months | 84.97 | 85.95 | After six months |
| interest_on | 87.88 | 88.88 | that whole amount earns |
| v225 | 90.72 | 91.56 | two twenty five |
| four | 92.82 | 93.65 | four times a year |
| v244 | 94.38 | 95.04 | two forty four |
| month | 95.40 | 96.01 | Every month |
| day | 97.50 | 98.54 | Every single day |
| finer | 101.80 | 102.97 | finer and finer |
| infinity | 104.04 | 104.91 | run off to infinity |
| settles | 105.56 | 106.81 | settles on one number |
| v2718 | 107.20 | 108.74 | Two point seven one eight |
| is_e | 109.60 | 110.45 | number is e |
| cut_growth ✂ | 110.88 | 110.88 | e. ✂ Here |
| special | 111.82 | 112.71 | what makes it special |
| continuously | 113.86 | 115.06 | paid continuously |
| rate_eq | 115.98 | 116.78 | a rate equal to |
| hold1 | 118.03 | 118.98 | Hold one dollar |
| hold2 | 120.82 | 121.61 | Hold two |
| graph | 123.16 | 124.35 | Draw it as a graph |
| et | 124.88 | 125.67 | e to the t |
| slope | 127.07 | 128.00 | the slope of the curve |
| height | 128.08 | 128.78 | equals its height |
| motion | 130.10 | 131.09 | picture it as motion |
| pt_line | 131.82 | 132.55 | point on a line |
| vel_pos | 132.74 | 134.26 | velocity is always equal |
| faster | 136.61 | 137.63 | the faster it runs |
| sentence | 138.49 | 139.69 | Hold on to that sentence |
| v_eq_x | 140.02 | 141.67 | Velocity equals position |
| heart | 142.36 | 143.18 | the heart of e |
| one_word | 144.36 | 145.48 | change just one word |
| cut_ch2 ✂ | 146.70 | 146.70 | it. ✂ Now |
| now_i | 147.70 | 148.60 | Now for i |
| cannot | 150.98 | 151.76 | cannot exist |
| actions | 153.34 | 154.37 | numbers as actions |
| line | 155.20 | 156.04 | Lay every number |
| times2 | 157.92 | 159.00 | by two is an action |
| stretches | 159.34 | 160.57 | It stretches the line |
| half_sq | 163.48 | 164.68 | by one half squeezes |
| neg | 165.82 | 167.52 | multiplying by negative one |
| three | 167.78 | 169.37 | Three goes to negative three |
| neg2 | 169.77 | 171.28 | Negative two goes to two |
| swings | 172.62 | 173.90 | swings to the other side |
| half_turn | 174.71 | 175.88 | It is a half turn |
| remember | 176.76 | 177.96 | Remember that |
| plant | 177.96 | 179.57 | Negative one is a half turn |
| matter | 180.24 | 180.95 | going to matter |
| cut_quarter ✂ | 181.38 | 181.38 | matter. ✂ Now |
| question | 182.62 | 184.03 | the question that i answers |
| twice | 184.53 | 185.54 | What action |
| not_stretch | 188.33 | 189.32 | Not a stretch |
| further | 190.44 | 191.35 | only stretch further |
| quarter | 192.12 | 193.00 | a quarter turn |
| plane | 196.14 | 197.47 | let the line become a plane |
| any_dir | 199.02 | 199.74 | any direction |
| i_quarter | 200.30 | 201.61 | i is the quarter turn |
| one_i | 202.08 | 203.37 | One goes to i |
| i_neg1 | 204.70 | 205.66 | goes to negative one |
| neg_i | 206.86 | 208.49 | goes down to negative i |
| back_one | 208.98 | 209.90 | back to one |
| ii | 210.63 | 212.50 | i times i is negative one |
| not_rule | 212.90 | 213.68 | Not as a rule |
| two_quarters | 215.24 | 216.24 | two quarter turns make |
| whole | 219.38 | 220.50 | turns the whole plane |
| ninety | 221.86 | 223.15 | rotated ninety degrees |
| cut_ch3 ✂ | 224.08 | 224.08 | degrees. ✂ Now |
| read_eit | 225.84 | 227.11 | read e to the i t |
| rule_et | 228.58 | 229.70 | the rule for e to the t |
| v_x | 230.01 | 231.56 | Velocity equals position |
| picks | 234.02 | 235.25 | picks up a single i |
| v_ix | 235.50 | 237.46 | Velocity equals i times |
| know_i | 238.66 | 239.62 | we know what i does |
| turns_arrow | 240.10 | 240.82 | turns an arrow |
| always_pos | 242.46 | 243.94 | the velocity is always the |
| turned90 | 244.82 | 245.74 | turned ninety degrees |
| watch | 246.65 | 247.35 | Let us watch |
| start1 | 247.74 | 248.72 | Start at one |
| pos_right | 250.04 | 251.34 | position arrow points right |
| vel_up | 252.04 | 253.55 | velocity points straight up |
| moves_up | 254.38 | 255.59 | The point moves up |
| tilts | 257.10 | 258.23 | position arrow tilts |
| right_angle | 260.39 | 261.79 | Always at a right angle |
| sideways | 262.01 | 263.54 | Always pushing sideways |
| never_closer | 267.32 | 268.44 | never bring you closer |
| stays | 270.96 | 272.48 | stays exactly one unit |
| circle | 273.55 | 274.73 | It traces a circle |
| how_fast | 275.86 | 276.58 | how fast does it |
| same_len | 278.58 | 279.72 | same length as the position |
| unit_time | 284.29 | 285.14 | per unit of time |
| whole_plane | 286.10 | 287.16 | Let the whole plane |
| outward | 290.68 | 291.41 | flying outward |
| spiral | 293.56 | 294.44 | the points spiral |
| all_way | 295.40 | 296.08 | all the way |
| circles | 297.16 | 298.79 | every point circles forever |
| cut_walk ✂ | 299.22 | 299.22 | forever. ✂ So |
| meaning | 301.10 | 301.74 | has a simple |
| walk | 302.62 | 303.73 | Walk along the unit circle |
| dist_t | 304.38 | 304.89 | distance t |
| predict | 306.40 | 307.33 | pause and predict |
| start_one | 307.73 | 308.59 | We start at one |
| how_far | 309.00 | 309.84 | How far do we have |
| reach | 311.26 | 311.26 | reach negative one |
| halfway | 314.20 | 315.46 | Halfway around a circle |
| two_pi | 316.77 | 317.78 | The full way around |
| halfway_pi | 318.86 | 319.90 | So halfway |
| after_pi | 320.98 | 322.37 | After walking a distance pi |
| lands_neg1 | 323.14 | 324.29 | lands on negative one |
| eq_pay | 324.71 | 326.42 | e to the i pi equals |
| half_pay | 327.37 | 328.08 | A half turn |
| exactly | 328.82 | 329.94 | exactly what we said |
| the_picture | 331.84 | 332.85 | That is the picture |
| fool | 334.00 | 334.50 | can fool you |
| check | 335.04 | 335.58 | let us check it |
| arithmetic | 337.16 | 338.28 | nothing but arithmetic |
| cut_ch4 ✂ | 338.88 | 338.88 | arithmetic. ✂ Go |
| back_bank | 339.70 | 340.82 | Go back to the bank |
| compounding | 341.38 | 342.85 | e came from compounding |
| lim_e | 343.30 | 344.86 | One plus one over n |
| should | 348.10 | 349.22 | should come from compounding |
| lim_ipi | 350.38 | 352.30 | One plus i pi over n |
| crude | 354.26 | 355.23 | Start crude |
| n1 | 355.60 | 356.64 | Let n be one |
| one_ipi | 357.04 | 358.29 | One plus i pi |
| far | 359.80 | 360.93 | far up and to the right |
| nowhere | 361.32 | 362.04 | Nowhere near |
| n2 | 363.77 | 364.72 | Let n be two |
| mult2 | 365.30 | 366.70 | Multiplying by one plus |
| little | 369.50 | 370.38 | stretches it a little |
| land_here | 372.14 | 372.89 | we land up here |
| n4 | 374.01 | 374.87 | Four steps |
| smaller | 375.96 | 377.04 | a smaller turn |
| bend | 379.20 | 380.06 | begins to bend |
| n8 | 381.21 | 381.94 | Eight steps |
| n16 | 382.45 | 383.19 | Sixteen |
| n100 | 383.72 | 384.36 | A hundred |
| shrink | 385.22 | 386.02 | stretches shrink |
| add_up | 387.10 | 388.26 | The turns add up |
| hugs | 390.82 | 391.70 | the path hugs |
| final | 393.62 | 394.44 | its final spot |
| landed | 395.49 | 396.28 | Negative one |
| growth_e | 398.14 | 399.49 | rate of growth gives e |
| turning_circle | 400.62 | 401.66 | rate of turning gives |
| cut_ch5 ✂ | 403.82 | 403.82 | circle. ✂ There |
| second_way | 405.16 | 405.72 | a second way |
| inf_sum | 407.40 | 408.68 | An infinite sum |
| plus_x | 409.76 | 410.52 | plus x |
| x2 | 410.84 | 412.04 | x squared over two |
| x3 | 412.36 | 413.64 | x cubed over six |
| so_on | 413.72 | 413.96 | and so |
| nfact | 416.92 | 417.72 | n factorial |
| plug | 418.65 | 420.06 | Plug in i pi |
| arrows | 420.30 | 421.90 | treat each term as an arrow |
| tip | 422.22 | 422.85 | tip to tail |
| first | 423.86 | 425.14 | The first term is one |
| step_right | 425.35 | 426.27 | A step to the right |
| second | 427.36 | 428.81 | The second is i pi |
| i_turns | 430.06 | 431.30 | turns it a quarter turn |
| up_pi | 431.62 | 432.61 | step straight up |
| third | 434.57 | 436.20 | The third has i squared |
| left | 437.53 | 438.45 | So it points left |
| pi2 | 438.70 | 439.86 | Pi squared over two |
| v49 | 440.64 | 441.32 | four point nine |
| next_turn | 443.14 | 443.87 | turns again |
| down | 444.14 | 444.67 | points down |
| right | 444.99 | 445.51 | Then right |
| up | 445.83 | 446.37 | Then up |
| each | 446.89 | 447.74 | Each new step |
| grow | 450.64 | 451.63 | the steps grow |
| factorials | 453.84 | 455.36 | the factorials grow faster |
| shrink2 | 457.68 | 458.76 | the steps shrink |
| spirals | 459.44 | 460.29 | spirals inward |
| one_point | 460.55 | 462.52 | closer and closer to one point |
| again | 464.50 | 464.80 | again |
| horizontal | 466.44 | 468.25 | the horizontal steps |
| cos_pi | 469.56 | 470.27 | cosine of pi |
| vertical | 470.77 | 471.72 | The vertical steps |
| sin_pi | 472.36 | 472.96 | sine of pi |
| zero | 473.22 | 474.17 | Which is zero |
| cut_ch6 ✂ | 475.17 | 475.17 | zero. ✂ Pi |
| never | 476.01 | 477.97 | Pi was never special |
| any_theta | 478.07 | 479.33 | Walk any distance theta |
| how_right | 481.88 | 482.44 | How far right |
| cos_t | 483.60 | 484.49 | the cosine of theta |
| how_up | 484.89 | 485.61 | How far up |
| sin_t | 485.95 | 486.75 | The sine of theta |
| euler | 487.72 | 489.32 | e to the i theta equals |
| plus_isin | 490.28 | 491.64 | plus i times sine |
| formula | 492.64 | 493.85 | This is Euler's formula |
| cut_helix ✂ | 494.33 | 494.33 | formula. ✂ Now |
| time_runs | 495.30 | 496.30 | let time run |
| third_dir | 497.74 | 498.49 | a third direction |
| helix | 500.75 | 501.49 | a helix |
| side | 502.30 | 502.97 | from the side |
| sine_wave | 503.42 | 504.02 | a sine wave |
| below | 504.34 | 505.09 | Look from below |
| cos_wave | 505.30 | 506.16 | a cosine wave |
| head_on | 506.98 | 507.62 | head on |
| collapses | 507.94 | 508.70 | collapses back |
| why | 510.88 | 511.68 | why circles hide |
| springs | 514.16 | 514.99 | Springs |
| ac | 515.33 | 515.68 | alternating |
| sound | 516.40 | 517.39 | sound |
| oscillates | 517.49 | 518.83 | Wherever something oscillates |
| arrow_under | 519.68 | 520.93 | a turning arrow underneath |
| cut_identity ✂ | 521.33 | 521.33 | underneath. ✂ Now |
| special_vals | 522.18 | 523.57 | a few special values |
| th_half | 524.08 | 525.83 | Theta equals pi over two |
| land_i | 527.70 | 528.69 | you land on i |
| th_pi | 529.12 | 530.46 | Theta equals pi |
| land_neg1 | 531.86 | 533.04 | land on negative one |
| th_2pi | 533.44 | 535.03 | Theta equals two pi |
| back_at_one | 536.98 | 537.76 | back at one |
| mult_theta | 539.24 | 541.00 | multiplying by e to the i theta |
| not_just | 541.08 | 542.04 | does not just move |
| entire | 543.24 | 544.76 | turns the entire plane |
| half_all | 547.16 | 548.52 | turns everything by half |
| move_one | 549.95 | 551.42 | Move the one across |
| famous | 551.82 | 552.78 | the famous form |
| final_eq | 553.23 | 554.30 | e to the i pi |
| cut_outro ✂ | 557.22 | 557.22 | zero. ✂ So |
| one_last | 559.72 | 560.52 | one last time |
| o_growth | 561.72 | 562.78 | e is growth |
| o_quarter | 565.05 | 566.40 | i is a quarter turn |
| o_sideways | 568.06 | 569.57 | growth turns sideways |
| o_circle | 571.82 | 572.97 | walks around a circle |
| o_speed | 573.22 | 574.02 | at speed one |
| o_dist | 575.02 | 576.51 | Pi is the distance |
| o_half | 578.12 | 579.20 | gone halfway around |
| o_neg1 | 581.44 | 582.59 | what negative one means |
| agree | 586.42 | 587.01 | all agree |
| o_eq | 587.64 | 589.56 | e to the i pi equals |
| coincidence | 590.82 | 591.64 | Not a coincidence |
| o_half_turn | 592.67 | 593.50 | A half turn |
| next_video | 594.61 | 595.18 | If you want to see |
| fourier | 599.02 | 599.91 | Fourier series |
| going_next | 600.94 | 602.22 | where we are going next |
