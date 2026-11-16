# What Is Consciousness? (lab, 2026-11-15)

A 3:17 cinematic, philosophical short. Abstract point-cloud worlds, narration by ElevenLabs (voice
XxR1oG87tbJnnecXwla6), all visuals procedural: Taichi geometry bakes → moderngl point sprites + thin lines →
Kawase bloom, tinted haze, fog/depth fade, ACES, vignette, grain. Every frame is a pure function of audio time,
and every event is placed on a word of the narration (`beats.py`). Built on the 'What Is Time?' lab pipeline.

```bash
uv run aion voice lab/2026-11-15-what-is-consciousness --dry-run         # 2057 chars (generated, cached)
uv run python lab/2026-11-15-what-is-consciousness/geometry.py            # bake all sets (~100 s, 290 MB peak)
uv run python lab/2026-11-15-what-is-consciousness/render.py still --height 360 --cols 5    # contact sheet
uv run python lab/2026-11-15-what-is-consciousness/render.py still --at cells+1 sky+0.8 --height 540
uv run python lab/2026-11-15-what-is-consciousness/render.py video --height 480 --fps 24 --preset veryfast --crf 20
uv run python lab/2026-11-15-what-is-consciousness/render.py video --height 1080 --fps 30     # final (not run yet)
```
Still `--at` takes beat names with offsets (`notice+1`). Geometry is cached per builder (hash of the builder's
source), so editing one set re-bakes only that set (`geometry.py brain flux` to force a subset).

## Narration
`voiceover.md` (7 sections), `voice.toml`: eleven_v4, speed 0.86, stability 0.6, seed 17; pacing lead-in 3.0 s,
paragraph gap 0.9 s, section gap 2.1 s, tail 5.5 s. 351 words → 196.96 s. Facts checked (see the comment at the top
of voiceover.md): ~86 billion neurons, thousands of synapses each, electrical + chemical signalling, "many" atoms
forged in stars, ~3 lb brain, perception as a constructed model, reconsolidation of memories, Chalmers' hard
problem, IIT-style vs panpsychist views stated as views, "much of" the body's matter replaced.

## Chapters (cuts snap into real silences)
| range | world | on the words |
|---|---|---|
| 0–26.0 DARK | 80k dust points, born one by one | first sparks in black; title of 34k particles on *from the inside*; 42% gather into 70 star clusters on *Dust, gathering into stars*; a slow green wave of light on *began to notice* |
| 26.0–58.1 MATTER | 520 neurons: somas, branching dendrites (random walks), bezier axons, synapse puffs (370k pts, 263k line verts) | one neuron alone, dendrites growing (*Look closely… Only cells*); all somas appear near-to-far (*Eighty-six billion*); axons grow (*reaching out*); green pulses race along axons (*Tiny pulses*); synapses puff when a pulse lands (*Chemicals drift*); pull back until the network is a far star cluster that twinkles (*forged in stars*) |
| 58.1–74.3 BRAIN | Taichi cortex: two half-ellipsoid hemispheres, sulci = contour lines of fbm, temporal bulge, cerebellum with folia, stem, 240 fibre tracts | condenses from the storm; random firing + a travelling wave (*electrical storm*); occipital lights (*color of the sky*), insula (*tastes the sea*), temporal (*a voice it loved*); camera dives in → white flash |
| 74.3–93.2 TUNNEL | Taichi tunnel with folded walls + 12 rails + 2.6k streaks | dims on *built in darkness*; light streaks rush toward the camera (*Light becomes signals*); waves of green along the walls (*Signals become color*); fog lifts (*depth*); a particle face condenses ahead (*and a face*) |
| 93.2–109.7 MEMORY | 24 floating landscape fragments (Taichi), photo frames, thought rings, a broken ground far below | fragments start flat inside frames; frames scatter and the fragments inflate (*not stored like photographs*); each dissolves and reforms with a slightly different relief, staggered (*rebuild the moment, a little differently*); rings rise and fade (*rising, and fading away*) |
| 109.7–141.0 GAP | 21³ lattice (dotted edges, 16% as lines), 70 traced lattice walks, an empty spherical chamber of radius 7.5 | one pathway traced (*trace every signal*), then all (*map every pathway*); nodes spike (*measure every spike*); the camera flies into the empty chamber (*nowhere in that map*); layers twist and slide (*hard problem*); a small light in the chamber (*experience*); everything dims (*in the dark*) |
| 141.0–172.4 FLUX | one 180k cloud (pos = brain sample, B = face sample; knot/galaxy/chaos computed in the shader) | woven 7-strand torus knot (*woven together*); spiral galaxy (*a property of the universe*); formless (*No one knows*); brain (*It forms*), dissolve (*dissolves*), face (*forms again*); particles stream out and in while the face holds (*replaced… you remain*) |
| 172.4–end END | the dust field again + closing question in particles | the face streams away (*a process*); pull back into a gathered cosmos (*the universe is running*); line 1 of the question forms on *Is consciousness*, line 2 on *Or is it a way*; far particles go out, one remains and pulses, dark |

