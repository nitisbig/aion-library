# AGENTS.md: working in aion

aion turns narration into premium math explainer video. Pipeline:
`voiceover.md → (ElevenLabs) audio + word cues → beats.py → @scene layers → GPU comp → render → mux → audit`.

## Reading order (stop as soon as you know enough)
1. **CHEATSHEET.md**: every common pattern on one page. Usually enough.
2. **`uv run aion catalog <word>`**: signatures + one-line docs. `--full` adds examples. Never read aion source to learn the API.
3. **`uv run aion docs <topic>`**: pipeline, timing, layers, fx, sim, render, voice, perf, troubleshooting, recipes.
4. **llms.txt** is the compact index. **llms-full.txt** has everything in one file (only if you must load it all).

Skip: `videos/001-*`…`003-*` and `lab/` (legacy, pre-v2 API, do not copy), `media/`, `.aion-cache/`, `out/`.

## Hard rules
1. **Time is absolute audio seconds.** Every layer is a pure function of `t`. No state carried between frames.
2. **Timing comes from beats only.** `at=T.name`, never `at=12.3`. Beats live in `beats.py`, resolved in order from the SRT.
3. **`at=` lands on the beat.** Motion starts `lead` (theme, 0.15 s) earlier. `lead=0` starts exactly on it.
4. **Manim inside aion:** `m = s.manim()` then `m.add / m.play(anim, at=) / m.seq / m.drive / m.redraw / m.remove`. Never `self.play`, `self.wait` or `add_updater`.
5. **Colors and sizes come from the theme:** `C.<role>`. Define per-video math colors in `theme.py` (`BASE.extend(x=..., fx=...)`). One object keeps one color for the whole video.
6. **Math is computed, never eyeballed.** Use numpy/sympy, and `aion.maths` (fourier…).
7. **Seed everything.** `rng(seed)`, `Sim(seed=...)`.
8. **Look before you render:** `aion still … --at <beat>`, then view the PNG. Then `aion preview`. Only then `aion render --final --bg`.
9. **Storyboard first** (`storyboard.md`, user approval) for production work. Exploration goes in `lab/<date-idea>/` with a NOTES.md.
10. Run `aion audit <video>` before calling a video done (add `--delivery` after the final render).

## Commands (`uv run aion …`, from the repo root)
| task | command |
|---|---|
| check machine | `doctor` |
| new video | `new <slug>` |
| narration | `voice <v> --dry-run`, then `voice <v>` (asks before spending credits) |
| narration structure | `plan <v>` (phrases, silences, suggested `cut(...)`) |
| beat table | `beats <v> [--md]` |
| frame check | `still <v> <scene> --at <beat or s> [--layers]` / `sheet <v> <scene>` |
| preview (480p15) | `preview <v> [scene…] [--range A B]` |
| final (1080p60) | `render <v> --bg` then `status` / `--4k` |
| checks | `audit <v> [--design] [--delivery]` |
| API lookup | `catalog [query] [--full]` / `docs [topic]` |
| cache | `cache ls` / `cache prune --older 7` |

## Video folder
`videos/NNN-slug/`: `video.py` (Video(theme, fps)), `theme.py`, `beats.py` (T), `voiceover.md`, `voice.toml`,
`storyboard.md`, `scenes/sNN_name.py` (one `@scene` per storyboard section), `shaders/` (optional GLSL),
`assets/` (audio.wav/mp3, cue-per-word.srt, words.json, subtitles.srt), `out/` (renders, stills; gitignored).

## When you change aion itself
Add the name to the subpackage's `EXPORTS`, give it a docstring (one-line summary + `Example:`), add a test,
then run `uv run aion docs --build` and `uv run pytest`.
