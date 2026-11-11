# The Math That Shows You a Black Hole: storyboard

Audio: `assets/audio.wav` (duration: 591.88 s = 9:52, 1,655 words, about 168 words a minute)

Pacing (`voice.toml [pacing]`): 4 s silent lead-in, +0.5 s after each paragraph, +1.5 s between chapters,
2.5 s tail. Word cues are snapped to the real speech onsets. Full beat table at the end of this file.

## Visual system

| object | color token | meaning |
|---|---|---|
| rays of light, u = 1/r | `C.light` | the thing we follow all video |
| mass M, the term 3GM/c² u² | `C.mass` | what bends the path |
| Schwarzschild radius r_s | `C.horizon` | edge of no return |
| photon sphere, 1.5 r_s | `C.ring` | where light orbits |
| shadow edge, 2.6 r_s | `C.shadow` | the dividing aim distance |
| thrown-ball prediction | `C.newton` | the wrong-by-two answer |
| space grid / funnel | `C.grid` | the stage, never the subject |

Black background everywhere, no grain, no vignette. One focal point per frame. Each chapter's result
shrinks into a small corner badge that stays (r_s → funnel → equation → three fates), so progress is
visible without a spoken recap.

The one equation: `u'' + u = (3GM/c²) u²`, with `u` in `C.light` and the right side in `C.mass`.

## Scenes

### s00_cold_open · T.start → T.cut_intro  (0:00–0:14, 15 s)
- **Narration:** 4 s of silence, then "This is a black hole. Nobody painted it… placed there by a calculation."
  The same cinematic shot keeps running under the intro until about 0:46, so the black hole owns the first 45 s.
- **Visual idea (why it explains):** the finished result first, unexplained. Ray-traced hole with disk,
  photon ring and a lensed galaxy band; slow push-in (distance eased in log r) with a slight orbit.
- **Beats:** `black_hole`, `painted`, `calculation`
- **In / out:** fade up from black; the push-in settles into the intro's held frame (no cut).
- **Layers:** `BlackHoleLayer` (look GO) + Tonemap + Bloom(C.bloom)

### s01_intro · T.cut_intro → T.cut_ch1  (0:14–0:53, 39 s)
- **Narration:** "…one equation… you will be able to read that equation… this bright arc… not a second ring…
  one pixel at a time."
- **Visual idea:** promise inside 10 s. The equation appears soft and unexplained over the image. A thin
  outline traces the upper arc on "this bright arc" (opens the loop Ch5 closes). On the map sentence one
  gold ray enters frame, then the image dissolves into scanlines.
- **Beats:** `one_equation`, `read`, `arc`, `second_ring`, `not`, `single_ray`, `pixel`
- **In / out:** continuous from s00; out: the single ray stays and becomes Ch1's first object.
- **Layers:** `BlackHoleLayer` (held, `animated=False` where still) · manim (Eqn ghost, arc outline, ray)

### s02_trapped · T.cut_ch1 → T.cut_ch2  (0:53–2:29, 95 s)  — Ch1 Can light be trapped?
- **Narration:** ball → escape velocity (Earth, eleven km/s) → squeeze the mass → set v = c →
  r_s = 2GM/c² → Earth nine millimetres, Sun three kilometres → the factor-of-two plant.
- **Visual idea:** three launch arcs on a planet limb, computed Kepler trajectories, the third leaves.
  `v = √(2GM/r)` writes on; the planet shrinks while a speed dial climbs to c; the equation morphs into
  `r_s = 2GM/c²` (TransformMatchingTex). Earth collapses to a marble beside a 9 mm ruler tick.
  Plant: a grey Newtonian ray with a small "× 2 ?" tag, parked in the corner.
- **Beats:** `ball`, `faster`, `never`, `eleven`, `formula`, `squeeze`, `reaches_c`, `rs`, `nine_mm`,
  `three_km`, `edge`, `problem`, `factor_two`
- **In / out:** in from the ray; out: r_s badge to the corner.
- **Layers:** manim only (+ Glow on trajectories)

### s03_curved · T.cut_ch2 → T.cut_ch3  (2:29–3:42, 73 s)  — Ch2 Straight lines in curved space
- **Narration:** light always goes straight; gravity changes what straight means; flat sheet; mass;
  two rays; look from above.
