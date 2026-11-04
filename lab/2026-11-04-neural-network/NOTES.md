# Neural network: 30 s hobby piece, handwritten-digit countdown

## v3: crisp, colourful, deeper (current, look D)
Changes requested after v2: less glow and fewer stacked effects, a calmer camera that never runs off screen,
closer layers with 6 hidden layers, and colour.
- **Network:** 196 → 40 → 36 → 32 → 28 → 24 → 16 → 10 (**6 hidden layers**), **97.3 % test accuracy**.
  The countdown digits are re-picked by the same rule (all p > 0.995).
- **Compact layout:** layers 1.8 apart (was 3.6), x ∈ [−6.3, 6.3]. Input fan display-pruned to 24 per neuron
  (960 of 7840 edges); 5,664 edges drawn in all.
- **Crisp look D:** no depth of field, scanlines or grain; bloom only above HDR 0.95 at 0.10 strength; 1-px-AA lines;
  solid lit spheres (Lambert + small specular, sharp edge, tight halo only when active); glyphs with a
  thresholded crisp edge and 0.12 glow; one thin shockwave ring instead of two soft ones; ink is a tight gaussian.
- **Colour:** one hue per layer along a spectrum (sky → teal → green → yellow → orange → coral → violet →
  periwinkle). Edges blend from their source layer's hue to their target's. Negative weights use the same hue,
  darker and desaturated, so the sign still reads. Each output digit has its own hue, and its glyph and ring use it.
- **Camera:** 7 keyframes, no handheld drift, no roll. Keyframe targets and distances were solved numerically
  to centre the projected network, then verified: `timeline.framing_report()` projects every visible neuron and
  glyph in all 900 frames and reports **0 frames outside the 5 % safe margin**.


Black background, no text except the recognised digits. A real MNIST classifier counts down 9 → 0:
each handwritten digit is written onto the input grid as glowing ink, the signal races through
four hidden layers, the matching output flares, and the clean digit rolls out beside it.
The chosen look is **C (hologram)**, with smaller glowing neurons.

## v2: digit recognition (superseded by v3; look C)
- `network.py`: a real MNIST network, **196 (14×14) → 32 → 28 → 24 → 16 → 10**. It uses ReLU, softmax and Adam,
  12 epochs, seed 7. The 28×28 images are 2×2 average-pooled so the input grid stays readable.
  - **Test accuracy 96.8 %** on the 10k MNIST test set. A gradient check runs on every build.
  - The countdown digits are real **test-set** images: for each class, a sample the net gets right with p > 0.98
    whose ink amount is closest to the class median (typical handwriting, not cherry-picked).
    The glyph that appears is the network's actual argmax. The code asserts it equals the digit.
  - MNIST is downloaded from `storage.googleapis.com/cvdf-datasets/mnist` into `out/mnist/` (gitignored).
    The loader checks the idx magic numbers and sizes.
- `layout.py`: the input grid is **tilted 55° toward the camera's side**, like a screen, so the digit is never seen
  mirrored from any camera angle in the piece. Hidden layers are sunflower discs, and the outputs form a column
  with 9 at the top and 0 at the bottom.
  - **Display pruning:** each hidden-1 neuron draws only its 28 strongest input weights (896 of 6272 edges);
    every other layer is drawn in full, 3008 edges in all. The forward pass always uses every weight.
- `timeline.py`:
  - **Countdown:** the pace accelerates from 2.4 s to 1.3 s per digit, with a slower dramatic pass for 0.
    Passes overlap, so several digits can be in flight in different layers.
  - **Ink:** 1500 particles per digit are sampled from the 28×28 intensity. They fly in from the front of the grid,
    written top to bottom, settle to a soft residue, then get sucked into the network when the next digit arrives.
  - **Recognition:** the winning output flares and two shockwave rings expand from it. The digit glyph
    (Inter Light, crisp mask + gaussian glow atlas) rolls in like an odometer: the old digit slides up and fades
    while the new one rises in.
  - **Camera:** PCHIP keyframes. A frontal hero shot as 9 is written, then follow the signal to the output, then
    wide orbits (low and high angles) during the fast digits, a close-up as 0 is written, a whip along the network
    to an output push-in, and a wide pull-back with a fade.
- `render.py`: look C now has smaller neurons (radius 0.05–0.095, about 40 % of v1), an emissive idle glow
  (`idle`), a larger halo (`MARGIN` 4) and a lighter glass body. A new `sprite.*` program handles ink, glyphs and
  rings, and the edges carry a per-layer dimming attribute.
- Speed: about 0.2 s/frame at 540p with SSAA. The 480p30 preview takes about 2 min.

## Findings
- Viewing the input plane from behind mirrors the digit (6, 5 and 4 read backwards in the first v2 preview).
  Tilting the input layer fixed it without restricting the camera.
- Glyph overlap on fast beats turned into a feature: the odometer roll.
- Ink at full brightness turned into a blob in close-ups, so it now runs at 0.55× brightness with smaller particles.
- Wide side views (yaw ≈ 85°) flatten the hidden discs into lines. Keep wide shots at a three-quarter angle (yaw 60–100).

## v1 (superseded)
36 → 16 → 12 → 4 glyph classifier with a learning act. Looks A/B/C were compared and **C was chosen**.
The renders `out/neural_{A,B,C}_480p30.mp4` are from that version.

## Render
```bash
uv run python lab/2026-11-04-neural-network/network.py                       # train + validate (~70 s)
uv run python lab/2026-11-04-neural-network/render.py still --look C --t 6.2 13 22 25.5
uv run python lab/2026-11-04-neural-network/render.py video --look C --height 480 --fps 30
uv run python lab/2026-11-04-neural-network/render.py video --look D --height 1080 --fps 60 --preset slow
uv run python -c "import sys; sys.path.insert(0,'lab/2026-11-04-neural-network'); import timeline as T; print(T.framing_report())"
```
