# Bridge Architecture: 30 s hobby scene (exploration)

**Subject:** Tower Bridge, London (1886–1894; Horace Jones & John Wolfe Barry), which is
what most people picture when they say "London Bridge". The actual London Bridge
(1973) is a plain three-span concrete box girder with very little to animate.

**Look:** black background, no text. Glowing line art drawn in 3D, with a slow cinematic
camera, bloom, a little motion blur and film grain: an After Effects "blueprint
construction" look.
**Length:** 30.0 s · 60 fps · 1800 frames · final 1920×1080, previews 854×480 @ 30 fps.

## The idea the animation explains

Tower Bridge *looks* like a stone castle, but it's a **steel machine dressed in stone**:
1. Steel frame towers stand on two river piers.
2. The two side spans hang from **suspension chains** anchored at the shore.
3. The chains pull the tower tops inward, toward the river. The **high-level walkways**
   tie the two tower tops together and hold that pull in tension.
4. The central road is two **bascules** (counterweighted leaves) that rotate up to
   86°, pivoting inside the piers.

The viewer should come away understanding the structure, not just the silhouette.

## Real proportions (metres, used to build the geometry)

| Element | Value |
|---|---|
| Total length | 244 |
| Tower height (above pier) | 65 |
| Central opening between towers | 61 |
| Side suspension spans | 82 each |
| Walkway height above high water | 44 |
| Bascule leaf length | ~30.5 each, opening to 86° |
| Suspension chain shape | parabola (uniform deck load), computed with numpy |

## Shot list

| # | Time | What we see | Why | Camera |
|---|---|---|---|---|
| 1 | 0.0–3.0 | Black. A single glowing waterline draws outward from the centre, with a faint shimmer of reflection below it. | Sets the ground plane | Static, low, front-on |
| 2 | 3.0–8.0 | Two piers rise from the water. The steel skeletons of the towers draw bottom-up (columns, then bracing, then floors), staggered left to right. | Steel first: this is the real structure | Slow push-in, slight rise |
| 3 | 8.0–13.0 | Gothic stone outlines (turrets, pointed roofs, arched windows) trace *over* the steel in a warmer, dimmer colour, and the steel stays visible beneath. | "Castle" is a skin | Slow orbit to 3/4 view |
| 4 | 13.0–18.0 | The walkways extend across between the tower tops. Shore anchorages appear, then the chains sweep up as parabolas to the tower tops, and hangers drop down to the side decks. | The suspension system | Continue orbit, pull back |
| 5 | 18.0–22.0 | Light pulses run along the chains toward the towers and along the walkways (amber = tension). The walkways brighten as they "catch" the pull. | Load path: the walkways are ties | Hold, gentle drift |
| 6 | 22.0–27.0 | The bascules rotate open to 86° on eased motion. Cutaway: the counterweights swing down into the piers. | The machine | Low angle, slow dolly toward the centre |
| 7 | 27.0–30.0 | Bascules close, the camera pulls back to a hero 3/4 shot, and everything holds, then fades to black. | Resolve | Pull back, then fade out |

At most ~3 things change at once. Every element draws on (stroke reveal along its
length) and nothing pops in.

## Engine choice

**moderngl (GPU, headless on the Radeon R4) for everything.** Reasons:
- Manim's Cairo renderer is CPU-only. On 2 cores, a 3D scene with ~thousands of segments plus
  glow at 60 fps would take hours, and Manim has no real bloom or motion blur.
- In a shader, the AE look (HDR additive glow, multi-pass bloom, grain, vignette,
  subtle chromatic aberration) is cheap and per-pixel.
- pyvista could do shaded meshes, but the line-art "construction" look and draw-on reveal
  are much easier to control in our own shaders.

Pipeline:
1. **Geometry (numpy):** the bridge built as 3D polylines from the proportions above.
   Each polyline has a `group` (pier / steel / stone / walkway / chain / hanger / bascule)
   and an arc-length parameter `s ∈ [0,1]` for draw-on.
2. **Line renderer (moderngl):** polylines expanded into camera-facing quads with
   analytic anti-aliasing. Per-group uniforms set `reveal`, colour, intensity, and the bascule
   rotation. Additive blend into an RGBA16F target.
3. **Post (shaders):** bloom (6-level down/up chain), light motion blur (accumulating 4
   sub-frames), vignette, grain (seeded), slight lens chromatic aberration.
4. **Timeline (Python):** keyframed tracks with eased curves (`smootherstep`, ease-out-expo)
   for reveals, camera spline, and bascule angle. Deterministic.
5. **Output:** raw frames piped to ffmpeg (`libx264`, CRF 16, yuv420p) under a `tqdm` bar
   with ETA (per CLAUDE.md).

## Palette (lab only, may be promoted into style.py later)

- Background `#000000` (pure black, as requested; this departs from the style guide)
- Steel `#58C4DD` cyan (the existing `ACCENT`)
- Stone `#C9B79C` warm stone, dimmer
- Tension pulses `#F4A259` amber
- Water `#2A6F97` (the existing `GRID`), low intensity

## Before the full render

Render three **look variations of the hero frame (t≈20 s)** side by side for comparison:
- **A. Blueprint:** cyan steel + stone line art, strong bloom (the plan above)
- **B. Gold hologram:** monochrome warm gold, thinner lines, heavier glow + grain
- **C. Night photo-real-ish:** dim filled stone silhouettes with rim-lit edges + glowing lines

Then do a 480p30 preview of the full 30 s, then the final 1080p60 render in the background.

## Decision (after the look test)
**Hybrid** was chosen: look A (blueprint x-ray) through the build, load path and bascule
cutaway. Then C's solid stone dissolves in bottom-up from 25.5–27.5 s while the bascules
close, and the hero ending holds on the solid bridge.
