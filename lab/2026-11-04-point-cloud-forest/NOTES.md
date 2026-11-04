# Point Cloud Forest: 30 s hobby piece (exploration)

A night forest made only of points, in pure black, no text. A LiDAR-style scan paints the forest floor and then
the whole forest into existence. The camera walks a winding path, crosses a clearing with a stream, climbs a
giant tree through its canopy, and pulls up while a gust lifts the forest away as dust. Plan: `storyboard.md`.

```bash
uv run python lab/2026-11-04-point-cloud-forest/forest.py                        # build + stats (~20 s, cached in out/)
uv run python lab/2026-11-04-point-cloud-forest/render.py looks                  # out/contact_{A,B,C}.png
uv run python lab/2026-11-04-point-cloud-forest/render.py still --look A --t 2.6 13
uv run python lab/2026-11-04-point-cloud-forest/render.py video --look A --height 480 --fps 30     # preview
uv run python lab/2026-11-04-point-cloud-forest/render.py video --look A --height 1080 --fps 60    # final
ONLY_MAT=7 uv run python lab/2026-11-04-point-cloud-forest/render.py still --t 13 --tag _ferns    # debug one material
```
Renders are resumable (150-frame segments keyed by a hash of the code and settings).

## Pipeline
| File | Role |
|---|---|
| `forest.py` | Seeded world, ~4.5M points. Analytic terrain (sum of sines) with a flattened clearing and a carved stream; a winding path. 22 tree templates: 14 broadleaf trees grown by **space colonization** (pipe-model radii, root flare, bark furrows, leaf clusters at the tips) and 8 conifers (whorls of drooping needle branches). These are instanced ~410× with rotation/scale, with LOD by distance from the camera route (energy compensated). Giant 34 m tree with buttress roots. Ferns (arching fronds with pinnae), grass tufts, rocks + stepping stones, mossy logs with bracket fungi, mushrooms, flowers, mist, fireflies, and water stored as (x₀, lateral) |
| `timeline.py` | PCHIP camera keys per shot, handheld drift, banking from path curvature, a sim time τ that slows to 15% at the canopy break-through, focus/aperture/fog/exposure curves, scan line and sphere |
| `shaders/points.vert/.frag` | One `GL_POINTS` draw, **additive, so no depth sort**. All animation runs in the vertex shader: wind (sway + leaf flutter), flowing water, firefly paths and blinking, mist drift, the gust dissolve, the scan reveal with white flash and front glow. **Per-point bokeh:** size = max(base dot, circle of confusion `A·f_y·|1/focus − 1/z|`) with energy conserved, so out-of-focus points become dimmer soft discs with a slight rim. **Stream reflection:** a second draw of ~2.2M nearby points mirrored about the water plane, kept only if the ray to the mirrored point hits the stream (exact for a flat plane) |
| `render.py` | Kawase bloom → composite (zoom streaks, edge CA, ACES, split tone, vignette, grain) from the splat-city lab. Grain is scaled by luminance so the black stays pure `#000` |

## Numbers
| | |
|---|---|
| Points | ~4.5M (needles 0.44M, leaves 0.89M, ground+litter 1.3M, ferns 0.43M, bark+twigs 0.7M, giant tree 0.19M) |
| Speed @ 480p | 0.03–0.15 s/frame on the Radeon R4. A 900-frame 480p30 preview takes ~2 min |

## What worked
- **Additive points instead of sorted splats.** It is ~5× faster than the splat city with 4× the elements, and it looks right for LiDAR.
- **Energy = represented area × f_y²/z², capped.** The brightness of a surface stays independent of its point density and of the resolution. The cap keeps close surfaces reading as separate dots.
- **Per-point CoC bokeh** gives real rack focus for free: the macro floor shot, ferns sliding past the lens, the leaf blizzard.
- The **exact planar reflection test** in the vertex shader makes the stream mirror the trees and costs only one extra draw.

## What didn't (and the fixes)
- **Horizon bands.** Additive points pile up wherever many surfaces line up along the view: the ground at grazing angles, and especially the ferns lining the path, which all converge at the vanishing point. The fix multiplies energy by |n·view| (the true projected area), and low ground cover fades into the fog at 0.45× the distance.
- The mist got a world-size energy override, and along the path it formed a glowing band. Now only fireflies keep the override.
- The first version of the climb looked straight up into the black sky at the slow-motion moment. The camera now turns to look out across the canopy top as it breaks through.
- Zoom streaks during the fast aerial pull-back smeared everything into blobs, so streaks and CA are limited to the walk.
- Still open: canopies seen from above stack into hotspots (handled with an exposure dip from 24 to 27 s).
