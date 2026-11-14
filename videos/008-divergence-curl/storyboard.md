# Divergence and Curl, Finally Explained Visually: storyboard

Audio: `assets/audio.wav` (741.24 s = 12:21, 2,044 words, about 165 words a minute, voice speed 0.92)

Pacing (`voice.toml [pacing]`): 1.5 s lead-in, +0.5 s after each paragraph, +1.5 s between chapters, 3.0 s tail,
a held 3 s pause after the intro map, and three 2 s pause-and-predict pauses (saddle, lamp, river).
Captions for YouTube: `assets/subtitles.srt`. The full beat table is at the end (`uv run aion beats 008 --md`).

Structure: intro, five chapters, outro. Fourteen scene files.

| # | scene | chapter | range | length | mode |
|---|---|---|---|---|---|
| 0 | `s00_hook` | Intro: dust in a stream, the wrong intuition | 0:00–0:42 | 42 s | cinematic particles |
| 1 | `s01_preview` | Intro: preview montage + one-sentence map | 0:42–1:24 | 42 s | hero montage |
| 2 | `s02_arrows` | Ch1 A field of arrows | 1:24–2:04 | 40 s | one arrow → field → equation |
| 3 | `s03_flow` | Ch1 (cont.) arrows carry dust, meet the cast | 2:04–2:43 | 39 s | arrows → flow, panels |
| 4 | `s04_blob` | Ch2 Is stuff leaving? A drop of dye | 2:43–3:46 | 63 s | concrete, predict #1 |
| 5 | `s05_flux_box` | Ch2 (cont.) out minus in → ∇·F | 3:46–4:43 | 58 s | derivation |
| 6 | `s06_div_map` | Ch2 (cont.) divergence map, the lamp (plant) | 4:43–5:45 | 62 s | heat map, predict #2 |
| 7 | `s07_paddle` | Ch3 Is stuff turning? Whirl, river, drain | 5:45–6:52 | 67 s | wrong intuition ×2, **midpoint re-hook** |
| 8 | `s08_circulation` | Ch3 (cont.) around the square → curl | 6:52–7:50 | 58 s | derivation |
| 9 | `s09_curl_3d` | Ch3 (cont.) curl in 3D, ∇ as a mnemonic | 7:50–8:32 | 42 s | 2D → 3D |
| 10 | `s10_gauss` | Ch4 Adding up the boxes → divergence theorem | 8:32–9:37 | 65 s | tiling, cancellation, 3D, payoff |
| 11 | `s11_stokes` | Ch4 (cont.) adding up the loops → Stokes | 9:37–10:19 | 43 s | tiling, soap film 3D |
| 12 | `s12_maxwell` | Ch5 Where they live: Maxwell, water, weather | 10:19–11:31 | 72 s | application, promise kept |
| 13 | `s13_outro` | Outro: back to the stream → lesson → next | 11:31–12:21 | 50 s | callback |

## The story spine
"Two questions you can ask any point in a flow: is stuff leaving, and is stuff turning?" Each idea is shown
concretely first (dye, paddle wheel), then measured on a tiny square (which gives the formula), then added up over a
region (which gives the theorems), then read in Maxwell's equations. The midpoint re-hook lands at 6:08–6:12 on the
river ("Will the wheel spin? … It does.").

## Running numbers (computed with numpy/sympy at build time, never typed)

| use | value | where |
|---|---|---|
| source (x, y) | div 2, curl 0; dye area × e^{2t} → 2.72 at t = 0.5 | Ch1–Ch3 |
| whirl (−y, x) | div 0, curl 2; area × 1.00; wheel turns at curl/2 = 1 rad/s | Ch1–Ch3 |
| saddle (x, −y) | div 0, curl 0; dye stretches × 1.65 by × 0.61 at t = 0.5, area 1.00 | Ch1–Ch3 |
| river (y + 2.2, 0) | div 0, curl −1 (clockwise); every arrow points right on screen | Ch3 |
| drain (−y, x)/r² | curl 0 for r ≠ 0, circulation 2π around the centre | Ch3 |
| lamp (x, y)/r² | div 0 for r ≠ 0, flux 2π through every circle; 3D (x, y, z)/r³ → 4π through every sphere | Ch2 → Ch4 |
| hero field | 2 smoothed sources/sinks (q = ±1.3) + 2 vortices (g = +1.5, −1.1) + drift (0.35, 0), a = 0.9; div and curl in closed form, checked against finite differences (`python shots.py`) | intro, Ch2, outro |
| checks on screen | 1 + 1 = 2, 0 + 0 = 0, 1 − 1 = 0; 1 − (−1) = 2, 0 − 1 = −1 | Ch2, Ch3 |

## Visual system

Design: **Classic** (the BASE default). Pure black, crisp unglowed lines, Computer Modern for all text, no bloom,
glow, blur, vignette or grain. Field scenes dim the grid to `C.grid_minor` so the cyan arrows read. "After Effects
grade" comes from motion: eased and staggered reveals, match cuts, morphs, 2.5D camera pushes, parallax, flowing
dust and streak textures. Design sheet: `out/design/design_{1,2}.png` (`python design_sheet.py`).

| object | color token | meaning |
|---|---|---|
| vector field arrows, streak texture | `C.field` (light cyan) | the flow |
| dust grains, dye | `C.dust` (white) | stuff carried by the flow |
| positive divergence, sources, ∇· | `C.div` (orange) | stuff leaving |
| negative divergence, sinks | `C.sink` (blue) | stuff arriving |
| counter-clockwise spin, curl > 0, ∇× | `C.curl` (green) | turning |
| clockwise spin, curl < 0 | `C.cw` (pink) | turning the other way |
| P, ∂/∂x terms | `C.xpart` (teal) | the horizontal part |
| Q, ∂/∂y terms | `C.ypart` (purple) | the vertical part |
| tiny square, region boundary, wire loop, ∮ ∯ | `C.boundary` (yellow) | the edge |
| E field / B field (Ch5 only) | `C.efield` / `C.bfield` | Maxwell |
| grid / panel borders | `C.grid` `C.grid_minor` `C.axis` `C.frame` | the stage |