- **Visual idea:** mode switch to 3D. A flat grid in perspective, two parallel gold lines. The grid sinks
  into Flamm's paraboloid `z = 2√(r_s (r − r_s))` (exact, one sink parameter). Two geodesics computed on
  the surface bend toward the mass. Camera tilts to top-down: the funnel flattens into the 2D picture
  (mass + bending ray) used for the rest of the video.
- **Beats:** `straight`, `always`, `means`, `sheet`, `side_by_side`, `mass_in`, `computed`, `two_rays`,
  `bend`, `nothing_pulled`, `above`, `what_curve`
- **In / out:** in: grid fades up; out: top-down ray picture carries straight into Ch3.
- **Layers:** manim (numpy-projected wireframe via `m.redraw`), Glow on rays

### s04_equation · T.cut_ch3 → T.cut_ch4  (3:42–5:45, 123 s)  — Ch3 The equation
- **Narration:** φ and r; u = 1/r; no mass → sine wave; u'' + u = 0; Einstein's one term; what the term
  does; Sun-grazing ray 1.75″; twice the thrown-ball answer; 1919; aim closer?
- **Visual idea:** left: the ray picture with a rotating radius arm (φ, r labels). Right: a live plot of
  u against φ. With M = 0 the plot is exactly `sin φ / b`. `u'' + u = 0` writes under it. Then the zero
  morphs into the `C.mass` term while M ramps up and the *same* ray bends (real ODE solution per frame).
  Sun test: counter runs to 1.75″, the grey Newtonian ray from Ch1 returns at half the angle (payoff).
- **Beats:** `phi`, `r`, `u`, `far`, `close`, `no_mass`, `sine`, `straight_eq`, `mass_back`, `new_term`,
  `that_is_it`, `u_squared`, `wakes`, `sun`, `arcsec`, `twice`, `eclipse`, `aim_closer`
- **In / out:** out: equation shrinks to the top edge and stays through Ch4 and Ch5.
- **Layers:** manim (two layers: static axes / moving ray)

### s05_fates · T.cut_ch4 → T.cut_ch5  (5:45–7:28, 102 s)  — Ch4 Three fates of a light ray
- **Narration:** far ray; aim closer (90°, U-turn); full loop; make a guess; it circles; u'' = 0 ⇒
  1.5 r_s; photon sphere; unstable; three fates; 2.6 r_s; shadow bigger than the hole.
- **Visual idea:** black disk with `C.horizon` rim; one exact ray whose aim distance slides inward
  (path recomputed per frame). Hold on the guess. Near-critical ray winds around; `C.ring` circle appears.
  Algebra in three morphs: cross out u'', `u = (3GM/c²)u²`, `r = 1.5 r_s`. Then a full fan of rays coloured
  by fate, and the `C.shadow` circle at 2.6 r_s.
- **Beats:** `far`, `closer`, `ninety`, `home`, `loop`, `guess`, `circles`, `where`, `cross_out`,
  `one_and_half`, `photon_sphere`, `pencil`, `outside`, `inside`, `three_fates`, `two_point_six`, `bigger`
- **In / out:** out: the fan rotates so the rays point at a camera icon (sets up Ch5).
- **Layers:** manim + Glow

### s06_image · T.cut_ch5 → T.cut_outro  (7:28–9:08, 100 s)  — Ch5 Building the image
- **Narration:** camera, pixels; run light backwards; shadow; bent sky; add the disk; front band; ray over
  the top → back of the disk; "that is the arc"; underside; photon ring; brighter side.
- **Visual idea:** left third: side view with camera, hole, edge-on disk and backward rays. Right: the
  image, filled in scanline by scanline. Stages: shadow only → celestial grid wrapped into rings (look K)
  → disk added. For the arc, one ray in the side view goes over the top and lands behind; a link line ties
  it to its pixel in the image, which lights up. Then the side view fades and the full image takes the frame.
- **Beats:** `camera`, `pixel`, `backwards`, `fall_in`, `shadow`, `stars`, `rings`, `disk`, `front`,
  `over_top`, `back`, `the_arc`, `underside`, `thin_line`, `brighter`, `reason`
- **In / out:** out: holds on the complete image.
- **Layers:** `BlackHoleLayer` (reveal / sky / disk switches) · manim side view · Tonemap + Bloom

