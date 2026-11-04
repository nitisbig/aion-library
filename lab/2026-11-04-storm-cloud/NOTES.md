# Storm Cloud: 30 s hobby piece (exploration)

A thunderstorm cell alone in black, built from **~5.9M particles**, lit only by lightning inside it. Flashes
crawl from cell to cell, backlight the turrets, glow through the volume, and build to a slow-motion
cloud-to-ground strike. No text. Plan: `storyboard.md`.

```bash
uv run python lab/2026-11-04-storm-cloud/cloud.py                  # particles + stats
uv run python lab/2026-11-04-storm-cloud/lightning.py              # grow the DBM bolts
uv run python lab/2026-11-04-storm-cloud/render.py looks           # out/contact_{A,B,C}.png
uv run python lab/2026-11-04-storm-cloud/render.py still --look A --t 10.05 23.66 --height 720
uv run python lab/2026-11-04-storm-cloud/render.py video --look A --height 480 --fps 30 --preset veryfast   # preview
uv run python lab/2026-11-04-storm-cloud/render.py video --look A --height 1080 --fps 60 --crf 16           # final
NO_GLINT=1 uv run python lab/2026-11-04-storm-cloud/render.py still --t 5.65 --tag _ng   # volume only (debug)
```
Renders are resumable (150-frame segments keyed by a hash of the code and settings). Scene data (particles,
bolts, noise) is cached in `out/scene_<hash>.npz`.

## Pipeline (per frame, all on the Radeon R4)
| Step | What |
|---|---|
| `cloud.py` | 3.7k blobs in a hierarchy (tower → column → turret → sub-turret, plus a base shelf, a sheared anvil and an overshooting top). Particles are sampled inside blobs and stored in blob-local coordinates. 5.1M cloud + 0.22M haze + 0.26M rain + 0.09M free droplets. Billowing = per-frame blob transforms on the CPU (towers rise, turrets swell and roll outward about horizontal axes); the particles follow in the shaders |
| `splat.comp` → `resolve.comp` | Particles atomically added into a 224×136×144 `r32ui` volume, then a 7-tap smooth → saturating density `1 − e^(−1.3c)`, flat base, the carved tunnel for the inside shot → `r16f` + mips |
| `illum.comp` | 112×68×72 RGBA light volume: per voxel, per light (4 line-segment lights), a 20-step Beer–Lambert march to the channel + 3 multiple-scattering octaves |
| `march.frag` (half res) | Density = blurred particle field thresholded by a billowy Worley fBm (crisp cauliflower edges, LOD from the pixel footprint), stretched noise in the anvil, analytic rain shaft. Two-lobe HG phase (silver lining), powder darkening, a 4-step fine self-shadow toward the brightest light. Outputs colour + the depth where T < 0.5 |
| `bolt.*` | DBM segments as instanced screen-space quads; white core + tinted halo; transmittance through the cloud per endpoint (core hidden, scattered glow still escapes) |
| `glint.*` | Every particle again as a droplet point lit from the light volume, hidden behind the march depth, per-point CoC bokeh |
| post | Light shafts toward the brightest flash, Kawase bloom, flash-frame exposure kick, zoom streak, CA, ACES, split tone, vignette, luminance-gated grain |

## Looks (`out/contact_{A,B,C}.png`)
| Look | Verdict |
|---|---|
| **A Storm noir** | Silver-white cloud, blue-white bolts. The most cinematic; used for the preview |
| **B Electric violet** | Strong and stylised; the inside shot turns fully purple, which some may find too much |
| **C Ember storm** | The amber underglow is too faint to read; nearly identical to A. Needs a stronger underglow to earn its place |

## Lightning (`lightning.py`)
Dielectric-breakdown growth on a 26-neighbour lattice with a charge-superposition potential
`φ_i = E·x_i − q Σ 1/r_ik`, `p_i ∝ exp((φ_i − max φ)/T)`. Each site stores its growth step, so the stepped
leader replays in slow motion and the return stroke lights the root→ground path. 2 s for all three bolts.

## What worked
- **Particles → volume → light.** The particles give structure and motion; the volume gives self-shadowing and
  scattering, which additive points alone can't. The same particles drawn as glints give the droplet bokeh.
