# Tower Bridge: architecture in 30 s

A 30 s hobby piece with no text on a black background, made with After Effects-style
GPU line art. The plan is in `storyboard.md`.

## What was built
- `geometry.py` builds Tower Bridge from real proportions as about 1,580 polylines (12k
  segments) plus 576 triangles for the solid look. It includes steel tower frames, the
  Gothic stone skin (turrets, spires, pointed-arch windows, crenellations), walkway trusses,
  suspension chains (the parabola is solved through the real anchor heights:
  a = 0.01439, vertex at |x| = 96 m), hangers, the deck, bascules with counterweights,
  and the pier chambers.
- `render.py` is a moderngl renderer running headless on the Radeon R4:
  - The geometry shader expands each segment into an anti-aliased screen-space quad. A
    per-group reveal and per-polyline order give the staggered draw-on, with a bright
    "drawing head" at the tip.
  - The bascules rotate in the vertex shader about their real pivots (0 → 86° → 0).
  - The water reflection is the same geometry mirrored, with depth-scaled wobble.
  - Amber tension pulses run chain → tie → walkway, toward the centre.
  - Post: motion blur from 4 accumulated sub-frames, 6-level dual-filter bloom, radial
    chromatic aberration, filmic soft clip, vignette, and seeded grain.

## Looks compared (`out/looks_*.png`)
| Look | Verdict |
|---|---|
| A Blueprint (cyan steel, warm stone, x-ray) | Clearest explanation. Steel inside the stone stays visible |
| B Gold hologram | Most moody, but one hue loses the steel-vs-stone story |
| C Rim-lit solids with hidden lines removed | Most "real", but hides the steel and counterweights |
| **H Hybrid (chosen)** | A until 25.5 s, then C's solid stone dissolves in bottom-up while the bascules close |

## Crisp variant (look S)
A second design for maximum clarity with no blur at all. It turns off bloom, motion blur,
chromatic aberration and grain, and makes the reflection a clean mirror (no wobble). It
renders at 2× supersampling (3840×2160 internally) and box-downsamples to 1080p for clean
anti-aliasing. To make up for the light bloom no longer adds, exposure goes up (1.9) and
lines get slightly heavier (1.5). The result looks like a technical illustration.
`render.py video --look S --height 1080 --fps 60 --crf 12 --preset slow`

## What worked / what didn't
- The GPU is fast: the 480p30 preview takes about 22 s (about 40 fr/s). Stills take about 1 s.
- The first pass was overexposed: overlapping additive lines clipped to white and hid the
  colours and the pulses. Fixed by lowering exposure from 1.6 to 0.95, darkening the
  walkway/chain base during the pulse window so amber carries it, and saturating the stone.
- Hermite camera keys placed close together can swing in too close (26.5 s was clipped).
  Keep consecutive keys at similar distances.
- From the front, the raised leaves line up with the tower lines. A low, oblique key at
  25 s fixes it.
- Reflections need to be faint (0.07). At 0.16 they read as a second bridge.

## Render
```bash
uv run python lab/2026-11-04-london-bridge/render.py looks --t 6 11 20 24            # A/B/C sheets
uv run python lab/2026-11-04-london-bridge/render.py still --look H --t 20 --height 540
uv run python lab/2026-11-04-london-bridge/render.py video --look H --height 480 --fps 30 --preset veryfast
uv run python lab/2026-11-04-london-bridge/render.py video --look H --height 1080 --fps 60 --mb 4   # final
```

## Promotion candidates
The line renderer (GS quads + reveal + bloom post) is a reusable "construction line art"
engine. It's worth generalizing into `aion/shaders/` + `aion/render/` if we use it again.
