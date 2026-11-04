# Black hole: 58 s hobby piece (look B)

A teaser for the *math behind black holes* video, with no text on a black background. The plan
and architecture are in `storyboard.md`. Every pixel is ray-traced through the Schwarzschild metric.

## What was built
- `geodesics.py` solves the photon orbit equation u'' = 3u² − u once for 4096 impact
  parameters (densely sampled near √27 with a sinh mapping), using vectorised RK4 in numpy
  (≈20 s, cached to `out/lut_cache.npz`). It builds three tables:
  `U[b, φ]`, the camera-phase table `φc(b, u_cam)` (by quadrature in u), and `φ_end(b)`.
  - **Validated on every build:** the capture edge falls at b = √27 (bracketed to 4e-4); the largest
    table error against DOP853 is 1.5e-8; the weak-field deflection matches
    4/b + 15π/4b² + 128/3b³ + 3465π/64b⁴ to 2e-5; φc agrees with adaptive quadrature;
    and the two tables are consistent with each other (u(b, φc) = u_cam).
- `blackhole.frag` (moderngl, Radeon R4) runs once per pixel. It computes b and the ray plane, then
  finds the disk crossings at φc + ψ₀ + kπ (k = 0, 1, 2 give the primary, secondary and tertiary
  images). Escaping rays look up their exit direction. Lookups use manual bilinear interpolation,
  because hardware filtering has only 8-bit weights and that bands near the critical curve.
  - **Disk:** Novikov–Thorne flux, a blackbody colour LUT (Planck → CIE → sRGB),
    g = √(1−3/r)/(1−ΩL_z)·(1−2/r_cam)^(-½), Keplerian advection of domain-warped fbm.
  - **Stars:** procedural, on a cube-sphere cell grid, with the kernel width set from the
    screen-space derivative of the lensed direction. Arcs and Einstein rings come out of this
    with no special cases. The planned cubemap (`starfield.py`) wasn't needed.
  - **Photon ring:** a thin emission layer placed exactly at b = √27, with a sweep for the 7.5 s beat.
- Overlay: the exact DOP853 photon paths for a parallel beam (8 impact parameters per side, including
  √27 ± 0.002, which wind around the photon sphere). They're drawn as anti-aliased geometry-shader
  lines with the ray tracer's own pinhole camera. Outgoing legs are trimmed at r = 9 to keep the frame calm.
- Post: dual-filter bloom, an anamorphic streak (look A), ACES, radial CA, vignette, and grain
  gated by luminance, so the black stays black.

## v2: travel intro + spacetime grid (look B chosen)
- `space.py`: act-1 dust (5k streaks + about 70 passing stars), scattered around the flight path, with
  lateral spread ∝ distance from the hole so the field streams past at a steady log-speed. Drawn as
  motion streaks between the previous and current camera projections (`dust.*` shaders).
- Act 3: Flamm's paraboloid line art (`grid.*` shaders). The surface height is computed in the vertex
  shader, so the "sink" from a flat sheet to the exact funnel is a single uniform.
- The tables now run to b = 2000 (6144 samples). The camera-u axis is sampled at u = U_CMAX·s², which
  keeps far-camera phase errors below 1e-6. Validated against quadrature at r = 3000 and against
  the weak-field series at b = 400 and 1500.
- Camera: distance is interpolated in log r (steady sense of speed). Added a look-at target height
  and yaw/pitch offsets for the travelling and oblique shots.
- The ray-traced pass is skipped once only the grid is on screen. Bloom is reduced while the dense grid
  is up, so the background stays black.
- 480p30 preview of the full 58 s: about 56 s to render. Final 1080p60 with 4× motion blur: 23m53s (2.4 fr/s), 123 MB, 3480 frames.

## v3: crisp family (S / G / K), based on look B's physical disk
- **Crisp pipeline:** 2× SSAA (4K internal for a 1080p output). Composite outputs *tonemapped linear*,
  and `resolve.frag` box-averages then applies gamma, so edges are anti-aliased in linear light. No motion
  blur, chromatic aberration or grain. Bloom only above HDR 0.9 (threshold on the first downsample).
  At 1:1, B's photon-ring and hat edges sparkle; S's are solid. With SSAA there's headroom for one
  finer filament layer in the gas (lr·120) without shimmer.
