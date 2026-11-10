---
name: aion
description: Produce or prototype a math/CS/physics explainer video with the aion engine (narration → beats → GPU-composited scenes → render → audit). Use for any request to make, edit, time, render or check a video in this repo, or to try a new visual technique.
---

# aion video production

Read `AGENTS.md` (rules) and `CHEATSHEET.md` (patterns) first. Look up API with `uv run aion catalog <word>`,
not by reading source. Topic docs: `uv run aion docs <topic>`.

## Production checklist (one video in `videos/NNN-slug/`)
1. **Scaffold:** `uv run aion new NNN-slug --title "…"` (skip if it exists).
2. **Narration:**
   - From a script: write/approve `voiceover.md`, run `uv run aion voice NNN --dry-run`, tell the user the billable
     characters, and run `uv run aion voice NNN` only after they OK the spend.
   - From supplied audio: `assets/audio.mp3` (or .wav) + `assets/cue-per-word.srt`.
3. **Structure:** `uv run aion plan NNN`. Read the phrases, silences and suggested cuts.
4. **Beats:** write `beats.py` (`T = beats(...)` with `cut(...)` for every scene boundary), then
   `uv run aion beats NNN --md`.
5. **Storyboard:** `storyboard.md`. For each scene: range (beats), narration, visual idea and *why it explains*,
   beats, transitions, layers/tools. **Stop and get user approval.**
6. **Theme:** `theme.py`. One color per math object for the whole video (`BASE.extend(x=…, fx=…)`).
7. **Scenes:** `scenes/sNN_name.py`, one `@scene(T.a, T.b)` per section. Score with `m.play(at=T.x)`.
   No hard-coded times, no hex colors, no updaters.
8. **Look:** `uv run aion still NNN sNN --at <beat> --at <beat>+0.5`, then **Read the PNGs** in `out/stills/`.
   Fix overlaps, off-frame text, contrast, crowding (≤ 3 things moving).
9. **Audit:** `uv run aion audit NNN --design`. Fix ✘ and judge ⚠.
10. **Preview:** `uv run aion preview NNN [sNN]`. Check sync by ear when the user can.
11. **Final:** `uv run aion render NNN --bg`, then report `uv run aion status` progress/ETA while waiting.
12. **Delivery:** `uv run aion audit NNN --delivery`. Video and audio must match within one frame, bt709, yuv420p.
    Report the path `videos/NNN-slug/out/final.mp4`.

## Exploration (`lab/YYYY-MM-DD-idea/`)
Fast, low-res, bold. Build 2–3 variations side by side. Use `aion` layers in a scratch video folder, or
`ProgressScene` for raw Manim. Write `NOTES.md` (what was tried, what worked, render command, frames).
Report honestly when something looks bad or renders slowly. Promote winners into `aion/` with an `EXPORTS`
entry, a docstring with `Example:`, a test, and `uv run aion docs --build`.

## Never
- Spend ElevenLabs credits, run `pytest -m live`, delete files or commit without the user's OK.
- Print or log `ELEVENLABS_API_KEY`.
- Copy patterns from `videos/001-003` or `lab/`: they use the retired v1 API.
