# Luminous terrain (chapter 0 redesign of 002)

**Goal:** a premium, black-stage mountain for the Hessian intro, in the Aion YouTube
design system (black stays black, light only from thin geometry, glow, vignette + grain),
inspired by the FacelessChamp convolution video (glowing wireframe on black) and the
moon-lake piece (point-cloud landscape).

## What was tried
1. **Contours + wire grid everywhere** (first pass). The patches near the walker
   (dome, bowl, pass, tinted bends) looked great right away. The mountains did not:
   noise contours read as coastline blobs, and grid on mountains read as retro synthwave.
2. **Alpine basin** (ridged fBm, domain-warped, walls rising with distance). Better
   forms, but stacked contour stripes on mountain faces still looked cheap, and the camera
   stood inside the wall (grey frames). Fixed with `mback`: the range is pushed back on
   the camera side, so the camera stands in an open valley.
3. **Final: the math is lines, the world is dust.** Mountains = 450k moonlit points
   (lit by slope, peaks brighter, height fog), with only faint major contours. The
   walker's ground keeps crisp silver contours + a local wire grid. That split also
   teaches: crisp = math, soft = world.

## Bugs found on the way
- A contour sat exactly at height 0 → flat ground glowed as a white blob. Fixed:
  contours offset by half a step.
- Rim light fired on the flat floor at grazing angles and bloom tripled it (grey wash).
  Fixed: rim only on the mountain mask; bloom threshold 0.05.

## Numbers
- ~22 ms/frame at 480p on the Radeon R4 (terrain + 450k dots + mist + 2-level bloom).
- Scene 01 (28 s) previews in ~90–120 s at 480p15.

## Render
```bash
uv run python lab/2026-11-05-luminous-terrain/stills.py 480     # stills → out/
uv run manim -ql videos/002-hessian-matrix/scenes/scene_01_fog.py Scene01Fog
```

## Promoted
`aion/components/terrain_gl.py` (`TerrainPlate`), `aion/shaders/terrain.glsl`,
`aion/components/title.py` (`TitlePlate`), new tokens in `aion/style.py`.