### s07_outro · T.cut_outro → T.end  (9:08–9:51, 43 s)
- **Narration:** 2019 telescope; a map of where straight lines go; four-clause lesson; real holes spin.
- **Visual idea:** our own image blurred to telescope resolution (labelled as a simulation), then sharp
  again. The four corner badges light in turn on the four clauses, then fly into the image. Final shot:
  the cold-open framing with the three radii drawn faintly. On "spin", the shadow outline skews slightly.
- **Beats:** `telescope`, `as_said`, `map`, `radius`, `idea`, `path`, `picture`, `spin`, `next`
- **In / out:** fade to black.
- **Layers:** `BlackHoleLayer` + Blur track · manim badges

## As built (differences from the plan above)

All eight scenes are built and tile the audio. Where the build differs from the scene notes above:

- **Cold open / intro:** the push-in finishes inside the cold open (distance 120 M → 50 M); the hole slides left
  while the equation sits top-right, blurred, and sharpens briefly on "read that equation". The arc outline is the
  computed image of the disk ring at 16.5 M.
- **Ch1:** three radial throws under inverse-square gravity; a live escape-velocity readout climbs to 299,792 km/s
  during the squeeze. Earth and Sun shrink to dots labelled 9 mm and 3 km (not to scale).
- **Ch2:** Cartesian grid sinking into the exact Flamm surface; two geodesics on it; on the top-down view the
  funnel paths crossfade to the true light path (the funnel alone gives half the bend).
- **Ch3:** ray panel left, u(φ) plot right, equation below; two bars (u and the new term) on the plot's scale.
  The Sun test exaggerates the 1.75″ bend to about 8° so it is visible.
- **Ch4:** aim distances for the 90° bend, U-turn and full loop are solved exactly (3.084, 2.678, 2.601 r_s).
  Captured rays use the theme's red (`C.bad`).
- **Ch5:** camera at 30 M; the image sits in a 16:9 panel beside a side view and grows to full frame at
  "one side is brighter". The sky stage uses the lensed coordinate grid. New theme token `C.disk`.
- **Outro:** the 2019 picture is our own render, blurred and labelled as a simulation (no telescope image is
  used). The lesson is three badges (r_s, funnel, equation) that fly into the image. The lopsided shadow of a
  spinning hole is a labelled sketch, not computed.

Disk gas: `disk_rate` and `disk_t0` keep the Keplerian shear from winding the texture into grooves.

## Deeper looks (added for undergraduate viewers; the main story works without them)

Audio is now 732.46 s (12:12). Both sections were added as `> [insert]` narration, spliced into the
existing audio. Each opens by telling casual viewers they can coast, and shows a small ring that
empties over its duration.

### s03b_spacetime · T.cut_deep1 → T.cut_ch3  (3:43–5:06, 83 s)
- **Idea:** a spacetime map, r across and t up, in ingoing Eddington–Finkelstein coordinates. Colour is the
  clock rate √(1 − r_s/r) (tokens `C.time_fast/mid/slow`); dashes climb each world-line at that rate.
  Light cones stand upright far away, tip toward the mass, have a vertical outer edge at r_s, and point
  wholly inward inside. Then the Schwarzschild metric, ds² = 0 for light, and the light-path equation.
- **Layers:** `spacetime.frag` shader · manim (cones, clocks, axes, equations) · starfield

### s05b_hill · T.cut_deep2 → T.cut_ready  (8:45–9:42, 57 s)
- **Idea:** the radial motion as a ball on V(r) = (1 − r_s/r)/r², peak 4/27 at 1.5 r_s. The ball's level is
  1/b² with b read out live: b = 4 turns back (escape), b = 2.60 balances on the summit (orbit), b = 2.35
  rolls over into the hole (capture). An inset draws the matching ray round the hole for each run.
- **Layers:** manim · starfield

### s05c_ready · T.cut_ready → T.cut_ch5  (9:42–9:49, 7 s)
- **Idea:** "one equation, three fates": the equation, three rays round one hole, then the shadow circle
  chapter 5 starts from. (This was the end of s05 before the hill was inserted.)

## Beats (from `uv run aion beats 004 --md`)

