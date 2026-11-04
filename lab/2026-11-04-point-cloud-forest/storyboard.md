# Point Cloud Forest: 30 s hobby scene (exploration)

A night forest made only of **points**, floating in pure black. The camera travels through it as if
someone were walking a LiDAR scanner down a path: trunks, branches, leaves, ferns, and the ground all exist
only as millions of tiny glowing dots. Sweeps of the scanner "paint" the forest into existence. Wind moves
the canopy, fireflies drift, and at the end the whole forest lifts off into the sky as dust.

**Look:** pure black background (`#000`, as asked; a hobby piece, not channel style). **No text at all.**
After Effects grade: point-size bokeh DOF with rack focus, speed ramps, bloom, light-wrap glow on
the scan front, subtle chromatic aberration at the frame edges, ACES tonemap, split tone, vignette, grain,
and a slight camera handheld drift.
**Length:** 30.0 s · 60 fps · 1800 frames. Final 1920×1080, previews 854×480 @ 30 fps.

## Why this is a different piece from the splat city

The city drew sorted, alpha-blended Gaussians. This one is **additive points**, the real look of LiDAR /
photogrammetry captures. Order-independent blending means **no per-frame depth sort**, so we can afford
~3–5M points on the R4. That is the budget that makes a forest read: leaves need density.

## Engine choice

| Need | Tool | Why |
|---|---|---|
| Procedural forest geometry | **numpy + scipy** (seeded) | Trees grown by **space colonization** (Runions 2007): branching that looks organic rather than L-system-regular. Trunk/branch cylinders sampled with a bark-noise radius; leaf clusters at branch tips; terrain from fBm noise; ferns, grass tufts, fallen logs, rocks, a stream. Each point gets position, normal, a "material" id, a wind weight (0 at the roots → 1 at the leaf tips), and an intensity like a LiDAR return |
| Point rasterizer | **moderngl** on the Radeon R4: `GL_POINTS`, size from perspective + **circle of confusion** (out-of-focus points grow into soft discs and dim by 1/area, i.e. true bokeh DOF *per point*, not a post blur), additive blend into an f16 target | Order-independent, so no sort. Per-point animation (wind sway, scan reveal, dissolve) runs in the vertex shader |
| Wind | vertex shader: layered sine + noise displacement × wind weight | Free per frame; the canopy breathes |
| Fireflies, mist, falling dust | small extra point sets, CPU-simulated (numpy) with curl noise | A few thousand points, cheap |
| AE post: bloom, scan glow, CA, ACES, split tone, vignette, grain | **moderngl** post passes | Reuse the Kawase bloom / grade passes from the earlier labs |
| Encode | **ffmpeg** + **tqdm** ETA bar, resumable segments | Same as the other labs |

Not used: **Manim** (no text or equations; Cairo on 2 CPU cores can't push millions of points),
**pyvista** (renders points well but can't do per-point bokeh DOF, additive HDR, or vertex-shader wind),
**skia** (nothing 2D needed). No downloaded scan: a procedural forest stays deterministic and licence-free,
and we control the reveal.

**Budget:** ~3–5M points. Measure s/frame at 480p from stills before the long render. If fill rate
(big bokeh discs) is the bottleneck, cap the CoC size and skip far points under a brightness threshold.

## Shot list (30.0 s)

| # | Time | What the viewer sees | Camera | AE touch |
|---|---|---|---|---|
| 1 | 0.0–4.0 | Black. A few fireflies blink. A thin horizontal **scan line** sweeps across the ground at the viewer's feet, and where it passes, the forest floor appears as dots: moss, roots, leaf litter | Low, near the ground, almost still; tiny handheld drift | Very shallow DOF: the foreground is sharp, everything beyond is soft bokeh discs |
| 2 | 4.0–9.0 | **The scan expands.** A spherical scan front (a glowing shell) grows outward from the camera. Trunks rise out of the dark as it passes; branches, then leaves fill in. Behind the front points settle from bright white to their resting colour | Slow rise to eye height, gentle push forward | Glow on the scan front, rack focus pulls out to infinity as the forest appears |
| 3 | 9.0–17.0 | **The walk.** Travel down a winding path between trunks. Ferns and trunks slide past close to the lens as big soft discs, the canopy sways in the wind, fireflies cross the frame | Forward dolly along a spline, slight banking on the curves; speed ramp slow → fast (~13 s) → slow | Foreground bokeh, motion streaks on the fast part, CA at the edges |
| 4 | 17.0–22.0 | **The stream.** The path opens onto a clearing with a stream. The water is a flowing band of points that streams downhill; its reflections are a dimmer mirrored copy of the trees. Mist (drifting low points) hangs over it | Slow crane up and arc around the clearing | Bloom on the water sparkle, longer focal length feel (narrow FOV) |
| 5 | 22.0–26.0 | **The giant tree.** A huge old tree on the far bank. The camera rises up its trunk, through the canopy; leaves pass the lens as a blizzard of out-of-focus dots | Vertical climb, slow rotation around the trunk | Near-freeze speed ramp at the moment we break through the leaves |
| 6 | 26.0–30.0 | **Above the forest.** The camera clears the canopy: the whole forest below as a sea of points under the black sky. A wind gust starts at the edges and the points lift off as drifting dust, rising like a reverse snowfall, until only a soft glow remains, then black | Pull up and back, ease into a hold | Fade to black on the last 0.8 s |

At most ~3 things change at once. Nothing pops: every point fades/grows in with easing.

## Look options (stills first, side by side, pick one)

| Look | Feel |
|---|---|
| **A: Moonlit** | Cool silver-white points, cyan accents on wet surfaces, warm amber fireflies. Calm, cinematic |
| **B: LiDAR spectrum** | Points coloured by height (deep blue at the ground → teal → green → yellow at the canopy tips), the classic scan-viewer look, but desaturated and graded. Techy |
| **C: Bioluminescent** | Mostly dark-green/teal forest with glowing magenta and cyan moss, fungi, and flowers. Avatar-like, saturated |

## Files (planned)

| File | Role |
|---|---|
| `forest.py` | Seeded terrain, path spline, stream, space-colonization trees, ferns, rocks, logs → point arrays (pos, colour, intensity, wind weight, material). Prints stats |
| `timeline.py` | Camera spline (PCHIP keys + speed ramp), focus distance, the scan fronts, gust/dissolve, as functions of t |
| `shaders/points.vert`, `points.frag` | Projection, wind, scan reveal, CoC point size + bokeh disc, dissolve |
| `shaders/*.frag` | Bloom, streaks, composite/grade |
| `render.py` | `still`, `looks`, `video` subcommands, tqdm ETA, resumable ffmpeg segments → `out/` |
| `NOTES.md` | Results, timings, what worked |

## Render plan

1. Contact sheet: one still per shot in all 3 looks at 480p → you pick a look. Report s/frame.
2. 480p30 preview of the whole 30 s.
3. 1080p60 final in the background, once the preview is approved.
