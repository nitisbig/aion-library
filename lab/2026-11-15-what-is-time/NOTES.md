# What Is Time? (lab, 2026-11-15)

A 2:32 cinematic, philosophical short. Abstract point-cloud worlds, narration by ElevenLabs, all visuals procedural
(Taichi geometry bakes → moderngl point sprites + thin lines → bloom/haze/grain). Every frame is a pure function of
audio time, and every event is placed on a word of the narration (`beats.py`).

```bash
uv run aion voice lab/2026-11-15-what-is-time --dry-run          # 1503 chars (already generated, cached)
uv run python lab/2026-11-15-what-is-time/geometry.py              # bake all point sets (~40 s, 270 MB peak)
uv run python lab/2026-11-15-what-is-time/render.py still --at now place+1 sink+3 --height 540
uv run python lab/2026-11-15-what-is-time/render.py video --height 480 --fps 15 --preset veryfast   # preview, ~10 min
uv run python lab/2026-11-15-what-is-time/render.py video --height 1080 --fps 30    # final, ~80 min (not run yet)
uv run python lab/2026-11-15-what-is-time/render.py video --height 540 --start sink --stop sats+3 --tag _bend
```
Still `--at` takes beat names with offsets (`heart+0.3`).

## Narration
`voiceover.md` (7 sections; section gaps = long breaths), `voice.toml`: voice XxR1oG87tbJnnecXwla6 (this video only), speed 0.86, stability 0.6,
lead-in 3 s, tail 5 s. 276 words → 151.7 s. Facts checked: time dilation from speed (SR) and gravity (GR); GPS
clocks are corrected (net ≈ +38 µs/day); no universal "now" (relativity of simultaneity); the block universe is
stated as one view ("some physicists"); the arrow of time as entropy growth.

## Chapters (cuts snap into real silences)
| range | world | on the words |
|---|---|---|
| 0–20.8 DARK | 70k dust points born one by one (birth twinkle) | title made of 42k particles condenses on *What is time?*; light pulse on *heart*; green dusk light on *evening*; the field flies apart on *slips away* |
| 20.8–40.7 ROAD | Taichi tunnel, 700k pts + time rings + 10 rails | past = solid gray (camera turns back on *Behind us*), future = flickering unformed green cloud (*open, unformed*), a bright ring at the *now* edge; camera pushes through it → white flash |
| 40.7–58.2 FABRIC | 7 stacked space-grids + 260 rising time threads | threads weave in on *woven together*; one slice lights on *a when*; an event flashes and rings out on *a place* |
| 58.2–86.8 BEND | grid sheet + 12 billboard clocks + orbit | ripple on *bends*; a clock at 0.9c ticks 1/γ = 0.44× (*slower*); the sheet sinks into a well (*Sink deeper*), a clock slides to the throat and slows by √(1−r_s/r); satellite orbits (*Satellites*); three planes of simultaneity sweep at different angles (*no single now*); 8 clocks at different radii, each its own rate (*our own time*) |
| 86.8–103.7 BLOCK | 18 Taichi landscapes stacked (468k), dune travels slab to slab | a moving bright "now" slab that stops on *nothing truly passes*, then every slice equally lit; stack spreads into frames (*frames of a film*) |
| 103.7–117.1 ARROW | ordered crystal: fibonacci shells + rings + 900 stars | diffuses (σ ∝ √t) on *Order gives way*; cools (green → gray) on *Coffee cools*; stars blink out on *Stars burn out*; everything streams one way, tapering like an arrowhead (*the arrow*) |
| 117.1–end END | the dust field again | drifts, then freezes on *something we bring*; a single moment-plane sweeps (everything else dims) on *one moment at a time*; far particles go out first; one particle remains, pulses on *at all*, dark |

## Pipeline
- `geometry.py`: one builder per set, cached `out/geo_<set>_<hash>.npz`. Layout pos | A(alb, green, size, aux) | B(4).
  Lines are the same layout in vertex pairs. The dissolve direction is hashed from `gl_VertexID` (no extra attribute).
- `shaders/world.vert`: one vertex shader for all sets (`u_mode` switch) + `#define LINES` variant. Shared dissolve
  (`u_form`) gives every chapter crossfade: the outgoing world scatters to dust while the next condenses.
- `render.py`: chapter = (window, fn(t) → camera, draws). Overlapping windows render additively with each chapter's own
  camera. A camera-wrapped dust box (mode 8) adds volumetric particles. Post: Kawase bloom (threshold 0.55), a wide
  bloom level as tinted haze, ACES, vignette, grain (near-black kept almost clean), flash, final fade.

## Findings
- **Constant-energy sprites are resolution-dependent.** Sets without the area normalisation (grids, title, crystal)
  look ~2× dimmer at 1080 than at 360. Tune those at the final resolution. The area-normalised sets (tunnel, block)
  transfer.
- **Overlap is the enemy in additive point clouds.** The block stack and the crystal blew out until their energy
  dropped 4–8×. Anything that piles up along the view ray (stack seen from above, a sphere's shells) needs much less.
- **A gravity well seen from above is invisible.** Lines just converge in perspective. A low side-on camera shows the
  funnel profile; brightening and greening the throat by depth helps.
- **Reversed `smoothstep(e0 > e1)` is undefined in GLSL.** On radeonsi it hid the time threads entirely. Use
  `1 - smoothstep(lo, hi, x)`.
- Future-as-unformed-cloud worked once the scatter was small (≤1.1 units growing over 30 units ahead). Bigger scatter
  hid the tunnel.
- Still weak: the arrow streams read as a soft smear rather than a sharp arrow; the moment-sweep at the end is subtle.

## Numbers
1.88M vertices on the GPU. R4 iGPU: ~0.15–0.3 s/frame at 360p, ~0.9–1.4 s/frame at 1080p.

## 4K final on Kaggle (2026-11-15)
`kaggle/what-is-time-4k/`: `dataset/` (wit-bundle.tar.bin = render.py, geometry.py, beats.json, shaders, audio.wav, baked
geo npz; private dataset nitesh1230/what-is-time-4k-input) and `kernel/` (private GPU kernel
nitesh1230/what-is-time-4k-render). `render.py freeze` writes beats.json; without aion, render.py falls back to it and to
a plain progress printer. `WIT_GL_BACKEND=egl` selects EGL.
Result: Tesla T4 via NVIDIA EGL (GL 4.3), 4552 frames at 2.2 fr/s, 36 min total. 3840x2160 30 fps, yuv420p bt709, A/V
151.73 s / 151.72 s, 3.1 GB (crf 16; grain makes it big). Looks the same as the Mesa renders.
Re-run: rebuild the tar, `kaggle datasets version -p dataset -m …`, `kaggle kernels push -p kernel`.