| beat | time | end | words |
|---|---|---|---|
| black_hole | 4.00 | 5.49 | This is a black hole |
| painted | 6.36 | 7.22 | Nobody painted |
| photographed | 7.81 | 8.90 | Nobody photographed |
| calculation | 11.96 | 13.58 | placed there by a calculation |
| cut_intro ✂ | 14.53 | 14.53 | calculation. ✂ And |
| one_equation | 17.30 | 18.22 | one equation |
| where_to_go | 21.38 | 21.93 | where to go |
| read | 25.12 | 26.33 | read that equation |
| stranger | 30.90 | 32.07 | stranger than it seems |
| arc | 32.86 | 33.82 | this bright arc |
| second_ring | 36.46 | 37.62 | a second ring of gas |
| is_not | 40.49 | 40.75 | not |
| one_disk | 41.02 | 42.30 | only one flat disk |
| single_ray | 48.56 | 49.46 | a single ray of light |
| pixel | 51.76 | 52.94 | one pixel at a time |
| cut_ch1 ✂ | 53.92 | 53.92 | time. ✂ Let |
| trapped | 57.07 | 58.28 | Can light be trapped |
| ball | 59.16 | 59.84 | Throw a ball |
| faster | 61.70 | 62.67 | Throw it faster |
| never | 66.68 | 67.71 | never returns at all |
| escape_v | 69.08 | 69.89 | escape velocity |
| eleven | 71.64 | 72.56 | eleven kilometres |
| formula | 74.24 | 75.26 | The formula is short |
| more_mass | 80.82 | 81.67 | More mass |
| squeeze | 88.65 | 89.56 | Squeeze a mass |
| keeps_rising | 93.72 | 94.44 | keeps rising |
| reaches_c | 95.96 | 97.13 | reaches the speed of light |
| set_equal | 98.11 | 99.34 | Set the escape velocity |
| rs | 103.42 | 104.38 | Two times G |
| schwarzschild | 108.50 | 109.61 | Schwarzschild radius |
| nine_mm | 112.36 | 113.16 | nine millimetres |
| marble | 114.75 | 115.65 | pressed into a marble |
| three_km | 117.24 | 118.00 | three kilometres |
| edge | 124.58 | 125.69 | edge of no return |
| problem | 126.76 | 128.60 | this argument has a problem |
| no_mass | 130.76 | 132.03 | light has no mass |
| should_bend | 136.36 | 137.16 | should bend |
| factor_two | 140.87 | 142.15 | factor of exactly two |
| remember | 142.67 | 143.48 | Remember that number |
| better_idea | 146.54 | 147.26 | a better idea |
| cut_ch2 ✂ | 149.37 | 149.37 | is. ✂ Here |
| straight | 152.60 | 153.82 | travels in a straight line |
| always | 154.23 | 154.80 | Always |
| means | 159.02 | 160.60 | change what straight means |
| sheet | 161.49 | 162.88 | Picture a flat sheet |
| side_by_side | 169.60 | 170.37 | side by side |
| mass_in | 174.02 | 175.10 | put a mass in the middle |
| stretch | 178.74 | 179.98 | distances stretch |
| computed | 182.66 | 183.94 | Its shape is computed |
| two_rays | 188.87 | 189.80 | Send two rays |
| never_turns | 194.52 | 195.51 | never turns left |
| bend | 198.60 | 199.79 | bend toward the mass |
| nothing_pulled | 200.58 | 201.34 | Nothing pulled |
| above | 208.48 | 209.97 | look from directly above |
| picture2d | 212.59 | 213.56 | A mass at the centre |
| what_curve | 219.38 | 220.34 | Exactly what curve |
| cut_ch3 ✂ | 222.62 | 222.62 | follow? ✂ To |
| phi | 228.60 | 229.14 | called phi |
| r | 231.12 | 231.58 | called r |
| trick | 233.06 | 233.46 | one trick |
| u | 238.93 | 239.59 | Call it u |
| far | 240.90 | 241.66 | far away |
| close | 243.74 | 244.62 | comes close |
| mass_away | 247.00 | 247.80 | take the mass away |
| sine | 254.84 | 255.64 | pure sine wave |
| rises | 255.87 | 256.76 | It rises |
| peaks | 258.09 | 258.33 | peaks |
| famous | 262.75 | 264.26 | famous little equation |
| straight_eq | 270.78 | 271.85 | U double prime |
| mass_back | 274.64 | 275.62 | bring the mass back |
| one_place | 278.40 | 280.12 | exactly one place |
| new_term | 282.92 | 283.84 | Three times G |
| that_is_it | 288.19 | 289.63 | That is it |
| every_image | 291.22 | 292.39 | every black hole image |
| u_squared | 295.56 | 296.60 | contains u squared |
| tiny | 298.28 | 299.20 | u is tiny |
| wakes | 306.04 | 306.76 | wake up |
| test | 308.98 | 310.41 | Let us test it |
| sun | 311.82 | 313.02 | grazing the edge of the Sun |
| arcsec | 315.30 | 316.46 | one point seven five |
| coin | 318.62 | 319.58 | small coin |
| twice | 322.32 | 323.36 | exactly twice |
| eclipse | 326.08 | 326.93 | nineteen nineteen |
| shifted | 331.24 | 332.08 | had shifted |
| aim_closer | 340.33 | 341.62 | What happens when we aim |
| cut_ch4 ✂ | 345.95 | 345.95 | closer? ✂ Here |
| far_ray | 349.48 | 351.07 | passing far from it |
| closer | 353.70 | 354.39 | Aim closer |
| ninety | 356.25 | 357.19 | Ninety degrees |
| home | 361.34 | 361.70 | heads home |
| loop | 365.56 | 366.28 | a full loop |
| guess | 369.45 | 370.54 | make a guess |
| circles | 377.33 | 378.18 | It circles |
| where | 385.58 | 386.22 | tells us where |
| perfect_circle | 387.25 | 387.79 | perfect circle |
| cross_out | 393.43 | 394.29 | Cross that term out |
| one_and_half | 398.18 | 399.06 | one and a half times |
| photon_sphere | 402.12 | 402.88 | photon sphere |
| pencil | 407.71 | 408.06 | pencil |
| outside | 410.78 | 412.10 | slightest bit outside |
| inside | 413.58 | 414.89 | slightest bit inside |
| three_fates | 419.44 | 420.13 | three fates |
| escapes | 420.50 | 421.19 | It escapes |
| orbits | 421.50 | 422.20 | it orbits |
| captured | 423.04 | 423.48 | captured |
| two_point_six | 429.52 | 430.24 | two point six |
| bigger | 435.82 | 436.58 | bigger than the hole |
| everything | 442.72 | 443.40 | everything we need |
| cut_ch5 ✂ | 448.08 | 448.08 | picture. ✂ Put |
| camera | 449.11 | 449.78 | Put a camera |
| each_pixel | 451.19 | 451.78 | Each pixel |
| backwards | 460.44 | 461.50 | run the light backwards |
| start_ray | 461.73 | 462.52 | Start a ray |
| fall_in | 469.98 | 470.81 | fall into the hole |
| shadow | 475.34 | 476.08 | form the shadow |
| stars | 480.84 | 481.83 | distant stars |
| rings | 490.08 | 491.08 | wrapped into rings |
| disk | 492.14 | 493.33 | Now add the disk |
| front | 498.84 | 499.56 | front of the disk |
| follow_ray | 504.06 | 504.62 | follow a ray |
| over_top | 508.02 | 509.02 | bends over the top |
| back | 514.74 | 515.62 | back of the disk |
| the_arc | 517.49 | 518.48 | That is the arc |
| same_disk | 520.77 | 521.95 | The same disk |
| underside | 524.50 | 525.52 | the underside |
| thin_line | 528.42 | 529.42 | one more line |
| circled | 531.90 | 533.10 | circled the photon sphere |
| brighter | 535.72 | 536.68 | one side is brighter |
| rushing | 539.24 | 540.56 | rushing toward the camera |
| reason | 545.84 | 547.26 | Every feature has a reason |
| cut_outro ✂ | 548.57 | 548.57 | now. ✂ In |
| telescope | 550.71 | 551.72 | a telescope the size |
| showed | 557.04 | 557.48 | It showed |
| as_said | 560.50 | 561.82 | Just as the equation said |
| map | 566.54 | 568.41 | a map of where straight lines go |
| l_radius | 570.81 | 571.60 | A speed limit |
| l_idea | 572.98 | 573.92 | Curved space gave |
| l_path | 575.06 | 576.08 | One extra term |
| l_picture | 577.36 | 578.81 | the path gave us the picture |
| left_out | 579.78 | 580.70 | One thing we left out |
| spin | 581.13 | 582.49 | Real black holes spin |
| lopsided | 586.26 | 586.78 | lopsided |
| next_video | 588.34 | 589.81 | the next video |