Rules for every scene:
- One focal point per frame, at most three things moving. Symbols, equations and numbers only, with no caption text.
- Equations through `div_eq()`, `curl_eq()` and `tex(..., colors=)` in `shots.py`: ∇· orange, ∇× green, P teal,
  Q purple, boundary integrals yellow. ∯ comes from `oiint()` (∬ with a drawn ring; the esint font doesn't render).
- **Cast rail** (left edge, from s03 on): three small framed panels (source, whirl, saddle) that light up when
  named. **Badges** at chapter ends stack under the rail: `F` → `∇·F` → `∇×F` → `∮ ∯` → Maxwell. The outro
  gathers them.
- Transform, don't cut: the hook's stream returns in s06 and s13; the s04 dye shrinks into the s05 tiny square; the
  s05 square becomes the s08 circulation loop; the s08 square tiles into the s10 region; the s01 Maxwell block
  pays off in s12; the s06 lamp pays off in s10.
- Motion: `easy_ease` for camera, `smooth` for motion, `out_back` for label pops, `spring` for badge drops.
- Shared helpers live in `shots.py` (fields, `field_arrows`, `dye`, `flow_linear`, `advect`, `paddle`,
  `spin_glyph`, `panel`, `ortho`, `cube_edges`, `div_eq`, `curl_eq`, `oiint`).

### Engines
| engine | used for |
|---|---|
| Manim (ManimLayer) | arrows, equations, panels, the dye polygon, paddle wheels, tiny squares, tiling and cancellation, ortho-3D cube, closed surface, wire loop and soap film as crisp lines (`ortho()` in `shots.py`, 007 `shots3d.py` pattern) |
| ModernGL | GPU compositing, the 2.5D camera, a new `shaders/lic.frag` (animated line-integral-convolution streaks of the hero field) in s00, s01, s06 and s13 |
| Taichi | `FlowSim(Sim)` in `sims.py`: RK4 dust advection through the hero field with respawn (baked, cached, seeded) → `PointsLayer(glow=0)` |
| numpy (exact) | dye in the cast fields via the matrix exponential (`flow_linear`), drain/river dust, flux and circulation readouts, div/curl maps → `FieldLayer(cmap="diverging")` |
| skia-python → `ArrayLayer` | static long-exposure streamline plates (s03, badges) |
| pyvista | optional hero still for s10 (closed surface with flux glyphs). An animated version needs an animated-array layer in aion first; decide when building Ch4. Default: Manim ortho-3D. |

## Retention plan

| device | where |
|---|---|
| Visual question inside 10 s | `spreads` (0:08) the dust spreads apart; `turn` (0:17) it starts to turn |
| Wrong intuition first | `formula` → `never` (0:32–0:40) "just partial derivatives to memorize" |
| Preview the result, unexplained | `map` (0:55) heat map, `spin` (1:00) paddle wheel, `add_up` cube and soap film, `four_eq` (1:16) Maxwell block |
| Map in one sentence | `arrows_page` → `light` (1:13–1:20), then a 3 s hold |
| Plant → payoff | `fool` (2:41) "the saddle will fool us" → `neither` (3:20); `matters` (5:03) the lamp → `lamp_pays` (9:20); `four_eq` (1:16) → `four` (10:21) |
| Pause and predict | `guess` (3:14), `right_q` (5:15), `will_spin` (6:08), each followed by about 3 s of silence |
| Midpoint re-hook | `it_does` (6:12) the river spins the wheel; `so_curl` (6:43) "curl isn't whether arrows circle" |
| Mode switches | particles → montage → arrows → flow panels → dye → derivation → heat map → wheels → loop walk → 3D → tiling → soap film → equations → callback |
| Close each chapter visually | badge drops at `fool`, `comes_back`, `trick`, `one_idea`, `patch` |
| End on the payoff | `warm_spot` (11:41) and `green_swirl` (11:47): the hook's two places are the warm spot and the green swirl |

## Scenes

### s00_hook · T.start → T.cut_preview (0:00–0:42, 42 s)
- **Narration:** "Drop a pinch of dust into a moving stream… Here, the dust spreads apart… here, the dust starts to
  turn… Those two motions have names. The first is divergence. The second is curl. Most of us meet them as a row
  of partial derivatives… the picture never quite shows up."
- **Visual idea:** black fades up to the hero field as a slow LIC streak texture in `C.field` at low opacity, with
  white dust flowing over it. On `two_places` two faint rings mark the source region and the ccw vortex. On
  `spreads` the camera pushes into the source (2.5D, `easy_ease`) and a dye drop blooms outward. On `turn` the
  camera pans to the vortex and a second drop starts to swirl. On `names` the camera pulls back. On `divergence`,
  ∇·F writes on in orange over the first ring; on `curl`, ∇×F in green over the second. On `formula` the two
  symbols slide together and unfold into `∂P/∂x + ∂Q/∂y` and `∂Q/∂x − ∂P/∂y`, colored by part. On `never` the
  formulas grey out and the stream dims behind them.
- **Why it explains:** the viewer sees both behaviours before hearing a definition, and the formulas arrive as
  the thing that hides them.
- **Beats:** `dust` `two_places` `spreads` `neighbors` `welling` `turn` `whirlpool` `names` `divergence` `curl`
  `partials` `formula` `exam` `never`
- **In / out:** fade up from black. Out: the grey formulas dissolve; the stream stays for s01.
- **Layers:** shader (lic.frag) · Taichi dust → PointsLayer · numpy dye → manim · manim Eqn · camera push/pan.

### s01_preview · T.cut_preview → T.cut_ch1 (0:42–1:24, 42 s)
- **Narration:** "So let's put the picture first… Is stuff leaving this point? And is stuff turning around it?…
  a map of where the flow is born… every hidden spin… Two of the biggest theorems… We will start with arrows on a
  page, and end with the four equations behind every radio, every motor, and every beam of light." Then a 3 s hold.
- **Visual idea:** on `leaving` and `turning` the two questions appear as symbols only, `∇·F = ?` and `∇×F = ?`.
  Four match-cut shots, each landing on its word. `map`: the divergence heat map paints in under the stream
  (`FieldLayer`, wiping left to right). `spin`: a paddle wheel drops (`spring`) into a straight-looking shear patch
  and turns. `add_up`: a 3D cube of small cubes with orange flux arrows out of its faces (ortho-3D, slow orbit).
  `theorems`: a yellow wire loop with a soap film that bulges. `arrows_page`: a single arrow on black. `four_eq`:
  Maxwell's four equations flick in as a ghosted 2×2 block and hang there through the hold. On `light` the block
  dims to a faint ghost.
- **Why it explains:** it promises the whole arc in pictures without explaining any of it.
- **Beats:** `picture_first` `question` `leaving` `turning` `map` `born` `spin` `straight` `add_up` `theorems`
  `arrows_page` `four_eq` `radio` `light`
- **In / out:** continuous from the stream. Out: the ghost block fades and one arrow remains for s02.
- **Layers:** FieldLayer · manim · ortho-3D lines · camera.

### s02_arrows · T.cut_ch1 → T.cut_flow (1:24–2:04, 40 s) · Ch1 A field of arrows
- **Narration:** "Pick a point in the plane, and attach an arrow to it… wind, gravity, an electric charge… Do that
  at every point, and you have a vector field… A weather map of the wind… split each arrow into two parts… P… Q…
  F of x y equals P of x y, Q of x y."
- **Visual idea:** the dim grid draws on. On `point` a dot appears; on `attach` an arrow grows from it. On
  `anything` the arrow swings three times (`wind`, `gravity`, `charge`), changing direction and length. On
  `every_point` the arrow copies outward in a staggered ring wave (`out_back`) to fill the frame with the hero field
  (`field_arrows`, normalized lengths). On `weather` a soft coastline outline appears under the arrows (skia plate)
  and each arrow breathes slightly. On `write` the camera pushes into one arrow; on `call_P` its horizontal leg
  splits off in teal, on `call_Q` its vertical leg in purple. On `F_eq`, `F(x,y) = (P(x,y), Q(x,y))` builds term
  by term over the top.
- **Why it explains:** a field is defined by building it, one arrow at a time.
- **Beats:** `point` `attach` `anything` `wind` `gravity` `charge` `every_point` `vector_field` `rule` `weather`
  `town` `write` `two_parts` `call_P` `call_Q` `depend` `F_eq`
- **Layers:** manim (grid, arrows, Eqn) · skia ArrayLayer (coastline) · camera push.

### s03_flow · T.cut_flow → T.cut_ch2 (2:04–2:43, 39 s)
- **Narration:** "Arrows alone are hard to read. So let them carry something… Now the field is a flow… Three
  flows will keep us company… the source… the whirl… a saddle. Keep an eye on the saddle. It is going to fool us
  in a minute."
- **Visual idea:** on `sprinkle` dust rains in and starts following the arrows (Taichi bake); the arrows fade to
  30 % and a long-exposure streamline plate fades in behind. On `company` the frame splits into three framed panels
  (`panel`) with a staggered slide-in. `source`, `whirl` and `saddle` each fill their panel with arrows plus dust in
  exact flow (`flow_linear`) as they are named. On `keep_eye` the saddle panel pulses once. On `fool` the three
  panels shrink and dock as the **cast rail** on the left, and the `F` badge drops (`spring`).
- **Why it explains:** dust makes the flow readable, and the three cast members become reference points for the
  rest of the video.
- **Beats:** `hard` `carry` `sprinkle` `is_flow` `velocity` `dust_shows` `company` `away` `name_source` `around` `whirl`
  `saddle_in` `saddle` `keep_eye` `fool`
- **Layers:** Taichi PointsLayer · skia ArrayLayer · manim panels · numpy exact flows.

### s04_blob · T.cut_ch2 → T.cut_flux (2:43–3:46, 63 s) · Ch2 Is stuff leaving?
- **Narration:** "Drop a small circle of dye… what happens to its area… In the source… The circle grows… nearly
  tripled… In the whirl… stays exactly the same… Now the saddle… make a guess… It does neither… thin ellipse…
  looks dramatic… the area stays put. That is what divergence measures… how fast a tiny drop is swelling… Positive…
  Negative… Zero…"
- **Visual idea:** the source panel expands from the rail to full frame. On `dye` a white dye disc drops in
  (`dye`, 200 vertices). On `grows` it is carried by the exact flow, with a ghost outline of the start left behind
  and an `area × 1.00 → 2.72` readout ticking (`poly_area`), in orange. Match cut to the whirl on `in_whirl`: the
  disc swings around the centre, readout locked at `1.00`. Saddle on `now_saddle`: on `guess` the motion freezes
  mid-stretch for the predict pause. On `neither` it resumes into a long ellipse, and on `stays_put` the readout
  pulses at `1.00`. On `measures` three small dye discs line up and play `+`, `−` and `0` (grow / shrink / reshape)
  on `positive`, `negative` and `zero`.
- **Why it explains:** divergence is defined by what you can see (area change) before any symbol appears.
- **Beats:** `first_q` `dye` `area` `in_source` `grows` `tripled` `in_whirl` `same` `now_saddle` `pulled` `guess`
  `grow_shrink` `neither` `ellipse` `dramatic` `stays_put` `measures` `wild` `swelling` `positive` `negative` `zero`
- **Layers:** manim (arrows, dye polygon, readout, rail) · numpy `flow_linear`.

### s05_flux_box · T.cut_flux → T.cut_map (3:46–4:43, 58 s)
- **Narration:** "To turn that into a formula, shrink the drop to a tiny square… Whatever flows out, minus whatever
  flows in… left and right edges… P… a little bigger on the right… the partial derivative of P… top and bottom… Q…
  Del dot F equals… Check it on our three flows…"
- **Visual idea:** on `square` the dye disc morphs into a yellow square in a general field, and the camera pushes in.
  On `lr` the left and right edges brighten; on `only_P` teal arrows pierce them (horizontal parts only). On `bigger`
  the right arrow grows longer than the left; their difference is lifted out as a small teal bar, and on `dPdx` it
  becomes `∂P/∂x`. The same for top and bottom in purple on `tb` → `∂Q/∂y`. On `add_two` the two terms slide
  together; on `del_dot` the full `div_eq()` assembles. On `check` the cast rail lights up one panel at a time with
  `1 + 1 = 2`, `0 + 0 = 0`, `1 − 1 = 0`; the saddle's `0` gets a small tick.
- **Why it explains:** the formula is literally "out minus in, per area", one direction at a time.
- **Beats:** `to_formula` `square` `count` `out_in` `lr` `only_P` `bigger` `dPdx` `tb` `dQdy` `add_two` `del_dot`
  `check` `chk_source` `chk_two` `chk_whirl` `chk_saddle` `chk_zero` `sees`
- **Layers:** manim · camera push/pull.

### s06_div_map · T.cut_map → T.cut_ch3 (4:43–5:45, 62 s)
- **Narration:** "Now do it at every point, and color the plane. Warm… cool… sources… sinks… the dust agrees…
  One more flow, and this one matters later… like light fading from a lamp… So the divergence must be positive.
  Right?… The map stays dark… except the single point… twice as wide… half as long… the same amount of water
  crosses every circle… Hold on to that. It comes back."
- **Visual idea:** the hero stream returns (match cut from s00). On `color_plane` the divergence map wipes in
  (`FieldLayer`, sink blue → black → orange) and labels `+` and `−` pop on the two blobs on `sources` and `sinks`.
  On `agrees` the dust visibly spreads over orange and bunches over blue. Hard reset on `one_more`: the lamp field on
  black, arrows shrinking outward. On `must` the viewer expects orange; on `right_q` the frame holds (predict). On
  `dark` the map fades in: all black, with one orange pixel at the centre. On `circle` a yellow circle appears; on
  `twice` a second one twice as wide; arrow lengths on each are measured with ticks (`half`); on `every_circle` a
  flux readout `2π` sits on each circle. On `hold` the lamp shrinks into a small badge parked top-right (the plant),
  and the `∇·F` badge drops under the rail.
- **Why it explains:** the map generalises the dye to every point, and the lamp breaks the "arrows point out ⇒
  positive" intuition.
- **Beats:** `color_plane` `warm` `cool` `sources` `sinks` `agrees` `spreads_warm` `crowds` `one_more` `matters`
  `shrink` `lamp` `outward` `must` `right_q` `dark` `except_pt` `circle` `twice` `edge_long` `half` `cancel`
  `every_circle` `nothing` `one_point` `hold` `comes_back`
- **Layers:** shader (lic) · FieldLayer · Taichi PointsLayer · manim.

### s07_paddle · T.cut_ch3 → T.cut_circ (5:45–6:52, 67 s) · Ch3 Is stuff turning?
- **Narration:** "drop in a tiny paddle wheel, pinned in place… In the whirl, it turns… Now a river… faster near the
  top… Will the wheel spin?… It does… clockwise… Straight arrows, and still a spin… Here is a drain… Pin a wheel
  anywhere away from the center, and it does not turn… Let it float… stays upright, like a car on a Ferris wheel…
  So curl is not about whether the arrows go in circles…"
- **Visual idea:** whirl panel from the rail. On `paddle` a wheel drops in with a little `spring`. On `whirl_turns`
  it turns ccw (angle = curl/2 · t), with a green spin glyph. On `same_rate` two more wheels appear elsewhere, all
  turning in sync. On `river` there is a cut to the shear flow (all arrows right, longer on top). On `will_spin` a
  wheel sits motionless for the predict pause. On `it_does` it begins to turn clockwise (pink glyph), and on
  `top_pushed` the top vane's push arrow brightens against the bottom one. On `drain` the drain field appears; on
  `pin` a pinned wheel stays still; on `float_` a wheel rides around the drain, keeping its orientation, with
  ghosted copies along the path (the Ferris-wheel look). On `so_curl` the three cases sit side by side, and on
  `tiny_wheel` one wheel zooms to the centre.
- **Why it explains:** two counterexamples separate "arrows that circle" from "local spin".
- **Beats:** `second_q` `paddle` `pinned` `whirl_turns` `steadily` `same_rate` `river` `straight_right` `faster_top`
  `will_spin` `it_does` `top_pushed` `clockwise` `still_spin` `reverse` `drain` `circles` `pin` `not_turn` `float_`
  `around_drain` `upright` `ferris` `balance` `so_curl` `tiny_wheel` `how_fast`
- **Layers:** manim (paddle via `m.redraw`, arrows) · numpy dust for river/drain → PointsLayer.

### s08_circulation · T.cut_circ → T.cut_3d (6:52–7:50, 58 s)
- **Narration:** "walk once around a tiny square, counterclockwise, and add up how much the flow pushes you… the
  circulation. Along the bottom… P helps you. Along the top… P works against you… minus partial P, partial y. On the
  right edge… partial Q, partial x… The curl is partial Q partial x, minus partial P partial y… Check it…"
- **Visual idea:** the wheel shrinks into the yellow tiny square from s05 (continuity). On `walk` a marker walks the
  boundary with a running `circulation` readout. On `bottom` the bottom edge shows teal P arrows pointing along the
  walk (+); on `top` the top edge shows them against it (−); on `minus_dPdy` the difference becomes `−∂P/∂y`. Right
  and left edges in purple give `∂Q/∂x`. On `curl_is` `curl_eq()` assembles; on `per_area` "÷ area" folds in. On
  `check2` the rail panels light with `1 − (−1) = 2`, the river with `0 − 1 = −1` in pink, then `0` for source and
  saddle.
- **Why it explains:** the same tiny square measures the second question; curl is circulation per area.
- **Beats:** `walk` `add_push` `circulation` `bottom` `P_helps` `top` `against` `lose` `minus_dPdy` `right_edge`
  `left_down` `dQdx` `together` `curl_is` `per_area` `check2` `c_whirl` `c_two` `c_river` `c_neg` `c_cw` `c_zero`
  `no_spin`
- **Layers:** manim · camera.

### s09_curl_3d · T.cut_3d → T.cut_ch4 (7:50–8:32, 42 s)
- **Narration:** "In three dimensions, a wheel can tilt. So the curl becomes a vector… the axle that makes the wheel
  spin fastest… right hand rule… Our flat curl was only one piece… Write del as a list of three derivatives… dot
  product… divergence… cross product… curl. It is a memory trick, not a meaning…"
- **Visual idea:** on `three_d` the plane tilts back into an ortho-3D view (`ortho()`, `easy_ease`). The paddle
  becomes a 3D wheel with an axle; on `axle` the axle swings through a few angles while its spin rate readout
  changes, then settles on the green curl vector. On `rhr` a minimal right-hand glyph (curled arc + thumb arrow)
  appears. On `flat` the plane flattens back and the vector shrinks to its z part. On `del_list`
  `∇ = (∂x, ∂y, ∂z)` assembles; on `dot` `∇·F` slides off to the left (orange); on `cross` the 3×3 determinant
  `curl` slides to the right (green). On `trick` both dim, and on `meaning` the dye disc and paddle wheel icons sit
  beside them. The `∇×F` badge drops.
- **Why it explains:** 3D curl is the same wheel with a free axle; the nabla notation is labelled as a mnemonic.
- **Beats:** `three_d` `vector` `axle` `rhr` `fingers` `thumb` `flat` `out_page` `shorthand` `del_list` `dxdydz`
  `dot` `cross` `trick` `meaning`
- **Layers:** manim ortho-3D · Eqn.

### s10_gauss · T.cut_ch4 → T.cut_stokes (8:32–9:37, 65 s) · Ch4 Adding up the little pieces
- **Narration:** "So far, everything has been tiny. Now let's zoom out… cut it into small squares… Its divergence,
  times its area… two neighboring squares… Out for one, in for the other… every inside edge… only the outer
  boundary… the divergence theorem. And now the lamp from earlier pays off… every sphere… a point charge."
- **Visual idea:** the camera pulls back from one square (`zoom`) to a blob region in the hero field. On `squares`
  it tiles into an 8×6 grid of small squares (staggered). On `outflow` each shows tiny out-arrows sized by local
  divergence. On `neighbors2` two squares lift and highlight; their shared edge has an orange out-arrow and a blue
  in-arrow that meet and annihilate on `edge_cancels`. On `every_inside` all interior edges cancel in a sweeping
  wave; on `boundary` only the yellow outer boundary remains, with flux arrows. On `cubes` the region extrudes into
  3D cubes (ortho) and merges into a smooth closed surface with normals on `surface`. On `div_thm`
  `∭ ∇·F dV = ∯ F·n dS` assembles (`oiint()`). On `lamp_pays` the parked lamp badge flies back and inflates into a
  3D point source with nested spheres; on `every_sphere` a `4π` readout sits on each sphere; on `point_charge` a
  `+` charge glyph appears at the centre.
- **Why it explains:** the cancellation is shown edge by edge, so the theorem is something you watch happen.
- **Beats:** `tiny` `zoom` `region` `squares` `outflow` `div_area` `neighbors2` `shared` `out_one` `edge_cancels`
  `every_inside` `every_one` `boundary` `adding` `cubes` `surface` `div_thm` `lamp_pays` `square_dist`
  `every_sphere` `sits` `point_charge`
- **Layers:** manim (tiles, ortho-3D) · FieldLayer (faint div map under the tiles) · camera pull.

### s11_stokes · T.cut_stokes → T.cut_ch5 (9:37–10:19, 43 s)
- **Narration:** "Curl adds up the same way… its own little loop of circulation… opposite directions. They cancel
  again. Only the outer loop survives… Green's theorem. Lift it into space… a loop of wire, like a soap film. Push
  the film out into a bubble… Only the wire matters. This is Stokes' theorem. Two theorems, one idea…"
- **Visual idea:** same tiling (continuity), now with tiny green ccw loop arrows in each square. On `opposite` two
  shared-edge arrows point opposite ways and cancel; on `outer` the cancellation sweeps inward and leaves one yellow
  loop. On `green` `∬ curl F dA = ∮ F·dr` assembles. On `lift` the plane tilts into 3D and the loop becomes a wire;
  on `soap` a gently curved film fills it (ortho-3D mesh lines); on `bubble` the film morphs into a dome and the
  integral readout stays fixed. On `stokes` `∬ (∇×F)·n dS = ∮ F·dr`. On `one_idea` the two theorems sit side by
  side and their right-hand sides (the edges) pulse together. Badge `∮ ∯` drops.
- **Why it explains:** the same cancellation argument, applied to loops, gives the second theorem.
- **Beats:** `curl_adds` `loops` `meet` `opposite` `cancel_again` `outer` `total_curl` `green` `lift` `wire` `soap`
  `bubble` `no_change` `only_wire` `stokes` `one_idea` `except_edge`
- **Layers:** manim (tiles, ortho-3D surface morph).

### s12_maxwell · T.cut_ch5 → T.cut_outro (10:19–11:31, 72 s) · Ch5 Where they live
- **Narration:** "those four equations from the beginning. They are Maxwell's equations… Del dot E… charges are the
  sources and sinks… Del dot B equals zero… never start or end… Del cross E… a changing magnetic field stirs up an
  electric whirl… Spin a magnet near a coil… Del cross B… Currents wrap themselves in magnetic whirls… That is
  light. Water barely compresses… a hurricane… a giant patch of curl."
- **Visual idea:** on `four` the ghost 2×2 block from s01 returns and sharpens (promise kept). Each equation
  enlarges in turn with a 4–6 s micro-scene beside it: `div_E` a + and − charge with E lines radiating and
  converging (orange); `div_B` a bar magnet with closed B loops (violet-blue), with one loop traced all the way
  around; `curl_E` a magnet sliding into a coil and E whirl arrows circling the coil; `curl_B` a straight current
  with concentric B rings. On `together2` an E and B wave pair travels across the frame (crisp sine lines in
  ortho-3D), and on `light2` it runs out of frame. On `water` a quick river with `∇·v = 0`; on `hurricane` a
  top-down spiral of dust in the hero-style field with a green curl map underneath. The Maxwell badge drops.
- **Why it explains:** each equation is read as one of the two questions, in plain words.
- **Beats:** `four` `read_them` `div_E` `charges` `div_B` `no_sources` `never_end` `loop_back` `curl_E` `stirs`
  `magnet` `electricity` `curl_B` `changing_E` `wrap` `together2` `travel` `light2` `far` `water` `hurricane` `patch`
- **Layers:** manim · numpy dust (hurricane) · FieldLayer.

### s13_outro · T.cut_outro → T.end (11:31–12:21, 50 s)
- **Narration:** "Let's go back to the stream we started with. Here is the divergence map… sits right on a warm
  spot. And here is the curl… this green swirl. Divergence asks how much is leaving… Curl asks how much is
  turning… only the boundary is left. The formulas you memorized were never the point… Next time… the Laplacian…"
- **Visual idea:** the exact s00 shot returns (same camera, same dust). On `div_map` the divergence map fades in
  under it, and on `warm_spot` the s00 ring lands on the orange blob. On `here_curl` it crossfades to the curl map,
  and on `green_swirl` the second ring lands on the green blob. On `div_asks` and `curl_asks` the badges gather
  into two lines, `∇·F` with the dye icon and `∇×F` with the wheel icon. On `either` `∮` and `∯` join under them.
  On `memorized` the s00 grey formulas return and recolor in full. On `next_` everything dims and a single
  `∇·∇f = ∇²f` writes on. On `laplacian` it holds, then fades to black over the tail.
- **Why it explains:** the opening's two places are now readable at a glance; that is the payoff.
- **Beats:** `back` `div_map` `warm_spot` `here_curl` `green_swirl` `div_asks` `curl_asks` `either` `only_bound`
  `memorized` `symbols` `next_` `laplacian` `physics`
- **Layers:** shader (lic) · Taichi PointsLayer · FieldLayer ×2 · manim.

## Build order
Ch-by-Ch, each ending with `aion still` on the key beats → read PNGs → `aion audit 008 --design` → `aion preview`:
1. Infrastructure: `sims.py` (FlowSim bake), `shaders/lic.frag`, the rail/badge helpers in `shots.py`.
2. Intro (s00, s01) → Ch1 (s02, s03) → Ch2 (s04–s06) → Ch3 (s07–s09) → Ch4 (s10, s11) → Ch5 (s12) → outro (s13).

## Beat table
| beat | time | end | words |
|---|---|---|---|
| dust | 1.50 | 2.65 | Drop a pinch of dust |
| two_places | 5.26 | 6.02 | two places |
| spreads | 7.67 | 8.89 | the dust spreads apart |
| neighbors | 9.26 | 10.40 | Grains that started |
| welling | 13.44 | 13.84 | welling up |
| turn | 16.88 | 18.32 | the dust starts to turn |
| whirlpool | 21.30 | 22.22 | edge of a whirlpool |
| names | 23.34 | 24.86 | Those two motions have names |
| divergence | 25.29 | 26.75 | The first is divergence |
| curl | 27.13 | 28.40 | The second is curl |
| partials | 30.66 | 32.01 | row of partial derivatives |
| formula | 32.22 | 33.26 | Partial P |
| exam | 38.06 | 39.50 | right answers on the exam |
| never | 39.98 | 41.34 | picture never quite shows up |
| cut_preview ✂ | 41.83 | 41.83 | up. ✂ So |
| picture_first | 42.72 | 43.72 | put the picture first |
| question | 45.32 | 46.32 | a question you can ask |
| leaving | 48.66 | 49.36 | Is stuff leaving |
| turning | 50.72 | 51.36 | is stuff turning |
| map | 54.86 | 55.46 | you get a map |
| born | 55.70 | 56.74 | where the flow is born |
| spin | 60.02 | 61.42 | every hidden spin |
| straight | 62.82 | 63.81 | look perfectly straight |
| add_up | 66.52 | 68.13 | add up all those tiny answers |
| theorems | 68.52 | 69.80 | Two of the biggest theorems |
| arrows_page | 73.74 | 74.57 | arrows on a page |
| four_eq | 75.58 | 76.46 | the four equations |
| radio | 77.54 | 77.69 | radio |
| light | 79.18 | 80.00 | every beam of light |
| cut_ch1 ✂ | 84.03 | 84.03 | light. ✂ Pick |
| point | 85.06 | 85.52 | Pick a point |
| attach | 86.52 | 87.12 | attach an arrow |
| anything | 88.40 | 89.15 | could mean anything |
| wind | 89.76 | 90.75 | speed of the wind |
| gravity | 91.48 | 91.89 | gravity |
| charge | 92.08 | 93.43 | push of an electric charge |
| every_point | 94.36 | 95.83 | Do that at every point |
| vector_field | 96.50 | 97.30 | a vector field |
| rule | 97.64 | 98.58 | A rule that hands |
| weather | 101.21 | 101.72 | A weather map |
| town | 103.85 | 105.11 | Every town gets an arrow |
| write | 109.02 | 110.02 | To write it down |
| two_parts | 111.34 | 111.92 | two parts |
| call_P | 113.93 | 114.54 | we call P |
| call_Q | 116.35 | 117.06 | we call Q |
| depend | 117.52 | 118.14 | Both depend |
| F_eq | 119.42 | 120.70 | So the field is F |
| cut_flow ✂ | 124.32 | 124.32 | y. ✂ Arrows |
| hard | 124.82 | 125.92 | Arrows alone are hard |
| carry | 127.00 | 127.96 | let them carry something |
| sprinkle | 128.38 | 129.87 | Sprinkle dust everywhere |
| is_flow | 133.24 | 134.72 | Now the field is a flow |
| velocity | 135.82 | 136.98 | the velocity of the water |
| dust_shows | 138.18 | 139.14 | the dust shows you |
| company | 141.11 | 142.61 | Three flows will keep us company |
| away | 143.96 | 145.24 | every arrow points away |
| name_source | 146.24 | 147.29 | Call it the source |
| around | 148.63 | 149.96 | every arrow points around |
| whirl | 150.74 | 151.71 | Call it the whirl |
| saddle_in | 153.16 | 154.44 | water comes in from above |
| saddle | 157.15 | 158.34 | That one is a saddle |
| keep_eye | 159.30 | 160.34 | Keep an eye on the saddle |
| fool | 160.86 | 161.50 | going to fool us |
| cut_ch2 ✂ | 162.80 | 162.80 | minute. ✂ Here |
| first_q | 163.68 | 164.90 | Here is the first question |
| dye | 165.80 | 167.08 | a small circle of dye |
| area | 168.60 | 169.80 | what happens to its area |
| in_source | 170.88 | 171.86 | In the source |
| grows | 174.44 | 175.46 | The circle grows |
| tripled | 177.54 | 178.33 | nearly tripled |
| in_whirl | 179.46 | 180.37 | In the whirl |
| same | 184.36 | 186.32 | Its area stays exactly the same |
| now_saddle | 187.44 | 188.27 | Now the saddle |
| pulled | 189.42 | 190.50 | pulled out sideways |
| guess | 193.94 | 194.54 | make a guess |
| grow_shrink | 194.90 | 196.15 | Does the area grow |
| neither | 199.74 | 200.60 | It does neither |
| ellipse | 203.00 | 203.80 | thin ellipse |
| dramatic | 204.18 | 205.11 | It looks dramatic |
| stays_put | 208.92 | 210.11 | the area stays put |
| measures | 211.04 | 212.76 | That is what divergence measures |
| wild | 213.07 | 213.90 | Not how wild |
| swelling | 215.46 | 217.50 | how fast a tiny drop is swelling |
| positive | 218.95 | 219.74 | Positive means |
| negative | 221.00 | 221.82 | Negative means |
| zero | 222.80 | 223.58 | Zero means |
| cut_flux ✂ | 225.67 | 225.67 | it. ✂ To |
| to_formula | 226.19 | 227.88 | To turn that into a formula |
| square | 227.92 | 229.81 | shrink the drop to a tiny square |
| count | 230.00 | 230.96 | count the water crossing |
| out_in | 231.99 | 233.08 | Whatever flows out |
| lr | 236.06 | 237.01 | left and right edges |
| only_P | 237.78 | 239.42 | the sideways part of the arrows |
| bigger | 242.34 | 243.46 | a little bigger on the right |
| dPdx | 249.46 | 251.06 | the partial derivative of P |
| tb | 253.02 | 254.20 | The top and bottom edges |
| dQdy | 259.76 | 260.88 | gives partial Q |
| add_two | 262.47 | 263.31 | Add the two |
| del_dot | 264.95 | 266.30 | Del dot F equals |
| check | 270.40 | 271.73 | Check it on our three flows |
| chk_source | 272.09 | 273.76 | The source gives one plus one |
| chk_two | 274.13 | 274.43 | Two |
| chk_whirl | 274.82 | 276.00 | The whirl gives zero |
| chk_saddle | 277.12 | 278.44 | the saddle gives one |
| chk_zero | 279.33 | 279.80 | Zero |
| sees | 280.20 | 281.12 | The formula sees |
| cut_map ✂ | 283.23 | 283.23 | us. ✂ Now |
| color_plane | 285.50 | 286.12 | color the plane |
| warm | 286.43 | 286.98 | Warm where |
| cool | 288.53 | 289.14 | cool where |
| sources | 290.15 | 291.82 | The warm spots are sources |
| sinks | 293.15 | 294.78 | The cool spots are sinks |
| agrees | 296.18 | 297.17 | the dust agrees |
| spreads_warm | 297.70 | 298.82 | spreads out over the warm |
| crowds | 299.74 | 300.42 | crowds together |
| one_more | 302.25 | 303.29 | One more flow |
| matters | 303.48 | 304.36 | this one matters later |
| shrink | 307.56 | 308.99 | they shrink as you move outward |
| lamp | 309.88 | 310.72 | fading from a lamp |
| outward | 311.55 | 312.94 | Everything points outward |
| must | 313.21 | 314.54 | So the divergence must be |
| right_q | 315.30 | 315.53 | Right |
| dark | 318.41 | 319.72 | The map stays dark |
| except_pt | 321.08 | 322.24 | except the single point |
| circle | 323.35 | 324.32 | Look at a circle |
| twice | 326.28 | 327.31 | twice as wide |
| edge_long | 327.44 | 328.56 | its edge is twice |
| half | 331.08 | 331.66 | half as long |
| cancel | 332.07 | 333.87 | The two effects cancel |
| every_circle | 335.20 | 336.44 | crosses every circle |
| nothing | 336.71 | 338.00 | Nothing is created |
| one_point | 339.52 | 340.96 | comes from that one point |
| hold | 341.89 | 342.70 | Hold on to that |
| comes_back | 343.10 | 343.77 | It comes back |
| cut_ch3 ✂ | 344.83 | 344.83 | back. ✂ Now |
| second_q | 345.90 | 347.13 | Now the second question |
| paddle | 349.04 | 350.11 | a tiny paddle wheel |
| pinned | 350.37 | 351.04 | pinned in place |
| whirl_turns | 353.70 | 354.83 | whirl it turns |
| steadily | 355.15 | 355.87 | Steadily |
| same_rate | 357.58 | 358.58 | same rate no matter |
| river | 360.34 | 361.26 | Now a river |
| straight_right | 362.52 | 363.63 | points straight to the right |
| faster_top | 364.56 | 366.28 | water near the top moves faster |
| will_spin | 368.01 | 368.86 | Will the wheel spin |
| it_does | 372.00 | 373.13 | It does |
| top_pushed | 373.13 | 373.82 | The top paddles |
| clockwise | 375.90 | 377.37 | the wheel turns clockwise |
| still_spin | 377.69 | 379.67 | Straight arrows and still a spin |
| reverse | 380.70 | 381.68 | The reverse can happen |
| drain | 382.44 | 383.39 | Here is a drain |
| circles | 384.48 | 385.72 | go around in circles |
| pin | 386.99 | 388.40 | Pin a wheel anywhere |
| not_turn | 389.60 | 391.20 | it does not turn |
| float_ | 391.20 | 391.68 | Let it float |
| around_drain | 393.20 | 394.56 | all the way around the drain |
| upright | 394.76 | 395.41 | stays upright |
| ferris | 396.48 | 396.99 | Ferris wheel |
| balance | 401.32 | 402.32 | balance out perfectly |
| so_curl | 403.35 | 404.74 | So curl is not about |
| tiny_wheel | 407.26 | 408.53 | whether a tiny wheel |
| how_fast | 410.55 | 411.38 | And how fast |
| cut_circ ✂ | 411.82 | 411.82 | fast. ✂ To |
| walk | 413.32 | 415.28 | walk once around a tiny square |
| add_push | 416.68 | 418.28 | add up how much the flow pushes |
| circulation | 420.56 | 421.58 | called the circulation |
| bottom | 422.61 | 423.74 | Along the bottom edge |
| P_helps | 426.38 | 426.99 | P helps you |
| top | 427.33 | 428.38 | Along the top |
| against | 429.82 | 430.86 | P works against |
| lose | 433.26 | 434.73 | you lose more than you gain |
| minus_dPdy | 436.42 | 437.53 | minus partial P |
| right_edge | 439.09 | 439.92 | On the right edge |
| left_down | 441.00 | 442.93 | on the left edge you walk down |
| dQdx | 444.64 | 445.81 | gives you partial Q |
| together | 447.39 | 448.09 | Put them together |
| curl_is | 448.33 | 450.02 | The curl is partial Q |
| per_area | 454.26 | 455.14 | per unit of area |
| check2 | 456.15 | 456.49 | Check it |
| c_whirl | 456.84 | 458.40 | The whirl gives one |
| c_two | 459.91 | 460.21 | Two |
| c_river | 461.08 | 462.08 | river gives zero |
| c_neg | 462.91 | 463.55 | Negative one |
| c_cw | 463.95 | 465.16 | Clockwise just like |
| c_zero | 466.44 | 467.88 | source and the saddle give zero |
| no_spin | 468.12 | 469.00 | No spin at all |
| cut_3d ✂ | 469.50 | 469.50 | all. ✂ In |
| three_d | 471.02 | 471.99 | a wheel can tilt |
| vector | 472.54 | 473.82 | the curl becomes a vector |
| axle | 474.66 | 475.50 | points along the axle |
| rhr | 477.66 | 478.46 | the right hand rule |
| fingers | 479.98 | 480.70 | Curl your fingers |
| thumb | 481.78 | 482.54 | your thumb points |
| flat | 484.12 | 484.88 | Our flat curl |
| out_page | 488.79 | 489.52 | out of the page |
| shorthand | 490.98 | 491.86 | a famous shorthand |
| del_list | 492.85 | 493.78 | Write del |
| dxdydz | 495.86 | 498.43 | Partial x partial y partial z |
| dot | 499.30 | 500.02 | its dot product |
| cross | 502.58 | 503.73 | its cross product |
| trick | 505.46 | 506.38 | a memory trick |
| meaning | 507.72 | 508.98 | The meaning is the drop |
| cut_ch4 ✂ | 511.50 | 511.50 | wheel. ✂ So |
| tiny | 513.36 | 514.54 | everything has been tiny |
| zoom | 515.76 | 516.12 | zoom out |
| region | 516.98 | 518.55 | Take a whole region |
| squares | 518.74 | 520.13 | cut it into small squares |
| outflow | 521.38 | 522.95 | has its own outflow |
| div_area | 523.01 | 524.75 | Its divergence times its area |
| neighbors2 | 526.36 | 528.09 | two neighboring squares |
| shared | 528.23 | 529.24 | Whatever leaves the first |
| out_one | 531.84 | 532.48 | Out for one |
| edge_cancels | 534.96 | 536.04 | that edge cancels |
| every_inside | 538.06 | 539.21 | every inside edge |
| every_one | 539.52 | 541.13 | Every single one cancels |
| boundary | 543.02 | 544.35 | the ones on the outer boundary |
| adding | 545.68 | 547.20 | adding up the divergence inside |
| cubes | 552.45 | 554.01 | the squares become little cubes |
| surface | 555.04 | 556.96 | becomes a closed surface |
| div_thm | 556.96 | 558.54 | This is the divergence theorem |
| lamp_pays | 560.10 | 561.69 | the lamp from earlier pays off |
| square_dist | 564.74 | 566.30 | square of the distance |
| every_sphere | 567.26 | 568.34 | crosses every sphere |
| sits | 571.06 | 572.41 | sits at that one point |
| point_charge | 575.22 | 575.78 | a point charge |
| cut_stokes ✂ | 576.80 | 576.80 | behaves. ✂ Curl |
| curl_adds | 577.27 | 578.74 | Curl adds up the same way |
| loops | 580.64 | 581.56 | its own little loop |
| meet | 582.96 | 583.95 | Where two squares meet |
| opposite | 586.32 | 587.45 | in opposite directions |
| cancel_again | 587.76 | 588.60 | They cancel again |
| outer | 589.67 | 591.30 | Only the outer loop survives |
| total_curl | 591.58 | 593.15 | The total curl inside |
| green | 595.68 | 596.70 | That is Green's |
| lift | 598.09 | 599.47 | Lift it into space |
| wire | 602.00 | 602.74 | a loop of wire |
| soap | 602.95 | 603.44 | like a soap |
| bubble | 604.40 | 605.20 | Push the film out |
| no_change | 606.32 | 607.72 | the answer does not change |
| only_wire | 608.01 | 609.33 | Only the wire matters |
| stokes | 609.67 | 610.76 | This is Stokes' |
| one_idea | 612.02 | 613.60 | Two theorems one idea |
| except_edge | 616.50 | 618.43 | everything cancels except the edge |
| cut_ch5 ✂ | 619.42 | 619.42 | edge. ✂ Now |
| four | 620.96 | 621.76 | those four equations |
| read_them | 624.72 | 625.28 | you can read them |
| div_E | 626.59 | 627.46 | Del dot E |
| charges | 629.74 | 631.38 | Electric charges are the sources |
| div_B | 633.98 | 634.92 | Del dot B |
| no_sources | 637.32 | 638.80 | no sources at all |
| never_end | 639.48 | 640.65 | never start or end |
| loop_back | 640.91 | 642.08 | They only loop back |
| curl_E | 642.88 | 643.82 | Del cross E |
| stirs | 648.38 | 650.05 | stirs up an electric whirl |
| magnet | 650.98 | 651.98 | a magnet near a coil |
| electricity | 656.22 | 657.26 | most of our electricity |
| curl_B | 659.03 | 660.00 | Del cross B |
| changing_E | 662.16 | 663.76 | a term for a changing electric |
| wrap | 665.36 | 666.16 | wrap themselves |
| together2 | 668.82 | 669.92 | the last two equations |
| travel | 675.20 | 676.15 | travel on its own |
| light2 | 676.63 | 677.84 | That is light |
| far | 680.50 | 681.59 | far from electricity |
| water | 681.86 | 683.94 | Water barely compresses |
| hurricane | 686.45 | 687.38 | a hurricane |
| patch | 688.66 | 690.28 | a giant patch of curl |
| cut_outro ✂ | 691.33 | 691.33 | curl. ✂ Let's |
| back | 692.60 | 693.44 | go back to the stream |
| div_map | 695.36 | 696.98 | Here is the divergence map |
| warm_spot | 700.60 | 702.14 | sits right on a warm spot |
| here_curl | 702.54 | 704.02 | And here is the curl |
| green_swirl | 706.66 | 707.78 | this green swirl |
| div_asks | 708.84 | 709.80 | Divergence asks |
| curl_asks | 713.38 | 714.20 | Curl asks |
| either | 716.10 | 717.32 | Add up either one |
| only_bound | 718.68 | 720.16 | only the boundary is left |
| memorized | 721.18 | 722.38 | The formulas you memorized |
| symbols | 726.46 | 727.46 | written in symbols |
| next_ | 728.44 | 729.12 | Next time |
| laplacian | 731.92 | 733.28 | called the Laplacian |
| physics | 736.48 | 738.32 | every equation in physics |
281 beats, 14 scenes, audio 741.24s
