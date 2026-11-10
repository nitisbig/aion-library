# Lab: epicycles (video 003 pre-production checks), 2026-11-09

The four checks that `videos/003-fourier-series/storyboard.md` asks for before building scenes. All run on this machine (AMD A6-9225, Radeon R4, Mesa radeonsi).

## 1. Treble clef outline → **works**
- Source: **Noto Music** (`/usr/share/fonts/truetype/noto/NotoMusic-Regular.ttf`, SIL OFL, already installed), glyph U+1D11E. This replaces Bravura from the plan, so there's nothing to download.
- 4 contours: the outside plus 3 holes. `fourier.bridge` joins them into one loop, and the short out-and-back bridges read as part of the drawing.
- Promoted: `aion/drawings.py` → `treble_clef(n)` (centered, max |z| = 1).
- Convergence (`clef_convergence.png`), max error relative to the clef's radius:
  - 1 circle: 0.68 (a plain loop)
  - 5 circles: 0.38 (a rough blob)
  - 20 circles: 0.13 (it starts to read)
  - 50 circles: 0.035
  - 201 circles: **0.008**
- That matches the narration in S25 word for word ("one circle, a loop; five, a rough blob; by twenty you can see it").
- **Gotcha:** the drawing is centered, so c₀ = 0. Sort it with `order_terms(c, keep_zero_first=False)`; otherwise "1 circle" is the zero-radius c₀ and draws a dot.

Run: `uv run python lab/2026-11-09-epicycles/clef_preview.py`

## 2. EpicyclePlate on the GPU → **fast enough, but only after vectorizing**
Prototype: `epicycle_gl.py`, a moderngl additive renderer with 4× MSAA and the shared `post_gl.GlowFinish`.

The first version took 160–650 ms per frame. All of that time was numpy, not the GPU: a Python loop over rims, and re-summing the ink every frame. After vectorizing it, median times per frame were:

| | 200 circles | 500 circles |
|---|---|---|
| 854×480 | 24–48 ms | 27–36 ms |
| 1920×1080 | 37–50 ms | 44–52 ms |

A 15 s 1080p60 shot is about 45–60 s of plate time, before Manim compositing.

What made the difference:
- **The ink is sampled once per set of terms** (8,000 samples per loop, cached), and each frame takes a slice.
- **Rims are one batched strip**, and rims under 1.5 px are skipped.
- **Arms fade by length.** Without this, 200 overlapping joints near the pen bloomed into a white blob (seen in the first stills).

Ink styles for you to pick from: `ink_compare.mp4` (6 s, side by side) and `ink_compare.png`.
- **A · hairline:** a constant 2.2 px line, fading with age. Cleanest, reads as "light".
- **B · brush:** tapers from about 5 px at the pen to 1 px, with a soft glow at the head. The most "after-effects" look, and still readable on a phone.
- **C · dotted comet:** dashed old ink, with a solid glowing head. Distinctive, but the dashes flicker at 60 fps, and dashed lines already mean "ghost/target" in our style. **Not recommended.**

**40× zoom** (`zoom40x.png`): the ink needs **re-sampling near the pen when zoomed**. The cached 8,000 samples per loop become 17 px straight segments at 40×. To fix it, evaluate the last ~2 % of the loop fresh at high resolution while zoom > 4. Also pick the zoom target at a sharp turn (the bottom hook or the bridge corner), since that's where the last 50 circles visibly matter for S25's toggle.

Run: `uv run python lab/2026-11-09-epicycles/bench_plate.py`, then `… ink_clip.py`

## 3. pyvista off-screen spring → **works**
- VTK renders off-screen on the **Radeon R4** (OpenGL renderer string confirmed).
- Timing: 7 s setup, then about **75 ms per 1080p frame** with SSAA. S06's 15 s at 60 fps is about 70 s.
- Look (`pyvista_helix.png`): the gold tube with Phong shading (`ambient 0.35, specular 0.8`) on two dark glass walls, with the sine on the back wall and the cosine on the floor.
- PBR metallic made the gold muddy olive, because there's no environment map to reflect. Don't use it.
- For production:
  - Size the walls to the shadow curves; they currently overhang.
  - Pass the frames through `GlowFinish` so the bloom matches the other plates.
  - Export the camera matrix for Manim's `\sin t` / `\cos t` labels.
- The Manim 3D fallback isn't needed.

Run: `uv run python lab/2026-11-09-epicycles/pyvista_helix.py`

## 4. Taichi InkParticles → **works**
- 20,000 seeded sparks, with a divergence-free swirl drift and a cooling fade from gold to ember (`taichi_sparks.png`).
- Taichi picks **Vulkan on the R4**: **6.6 ms per step** including the readback. The CPU (x64) takes 7.1 ms, so either is fine.
- Determinism: `ti.init(random_seed=…)` plus a fixed emission ring buffer.
- To do for production: **emit along the pen's path between frames**, not at one point. The fast pen currently leaves visible gaps of separate dots at the head. Draw the points into the plate's own MSAA buffer (additive), so they share its bloom.

Run: `uv run python lab/2026-11-09-epicycles/taichi_sparks.py gpu`

## Promoted
- `aion/fourier.py`: series, FFT coefficients, spin-average, chain joints, square wave/loop, heat ring, Gibbs. Covered by `tests/test_fourier.py` (10 tests).
- `aion/drawings.py`: glyph outlines and `treble_clef()`.
- `aion/style.py`: the 003 palette (`INK FWD BWD STILL PHASE ARM RIM_OPACITY GHOST_LINE SPIKE HEAT_RAMP`).
- Next: `epicycle_gl.py` → `aion/components/epicycle_gl.py` as `EpicyclePlate`, a Manim `ImageMobject` driven by a state callback, like `SurfacePlate`. Add `project()`, the zoom re-sampling, the chosen ink style, and the particles.
