# Supernova → black hole: 30 s hobby scene (exploration)

A giant star dies. Its iron core implodes, the star explodes, and a black hole is left behind.
The hole then lenses the wreckage and the sky around it. Black background. The only text is a
small mission clock in the bottom-right corner that shows the **physical time** of each frame, so
the viewer feels the fast-forward (and the slow motion at the collapse).

Finish: After Effects grade (eased log-zoom camera, restrained bloom, ACES tonemap, crisp 2× SSAA).
Earlier lab feedback was "too much blur and glow", so the crisp pipeline is the default.

---

## 1. The scientific scenario (all numbers computed in `astro.py`, asserted on every build)

A **25 M☉ red supergiant** ending as a **fallback supernova**: the shock unbinds the envelope, but
enough matter falls back onto the proto-neutron star to push it past the maximum neutron-star mass,
and it collapses into a black hole within seconds. Simulations of this channel exist (e.g. Chan,
Müller, Heger et al. 2018). The alternative, a *failed* supernova with no explosion, is real too, but
it doesn't give us the explosion.

| Quantity | Value (approx., pinned in `astro.py`) | How it's obtained |
|---|---|---|
| Star radius | ≈ 900 R☉ ≈ 6.3·10⁸ km (≈ 4 AU) | RSG pre-SN models |
| Shell radii (onion) | Fe core ≈ 1 500 km · Si ≈ 4 000 km · O ≈ 5·10⁴ km · He core ≈ 1 R☉ · H envelope → 900 R☉ | pre-SN profile of a 25 M☉ model (Woosley–Heger–Weaver 2002 scale) |
| Si burning (last stage) | ≈ 1 day | same source. The clock starts here |
| Core collapse, onset → bounce | ≈ 0.3 s, infall up to ≈ 0.25 c | free fall t_ff = √(3π / 32Gρ) as the check |
| Bounce | ρ ≈ 2.7·10¹⁴ g/cm³ (nuclear), core 1 500 km → ≈ 30 km | |
| Neutrino burst | ≈ 10 s, ≈ 3·10⁵³ erg (99 % of the energy) | |
| Black hole forms | **T + 1.98 s**, when the PNS passes M_max ≈ 2.3 M☉ | fallback accretion rate model |
| Shock breakout at the surface | **T + 2.05 d** | t ≈ ∫ dr / v_sh(r), Matzner–McKee shock speed |
| Ejecta speed | **3 737 km/s** | v ≈ √(10E / 3M_ej), E = 10⁵¹ erg, M_ej = 12 M☉ |
| Final BH | 6 M☉ → r_s ≈ 17.7 km (2.3 M☉ at birth: shadow radius 17.6 km) | |
| End of scene | T + 300 yr (Cas A age), remnant radius **1.15 pc** | free expansion |

**Clock** = physical time *T* relative to core bounce. Screen time → *T* is a smooth, monotonic,
piecewise-log map, so its rate swings from **×10⁴ fast forward** to **×0.15 slow motion** and up to
**×10⁹**. All of it is computed, nothing is hand-typed.

---

## 2. Shot list (30.0 s)

