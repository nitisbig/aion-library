# Performance on this machine (AMD A6-9225, 2 cores, Radeon R4, 3.7 GB RAM)

Measured with aion 2.0.0.dev0. Numbers are steady state, after shader compilation (the first frame takes about 1 s).

| workload | resolution | ms / frame |
|---|---|---|
| s01 demo: gradient + Manim text/shapes + bloom + vignette (scene average, holds included) | 1920×1080 | **31** (≈ 32 fps) |
| same scene, plain `manim -qh` (Cairo, Scene.play) | 1920×1080 | ≈ 200 |
| s02 demo: shader + Glow + MathTex + camera zoom | 1920×1080 | 72.5 |
| typical preview frames | 854×480 | 25–28 |
| 40k particles + field + cloth + bloom + grain | 1280×720 | ≈ 96 |
| hold frames (nothing changes) | any | ≈ 0 (previous frame reused) |
| changed frame, gradient only (comp + readback) | 1920×1080 | 37 |
| + Bloom / Glow / Blur(4) / Grade / Lens / ZoomBlur | 1920×1080 | +35 / +51 / +35 / +10 / +14 / +17 |

So aion renders the same Manim content about 6× faster than plain Manim, mostly because:
holds skip rasterization, the background/fx run on the GPU, and Manim only rasterizes the vector layer.

Effect costs are the main lever on changed frames: a full Bloom + Lens finish roughly doubles the frame cost.
Optimising the blur pyramid (half-res prefilter, fewer levels) is an open item.

## Other timings
- `aion plan` on a 10-minute narration: 31 s the first time (decode + silence scan), cached afterwards.
- Workers: with ~0.8 GB free RAM, `suggested_workers()` returns 1. Each worker holds its own GL context, Manim
  and LaTeX state, and the rule allows one worker per 0.75 GB free. Add `-j 2` only when `aion doctor` reports enough free memory.

## Budget guide for a 1080p60 final (10 min ≈ 36 000 frames)
At 50 ms/frame average that is ≈ 30 min. Heavy shader/sim scenes at 100+ ms/frame dominate, so preview them
with `--range` and render the final in the background.