- **More visible lensing:** the lensing only shows if there's structure behind the hole, so two
  celestial layers are mapped through the exact exit direction:
  - **G:** a procedural galaxy band + bulge (pole tilted 25°, centre placed behind the hole at
    t ≈ 27 s), with fbm level of detail driven by the lensed footprint fp (octaves finer than a pixel
    collapse to their mean, so the region near the critical curve doesn't sparkle). The bulge's lensed
    image becomes a glowing crescent hugging the shadow.
  - **K:** a 10° latitude/longitude grid on the celestial sphere (30° majors, amber equator), lines
    anti-aliased in pixel units from fwidth, fading where they compress below ~3 px. It makes the
    lensing map visible: nested Einstein loops, the folded secondary image and the critical curve.
- **Cost:** about 1.0 s per frame at 1080p (4K internal, ray trace + post). The 58 s at 60 fps
  takes roughly 1 h in the background.
- Not added: higher-order disk images (k ≥ 3). At this framing the k = 3 image is about 5e-4·b
  wide, far below one pixel, so it would only cost time.

## v4: celestial objects (looks SO / GO = S / G + objects; K stays clean for chapters)
Use: **SO / GO for intros**, **K for the explanation chapters**. Placements in `objects.py` are derived
from the camera path, so each object lands where it should in frame.
- **Nebulae (3)**, on the sky sphere and lensed exactly: domain-warped fbm with ionisation-front filaments
  and dust lanes, coloured with emission-line hues (Hα red, O III teal, S II magenta). N1 sits behind the
  hole at the shadow reveal (≈20.5 s) and becomes a full red/teal **Einstein ring**. N2 is in the travel
  shot, N3 behind the face-on orbit. Filtered by the lensed footprint, like the galaxy band.
- **Supernova** at 5.6 s (upper right): fast rise, exponential decay with a faint tail, cooling from
  16000 K to 5000 K through the blackbody LUT; diffraction spikes (4 + 4 faint) and a fading light-echo
  ring. Drawn on the sky, so it is lensed too (negligibly, at that angle).
- **Distant galaxies**: rare elliptical smudges (warm ellipticals, spirals with a bluer disk).
- **Pulsar fly-by** (3–10 s, passes at 8.6 s): `pulsar.frag`, a volumetric ray march (96 steps) of
  two magnetic-pole beams precessing around a spin axis tilted so a beam sweeps across the camera once
  per turn (the lighthouse flash), plus a pulsar-wind torus, polar jets and a pinpoint core. It uses straight
  rays: at r ≳ 300M the hole bends light by < 1°, so lensing is ignored there.
- **Time compression:** the pulsar's 1.15 s period and the supernova's seconds-long light curve are
  stylised (real ones: ms to s, and weeks). They're illustrative, not to scale.

## Looks (`out/looks_*.png`, `out/contact_all.png`)
| Look | Verdict |
|---|---|
| **A Cinematic** | Warm, the most "film" look. Needs restraint on the streak and bloom, or the background turns orange |
| **B Physical** | True g⁴ beaming: the left side is much brighter than the right. The most honest, and a little colder |
| **C Spectral** | Iso-radius contours r = 6…19 with dashes moving at each ring's own Ω. They show the lensing warp (Luminet-style) and the Keplerian shear directly. The most "math channel" |

## What worked / what didn't
- The LUT approach is fast: video renders at about 35 fr/s at 480p on the R4 (the 30 s preview takes 25 s).
  Stills take about 0.3 s each, but that includes setup.
- The hero frame at r = 23.5M overfilled the frame, so the camera key was pulled back to r = 28M.
- **Gotcha:** several `moderngl.create_context(standalone=True)` contexts in one process don't
  switch, so everything renders into the last one. Use one context at a time (`looks` does that now).
- The first exposure pass was blown out. The disk HDR p90 is about 1.0, and the full bloom pyramid
  at 0.28 flooded the shadow. Bloom is now about 0.03–0.05 of the pyramid.
- Physical Keplerian shear turns radial spokes into moiré within 15 s. Dashes riding on each contour
  show the same differential rotation cleanly.
- With a near-critical beam, escaping rays leave at every angle, and drawn in full they cluttered the
  frame. Trimming them fixed that.
- Simplifications: the camera is treated as a static observer (no aberration from its own orbital
  motion), and the disk is geometrically thin.

## Render
`video` is **resumable**. It encodes 240-frame segments into `out/segments/<look>_<res>_<hash>/`, and a
segment only appears once it's complete (written as `.part`, then atomically renamed). Re-running the same
command after a crash or power cut skips the finished segments, then joins them with the concat demuxer
(stream copy, lossless). The hash covers every `.py` and shader file plus the render settings, so editing
the code never reuses stale segments. Pass `--fresh` to start over. (A plain single-pass MP4 can't be
salvaged after a power cut: its index is written only at the end.)

```bash
uv run python lab/2026-11-04-black-hole/geodesics.py                       # rebuild + validate tables
uv run python lab/2026-11-04-black-hole/render.py looks --t 3 8 12 18 24.6 28.6 --height 360
uv run python lab/2026-11-04-black-hole/render.py still --look A --t 12 --height 540
uv run python lab/2026-11-04-black-hole/render.py video --look A --height 480 --fps 30 --preset veryfast
uv run python lab/2026-11-04-black-hole/render.py video --look B --height 1080 --fps 60 --mb 4 --crf 14 --preset slow   # final
```

## Promotion candidates
`geodesics.py` + `blackhole.frag` → `aion/components/schwarzschild.py` + `aion/shaders/`, for
the real black-hole video. The blackbody LUT is generic and worth moving to `aion/` now.
