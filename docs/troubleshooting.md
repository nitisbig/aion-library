# Troubleshooting

| symptom | cause | fix |
|---|---|---|
| `KeyError: phrase 'x' not found after 12.3s` | beats resolve in order; earlier beat jumped past it, or a typo | reorder specs, check `aion beats`, use `nth=` |
| `scene s02: event at 40.1s outside [12.0, 30.5)` | wrong beat used in a scene | use a beat inside the scene's range |
| `an animation runs until … past the scene end` | `dur` too long near a cut | shorten `dur` or move the cut |
| scenes don't tile the audio | gap/overlap between `@scene` ranges | ranges must chain `T.start → T.cut1 → … → T.end` |
| `BackwardSeek` | one built comp was asked for an earlier time (custom loop) | build a fresh comp: `vid.scene(name).comp(size, fps)` |
| a `drive()`d object jumps | fn increments state instead of computing from t | make it absolute: `mob.move_to(f(t))` |
| shader uniform warning `u_foo unused` | GLSL compiler removed the uniform | use it in the shader, or drop the kwarg |
| black output from a shader | wrote sRGB or premultiplied alpha | output linear RGB, straight alpha (`srgb2lin`) |
| LaTeX error | missing package | `uv run tlmgr install <pkg>`; always run via `uv run` |
| `ELEVENLABS_API_KEY missing` | key not in root `.env` | add it; `aion doctor` confirms |
| render slow / swapping | too many workers for RAM | `-j 1`; `aion doctor` shows suggested workers |
| Taichi `TaichiSyntaxError` on annotations | `from __future__ import annotations` in a sim module | remove it there |
| Wave sim explodes | custom PDE violates CFL | use substeps (see `Wave2D`) |
| colors look washed out / too dark | mixing sRGB and linear values | pass hex colors / `C.*`; aion converts |
| changes not visible after an edit | stale chunk? | chunk keys hash all sources; `aion cache ls`, delete `out/.chunks` to force |
