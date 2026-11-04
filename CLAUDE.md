# CLAUDE.md

## What this project is

**aion** is the animation engine behind a math YouTube channel. Every video explains a math concept with motion-graphics-grade visuals, in the spirit of 3Blue1Brown: the animation *is* the explanation, not decoration on top of it.

The repo serves two modes of work. Figure out which one a request belongs to before starting:

| Mode | Goal | Inputs | Bar |
|---|---|---|---|
| **Production** | A finished, publishable video | `audio.mp3` + `cue-per-words.srt` (+ optional script/notes) | Frame-accurate sync with narration, polished, consistent style, renders at 1080p60 or 4K |
| **Exploration** | Try ideas, find new visual language, prototype techniques | A concept, a question, or "try something" | Fast iteration, low-res previews, bold experiments. Breaking the style guide is allowed |

If the request is ambiguous, ask which mode it is. A good exploration result can be promoted into the reusable library (see *Promoting experiments*).

## Environment

- Python 3.12, managed with **uv**. Use `uv run ...` and `uv add <pkg>`. Never use bare `pip install`.
- `aion/` is installed in editable mode (hatchling build backend), so `from aion import style` works from any scene in `videos/` or `lab/`.
- Installed: `manim` (Community Edition 0.22), `moderngl`, `skia-python`, `pyvista`, `pytinytex`.
- System: `ffmpeg`/`ffprobe` are on PATH. The hardware is modest: an **AMD A6-9225 APU** (2 CPU cores) with an integrated **Radeon R4 GPU** (Stoney, `amdgpu` driver, Mesa radeonsi, OpenGL 4.5).
  - moderngl gets **hardware acceleration** headlessly: `moderngl.create_context(standalone=True)` (or `backend='egl'`) renders on the Radeon R4, with no window needed.
  - It's a low-end integrated GPU with shared memory. Shaders run fine, but keep heavy effects (many passes, huge particle counts, 4K) for final renders, and preview at low resolution.
  - Manim CE's default Cairo renderer runs on the **CPU** only, and with 2 cores long Manim renders are slow. Preview with `-ql`, and render finals in the background.
- **LaTeX** comes from TinyTeX via pytinytex (`~/.pytinytex/.TinyTeX/`). It's available through `.venv/bin` symlinks, so always run Manim with `uv run`; bare `manim`/`latex` from the system shell won't find it. As a fallback, `import aion` also puts the TinyTeX bin directory on PATH. If a LaTeX package is missing: `uv run tlmgr install <pkg>`.

## Directory layout

This is a git repo (`main` branch). `.gitignore` already excludes `.venv/`, `media/`, rendered video, and source audio. Create this structure as it's needed and keep to it:

```
aion/
├── CLAUDE.md
├── pyproject.toml
├── aion/                     # reusable library. Production code imports from here
│   ├── __init__.py           # ensures TinyTeX is on PATH
│   ├── style.py              # palette, fonts, stroke widths, timing constants
│   ├── sync.py               # SRT parsing, word/phrase lookup, timing helpers
│   ├── components/           # reusable mobjects (graphs, labeled vectors, callouts…)
│   ├── shaders/              # GLSL used with moderngl
│   └── render/               # compositing / ffmpeg muxing helpers
├── videos/                   # one folder per production video
│   └── <NNN-slug>/           # e.g. 001-fourier-series
│       ├── assets/           # audio.mp3, cue-per-words.srt, images
│       ├── storyboard.md     # the plan (written BEFORE any scene code)
│       ├── scenes/           # scene_01_intro.py, scene_02_*.py …
│       └── out/              # rendered clips + final.mp4 (gitignored)
├── lab/                      # exploration: free-form experiments
│   └── <YYYY-MM-DD-idea>/    # each experiment self-contained, with a NOTES.md
└── media/                    # manim's default output dir (gitignored)
```

Production scenes must not import from `lab/`. Promote the code into `aion/` first.

## Production workflow

