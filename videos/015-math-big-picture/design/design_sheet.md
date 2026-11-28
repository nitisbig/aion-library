# Fundamentals of Math: The Big Picture: design sheet

Rendered reference: `design/style_frames/01_cold_open.png` … `08_map_lit.png` (one look frame per chapter, picked from
`plan/scenes.yaml`), plus `design/components_card.png` (a chapter card) and `design/components.png` (the furniture at
true size). They are rendered through aion itself (theme, LaTeX, Manim rasteriser, GPU compositor) at 1920×1080, and
every value on them is computed. Rebuild them with `uv run python videos/015-math-big-picture/design/style_frames.py`
(all frames, or pass frame numbers). Tokens live in `design/tokens.json`, written by
`uv run python videos/015-math-big-picture/scripts/export_tokens.py`, which also runs the palette checks below
(`--check` only checks). `theme.py` is the single source of truth for colour; `plan/scenes.yaml` is the source of
truth for what each scene shows.

The look is the channel's **Classic** style: pure black, crisp unglowed lines, Computer Modern for every glyph, key
words only. No bloom, glow, blur, vignette or grain. The quality comes from exact geometry, continuity, eased motion
and holds.

## Signature ideas
1. **One circle, six lenses.** THE circle (`C.circle`, warm white, stroke 5) is in every chapter, always the same
   object: the needle-tip trace, x² + y² = 25, the unit circle, the loops on the torus, the disk that unrolls, the hub
   of the map. Warm white keeps it apart from plain text.
2. **The Map of Math is the spine.** Six nodes on a ring around the circle. At every chapter end the hero object
   shrinks into its node, the node lights, new links draw, and the ring turns 60° so the next pillar arrives at
   6 o'clock and opens into its chapter card. Six turns make a full turn: the group C6 of Chapter 3 is the map's own
   motion.
3. **One hue per pillar, everywhere.** A pillar's hue is its node, its card glyph, its equation terms and its visuals.
   When branches meet, each object keeps its own branch's hue (Ch6: the rectangle is Space, the arch is Change, the
   width π is Quantity, the throws are Uncertainty), so colour says which branch is speaking.
4. **The needles bookend the video.** One seeded stream (seed 1777, placement seed 1778) drives the cold open, the
   Ch6 floor, the (θ, x) dots and the convergence plot, and returns in ch7_s03. Same boards, same throws.
5. **Euler's identity assembles in pillar hues** at the hub: e Change, i Structure, π Quantity, 1 and 0 Foundations.

**Signature shots** (hold 1.5–2.5 s each): the tips tracing the circle (co_s01) · six nodes appearing (in_s04) · each
map turn · the gap at the deepest zoom (ch2_s02) · the expansion cancelling to i (ch3) · a loop snagging on the torus
(ch4) · the rings unrolling into the triangle (ch5_s06) · the arch filling and the sticks sliding to the centre
(ch6_s04) · e^{iπ} + 1 = 0 at the hub (ch7) · six arcs closing into one circle (out_s01).

## 1. Stage
- 16:9. Draft 1920×1080 at 30 fps; master 3840×2160 at 60 fps, SDR Rec.709 (plan D14). World frame 14.22 × 8 units;
  **1 unit = 135 px at 1080p** (270 px at 4K). All sizes below are world units or Manim sizes, so they hold at 4K.
- Background `C.bg` #000000, flat. No `Glow`, `Bloom`, `Blur`, `Lens` or grain.
- Margins: nothing is drawn beyond the BASE margin (0.45 u, 61 px). **Text and HUD stay inside the safe inset
  (0.71 u, 96 px, the DS safe-margin).** `aion audit --design` checks only the 0.45 margin, so check the inset by eye.
- Fixed corners: mini-map top-right; e·i·π tracker top-left (ch3_s05 to ch7_s02); lower thirds bottom-left; the
  takeaway on the bottom band, centred. Keep these clear in every scene that shows them.
- The Classic grid (`C.grid` over `C.grid_minor`, white `C.axis`) appears only where coordinates matter: Ch1 (the
  circle as a set), Ch3 (the complex plane), Ch5 (the exponential curve). Never under the map.

