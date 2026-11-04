# Storm Cloud: 30 s hobby scene (exploration)

A thunderstorm cell alone in a black void. The cloud is built from **millions of particles** (water
droplets) that billow and roll. There is no sun: every bit of light comes from **lightning inside the
cloud**, so the storm exists only when it flashes. Flashes crawl from cell to cell, backlight the turrets
with a silver rim, glow through the volume as soft internal light, and build to one hero bolt that forks
out of the cloud base in slow motion.

**Look:** pure black background (`#000`). **No text at all.**
After Effects grade: speed ramps (time-lapse billowing ↔ slow-motion strike), rack focus with droplet
bokeh near the lens, volumetric god rays, bloom + glow on the bolt, exposure "flash frames" on the
return stroke, subtle CA at the edges, ACES tonemap, cool/violet split tone, vignette, luminance-gated grain
(so the black stays black), slight handheld drift.
**Length:** 30.0 s · 60 fps · 1800 frames. Final 1920×1080, previews 854×480 @ 30 fps.

## Why particles *and* a volume

Additive points alone (the forest piece) can't make a cloud read as a cloud: clouds look solid because
they **shadow and scatter** their own light. So the particles do double duty each frame:

1. **Particles → density volume.** ~2–3M droplet particles are splatted into a 3D density texture
   (additive `GL_POINTS` into a 2D slice atlas, ~192³ voxels). The particles carry the structure and
   motion: cauliflower turrets, an anvil top, a rain shaft below, and curl-noise billowing.
2. **Volume → light.** A ray march through that density with Beer–Lambert transmittance, a
   Henyey–Greenstein phase function (strong forward scattering = silver lining when lit from behind) and a
   cheap multiple-scattering approximation (several octaves of attenuated extinction, Wrenninge 2013). The
   lights are the lightning channels themselves, as line lights *inside* the volume, so a flash deep in
   the cloud glows softly through it, and one near the edge lights the rim hard.
3. **Particles → glints.** The same particles near the camera are also drawn directly as tiny droplets that
   catch each flash, as bokeh discs when out of focus. This is where you *see* that it is particles.

## The lightning

Bolts are grown with the **Dielectric Breakdown Model** (Niemeyer, Pietronero & Wiesmann 1984): the channel
grows where the electric potential gradient is strongest, with growth probability ∝ (∂φ)^η. It uses the
fast charge-superposition form (Kim & Lin 2007), where φ at each candidate site is a sum of 1/r terms from
the existing channel, vectorised in numpy. η controls branchiness (η ≈ 2–3 looks like real lightning).
Each bolt is stored as a tree with the growth time per segment, so the **stepped leader** can grow branch by
branch, then the main channel (the shortest path to ground) lights up as the **return stroke** and the dead
branches fade. Intra-cloud "spider" bolts are the same model grown sideways under the anvil.

## Engine choice

| Need | Tool | Why |
|---|---|---|
| Cloud particles: turrets, anvil, base, rain shaft | **numpy + scipy** (seeded) | Stacked metaball cumulus towers with fBm-displaced surfaces, sampled by rejection; per-particle size/brightness. Deterministic |
| Billowing motion | **moderngl** vertex shader: analytic curl-noise displacement + rising convective roll per particle | Stateless, so any frame renders on its own (resumable) |
| Particle → density splat | **moderngl** (Radeon R4): additive points into a slice atlas (3D texture) | Millions of points per frame at 1 px each is cheap |
| Volumetric light | **moderngl** fragment shader: ray march, HG phase, multi-scatter octaves, line lights from bolt segments, shadow/transmittance march toward the brightest channel | Per-pixel and GPU-only. Run at half resolution and upsample with depth awareness |
| Lightning geometry | **numpy** DBM (charge superposition) → segment tree | The math behind real lightning branching, not random jitter |
| Bolt rendering | **moderngl**: anti-aliased thick lines (geometry shader) with an HDR core + wide glow | Reuse the photon-path line shader from the black-hole lab |
| Droplet glints, bokeh, rain streaks | **moderngl** `GL_POINTS` with per-point CoC (forest lab technique) | |
| AE post: bloom, god rays, flash frames, CA, ACES, split tone, vignette, grain | **moderngl** post passes | Reuse the Kawase bloom + composite from the earlier labs |
| Encode | **ffmpeg** + **tqdm** ETA bar, resumable segments | Same as the other labs |