| # | Screen time | Physical time T | What the viewer sees | Why it's there |
|---|---|---|---|---|
| 1 **The giant** | 0.0 – 5.0 | −1 d → −1 h | Wide shot of the red supergiant: huge boiling convection cells, limb darkening, slow pulsation, a faint dusty wind shell. Background: Milky Way band, 2 emission nebulae, distant galaxies, a **pulsar** with sweeping beams, a globular cluster. The camera drifts in slowly | Calm before. Its surface gives no sign of what the core is doing |
| 2 **Into the core** | 5.0 – 9.0 | −1 h → −0.3 s | **Powers-of-ten dive**: a quarter of the star is cut away, and the camera falls through the onion shells. H (deep red) → He (orange) → C/O (gold) → Ne/Mg → Si (white-blue) → the grey-white iron core. Equal log-zoom speed, so each shell gets roughly equal screen time | Shows *where* the death happens: an Earth-sized iron ball inside a star 4 AU wide |
| 3 **Collapse** | 9.0 – 11.0 | −0.3 s → 0 | Slow motion (clock ×0.15). The iron core implodes from 1 500 km to 30 km, the surface crumples inward, and the shells overhead start to sag. **Bounce at 11.0**: a white flash | The collapse is faster than a blink, so we slow down to see it |
| 4 **Neutrinos + birth** | 11.0 – 14.0 | 0 → +2 s | Neutrino burst: faint blue streaks rushing outward through everything. **GW ripple #1** (bounce) runs across the frame. The stalled shock sloshes (SASI), then revives. At ≈13.3 fallback tips the core over: **the neutrino glow switches off abruptly** (a real signature of BH formation), and **GW ripple #2**, a sharper ringdown, sweeps the whole frame, bending the shells, nebulae, pulsar and stars as it passes | The black hole's birth is invisible, but spacetime rings |
| 5 **Breakout** | 14.0 – 19.5 | +2 s → +2 d | A log pull-back that rides the shock outward through the shells. Rayleigh–Taylor fingers mix the layers' colours. At ≈19.0 the shock reaches the surface: **breakout flash** (UV-hot blue-white), and the whole star brightens and swells | The explosion takes a day to reach the surface |
| 6 **The remnant** | 19.5 – 24.5 | +2 d → +300 yr | The camera keeps pulling back as the ejecta expands. Its colour follows the photosphere temperature (blue-white → yellow → red, the ~100-day plateau), then it turns transparent and becomes a filamentary remnant (Hα red, O III teal, Cas A-like). A light echo ripples across the wind shell | Fast forward through centuries. The star becomes a nebula |
| 7 **The hole** | 24.5 – 30.0 | +300 yr (×1) | A log dive from the remnant's scale (≈10¹² r_s) to ≈30 r_s at the centre. In the last two decades, **gravitational lensing** switches on: the remnant's filaments and the background bend around a black shadow, the photon ring appears, and the remnant shell lensed behind the hole forms an **Einstein ring**. Slow orbit (lensing reads best in motion), then a held final frame | What's left: nothing, and the light bending around it |

Transitions are all continuous camera moves (dive → pull-back → dive). There are no cuts.

### Gravitational ripples (stylised amplitude, honest shape)
- They're drawn as **transverse quadrupole** distortion: a GW stretches space along one axis while
  squeezing it along the other (h₊ ∝ cos 2φ). It doesn't push radially. The ripple is an expanding
  shell from the source, and as it passes, every background element (stars, nebulae, pulsar, the star's
  shells) is displaced by this pattern.
- Real strain is ~10⁻²¹. The amplitude is **exaggerated ~10¹⁹×** and the wavelength is stretched to
  screen scale. This goes in NOTES.md, the same way the black-hole lab flagged its stylised pulsar.

### Lensing
- Reuses the black-hole lab's exact Schwarzschild LUT ray tracer (b → deflection, √27 shadow).
- In shot 7 the remnant is ~10¹⁰ times farther than the camera's distance from the hole, so it sits
  on the **sky sphere** (treating it as at infinity is exact to well below a pixel) and gets lensed from the exact
  exit direction. The Einstein ring comes out of the geometry, with no special cases.
- Before shot 7 the camera is ≥10⁶ r_s from the hole, so the lensing there is < 10⁻⁵ rad. Showing none
  is the correct answer, not an omission.

---

## 3. HUD (the only text)

Bottom-right corner, inside the 5% safe margin. A small, dim monospace (tabular figures), roughly:

```
                                   T − 23 h 14 m
                                   ▸▸ ×1.6·10⁴
                         ├──────────●───────────────┤   (log time rail: 1 ms … 1 kyr)
```

Units switch automatically (h m → s → ms → s → d → yr). The rate line changes to `×0.15` in the slow
motion. Fades in at 0.4 s and out over the last 0.8 s. Rendered with **skia-python** (crisp
glyph anti-aliasing) to an RGBA texture, then composited on the GPU.

---

## 4. Engine choice