## 2. Palette (`theme.py`; scenes use `C.<role>` only)
| role | hex | from DS | contrast on #000 | object |
|---|---|---|---|---|
| `foundations` | `#7EB7E7` | hue-blue `#5FB6FF`, ΔE00 4.0 | 9.81 | sets, logic, ∈, set-builder braces, the point that joins the set, the inside tint |
| `quantity` | `#FFDC84` | hue-gold `#FFD17E`, ΔE00 4.0 | 15.82 | π as a quantity (the locked estimate, the width tick π, the π of 2/π), 22/7, 355/113, √2, the inscribed square |
| `structure` | `#A77FFF` | hue-violet `#B58CFF`, ΔE00 4.1 | 7.12 | rotations e^{iθ} and their arcs, i, the group C6 and its progress arc, quaternions |
| `space` | `#1FE0AB` | hue-teal `#36D6B0`, ΔE00 4.0 | 12.31 | χ = V − E + F, the torus mesh, rubber-band shapes, the Tube map, the (θ, x) rectangle |
| `change` | `#FF9A3B` | hue-orange `#FF9F3D`, ΔE00 1.7 | 9.94 | d/dr, the rings and strips (two tints: opacity 1 and 0.6), e, slopes, the sine arch and its area |
| `uncertainty` | `#FF5DA7` | hue-pink `#FF6FA8`, ΔE00 3.4 | 7.38 | P, the needles, the dots of the throws, running shares and estimates |
| `circle` | `#F4EFE0` | (warm white) | 18.27 | THE circle in every chapter, the hub, the unrolled base 2πR |
| `map_off` | `#5A606B` | (dim slate) | 3.32 | unlit nodes, the ring track, unlit chords, empty tracker slots, the floorboard cracks. **Graphics only, never text** |
| `alert` | `#FF5A4E` | hue-red, unchanged | 6.82 | **once**: the p/q parity clash struck through in ch2_s04 |
| `text` / `muted` | BASE `#FFFFFF` / `#A6A6A6` | | 21.0 / 8.63 | text, operators, digits / tick numbers, axis names, HUD labels |
| `grid` / `axis` / `frame` | BASE `#1FA2DC` / `#FFFFFF` / `#BDBDBD` | | 7.26 / 21.0 / 11.18 | Classic plane; the border of `panel()` |
| `faint` | BASE `#3A3A3A` | | 1.85 | the solid fill of Hamilton's stone card (ch3_s07), nothing else |
| `grid_minor` | BASE `#0F3E4D` | | 1.82 | decorative only |

**Why the hexes are not the DS hues as given.** With the six DS hues the pillars collapse for colour-blind viewers
(CIEDE2000, Machado 2009 at full severity): Foundations/Structure 2.6 under deuteranopia and 7.6 under protanopia,
Space/Uncertainty 3.9 (deutan), Quantity/Change 15.1 in normal vision and 8.8 (deutan), Foundations/Space 8.2 and
Change/Uncertainty 9.0 (tritan); the circle sat 9.7 from Space. No single swap to an unused DS hue fixes it, and no set
of six of the nine DS hues passes either (best: orange, gold, lime, teal, blue, pink, still 6.2 short). So each pillar
keeps its DS hue family and moves the least (differential evolution over L\*, C\*, h; at most 4.1 ΔE00):
Foundations calmer (chroma 44 → 30) and a touch more cyan; Quantity lighter and yellower; Structure darker and more
saturated; Space lighter, more saturated and greener; Change barely moves; Uncertainty darker, more saturated and a
touch more magenta. **No hue swaps.**

**Checks** (all pass; `export_tokens.py` prints them and stores them in `tokens.json`):
- WCAG contrast on #000: every text colour ≥ 4.5:1 (lowest: Structure 7.12); graphics-only tokens ≥ 3:1 (map_off 3.32).
- Pillar separation, CIEDE2000, minimum over the 15 pairs: **normal 20.7** (Quantity/Change), **deutan 10.5**
  (Space/Uncertainty), **protan 10.9** (Quantity/Space), **tritan 10.6** (Foundations/Space; Change/Uncertainty 10.6).
  Targets 20 and 10.

