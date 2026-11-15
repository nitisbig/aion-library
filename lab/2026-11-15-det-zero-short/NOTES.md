# Lab: "Determinant = 0" portrait short (2026-11-15)

Built from a reference frame the user supplied: a portrait layout with an outlined two-line title, then
det [3×3] = value with a dim yellow column box, then a perspective 3D lattice with fixed white axes (arrowheads,
integer ticks) and a small yellow object at the origin. The look is Classic (black, crisp, Computer Modern).
The landscape sibling is `lab/2026-11-15-3d-matrices`.

## Setup
A mini video folder: `Video(size=(1080, 1920))`. The frame is 8 units wide and 14.22 tall. The audio is 20 s of
silence and the beats are set by hand (`beats.py`).

## The 20 seconds
| t (s) | what happens |
|---|---|
| 0.2–2.2 | "Matrix 3D" / "Determinant = 0" draw in (outlined CM, gradient yellow-green → blue) |
| 0.6–2.4 | lattice grows out from the origin, axes draw |
| 2.2 / 2.8 | det [I] = 1, yellow unit cube |
| 4.6 | column box on c3: (0,0,1) → (0,0,2), det 1 → 2 (cube stretches up) |
| 8.6 | box moves to c1: (1,0,0) → (1,0,1), det stays 2 (shear) |
| 12.6 | box back to c3: (0,0,2) → (1,1,1) = c1 + c2, det 2 → 0. The camera swings round to face the plane |
| 15.8 | the plane x = z lights pink, det = 0 in pink, the title pulses |

The changing column is a yellow arrow from the origin. The det value is live, and the matrix entries crossfade per
column.

## Findings
- **Perspective** is a single divide, `DIST / (DIST + depth)`, in the hand-made camera. With DIST = 11 it matches
  the reference's gentle convergence of the vertical lines.
- **The lattice must be clipped to a fixed world box after M** (Liang-Barsky, `clip_box`). Without the clip, the
  sheared lattice grows off-screen and over the equation.
- **A collapsed plane is invisible edge-on.** The plane x = z faces the camera at az = ±90°. The camera eases to
  −80° (and 22° → 32° elevation) during the last stage, so the collapse reads as a flat sheet.
- **Outlined title:** `Tex` → `set_color_by_gradient` → fill opacity 0 → stroke 1.8. That's close to the reference's
  hollow type.
- **Speed:** a 480×854 preview renders at ~1.35 fr/s (222 s for 300 frames). A 1080p60 final would be ~1200 frames;
  expect roughly 30–40 min on this machine.

## Commands
```bash
uv run aion still lab/2026-11-15-det-zero-short s01 --at 3.6 --at 7.5 --at 18
uv run aion preview lab/2026-11-15-det-zero-short
```

## Silent track (not committed)
`assets/audio.wav` is gitignored-by-convention; recreate it before rendering:
```bash
ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 20 -c:a pcm_s16le lab/2026-11-15-det-zero-short/assets/audio.wav
```