## Pipeline
- `geometry.py`: one builder per set, cached `out/geo_<set>_<hash>.npz`. Layout pos | A(alb, green, size, aux) | B(4).
  Lines use the same layout in vertex pairs.
- `shaders/world.vert`: one vertex shader for every set (`u_mode` 0–10) + a `#define LINES` variant. Shared
  dissolve (`u_form`) gives every chapter crossfade: the outgoing world scatters to dust while the next condenses.
- `render.py`: chapter = (window, fn(t) → camera, draws). Overlapping windows render additively, each with its own
  camera. A camera-wrapped dust box adds volumetric particles. Post as in the 'What Is Time?' lab.

## Findings
- **Use area-normalised energy for every dense set.** Constant-energy sprites (`cap` only) blew neurons, brain,
  face, islands and flux into white blobs at 270–360p. With `area`, energy per world area is constant, so the look
  is also resolution independent. Only sparse sets (dust, text, lattice) stay on `cap`.
- **Half-ellipsoid hemispheres need their own medial radius.** Clamping x onto the fissure packed half of each
  hemisphere's points onto a flat wall that, seen face-on, became a bright core. Sample the medial side with its
  own small radius, sparse (18%) and dim.
- **Back-face dimming makes the cortex folds read.** Additive shells sum front and back; dimming points whose
  ellipsoid normal faces away (×0.22) lets the sulci show.
- **Shade particle faces with the full relief's normals.** Normals from the base ellipsoid alone gave a smooth egg;
  with the nose/eyes/brow/lips in the height function, the face reads frontally.
- **A light parked at the camera's focus point plus low fog piles the far tunnel into a halo.** Keep tunnel fog
  ≥ 0.095 and the fill light weak; dim the tunnel when something must read in its centre.
- **Scattered (dissolving) dust must fade faster than it moves.** `vis *= (1 − 0.9·sc)²` stops a condensing
  650k-point set from flooding the frame around the camera.

## Numbers
2.79M vertices on the GPU. R4 iGPU: ~0.1–0.25 s/frame at 360p. Bakes: neurons 17 s, brain 35 s, tunnel 31 s,
islands 32 s (Taichi CPU, 2 threads).

## 4K final on Kaggle (2026-11-15)
`kaggle/what-is-consciousness-4k/`: `dataset/` (wic-bundle.tar.bin = render.py, geometry.py, beats.json, shaders,
audio.wav, baked geo npz; private dataset nitesh1230/what-is-consciousness-4k-input) and `kernel/` (private T4 GPU
kernel nitesh1230/what-is-consciousness-4k-render, NVIDIA EGL, `WIC_GL_BACKEND=egl`). `render.py freeze` writes
beats.json; without aion, render.py falls back to it and to a plain progress printer.
Constant-energy point sprites (`cap` only: text, lattice) are scaled in `Renderer._draw` so their image energy
density matches the 480p preview at any resolution (checked with local 2160p stills).
Re-run: rebuild the tar, `kaggle datasets version -p dataset -m …`, `kaggle kernels push -p kernel`.