| Need | Tool | Why |
|---|---|---|
| Timeline physics (clock map, shell radii, shock radius r_sh(T), temperatures, BH formation time) | **numpy + scipy** (`astro.py`) | Real formulas, cached, asserted against limits |
| Photon geodesic LUT | **numpy/scipy**, copied from `lab/…-black-hole/geodesics.py` | Already validated (√27 edge, weak-field series) |
| Star surface, cutaway shells, shock, ejecta, remnant | **moderngl**: one volumetric ray-march shader (half-res, 48–96 steps, seeded blue-noise jitter) | Per-pixel volumetrics. The only practical option on the R4 |
| Sky: stars, Milky Way, nebulae, galaxies, globular cluster | **moderngl**, reusing `blackhole.frag` / `objects.py` sky functions | Already lensable by exit direction |
| Pulsar / neutron star | **moderngl**, adapting `pulsar.frag` | Volumetric beams, already built |
| GW ripples | **moderngl**: the quadrupole displacement perturbs the view direction before every sky and volume lookup | Everything is distorted consistently |
| Neutrino streaks | **moderngl** geometry-shader lines (from the `dust.*` shaders) | |
| Post: bloom, ACES, vignette, luminance-gated grain, SSAA resolve | **moderngl**, reusing the existing post chain | |
| HUD clock | **skia-python** | Best typography of the options |
| Encode | **ffmpeg** via resumable 240-frame segments (same scheme as the black-hole lab) | Safe against crashes |

Not used: **Manim** (no equations, and far too slow per pixel), **pyvista** (it can't do curved-spacetime
rays or soft volumetric emission). The lab stays self-contained: the reused files are **copied**, not
imported across labs. The LUT tracer and post chain are now in two labs, so they're good
candidates for promotion to `aion/shaders/` afterwards.

### Files
```
lab/2026-11-04-supernova-black-hole/
  storyboard.md   NOTES.md
  astro.py        # scenario numbers, clock map T(s), shock/ejecta/temperature curves (+ asserts)
  timeline.py     # camera keys (log distance), every animated uniform as f(t)
  geodesics.py    # copied LUT builder
  hud.py          # skia clock → RGBA
  render.py       # still / looks / video (resumable)
  shaders/        # star.frag (volume), sky.glsl, lens.frag, pulsar.frag, neutrino.*, post chain
```

---

## 5. Looks (exploration: 2 variations side by side)

| Look | Feel |
|---|---|
| **A Crisp physical** | Blackbody colours straight from temperature, 2× SSAA, bloom only above HDR 0.9, no motion blur or chromatic aberration. The default |
| **B Cinematic** | The same frames, plus an anamorphic streak on the bounce and breakout flashes, a slight teal-shadow / warm-highlight grade, 4-sample motion blur on the dives |

Contact sheet at the key beats first (2.0, 7.0, 10.0, 11.0, 13.3, 17.0, 19.0, 22.0, 27.0, 29.5), then a 480p30 preview,
then the final 1080p60.

## 6. Render budget (Radeon R4)
- Stills at 360p: ~1 s each. 480p30 preview of 30 s: est. 3–6 min (the volumetric pass dominates).
- 1080p60 final (2× SSAA, half-res volume): est. 1.0–2.0 s/frame → **30–60 min** in the background,
  resumable, with a tqdm bar and ETA.

## 7. Honesty notes (go into NOTES.md)
Real: the time on the clock, the shell ordering and radii (via log zoom), the colours from blackbody
temperatures, the lensing geometry, the neutrino cut-off at BH formation.
Stylised: GW amplitude and wavelength, neutrino streaks (neutrinos are invisible), RT fingers
(procedural noise, not hydrodynamics), the placement of the background objects, and the pulsar's spin
period (slowed so its beams can be seen).

---

## Changes during the build (see NOTES.md)
- **Background ripples.** The camera is inside the star when the black hole forms, so no sky is in view. The background
  objects therefore ripple when the wave *physically* reaches them. An object at distance d is seen to ripple at
  T = (|p| + |p − cam|)/c ≈ 2d/c, so stars and nebulae 3–140 ly away ripple one after another during shot 6
  (T ≈ 6–280 yr), and the pulsar (26 ly) ripples at ≈ 52 yr. Inside the star, the two rings (bounce, birth) stay as planned.
- The light echo was dropped: a dusty shell at 0.1 pc would echo for ~0.6 yr, which is about 0.3 s of screen time at that clock rate.
