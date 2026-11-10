# CLAUDE.md

## What this project is

**aion** is the animation engine behind an educational YouTube channel. Each video explains a math, CS,
engineering or physics concept with motion-graphics-grade visuals in the spirit of 3Blue1Brown: the
animation *is* the explanation.

aion v2 is an integrated, agent-first pipeline:
`voiceover.md → ElevenLabs (audio + word cues) → beats → @scene layer stacks → GPU compositor → chunked render → mux → audit`.

**Read [AGENTS.md](AGENTS.md) first** (rules, reading order, command table), then [CHEATSHEET.md](CHEATSHEET.md).
Look up the API with `uv run aion catalog <word>` and topics with `uv run aion docs <topic>`. Don't read
aion's source to learn the API.

**Ignore `videos/001-*`…`003-*` and `lab/` from before v2.** They use the retired v1 API (`aion.style`,
`aion.sync`, `shared.py`). Don't copy from them, don't fix them, and don't run them.

## Two modes. Decide which before starting

| Mode | Goal | Inputs | Bar |
|---|---|---|---|
| **Production** | A finished, publishable video in `videos/NNN-slug/` | `voiceover.md` (→ `aion voice`) or `audio.mp3` + `cue-per-word.srt` | Frame-accurate sync, polished, theme-consistent, 1080p60 (4K on request) |
| **Exploration** | New visual language, techniques | A concept, a question, "try something" | Fast, low-res, bold; 2–3 variations; `lab/<YYYY-MM-DD-idea>/` with a NOTES.md |

If the request is ambiguous, ask which mode it is. The production checklist lives in
`.claude/skills/aion/SKILL.md`.

## Environment

- Python 3.12 with **uv**: `uv run …`, `uv add <pkg>`, never bare `pip`. aion is an editable install, and the CLI is `uv run aion`.
- Engines: **Manim CE 0.22** (as a rasterizer inside aion), **moderngl** (the GPU compositor, shaders, fx),
  **Taichi** (simulations, baked), **pyvista** and **skia-python** (render to arrays → `ArrayLayer`), **ffmpeg** (encode/mux).
- Hardware: AMD A6-9225 (2 cores), Radeon R4 iGPU (Mesa radeonsi, GL 4.5, VAAPI), 3.7 GB RAM (often < 1 GB free).
  moderngl runs headless on the GPU. Keep 1 render worker unless `aion doctor` suggests more.
- LaTeX comes from TinyTeX (pytinytex) via `.venv/bin`. Always run through `uv run`. Missing package: `uv run tlmgr install <pkg>`.
- Secrets: `ELEVENLABS_API_KEY` in the repo-root `.env` (gitignored). Never print or log it. `aion doctor` only reports whether it is present.
- `uv run aion doctor` checks GL, 16F, VAAPI, ffmpeg, LaTeX, fonts, Taichi, RAM and the key.

## Directory layout

```
aion/                 library: core/ sync/ voice/ theme/ gpu/ layers/ comp/ fx/ sim/ maths/ components/
                      render/ audit/ cli/ catalog.py; shaders/{common,comp,fx,layers}; templates/video/
docs/                 topic docs (aion docs <topic>)       AGENTS.md CHEATSHEET.md llms.txt llms-full.txt
videos/NNN-slug/      video.py theme.py beats.py voiceover.md voice.toml storyboard.md
                      scenes/sNN_name.py  shaders/  assets/ (audio.wav/mp3, cue-per-word.srt, words.json, subtitles.srt)
                      out/ (stills, chunks, preview/final mp4; gitignored)
lab/<date-idea>/      experiments (self-contained, NOTES.md)
tests/                pytest (markers: gpu, tex, live; `live` spends ElevenLabs credits and is off by default)
.aion-cache/ media/   caches and progress files (gitignored)
```
Production code never imports from `lab/`. Promote the code into `aion/` first.

## Production rules

1. **Timing comes from the narration.** Word cues are the ground truth. `beats.py` names the moments
   (`T = beats(lam="lambda", cut1=cut("a", "b"))`). Scenes use `at=T.name`, never literal seconds. `cut()`
   places scene boundaries inside real silences.
