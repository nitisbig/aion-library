# Supernova → black hole: 30 s hobby piece

## v2: exterior only (current)
User feedback on v1: "don't show the inner parts of the star, just explode with cinematic shots." The cut-away dive is gone.
The camera never enters the star:
| Screen | T | Shot |
|---|---|---|
| 0–5 | −1 d → −0.3 s | Wide shot of the giant with a slow orbit and push-in. The collapse begins unseen inside a calm star |
| 5–8 | bounce (6.5), black hole (8.0) | The neutrino burst streaks out through the star (dimmed over the disc), and ripple rings at bounce and at birth warp the sky. Streaks stop at T_BH |
| 8–12.8 | +2 s → +2.05 d | Push in to 1.6 R★ and yaw onto the limb: the surface stays quiet while the shock crosses the envelope (it really does) |
| 12.8 | breakout | Flash. The camera is pushed back just ahead of the photosphere (1.72 → 6 R_ej). A blast corona of radial rays plus RT hot plumes decays over ~1.4 s |
| 13–23 | → 300 yr | The photosphere cools (blue → cream → red), turns transparent, and becomes the remnant. The GW sweep crosses the background |
| 23–30 | 300 yr, ×1 | Dive to the hole: lensing, the photon ring, and an orbit for the final hold |
The interior code (onion, shock, PNS, shadow) is still in `matter.frag`; v2 just never shows it (`cut = 1e30`, core off).


A 25 M☉ red supergiant runs out of fuel. Its iron core implodes, the star explodes as a fallback supernova, and a
6 M☉ black hole is left at the centre of a 300-year-old remnant. Black background. The only text is a mission
clock in the bottom-right corner showing the **physical time** of each frame and how fast it is running.
The plan is in `storyboard.md`. The output is `out/supernova_A_*.mp4`, with stills at `out/contact_A.png`.

## Pipeline
| File | Role |
|---|---|
| `astro.py` | The scenario: the onion's shell radii and masses, cycloid free fall of every shell (tuned to the simulated 0.3 s collapse), the Matzner–McKee shock integrated to the surface, the fallback that turns the PNS into a black hole, the type II-P photosphere, free expansion. **Asserted on every import** |
| `timeline.py` | The clock map T(s) is a PCHIP through physical event keys in asinh(T / 50 ms), so it is log-like far from the bounce and linear near it. The camera distance comes from physics where it matters: it follows 60% of the core's log-collapse, rides 3.2 R_shock, then 6 R_ejecta. Everything is f(s) |
| `shaders/matter.frag` | One pass for the star: an analytic sphere minus a cut-away octant (the faces show the onion in log-polar texture coordinates, so the pattern is self-similar under the zoom), the uncut core, PNS or shadow, the shocked gas, the ejecta photosphere, the ray-marched remnant, and the neutrino streaks. Lengths are in units of the camera distance, so 18 decades of zoom keep float precision |
| `shaders/sky.frag` | Stars, Milky Way band, galaxies, a globular cluster, 3 nebulae, all lensed through the exact Schwarzschild tables (from the black-hole lab) for b < 2000 M, and the weak-field (2M/b)(1 + cos A) beyond. Plus the photon ring and the GW sweep |
| `shaders/pulsar.frag` | The black-hole lab's volumetric pulsar, held at a fixed sky direction |
| `shaders/composite.frag` | The h₊ ring warp (bounce and birth), bloom, ACES, grade, vignette |
| `hud.py` | The skia clock: time with automatic units, rate (`▸▸ ×1.6·10⁴`, `▸ ×0.07` in slow motion), and a log-time rail from −1 d to +300 yr |
| `geodesics.py`, `blackbody.py` | Copied from `lab/2026-11-04-black-hole` (the lab stays self-contained); `out/lut_cache.npz` copied too |

## The numbers (`uv run python astro.py`)
| | |
|---|---|
| Collapse | 1500 km → 30 km in 0.30 s (pressureless free fall would take 0.13 s; the check bounds the ratio) |
| Black hole forms | T + 1.98 s (the PNS reaches 2.3 M☉). Ringdown 5.2 kHz, τ = 0.13 ms |
| Shock | 7 000 km at 1 s, 78 R☉ at 1 h, **breakout at T + 2.05 d** |
| Ejecta | 3 737 km/s, so the remnant has a 1.15 pc radius at 300 yr |
| Photosphere | ≈10⁵ K at breakout → 22 000 K at 1 d → 6 000 K plateau → transparent by ~220 d |
| Shadow | 17.6 km radius at birth (2.3 M☉), growing with fallback to 6 M☉ |

## What worked
- **The cut-away octant as a concave corner.** Three faces meet at the centre. The y face is lit like a floor, the walls are darker,
  and ambient occlusion along the edges makes it read as a room corner, not a cube. The shells pass by one after another during the dive.
