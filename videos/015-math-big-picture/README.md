# 015 · Fundamentals of Math: The Big Picture

Phase 1 (planning, narration, audio, subtitles, design) for a 25-minute overview of six branches of math, all seen
through one circle. Phase 2 builds the scenes.

Run every command from the **repo root** (`~/Desktop/aion`) so `uv` and `manim.cfg` apply.

## The one source of truth

`plan/scenes.yaml` holds every scene: narration, visuals, reveal cues (`at_word`), engines, transitions, map updates,
loops and chapters. Everything else is generated from it or from the audio. Edit the YAML, then rerun the steps below.

```
plan/scenes.yaml ──build_script──▶ voiceover.md, script/narration_full.md, plan/scene_plan.md
voiceover.md ──aion voice──▶ audio/scenes/*.mp3, audio/alignment/*.json, assets/{audio.wav, words.json, scenes.json, subtitles.*}
audio + scenes.yaml ──timing──▶ plan/timing.json, real duration_s, audio/voice_settings.json, subtitles/full.*, audio/full_narration.wav
words + scenes.yaml ──make_beats──▶ beats.py
```

## Rerunning each step

| Step | Command | Cost |
|---|---|---|
| Script and plan docs | `uv run python videos/015-math-big-picture/scripts/build_script.py` (`--check` writes nothing) | free |
| Lint the narration | `uv run python videos/015-math-big-picture/scripts/lint_script.py` | free |
| What voicing would bill | `uv run aion voice 015 --dry-run` | free |
| Voice everything | `uv run aion voice 015` (asks first) | **credits** for changed scenes only |
| Re-voice one scene | `uv run python videos/015-math-big-picture/scripts/regen_scene.py <id>` (dry run), then add `--yes` | **credits**, that scene only |
| A new take of one scene | `... regen_scene.py <id> --retake --yes` (new seed; the old take stays cached) | **credits**, that scene only |
| Real timing | `uv run python videos/015-math-big-picture/scripts/timing.py` | free |
| Beats | `uv run python videos/015-math-big-picture/scripts/make_beats.py`, then `uv run aion beats 015 --md` | free |
| Design tokens | `uv run python videos/015-math-big-picture/scripts/export_tokens.py` (from `theme.py`) | free |
| Style frames | `uv run python videos/015-math-big-picture/design/style_frames.py` | free (GPU, ~1 min each) |
| Self-review | `uv run python videos/015-math-big-picture/scripts/check_plan.py` | free |
| Voice test | `uv run python videos/015-math-big-picture/scripts/voice_test.py` (`--yes` to spend) | **credits** |

Pauses, pacing (`[pacing]` in `voice.toml`) and subtitles are applied after the TTS, so changing them and rerunning
`aion voice 015` costs nothing. Changing a scene's words re-bills that scene only; changing the voice, model or
settings re-bills every scene. Spending credits always needs an OK first.

## Folders

| Path | What |
|---|---|
| `plan/` | `research_digest.md` (rules R1–R15), `decisions.md` (D1–D34, **Review** items), `scenes.yaml`, `scene_plan.md`, `timing.json` |
| `script/` | `narration_full.md` (clean read-through), `pronunciation.md` |
| `audio/` | `scenes/<id>.mp3`, `alignment/<id>.json`, `manifest.json` (pinned requests), `voice_settings.json`, `full_narration.wav` (hard link to `assets/audio.wav`), `voice_test/` |
| `subtitles/` | `full.srt`, `full.vtt` (≤ 42 characters per line, ≤ 2 lines, 1–6 s per cue) |
| `design/` | `design_sheet.md`, `tokens.json`, `style_frames/*.png`, `style_frames.py`, component sheets |
| `scripts/` | the tools above |
| aion files | `voice.toml`, `voiceover.md`, `beats.py`, `theme.py`, `video.py`, `storyboard.md` (points to `plan/scene_plan.md`), `scenes/` (Phase 2) |

`requirements.txt` is exported from `uv.lock` for reference (`uv export --no-hashes --no-dev --format
requirements-txt --no-emit-project`); `uv sync` is the real install.

## Phase 2

Scene files will be `scenes/sNN_<id>.py`, one `@scene(T.<id>, T.<next id>)` per `scenes.yaml` entry (the ranges are
listed in `beats.SCENES`), scored with `at=T.<id>_<word>`. Then `aion still`, `aion audit`, `aion preview`,
`aion render --bg` and `aion audit --delivery`.