Not used: **Manim** (no text or math on screen; Cairo on 2 CPU cores can't do volumes), **pyvista**
(can render a volume, but not lit from internal line lights, animated, with an AE grade),
**skia** (nothing 2D needed).

**Budget:** 2–3M particles. Measure the splat + march cost per frame at 480p from stills before any long
render. If the march is the bottleneck, drop the volume to 160³ and march at half res; the glint layer
stays full res, so the frame still looks sharp.

## Shot list (30.0 s)

| # | Time | What the viewer sees | Camera | AE touch |
|---|---|---|---|---|
| 1 | 0.0–3.5 | **Black.** A dim flicker deep inside: for 3 frames the silhouette of a towering cloud glows faintly from within, then darkness. A second, closer flicker shows a little more | Locked off, very wide, almost still | Flash frames are underexposed: the storm is hinted, not shown |
| 2 | 3.5–9.0 | **The storm reveals itself.** Intra-cloud flashes crawl from cell to cell across the tower (left base → core → anvil), each lighting a different region from inside. Between flashes the cloud billows in time-lapse | Slow push in, slight upward tilt toward the anvil | Volumetric glow, bloom; speed ramp: time-lapse billowing |
| 3 | 9.0–15.0 | **Along the cloud wall.** Close to the turrets: rolling cauliflower bulges, edges lit by flashes from behind (silver lining), dark cores. Droplets drift past the lens as bokeh | Lateral tracking glide, banking, rack focus from droplets in the foreground to the wall | Rim light, god rays through gaps, foreground bokeh |
| 4 | 15.0–20.0 | **Inside.** The camera pushes into the cloud. Fog of droplets streams past; flashes light the whole interior from different directions, briefly revealing internal cavities and a spider bolt crawling overhead | Forward dolly into the volume, slow roll | Volume fills the frame, flash-lit droplets, exposure pumping |
| 5 | 20.0–25.5 | **The hero strike.** The camera drops out of the cloud base. The stepped leader grows down out of the base in slow motion, forking branch by branch; then the return stroke: the main channel goes white, the whole cloud base lights up, and the dead branches fade | Exits below the base and holds, a slight dolly back as the bolt grows | Speed ramp to ~10% for the leader, back to 100% on the return stroke. One white flash frame, bloom halo, afterglow |
| 6 | 25.5–30.0 | **Afterglow and recede.** Two fading restrikes on the same channel, a last weak flicker high in the anvil. The cloud returns to black | Slow pull back and up to the wide shot, ease into a hold | Fade to black over the last 1.0 s |

At most ~3 things change at once. Nothing pops: flashes have a real light curve (a sharp rise of a few
frames, exponential decay with restrike flickers), and particles fade/grow in with easing.

## Look options (stills first, side by side, pick one)

| Look | Feel |
|---|---|
| **A: Storm noir** | Neutral silver-white cloud, blue-white lightning. Monochrome, closest to a real night storm photo |
| **B: Electric violet** | Lightning tinted violet/magenta, scattering inside the cloud shifts to deep purple, cyan rim on the edges. The long-exposure storm-photography look |
| **C: Ember storm** | A faint warm amber underglow from below (city light), cold blue-white lightning on top. Two-tone, most cinematic contrast |

## Files (planned)

| File | Role |
|---|---|
| `cloud.py` | Seeded cumulonimbus → particle arrays (pos, size, density weight, seed). Prints stats |
| `lightning.py` | DBM bolt growth (charge superposition) → segment trees with growth times, main channel. Cached |
| `timeline.py` | Camera keys (PCHIP) + handheld drift, sim time τ with speed ramps, flash light curves per bolt, focus / exposure curves |
| `shaders/splat.*` | Particles + curl-noise billowing → density slice atlas |
| `shaders/march.frag` | Volumetric ray march with internal line lights, HG phase, multi-scatter |
| `shaders/bolt.*` | Thick glowing lines for the channels |
| `shaders/glint.*` | Near-camera droplets with CoC bokeh |
| `shaders/*.frag` | Bloom, god rays, composite / grade |
| `render.py` | `still`, `looks`, `video` subcommands, tqdm ETA, resumable ffmpeg segments → `out/` |
| `NOTES.md` | Results, timings, what worked |

## Render plan

1. One still per shot in all 3 looks at 480p → contact sheets; you pick a look. Report s/frame.
2. 480p30 preview of the whole 30 s.
3. 1080p60 final in the background, once the preview is approved.
