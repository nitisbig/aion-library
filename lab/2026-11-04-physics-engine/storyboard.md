# Classical mechanics: 60 s hobby scene (exploration)

**One glowing ball travels through the whole piece.** Each act gives it one new law, so the
viewer meets the ideas in order: inertia → force and acceleration → gravity → springs →
energy → momentum → orbits → chaos. Black background, **no text**. The meaning is carried by colour,
used consistently, and by motion. After Effects-grade finish: motion blur, glow, light trails,
impact shockwaves and eased camera moves.

**Everything is simulated.** Nothing is keyframed by hand. A small deterministic engine in numpy
integrates every object, and each act asserts its law against the analytic answer (see §4).

### Colour language (fixed for all 60 s)

| Quantity | Colour | Drawn as |
|---|---|---|
| The ball / mass | warm white core, amber rim | lit disc. Its area ∝ mass |
| Velocity **v** | cyan `#58C4DD` | arrow from the centre, length ∝ \|v\| |
| Force **F** | coral `#FC6255` | thick arrow, pushing at the contact point |
| Acceleration **a** | yellow `#F4D35E` | thin arrow, length ∝ \|a\| |
| Momentum **p** | green `#83C167` | glowing pulse that passes between bodies |
| Kinetic / potential energy | cyan / violet `#B48CFF` | two liquid columns that slosh |
| Spring | steel grey; reddens when compressed, cools to blue when stretched | helix polyline |
| Strobe ghosts | the ball at 15 % opacity every 0.25 s | equal spacing means constant velocity |

---

## 1. Engine choice

| Need | Tool | Why |
|---|---|---|
| Physics: integrators, collisions, springs, orbits, double pendulum | **numpy** (own ~300-line engine, `physics.py`) | Every act has at most 6 bodies, so a general engine isn't needed. Our own code gives exact control: velocity Verlet / RK4 with 1 ms substeps, event-located collisions, and analytic cross-checks. It's deterministic and adds no new dependency |
| All drawing: SDF discs, arrows, helix springs, trails, strobe ghosts, energy columns, rings | **moderngl** (Radeon R4) | Everything is 2D signed-distance shapes plus instanced line segments, which is cheap on the GPU. It reuses the AA line and bloom passes from the neural-network and black-hole labs |
| AE finish: per-object motion blur (8 sub-frames accumulated), bloom, trail decay, shockwave, subtle grain and vignette, camera shake on impacts | **moderngl** post passes | All stays on the GPU. At 1080p60 it's an estimated 0.08–0.15 s/frame, so the 3600-frame final takes about 6–9 min |
| Camera (pan, zoom, dolly, shake) | **numpy** PCHIP keyframes | The same approach as the earlier labs, with the same safe-margin framing check |
| Encode | **ffmpeg** + **tqdm** ETA bar | |

