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