| pair | normal | deutan | protan | tritan |
|---|---|---|---|---|
| foundations/structure | 21.1 | 10.6 | 14.0 | 25.7 |
| foundations/space | 34.6 | 28.8 | 34.7 | 10.6 |
| quantity/change | 20.7 | 10.8 | 14.4 | 18.3 |
| quantity/space | 34.2 | 18.9 | 10.9 | 43.4 |
| space/uncertainty | 82.0 | 10.5 | 37.3 | 73.4 |
| change/uncertainty | 43.2 | 26.7 | 44.2 | 10.6 |
| structure/uncertainty | 24.6 | 26.4 | 14.6 | 31.5 |
| (the other 8 pairs) | ≥ 45 | ≥ 19 | ≥ 15 | ≥ 27 |

- THE circle against every pillar, all four conditions ≥ 10: nearest are Space (protan 10.6, deutan 11.2) and Quantity
  (tritan 12.6).
- Neighbours that never carry meaning alone: circle/text 6.0–7.6 (the circle is a stroke-5 shape, text is glyphs);
  grid/foundations 5.8–9.7 (so Foundations objects on the grid are filled dots or full-stroke shapes, never hairlines);
  alert/change deutan 9.1 and alert/uncertainty tritan 7.2 (ch2_s04 has no orange or pink on screen).
- Colour is never the only cue: each pillar also has a ring position and a glyph.

**Opacity, in aion's linear-light compositor.** Translucency reads much stronger here than in an sRGB editor, so the
plan's percentages map to lower tokens:
| token | value | use (plan wording) |
|---|---|---|
| `opacity-fill` | 0.06 | set tints (the inside of the circle, overlapping disks), a lit node's disk; the ch4_s03 disk ("15 percent") |
| `opacity-region` | 0.10 | the one shaded region a beat is about: the area under the sine arch (ch6_s04, "30 percent") |
| `opacity-dim` | 0.30 | old equation lines (dimmed, never deleted), dots outside a region, needles that miss; ch2_s04 "dimming to 40 percent" (0.4 still reads bright; at 0.3 white text keeps 7:1) |
| `opacity-floor` | 0.40 | the cold-open floor after "no circle" (co_s01, "dims to 40%") |
| `opacity-ghost` | 0.25 | the ghost of a previous state in a morph (the Ch3 symmetry ghosts) |
| `opacity-chord` | 0.85 | lit chords (a lit ring arc between neighbours: 0.9) |

Inside **one** Manim layer Cairo blends in sRGB, so a translucent fill over another shape of the same layer comes out
about 11× darker than over the stage. A tinted disk that must also hide what is under it (a lit node over its chords)
uses the solid colour `tint(hue, 0.06)` at opacity 1 (`style_frames.py`). Dark orange reads as brown: keep Change
fills at `opacity-region` or below, and keep the second ring tint at opacity 0.6, not lower.

## 3. Typography (all Computer Modern via LaTeX)
Measured: Manim `font_size` ≈ rendered cap px at 1080p (28 → 27 px, 48 → 46 px, 72 → 69 px). Minimum 28 for anything
read.
| token | face | how | size | use |
|---|---|---|---|---|
| math-hero | CM roman | `Eqn` / `MathTex` | 72–96 (52 beside its visual) | the one hero equation of a beat |
| math-working | CM roman | `Eqn` | 48 | derivations, worked examples, counts |
| math-label | CM roman | `MathTex` | 34–40 (min 28) | point and tick labels: (3, 4), 22/7, π/3 |
| glyph | CM roman | `MathTex` | 44 in a node (≤ 1.5 × node radius wide), 36 in the tracker, 96 on a card | ∈ π e^{iθ} χ d/dr P |
| label | CM sans | `Tex(r"\textsf{…}")` | 30–34 | key words and tags (inside, on, outside), axis words, takeaway words |
| caps-name | CM small caps | `Tex(r"\textsc{…}")` | 32–36 | lower thirds `Name · year` (34), pillar names beside nodes (32) |
| caps-card | CM small caps | `\textsc` | 64–80 | the chapter card's pillar name (80), "How it connects", the title lockup |
| caps-eyebrow | CM small caps | `\textsc` | 28–30 | the key-idea eyebrow (28, `C.muted`), a small header over a panel |
| readout | CM sans digits | `\textsf` in `\makebox` columns | 34 (HUD) to 48 | counters: throws, crossings, 2N/H, flips |

