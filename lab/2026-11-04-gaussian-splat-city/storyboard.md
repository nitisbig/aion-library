# Gaussian Splat City Tour: 30 s hobby scene (exploration)

A night city that exists only as **3D Gaussian splats**, floating in a black void. The camera flies a
drone tour through it: it starts as a sparse point cloud, *trains* into a crisp city, glides down an
avenue, orbits a hero tower, briefly shows what it is really made of (millions of anisotropic ellipsoids),
then dissolves back into drifting splats.

**Look:** black background, **no text**. After Effects grade: speed ramps, rack focus / DOF, bloom,
light-streak motion blur, subtle chromatic aberration at the edges, ACES tonemap, teal/amber split tone,
vignette, film grain.
**Length:** 30.0 s · 60 fps · 1800 frames. Final 1920×1080, previews 854×480 @ 30 fps.

## The idea the animation explains

A Gaussian splat scene (Kerbl et al., 2023) is not a mesh. It is a cloud of 3D Gaussians, each with a
position **μ**, a covariance **Σ = R S Sᵀ Rᵀ** (rotation + 3 scales → an oriented ellipsoid), an opacity α,
and a view-dependent colour (spherical harmonics). Rendering = project each ellipsoid to a 2D ellipse
(**Σ′ = J W Σ Wᵀ Jᵀ**), sort by depth, and alpha-blend front to back. The viewer should *see* that:
the city is soft blobs that read as hard architecture only once enough of them overlap.

## Engine choice

| Need | Tool | Why |
|---|---|---|
| Procedural city as splats: towers, window grids, streets, lamps, trees, cars, a landmark spire | **numpy** (seeded) | Real 3DGS parameters (μ, scales, quaternion, α, SH deg-1) generated per element. Deterministic |
| Splat rasterizer | **moderngl** on the Radeon R4: instanced quads, EWA projection of Σ in the vertex shader (the real 3DGS math, incl. the 0.3 px low-pass), Gaussian falloff in the fragment shader, premultiplied back-to-front blending | No CUDA here, so `gsplat` / the reference rasterizer are out. Writing it ourselves also lets us animate every Gaussian's parameters per frame |
| Depth sort | **numpy** `argsort` per frame → index buffer | ~1M splats sort in ~0.1 s on the A6. Fine offline |
| AE post: DOF, bloom, motion streaks, CA, ACES, split tone, vignette, grain | **moderngl** post passes | Adapted from the black-hole / cell-DNA composite |
| Encode | **ffmpeg** + **tqdm** ETA bar, resumable segments | Same as the other labs |

Not used: **Manim** (no text/equations; CPU Cairo can't do 1M soft blended splats), **skia** (nothing 2D),
**pyvista** (no proper sorted Gaussian blending; can't animate per-splat). No downloaded capture either:
a procedural city keeps it deterministic, licence-free, and lets us animate the "training" reveal.

**Budget:** target ~0.8–1.2M splats. Measure s/frame on the R4 at 480p from stills before the long render;
if fill rate is the bottleneck, cull splats under ~0.5 px and drop the far LOD.

## Shot list (30.0 s)

| # | Time | What the viewer sees | Camera | AE touch |
|---|---|---|---|---|
| 1 | 0.0–3.5 | Black. A sparse cloud of tiny white points fades up and drifts, the SfM seed points. The outline of a city slowly becomes readable in them | High, slow push-in from far above | Shallow DOF, grain, points twinkle |
| 2 | 3.5–8.5 | **Training reveal.** A wave sweeps out from the centre: each point inflates into a big, soft, blurry Gaussian, then the Gaussians split, shrink and sharpen into towers with lit window grids, glowing streets, lamps. Blurry → crisp, like watching optimization run | Descending 60° orbit | Bloom swells with the wave, focus pulls in as it sharpens |
| 3 | 8.5–16.5 | **Avenue fly-through.** Dive down to street level and glide between towers: windows stream past, sodium lamps, trees as clusters of leaf splats, cars as moving light trails (headlights white, tails red). Glass facades shift tint with view angle (SH) | Speed ramp: slow → whip (~10.5 s) → slow, slight banking | Motion streaks on the whip, CA at the edges |
| 4 | 16.5–22.0 | **Hero tower.** The avenue opens onto a plaza; the camera rises and orbits a tall spire tower, lights pulsing up its crown | Rising orbit, tight then wider | Rack focus from foreground lamp to tower |
| 5 | 22.0–26.0 | **What it's made of.** Time slows. The splats under a sweeping plane shrink to ~30% so gaps open and each one reads as a separate coloured ellipsoid (with a thin rim), showing their orientations hugging walls and edges. The plane passes; they grow back to solid | Slow push into a facade corner | Near-freeze speed ramp, extra bloom on the rims |
| 6 | 26.0–30.0 | **Dissolve.** Pull back up and away. The city's outer blocks lose opacity and their splats drift off into the void like floaters, until only a soft glowing core remains, then black | Fast exponential pull-back, ease into a hold | Fade to black on the last 0.8 s |

At most ~3 things change at once. Nothing pops: every splat change is an eased fade/scale.

## Look options (stills first, side by side, pick one)

| Look | Feel |
|---|---|
| **A: Neon night** | Dark buildings with warm/cool window grids, cyan and magenta signage accents, amber streets. Cyberpunk-adjacent but restrained |
| **B: Golden scan** | Warm amber/gold splats on black, monochrome-ish, like a lidar scan lit by sunset. Elegant, minimal |
| **C: Hologram** | Desaturated cyan splats with bright edges, the "digital twin" look. Crisp, less bloom |

## Files (planned)

| File | Role |
|---|---|
| `city.py` | Seeded procedural city → splat arrays (μ, scale, quat, α, SH). Block grid, tower heights, windows, lamps, trees, cars, hero spire. Asserts splat count and that Σ is positive-definite |
| `timeline.py` | Camera path (PCHIP keys + speed ramps) and every event as a function of t (reveal wave, ellipsoid sweep, dissolve) |
| `shaders/splat.vert`, `splat.frag` | 3DGS projection + Gaussian alpha, per-splat animated scale/opacity/colour |
| `shaders/*.frag` | DOF, bloom (Kawase), streaks, composite/grade |
| `render.py` | `still`, `looks`, `video` subcommands, tqdm ETA, resumable ffmpeg segments → `out/` |
| `NOTES.md` | Results, timings, what worked |

## Render plan

1. Contact sheet of 6 stills (one per shot) in all 3 looks at 480p → you pick a look. Report s/frame.
2. 480p30 preview of the whole 30 s.
3. 1080p60 final in the background, once the preview is approved.
