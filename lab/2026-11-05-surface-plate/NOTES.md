# SurfacePlate lab (prerequisite for video 002)

**Question:** can a moderngl surface rendered every frame inside Manim carry the 3D in
video 002 (morphing quadratic surfaces, fog, slices, pinned 2D overlays) at 1080p60
on the A6-9225 / Radeon R4?

**Answer: yes**, after one fix to Manim's compositing. Promoted to
`aion/components/surface_gl.py` (+ `aion/shaders/surface.glsl`, `aion/components/blit.py`).

## Render commands

```bash
uv run python lab/2026-11-05-surface-plate/bench.py                         # GPU-side timing
uv run manim -sqm lab/2026-11-05-surface-plate/surface_test.py FogLook      # stills
uv run manim -sqm lab/2026-11-05-surface-plate/surface_test.py PuzzleLook
uv run manim -sqm lab/2026-11-05-surface-plate/surface_test.py RulingsLook
uv run manim -qh  lab/2026-11-05-surface-plate/surface_test.py MotionTest   # 6 s
```

## Speed

| | 480p | 1080p |
|---|---|---|
| `render_gl()` (draw + MSAA resolve + readback), opaque | 18 ms | 53 ms |
| same, `opaque=False` (unpremultiply in numpy) | 47 ms | 197 ms → avoid |
| Manim compositing the plate, **stock** (PIL affine transform) | | **606 ms** |
| Manim compositing, **`blit.py` fast path** | | **3.7 ms** (pixel-identical) |
| MotionTest end to end, 1080p60 | | 360 fr in 60 s ≈ **6 fr/s** |

The stock Cairo camera spends ~0.6 s per 1080p frame pushing any ImageMobject through
`PIL.Image.transform`, even when it's already pixel-exact. `blit.install()` patches
`Camera.display_image_mobject`: mobjects marked `_fast_blit` that are axis-aligned and
pixel-exact are copied with numpy; anything else (MovingCamera zoom, rotation) falls
back to the stock path. ShaderPlate (video 001) gets the speed-up too.

## Look: what worked, what didn't

- **Line anti-aliasing:** the first version took `fwidth()` of `fract(...)`, which
  explodes at the wrap seam and drew dotted ghost lines between grid/contour lines.
  Fixed by taking `fwidth` of the continuous coordinate; lines are now a fixed pixel
  width (scaled to 1080p) and fade out where they get denser than ~1 per 3 px.
- **Fog:** with fog colour ≈ surface colour, fog was invisible. Works with a lighter
  fog (`#4A5468`), distance fog ~0.1, drifting height fog, a **horizon haze backdrop**
  (`sky`), and a soft height clamp (`zclip`) so the far ground flattens into a plain.
- **Edge:** a circular fade read as a blob; a rounded-square (superellipse) fade reads
  as a patch of landscape.
- **Slice planes:** translucent quads looked murky on black, and a curtain *under* the
  cut curve is hidden by the opaque surface. What works is a light sheet *rising
  above* the cut curve (brightest at the curve, fading upward and at the ends).
- **Tangent disc:** depth-tested, the surface poked through it (notched). It's an
  annotation, so it's now drawn without depth test.
- **Rulings (`fill` < 1):** additive line mode with no depth write shows `z = xy` as
  its straight rulings cleanly.
- **project():** shares the exact camera matrix, so Manim dots stay locked to the
  surface through morphs and orbits (checked in MotionTest).
