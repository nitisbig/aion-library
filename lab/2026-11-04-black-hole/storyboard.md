# Black hole: 30 s hobby scene (exploration)

A teaser for the upcoming *math behind black holes* video. Black background, no text.
After Effects-grade finish. **Every pixel comes from the real math**: the image is ray-traced
through the Schwarzschild metric, not painted to look like a black hole.

Units: G = c = 1, mass M = 1. The numbers that appear on screen as *shapes*, never as text:

| Feature | Value | Where you see it |
|---|---|---|
| Event horizon | r = 2M | never seen directly (it's hidden inside the shadow) |
| Photon sphere | r = 3M | light can orbit here, which makes the thin photon ring |
| Shadow edge (critical impact parameter) | b = √27 M ≈ 5.196M | the radius of the black disc |
| ISCO (innermost stable circular orbit) | r = 6M | the inner edge of the accretion disk |

---

## 1. Engine choice

| Need | Tool | Why |
|---|---|---|
| Photon geodesics, lookup tables | **numpy + scipy** (`solve_ivp`, DOP853) | Solve the exact orbit equation offline, once, to 1e-10 accuracy |
| Per-pixel ray tracing, disk, lensed stars | **moderngl** (fragment shader, Radeon R4) | Per-pixel work is the GPU's job. Manim's CPU renderer could never do this at 1080p60 |
| Geodesic line-art overlay | **moderngl** geometry-shader lines | Reuses the anti-aliased line technique from `lab/2026-11-04-london-bridge` |
| Bloom, flare, grain, chromatic aberration, tonemap | **moderngl** post passes | Keeps the whole frame on the GPU, with no round trips |
| Starfield texture | **numpy** (seeded) → cubemap | Deterministic and sparse, so the background stays black |
| Encode | **ffmpeg** (raw frames piped in) | |

Not used: **Manim** (no equations or text in this piece, and too slow per pixel), **pyvista**
(we ray-trace curved spacetime, which a rasterizer can't do), **skia** (the post-processing is
cheaper in GLSL).

### The key trick: the Luminet lookup table (fast *and* exact)

Brute-force ray marching (≈300 RK4 steps per pixel × 2 M pixels × 1800 frames) would take
hours on the R4. We don't need it, because Schwarzschild spacetime is spherically symmetric:

1. Every photon moves in a **plane through the black hole**, and its path depends only on its
   impact parameter **b**. With u = 1/r, the orbit equation is
   **d²u/dφ² = 3M·u² − u**.
2. So we solve it **once per b** on the CPU and store a 2D float texture
   `LUT[b, φ] = (u, du/dφ)`, about 1024 × 2048 values. That's the whole of general relativity
   for this scene.
3. In the shader, each pixel:
   - computes its b (from the view angle α and the camera distance r_cam:
     b = r_cam·sin α / √(1 − 2M/r_cam)) and its ray plane;
   - b < √27 → the ray is captured (it heads into the shadow), unless it hits the disk first;
   - the disk plane cuts the ray plane in a line, so the photon crosses the disk at swept angles
     φ₀, φ₀+π, φ₀+2π. Look up r at each one → the **primary, secondary and tertiary images**
     of the disk, which give the famous "hat" over the shadow and the thin inner rings;
   - escaping rays look up their total deflection Δφ(b) → the **lensed starfield and Einstein rings**.

   That's about 3–5 texture reads per pixel instead of 300 integration steps, so it should be
   roughly 50× faster, with no loss of accuracy.

4. Validation (in `geodesics.py`, asserted every run): the capture threshold comes out at
   b = √27; the weak-field deflection matches 4M/b for large b; the shadow radius is checked
   against a pixel measurement of a rendered still.

### Disk physics (in the shader)
- Temperature: Novikov–Thorne / Shakura–Sunyaev profile
  T(r) ∝ r^(−3/4) · (1 − √(6M/r))^(1/4) → blackbody colour (Planck → CIE → sRGB, precomputed as a 1D LUT).
- Keplerian rotation Ω = √(M/r³). The inner disk visibly spins faster than the outer disk, and
  the turbulence texture is advected along it, so the swirl is physically sheared.
- Redshift factor g = √(1 − 3M/r) / (1 + Ω·L_z), where L_z is the photon's angular momentum
  about the disk axis. Observed intensity I ∝ g⁴·I_emit, with colour temperature T·g.
  → **Doppler beaming**: the approaching side is brighter and bluer, the receding side dim and red.
- The beaming strength is a look parameter (see *Looks*). Fully physical is very asymmetric.

---

## 2. Storyboard (30.0 s @ 60 fps = 1800 frames)

At most about 3 things change at once. The camera moves continuously; there are no cuts.

| # | Time | What the viewer sees | Why (the math it previews) | Camera |
|---|---|---|---|---|
| 1 | 0.0–4.0 | **Void.** Pure black. Sparse stars fade in and drift slowly. Then one star passes near the centre and *smears into an arc*, then a full **Einstein ring**. Nothing is visible there. | Gravity bends light. Something invisible is acting as a lens. | Far (r = 60M), still, slow push |
| 2 | 4.0–9.0 | Lensing grows as we approach: the starfield folds around an **empty black disc**. On a beat (≈7.5 s) a hairline **photon ring** glints into existence at its edge, with a bright sweep running once around the circle. | The shadow edge b = √27 M, and light orbiting at r = 3M. | Push in r 60 → 25M, inclination 85° |
| 3 | 9.0–15.0 | **Ignition.** Gas spirals in from the dark and lights up from the outside in, until the inner edge locks at the ISCO. The far side of the disk **bends up over the shadow** (the "hat"), and a fainter secondary image wraps underneath. One side glows brighter. | Light from behind the hole is bent over it. ISCO r = 6M. Doppler beaming. | Near edge-on (i ≈ 84°), slow drift |
| 4 | 15.0–22.0 | **Orbit.** The camera rises from edge-on toward ~25° from face-on, then back down, while circling the hole. The lensed image morphs continuously; the inner disk visibly spins faster than the outer disk. | The same spacetime seen from different angles. Keplerian Ω ∝ r^(−3/2). | Azimuth +70°, inclination 84° → 25° → 75° |
| 5 | 22.0–26.5 | **The math layer.** The disk dims to about 30%. Thin glowing **photon trajectories** (the exact geodesics from the LUT) are drawn from the camera toward the hole as a fan: far rays bend slightly, rays near √27 M wind once around the photon sphere, inner rays fall in. Then the lines fade back into the image. | *This is the explanation*: the shadow is the set of rays that never escape. | Slow push-in, slight roll |
| 6 | 26.5–30.0 | **Resolve.** The disk brightens once more (a hero frame, held ~1.5 s), then the light drains inward, the disk first and then the stars, leaving only the photon ring, which fades last to black. | The ending lands on the circle the next video is about. | Gentle pull-back, settle |

Sound: none (hobby scene). If you add music later, the beats at 4.0, 7.5, 9.0, 22.0 and 26.5 are the cut points.

---

## 3. Looks (2–3 variations, compared side by side before the final)

| Look | Description |
|---|---|
| **A Cinematic** | Warm amber/white blackbody, beaming toned down (g^1.5), strong bloom, soft anamorphic streak. Reads as "Interstellar-like". The most beautiful option |
| **B Physical** | True g⁴ beaming and gravitational redshift, blue-white approaching side, deep red receding side. The most honest option, and the best fit for a math channel |
| **C Spectral line** | Desaturated disk rendered as fine glowing iso-radius contour lines (r = 6, 8, 10 … M) instead of gas. Very graphic, ties directly into the geodesic-overlay layer |

I'll render beat stills (t = 3, 8, 12, 18, 24, 28 s) for A/B/C as a contact sheet before committing to the full video.

## 4. "After Effects" finish (post stack, all GLSL)
1. **Motion blur**: 4–8 accumulated sub-frames (final only).
2. **Bloom**: 6-level dual-filter (Kawase) on HDR, plus a thin horizontal anamorphic streak (look A only).
3. **Filmic tonemap**: ACES-fitted curve, exposure keyed on the timeline.
4. **Chromatic aberration**: radial and subtle, stronger toward the edges.
5. **Vignette + seeded film grain**, kept very light so the background stays black, not grey.
6. **Light leaks / flare: none.** They read as cheap; restraint looks more premium.

---

## 5. Architecture

```
lab/2026-11-04-black-hole/
├── storyboard.md          # this file
├── NOTES.md               # results, timings, frames (after building)
├── geodesics.py           # numpy/scipy: orbit equation, LUT builder, validation, overlay paths
├── timeline.py            # camera keys + every animated parameter, as pure functions of t
├── starfield.py           # seeded star cubemap (numpy)
├── shaders/
│   ├── fullscreen.vert
│   ├── blackhole.frag     # per-pixel: b, ray plane, LUT lookups, disk images, stars, photon ring
│   ├── lines.vert/.geom/.frag   # geodesic overlay (AA quads + reveal head)
│   ├── bloom_down.frag / bloom_up.frag
│   └── composite.frag     # tonemap, CA, vignette, grain
├── render.py              # CLI: still | looks | video ; tqdm bar ; ffmpeg pipe
└── out/                   # stills, contact sheets, mp4 (gitignored)
```

**Data flow per frame**

```
          (once, cached .npy)
geodesics.py ──► LUT texture  (u, du/dφ)[b, φ]  +  Δφ(b)  +  blackbody LUT
starfield.py ──► star cubemap
                         │
timeline.py ── t ──► uniforms: camera pose, fov, disk ignition, beaming, overlay reveal, exposure
                         │
           ┌─────────────▼──────────────┐
           │ blackhole.frag (HDR RGBA16F)│  ← one fullscreen pass
           └─────────────┬──────────────┘
                         │  + lines pass (additive, scene 5 only)
                         ▼
     sub-frame accumulate (motion blur) → bloom pyramid → composite.frag
                         │
                 glReadPixels → ffmpeg (libx264, yuv420p, crf 14)  → out/blackhole.mp4
```

**Design decisions**
- **Timeline as pure functions of t** (`timeline.py`): any frame renders independently, so
  stills, previews and finals come from the same code, and everything is deterministic.
- **The LUT is the single source of physics truth**: the shader and the overlay lines both read
  geodesics from it, so the drawn trajectories line up exactly with the lensed image.
- **Resolution-independent**: `--height 270/480/1080/2160`. Iterate at 480p, final at 1080p60.
- **Progress rule**: `render.py` wraps the frame loop in `tqdm(total=1800)` with an ETA,
  as CLAUDE.md requires for non-Manim pipelines.
- **Promotion path**: if this works, `geodesics.py` + `blackhole.frag` become
  `aion/components/schwarzschild.py` + `aion/shaders/blackhole.frag`, ready for the real video.

**Estimated cost on the A6/R4** (to verify): LUT build ≈ 10–20 s (cached afterwards).
480p30 preview ≈ 1–2 min. 1080p60 final with 4× motion blur ≈ 15–30 min, in the background.

---

## 6. Open questions for you
1. **Look**: A, B or C, or should I render all three as stills first? (Recommended: stills first.)
2. **Stars**: sparse and dim (stays black, my default), or none at all (pure black, but then
   the lensing in scenes 1–2 has nothing to bend)?
3. **Scene 5 math layer**: keep the geodesic-line overlay (more "math channel"), or go purely
   cinematic?

---

## v2 (approved: look B, 58 s, three acts)

| Act | Time | What the viewer sees | The math |
|---|---|---|---|
| **1 Travel** | 0–15 s | The camera flies in from r = 3000M to 80M on a curving 3D path (yaw, roll, a slight look-away that settles onto the hole). Dust and a few nearby stars streak past with parallax. At the centre, a small lensing distortion grows steadily: something invisible is bending the starlight | Einstein angle ≈ √(4M/r) grows as r falls. The tables now extend to b = 2000, so the far-field lensing is exact too |
| **2 The black hole** | 15–45 s | The original 30 s piece, unchanged apart from a +15 s shift. The final ring holds on and hands over to act 3 | (as above) |
| **3 Spacetime** | 44–58 s | The photon-sphere circle (r = 3) draws on where the photon ring was, then the horizon (r = 2) and the ISCO (r = 6). Radial lines grow outward and circles appear inside → out. The camera rises to an oblique 3D view, and at 49–52 s the flat sheet **sinks into Flamm's paraboloid**. The deep part warms in colour (∝ √(1−2M/r)). Pulses of matter fall down the radial lines, accelerating. The camera orbits and pushes toward the throat, then fades | The exact embedding of the Schwarzschild equatorial slice, z = √(8M(r−2M)). Circles are spaced equally in **proper** distance s = √(r(r−2)) + 2 ln((√r+√(r−2))/√2), so their crowding at the throat is real stretching, not decoration |
