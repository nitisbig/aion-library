# Rendering

| command | output | notes |
|---|---|---|
| `aion still <v> <scene> --at <beat|s|beat+0.3>` | `out/stills/*.png` | repeat `--at`; `--layers` dumps every layer alone |
| `aion sheet <v> <scene>` | `out/stills/<scene>_sheet.png` | contact sheet at the scene's beats |
| `aion preview <v> [scenes] [--range A B]` | `out/preview*.mp4` | 854×480@15 with audio |
| `aion render <v> [scenes] [--range A B]` | `out/final.mp4` | 1920×1080@60 |
| `aion render <v> --4k` / `--draft` / `--low` / `--res 1280x720 --fps 30` | `out/<quality>.mp4` | quality presets |
| `aion render <v> --bg` | detached | then `aion status` (percent, ETA) |

## How a render runs
1. `load_video` imports `video.py`, `theme.py`, `beats.py` and `scenes/s*.py`, and checks that the scenes tile the audio.
2. The timeline is split into **2 s chunks** per scene (`--chunk`). Each chunk's file name contains a hash of
   the video source, aion, theme, size, fps and frame range: `out/.chunks/1080p60-final/s02_0120_0240_<key>.mp4`.
3. Missing chunks render (in parallel with `-j N`; the default is what free RAM allows, which is 1 on this machine).
   **A killed render resumes**: finished chunks are reused. Editing one scene re-renders only its chunks.
4. Chunks are concatenated (stream copy) and the narration is muxed (AAC 320k). The duration equals the audio.

Final encodes use libx264 `-preset slow -tune animation -crf 16`, yuv420p, with BT.709 conversion and tags.
Previews use `-preset ultrafast -crf 23`.

## Progress
Every render prints one bar with an ETA and writes `media/progress/<name>.json` (`frames`, `total_frames`,
`percent`, `elapsed_s`, `eta_s`, `done`). `aion status` reads them. Raw Manim scenes in `lab/` use
`aion.progress.ProgressScene` / `ProgressThreeDScene`. Custom frame loops use `aion.progress.Progress`.

## Speed tips (R4 / 2 cores)
- Iterate with `still`, then `preview --range`. Render finals with `--bg`.
- Split heavy Manim content: static parts in one `manim()` layer, moving parts in another.
- Expensive shaders: `scale_res=0.5`. Sims: bake once (cached).
- 4K is local-only for fx-light scenes. Kaggle bundling is not implemented yet.