- Do not use aion's `Label` or `Title` here: they set Inter and Space Grotesk through Pango. Use the `sans()` and
  `caps()` helpers in `style_frames.py`.
- Key words only: a tag is at most four words; the takeaway at most four words plus one equation.
- Labels that sit on the grid get a black backing (`backed()`, pad 0.04–0.06 u) so grid lines never cut glyphs.
- Lower thirds: `\textsc{Name}\enspace$\cdot$\enspace\textsc{year}` at 34, bottom-left on the inset, a 0.9 u muted
  rule (stroke 2) 0.16 u above. The longest in the plan, "G.-L. Leclerc, Comte de Buffon · 1777", is 7.1 u wide;
  "I. Newton · G. W. Leibniz · 1680s" writes its inner middot as `$\cdot$` too.
- Write π, ·, ≤ and dashes in text as `$\pi$`, `$\cdot$`, `$\le$`, `--`: the TeX template rejects those Unicode
  characters.
- Counters: CM digits share one width, so figures are tabular for free. Thousands get a thin space (30 331). Put the
  label and value of a row in one `Tex` with `\makebox` columns, and place rows on fixed baselines (the digits'
  bottoms), not with `arrange`, so descenders do not shift rows.

## 4. Equations
- **One new equation per beat.** It writes on its beat (`at=`), left side first, then term by term.
- **Terms take the colour of their visuals** (`Eqn(colors={…})`): the braces and ∈ in Foundations, π in Quantity
  when it is the number, i in Structure, χ in Space, the d/dr side and e in Change, P in Uncertainty, the circle's own
  equation x² + y² = 25 in `C.circle`.
- Derivations: one line at a time, `TransformMatchingTex` so shared terms travel; colours persist from line to line.
  **Older lines dim to `opacity-dim` and are never deleted** within a scene; a derivation column has a fixed frame.
- Hero equation: alone in its area, 72–96 when it is the subject, 52 when it sits beside its visual (the set-builder
  hero at 52 is 6.5 u wide). Equations sit to the right of their visual; stacks are left-aligned.
- The video's one `C.alert`: the clash "p even, q even" struck through in ch2_s04, with the plan's single low tap.
- Gotcha: `Eqn` isolates substrings, so isolating one letter ("i") colours every i. Colour such a term by index
  (`hero[-1][-1]` in frame 4).

## 5. Motion language
| token | duration | ease | use |
|---|---|---|---|
| lead | 0.15 s | | motion lands on the beat and starts this early (`at=`) |
| micro | 0.3 s | `smooth` | fades, highlights, a tag or lower third in/out, a glyph appearing |
| standard | 0.8 s | `easy_ease` | moves, transforms, a term arriving, a dot sliding, a hero shrinking into its node, a link drawing |
| hero | 1.5–2.5 s | `easy_ease` | the needle slide (2.0, co_s01), the map turn (1.8), node → card (1.5), rings unrolling |
| stagger | 50 ms | | between members of a group, unless the plan gives its own (below) |
| hold | 1.5–2.5 s | | after every signature shot |
| camera push | ≤ 1.15×, 2–3 s | `easy_ease` | payoffs and node openings only; pull-backs are free (co_s01 8 %, in_s02 20 %, ch3_s03 15 %) |

- **Banned:** linear motion, `out_back`, `out_elastic`, spring pops, shake, `ZoomBlur`, wipes. Things arrive with
  `easy_ease` and settle; nothing overshoots.
