# Lab: 3D matrices (2026-11-15)

**Question:** can aion's Classic look carry a 3×3 linear map in 3D (a lattice, basis arrows, the unit cube, a live
determinant) with a camera that keeps orbiting, using only crisp Manim lines?

**Answer: yes.** The view is drawn by a hand-made orthographic camera (azimuth + elevation, as in video 006 ch. 6)
inside one `m.redraw`, so it matches the 2D look exactly. There is no Manim ThreeDScene, no shading and no glow.

## How this folder is set up
It's a mini video folder, so the normal `aion still / preview` commands work on it:
- `assets/audio.wav` is 20 s of silence, made with ffmpeg `anullsrc`.
- `beats.py` builds `Beats({...}, duration=20)` by hand. There's no narration, so there are no word cues.
- `theme.py` is `BASE` (Classic) plus `ihat` / `jhat` / `khat` / `vol` / `collapse`.
- `scenes/s01_space.py` is the one 20 s scene.

## The 20 seconds
| t (s) | beat | what happens |
|---|---|---|
| 0.3 | floor | fixed dim floor grid fades in (top-down view) |
| 0.8 | tilt | camera tips to an oblique view; slow orbit (1.6°/s) from here on |
| 1.8 | hats | î, ĵ, k̂ grow in turn |
| 3.0 | cube | unit cube, 3D lattice, identity matrix, det = 1 |
| 4.2 | shear | I → A = [[1,1,0],[0,1,0],[0,1,2]]: j leans to (1,1,1), k stretches to 2; det 1 → 2 |
| 8.2 | rotate | 90° about **x**: the box tips over onto the floor; det stays 2 |
| 12.2 | squash | flatten z: the box becomes a pink parallelogram on the floor; det → 0 |
| 16.0 | restore | every move undone at once → identity |
| 19.2 | out | HUD fades |

The total matrix is `Q(t) @ R(t) @ S(t)` and is built from the moves, not interpolated elementwise. That keeps the
rotation a true rotation (det stays 2 all the way through it).

## Findings
- **Rotation about z looked like a camera orbit.** With an orbiting camera, Rz is the same motion as the orbit,
  and RzA went edge-on (its projected area was ~1.35 against 2.4 for A). Rotation about x, measured against the
  fixed floor, reads as a real 3D move and stays ≥ 2.0 projected area for every azimuth from −60° to +20°.
- The dim fixed floor (`C.grid_minor`) is what makes every move readable. Without it, the lattice has no reference.
- Depth cue is opacity only: far lattice lines fade to 15 %, and lines are painted far to near. That's enough at
  this lattice size (75 lines, [-2, 2]³).
- The HUD matrix crossfades between the key matrices instead of showing live entries. Live entries would compile
  new LaTeX on every frame. The live det readout is fine because its values repeat.
- Possible next steps: a vector `x` with its image `Ax` traced live; a split view with the 2D analogue; perspective
  (just divide by depth in `Cam.scr`).

## Commands
```bash
uv run aion still lab/2026-11-15-3d-matrices s01 --at 7.5 --at 11.5 --at 15.5
uv run aion preview lab/2026-11-15-3d-matrices
```
Frames: `out/stills/`. Preview: `out/` (see `out/preview.log`).

## Silent track (not committed)
`assets/audio.wav` is gitignored-by-convention; recreate it before rendering:
```bash
ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 20 -c:a pcm_s16le lab/2026-11-15-3d-matrices/assets/audio.wav
```