- **Lights as line segments inside the volume** with multi-scatter octaves: a flash deep inside glows softly
  through the cloud, a flash near the surface rims it hard. Shot 3 (lightning glowing through the towers) and
  the inside shot are the strongest frames.
- **Speed:** mean 0.24 s/frame at 480p (0.2–0.45), volume rebuild (splat + resolve + light) ≈ 0.08 s of that.
  The full 900-frame 480p30 preview renders in ~4 min. Expect ~1.5 s/frame at 1080p → ~45 min for 1800 frames.

## What didn't (and the fixes)
- **DBM as first written** (Kim & Lin's averaged `Σ(1 − R₁/r)` with min–max normalisation) grew a bush that
  never reached the target in 6000 sites (164 s). The averaged potential barely screens the cluster interior.
  Coulomb screening + a Boltzmann choice fixed it: 0.7 s per bolt, realistic forks. A T/q sweep picked T=10, q=7.
- **Smooth "blob" clouds:** eroding the raw particle density only moved edges by a voxel. Thresholding a
  *blurred* density (mip 1.4) with noise moves the surface by up to ~1 unit, giving billows.
- **Diagonal hatching** on lit surfaces: interleaved-gradient-noise step jitter at half res. Replaced with a
  PCG hash + tent upsample, and finer steps (≤ 0.14), which also removed the step noise at crisp edges.
- **Moiré in wide shots:** fine noise octaves aliasing; fixed with explicit noise LOD from the pixel footprint.
- **Light shafts** turned the hero bolt into a dotted spray; shafts are now off during the strike.
- **Glints were invisible** at first: no droplets sat near the lens. Added 90k free droplets along the
  close-up camera route.
- The spider bolt was first placed above the frame and its light was 10× weaker than the flashes; moved it into
  the inside shot's view. The exit through the base looked into empty void: the camera now tilts up at the lit base.
- Still open: the towers in the wide shots are a little too round/bulbous; more turret levels or a stronger
  large-scale erosion would help. The rain shaft reads as a curtain of vertical bars.

## v2: Dusk squall line (`--scene dusk`, looks D1 Golden hour / D2 Afterglow)
A calm sunset version seen from cruising altitude: a ~75-unit squall line (19 main towers with two giant cells,
a back row, low foothill cumulus, a thick shared base, an anvil on each giant), **11.9M particles**, lit by a low
sun with soft lightning pulses deep inside the towers. The camera makes one stable glide along the line
(constant 1° bank, no shake). The cloud barely evolves (billow clock 0.12/s).
```bash
uv run python lab/2026-11-04-storm-cloud/render.py still --scene dusk --look D1 --t 8 22 --height 720
uv run python lab/2026-11-04-storm-cloud/render.py video --scene dusk --look D1 --height 480 --fps 30 --preset veryfast
uv run python lab/2026-11-04-storm-cloud/render.py video --scene dusk --look D1 --height 1080 --fps 60 --crf 16
```
- **Sun:** `illum.comp` also writes a sun-transmittance volume (28 steps toward the sun + multi-scatter
  octaves). `march.frag` adds a 4-step fine sun shadow, sky occlusion on the ambient (bright tops, dark
  undersides), an Earth-shadow line (D2: only the tops catch the pink light), a procedural sky (zenith →
  warm horizon, sun disk + halo) and a distant **cloud deck** below (a 36-step slab march with horizon haze).
- **Memory:** 3.8 GB RAM / 80 MB VRAM (the GPU uses system RAM). The massif is sampled in float32 (1.4 GB peak) and the
  particle array is cached as a memory-mapped `.npy`. Volume 440×98×130 at 0.2 units/voxel.
- **Speed:** ~0.3–0.4 s/frame at 480p; the 900-frame preview takes ~6 min.
- Iterations: a single tower looked like a toy; a continuous anvil "lid" over equal-height towers read as a
  bench with odd sunlit windows; straight backlight left the faces black. What fixed it: a skyline envelope with two
  giant cells, a camera above the mid tops, side-back sun, and thicker, sagging anvils.