- **The plan's own timings win** where it gives them: staggers of 120 ms (in_s02 fragments) and 60 ms (ch2_s03
  midpoints, ch5_s06 rings); the in_s05 preview turn, 1.2 s each way; the out_s01 pull-back, 3 s. One exception: in_s05
  asks for a 1.2× push into the Foundations node; keep the camera at 1.15× and let the node's own scale-up into the card
  carry the rest.
- **The plan's verbs in the Classic look:** a *pulse* is scale 1 → 1.08 → 1 over 0.4 s, `smooth` each way; a *flash*
  is a micro rise to full opacity and back; *pop in* (in_s02) is a micro fade with scale 0.9 → 1, no overshoot;
  *springs back* (ch4_s02) is a standard `easy_ease` return; *glows* (ch2_s02 gap tag, ch6_s04 arc, ch7_s02 identity)
  is a colour change plus a step to stroke 5 or a pulse, never a `Glow` layer.
- Counters change value per frame (`steps`), never tween between numbers. Clocks (the needle rain rate) are clocks,
  not eases.
- At most about three things change at once. The ch2 log zoom is a redraw of the number line per frame (`m.redraw`),
  not a camera move, so ticks stay crisp at every scale.
- **The cold open's last line** (frame 1): the needles leave the floor in order of their angle θ, spread over the
  2.0 s slide (this replaces the plan's 15 ms stagger, which would take minutes over thousands of needles). Each slides
  its centre to the circle's centre, keeping its angle, and stretches from the board width to the circle's diameter
  (length eased by e³, so it stretches as it lands). Its two tips land at θ and θ + π, so two pens draw the circle in
  half a turn: the same half turn of directions that turns gold in ch6_s04. A landed needle fades over the next 0.3π
  of sweep, quadratically to zero, so a short fan trails each pen. The HUD stops at throw 30 331 (19 309 crossings),
  the first time the seeded stream reads 2N/H = 3.1416.

## 6. Transitions
**The signature move, at every chapter boundary** (chN_s07 into the next chapter's s01; each scene's `map_update`
in `scenes.yaml` says which node lights, which links draw and which card opens):
1. The chapter's hero callback shrinks into its node (standard).
2. The node lights: stroke 3 in its hue, solid tint fill, glyph, name (micro).
3. The chapter's links draw node to node, two-hue gradients (standard, 50 ms stagger).
4. Silent beat: the camera pulls back to the full map and the ring turns **+60° counter-clockwise** (1.8 s
   `easy_ease`), bringing the next pillar to 6 o'clock.
5. That node opens into the chapter card (1.5 s): the node scales up into the card's ring while the map fades out;
   a push of at most 1.15× rides along. The card holds about 2 s, then shrinks back into the node (standard) and the
   chapter starts around THE circle.

**Inside a chapter:** a continuity morph (`Transform`, `TransformMatchingTex`), a camera pan along a plane, or a
**lens swap on the anchored circle**: the circle stays exactly where it is and only the drawing around it changes.
No wipes, no hard cuts mid-chapter, never a dissolve of the circle itself. The cold open's circle stays where it
formed and becomes the intro's centre. The map arrives in two steps: the dim ring and its faint chords in in_s02 (the
"streets" of the city), the six nodes in in_s04. Outro: six 60° arcs in the pillar hues join into one circle,
cross-fade to `C.circle`, and the lit map pulls back into a small emblem.

## 7. The Map of Math
- Ring radius **2.75 u**, node radius **0.4 u**, hub = THE circle, radius **1.375 u = R/2**. At R/2 the six skip-one
  chords are tangent to the hub (a hexagram around it) and the three diameters run behind it (black fill). The hub
  holds e^{iπ} + 1 = 0 at 50 (2.5 u wide inside a 2.75 u disk).
- Node k (order Foundations, Quantity, Structure, Space, Change, Uncertainty) sits at angle −90° − 60°·k + turn:
  Foundations at 6 o'clock, the rest clockwise (the plan's `ring_deg`). After chapter k the ring has turned 60°·k
  counter-clockwise, so chapter k + 1 is at 6 o'clock; after six turns it is home (C6).