Not used: **Manim** (CPU-only Cairo renderer, and AE-style motion blur and bloom are awkward in it; there's no
LaTeX in this piece), **pyvista** (it's all 2D), **skia** (beautiful AA, but CPU-bound, and with 8× motion-blur
sub-frames × 3600 frames that's too slow on 2 cores). **pymunk** (Chipmunk2D) is a fallback only if we
later want a big many-body pile. It isn't installed, and nothing in this plan needs it.

---

## 2. Storyboard (60.0 s @ 60 fps = 3600 frames)

| # | Time | Concept | What the viewer sees | Camera |
|---|---|---|---|---|
| 1 | 0.0–4.5 | **Inertia** (Newton I) | Black. A spark ignites and becomes the ball, drifting left → right. The cyan **v** arrow grows out of it and never changes. Strobe ghosts trail behind, **evenly spaced**. Nothing pushes, so nothing changes | Slow push-in |
| 2 | 4.5–12.0 | **F = ma** (Newton II) | A coral **F** arrow snaps in behind the ball (overshoot ease). A yellow **a** arrow appears, parallel to F. The strobe spacing grows in the ratio **1 : 3 : 5 : 7** (Galileo's odd numbers, so the distance is ∝ t²). At 8.0 s the frame splits: a **twin with 2× mass** (a disc with √2× the radius) gets the identical F below it. Its **a** arrow is half as long and its ghosts are exactly half-spaced. At 11 s F switches off and both coast: they're back to constant v, which is Newton I again | Track the ball, then widen to fit both |
| 3 | 12.0–20.0 | **Gravity, projectile** | The twin fades out and a floor line draws itself in. The ball is launched up and to the right. Gravity is a constant coral **F** pointing down, and **a** stays fixed and yellow. **v** swings around. A dashed shadow on the floor slides **uniformly** (vx is constant), the trail paints a parabola, and peak-height and range ticks flash. Two bounces (restitution e = 0.7), each with a shockwave ring and a 3-frame camera shake; each bounce is lower by e² | Wide, with a gentle follow |
| 4 | 20.0–30.0 | **Spring: Hooke + SHM** | A spring uncoils down from above and hooks the ball as it comes up off its last bounce. The spring's **F** arrow length is exactly k·\|x\| and always points back toward rest. The ball oscillates vertically. A trace beam spins out to the right: x(t) scrolls and **paints a sine wave** as it goes. The spring's coil colour shows its stress | Pan right as the trace grows |
| 5 | 30.0–37.0 | **Energy & damping** | Two liquid columns rise beside the spring: KE (cyan) and PE (violet) slosh out of phase while a thin white line marks the **constant total**. At 33 s air drag switches on (ζ = 0.08): the oscillation decays, the trace's exponential envelope ghosts in, the total line sinks, and heat motes drift off the ball (where the energy went) | Hold, slight drift |
| 6 | 37.0–45.0 | **Momentum & Newton III** | The spring releases the ball and it flies along a track into a row of 4 resting balls of equal mass. At each contact a **pair of equal and opposite F arrows** flashes (Newton III), and a green **p** pulse runs down the row. The first ball stops dead and the last one flies off with the same speed (elastic, equal masses: velocity exchange) | Track along the row |
| 7 | 45.0–53.0 | **Universal gravitation, orbits** | The camera pulls back fast (a whip zoom out). A star ignites and catches the ball into an **ellipse (e = 0.55)**. **F** always points at the star, with length ∝ 1/r². **v** stays tangent. The ball speeds up at perihelion. Six wedges swept in **equal times** are painted in, each with **equal area** (Kepler II) | Wide; the star is placed off-centre |
| 8 | 53.0–58.5 | **Chaos** | The star collapses into a pivot point and the ball swings out as the bob of a **double pendulum**. Two ghost twins split off with a 10⁻³ rad offset. For 2 s all three move as one; then they **diverge** into three coloured light trails | Slow push-in, then hold |
| 9 | 58.5–60.0 | Out | The trails fade, the three bobs dim to sparks, and a final ember goes to black | Hold |

Continuity: it's always the same ball. Arrows morph rather than cut (the F of gravity in act 3 turns
into the spring's F in act 4, and into the star's F in act 7). At most 3 things change at once.

---

## 3. AE-grade finish (the "look")

- **Motion blur**: 8 sub-frame accumulation (shutter 180°), so fast bounces and the orbit whip smear properly.
- **Glow**: HDR bloom only on the ball core, impacts and the star (threshold-gated, so lines stay crisp).
- **Trails**: exponential-decay light trails on everything in motion. Their length is set per act.
- **Impacts**: a shockwave ring, a 2–3 frame camera shake and a small chromatic split on the ring only.
- **Easing**: arrows appear with a spring-overshoot ease (ironically, a damped oscillator). Cameras use PCHIP easing.
  Nothing pops in: elements fade in with a slight shift, staggered.
- **Grade**: a deep black background (`#05060A`, not pure black), a soft vignette and very light grain. All colours come from the table above.

Three looks, shown as still sheets first so you can pick one:
- **A, Crisp neon**: thin 1.5 px lines, solid discs, minimal bloom (like the neural-network look D)
- **B, Light painting**: long glowing trails, stronger bloom, heavier motion blur, a filmic feel
- **C, Blueprint ink**: hairline strokes, the strobe ghosts as the main motif, almost no glow, an "engineering diagram" feel

---

## 4. Physics correctness (asserted in `physics.py` on every build)

| Act | Check |
|---|---|
| 2 | Strobe gaps follow 1:3:5:7 to 1e-9; the 2m twin's displacement is exactly ½ |
| 3 | Trajectory matches y = v₀y·t − ½gt² to 1e-6; bounce heights fall by e² |
| 4 | Simulated x(t) matches A·cos(ωt), ω = √(k/m), to 1e-5 over 10 periods; energy drift < 1e-6 (Verlet) |
| 5 | The decay envelope matches A·e^(−ζωt); the total energy loss equals the work done by drag |
| 6 | Total momentum and kinetic energy are conserved through the collisions to 1e-9 |
| 7 | Orbit closes; equal-time wedges have equal area to 1e-4; energy and angular momentum are conserved |
| 8 | RK4 energy drift < 1e-6 over the window; the twins' separation grows exponentially (rough Lyapunov estimate) |

## 5. Files (planned)
`physics.py` (engine + checks) · `timeline.py` (per-frame state, camera) · `render.py` (moderngl, CLI:
`still` / `looks` / `video`) · `shaders/` · `NOTES.md`

## 6. Build order
1. `physics.py`, with all the checks passing
2. Look sheets A/B/C at 4 key moments (6.5 s, 15 s, 34 s, 50 s), for you to pick from
3. A 480p30 preview of the full 60 s, then frame checks at every act boundary
4. The 1080p60 final, in the background
