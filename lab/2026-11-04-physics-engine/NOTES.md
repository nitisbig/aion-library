# Classical mechanics: 60 s hobby piece (exploration)

One glowing ball goes through eight laws: inertia → F = ma → gravity/projectile → Hooke + SHM →
energy and damping → momentum / Newton III → Kepler orbit → chaos. Black background, small LaTeX labels
on the arrows, and one small colour-coded equation per act. Plan: `storyboard.md`.

## Status
**Chosen look: D**, a crisp mix of A and B (user feedback on the first looks: "too much blur and glow").
D keeps A's solid lit discs and clean edges, and B's long trails, long chaos trails and faint parallax dust. It has
**no motion blur** (1 sub-frame), **no bloom** and no soft halos: the momentum glow became a thin green ring, the star lost
its halo and got a crisp corona ring, and the bounce flash is a ring only.
Final: `out/physics_D_1080p60.mp4`. Stills: `out/contact_D.png`.

Timing fixes after the 480p previews:
- act 3's equation moved to the top, because the gravity arrows dip below the floor at each bounce
- the energy column and trace now fade out before the camera pans to the collision row
- the orbit's equation now arrives with the first wedge

The looks that were compared:

| Look | Feel | Sheet | Preview |
|---|---|---|---|
| **A, crisp neon** | solid lit discs, 2–4 px lines, short trails, small bloom, 6 sub-frame blur | `out/contact_A.png` | `out/physics_A_480p30.mp4` |
| **B, light painting** | HDR cores, long additive glowing trails, strong bloom, full-shutter blur, parallax dust | `out/contact_B.png` | `out/physics_B_480p30.mp4` |
| **C, blueprint ink** | hollow balls with crosshairs, hairlines, open arrowheads, dashed trails, faint grid | `out/contact_C.png` | `out/physics_C_480p30.mp4` |

## Engine (all numpy, `physics.py`, cached to `out/sim_<hash>.npz`)
Each act is integrated and asserted against its analytic answer on every build:

| Act | Integrator | Check (measured) |
|---|---|---|
| 1–3 | exact constant-acceleration steps, impact time solved in-step | strobe gaps grow by exactly a·Δt² = 0.1125; the 2m twin's extra displacement is exactly ½; first impact matches √(2h/g) to 1e-9; bounce speeds fall by e = 0.7 exactly |
| 4 | RK4, dt = 1/12000 s | \|x − A sin ωt\| ≤ 1e-12 over 4 periods |
| 5 | RK4 with drag, heat Q integrated alongside | matches the exact underdamped solution to 5e-13; K + U + Q drift 2e-12 |
| 6 | Verlet, linear contact springs | Δp = 4e-16; KE ratio 0.999998; the last ball leaves at the incoming speed |
| 7 | Verlet, central 1/r² | energy drift 9e-9; closes to 6e-8; six equal-time wedges have equal area to 3e-7 |
| 8 | RK4 double pendulum ×3 | energy drift 3e-12; twins (±0.01 rad) split visibly ≈ 55 s; λ ≈ 0.35/s |

The acts hand off physically: the wall is placed so that the ball meets the spring at exactly 20.0 s. The ball is
released at an equilibrium crossing, where the spring force is 0. The floor vanishes under the last ball while it moves
horizontally, which makes that point the **apoapsis** of a Kepler orbit (r_a and GM are solved so that T = 6 s,
e = 0.4). The pendulum starts with the orbit's angular velocity, so the ball's motion is continuous.

## Changes from the storyboard
- Act 2: the ball enters with v ≠ 0, so the strobe gaps form an arithmetic progression (constant difference a·Δt²)
  rather than Galileo's 1:3:5:7, which needs a start from rest.
- The spring is horizontal (the ball rolls into it after its bounces), and x(t) is written **upward**, so the sine wave rises.
- The energy column appears at 21 s, so K and U are seen trading off before the drag (31–34.6 s) adds Q.
- Orbit e = 0.4, not 0.55. At 0.55 the 1/r² force arrow varies 12× around the orbit, so it was invisible at apoapsis or
  ran into the star at periapsis. At 0.4 it varies 5.4×, which is readable and still honest.
- Chaos: δ = 0.01 rad and arms 0.6 : 0.4. With δ = 1e-3 the split only became visible at 57 s.

## Render
```bash
uv run python lab/2026-11-04-physics-engine/physics.py                    # simulate + all checks (~40 s, cached)
uv run python lab/2026-11-04-physics-engine/render.py looks --t 2.5 8.5 14.5 27 33 36.4 44 56.5
uv run python lab/2026-11-04-physics-engine/render.py video --look A --height 480 --fps 30
uv run python lab/2026-11-04-physics-engine/render.py video --look A --height 1080 --fps 60 --preset slow
uv run python -c "import sys; sys.path.insert(0,'lab/2026-11-04-physics-engine'); import timeline as T; print(T.framing_report())"
```
Speed on the R4: about 0.1–0.2 s per frame at 540p with 6–8 motion-blur sub-frames, mostly Python primitive building.
`framing_report()` reports 0 frames with the moving body outside the 5 % safe margin.

## Files
`physics.py` (engine + checks) · `labels.py` (MathTex → skia → RGBA atlas) · `timeline.py` (camera, looks, primitives)
· `render.py` (moderngl SDF primitives, motion-blur accumulation, bloom, CLI) · `shaders/`

## Findings
- SDF primitives in a single instanced geometry-shader pass (capsule, disc, ring, triangle, rounded rect,
  gaussian, label) cover everything in a 2D physics piece. Analytic AA means no SSAA is needed, which makes
  8× motion-blur sub-frames affordable.
- Real motion blur makes the bounce impacts and the collision chain read as fast. Stills under-sell it.
- Contact forces last about 3 frames, so the arrows get a short peak-hold afterglow (τ = 0.2 s). Without it, motion
  blur averages them to nearly nothing.
- Look B with the first settings (ball core 2.4, bloom threshold 0.35) blew the balls out into white blobs. Now tamed to 1.6 / 0.62.