- **Links** (`scenes.yaml` → `map_edges`, 15 in all, two-hue gradients via `set_stroke(color=[a, b])` plus
  `set_sheen_direction`): the 6 between ring neighbours light their track arc (stroke 2.4, opacity 0.9); the other 9
  (six skip-one chords and three diameters) draw as straight chords (stroke 2.4, opacity 0.85). Both stop 0.05 u
  clear of each node.
- Unlit: the track in `map_off` at 1.6. Unlit chords are hidden, except in the intro's dim map (in_s02–in_s03) and the
  in_s05 flash, where all 15 show in `map_off` at 1.6.
- Nodes: unlit = `map_off` ring (stroke 2.0) on black (the plan's "C.map_off fill" in in_s04 means this); lit = hue
  stroke 3.0, fill `tint(hue, 0.06)` (a dark tint of its hue: Structure "fills violet"), glyph in the hue. The name in
  small caps 32 in the hue: the four side nodes put it straight out (0.16 u gap); the 12 and 6 o'clock nodes put it
  beside the node toward +x, raised or lowered by 0.55 × node radius, so it clears the track and stays inside the inset.
- **Mini-map** (added by this design; not in the plan): top-right, centre (6.05, 3.0), radius 0.3. The ring in
  `map_off` 1.6; dots for the chapters done plus the current one in their hues (radius 0.062), the rest `map_off`
  (0.045); the current pillar ringed (0.125, its hue, stroke 2.2). It turns with the big map, so the current pillar
  sits at 6 o'clock. Shown from ch1_s01 to ch6_s07; hidden whenever the full map, a card or the hub is on screen.
- **e·i·π tracker** (top-left, loop L2): three slots of radius 0.25, 0.66 u apart, on the inset. An empty slot is a
  `map_off` ring; a parked glyph sits at 36 in its hue inside a ring of that hue (e Change, i Structure, π Quantity).
  All three park in ch3_s05; in ch5_s03 the e of the exponential flies into its slot; they leave in ch7_s02.
- **C6 progress arc** (loop L3: ch3_s03, ch7_s01): six 60° segments just outside THE circle, done turns in
  `C.structure`, the rest in `map_off`; ch3_s03 shows two of six, ch7_s01 closes it.

## 8. Components (true size in `design/components.png` and `components_card.png`)
- **Chapter card:** the node's ring scaled to radius 0.78 with the solid tint, glyph at 96 in the hue; the pillar name
  in small caps 80 (`C.text`) under it; the field in CM sans 36 (`C.muted`, e.g. "probability and statistics").
  Nothing else in frame. "How it connects" uses the same name style without a ring.
- **Lower third:** see §3. In and out with micro fades plus a 0.1 u rise; holds about 3 s.
- **Takeaway** (chN_s07, over the hero callback): at most four key words in CM sans 34, a short muted vertical rule,
  one equation at 48 coloured like its visual; centred on the bottom band (y = −2.79) with a thin muted rule above.
- **Key-idea panel:** `panel()` from `aion/components/linalg.py` (black inside, thin `C.frame` border), small-caps
  eyebrow "key idea" at 28 in `C.muted`, one equation at 48, one CM sans line at 32. The ch5_s03 savings card and the
  out_s02 end card use the same panel.
- **Hamilton's stone card** (ch3_s07, the plan's "flat stone-grey card"): a flat rectangle filled solid `C.faint`
  (#3A3A3A), no border, no shadow; the rule i² = j² = k² = ijk = −1 in CM roman 48 in `C.text` (11.4:1; `C.muted`
  4.7:1). Pillar hues stay off it (Structure would drop to 3.9:1).
- **Mini-map, tracker, map nodes, links:** §7.

