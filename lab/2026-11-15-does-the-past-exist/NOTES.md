# Does the Past Still Exist? (lab, 2026-11-15)

A 2:57 cinematic, philosophical short. Abstract point-cloud worlds, narration by ElevenLabs (voice
XxR1oG87tbJnnecXwla6). All visuals are procedural: Taichi bakes → moderngl point sprites + thin lines → Kawase bloom,
tinted haze, fog/depth fade, motion streaks, ACES, vignette, grain. Every frame is a pure function of audio time,
and every event lands on a word of the narration (`beats.py`). Built on the 'What Is Consciousness?' lab pipeline
(same renderer and post-processing; new worlds, shader modes and timeline).

```bash
uv run aion voice lab/2026-11-15-does-the-past-exist --dry-run            # 1664 chars (generated, cached)
uv run python lab/2026-11-15-does-the-past-exist/geometry.py               # bake all sets (~52 s, 335 MB peak)
uv run python lab/2026-11-15-does-the-past-exist/render.py still --height 270 --cols 4      # contact sheet
uv run python lab/2026-11-15-does-the-past-exist/render.py still --at pieces+2 present+2 --height 540
uv run python lab/2026-11-15-does-the-past-exist/render.py video --height 480 --fps 24 --preset veryfast --crf 20
uv run python lab/2026-11-15-does-the-past-exist/render.py video --height 1080 --fps 30    # final (not run yet)
```
Still `--at` takes beat names with offsets (`where+2`).

## Narration
`voiceover.md` (7 sections), `voice.toml`: eleven_v4, speed 0.85, stability 0.62, seed 23. Pacing: lead-in 3.5 s,
paragraph gap 1.25 s (the pauses after questions), section gap 3.0 s, tail 7 s. 290 words → 176.7 s.
Facts checked (see the comment at the top of voiceover.md): sunlight ≈ 8 min old, Andromeda ≈ 2.5 million
light years, relativity of simultaneity, block universe stated as one view, Einstein's 1955 Besso letter,
reconstructive memory, presentism / growing block / eternalism stated as open possibilities.

## Chapters (cuts snap into real silences)
| range | world | on the words |
|---|---|---|
| 0–25 FORM | Taichi ground (460k), a tree (branches as capsules + foliage, crisp branch lines), three people, a low sun | ground condenses from the centre out (*Think of a moment… A place*); the sun appears and a wave of light crosses the ground (*The light*); the people condense one by one (*The people*); wind loosens it (*And then*); it dissolves into dust and darkness (*gone*); title in 38k particles (*Does the past still exist?*) |
| 22–66 TUNNEL | Taichi tunnel with strata (900k), moment rings every 4 units, floor rails, 6k streaking dust, 40k motes | camera accelerates (*moving instant*); rings flash as they pass (*Each moment arrives*); dust streaks by camera velocity; slows on *the past*, turns 180° to look back (*But where does it go?*): the tunnel behind breaks into drifting fragments; the remembered place reappears in pieces behind us (*keep pieces*), its fragments drift further apart (*not recordings*), dissolve and rebuild in slightly different places (*rebuilds… differently*), fade (*Fragments fade*), blur (*Edges blur*) |
| 63–87 LIGHT | Sun, Earth, Andromeda (160k spiral), 26k stars, 14 shells of incoming light, two light paths | stars brighten (*keeps its own records*); a photon crosses Sun → Earth, Earth glints on arrival (*eight minutes ago*); camera swings to Andromeda, its light thread creeps toward Earth (*two and a half million years*); shells of light converge on Earth (*To look out is to look back… still arriving*) |
| 85–164 BLOCK | 16 slices of the remembered place along the time axis (350k): ground band, tree, three walkers, a sinking sun, thin frames | a 'now' plane sweeps along (*Physics goes further*), stops (*no single universal now*); a green tilted 'now' for another observer cuts diagonally across past and future slices (*What is now for one observer…*); all slices lit, pull back (*a block… laid out together*); slow dolly alongside (Besso quote); only one slice lit, the rest sparse traces (*only the present is real*); past solid, future an unformed flickering cloud, the edge advances (*still being written*); all lit, a soft glow sweeps (*the passing is something we feel*); flicker (*not decided*); the block scatters (*traces are scattered*) |
| 152–end END | the dust field + one expanding light shell + the question in particles | a shell of light expands away (*still travelling*); line 1 forms (*So, if the past no longer exists*), line 2 (*Where did it go?*); far particles go out first, one remains and pulses, dark |

## Pipeline
- `geometry.py`: one builder per set, cached `out/geo_<set>_<hash>.npz`. Layout pos | A(alb, green, size, aux) | B(4).
  Fragment ids are a hash of the point's voxel cell (`cell_hash`), so a whole fragment moves as one piece.
- `shaders/world.vert`: one vertex shader for every set (`u_mode` 0 dust, 1 text, 2 scene, 3 tunnel, 4 cosmos,
  5 block, 9 camera dust) + a `#define LINES` variant. Shared dissolve (`u_form`) crossfades chapters.
- `render.py`: chapter = (window, fn(t) → camera, draws). Overlapping windows render additively, each with its own
  camera. Post is the consciousness lab's (bloom threshold 0.55, haze, ACES, vignette, gated grain).

## Findings
- **Dense sub-objects need their own albedo even with area-normalised energy.** The people (16k points on ~1.5 m²)
  and the trunk were white blobs; the area normalisation assumes the set's average density. Scaling albedo by kind
  (people ×0.2, branches ×0.22, foliage ×0.45) fixed it.
- **Cosmos: cap 0.05 per sprite.** The galaxy and the Sun's 24k-point shell pile up along the view ray; 0.16 blew
  them into white discs.
- **Memory inside the tunnel:** the remembered place at scale 0.3 vanished against the walls. Scale 0.62, a clip
  radius, and dimming the tunnel by 70% while it is on screen make it read.
- **Fragment by cell, not by point.** Per-point noise reads as dust; per-cell offsets read as broken pieces.
- Still weak: the people are blocky capsules (fine at a distance, crude in close-up); the block is bright when the
  camera is close to it during the Besso dolly; the tunnel centre gets hot when the camera looks far down it.

## Numbers
2.27M vertices on the GPU. R4 iGPU: ~0.1–0.2 s/frame at 270–360p. Bakes: scene 24 s, tunnel 26 s (Taichi CPU, 2 threads).
