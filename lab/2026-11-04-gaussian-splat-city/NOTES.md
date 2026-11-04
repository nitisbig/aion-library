# Gaussian Splat City Tour: 30 s hobby piece (exploration)

A procedural night city made only of 3D Gaussian splats, flown as a drone tour in a black void. The plan is in
`storyboard.md`. Status: **look stills done (A/B/C)**. The 480p preview and 1080p final are not rendered yet.

```bash
uv run python lab/2026-11-04-gaussian-splat-city/city.py                       # stats + Σ positive-definite assert
uv run python lab/2026-11-04-gaussian-splat-city/render.py looks               # out/contact_{A,B,C}.png
uv run python lab/2026-11-04-gaussian-splat-city/render.py still --look A --t 2.5 6.5 11.5
uv run python lab/2026-11-04-gaussian-splat-city/render.py video --look A --height 480 --fps 30    # preview
uv run python lab/2026-11-04-gaussian-splat-city/render.py video --look A --height 1080 --fps 60   # final
```
Renders are resumable (150-frame segments keyed by a hash of the code and settings).

## Pipeline
| File | Role |
|---|---|
| `city.py` | Seeded city → ~1.07M static splats + ~7.3k car splats (489 cars). 210 buildings on a 90 m grid with setback tiers, 3 facade styles, shop fronts, neon, rooftop plant, antennas with beacons; a 300 m hero tower with a spire in a round plaza; streets, lane markings, zebras, 332 lamps, 170 trees, floaters. Σ is built as Σ_k s_k² a_k a_kᵀ from three axes and three σ's; lamp light baked per splat with a KD-tree |
| `timeline.py` | PCHIP camera keys, roll, the reveal wave, scan plane, dissolve radius, a sim-time τ that slows to 15% during the scan, zoom streaks from forward speed / height |
| `shaders/splat.vert/.frag` | Our own 3DGS rasterizer: SSBO of 5×vec4 per splat, one instanced quad each. EWA projection Σ′ = J W Σ Wᵀ Jᵀ, 0.3 px low-pass with mip-splatting opacity compensation, quad along the 2D eigenvectors at ±3σ. Per-splat animation of scale, isotropic blur, α, μ, and colour. Glass has a view-dependent lobe plus moving reflection bands |
| `render.py` | CPU frustum cull + numpy argsort back-to-front each frame → instance index buffer. Premultiplied over-blending into two f16 targets (colour, α-weighted depth) → depth resolve → **depth-buffer autofocus** (patch median, eased ~0.25 s) → DOF → Kawase bloom → zoom streaks, edge CA, ACES, split tone, vignette, grain |

## Numbers
| | |
|---|---|
| Splats | 1,064,746 static + 7,335 dynamic |
| Speed @ 480p | 0.12–0.7 s/frame, ~0.46 mean (sorting ~1M is a good part of it). 900 frames at 480p30 ≈ 7 min |
| No CUDA | `gsplat` / the reference rasterizer need CUDA; the moderngl version runs on the Radeon R4 at 430 core |

## What worked
- **The reveal reads as "training"**: seeds become large isotropic blobs (opacity, density ordered by a per-splat hash), then sharpen to anisotropic splats as the wave passes.
- **The scan shot**: shrinking Σ by 0.33 and drawing a 2σ rim makes the individual ellipses (and how they tile a wall) obvious.
- **Thin anisotropic rim splats on every edge** make the soft splat buildings read as hard architecture.
- **Autofocus from the depth buffer** fixed the close shots: target-based focus was focusing on the tower's centre, not its facade.

## What didn't (and the fixes)
- One Gaussian per window looked like a bokeh oval up close. Each window is now a 3×2 / 3×3 sub-grid of tighter splats (what densification would do on a real capture). This took the count from 0.6M to 1.07M.
- The first orbit around the tower passed *through* buildings (radius 94 m, plaza radius 56 m). The orbit now stays inside the plaza.
- Seed points too dense (60k) → a white blob. Now ~3.5% of splats, dimmer.
- Neon splats in the blob stages (reveal edge, dissolve) bloomed into pink clouds. Colour is now scaled down while a splat is still a blob.
- Still soft: in the scan shot, the upper tier sits in front of the focus plane and stays blurred.