## 9. The frames
| frame | scene | what it fixes |
|---|---|---|
| 01 cold open | co_s01, last line | the θ-ordered slide and two-pen trace; the floor at 40 %; pink needles; the CM-sans HUD with gold 3.1416 ≈ π. The unlit map is drawn only to show the hub's scale: co_s01 itself has no map |
| 02 Ch1 set | ch1_s04 | x² + y² = 25 on the Classic grid; only (3, 4) takes Foundations; older rows dimmed; inside/on/outside tags |
| 03 Ch2 gap | ch2_s02 + s04 | fraction ticks (height by denominator), π gold, a ×7 500 lens where 355/113 is the only fraction with q ≤ 120; the square, √2 ≠ p/q; lower third |
| 04 Ch3 rotation | ch3 (multiplying adds angles) | violet arcs on the unit circle, the hero product, the key-idea panel, the tracker |
| 05 Ch4 torus | ch4 (Euler characteristic) | PyVista torus in Space with its two loops in `C.circle`; V, E, F counted from the drawn mesh (128, 256, 128) |
| 06 Ch5 rings | ch5_s06 / s07 | 12 rings in two tints, the next ring cut at the top and uncurling, strips stacking into the triangle; the takeaway |
| 07 Ch6 needles | ch6_s03 / s04 / s05 | the floor (crossing needles full, misses dimmed), the (θ, x) rectangle in Space, the arch in Change, π in Quantity, P = 2/π ≈ 0.6366, 2N/H from 10 to 100 000 throws (3.1348 at 100 000) |
| 08 map lit | ch7_s02 / s04 | all 15 links, lit nodes, names, e^{iπ} + 1 = 0 in pillar hues at the hub |

## 10. Library gaps (not fixed in `aion/`; working versions are in `design/style_frames.py`)
1. **No CM text helpers.** `Label` and `Title` render Inter / Space Grotesk; this video needs `\textsf` and `\textsc`
   wrappers (`sans()`, `caps()`).
2. **No safe dim.** Manim's `set_opacity` on a shape with fill opacity 0 turns its fill on, and `set_fill` on a group
   cascades into children. `dim(mob, k)` scales each submobject's own stroke and fill opacity.
3. **No `tint(color, a)`.** A solid linear-light mix is needed because Cairo blends in sRGB inside one Manim layer.
4. **No gradient-stroke helper.** `gradient_line` sets `set_stroke(color=[a, b])` and `set_sheen_direction` along the
   segment; arcs need the same two calls.
5. **No map kit.** `map_of_math`, `minimap`, `tracker`, `chapter_card`, `lower_third`, the takeaway bar and
   `gradient_line` belong in a video-local module (for example `videos/015-math-big-picture/kit.py`) before the scenes
   are built; scenes must not import from `design/`.
6. **No `MeshLayer`.** PyVista renders off-screen to RGBA (2× supersample; premultiply before the LANCZOS downsample;
   zero the 3 border rows) and enters as `ArrayLayer(premultiplied=True)`.
7. **Skia arrays must stay premultiplied** (`kPremul_AlphaType`, `ArrayLayer(premultiplied=True)`); un-premultiplying
   faint strokes quantises their colour (purple fringes in the first frame-1 render).
8. **No tabular readout.** See §3 for the `\makebox` pattern.
9. **No Unicode in the TeX template** (π, ·, ≤, en dash fail in `Tex`); see §3.
10. **`aion audit --design` does not check the 96 px text inset**, only the theme margin (0.45 u).
11. **Seeded streams:** draw (x, θ) as rows (`rng.random((n, 2))`) so throw k is the same for every n; drawing two
    arrays of length n makes the stream depend on n.

## 11. Render notes
- `style_frames.py` renders each frame in its own subprocess, one at a time (2 cores, about 3.7 GB RAM). Each loads
  the theme through `load_video("015", …, only=["__none__"])`, builds one `@scene` and saves the frame at t = 5 s.
- Frame 5 renders the PyVista torus first, before aion creates its GL context in that process.
- Frames 1 and 7 draw needles with skia. The numbers on screen are asserted in the script (the 30 331 / 19 309 lock,
  355/113 alone in the lens), so a changed seed or range fails loudly.
- Run `export_tokens.py --check` after any colour change in `theme.py`; it exits 1 when a palette check fails.
