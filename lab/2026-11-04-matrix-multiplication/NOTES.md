# Matrix multiplication, 30 s (exploration)

A silent hobby scene with captions. `A = [[1,2,3],[4,5,6]]` (2×3), `B = [[7,8],[9,10],[11,12]]` (3×2),
`C = A @ B = [[58,64],[139,154]]`, computed with numpy.

## Timeline

| Time (s) | Beat |
|---|---|
| 0–3 | Title card "Matrix multiplication / row × column" |
| 3–7.6 | A · B = C fades in, with C as `?` slots. Size labels 2×3 · 3×2: the inner 3s flash, the outer sizes fly down to make 2×2 |
| 8–15.4 | c₁₁ done slowly: row/column boxes appear, each pair pulses and flies down as `1·7 + 2·9 + 3·11 = 58`, then 58 drops into its slot |
| 15.4–25.3 | c₁₂, c₂₁, c₂₂: the same boxes slide to the next row/column and each entry is faster than the last |
| 25.3–30 | General rule `c_ij = Σ_k a_ik b_kj`, with the indices colored to match (i = row blue, j = column yellow, k = green) |

Colors: rows of A / i → `ACCENT`, columns of B / j → `VEC`, results and k → `I_HAT`.

## Render

```bash
uv run manim -ql lab/2026-11-04-matrix-multiplication/matrix_multiplication.py MatrixMultiplication   # preview, ~30 s
uv run manim -qh lab/2026-11-04-matrix-multiplication/matrix_multiplication.py MatrixMultiplication   # 1080p60
```

## What worked

- **Going from slow to fast.** The first entry is computed term by term; the next ones speed up
  (speed 1.0 → 0.5 → 0.3 → 0.2). The viewer learns the move once and then watches the pattern repeat.
- The highlight boxes are `Transform`ed from one row/column to the next instead of being redrawn,
  so the eye follows them around.
- Using the same colors in the expression, the boxes and the formula's indices ties the
  numbers to the general rule.

## Issues / ideas

- The first draft ran 31 s. The fast entries took longer than planned, so the speeds were tightened.
- `compute_entry` could be promoted to `aion/components/` as a reusable "dot-product walk".
- Variation to try: show the column of B lifting up and rotating to lie over the row of A
  (the classic "pour the column into the row" picture).
- Non-square follow-up: show that B·A is 3×3, so the order matters.