The SRT is word-level and generated from the real audio, so its timestamps are the ground truth for timing. Plan from it; never guess timings.

### 1. Read the inputs
- Parse `cue-per-words.srt` with `aion/sync.py` (write it if it doesn't exist). Build a list of `(word, start, end)` and derive:
  - **sentences/phrases**: split on punctuation and on pauses longer than ~0.35 s
  - **beats**: the moments a visual should land, i.e. key nouns, "this", "here", "notice", equation terms, numbers
  - **silences**: gaps where the visuals can breathe or transition
- Get the true audio duration with `ffprobe`. The video must match it exactly.

### 2. Write `storyboard.md` before writing scene code
For each scene: the time range, the narration text, the **visual idea** (what the viewer sees and *why it explains the concept*), the key beats with their timestamps, the transition in and out, and the tool chosen (Manim, moderngl, skia, pyvista). Show the storyboard to the user and get approval before building anything long. Re-planning costs far less than re-rendering.

Storyboard principles:
- One idea per visual moment. Build complexity up step by step; never show the final, complex picture first.
- Show before you tell. The visual should appear slightly before or exactly on the word, never after it.
- Keep continuity: transform objects into each other instead of cutting. The viewer should be able to track every element.
- Leave space for the viewer to think. Hold important frames during pauses in the narration.

### 3. Build scenes synced to the SRT
- **Never hard-code timings.** Look them up from the SRT, e.g. `t = cue.at("derivative")` or `cue.phrase("the area under the curve")`, then drive `self.wait()` / `run_time` from the differences. One scene file per storyboard section. Each scene knows its absolute start time and plays a slice of the audio.
- Use a helper like `self.wait_until(t)` that waits for `t - self.renderer.time`, so drift can't build up.
- Add the narration to each scene for previews (`self.add_sound(audio_path, time_offset=-scene_start)` or an equivalent slice) so sync can be checked by ear.
- Animation start ≈ beat time − a small lead (~0.1–0.2 s). Most `run_time`s fall between 0.5 and 1.5 s. Avoid robotic linear easing; use `smooth`, `rush_from`, `there_and_back`, etc.

### 4. Preview → verify → final
```bash
# fast preview (480p15). Use this during iteration
uv run manim -pql videos/<slug>/scenes/scene_01_intro.py Scene01Intro
# single still frame to check the layout
uv run manim -sql videos/<slug>/scenes/scene_01_intro.py Scene01Intro
# final quality
uv run manim -qh  ...   # 1080p60
uv run manim -qk  ...   # 4K60, only when asked
```
- After rendering, **check your own output**: extract frames at the key beats (`ffmpeg -ss <t> -i clip.mp4 -frames:v 1 beat.png`) and look at them. Check for overlaps, text running off the frame, and unreadable contrast.
- Check that each clip's duration matches its storyboard range (`ffprobe`).
- Concatenate the clips with ffmpeg's concat demuxer, then mux in the original `audio.mp3` (`-c:v copy -c:a aac -b:a 320k`). Write the result to `videos/<slug>/out/final.mp4`, then confirm with `ffprobe` that the video and audio durations match to within one frame.

## Exploration workflow

- Work in `lab/<date-idea>/`. Speed over polish: low-res renders, still frames, short loops.
- Push the boundaries: custom shaders, particle systems, 3D surfaces, unusual transitions, new typography treatments, mixing Manim with raw GPU/2D rendering.
- When trying a visual idea, build 2–3 variations side by side rather than one, so the user can compare.
- Every experiment gets a short `NOTES.md`: what was tried, what worked, what didn't, the render command, and screenshots or frames.
- Report findings honestly. If a technique looks bad or is too slow to render, say so.

### Promoting experiments
When an exploration produces something worth reusing, generalize it into `aion/components/` (or `aion/shaders/`), give it a clean parameterized API that follows `style.py`, and leave a pointer in the experiment's NOTES.md.

## Choosing the right tool

Plan which library fits each scene **before** writing it. Mixing is fine, since everything ends up as video frames and is composited with ffmpeg or loaded into Manim as an `ImageMobject`/video texture.

| Library | Use it for |
|---|---|
| **Manim CE** | The default. Equations (`MathTex`), geometry, graphs, axes, coordinate planes, morphing/transforms, most 2D explanation. Its camera and Transform system are the core of the channel's look |
| **moderngl** | GPU shader work: fields, fluid-like flows, fractals, complex-function domain coloring, glow/bloom, millions of particles, anything per-pixel. Runs on the integrated Radeon R4 through a headless standalone context. For scenes heavy enough to make Manim's CPU renderer struggle, consider rendering them here instead |
| **skia-python** | High-quality 2D vector/raster drawing with precise antialiasing, gradients, blur, blend modes, and custom typography. Good for stylized overlays, texture generation, and post-processing frames |
| **pyvista** | Scientific 3D: surfaces, meshes, volumes, iso-surfaces, vector fields in 3D, where Manim's `ThreeDScene` is too slow or limited |
| **ffmpeg** | Compositing, concatenation, audio muxing, format conversion, frame extraction |

If another library would clearly do the job better (e.g. `numpy`/`scipy` for computing the math, `sympy` for symbolic steps, `Pillow`, `opensimplex`), propose it and add it with `uv add`.

## Visual style (production)

Define these in `aion/style.py` and **use the constants. Never use ad-hoc colors or sizes in production scenes.**
- Dark background (near-black, slightly blue/neutral, not pure `#000`), with a restrained palette of a few semantic accent colors. Each mathematical object keeps **the same color for the whole video** (e.g. *x* is always blue, *f(x)* always yellow).
- Equations are typeset with LaTeX. Color-code the terms in an equation to match their visual counterparts.
- Clean, generous composition: keep a safe margin (~5% of the frame), don't crowd the frame, and keep at most ~3 things changing at once.
- Motion should look deliberate: eased, spatially continuous, with subtle secondary motion (fade + slight shift, staggered `LaggedStart`) instead of things popping in.
- Readability first. Text must be legible on a phone screen at 1080p.

The style is meant to evolve. When exploration produces a better look, propose updating `style.py` instead of drifting scene by scene.

## Code conventions

- Scene classes: `SceneNNName` in files `scene_NN_name.py`. One storyboard section per file.
- Math correctness is non-negotiable. Compute the plotted curves, values, and labels from the actual math (numpy/sympy). Don't eyeball or fake them, and double-check any formula shown on screen.
- Keep scenes deterministic (seed every RNG) so re-renders are identical.
- Don't commit rendered media (`media/`, `out/`, `*.mp4`, `*.png` frames). Do commit storyboards, scenes, and the library.
- Render long finals in the background and report when they're done. Don't block on multi-minute renders during iteration.

## Render progress (required)

Every render must show **one whole-scene progress bar with an ETA**.
- Every scene inherits from `aion.progress.ProgressScene` (or `ProgressThreeDScene`), **never** plain `Scene`, and sets `TOTAL_DURATION` (in seconds). In production that's the scene's slice of the audio, taken from the SRT or `ffprobe`. Without it, the duration of the previous render is used, and a first render shows no ETA.
- If a scene overrides `render()`, it must call `super().render()`.
- The bar prints `Scene@480p15: 42%|████| 285/675 fr [elapsed, ETA, fr/s]` and finishes with a `✔ … → <output path>` line. `manim.cfg` turns off Manim's per-animation bars and INFO logs; add `-v INFO` to see the logs.
- Live status is written to `media/progress/<Scene>.json` (frames, percent, elapsed_s, eta_s, done) about once a second. When a render runs in the background, read that file to report progress and the ETA to the user.
- Always run renders from the repo root so `manim.cfg` applies.
- Non-Manim pipelines (moderngl, skia, pyvista frame loops, long ffmpeg jobs) follow the same rule: wrap the frame loop in a `tqdm` bar with a known total frame count, so it shows an ETA.
