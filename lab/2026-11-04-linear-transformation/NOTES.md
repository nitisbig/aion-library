# Linear transformation, 45 s (exploration)

The first hobby scene. It's silent with on-screen captions, so there's no audio or SRT.
Matrix used: `A = [[2, -1], [1, 1]]`, vector `v = (2, 1)`, so `Av = (3, 3)`.

## Timeline

| Time (s) | Beat |
|---|---|
| 0–5 | Title card |
| 5–10 | Grid draws in, î and ĵ grow |
| 10–15 | v = 2î + 1ĵ shown as a tip-to-tail recipe, equation in a panel |
| 15–24.5 | Space transforms (4 s), ghost grid stays behind; "lines stay straight…", flash at origin |
| 24.5–29 | Equation morphs to T(v) = 2T(î) + 1T(ĵ); the recipe arrows moved *with* space |
| 29–35 | Landing coordinates of î and ĵ appear and fly into the matrix columns |
| 35–41 | A·v computed column by column = (3, 3), v's tip flashes |
| 41–45 | "A matrix is just a record of where î and ĵ land." |

## Render

```bash
uv run manim -ql --media_dir media lab/2026-11-04-linear-transformation/linear_transformation.py LinearTransformation   # preview, ~70 s
uv run manim -qh --media_dir media lab/2026-11-04-linear-transformation/linear_transformation.py LinearTransformation   # 1080p60
```

## What worked

- **One ValueTracker drives everything.** `M(t) = (1-t)I + tA` is exactly the path
  `ApplyMatrix` takes, so the grid (rebuilt with `apply_matrix` every frame), the vectors,
  the labels and the recipe arrows all move in perfect sync. The arrows are redrawn each
  frame instead of being matrix-transformed, so their tips never get skewed.
  This is worth promoting to `aion/components/` as a reusable "transformable plane".
- Recipe arrows (2î, then ĵ) that are already on screen before the transform and simply
  ride along with it make the "linearity" point without any extra words.
- A `wait_until(absolute_t)` helper keeps the timing exact: 45.07 s at 15 fps, with no drift.
- Building the whole panel layout up front, then growing its background, avoids things
  jumping around in the layout.

## Ideas / next experiments

- Add narration and swap the captions for SRT-driven timing (a test of the production workflow).
- Show a non-linear transform side by side (curved grid) as a counterexample.
- Show the determinant: track the unit square's area as t goes from 0 to 1.
- Use moderngl to draw a glow or bloom on the vectors.