- **Log-polar texture coordinates** (direction + log r): cells keep the same apparent size at every depth, so the dive
  looks like a continuous powers-of-ten zoom instead of a texture blowing up.
- **Cores drawn whole.** The iron core, PNS and shadow ignore the cut, otherwise only an eighth of the sphere showed.
- **Camera follows 60% of the collapse in log space**, so the core visibly shrinks about 5× on screen instead of staying the same size (100%)
  or vanishing in a frame (0%).
- **Hot gas from blackbody temperature** (2 400–7 000 K, saturated) instead of composition colours: it reads as fire, and
  the composition is a 12% tint plus the Rayleigh–Taylor fingers.
- The lensing tables from the black-hole lab work unchanged once a weak-field branch covers b > 2000 M.

## What didn't (and the fixes)
- First pass: the star was never switched off after breakout, so the camera flew through the old star's faces in shot 7.
- Composition colours at full brightness washed out to pastel under ACES. Fixed by scaling the interiors to about 0.4 HDR.
- The texture-noise nebulae looked like speckled marble. Switched back to the black-hole lab's procedural LOD fbm.
- From inside the remnant, the whole sky filled with filaments and the black background was gone. Fixed by dimming the remnant ×0.1 inside, so
  stars and the lensed nebula carry the last shot.
- A uniform array trimmed by the driver (`u_shell[6]` → 5 used) crashed moderngl. Fixed in `setu()`, which trims lists.

## Honesty notes
**Real:** every clock value and rate, the order and sizes of the shells (through the log zoom), the collapse curve,
the shock position, the breakout time, the photosphere temperatures (through a Planck → CIE → sRGB table), the shadow size, the lensing,
the photon ring at b = √27, and the neutrino cut-off at black-hole formation (emission stops at T_BH, the last streaks fly out).

**Stylised:**
- **GW amplitude** (×~10¹⁹) and the width of the wave packet. Inside the star the two rings expand at screen speed rather than c
  (at c they would cross the frame in microseconds).
- **The sky ripple timing is physical**: an object at distance d ripples when T = (|p| + |p − cam|)/c, with distances from a smooth
  3–140 ly field. The amplitude is not.
- Neutrinos are invisible. The streaks are drawn and slowed about 100× so they can be seen.
- The SASI sloshing uses the real ≈40 ms period, but its amplitude is drawn.
- The RT fingers and convection are procedural noise, not hydrodynamics.
- The remnant is dimmed from inside, and the pulsar's spin is slowed to 1.25 s.
- The light echo was dropped: about 0.3 s of screen time at that clock rate.
- The first sky-sweep packet (width 0.035 in ln T) changed only 0.1% of pixels, so it was invisible. Widened to 0.10 with amplitude 0.22.
  Checked by rendering with and without the wave and differencing: the nebula filaments and stars visibly shift as the front passes.

## Render
```bash
uv run python lab/2026-11-04-supernova-black-hole/astro.py                    # numbers + checks
uv run python lab/2026-11-04-supernova-black-hole/render.py sheet --height 270 # contact sheet of the beats
uv run python lab/2026-11-04-supernova-black-hole/render.py still --t 13.6 29.6 --height 540
uv run python lab/2026-11-04-supernova-black-hole/render.py video --look A --height 480 --fps 30 --preset veryfast
uv run python lab/2026-11-04-supernova-black-hole/render.py video --look A --height 1080 --fps 60 --crf 14 --preset slow   # final
```
Cost on the Radeon R4: the 480p30 preview (960p internal) takes ≈4 min. The 1080p60 final (4K internal, 2× SSAA) runs at ≈1.1 s/frame, so ≈35 min.
Look B (`--look B`: streak, grade, 4× motion blur, no SSAA) is the cinematic alternative. See `out/contact_B.png`.

`video` is resumable (240-frame segments keyed by a hash of the code and settings), like the black-hole lab.

## GPU timeout at 1080p (fixed)
The first 1080p run died at frame 717 (s ≈ 23.9, the dive into the remnant) with
`amdgpu: ring gfx timeout, but soft recovered`: one full-screen draw at 4K internal (2× SSAA) ran for seconds, and the
driver killed it. The sky, pulsar and matter passes now draw in 4×3 scissored tiles with `ctx.finish()` between them
(`Renderer._tiled`). The output is identical, and each draw call takes ≈0.15 s. The segment key now hashes only what changes pixels (shaders, the
physics/timeline/HUD modules, the look), so fixes to render.py's pipeline can resume a render. Use `--fresh` after a pixel-changing edit
to render.py. Each segment is decode-checked before it is accepted.