2. **Storyboard before scene code.** `storyboard.md` gives each scene's range, narration, visual idea and why it
   explains, beats, transitions and layers. Get user approval before building anything long.
3. **Every layer is a pure function of absolute audio time.** Manim content is scored with
   `m.play(anim, at=T.x)` / `m.seq` / `m.drive` / `m.redraw`. No `self.play`, `self.wait` or `add_updater`.
4. **Show before you tell.** `at=` lands motion on the beat (it starts `lead` = 0.15 s early). Hold important
   frames during pauses. Use continuity (transform objects) rather than cuts. At most ~3 things change at once.
5. **Look at your output.** Run `aion still <v> <scene> --at <beat>` and read the PNG before previewing.
   Then `aion audit`. Run finals with `aion render <v> --bg`, then `aion audit <v> --delivery`
   (A/V within one frame, bt709, loudness).
6. Credits, deletions and commits need the user's OK. `aion voice` asks before spending credits.

## Choosing the right tool (per layer, mixed freely in one comp)

| Need | Use |
|---|---|
| Equations, geometry, axes, graphs, morphing | `s.manim()` → Manim mobjects + animations |
| Per-pixel: fields, domain coloring, fractals, glow-heavy looks | `s.shader("x.frag", u_*=Track)` (GLSL, linear light) |
| Physics: particles, n-body, waves, heat, cloth | `bake(Sim)` (Taichi) → `PointsLayer` / `FieldLayer` |
| Point clouds / samples / scalar fields from numpy | `PointsLayer`, `FieldLayer` |
| Scientific 3D (surfaces, volumes) | pyvista off-screen → `ArrayLayer` (no MeshLayer yet) |
| Stylized 2D drawing / textures | skia-python → `ArrayLayer` |
| Photos, diagrams | `s.image(path, height=)` |
| Finishing | `Bloom`, `Glow`, `Blur`, `Grade` (+LUT), `Lens` (vignette/CA/grain), `ZoomBlur`, 2.5D `s.camera` |

Math libraries (numpy, scipy, sympy, opensimplex) are available. Compute every plotted value from the real math,
and double-check formulas shown on screen. `aion.maths` holds verified helpers (`fourier`).

## Visual style

The theme is code: `aion/theme/tokens.py` (`BASE`), extended per video in `theme.py`. Scenes use `C.<token>` only;
`aion audit` flags raw hex colors.
- Dark, slightly blue background (`C.bg`), restrained semantic accents. **Each math object keeps one color for
  the whole video** (define roles: `BASE.extend(x=…, fx=…)`).
- Equations via `Eqn(tex, colors={term: C.role})`, colored to match their visuals.
- Safe margin (`C.margin`), uncluttered frames, text legible on a phone at 1080p (audit `--design`).
- Deliberate motion: eased (`smooth`, `easy_ease`, `out_back`, `spring`), staggered, never popping.
- Improve the style by proposing changes to the theme tokens, not by drifting scene by scene.

## Render progress (required)

- Renders go through `aion still | sheet | preview | render`. Each shows one whole-job tqdm bar with an ETA and writes
  `media/progress/<name>.json`. `aion status` reads it. Report the progress and ETA to the user for background renders.
- Sim bakes show their own bar. Custom frame loops use `aion.progress.Progress(name, total)`.
- Raw Manim experiments in `lab/` inherit `aion.progress.ProgressScene` / `ProgressThreeDScene` (set
  `TOTAL_DURATION`, and call `super().render()` if `render()` is overridden).
- Always run from the repo root (`manim.cfg` applies).

## Code conventions

- Scenes: `scenes/sNN_name.py` with one `@scene(T.a, T.b) def sNN_name(s)` per storyboard section. Scene ranges tile the audio.
- Seed every RNG (`rng(seed)`, `Sim(seed=)`). Renders must be deterministic.
- Commit storyboards, scenes, the library, docs and tests. Never commit `out/`, `media/`, `.aion-cache/`, rendered video, `.env`.
- When you change aion: add the name to its subpackage's `EXPORTS`, write a docstring (summary + `Example:`), add a
  test, run `uv run aion docs --build`, then `uv run pytest`.
